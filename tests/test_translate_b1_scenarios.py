"""Kịch bản TÍCH HỢP cho fix translate-b1 (review độc lập 2026-11-11).

run_review chạy ĐẦU-CUỐI (review_batch / _parse_review_fixes / _review_chunk_with_fallback /
_apply_result / thử lại B1 / park B2 đều là code thật) — chỉ `chat` (LLM) và
`preset_switcher.switch_preset` là giả. Không HTTP, không LLM, không GPU.

Kiểm:
 (a) không câu nào rv mà chưa nằm trong một lần gọi REVIEW trả kết quả HỢP LỆ;
 (b) câu manual giữ nguyên vi;
 (c) switch_preset (giả) gọi ≤ 1 lần / lượt run_review;
 (d) không treo / deadlock (kể cả switch_preset ném exception) — mỗi lượt có timeout;
 (e) lô lỗi → RuntimeError (park) và lượt sau resume đúng phần chưa rv;
 (f) run_translate giữ trường thêm của asr.json qua resume, không sinh src_i.
"""
from __future__ import annotations

import json
import random
import threading
from pathlib import Path

import pytest
import requests

import engines.translate as T
from engines.llm import LLMUnavailable

N_ROWS = 300


def _rows(n: int, manual_every: int = 13) -> list[dict]:
    rows = []
    for i in range(n):
        r = {"i": i, "start": float(i), "end": float(i) + 1.5,
             "zh": f"这是第{i}句话。", "vi": f"Đây là câu số {i}."}
        if i % manual_every == 5:
            r["manual"] = 1
            r["vi"] = f"NGƯỜI SỬA TAY {i}."
        rows.append(r)
    return rows


def _job(tmp_path: Path, rows: list[dict]) -> Path:
    wd = tmp_path / "job"
    wd.mkdir()
    (wd / "script.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    (wd / "manifest.json").write_text(
        json.dumps({"stages": {"translate": {"status": "done"}}}), encoding="utf-8")
    return wd


def _env(monkeypatch, workers: int):
    # translate-b2: REVIEW_CLOUD_RETRY=0 → kịch bản C9/B1 như đợt 1 (retry cloud: test_translate_b2)
    cfg = {"REVIEW_RETRY_BACKOFF_SEC": "0", "AUTO_SWITCH_PRESETS": "0", "REVIEW_CLOUD_RETRY": "0",
           "REVIEW_PRONOUN_MASK": "0", "REVIEW_PRESET": "qwen-test"}
    monkeypatch.setattr(T, "run_review_pass1_full_vi", lambda wd_, rows_, plan, model=None: plan)
    monkeypatch.setattr(T, "_resolve_review_model", lambda wd_, m=None: "chatgpt/test")
    monkeypatch.setattr(T, "_review_parallel_workers", lambda wd_, m: workers)
    monkeypatch.setattr(T, "is_local", lambda m: False)
    monkeypatch.setattr(T, "unload_local", lambda m: None)
    monkeypatch.setattr(T, "_cfg_get", lambda k, d=None: cfg.get(k, d))
    monkeypatch.setattr(T, "_is_llama_local_model", lambda m: str(m or "").startswith("llama/"))
    # không cosmetic-filter: để fix giả («LLMFIX») đi thẳng tới _apply_result
    monkeypatch.setattr(T, "_filter_cosmetic_nmt_fixes", lambda fixes, rows, plan: fixes)
    import engines.pronoun_consistency as PC
    monkeypatch.setattr(PC, "run_post_translate_consistency",
                        lambda wd_, rows_, plan, fix_with_gpt=True: {"ok": True})
    monkeypatch.setattr(PC, "filter_review_fixes_for_lock", lambda raw, rows, plan: raw)
    import agents.agent_hang_fix as agent_hang_fix
    monkeypatch.setattr(agent_hang_fix, "fix_hang_job", lambda *a, **k: {"skipped": True})
    import engines.series_glossary as series_glossary
    monkeypatch.setattr(series_glossary, "save_from", lambda *a, **k: None)


def _http(code: int) -> requests.HTTPError:
    resp = requests.Response()
    resp.status_code = code
    return requests.HTTPError(f"{code} fake", response=resp)


