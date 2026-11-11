# `agents.hongguo_bridge`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-11 02:38. Đừng sửa tay khối này. -->
**File:** `agents/hongguo_bridge.py` · **Lớp:** `source` · **4210 dòng** (3736 code) · **118 hàm**, **0 class** · sha1 `16b07bb99f`

> hongguo_bridge.py — client mỏng gọi Hongguo Downloader local API (:8000). App Hongguo phải đang chạy. Pineline chỉ proxy + queue merge tuần tự. Merge Hongguo gốc là -c copy (giữ nguyên bitstream) → series lẫn 1080/720

### Phụ thuộc

- **Gọi tới (import nội bộ):** [agents.hongguo_rpc](./agents.hongguo_rpc.md), [core](./core.md), [core.config](./core.config.md), [core.film_db](./core.film_db.md), [film_db](./film_db.md), [hg_ui_ctx](./hg_ui_ctx.md), [hongguo_license_ensure](./hongguo_license_ensure.md), [hongguo_rpc](./hongguo_rpc.md)
- **Được dùng bởi:** [agents.agent_hongguo](./agents.agent_hongguo.md), [agents.meta_studio](./agents.meta_studio.md), [core.film_db](./core.film_db.md), [engines.series_glossary](./engines.series_glossary.md), [film_db](./film_db.md), [http_routes.routes_uploader_settings](./http_routes.routes_uploader_settings.md), [scripts.check_batch1](./scripts.check_batch1.md), [scripts.check_batch2](./scripts.check_batch2.md)
- **Được nhắc tên file `.py` (subprocess/script) bởi:** [hongguo_bridge](./hongguo_bridge.md), [restart_server](./restart_server.md), [scripts._port_hg_watchlist_bridge](./scripts._port_hg_watchlist_bridge.md)
- **Test:** `tests/test_hg_merge_queue.py`

