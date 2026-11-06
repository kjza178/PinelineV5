# Settings + Uploader API 404 trên :8802; thiếu skip upload

- **Date:** 2026-11-07
- **Job / khu vực:** sidecar `agent_tele_cmd.py` :8802 · Films UI Upload/Settings · `Z:\yt_uploader`
- **Status:** fixed

## Triệu chứng

Films UI (`/films/ui`) gọi `/api/settings` và `/api/uploader/*` → 404 trên sidecar :8802. Không skip được video đang upload từ UI.

## Root cause

Sidecar `agent_tele_cmd` không có handler Settings/Uploader (chỉ có trên FastAPI `routes_uploader_settings`). `yt_uploader` cũng chưa đọc tín hiệu skip từ ngoài.

## Evidence

- Trước: GET `:8802/api/settings` / `/api/uploader/status` → 404 (toast Films UI).
- Sau restart sidecar PID 16628: cả hai → 200 `ok=true`.

## Fix

- Thêm `uploader_settings_api.py` (stdlib dict API) + wire `dispatch` vào `agent_tele_cmd` GET/POST.
- Endpoints mới: `/api/uploader/skip`, `/skip-current`, `/clear-skipped`, `/move`, `/settings`.
- Films UI: nút Skip đang upload, skip từng mục, ↑↓, priority enqueue, auto-launch, dọn skipped; map status VN (`chờ`/`đang upload`/`bỏ qua`).
- `yt_uploader.py`: `skip_current.flag` + `apply_external_skips()` trong vòng upload.
- Sync V4/V5; V5 FastAPI bridge các endpoint skip.
- Backup: `Z:\PinelineV2_backup_2026-11-07_0034.zip` · `Z:\PinelineV2_codebak\2026-11-07_uploader-settings-8802\`

## Recheck

1. Hard refresh `http://127.0.0.1:8802/films/ui` → tab Upload / Settings.
2. `curl http://127.0.0.1:8802/api/settings` và `/api/uploader/status` → `ok:true`.
3. Khi có item đang upload: bấm **⏭ Skip đang upload** → queue status `bỏ qua`, yt_uploader log skip, chuyển mục kế.
4. **Pass nếu:** Settings mở/lưu được; queue hiện status đúng; skip-current tạo/clear `Z:\yt_uploader\skip_current.flag`.
5. **Fail nếu:** vẫn 404; hoặc skip không đổi status / uploader không dừng item.

## Liên quan

- Sidecar restarted :8802 (PID 16628). Không restart :8801.
- Keys: `YT_UPLOADER_DIR`, `skip_current.flag`, `queue_state.json`
