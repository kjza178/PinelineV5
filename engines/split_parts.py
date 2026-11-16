"""
split_parts.py — Tự động tính toán và chia video dài (3h-12h+) thành các Part 2-2.5h
để chạy ASR/TTS/Render độc lập chống lệch time, sau đó ghép concat lại thành bản Full.
"""
from __future__ import annotations
import sys as _sync_sys  # sync_from_v2: bootstrap — chạy trực tiếp vẫn import được core.*/engines.*
from pathlib import Path as _SyncP
_SYNC_ROOT = str(_SyncP(__file__).resolve().parents[1])
if _SYNC_ROOT not in _sync_sys.path:
    _sync_sys.path.insert(0, _SYNC_ROOT)

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


# fix 2026-11-13 agentS: Full 60892cc63cb7 ghép `-c copy` hỏng NAL chỉ phát hiện SAU (người xem).
# Nay ghép xong → giải mã thử ±30 s quanh MỖI mối nối (+ đếm cảnh báo DTS); lỗi → ghép lại «regen»
# (genpts + SPS/PPS trong luồng); vẫn lỗi → báo lỗi rõ, KHÔNG thay Full cũ.
MERGE_JOINT_WINDOW_SEC = 30.0
_DECODE_ERR_RE = re.compile(
    r"invalid nal|error while decoding|non-existing pps|decode_slice_header|no frame!|concealing|"
    r"missing reference|corrupt|illegal|invalid data found|error at mb|damaged|"
    r"sps_id|pps_id|top block unavailable|left block unavailable",
    re.I,
)
_DTS_WARN_RE = re.compile(r"non[- ]monoton", re.I)


