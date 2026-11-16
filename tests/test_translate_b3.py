"""fix 2026-11-12 translate-b3 — cờ thử nghiệm chất lượng dịch (mặc định TẮT = như cũ).

- PRONOUN_REGEX_MIXED (mặc định 1): 0 = bỏ phép đổi đại từ tất định ở nhánh mixed.
- REVIEW_PRONOUN_MASK=0 (+ REVIEW_PRONOUN_PLAN_GUIDE, mặc định 1): REVIEW có khối (G) xưng hô theo plan
  và giữ fix chỉ-đổi-đại-từ sang dạng có trong plan.
- HALFCUE_MERGE (mặc định 0): gom cue cắt đôi → dịch 1 đơn vị → chia lại cho cue gốc.
- FILL_PENDING_PARK (mặc định 0): D1 — câu NMT sót vá cloud lỗi → park waiting_review (B2) thay vì dừng.

Đối chiếu hành vi mặc định với bản gốc trong `.backup_edit_20261112_translate_b3/` (bỏ qua nếu không có).
Không HTTP / LLM / GPU: chat, NMT, switch_preset đều giả.
"""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

import engines.cloud_retry as CR
import engines.translate as T
from tests.test_translate_b2 import (  # helper dùng chung
    _SEGS,
    _cfg,
    _read,
    _translate_env,
    _translate_job,
)

ROOT = Path(__file__).resolve().parents[1]
_BACKUP = ROOT / ".backup_edit_20261112_translate_b3"


@pytest.fixture(autouse=True)
def _iso(monkeypatch):
    CR.reset_gates()
    monkeypatch.setattr(T, "_log_vram", lambda stage: None, raising=False)
    # F2 2026-11-12: mặc định đã là luồng simple — file này kiểm luồng CŨ → đặt legacy tường minh
    monkeypatch.setenv("TRANSLATE_PIPELINE", "legacy")
    for k in ("PRONOUN_REGEX_MIXED", "HALFCUE_MERGE", "FILL_PENDING_PARK", "REVIEW_PRONOUN_PLAN_GUIDE",
              "PINELINE_CFG_KEYS"):
        monkeypatch.delenv(k, raising=False)
    yield
    CR.reset_gates()


def _set_cfg(monkeypatch, **kv):
    cfg = {k: str(v) for k, v in kv.items()}
    monkeypatch.setattr(T, "_cfg_get", lambda k, d=None: cfg.get(k, d))
    return cfg


PLAN_MIXED = {"genre": "đô thị dị năng, tu tiên", "style_lock": {"mode": "mixed"},
              "characters": [{"zh": "顾青", "vi": "Cố Thanh"}, {"zh": "夏书然", "vi": "Hạ Thư Nhiên"}],
              "pronouns": [{"who": "Cố Thanh", "to": "Hạ Thư Nhiên", "self": "anh", "call": "em"},
                           {"who": "Ngao Hoàng", "to": "Long Ngạo Thiên", "self": "lão phu", "call": "tiểu tử"}]}
PLAN_MODERN_BLOB_MIXED = {"genre": "đô thị dị năng võ", "style_lock": {"mode": "modern"},
                          "pronouns": [{"who": "A", "to": "B", "self": "tôi", "call": "cậu"}]}
PLAN_MODERN = {"genre": "đô thị", "style_lock": {"mode": "modern"}}
PLAN_ANCIENT = {"genre": "tu tiên cổ trang", "style_lock": {"mode": "ancient"}}

SAMPLE = [
    ("你想死吗？我会杀了你。", "Ngươi muốn chết sao? Ta sẽ giết ngươi."),
    ("他说的", "Cậu ta nói thế, ta không tin."),
    ("把他变成你的奴隶", "Ta sẽ biến cậu ta thành nô lệ của ngươi."),
    ("你没大没小", "Ngươi chưa lớn không nhỏ."),
    ("我来自东方", "Tôi đã đến từ phương Đông."),
    ("三点一万亿", "Ba vạn tỷ, 3,1 vạn tỷ."),
    ("第二星球", "Ta tới hành tinh thứ hai."),
    ("我们走", "Chúng ta đi thôi, ông ta đợi rồi."),
    ("过山", "qua núi rồi, ngươi đi đâu"),
    ("师兄", "Sư huynh, ta sai rồi."),
    ("觉醒者", "Người thức tỉnh tới, ngươi chạy đi."),
    ("", ""),
]


def _sample_rows():
    return [{"i": k, "start": float(k), "end": k + 1.0, "zh": zh, "vi": vi} for k, (zh, vi) in enumerate(SAMPLE)]


