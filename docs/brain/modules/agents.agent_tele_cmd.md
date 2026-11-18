# `agents.agent_tele_cmd`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-17 19:05. Đừng sửa tay khối này. -->
**File:** `agents/agent_tele_cmd.py` · **Lớp:** `sidecar` · **2469 dòng** (2240 code) · **42 hàm**, **2 class** · sha1 `a1fbd99c0a`

> Sidecar: Telegram lệnh + Auto-pilot + HTTP :8802 KHÔNG restart Pineline server — chỉ gọi API :8801. Chạy:  python agent_tele_cmd.py

### Phụ thuộc

- **Gọi tới (import nội bộ):** [agents.agent_autopilot](./agents.agent_autopilot.md), [agents.agent_feeder](./agents.agent_feeder.md), [agents.agent_hongguo](./agents.agent_hongguo.md), [agents.agent_watch](./agents.agent_watch.md), [agents.auto_publisher](./agents.auto_publisher.md), [agents.canva_client](./agents.canva_client.md), [agents.films_merge_api](./agents.films_merge_api.md), [agents.hongguo_bridge](./agents.hongguo_bridge.md), [agents.meta_studio](./agents.meta_studio.md), [agents.test_channel](./agents.test_channel.md), [agents.uploader_settings_api](./agents.uploader_settings_api.md), [core.batch_config](./core.batch_config.md), [core.film_db](./core.film_db.md), [engines.check_block](./engines.check_block.md), [engines.lib_normalize](./engines.lib_normalize.md), [engines.llm](./engines.llm.md), [engines.title_mt](./engines.title_mt.md), [tools.lib_check](./tools.lib_check.md)
- **Được dùng bởi:** [agents.auto_publisher](./agents.auto_publisher.md), [scripts.check_batch5](./scripts.check_batch5.md), [scripts.check_sidecar_lock](./scripts.check_sidecar_lock.md)
- **Được nhắc tên file `.py` (subprocess/script) bởi:** [restart_server](./restart_server.md), [scripts.check_batch2](./scripts.check_batch2.md), [tools.migrate_work](./tools.migrate_work.md)
- **Test:** `tests/test_agent_hold_telegram.py`
- **Thư viện ngoài:** `PIL`, `requests`