```mermaid
flowchart LR
  agents_hongguo_bridge[[agents.hongguo_bridge]]
  agents_agent_hongguo[agents.agent_hongguo] --> agents_hongguo_bridge
  agents_meta_studio[agents.meta_studio] --> agents_hongguo_bridge
  core_film_db[core.film_db] --> agents_hongguo_bridge
  engines_series_glossary[engines.series_glossary] --> agents_hongguo_bridge
  film_db[film_db] --> agents_hongguo_bridge
  http_routes_routes_uploader_settings[http_routes.routes_uploader_settings] --> agents_hongguo_bridge
  scripts_check_batch1[scripts.check_batch1] --> agents_hongguo_bridge
  scripts_check_batch2[scripts.check_batch2] --> agents_hongguo_bridge
  agents_hongguo_bridge --> agents_hongguo_rpc[agents.hongguo_rpc]
  agents_hongguo_bridge --> core[core]
  agents_hongguo_bridge --> core_config[core.config]
  agents_hongguo_bridge --> core_film_db[core.film_db]
  agents_hongguo_bridge --> film_db[film_db]
  agents_hongguo_bridge --> hg_ui_ctx[hg_ui_ctx]
  agents_hongguo_bridge --> hongguo_license_ensure[hongguo_license_ensure]
  agents_hongguo_bridge --> hongguo_rpc[hongguo_rpc]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `apply_request_backend` | 33 | 4 | `ui, referer` | Gắn backend theo UI — ủy quyền `hg_ui_ctx` (module không reload). |
| `_hg_backend_pref` | 42 | 16 | `` |  |
| `_rpc_mod` | 60 | 34 | `` | Trả module RPC. |
| `_http_reachable` | 99 | 13 | `base, timeout` | Downloader 1.x :8000 còn sống? (status không cần token). |
| `_use_rpc` | 114 | 39 | `` |  |
| `_save_merge_state` | 201 | 13 | `` | Gọi khi đang giữ _merge_lock. |
| `_load_merge_state` | 216 | 18 | `` |  |
| `_set_phase` | 240 | 10 | `name, phase, pct` |  |
| `season_stem` | 255 | 13 | `title` | Bỏ hậu tố mùa để gom series cùng tên gốc. |
| `franchise_core` | 270 | 3 | `title` | Lấy tên thương hiệu/series chuẩn để nhóm mùa chính xác mà không gộp nhầm thể loại (như 高武：, 游戏入侵：). |
| `_parse_cn_int` | 281 | 18 | `s` |  |
| `season_timeline_key` | 301 | 19 | `title, series_id` | Thứ tự phát hành ≈ series_id (snowflake). Phụ: cung/第N季 để ổn định khi thiếu id. |
| `order_franchise_items` | 322 | 67 | `items` | Sort theo thời gian phát hành (series_id) + gắn SS1→SSN. |
| `web_search_hongguoduanju` | 405 | 61 | `q, timeout` | Search trên hongguoduanju.com — thường ra đủ 第N季 mà /dl/search sót. |
| `_ingest_web_into` | 468 | 21 | `by_id, q, core_filter` | Ingest web results; nếu có core_filter chỉ giữ title cùng thương hiệu. |
| `web_expand_queries` | 497 | 24 | `q` | Query web tối thiểu nhưng phủ cao: exact + stem + vài mốc mùa. |
| `web_expand_into` | 523 | 28 | `by_id, q, workers` | Chạy song song vài web search → gộp vào by_id (lọc theo core). |
| `_load_title_cache` | 553 | 16 | `` |  |
| `_save_title_cache` | 571 | 8 | `data` |  |
| `lookup_series` | 581 | 73 | `series_id, base` | Lấy meta từ series_id (khi search không ra). |
| `series_seasons` | 656 | 20 | `series_id, base` |  |
| `series_qualities` | 678 | 23 | `series_id, base` | Không bao giờ 502 — catalog RPC chết thì trả ladder mặc định. |
| `_normalize_episode_cnt` | 703 | 18 | `v` | RPC 2.x đôi khi trả episodes=list[{number,durationSec}] — UI cũ cần int. |
| `resolve_text` | 723 | 73 | `text, base` | Parse link/share → series. Nhận URL detail/player hoặc series_id thuần. |
| `_cache_put` | 798 | 13 | `r` |  |
| `_fill_missing_from_cache` | 813 | 36 | `by_id, stem, base` | Với stem gốc, dò cache/seed cho 第1–15季 nếu search bỏ sót. |
| `expand_queries` | 851 | 28 | `q` | Sinh thêm query để bắt mùa đổi tên (灵界篇/仙界篇…). |
| `_base_port` | 881 | 8 | `base` |  |
| `_read_process_env_win` | 891 | 54 | `pid` | Đọc môi trường process khác (x64) qua PEB — lấy HG_UI_TOKEN. |
| `_hongguo_pids` | 947 | 16 | `` | PID process Hongguo Downloader (pythonw trong thư mục cài đặt). |
| `discover_ui_token` | 965 | 31 | `force` | Lấy HG_UI_TOKEN: env Pineline → cache → env process Downloader. |
| `_auth_headers` | 998 | 9 | `base` |  |
| `_is_ui_auth_error` | 1009 | 9 | `detail` |  |
| `_req` | 1020 | 53 | `method, base, path, payload, query, timeout, _retry_auth` |  |
| `_license_magic` | 1075 | 26 | `cmd, payload` | Hot-path license ops via search/resolve (works before :8801 reload of /api/hg/license/*). |
| `ping` | 1103 | 42 | `base` |  |
| `search` | 1147 | 166 ⚠️ | `q, base, expand` |  |
| `status` | 1315 | 4 | `base` |  |
| `settings` | 1321 | 10 | `base` | WinUI settings.get — saveFolder/quality/parallel… |
| `settings_update` | 1333 | 11 | `patch, base` | WinUI settings.update — ghi patch vào helper (cùng store với app). |
| `cancel` | 1346 | 5 | `base` | Stop all active downloads. |
| `cancel_download` | 1353 | 12 | `series_id, base` | Stop 1 download (RPC: cancelAll + requeue others). |
| `clear_finished` | 1367 | 4 | `base` |  |
| `remove_download` | 1373 | 7 | `series_id, base` |  |
| `retry_download` | 1382 | 7 | `series_id, base` |  |
| `open_folder` | 1391 | 24 | `path, name` | Mở thư mục series trong Explorer (WinUI Open folder). |
| `submit` | 1417 | 17 | `series_ids, base, scores, quality` |  |
| `library_update` | 1436 | 20 | `base, names` |  |
| `library_update_info` | 1458 | 5 | `base` | WinUI nút Update info — quét meta/poster, không tải mùa mới. |
| `seasons_decline` | 1465 | 5 | `series_ids, base` |  |
| `_normalize_browse_items` | 1472 | 25 | `items` |  |
| `_filter_by_genre_tag` | 1524 | 15 | `results, genre` |  |
| `_feed_labels` | 1564 | 18 | `` |  |
| `_feed_item_en` | 1584 | 5 | `zh_name` |  |
| `_localize_feed_rows` | 1591 | 25 | `rows` | Gắn label EN (WinUI FilterText) cho selector panel. |
| `feed_browse` | 1618 | 66 | `select, offset, size, panel, session_id` | Hongguo 2.x Browse = feed.page + selector panel (genre/theme/setting/…). |
| `_filter_by_status` | 1686 | 17 | `results, status` |  |
| `_rank_board_label` | 1761 | 7 | `zh` |  |
| `_localize_rank_charts` | 1770 | 23 | `charts` |  |
| `_resolve_rank_chart` | 1795 | 12 | `chart, board_legacy` |  |
| `_resolve_rank_board` | 1809 | 14 | `board, category` | RPC board id ('' = 总榜). category giữ alias cũ all/female/male/… |
| `rank_page` | 1825 | 38 | `chart, board, category, offset, size` | Hongguo 2.x Ranking = rank.page (charts + boards). |
| `rank` | 1865 | 133 ⚠️ | `category, board, offset, size, base, chart` | Bảng hot giống app Hongguo Downloader. |
| `genres` | 2000 | 15 | `limit` | Lấy danh sách các thể loại phim từ Hongguo Catalog Explorer. |
| `catalog` | 2017 | 62 | `genre, sort, status, q, page, size` | Khám phá kho phim Hongguo Catalog (Explorer). |
| `rank_episodes` | 2081 | 7 | `series_ids, base` | Bổ sung số tập cho list rank (POST /dl/rank-episodes). |
| `preview_series` | 2090 | 81 | `series_id, ep, fresh, base, quality` | Xem thử 1 tập. |
| `library` | 2173 | 34 | `base` |  |
| `_output_dir` | 2209 | 13 | `base` |  |
| `inspect_series_folder` | 2224 | 35 | `folder` | Quét folder series: có file (merged)? còn bao nhiêu mảnh tập? |
| `safe_child` | 2261 | 13 | `root, name` | root/name chỉ khi name là 1 cấp thư mục ngay dưới root. |
| `resolve_preview_path` | 2276 | 11 | `name, base` | Đường dẫn file xem thử trong thư viện (merged hoặc tập đầu). |
| `resolve_poster_path` | 2289 | 13 | `name, base` | poster.jpg/png trong folder series (local). |
| `fetch_poster` | 2304 | 32 | `name, base` | Bytes poster: ưu tiên /dl/poster (auth), fallback file local. |
| `fetch_img_proxy` | 2342 | 64 | `url, base` | Proxy ảnh cover: RPC ``covers.get`` → file local; HTTP :8000/img; fallback fetch trực tiếp. |
| `_trash_root` | 2412 | 7 | `folder` | Thùng rác NGOÀI thư viện (D:\Lib → D:\Lib_trash): Hongguo/Pineline quét thư viện |
| `purge_trash` | 2421 | 24 | `folder, days` | Xoá hẳn các lô trong thùng rác cũ hơn `days` ngày. Trả số lô đã xoá. |
| `merged_covers_fragments` | 2447 | 34 | `folder, merged_file` | Kiểm file gộp có chứa đủ các tập lẻ đang nằm trong folder không. |
| `_move_to_trash` | 2483 | 12 | `folder, files` |  |
| `cleanup_fragments` | 2497 | 30 | `folder` | Dọn tập lẻ sau khi đã có (merged) ĐỦ nội dung: chỉ file đúng mẫu tên tập, |
| `_ep_num_from_name` | 2529 | 15 | `name` | Số tập từ S01E013 / 第013集 / E13 / EP13 — không lấy nhầm season S01. |
| `_list_episode_frags` | 2546 | 33 | `folder` | Liệt kê tập mảnh; dedupe cùng số tập (ưu tiên SxxExxx + file đọc được). |
| `_probe_wh` | 2581 | 20 | `path` |  |
| `_probe_dur` | 2603 | 11 | `path` |  |
| `_frame_wh_at` | 2616 | 24 | `path, t` | Decode 1 frame tại t — bắt size thật (kể cả mid-stream đổi res). |
| `_pick_h264_encoder` | 2642 | 15 | `` | Args -c:v … cho normalize (ưu tiên NVENC). |
| `_scale_vf` | 2659 | 6 | `w, h` |  |
| `episode_resolutions` | 2667 | 20 | `folder` | Quét độ phân giải từng tập mảnh. mixed=True nếu lệch nhau. |
| `merged_has_mixed_res` | 2689 | 30 | `path, samples` | Kiểm tra file (merged) có đổi res giữa chừng không. |
| `normalize_merged_file` | 2721 | 72 | `path, target_wh, on_pct` | Re-encode 1 file (merged) về canvas cố định (scale+pad). |
| `merge_series_normalized` | 2795 | 117 | `folder, on_pct, target_wh` | Merge các tập mảnh về 1 canvas (scale+pad) rồi concat. |
| `mark_done` | 2914 | 8 | `name, merged_file, removed` |  |
| `merge_one` | 2924 | 5 | `name, base` |  |
| `merge_status` | 2931 | 2 | `base` |  |
| `open_library` | 2935 | 3 | `name, base` |  |
| `_film_db` | 2940 | 8 | `` | film_db dual-tree: V5 `core.film_db` hoặc V2/V4 `film_db`. |
| `remember_library_items` | 2950 | 9 | `items, source, on_disk, deleted` | Ghi meta series vào hg_watchlist (không giữ video). |
| `season_num` | 2961 | 14 | `title, season_field` | Số mùa từ field hoặc chữ 「第N季」 trong title; 0 = không rõ. |
| `discover_new_seasons` | 2977 | 197 ⚠️ | `base, max_cores, expand` | Chỉ tìm mùa/series mới theo watchlist+films+lib hiện có — KHÔNG gọi /dl/library/update. |
| `delete_library_series` | 3176 | 100 | `names, base` | Xoá vĩnh viễn thư mục series tại ổ đĩa D:\Lib để giải phóng dung lượng. |
| `merge_resume` | 3280 | 15 | `base` | Hàng đợi còn (nạp lại sau restart) mà không có worker → chạy tiếp, chỉ khi Hongguo đang mở |
| `merge_queue_state` | 3297 | 20 | `base` |  |
| `merge_queue_add` | 3319 | 41 | `names, base, skip_done` | Chỉ xếp hàng rồi trả về ngay — kiểm tra/chuẩn hoá/dọn tập đều do worker làm (UI thấy tiến độ). |
| `merge_queue_clear` | 3362 | 7 | `` |  |
| `_start_worker` | 3371 | 9 | `base` |  |
| `_finish` | 3382 | 13 | `name` | Kết thúc 1 series (xong hoặc lỗi): bỏ current, xoá phase, đếm vào batch, lưu state. |
| `_merge_worker` | 3397 | 244 ⚠️ | `base` |  |
| `_hist` | 3643 | 10 | `name, status, detail` |  |
| `_baike_get` | 3667 | 4 | `url, timeout` |  |
| `_baike_clean_title` | 3673 | 5 | `t` |  |
| `_titles_same_franchise` | 3680 | 21 | `root, other` | True nếu other cùng họ với root (bỏ ranking nhiễu trong 同系列). |
| `baike_search` | 3703 | 54 | `q, timeout` | Search https://www.duanjubaike.net/so.html?keyword=… |
| `baike_info` | 3759 | 189 ⚠️ | `series_id, timeout` | Trang info-{id}: meta + 同系列 (đã lọc nhiễu ranking). |
| `baike_deep` | 3950 | 37 | `series_id, title, timeout` | Lấy info sâu từ baike: ưu tiên series_id, không có thì search theo title. |
| `baike_versions` | 3989 | 51 | `q, timeout` | Q → search baike → chọn hit khớp nhất → danh sách version (đã lọc). |
| `_norm_title_key` | 4042 | 5 | `t` |  |
| `_hongguo_match_version` | 4049 | 94 | `ver, base` | Map 1 version baike → Hongguo. Ưu tiên series_id, rồi search đúng tên. |
| `search_via_baike` | 4145 | 66 | `q, base` | Baike nhận diện → versions → match từng cái trên Hongguo. |

**Hàm dài ≥120 dòng:** `_merge_worker` (244, L3397), `discover_new_seasons` (197, L2977), `baike_info` (189, L3759), `search` (166, L1147), `rank` (133, L1865)

### Config / env keys (2)

`HG_BACKEND`, `HG_UI_TOKEN`

**Cổng nhắc tới:** 8000

**File/artifact nhắc tới:** `.norm.partial.mp4`, `.norm.tmp.mp4`, `.series.json`, `.tmp.mp4`, `hg_merge_state.json`, `hg_title_cache.json`, `hongguo_feed_labels.json`, `list.txt`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=89 · file_writes=2 · global_stmt=7 · pools=2 · sleep=4 · subprocess=11 · swallow_except=25 · threads=1

### Lịch sử (từ docs/)

- **Fix logs (14):**
  - [`/api/hg/poster` 502 với job_id / `downloads`](../../fixes/2026-11-09-hg-poster-502-junk-name.md)
  - [Merge queue: «need at least 2 episodes» + NVENC -22 ep 第013集](../../fixes/2026-11-08-merge-frag-naming.md)
  - [Settings hongguo2 lệch WinUI + toast «Cần license»](../../fixes/2026-11-08-hongguo2-settings-winui.md)
  - [Hongguo2 Ranking/New lệch WinUI 2.x](../../fixes/2026-11-08-hongguo2-rank-new.md)
  - [Hongguo2: qualities 502 + /api/disk 404](../../fixes/2026-11-08-hongguo2-qualities-disk.md)
  - [Hongguo2: dropdown filter chữ mờ + chọn không đổi grid](../../fixes/2026-11-08-hongguo2-dropdown-winui.md)
  - [Hongguo2 Browse chỉ hiện ~20 phim](../../fixes/2026-11-08-hongguo2-browse-pagesize.md)
  - [Hongguo2 Browse filters lệch WinUI 2.x (3 dropdown giả)](../../fixes/2026-11-08-hongguo2-browse-facets.md)
  - [Helper Pineline leak / lệch WinUI (spawn riêng)](../../fixes/2026-11-08-helper-singleton-winui-parity.md)
  - [Hongguo "Merge all": không thấy đang chạy gì, 16 series rất lâu mới ra 1](../../fixes/2026-10-07-hg-merge-queue.md)
  - [Đợt 7: gỡ UI cũ, tách server.py](../../fixes/2026-10-06-batch7-ui-split.md)
  - [2026-10-06 — Đợt 6 review: bảo trì (git, pytest, M3, dọn script chết)](../../fixes/2026-10-06-batch6-maintenance.md)
  - [2026-10-06 — Đợt 2 review: bảo mật + config một nguồn + LLM sập không để trống câu](../../fixes/2026-10-06-batch2-security.md)
  - [Đợt 1 — chặn mất dữ liệu (review 6/10)](../../fixes/2026-10-06-batch1-data-loss.md)
- **Reviews:** [_atoms_http_agents](../../reviews/_atoms_http_agents.md), [2026-11-07-hongguo-lic-host-portability](../../reviews/2026-11-07-hongguo-lic-host-portability.md), [2026-11-07-hongguo-2x-post-restart-test](../../reviews/2026-11-07-hongguo-2x-post-restart-test.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md), [2026-10-06-code-review](../../reviews/2026-10-06-code-review.md)
- Nhắc trong CHANGELOG: **5** lần · DECISIONS: **0** lần

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
