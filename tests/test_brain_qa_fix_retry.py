"""2026-11-17: Brain tự xử lý cờ QA high (agent_qa_fix) + tự thử lại stage failed (agent_retry)."""
import json
import time

try:
    import agents.agent_qa_fix as qf
    import agents.agent_retry as ar
    from agents.agent_quality import scan_script
except ImportError:
    import agent_qa_fix as qf
    import agent_retry as ar
    from agent_quality import scan_script


ROWS = [
    {"i": 1, "zh": "圣者你也是圣者废话。", "vi": "Thánh Giả cậu cũng là Thánh Giả nói nhảm."},
    {"i": 2, "zh": "你好。", "vi": ""},
    {"i": 3, "zh": "走吧。", "vi": "Đi thôi."},
]


def test_qa_ack_suppresses_flag():
    rows = [dict(r) for r in ROWS]
    assert any(f["kind"] == "name_echo" for f in scan_script(rows))
    rows[0]["qa_ack"] = ["name_echo"]
    assert not any(f["kind"] == "name_echo" for f in scan_script(rows))


def test_fix_qa_job_ack_and_fix(tmp_path, monkeypatch):
    (tmp_path / "script.json").write_text(json.dumps(ROWS, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(qf, "_llm_batch", lambda cases: [
        {"i": 1, "kind": "name_echo", "verdict": "false_positive", "vi": "", "why": "đúng nghĩa"},
        {"i": 2, "kind": "empty_vi", "verdict": "fix", "vi": "Xin chào.", "why": "trống"},
    ])
    r = qf.fix_qa_job(tmp_path)
    assert r["n_ack"] == 1 and r["n_fixed"] == 1
    rows = json.loads((tmp_path / "script.json").read_text(encoding="utf-8"))
    assert rows[1]["vi"] == "Xin chào."
    assert not [f for f in scan_script(rows) if f["sev"] == "high"]
    # lần 2: không còn case → không gọi LLM
    monkeypatch.setattr(qf, "_llm_batch", lambda cases: (_ for _ in ()).throw(AssertionError("gọi LLM")))
    assert qf.fix_qa_job(tmp_path)["n_cases"] == 0


def test_fix_qa_job_llm_error_does_not_burn_tries(tmp_path, monkeypatch):
    (tmp_path / "script.json").write_text(json.dumps(ROWS, ensure_ascii=False), encoding="utf-8")
    def boom(cases):
        raise RuntimeError("timeout")
    monkeypatch.setattr(qf, "_llm_batch", boom)
    assert qf.fix_qa_job(tmp_path)["ok"] is False
    rows = json.loads((tmp_path / "script.json").read_text(encoding="utf-8"))
    assert "qa_fix_try" not in rows[0]


def _job(root, jid, stages, agent=None):
    d = root / jid
    d.mkdir()
    (d / "manifest.json").write_text(json.dumps({"job_id": jid, "stages": stages, "agent": agent or {}}),
                                     encoding="utf-8")
    return d


def test_retry_failed_backoff_and_giveup(tmp_path, monkeypatch):
    monkeypatch.setattr(ar, "_queued_ids", lambda: set())
    monkeypatch.setenv("RETRY_BACKOFF_MIN", "5")
    monkeypatch.setenv("RETRY_MAX", "2")
    d = _job(tmp_path, "j1", {"tts": {"status": "failed", "error": "CUDA error: launch failure"}})
    resumed, notes = [], []
    hooks = {"resume": lambda jid: resumed.append(jid) or {"ok": True}, "job_active": lambda jid: None}
    st = {}
    t0 = time.time()
    assert ar.retry_failed_jobs(tmp_path, st, hooks, log=lambda m: None, notify=notes.append, now=t0) == []
    r = ar.retry_failed_jobs(tmp_path, st, hooks, log=lambda m: None, notify=notes.append, now=t0 + 301)
    assert resumed == ["j1"] and r[0]["try"] == 1
    m = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    assert m["stages"]["tts"]["status"] == "pending"
    # fail lại → thử lần 2 sau backoff, rồi bỏ cuộc
    m["stages"]["tts"]["status"] = "failed"
    (d / "manifest.json").write_text(json.dumps(m), encoding="utf-8")
    ar.retry_failed_jobs(tmp_path, st, hooks, log=lambda m: None, notify=notes.append, now=t0 + 700)
    assert resumed == ["j1", "j1"]
    m = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    m["stages"]["tts"]["status"] = "failed"
    (d / "manifest.json").write_text(json.dumps(m), encoding="utf-8")
    ar.retry_failed_jobs(tmp_path, st, hooks, log=lambda m: None, notify=notes.append, now=t0 + 1200)
    assert resumed == ["j1", "j1"] and any("cần người xem" in n for n in notes)


def test_retry_skips_notify_only_held_stopped(tmp_path, monkeypatch):
    monkeypatch.setattr(ar, "_queued_ids", lambda: set())
    _job(tmp_path, "a", {"tts": {"status": "failed", "error": "chưa chọn giọng"}})
    _job(tmp_path, "b", {"mux": {"status": "failed", "error": "x"}}, {"qa_blocked": True, "held_at": "qa_brain"})
    c = _job(tmp_path, "c", {"mux": {"status": "failed", "error": "x"}})
    (c / ".stop").write_text("1")
    resumed, notes = [], []
    hooks = {"resume": lambda jid: resumed.append(jid) or {"ok": True}, "job_active": lambda jid: None}
    ar.retry_failed_jobs(tmp_path, {}, hooks, log=lambda m: None, notify=notes.append, now=time.time() + 10_000)
    assert resumed == [] and len(notes) == 1 and "a " in notes[0]
