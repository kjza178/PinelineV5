# Film DB queue listing (V5) — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans (or implement directly in-session). Steps are ordered.

**Goal:** Queue/UI metadata từ `films.db` (series_ui, season, group_index); giảm đọc `manifest.json` khi poll `/api/queue/jobs`.

**Architecture:** Enrich `film_db.row_from_manifest` → `get_job_info` DB-first → `GET /api/queue/jobs` batch `get_many`; manifest chỉ cho live progress của `current`.

**Tech:** SQLite `data/films.db`, `job_queue.py`, `server.py` (+ `pineline/server/routes/queue.py` nếu mirror).

## File map

| File | Responsibility |
|---|---|
| `film_db.py` | migrate cột, populate, `get_many` |
| `job_queue.py` | DB-first `get_job_info` |
| `server.py` | bỏ double-read pending |
| `pineline/server/routes/queue.py` | mirror nếu tồn tại |
| `tests/test_film_db_queue_meta.py` | sync + DB-first + API |

## Tasks

1. Schema migrate + `row_from_manifest` fill `group_index`/`series_ui`/`season` (UI semantics)
2. `get_many` + test backfill
3. `get_job_info` DB-first + fallback file
4. Slim `api_queue_jobs_state`
5. Docs CHANGELOG/worklog/fix; restart note :8805
