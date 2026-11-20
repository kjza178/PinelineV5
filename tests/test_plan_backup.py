"""2026-11-20: plan luôn main + backup (PLAN_MODEL_BACKUP / Aurora)."""
from __future__ import annotations

import json
from pathlib import Path

try:
    from engines.translate_simple import cfg
except ImportError:
    from translate_simple import cfg


def _cfg(monkeypatch, vals):
    monkeypatch.setattr(cfg, "get", lambda k, d=None: vals.get(k, d))


def test_plan_models_main_then_backup(monkeypatch):
    _cfg(monkeypatch, {
        "PLAN_MODEL": "deepseek/deepseek-flash",
        "PLAN_MODEL_BACKUP": "chatgpt/gpt-6",
        "AURORA_REVIEW_MODEL": "chatgpt/gpt-6",
    })
    assert cfg.plan_model() == "deepseek/deepseek-flash"
    assert cfg.plan_backup_model() == "chatgpt/gpt-6"
    assert cfg.plan_models() == ["deepseek/deepseek-flash", "chatgpt/gpt-6"]


def test_plan_backup_defaults_to_aurora(monkeypatch):
    _cfg(monkeypatch, {
        "PLAN_MODEL": "deepseek/deepseek-flash",
        "AURORA_REVIEW_MODEL": "chatgpt/gpt-6",
    })
    assert cfg.plan_backup_model() == "chatgpt/gpt-6"


def test_plan_backup_none_when_same_as_main(monkeypatch):
    _cfg(monkeypatch, {
        "PLAN_MODEL": "chatgpt/gpt-6",
        "PLAN_MODEL_BACKUP": "chatgpt/gpt-6",
    })
    assert cfg.plan_backup_model() is None
    assert cfg.plan_models() == ["chatgpt/gpt-6"]


def test_review_backup_default_on_when_key_missing(tmp_path, monkeypatch):
    _cfg(monkeypatch, {
        "REVIEW_MODEL": "deepseek/deepseek-flash",
        "AURORA_REVIEW_MODEL": "chatgpt/gpt-6",
    })
    import translate as T
    monkeypatch.setattr(T, "_rmodel", lambda: "deepseek/deepseek-flash")
    wd = tmp_path / "j"
    wd.mkdir()
    (wd / "manifest.json").write_text(json.dumps({"queue_opts": {}}), encoding="utf-8")
    assert cfg.backup_model(wd) == "chatgpt/gpt-6"
    (wd / "manifest.json").write_text(
        json.dumps({"queue_opts": {"review_backup": "off"}}), encoding="utf-8"
    )
    assert cfg.backup_model(wd) is None


def test_build_plan_tries_backup_on_a7_fail(tmp_path, monkeypatch):
    import translate as T
    from translate_simple import stage_draft

    segs = [{"i": i, "start": i, "end": i + 1, "text": f"台词{i}好"} for i in range(8)]
    (tmp_path / "asr.json").write_text(json.dumps(segs, ensure_ascii=False), encoding="utf-8")
    calls: list[str] = []

    def fake_a7(work_dir, segments, target="Tiếng Việt", *, model=None, name_hints=None, series_plan=None):
        calls.append(str(model))
        if model and "deepseek" in str(model):
            return None
        return {
            "characters": [{"zh": "林", "vi": "Lâm"}],
            "terms": [{"zh": "剑", "vi": "kiếm"}],
            "pronouns": [],
            "plan_status": "ok",
        }

    monkeypatch.setattr(stage_draft, "build_full_movie_plan", fake_a7)
    monkeypatch.setattr(T, "_plan_mode", lambda: "file")
    monkeypatch.setattr(cfg, "full_plan_enabled", lambda: True)
    monkeypatch.setattr(cfg, "plan_models", lambda work_dir=None: [
        "deepseek/deepseek-flash", "chatgpt/gpt-6",
    ])
    monkeypatch.setattr(T, "_build_plan_from_file", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("skip file")))
    monkeypatch.setattr(T, "_build_plan_sample", lambda *a, **k: {"characters": [], "terms": []})
    monkeypatch.setattr(T, "_normalize_plan_data", lambda d: d if isinstance(d, dict) else {})

    data = T.build_plan(segs, work_dir=tmp_path, model="deepseek/deepseek-flash")
    assert calls == ["deepseek/deepseek-flash", "chatgpt/gpt-6"]
    assert (data.get("_meta") or {}).get("plan_model_role") == "backup"
    assert (data.get("_meta") or {}).get("plan_model") == "chatgpt/gpt-6"
