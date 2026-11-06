# Task 5 Report — Docs sync (job queue)

- **Status:** complete
- **Date:** 2026-09-24

## Files verified (exist)

| File | Role |
|------|------|
| `job_queue.py` | State, persist, worker, hooks |
| `server.py` | `JobQueueReq`, 4 routes, `_queue_run_one`, wire hooks |
| `index3.html` | Primary UI — `#qbar`, `listSel`, poll |
| `index.html` | Mirror |
| `tests/test_job_queue.py` | add/skip/clear/order |
| `tests/test_job_queue_worker.py` | worker order + stop |
| `tests/test_queue_run_one.py` | blocking runner + voice/stop |
| `tests/test_queue_jobs_api.py` | TestClient API smoke |

## API surface

| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/queue/jobs` | `JobQueueReq`: `job_ids` + `RunAllReq` opts + `skip_done` |
| GET | `/api/queue/jobs` | `{queue, current, history[-20], worker, opts}` |
| POST | `/api/queue/jobs/stop` | clear + `_stop_job(current)` → `{ok, stopped_job}` |
| POST | `/api/queue/jobs/clear` | clear list only → `{ok, …queue_state}` |

Persist: `work/_job_queue.json` (`queue`, `opts`, `current`).

## Spec match

- Sequential blocking runner via `_gpu.submit` + `Event.wait()` in `_queue_run_one`.
- UI reuses `listSel` / `.jchk`; no second checkbox column.
- Single-job `POST /api/jobs/{id}/run-all` unchanged.
- Deviations documented in spec § Implementation notes.

## Recheck E2E

**Automated:**

```bash
python -m pytest tests/test_job_queue.py tests/test_job_queue_worker.py tests/test_queue_run_one.py tests/test_queue_jobs_api.py -q
```

Pass: 11 passed.

**Manual (`/ui3`):**

1. Two jobs with only `download=done`, valid clone voice selected in 1-click bar.
2. Tick both → **▶ Chạy hàng chờ** (confirm).
3. Job2 must not claim `__all__` until job1 mux done + `output.mp4` > 0.
4. **⏹ Dừng hàng chờ** mid job1 → queue empty; job2 never starts.
5. Enqueue job already wired done → `skipped_done`.
6. Restart server with pending ids in `work/_job_queue.json` → worker resumes.

**Pass:** one GPU job at a time, stop clears queue, skip done, persist resume.  
**Fail:** parallel ffmpeg/ASR, queue stuck, single run-all 409 regression.

## Docs updated

- `docs/superpowers/specs/2026-09-24-job-queue-design.md` — status → implemented + notes
- `docs/superpowers/sdd/2026-09-24-job-queue-progress.md` — Task 5 complete
- This report

No git commits (workspace not a git repo).
