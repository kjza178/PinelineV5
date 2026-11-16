"""fix 2026-11-11 translate-b1 — chặn hỏng dữ liệu ở bước Dịch/REVIEW (V2, layout phẳng).

C1  REVIEW trả rỗng / JSON cụt / {} → LÔ LỖI (không rv); fixes=[] hợp lệ → rv.
C2  câu manual (người sửa tay) không bị REVIEW / name pass / pronoun pass / register policy /
    pronoun-QA GPT / hậu kỳ ghi đè vi.
C3  «cậu» chỉ thay khi là đại từ ngôi 2 độc lập («Cậu ấy», «cậu ruột», «ông cậu» giữ nguyên).
C9  fallback local khi REVIEW song song: switch_preset đúng 1 lần; 413 → chia lô, không switch;
    lỗi 400/parse/chuỗi 'token'/'500' không switch; pytest không bao giờ switch thật.
T18 run_translate giữ trường thêm của asr.json.

Thuần: không HTTP, không LLM, không GPU (chat/review_batch/switch_preset đều monkeypatch).
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import pytest

import engines.translate as T
from engines.llm import LLMUnavailable


# ───────────────────────── helpers ─────────────────────────

def _rows(n: int) -> list[dict]:
    return [{"i": i, "start": i, "end": i + 1, "zh": f"zh{i}", "vi": f"vi{i}"} for i in range(n)]


def _job(tmp_path: Path, rows: list[dict]) -> Path:
    wd = tmp_path / "job"
    wd.mkdir()
    (wd / "script.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    (wd / "manifest.json").write_text(
        json.dumps({"stages": {"translate": {"status": "done"}}}), encoding="utf-8"
    )
    return wd


def _review_env(monkeypatch, workers: int = 1, extra_cfg: dict | None = None):
    # translate-b2: REVIEW_CLOUD_RETRY=0 → test đường C9/B1 trực tiếp (retry cloud có test riêng)
    cfg = {"REVIEW_RETRY_BACKOFF_SEC": "0", "AUTO_SWITCH_PRESETS": "0",
           "REVIEW_PRONOUN_MASK": "0", "REVIEW_PRESET": "qwen-test", "REVIEW_CLOUD_RETRY": "0"}
    cfg.update(extra_cfg or {})
    monkeypatch.setattr(T, "run_review_pass1_full_vi", lambda wd_, rows_, plan, model=None: plan)
    monkeypatch.setattr(T, "_resolve_review_model", lambda wd_, m=None: "chatgpt/test")
    monkeypatch.setattr(T, "_review_parallel_workers", lambda wd_, m: workers)
    monkeypatch.setattr(T, "is_local", lambda m: False)
    monkeypatch.setattr(T, "unload_local", lambda m: None)
    monkeypatch.setattr(T, "_cfg_get", lambda k, d=None: cfg.get(k, d))
    # hậu kỳ LLM ngoài phạm vi test → tắt
    import engines.pronoun_consistency as PC
    monkeypatch.setattr(PC, "run_post_translate_consistency",
                        lambda wd_, rows_, plan, fix_with_gpt=True: {"ok": True})
    try:
        import agents.agent_hang_fix as agent_hang_fix
        monkeypatch.setattr(agent_hang_fix, "fix_hang_job", lambda *a, **k: {"skipped": True})
    except Exception:  # noqa: BLE001
        pass
    try:
        import engines.series_glossary as series_glossary
        monkeypatch.setattr(series_glossary, "save_from", lambda *a, **k: None)
    except Exception:  # noqa: BLE001
        pass


def _read(wd: Path) -> dict[int, dict]:
    return {r["i"]: r for r in json.loads((wd / "script.json").read_text(encoding="utf-8"))}


# ───────────────────────── C1 ─────────────────────────

_BAD_OUTPUTS = [
    pytest.param("", id="rong"),
    pytest.param("   \n", id="khoang-trang"),
    pytest.param('{"fixes":[{"i":1,"vi":"Xin chào cậu nhé', id="json-cut"),
    pytest.param('{"fixes":[{"i":1,"vi":"Một"},{"i":2,"vi":"Hai', id="json-cut-giua-lo"),
    pytest.param("{}", id="object-rong"),
    pytest.param('{"items":[]}', id="thieu-fixes"),
    pytest.param('{"fixes": null}', id="fixes-null"),
    pytest.param('```json\n{"fixes":[{"i":1,"vi":"x"}', id="fence-mo-khong-dong"),
    pytest.param("Xin lỗi, tôi không thể giúp.", id="van-xuoi"),
]


@pytest.mark.parametrize("out", _BAD_OUTPUTS)
def test_c1_bad_output_is_failed_chunk(monkeypatch, out):
    monkeypatch.setattr(T, "chat", lambda *a, **k: out)
    monkeypatch.setattr(T, "_cfg_get", lambda k, d=None: {"REVIEW_PRONOUN_MASK": "0"}.get(k, d))
    switched = []
    import tools.preset_switcher as preset_switcher
    monkeypatch.setattr(preset_switcher, "switch_preset", lambda *a, **k: switched.append(a) or True)
    rows = _rows(3)
    fixes, _m = T._review_chunk_with_fallback(
        rows, rows, "", [], target="vi", rmodel="chatgpt/x", plan={}, exemplars_pool=rows,
    )
    assert fixes is None, f"output hỏng {out!r} phải là lô lỗi, nhận {fixes!r}"
    assert not switched, "lỗi output không được đổi preset GPU"


@pytest.mark.parametrize("out", [
    '{"fixes":[]}',
    '```json\n{"fixes": []}\n```',
    '{"fixes":[],}',
    '{"fixes":[]} -- hết',
    "[]",
])
def test_c1_valid_no_fix_is_ok(monkeypatch, out):
    monkeypatch.setattr(T, "chat", lambda *a, **k: out)
    monkeypatch.setattr(T, "_cfg_get", lambda k, d=None: {"REVIEW_PRONOUN_MASK": "0"}.get(k, d))
    rows = _rows(3)
    fixes, _m = T._review_chunk_with_fallback(
        rows, rows, "", [], target="vi", rmodel="chatgpt/x", plan={}, exemplars_pool=rows,
    )
    assert fixes == {}


def test_c1_run_review_empty_output_not_rv(monkeypatch, tmp_path):
    wd = _job(tmp_path, _rows(8))
    _review_env(monkeypatch)
    monkeypatch.setattr(T, "chat", lambda *a, **k: "")
    with pytest.raises(RuntimeError, match="REVIEW lỗi"):
        T.run_review(wd, batch=4)
    assert not any(r.get("rv") for r in _read(wd).values())


def test_c1_run_review_truncated_output_not_rv(monkeypatch, tmp_path):
    wd = _job(tmp_path, _rows(8))
    _review_env(monkeypatch)
    monkeypatch.setattr(T, "chat", lambda *a, **k: '{"fixes":[{"i":1,"vi":"vi1 sửa"},{"i":2,"vi":"vi2')
    with pytest.raises(RuntimeError, match="REVIEW lỗi"):
        T.run_review(wd, batch=4)
    rows = _read(wd)
    assert not any(r.get("rv") for r in rows.values())
    assert rows[1]["vi"] == "vi1", "không được áp fix vớt một phần từ JSON cụt"


def test_c1_run_review_valid_empty_fixes_marks_rv(monkeypatch, tmp_path):
    wd = _job(tmp_path, _rows(8))
    _review_env(monkeypatch)
    monkeypatch.setattr(T, "chat", lambda *a, **k: '{"fixes":[]}')
    T.run_review(wd, batch=4)
    rows = _read(wd)
    assert all(r.get("rv") for r in rows.values())
    assert [rows[i]["vi"] for i in range(8)] == [f"vi{i}" for i in range(8)]


# ───────────────────────── C2 ─────────────────────────

def test_c2_review_does_not_overwrite_manual(monkeypatch, tmp_path):
    rows = _rows(8)
    rows[2].update({"vi": "Câu người sửa.", "manual": 1})
    rows[5].update({"vi": "Câu chọn alt.", "manual": True})
    wd = _job(tmp_path, rows)
    _review_env(monkeypatch)
    monkeypatch.setattr(T, "review_batch",
                        lambda chunk_exp, *a, **k: {r["i"]: f"LLM{r['i']}" for r in chunk_exp})
    T.run_review(wd, batch=4, force=True)
    out = _read(wd)
    assert out[2]["vi"] == "Câu người sửa."
    assert out[5]["vi"] == "Câu chọn alt."
    assert out[0]["vi"] == "LLM0" and out[7]["vi"] == "LLM7"
    # phương án: câu manual vẫn đánh rv (người đã duyệt) để gate không park mãi
    assert out[2].get("rv") and out[5].get("rv")


def test_c2_postpass_layers_skip_manual():
    plan = {"genre": "đô thị hiện đại", "style_lock": {"mode": "modern"},
            "terms": [{"zh": "我一共三万一千一血", "vi": "LOCK", "type": "lock"}]}
    rows = [
        {"i": 0, "zh": "我一共三万一千一血", "vi": "Người sửa giữ nguyên.", "manual": 1},
        {"i": 1, "zh": "不对不对，", "vi": "Không đúng không đúng,", "manual": 1},
        {"i": 2, "zh": "我也一样，之前。", "vi": "Tôi cũng vậy, trước đó.", "manual": 1},
        {"i": 3, "zh": "你去吧", "vi": "Ngươi đi đi. Ta ở lại.", "manual": 1},
    ]
    before = [r["vi"] for r in rows]
    T.apply_hard_term_locks(rows, plan)
    T.apply_style_polish(rows, plan)
    T.apply_pronoun_postpass(rows, plan)
    T.apply_asr_stutter_heal(rows)
    T.apply_halfcue_dangling_heal(rows)
    assert [r["vi"] for r in rows] == before


def _write_job(tmp_path: Path, rows: list[dict], plan: dict) -> Path:
    wd = tmp_path / "jobp"
    wd.mkdir()
    (wd / "script.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    (wd / "glossary.json").write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    (wd / "manifest.json").write_text(json.dumps({"stages": {}}), encoding="utf-8")
    return wd


def test_c2_name_pass_skips_manual(monkeypatch, tmp_path):
    import agents.agent_name_pass as NP
    plan = {"characters": [{"zh": "林凡", "vi": "Lâm Phàm"}]}
    rows = [
        {"i": 0, "zh": "林凡来了", "vi": "Lin Fan tới rồi.", "manual": 1},
        {"i": 1, "zh": "林凡走了", "vi": "Lin Fan đi rồi."},
    ]
    issues = NP.find_issues(rows, plan)
    assert [x["i"] for x in issues] == [1]
    wd = _write_job(tmp_path, rows, plan)
    monkeypatch.setattr(NP, "_fix_batch", lambda chunk, pb, m: {0: "Lâm Phàm tới rồi.", 1: "Lâm Phàm đi rồi."})
    monkeypatch.setattr(NP, "is_local", lambda m: False)
    NP.run_name_pass(wd, model="chatgpt/x")
    out = _read(wd)
    assert out[0]["vi"] == "Lin Fan tới rồi."
    assert out[1]["vi"] == "Lâm Phàm đi rồi."


def test_c2_pronoun_pass_and_register_policy_skip_manual(monkeypatch, tmp_path):
    import agents.agent_pronoun_pass as PP
    plan = {"genre": "tiên hiệp cổ phong", "style_lock": {"mode": "ancient"}}
    rows = [
        {"i": 0, "zh": "门主", "vi": "Môn chủ!"},
        {"i": 1, "zh": "你敢", "vi": "Cậu dám cãi Môn chủ?", "manual": 1},
        {"i": 2, "zh": "你敢", "vi": "Cậu dám cãi Môn chủ?"},
    ]
    wd = _write_job(tmp_path, rows, plan)
    monkeypatch.setattr(PP, "_fix_batch",
                        lambda chunk, pb, m, system=None: {1: "LLM đè câu manual", 2: "Ngươi dám cãi Môn chủ?"})
    monkeypatch.setattr(PP, "is_local", lambda m: False)
    PP.run_pronoun_pass(wd, model="chatgpt/x")
    out = _read(wd)
    assert out[1]["vi"] == "Cậu dám cãi Môn chủ?"
    assert out[2]["vi"] == "Ngươi dám cãi Môn chủ?"


def test_c2_register_policy_functions_skip_manual():
    import engines.pronoun_register_policy as RP
    rows = [
        {"i": 0, "zh": "门主", "vi": "Môn chủ!"},
        {"i": 1, "zh": "你", "vi": "Cậu muốn chết à? Ông định làm gì?", "manual": 1},
    ]
    assert RP.scan_title_intimate_issues(rows) == []
    assert RP.enforce_remaining_cau(rows, "ngươi") == []
    RP.normalize_ong_nguoi_in_title_window(rows, {1}, "ngươi")
    assert rows[1]["vi"] == "Cậu muốn chết à? Ông định làm gì?"


def test_c2_pronoun_qa_gpt_skips_manual(monkeypatch, tmp_path):
    import agents.agent_pronoun_pass as PP
    import engines.pronoun_consistency as PC
    rows = [
        {"i": 0, "zh": "你", "vi": "Anh đi đi.", "manual": 1},
        {"i": 1, "zh": "你", "vi": "Mày đi đi."},
    ]
    monkeypatch.setattr(PC, "find_pronoun_jumps",
                        lambda rows_, window=6: [{"i": 0, "zh": "你", "vi": "x", "reasons": ["r"]},
                                                 {"i": 1, "zh": "你", "vi": "x", "reasons": ["r"]}])
    monkeypatch.setattr(PP, "_fix_batch", lambda chunk, block, model, system=None: {0: "GPT đè", 1: "Cậu đi đi."})
    monkeypatch.setattr(PC, "analyze_model", lambda: "chatgpt/x")
    wd = tmp_path / "jq"
    wd.mkdir()
    PC.run_post_translate_consistency(wd, rows, {}, fix_with_gpt=True)
    assert rows[0]["vi"] == "Anh đi đi."
    assert rows[1]["vi"] == "Cậu đi đi."


# ───────────────────────── C3 ─────────────────────────

@pytest.mark.parametrize("vi,want", [
    # KHÔNG phải ngôi 2 độc lập → giữ nguyên
    ("Cậu ấy là ai?", "Cậu ấy là ai?"),
    ("Cậu ruột của tôi à?", "Cậu ruột của tôi à?"),
    ("Cậu ấy là ai? Cậu ruột của tôi à?", "Cậu ấy là ai? Cậu ruột của tôi à?"),
    ("cậu ta đi rồi.", "cậu ta đi rồi."),
    ("Cậu bé kia đứng lại.", "Cậu bé kia đứng lại."),
    ("Ông cậu tôi là Môn chủ.", "Ông cậu tôi là Môn chủ."),
    ("Cậu Lâm, mời ngồi.", "Cậu Lâm, mời ngồi."),
    ("Cậu chủ về rồi.", "Cậu chủ về rồi."),
    ("Cậu mợ tôi ở quê.", "Cậu mợ tôi ở quê."),
    ("Các cậu ấy đi rồi.", "Các cậu ấy đi rồi."),
    # ngôi 2 độc lập → đổi
    ("Cậu muốn chết à?", "Ngươi muốn chết à?"),
    ("Tôi sẽ giết cậu!", "Tôi sẽ giết ngươi!"),
    ("Đó là lỗi của cậu.", "Đó là lỗi của ngươi."),
    ("Các cậu lui ra.", "Các ngươi lui ra."),
    ("Cậu ấy nói cậu là kẻ phản bội.", "Cậu ấy nói ngươi là kẻ phản bội."),
    ("cậu, đứng lại!", "Ngươi, đứng lại!"),
])
def test_c3_mechanical_cau_table(vi, want):
    import engines.pronoun_register_policy as RP
    assert RP.mechanical_cau_to_formal(vi, "ngươi") == want


def test_c3_enforce_remaining_cau_not_third_person():
    import engines.pronoun_register_policy as RP
    rows = [
        {"i": 0, "zh": "门主", "vi": "Môn chủ!"},
        {"i": 1, "zh": "他是谁", "vi": "Cậu ấy là ai? Cậu ruột của tôi à?"},
        {"i": 2, "zh": "你敢", "vi": "Cậu dám vô lễ với Môn chủ?"},
        {"i": 3, "zh": "他是谁", "vi": "Cậu ấy là ai? Cậu ruột của tôi à?", "manual": True},
    ]
    ch = RP.enforce_remaining_cau(rows, "ngươi")
    assert rows[1]["vi"] == "Cậu ấy là ai? Cậu ruột của tôi à?"
    assert rows[2]["vi"] == "Ngươi dám vô lễ với Môn chủ?"
    assert rows[3]["vi"] == "Cậu ấy là ai? Cậu ruột của tôi à?"
    assert [c["i"] for c in ch] == [2]


# ───────────────────────── C9 ─────────────────────────

class _SwitchSpy:
    def __init__(self, ok: bool = True, delay: float = 0.2):
        self.calls = 0
        self.ok = ok
        self.delay = delay
        self._lk = threading.Lock()

    def __call__(self, preset_id, max_wait_sec=180):
        with self._lk:
            self.calls += 1
        time.sleep(self.delay)
        return self.ok


def _parallel_review(monkeypatch, tmp_path, cloud_exc, *, ok=True, n=32, batch=4, workers=8):
    import tools.preset_switcher as preset_switcher
    wd = _job(tmp_path, _rows(n))
    _review_env(monkeypatch, workers=workers)
    monkeypatch.setattr(T, "_is_llama_local_model", lambda m: str(m or "").startswith("llama/"))
    spy = _SwitchSpy(ok=ok)
    monkeypatch.setattr(preset_switcher, "switch_preset", spy)
    local_calls = []

    def fake_rb(chunk_exp, plan_block, prev_ctx, model=None, **k):
        if str(model or "").startswith("llama/"):
            local_calls.append(len(chunk_exp))
            return {}
        raise cloud_exc

    monkeypatch.setattr(T, "review_batch", fake_rb)
    return wd, spy, local_calls


def test_c9_parallel_fallback_switches_once(monkeypatch, tmp_path):
    wd, spy, local_calls = _parallel_review(
        monkeypatch, tmp_path, LLMUnavailable("Aurora/ChatGPT thất bại: 429 Too Many Requests"))
    T.run_review(wd, batch=4)
    assert spy.calls == 1, f"8 luồng phải chỉ đổi preset 1 lần, thực tế {spy.calls}"
    assert all(r.get("rv") for r in _read(wd).values())
    assert len(local_calls) == 8


def test_c9_parallel_switch_fail_no_rv_single_attempt(monkeypatch, tmp_path):
    wd, spy, _lc = _parallel_review(
        monkeypatch, tmp_path, LLMUnavailable("Aurora/ChatGPT thất bại: 503"), ok=False)
    with pytest.raises(RuntimeError, match="REVIEW lỗi"):
        T.run_review(wd, batch=4)
    assert spy.calls == 1
    assert not any(r.get("rv") for r in _read(wd).values())


def test_c9_413_splits_not_switch(monkeypatch, tmp_path):
    import tools.preset_switcher as preset_switcher
    wd = _job(tmp_path, _rows(16))
    _review_env(monkeypatch, workers=1)
    monkeypatch.setattr(T, "_is_llama_local_model", lambda m: str(m or "").startswith("llama/"))
    spy = _SwitchSpy()
    monkeypatch.setattr(preset_switcher, "switch_preset", spy)
    sizes = []

    def fake_rb(chunk_exp, plan_block, prev_ctx, model=None, **k):
        sizes.append(len(chunk_exp))
        if len(chunk_exp) > 5:
            raise LLMUnavailable("Aurora/ChatGPT 413 (no-retry): Request Entity Too Large")
        return {r["i"]: r["vi"] + "*" for r in chunk_exp}

    monkeypatch.setattr(T, "review_batch", fake_rb)
    T.run_review(wd, batch=8)
    assert spy.calls == 0, "413 không được đổi preset GPU"
    rows = _read(wd)
    assert all(r.get("rv") for r in rows.values())
    assert all(r["vi"].startswith(f"vi{i}") for i, r in rows.items())
    assert min(sizes) <= 5


@pytest.mark.parametrize("exc", [
    pytest.param(LLMUnavailable("Aurora/ChatGPT 400 (no-retry): bad request"), id="400"),
    pytest.param(RuntimeError("LLM từ chối payload (422): invalid"), id="422"),
    pytest.param(ValueError("max token count mismatch in parser"), id="chuoi-token"),
    pytest.param(RuntimeError("lỗi parse ở offset 500"), id="chuoi-500"),
    pytest.param(T.ReviewBadOutput("rỗng") if hasattr(T, "ReviewBadOutput") else ValueError("rỗng"),
                 id="bad-output"),
])
def test_c9_non_quota_errors_do_not_switch(monkeypatch, exc):
    import tools.preset_switcher as preset_switcher
    spy = _SwitchSpy(delay=0)
    monkeypatch.setattr(preset_switcher, "switch_preset", spy)
    monkeypatch.setattr(T, "_is_llama_local_model", lambda m: str(m or "").startswith("llama/"))

    def boom(*a, **k):
        raise exc

    monkeypatch.setattr(T, "review_batch", boom)
    rows = _rows(3)
    fixes, _m = T._review_chunk_with_fallback(
        rows, rows, "", [], target="vi", rmodel="chatgpt/x", plan={}, exemplars_pool=rows,
    )
    assert fixes is None
    assert spy.calls == 0


def test_c9_preset_switcher_blocked_under_pytest(monkeypatch):
    import tools.preset_switcher as PS
    called = []
    monkeypatch.setattr(PS, "_switch_preset_unlocked", lambda *a, **k: called.append(a) or True)
    assert PS.switch_preset("qwen36-turbo", max_wait_sec=1) is False
    assert not called, "pytest không bao giờ được restart llama-server thật"


# ───────────────────────── T18 ─────────────────────────

def test_t18_run_translate_keeps_asr_extra_fields(monkeypatch, tmp_path):
    wd = tmp_path / "jt"
    wd.mkdir()
    segs = [
        {"i": 0, "start": 0.0, "end": 1.0, "text": "你好", "spk": "A", "asr_conf": 0.91},
        {"i": 1, "start": 1.0, "end": 2.0, "text": "哈哈哈", "spk": "B", "asr_conf": 0.5},
        {"i": 2, "start": 2.0, "end": 3.0, "text": "再见", "spk": "A", "asr_conf": 0.8,
         "words": [{"w": "再"}, {"w": "见"}]},
    ]
    (wd / "asr.json").write_text(json.dumps(segs, ensure_ascii=False), encoding="utf-8")
    (wd / "glossary.json").write_text(json.dumps({"characters": [], "terms": []}), encoding="utf-8")
    (wd / "manifest.json").write_text(json.dumps({"stages": {}}), encoding="utf-8")
    monkeypatch.setattr(T, "_cfg_get", lambda k, d=None: {"AUTO_SWITCH_PRESETS": "0"}.get(k, d))
    monkeypatch.setattr(T, "is_local", lambda m: False)
    monkeypatch.setattr(T, "unload_local", lambda m: None)
    import engines.series_glossary as series_glossary
    monkeypatch.setattr(series_glossary, "apply", lambda wd_, plan: plan)
    monkeypatch.setattr(series_glossary, "save_from", lambda *a, **k: None)
    import engines.pronoun_consistency as PC
    monkeypatch.setattr(PC, "ensure_analyze_before_translate",
                        lambda wd_, plan, segments=None, force=False: (plan, {"skipped": True}))
    monkeypatch.setattr(PC, "run_post_translate_consistency",
                        lambda wd_, rows_, plan, fix_with_gpt=True: {"ok": True})
    import engines.mt_zh_vi as mt_zh_vi
    monkeypatch.setattr(mt_zh_vi, "enabled", lambda: False)
    monkeypatch.setattr(T, "_translate_safe",
                        lambda chunk, *a, **k: {s["i"]: f"VI{s['i']}" for s in chunk})
    T.run_translate(wd, auto_review=False, mode="batch")
    rows = {r["i"]: r for r in json.loads((wd / "script.json").read_text(encoding="utf-8"))}
    assert rows[0]["spk"] == "A" and rows[0]["asr_conf"] == 0.91
    assert rows[1]["spk"] == "B"            # câu cười prefill cũng giữ
    assert rows[2]["spk"] == "A" and rows[2]["asr_conf"] == 0.8
    assert "words" not in rows[2]           # timestamp từng chữ không chép sang script
    assert rows[0]["vi"] == "VI0" and rows[0]["zh"] == "你好"
    assert "text" not in rows[0]


def test_c9_default_state_without_fb_state_switches_once_then_ttl(monkeypatch):
    """Caller cũ (không truyền fb_state, vd run_review cũ còn trong server sau reload):
    dùng state mặc định — vẫn chỉ switch 1 lần, hết TTL mới thử lại."""
    import tools.preset_switcher as preset_switcher
    spy = _SwitchSpy(ok=False, delay=0)
    monkeypatch.setattr(preset_switcher, "switch_preset", spy)
    monkeypatch.setattr(T, "_is_llama_local_model", lambda m: str(m or "").startswith("llama/"))
    monkeypatch.setattr(T, "_REVIEW_FB_STATE_DEFAULT", T._new_review_fallback_state())
    # translate-b2: tắt retry cloud để test đúng logic state mặc định C9
    monkeypatch.setattr(T, "_cfg_get", lambda k, d=None: {"REVIEW_CLOUD_RETRY": "0"}.get(k, d))

    def boom(*a, **k):
        raise LLMUnavailable("Aurora/ChatGPT thất bại: 429")

    monkeypatch.setattr(T, "review_batch", boom)
    rows = _rows(3)
    for _ in range(3):
        fixes, _m = T._review_chunk_with_fallback(
            rows, rows, "", [], target="vi", rmodel="chatgpt/x", plan={}, exemplars_pool=rows)
        assert fixes is None
    assert spy.calls == 1
    T._REVIEW_FB_STATE_DEFAULT["ts"] = time.time() - T._REVIEW_FB_DEFAULT_TTL - 1
    T._review_chunk_with_fallback(rows, rows, "", [], target="vi", rmodel="chatgpt/x",
                                  plan={}, exemplars_pool=rows)
    assert spy.calls == 2