# ───────────────────────── 1. PRONOUN_REGEX_MIXED ─────────────────────────

def test_regex_default_still_flattens_mixed(monkeypatch):
    _set_cfg(monkeypatch)
    rows = _sample_rows()
    T.apply_style_polish(rows, copy.deepcopy(PLAN_MIXED))
    assert rows[0]["vi"] == "Cậu muốn chết sao? Tôi sẽ giết cậu."
    assert "Tinh cầu hai sao" in rows[6]["vi"]


def test_regex_off_keeps_pronouns_but_other_rules_run(monkeypatch):
    _set_cfg(monkeypatch, PRONOUN_REGEX_MIXED="0")
    rows = _sample_rows()
    T.apply_style_polish(rows, copy.deepcopy(PLAN_MIXED))
    assert rows[0]["vi"] == "Ngươi muốn chết sao? Ta sẽ giết ngươi."
    assert rows[1]["vi"] == "Cậu ta nói thế, ta không tin."
    assert rows[2]["vi"] == "Ta sẽ biến cậu ta thành nô lệ của ngươi."
    assert rows[9]["vi"] == "Sư huynh, ta sai rồi."
    # luật khác vẫn chạy
    assert "không biết trên dưới" in rows[3]["vi"] and rows[3]["vi"].startswith("Ngươi")
    assert rows[4]["vi"] == "Tôi đến từ phương Đông."
    assert rows[5]["vi"] == "3.000 tỷ, 31.000 tỷ."
    assert rows[6]["vi"] == "Ta tới Tinh cầu hai sao."
    assert rows[8]["vi"].startswith("Quá Sơn") and "ngươi" in rows[8]["vi"]
    assert "Giác Tỉnh Giả" in rows[10]["vi"] and "ngươi" in rows[10]["vi"]


def test_regex_off_does_not_touch_manual(monkeypatch):
    _set_cfg(monkeypatch, PRONOUN_REGEX_MIXED="1")
    rows = _sample_rows()
    rows[0]["manual"] = 1
    T.apply_style_polish(rows, copy.deepcopy(PLAN_MIXED))
    assert rows[0]["vi"] == SAMPLE[0][1]


def test_postpass_regex_off_only_for_mixed(monkeypatch):
    # mode=modern nhưng genre đô thị+võ → _is_mixed_genre True: cờ 0 → không detox
    rows_on = [{"i": 0, "zh": "你", "vi": "Ngươi đi đi, Ta ở lại."}]
    rows_off = copy.deepcopy(rows_on)
    _set_cfg(monkeypatch)
    T.apply_pronoun_postpass(rows_on, copy.deepcopy(PLAN_MODERN_BLOB_MIXED))
    assert rows_on[0]["vi"] == "Cậu đi đi, Tôi ở lại."
    _set_cfg(monkeypatch, PRONOUN_REGEX_MIXED="0")
    T.apply_pronoun_postpass(rows_off, copy.deepcopy(PLAN_MODERN_BLOB_MIXED))
    assert rows_off[0]["vi"] == "Ngươi đi đi, Ta ở lại."
    # đô thị THUẦN (không mixed): cờ không ảnh hưởng
    rows_m = [{"i": 0, "zh": "你", "vi": "Ngươi đi đi."}]
    T.apply_pronoun_postpass(rows_m, copy.deepcopy(PLAN_MODERN))
    assert rows_m[0]["vi"] == "Cậu đi đi."


# ───────────────────────── 2. REVIEW mask tắt → khối (G) ─────────────────────────

def _review_capture(monkeypatch, reply: dict, **cfg):
    _set_cfg(monkeypatch, **cfg)
    seen = {}

    def fake_chat(messages, **k):
        seen["sys"] = messages[0]["content"]
        seen["user"] = messages[1]["content"]
        return json.dumps(reply, ensure_ascii=False)

    monkeypatch.setattr(T, "chat", fake_chat)
    return seen


_RV_ROWS = [
    {"i": 0, "start": 0.0, "end": 3.0, "zh": "顾青：我猜你新学会做某种好吃的甜品。",
     "vi": "Tôi đoán cậu mới học được cách làm món tráng miệng ngon."},
    {"i": 1, "start": 3.0, "end": 6.0, "zh": "还是不对", "vi": "Vẫn chưa đúng."},
    {"i": 2, "start": 6.0, "end": 9.0, "zh": "老夫来了", "vi": "Tôi tới rồi, cậu chờ đó."},
]


