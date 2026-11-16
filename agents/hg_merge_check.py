"""hg_merge_check.py — kiểm tra + chuẩn hoá các tập TRƯỚC khi gộp, và kiểm file SAU khi gộp (2026-11-16).

Vì sao: gộp `-c copy` thẳng các tập tải về cho ra nhiều file gộp hỏng — tập tải cụt / không đọc được, tập lệch
độ phân giải / fps / codec / tham số tiếng, tập thiếu tiếng, hình và tiếng lệch độ dài, SPS khác nhau giữa các tập
(mối nối vỡ hình). Bản cũ còn LẶNG LẼ bỏ tập hỏng → phim gộp thiếu tập mà không ai biết.

Luồng (run_merge):
  1. check_episode() từng tập: ffprobe + quét gói toàn file + giải mã thử (tiếng toàn bộ, hình đầu/cuối;
     HG_MERGE_CHECK=deep → giải mã toàn bộ hình).
  2. make_plan(): tập HỎNG (không đọc được / cụt / không có hình) → DỪNG, báo tên tập (HG_MERGE_ON_BAD=skip để bỏ qua);
     mọi tập cùng tham số, không lỗi → «copy»; có tập lệch tham số / thiếu tiếng / lệch hình-tiếng / lỗi giải mã lẻ
     → «normalize» (mã hoá lại TẤT CẢ về một chuẩn → SPS đồng nhất).
  3. Gộp concat `-c copy` → verify_merged(): độ dài = tổng các tập (±), giải mã thử quanh MỖI mối nối.
     Bản «copy» hỏng mối nối → tự làm lại theo «normalize».
  4. Ghi `merge_check.json` cạnh file gộp (tập nào lỗi gì, thiếu số tập nào, đã làm gì).
Không import hongguo_bridge (thuần + ffmpeg) → test được riêng.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable

REPORT = "merge_check.json"
_NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)
_ERR_RE = re.compile(
    r"invalid data|error while decoding|corrupt|missing picture|no frame|non-existing|"
    r"moov atom not found|invalid nal|concealing|decode_slice|error splitting|partial file|"
    r"truncat|out of range|illegal|bad|failed", re.I)


def _cfg(key: str, default: str) -> str:
    v = os.environ.get(key)
    if v is None or not str(v).strip():
        for mod in ("config", "core.config"):
            try:
                m = __import__(mod, fromlist=["get"])
                v = m.get(key, None)
                break
            except Exception:  # noqa: BLE001
                continue
    return str(default if v is None or str(v).strip() == "" else v).strip()


def _run(cmd: list[str], timeout: float = 600) -> tuple[int, str, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, creationflags=_NOWIN)
        return r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except OSError as e:
        return 127, "", str(e)


def _f(v, d: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def _fps(s: str | None) -> float:
    try:
        a, b = str(s or "0/1").split("/")
        return round(float(a) / float(b), 2) if float(b) else 0.0
    except (ValueError, ZeroDivisionError):
        return 0.0


def _err_lines(stderr: str) -> list[str]:
    return [ln.strip()[:160] for ln in (stderr or "").splitlines() if ln.strip() and _ERR_RE.search(ln)]


# ----------------------------------------------------------------------------- 1) kiểm từng tập
def probe(path: Path) -> dict | None:
    rc, out, _ = _run(["ffprobe", "-v", "error", "-show_data_hash", "md5", "-show_entries",
                       "format=duration,size:stream=index,codec_type,codec_name,profile,width,height,pix_fmt,"
                       "r_frame_rate,avg_frame_rate,sample_rate,channels,duration,nb_frames,extradata_hash,"
                       "sample_aspect_ratio", "-of", "json", str(path)], timeout=60)
    if rc != 0 or not out.strip():
        return None
    try:
        return json.loads(out)
    except ValueError:
        return None


def last_video_pts(path: Path) -> float | None:
    """pts (giây) của gói hình cuối cùng thật sự có trong file — None nếu không đọc được."""
    rc, out, _ = _run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time,duration_time",
                       "-of", "csv=p=0", str(path)], timeout=300)
    last = None
    for ln in out.splitlines():
        parts = [x for x in ln.strip().split(",") if x and x != "N/A"]
        if parts:
            try:
                v = float(parts[0]) + (float(parts[1]) if len(parts) > 1 else 0.0)
                last = v if last is None else max(last, v)
            except ValueError:
                continue
    return last


def check_episode(path: str | Path, *, deep: bool | None = None) -> dict:
    """{name, ok, fatal:[...], fix:[...], warn:[...], dur, sig{...}} — fatal = không dùng được; fix = cần chuẩn hoá."""
    p = Path(path)
    if deep is None:
        deep = _cfg("HG_MERGE_CHECK", "quick").lower() == "deep"
    res: dict[str, Any] = {"name": p.name, "path": str(p), "ok": False, "fatal": [], "fix": [], "warn": [],
                           "dur": 0.0, "sig": {}}
    try:
        size = p.stat().st_size
    except OSError:
        res["fatal"].append("không thấy file")
        return res
    res["size"] = size
    if size < 20_000:
        res["fatal"].append(f"file quá nhỏ ({size} byte) — tải cụt")
        return res
    info = probe(p)
    if not info:
        res["fatal"].append("không đọc được (ffprobe lỗi — thường do tải cụt / thiếu moov)")
        return res
    streams = info.get("streams") or []
    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    fdur = _f((info.get("format") or {}).get("duration"))
    if not v or not int(v.get("width") or 0):
        res["fatal"].append("không có luồng hình")
        return res
    vdur = _f(v.get("duration"), fdur)
    adur = _f(a.get("duration"), fdur) if a else 0.0
    dur = max(vdur, fdur) if vdur else fdur
    res["dur"] = round(dur, 3)
    if dur < 1.0:
        res["fatal"].append(f"quá ngắn ({dur:.2f}s)")
        return res
    res["sig"] = {
        "vcodec": v.get("codec_name"), "w": int(v.get("width") or 0), "h": int(v.get("height") or 0),
        "pix_fmt": v.get("pix_fmt"), "fps": _fps(v.get("avg_frame_rate") or v.get("r_frame_rate")),
        "acodec": a.get("codec_name") if a else None, "sr": int(_f(a.get("sample_rate"))) if a else 0,
        "ch": int(a.get("channels") or 0) if a else 0, "vx": v.get("extradata_hash") or "",
    }
    if not a:
        res["fix"].append("thiếu tiếng → thêm tiếng im lặng")
    elif vdur and adur and abs(vdur - adur) > max(0.5, 0.03 * dur):
        res["fix"].append(f"hình {vdur:.1f}s ≠ tiếng {adur:.1f}s (lệch {abs(vdur - adur):.1f}s)")
    if res["sig"]["pix_fmt"] not in ("yuv420p", "yuvj420p"):
        res["fix"].append(f"pix_fmt {res['sig']['pix_fmt']}")
    # quét gói toàn file (nhanh): hỏng container / cụt giữa chừng
    rc, _, err = _run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(p), "-map", "0:v:0", "-map", "0:a:0?",
                       "-c", "copy", "-f", "null", "-"], timeout=300)
    el = [ln.strip()[:160] for ln in (err or "").splitlines() if ln.strip()]
    if rc != 0:
        res["fatal"].append("đọc gói lỗi: " + (el[0] if el else f"rc={rc}"))
        return res
    # độ dài THẬT = gói hình cuối đọc được (file faststart cụt vẫn khai báo đủ độ dài trong moov)
    real = last_video_pts(p)
    if real is not None:
        res["real_dur"] = round(real, 3)
        if real < dur - max(1.5, 0.05 * dur):
            res["fatal"].append(f"tải cụt: chỉ đọc được {real:.1f}s / khai báo {dur:.1f}s")
            return res
    if el:
        res["fix"].append(f"container có {len(el)} lỗi gói ({el[0][:70]})")
    # giải mã thử
    n_dec = 0
    first = ""
    jobs: list[list[str]] = []
    if a:
        jobs.append(["ffmpeg", "-v", "error", "-nostdin", "-i", str(p), "-vn", "-map", "0:a:0", "-f", "null", "-"])
    if deep:
        jobs.append(["ffmpeg", "-v", "error", "-nostdin", "-i", str(p), "-an", "-map", "0:v:0", "-f", "null", "-"])
    else:
        jobs.append(["ffmpeg", "-v", "error", "-nostdin", "-t", "3", "-i", str(p), "-an", "-map", "0:v:0",
                     "-f", "null", "-"])
        jobs.append(["ffmpeg", "-v", "error", "-nostdin", "-sseof", "-3", "-i", str(p), "-an", "-map", "0:v:0",
                     "-f", "null", "-"])
    for cmd in jobs:
        rc, _, err = _run(cmd, timeout=900)
        el = _err_lines(err)
        if rc != 0 and not el:
            el = [f"rc={rc}"]
        n_dec += len(el)
        first = first or (el[0] if el else "")
    if n_dec:
        res["fix"].append(f"{n_dec} lỗi giải mã ({first[:70]})")
        res["n_decode_err"] = n_dec
    res["ok"] = True
    return res


def check_all(eps: list[Path], *, deep: bool | None = None, workers: int | None = None,
              on_pct: Callable[[float], None] | None = None) -> list[dict]:
    workers = workers or max(1, min(6, int(_f(_cfg("HG_MERGE_CHECK_WORKERS", "4"), 4))))
    out: list[dict | None] = [None] * len(eps)
    done = [0]

    def one(k: int) -> None:
        out[k] = check_episode(eps[k], deep=deep)
        done[0] += 1
        if on_pct:
            on_pct(done[0] / max(1, len(eps)) * 100.0)

    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="hg-chk") as ex:
        list(ex.map(one, range(len(eps))))
    return [r for r in out if r is not None]


# ----------------------------------------------------------------------------- 2) kế hoạch
_SIG_KEYS = ("vcodec", "w", "h", "pix_fmt", "fps", "acodec", "sr", "ch")


def _sig_tuple(s: dict) -> tuple:
    return tuple(s.get(k) for k in _SIG_KEYS)


def missing_numbers(nums: list[int]) -> list[int]:
    ns = sorted({n for n in nums if 0 < n < 10**6})
    if len(ns) < 2:
        return []
    have = set(ns)
    return [n for n in range(ns[0], ns[-1] + 1) if n not in have][:200]


def make_plan(checks: list[dict], *, on_bad: str | None = None, ep_nums: list[int] | None = None) -> dict:
    """{"mode": copy|normalize|stop, "reasons": [...], "bad": [...], "use": [chỉ số tập dùng], "target": {...}}"""
    on_bad = (on_bad or _cfg("HG_MERGE_ON_BAD", "stop")).lower()
    bad = [c for c in checks if not c.get("ok")]
    good_idx = [k for k, c in enumerate(checks) if c.get("ok")]
    plan: dict[str, Any] = {"mode": "copy", "reasons": [], "bad": [{"name": c["name"], "why": c["fatal"]} for c in bad],
                            "use": good_idx, "warn": []}
    if ep_nums:
        miss = missing_numbers(ep_nums)
        if miss:
            plan["missing_eps"] = miss
            plan["warn"].append(f"thiếu {len(miss)} số tập: " + ", ".join(map(str, miss[:20])))
    if bad and on_bad != "skip":
        plan["mode"] = "stop"
        plan["reasons"].append(f"{len(bad)} tập hỏng — cần tải lại: " + ", ".join(c["name"] for c in bad[:10]))
        return plan
    if bad:
        plan["warn"].append(f"BỎ QUA {len(bad)} tập hỏng (HG_MERGE_ON_BAD=skip): "
                            + ", ".join(c["name"] for c in bad[:10]))
    if len(good_idx) < 2:
        plan["mode"] = "stop"
        plan["reasons"].append(f"chỉ còn {len(good_idx)} tập đọc được")
        return plan
    good = [checks[k] for k in good_idx]
    sigs = Counter(_sig_tuple(c["sig"]) for c in good)
    major = sigs.most_common(1)[0][0]
    ms = dict(zip(_SIG_KEYS, major))
    # chuẩn đích: độ phân giải / fps của số đông; tiếng 48 kHz stereo nếu số đông không rõ
    plan["target"] = {"w": int(ms["w"]) - int(ms["w"]) % 2, "h": int(ms["h"]) - int(ms["h"]) % 2,
                      "fps": ms["fps"] or 30.0, "sr": ms["sr"] or 48000, "ch": ms["ch"] or 2}
    n_fix = [c for c in good if c.get("fix")]
    if len(sigs) > 1:
        plan["mode"] = "normalize"
        plan["reasons"].append(f"{len(good) - sigs[major]} tập lệch tham số (res/fps/codec/tiếng) so với số đông "
                               f"{ms['w']}x{ms['h']} {ms['fps']}fps {ms['vcodec']}/{ms['acodec']}")
    if n_fix:
        plan["mode"] = "normalize"
        plan["reasons"].append(f"{len(n_fix)} tập cần sửa: " + "; ".join(
            f"{c['name']}: {c['fix'][0]}" for c in n_fix[:5]))
    if ms["vcodec"] not in ("h264", "hevc") or (ms["acodec"] not in (None, "aac")):
        plan["mode"] = "normalize"
        plan["reasons"].append(f"codec {ms['vcodec']}/{ms['acodec']} không hợp ghép mp4 trực tiếp")
    if plan["mode"] == "copy" and len({c["sig"].get("vx") for c in good if c["sig"].get("vx")}) > 1:
        plan["sps_differs"] = True   # vẫn thử copy; verify_merged quyết định có phải chuẩn hoá không
        plan["warn"].append("tham số mã hoá (SPS) khác nhau giữa các tập — sẽ kiểm kỹ mối nối sau khi gộp")
    return plan


# ----------------------------------------------------------------------------- 3) chuẩn hoá + ghép + kiểm
def normalize_episode(src: Path, dst: Path, target: dict, vargs: list[str], *, has_audio: bool) -> tuple[bool, str]:
    w, h, fps = int(target["w"]), int(target["h"]), float(target["fps"])
    sr, ch = int(target["sr"]), int(target["ch"])
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,"
          f"setsar=1,fps={fps:g}")
    last = ""
    for enc in (vargs, ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20"]):
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-nostdin", "-err_detect", "ignore_err",
               "-fflags", "+genpts+discardcorrupt", "-i", str(src)]
        if not has_audio:
            cmd += ["-f", "lavfi", "-i", f"anullsrc=r={sr}:cl={'stereo' if ch >= 2 else 'mono'}"]
        cmd += ["-map", "0:v:0", "-map", "0:a:0" if has_audio else "1:a:0", "-vf", vf, *enc, "-pix_fmt", "yuv420p",
                "-af", "aresample=async=1:first_pts=0", "-c:a", "aac", "-b:a", "192k", "-ar", str(sr), "-ac", str(ch),
                "-video_track_timescale", "90000", "-shortest", "-movflags", "+faststart", str(dst)]
        rc, _, err = _run(cmd, timeout=3600)
        if rc == 0 and dst.is_file() and dst.stat().st_size > 10_000:
            return True, ""
        last = (err or f"rc={rc}")[-300:]
        try:
            dst.unlink(missing_ok=True)
        except OSError:
            pass
    return False, last


def concat_copy(parts: list[Path], out: Path) -> tuple[bool, str]:
    tmp = Path(tempfile.mkdtemp(prefix="hg_concat_"))
    try:
        lst = tmp / "list.txt"
        with lst.open("w", encoding="utf-8") as f:
            for p in parts:
                esc = Path(p).resolve().as_posix().replace("'", r"'\''")
                f.write(f"file '{esc}'\n")
        rc, _, err = _run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-nostdin", "-f", "concat",
                           "-safe", "0", "-i", str(lst), "-c", "copy", "-f", "mp4", "-movflags", "+faststart",
                           str(out)], timeout=6 * 3600)
        if rc != 0 or not out.is_file() or out.stat().st_size < 100_000:
            return False, (err or f"rc={rc}")[-400:]
        return True, ""
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def verify_merged(out: Path, durs: list[float], *, span: float = 2.0) -> dict:
    """Độ dài file gộp ≈ tổng các tập; giải mã thử quanh mỗi mối nối. {"ok", "dur", "expect", "bad_joints": [...]}"""
    info = probe(out)
    if not info:
        return {"ok": False, "error": "không đọc được file gộp"}
    md = _f((info.get("format") or {}).get("duration"))
    expect = sum(durs)
    tol = max(2.0, 0.005 * expect, 0.08 * len(durs))
    res: dict[str, Any] = {"ok": True, "dur": round(md, 2), "expect": round(expect, 2), "bad_joints": []}
    if abs(md - expect) > tol:
        res["ok"] = False
        res["error"] = f"độ dài file gộp {md:.1f}s ≠ tổng các tập {expect:.1f}s (lệch {md - expect:+.1f}s)"
    joints, t = [], 0.0
    for d in durs[:-1]:
        t += d
        joints.append(t)

    def one(tj: float) -> tuple[float, int, str]:
        rc, _, err = _run(["ffmpeg", "-v", "error", "-nostdin", "-ss", f"{max(0.0, tj - span):.3f}", "-t",
                           f"{2 * span:.3f}", "-i", str(out), "-f", "null", "-"], timeout=120)
        el = _err_lines(err)
        return tj, (len(el) if (el or rc == 0) else 1), (el[0] if el else ("" if rc == 0 else f"rc={rc}"))

    with ThreadPoolExecutor(max_workers=4, thread_name_prefix="hg-joint") as ex:
        for tj, n, first in ex.map(one, joints):
            if n:
                res["bad_joints"].append({"t": round(tj, 2), "n": n, "err": first[:120]})
    if res["bad_joints"]:
        res["ok"] = False
        res.setdefault("error", f"{len(res['bad_joints'])}/{len(joints)} mối nối lỗi giải mã "
                                f"(đầu tiên @{res['bad_joints'][0]['t']}s)")
    return res


def _write_report(folder: Path, rep: dict) -> None:
    try:
        tmp = folder / (REPORT + ".tmp")
        tmp.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, folder / REPORT)
    except OSError:
        pass


def run_merge(folder: str | Path, eps: list[Path], *, out_name: str | None = None,
              vargs: list[str] | None = None, ep_nums: list[int] | None = None,
              on_phase: Callable[[str, float | None], None] | None = None,
              on_note: Callable[[str, str], None] | None = None,
              on_bad: str | None = None, stop_check: Callable[[], bool] | None = None) -> dict:
    """Kiểm → (chuẩn hoá) → gộp → kiểm lại. Trả {"ok", "merged_file", "policy", "report", "error"?}."""
    folder = Path(folder)
    out_name = out_name or f"{folder.name} (merged).mp4"
    out_path = folder / out_name
    vargs = vargs or ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20"]
    phase = on_phase or (lambda s, p=None: None)
    note = on_note or (lambda k, s: None)
    stop = stop_check or (lambda: False)
    t0 = time.time()
    rep: dict[str, Any] = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "folder": folder.name, "n_eps": len(eps)}
    for stale in folder.glob("*.tmp.mp4"):
        try:
            stale.unlink()
        except OSError:
            pass
    phase("kiểm tra từng tập (đọc + giải mã thử)", 0)
    checks = check_all(eps, on_pct=lambda p: phase("kiểm tra từng tập (đọc + giải mã thử)", p))
    plan = make_plan(checks, on_bad=on_bad, ep_nums=ep_nums)
    rep.update({"plan": {k: plan[k] for k in plan if k != "use"},
                "episodes": [{"name": c["name"], "ok": c["ok"], "dur": c.get("dur"), "fatal": c["fatal"],
                              "fix": c["fix"], "sig": {k: c["sig"].get(k) for k in _SIG_KEYS} if c.get("sig") else {}}
                             for c in checks]})
    for w in plan.get("warn") or []:
        note("warn", w)
    if plan["mode"] == "stop":
        rep.update({"ok": False, "error": "; ".join(plan["reasons"])})
        _write_report(folder, rep)
        return {"ok": False, "error": rep["error"], "bad": plan["bad"], "report": rep, "stopped": True}
    use = [checks[k] for k in plan["use"]]
    use_paths = [Path(c["path"]) for c in use]
    partial = folder / (out_name + ".tmp.mp4")

    def _finish_ok(policy: str, ver: dict, extra: dict | None = None) -> dict:
        os.replace(partial, out_path)   # ghi đè nguyên tử (không cần xoá trước)
        rep.update({"ok": True, "policy": policy, "verify": ver, "sec": round(time.time() - t0, 1), **(extra or {})})
        _write_report(folder, rep)
        return {"ok": True, "merged_file": out_name, "path": str(out_path), "policy": policy, "episodes": len(use),
                "size": out_path.stat().st_size, "report": rep, "warn": plan.get("warn") or [],
                "skipped": [b["name"] for b in plan["bad"]]}

    if plan["mode"] == "copy":
        phase("gộp -c copy (mọi tập cùng chuẩn)", 0)
        ok, err = concat_copy(use_paths, partial)
        if ok:
            phase("kiểm file gộp (độ dài + mối nối)", 50)
            ver = verify_merged(partial, [float(c["dur"]) for c in use])
            if ver.get("ok"):
                return _finish_ok("concat_copy", ver)
            note("normalize", f"gộp copy không đạt ({ver.get('error')}) → mã hoá lại về một chuẩn")
            rep["copy_failed"] = ver
        else:
            note("normalize", f"gộp copy lỗi ({err[:120]}) → mã hoá lại về một chuẩn")
            rep["copy_failed"] = {"error": err}
        try:
            partial.unlink(missing_ok=True)
        except OSError:
            pass
    else:
        note("normalize", "; ".join(plan["reasons"])[:300])
    # normalize: mã hoá lại MỌI tập về chuẩn đích
    tgt = plan["target"]
    tmp_root = Path(tempfile.mkdtemp(prefix="hg_norm_", dir=_cfg("HG_MERGE_TMP", "") or None))
    try:
        parts: list[Path] = []
        durs: list[float] = []
        failed: list[str] = []
        n = len(use)
        for k, c in enumerate(use):
            if stop():
                return {"ok": False, "error": "đã dừng", "stopped_by_user": True, "report": rep}
            dst = tmp_root / f"{k:05d}.mp4"
            ok, err = normalize_episode(Path(c["path"]), dst, tgt, vargs, has_audio=bool(c["sig"].get("acodec")))
            if not ok:
                failed.append(f"{c['name']}: {err[-120:]}")
            else:
                pi = probe(dst)
                durs.append(_f(((pi or {}).get("format") or {}).get("duration"), float(c["dur"])))
                parts.append(dst)
            phase(f"chuẩn hoá {tgt['w']}x{tgt['h']} {tgt['fps']:g}fps ({k + 1}/{n})", (k + 1) / n * 90.0)
        if failed and (on_bad or _cfg("HG_MERGE_ON_BAD", "stop")).lower() != "skip":
            rep.update({"ok": False, "error": f"{len(failed)} tập không mã hoá lại được: " + "; ".join(failed[:5])})
            _write_report(folder, rep)
            return {"ok": False, "error": rep["error"], "report": rep, "stopped": True}
        if len(parts) < 2:
            rep.update({"ok": False, "error": "không đủ tập sau chuẩn hoá"})
            _write_report(folder, rep)
            return {"ok": False, "error": rep["error"], "report": rep}
        phase("ghép các tập đã chuẩn hoá", 92)
        ok, err = concat_copy(parts, partial)
        if not ok:
            rep.update({"ok": False, "error": f"concat: {err}"})
            _write_report(folder, rep)
            return {"ok": False, "error": rep["error"], "report": rep}
        phase("kiểm file gộp (độ dài + mối nối)", 96)
        ver = verify_merged(partial, durs)
        if not ver.get("ok"):
            try:
                partial.unlink(missing_ok=True)
            except OSError:
                pass
            rep.update({"ok": False, "error": f"file gộp sau chuẩn hoá vẫn lỗi: {ver.get('error')}", "verify": ver})
            _write_report(folder, rep)
            return {"ok": False, "error": rep["error"], "report": rep}
        return _finish_ok("normalize", ver, {"target": tgt, "normalize_failed": failed})
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
