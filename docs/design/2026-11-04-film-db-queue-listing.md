# Design: Queue/UI listing từ `films.db` (thay manifest per-job)

- **Date:** 2026-11-04
- **Scope:** Pineline **V5 only** (so sánh evidence với V2 work/DB khi cần)
- **Status:** research — chưa implement

## 1. Pain hiện tại

Queue modal + `/api/queue/jobs` vẫn **đọc `work/<id>/manifest.json` từng job** (không cache) để lấy title / series / season / group_*, trong khi V5 đã có SQLite `data/films.db` (`film_db.py`) sync định kỳ và API `/films*`.

Hệ quả:

- I/O lặp khi poll hàng chờ (mỗi 2s khi worker/queue busy).
- Logic season/series **lệch** giữa 3 nơi: `job_queue.get_job_info`, `film_db.row_from_manifest`, UI `index3.html` `getDisplayInfo`.
- Sort/badge phụ thuộc parse title mỗi lần (đã fix ưu tiên «Phần N» — `docs/fixes/2026-11-04-queue-sort-move.md`) nhưng vẫn tốn file read.

V5 workspace hiện gần trống (`work/` ~1 job, `films.db` ~1 row). Evidence gap lấy từ **V2** (`work/` 30 manifest, `films.db` 37 rows) vì cùng schema/`film_db`/`get_job_info`.

## 2. DB capabilities (`film_db.py`)

### Schema `films` (SCHEMA + migrate runtime)

| Column | Có | Ghi chú |
|---|---|---|
| `job_id` PK | ✓ | |
| `title`, `title_vi` | ✓ | `title` = CN/request; `title_vi` từ manifest |
| `series`, `season` | ✓ | **không** cùng semantics với `get_job_info` |
| `group_id`, `group_title` | ✓ | từ `request.*` |
| `group_index` | ✗ | **thiếu cột** — chỉ có trong manifest / `get_job_info` |
| `status`, `stage` | ✓ | từ stages + upload lock |
| `yt_url`, `yt_channel`, `uploaded_at` | ✓ | `sync_uploads()` |
| `work_exists` | ✓ | 0 khi xoá thư mục, vẫn giữ history |
| `voice`, `tts_engine`, `audio_mode`, `opts_json` | ✓ | |
| `duration_sec`, `width`, `height`, `output_*` | ✓ | |
| `hg_name`, `hg_series_id` | ✓ | Hongguo |
| `block_status`, `block_reason`, `checked_at` | ✓ | migrate ALTER |
| `note`, `created_at`, `finished_at`, `updated_at` | ✓ | |

Tables khác: `events`, `library_blocks`, `series_glossary`.

### Sync đã có

| API | File | Việc |
|---|---|---|
| `row_from_manifest(job_id, m)` | `film_db.py` | Map manifest → row |
| `sync_one(job_id)` | `film_db.py` | Upsert 1 job |
| `sync(hg_library=None)` | `film_db.py` | Quét mọi `work/*/manifest.json` + `work_exists=0` |
| `sync_uploads()` | `film_db.py` | YT history / queue_state |
| `query` / `get` / `stats` / `delete_*` / `purge_missing` | `film_db.py` | Tra cứu |
| `filmdb_loop` | `agent_tele_cmd.py` | Background mỗi `FILMDB_SEC` (default **120s**) |
| `POST /films/sync`, `GET /films`, `GET /films/{id}` | `routes_films.py` | UI thư viện (không phải job queue) |

`series`/`season` trong sync hiện lấy từ `hongguo_bridge.franchise_core` + `season_timeline_key` trên **title CN** (`_series_season`), không phải parser VI của queue.

## 3. Call sites cần metadata (manifest / `get_job_info`)

