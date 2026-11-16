"""agentS 2026-11-13 — 60892cc63cb7: Full đã ghép mà part vẫn ASR lại.

Chuỗi thật (UTC): 21:36 Brain heal aggressive `asr_run_force` trên PARENT (parent «asr failed», không
asr.json theo thiết kế) → run_stage(parent, asr, force) nằm hàng _gpu tới 23:36 → split_job_to_subjobs
cắt lại + reset tts part → ép ASR p01 (--force xoá asr.json) rồi p02, trong khi Full ghép nền xong 00:12.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest


@pytest.fixture
def srv(tmp_path, monkeypatch):
    server = pytest.importorskip("server")
    monkeypatch.setattr(server, "WORK_ROOT", tmp_path)
    monkeypatch.setattr(server, "free_gpu_vram", lambda *a, **k: None)
    monkeypatch.setattr(server, "_resolve_asr_engine", lambda wd, e=None: "firered_asr")
    return server


def _mk(root: Path, jid: str, data: dict) -> Path:
    d = root / jid
    d.mkdir(parents=True, exist_ok=True)
    (d / "manifest.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return d


def _rd(root: Path, jid: str) -> dict:
    return json.loads((root / jid / "manifest.json").read_text(encoding="utf-8"))


P = "60892cc63cb7"
SUBS = [f"{P}_p01", f"{P}_p02"]
LONG = {"download": {"status": "done", "duration_sec": 19750.0}}


def _merge_parent(root: Path):
    d = root / P
    data = _rd(root, P)
    data.setdefault("split_info", {})["status"] = "merged"
    data["stages"] = {s: {"status": "done"} for s in ("download", "asr", "translate", "tts", "mux")}
    data["stages"]["mux"]["is_full_merged"] = True
    data["stages"]["download"]["duration_sec"] = 19750.0
    (d / "manifest.json").write_text(json.dumps(data), encoding="utf-8")
    (d / "output_full.mp4").write_bytes(b"x" * 1_000_001)


def _engine_spy(srv, monkeypatch):
    calls = []
    monkeypatch.setattr(srv, "_run_engine", lambda script, wd, *a: calls.append((Path(wd).name, a)))
    return calls


# ───────── force «dùng một lần» ─────────

def test_force_consumed_by_newer_artifact(srv, tmp_path):
    d = _mk(tmp_path, "j", {"stages": {}})
    t = time.time()
    assert srv._force_consumed(d, t) is False                 # chưa có asr.json
    (d / "asr.json").write_text("[]", encoding="utf-8")
    os.utime(d / "asr.json", (t + 5, t + 5))
    assert srv._force_consumed(d, t) is True                  # đã làm lại sau lệnh → không ép nữa
    assert srv._force_consumed(d, t + 10) is False
    assert srv._force_consumed(d, None) is False              # lệnh mới (không mốc) → giữ force


def test_single_job_asr_force_not_reapplied_when_asr_newer(srv, tmp_path, monkeypatch):
    d = _mk(tmp_path, "solo", {"stages": {"download": {"status": "done", "duration_sec": 600}}})
    req_at = time.time() - 100
    (d / "asr.json").write_text("[]", encoding="utf-8")       # mtime = bây giờ > req_at
    calls = _engine_spy(srv, monkeypatch)
    srv._run_stage("solo", "asr", "Tiếng Việt", True, requested_at=req_at)
    assert calls == [("solo", ())]                            # không --force
    calls.clear()
    srv._run_stage("solo", "asr", "Tiếng Việt", True, requested_at=time.time() + 100)
    assert calls == [("solo", ("--force",))]


# ───────── lệnh ASR trên PARENT (đường thật của sự cố) ─────────

def test_parent_asr_command_dropped_when_full_already_merged(srv, tmp_path, monkeypatch):
    import engines.split_parts as split_parts
    _mk(tmp_path, P, {"stages": dict(LONG), "split_info": {"sub_job_ids": SUBS, "status": "split_done"}})
    _merge_parent(tmp_path)
    called = []
    monkeypatch.setattr(split_parts, "split_job_to_subjobs", lambda *a, **k: called.append("split") or {})
    removed = []
    monkeypatch.setattr(srv.job_queue, "queue_remove", lambda ids: removed.append(list(ids)))
    calls = _engine_spy(srv, monkeypatch)
    srv._run_stage(P, "asr", "Tiếng Việt", True, requested_at=time.time() - 7200)
    assert called == [] and calls == []
    assert removed == [[P]]
    # parent split thiếu duration_sec → vẫn nhận là parent (không ASR thẳng lên parent)
    data = _rd(tmp_path, P)
    data["stages"]["download"].pop("duration_sec")
    (tmp_path / P / "manifest.json").write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(srv, "_find_video", lambda wd: None)
    srv._run_stage(P, "asr", "Tiếng Việt", True)
    assert called == [] and calls == []


def test_parent_asr_force_skips_done_parts_and_consumed_force(srv, tmp_path, monkeypatch):
    import engines.split_parts as split_parts
    _mk(tmp_path, P, {"stages": dict(LONG), "split_info": {"sub_job_ids": SUBS}})
    p1 = _mk(tmp_path, SUBS[0], {"stages": {}})
    p2 = _mk(tmp_path, SUBS[1], {"stages": {}})
    (p2 / "asr.json").write_text("[]", encoding="utf-8")
    kw = {}
    monkeypatch.setattr(split_parts, "split_job_to_subjobs",
                        lambda jid, **k: kw.update(k) or {"sub_job_ids": SUBS})
    merged = []
    monkeypatch.setattr(split_parts, "merge_subjob_asr_to_parent", lambda jid, **k: merged.append(k))
    monkeypatch.setattr(srv, "_part_pipeline_complete", lambda wd: Path(wd).name == SUBS[0])
    calls = _engine_spy(srv, monkeypatch)
    srv._run_stage(P, "asr", "Tiếng Việt", True, requested_at=time.time() - 100)
    assert kw.get("work_root") == tmp_path                    # trước: work_root mặc định "work"
    assert calls == [(SUBS[1], ())]                           # p01 đã mux → bỏ; p02 asr mới hơn lệnh → không --force
    assert merged and merged[0].get("work_root") == tmp_path


def test_parent_asr_loop_stops_when_full_merged_midway(srv, tmp_path, monkeypatch):
    import engines.split_parts as split_parts
    _mk(tmp_path, P, {"stages": dict(LONG), "split_info": {"sub_job_ids": SUBS}})
    for s in SUBS:
        _mk(tmp_path, s, {"stages": {}})
    monkeypatch.setattr(split_parts, "split_job_to_subjobs", lambda jid, **k: {"sub_job_ids": SUBS})
    merged = []
    monkeypatch.setattr(split_parts, "merge_subjob_asr_to_parent", lambda jid, **k: merged.append(1))
    monkeypatch.setattr(srv, "_part_pipeline_complete", lambda wd: False)
    monkeypatch.setattr(srv.job_queue, "queue_remove", lambda ids: None)
    calls = []

    def eng(script, wd, *a):
        calls.append(Path(wd).name)
        _merge_parent(tmp_path)                               # Full ghép nền xong trong lúc ASR p01
    monkeypatch.setattr(srv, "_run_engine", eng)
    srv._run_stage(P, "asr", "Tiếng Việt", True)
    assert calls == [SUBS[0]] and merged == []                # p02 KHÔNG chạy, không gộp ASR


# ───────── vòng auto-split (queue → parent) ─────────

def test_auto_split_loop_stops_and_dequeues_when_parent_finished(srv, tmp_path, monkeypatch):
    import engines.split_parts as split_parts
    _mk(tmp_path, P, {"stages": {}, "split_info": {"status": "split_done", "sub_job_ids": SUBS}})
    for s in SUBS:
        _mk(tmp_path, s, {"stages": {}})
    monkeypatch.setattr(srv, "_find_video", lambda wd: tmp_path / P / "manifest.json")
    monkeypatch.setattr(split_parts, "probe_duration", lambda v: 5.5 * 3600)
    monkeypatch.setattr(split_parts, "merge_job_parts", lambda *a, **k: pytest.fail("không được ghép lại"))
    monkeypatch.setattr(srv, "_part_pipeline_complete", lambda wd: False)
    removed = []
    monkeypatch.setattr(srv.job_queue, "queue_remove", lambda ids: removed.append(list(ids)))
    ran, aborts = [], []

    def fake_gpu(s_id, *a, abort_if=None, **k):
        ran.append(s_id)
        _merge_parent(tmp_path)                               # Full ghép xong (nền) khi p01 chạy
        aborts.append(abort_if() if abort_if else None)
    monkeypatch.setattr(srv, "_auto_gpu", fake_gpu)
    assert srv._check_and_run_auto_split_parts(P, "Tiếng Việt", "duck", 0.2, 0.22, False) is True
    assert ran == [SUBS[0]]                                   # p02 không chạy
    assert aborts == [True]                                   # _auto_gpu nhận abort_if → dừng trước stage kế
    assert removed == [[P]]


def test_auto_gpu_abort_if_stops_before_asr(srv, tmp_path, monkeypatch):
    _mk(tmp_path, SUBS[0], {"stages": {}})
    monkeypatch.setattr(srv, "_part_pipeline_complete", lambda wd: False)
    calls = _engine_spy(srv, monkeypatch)
    srv._auto_gpu(SUBS[0], "Tiếng Việt", "duck", 0.2, 0.22, False, abort_if=lambda: True)
    assert calls == []


def test_queue_run_parent_not_marked_asr(srv, tmp_path, monkeypatch):
    """Parent split: _queue_run_one đánh mux (không asr) → không còn «asr failed» trên parent cho Brain."""
    _mk(tmp_path, P, {"stages": {}, "split_info": {"sub_job_ids": SUBS}})
    marked = []
    orig = srv.Manifest.mark_running

    def spy(self, name):
        marked.append(name)
        return orig(self, name)
    monkeypatch.setattr(srv.Manifest, "mark_running", spy)
    monkeypatch.setattr(srv, "_resolve_queue_voice", lambda wd, v: "v6")
    monkeypatch.setattr(srv, "list_clone_voices", lambda: ["v6"])
    monkeypatch.setattr(srv, "_find_video", lambda wd: None)
    srv._queue_run_one(P, {"voice": "v6"})
    assert marked and marked[0] == "mux"


# ───────── Brain heal: parent split không «asr_bad» ─────────

def test_heal_no_asr_force_on_split_parent(tmp_path):
    import agents.agent_heal as agent_heal
    _mk(tmp_path, P, {"stages": {"download": {"status": "done"}, "asr": {"status": "failed"},
                                 "translate": {"status": "pending"}},
                      "split_info": {"sub_job_ids": SUBS, "status": "split_done"}})
    d = agent_heal.diagnose_job(tmp_path, P)
    acts = [a["action"] for a in d.get("actions_aggressive") or []]
    assert "asr_run_force" not in acts
    assert not any(i["code"] == "asr_bad" for i in d["issues"])
    _mk(tmp_path, "solo", {"stages": {"asr": {"status": "failed"}}})
    acts2 = [a["action"] for a in agent_heal.diagnose_job(tmp_path, "solo").get("actions_aggressive") or []]
    assert "asr_run_force" in acts2                           # job thường giữ hành vi cũ


# ───────── hàng đợi: cờ một lần không lưu ─────────

def test_queue_opts_drop_one_shot_flags(tmp_path, monkeypatch):
    import core.job_queue as jq
    monkeypatch.setattr(jq, "WORK_ROOT", tmp_path)
    jq._reset_for_tests()
    monkeypatch.setattr(jq, "_ensure_worker_unlocked", lambda: None)
    _mk(tmp_path, P, {"stages": {}})
    jq.queue_add([P], opts={"voice": "v6", "force": True, "skip_done": False}, skip_done=False)
    st = jq.queue_state()
    assert st["opts_by_job"][P] == {"voice": "v6"}
    saved = json.loads((tmp_path / jq._PERSIST_NAME).read_text(encoding="utf-8"))
    assert "force" not in json.dumps(saved) and "skip_done" not in json.dumps(saved)
    jq._reset_for_tests()


# ───────── re-split: dùng lại part, giữ kết quả ─────────

def _split_env(tmp_path, monkeypatch, *, part_durs, keep_split_info=True):
    import engines.split_parts as split_parts
    import engines.render as render
    src = tmp_path / "src.mp4"
    src.write_bytes(b"s" * 5000)
    parts = [{"part": 1, "total_parts": 2, "start": 0.0, "end": 9875.707, "duration": 9875.707, "smart_cut": True},
             {"part": 2, "total_parts": 2, "start": 9875.707, "end": 19750.853, "duration": 9875.146,
              "smart_cut": True}]
    si = {"status": "merged", "merged_at": "x", "sub_job_ids": SUBS, "parts": parts, "total_parts": 2}
    _mk(tmp_path, P, {"stages": {"tts": {"voice": "v6", "speed": 1.1}},
                      "queue_opts": {"voice": "v6", "speed": 1.1, "tts_engine": "vieneu"},
                      **({"split_info": si} if keep_split_info else {})})
    durs = {}
    for k, s in enumerate(SUBS, 1):
        d = _mk(tmp_path, s, {"request": {"parent_job_id": P},
                              "stages": {"download": {"status": "done", "finished_at": "OLD",
                                                      "video_path": f"x/{P}_part_{k:02d}_of_02.mp4"},
                                         "asr": {"status": "done"}, "translate": {"status": "done"},
                                         "tts": {"status": "done", "voice": "v6"}, "mux": {"status": "done"}}})
        f = d / f"{P}_part_{k:02d}_of_02.mp4"
        f.write_bytes(b"p" * 2000)
        durs[str(f)] = part_durs[k - 1]
    durs[str(src)] = 19750.853

    def probe(v):
        return durs.get(str(v), 0.0)
    monkeypatch.setattr(split_parts, "probe_duration", probe)
    monkeypatch.setattr(render, "_find_video", lambda wd: src)
    monkeypatch.setattr(split_parts, "compute_smart_plan", lambda v, target_hours=2.5: [dict(p) for p in parts])
    cut = []
    monkeypatch.setattr(split_parts, "split_video_to_parts", lambda *a, **k: cut.append(1) or pytest.skip("cut"))
    return split_parts, cut


@pytest.mark.parametrize("keep_si", [True, False])
def test_resplit_reuses_parts_and_keeps_part_results(tmp_path, monkeypatch, keep_si):
    sp, cut = _split_env(tmp_path, monkeypatch, part_durs=[9876.9, 9874.0], keep_split_info=keep_si)
    r = sp.split_job_to_subjobs(P, work_root=tmp_path)
    assert r["reused"] is True and cut == []
    for s in SUBS:
        st = _rd(tmp_path, s)["stages"]
        assert st["tts"]["status"] == "done"                  # trước: tts → pending
        assert st["download"]["finished_at"] == "OLD"
        assert st["asr"]["status"] == "done" and st["mux"]["status"] == "done"
    si = _rd(tmp_path, P)["split_info"]
    assert si["reused_parts"] is True and si["source_sig"]["duration"] == 19750.853
    if keep_si:
        assert si["status"] == "merged"                       # không làm parent «chưa ghép»


def test_resplit_recuts_when_part_does_not_match_plan(tmp_path, monkeypatch):
    sp, cut = _split_env(tmp_path, monkeypatch, part_durs=[9000.0, 10750.0], keep_split_info=False)
    with pytest.raises(pytest.skip.Exception):
        sp.split_job_to_subjobs(P, work_root=tmp_path)
    assert cut == [1]


# ───────── ghép Full: kiểm mối nối ─────────

needs_ffmpeg = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="cần ffmpeg")


def _clip(path: Path, freq: int, profile: str):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=160x120:r=25",
                    "-f", "lavfi", "-i", f"sine=f={freq}:r=48000", "-t", "3", "-c:v", "libx264",
                    "-profile:v", profile, "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(path)],
                   check=True)


@needs_ffmpeg
def test_merge_checked_real_ffmpeg_joint_ok(tmp_path):
    import engines.split_parts as sp
    a, b = tmp_path / "a.mp4", tmp_path / "b.mp4"
    _clip(a, 440, "baseline")
    _clip(b, 660, "high")
    rep = sp.merge_parts_checked([a, b], tmp_path / "full.mp4", window=2.0)
    assert rep["ok"] and rep["mode"] == "copy" and len(rep["joints"]) == 1
    assert abs(rep["joints"][0]["t"] - sp.probe_duration(a)) < 0.01
    assert (tmp_path / "full.mp4").stat().st_size > 1000


@needs_ffmpeg
def test_merge_checked_falls_back_to_regen_then_fails_clearly(tmp_path, monkeypatch):
    import engines.split_parts as sp
    a, b = tmp_path / "a.mp4", tmp_path / "b.mp4"
    _clip(a, 440, "high")
    _clip(b, 660, "high")
    modes = []
    real_concat = sp._concat_run

    def concat(parts, out, mode="copy"):
        modes.append(mode)
        return real_concat(parts, out, mode)
    monkeypatch.setattr(sp, "_concat_run", concat)
    bad = "[h264 @ 0x1] Invalid NAL unit size (1234 > 99).\n[h264 @ 0x1] error while decoding MB 3 4"
    seq = [(0, bad), (0, "")]
    monkeypatch.setattr(sp, "_decode_window", lambda *a: seq.pop(0))
    rep = sp.merge_parts_checked([a, b], tmp_path / "full.mp4", window=1.0)
    assert rep["ok"] and rep["mode"] == "regen" and modes == ["copy", "regen"]
    assert not rep["attempts"][0]["ok"] and rep["attempts"][0]["joints"][0]["n_errors"] == 2
    monkeypatch.setattr(sp, "_decode_window", lambda *a: (0, bad))
    rep2 = sp.merge_parts_checked([a, b], tmp_path / "full2.mp4", window=1.0)
    assert rep2["ok"] is False and "mối nối" in rep2["message"]
    assert not (tmp_path / "full2.mp4").exists()


def test_dts_warning_is_not_decode_error(monkeypatch, tmp_path):
    import engines.split_parts as sp
    w = ("[null @ 0x5d] Application provided invalid, non monotonically increasing dts to muxer "
         "in stream 0: 1076 >= 1074")
    monkeypatch.setattr(sp, "_decode_window", lambda *a: (0, w + "\n" + w))
    r = sp.check_merge_joints(tmp_path / "x.mp4", [9875.8])
    assert r["ok"] and r["joints"][0]["dts_warnings"] == 2 and r["decode_errors"] == 0


def _merge_job_env(tmp_path, monkeypatch, *, status="split_done"):
    import engines.split_parts as sp
    _mk(tmp_path, P, {"stages": {}, "split_info": {"status": status, "sub_job_ids": SUBS}})
    for s in SUBS:
        d = _mk(tmp_path, s, {"stages": {"mux": {"status": "done"}}})
        (d / "output.mp4").write_bytes(b"o" * 200_000)
    full = tmp_path / P / "output_full.mp4"
    full.write_bytes(b"OLD" * 400_000)
    return sp, full


def test_merge_job_keeps_old_full_when_joint_bad(tmp_path, monkeypatch):
    sp, full = _merge_job_env(tmp_path, monkeypatch)
    monkeypatch.setattr(sp, "merge_parts_checked",
                        lambda parts, out, **k: {"ok": False, "message": "Ghép Full LỖI: mối nối", "attempts": []})
    r = sp.merge_job_parts(P, work_root=tmp_path)
    assert r["ok"] is False and "mối nối" in r["message"]
    assert full.read_bytes()[:3] == b"OLD"                    # trước: Full cũ bị xoá TRƯỚC khi ghép
    assert _rd(tmp_path, P)["split_info"]["merge_check"]["ok"] is False


def test_merge_job_skips_when_already_merged_and_parts_unchanged(tmp_path, monkeypatch):
    sp, full = _merge_job_env(tmp_path, monkeypatch, status="merged")
    t = time.time()
    for s in SUBS:
        os.utime(tmp_path / s / "output.mp4", (t - 100, t - 100))
    monkeypatch.setattr(sp, "merge_parts_checked", lambda *a, **k: pytest.fail("không được ghép đè"))
    r = sp.merge_job_parts(P, work_root=tmp_path)
    assert r["ok"] and r["skipped"] == "already_merged"


def test_merge_job_success_replaces_and_records_check(tmp_path, monkeypatch):
    sp, full = _merge_job_env(tmp_path, monkeypatch)

    def ok(parts, out, **k):
        Path(out).write_bytes(b"NEW" * 400_000)
        return {"ok": True, "mode": "copy", "joints": [{"t": 1.0, "ok": True, "n_errors": 0, "dts_warnings": 3}],
                "attempts": [{"mode": "copy"}], "concat_dts_warnings": 3}
    monkeypatch.setattr(sp, "merge_parts_checked", ok)
    r = sp.merge_job_parts(P, work_root=tmp_path)
    assert r["ok"] and r["merge_check"]["concat_dts_warnings"] == 3
    out = tmp_path / P / "output.mp4"
    assert out.read_bytes()[:3] == b"NEW" and not (tmp_path / P / "output.merging.mp4").exists()
    m = _rd(tmp_path, P)
    assert m["split_info"]["status"] == "merged" and m["stages"]["mux"]["merge_check"]["ok"] is True
