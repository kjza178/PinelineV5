# `/library/action` crash — gọi API film_db không tồn tại

- **Date:** 2026-11-02
- **Job / khu vực:** `routes_films.py` · library UI
- **Status:** fixed

## Triệu chứng

Skip / ưu tiên / enqueue từ `/films/ui` (hoặc `/library/action`) lỗi AttributeError vì `film_db.mark_library_*` / `enqueue_library_item` không có trong codebase.

## Root cause

Port V4 thêm `routes_films` giả định API `film_db` chưa từng implement. Skip/priority thật sự sống trong `agent_feeder.library_action` (state feeder).

## Evidence

- Grep: `mark_library` chỉ xuất hiện trong `routes_films.py`, không có `def` ở `film_db.py` (V2 lẫn V4 cũ).
- `agent_feeder.library_action` đã hỗ trợ `priority|unpriority|skip|unskip|add|merge|…`.

## Fix

- `routes_films.library_action` ủy thác `agent_feeder.library_action(base, action, names=…, cores=…)`.
- Alias `enqueue` → `add`.

## Recheck

1. Start V4 (`run_v4.bat` mode web hoặc desktop).
2. `POST /library/action` body `{"action":"skip","name":"<core_or_folder>"}` → `{"ok":true,…}` không 500.
3. `POST` `{"action":"priority","cores":["…"]}` tương tự.
4. **Pass nếu:** HTTP 200 + state feeder cập nhật (`work/logs` / autopilot feeder state).
5. **Fail nếu:** AttributeError `mark_library_*` hoặc 500.

## Liên quan

- Review: `docs/reviews/2026-11-02-v4-structure-and-v2-port.md`
- Backup: `Z:\PinelineV2_codebak\2026-11-02_v4-port-v2\`
