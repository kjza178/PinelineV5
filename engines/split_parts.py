"""
split_parts.py — Tự động tính toán và chia video dài (3h-12h+) thành các Part 2-2.5h
để chạy ASR/TTS/Render độc lập chống lệch time, sau đó ghép concat lại thành bản Full.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Chuẩn thời lượng lý tưởng mỗi part: 2.0h đến 2.5h (tối đa 3.0h)
DEFAULT_TARGET_HOURS = 2.5
MIN_SPLIT_HOURS = 3.0  # Dưới 3 tiếng thì không cần chia part

# Copy-mode cần ~1× kích thước nguồn (+ margin). Re-encode ENOSPC → phình gấp nhiều lần.
_DISK_FULL_RE = re.compile(
    r"no space|enospc|disk.*(full|quota)|not enough space|errno\s*28|os error 28",
    re.I,
)
_SPLIT_FREE_MARGIN = 1.15  # cần free ≥ source×1.15
_SPLIT_FREE_FLOOR_BYTES = 512 * 1024 * 1024  # tối thiểu +512MB


class DiskFullError(OSError):
    """Ổ đầy — dừng split, không fallback re-encode."""


def _is_disk_full_text(*chunks: str | None) -> bool:
    blob = "\n".join(c or "" for c in chunks)
    return bool(_DISK_FULL_RE.search(blob))


def free_bytes(path: str | Path) -> int:
    """Dung lượng trống trên volume chứa `path` (tạo parent nếu chưa có)."""
    p = Path(path)
    probe = p if p.exists() else p.parent
    while not probe.exists() and probe.parent != probe:
        probe = probe.parent
    return int(shutil.disk_usage(str(probe)).free)


def estimate_split_need_bytes(video_path: str | Path) -> int:
    """Ước lượng chỗ cần cho split copy-mode (= gần bằng size nguồn + margin)."""
    src = Path(video_path).stat().st_size
    return int(src * _SPLIT_FREE_MARGIN) + _SPLIT_FREE_FLOOR_BYTES


def assert_enough_space_for_split(video_path: str | Path, out_dir: str | Path) -> None:
    need = estimate_split_need_bytes(video_path)
    free = free_bytes(out_dir)
    if free < need:
        raise DiskFullError(
            f"Không đủ chỗ để split: cần ≥{need/1e9:.1f}GB, còn {free/1e9:.1f}GB "
            f"tại {Path(out_dir).resolve()} (Errno 28 / ENOSPC guard)."
        )


def _unlink_quiet(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


def probe_duration(video_path: str | Path) -> float:
    """Lấy thời lượng video tính bằng giây."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json", str(video_path)
    ]
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=flags)
    try:
        data = json.loads(res.stdout)
        return float(data.get("format", {}).get("duration", 0.0))
    except Exception:
        return 0.0


def calculate_part_plan(total_sec: float, target_hours: float = DEFAULT_TARGET_HOURS) -> list[tuple[float, float]]:
    """
    Tính toán danh sách (start_sec, end_sec) cho từng part.
    Nếu total_sec <= 2.5h hoặc < MIN_SPLIT_HOURS: trả về 1 part duy nhất.
    """
    total_hours = total_sec / 3600.0
    if total_hours < MIN_SPLIT_HOURS:
        return [(0.0, round(total_sec, 3))]

    # Số part = làm tròn (tổng giờ / target_hours)
    n_parts = max(2, int(round(total_hours / target_hours)))
    part_dur = total_sec / n_parts

    plan = []
    for i in range(n_parts):
        st = i * part_dur
        en = total_sec if i == n_parts - 1 else (i + 1) * part_dur
        plan.append((round(st, 3), round(en, 3)))
    return plan


