# Hợp đồng dữ liệu: manifest vs films.db

_Cập nhật: 2026-11-04_

Hai nơi lưu — **không** nhét mọi thứ vào một chỗ. Mỗi field có một nguồn đọc mặc định.

## `work/<job_id>/manifest.json` — sự thật theo job (live + pipeline)

| Nhóm | Ví dụ | Ai ghi |
|---|---|---|
| Request / nguồn | `request.*`, URL, path local, group_* | create job, group API, import |
| Stage runtime | `stages.*.status/progress/started_at` | asr/translate/tts/mux… |
| Artifact paths | `script.json`, wav, `final.mp4` | pipeline |
| Opts snapshot | opts lúc worker nhận job | job_queue worker |

**Đọc live:** progress/ETA dashboard (`job_queue.current_detail`), stage đang chạy, debug 1 job.

## `data/films.db` — chỉ mục UI / hàng chờ / thư viện

| Cột / nhóm | Dùng cho |
|---|---|
| `title`, `series_ui`, `season_ui`, `group_index`, `group_id`, `group_title` | Queue list, sort, label |
| Upload / YT / lib | Films UI, sync uploader |
| Trạng thái tóm tắt | Lọc thư viện (không thay stage chi tiết) |

**Đọc list:** `job_queue.get_job_info` / `get_jobs_info` (DB-first). Sync từ manifest qua `film_db.sync_one` / migrate.

## Ai gọi cái gì

| Nhu cầu | API / hàm | Nguồn |
|---|---|---|
| Poll hàng chờ (N job) | `GET /api/queue/jobs` → `http_queue_state` | DB batch + **1** manifest (`current`) |
| Sort / move nội bộ | `queue_sort` / `job_sort_key` | `get_job_info` (DB-first) |
| Chi tiết 1 job / stage | `GET /api/jobs/{id}` | manifest |
| Đổi nhóm series | `POST /api/queue/group` | ghi manifest (+ sync DB) |

## Không làm

- Không đọc N manifest mỗi lần poll queue.
- Không coi package `pineline.server.routes.queue` là bản copy thứ hai của handler — chỉ **registry path** (`attach`).
- Không ghi secret vào manifest/DB docs.
