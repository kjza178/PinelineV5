# Job Queue (Approach A) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tick nhiều job chưa xong → chạy run-all đủ pipeline **tuần tự** đến hết hàng, có Dừng và persist nhẹ.

**Architecture:** Module `job_queue.py` (state + worker daemon, pattern `hongguo_bridge.merge_queue_*`). Runner blocking inject từ `server.py`: download sync + `_gpu.submit(_auto_gpu)` + `Event.wait()` (không chồng GPU). API `/api/queue/jobs*`. UI `/ui3` reuse checkbox `listSel`.

**Tech Stack:** Python 3.11+, FastAPI/`server.py`, threading, `Manifest`, `_auto_gpu`, pytest.

## Global Constraints

- Một job GPU tại một thời điểm (queue worker chờ `_gpu`; không gọi `_auto_gpu` song song).
- Mỗi job: resume bước thiếu; xong = 5 stage `WIRED_STAGES` done **và** `output.mp4` size > 0.
- Job thiếu giọng → history failed, không kẹt queue.
- Persist: `work/_job_queue.json` (queue + opts + current); history chỉ RAM.
- Không phá `POST /api/jobs/{id}/run-all` / claim `__all__` hiện tại.
- Primary UI: `index3.html` (`/ui3`).

## File map

| File | Responsibility |
|------|----------------|
| `job_queue.py` | State, persist, worker loop, `set_runner` |
| `server.py` | `_queue_run_one`, `JobQueueReq`, 4 routes, wire `set_runner` |
| `tests/test_job_queue.py` | Unit queue add/skip/clear/order |
| `tests/test_job_queue_worker.py` | Worker order + stop với fake runner |
| `index3.html` | qbar buttons + JS enqueue/stop/poll |
| `index.html` | Mirror tối thiểu (cùng API) |
| Spec (đã có) | `docs/superpowers/specs/2026-09-24-job-queue-design.md` |

---


---

### Task 2: Blocking runner + wire stop

**Files:**
- Modify: `z:\Pineline\server.py` (sau `run_all` / gần `_auto_pipeline`)
- Modify: `z:\Pineline\job_queue.py` (nếu cần chỉnh hook)
- Create: `z:\Pineline\tests\test_job_queue_worker.py`

**Interfaces:**
- Consumes: `_heal_stale_running`, `_claim_stage`, `_release_stage`, `_clear_stop`, `_STOP_JOBS`, `_stop_job`, `_find_video`, `download_video`, `_auto_gpu`, `_resolve_voice`, `_save_tts_*`, `_resolve_asr_engine`, `_gpu`, `Manifest`, `WORK_ROOT`, `list_clone_voices`
- Produces: `server._queue_run_one(job_id, opts) -> "done"|"failed"|"stopped"`
- `job_queue.set_runner(_queue_run_one)` + `set_stop_hook(_stop_job)` lúc startup
- `job_queue.WORK_ROOT = WORK_ROOT` trước `_load()` lại

- [ ] **Step 1: Failing test — order + stop**

```python
# tests/test_job_queue_worker.py
import json
import time
from pathlib import Path
import job_queue as jq


def _mf(wd: Path) -> None:
    wd.mkdir(parents=True, exist_ok=True)
    (wd / "manifest.json").write_text(
        json.dumps({"stages": {"download": {"status": "done"}}}), encoding="utf-8"
    )


def test_worker_runs_in_order(tmp_path, monkeypatch):
    monkeypatch.setattr(jq, "WORK_ROOT", tmp_path)
    jq._reset_for_tests()
    calls = []

    def fake(job_id, opts):
        calls.append(job_id)
        time.sleep(0.05)
        return "done"

    jq.set_runner(fake)
    _mf(tmp_path / "j1")
    _mf(tmp_path / "j2")
    jq.queue_add(["j1", "j2"], opts={"voice": "v5"})
    for _ in range(100):
        if not jq.queue_state()["worker"] and not jq.queue_state()["queue"]:
            break
        time.sleep(0.05)
    assert calls == ["j1", "j2"]


def test_stop_clears_remaining(tmp_path, monkeypatch):
    monkeypatch.setattr(jq, "WORK_ROOT", tmp_path)
    jq._reset_for_tests()
    stopped = []

    def fake(job_id, opts):
        time.sleep(0.3)
        return "done"

    def hook(jid):
        stopped.append(jid)

    jq.set_runner(fake)
    jq.set_stop_hook(hook)
    _mf(tmp_path / "j1")
    _mf(tmp_path / "j2")
    jq.queue_add(["j1", "j2"], opts={})
    time.sleep(0.05)
    r = jq.queue_stop()
    time.sleep(0.4)
    st = jq.queue_state()
    assert st["queue"] == []
    assert r["stopped_job"] == "j1"
    assert stopped == ["j1"]
```

- [ ] **Step 2: Implement `_queue_run_one` in `server.py`**

Đặt ngay sau `run_all` (~dòng 2621):

