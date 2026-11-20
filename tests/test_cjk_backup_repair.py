"""2026-11-20: còn CJK sau vá DeepSeek → 1 lượt vá bằng backup (Aurora), không park ngay."""
from __future__ import annotations

import json
from pathlib import Path

try:
    from engines.translate_simple import cfg, pipeline, repair, validate
    from engines.translate_simple.plan_view import PlanView
    from engines.translate_simple.script_store import ScriptStore
except ImportError:
    from translate_simple import cfg, pipeline, repair, validate
    from translate_simple.plan_view import PlanView
    from translate_simple.script_store import ScriptStore

PLAN = {"characters": [{"zh": "赢怀虚", "vi": "Ngân Hoài Hư"}], "terms": [], "pronouns": []}


def test_pipeline_backup_repairs_leftover_cjk(tmp_path, monkeypatch):
    wd = tmp_path / "j"
    wd.mkdir()
    (wd / "manifest.json").write_text(
        json.dumps({"queue_opts": {"review_backup": "aurora_parallel"}}), encoding="utf-8"
    )
    segs = [{"i": 0, "start": 0, "end": 1, "text": "短暂截取一下赢怀虚的投影，"}]
    (wd / "asr.json").write_text(json.dumps(segs, ensure_ascii=False), encoding="utf-8")
    st = ScriptStore(wd)
    st.ensure_from_asr(segs)
    st.rows[0]["vi"] = "Tạm thời cắt lấy một投影 của Ngân Hoài Hư,"
    st.rows[0]["rv"] = 1
    st.save()

    monkeypatch.setattr(cfg, "backup_model", lambda work_dir=None: "chatgpt/gpt-6")
    monkeypatch.setattr(cfg, "repair_rounds", lambda: 1)
    monkeypatch.setattr(cfg, "batch", lambda: 30)
    monkeypatch.setattr(cfg, "ctx", lambda: 0)

    calls: list[str] = []

    def fake_call(system, user, want, *, model, stop_check=None, label="", pair_sink=None):
        calls.append(str(model))
        if "chatgpt" in str(model):
            return {0: {"vi": "Tạm thời cắt lấy một hình chiếu của Ngân Hoài Hư,",
                        "spk": "?", "to": "?", "conf": 0.9}}
        # DeepSeek «vá» nhưng vẫn để sót CJK
        return {0: {"vi": "Tạm thời cắt lấy một投影 của Ngân Hoài Hư,",
                    "spk": "?", "to": "?", "conf": 0.9}}

    # Patch đúng module mà repair đang dùng (V2/V4: translate_simple · V5: engines.translate_simple)
    monkeypatch.setattr(repair.stage_review, "call_llm", fake_call)

    flags = validate.validate(st.rows, PlanView(PLAN), 0.7)
    assert any(f["code"] == "cjk" for f in flags[0])

    # giả pipeline đoạn vá: main rồi backup hard
    model = "deepseek/deepseek-flash"
    bmodel = "chatgpt/gpt-6"
    flags, rlog = repair.run(st, PlanView(PLAN), flags, model=model, rounds=1)
    hard = {i: fl for i, fl in flags.items()
            if any((f.get("code") or "") in ("cjk", "empty") for f in fl)}
    assert hard
    hard_left, blog = repair.run(st, PlanView(PLAN), hard, model=bmodel, rounds=1)
    assert hard_left == {}
    assert "投影" not in (st.rows[0].get("vi") or "")
    assert "hình chiếu" in (st.rows[0].get("vi") or "")
    assert calls == [model, bmodel]
