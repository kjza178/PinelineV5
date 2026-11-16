"""2026-11-17: kiểm tra / chuẩn hoá tập trước khi gộp (hg_merge_check) + bỏ Hongguo classic."""
import shutil
import subprocess
from pathlib import Path

import pytest

import agents.hg_merge_check as mc


def _sig(**kw):
    s = {"vcodec": "h264", "w": 1080, "h": 1920, "pix_fmt": "yuv420p", "fps": 30.0,
         "acodec": "aac", "sr": 44100, "ch": 2, "vx": "a"}
    s.update(kw)
    return s


def _ck(name, ok=True, fix=None, **sig):
    return {"name": name, "ok": ok, "fatal": [] if ok else ["tải cụt"], "fix": fix or [],
            "warn": [], "dur": 60.0, "real_dur": 60.0, "sig": _sig(**sig)}


def test_missing_numbers():
    assert mc.missing_numbers([1, 2, 4, 7]) == [3, 5, 6]
    assert mc.missing_numbers([1, 2, 3]) == []


def test_plan_copy_when_all_same():
    p = mc.make_plan([_ck("E1"), _ck("E2"), _ck("E3")], on_bad="stop", ep_nums=[1, 2, 3])
    assert p["mode"] == "copy" and p["use"] == [0, 1, 2] and not p.get("missing_eps")


def test_plan_stop_on_bad_episode():
    p = mc.make_plan([_ck("E1"), _ck("E2", ok=False), _ck("E3")], on_bad="stop")
    assert p["mode"] == "stop" and p["bad"][0]["name"] == "E2"


def test_plan_skip_bad_then_normalize_mixed_res():
    p = mc.make_plan([_ck("E1"), _ck("E2", ok=False), _ck("E3", w=720, h=1280), _ck("E4")], on_bad="skip")
    assert p["mode"] == "normalize" and p["use"] == [0, 2, 3]
    assert (p["target"]["w"], p["target"]["h"]) == (1080, 1920)


def test_plan_normalize_on_fix_and_missing_eps_warn():
    p = mc.make_plan([_ck("E1"), _ck("E2", fix=["lệch tiếng/hình 4s"])], on_bad="stop", ep_nums=[1, 3])
    assert p["mode"] == "normalize" and p["missing_eps"] == [2]


def test_plan_too_few_good():
    assert mc.make_plan([_ck("E1"), _ck("E2", ok=False)], on_bad="skip")["mode"] == "stop"


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"), reason="cần ffmpeg")
def test_run_merge_detects_corrupt_and_merges_good(tmp_path: Path):
    def mk(name, sec):
        out = tmp_path / name
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"testsrc=s=320x240:r=25:d={sec}",
                        "-f", "lavfi", "-i", f"sine=f=440:d={sec}", "-c:v", "libx264", "-preset", "ultrafast",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(out)], check=True)
        return out
    e1, e2 = mk("S01E001.mp4", 3), mk("S01E002.mp4", 3)
    bad = tmp_path / "S01E003.mp4"
    bad.write_bytes(e1.read_bytes()[: 30_000])          # thiếu moov
    r = mc.run_merge(tmp_path, [e1, e2, bad], out_name="x (merged).mp4", vargs=["-c:v", "libx264"],
                     ep_nums=[1, 2, 3], on_bad="stop")
    assert r["ok"] is False and any("S01E003" in str(b) for b in r.get("bad") or [])
    assert (tmp_path / "merge_check.json").is_file()
    r2 = mc.run_merge(tmp_path, [e1, e2], out_name="x (merged).mp4", vargs=["-c:v", "libx264"], ep_nums=[1, 2])
    assert r2["ok"] is True and (tmp_path / "x (merged).mp4").is_file()


def test_classic_removed():
    root = Path(__file__).resolve().parents[1]
    assert not (root / "agents" / "hg_ui_ctx.py").exists()
    src = (root / "agents" / "hongguo_bridge.py").read_text(encoding="utf-8")
    for bad in ("_req(\"/dl/", "_req(f\"/dl/", "_use_rpc", "discover_ui_token", "127.0.0.1:8000", "def merge_one"):
        assert bad not in src, bad
