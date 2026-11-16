"""review 2026-11-12 translate-b2 — kịch bản đầu-cuối cho cửa chờ cloud (Việc A) và bỏ gemma
khỏi bước dịch (Việc B). Không HTTP / LLM / GPU: chat, NMT, switch_preset đều giả.

- Đồng hồ «tăng tốc» (ScaledClock) cho test nhiều luồng: thời gian ảo chạy nhanh K lần, mọi
  luồng thấy cùng một đồng hồ (FakeClock cộng dồn của test_translate_b2 không dùng được khi
  nhiều luồng ngủ song song).
- Đối chiếu cấu hình cũ (REVIEW_CLOUD_RETRY=0, TRANSLATE_FILL_MODEL=local) với BẢN GỐC trước
  b2 trong `.backup_edit_20261111_translate_b2/` (bỏ qua nếu không có thư mục backup).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest
import requests

import engines.cloud_retry as CR
import engines.translate as T
from engines.llm import LLMUnavailable
from tests.test_translate_b2 import (  # helper dùng chung (tên bắt đầu bằng _ → pytest không thu lại test)
    FakeClock,
    SwitchSpy,
    _SEGS,
    _aurora_429,
    _cfg,
    _job,
    _read,
    _review_env,
    _rows,
    _translate_env,
    _translate_job,
)

ROOT = Path(__file__).resolve().parents[1]


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
    monkeypatch.setattr(CR, "_rand", lambda: 0.5)
    return c


class ScaledClock:
    """Thời gian ảo = K × thời gian thật (chung mọi luồng)."""

    def __init__(self, k: float = 200.0, t0: float = 5_000_000.0):
        self.k = k
        self.t0 = t0
        self.r0 = time.perf_counter()   # monotonic trên Windows thô ~15,6 ms (×200 = 3 s ảo)

    def now(self) -> float:
        return self.t0 + (time.perf_counter() - self.r0) * self.k

    def sleep(self, dt: float) -> None:
        time.sleep(max(0.0, dt) / self.k)


@pytest.fixture
def fast(monkeypatch):
    c = ScaledClock()
    monkeypatch.setattr(CR, "_sleep", c.sleep)
    monkeypatch.setattr(CR, "_now", c.now)
    monkeypatch.setattr(CR, "_rand", lambda: 0.5)
    return c


def _err(status: int, retry_after: str | None = None) -> LLMUnavailable:
    """Lỗi y như llm._chatgpt_chat dựng: LLMUnavailable(...) from HTTPError(response=r)."""
    resp = requests.Response()
    resp.status_code = status
    if retry_after is not None:
        resp.headers["Retry-After"] = retry_after
    inner = requests.HTTPError(f"{status} upstream", response=resp)
    try:
        raise LLMUnavailable(f"Aurora/ChatGPT thất bại: {inner}") from inner
    except LLMUnavailable as e:
        return e


def _run_threads(n: int, target) -> list[BaseException | None]:
    out: list[BaseException | None] = [None] * n
    bar = threading.Barrier(n)

    def w(k: int) -> None:
        try:
            bar.wait()
            target(k)
        except BaseException as e:  # noqa: BLE001
            out[k] = e

    ths = [threading.Thread(target=w, args=(k,), daemon=True) for k in range(n)]
    for th in ths:
        th.start()
    for th in ths:
        th.join(60)
        assert not th.is_alive(), "luồng treo (deadlock cửa chờ?)"
    return out


# ───────────────────────── Việc A: cửa chờ nhiều luồng ─────────────────────────

def test_many_threads_cloud_dead_total_wait_bounded(fast):
    """24 luồng, Aurora 429 mãi (xen 5xx): tổng thời gian ảo ≤ ngân sách chung (~577 s),
    KHÔNG ∝ số luồng (trước review: luồng lần lượt làm probe → ~24 × 420 s)."""
    n = 24
    lk = threading.Lock()
    calls: list[float] = []

    def fn():
        with lk:
            calls.append(fast.now())
            k = len(calls)
        raise _err(503 if k % 5 == 0 else 429)

    t0 = fast.now()

    def tgt(k):
        CR.call_with_cloud_retry(fn, model="chatgpt/gpt-6", log=lambda s: None)

    errs = _run_threads(n, tgt)
    elapsed = fast.now() - t0
    budget = CR.outage_budget_sec(4, list(CR.DEFAULT_BACKOFF))
    assert all(isinstance(e, LLMUnavailable) and getattr(e, "_cloud_retry_exhausted", False) for e in errs), \
        [(type(e).__name__, getattr(e, "_cloud_retry_exhausted", None), str(e)[:60]) for e in errs]
    # trần thiết kế: không bắt đầu lần thử mới sau 2 × ngân sách (+ 1 lần ngủ lỗi tạm ≤ 264 s + nhiễu)
    assert elapsed <= 2 * budget + 300, f"chờ {elapsed:.0f}s > trần {2 * budget + 300:.0f}s"
    # không bão: mỗi luồng ≤ 1 + 4 lần gọi, phần lớn luồng chỉ gọi 1–2 lần
    assert len(calls) <= n * 5
    assert len(calls) <= 3 * n, f"bão retry: {len(calls)} lần gọi cho {n} luồng"


def test_retry_after_huge_gives_up_without_waiting(clock):
    """Retry-After 3600 s (trần 900) > ngân sách chờ → bỏ cloud NGAY, không ngủ 15 phút × 4."""
    n = []

    def fn():
        n.append(1)
        raise _err(429, retry_after="3600")

    with pytest.raises(LLMUnavailable) as ei:
        CR.call_with_cloud_retry(fn, model="chatgpt/gpt-6", log=lambda s: None)
    assert getattr(ei.value, "_cloud_retry_exhausted", False)
    assert len(n) == 1 and sum(clock.sleeps) == 0


def test_retry_after_reasonable_is_used(clock):
    n = []

    def fn():
        n.append(clock.now())
        if len(n) == 1:
            raise _err(429, retry_after="45")
        return "ok"

    assert CR.call_with_cloud_retry(fn, model="chatgpt/gpt-6", log=lambda s: None) == "ok"
    assert 45 <= n[1] - n[0] <= 45 + 5 + CR.STOP_SLICE_SEC


def test_stale_inflight_success_does_not_reopen_gate(clock):
    """Request bay TỪ TRƯỚC khi bị 429 trả OK → không mở cửa (luồng đang chờ không bắn lại ngay)."""
    g = CR.get_gate("chatgpt/x")
    t_before = clock.now() - 1.0
    g.trip(clock.now() + 30)
    g.success(started_at=t_before)
    assert g.tripped is True
    g.success(started_at=clock.now())
    assert g.tripped is False


def test_stale_success_threads_do_not_burn_retries(fast):
    """Luồng A gặp 429, luồng B (bay từ trước) trả OK ngay sau đó: A vẫn chờ backoff ≥ ~30 s."""
    a_calls: list[float] = []
    started = threading.Event()

    def fa():
        a_calls.append(fast.now())
        if len(a_calls) < 3:
            raise _err(429)
        return "ok"

    def fb():
        started.set()
        time.sleep(0.05)              # bay qua lúc A bị 429
        return "ok"

    tb = threading.Thread(target=lambda: CR.call_with_cloud_retry(fb, model="chatgpt/x", log=lambda s: None))
    tb.start()
    started.wait(5)
    assert CR.call_with_cloud_retry(fa, model="chatgpt/x", log=lambda s: None) == "ok"
    tb.join(10)
    assert a_calls[1] - a_calls[0] >= 25, f"thử lại sau {a_calls[1] - a_calls[0]:.1f}s (bị mở cửa bởi request cũ)"


def test_probe_base_exception_releases_probe(clock):
    g = CR.get_gate("chatgpt/x")
    g.trip(clock.now() - 1)          # mốc đã qua → lượt sau là probe

    def boom():
        raise SystemExit("worker chết")

    with pytest.raises(SystemExit):
        CR.call_with_cloud_retry(boom, model="chatgpt/x", log=lambda s: None)
    assert g.probe_since is None, "probe chết phải nhả quyền dò ngay"
    assert g.wait_turn() is True


def test_probe_non_retry_error_releases(clock):
    g = CR.get_gate("chatgpt/x")
    g.trip(clock.now() - 1)
    with pytest.raises(LLMUnavailable):
        CR.call_with_cloud_retry(lambda: (_ for _ in ()).throw(_err(400)), model="chatgpt/x",
                                 log=lambda s: None)
    assert g.probe_since is None


def test_stop_during_shared_wait_all_threads_exit(fast, tmp_path):
    stop = tmp_path / ".stop"

    def fn():
        raise _err(429)

    def tgt(k):
        CR.call_with_cloud_retry(fn, model="chatgpt/gpt-6", stop_check=CR.stop_checker(stop),
                                 log=lambda s: None)

    def later():
        time.sleep(0.2)               # ≈ 40 s ảo, đang chờ mốc 30→60
        stop.write_text("1")

    threading.Thread(target=later, daemon=True).start()
    r0 = time.monotonic()
    errs = _run_threads(8, tgt)
    assert all(isinstance(e, CR.CloudRetryStopped) for e in errs), errs
    assert "stopped by user" in str(errs[0])
    assert time.monotonic() - r0 < 2.0


def test_mixed_429_5xx_then_recover_all_ok(fast):
    """429 / 503 xen kẽ tới t+150 s ảo rồi cloud hồi: mọi luồng OK, không luồng nào hết lượt."""
    n = 12
    t_open = fast.now() + 150
    lk = threading.Lock()
    calls = {"n": 0}

    def fn():
        with lk:
            calls["n"] += 1
            k = calls["n"]
        if fast.now() < t_open:
            raise _err(503 if k % 3 == 0 else 429)
        return "ok"

    res: list = [None] * n

    def tgt(k):
        res[k] = CR.call_with_cloud_retry(fn, model="chatgpt/gpt-6", log=lambda s: None)

    errs = _run_threads(n, tgt)
    assert errs == [None] * n and res == ["ok"] * n
    assert calls["n"] <= 4 * n


def test_slow_transient_call_not_retried_after_elapsed_cap(clock):
    """llm.py tự thử tới 12 request × timeout 900 s: 1 lần gọi đã treo > trần → không thử lại."""
    n = []

    def fn():
        n.append(1)
        clock.t += 3 * 900.0          # lời gọi kéo dài 45 phút rồi timeout
        raise LLMUnavailable("Aurora/ChatGPT thất bại: HTTPConnectionPool read timed out")

    with pytest.raises(LLMUnavailable) as ei:
        CR.call_with_cloud_retry(fn, model="chatgpt/gpt-6", log=lambda s: None)
    assert len(n) == 1 and getattr(ei.value, "_cloud_retry_exhausted", False)


def test_outage_cools_down_next_job_gets_full_retries(clock):
    """Đợt limit cũ đã nguội (không lỗi mới trong ≥ ngân sách) → job sau lại được chờ/thử đủ."""
    with pytest.raises(LLMUnavailable):
        CR.call_with_cloud_retry(lambda: (_ for _ in ()).throw(_err(429)), model="chatgpt/x",
                                 log=lambda s: None)
    clock.t += 3600
    n = []

    def fn():
        n.append(clock.now())
        if len(n) <= 2:
            raise _err(429)
        return "ok"

    assert CR.call_with_cloud_retry(fn, model="chatgpt/x", log=lambda s: None) == "ok"
    assert len(n) == 3


def test_classify_real_llm_errors():
    """Lỗi do llm._chatgpt_chat dựng thật (đọc các chỗ raise trong llm.py)."""
    # 400/413/422 → «(no-retry)»
    assert CR.classify_cloud_retry(LLMUnavailable("Aurora/ChatGPT 413 (no-retry): too large")) is None
    # 401 không key → raise_for_status → HTTPError(response) → «thất bại: 401 …»
    resp = requests.Response()
    resp.status_code = 401
    inner = requests.HTTPError("401 Client Error: Unauthorized", response=resp)
    try:
        raise LLMUnavailable(f"Aurora/ChatGPT thất bại: {inner}") from inner
    except LLMUnavailable as e:
        assert CR.classify_cloud_retry(e) is None
    # Hết lượt mà last_err=None (model trả rỗng mãi) → coi là lỗi tạm
    assert CR.classify_cloud_retry(LLMUnavailable("Aurora/ChatGPT thất bại: None")) == "transient"
    # file-QA lệch account (không phải mạng) → không retry
    assert CR.classify_cloud_retry(LLMUnavailable(
        "Aurora nhận file_id nhưng GPT không đọc được (upload/chat lệch account). last=x")) is None
    # 429 dài có Retry-After
    assert CR.retry_after_seconds(_err(429, retry_after="3600")) == CR.RETRY_AFTER_MAX_SEC


# ───────────────────────── Việc A + B: run_review nhiều luồng ─────────────────────────

def test_run_review_parallel_long_outage_bounded_and_manual_untouched(monkeypatch, fast, tmp_path):
    """8 luồng REVIEW, Aurora 429 suốt (REVIEW_LOCAL_FALLBACK=0): tổng chờ ảo ≤ ~ngân sách,
    không switch preset, câu manual giữ nguyên, không rv câu lỗi → raise để park B2."""
    import tools.preset_switcher as preset_switcher
    _review_env(monkeypatch, workers=8, REVIEW_LOCAL_FALLBACK=0)
    spy = SwitchSpy()
    monkeypatch.setattr(preset_switcher, "switch_preset", spy)
    monkeypatch.setattr(T, "review_batch", lambda *a, **k: (_ for _ in ()).throw(_err(429)))
    rows = _rows(64)
    rows[10]["manual"] = 1
    rows[10]["vi"] = "SỬA TAY"
    wd = _job(tmp_path, rows)
    t0 = fast.now()
    with pytest.raises(RuntimeError, match="REVIEW lỗi"):
        T.run_review(wd, batch=4)
    elapsed = fast.now() - t0
    budget = CR.outage_budget_sec(4, list(CR.DEFAULT_BACKOFF))
    assert elapsed <= 2 * budget + 300, f"{elapsed:.0f}s"
    assert spy.calls == []
    out = _read(wd)
    assert out[10]["vi"] == "SỬA TAY"
    assert not any(r.get("rv") for r in out.values())


# ───────────────────────── Việc B: cloud hỏng hẳn → không lặp nóng ─────────────────────────

def _real_chain_env(monkeypatch, *, local_fallback: str):
    """run_translate + run_review THẬT (chat giả): Aurora 429 mãi cho mọi model cloud;
    model llama local trả {} (soát OK)."""
    import agents.agent_hang_fix as agent_hang_fix
    import engines.pronoun_consistency as PC
    spy, _ = _translate_env(monkeypatch, REVIEW_LOCAL_FALLBACK=local_fallback,
                            REVIEW_PRESET="qwen-test", AUTO_REVIEW=1)
    monkeypatch.setattr(T, "run_review_pass1_full_vi", lambda wd_, rows_, plan, model=None: plan)
    monkeypatch.setattr(T, "_review_parallel_workers", lambda wd_, m: 4)
    monkeypatch.setattr(T, "_filter_cosmetic_nmt_fixes", lambda fixes, rows, plan: fixes)
    monkeypatch.setattr(PC, "filter_review_fixes_for_lock", lambda raw, rows, plan: raw)
    monkeypatch.setattr(agent_hang_fix, "fix_hang_job", lambda *a, **k: {"skipped": True})
    lk = threading.Lock()
    calls = {"cloud": 0, "local": 0}

    def _is_cloud(model):
        return str(model or "").startswith("chatgpt/")

    def ts(chunk, plan_block, prev_ctx, target=None, model=None, plan=None):
        with lk:
            calls["cloud" if _is_cloud(model) else "local"] += 1
        if _is_cloud(model):
            raise _err(429)
        return {s["i"]: f"L{s['i']}" for s in chunk}

    def rb(chunk_exp, plan_block, prev_ctx, model=None, **k):
        with lk:
            calls["cloud" if _is_cloud(model) else "local"] += 1
        if _is_cloud(model):
            raise _err(429)
        return {}

    monkeypatch.setattr(T, "_translate_safe", ts)
    monkeypatch.setattr(T, "review_batch", rb)
    return spy, calls


@pytest.mark.parametrize("local_fallback", ["0", "1"])
def test_cloud_dead_server_chain_parks_no_hot_loop(monkeypatch, fast, tmp_path, local_fallback):
    """Cấu hình V2 hiện tại (NMT primary + REVIEW chatgpt), Aurora chết hẳn, qua _auto_gpu THẬT:
    - không bao giờ nạp gemma (TRANSLATE_PRESET);
    - tổng chờ ảo bị chặn (~1 ngân sách, không nhân theo số lượt run_review/luồng);
    - số lần gọi cloud hữu hạn nhỏ; job dừng (park/pending), KHÔNG TTS, không lặp nóng;
    - câu NMT sót còn trống mang fill_pending=1."""
    server = pytest.importorskip("server")
    spy, calls = _real_chain_env(monkeypatch, local_fallback=local_fallback)
    monkeypatch.setattr(server, "WORK_ROOT", tmp_path)
    segs = [dict(s) for s in _SEGS] + [
        {"i": 4 + k, "start": 4.0 + k, "end": 5.0 + k, "text": f"第{k}句", "spk": "A"} for k in range(20)
    ]
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
    monkeypatch.setattr(server, "_run_requested_review", lambda *a, **k: tts.append("review_req"))
    # 12-11: đo TỔNG THỜI GIAN NGỦ ảo (không đo đồng hồ ảo trôi): trên máy chậm (Windows, ổ Z:)
    # phần tính toán thật ×200 làm đồng hồ ảo trôi hàng nghìn giây và làm đợt limit "nguội" giả.
    slept = []
    _orig_sleep = CR._sleep

    def _rec_sleep(dt):
        slept.append(max(0.0, dt))
        _orig_sleep(dt)
    monkeypatch.setattr(CR, "_sleep", _rec_sleep)
    r0 = time.monotonic()
    server._auto_gpu("j1", "Tiếng Việt", "replace", 1.0, 0.0, False)
    elapsed = sum(slept)
    budget = CR.outage_budget_sec(4, list(CR.DEFAULT_BACKOFF))
    assert time.monotonic() - r0 < 60
    assert elapsed <= 2 * budget + 300, f"chờ ảo {elapsed:.0f}s"
    assert "gemma-test" not in spy.calls, f"không được nạp gemma: {spy.calls}"
    if local_fallback == "0":
        assert spy.calls == []
    assert calls["cloud"] <= 60, calls
    assert tts == [], "không được đi tiếp TTS/QA khi còn câu trống"
    rows = _read(wd)
    assert rows[1]["vi"] == "" and rows[1].get("fill_pending") == 1 and rows[1]["spk"] == "B"
    man = json.loads((wd / "manifest.json").read_text(encoding="utf-8"))
    tr = (man.get("stages") or {}).get("translate") or {}
    ag = man.get("agent") or {}
    assert tr.get("status") == "pending" or ag.get("held_at") == "waiting_review", (tr, ag)


# ───────────────────────── Việc B: câu manual + hậu kỳ ─────────────────────────

def test_review_step0_never_touches_manual_or_other_rows(monkeypatch, tmp_path):
    import engines.mt_zh_vi as mt_zh_vi
    _review_env(monkeypatch, workers=1, rmodel="chatgpt/gpt-6")
    monkeypatch.setattr(mt_zh_vi, "enabled", lambda: True)
    monkeypatch.setattr(mt_zh_vi, "primary_mode", lambda: True)
    rows = _rows(10)
    for r in rows:
        r["rv"] = 1
    rows[3]["vi"] = ""
    rows[4]["manual"] = 1
    rows[4]["vi"] = "Ta là tay"           # có «Ta» → pronoun postpass sẽ đụng nếu chạy nhầm
    rows[5]["vi"] = "Ta ở đây"             # câu máy khác — không được hậu kỳ lại ở bước 0
    wd = _job(tmp_path, rows)
    monkeypatch.setattr(T, "_translate_safe",
                        lambda payload, pb, ctx, target=None, model=None, plan=None:
                        {p["i"]: "Ta tới rồi" for p in payload})
    seen: list[list[int]] = []

    def spy_post(rs, plan=None):
        seen.append(sorted(r["i"] for r in rs))
        for r in rs:
            if not r.get("manual") and r["i"] == 3:   # hậu kỳ thật bỏ qua manual
                r["vi"] = r["vi"] + " ."
        return len(rs)

    monkeypatch.setattr(T, "apply_hard_term_locks", spy_post)
    monkeypatch.setattr(T, "apply_style_polish", lambda rs, plan=None: 0)
    monkeypatch.setattr(T, "apply_pronoun_postpass", lambda rs, plan=None: 0)
    monkeypatch.setattr(T, "review_batch", lambda *a, **k: {})
    T.run_review(wd, batch=40)
    out = _read(wd)
    assert seen and seen[0] == [3], "hậu kỳ bước 0 chỉ chạy trên câu vừa vá"
    assert out[4]["vi"] == "Ta là tay" and out[5]["vi"] == "Ta ở đây"
    assert out[4].get("manual") == 1
    assert out[3]["vi"].startswith("Ta tới rồi .") and "fill_pending" not in out[3]


def test_fill_pending_cleared_when_later_filled(monkeypatch, tmp_path):
    import engines.mt_zh_vi as mt_zh_vi
    _review_env(monkeypatch, workers=1, rmodel="chatgpt/gpt-6")
    monkeypatch.setattr(mt_zh_vi, "enabled", lambda: True)
    monkeypatch.setattr(mt_zh_vi, "primary_mode", lambda: True)
    rows = _rows(4)
    rows[2]["vi"] = ""
    rows[2]["fill_pending"] = 1
    wd = _job(tmp_path, rows)
    monkeypatch.setattr(T, "_translate_safe",
                        lambda payload, pb, ctx, target=None, model=None, plan=None:
                        {p["i"]: "OK" for p in payload})
    monkeypatch.setattr(T, "review_batch", lambda *a, **k: {})
    T.run_review(wd, batch=40)
    assert "fill_pending" not in _read(wd)[2]


# ───────────────────────── cấu hình cũ = bản gốc trước b2 ─────────────────────────

_BACKUP = ROOT / ".backup_edit_20261111_translate_b2"

_DIFF_SCRIPT = r'''
import json, sys, threading, tempfile, shutil
from pathlib import Path
first, root = sys.argv[1], sys.argv[2]
sys.path[:0] = [first, root]
import requests
import translate as T
assert Path(T.__file__).resolve().parent == Path(first).resolve(), T.__file__
from llm import LLMUnavailable
import mt_zh_vi, preset_switcher, series_glossary, agent_hang_fix
import pronoun_consistency as PC

CFG = {"REVIEW_RETRY_BACKOFF_SEC": "0", "AUTO_SWITCH_PRESETS": "1", "REVIEW_PRONOUN_MASK": "0",
       "REVIEW_PRESET": "qwen-test", "TRANSLATE_PRESET": "gemma-test", "TRANSLATE_MODEL": "local",
       "REVIEW_CLOUD_RETRY": "0", "TRANSLATE_FILL_MODEL": "local", "AUTO_REVIEW": "1"}
T._cfg_get = lambda k, d=None: CFG.get(k, d)
if hasattr(T, "_log_vram"):
    T._log_vram = lambda stage: None
T._is_llama_local_model = lambda m: str(m or "").startswith("llama/") or str(m or "") in ("local", "llama")
T.is_local = lambda m: False
T.unload_local = lambda m: None
T._resolve_review_model = lambda wd_, m=None: m or "chatgpt/gpt-6"
T.run_review_pass1_full_vi = lambda wd_, rows_, plan, model=None: plan
T._review_parallel_workers = lambda wd_, m: 1
T._filter_cosmetic_nmt_fixes = lambda fixes, rows, plan: fixes
series_glossary.apply = lambda wd_, plan: plan
series_glossary.save_from = lambda *a, **k: None
PC.ensure_analyze_before_translate = lambda wd_, plan, segments=None, force=False: (plan, {"skipped": True})
PC.run_post_translate_consistency = lambda wd_, rows_, plan, fix_with_gpt=True: {"ok": True}
PC.filter_review_fixes_for_lock = lambda raw, rows, plan: raw
agent_hang_fix.fix_hang_job = lambda *a, **k: {"skipped": True}
mt_zh_vi.enabled = lambda: True
mt_zh_vi.primary_mode = lambda: True
mt_zh_vi.resolve_model_id = lambda plan: "HachimiMT-60-zh-vi"
D = {0: "Xin chào", 1: "", 2: "他 đi rồi", 3: "Tạm biệt"}
mt_zh_vi.draft_rows = lambda items, plan=None: {it["i"]: D.get(it["i"], "") for it in items}
trace = []
preset_switcher.switch_preset = lambda pid, max_wait_sec=180: trace.append(("switch", pid)) or True

def err(st):
    r = requests.Response(); r.status_code = st
    inner = requests.HTTPError(f"{st} x", response=r)
    try:
        raise LLMUnavailable(f"Aurora/ChatGPT thất bại: {inner}") from inner
    except LLMUnavailable as e:
        return e

MODE = {"cloud": "ok"}
def ts(chunk, plan_block, prev_ctx, target=None, model=None, plan=None):
    trace.append(("ts", [s["i"] for s in chunk], model))
    return {s["i"]: f"T{s['i']}" for s in chunk}
def rb(chunk_exp, plan_block, prev_ctx, model=None, **k):
    trace.append(("rb", [r["i"] for r in chunk_exp], model))
    if str(model or "").startswith("chatgpt/") and MODE["cloud"] != "ok":
        raise err(int(MODE["cloud"]))
    return {chunk_exp[0]["i"]: "SỬA"} if chunk_exp else {}
T._translate_safe = ts
T.review_batch = rb

SEGS = [{"i": i, "start": float(i), "end": i + 1.0, "text": t, "spk": s} for i, (t, s) in
        enumerate([("你好", "A"), ("他来了", "B"), ("他走了", "A"), ("再见", "B")])]
out = {}
tmp = Path(tempfile.mkdtemp())
def job(name, rows=None):
    wd = tmp / name; wd.mkdir()
    (wd / "manifest.json").write_text(json.dumps({"stages": {}}), encoding="utf-8")
    (wd / "glossary.json").write_text(json.dumps({"characters": [], "terms": []}), encoding="utf-8")
    (wd / "asr.json").write_text(json.dumps(SEGS, ensure_ascii=False), encoding="utf-8")
    if rows is not None:
        (wd / "script.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    return wd
def read(wd):
    return json.loads((wd / "script.json").read_text(encoding="utf-8"))
def rows_n(n):
    return [{"i": i, "start": float(i), "end": i + 1.0, "zh": f"第{i}句", "vi": f"vi{i}"} for i in range(n)]

for name, cloud, fn in [
    ("translate_noreview", "ok", lambda wd: T.run_translate(wd, auto_review=False)),
    ("translate_with_review", "ok", lambda wd: T.run_translate(wd)),
    ("translate_review_429", "429", lambda wd: T.run_translate(wd)),
    ("translate_review_503", "503", lambda wd: T.run_translate(wd)),
]:
    trace.clear(); MODE["cloud"] = cloud
    wd = job(name)
    try:
        fn(wd); res = "ok"
    except Exception as e:
        res = type(e).__name__ + ":" + str(e)[:80]
    out[name] = {"trace": list(trace), "rows": read(wd), "res": res}

for name, cloud in [("review_step0", "ok"), ("review_c9_429", "429"), ("review_c9_503", "503"),
                    ("review_c9_413", "413")]:
    trace.clear(); MODE["cloud"] = cloud
    rows = rows_n(9)
    rows[2]["vi"] = ""; rows[5]["vi"] = ""; rows[6]["manual"] = 1; rows[6]["vi"] = "SỬA TAY"
    wd = job(name, rows)
    try:
        T.run_review(wd, batch=3); res = "ok"
    except Exception as e:
        res = type(e).__name__ + ":" + str(e)[:80]
    out[name] = {"trace": list(trace), "rows": read(wd), "res": res}
shutil.rmtree(tmp, ignore_errors=True)
print("@@JSON@@" + json.dumps(out, ensure_ascii=False, sort_keys=True))
'''


def _diff_run(first: Path, tmp_path: Path) -> dict:
    script = tmp_path / "diff_scn.py"
    script.write_text(_DIFF_SCRIPT, encoding="utf-8")
    env = dict(os.environ, AGENT_BRAIN="0", PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    p = subprocess.run([sys.executable, str(script), str(first), str(ROOT)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=300, env=env,
                       cwd=str(tmp_path))
    assert p.returncode == 0, p.stderr[-3000:]
    line = [ln for ln in p.stdout.splitlines() if ln.startswith("@@JSON@@")][-1]
    return json.loads(line[len("@@JSON@@"):])


@pytest.mark.skipif(not (_BACKUP / "translate.py").is_file(), reason="không có bản gốc trước b2")
def test_old_config_identical_to_pre_b2(tmp_path):
    """REVIEW_CLOUD_RETRY=0 + TRANSLATE_FILL_MODEL=local → hành vi (switch preset, model từng lời
    gọi, thứ tự lô, script.json cuối, kết quả/lỗi) Y HỆT bản trước b2."""
    old_dir = tmp_path / "old"
    old_dir.mkdir()
    (old_dir / "translate.py").write_bytes((_BACKUP / "translate.py").read_bytes())
    new_dir = tmp_path / "new"
    new_dir.mkdir()
    (new_dir / "translate.py").write_bytes((ROOT / "translate.py").read_bytes())
    old = _diff_run(old_dir, tmp_path)
    new = _diff_run(new_dir, tmp_path)
    assert set(old) == set(new)
    for k in sorted(old):
        assert new[k] == old[k], f"cấu hình cũ lệch bản gốc ở kịch bản {k}"
    # chắc kịch bản có nghĩa: có switch gemma ở dịch, có C9 ở review 429
    assert ["switch", "gemma-test"] in old["translate_noreview"]["trace"]
    assert any(t[0] == "switch" and t[1] == "qwen-test" for t in old["review_c9_429"]["trace"])
