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

### Task 3: API endpoints

**Files:**
- Modify: `z:\Pineline\server.py` (sau `/api/queue/group` ~1514, **hoặc** cạnh các route queue khác)

**Interfaces:**
- `JobQueueReq(BaseModel)` — `job_ids: list[str]`, `skip_done: bool = True`, + mọi field của `RunAllReq`
- `POST /api/queue/jobs`, `GET /api/queue/jobs`, `POST /api/queue/jobs/stop`, `POST /api/queue/jobs/clear`

- [ ] **Step 1: Model** (cạnh `RunAllReq`)

```python
class JobQueueReq(RunAllReq):
    job_ids: list[str]
    skip_done: bool = True
```

(Pydantic v2: field `job_ids` thêm vào subclass OK; nếu xung đột, dùng model phẳng copy field.)

- [ ] **Step 2: Routes**

```python
@app.post("/api/queue/jobs")
def api_queue_jobs_add(req: JobQueueReq):
    ids = [str(x).strip() for x in (req.job_ids or []) if str(x).strip()]
    if not ids:
        return JSONResponse({"error": "chọn ≥1 job"}, status_code=400)
    # opts dict từ req (exclude job_ids/skip_done)
    opts = req.model_dump(exclude={"job_ids", "skip_done"})
    # voice: cho phép thiếu trên body nếu từng job đã lưu — runner sẽ fail từng job
    try:
        return job_queue.queue_add(ids, opts=opts, skip_done=bool(req.skip_done))
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.get("/api/queue/jobs")
def api_queue_jobs_state():
    return job_queue.queue_state()


@app.post("/api/queue/jobs/stop")
def api_queue_jobs_stop():
    return job_queue.queue_stop()


@app.post("/api/queue/jobs/clear")
def api_queue_jobs_clear():
    return job_queue.queue_clear()
```

- [ ] **Step 3: Manual curl** (server đang chạy `:8800`)

```bash
curl -s http://127.0.0.1:8800/api/queue/jobs
curl -s -X POST http://127.0.0.1:8800/api/queue/jobs -H "Content-Type: application/json" -d "{\"job_ids\":[\"JOB_INCOMPLETE\"],\"voice\":\"VOICE_ID\",\"audio_mode\":\"voice_bgm\",\"orig_vol\":0.22}"
curl -s -X POST http://127.0.0.1:8800/api/queue/jobs/stop
```

Expected: state JSON; add trả `queued`/`skipped_*`; stop `ok: true`.

- [ ] **Step 4: Commit**

```bash
git add server.py
git commit -m "feat: API endpoints for sequential job run-all queue"
```

---

### Task 4: UI `/ui3` — reuse listSel + thanh queue

**Files:**
- Modify: `z:\Pineline\index3.html` (`#qbar` trong `renderList`, + JS)
- Modify: `z:\Pineline\index.html` (mirror cùng button/JS nếu sidebar tương tự)

**UI spec:**
1. Không thêm checkbox mới — dùng `listSel` / `.jchk`.
2. Trong `#qbar` thêm:

```html
<button type="button" class="btn pri" id="btn-queue-run" onclick="runJobQueue()" title="Chạy run-all tuần tự các job đã tick">▶ Chạy hàng chờ</button>
<button type="button" class="btn stop" id="btn-queue-stop" onclick="stopJobQueue()">⏹ Dừng hàng chờ</button>
<span class="qhint" id="queue-status"></span>
```

3. Poll status khi worker bật.

- [ ] **Step 1: Patch `renderList` qbar** trong `index3.html` — thêm 2 nút + `#queue-status` cạnh hint chọn.

- [ ] **Step 2: JS helpers** (cạnh `runAll`)

