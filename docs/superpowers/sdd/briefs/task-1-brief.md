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

### Task 1: Module queue + persist (chưa gọi pipeline)

**Files:**
- Create: `z:\Pineline\job_queue.py`
- Create: `z:\Pineline\tests\test_job_queue.py`
- Create: `z:\Pineline\tests\__init__.py` (empty) nếu chưa có

**Interfaces:**
- Produces:
  - `WORK_ROOT: Path` (monkeypatchable; default `Path("work")` — server ghi đè bằng `server.WORK_ROOT`)
  - `WIRED = ("download","asr","translate","tts","mux")`
  - `is_wired_done(work_dir: Path) -> bool`
  - `queue_state() -> dict`
  - `queue_add(job_ids, opts=None, skip_done=True) -> dict`
  - `queue_clear() -> dict`
  - `queue_stop() -> dict` (skeleton: clear + set stop; stop job khi có runner)
  - `set_runner(fn: Callable[[str, dict], str]) -> None`
  - `_ensure_worker()` / `_worker_loop()`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_job_queue.py
from __future__ import annotations
import json
from pathlib import Path
import job_queue as jq


def _manifest(wd: Path, stages: dict) -> None:
    wd.mkdir(parents=True, exist_ok=True)
    (wd / "manifest.json").write_text(
        json.dumps({"stages": stages}, ensure_ascii=False), encoding="utf-8"
    )


def test_add_skips_missing_done_dedupe(tmp_path, monkeypatch):
    monkeypatch.setattr(jq, "WORK_ROOT", tmp_path)
    jq._reset_for_tests()
    _manifest(tmp_path / "a", {s: {"status": "done"} for s in jq.WIRED})
    (tmp_path / "a" / "output.mp4").write_bytes(b"x" * 100)
    _manifest(tmp_path / "b", {"download": {"status": "done"}})
    r = jq.queue_add(["missing", "a", "b", "b"], opts={"voice": "v5"}, skip_done=True)
    assert r["queued"] == ["b"]
    assert "a" in r["skipped_done"]
    assert "missing" in r["skipped_missing"]
    assert jq.queue_state()["queue"] == ["b"]


def test_clear_empties_queue(tmp_path, monkeypatch):
    monkeypatch.setattr(jq, "WORK_ROOT", tmp_path)
    jq._reset_for_tests()
    _manifest(tmp_path / "b", {"download": {"status": "done"}})
    jq.queue_add(["b"], opts={})
    jq.queue_clear()
    st = jq.queue_state()
    assert st["queue"] == []
    assert st["current"] is None


def test_persist_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(jq, "WORK_ROOT", tmp_path)
    jq._reset_for_tests()
    _manifest(tmp_path / "b", {"download": {"status": "done"}})
    jq.queue_add(["b"], opts={"voice": "v5", "orig_vol": 0.22})
    raw = json.loads((tmp_path / "_job_queue.json").read_text(encoding="utf-8"))
    assert raw["queue"] == ["b"]
    assert raw["opts"]["voice"] == "v5"
    jq._reset_for_tests(load_disk=False)
    jq._load()
    assert jq.queue_state()["queue"] == ["b"]
    assert jq.queue_state()["opts"]["orig_vol"] == 0.22
```

- [ ] **Step 2: Run — expect FAIL (module missing)**

```bash
cd /d z:\Pineline
python -m pytest tests/test_job_queue.py -v
```

Expected: `ModuleNotFoundError: No module named 'job_queue'` (or collection error).

- [ ] **Step 3: Implement `job_queue.py`**

```python
# job_queue.py
from __future__ import annotations

import json
import threading
import time
from collections.abc import Callable
from pathlib import Path

WORK_ROOT = Path("work")
WIRED = ("download", "asr", "translate", "tts", "mux")
_PERSIST_NAME = "_job_queue.json"

_lock = threading.Lock()
_q: list[str] = []
_current: str | None = None
_opts: dict = {}
_hist: list[dict] = []
_stop = False
_thread: threading.Thread | None = None
_runner: Callable[[str, dict], str] | None = None


def _reset_for_tests(load_disk: bool = False) -> None:
    """Chỉ dùng trong pytest."""
    global _q, _current, _opts, _hist, _stop, _thread, _runner
    with _lock:
        _q.clear()
        _current = None
        _opts = {}
        _hist = []
        _stop = True
        _thread = None
        # giữ _runner nếu test worker đã set
    if load_disk:
        _load()


def set_runner(fn: Callable[[str, dict], str]) -> None:
    global _runner
    _runner = fn


def is_wired_done(work_dir: Path) -> bool:
    mf = work_dir / "manifest.json"
    out = work_dir / "output.mp4"
    if not mf.is_file() or not out.is_file() or out.stat().st_size <= 0:
        return False
    try:
        data = json.loads(mf.read_text(encoding="utf-8"))
    except Exception:
        return False
    stages = data.get("stages") or {}
    return all((stages.get(s) or {}).get("status") == "done" for s in WIRED)


