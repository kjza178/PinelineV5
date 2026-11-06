# 2026-09-26 — P0 job management (PinelineV2)

## Shipped
1. **Opts per-job** — `job_queue._opts_by_job`; batch sau không đè voice/mode job đang chờ.
2. **Enqueue series** — `POST /api/queue/jobs/group` + nút ▶ trên group head (sort `group_index`).
3. **Queue dashboard** — `GET /api/queue/jobs` thêm `current_detail` (stage/%/ETA thô/title) + history fail trên `#queue-status`.
4. **GPU gate** — `queue_busy()`; watcher + `/api/agent/heal-failed` apply skip khi queue đang chạy.

## APIs
- `POST /api/queue/jobs/group` `{group_id, ...RunAllOpts, skip_done}`
- `POST /api/queue/jobs/remove` `{job_ids}`
- `GET /api/queue/jobs` → `current_detail`, `queue_labels`, `busy`, `opts_by_job`

## Tests
`tests/test_job_queue.py` + `test_job_queue_worker.py` — 13 passed.