```javascript
function collectRunAllOpts(){
  const audio_mode=(document.getElementById('auto-audio')||{value:'voice_bgm'}).value;
  const voice=(document.getElementById('auto-voice')||{}).value||null;
  const speed=parseFloat((document.getElementById('auto-speed')||{value:'1.0'}).value);
  const tts_engine=(document.getElementById('auto-engine')||{value:'vieneu'}).value;
  const asr_engine=(document.getElementById('auto-asr')||{value:'hybrid_fa'}).value;
  const ocr=!!(document.getElementById('auto-ocr')||{}).checked;
  const fit=(document.getElementById('auto-fit')||{checked:true}).checked;
  const resolution=(document.getElementById('auto-res')||{value:'source'}).value||'source';
  const translate_mode=(document.getElementById('auto-tr-mode')||{value:'batch'}).value||'batch';
  const zoom=parseFloat((document.getElementById('auto-zoom')||{value:'1.12'}).value)||1.12;
  const motion=!!(document.getElementById('auto-motion')||{checked:true}).checked;
  const lut=!!(document.getElementById('auto-lut')||{checked:true}).checked;
  const grain=(document.getElementById('auto-grain')||{value:'weak'}).value||'weak';
  const vbitrate=(document.getElementById('auto-vbit')||{value:'8M'}).value||'8M';
  const flip=(document.getElementById('auto-flip')||{value:''}).value||'';
  const frame=(document.getElementById('auto-frame')||{value:'off'}).value||'off';
  const brand_mode=(document.getElementById('auto-brand-mode')||{value:'off'}).value||'off';
  const brand_text=(document.getElementById('auto-brand-text')||{value:''}).value||'';
  const brand_logo=(document.getElementById('auto-brand-logo')||{value:'off'}).value||'off';
  const orig_vol=parseFloat((document.getElementById('auto-ovol')||{value:(audio_mode==='duck_bgm')?'0.22':'0.6'}).value);
  return {voice,speed,tts_engine,asr_engine,audio_mode,voice_vol:0.2,orig_vol,ocr,fit,resolution,translate_mode,
    zoom,motion,lut,grain,flip,frame,brand:brand_mode!=='off',brand_mode,brand_text,brand_logo,vbitrate};
}

let _queuePollTimer=null;
async function paintQueueStatus(){
  try{
    const st=await (await fetch('/api/queue/jobs')).json();
    const el=document.getElementById('queue-status');
    if(!el) return;
    if(st.current|| (st.queue&&st.queue.length)||st.worker){
      el.textContent=`Queue: ${st.current||'—'} · còn ${(st.queue||[]).length}`+(st.worker?' · chạy':'');
    } else {
      el.textContent='';
    }
    if(st.worker || (st.queue&&st.queue.length) || st.current){
      if(!_queuePollTimer) _queuePollTimer=setInterval(()=>{ void paintQueueStatus(); void refresh(); }, 2000);
    } else if(_queuePollTimer){
      clearInterval(_queuePollTimer); _queuePollTimer=null;
    }
  }catch(e){}
}

async function runJobQueue(){
  const ids=[...listSel];
  if(!ids.length){ alert('Tick ít nhất 1 job ở sidebar'); return; }
  if(!confirm(`Chạy hàng chờ ${ids.length} job (tuần tự run-all)?`)) return;
  const body={job_ids:ids, skip_done:true, ...collectRunAllOpts()};
  if(!body.voice){ alert('Chọn giọng trên thanh 1-click trước'); return; }
  const r=await fetch('/api/queue/jobs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const d=await r.json().catch(()=>({}));
  if(!r.ok){ alert(d.error||r.status); return; }
  alert(`Đã xếp ${ (d.queued||[]).length } job`+(d.skipped_done&&d.skipped_done.length?` · bỏ qua done: ${d.skipped_done.length}`:''));
  void paintQueueStatus(); void refresh();
}

async function stopJobQueue(){
  await fetch('/api/queue/jobs/stop',{method:'POST'});
  void paintQueueStatus(); void refresh();
}
```

Gọi `paintQueueStatus()` một lần trong `refresh()` cuối.

Refactor nhẹ (optional cùng task): `runAll` dùng `collectRunAllOpts()` để DRY — không bắt buộc.

- [ ] **Step 3: Manual UI**
  1. Mở `http://127.0.0.1:8800/ui3`
  2. Tick 2 job incomplete, chọn giọng + Âm nền
  3. **Chạy hàng chờ** → job1 `running`, job2 chưa claim `__all__` đến khi job1 mux done
  4. **Dừng hàng chờ** giữa chừng → queue trống, ffmpeg chết

- [ ] **Step 4: Mirror `index.html`** nếu còn `.qbar` / `listSel` tương tự; nếu không có listSel, thêm checkbox tối thiểu + cùng JS.

- [ ] **Step 5: Commit**

```bash
git add index3.html index.html
git commit -m "feat: UI multi-select sequential job queue on ui3"
```

---

### Task 5: Docs sync (spec đã viết)

**Files:**
- Verify: `z:\Pineline\docs\superpowers\specs\2026-09-24-job-queue-design.md`
- Verify: plan này

- [ ] **Step 1:** Đọc lại spec — API / persist / non-goals khớp code.
- [ ] **Step 2:** Commit docs nếu còn dirty

```bash
git add docs/superpowers/specs/2026-09-24-job-queue-design.md docs/superpowers/plans/2026-09-24-job-queue-sequential.md
git commit -m "docs: job queue sequential design and implementation plan"
```

*(Fix-log `docs/fixes/` chỉ tạo khi implement gặp/sửa bug runtime — không bắt buộc ở phase plan.)*

---

## Recheck (end-to-end)

1. 2 job chỉ `download=done`, cùng voice clone hợp lệ.
2. Tick cả hai → Chạy hàng chờ (`voice_bgm` hoặc `duck_bgm` + Tiếng gốc nền).
3. Job1 chạy ASR…mux; job2 **không** `running`/`__all__` đến khi job1 `mux=done` + có `output.mp4`.
4. Dừng giữa TTS job1 → queue trống; job2 không start; process ffmpeg/ASR theo cwd job1 chết.
5. Enqueue job 5/5 done + `output.mp4` → `skipped_done`.
6. Restart server khi `work/_job_queue.json` còn id → worker tự resume.

**Pass:** tuần tự đúng, stop dứt, skip done, persist resume.  
**Fail:** 2 ffmpeg/ASR cùng lúc; queue bỏ sót job chưa xong; 1-click single-job 409/regress.

---

## Spec coverage checklist

| Spec item | Task |
|-----------|------|
| Enqueue tick + opts 1-click | T3 + T4 |
| Skip mux done | T1 `is_wired_done` |
| Worker sequential blocking | T2 |
| Stop = clear + `_stop_job` | T1/T2 `queue_stop` + hook |
| Persist `_job_queue.json` | T1 |
| API 4 endpoints | T3 |
| UI `/ui3` listSel | T4 |
| Non-goal: no cron / no parallel | Global Constraints |
| Không phá `run_all` | T2 path riêng `_queue_run_one` |