| Nơi | Hàm / endpoint | Cần gì | Nguồn hiện tại |
|---|---|---|---|
| `job_queue.py` | `get_job_info` | title, series, season, group_* | **manifest mỗi lần** |
| `job_queue.py` | `job_sort_key`, `queue_sort`, `queue_add(sort_first)` | sort key | → `get_job_info` |
| `job_queue.py` | `queue_state` | `queue_items`, `current_info` | N(+1) × `get_job_info` |
| `job_queue.py` | `queue_add_group` | group members by index | **scan mọi** manifest |
| `server.py` | `api_queue_jobs_state` `GET /api/queue/jobs` | labels + `queue_items` | `_queue_current_detail` **+** `get_job_info` **lặp lại** |
| `pineline/server/routes/queue.py` | cùng shape | mirror server | giống trên |
| `server.py` | `_queue_current_detail` | title + group_* + **live** stage/progress/ETA | manifest (live — giữ) |
| `server.py` | `list_jobs` `GET /api/jobs` | full job cards | `read_job` + `_job_cache` theo mtime/size |
| `index3.html` | `paintQueueStatus` / `openQueueModal` / `renderQueueModal` | hiển thị queue | `/api/queue/jobs` (+ fallback parse từ `cache` `/api/jobs`) |
| `auto_publisher.py` / `meta_studio.py` | season / title | 1-off | `get_job_info` hoặc `film_db.get` |

`GET /api/jobs` **không** dùng `film_db`. Cache `_job_cache` chỉ giảm parse khi mtime/size không đổi; mỗi poll vẫn `stat()` mọi job.

## 4. Số lần hit manifest — queue modal / poll

Gọi `N` = số job pending trong `_q`, `C` = 1 nếu có `current`, `M` = số thư mục work có manifest.

### Một lần `GET /api/queue/jobs`

1. `queue_state()`: **N + C** lần `get_job_info` → **N+C** đọc/parse manifest (không cache).
2. `_queue_current_detail(current)`: **C** đọc manifest (live progress).
3. Với mỗi pending: `_queue_current_detail(jid)` + `get_job_info(jid)` → **2N** đọc nữa.

**Tổng ≈ 3N + 2C** mở/parse `manifest.json` mỗi request.  
Trong đó **~2N** là trùng lặp thuần metadata (state đã build `queue_items` rồi API build lại).

### Khi modal mở + queue busy (`index3.html`)

- `setInterval(..., 2000)` → `paintQueueStatus()` + `refresh()`.
- Mỗi 2s: **1×** `/api/queue/jobs` (công thức trên) **+** **1×** `/api/jobs` (`list_jobs` → M × `stat`, parse nếu miss cache).
- `openQueueModal`: có thể thêm 1× `/api/jobs` nếu `cache` trống.

Ví dụ N=20, C=1, M=30: mỗi 2s ≈ **62** manifest metadata reads (queue) + 30 stats (list). Sort `series_season` thêm N reads.

## 5. Gap list — DB vs `get_job_info` (V2 sample 30 live jobs)

So sánh sau `chdir Z:\PinelineV2`:

| Metric | Kết quả |
|---|---|
| Cùng series+season DB vs jq | **2 / 30** |
| Lệch `series` | **28 / 30** |
| Lệch `season` | **2 / 30** |
| Cột `group_index` trong DB | **không có** |
| jq có `group_index` | 26/28 diffs |

**Semantics lệch (quan trọng):**

| Field | `get_job_info` (queue UI) | `film_db.row_from_manifest` |
|---|---|---|
| Display title | `title_vi` ‖ req title ‖ zh | `title` = CN clean; `title_vi` riêng |
| `series` | Strip «Phần N» từ **title_vi** → tên VI ngắn (vd `Tu Tiên Ngũ Linh Căn`) | `franchise_core(CN title)` → stem **Trung** |
| `season` | Parse «Phần N» / 第N季 từ title; fallback `group_index` | `season_timeline_key` số mùa CN; có thể `None`→DB vẫn hay có số |
| `group_index` | Có | Không lưu |

Kết luận: **không thể** swap queue sang `films.series`/`season` hiện tại mà không đổi sync — UI sẽ hiện series Trung / lệch sort key so với fix 2026-11-04.

## 6. Design đề xuất (V5-first, phased)

### Nguyên tắc

1. **Nguồn sự thật lâu dài:** `films.db` cho metadata ổn định (title_vi, series UI, season, group_*).
2. **Manifest vẫn bắt buộc** cho tiến độ live (`stages`, progress, ETA) và khi row thiếu/`work_exists` lệch.
3. Một hàm parse dùng chung với `get_job_info` (tránh 3 bản regex).

### Phase A — Schema + sync (không đổi UI)

**Thêm/populate:**

