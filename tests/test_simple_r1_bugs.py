"""G1.1 / R1.1–R1.5 — regress bug simple đã tái hiện 2026-11-14."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from engines.translate_simple import gate, stage_draft, stage_review, validate
from engines.translate_simple.plan_view import PlanView
from engines.translate_simple.script_store import ScriptStore


def test_r14_now_iso_has_timezone():
    from core.timeutil import now_iso
    from engines.translate_simple.pipeline import _now
    s = _now()
    assert "+" in s or s.endswith("Z") or "+00:00" in s
    assert "T" in s
    assert abs(__import__("time").time() - __import__("core.timeutil", fromlist=["to_epoch"]).to_epoch(now_iso())) < 5


def test_r11_rereview_cloud_fail_clears_rv(tmp_path):
    """Soát lại + cloud chết: phải bỏ rv cũ → n_ok=0, không done giả."""
    wd = tmp_path / "j"
    wd.mkdir()
    rows = [
        {"i": 0, "zh": "你好", "vi": "Xin chào", "rv": 1},
        {"i": 1, "zh": "谢谢", "vi": "Cảm ơn", "rv": 1},
    ]
    (wd / "script.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    store = ScriptStore(wd)
    store.load()
    pv = PlanView({"pronouns": [], "characters": []})

    def _boom(*a, **k):
        raise RuntimeError("429 rate limit aurora")

    with patch.object(stage_review, "call_llm", _boom):
        with patch.object(stage_review.cfg, "workers", lambda: 1):
            with patch.object(stage_review.cfg, "batch", lambda: 30):
                st = stage_review.run(store, pv, model="x", rereview=True)
    assert st["n_todo"] == 2
    assert st["n_ok"] == 0
    assert st["n_left"] == 2
    assert all(not r.get("rv") for r in store.rows)
    cloud_dead = st["n_todo"] > 0 and st["n_ok"] == 0
    assert cloud_dead is True


def test_r12_plan_usable_rejects_empty_failed():
    assert stage_draft._plan_usable(None) is False
    assert stage_draft._plan_usable({"plan_status": "failed", "pronouns": [], "characters": []}) is False
    assert stage_draft._plan_usable({"pronouns": [], "characters": [], "terms": []}) is False
    assert stage_draft._plan_usable({"pronouns": [{"who": "A", "to": "B"}], "characters": []}) is True
    assert stage_draft._plan_usable({"plan_status": "ok", "pronouns": [], "characters": []}) is True


def test_r12_failed_plan_not_written_as_glossary(tmp_path, monkeypatch):
    wd = tmp_path / "j"
    wd.mkdir()
    segs = [{"i": 0, "start": 0, "end": 1, "text": "你好"}]

    def _fail(*a, **k):
        raise RuntimeError("plan upload failed")

    monkeypatch.setattr("translate.build_plan", _fail, raising=False)
    import engines.translate as T
    monkeypatch.setattr(T, "build_plan", _fail)
    monkeypatch.setattr(T, "ensure_hard_terms", lambda p: p)
    monkeypatch.setattr(T, "_ocr_name_hints", lambda w: None)

    plan = stage_draft.build_plan(wd, segs, "Tiếng Việt", force=True)
    assert plan.get("plan_status") == "failed"
    assert not (wd / "glossary.json").exists()
    assert (wd / "glossary.plan_failed.json").exists()


def test_r12_gate_hold_on_plan_failed():
    g = gate.decide(n_rows=10, n_asr=10, coverage_gap=0, n_missing=0, n_unreviewed=0,
                    flags={}, plan_failed=True)
    assert g["status"] == "hold"
    assert any("plan" in r.lower() for r in g["reasons"])


def test_r13_code_error_not_swallowed_as_lot_fail(tmp_path):
    wd = tmp_path / "j"
    wd.mkdir()
    rows = [{"i": 0, "zh": "a", "vi": "b", "rv": 0}]
    (wd / "script.json").write_text(json.dumps(rows), encoding="utf-8")
    store = ScriptStore(wd)
    store.load()
    pv = PlanView({})

    def _code(*a, **k):
        raise TypeError("bug in prompt builder")

    with patch.object(stage_review, "call_llm", _code):
        with patch.object(stage_review.cfg, "workers", lambda: 1):
            with pytest.raises(TypeError, match="bug in prompt"):
                stage_review.run(store, pv, model="x", rereview=False)


def test_r15_kin_speech_verb_not_violation():
    """«Chị bảo tôi tới» — không cờ KIN «Chị» (ngôi 3 tường thuật). «tôi» lệch cặp anh–em vẫn có thể cờ riêng."""
    v = validate.pronoun_violations("Chị bảo tôi tới.", ["anh"], ["em"])
    assert not any(x.lower() == "chị" for x in v), v
    v2 = validate.pronoun_violations("Anh nói với em rồi.", ["anh"], ["em"])
    assert not any(x.lower() == "anh" for x in v2), v2
    # vẫn bắt lệch ngôi 1 thật
    v3 = validate.pronoun_violations("Tôi bảo em tới.", ["anh"], ["em"])
    assert any(x.lower() == "tôi" for x in v3), v3
    assert validate.pronoun_violations("Anh bảo em tới.", ["anh"], ["em"]) == []