def test_mask_on_prompt_has_no_guide_block(monkeypatch):
    seen = _review_capture(monkeypatch, {"fixes": []}, REVIEW_PRONOUN_MASK="1")
    T.review_batch([dict(r) for r in _RV_ROWS], "PLAN", [], plan=copy.deepcopy(PLAN_MIXED))
    assert "(G) XƯNG HÔ THEO PLAN" not in seen["sys"]
    assert "⟦P" in seen["user"]


def test_mask_off_prompt_has_guide_block_with_pairs(monkeypatch):
    seen = _review_capture(monkeypatch, {"fixes": []}, REVIEW_PRONOUN_MASK="0")
    T.review_batch([dict(r) for r in _RV_ROWS], "PLAN", [], plan=copy.deepcopy(PLAN_MIXED))
    assert "(G) XƯNG HÔ THEO PLAN" in seen["sys"]
    assert "Cố Thanh → Hạ Thư Nhiên: «anh» / «em»" in seen["sys"]
    assert "⟦P" not in seen["user"]


def test_mask_off_guide_off_prompt_like_before(monkeypatch):
    seen = _review_capture(monkeypatch, {"fixes": []}, REVIEW_PRONOUN_MASK="0", REVIEW_PRONOUN_PLAN_GUIDE="0")
    T.review_batch([dict(r) for r in _RV_ROWS], "PLAN", [], plan=copy.deepcopy(PLAN_MIXED))
    assert "(G) XƯNG HÔ THEO PLAN" not in seen["sys"]


def test_mask_off_keeps_pronoun_only_fix_in_plan(monkeypatch):
    reply = {"fixes": [
        {"i": 0, "vi": "Anh đoán em mới học được cách làm món tráng miệng ngon."},   # chỉ đổi đại từ → giữ
        {"i": 1, "vi": "Vẫn sai, đoán tiếp đi."},                                       # cosmetic → bỏ (K20)
        {"i": 2, "vi": "Lão phu tới rồi, tiểu tử chờ đó."},                              # đại từ theo plan → giữ
    ]}
    _review_capture(monkeypatch, reply, REVIEW_PRONOUN_MASK="0")
    out = T.review_batch([dict(r) for r in _RV_ROWS], "PLAN", [], plan=copy.deepcopy(PLAN_MIXED))
    assert out.get(0) == reply["fixes"][0]["vi"]
    assert out.get(2) == reply["fixes"][2]["vi"]
    assert 1 not in out


def test_mask_off_pronoun_fix_outside_plan_or_with_rewrite_dropped(monkeypatch):
    reply = {"fixes": [
        {"i": 0, "vi": "Tao đoán mày mới học được cách làm món tráng miệng ngon."},  # dạng không có trong plan
        {"i": 2, "vi": "Lão phu đến đây rồi, tiểu tử."},                              # đổi đại từ + viết lại
    ]}
    _review_capture(monkeypatch, reply, REVIEW_PRONOUN_MASK="0")
    out = T.review_batch([dict(r) for r in _RV_ROWS], "PLAN", [], plan=copy.deepcopy(PLAN_MIXED))
    assert 0 not in out and 2 not in out


def test_mask_on_still_freezes_pronoun_changes(monkeypatch):
    reply = {"fixes": [{"i": 0, "vi": "Anh đoán em mới học được cách làm món tráng miệng ngon."}]}
    _review_capture(monkeypatch, reply, REVIEW_PRONOUN_MASK="1")
    out = T.review_batch([dict(r) for r in _RV_ROWS], "PLAN", [], plan=copy.deepcopy(PLAN_MIXED))
    assert 0 not in out


# ───────────────────────── 3. HALFCUE_MERGE ─────────────────────────

def _seg(i, s, e, t):
    return {"i": i, "start": s, "end": e, "text": t}


