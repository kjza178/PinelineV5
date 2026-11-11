"""
separate.py — STAGE 6 (Tách nền): dùng Demucs bỏ GIỌNG NÓI (tiếng Trung) khỏi audio
gốc, GIỮ lại nhạc nền + tiếng động. Bước render sẽ trộn nền này với giọng Việt (F5)
-> không còn tiếng Trung lọt qua (hơn hẳn ducking).

Đầu vào : work/<job>/source.mp4
Đầu ra  : work/<job>/no_vocals.wav   (nhạc/SFX)  [+ vocals.wav để soi nếu cần]

Chạy Demucs qua SUBPROCESS -> model nạp ở tiến trình con, xong là tự nhả VRAM
(không đụng model chính). htdemucs xử theo chunk nên VRAM bị chặn (~4-6GB), vừa 12GB.

Chạy tay:
    python separate.py work/<job>
    python separate.py work/<job> --device cpu     # nếu GPU bận
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

from core.manifest import Manifest
from engines.vram import free_gpu_vram

STAGE = "separate"
# Mặc định cắt mỗi khúc 1 tiếng (3600s) khi phim dài > 70 phút (4200s)
# Giúp Demucs chỉ tốn ~4-5GB RAM thay vì 70GB RAM trên phim 10-12 tiếng và không vượt trần 4GB WAV.
CHUNK_SEC = int(os.getenv("DEMUCS_CHUNK_SEC", "3600") or "3600")
LONG_AUDIO_THRESHOLD_SEC = int(os.getenv("DEMUCS_LONG_THRESHOLD_SEC", "4200") or "4200")


def _find_video(work_dir: Path) -> Path | None:
    m = Manifest(work_dir)
    vp = (m.stage("download") or {}).get("video_path")
    if vp and Path(vp).exists():
        return Path(vp)
    for c in sorted(work_dir.glob("source.*")):
        if c.suffix.lower() in {".mp4", ".mkv", ".webm", ".mov"}:
            return c
    return None


def _probe_duration(path: Path) -> float:
    """Lấy thời lượng file media (giây) qua ffprobe."""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(path)],
            capture_output=True, text=True, timeout=60,
        )
        return float((r.stdout or "0").strip() or 0.0)
    except Exception:  # noqa: BLE001
        return 0.0


def _update_sep_progress(m: Manifest, pct: float | None, cur_text: str) -> None:
    """Cập nhật tiến độ vào stage 'separate' VÀ đồng bộ sang stage 'asr' nếu ASR đang chờ tách giọng."""
    now = time.time()
    try:
        st = m.data.setdefault("stages", {}).setdefault(STAGE, {})
        st.update({"status": "running", "progress": pct, "cur_text": cur_text, "updated_at": now})
        m.data["stages"][STAGE] = st

        asr_st = m.data.get("stages", {}).get("asr")
        if isinstance(asr_st, dict) and asr_st.get("status") == "running":
            asr_st["cur_text"] = cur_text
            if pct is not None:
                asr_st["progress"] = pct
            asr_st["updated_at"] = now
        m.save()
    except Exception:  # noqa: BLE001
        pass


def _extract_audio(video: Path, out_audio: Path) -> None:
    """Tách audio GỐC chất lượng cao (stereo 44.1k) — khác audio.wav 16k mono của ASR.

    Dùng FLAC (không phải PCM WAV): phim dài (~8h+) ở 44.1k stereo 16-bit vượt
    giới hạn WAV cổ điển (~4GB) -> ffmpeg báo 'Filesize ... invalid for wav' và
    Demucs đọc file hỏng (mã lỗi 1).
    """
    out_audio = Path(out_audio)
    # FLAC lossless, không dính trần 4GB của header WAV.
    if out_audio.suffix.lower() != ".flac":
        out_audio = out_audio.with_suffix(".flac")
    from engines.media_ts import AUDIO_TS_FIX
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(video), "-vn", "-af", AUDIO_TS_FIX, "-ac", "2", "-ar", "44100",
         "-c:a", "flac", str(out_audio), "-loglevel", "error"],
        check=True)


def _run_demucs_on_file(
    src_audio: Path,
    tmp_out: Path,
    device: str,
    work_dir: Path,
    m: Manifest,
    chunk_idx: int = 0,
    n_chunks: int = 1,
) -> tuple[Path, Path]:
    """Chạy Demucs trên 1 file audio (ngắn hoặc 1 chunk) và trả về (no_vocals_wav, vocals_wav)."""
    if tmp_out.exists():
        shutil.rmtree(tmp_out, ignore_errors=True)
    tmp_out.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", "demucs", "--two-stems=vocals",
        "--device", device, "-o", str(tmp_out), str(src_audio),
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace", bufsize=1,
    )

    last = 0.0
    pat = re.compile(r"(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)")
    tail_lines: list[str] = []
    for line in proc.stdout:
        if (work_dir / ".stop").exists():
            try:
                proc.terminate()
                proc.kill()
            except Exception:  # noqa: BLE001
                pass
            raise RuntimeError("Đã dừng tách nền theo yêu cầu (.stop)")
        s_line = line.strip()
        if s_line:
            tail_lines.append(s_line)
            if len(tail_lines) > 15:
                tail_lines.pop(0)
        mo = pat.search(line)
        now = time.time()
        if now - last > 1.5:
            last = now
            chunk_pct = None
            if mo:
                cur, tot = float(mo.group(1)), float(mo.group(2))
                chunk_pct = min(cur / tot * 100.0, 99.9) if tot else None
            if chunk_pct is not None:
                if n_chunks > 1:
                    overall_pct = round(((chunk_idx + chunk_pct / 100.0) / n_chunks) * 100.0, 1)
                    label = f"Tách giọng Demucs (khúc {chunk_idx + 1}/{n_chunks}): {overall_pct}%"
                else:
                    overall_pct = round(chunk_pct, 1)
                    label = f"Tách giọng Demucs: {overall_pct}%"
                _update_sep_progress(m, overall_pct, label)

    proc.wait()
    if proc.returncode != 0:
        err_tail = " | ".join(tail_lines[-4:]) if tail_lines else ""
        raise RuntimeError(f"Demucs lỗi (mã {proc.returncode})" + (f": {err_tail[:240]}" if err_tail else ""))

    nv = next(tmp_out.rglob("no_vocals.wav"), None)
    if not nv:
        raise RuntimeError("Không thấy no_vocals.wav sau Demucs")
    voc = next(tmp_out.rglob("vocals.wav"), None)
    if not voc:
        raise RuntimeError("Không thấy vocals.wav sau Demucs")
    return nv, voc


def _concat_wav_chunks(chunk_files: list[Path], out_wav: Path, work_dir: Path) -> None:
    """Ghép các chunk WAV thành 1 file WAV hoàn chỉnh (dùng -rf64 auto để hỗ trợ >4GB cho phim dài)."""
    list_file = work_dir / f"_concat_{out_wav.stem}.txt"
    part_out = out_wav.with_name(out_wav.stem + ".partial.wav")
    try:
        lines = []
        for f in chunk_files:
            safe_p = str(f.resolve()).replace("\\", "/").replace("'", "'\\''")
            lines.append(f"file '{safe_p}'")
        list_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(list_file), "-rf64", "auto", "-c", "copy",
                str(part_out), "-loglevel", "error",
            ],
            check=True,
        )
        os.replace(part_out, out_wav)
    finally:
        list_file.unlink(missing_ok=True)
        part_out.unlink(missing_ok=True)


def run_separate(work_dir: str | Path, device: str = "cuda", force: bool = False) -> dict:
    work_dir = Path(work_dir)
    m = Manifest(work_dir)
    if m.is_done(STAGE) and not force:
        st = m.stage(STAGE)
        nv_ok = st and Path(st.get("no_vocals_path", "")).exists()
        voc_ok = (work_dir / "vocals.wav").exists() and (work_dir / "vocals.wav").stat().st_size > 1000
        if nv_ok and voc_ok:
            if not (work_dir / "audio.wav").exists():
                from engines.asr.asr import extract_audio
                extract_audio(str(work_dir / "vocals.wav"), str(work_dir / "audio.wav"))
            print(f"[skip] Tách nền/tiếng đã xong: {st['no_vocals_path']}")
            return st

    video = _find_video(work_dir)
    if not video:
        raise RuntimeError("Chưa có video (chạy download trước).")

    m.mark_running(STAGE)
    _update_sep_progress(m, 0.0, "Đang chuẩn bị tách giọng (Demucs)…")
    free_gpu_vram("trước tách nền Demucs")
    try:
        # Xóa WAV hỏng cũ (nếu có) — phim dài từng ghi PCM >4GB không có RF64.
        for stale in (work_dir / "orig_audio.wav", work_dir / "orig_audio.flac"):
            if stale.exists() and stale.suffix.lower() == ".wav" and stale.stat().st_size > 4_000_000_000:
                try:
                    stale.unlink()
                    print(f"[sep] Xóa WAV quá lớn/hỏng: {stale.name}")
                except OSError:
                    pass

        dur_sec = float((m.stage("download") or {}).get("duration_sec") or 0.0) or _probe_duration(video)
        tmp_out = work_dir / "_demucs"
        dest_nv = work_dir / "no_vocals.wav"
        dest_voc = work_dir / "vocals.wav"

        if dur_sec > LONG_AUDIO_THRESHOLD_SEC:
            # === CHẾ ĐỘ CẮT KHÚC (CHUNKED DEMUCS) CHO PHIM DÀI (>70 PHÚT, VD 2H - 12H) ===
            # Tránh nạp nguyên tensor 12h (~70GB RAM) gây sập Demucs mã 1 và hỗ trợ resume từng khúc.
            chunks_dir = work_dir / "_demucs_chunks"
            if force and chunks_dir.exists():
                shutil.rmtree(chunks_dir, ignore_errors=True)
            chunks_dir.mkdir(parents=True, exist_ok=True)

            v_stat = video.stat()
            meta_file = chunks_dir / "chunks_meta.json"
            src_sig = {"video": video.name, "size": v_stat.st_size, "mtime": int(v_stat.st_mtime), "chunk_sec": CHUNK_SEC}
            need_split = True
            if meta_file.is_file():
                try:
                    old_sig = json.loads(meta_file.read_text(encoding="utf-8"))
                    if old_sig == src_sig and int(old_sig.get("n_chunks") or 0) > 0:
                        need_split = False
                except Exception:  # noqa: BLE001
                    need_split = True

            if need_split:
                shutil.rmtree(chunks_dir, ignore_errors=True)
                chunks_dir.mkdir(parents=True, exist_ok=True)
                est_chunks = max(1, int((dur_sec + CHUNK_SEC - 1) // CHUNK_SEC))
                print(f"[sep] Phim dài {dur_sec/3600:.1f}h -> Cắt thành ~{est_chunks} khúc ({CHUNK_SEC//60} phút/khúc) để không tràn RAM...", flush=True)
                _update_sep_progress(m, 0.5, f"Đang tách audio gốc thành {est_chunks} khúc FLAC…")
                from engines.media_ts import AUDIO_TS_FIX
                subprocess.run(
                    [
                        "ffmpeg", "-y", "-i", str(video), "-vn",
                        "-af", AUDIO_TS_FIX, "-ac", "2", "-ar", "44100",
                        "-c:a", "flac", "-f", "segment", "-segment_time", str(CHUNK_SEC),
                        str(chunks_dir / "chunk_%03d.flac"), "-loglevel", "error",
                    ],
                    check=True,
                )
                chunk_inputs = sorted(chunks_dir.glob("chunk_*.flac"))
                src_sig["n_chunks"] = len(chunk_inputs)
                meta_file.write_text(json.dumps(src_sig, ensure_ascii=False, indent=2), encoding="utf-8")
                # Dọn orig_audio.flac nguyên cục cũ (nếu có) để giải phóng ổ đĩa
                try:
                    (work_dir / "orig_audio.flac").unlink(missing_ok=True)
                except OSError:
                    pass

            meta_info = json.loads(meta_file.read_text(encoding="utf-8"))
            n_chunks = int(meta_info.get("n_chunks") or 0)
            if n_chunks <= 0:
                raise RuntimeError("Không cắt được chunk audio nào cho Demucs")

            nv_chunks: list[Path] = []
            voc_chunks: list[Path] = []
            for idx in range(n_chunks):
                c_flac = chunks_dir / f"chunk_{idx:03d}.flac"
                c_nv = chunks_dir / f"no_vocals_{idx:03d}.wav"
                c_voc = chunks_dir / f"vocals_{idx:03d}.wav"
                if c_nv.exists() and c_nv.stat().st_size > 1000 and c_voc.exists() and c_voc.stat().st_size > 1000:
                    print(f"[sep] Khúc {idx + 1}/{n_chunks} đã tách xong từ trước -> dùng lại (resume).", flush=True)
                    pct_done = round(((idx + 1) / n_chunks) * 100.0, 1)
                    _update_sep_progress(m, pct_done, f"Tách giọng Demucs (khúc {idx + 1}/{n_chunks}): {pct_done}%")
                else:
                    if not c_flac.exists():
                        raise RuntimeError(f"Thiếu file {c_flac.name} khi resume Demucs")
                    print(f"[sep] Demucs ({device}) đang tách khúc {idx + 1}/{n_chunks} ({c_flac.name})...", flush=True)
                    base_pct = round((idx / n_chunks) * 100.0, 1)
                    _update_sep_progress(m, base_pct, f"Tách giọng Demucs (khúc {idx + 1}/{n_chunks}): {base_pct}%")
                    nv_tmp, voc_tmp = _run_demucs_on_file(
                        c_flac, tmp_out, device, work_dir, m, chunk_idx=idx, n_chunks=n_chunks,
                    )
                    shutil.move(str(nv_tmp), str(c_nv))
                    shutil.move(str(voc_tmp), str(c_voc))
                    shutil.rmtree(tmp_out, ignore_errors=True)
                    try:
                        c_flac.unlink(missing_ok=True)
                    except OSError:
                        pass
                nv_chunks.append(c_nv)
                voc_chunks.append(c_voc)

            print(f"[sep] Đang ghép {n_chunks} khúc thành vocals.wav & no_vocals.wav (RF64)...", flush=True)
            _update_sep_progress(m, 99.0, "Đang ghép các khúc âm thanh sau Demucs…")
            _concat_wav_chunks(nv_chunks, dest_nv, work_dir)
            _concat_wav_chunks(voc_chunks, dest_voc, work_dir)
            shutil.rmtree(chunks_dir, ignore_errors=True)
        else:
            # === PHIM NGẮN / VỪA (<= 70 PHÚT): CHẠY 1 LƯỢT NHƯ CŨ ===
            orig = work_dir / "orig_audio.flac"
            print("[sep] Tách audio gốc FLAC (44.1k stereo)...")
            _update_sep_progress(m, 1.0, "Đang tách audio gốc FLAC từ video…")
            _extract_audio(video, orig)

            print(f"[sep] Demucs ({device})...")
            _update_sep_progress(m, 2.0, "Tách giọng Demucs: 0%")
            nv, voc = _run_demucs_on_file(orig, tmp_out, device, work_dir, m, chunk_idx=0, n_chunks=1)
            shutil.move(str(nv), str(dest_nv))
            shutil.move(str(voc), str(dest_voc))

        # Tách audio.wav (16kHz mono PCM) trực tiếp từ vocals.wav để các engine ASR dùng
        from engines.asr.asr import extract_audio
        dest_audio = work_dir / "audio.wav"
        print("[sep] Trích xuất audio.wav (16k mono PCM) từ vocals.wav để ASR chính xác...")
        _update_sep_progress(m, 99.5, "Đang trích xuất audio 16kHz cho ASR…")
        extract_audio(str(dest_voc), str(dest_audio))

        shutil.rmtree(tmp_out, ignore_errors=True)
        try:
            (work_dir / "orig_audio.flac").unlink(missing_ok=True)
        except OSError:
            pass
        try:
            stale_wav = work_dir / "orig_audio.wav"
            if stale_wav.exists():
                stale_wav.unlink()
        except OSError:
            pass
    except Exception as e:  # noqa: BLE001
        m.mark_failed(STAGE, e)
        raise

    result = m.mark_done(
        STAGE,
        no_vocals_path=str(work_dir / "no_vocals.wav"),
        vocals_path=str(work_dir / "vocals.wav"),
        audio_path=str(work_dir / "audio.wav"),
        device=device,
    )
    print(f"[ok] Tách nền & tiếng xong -> {result['no_vocals_path']} | {result['vocals_path']}")
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage tách nền (Demucs).")
    ap.add_argument("work_dir")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)
    run_separate(args.work_dir, device=args.device, force=args.force)


if __name__ == "__main__":
    main()
