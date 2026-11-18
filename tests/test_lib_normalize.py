"""2026-11-17/18: chuẩn hóa thư viện — hàng đợi nền + kiểm đã chuẩn + tiến độ/log (lib_normalize)."""
import json
import os
import stat
import sys
import time

import agents.hongguo_bridge as hg
import engines.lib_normalize as ln


def _reset(tmp_path, monkeypatch):
    monkeypatch.setenv("PINELINE_LIB_ROOT", str(tmp_path / "Lib"))
    ln.set_log_dir(tmp_path / "logs")
    with ln._lock:
        ln._items.clear(); ln._order.clear(); ln._queue.clear(); ln._logbuf.clear()


def _season(tmp_path, name, *, report=None):
    d = tmp_path / "Lib" / name
    d.mkdir(parents=True)
    f = d / f"{name} (merged).mp4"
    f.write_bytes(b"0" * 100)
    if report is not None:
        time.sleep(0.01)
        (d / "merge_check.json").write_text(json.dumps(report), encoding="utf-8")
    return f


def _wait_idle(sec=5):
    t = time.time()
    while time.time() - t < sec:
        st = ln.status()
        if not st["worker"] and not st["queue"]:
            return st
        time.sleep(0.05)
    return ln.status()


def test_batch_skips_normalized_and_checked_reports_failures(tmp_path, monkeypatch):
    _reset(tmp_path, monkeypatch)
    _season(tmp_path, "A")                                   # gộp cũ → chuẩn hóa
    _season(tmp_path, "B", report={"ok": True, "policy": "copy", "merged_file": "B (merged).mp4"})
    _season(tmp_path, "C")                                   # đã có MARK
    _season(tmp_path, "D")                                   # ffmpeg lỗi
    (tmp_path / "Lib" / "E").mkdir()                         # chưa gộp
    monkeypatch.setattr(ln, "_probe", lambda p: {
        "format": {"tags": {"comment": ln.MARK if p.parent.name == "C" else ""}},
        "streams": [{"codec_type": "video", "codec_name": "h264", "width": 1280, "height": 720}]})
    ran = []

    def fake(path, target_wh=None, on_progress=None, auto_orient=False, **k):
        ran.append(path.parent.name)
        assert auto_orient
        on_progress({"phase": "encode", "pct": 50.0, "out_sec": 50.0, "dur": 100.0, "speed": "3x"})
        if path.parent.name == "D":
            return {"ok": False, "error": "ffmpeg rc=1", "error_tail": ["Invalid data found when processing input"]}
        return {"ok": True, "encoder": "h264_nvenc", "target": "1920x1080", "n_err": 3}
    monkeypatch.setattr(hg, "normalize_merged_file", fake)
    r = ln.enqueue(["A", "B", "C", "D", "E", "../x"])
    assert r["ok"] and len(r["added"]) == 6
    st = _wait_idle()
    by = {x["name"]: x for x in st["items"]}
    assert ran == ["A", "D"]
    assert by["A"]["state"] == "done" and "bỏ qua 3 dòng lỗi" in by["A"]["text"]
    assert by["B"]["state"] == "skipped" and "gộp mới đã kiểm" in by["B"]["text"]
    assert by["C"]["state"] == "skipped" and "đã chuẩn hóa" in by["C"]["text"]
    assert by["D"]["state"] == "failed" and "Invalid data" in by["D"]["text"]
    assert by["E"]["state"] == "failed" and "chưa có file gộp" in by["E"]["text"]
    assert by["../x"]["state"] == "failed"
    assert st["counts"] == {"done": 1, "skipped": 2, "failed": 3}
    log = "\n".join(st["log"])
    assert "▶ chuẩn hóa" in log and "⏭ bỏ qua" in log and "ffmpeg: Invalid data" in log
    assert (tmp_path / "logs" / "lib_normalize.log").is_file()