def test_halfcue_groups_criteria():
    segs = [
        _seg(0, 0.0, 1.0, "陈先生进入以后"),     # không dấu kết → gom với 1
        _seg(1, 1.2, 2.0, "我们就动手。"),
        _seg(2, 2.1, 3.0, "好的。"),            # 1 kết câu → không gom 1-2
        _seg(3, 3.0, 4.0, "你先走，"),
        _seg(4, 5.0, 6.0, "我断后。"),          # nghỉ 1.0 s > 0.35 → không gom 3-4
        _seg(5, 6.0, 6.5, "一"), _seg(6, 6.5, 7.0, "二"), _seg(7, 7.0, 7.5, "三"), _seg(8, 7.5, 8.0, "四"),
        _seg(9, 8.5, 9.0, "这是一句非常非常长的中文句子用来测试字数上限的"),
        _seg(10, 9.0, 9.5, "这是一句非常非常长的中文句子用来测试字数上限的"),
        _seg(11, 9.6, 10.0, "他说……"),          # … kết câu
        _seg(12, 10.0, 11.0, "对"),
    ]
    g = T.halfcue_groups(segs, gap=0.35, max_chars=40, max_cues=3)
    assert g[0] == g[1] == "hc0"
    assert 2 not in g and 3 not in g and 4 not in g
    assert g[5] == g[6] == g[7] == "hc5" and g.get(8) != g[5]        # tối đa 3 cue
    assert 9 not in g or g.get(9) != g.get(10)                      # vượt 40 ký tự
    assert 12 not in g                                              # 11 kết bằng …


def test_halfcue_split_prefers_comma_near_ratio():
    parts = T.halfcue_split_vi("Sau khi anh Trần vào, chúng ta sẽ ra tay.", ["陈先生进入以后，", "我们就动手。"])
    assert parts == ["Sau khi anh Trần vào,", "chúng ta sẽ ra tay."]


def test_halfcue_split_word_boundary_and_never_empty():
    parts = T.halfcue_split_vi("Một hai ba bốn năm sáu", ["一二三", "四五六"])
    assert parts and len(parts) == 2 and all(p.strip() for p in parts)
    assert " ".join(parts) == "Một hai ba bốn năm sáu"
    assert T.halfcue_split_vi("Được", ["好", "的"]) is None
    p3 = T.halfcue_split_vi("Anh đi trước, em theo sau, rồi gặp nhau.", ["你先走", "我跟着", "然后见"])
    assert p3 and len(p3) == 3 and all(p.strip() for p in p3)


_HC_SEGS = [
    {"i": 0, "start": 0.0, "end": 1.0, "text": "陈先生进入以后，", "spk": "A"},
    {"i": 1, "start": 1.1, "end": 2.0, "text": "我们就动手。", "spk": "A"},
    {"i": 2, "start": 2.0, "end": 3.0, "text": "明白。", "spk": "B"},
    {"i": 3, "start": 3.0, "end": 4.0, "text": "你先走", "spk": "A"},
    {"i": 4, "start": 5.5, "end": 6.0, "text": "我断后。", "spk": "A"},
]


def test_halfcue_nmt_primary_merge_split(monkeypatch, tmp_path):
    import engines.mt_zh_vi as mt_zh_vi
    _translate_env(monkeypatch, HALFCUE_MERGE=1)
    sent = []
    vis = {"陈先生进入以后，我们就动手。": "Sau khi anh Trần vào, chúng ta sẽ ra tay.", "明白。": "Rõ.",
           "你先走": "Anh đi trước", "我断后。": "Tôi chặn hậu."}

    def draft(items, plan=None):
        sent.append([it["text"] for it in items])
        return {it["i"]: vis.get(it["text"], "") for it in items}

    monkeypatch.setattr(mt_zh_vi, "draft_rows", draft)
    monkeypatch.setattr(T, "_translate_safe", lambda *a, **k: pytest.fail("không cần LLM"))
    wd = _translate_job(tmp_path, _HC_SEGS)
    T.run_translate(wd, auto_review=False)
    assert sent[0] == ["陈先生进入以后，我们就动手。", "明白。", "你先走", "我断后。"]
    rows = _read(wd)
    assert rows[0]["vi"] == "Sau khi anh Trần vào," and rows[1]["vi"] == "chúng ta sẽ ra tay."
    assert rows[0]["group_id"] == rows[1]["group_id"] == "hc0"
    assert "group_id" not in rows[2] and "group_id" not in rows[3] and "group_id" not in rows[4]
    for s in _HC_SEGS:  # giữ timing + zh + spk từng cue
        r = rows[s["i"]]
        assert (r["start"], r["end"], r["zh"], r["spk"]) == (s["start"], s["end"], s["text"], s["spk"])
        assert r["vi"].strip()
    assert T.count_script_missing(wd) == 0


def test_halfcue_split_fail_falls_back_to_single_nmt(monkeypatch, tmp_path):
    import engines.mt_zh_vi as mt_zh_vi
    _translate_env(monkeypatch, HALFCUE_MERGE=1)
    calls = []

    def draft(items, plan=None):
        calls.append([it["i"] for it in items])
        return {it["i"]: ("Ừ" if len(calls) == 1 else f"V{it['i']} câu") for it in items}

    monkeypatch.setattr(mt_zh_vi, "draft_rows", draft)
    wd = _translate_job(tmp_path, _HC_SEGS[:2])
    T.run_translate(wd, auto_review=False)
    assert calls == [[0], [0, 1]]
    rows = _read(wd)
    assert rows[0]["vi"] == "V0 câu" and rows[1]["vi"] == "V1 câu"
    assert "group_id" not in rows[0]