class FakeLLM:
    """chat() giả: ngẫu nhiên theo seed, an toàn luồng; ghi lại i nào được soát HỢP LỆ."""

    CLOUD_MIX = [
        ("valid", 40), ("empty_fixes", 12), ("fenced", 5), ("prose_obj", 3),
        ("empty", 5), ("truncated", 6), ("no_fixes_key", 2), ("garbage", 2),
        ("e429", 7), ("e500", 4), ("e413", 4), ("timeout", 4), ("e400", 2),
        ("unavailable", 3), ("ctx400", 2),
        ("prose_arr", 2), ("think", 2), ("trunc_br", 3),
    ]

    def __init__(self, seed: int, local_fail: float = 0.1, cloud_mix=None):
        self.rng = random.Random(seed)
        self.lk = threading.Lock()
        self.valid_ids: set[int] = set()
        self.calls = 0
        self.local_calls = 0
        self.local_fail = local_fail
        mix = cloud_mix or self.CLOUD_MIX
        self.kinds = [k for k, w in mix for _ in range(w)]

    @staticmethod
    def _ids(messages) -> list[int]:
        user = messages[-1]["content"]
        payload = json.loads(user.rsplit("\n\n", 1)[1])
        return [int(p["i"]) for p in payload]

    def _fixes(self, ids):
        # sửa ~1/3 câu, KỂ CẢ câu manual (để kiểm C2)
        return [{"i": i, "vi": f"LLMFIX {i}."} for i in ids if i % 3 == 2]

    def __call__(self, messages, model=None, **kw):
        ids = self._ids(messages)
        with self.lk:
            self.calls += 1
            local = str(model or "").startswith("llama/")
            if local:
                self.local_calls += 1
                kind = "empty" if self.rng.random() < self.local_fail else "valid"
            else:
                kind = self.rng.choice(self.kinds)
            if kind in ("valid", "empty_fixes", "fenced", "prose_obj", "prose_arr", "think"):
                self.valid_ids.update(ids)
        fx = self._fixes(ids)
        if kind == "valid":
            return json.dumps({"fixes": fx}, ensure_ascii=False)
        if kind == "empty_fixes":
            return '{"fixes": []}'
        if kind == "fenced":
            return "```json\n" + json.dumps({"fixes": fx}, ensure_ascii=False) + "\n```"
        if kind == "prose_obj":
            return "Kết quả:\n" + json.dumps({"fixes": fx}, ensure_ascii=False) + "\nXong."
        if kind == "prose_arr":
            return "Kết quả:\n" + json.dumps(fx or [{"i": ids[0], "vi": f"LLMFIX {ids[0]}."}],
                                             ensure_ascii=False)
        if kind == "think":
            return "<think>xét {i} từng câu</think>\n" + json.dumps({"fixes": fx}, ensure_ascii=False)
        if kind == "trunc_br":
            # JSON cụt mà bên trong có «[]» / object con trọn — KHÔNG được coi là hợp lệ
            return '{"fixes":[{"i":%d,"vi":"[]"},{"i":%d,"vi":"Một' % (ids[0], ids[-1])
        if kind == "empty":
            return ""
        if kind == "truncated":
            s = json.dumps({"fixes": fx or [{"i": ids[0], "vi": "x"}]}, ensure_ascii=False)
            return s[: max(5, len(s) * 2 // 3)]
        if kind == "no_fixes_key":
            return '{"items": []}'
        if kind == "garbage":
            return "Xin lỗi, tôi không thể giúp."
        if kind == "e429":
            raise _http(429)
        if kind == "e500":
            raise _http(500)
        if kind == "e413":
            raise _http(413)
        if kind == "e400":
            raise _http(400)
        if kind == "ctx400":
            resp = requests.Response()
            resp.status_code = 400
            raise requests.HTTPError("400 maximum context length exceeded", response=resp)
        if kind == "timeout":
            raise requests.Timeout("read timed out")
        if kind == "unavailable":
            raise LLMUnavailable("hết lượt thử")
        raise AssertionError(kind)


class SwitchSpy:
    def __init__(self, mode: str):
        self.mode = mode  # ok | fail | raise
        self.calls = 0
        self.lk = threading.Lock()

    def __call__(self, preset_id, max_wait_sec=180):
        with self.lk:
            self.calls += 1
        if self.mode == "raise":
            raise RuntimeError("llama-server không lên (giả)")
        return self.mode == "ok"


def _run_review_with_timeout(wd: Path, batch: int, timeout: float = 60.0):
    box: dict = {}

    def _t():
        try:
            box["res"] = T.run_review(wd, batch=batch)
        except BaseException as e:  # noqa: BLE001
            box["exc"] = e

    th = threading.Thread(target=_t, daemon=True)
    th.start()
    th.join(timeout)
    assert not th.is_alive(), "run_review treo (deadlock?)"
    return box


def _read(wd: Path) -> dict[int, dict]:
    return {r["i"]: r for r in json.loads((wd / "script.json").read_text(encoding="utf-8"))}


@pytest.mark.parametrize("seed", list(range(8)))
@pytest.mark.parametrize("switch_mode", ["ok", "fail", "raise"])
@pytest.mark.parametrize("workers", [1, 6])
def test_run_review_end_to_end_chaos(monkeypatch, tmp_path, seed, switch_mode, workers):
    import tools.preset_switcher as preset_switcher
    base = _rows(N_ROWS + seed * 25)
    manual_vi = {r["i"]: r["vi"] for r in base if r.get("manual")}
    wd = _job(tmp_path, base)
    _env(monkeypatch, workers)
    fake = FakeLLM(seed)
    monkeypatch.setattr(T, "chat", fake)
    finished = False
    for lượt in range(12):
        spy = SwitchSpy(switch_mode)
        monkeypatch.setattr(preset_switcher, "switch_preset", spy)
        box = _run_review_with_timeout(wd, batch=20)
        rows = _read(wd)
        # (c) ≤ 1 lần switch / lượt
        assert spy.calls <= 1, f"lượt {lượt}: switch_preset gọi {spy.calls} lần"
        # (a) rv ⇒ đã nằm trong 1 lần gọi trả kết quả hợp lệ
        bad = [i for i, r in rows.items() if r.get("rv") and i not in fake.valid_ids]
        assert not bad, f"rv mà chưa soát hợp lệ: {bad[:10]}"
        # (b) manual giữ nguyên
        for i, v in manual_vi.items():
            assert rows[i]["vi"] == v, f"manual {i} bị ghi đè: {rows[i]['vi']!r}"
        if "exc" in box:
            # (e) park: chỉ được là RuntimeError «REVIEW lỗi … lô» hoặc LLMUnavailable (local chết)
            e = box["exc"]
            assert isinstance(e, (RuntimeError,)), repr(e)
            assert "REVIEW lỗi" in str(e) or isinstance(e, LLMUnavailable), str(e)
            assert any(not r.get("rv") for r in rows.values()), "park mà mọi câu đã rv"
            continue
        assert all(r.get("rv") for r in rows.values()), "xong lượt mà còn câu chưa rv"
        finished = True
        break
    assert finished, "12 lượt vẫn chưa soát xong"
    rows = _read(wd)
    # fix thật sự được áp cho câu thường
    assert any(str(r["vi"]).startswith("LLMFIX") for r in rows.values())
    assert len(rows) == len(base)


def test_run_review_cloud_down_local_dead_parks_every_round(monkeypatch, tmp_path):
    """Cloud luôn 500 + switch hỏng: mỗi lượt park, 0 câu rv, switch đúng 1 lần/lượt."""
    import tools.preset_switcher as preset_switcher
    wd = _job(tmp_path, _rows(200))
    _env(monkeypatch, workers=6)
    fake = FakeLLM(1, cloud_mix=[("e500", 1)])
    monkeypatch.setattr(T, "chat", fake)
    for _ in range(3):
        spy = SwitchSpy("fail")
        monkeypatch.setattr(preset_switcher, "switch_preset", spy)
        box = _run_review_with_timeout(wd, batch=20)
        assert isinstance(box.get("exc"), RuntimeError) and "REVIEW lỗi" in str(box["exc"])
        assert spy.calls == 1
        assert not any(r.get("rv") for r in _read(wd).values())
    assert fake.local_calls == 0


def test_run_review_cloud_quota_local_ok_finishes_in_one_round(monkeypatch, tmp_path):
    """Cloud luôn 429, local OK: 1 lần switch, mọi lô chạy local TUẦN TỰ, xong 1 lượt."""
    import tools.preset_switcher as preset_switcher
    wd = _job(tmp_path, _rows(240))
    _env(monkeypatch, workers=6)
    fake = FakeLLM(2, local_fail=0.0, cloud_mix=[("e429", 1)])
    conc = {"now": 0, "max": 0}
    lk = threading.Lock()
    orig = fake.__call__

    def chat(messages, model=None, **kw):
        if str(model or "").startswith("llama/"):
            with lk:
                conc["now"] += 1
                conc["max"] = max(conc["max"], conc["now"])
            try:
                return orig(messages, model=model, **kw)
            finally:
                with lk:
                    conc["now"] -= 1
        return orig(messages, model=model, **kw)

    monkeypatch.setattr(T, "chat", chat)
    spy = SwitchSpy("ok")
    monkeypatch.setattr(preset_switcher, "switch_preset", spy)
    box = _run_review_with_timeout(wd, batch=20)
    assert "exc" not in box, box.get("exc")
    assert spy.calls == 1
    assert conc["max"] == 1, "request local phải tuần tự"
    assert all(r.get("rv") for r in _read(wd).values())


# ───────────────────────── T18 + resume ─────────────────────────

def _translate_env(monkeypatch):
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


def test_t18_run_translate_resume_keeps_fields_no_src_i(monkeypatch, tmp_path):
    wd = tmp_path / "jt"
    wd.mkdir()
    segs = [{"i": i, "start": float(i), "end": i + 1.0, "text": f"第{i}句", "spk": f"S{i % 3}",
             "asr_conf": round(0.5 + i / 400, 3), "words": [{"w": "x"}], "src_i": 99}
            for i in range(120)]
    (wd / "asr.json").write_text(json.dumps(segs, ensure_ascii=False), encoding="utf-8")
    (wd / "glossary.json").write_text(json.dumps({"characters": [], "terms": []}), encoding="utf-8")
    (wd / "manifest.json").write_text(json.dumps({"stages": {}}), encoding="utf-8")
    _translate_env(monkeypatch)
    # lượt 1: «LLM» bỏ trống câu lẻ
    monkeypatch.setattr(T, "_translate_safe",
                        lambda chunk, *a, **k: {s["i"]: f"VI{s['i']}" for s in chunk if s["i"] % 2 == 0})
    try:
        T.run_translate(wd, auto_review=False, mode="batch")
    except Exception:  # noqa: BLE001 — còn câu trống có thể báo lỗi; script vẫn phải ghi
        pass
    rows1 = json.loads((wd / "script.json").read_text(encoding="utf-8"))
    assert all("src_i" not in r for r in rows1), "src_i từ asr không được chép (resume tưởng post-split)"
    # lượt 2: resume — vá phần trống, không remap sai
    monkeypatch.setattr(T, "_translate_safe",
                        lambda chunk, *a, **k: {s["i"]: f"VI{s['i']}" for s in chunk})
    T.run_translate(wd, auto_review=False, mode="batch")
    rows = json.loads((wd / "script.json").read_text(encoding="utf-8"))
    assert len(rows) == len(segs)
    for r in rows:
        s = segs[r["i"]]
        assert r["vi"] == f"VI{r['i']}"
        assert r["spk"] == s["spk"] and r["asr_conf"] == s["asr_conf"]
        assert "words" not in r and "text" not in r and "src_i" not in r
        assert r["zh"] == s["text"]


# ───────────────────────── review 2026-11-11: sửa thêm ─────────────────────────

@pytest.mark.parametrize("out,want", [
    # JSON TRỌN giữa chữ thừa → hợp lệ (object parse trọn mà thiếu «fixes» vẫn là lỗi)
    ('Đây là kết quả:\n[{"i":1,"vi":"a"}]', {1: "a"}),
    ('<think>xem {i} nào</think>\n{"fixes":[{"i":1,"vi":"a"}]}', {1: "a"}),
    ('<think>ok</think>{"fixes":[]}', {}),
    ('Ghi chú: {i} là chỉ số. {"fixes":[]}', {}),
    ('{"result":{"fixes":[{"i":2,"vi":"b"}]}}', None),  # bọc lạ → vẫn chặt
    ('[{"i":1,"vi":"a"}]', {1: "a"}),
    ('{"fixes":[]}', {}),
    # cụt / mơ hồ → None (lô lỗi)
    ('{"fixes":[{"i":1,"vi":"[]"},{"i":2,"vi":"abc', None),
    ('Kết quả: [{"i":1,"vi":"a"},{"i":2,"vi":"b', None),
    ('<think>đang nghĩ {"fixes":[]', None),
    ('Không cần sửa, fixes=[]', None),
    ('[{"i":1,"zh":"x","vi_nhap":"y"}] rồi', None),
    ('{"fixes": null}', None),
    ("", None),
])
def test_review_parse_embedded_json(out, want):
    assert T._parse_review_fixes(out) == want


@pytest.mark.parametrize("vi,want", [
    ("Cậu chủ, mời vào.", "Cậu chủ, mời vào."),
    ("Cậu ấm nhà họ Lâm.", "Cậu ấm nhà họ Lâm."),
    ("Cậu Ba về rồi.", "Cậu Ba về rồi."),
    ("Cậu này là ai?", "Cậu này là ai?"),
    ("Cậu con trai nhà họ Lâm đâu?", "Cậu con trai nhà họ Lâm đâu?"),
    ("Cậu thiếu gia kia ngạo quá.", "Cậu thiếu gia kia ngạo quá."),
    ("cậu chàng ngốc nghếch", "cậu chàng ngốc nghếch"),
    ("Cậu cháu họ về rồi.", "Cậu cháu họ về rồi."),
    ("Cậu nói gì?", "Ngươi nói gì?"),
    ("Tôi và cậu à.", "Tôi và ngươi à."),
    ("Thôi mà cậu à.", "Thôi mà ngươi à."),
    ("Tôi bảo các cậu lui ra.", "Tôi bảo các ngươi lui ra."),
    ("Các cậu lui ra.", "Các ngươi lui ra."),
    ("Đi đi. các cậu lui ra.", "Đi đi. Các ngươi lui ra."),
])
def test_c3_real_film_cases(vi, want):
    import engines.pronoun_register_policy as RP
    assert RP.mechanical_cau_to_formal(vi, "ngươi") == want