```python
def _queue_run_one(job_id: str, opts: dict) -> str:
    """Runner cho job_queue: blocking đến mux xong / fail / stop. Return status str."""
    import threading as _threading

    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return "failed"
    _heal_stale_running(work_dir)
    if job_queue.is_wired_done(work_dir):
        return "done"

    voice = opts.get("voice")
    speed = opts.get("speed")
    tts_engine = opts.get("tts_engine")
    asr_engine = opts.get("asr_engine")
    if voice:
        _save_tts_voice(work_dir, voice)
    if speed and float(speed) > 0:
        _save_tts_speed(work_dir, float(speed))
    if tts_engine:
        _save_tts_engine(work_dir, tts_engine)
    if asr_engine:
        _resolve_asr_engine(work_dir, asr_engine)

    resolved = _resolve_voice(work_dir, voice)
    if not resolved or resolved not in list_clone_voices():
        return "failed"

    if _job_any_busy(job_id) or _manifest_running(work_dir):
        # heal lại; nếu vẫn busy → fail (tránh treo)
        _heal_stale_running(work_dir)
        if _job_any_busy(job_id) or _manifest_running(work_dir):
            return "failed"

    if not _claim_stage(job_id, "__all__"):
        return "failed"
    _clear_stop(job_id)

    audio_mode = str(opts.get("audio_mode") or "voice_bgm")
    voice_vol = float(opts.get("voice_vol") if opts.get("voice_vol") is not None else 0.2)
    orig_vol = float(opts.get("orig_vol") if opts.get("orig_vol") is not None else 0.6)
    use_ocr = bool(opts.get("ocr"))
    fit = bool(opts.get("fit", True))
    resolution = str(opts.get("resolution") or "source")
    translate_mode = opts.get("translate_mode")
    brand_mode = str(opts.get("brand_mode") or "off").strip() or "off"
    brand_on = bool(opts.get("brand")) or brand_mode not in ("off", "", "0", "false")
    render_kw = {
        "flip": str(opts.get("flip") or "").strip(),
        "zoom": float(opts.get("zoom") or 1.12),
        "motion": bool(opts.get("motion", True)),
        "lut": bool(opts.get("lut", True)),
        "grain": str(opts.get("grain") or "weak"),
        "brand": brand_on,
        "brand_mode": brand_mode,
        "brand_text": str(opts.get("brand_text") or ""),
        "brand_logo": str(opts.get("brand_logo") or "off"),
        "frame": str(opts.get("frame") or "off"),
        "vbitrate": str(opts.get("vbitrate") or "8M"),
    }

    try:
        early = _next_incomplete_stage(work_dir) or "mux"
        Manifest(work_dir).mark_running(early)
    except Exception:
        pass

    # --- download sync (copy nhánh từ _auto_pipeline) ---
    try:
        if job_id in _STOP_JOBS:
            return "stopped"
        m = Manifest(work_dir)
        req = m.data.get("request", {})
        target = req.get("target", "Tiếng Việt")
        if not _find_video(work_dir):
            url = req.get("url")
            if not url:
                return "failed"
            try:
                download_video(url, work_dir, cookies_from_browser=req.get("cookies_from_browser"))
            except Exception:
                return "failed"
        if job_id in _STOP_JOBS or not _find_video(work_dir):
            return "stopped" if job_id in _STOP_JOBS else "failed"

        done_ev = _threading.Event()
        box: dict = {"err": None}

        def _gpu_job():
            try:
                _auto_gpu(
                    job_id, target, audio_mode, voice_vol, orig_vol, use_ocr,
                    fit, resolution, translate_mode, render_kw,
                )
            except Exception as e:  # noqa: BLE001
                box["err"] = e
            finally:
                _release_stage(job_id, "__all__")
                done_ev.set()

        _gpu.submit(_gpu_job)
        done_ev.wait()
        if job_id in _STOP_JOBS:
            return "stopped"
        if box["err"] is not None:
            return "failed"
        return "done" if job_queue.is_wired_done(work_dir) else "failed"
    except Exception:
        _release_stage(job_id, "__all__")
        return "failed"
```

- [ ] **Step 3: Wire tại startup `server.py`**

Gần cuối file (sau khi `WORK_ROOT` / app đã định nghĩa), hoặc ngay sau import block dùng được `WORK_ROOT`:

```python
import job_queue

job_queue.WORK_ROOT = WORK_ROOT
job_queue._load()  # reload với đúng WORK_ROOT
job_queue.set_runner(_queue_run_one)
job_queue.set_stop_hook(_stop_job)
# Nếu queue còn việc sau restart:
if job_queue.queue_state()["queue"]:
    job_queue._ensure_worker()
```

**Import cycle:** `job_queue` không import `server` ở top-level. `server` import `job_queue` **sau** khi `_queue_run_one` / `_stop_job` đã định nghĩa (đặt block wire ở cuối `server.py` trước `if __name__`).

- [ ] **Step 4: Run worker tests**

```bash
python -m pytest tests/test_job_queue_worker.py tests/test_job_queue.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add server.py job_queue.py tests/test_job_queue_worker.py
git commit -m "feat: blocking queue runner wires sequential run-all"
```

---