def test_halfcue_llm_path_merges_and_splits(monkeypatch, tmp_path):
    # NMT tắt → LLM dịch: _translate_safe nhận 1 đơn vị cho nhóm; chia lại; không câu trống
    _translate_env(monkeypatch, nmt_on=False, HALFCUE_MERGE=1)
    got = []

    def ts(chunk, plan_block, prev_ctx, target=None, model=None, plan=None):
        got.append([(s["i"], s["text"], s["start"], s["end"]) for s in chunk])
        return {s["i"]: ("Sau khi anh Trần vào, chúng ta sẽ ra tay." if s["i"] == 0 else f"Câu {s['i']}.")
                for s in chunk}

    monkeypatch.setattr(T, "_translate_safe", ts)
    wd = _translate_job(tmp_path, _HC_SEGS)
    T.run_translate(wd, auto_review=False, mode="batch")
    assert got[0][0] == (0, "陈先生进入以后，我们就动手。", 0.0, 2.0)
    assert [x[0] for x in got[0]] == [0, 2, 3, 4]
    rows = _read(wd)
    assert rows[0]["vi"] == "Sau khi anh Trần vào," and rows[1]["vi"] == "chúng ta sẽ ra tay."
    assert rows[1]["group_id"] == "hc0" and all(r["vi"].strip() for r in rows.values())


def test_halfcue_off_is_default(monkeypatch, tmp_path):
    import engines.mt_zh_vi as mt_zh_vi
    _translate_env(monkeypatch)
    sent = []
    monkeypatch.setattr(mt_zh_vi, "draft_rows", lambda items, plan=None: sent.append(
        [it["text"] for it in items]) or {it["i"]: f"V{it['i']}" for it in items})
    wd = _translate_job(tmp_path, _HC_SEGS)
    T.run_translate(wd, auto_review=False)
    assert sent == [[s["text"] for s in _HC_SEGS]]
    assert not any("group_id" in r for r in _read(wd).values())


# ───────────────────────── 4. D1 — FILL_PENDING_PARK ─────────────────────────

def _d1_chain(monkeypatch, tmp_path, *, park: str, fill_model: str = ""):
    server = pytest.importorskip("server")
    from tests.test_translate_b2_review import _real_chain_env
    spy, calls = _real_chain_env(monkeypatch, local_fallback="0")
    if fill_model:
        base = T._cfg_get
        monkeypatch.setattr(T, "_cfg_get", lambda k, d=None: fill_model if k == "TRANSLATE_FILL_MODEL" else base(k, d))
    monkeypatch.setenv("FILL_PENDING_PARK", park)
    monkeypatch.setattr(server, "WORK_ROOT", tmp_path)
    # review cloud OK cho câu có vi; vá câu trống (cloud) thì 429 mãi
    monkeypatch.setattr(T, "review_batch", lambda chunk, *a, **k: {})
    segs = [dict(s) for s in _SEGS]
    wd = tmp_path / "j1"
    wd.mkdir()
    (wd / "manifest.json").write_text(json.dumps({"stages": {}}), encoding="utf-8")
    (wd / "asr.json").write_text(json.dumps(segs, ensure_ascii=False), encoding="utf-8")
    (wd / "glossary.json").write_text(json.dumps({"characters": [], "terms": []}), encoding="utf-8")
    monkeypatch.setattr(server, "_part_pipeline_complete", lambda wd_: False)
    monkeypatch.setattr(server, "free_gpu_vram", lambda *a, **k: None)
    monkeypatch.setattr(server, "_resolve_asr_engine", lambda wd_, e=None: "x")
    monkeypatch.setattr(server, "_asr_script", lambda e: "x.py")
    monkeypatch.setattr(server, "_run_engine", lambda *a, **k: None)
    monkeypatch.setattr(server, "run_translate", T.run_translate)
    tts = []
    monkeypatch.setattr(server, "_run_requested_review", lambda *a, **k: tts.append("next"))
    return server, wd, spy, calls, tts


def _man(wd):
    return json.loads((wd / "manifest.json").read_text(encoding="utf-8"))


