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

