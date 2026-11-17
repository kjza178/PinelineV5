"""2026-11-17: HOLD QA kẹt vô hạn (ff8e66b475a7) — phase mồ côi + timeout + resume."""
import json
import time

try:
    import agents.agent_brain as ab  # V5
except ImportError:
    import agent_brain as ab


def _job(tmp_path, agent, tts="running"):
    wd = tmp_path / "j1"
    wd.mkdir()
    (wd / "manifest.json").write_text(json.dumps({
        "job_id": "j1", "agent": agent,
        "stages": {"translate": {"status": "done"}, "tts": {"status": tts}},
    }), encoding="utf-8")
    return wd


def test_phase_stale_tts_running_while_held_is_not_post_tts(tmp_path):
    wd = _job(tmp_path, {"qa_blocked": True, "held_at": "qa_brain"})
    assert ab._qa_pipeline_phase(wd)["phase"] != "post_tts"


def test_phase_real_tts_running_is_post_tts(tmp_path):
    wd = _job(tmp_path, {})
    assert ab._qa_pipeline_phase(wd)["phase"] == "post_tts"


def test_hold_timeout_soft_kinds_resumes(tmp_path, monkeypatch):
    wd = _job(tmp_path, {"qa_blocked": True, "held_at": "qa_brain"}, tts="pending")
    calls = []
    monkeypatch.setattr(ab, "_telegram", lambda *a, **k: None)
    monkeypatch.setattr(ab, "_emit", lambda *a, **k: None)
    monkeypatch.setenv("QA_HOLD_MAX_MIN", "1")
    hooks = {"resume": lambda jid: calls.append(jid) or {"ok": True}}
    r = {"high_i": [380, 2483], "high_sample": [{"sev": "high", "kind": "name_echo"}] * 2}
    st = {}
    ab._qa_hold_timeout(st, hooks, tmp_path, wd, "j1", r)
    assert calls == []
    st["qa_hold"]["j1"]["since"] = time.time() - 120
    ab._qa_hold_timeout(st, hooks, tmp_path, wd, "j1", r)
    assert calls == ["j1"]


def test_hold_timeout_hard_kind_does_not_resume(tmp_path, monkeypatch):
    wd = _job(tmp_path, {"qa_blocked": True, "held_at": "qa_brain"}, tts="pending")
    calls = []
    monkeypatch.setattr(ab, "_telegram", lambda *a, **k: None)
    monkeypatch.setenv("QA_HOLD_MAX_MIN", "1")
    hooks = {"resume": lambda jid: calls.append(jid)}
    r = {"high_i": [5], "high_sample": [{"sev": "high", "kind": "empty_vi"}]}
    st = {"qa_hold": {"j1": {"since": time.time() - 120, "sig": "5"}}}
    ab._qa_hold_timeout(st, hooks, tmp_path, wd, "j1", r)
    assert calls == []