@pytest.fixture
def fastclock(monkeypatch):
    from tests.test_translate_b2_review import ScaledClock
    c = ScaledClock()
    monkeypatch.setattr(CR, "_sleep", c.sleep)
    monkeypatch.setattr(CR, "_now", c.now)
    monkeypatch.setattr(CR, "_rand", lambda: 0.5)
    return c


def test_d1_park_waiting_review_and_retry_due(monkeypatch, tmp_path, fastclock):
    server, wd, spy, calls, tts = _d1_chain(monkeypatch, tmp_path, park="1")
    server._auto_gpu("j1", "Tiếng Việt", "replace", 1.0, 0.0, False)
    ag = _man(wd).get("agent") or {}
    assert ag.get("held_at") == "waiting_review", ag
    assert ag.get("review_retries") == 1 and float(ag.get("review_retry_at") or 0) > time.time()
    assert "trống" in ag.get("hold_reason", "")
    assert tts == [] and spy.calls == []
    rows = _read(wd)
    assert rows[1]["vi"] == "" and rows[1].get("fill_pending") == 1
    # queue: chưa tới hạn → KHÔNG chạy lại (không lặp nóng dù unrev=0)
    assert server._queue_park_ready("j1") is False
    m = _man(wd)
    m["agent"]["review_retry_at"] = time.time() - 1
    (wd / "manifest.json").write_text(json.dumps(m), encoding="utf-8")
    assert server._queue_park_ready("j1") is True
    # lượt 2, 3 vẫn lỗi → đếm tăng (không bị xoá); lượt 4 > max → review_failed
    for want in (2, 3):
        server._auto_gpu("j1", "Tiếng Việt", "replace", 1.0, 0.0, False)
        assert (_man(wd).get("agent") or {}).get("review_retries") == want
    server._auto_gpu("j1", "Tiếng Việt", "replace", 1.0, 0.0, False)
    ag = _man(wd).get("agent") or {}
    assert ag.get("held_at") == "review_failed" and ag.get("hold_after_translate") is True
    assert tts == []


def test_d1_default_off_stops_like_before(monkeypatch, tmp_path, fastclock):
    server, wd, spy, calls, tts = _d1_chain(monkeypatch, tmp_path, park="0")
    server._auto_gpu("j1", "Tiếng Việt", "replace", 1.0, 0.0, False)
    man = _man(wd)
    assert (man.get("agent") or {}).get("held_at") is None
    tr = man["stages"]["translate"]
    assert tr["status"] == "pending" and "chưa đủ để TTS" in tr["cur_text"]
    assert tts == []


def test_d1_respects_fill_model_local(monkeypatch, tmp_path, fastclock):
    """TRANSLATE_FILL_MODEL=local → đường cũ (gemma vá), D1 không park."""
    server, wd, spy, calls, tts = _d1_chain(monkeypatch, tmp_path, park="1", fill_model="local")
    server._auto_gpu("j1", "Tiếng Việt", "replace", 1.0, 0.0, False)
    assert (_man(wd).get("agent") or {}).get("held_at") != "waiting_review"
    assert "gemma-test" in spy.calls  # đường cũ: nạp preset local (giả) để vá
    rows = _read(wd)
    assert all(r["vi"].strip() for r in rows.values()) and not any(r.get("fill_pending") for r in rows.values())


# ───────────────────────── 5. Mặc định = bản gốc (backup) ─────────────────────────