def find_best_cut_point(video_path: str | Path, target_cut_sec: float, search_radius_sec: float = 90.0) -> float:
    """
    Tìm điểm khoảng lặng (silence) gần nhất với target_cut_sec trong phạm vi ±search_radius_sec.
    Tránh cắt đứt ngang câu thoại đang nói của diễn viên.
    """
    t0 = max(0.0, target_cut_sec - search_radius_sec)
    dur = search_radius_sec * 2.0
    cmd = [
        "ffmpeg", "-y", "-hide_banner",
        "-ss", str(t0), "-t", str(dur),
        "-i", str(video_path),
        "-vn", "-af", "silencedetect=n=-25dB:d=0.20",
        "-f", "null", "-"
    ]
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=flags)
    output = res.stderr or ""

    # Parse mốc silence_start và silence_end
    silences: list[tuple[float, float]] = []
    cur_start = None
    for line in output.splitlines():
        m_st = re.search(r"silence_start:\s*([0-9.]+)", line)
        if m_st:
            cur_start = float(m_st.group(1)) + t0
            continue
        m_en = re.search(r"silence_end:\s*([0-9.]+)", line)
        if m_en and cur_start is not None:
            cur_end = float(m_en.group(1)) + t0
            silences.append((cur_start, cur_end))
            cur_start = None

    if not silences:
        return target_cut_sec

    # Chọn khoảng lặng gần target_cut_sec nhất
    best_silence = min(silences, key=lambda s: abs((s[0] + s[1]) / 2.0 - target_cut_sec))
    best_point = (best_silence[0] + best_silence[1]) / 2.0
    return round(best_point, 3)


def compute_smart_plan(video_path: str | Path, target_hours: float = DEFAULT_TARGET_HOURS) -> list[dict]:
    """
    Tính plan hoàn chỉnh có điểm cắt thông minh (tránh đứt câu thoại).
    """
    total_sec = probe_duration(video_path)
    if total_sec <= 0:
        raise ValueError(f"Không lấy được thời lượng video: {video_path}")

    raw_plan = calculate_part_plan(total_sec, target_hours)
    if len(raw_plan) <= 1:
        return [{
            "part": 1,
            "total_parts": 1,
            "start": 0.0,
            "end": total_sec,
            "duration": total_sec,
            "smart_cut": False,
        }]

    # Tìm smart cut cho các điểm ranh giới giữa
    boundaries = [0.0]
    for i in range(len(raw_plan) - 1):
        raw_cut = raw_plan[i][1]
        smart_cut = find_best_cut_point(video_path, raw_cut, search_radius_sec=90.0)
        boundaries.append(smart_cut)
    boundaries.append(total_sec)

    plan = []
    for i in range(len(boundaries) - 1):
        st = boundaries[i]
        en = boundaries[i + 1]
        plan.append({
            "part": i + 1,
            "total_parts": len(boundaries) - 1,
            "start": st,
            "end": en,
            "duration": round(en - st, 3),
            "smart_cut": True,
        })
    return plan