| Column | Populate từ |
|---|---|
| `group_index` INTEGER | `request.group_index` |
| `series_ui` TEXT (mới) **hoặc** overwrite semantics `series` cho UI | Cùng logic extract VI như `get_job_info` |
| `season` | Ưu tiên `_parse_season_from_text(title_vi,…)` rồi `group_index` rồi CN 第N季 |
| Giữ `series` cũ (CN franchise) | Đổi tên conceptual → `series_core` (ALTER hoặc cột mới `series_core`, migrate) |

Khuyến nghị an toàn: **thêm** `series_ui` + `group_index`; giữ `series` CN cho films UI / feeder; queue dùng `series_ui`.

**Code touch:** `film_db.row_from_manifest`, `_SYNC_COLS`, migrate trong `connect()`, `sync`/`sync_one`. Share parse: import từ `job_queue` (`_parse_season_from_text` + extract series) hoặc module nhỏ `job_meta.py`.

**Backfill:** `POST /films/sync` hoặc `film_db.sync()` / script one-shot — đã quét mọi manifest.

### Phase B — `get_job_info` DB-first

```text
get_job_info(jid):
  row = film_db.get(jid)   # hoặc get_lite không events
  if row and (row.title_vi or row.title) and row.work_exists is not None:
     return map_row_to_queue_item(row)  # title=title_vi|title, series=series_ui|…
  fallback: đọc manifest như hiện tại
  optionally sync_one(jid) async/lazy
```

`job_sort_key` / `queue_sort` / `queue_state` hưởng lợi ngay, không đổi API shape.

### Phase C — API queue từ DB (batch)

- `film_db.get_many(job_ids: list[str]) -> dict[str, dict]` một query `WHERE job_id IN (…)`.
- `server.api_queue_jobs_state` / `pineline.server.routes.queue`:
  - Bỏ vòng `get_job_info` trùng; build `queue_items` từ `get_many(queue)`.
  - `_queue_current_detail` **chỉ** cho `current` (và optionally job đang running trong list nếu cần progress) — **không** đọc manifest mọi pending chỉ để lấy title/group.
- `queue_state()` có thể thôi embed full `queue_items` nếu API luôn enrich — hoặc để `queue_items` DB-backed một lần.

**Fallback:** thiếu row → manifest; thiếu cả hai → `{job_id, title:jid, season:1}`.

### Phase D — (tuỳ chọn) Sidebar `/api/jobs` nhẹ

Không thay `read_job` đầy đủ ngay. Có thể:

- Endpoint mới `GET /api/jobs/summary` từ DB (title, status, group_*, overall coarse), hoặc
- `list_jobs` join DB cho title/group khi cache miss.

Giữ `GET /api/jobs/{id}` = manifest/`read_job` cho detail panel (stages, n_missing, …).

### Không làm trong phase đầu

- Xoá manifest.
- Bắt buộc sidecar `:8802` cho queue (routes_films đã gắn server V5).
- Đổi films_ui sang series_ui nếu chưa migrate UI thư viện.

## 7. Acceptance / recheck (khi implement)

1. Queue N≥10: mở modal, poll 10s — số lần `manifest.json` open cho pending metadata ≈ 0 (chỉ current progress).
2. Sort «Phần 1→Pn» giữ hành vi test `test_queue_sort_prefers_title_phan_over_group_index`.
3. Job mới tạo: sau `sync_one` (hoặc fallback file) modal hiện title_vi đúng.
4. Job `work_exists=0`: vẫn list được trong `/films`; queue add vẫn skip missing manifest.
5. So sánh sample: `series_ui` khớp `get_job_info().series` trên ≥95% live V2/V5 jobs sau backfill.

## 8. File map (implement sau)

| File | Việc |
|---|---|
| `film_db.py` | cột mới, `row_from_manifest`, `get_many`, migrate |
| `job_queue.py` | DB-first `get_job_info`; optional `queue_add_group` query DB |
| `server.py` + `pineline/server/routes/queue.py` | bỏ double-read; enrich từ DB |
| `routes_films.py` | expose sync/backfill nếu cần |
| `tests/test_job_queue.py`, `test_queue_jobs_api.py` | DB hit / fallback |
| `index3.html` | hầu như không đổi nếu `queue_items` shape giữ nguyên |

## Liên quan

- Fix season/sort: `docs/fixes/2026-11-04-queue-sort-move.md`
- Films API: `routes_films.py`, sync loop `agent_tele_cmd.filmdb_loop`
- Evidence DB: `Z:\PinelineV2\data\films.db` (37 rows); V5 DB hiện gần trống