_CHAR_SCRIPT = r'''
import copy, json, sys, tempfile, shutil
from pathlib import Path
first, root, golden = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path[:0] = [first, root]
import translate as T
assert Path(T.__file__).resolve().parent == Path(first).resolve(), T.__file__
import mt_zh_vi, preset_switcher, series_glossary
import pronoun_consistency as PC
CFG = json.loads(sys.argv[4])
T._cfg_get = lambda k, d=None: CFG.get(k, d)
if hasattr(T, "_log_vram"):
    T._log_vram = lambda stage: None
out = {}
SAMPLE = json.loads(sys.argv[5])
PLANS = json.loads(sys.argv[6])
for pn, plan in PLANS.items():
    rows = [{"i": k, "start": float(k), "end": k + 1.0, "zh": zh, "vi": vi} for k, (zh, vi) in enumerate(SAMPLE)]
    rows[3]["manual"] = 1
    T.apply_hard_term_locks(rows, copy.deepcopy(plan))
    T.apply_style_polish(rows, copy.deepcopy(plan))
    T.apply_pronoun_postpass(rows, copy.deepcopy(plan))
    out["post_" + pn] = rows
# golden thật (vi_system) — nếu có
if golden and Path(golden).is_dir():
    for jd in sorted(Path(golden).iterdir()):
        f = jd / "lines.gold.jsonl"
        if not f.is_file():
            continue
        lines = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
        rows = [{"i": g["i"], "start": 0.0, "end": 1.0, "zh": g["zh"], "vi": g.get("vi_system") or ""} for g in lines]
        plan = {"genre": "mixed", "style_lock": {"mode": "mixed"}}
        T.apply_style_polish(rows, plan)
        T.apply_pronoun_postpass(rows, plan)
        out["golden_" + jd.name] = rows
# review_batch: prompt + kết quả
captured = []
def chat(messages, **k):
    captured.append([m["content"] for m in messages])
    return json.dumps({"fixes": [{"i": 0, "vi": "Anh đoán em mới học được cách làm món tráng miệng ngon."},
                                 {"i": 1, "vi": "Vẫn sai rồi."}]}, ensure_ascii=False)
T.chat = chat
RV = [{"i": 0, "start": 0.0, "end": 3.0, "zh": "我猜你新学会做某种好吃的甜品。",
       "vi": "Tôi đoán cậu mới học được cách làm món tráng miệng ngon."},
      {"i": 1, "start": 3.0, "end": 6.0, "zh": "还是不对再猜", "vi": "Vẫn là không nên đoán tiếp."}]
for pn, plan in PLANS.items():
    captured.clear()
    res = T.review_batch(copy.deepcopy(RV), "PLAN", [], plan=copy.deepcopy(plan))
    out["review_" + pn] = {"res": {str(k): v for k, v in res.items()}, "msgs": list(captured)}
# run_translate (NMT primary, cấu hình hiện tại; fill cloud OK)
T._is_llama_local_model = lambda m: str(m or "").startswith("llama/") or str(m or "") in ("local", "llama")
T.is_local = lambda m: False
T.unload_local = lambda m: None
T._resolve_review_model = lambda wd_, m=None: m or "chatgpt/gpt-6"
series_glossary.apply = lambda wd_, plan: plan
series_glossary.save_from = lambda *a, **k: None
PC.ensure_analyze_before_translate = lambda wd_, plan, segments=None, force=False: (plan, {"skipped": True})
PC.run_post_translate_consistency = lambda wd_, rows_, plan, fix_with_gpt=True: {"ok": True}
mt_zh_vi.enabled = lambda: True
mt_zh_vi.resolve_model_id = lambda plan: "HachimiMT-60-zh-vi"
trace = []
preset_switcher.switch_preset = lambda pid, max_wait_sec=180: trace.append(("switch", pid)) or True
def ts(chunk, plan_block, prev_ctx, target=None, model=None, plan=None):
    trace.append(("ts", [(s["i"], s.get("text"), s.get("mt_vi")) for s in chunk], model))
    return {s["i"]: f"T{s['i']} ngươi" for s in chunk}
T._translate_safe = ts
SEGS = [{"i": 0, "start": 0.0, "end": 1.0, "text": "陈先生进入以后，"}, {"i": 1, "start": 1.1, "end": 2.0, "text": "我们就动手。"},
        {"i": 2, "start": 2.0, "end": 3.0, "text": "他来了"}, {"i": 3, "start": 3.0, "end": 4.0, "text": "你先走"},
        {"i": 4, "start": 4.1, "end": 5.0, "text": "我断后。"}]
DR = {0: "Sau khi anh Trần vào,", 1: "", 2: "他 đến", 3: "Ngươi đi trước", 4: "ta chặn hậu."}
tmp = Path(tempfile.mkdtemp())
for name, prim in [("rt_primary", True), ("rt_hint", False)]:
    trace.clear()
    mt_zh_vi.primary_mode = (lambda p: (lambda: p))(prim)
    mt_zh_vi.draft_rows = lambda items, plan=None: (trace.append(("nmt", [it["i"] for it in items])),
                                                    {it["i"]: DR.get(it["i"], "") for it in items})[1]
    wd = tmp / name; wd.mkdir()
    (wd / "manifest.json").write_text(json.dumps({"stages": {}}), encoding="utf-8")
    (wd / "glossary.json").write_text(json.dumps({"characters": [], "terms": [], "style_lock": {"mode": "mixed"}}), encoding="utf-8")
    (wd / "asr.json").write_text(json.dumps(SEGS, ensure_ascii=False), encoding="utf-8")
    T.run_translate(wd, auto_review=False, model=None if prim else "chatgpt/gpt-6")
    out[name] = {"trace": list(trace), "rows": json.loads((wd / "script.json").read_text(encoding="utf-8"))}
shutil.rmtree(tmp, ignore_errors=True)
print("@@JSON@@" + json.dumps(out, ensure_ascii=False, sort_keys=True))
'''