def split_video_to_parts(
    video_path: str | Path,
    out_dir: str | Path,
    target_hours: float = DEFAULT_TARGET_HOURS,
    prefix: str = "part",
) -> list[dict]:
    """
    Cắt video thành các part theo smart plan (lossless copy).

    ENOSPC / disk full → dừng ngay, không fallback re-encode (re-encode phình GB
    và làm đầy ổ hơn). Fail mid-way → xoá `out_dir` partial.
    """
    video_path = Path(video_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    plan = compute_smart_plan(video_path, target_hours=target_hours)
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    # Preflight: copy-mode cần khoảng bằng size nguồn
    if len(plan) > 1:
        assert_enough_space_for_split(video_path, out_dir)
        print(
            f"[split_parts] Free check OK: cần ~{estimate_split_need_bytes(video_path)/1e9:.1f}GB, "
            f"còn {free_bytes(out_dir)/1e9:.1f}GB",
            flush=True,
        )

    results = []
    try:
        for item in plan:
            k = item["part"]
            total_k = item["total_parts"]
            st = item["start"]
            en = item["end"]
            out_file = out_dir / f"{prefix}_{k:02d}_of_{total_k:02d}.mp4"

            print(f"[split_parts] Cắt Part {k}/{total_k}: {st:.1f}s -> {en:.1f}s (dur: {item['duration']:.1f}s) -> {out_file.name}...", flush=True)

            if total_k == 1:
                # Video ngắn không cần cắt, copy hoặc link
                shutil.copy2(video_path, out_file)
            else:
                cmd = [
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-ss", str(st), "-to", str(en),
                    "-i", str(video_path),
                    "-c", "copy",
                    "-avoid_negative_ts", "make_zero",
                    "-movflags", "+faststart",
                    str(out_file)
                ]
                r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=flags)
                err_blob = (r.stderr or "") + "\n" + (r.stdout or "")
                copy_bad = r.returncode != 0 or not out_file.exists() or out_file.stat().st_size < 1000

                if copy_bad and _is_disk_full_text(err_blob):
                    _unlink_quiet(out_file)
                    raise DiskFullError(
                        f"ffmpeg copy Part {k}/{total_k} hết ổ (ENOSPC) — dừng, không re-encode. "
                        f"stderr: {(r.stderr or '')[:400]}"
                    )
                # File stub >1KB nhưng stderr không rõ — nếu free gần 0 thì cũng coi là ENOSPC
                if copy_bad and free_bytes(out_dir) < _SPLIT_FREE_FLOOR_BYTES:
                    _unlink_quiet(out_file)
                    raise DiskFullError(
                        f"ffmpeg copy Part {k}/{total_k} thất bại và ổ gần đầy "
                        f"(free<{_SPLIT_FREE_FLOOR_BYTES/1e6:.0f}MB) — dừng, không re-encode."
                    )

                if copy_bad:
                    # Chỉ re-encode khi lỗi keyframe/copy — KHÔNG khi disk full
                    print(
                        f"[split_parts] Copy Part {k} lỗi (rc={r.returncode}); thử re-encode nhẹ "
                        f"(không phải ENOSPC)...",
                        flush=True,
                    )
                    _unlink_quiet(out_file)
                    # Re-check free trước re-encode (re-encode cần nhiều hơn copy)
                    free = free_bytes(out_dir)
                    # Ước part ~ source/n_parts nhưng ultrafast CRF18 có thể lớn hơn nhiều —
                    # yêu cầu còn ≥ 2× ước part copy, tối thiểu 2GB
                    part_est = max(2 * 1024**3, int(video_path.stat().st_size / max(1, total_k) * 2.0))
                    if free < part_est:
                        raise DiskFullError(
                            f"Không đủ chỗ để re-encode Part {k}: cần ~{part_est/1e9:.1f}GB, còn {free/1e9:.1f}GB"
                        )
                    cmd_fb = [
                        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                        "-ss", str(st), "-to", str(en),
                        "-i", str(video_path),
                        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
                        "-c:a", "aac", "-b:a", "192k",
                        "-movflags", "+faststart",
                        str(out_file)
                    ]
                    r_fb = subprocess.run(
                        cmd_fb, capture_output=True, text=True,
                        encoding="utf-8", errors="replace", creationflags=flags,
                    )
                    fb_err = (r_fb.stderr or "") + "\n" + (r_fb.stdout or "")
                    if r_fb.returncode != 0 or not out_file.exists() or out_file.stat().st_size < 1000:
                        _unlink_quiet(out_file)
                        if _is_disk_full_text(fb_err):
                            raise DiskFullError(
                                f"ffmpeg re-encode Part {k}/{total_k} hết ổ (ENOSPC). "
                                f"stderr: {(r_fb.stderr or '')[:400]}"
                            )
                        raise RuntimeError(
                            f"ffmpeg re-encode Part {k}/{total_k} thất bại (rc={r_fb.returncode}): "
                            f"{(r_fb.stderr or '')[:400]}"
                        )

            results.append({
                **item,
                "file": str(out_file),
                "size_mb": round(out_file.stat().st_size / 1e6, 1),
            })

        # Lưu plan JSON để dùng lại khi cần merge
        manifest_file = out_dir / "split_manifest.json"
        manifest_file.write_text(json.dumps({
            "source_video": str(video_path),
            "total_duration": probe_duration(video_path),
            "target_hours": target_hours,
            "parts": results,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }, ensure_ascii=False, indent=2), encoding="utf-8")

        return results
    except Exception:
        # Fail giữa chừng (chưa đủ part) → dọn orphan GB. Đủ part rồi thì giữ.
        if len(results) < len(plan):
            cleanup_split_parts_dir(out_dir)
        raise