def test_single_force_runs_even_if_normalized_and_no_double_queue(tmp_path, monkeypatch):
    _reset(tmp_path, monkeypatch)
    _season(tmp_path, "C")
    monkeypatch.setattr(ln, "_probe", lambda p: {"format": {"tags": {"comment": ln.MARK}}, "streams": [{}]})
    gate = {"go": False}
    ran = []

    def fake(path, **k):
        while not gate["go"]:
            time.sleep(0.02)
        ran.append(1)
        return {"ok": True, "encoder": "x", "target": "1920x1080"}
    monkeypatch.setattr(hg, "normalize_merged_file", fake)
    ln.enqueue(["C"], force=True, front=True)
    assert ln.enqueue(["C"])["already"] == ["C"]
    gate["go"] = True
    st = _wait_idle()
    assert ran == [1] and st["items"][0]["state"] == "done"


def test_cancel_queued(tmp_path, monkeypatch):
    _reset(tmp_path, monkeypatch)
    for n in ("A", "B", "C"):
        _season(tmp_path, n)
    monkeypatch.setattr(ln, "_probe", lambda p: {"streams": [{}]})
    gate = {"go": False}

    def fake(path, **k):
        while not gate["go"]:
            time.sleep(0.02)
        return {"ok": True}
    monkeypatch.setattr(hg, "normalize_merged_file", fake)
    ln.enqueue(["A", "B", "C"])
    time.sleep(0.2)
    assert set(ln.cancel_queued()["cancelled"]) == {"B", "C"}
    gate["go"] = True
    st = _wait_idle()
    assert {x["name"]: x["state"] for x in st["items"]} == {"A": "done", "B": "cancelled", "C": "cancelled"}


def _fake_ff(tmp_path, monkeypatch, *, nvenc_fail=False, w=1280, h=720):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    (bindir / "ffprobe").write_text(
        "#!/bin/sh\ncase \"$*\" in *width,height*) echo '%d,%d';; *) echo 100;; esac\n" % (w, h))
    (bindir / "ffmpeg").write_text(
        "#!/bin/sh\n"
        "case \"$*\" in *-encoders*) echo ' V..... h264_nvenc'; exit 0;; esac\n"
        "echo \"$*\" >> \"%s/calls.txt\"\n" % tmp_path +
        ("case \"$*\" in *h264_nvenc*) echo 'nvenc boom'; exit 1;; esac\n" if nvenc_fail else "") +
        "for a; do out=$a; done\n"
        "echo '[h264 @ 0x1] Invalid data found when processing input'\n"
        "printf 'out_time_us=40000000\\nspeed=2.5x\\nprogress=continue\\n'\n"
        "printf 'out_time_us=90000000\\nspeed=2.6x\\nprogress=end\\n'\n"
        "head -c 2000 /dev/zero > \"$out\"\n")
    for f in bindir.iterdir():
        f.chmod(f.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.environ['PATH']}")


def test_normalize_parses_progress_and_marks(tmp_path, monkeypatch):
    if sys.platform.startswith("win"):
        return
    _fake_ff(tmp_path, monkeypatch)
    src = tmp_path / "x (merged).mp4"
    src.write_bytes(b"0" * 3000)
    seen = []
    r = hg.normalize_merged_file(src, target_wh=(1920, 1080), on_progress=seen.append, auto_orient=True)
    assert r["ok"] and r["n_err"] == 1 and r["target"] == "1920x1080"
    enc = [d for d in seen if d.get("phase") == "encode" and "out_sec" in d]
    assert [d["pct"] for d in enc] == [40.0, 90.0] and enc[-1]["speed"] == "2.6x"
    call = (tmp_path / "calls.txt").read_text()
    assert f"comment={hg.NORM_MARK}" in call and "discardcorrupt" in call and "-ac 2" in call


def test_normalize_nvenc_fail_falls_back_and_portrait(tmp_path, monkeypatch):
    if sys.platform.startswith("win"):
        return
    _fake_ff(tmp_path, monkeypatch, nvenc_fail=True, w=720, h=1280)
    src = tmp_path / "y (merged).mp4"
    src.write_bytes(b"0" * 3000)
    r = hg.normalize_merged_file(src, target_wh=(1920, 1080), auto_orient=True)
    assert r["ok"] and r["encoder"] == "libx264" and r["target"] == "1080x1920"
    assert any("thử lại libx264" in x for x in r["error_tail"]) or r["n_err"] >= 1
