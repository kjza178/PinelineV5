# Films UI Test Block báo hết quota dù GCP còn hạn

- **Date:** 2026-11-09
- **Job / khu vực:** `test_channel.py` + `films_ui.html` (Kênh Test / Test Block)
- **Status:** fixed
- **Backup zip:** `Z:\PinelineV2_backup_2026-11-09_0521.zip`
- **Codebak:** `Z:\PinelineV2_codebak\2026-11-09_tc-quota-stale\`

## Triệu chứng

Films UI (`:8802/films`) hiện `0/3 Proj` + «Hết quota hôm nay (429)» trong khi Console GCP vẫn còn quota.

## Root cause

1. `exhausted.json` gắn cả 3 project ngày `"2026-11-08"` (cờ **local**, không phải số liệu GCP).
2. So sánh ngày bằng `_today_utc()` — lúc VN đã 9/11 sáng, UTC vẫn 8/11 → cờ còn «hôm nay».
3. Upload mark quá rộng: `"quota" in err` / `"429" in err` → false positive; sau đó UI tin cờ local.

## Evidence

- Trước: `exhausted.json` = proj_1/2/3 → `2026-11-08`; status `available_projects=0`.
- `today_uploads` VN=0 / UTC=10 — không chứng minh hết API quota.
- Sau purge + classify chặt: `available=3/3`, file `{}`.

## Fix

- Ngày cờ theo **Pacific** (`_quota_day`) — khớp reset YouTube API.
- `_classify_yt_block_error`: chỉ `quotaExceeded` / `dailyLimitExceeded` / `uploadLimitExceeded` / `rateLimitExceeded` (bỏ khớp mơ hồ).
- `exhausted.json` structured `{day, reason, at}`; legacy string → **auto purge**; `rate_limit` TTL 30 phút.
- UI hiện lý do: quota API / upload limit / rate limit tạm.
- Sync V2/V4/V5. Sidecar reload `test_channel` mỗi request — **không bắt buộc restart :8802**.

## Recheck

1. `Get-Content Z:\PinelineV2\data\test_channel\exhausted.json` → `{}` (hoặc chỉ entry structured ngày Pacific).
2. `Invoke-RestMethod http://127.0.0.1:8802/test-channel/status` → `available_projects` = số project connected+API.
3. Hard refresh Films UI → badge `3/3 Proj` (hoặc N/N), không còn «Hết quota» đỏ nếu GCP còn hạn.
4. **Pass nếu:** không báo hết quota khi Console còn hạn mức.
5. **Fail nếu:** lại `0/N` chỉ vì cờ local cũ / lỗi chứa chữ «quota» chung.

## Follow-up ~05:35 — Alert uploadLimitExceeded

User test lại → popup «Sai Kira hết lượt upload». YouTube trả `uploadLimitExceeded` trên pool auto-rotate. User Cloud **12/100** → cờ local lệch với hạn mức Console.

## Follow-up ~05:42 — Chọn account khi test

- Modal Test Block: dropdown **Account / Project**.
- `test-one` nhận `project_id` → upload exclusive 1 acc (xoá cờ local acc đó khi chọn tay).
- Xoá `exhausted.json` (lại `available=3`). Hard refresh Films UI.

## Liên quan

- `docs/fixes/2026-11-07-test-channel-exhausted-mask.md`
- Films UI trên `:8802` (API test-channel); `:8801/test-channel/*` vẫn 404
