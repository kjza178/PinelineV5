"""Studio SOP seat-lock: không GPU heal/fill khi queue.current là job khác."""
from __future__ import annotations

import agents.agent_heal as ah


def test_on_queue_seat_parent_part():
    assert ah._on_queue_seat("abc", None) is True
    assert ah._on_queue_seat("abc", "abc") is True
    assert ah._on_queue_seat("abc_p01", "abc") is True
    assert ah._on_queue_seat("abc", "abc_p02") is True
    assert ah._on_queue_seat("other_p01", "abc") is False
    assert ah._on_queue_seat("xyz", "abc") is False


def test_other_seat_busy(monkeypatch):
    class _JQ:
        _current = "seatjob"

        @staticmethod
        def queue_state():
            return {"current": "seatjob"}

    import sys
    monkeypatch.setitem(sys.modules, "core.job_queue", _JQ)
    assert ah.other_seat_busy("seatjob") is None
    assert ah.other_seat_busy("seatjob_p02") is None
    assert ah.other_seat_busy("other") == "queue.current=seatjob"
    _JQ._current = None

    class _JQ2:
        _current = None

        @staticmethod
        def queue_state():
            return {"current": None}

    monkeypatch.setitem(sys.modules, "core.job_queue", _JQ2)
    assert ah.other_seat_busy("other") is None


def test_heal_skips_translate_fill_when_other_seat(tmp_path, monkeypatch):
    class _JQ:
        _current = "busyjob"

        @staticmethod
        def queue_state():
            return {"current": "busyjob"}

    import sys
    monkeypatch.setitem(sys.modules, "core.job_queue", _JQ)

    jid = "waitingjob"
    wd = tmp_path / jid
    wd.mkdir()
    (wd / "manifest.json").write_text(
        '{"stages":{"download":{"status":"done"},"asr":{"status":"done"},'
        '"translate":{"status":"pending"},"tts":{"status":"pending"},'
        '"mux":{"status":"pending"}},"request":{}}',
        encoding="utf-8",
    )
    (wd / "asr.json").write_text("[]", encoding="utf-8")
    (wd / "script.json").write_text(
        '[{"i":0,"zh":"你好","vi":""},{"i":1,"zh":"谢谢","vi":""}]',
        encoding="utf-8",
    )

    called = {"fill": 0}

    def _fill(_jid):
        called["fill"] += 1
        return {"started": True}

    r = ah.heal_job(
        tmp_path,
        jid,
        apply=True,
        level="safe",
        hooks={"translate_fill": _fill, "heal_stale": lambda _j: {"ok": True}},
    )
    assert r.get("ok") is True
    fills = [x for x in (r.get("results") or []) if x.get("action") == "translate_fill"]
    assert fills, r
    assert fills[0]["result"].get("blocked_by_seat") is True
    assert called["fill"] == 0
