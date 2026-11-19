"""2026-11-18: Aurora = DỰ PHÒNG thật cho soát simple — DeepSeek soát chính, chỉ lô lỗi mới làm lại bằng Aurora."""
import json

try:
    from engines.translate_simple import cfg, stage_review  # V5
    from engines.translate_simple.plan_view import PlanView
    from engines.translate_simple.script_store import ScriptStore
except ImportError:
    from translate_simple import cfg, stage_review
    from translate_simple.plan_view import PlanView
    from translate_simple.script_store import ScriptStore

PLAN = {"characters": [{"zh": "林凡", "vi": "Lâm Phàm"}], "terms": [], "pronouns": []}


def _wd(tmp_path, rb):
    wd = tmp_path / "j"
    wd.mkdir()
    (wd / "manifest.json").write_text(json.dumps({"queue_opts": {"review_backup": rb}}), encoding="utf-8")
    segs = [{"i": k, "start": k, "end": k + 1, "text": f"台词{k}"} for k in range(12)]
    (wd / "asr.json").write_text(json.dumps(segs, ensure_ascii=False), encoding="utf-8")
    st = ScriptStore(wd)
    st.ensure_from_asr(segs)
    return wd, st


def _cfg(monkeypatch, vals):
    monkeypatch.setattr(cfg, "get", lambda k, d=None: vals.get(k, d))


def test_models_primary_is_deepseek_even_with_aurora_backup(tmp_path, monkeypatch):
    _cfg(monkeypatch, {"REVIEW_MODEL": "deepseek/deepseek-flash", "AURORA_REVIEW_MODEL": "chatgpt/gpt-6"})
    import engines.translate as T
    monkeypatch.setattr(T, "_rmodel", lambda: "deepseek/deepseek-flash")
    wd, _ = _wd(tmp_path, "aurora_parallel")
    assert cfg.review_model(wd) == "deepseek/deepseek-flash"
    assert cfg.backup_model(wd) == "chatgpt/gpt-6"
    wd2 = tmp_path / "k"
    wd2.mkdir()
    (wd2 / "manifest.json").write_text(json.dumps({"queue_opts": {"review_backup": "off"}}), encoding="utf-8")
    assert cfg.backup_model(wd2) is None


def test_failed_lots_go_to_backup_only(tmp_path, monkeypatch):
    wd, st = _wd(tmp_path, "aurora_parallel")
    _cfg(monkeypatch, {"SIMPLE_BATCH": "4", "SIMPLE_BACKUP_BATCH": "30"})
    monkeypatch.setattr(cfg, "workers", lambda m=None: 1)
    monkeypatch.setattr(cfg, "batch_for_rows", lambda n, w, explicit=None: 4)
    calls = []

    def fake_call(system, user, want, *, model, stop_check=None, label="", pair_sink=None):
        calls.append((model, sorted(want)))
        if model == "deepseek/deepseek-flash" and 4 in want:          # lô thứ 2 của DeepSeek lỗi
            raise RuntimeError("DeepSeek (deepseek-flash) thất bại sau 4 lần: 503")
        return {i: {"vi": f"v{i}", "spk": "?", "to": "?", "conf": 0.9} for i in want}
    monkeypatch.setattr(stage_review, "call_llm", fake_call)
    stats = stage_review.run(st, PlanView(PLAN), model="deepseek/deepseek-flash",
                             backup_model="chatgpt/gpt-6")
    assert stats["n_ok"] == 12 and stats["n_left"] == 0 and stats["n_fail_lots"] == 1
    assert stats["backup"] == {"model": "chatgpt/gpt-6", "n": 4, "ok": 4}
    ds = [w for m, w in calls if m == "deepseek/deepseek-flash"]
    au = [w for m, w in calls if m == "chatgpt/gpt-6"]
    assert len(ds) == 3 and au == [[4, 5, 6, 7]]                       # Aurora CHỈ làm lô lỗi


def test_no_backup_retries_same_model(tmp_path, monkeypatch):
    wd, st = _wd(tmp_path, "off")
    _cfg(monkeypatch, {})
    monkeypatch.setattr(cfg, "workers", lambda m=None: 1)
    monkeypatch.setattr(cfg, "batch_for_rows", lambda n, w, explicit=None: 4)
    seen = {"n": 0}
    calls = []

    def fake_call(system, user, want, *, model, stop_check=None, label="", pair_sink=None):
        calls.append(model)
        seen["n"] += 1
        if seen["n"] == 1:
            raise RuntimeError("503")
        return {i: {"vi": f"v{i}", "spk": "?", "to": "?", "conf": 0.9} for i in want}
    monkeypatch.setattr(stage_review, "call_llm", fake_call)
    stats = stage_review.run(st, PlanView(PLAN), model="deepseek/deepseek-flash")
    assert stats["n_left"] == 0 and set(calls) == {"deepseek/deepseek-flash"} and "backup" not in stats