```mermaid
flowchart LR
  agents_agent_tele_cmd[[agents.agent_tele_cmd]]
  agents_auto_publisher[agents.auto_publisher] --> agents_agent_tele_cmd
  scripts_check_batch5[scripts.check_batch5] --> agents_agent_tele_cmd
  scripts_check_sidecar_lock[scripts.check_sidecar_lock] --> agents_agent_tele_cmd
  agents_agent_tele_cmd --> agents_agent_autopilot[agents.agent_autopilot]
  agents_agent_tele_cmd --> agents_agent_feeder[agents.agent_feeder]
  agents_agent_tele_cmd --> agents_agent_hongguo[agents.agent_hongguo]
  agents_agent_tele_cmd --> agents_agent_watch[agents.agent_watch]
  agents_agent_tele_cmd --> agents_auto_publisher[agents.auto_publisher]
  agents_agent_tele_cmd --> agents_canva_client[agents.canva_client]
  agents_agent_tele_cmd --> agents_films_merge_api[agents.films_merge_api]
  agents_agent_tele_cmd --> agents_hongguo_bridge[agents.hongguo_bridge]
  agents_agent_tele_cmd --> agents_meta_studio[agents.meta_studio]
  agents_agent_tele_cmd --> agents_test_channel[agents.test_channel]
  agents_agent_tele_cmd --> agents_uploader_settings_api[agents.uploader_settings_api]
  agents_agent_tele_cmd --> core_batch_config[core.batch_config]
  agents_agent_tele_cmd --> core_film_db[core.film_db]
  agents_agent_tele_cmd --> engines_check_block[engines.check_block]
  agents_agent_tele_cmd --> engines_lib_normalize[engines.lib_normalize]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| **class `CtrlHandler`** | 991 | 8 method | |  |
| **class `_ExclusiveHTTPServer`** | 2395 | 1 method | | Windows: SO_REUSEADDR (mặc định của HTTPServer) cho bản thứ 2 bind trùng cổng. |
| `_load_history_from_disk` | 88 | 10 | `` |  |
| `_save_history_to_disk` | 100 | 11 | `` |  |
| `get_user_history` | 116 | 9 | `uid` |  |
| `add_user_history` | 127 | 11 | `uid, role, content` |  |
| `clear_user_history` | 140 | 5 | `uid` |  |
| `_ensure_agent_telegram` | 147 | 4 | `` |  |
| `tg_send` | 153 | 3 | `text, force` |  |
| `tg_api` | 158 | 13 | `method, payload` |  |
| `allowed_uids` | 173 | 3 | `` |  |
| `tg_send_video` | 178 | 19 | `chat_id, path, caption, buttons, meta` |  |
| `send_preview` | 202 | 42 | `uid, ref, ep` | Gửi tập xem thử (miễn phí) vào chat: video + nút chuyển tập + nút làm A-Z. |
| `send_covers` | 246 | 37 | `uid, page` | Album ảnh bìa (tối đa 10) của trang Leaderboard/Catalog đang xem — giống lưới poster của app. |
| `_edit_or_send` | 285 | 10 | `uid, cq, text, buttons` |  |
| `spawn_preview` | 297 | 2 | `uid, ref, ep` |  |
| `_parse_catalog_args` | 306 | 25 | `text` | '/hg catalog Urban popular completed' → genre / sort / status; phần còn lại = từ khoá. |
| `hg_tele_command` | 333 | 223 ⚠️ | `raw, uid` |  |
| `_send_confirm_buttons` | 558 | 12 | `uid, confirms` |  |
| `_agent_ask` | 572 | 13 | `msg, uid` | Chat agent; có uid (Telegram) thì tool phá huỷ đỗ lại và gửi nút ✅/❌. |
| `_qa_post` | 591 | 7 | `body` |  |
| `_qa_strip_buttons` | 600 | 5 | `d` | Hết câu chờ → gỡ nút trên mọi tin hỏi của job (tránh bấm lại). |
| `_qa_show` | 607 | 18 | `uid, ref` | /qa <job>: hiện lại câu bị cờ + đề xuất + 3 nút (có thể mất ~1–2' nếu phải nhờ LLM đề xuất). |
| `_qa_callback` | 627 | 11 | `uid, cq, data` |  |
| `_qa_reply` | 640 | 22 | `uid, msg, text` | Reply vào tin HOLD QA → gửi câu VI mới. True = đã xử lý (không đưa sang agent chat). |
| `_confirm_callback` | 664 | 12 | `uid, cq, data` |  |
| `_slash_hint` | 686 | 32 | `text` | Chữ thường (không '/') mà đổi trạng thái → ("hint", gợi ý) nếu ngắn kiểu lệnh hoặc có tiền tố |
| `handle_command` | 720 | 219 ⚠️ | `text, uid` |  |
| `_agent_reply` | 941 | 10 | `msg, uid` |  |
| `_fetch_poster_bytes` | 953 | 33 | `name` |  |
| `autopilot_loop` | 2041 | 21 | `stop` |  |
| `filmdb_loop` | 2067 | 17 | `stop` |  |
| `runwatch_loop` | 2132 | 10 | `stop` | Luôn theo dõi job chạy + báo xong/treo; chỉ tự xử lý treo khi Auto-pilot ON. |
| `feeder_loop` | 2144 | 13 | `stop` |  |
| `_sync_and_report` | 2162 | 10 | `reason` |  |
| `config_watch_loop` | 2174 | 15 | `stop` |  |
| `_inline_kb` | 2191 | 3 | `rows` |  |
| `_on_callback` | 2196 | 96 | `cq, allow` |  |
| `telegram_loop` | 2294 | 49 | `stop` |  |
| `is_priority_cmd` | 2349 | 4 | `text` | Lệnh chạy ngay trên luồng poll, không xếp sau lượt agent đang nghĩ (tới 180s). |
| `_tg_worker` | 2355 | 10 | `stop` |  |
| `_handle_tg_text` | 2367 | 26 | `uid, text` |  |
| `_single_instance_lock` | 2405 | 14 | `` | Khoá 1 bản / cổng; trả file handle (giữ sống tới khi thoát) hoặc None nếu đã có bản khác. |
| `main` | 2421 | 45 | `` |  |

**Hàm dài ≥120 dòng:** `CtrlHandler.do_POST` (619, L1420), `CtrlHandler.do_GET` (371, L1048), `hg_tele_command` (223, L333), `handle_command` (219, L720)

### Config / env keys (11)

`AGENT_TELEGRAM`, `AUTOPILOT_HOST`, `AUTOPILOT_PORT`, `AUTOPILOT_TICK_SEC`, `FILMDB_SEC`, `PINELINE_BASE`, `QUEUE_LIVE_CONFIG`, `RUNWATCH_SEC`, `TELEGRAM_POLL_SEC`, `TEMP`, `TMP`

**Cổng nhắc tới:** 8000, 8801, 8802

**File/artifact nhắc tới:** `tele_chat_history.json`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=61 · file_writes=3 · global_stmt=3 · sleep=3 · subprocess=1 · swallow_except=10 · threads=12

### Lịch sử (từ docs/)

- **Fix logs (15):**
  - [Port V2→V5: Brain — job đã xong không heal + park tự động ≠ HOLD cần người](../../fixes/2026-11-13-port-brain-finished-hold.md)
  - [Port V2→V5: Second Brain (Telegram events + gỡ HOLD khi chạy tay) + đóng dấu luồng dịch theo job](../../fixes/2026-11-12-port-brain-hold-pipeline.md)
  - [REVIEW lỗi bị coi là đã soát · park treo hàng đợi · Brain V4 điều khiển nhầm V2](../../fixes/2026-11-11-review-fail-park-port.md)
  - [Meta tạo ảnh không work sau khi chuyển GPT local :3377](../../fixes/2026-11-09-meta-ai-image-3377.md)
  - [Helper Pineline leak / lệch WinUI (spawn riêng)](../../fixes/2026-11-08-helper-singleton-winui-parity.md)
  - [Settings + Uploader API 404 trên :8802; thiếu skip upload](../../fixes/2026-11-07-uploader-settings-8802.md)
  - [Films UI :8802 — onclick/`jq` chết + Settings/Uploader 404](../../fixes/2026-11-07-films-ui-syntax.md)
  - [Films UI thiếu nút gộp job đã làm (combine)](../../fixes/2026-11-07-films-combine-ui.md)
  - [Gộp job đã làm nối sai thứ tự Phần](../../fixes/2026-11-07-combine-part-order.md)
  - [Tìm mùa mới vẫn kéo download / mất base sau xoá Lib](../../fixes/2026-11-06-hg-watchlist-discover.md)
  - [Films UI: Studio lỗi + SyntaxError Test + poster 404 + toolbar rối](../../fixes/2026-11-06-films-ui-studio-test.md)
  - [Phim đã xoá thư mục vẫn tồn đọng trong films/ui và thiếu chức năng xoá phim](../../fixes/2026-10-09-films-ui-delete-missing.md)
  - [2026-10-06 — Đợt 5 review: agent an toàn hơn](../../fixes/2026-10-06-batch5-agent-safety.md)
  - [2026-10-06 — Đợt 4 review: tranh chấp ghi, một bản tiến trình, checkpoint an toàn](../../fixes/2026-10-06-batch4-write-races.md)
  - [2026-10-06 — Đợt 2 review: bảo mật + config một nguồn + LLM sập không để trống câu](../../fixes/2026-10-06-batch2-security.md)
- **Reviews:** [_atoms_http_agents](../../reviews/_atoms_http_agents.md), [2026-11-11-v4-v5-port-review](../../reviews/2026-11-11-v4-v5-port-review.md), [2026-11-07-films-ui-swarm](../../reviews/2026-11-07-films-ui-swarm.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md), [2026-11-02-v4-structure-sync](../../reviews/2026-11-02-v4-structure-sync.md), [2026-11-02-v4-structure-and-v2-port](../../reviews/2026-11-02-v4-structure-and-v2-port.md), [2026-10-06-code-review](../../reviews/2026-10-06-code-review.md)
- Nhắc trong CHANGELOG: **11** lần · DECISIONS: **1** lần

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
