"""fix 2026-11-11 translate-b2 — Việc A (retry cloud khi Aurora limit) + Việc B (bỏ gemma khỏi
luồng dịch khi NMT primary + REVIEW cloud).

Không HTTP, không LLM, không GPU: `review_batch` / `_translate_safe` / `switch_preset` / NMT là giả;
thời gian giả (cloud_retry._sleep/_now) trừ 1 test nhiều luồng chạy thời gian thật ~2–3 s.
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import pytest
import requests

import engines.cloud_retry as CR
import engines.translate as T
from engines.llm import LLMUnavailable


# ───────────────────────── tiện ích ─────────────────────────

class FakeClock:
    def __init__(self, t0: float = 1_000_000.0):
        self.t = t0
        self.sleeps: list[float] = []
        self.lock = threading.Lock()
        self.on_sleep = None

    def now(self) -> float:
        with self.lock:
            return self.t

    def sleep(self, dt: float) -> None:
        with self.lock:
            self.sleeps.append(float(dt))
            self.t += float(dt)
        if self.on_sleep:
            self.on_sleep(self)


@pytest.fixture(autouse=True)
def _iso(monkeypatch):
    CR.reset_gates()
    monkeypatch.setattr(T, "_log_vram", lambda stage: None, raising=False)
    # F2 2026-11-12: mặc định đã là luồng simple — file này kiểm luồng CŨ → đặt legacy tường minh
    monkeypatch.setenv("TRANSLATE_PIPELINE", "legacy")
    yield
    CR.reset_gates()


@pytest.fixture
def clock(monkeypatch):
    c = FakeClock()
    monkeypatch.setattr(CR, "_sleep", c.sleep)
    monkeypatch.setattr(CR, "_now", c.now)
    monkeypatch.setattr(CR, "_rand", lambda: 0.5)   # jitter trung tính (×1.0)
    return c


def _aurora_429(msg: str = "Too Many Requests", retry_after: str | None = None) -> LLMUnavailable:
    """Lỗi y như llm._chatgpt_chat dựng sau translate-b2: HTTPError(response=r) làm __cause__."""
    resp = requests.Response()
    resp.status_code = 429
    if retry_after is not None:
        resp.headers["Retry-After"] = retry_after
    inner = requests.HTTPError(f"429 {msg}", response=resp)
    try:
        raise LLMUnavailable(f"Aurora/ChatGPT thất bại: {inner}") from inner
    except LLMUnavailable as e:
        return e


class SwitchSpy:
    def __init__(self, ok: bool = True):
        self.calls: list[str] = []
        self.ok = ok
        self._lk = threading.Lock()

    def __call__(self, preset_id, max_wait_sec=180):
        with self._lk:
            self.calls.append(preset_id)
        return self.ok


def _rows(n: int) -> list[dict]:
    return [{"i": i, "start": float(i), "end": float(i) + 1.0, "zh": f"第{i}句", "vi": f"vi{i}"}
            for i in range(n)]


def _job(tmp_path: Path, rows: list[dict], name: str = "job") -> Path:
    wd = tmp_path / name
    wd.mkdir()
    (wd / "script.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    (wd / "manifest.json").write_text(json.dumps({"stages": {"translate": {"status": "done"}}}),
                                      encoding="utf-8")
    return wd


def _read(wd: Path) -> dict[int, dict]:
    return {r["i"]: r for r in json.loads((wd / "script.json").read_text(encoding="utf-8"))}


def _cfg(monkeypatch, **kv):
    cfg = {"REVIEW_RETRY_BACKOFF_SEC": "0", "AUTO_SWITCH_PRESETS": "1",
           "REVIEW_PRONOUN_MASK": "0", "REVIEW_PRESET": "qwen-test",
           "TRANSLATE_PRESET": "gemma-test", "TRANSLATE_MODEL": "local",
           "REVIEW_CLOUD_RETRY": "4", "REVIEW_CLOUD_BACKOFF": "30,60,120,240"}
    cfg.update({k: str(v) for k, v in kv.items()})
    monkeypatch.setattr(T, "_cfg_get", lambda k, d=None: cfg.get(k, d))
    return cfg


def _llama(monkeypatch):
    monkeypatch.setattr(T, "_is_llama_local_model", lambda m: str(m or "").startswith("llama/")
                        or str(m or "") in ("local", "llama"))
    monkeypatch.setattr(T, "is_local", lambda m: False)
    monkeypatch.setattr(T, "unload_local", lambda m: None)


# ───────────────────────── Việc A: phân loại ─────────────────────────

@pytest.mark.parametrize("exc,want", [
    pytest.param(_aurora_429(), "limit", id="429-cause"),
    pytest.param(LLMUnavailable("Aurora/ChatGPT thất bại: 429 Too Many Requests"), "limit", id="429-msg"),
    pytest.param(LLMUnavailable("Gọi LLM thất bại sau 4 lần: 429 slow down"), "limit", id="429-9router"),
    pytest.param(RuntimeError("account pool: usage limit reached, try later"), "limit", id="limit-text"),
    pytest.param(RuntimeError("insufficient_quota"), "limit", id="quota-text"),
    pytest.param(LLMUnavailable("Aurora/ChatGPT thất bại: 503 Service Unavailable"), "transient", id="503"),
    pytest.param(requests.Timeout("read timed out"), "transient", id="timeout"),
    pytest.param(LLMUnavailable("Aurora/ChatGPT thất bại: HTTPConnectionPool read timed out"), "transient",
                 id="exhausted-no-code"),
    pytest.param(LLMUnavailable("Aurora/ChatGPT 413 (no-retry): Request Entity Too Large"), None, id="413"),
    pytest.param(LLMUnavailable("Aurora/ChatGPT 400 (no-retry): bad request"), None, id="400"),
    pytest.param(RuntimeError("LLM từ chối payload (422): context length"), None, id="422"),
    pytest.param(T.ReviewBadOutput("rỗng"), None, id="bad-output"),
    pytest.param(ValueError("parse"), None, id="valueerror"),
    pytest.param(LLMUnavailable("Chưa set LLM_API_KEY (pineline.config.json)."), None, id="no-key"),
    pytest.param(RuntimeError("stopped by user"), None, id="stop"),
])
def test_classify_cloud_retry(exc, want):
    assert CR.classify_cloud_retry(exc) == want


def test_retry_after_parse():
    assert CR.retry_after_seconds(_aurora_429(retry_after="17")) == 17.0
    assert CR.retry_after_seconds(RuntimeError('429 {"error":{"retry_after": 42}}')) == 42.0
    assert CR.retry_after_seconds(RuntimeError("Rate limit. Please try again in 20s.")) == 20.0
    assert CR.retry_after_seconds(RuntimeError("try again in 2 minutes")) == 120.0
    assert CR.retry_after_seconds(_aurora_429()) is None


def test_backoff_config_parse():
    cfg = {"REVIEW_CLOUD_RETRY": "2", "REVIEW_CLOUD_BACKOFF": "5, 10;20"}
    g = lambda k, d=None: cfg.get(k, d)  # noqa: E731
    assert CR.retry_count(g) == 2
    assert CR.backoff_schedule(g) == [5.0, 10.0, 20.0]
    assert CR.retry_count(lambda k, d=None: d) == 4
    assert CR.backoff_schedule(lambda k, d=None: d) == [30.0, 60.0, 120.0, 240.0]
    assert CR.local_fallback_enabled(lambda k, d=None: d) is True
    assert CR.local_fallback_enabled(lambda k, d=None: "0") is False


# ───────────────────────── Việc A: lô REVIEW ─────────────────────────

def test_review_429_k_times_then_ok_no_switch(monkeypatch, clock, capsys):
    import tools.preset_switcher as preset_switcher
    _cfg(monkeypatch)
    _llama(monkeypatch)
    spy = SwitchSpy()
    monkeypatch.setattr(preset_switcher, "switch_preset", spy)
    calls = []

    def rb(chunk_exp, plan_block, prev_ctx, model=None, **k):
        calls.append(model)
        if len(calls) <= 2:
            raise _aurora_429()
        return {0: "vi0 sửa"}

    monkeypatch.setattr(T, "review_batch", rb)
    rows = _rows(3)
    fixes, used = T._review_chunk_with_fallback(
        rows, rows, "", [], target="vi", rmodel="chatgpt/gpt-6", plan={}, exemplars_pool=rows,
        fb_state=T._new_review_fallback_state())
    assert fixes == {0: "vi0 sửa"} and used == "chatgpt/gpt-6"
    assert calls == ["chatgpt/gpt-6"] * 3, "phải thử lại CÙNG model cloud"
    assert spy.calls == [], "429 tạm thời không được đổi preset local"
    assert abs(sum(clock.sleeps) - (30 + 60)) < 1e-6, clock.sleeps
    assert max(clock.sleeps) <= CR.STOP_SLICE_SEC + 1e-9, "ngủ theo lát ≤2 s để kiểm .stop"
    out = capsys.readouterr().out
    assert "[review] Aurora limit — thử lại cloud lần 1/4 sau 30s" in out
    assert "lần 2/4 sau 60s" in out


def test_review_backoff_has_jitter(monkeypatch, clock):
    _cfg(monkeypatch, REVIEW_CLOUD_RETRY=1)
    _llama(monkeypatch)
    monkeypatch.setattr(CR, "_rand", lambda: 1.0)   # +10 %
    n = []

    def rb(*a, **k):
        n.append(1)
        if len(n) == 1:
            raise _aurora_429()
        return {}

    monkeypatch.setattr(T, "review_batch", rb)
    rows = _rows(2)
    T._review_chunk_with_fallback(rows, rows, "", [], target="vi", rmodel="chatgpt/x", plan={},
                                  exemplars_pool=rows, fb_state=T._new_review_fallback_state())
    assert abs(sum(clock.sleeps) - 33.0) < 1e-6


def test_review_uses_retry_after_header(monkeypatch, clock):
    _cfg(monkeypatch)
    _llama(monkeypatch)
    n = []

    def rb(*a, **k):
        n.append(1)
        if len(n) == 1:
            raise _aurora_429(retry_after="7")
        return {}

    monkeypatch.setattr(T, "review_batch", rb)
    rows = _rows(2)
    fixes, _m = T._review_chunk_with_fallback(rows, rows, "", [], target="vi", rmodel="chatgpt/x",
                                              plan={}, exemplars_pool=rows,
                                              fb_state=T._new_review_fallback_state())
    assert fixes == {}
    assert 7.0 <= sum(clock.sleeps) <= 7.0 + 0.5, clock.sleeps


def test_review_stop_during_wait(monkeypatch, clock, tmp_path):
    _cfg(monkeypatch)
    _llama(monkeypatch)
    stop = tmp_path / ".stop"

    def mark_stop(c):
        if sum(c.sleeps) >= 4.0:
            stop.write_text("1")

    clock.on_sleep = mark_stop
    monkeypatch.setattr(T, "review_batch", lambda *a, **k: (_ for _ in ()).throw(_aurora_429()))
    rows = _rows(2)
    with pytest.raises(RuntimeError, match="stopped by user"):
        T._review_chunk_with_fallback(rows, rows, "", [], target="vi", rmodel="chatgpt/x", plan={},
                                      exemplars_pool=rows, fb_state=T._new_review_fallback_state(),
                                      stop_path=stop)
    assert sum(clock.sleeps) <= 6.0 + 1e-6, "phải dừng trong ≤2 s sau khi có .stop"


def test_review_exhausted_then_local_fallback_once(monkeypatch, clock):
    import tools.preset_switcher as preset_switcher
    _cfg(monkeypatch, REVIEW_CLOUD_RETRY=2, REVIEW_LOCAL_FALLBACK=1)
    _llama(monkeypatch)
    spy = SwitchSpy()
    monkeypatch.setattr(preset_switcher, "switch_preset", spy)
    cloud, local = [], []

    def rb(chunk_exp, plan_block, prev_ctx, model=None, **k):
        if str(model).startswith("llama/"):
            local.append(1)
            return {}
        cloud.append(1)
        raise _aurora_429()

    monkeypatch.setattr(T, "review_batch", rb)
    st = T._new_review_fallback_state()
    rows = _rows(2)
    fixes, used = T._review_chunk_with_fallback(rows, rows, "", [], target="vi", rmodel="chatgpt/x",
                                                plan={}, exemplars_pool=rows, fb_state=st)
    assert fixes == {} and used == "llama/qwen-test"
    assert len(cloud) == 3 and spy.calls == ["qwen-test"]
    assert abs(sum(clock.sleeps) - 90.0) < 1e-6
    # lô sau: local đã mở cho lượt này → không chờ backoff cloud nữa
    before = sum(clock.sleeps)
    fixes2, used2 = T._review_chunk_with_fallback(rows, rows, "", [], target="vi", rmodel="chatgpt/x",
                                                  plan={}, exemplars_pool=rows, fb_state=st)
    assert fixes2 == {} and used2 == "llama/qwen-test"
    assert sum(clock.sleeps) == before and spy.calls == ["qwen-test"]


def test_review_exhausted_no_local_fallback(monkeypatch, clock):
    import tools.preset_switcher as preset_switcher
    _cfg(monkeypatch, REVIEW_CLOUD_RETRY=2, REVIEW_LOCAL_FALLBACK=0)
    _llama(monkeypatch)
    spy = SwitchSpy()
    monkeypatch.setattr(preset_switcher, "switch_preset", spy)
    monkeypatch.setattr(T, "review_batch", lambda *a, **k: (_ for _ in ()).throw(_aurora_429()))
    rows = _rows(2)
    fixes, used = T._review_chunk_with_fallback(rows, rows, "", [], target="vi", rmodel="chatgpt/x",
                                                plan={}, exemplars_pool=rows,
                                                fb_state=T._new_review_fallback_state())
    assert fixes is None and used == "chatgpt/x"
    assert spy.calls == []


@pytest.mark.parametrize("exc", [
    LLMUnavailable("Aurora/ChatGPT 400 (no-retry): bad"),
    T.ReviewBadOutput("rỗng"),
    RuntimeError("lỗi lạ"),
])
def test_review_non_retry_errors_no_sleep(monkeypatch, clock, exc):
    _cfg(monkeypatch)
    _llama(monkeypatch)
    monkeypatch.setattr(T, "review_batch", lambda *a, **k: (_ for _ in ()).throw(exc))
    rows = _rows(2)
    fixes, _m = T._review_chunk_with_fallback(rows, rows, "", [], target="vi", rmodel="chatgpt/x",
                                              plan={}, exemplars_pool=rows,
                                              fb_state=T._new_review_fallback_state())
    assert fixes is None and clock.sleeps == []


def test_local_review_model_never_retries(monkeypatch, clock):
    _cfg(monkeypatch)
    _llama(monkeypatch)
    monkeypatch.setattr(T, "review_batch", lambda *a, **k: (_ for _ in ()).throw(
        LLMUnavailable("Gọi LLM thất bại sau 4 lần: 503")))
    rows = _rows(2)
    with pytest.raises(LLMUnavailable):
        T._review_chunk_with_fallback(rows, rows, "", [], target="vi", rmodel="llama/qwen", plan={},
                                      exemplars_pool=rows, fb_state=T._new_review_fallback_state())
    assert clock.sleeps == []


def _review_env(monkeypatch, workers=1, rmodel="chatgpt/test", **cfg_kv):
    cfg = _cfg(monkeypatch, **cfg_kv)
    _llama(monkeypatch)
    monkeypatch.setattr(T, "run_review_pass1_full_vi", lambda wd_, rows_, plan, model=None: plan)
    monkeypatch.setattr(T, "_resolve_review_model", lambda wd_, m=None: m or rmodel)
    monkeypatch.setattr(T, "_review_parallel_workers", lambda wd_, m: workers)
    monkeypatch.setattr(T, "_filter_cosmetic_nmt_fixes", lambda fixes, rows, plan: fixes)
    import engines.pronoun_consistency as PC
    monkeypatch.setattr(PC, "run_post_translate_consistency",
                        lambda wd_, rows_, plan, fix_with_gpt=True: {"ok": True})
    monkeypatch.setattr(PC, "filter_review_fixes_for_lock", lambda raw, rows, plan: raw)
    import agents.agent_hang_fix as agent_hang_fix
    monkeypatch.setattr(agent_hang_fix, "fix_hang_job", lambda *a, **k: {"skipped": True})
    import engines.series_glossary as series_glossary
    monkeypatch.setattr(series_glossary, "save_from", lambda *a, **k: None)
    return cfg


def test_run_review_cloud_limit_exhausted_parks_without_switch(monkeypatch, clock, tmp_path):
    """REVIEW_LOCAL_FALLBACK=0: hết retry → lô lỗi → B1 thử lại → RuntimeError (park B2), không rv."""
    import tools.preset_switcher as preset_switcher
    _review_env(monkeypatch, workers=1, REVIEW_CLOUD_RETRY=2, REVIEW_LOCAL_FALLBACK=0)
    spy = SwitchSpy()
    monkeypatch.setattr(preset_switcher, "switch_preset", spy)
    monkeypatch.setattr(T, "review_batch", lambda *a, **k: (_ for _ in ()).throw(_aurora_429()))
    wd = _job(tmp_path, _rows(8))
    n0 = len(clock.sleeps)
    with pytest.raises(RuntimeError, match="REVIEW lỗi"):
        T.run_review(wd, batch=4)
    assert spy.calls == []
    assert not any(r.get("rv") for r in _read(wd).values())
    # review 2026-11-12: lô 1 chờ 30+60 rồi hết lượt; lô 2 dùng CHUNG ngân sách của đợt limit
    # ((30+60)×1,25+15 = 127,5 s) — không cộng dồn 2×90 s; lượt thử lại B1 KHÔNG chờ backoff nữa.
    budget = CR.outage_budget_sec(2, [30.0, 60.0, 120.0, 240.0])
    assert 90.0 <= sum(clock.sleeps[n0:]) <= budget + CR.STOP_SLICE_SEC + 1e-6, clock.sleeps


def test_run_review_parallel_limit_then_ok(monkeypatch, clock, tmp_path):
    """Nhiều luồng (đồng hồ giả) — 429 vài lần rồi OK: tất cả rv, không đổi preset."""
    import tools.preset_switcher as preset_switcher
    _review_env(monkeypatch, workers=4, REVIEW_CLOUD_RETRY=4)
    spy = SwitchSpy()
    monkeypatch.setattr(preset_switcher, "switch_preset", spy)
    lk = threading.Lock()
    n = {"c": 0}

    def rb(chunk_exp, *a, **k):
        with lk:
            n["c"] += 1
            c = n["c"]
        if c <= 3:
            raise _aurora_429()
        return {}

    monkeypatch.setattr(T, "review_batch", rb)
    wd = _job(tmp_path, _rows(16))
    T.run_review(wd, batch=4)
    assert spy.calls == []
    assert all(r.get("rv") for r in _read(wd).values())


def test_many_threads_share_one_gate_no_storm(monkeypatch):
    """Thời gian THẬT ~2–3 s: 8 luồng cùng gặp limit → sau làn đầu chỉ 1 probe/lần thử
    (không 8 luồng tự bắn lại mỗi mốc)."""
    monkeypatch.setattr(CR, "_rand", lambda: 0.5)
    t0 = time.time()
    open_at = t0 + 1.5
    lk = threading.Lock()
    stat = {"rejected": [], "ok": 0}

    def fn():
        now = time.time()
        if now < open_at:
            with lk:
                stat["rejected"].append(now - t0)
            raise _aurora_429()
        with lk:
            stat["ok"] += 1
        return "ok"

    errs = []
    barrier = threading.Barrier(8)

    def worker():
        try:
            barrier.wait()
            CR.call_with_cloud_retry(fn, model="chatgpt/gpt-6", retries=4, schedule=[1.0, 1.0, 1.0, 1.0],
                                     log=lambda s: None)
        except Exception as e:  # noqa: BLE001
            errs.append(e)

    ths = [threading.Thread(target=worker) for _ in range(8)]
    for th in ths:
        th.start()
    for th in ths:
        th.join(30)
    assert not errs and stat["ok"] == 8
    first_wave = [x for x in stat["rejected"] if x < 0.5]
    later = [x for x in stat["rejected"] if x >= 0.5]
    assert len(first_wave) <= 8
    assert len(later) <= 2, f"bão retry: {later}"
    assert time.time() - t0 < 10


def test_gate_released_when_probe_fails_non_limit(clock):
    g = CR.CloudGate("t")
    g.trip(clock.now() + 5)
    assert g.wait_turn() is True          # hết mốc → luồng này là probe
    g.release_probe()
    assert g.wait_turn() is True          # probe lỗi khác → luồng sau được dò lại
    g.success()
    assert g.wait_turn() is False and g.tripped is False


# ───────────────────────── Việc A: pass1 full file ─────────────────────────

def test_pass1_upload_retries_cloud(monkeypatch, clock, tmp_path):
    import engines.llm as llm
    _cfg(monkeypatch)
    n = []

    def up(path, purpose="assistants"):
        n.append(1)
        if len(n) == 1:
            raise _aurora_429()
        return {"id": "f1", "base": "b", "account_id": ""}

    monkeypatch.setattr(llm, "aurora_upload_file", up)
    monkeypatch.setattr(llm, "chatgpt_chat_with_file", lambda *a, **k: '{"style_brief":"x"}')
    p = tmp_path / "a.srt"
    p.write_text("1\n00:00:00,000 --> 00:00:01,000\nx\n", encoding="utf-8")
    got = T._pass1_upload_one_srt(p, "q", use_model="chatgpt/gpt-6", timeout=120)
    assert got == {"style_brief": "x"} and len(n) == 2
    assert abs(sum(clock.sleeps) - 30.0) < 1e-6


def test_pass1_exhausted_skips_chunk_upload(monkeypatch, clock, tmp_path):
    import engines.llm as llm
    _cfg(monkeypatch, REVIEW_CLOUD_RETRY=1, REVIEW_PASS1_FULL_VI=1)
    n = []

    def up(path, purpose="assistants"):
        n.append(Path(path).name)
        raise _aurora_429()

    monkeypatch.setattr(llm, "aurora_upload_file", up)
    chunk = []
    monkeypatch.setattr(T, "_pass1_upload_full_via_chunks", lambda *a, **k: chunk.append(1) or {})
    wd = tmp_path / "p1"
    wd.mkdir()
    plan = T.run_review_pass1_full_vi(wd, _rows(5), {"terms": []})
    assert isinstance(plan, dict)
    assert len(n) == 2, "1 lần + 1 retry"
    assert chunk == [], "cloud hết lượt thử → không đốt tiếp chunk upload"


# ───────────────────────── Việc B: run_translate ─────────────────────────

def _translate_job(tmp_path: Path, segs: list[dict]) -> Path:
    wd = tmp_path / "tj"
    wd.mkdir()
    (wd / "asr.json").write_text(json.dumps(segs, ensure_ascii=False), encoding="utf-8")
    (wd / "glossary.json").write_text(json.dumps({"characters": [], "terms": []}), encoding="utf-8")
    (wd / "manifest.json").write_text(json.dumps({"stages": {}}), encoding="utf-8")
    return wd


_SEGS = [
    {"i": 0, "start": 0.0, "end": 1.0, "text": "你好", "spk": "A"},
    {"i": 1, "start": 1.0, "end": 2.0, "text": "他来了", "spk": "B"},
    {"i": 2, "start": 2.0, "end": 3.0, "text": "他走了", "spk": "A"},
    {"i": 3, "start": 3.0, "end": 4.0, "text": "再见", "spk": "B"},
]


def _translate_env(monkeypatch, *, nmt_on=True, rmodel="chatgpt/gpt-6", drafts=None, **cfg_kv):
    import engines.mt_zh_vi as mt_zh_vi
    import tools.preset_switcher as preset_switcher
    import engines.pronoun_consistency as PC
    import engines.series_glossary as series_glossary
    _cfg(monkeypatch, **cfg_kv)
    _llama(monkeypatch)
    monkeypatch.setattr(T, "_resolve_review_model", lambda wd_, m=None: m or rmodel)
    monkeypatch.setattr(series_glossary, "apply", lambda wd_, plan: plan)
    monkeypatch.setattr(series_glossary, "save_from", lambda *a, **k: None)
    monkeypatch.setattr(PC, "ensure_analyze_before_translate",
                        lambda wd_, plan, segments=None, force=False: (plan, {"skipped": True}))
    monkeypatch.setattr(PC, "run_post_translate_consistency",
                        lambda wd_, rows_, plan, fix_with_gpt=True: {"ok": True})
    monkeypatch.setattr(mt_zh_vi, "enabled", lambda: nmt_on)
    monkeypatch.setattr(mt_zh_vi, "primary_mode", lambda: True)
    monkeypatch.setattr(mt_zh_vi, "resolve_model_id", lambda plan: "HachimiMT-60-zh-vi")
    d = drafts if drafts is not None else {0: "Xin chào", 1: "", 2: "他 đi rồi", 3: "Tạm biệt"}
    monkeypatch.setattr(mt_zh_vi, "draft_rows", lambda items, plan=None: {
        it["i"]: d.get(it["i"], "") for it in items})
    spy = SwitchSpy()
    monkeypatch.setattr(preset_switcher, "switch_preset", spy)
    ts_calls: list[tuple] = []
    return spy, ts_calls


def test_b_nmt_primary_cloud_review_no_switch_fill_with_rmodel(monkeypatch, tmp_path):
    spy, ts_calls = _translate_env(monkeypatch)

    def ts(chunk, plan_block, prev_ctx, target, model, plan=None):
        ts_calls.append((tuple(s["i"] for s in chunk), model))
        return {s["i"]: f"CLOUD{s['i']}" for s in chunk}

    monkeypatch.setattr(T, "_translate_safe", ts)
    wd = _translate_job(tmp_path, _SEGS)
    T.run_translate(wd, auto_review=False)
    assert spy.calls == [], "NMT primary + review cloud: KHÔNG được switch preset gemma"
    assert ts_calls and all(m == "chatgpt/gpt-6" for _ids, m in ts_calls), ts_calls
    filled = sorted(i for ids, _m in ts_calls for i in ids)
    assert filled == [1, 2], "chỉ câu NMT sót (rỗng/CJK) được vá"
    rows = _read(wd)
    assert rows[0]["vi"] == "Xin chào" and rows[1]["vi"] == "CLOUD1" and rows[2]["vi"] == "CLOUD2"
    assert not any(r.get("fill_pending") for r in rows.values())
    assert rows[1]["spk"] == "B"


def test_b_cloud_fill_fails_sets_fill_pending(monkeypatch, clock, tmp_path):
    spy, _ = _translate_env(monkeypatch, REVIEW_CLOUD_RETRY=1)
    n = []

    def ts(chunk, *a, **k):
        n.append(1)
        raise _aurora_429()

    monkeypatch.setattr(T, "_translate_safe", ts)
    wd = _translate_job(tmp_path, _SEGS)
    T.run_translate(wd, auto_review=False)
    rows = _read(wd)
    assert spy.calls == []
    assert rows[1]["vi"] == "" and rows[1]["fill_pending"] == 1 and rows[1]["spk"] == "B"
    assert rows[2]["vi"] == "" and rows[2]["fill_pending"] == 1
    assert "fill_pending" not in rows[0] and rows[0]["vi"] == "Xin chào"
    assert len(n) == 2, "cloud hết lượt → không gọi cloud tiếp trong lượt (không đốt 3 vòng vá)"


@pytest.mark.parametrize("case", ["nmt_off", "review_local", "fill_local"])
def test_b_old_configs_keep_switch(monkeypatch, tmp_path, case):
    kw: dict = {}
    if case == "nmt_off":
        kw["nmt_on"] = False
    elif case == "review_local":
        kw["rmodel"] = "llama/qwen36-turbo"
    else:
        kw["TRANSLATE_FILL_MODEL"] = "local"
    spy, ts_calls = _translate_env(monkeypatch, **kw)

    def ts(chunk, plan_block, prev_ctx, target, model, plan=None):
        ts_calls.append(model)
        return {s["i"]: f"L{s['i']}" for s in chunk}

    monkeypatch.setattr(T, "_translate_safe", ts)
    wd = _translate_job(tmp_path, _SEGS)
    T.run_translate(wd, auto_review=False)
    assert spy.calls == ["gemma-test"], f"cấu hình cũ phải switch preset như trước ({case})"
    assert ts_calls and all(m is None for m in ts_calls), "đường cũ: model=None → TRANSLATE_MODEL"
    assert not any(r.get("fill_pending") for r in _read(wd).values())


def test_b_nmt_crash_reverts_to_local(monkeypatch, tmp_path):
    import engines.mt_zh_vi as mt_zh_vi
    spy, ts_calls = _translate_env(monkeypatch)
    monkeypatch.setattr(mt_zh_vi, "draft_rows", lambda items, plan=None: (_ for _ in ()).throw(
        RuntimeError("cuda OOM")))
    monkeypatch.setattr(T, "_translate_safe",
                        lambda chunk, pb, ctx, target, model, plan=None:
                        ts_calls.append(model) or {s["i"]: "L" for s in chunk})
    wd = _translate_job(tmp_path, _SEGS)
    T.run_translate(wd, auto_review=False)
    assert spy.calls == ["gemma-test"]
    assert all(m is None for m in ts_calls)


# ───────────────────────── Việc B: cổng server ─────────────────────────

def test_gate_action_pure(monkeypatch, tmp_path):
    _translate_env(monkeypatch)
    wd = tmp_path
    assert T.post_translate_gate_action(wd, 0, 0) == "ok"
    assert T.post_translate_gate_action(wd, 3, 0) == "review_fill"
    assert T.post_translate_gate_action(wd, 3, 5) == "translate", "coverage gap thật → như cũ"
    assert T.post_translate_gate_action(wd, 0, 5) == "translate"


def test_gate_action_old_configs(monkeypatch, tmp_path):
    _translate_env(monkeypatch, nmt_on=False)
    assert T.post_translate_gate_action(tmp_path, 3, 0) == "translate"
    _translate_env(monkeypatch, rmodel="llama/qwen")
    assert T.post_translate_gate_action(tmp_path, 3, 0) == "translate"
    _translate_env(monkeypatch, AUTO_REVIEW=0)
    assert T.post_translate_gate_action(tmp_path, 3, 0) == "translate"


def _server_auto_gpu(monkeypatch, tmp_path, *, cloud: bool):
    server = pytest.importorskip("server")
    _translate_env(monkeypatch, nmt_on=cloud)
    monkeypatch.setattr(server, "WORK_ROOT", tmp_path)
    wd = tmp_path / "j1"
    wd.mkdir()
    (wd / "manifest.json").write_text(json.dumps({"stages": {}}), encoding="utf-8")
    (wd / "asr.json").write_text(json.dumps(_SEGS, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(server, "_part_pipeline_complete", lambda wd_: False)
    monkeypatch.setattr(server, "free_gpu_vram", lambda *a, **k: None)
    monkeypatch.setattr(server, "_resolve_asr_engine", lambda wd_, e=None: "x")
    monkeypatch.setattr(server, "_asr_script", lambda e: "x.py")
    monkeypatch.setattr(server, "_run_engine", lambda *a, **k: None)
    tr_calls, rv_calls = [], []

    def fake_translate(wd_, *a, **k):
        tr_calls.append(k)
        rows = [{"i": s["i"], "start": s["start"], "end": s["end"], "zh": s["text"],
                 "vi": "" if s["i"] == 1 else "x", "rv": 1} for s in _SEGS]
        (Path(wd_) / "script.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")

    def fake_review(wd_, *a, **k):
        rv_calls.append(k)
        rows = json.loads((Path(wd_) / "script.json").read_text(encoding="utf-8"))
        for r in rows:
            r["vi"] = r["vi"] or "CLOUD"
            r["rv"] = 1
        (Path(wd_) / "script.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr(server, "run_translate", fake_translate)
    monkeypatch.setattr(T, "run_review", fake_review)
    monkeypatch.setattr(server, "translate_ready_for_tts", lambda wd_: (False, "test dừng ở đây"))
    server._auto_gpu("j1", "Tiếng Việt", "replace", 1.0, 0.0, False)
    return tr_calls, rv_calls


def test_server_gate_cloud_does_not_recall_translate(monkeypatch, tmp_path):
    tr_calls, rv_calls = _server_auto_gpu(monkeypatch, tmp_path, cloud=True)
    assert len(tr_calls) == 1, "NMT primary + review cloud: KHÔNG gọi lại run_translate (đường gemma)"
    assert len(rv_calls) == 1 and rv_calls[0].get("force") is False


def test_server_gate_old_config_recalls_translate(monkeypatch, tmp_path):
    tr_calls, rv_calls = _server_auto_gpu(monkeypatch, tmp_path, cloud=False)
    assert len(tr_calls) == 2 and tr_calls[1].get("batch") == 25
    assert rv_calls == []


# ───────────────────────── Việc B: run_review bước 0 ─────────────────────────

def test_review_step0_uses_rmodel_and_postpass_only_patched(monkeypatch, tmp_path):
    import engines.mt_zh_vi as mt_zh_vi
    _review_env(monkeypatch, workers=1, rmodel="chatgpt/gpt-6")
    monkeypatch.setattr(mt_zh_vi, "enabled", lambda: True)
    monkeypatch.setattr(mt_zh_vi, "primary_mode", lambda: True)
    rows = _rows(8)
    for r in rows:
        r["rv"] = 1
    rows[2]["vi"] = ""                       # NMT sót
    rows[5]["vi"] = ""                       # NMT sót
    rows[5]["spk"] = "B"
    rows[6]["manual"] = 1                     # câu sửa tay — không đụng
    rows[6]["vi"] = "SỬA TAY"
    wd = _job(tmp_path, rows)
    ts_models = []

    def ts(payload, plan_block, ctx, target=None, model=None, plan=None):
        ts_models.append(model)
        return {p["i"]: f"CLOUD{p['i']}" for p in payload}

    monkeypatch.setattr(T, "_translate_safe", ts)
    post_calls: dict[str, list] = {"lock": [], "style": [], "pron": []}
    monkeypatch.setattr(T, "apply_hard_term_locks",
                        lambda rs, plan=None: post_calls["lock"].append(sorted(r["i"] for r in rs)) or 0)
    monkeypatch.setattr(T, "apply_style_polish",
                        lambda rs, plan=None: post_calls["style"].append(sorted(r["i"] for r in rs)) or 0)
    monkeypatch.setattr(T, "apply_pronoun_postpass",
                        lambda rs, plan=None: post_calls["pron"].append(sorted(r["i"] for r in rs)) or 0)
    reviewed = []

    def rb(chunk_exp, plan_block, prev_ctx, model=None, **k):
        reviewed.append((model, [r["i"] for r in chunk_exp]))
        return {}

    monkeypatch.setattr(T, "review_batch", rb)
    T.run_review(wd, batch=40)
    assert ts_models and all(m == "chatgpt/gpt-6" for m in ts_models), ts_models
    for k in ("lock", "style", "pron"):
        assert post_calls[k][0] == [2, 5], f"hậu kỳ {k} phải chạy riêng trên câu vừa vá: {post_calls[k]}"
    out = _read(wd)
    assert out[2]["vi"] == "CLOUD2" and out[5]["vi"] == "CLOUD5" and out[5]["spk"] == "B"
    assert out[6]["vi"] == "SỬA TAY"
    seen = {i for _m, ids in reviewed for i in ids}
    assert {2, 5} <= seen, "câu vừa vá phải được lô REVIEW soát (bỏ rv cũ)"
    assert all(r.get("rv") for r in out.values())


def test_review_step0_cloud_fail_sets_fill_pending(monkeypatch, clock, tmp_path):
    import engines.mt_zh_vi as mt_zh_vi
    _review_env(monkeypatch, workers=1, rmodel="chatgpt/gpt-6", REVIEW_CLOUD_RETRY=1)
    monkeypatch.setattr(mt_zh_vi, "enabled", lambda: True)
    monkeypatch.setattr(mt_zh_vi, "primary_mode", lambda: True)
    rows = _rows(4)
    rows[1]["vi"] = ""
    rows[1]["spk"] = "B"
    wd = _job(tmp_path, rows)
    n = []
    monkeypatch.setattr(T, "_translate_safe", lambda *a, **k: n.append(1) or (_ for _ in ()).throw(_aurora_429()))
    monkeypatch.setattr(T, "review_batch", lambda *a, **k: {})
    T.run_review(wd, batch=40)
    out = _read(wd)
    assert out[1]["vi"] == "" and out[1]["fill_pending"] == 1 and out[1]["spk"] == "B"
    assert len(n) == 2, "hết retry → không cứu từng câu bằng cloud nữa"


def test_review_step0_old_config_uses_tmodel(monkeypatch, tmp_path):
    import engines.mt_zh_vi as mt_zh_vi
    _review_env(monkeypatch, workers=1, rmodel="chatgpt/gpt-6")
    monkeypatch.setattr(mt_zh_vi, "enabled", lambda: False)
    rows = _rows(3)
    rows[1]["vi"] = ""
    wd = _job(tmp_path, rows)
    models = []
    monkeypatch.setattr(T, "_translate_safe",
                        lambda payload, pb, ctx, target=None, model=None, plan=None:
                        models.append(model) or {p["i"]: "L" for p in payload})
    monkeypatch.setattr(T, "review_batch", lambda *a, **k: {})
    T.run_review(wd, batch=40)
    assert models == ["local"], "cấu hình cũ: vá bằng TRANSLATE_MODEL như trước"
    assert "fill_pending" not in _read(wd)[1]


# ───────────────────────── log VRAM ─────────────────────────

def test_log_vram(monkeypatch, capsys):
    import shutil
    import subprocess
    monkeypatch.undo()   # bỏ patch _log_vram của fixture autouse
    monkeypatch.setattr(shutil, "which", lambda name: "/x/nvidia-smi")

    class R:
        returncode = 0
        stdout = "5120, 12288\n"

    seen = {}

    def run(cmd, **k):
        seen["timeout"] = k.get("timeout")
        return R()

    monkeypatch.setattr(subprocess, "run", run)
    T._log_vram("translate:start")
    assert "[vram] translate:start 5120/12288 MiB" in capsys.readouterr().out
    assert seen["timeout"] == 3
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(subprocess.TimeoutExpired("x", 3)))
    T._log_vram("review:end")   # không ném
    monkeypatch.setattr(shutil, "which", lambda name: None)
    T._log_vram("review:end")
