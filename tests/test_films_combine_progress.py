# -*- coding: utf-8 -*-
"""films_combine: status + reject <2 jobs + busy lock."""
from __future__ import annotations

import time

import engines.films_combine as fc


def test_status_ok_shape():
    st = fc.status()
    assert st.get("ok") is True
    assert "phase" in st
    assert "log" in st
    assert isinstance(st["log"], list)


def test_start_needs_two_jobs():
    r = fc.start("http://127.0.0.1:8801", ["only_one"])
    assert r.get("ok") is False
    assert "2" in (r.get("error") or "")


def test_progress_updates_state(monkeypatch, tmp_path):
    fc.set_log_dir(tmp_path)
    calls = []

    def fake_combine(base, job_ids, **kw):
        on_p = kw.get("on_progress")
        assert on_p
        on_p({"phase": "concat", "text": "part 1/2", "pct": 40})
        calls.append(list(job_ids))
        time.sleep(0.05)
        on_p({"phase": "manifest", "text": "manifest", "pct": 90})
        return {
            "ok": True,
            "job_id": "merged_test",
            "title": "T",
            "title_vi": "T VI",
            "duration_sec": 10,
            "size_mb": 1.0,
            "mode": "test",
            "merged_from": list(job_ids),
            "publish": None,
        }

    class _FakeFeeder:
        combine_rendered_jobs = staticmethod(fake_combine)

    monkeypatch.setattr(fc, "_load_feeder", lambda: _FakeFeeder)

    # Wait any previous worker
    deadline = time.time() + 2
    while fc.status().get("running") and time.time() < deadline:
        time.sleep(0.05)

    r = fc.start("http://127.0.0.1:8801", ["a111", "b222"])
    assert r.get("ok") and r.get("started")
    busy = fc.start("http://127.0.0.1:8801", ["c333", "d444"])
    assert busy.get("busy") or busy.get("ok") is False

    deadline = time.time() + 3
    while fc.status().get("running") and time.time() < deadline:
        time.sleep(0.05)
    st = fc.status()
    assert st.get("phase") == "done"
    assert st.get("result", {}).get("job_id") == "merged_test"
    assert any("part 1/2" in x or "concat" in x for x in st.get("log") or [])
    assert calls == [["a111", "b222"]]