def _golden_dir() -> str:
    for c in (os.getenv("B3_GOLDEN_DIR") or "", str(ROOT.parent / "PinelineV6" / "data" / "golden")):
        if c and Path(c).is_dir():
            return c
    return ""


def _char_run(first: Path, tmp_path: Path, cfg: dict) -> dict:
    script = tmp_path / "char_b3.py"
    script.write_text(_CHAR_SCRIPT, encoding="utf-8")
    env = dict(os.environ, AGENT_BRAIN="0", PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    plans = {"mixed": PLAN_MIXED, "modern_blob_mixed": PLAN_MODERN_BLOB_MIXED, "modern": PLAN_MODERN,
             "ancient": PLAN_ANCIENT}
    p = subprocess.run(
        [sys.executable, str(script), str(first), str(ROOT), _golden_dir(), json.dumps(cfg),
         json.dumps(SAMPLE, ensure_ascii=False), json.dumps(plans, ensure_ascii=False)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300, env=env,
        cwd=str(tmp_path))
    assert p.returncode == 0, p.stderr[-3000:]
    line = [ln for ln in p.stdout.splitlines() if ln.startswith("@@JSON@@")][-1]
    return json.loads(line[len("@@JSON@@"):])


_BASE_CFG = {"REVIEW_PRONOUN_MASK": "1", "AUTO_SWITCH_PRESETS": "1", "TRANSLATE_PRESET": "gemma-test",
             "TRANSLATE_MODEL": "local", "REVIEW_CLOUD_RETRY": "0", "AUTO_REVIEW": "0"}


@pytest.mark.skipif(not (_BACKUP / "translate.py").is_file(), reason="không có bản gốc trước b3")
@pytest.mark.parametrize("cfg", [
    pytest.param(dict(_BASE_CFG), id="prod-default"),
    pytest.param(dict(_BASE_CFG, REVIEW_PRONOUN_MASK="0", REVIEW_PRONOUN_PLAN_GUIDE="0"), id="mask0-guide0"),
])
def test_default_identical_to_pre_b3(tmp_path, cfg):
    old_dir = tmp_path / "old"
    old_dir.mkdir()
    (old_dir / "translate.py").write_bytes((_BACKUP / "translate.py").read_bytes())
    new_dir = tmp_path / "new"
    new_dir.mkdir()
    (new_dir / "translate.py").write_bytes((ROOT / "translate.py").read_bytes())
    old = _char_run(old_dir, tmp_path, cfg)
    new = _char_run(new_dir, tmp_path, cfg)
    assert set(old) == set(new)
    for k in sorted(old):
        assert new[k] == old[k], f"mặc định lệch bản gốc ở {k}"
    # chắc kịch bản có nghĩa: nhánh mixed có đổi ngươi→cậu; có NMT + vá cloud
    assert old["post_mixed"][0]["vi"].startswith("Cậu")
    assert any(t[0] == "nmt" for t in old["rt_primary"]["trace"])
    if _golden_dir():
        assert any(k.startswith("golden_") for k in old)


@pytest.mark.skipif(not (_BACKUP / "translate.py").is_file(), reason="không có bản gốc trước b3")
def test_flags_on_actually_change_something(tmp_path):
    """Đối chứng: bật cờ thì KHÁC bản gốc (test đối chiếu không rỗng)."""
    cfg = dict(_BASE_CFG, PRONOUN_REGEX_MIXED="0", REVIEW_PRONOUN_MASK="0", HALFCUE_MERGE="1")
    old_dir = tmp_path / "old"
    old_dir.mkdir()
    (old_dir / "translate.py").write_bytes((_BACKUP / "translate.py").read_bytes())
    new_dir = tmp_path / "new"
    new_dir.mkdir()
    (new_dir / "translate.py").write_bytes((ROOT / "translate.py").read_bytes())
    old = _char_run(old_dir, tmp_path, cfg)
    new = _char_run(new_dir, tmp_path, cfg)
    assert new["post_mixed"] != old["post_mixed"]
    assert new["review_mixed"]["msgs"] != old["review_mixed"]["msgs"]
    assert new["rt_primary"]["trace"] != old["rt_primary"]["trace"]
    assert all((r.get("vi") or "").strip() for r in new["rt_primary"]["rows"])