def _persist_path() -> Path:
    return WORK_ROOT / _PERSIST_NAME


def _save() -> None:
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    payload = {"queue": list(_q), "opts": dict(_opts), "current": _current}
    _persist_path().write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _load() -> None:
    global _q, _opts, _current
    p = _persist_path()
    if not p.is_file():
        return
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return
    with _lock:
        _q = [str(x) for x in (data.get("queue") or []) if str(x).strip()]
        _opts = dict(data.get("opts") or {})
        # current lúc crash coi như chưa xong → đẩy lại đầu queue nếu có
        cur = data.get("current")
        if cur and cur not in _q:
            _q.insert(0, str(cur))
        _current = None


def _hist_push(job_id: str, status: str, detail: str = "") -> None:
    _hist.append(
        {"job_id": job_id, "status": status, "detail": detail, "ts": time.time()}
    )
    del _hist[:-20]


def queue_state() -> dict:
    with _lock:
        return {
            "queue": list(_q),
            "current": _current,
            "history": list(_hist[-20:]),
            "worker": bool(_thread and _thread.is_alive()),
            "opts": dict(_opts),
        }


def queue_add(
    job_ids: list[str],
    opts: dict | None = None,
    skip_done: bool = True,
) -> dict:
    cleaned: list[str] = []
    skipped_done: list[str] = []
    skipped_missing: list[str] = []
    seen: set[str] = set()
    for raw in job_ids or []:
        jid = str(raw or "").strip()
        if not jid or jid in seen:
            continue
        seen.add(jid)
        wd = WORK_ROOT / jid
        if not (wd / "manifest.json").is_file():
            skipped_missing.append(jid)
            continue
        if skip_done and is_wired_done(wd):
            skipped_done.append(jid)
            continue
        cleaned.append(jid)
    with _lock:
        if opts is not None:
            _opts = dict(opts)
        for jid in cleaned:
            if jid not in _q and jid != _current:
                _q.append(jid)
        _save()
        if cleaned:
            _ensure_worker_unlocked()
        return {
            "ok": True,
            "queued": cleaned,
            "skipped_done": skipped_done,
            "skipped_missing": skipped_missing,
            "queue": list(_q),
            "current": _current,
        }


def queue_clear() -> dict:
    with _lock:
        _q.clear()
        _save()
    return {"ok": True, **queue_state()}


def queue_stop() -> dict:
    """Clear queue + báo worker dừng; gọi _stop_job(current) nếu server đã wire."""
    global _stop, _current
    with _lock:
        _stop = True
        _q.clear()
        cur = _current
        _save()
    if cur and _runner is not None:
        # runner optional side-effect: server wraps stop via set_stop_hook
        stop_hook = getattr(queue_stop, "_hook", None)
        if callable(stop_hook):
            try:
                stop_hook(cur)
            except Exception:
                pass
    return {"ok": True, "stopped_job": cur}


def set_stop_hook(fn: Callable[[str], None] | None) -> None:
    queue_stop._hook = fn  # type: ignore[attr-defined]


def _ensure_worker_unlocked() -> None:
    global _thread, _stop
    if _thread and _thread.is_alive():
        return
    _stop = False
    _thread = threading.Thread(
        target=_worker_loop, daemon=True, name="pineline-job-queue"
    )
    _thread.start()


def _ensure_worker() -> None:
    with _lock:
        _ensure_worker_unlocked()


def _worker_loop() -> None:
    global _current, _stop
    while True:
        with _lock:
            if _stop:
                _current = None
                _save()
                return
            if not _q:
                _current = None
                _save()
                return
            job_id = _q.pop(0)
            _current = job_id
            opts = dict(_opts)
            _save()
        status = "failed"
        detail = ""
        try:
            if _runner is None:
                status, detail = "failed", "no runner"
            else:
                status = _runner(job_id, opts) or "failed"
        except Exception as e:  # noqa: BLE001
            status, detail = "failed", str(e)[:200]
        with _lock:
            _hist_push(job_id, status, detail)
            _current = None
            _save()
            if _stop:
                return


# Load persist khi import (server có thể set WORK_ROOT trước — xem Task 2)
_load()
```

- [ ] **Step 4: Re-run tests — expect PASS**

```bash
python -m pytest tests/test_job_queue.py -v
```

Expected: 3 passed. (Worker có thể start với `_runner is None` → job `b` fail nhanh; nếu test bị flake vì worker đua, trong `queue_add` test-only: hoặc monkeypatch `_ensure_worker_unlocked` no-op trong các test state-only.)

**Flake guard:** trong 3 test Task 1, thêm:

```python
monkeypatch.setattr(jq, "_ensure_worker_unlocked", lambda: None)
```

ngay sau `_reset_for_tests()`.

- [ ] **Step 5: Commit**

```bash
git add job_queue.py tests/test_job_queue.py tests/__init__.py
git commit -m "feat: job queue state module for sequential run-all"
```

---

