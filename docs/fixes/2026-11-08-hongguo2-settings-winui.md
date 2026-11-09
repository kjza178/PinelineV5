# Settings hongguo2 lệch WinUI + toast «Cần license»

- **Date:** 2026-11-08
- **Job / khu vực:** `/hongguo2` Settings · license prove
- **Status:** fixed

## Triệu chứng

Download báo «Cần license — mở Settings»; Settings Pineline chỉ form key (không giống WinUI Downloads/Output). WinUI Settings không có ô license trên màn hình đó. Sau restart helper, `has_key=true` nhưng `licensed=false` tới khi prove.

## Root cause

1. UI Settings chưa map `settings.get` / `settings.update` (saveFolder, quality, at-once, merge…).
2. Gate download chỉ check `licensed` — không auto-prove key DPAPI vào helper mới spawn.
3. License Pineline (DPAPI + prove) là lớp riêng; WinUI giữ license trong app — cần block License phụ dưới Settings.

## Evidence

- Screenshot WinUI Settings = Downloads + Output.
- `GET /api/hg/license/status` sau restart: `has_key=true`, `licensed=false`.
- `POST …/license/prove` → `state=licensed`.

## Fix

- `hongguo2.html`: Settings rows WinUI + License block; wire patch UI; mở Settings / download → auto prove nếu có key.
- `hongguo_rpc.settings_update`, `hongguo_bridge.settings_update`, `POST /api/hg/settings`.
- Backup: `Z:\PinelineV2_backup_2026-11-08_0435.zip`, `Z:\PinelineV2_codebak\2026-11-08_settings-winui\`.

## Recheck

1. Hard refresh `/hongguo2` → Settings: Save to / Quality / At once / Connections / File names / 4 toggles.
2. Đổi quality → `GET /api/hg/settings` phản ánh.
3. Restart :8801 → mở Settings (hoặc Download) → auto prove → pill «Yearly Unlimited».
4. **Pass nếu:** Settings khớp WinUI; download không toast license khi đã có key.
5. **Fail nếu:** Settings vẫn chỉ form key; hoặc `licensed=false` dù prove OK.

## Liên quan

- Helper singleton cùng ngày; license API `/api/hg/license/*`.

## Follow-up — Change folder không chọn được

- **Date:** 2026-11-08
- **Triệu chứng:** Nút Change Save to không đổi folder (prompt trình duyệt bị chặn / không phải dialog WinUI).
- **Fix:** `btnChangeFolder` → `POST /api/fs/pick-dir` (tkinter native trên máy server) rồi `settings.update` `saveFolder`.
- **Recheck:** Hard refresh → Settings → Change → chọn folder Windows → path cập nhật trên UI + `GET /api/hg/settings`.