def _hardlink_alias(primary: Path, alias: Path) -> bool:
    """Tạo alias cùng inode với primary. Không bao giờ copy2 (tránh nhân đôi GB)."""
    primary = Path(primary)
    alias = Path(alias)
    if not primary.is_file():
        return False
    try:
        if alias.exists() and os.path.samefile(primary, alias):
            return True
    except OSError:
        pass
    if alias.exists() or alias.is_symlink():
        try:
            alias.unlink()
        except OSError as e:
            print(f"[split_parts] không xoá alias cũ {alias.name}: {e}", flush=True)
            return False
    try:
        os.link(str(primary), str(alias))
        print(f"[split_parts] hardlink {alias.name} ← {primary.name} (cùng 1 bản trên đĩa)", flush=True)
        return True
    except OSError as e:
        print(
            f"[split_parts] hardlink {alias.name} thất bại ({e}) — "
            f"KHÔNG copy; chỉ giữ {primary.name}",
            flush=True,
        )
        return False


def cleanup_split_parts_dir(parts_dir: str | Path) -> None:
    """Xoá thư mục `_split_parts` dở (orphan GB sau fail / ENOSPC)."""
    d = Path(parts_dir)
    if not d.exists():
        return
    try:
        shutil.rmtree(d, ignore_errors=True)
        print(f"[split_parts] Đã xoá partial {d}", flush=True)
    except Exception as e:
        print(f"[split_parts] Không xoá được {d}: {e}", flush=True)


def merge_parts_to_full(part_videos: list[str | Path], out_full_mp4: str | Path) -> Path:
    """
    Nối danh sách các part đã render hoàn chỉnh thành 1 file full (lossless copy 30s).
    """
    out_full_mp4 = Path(out_full_mp4)
    out_full_mp4.parent.mkdir(parents=True, exist_ok=True)
    valid_parts = [Path(p) for p in part_videos if Path(p).is_file()]
    if not valid_parts:
        raise ValueError("Không có file part hợp lệ để nối")

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        list_file = f.name
        for p in valid_parts:
            esc = str(p.resolve()).replace("\\", "/").replace("'", "'\\''")
            f.write(f"file '{esc}'\n")

    try:
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            "-movflags", "+faststart",
            str(out_full_mp4)
        ]
        print(f"[split_parts] Đang ghép {len(valid_parts)} part -> {out_full_mp4.name} (concat copy)...", flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=flags)
        if r.returncode != 0 or not out_full_mp4.exists():
            raise RuntimeError(f"Ghép concat thất bại: {r.stderr}")
        print(f"[split_parts] Ghép thành công: {out_full_mp4.name} ({out_full_mp4.stat().st_size/1e6:.1f} MB)", flush=True)
        return out_full_mp4
    finally:
        try:
            os.unlink(list_file)
        except OSError:
            pass


