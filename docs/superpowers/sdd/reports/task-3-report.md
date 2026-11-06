# Task 3 Report: API endpoints for sequential job queue

## What was implemented

### Model

Added `JobQueueReq(RunAllReq)` in `server.py` with:

- `job_ids: list[str]`
- `skip_done: bool = True`
- All existing `RunAllReq` pipeline/render options inherited.

### Routes

Four endpoints added immediately after `/api/queue/group` (before `/api/jobs/local-path`):

| Method | Path | Handler | Delegates to |
|--------|------|---------|--------------|
| POST | `/api/queue/jobs` | `api_queue_jobs_add` | `job_queue.queue_add` |
| GET | `/api/queue/jobs` | `api_queue_jobs_state` | `job_queue.queue_state` |
| POST | `/api/queue/jobs/stop` | `api_queue_jobs_stop` | `job_queue.queue_stop` |
| POST | `/api/queue/jobs/clear` | `api_queue_jobs_clear` | `job_queue.queue_clear` |

POST add validates non-empty `job_ids` (400 `"chọn ≥1 job"`), dumps opts via `model_dump(exclude={"job_ids", "skip_done"})`, and returns queue module response or 400 on exception.

Existing `/api/queue/group` and worker wiring at module bottom unchanged.

## Test evidence

Added `tests/test_queue_jobs_api.py` using FastAPI `TestClient`:

- Enqueue job → GET state shows queue + opts.
- Stop and clear return `ok: true` and empty queue.
- Empty `job_ids` → 400.

```text
python -m pytest tests/test_queue_jobs_api.py -v
2 passed
```

Full queue suite (unchanged worker semantics):

```text
python -m pytest tests/test_queue_jobs_api.py tests/test_job_queue.py tests/test_job_queue_worker.py -q
8 passed
```

Manual curl (server on `:8800`):

```bash
curl -s http://127.0.0.1:8800/api/queue/jobs
curl -s -X POST http://127.0.0.1:8800/api/queue/jobs -H "Content-Type: application/json" -d "{\"job_ids\":[\"JOB_ID\"],\"voice\":\"VOICE_ID\",\"audio_mode\":\"voice_bgm\",\"orig_vol\":0.22}"
curl -s -X POST http://127.0.0.1:8800/api/queue/jobs/stop
curl -s -X POST http://127.0.0.1:8800/api/queue/jobs/clear
```

## Files changed

- `server.py` — `JobQueueReq` + 4 routes.
- `tests/test_queue_jobs_api.py` — API smoke tests.
- `docs/superpowers/sdd/reports/task-3-report.md` — this report.

## Constraints

- No git commits (per instruction).
- Queue worker semantics untouched (`job_queue.py` unchanged).
