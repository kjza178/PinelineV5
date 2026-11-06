# Task 2 Review Package

**Base:** after Task 1
**Head:** after Task 2

### tests\test_job_queue_worker.py (85 lines)

```python
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


def test_worker_clears_stale_stop_before_runner(tmp_path, monkeypatch):
    monkeypatch.setattr(jq, "WORK_ROOT", tmp_path)
    jq._reset_for_tests()
    events = []

    def clear_hook(job_id):
        events.append(("clear", job_id))

    def fake(job_id, opts):
        events.append(("run", job_id))
        return "done"

    jq.set_clear_stop_hook(clear_hook)
    jq.set_runner(fake)
    _mf(tmp_path / "j1")
    try:
        jq.queue_add(["j1"], opts={})
        for _ in range(100):
            if not jq.queue_state()["worker"]:
                break
            time.sleep(0.01)
        assert events == [("clear", "j1"), ("run", "j1")]
    finally:
        jq.set_clear_stop_hook(None)

```

### job_queue.py (full)

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

### server.py — _queue_run_one

```python
def _queue_run_one(job_id: str, opts: dict) -> str:
    """Run one queued job synchronously through mux and return its final status."""
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

    resolved = _resolve_queue_voice(work_dir, voice)
    if not resolved or resolved not in list_clone_voices():
        return "failed"

    if _job_any_busy(job_id) or _manifest_running(work_dir):
        _heal_stale_running(work_dir)
        if _job_any_busy(job_id) or _manifest_running(work_dir):
            return "failed"

    if not _claim_stage(job_id, "__all__"):
        return "failed"

    audio_mode = str(opts.get("audio_mode") or "voice_bgm")
    voice_vol = float(
        opts.get("voice_vol") if opts.get("voice_vol") is not None else 0.2
    )
    orig_vol = float(
        opts.get("orig_vol") if opts.get("orig_vol") is not None else 0.6
    )
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
    except Exception:  # noqa: BLE001
        pass

    submitted = False
    try:
        if job_id in _STOP_JOBS:
            return "stopped"
        manifest = Manifest(work_dir)
        request = manifest.data.get("request", {})
        target = request.get("target", "Tiếng Việt")
        if not _find_video(work_dir):
            url = request.get("url")
            if not url:
                return "failed"
            try:
                download_video(
                    url,
                    work_dir,
                    cookies_from_browser=request.get("cookies_from_browser"),
                )
            except Exception:  # noqa: BLE001
                return "stopped" if job_id in _STOP_JOBS else "failed"
        if job_id in _STOP_JOBS or not _find_video(work_dir):
            return "stopped" if job_id in _STOP_JOBS else "failed"

        done_event = threading.Event()
        error: list[Exception] = []

        def _gpu_job() -> None:
            try:
                _auto_gpu(
                    job_id,
                    target,
                    audio_mode,
                    voice_vol,
                    orig_vol,
                    use_ocr,
                    fit,
                    resolution,
                    translate_mode,
                    render_kw,
                )
            except Exception as exc:  # noqa: BLE001
                error.append(exc)
            finally:
                _release_stage(job_id, "__all__")
                done_event.set()

        _gpu.submit(_gpu_job)
        submitted = True
        done_event.wait()
        if job_id in _STOP_JOBS:
            return "stopped"
        if error:
            return "failed"
        return "done" if job_queue.is_wired_done(work_dir) else "failed"
    except Exception:  # noqa: BLE001
        return "failed"
    finally:
        if not submitted:
            _release_stage(job_id, "__all__")


```

### server.py — wire block

```python
 hg
    return hg.merge_queue_clear()


@app.post("/api/hg/library/open")
def hg_library_open(body: dict | None = None):
    import hongguo_bridge as hg
    body = body or {}
    try:
        return hg.open_library(body.get("name"), _hg_base(body.get("base")))
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


import job_queue

job_queue.WORK_ROOT = WORK_ROOT
job_queue._load()
job_queue.set_runner(_queue_run_one)
job_queue.set_stop_hook(_stop_job)
job_queue.set_clear_stop_hook(_clear_stop)
if job_queue.queue_state()["queue"]:
    job_queue._ensure_worker()


if __name__ == "__main__":
    import argparse
    import os

    import uvicorn

    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"))
    ap.add_argument("--port", type=int, default=int(os.getenv("PORT", "8800")))
    args = ap.parse_args()

    print(f"Mở http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)

```


## Updated after fixes

`python
def _queue_run_one(job_id: str, opts: dict) -> str:
    """Run one queued job synchronously through mux and return its final status."""
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

    resolved = _resolve_queue_voice(work_dir, voice)
    if not resolved or resolved not in list_clone_voices():
        return "failed"

    if _job_any_busy(job_id) or _manifest_running(work_dir):
        _heal_stale_running(work_dir)
        if _job_any_busy(job_id) or _manifest_running(work_dir):
            return "failed"

    if not _claim_stage(job_id, "__all__"):
        return "failed"

    audio_mode = str(opts.get("audio_mode") or "voice_bgm")
    voice_vol = float(
        opts.get("voice_vol") if opts.get("voice_vol") is not None else 0.2
    )
    orig_vol = float(
        opts.get("orig_vol") if opts.get("orig_vol") is not None else 0.6
    )
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
    except Exception:  # noqa: BLE001
        pass

    submitted = False
    try:
        if job_id in _STOP_JOBS:
            return "stopped"
        manifest = Manifest(work_dir)
        request = manifest.data.get("request", {})
        target = request.get("target", "Tiếng Việt")
        if not _find_video(work_dir):
            url = request.get("url")
            if not url:
                return "failed"
            try:
                download_video(
                    url,
                    work_dir,
                    cookies_from_browser=request.get("cookies_from_browser"),
                )
            except Exception:  # noqa: BLE001
                return "stopped" if job_id in _STOP_JOBS else "failed"
        if job_id in _STOP_JOBS or not _find_video(work_dir):
            return "stopped" if job_id in _STOP_JOBS else "failed"

        done_event = threading.Event()
        error: list[Exception] = []

        def _gpu_job() -> None:
            try:
                _auto_gpu(
                    job_id,
                    target,
                    audio_mode,
                    voice_vol,
                    orig_vol,
                    use_ocr,
                    fit,
                    resolution,
                    translate_mode,
                    render_kw,
                )
            except Exception as exc:  # noqa: BLE001
                error.append(exc)
            finally:
                _release_stage(job_id, "__all__")
                done_event.set()

        _gpu.submit(_gpu_job)
        submitted = True
        done_event.wait()
        if job_id in _STOP_JOBS:
            return "stopped"
        if error:
            return "failed"
        return "done" if job_queue.is_wired_done(work_dir) else "failed"
    except Exception:  # noqa: BLE001
        return "failed"
    finally:
        if not submitted:
            _release_stage(job_id, "__all__")


`

### job_queue.py after fixes

`python
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

`