def split_job_to_subjobs(job_id: str, target_hours: float = DEFAULT_TARGET_HOURS, work_root: str | Path = "work") -> dict:
    """
    Tự động chia một job video dài thành các sub-jobs (Part 1, Part 2...).
    Mỗi sub-job kế thừa thiết lập của job cha và có file video riêng.
    """
    from core.manifest import Manifest
    from engines.render import _find_video

    work_root = Path(work_root)
    work_dir = work_root / job_id
    if not work_dir.is_dir():
        raise FileNotFoundError(f"Không tìm thấy job: {job_id}")

    video = _find_video(work_dir)
    if not video or not video.exists():
        raise FileNotFoundError(f"Job {job_id} chưa có file video nguồn.")

    dur = probe_duration(video)
    if dur < MIN_SPLIT_HOURS * 3600.0:
        return {
            "ok": True,
            "split": False,
            "message": f"Video dài {dur/3600:.2f}h (< {MIN_SPLIT_HOURS}h), không cần chia part.",
            "job_ids": [job_id],
        }

    m_parent = Manifest(work_dir)
    parent_meta = m_parent.data.get("meta") or {}
    parent_title = parent_meta.get("title") or m_parent.data.get("request", {}).get("title") or job_id
    parent_opts = m_parent.data.get("opts") or {}

    parts_dir = work_dir / "_split_parts"
    try:
        parts_info = split_video_to_parts(video, parts_dir, target_hours=target_hours, prefix=f"{job_id}_part")
    except Exception as e:
        # split_video_to_parts đã rmtree partial; ghi rõ ENOSPC vào message
        if isinstance(e, DiskFullError) or _is_disk_full_text(str(e)):
            cleanup_split_parts_dir(parts_dir)
            raise DiskFullError(f"split_job_to_subjobs {job_id}: {e}") from e
        cleanup_split_parts_dir(parts_dir)
        raise

    sub_job_ids = []
    total_parts = len(parts_info)

    for item in parts_info:
        k = item["part"]
        sub_id = f"{job_id}_p{k:02d}"
        sub_dir = work_root / sub_id
        sub_dir.mkdir(parents=True, exist_ok=True)

        # Ưu tiên move (tránh nhân đôi dung lượng); fallback copy
        part_src = Path(item["file"])
        part_dest = sub_dir / part_src.name
        if not part_dest.exists() or part_dest.stat().st_size < 1000:
            try:
                shutil.move(str(part_src), str(part_dest))
            except Exception:
                try:
                    assert_enough_space_for_split(part_src, sub_dir)
                except DiskFullError:
                    cleanup_split_parts_dir(parts_dir)
                    raise
                shutil.copy2(part_src, part_dest)

        # Tạo manifest cho sub-job
        m_sub = Manifest(sub_dir)
        m_sub.data["request"] = {
            "local": True,
            "url": None,
            "title": f"{parent_title} - Phần {k}/{total_parts}",
            "group_id": job_id,
            "group_title": parent_title,
            "group_index": k,
            "group_total": total_parts,
            "part_title": f"Phần {k}/{total_parts}",
            "parent_job_id": job_id,
            "orig_path": str(part_dest),
        }
        m_sub.data["meta"] = {
            **parent_meta,
            "title": f"{parent_title} - Phần {k}/{total_parts}",
            "duration": item["duration"],
        }
        m_sub.data["opts"] = dict(parent_opts)
        # Kế thừa queue_opts của job cha (giọng/ASR/audio…) để xếp hàng part không lệch config
        parent_qopts = dict(m_parent.data.get("queue_opts") or {})
        if parent_qopts:
            m_sub.data["queue_opts"] = parent_qopts
        # Seed TTS — tránh _resolve_voice rơi về list_clone_voices()[0]
        parent_tts = (m_parent.data.get("stages") or {}).get("tts") or {}
        voice = (parent_qopts.get("voice") or parent_tts.get("voice") or parent_opts.get("voice") or "").strip()
        try:
            speed = parent_qopts.get("speed")
            if speed is None:
                speed = parent_tts.get("speed")
            if speed is None:
                speed = parent_opts.get("speed")
            speed_f = float(speed) if speed is not None else None
        except (TypeError, ValueError):
            speed_f = None
        eng = (
            parent_qopts.get("tts_engine") or parent_qopts.get("engine")
            or parent_tts.get("tts_engine") or parent_tts.get("engine")
            or parent_opts.get("tts_engine") or parent_opts.get("engine")
        )
        # Đánh dấu download done trên part (đã có file video)
        st_dl = m_sub.data.setdefault("stages", {}).setdefault("download", {})
        st_dl.update({
            "status": "done",
            "video_path": str(part_dest),
            "updated_at": time.time(),
            "from_split": True,
        })
        m_sub.data["stages"]["download"] = st_dl
        if voice or speed_f or eng:
            tts_seed: dict = {"status": "pending"}
            if voice:
                tts_seed["voice"] = voice
                tts_seed["cur_text"] = f"kế thừa giọng {voice} từ parent"
            if speed_f and speed_f > 0:
                tts_seed["speed"] = speed_f
            if eng:
                tts_seed["tts_engine"] = eng
                tts_seed["engine"] = eng
            m_sub.data["stages"]["tts"] = tts_seed
            try:
                cfg = {k: tts_seed[k] for k in ("voice", "speed", "tts_engine", "engine") if k in tts_seed}
                (sub_dir / "tts_config.json").write_text(
                    json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8",
                )
            except OSError:
                pass
        m_sub.save()
        sub_job_ids.append(sub_id)

    # Đánh dấu job cha
    m_parent.data.setdefault("split_info", {})
    m_parent.data["split_info"] = {
        "status": "split_done",
        "total_parts": total_parts,
        "sub_job_ids": sub_job_ids,
        "parts": parts_info,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "auto": bool((m_parent.data.get("split_info") or {}).get("auto")),
    }
    # Parent không chạy ASR/TTS/mux — chờ part + merge
    st_dl = m_parent.data.setdefault("stages", {}).setdefault("download", {})
    if st_dl.get("status") != "done":
        st_dl.update({"status": "done", "updated_at": time.time(), "note": "parent_after_split"})
        m_parent.data["stages"]["download"] = st_dl
    m_parent.save()

    print(f"[split_parts] Job {job_id} đã được chia thành {total_parts} sub-jobs: {', '.join(sub_job_ids)}", flush=True)
    return {
        "ok": True,
        "split": True,
        "total_parts": total_parts,
        "parent_job_id": job_id,
        "sub_job_ids": sub_job_ids,
        "parts": parts_info,
    }


