"""
firered_asr.py — STAGE ASR bằng FireRedASR2-AED (system VAD+LID+ASR+Punc).

Cần clone repo + tải model local (không pip một dòng):

    scripts\\install_firered_asr.bat

Hoặc thủ công:
    git clone https://github.com/FireRedTeam/FireRedASR2S.git vendor/FireRedASR2S
    pip install -r vendor/FireRedASR2S/requirements.txt
    huggingface-cli download FireRedTeam/FireRedASR2-AED --local-dir <FIRERED_MODELS>/FireRedASR2-AED
    ... (VAD, LID, Punc tương tự)

Config (pineline.config.json / env):
    FIRERED_ROOT   = Z:/Pineline/vendor/FireRedASR2S
    FIRERED_MODELS = D:/AI_CACHE/firered   (chứa FireRedASR2-AED, FireRedVAD, ...)

Chạy tay:
    python firered_asr.py work/<job>
    python firered_asr.py work/<job> --force
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

from engines.asr.asr import ensure_audio_wav, _salvage_asr
from core.config import get as cfg
from engines.asr.fun_asr_nano import _wav_dur
from core.manifest import Manifest
from engines.subs import split_long_segments, sub_split_cfg, to_srt
from engines.vram import free_gpu_vram

STAGE = "asr"
ENGINE = "firered_asr"
MODEL_ID = "FireRedASR2-AED"


def _roots() -> tuple[Path, Path]:
    root = Path(os.getenv("FIRERED_ROOT") or cfg("FIRERED_ROOT", "") or
                str(Path(__file__).resolve().parents[2] / "vendor" / "FireRedASR2S"))
    models = Path(os.getenv("FIRERED_MODELS") or cfg("FIRERED_MODELS", "") or
                  str(root / "pretrained_models"))
    return root, models


def _ensure_firered_importable(root: Path) -> None:
    if not root.is_dir():
        raise RuntimeError(
            f"Chưa có FireRedASR2S tại {root}. Chạy scripts/install_firered_asr.bat "
            "hoặc git clone https://github.com/FireRedTeam/FireRedASR2S.git vendor/FireRedASR2S"
        )
    # package nằm trong repo root
    p = str(root.resolve())
    if p not in sys.path:
        sys.path.insert(0, p)
    bin_dir = root / "fireredasr2s"
    if bin_dir.is_dir():
        os.environ["PATH"] = str(bin_dir.resolve()) + os.pathsep + os.environ.get("PATH", "")


def _parse_firered_result(result: dict) -> list[dict]:
    """FireRedAsr2System.process → [{start,end,text}]."""
    rows: list[dict] = []
    sents = result.get("sentences") or []
    if isinstance(sents, list) and sents:
        for s in sents:
            if not isinstance(s, dict):
                continue
            text = (s.get("text") or "").strip()
            if not text:
                continue
            st = float(s.get("start_ms", 0) or 0) / 1000.0
            en = float(s.get("end_ms", st) or st) / 1000.0
            rows.append({"start": round(st, 3), "end": round(max(en, st + 0.2), 3), "text": text})
        return rows
    # fallback: words → gom theo dấu / khoảng nghỉ
    words = result.get("words") or []
    if words:
        buf, st0, en0 = [], None, None
        for w in words:
            if not isinstance(w, dict):
                continue
            tok = (w.get("text") or "").strip()
            a = float(w.get("start_ms", 0) or 0) / 1000.0
            b = float(w.get("end_ms", a) or a) / 1000.0
            if not tok:
                continue
            if st0 is None:
                st0 = a
            buf.append(tok)
            en0 = b
            if tok.endswith(("。", "！", "？", ".", "!", "?")) or "。" in tok:
                piece = "".join(buf).strip()
                if piece:
                    rows.append({"start": round(st0, 3), "end": round(en0 or st0, 3), "text": piece})
                buf, st0, en0 = [], None, None
        if buf and st0 is not None:
            rows.append({"start": round(st0, 3), "end": round(en0 or st0, 3),
                         "text": "".join(buf).strip()})
        return rows
    text = (result.get("text") or "").strip()
    if text:
        dur = float(result.get("dur_s") or 1.0)
        rows.append({"start": 0.0, "end": round(dur, 3), "text": text})
    return rows


def run_asr_firered(
    work_dir: str | Path,
    device: str = "auto",
    force: bool = False,
) -> dict:
    work_dir = Path(work_dir)
    m = Manifest(work_dir)
    root, models = _roots()
    _ensure_firered_importable(root)

    need = {
        "FireRedASR2-AED": models / "FireRedASR2-AED",
        "FireRedVAD": models / "FireRedVAD",
        "FireRedLID": models / "FireRedLID",
        "FireRedPunc": models / "FireRedPunc",
    }
    missing = [k for k, p in need.items() if not p.exists()]
    if missing:
        raise RuntimeError(
            f"Thiếu model FireRed: {', '.join(missing)} trong {models}. "
            "Chạy scripts/install_firered_asr.bat"
        )

    # Skip theo FILE (không chỉ is_done) — tránh start_job mark_running làm chạy lại
    # ASR đè lên TTS đang đọc.
    asr_file = work_dir / "asr.json"
    if not force and asr_file.exists():
        st = m.stage(STAGE) or {}
        if not m.is_done(STAGE):
            try:
                n = len(json.loads(asr_file.read_text(encoding="utf-8")))
            except Exception:  # noqa: BLE001
                n = st.get("n_segments") or 0
            m.mark_done(
                STAGE,
                asr_path=str(st.get("asr_path") or asr_file),
                audio_path=st.get("audio_path"),
                n_segments=n,
                language=st.get("language") or "zh",
                model=st.get("model") or MODEL_ID,
                engine=st.get("engine") or ENGINE,
            )
            st = m.stage(STAGE) or {}
        print(f"[skip] ASR đã xong: {st.get('asr_path') or asr_file}")
        return st

    dl = m.stage("download")
    if not dl or not dl.get("video_path"):
        cands = list(work_dir.glob("source.*"))
        if not cands:
            raise RuntimeError("Chưa có video (download).")
        src = str(cands[0])
    else:
        src = dl["video_path"]

    asr_path = work_dir / "asr.json"
    wav = work_dir / "audio.wav"
    rows: list[dict] = []
    total = 0.0

    if force:
        try:
            asr_path.unlink(missing_ok=True)
        except OSError:
            pass

    m.mark_running(STAGE)
    free_gpu_vram("trước ASR FireRed")
    use_gpu = True
    if device and device != "auto" and "cpu" in device.lower():
        use_gpu = False

    try:
        st = m.data.setdefault("stages", {}).setdefault(STAGE, {})
        st.update({"engine": ENGINE, "model": MODEL_ID, "cur_text": "tách audio…",
                   "updated_at": time.time(), "status": "running", "progress": 2})
        m.data["stages"][STAGE] = st
        m.save()

        if ensure_audio_wav(src, wav, force=force):
            print(f"[{ENGINE}] Đã tách audio 16k mono")
        total = _wav_dur(wav)

        print(f"[{ENGINE}] Nạp system AED+VAD+LID+Punc · gpu={use_gpu}…")
        st.update({"cur_text": f"nạp {ENGINE}…", "progress": 10, "updated_at": time.time(),
                   "total_sec": total})
        m.save()

        from fireredasr2s import FireRedAsr2System, FireRedAsr2SystemConfig
        from fireredasr2s.fireredasr2 import FireRedAsr2Config
        from fireredasr2s.fireredlid import FireRedLidConfig
        from fireredasr2s.fireredpunc import FireRedPuncConfig
        from fireredasr2s.fireredvad import FireRedVadConfig

        vad_dir = need["FireRedVAD"] / "VAD"
        if not vad_dir.exists():
            # một số bản gói VAD trực tiếp dưới FireRedVAD/
            vad_dir = need["FireRedVAD"]

        vad_config = FireRedVadConfig(
            use_gpu=False,
            smooth_window_size=5,
            speech_threshold=0.4,
            min_speech_frame=20,
            max_speech_frame=2000,
            min_silence_frame=20,
            merge_silence_frame=0,
            extend_speech_frame=0,
            chunk_max_frame=30000,
        )
        lid_config = FireRedLidConfig(use_gpu=use_gpu, use_half=False)
        asr_config = FireRedAsr2Config(
            use_gpu=use_gpu,
            use_half=False,
            beam_size=3,
            nbest=1,
            decode_max_len=0,
            softmax_smoothing=1.25,
            aed_length_penalty=0.6,
            eos_penalty=1.0,
            return_timestamp=True,
        )
        punc_config = FireRedPuncConfig(use_gpu=use_gpu)

        asr_system_config = FireRedAsr2SystemConfig(
            str(vad_dir),
            str(need["FireRedLID"]),
            "aed", str(need["FireRedASR2-AED"]),
            str(need["FireRedPunc"]),
            vad_config, lid_config, asr_config, punc_config,
            enable_vad=1, enable_lid=1, enable_punc=1,
        )
        asr_system = FireRedAsr2System(asr_system_config)

        st.update({"cur_text": "đang nhận diện (FireRedASR2)…", "progress": 20,
                   "updated_at": time.time()})
        m.save()
        print(f"[{ENGINE}] process · audio {total:.0f}s...")

        # Video rất dài: cắt theo giờ để tránh OOM (FireRed system tự VAD trong clip)
        import subprocess
        import tempfile
        import math
        slice_sec = float(os.getenv("FIRERED_SLICE_SEC", "1200") or 1200)  # 20 phút
        n_slice = max(1, int(math.ceil(total / slice_sec)))
        tmp_dir = Path(tempfile.mkdtemp(prefix="firered_"))
        try:
            for si in range(n_slice):
                st0 = si * slice_sec
                en0 = min(total, (si + 1) * slice_sec)
                clip = tmp_dir / f"slice_{si:03d}.wav"
                subprocess.run(
                    ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                     "-ss", f"{st0:.3f}", "-to", f"{en0:.3f}", "-i", str(wav),
                     "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(clip)],
                    check=True,
                )
                result = asr_system.process(str(clip), f"slice{si}")
                if not isinstance(result, dict):
                    result = result[0] if result else {}
                part = _parse_firered_result(result or {})
                for r in part:
                    r["start"] = round(float(r["start"]) + st0, 3)
                    r["end"] = round(float(r["end"]) + st0, 3)
                rows.extend(part)
                pct = 20 + int(70 * (si + 1) / n_slice)
                st.update({
                    "progress": min(pct, 95),
                    "cur_text": f"ASR slice {si+1}/{n_slice} · {len(rows)} câu",
                    "n_segments": len(rows),
                    "done_sec": float(en0),
                    "total_sec": total,
                    "updated_at": time.time(),
                    "status": "running",
                    "engine": ENGINE, "asr_engine": ENGINE, "model": MODEL_ID,
                })
                m.data["stages"][STAGE] = st
                m.save()
                print(f"[{ENGINE}] slice {si+1}/{n_slice} · {len(rows)} câu · @{en0:.0f}s",
                      flush=True)
        finally:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)

        rows = [{"i": i, "start": r["start"], "end": r["end"], "text": r["text"]}
                for i, r in enumerate(rows)]
        max_zh, _, max_dur = sub_split_cfg()
        rows = split_long_segments(rows, max_chars=max_zh, key="text", max_dur=max_dur)
        for i, r in enumerate(rows):
            r["i"] = i
        try:
            from engines.asr.asr_spam import sanitize_asr_rows
            rows, spam_info = sanitize_asr_rows(
                rows, work_dir=work_dir, source_path=asr_path, heal=True)
            if spam_info.get("n_cleaned") or spam_info.get("n_healed"):
                print(f"[{ENGINE}] spam: cleaned={spam_info['n_cleaned']} "
                      f"healed={spam_info['n_healed']}", flush=True)
        except Exception as _se:  # noqa: BLE001
            print(f"[{ENGINE}] asr_spam skip: {_se}", flush=True)
        asr_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        (work_dir / "sub.zh.srt").write_text(to_srt(rows, key="text"), encoding="utf-8")

    except Exception as e:  # noqa: BLE001
        _salvage_asr(m, asr_path, rows, wav if wav.exists() else None, total, err=e)
        raise

    result = m.mark_done(
        STAGE, asr_path=str(asr_path), audio_path=str(wav),
        n_segments=len(rows), language="zh", model=MODEL_ID, engine=ENGINE,
    )
    print(f"[ok] {ENGINE}: {len(rows)} câu -> {asr_path}")
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="ASR FireRedASR2-AED (system).")
    ap.add_argument("work_dir")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)
    run_asr_firered(args.work_dir, device=args.device, force=args.force)
    os._exit(0)


if __name__ == "__main__":
    main()
