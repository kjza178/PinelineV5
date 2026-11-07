# Hongguo 2.x JSON-RPC bridge → `/api/hg/*`

- **Date:** 2026-11-07
- **Status:** implementing
- **Backup:** `Z:\PinelineV2_backup_2026-11-07_2107.zip` + `Z:\PinelineV2_codebak\2026-11-07_hongguo-rpc\`

## Bối cảnh

Hongguo WinUI 2.x không mở HTTP `:8000`. Engine `helper.jar` nói **JSON-RPC 2.0 theo dòng (stdio)**. Bản 1.x vẫn có thể chiếm `:8000` nếu chạy.

## Thiết kế

1. **`agents/hongguo_rpc.py`** — client stdio:
   - Spawn `engine/runtime/bin/java.exe … com.hongguo.helper.MainKt` (cwd `…/HongguoWinUI/current/engine`)
   - Singleton process + lock; `app.shutdown` / terminate khi idle lâu hoặc atexit
   - `call(method, params) → result`; notifications (`library.changed`, …) giữ bản mới nhất

2. **Adapter shape cũ** (để UI/feeder không đổi):
   - `search.page` cards → `results[]` với `series_id/title/cover/episode_cnt/…`
   - `rank.page` cards → `results[]` tương tự
   - `library.get` entries → `items[]` (`series_id`, `name`, `title`, `local/total/new`, …)
   - `downloads.snapshot` → gần `/dl/status`
   - `downloads.add` / `library.downloadNewSeasons` — cần license proof; trả lỗi rõ `need_license`

3. **`hongguo_bridge` backend:**
   - `HG_BACKEND=rpc|http|auto` (config/env, mặc định **`auto`**)
   - `auto`: ưu tiên RPC 2.x; nếu spawn fail → HTTP 1.x `:8000`
   - Merge queue Pineline giữ nguyên (không qua RPC)

4. **Routes `/api/hg/*`:** không đổi path; reload bridge như hiện tại.

## Ngoài phạm vi (phase sau)

- UI skin 2.x (`hongguo2.html`)
- `license.restore` từ `license.dat` (download New seasons / add)
- Playback / `:33080` local-play