def merge_job_parts(job_id: str, work_root: str | Path = "work") -> dict:
    """
    Kiểm tra các sub-job của job_id, nếu tất cả đã render xong thì ghép thành output_full.mp4.
    """
    from core.manifest import Manifest

    work_root = Path(work_root)
    work_dir = work_root / job_id
    if not work_dir.is_dir():
        raise FileNotFoundError(f"Không tìm thấy job: {job_id}")

    m_parent = Manifest(work_dir)
    split_info = m_parent.data.get("split_info") or {}
    sub_ids = split_info.get("sub_job_ids") or []

    if not sub_ids:
        # Tìm tự động các sub-job theo format {job_id}_p*
        sub_ids = sorted([
            p.name for p in work_root.glob(f"{job_id}_p[0-9][0-9]")
            if p.is_dir()
        ])

    if not sub_ids:
        raise ValueError(f"Job {job_id} không có sub-jobs nào để ghép.")

    rendered_parts: list[Path] = []
    missing_parts: list[str] = []

    for sid in sub_ids:
        s_dir = work_root / sid
        m_sub = Manifest(s_dir)
        out_mp4 = s_dir / "output.mp4"
        if out_mp4.exists() and out_mp4.stat().st_size > 100_000 and m_sub.is_done("mux"):
            rendered_parts.append(out_mp4)
        else:
            missing_parts.append(sid)

    if missing_parts:
        return {
            "ok": False,
            "ready": False,
            "message": f"Chưa thể ghép vì còn {len(missing_parts)} part chưa render xong: {', '.join(missing_parts)}",
            "missing_parts": missing_parts,
            "rendered_parts": [p.name for p in rendered_parts],
        }

    # Một lần ghi → output.mp4; output_full chỉ hardlink (không copy2)
    final_output = work_dir / "output.mp4"
    full_alias = work_dir / "output_full.mp4"
    for p in (final_output, full_alias):
        if p.exists() or p.is_symlink():
            try:
                p.unlink()
            except OSError as e:
                print(f"[split_parts] không xoá {p.name} cũ: {e}", flush=True)
    merge_parts_to_full(rendered_parts, final_output)
    linked = _hardlink_alias(final_output, full_alias)
    full_for_manifest = full_alias if linked and full_alias.exists() else final_output

    now = time.time()
    stages = m_parent.data.setdefault("stages", {})
    for name in ("download", "asr", "translate", "tts", "mux"):
        st = stages.setdefault(name, {})
        st.update({"status": "done", "updated_at": now, "from_split_merge": True})
        if name == "mux":
            st.update({
                "output_path": str(final_output),
                "output_full_path": str(full_for_manifest),
                "is_full_merged": True,
                "n_parts": len(rendered_parts),
                "hardlink_alias": bool(linked),
            })
        stages[name] = st
    info = m_parent.data.setdefault("split_info", {})
    info["status"] = "merged"
    info["merged_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    info["output_path"] = str(final_output)
    m_parent.save()

    parts_dir = work_dir / "_split_parts"
    if parts_dir.is_dir():
        cleanup_split_parts_dir(parts_dir)

    print(
        f"[split_parts] Job {job_id}: đã ghép {len(rendered_parts)} part → {final_output.name} "
        f"({final_output.stat().st_size/1e6:.1f} MB; hardlink={bool(linked)})",
        flush=True,
    )
    return {
        "ok": True,
        "ready": True,
        "output_path": str(final_output),
        "output_full_path": str(full_for_manifest),
        "hardlink_alias": bool(linked),
        "size_mb": round(final_output.stat().st_size / 1e6, 1),
        "n_parts": len(rendered_parts),
    }


def is_split_subjob(work_dir: str | Path) -> bool:
    """Part đã tách (…_p01) — không auto-split lần nữa."""
    try:
        from core.manifest import Manifest
        req = (Manifest(work_dir).data.get("request") or {})
        if req.get("parent_job_id"):
            return True
    except Exception:  # noqa: BLE001
        pass
    name = Path(work_dir).name
    return bool(re.search(r"_p\d{2}$", name))


def maybe_auto_split_job(
    job_id: str,
    *,
    work_root: str | Path = "work",
    enabled: bool = True,
    target_hours: float = DEFAULT_TARGET_HOURS,
    min_hours: float | None = None,
) -> dict:
    """
    Tự detect thời lượng video sau khi có source:
    - < min_hours → không chia, chạy job thường
    - ≥ min_hours → chia part + trả sub_job_ids (caller xếp hàng)
    - Đã là sub-job / đã split → không làm lại
    """
    if not enabled:
        return {"ok": True, "split": False, "skipped": "auto_split_off", "job_ids": [job_id]}

    work_root = Path(work_root)
    work_dir = work_root / job_id
    if not work_dir.is_dir():
        return {"ok": False, "split": False, "error": f"không tìm thấy job {job_id}"}

    if is_split_subjob(work_dir):
        return {"ok": True, "split": False, "skipped": "already_subjob", "job_ids": [job_id]}

    from core.manifest import Manifest
    m = Manifest(work_dir)
    info = m.data.get("split_info") or {}
    existing = list(info.get("sub_job_ids") or [])
    # Đã ghép Full → không chia / không xếp lại part
    if info.get("status") == "merged":
        return {
            "ok": True,
            "split": False,
            "skipped": "already_merged",
            "parent_job_id": job_id,
            "sub_job_ids": existing,
            "job_ids": [job_id],
        }
    if info.get("status") == "split_done" and existing:
        # Mọi part đã wired-done → không kích re-queue (chống TTS/mux lại)
        try:
            from core.job_queue import is_wired_done
            pending = [s for s in existing if not is_wired_done(work_root / s)]
        except Exception:  # noqa: BLE001
            pending = list(existing)
        if not pending:
            return {
                "ok": True,
                "split": False,
                "skipped": "parts_already_done",
                "already": True,
                "total_parts": len(existing),
                "parent_job_id": job_id,
                "sub_job_ids": existing,
                "job_ids": existing,
            }
        return {
            "ok": True,
            "split": True,
            "already": True,
            "total_parts": len(existing),
            "parent_job_id": job_id,
            "sub_job_ids": pending,  # chỉ part còn thiếu
            "job_ids": pending,
            "all_sub_job_ids": existing,
        }

    from engines.render import _find_video
    video = _find_video(work_dir)
    if not video or not video.exists():
        return {"ok": True, "split": False, "skipped": "no_video", "job_ids": [job_id]}

    thr = float(min_hours if min_hours is not None else MIN_SPLIT_HOURS)
    dur = probe_duration(video)
    if dur <= 0:
        return {"ok": True, "split": False, "skipped": "probe_failed", "duration_sec": dur, "job_ids": [job_id]}
    if dur < thr * 3600.0:
        return {
            "ok": True,
            "split": False,
            "skipped": "under_threshold",
            "duration_sec": dur,
            "duration_hours": round(dur / 3600.0, 2),
            "min_hours": thr,
            "job_ids": [job_id],
        }

    m.data.setdefault("split_info", {})["auto"] = True
    m.save()
    print(
        f"[auto_split] {job_id}: phát hiện video {dur/3600:.2f}h ≥ {thr}h → chia part "
        f"(target {target_hours}h/part)",
        flush=True,
    )
    res = split_job_to_subjobs(job_id, target_hours=float(target_hours), work_root=work_root)
    res["duration_sec"] = dur
    res["duration_hours"] = round(dur / 3600.0, 2)
    res["auto"] = True
    if res.get("sub_job_ids"):
        res["job_ids"] = list(res["sub_job_ids"])
    return res


def try_auto_merge_parent(
    job_id: str,
    *,
    work_root: str | Path = "work",
    enabled: bool = True,
) -> dict | None:
    """Sau khi một part mux xong: nếu mọi part done → merge output_full trên job cha."""
    if not enabled:
        return None
    work_root = Path(work_root)
    work_dir = work_root / job_id
    if not work_dir.is_dir():
        return None
    try:
        from core.manifest import Manifest
        req = (Manifest(work_dir).data.get("request") or {})
        parent = str(req.get("parent_job_id") or "").strip()
        if not parent:
            return None
        print(f"[auto_merge] part {job_id} xong → kiểm tra merge parent {parent}", flush=True)
        return merge_job_parts(parent, work_root=work_root)
    except Exception as e:  # noqa: BLE001
        print(f"[auto_merge] {job_id}: {e}", flush=True)
        return {"ok": False, "error": str(e)}


def main():
    ap = argparse.ArgumentParser(description="Chia video dài thành các part chuẩn 2-2.5h hoặc ghép lại thành Full.")
    ap.add_argument("video", nargs="?", default=None, help="Đường dẫn video cần chia")
    ap.add_argument("--target-hours", type=float, default=DEFAULT_TARGET_HOURS, help="Thời lượng mục tiêu mỗi part (mặc định 2.5h)")
    ap.add_argument("--out-dir", default=None, help="Thư mục xuất các part")
    ap.add_argument("--merge", nargs="+", default=None, help="Nối danh sách các part video lại")
    ap.add_argument("--out-full", default=None, help="Đường dẫn file full xuất ra khi dùng --merge")
    args = ap.parse_args()

    if args.merge:
        out = args.out_full or "output_full.mp4"
        merge_parts_to_full(args.merge, out)
        return

    if not args.video:
        ap.print_help()
        return

    v = Path(args.video)
    out_dir = Path(args.out_dir) if args.out_dir else v.parent / f"{v.stem}_parts"
    res = split_video_to_parts(v, out_dir, target_hours=args.target_hours)
    print("\n=== KẾT QUẢ PHÂN CHIA PART ===")
    for r in res:
        print(f"Part {r['part']}/{r['total_parts']}: {r['file']} ({r['duration']/3600:.2f}h, {r['size_mb']}MB)")


if __name__ == "__main__":
    main()
