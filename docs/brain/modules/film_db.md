# `film_db`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-11 02:38. Đừng sửa tay khối này. -->
**File:** `film_db.py` · **Lớp:** `publish` · **1091 dòng** (953 code) · **42 hàm**, **0 class** · sha1 `8104b8759a`

> Database phim đã làm (SQLite) — nguồn sự thật lâu dài, không mất khi xoá thư mục job. films   : 1 dòng / job — tên gốc + tên Việt, series/mùa, file nguồn, trạng thái, thời lượng, output, config lồng tiếng, link YouTube (

### Phụ thuộc

- **Gọi tới (import nội bộ):** [agents.hongguo_bridge](./agents.hongguo_bridge.md), [hongguo_bridge](./hongguo_bridge.md)
- **Được dùng bởi:** [agent_core](./agent_core.md), [agent_feeder](./agent_feeder.md), [agent_tele_cmd](./agent_tele_cmd.md), [agents.agent_feeder](./agents.agent_feeder.md), [agents.agent_tele_cmd](./agents.agent_tele_cmd.md), [agents.auto_publisher](./agents.auto_publisher.md), [agents.hongguo_bridge](./agents.hongguo_bridge.md), [agents.test_channel](./agents.test_channel.md), [auto_publisher](./auto_publisher.md), [films_merge_api](./films_merge_api.md), [hongguo_bridge](./hongguo_bridge.md), [http_routes.routes_hg](./http_routes.routes_hg.md), [meta_studio](./meta_studio.md), [routes_films](./routes_films.md), [routes_hg](./routes_hg.md), [series_glossary](./series_glossary.md), [split_parts](./split_parts.md), [test_channel](./test_channel.md), [tools.test_channel](./tools.test_channel.md)
- **Test:** ❌ chưa có test import trực tiếp
- **Thư viện ngoài:** `check_block`

```mermaid
flowchart LR
  film_db[[film_db]]
  agent_core[agent_core] --> film_db
  agent_feeder[agent_feeder] --> film_db
  agent_tele_cmd[agent_tele_cmd] --> film_db
  agents_agent_feeder[agents.agent_feeder] --> film_db
  agents_agent_tele_cmd[agents.agent_tele_cmd] --> film_db
  agents_auto_publisher[agents.auto_publisher] --> film_db
  agents_hongguo_bridge[agents.hongguo_bridge] --> film_db
  agents_test_channel[agents.test_channel] --> film_db
  auto_publisher[auto_publisher] --> film_db
  films_merge_api[films_merge_api] --> film_db
  hongguo_bridge[hongguo_bridge] --> film_db
  http_routes_routes_hg[http_routes.routes_hg] --> film_db
  meta_studio[meta_studio] --> film_db
  routes_films[routes_films] --> film_db
  routes_hg[routes_hg] --> film_db
  film_db --> agents_hongguo_bridge[agents.hongguo_bridge]
  film_db --> hongguo_bridge[hongguo_bridge]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `_strip_part_suffix` | 33 | 2 | `title` |  |
| `is_junk_hg_name` | 37 | 15 | `name, job_id` | True nếu không nên dùng làm tên folder Lib / query /api/hg/poster. |
| `derive_hg_name` | 54 | 52 | `job_id, req, title_clean` | Tên folder Hongguo/Lib cho poster — không lấy job_id / downloads / part folder. |
| `_utc` | 209 | 2 | `` |  |
| `norm_path` | 213 | 2 | `p` |  |
| `connect` | 217 | 28 | `` |  |
| `log_event` | 247 | 6 | `job_id, kind, detail` |  |
| `_status_of` | 257 | 12 | `stages` |  |
| `_series_season` | 271 | 8 | `title, series_id` |  |
| `_num` | 281 | 5 | `v, cast` |  |
| `_is_upload_lock_active` | 288 | 20 | `job_id` | Kiểm tra nhanh xem .upload.lock của job còn thuộc về tiến trình đang sống không. |
| `row_from_manifest` | 310 | 39 | `job_id, m` |  |
| `sync_one` | 358 | 38 | `job_id` | Đồng bộ tức thì 1 job từ work/<job_id>/manifest.json vào films.db. |
| `sync` | 398 | 57 | `hg_library` | Quét manifest → upsert films; ghi event khi trạng thái đổi. Trả {new, changed, total}. |
| `needs_series_ids` | 457 | 4 | `` |  |
| `sync_uploads` | 463 | 82 | `` | Link YouTube từ Z:\yt_uploader\upload_history.jsonl và queue_state.json. |
| `source_keys` | 549 | 3 | `` |  |
| `series_ids` | 554 | 3 | `` |  |
| `update_block_status` | 559 | 18 | `job_id, status, reason` | Cập nhật trạng thái bản quyền (clean/blocked/claim/private/unknown) và lý do cho 1 phim. |
| `query` | 579 | 32 | `q, status, limit, order, work_exists, block_status` |  |
| `get` | 613 | 9 | `job_id` |  |
| `delete_film` | 624 | 19 | `job_id, delete_work` | Xoá 1 film khỏi database và tuỳ chọn xoá thư mục work trên ổ đĩa. |
| `delete_films` | 645 | 21 | `job_ids, delete_work` | Xoá nhiều film theo danh sách job_id. |
| `purge_missing` | 668 | 13 | `only_pending_failed` | Xoá toàn bộ hoặc các job chưa hoàn thành mà thư mục work đã bị xoá (work_exists = 0). |
| `stats` | 683 | 18 | `` |  |
| `to_csv` | 703 | 10 | `rows` |  |
| `_dur` | 715 | 5 | `sec` |  |
| `format_stats` | 722 | 12 | `` |  |
| `format_rows` | 736 | 12 | `rows` |  |
| `format_detail` | 750 | 18 | `job_id` |  |
| `upsert_library_block` | 772 | 64 | `name, core, title_vi, video_path, status, reason, test_yt_url, test…` | Lưu hoặc cập nhật trạng thái bản quyền phim trong Thư viện gốc. |
| `get_library_block` | 838 | 4 | `name` |  |
| `list_pending_rechecks` | 844 | 7 | `` | Lấy danh sách các bản ghi đang chờ recheck (status='testing'). |
| `list_library_blocks` | 853 | 5 | `` | Trả về dict name -> record của tất cả các bộ đã check trong Thư viện. |
| `delete_library_block` | 860 | 4 | `name` |  |
| `upsert_hg_watchlist` | 871 | 58 | `sid, title, name, core, season, eps, score, album, source, on_disk,…` | Ghi/ cập nhật 1 series Hongguo vào watchlist (chỉ meta, không video). |
| `upsert_hg_watchlist_many` | 931 | 24 | `items, source, on_disk, deleted` |  |
| `mark_hg_watchlist_deleted_by_names` | 957 | 15 | `names` | Đánh dấu xoá theo tên folder Lib (giữ sid/core). |
| `list_hg_watchlist` | 974 | 9 | `include_deleted` |  |
| `known_hg_sids` | 985 | 8 | `` | Mọi sid đã biết: films + watchlist. |
| `watchlist_cores` | 995 | 46 | `limit` | Franchise cores để quét mùa mới (watchlist + films.series). |
| `sync_library_blocks_from_yt_queue` | 1043 | 48 | `check_live` | Đồng bộ trạng thái bản quyền từ Z:\yt_uploader\queue_state.json cho các video D:\Lib. |

### Config / env keys (2)

`FILM_DB`, `YT_UPLOADER_DIR`

**File/artifact nhắc tới:** `.upload.lock`, `films.db`, `manifest.json`, `queue_state.json`, `upload_history.jsonl`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=19 · swallow_except=11

### Lịch sử (từ docs/)

- **Fix logs (5):**
  - [`/api/hg/poster` 502 với job_id / `downloads`](../../fixes/2026-11-09-hg-poster-502-junk-name.md)
  - [Queue metadata từ films.db (V5) — bớt đọc manifest](../../fixes/2026-11-04-film-db-queue-meta.md)
  - [`/library/action` crash — gọi API film_db không tồn tại](../../fixes/2026-11-02-library-action-missing-api.md)
  - [Phim đã xoá thư mục vẫn tồn đọng trong films/ui và thiếu chức năng xoá phim](../../fixes/2026-10-09-films-ui-delete-missing.md)
  - [2026-10-06 — Đợt 6 review: bảo trì (git, pytest, M3, dọn script chết)](../../fixes/2026-10-06-batch6-maintenance.md)
- **Reviews:** [_atoms_core_server](../../reviews/_atoms_core_server.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md), [2026-11-02-v4-structure-and-v2-port](../../reviews/2026-11-02-v4-structure-and-v2-port.md), [2026-10-06-code-review](../../reviews/2026-10-06-code-review.md)
- Nhắc trong CHANGELOG: **3** lần · DECISIONS: **1** lần

<!-- AUTO:END -->

<!-- MANUAL:START -->
## Vai trò (viết tay)

_Chưa viết. 2–4 câu: module này chịu trách nhiệm gì trong pipeline, ai gọi nó, nó KHÔNG làm gì._

## Luồng chính

_Các hàm vào (entry) → bước chính → output/side effect. Ghi tên hàm thật._

## Bất biến & hợp đồng

_Điều luôn phải đúng (vd: chỉ ghi manifest qua `Manifest.update`; 1 job / ghế). Vi phạm = bug._

## Bẫy đã biết

_Lỗi từng gặp + link `docs/fixes/...`. Những chỗ dễ sửa sai._

## Ghi chú vận hành

_Config key quan trọng, cần restart gì khi sửa (:8801 / :8802 / hot-reload), cách test._
<!-- MANUAL:END -->
