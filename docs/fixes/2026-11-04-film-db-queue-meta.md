# Queue metadata từ films.db (V5) — bớt đọc manifest

- **Date:** 2026-11-04
- **Job / khu vực:** V5 `film_db.py` + `job_queue.py` + `server.py` / `pineline/server/routes/queue.py`
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-04_v5-film-db-queue\`

## Triệu chứng

Poll hàng chờ mở nhiều `manifest.json` chỉ để lấy title/series/season; đã có `films.db` nhưng chưa dùng cho queue UI.

## Root cause

`get_job_info` / `GET /api/queue/jobs` đọc file từng job; sync DB thiếu `series_ui` / `season_ui` / `group_index` (semantics UI).

## Fix

- Cột mới + populate khi `row_from_manifest` / `sync`
- `job_meta.py` parse dùng chung
- `get_job_info` / `get_jobs_info` DB-first
- `/api/queue/jobs`: batch DB cho pending; manifest chỉ `current` progress

## Recheck

1. `pytest tests/test_film_db_queue_meta.py tests/test_job_queue.py -q` → pass
2. `python -c "import film_db; print(film_db.sync())"` → rows có `series_ui`
3. `GET :8805/api/queue/jobs` — pending không cần N× manifest title
4. **Pass nếu:** `queue_items[].season` khớp Phần trên title; sort P1→Pn ổn
5. **Fail nếu:** mọi pending vẫn parse file hoặc `series_ui` null sau sync

## Liên quan

- Design: `docs/design/2026-11-04-film-db-queue-listing.md`
- Plan: `docs/superpowers/plans/2026-11-04-film-db-queue-listing.md`
- **Restart :8805** để nạp code