def _concat_run(valid_parts: list[Path], out_full_mp4: Path, mode: str = "copy") -> tuple[int, str]:
    """mode=copy: concat demuxer -c copy (cũ). mode=regen: +genpts, SPS/PPS trong luồng, make_zero."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        list_file = f.name
        for p in valid_parts:
            esc = str(Path(p).resolve()).replace("\\", "/").replace("'", "'\\''")
            f.write(f"file '{esc}'\n")
    try:
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        cmd = ["ffmpeg", "-y", "-hide_banner", "-nostdin", "-loglevel", "warning"]
        if mode == "regen":
            cmd += ["-fflags", "+genpts"]
        cmd += ["-f", "concat", "-safe", "0", "-i", list_file, "-map", "0", "-c", "copy"]
        if mode == "regen":
            vcodec = _probe_vcodec(valid_parts[0])
            if vcodec in ("h264", "hevc"):
                cmd += ["-bsf:v", f"{vcodec}_mp4toannexb"]
            cmd += ["-avoid_negative_ts", "make_zero"]
        cmd += ["-movflags", "+faststart", str(out_full_mp4)]
        print(f"[split_parts] Đang ghép {len(valid_parts)} part -> {out_full_mp4.name} (concat {mode})...", flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=flags)
        return r.returncode, (r.stderr or "")
    finally:
        try:
            os.unlink(list_file)
        except OSError:
            pass


def _probe_vcodec(path: str | Path) -> str:
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name",
             "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=flags,
        )
        return (r.stdout or "").strip().splitlines()[0].strip() if (r.stdout or "").strip() else ""
    except Exception:  # noqa: BLE001
        return ""


def _decode_window(full_mp4: Path, t0: float, dur: float) -> tuple[int, str]:
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    cmd = [
        "ffmpeg", "-nostdin", "-hide_banner", "-v", "warning",
        "-ss", f"{max(0.0, t0):.3f}", "-i", str(full_mp4), "-t", f"{dur:.3f}",
        "-map", "0:v:0?", "-map", "0:a:0?", "-f", "null", "-",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=flags)
    return r.returncode, (r.stderr or "")


def check_merge_joints(full_mp4: str | Path, joints: list[float],
                       window: float = MERGE_JOINT_WINDOW_SEC) -> dict:
    """Giải mã thử [t-window, t+window] quanh mỗi mối nối. ok=False nếu có lỗi giải mã (DTS chỉ cảnh báo)."""
    full_mp4 = Path(full_mp4)
    out = {"ok": True, "joints": [], "decode_errors": 0, "dts_warnings": 0}
    for t in joints:
        rc, err = _decode_window(full_mp4, float(t) - window, 2.0 * window)
        lines = [ln.strip() for ln in err.splitlines() if ln.strip()]
        dts = [ln for ln in lines if _DTS_WARN_RE.search(ln)]
        errs = [ln for ln in lines if _DECODE_ERR_RE.search(ln) and not _DTS_WARN_RE.search(ln)]
        ok = rc == 0 and not errs
        out["joints"].append({
            "t": round(float(t), 3), "ok": ok, "rc": rc,
            "n_errors": len(errs), "dts_warnings": len(dts), "errors": errs[:5],
        })
        out["decode_errors"] += len(errs)
        out["dts_warnings"] += len(dts)
        if not ok:
            out["ok"] = False
    return out


def merge_parts_checked(part_videos: list[str | Path], out_full_mp4: str | Path, *,
                        verify: bool = True, window: float = MERGE_JOINT_WINDOW_SEC) -> dict:
    """Ghép + kiểm mối nối. Trả {"ok", "mode", "joints", "attempts", "message"}; ok=False → đã xoá out."""
    out_full_mp4 = Path(out_full_mp4)
    out_full_mp4.parent.mkdir(parents=True, exist_ok=True)
    valid_parts = [Path(p) for p in part_videos if Path(p).is_file()]
    if not valid_parts:
        raise ValueError("Không có file part hợp lệ để nối")
    joints: list[float] = []
    acc = 0.0
    for p in valid_parts[:-1]:
        acc += probe_duration(p)
        joints.append(round(acc, 3))
    attempts: list[dict] = []
    for mode in ("copy", "regen"):
        _unlink_quiet(out_full_mp4)
        rc, err = _concat_run(valid_parts, out_full_mp4, mode)
        n_dts = sum(1 for ln in err.splitlines() if _DTS_WARN_RE.search(ln))
        if rc != 0 or not out_full_mp4.exists() or out_full_mp4.stat().st_size < 1000:
            attempts.append({"mode": mode, "ok": False, "rc": rc, "error": err.strip()[-400:]})
            print(f"[split_parts] Ghép ({mode}) thất bại rc={rc}: {err.strip()[-300:]}", flush=True)
            continue
        chk = check_merge_joints(out_full_mp4, joints, window) if verify else {"ok": True, "joints": []}
        attempts.append({"mode": mode, "ok": bool(chk["ok"]), "concat_dts_warnings": n_dts,
                         "joints": chk.get("joints") or []})
        if chk["ok"]:
            if n_dts or any(j.get("dts_warnings") for j in chk.get("joints") or []):
                print(f"[split_parts] CẢNH BÁO: {n_dts} dòng DTS không tăng đơn điệu lúc ghép ({mode}) — "
                      f"giải mã mối nối vẫn OK", flush=True)
            print(f"[split_parts] Ghép thành công ({mode}): {out_full_mp4.name} "
                  f"({out_full_mp4.stat().st_size/1e6:.1f} MB), {len(joints)} mối nối giải mã OK", flush=True)
            return {"ok": True, "mode": mode, "joints": chk.get("joints") or [],
                    "concat_dts_warnings": n_dts, "attempts": attempts, "output": str(out_full_mp4)}
        bad = [j["t"] for j in chk["joints"] if not j["ok"]]
        print(f"[split_parts] Mối nối LỖI giải mã ({mode}) tại {bad}s — "
              + ("thử ghép lại an toàn (regen pts + SPS/PPS)" if mode == "copy" else "bỏ"), flush=True)
    _unlink_quiet(out_full_mp4)
    bad_all = sorted({j["t"] for a in attempts for j in (a.get("joints") or []) if not j.get("ok")})
    return {
        "ok": False, "mode": None, "attempts": attempts, "joints": [],
        "message": ("Ghép Full LỖI: mối nối giải mã hỏng" + (f" tại {bad_all}s" if bad_all else "")
                    + " sau cả concat copy và regen — không thay Full cũ; cần render lại part "
                      "hoặc re-encode đoạn quanh mối nối (xem split_info.merge_check)"),
    }


def merge_parts_to_full(part_videos: list[str | Path], out_full_mp4: str | Path) -> Path:
    """
    Nối danh sách các part đã render hoàn chỉnh thành 1 file full (concat copy) + kiểm mối nối.
    """
    out_full_mp4 = Path(out_full_mp4)
    rep = merge_parts_checked(part_videos, out_full_mp4)
    if not rep.get("ok"):
        raise RuntimeError(rep.get("message") or "Ghép concat thất bại")
    return out_full_mp4


def _merge_check_summary(rep: dict) -> dict:
    return {
        "ok": bool(rep.get("ok")),
        "mode": rep.get("mode"),
        "concat_dts_warnings": int(rep.get("concat_dts_warnings") or 0),
        "joints": [{k: j.get(k) for k in ("t", "ok", "n_errors", "dts_warnings")} for j in rep.get("joints") or []],
        "attempts": [a.get("mode") for a in rep.get("attempts") or []],
        "checked_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def _source_sig(video: Path, dur: float) -> dict:
    try:
        st = Path(video).stat()
        return {"size": int(st.st_size), "mtime": int(st.st_mtime), "duration": round(float(dur), 3)}
    except OSError:
        return {"duration": round(float(dur), 3)}


def _sig_match(a: dict | None, b: dict | None) -> bool:
    if not a or not b:
        return False
    if a.get("size") and b.get("size") and int(a["size"]) != int(b["size"]):
        return False
    return abs(float(a.get("duration") or 0) - float(b.get("duration") or 0)) <= 1.0


def _part_dur_tol(d: float) -> float:
    # cắt -c copy lệch theo keyframe (vài giây); kế hoạch khác (điểm lặng khác) lệch xa hơn nhiều
    return max(10.0, 0.002 * float(d or 0))


def find_reusable_parts(job_id: str, work_root: Path, video: Path, dur: float,
                        target_hours: float = DEFAULT_TARGET_HOURS) -> list[dict] | None:
    """agentS 2026-11-13: part đã cắt đúng kế hoạch (cùng nguồn/độ dài) → trả parts_info để DÙNG LẠI.
    Nguồn kế hoạch: split_info cũ (nếu cùng nguồn) hoặc tính lại smart plan khi split_info bị xoá.
    None = phải cắt mới."""
    from core.manifest import Manifest

    work_root = Path(work_root)
    if not (work_root / f"{job_id}_p01").is_dir():
        return None
    try:
        si = Manifest(work_root / job_id).data.get("split_info") or {}
    except Exception:  # noqa: BLE001
        si = {}
    sig_now = _source_sig(video, dur)
    plan = None
    if si.get("parts") and (not si.get("source_sig") or _sig_match(si.get("source_sig"), sig_now)):
        plan = [{k: p.get(k) for k in ("part", "total_parts", "start", "end", "duration", "smart_cut")}
                for p in si["parts"]]
    if plan is None:
        try:
            plan = compute_smart_plan(video, target_hours=target_hours)
        except Exception as e:  # noqa: BLE001
            print(f"[split_parts] {job_id}: không tính lại được kế hoạch để dùng lại part: {e}", flush=True)
            return None
    if len(plan) < 2 or abs(float(plan[-1].get("end") or 0) - float(dur)) > 2.0:
        return None
    out = []
    for item in plan:
        k, n = int(item["part"]), int(item["total_parts"])
        sub_dir = work_root / f"{job_id}_p{k:02d}"
        f = sub_dir / f"{job_id}_part_{k:02d}_of_{n:02d}.mp4"
        if not f.is_file() or f.stat().st_size < 1000:
            return None
        try:
            req = Manifest(sub_dir).data.get("request") or {} if (sub_dir / "manifest.json").is_file() else {}
        except Exception:  # noqa: BLE001
            req = {}
        if req.get("parent_job_id") and req.get("parent_job_id") != job_id:
            return None
        d_part = probe_duration(f)
        if d_part <= 0 or abs(d_part - float(item["duration"])) > _part_dur_tol(item["duration"]):
            print(f"[split_parts] {job_id}: part {k} lệch kế hoạch ({d_part:.1f}s vs {item['duration']}s) "
                  f"— cắt lại", flush=True)
            return None
        out.append({**item, "file": str(f), "size_mb": round(f.stat().st_size / 1e6, 1), "reused": True})
    return out


def split_job_to_subjobs(job_id: str, target_hours: float = DEFAULT_TARGET_HOURS, work_root: str | Path = "work",
                         reset_parts: bool = False) -> dict:
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
    old_si = dict(m_parent.data.get("split_info") or {})
    # agentS: split_info bị xoá / lệnh ASR parent → part đã có đúng kế hoạch thì DÙNG LẠI (không cắt 10 GB,
    # không reset stage part). reset_parts=True (force rõ ràng) → cắt mới như cũ.
    reused = None if reset_parts else find_reusable_parts(job_id, work_root, video, dur, target_hours)
    try:
        if reused:
            print(f"[split_parts] {job_id}: DÙNG LẠI {len(reused)} part đã cắt đúng kế hoạch (không cắt lại)",
                  flush=True)
            parts_info = reused
        else:
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
        if item.get("reused"):
            pass
        elif not part_dest.exists() or part_dest.stat().st_size < 1000:
            try:
                shutil.move(str(part_src), str(part_dest))
            except Exception:
                try:
                    assert_enough_space_for_split(part_src, sub_dir)
                except DiskFullError:
                    cleanup_split_parts_dir(parts_dir)
                    raise
                shutil.copy2(part_src, part_dest)

        # Tên Lib/poster: kế thừa parent — KHÔNG dùng folder work/<sub_id>
        parent_hg = ""
        try:
            import core.film_db as _fdb
            parent_hg = _fdb.derive_hg_name(
                job_id,
                m_parent.data.get("request") or {},
                parent_title,
            )
        except Exception:
            parent_hg = ""
        if not parent_hg:
            try:
                preq = m_parent.data.get("request") or {}
                if preq.get("orig_path"):
                    parent_hg = Path(preq["orig_path"]).parent.name
            except Exception:
                parent_hg = ""
            if not parent_hg or parent_hg.lower() in {
                "downloads", "download", "work", "tmp", "temp", "_split_parts",
            }:
                parent_hg = parent_title

        # Tạo manifest cho sub-job
        m_sub = Manifest(sub_dir)
        _old_st = m_sub.data.get("stages") or {}
        # agentS: part dùng lại + đã có kết quả → GIỮ stage (download/tts…), chỉ bổ sung khoá thiếu
        keep_results = bool(item.get("reused")) and not reset_parts and any(
            (_old_st.get(s) or {}).get("status") == "done" for s in ("asr", "translate", "tts", "mux"))
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
            "hg_name": parent_hg,
        }
        m_sub.data["meta"] = {
            **parent_meta,
            "title": f"{parent_title} - Phần {k}/{total_parts}",
            "duration": item["duration"],
        }
        m_sub.data["opts"] = dict(parent_opts)
        qo = dict(m_parent.data.get("queue_opts") or {})
        m_sub.data["queue_opts"] = qo
        # Seed TTS từ parent/queue_opts — tránh _resolve_voice rơi về list_clone_voices()[0]
        parent_tts = (m_parent.data.get("stages") or {}).get("tts") or {}
        voice = (qo.get("voice") or parent_tts.get("voice") or parent_opts.get("voice") or "").strip()
        try:
            speed = qo.get("speed")
            if speed is None:
                speed = parent_tts.get("speed")
            if speed is None:
                speed = parent_opts.get("speed")
            speed_f = float(speed) if speed is not None else None
        except (TypeError, ValueError):
            speed_f = None
        eng = (
            qo.get("tts_engine") or qo.get("engine")
            or parent_tts.get("tts_engine") or parent_tts.get("engine")
            or parent_opts.get("tts_engine") or parent_opts.get("engine")
        )
        tts_seed: dict = {"status": "pending"}
        if voice:
            tts_seed["voice"] = voice
            tts_seed["cur_text"] = f"kế thừa giọng {voice} từ parent"
        if speed_f and speed_f > 0:
            tts_seed["speed"] = speed_f
        if eng:
            tts_seed["tts_engine"] = eng
            tts_seed["engine"] = eng
        stages = m_sub.data.setdefault("stages", {})
        _old_dl = stages.get("download") or {}
        if not (keep_results and _old_dl.get("status") == "done"
                and Path(str(_old_dl.get("video_path") or "")).name == part_dest.name):
            stages["download"] = {
                "status": "done",
                "video_path": str(part_dest),
                "duration_sec": item["duration"],
                "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            try:   # agentK 2026-11-12: part cắt từ nguồn đã kiểm/chuẩn hoá → kế thừa; không thì chờ kiểm
                from engines.source_preflight import inherit_payload
                stages["download"].update(inherit_payload(m_parent.stage("download") or {}, job_id))
            except Exception:  # noqa: BLE001
                pass
        if keep_results and (voice or speed_f or eng):
            _tts_old = dict(stages.get("tts") or {})
            for _k, _v in tts_seed.items():
                if _k not in ("status", "cur_text"):
                    _tts_old.setdefault(_k, _v)
            _tts_old.setdefault("status", "pending")
            stages["tts"] = _tts_old
            if not (sub_dir / "tts_config.json").is_file():
                try:
                    cfg = {k: tts_seed[k] for k in ("voice", "speed", "tts_engine", "engine") if k in tts_seed}
                    (sub_dir / "tts_config.json").write_text(
                        json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8",
                    )
                except OSError:
                    pass
        elif voice or speed_f or eng:
            stages["tts"] = tts_seed
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
    new_si = {
        "status": "split_done",
        "total_parts": total_parts,
        "sub_job_ids": sub_job_ids,
        "parts": parts_info,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source_sig": _source_sig(video, dur),
    }
    if reused:
        new_si["reused_parts"] = True
        # đã ghép Full trước đó (cùng part) → giữ dấu merged, không làm parent «chưa ghép»
        for k_keep in ("status", "merged_at", "output_path", "merge_check"):
            if old_si.get("status") == "merged" and k_keep in old_si:
                new_si[k_keep] = old_si[k_keep]
    m_parent.data["split_info"] = new_si
    m_parent.save()

    print(f"[split_parts] Job {job_id} đã được chia thành {total_parts} sub-jobs: {', '.join(sub_job_ids)}", flush=True)
    return {
        "ok": True,
        "split": True,
        "total_parts": total_parts,
        "parent_job_id": job_id,
        "sub_job_ids": sub_job_ids,
        "parts": parts_info,
        "reused": bool(reused),
    }


def merge_job_parts(job_id: str, work_root: str | Path = "work", force: bool = False) -> dict:
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

    # Một lần ghi → output.mp4; output_full.mp4 chỉ hardlink (KHÔNG copy2 nhân đôi GB)
    parent_output = work_dir / "output.mp4"
    full_alias = work_dir / "output_full.mp4"

    # agentS: đã ghép + không part nào render lại sau Full → KHÔNG ghép đè (chống vòng chạy lại đè Full)
    existing_full = full_alias if full_alias.is_file() else parent_output
    if (not force and str(split_info.get("status") or "").lower() == "merged"
            and existing_full.is_file() and existing_full.stat().st_size > 1_000_000):
        try:
            full_mt = existing_full.stat().st_mtime
            newer = [p.parent.name for p in rendered_parts if p.stat().st_mtime > full_mt]
        except OSError:
            newer = ["?"]
        if not newer:
            print(f"[split_parts] {job_id}: Full đã ghép, part không đổi — KHÔNG ghép lại", flush=True)
            return {
                "ok": True, "ready": True, "skipped": "already_merged",
                "output_path": str(existing_full), "output_full_path": str(existing_full),
                "size_mb": round(existing_full.stat().st_size / 1e6, 1), "n_parts": len(rendered_parts),
            }

    # agentS: ghép ra file TẠM + kiểm mối nối; chỉ thay Full cũ khi bản mới đạt
    tmp_out = work_dir / "output.merging.mp4"
    rep_merge = merge_parts_checked(rendered_parts, tmp_out)
    if not rep_merge.get("ok"):
        try:
            info_f = m_parent.data.setdefault("split_info", {})
            info_f["merge_check"] = _merge_check_summary(rep_merge)
            m_parent.save()
        except Exception:  # noqa: BLE001
            pass
        return {"ok": False, "ready": True, "message": rep_merge.get("message"),
                "merge_check": _merge_check_summary(rep_merge)}
    if full_alias.exists() or full_alias.is_symlink():
        try:
            full_alias.unlink()
        except OSError as e:
            print(f"[split_parts] không xoá {full_alias.name} cũ: {e}", flush=True)
    try:
        os.replace(str(tmp_out), str(parent_output))
    except OSError as e:
        return {"ok": False, "ready": True,
                "message": f"Ghép xong ({tmp_out.name}) nhưng không thay được {parent_output.name}: {e}",
                "merge_check": _merge_check_summary(rep_merge)}
    linked = _hardlink_alias(parent_output, full_alias)
    final = parent_output if parent_output.exists() else full_alias
    full_for_manifest = full_alias if linked and full_alias.exists() else final

    # Job cha không tự ASR/dịch/TTS — đánh done toàn bộ stage wired để UI/queue
    # không báo «pipeline kết thúc nhưng output chưa hoàn chỉnh» / failed.
    now = time.time()
    stages = m_parent.data.setdefault("stages", {})
    for name in ("download", "asr", "translate", "tts", "mux"):
        st = stages.setdefault(name, {})
        st.pop("error", None)
        st.pop("last_error", None)
        st.update({
            "status": "done",
            "updated_at": now,
            "from_split_merge": True,
        })
        if name == "mux":
            st.update({
                "output_path": str(final),
                "output_full_path": str(full_for_manifest),
                "is_full_merged": True,
                "n_parts": len(rendered_parts),
                "progress": 100,
                "cur_text": f"Hoàn tất bản Full ({len(rendered_parts)} parts ghép lại) ✓",
                "hardlink_alias": bool(linked),
            })
        stages[name] = st
    info = m_parent.data.setdefault("split_info", {})
    info["status"] = "merged"
    info["merged_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    info["output_path"] = str(final)
    info["merge_check"] = _merge_check_summary(rep_merge)
    stages["mux"]["merge_check"] = info["merge_check"]
    m_parent.save()

    # Dọn cắt tạm — không còn cần sau merge
    parts_dir = work_dir / "_split_parts"
    if parts_dir.is_dir():
        cleanup_split_parts_dir(parts_dir)

    return {
        "ok": True,
        "ready": True,
        "output_path": str(final),
        "output_full_path": str(full_for_manifest),
        "hardlink_alias": bool(linked),
        "size_mb": round(final.stat().st_size / 1e6, 1),
        "n_parts": len(rendered_parts),
        "merge_check": info["merge_check"],
    }


def merge_subjob_asr_to_parent(job_id: str, work_root: str | Path = "work") -> dict:
    """
    Gộp kết quả ASR (asr.json và sub.zh.srt) của các sub-job về job cha.
    Tự động cộng dồn time offset của từng part để mốc thời gian khớp 100% với video cha.
    """
    from core.manifest import Manifest

    work_root = Path(work_root)
    work_dir = work_root / job_id
    if not work_dir.is_dir():
        raise FileNotFoundError(f"Không tìm thấy job: {job_id}")

    m_parent = Manifest(work_dir)
    split_info = m_parent.data.get("split_info") or {}
    parts_meta = split_info.get("parts") or []
    sub_ids = split_info.get("sub_job_ids") or []

    if not sub_ids:
        sub_ids = sorted([p.name for p in work_root.glob(f"{job_id}_p[0-9][0-9]") if p.is_dir()])

    if not sub_ids:
        raise ValueError(f"Job {job_id} không có sub-jobs nào để gộp ASR.")

    # Tạo map offset cho từng part
    part_offsets: dict[str, float] = {}
    for p_info in parts_meta:
        k = p_info.get("part", 1)
        sub_id = f"{job_id}_p{k:02d}"
        part_offsets[sub_id] = float(p_info.get("start", 0.0))

    all_segments = []
    missing_asr = []

    for idx, sid in enumerate(sub_ids):
        s_dir = work_root / sid
        asr_file = s_dir / "asr.json"
        if not asr_file.exists():
            missing_asr.append(sid)
            continue

        offset = part_offsets.get(sid, 0.0)
        try:
            segs = json.loads(asr_file.read_text(encoding="utf-8"))
            if isinstance(segs, list):
                for s in segs:
                    st = float(s.get("start", 0.0)) + offset
                    en = float(s.get("end", 0.0)) + offset
                    seg_copy = dict(s)
                    seg_copy["start"] = round(st, 3)
                    seg_copy["end"] = round(en, 3)
                    all_segments.append(seg_copy)
        except Exception as e:
            print(f"[split_parts] Lỗi đọc ASR sub-job {sid}: {e}", flush=True)
            missing_asr.append(sid)

    if missing_asr:
        return {
            "ok": False,
            "message": f"Chưa thể gộp ASR vì còn các part chưa có asr.json: {', '.join(missing_asr)}",
            "missing_parts": missing_asr,
        }

    # Sắp xếp lại theo thời gian start
    all_segments.sort(key=lambda x: x.get("start", 0.0))

    # Ghi asr.json cho job cha
    parent_asr_path = work_dir / "asr.json"
    parent_asr_path.write_text(json.dumps(all_segments, ensure_ascii=False, indent=2), encoding="utf-8")

    # Tạo sub.zh.srt cho job cha
    def _sec_to_srt_time(sec: float) -> str:
        ms = int(round((sec - int(sec)) * 1000))
        s = int(sec)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    srt_lines = []
    for i, s in enumerate(all_segments, 1):
        t_st = _sec_to_srt_time(float(s.get("start", 0.0)))
        t_en = _sec_to_srt_time(float(s.get("end", 0.0)))
        txt = (s.get("text") or "").strip()
        srt_lines.append(f"{i}\n{t_st} --> {t_en}\n{txt}\n")

    parent_srt_path = work_dir / "sub.zh.srt"
    parent_srt_path.write_text("\n".join(srt_lines), encoding="utf-8")

    # Đánh dấu stage asr của job cha xong
    m_parent.data.setdefault("stages", {})["asr"] = {
        "status": "done",
        "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_segments": len(all_segments),
        "from_split_parts": len(sub_ids),
    }
    m_parent.save()

    print(f"[split_parts] Đã gộp ASR {len(sub_ids)} part ({len(all_segments)} câu) về job cha {job_id} -> asr.json & sub.zh.srt", flush=True)
    return {
        "ok": True,
        "total_segments": len(all_segments),
        "parts_merged": len(sub_ids),
        "asr_path": str(parent_asr_path),
    }


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
