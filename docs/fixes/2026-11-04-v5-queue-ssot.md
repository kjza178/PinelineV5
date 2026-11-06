# V5: queue/jobs dual-route + queue_state đọc N lần

- **Date:** 2026-11-04
- **Job / khu vực:** V5 `server.py`, `job_queue.py`, `pineline.server.routes.queue`
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-04_v5-queue-ssot\` (+ snapshot zip nếu có)

## Triệu chứng

Package `pineline.server.routes.queue` có body handler đầy đủ nhưng **không** `include_router` — docs ghi LIVE sai. `server.py` vẫn `@app` trùng. `queue_state()` gọi N× `get_job_info` rồi API xây lại `queue_items` lần nữa.

## Root cause

Refactor khung V5 dở: copy handler sang package rồi không cắt `@app` / không wire; `queue_state` và `api_queue_jobs_state` cùng enrich metadata.

## Evidence

- Audit: `grep include_router` không có queue/jobs package trước fix; OpenAPI chỉ từ `@app`.
- Sau fix: `queue.router.routes` = 12, `jobs.router.routes` = 43; OpenAPI ~10 `/api/queue*` + ~38 `/api/jobs*`.

## Fix

- `queue.py` package → chỉ `_ROUTES` + `attach` (như jobs).
- Strip `@app` queue/jobs; `attach` + `include_router` cuối `server.py`.
- `job_queue.current_detail` / `build_queue_items` / `http_queue_state`; `queue_state(enrich=True)` batch DB một lần.
- Docs: `MANIFEST_CONTRACT.md`, ARCHITECTURE, routes README.

## Recheck

1. `python -c "from pineline.server.routes import queue, jobs; import server as S; print(len(queue.router.routes), len(jobs.router.routes)); print(any('/api/queue/jobs' in p for p in S.app.openapi()['paths']))"`
2. `pytest tests/test_film_db_queue_meta.py tests/test_queue_http_state.py -q`
3. **Pass nếu:** attach counts > 0; OpenAPI có `/api/queue/jobs`; pytest xanh; sau restart :8805 UI queue sort/poll bình thường.
4. **Fail nếu:** 404 queue/jobs sau restart, hoặc OpenAPI thiếu path.

## Liên quan

- DECISIONS 2026-11-04 V5 queue/jobs SSOT
- `docs/fixes/2026-11-04-film-db-queue-meta.md`

## Follow-up — assets/fs attach (2026-11-04 ~19:45)

- **Backup:** `Z:\PinelineV2_codebak\2026-11-04_v5-assets-fs-attach\`
- Strip 10 `@app` cookies/voices/frames/brand/clone/voice-sample/models/llm/fs từ `server.py`; wire sẵn `assets.attach` + `fs.attach` + `include_router`.
- Verify: `re.findall` các path trên → `[]`; OpenAPI có `/api/cookies|voices|fs/list-dirs|models`; không Duplicate Operation ID job_video/hg.
- Archive oneshots → `scripts/archive/oneshot/`; xoá `scripts/archive/tauri_desktop/node_modules` (~16 MB).
- Pytest: `test_queue_http_state` + `test_film_db_queue_meta` → 5 passed.
- **Restart :8805** để process nạp server đã strip.
