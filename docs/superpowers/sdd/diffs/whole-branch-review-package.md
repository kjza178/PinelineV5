# Whole-branch review package — Job Queue Approach A

**Note:** Workspace has no git; this package lists new/changed artifacts.

## New / primary files
- `job_queue.py` (6411 bytes, 238 lines)
- `tests/test_job_queue.py` (2008 bytes, 52 lines)
- `tests/test_job_queue_worker.py` (2130 bytes, 85 lines)
- `tests/test_queue_run_one.py` (3401 bytes, 101 lines)
- `tests/test_queue_jobs_api.py` (1587 bytes, 55 lines)
- `docs/superpowers/specs/2026-09-24-job-queue-design.md` (6069 bytes, 122 lines)
- `docs/fixes/2026-09-24-queue-voice-stop-race.md` (2122 bytes, 48 lines)
- server.py contains `class JobQueueReq`: True
- server.py contains `def _queue_run_one`: True
- server.py contains `def _resolve_queue_voice`: True
- server.py contains `/api/queue/jobs`: True
- server.py contains `job_queue.set_runner`: True
- index3.html contains `runJobQueue`: True
- index3.html contains `Chạy hàng chờ`: True
- index3.html contains `collectRunAllOpts`: True

## job_queue.py
```python
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
_clear_stop_hook: Callable[[str], None] | None = None


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
    global _opts
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


def set_clear_stop_hook(fn: Callable[[str], None] | None) -> None:
    global _clear_stop_hook
    _clear_stop_hook = fn


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
            if _clear_stop_hook is not None:
                try:
                    _clear_stop_hook(job_id)
                except Exception:
                    pass
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