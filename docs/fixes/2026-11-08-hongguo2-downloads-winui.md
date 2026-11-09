# Hongguo2 Downloads lệch WinUI (list thô, thiếu tab/Open folder)

- **Date:** 2026-11-08
- **Job / khu vực:** `/hongguo2` Downloads
- **Status:** fixed

## Triệu chứng

Downloads chỉ hiện progress text; không có All/Active/Done/Failed, poster, quality badge, dòng Done xanh, Open folder / ×, Clear finished, speed.

## Root cause

UI tự chế từ `/api/hg/status` rút gọn; chưa map `downloads.snapshot` fields (`cover/quality/folder/bytes/state`) và RPC `clearFinished` / `remove`.

## Evidence

- Screenshot WinUI Downloads: tabs + row thumb + `Done · N episodes · …` + Open folder.
- Snapshot job keys: `seriesId,title,cover,quality,state,episodes,done,failed,progress,bytes,bytesPerSecond,folder`.

## Fix

- `hongguo_rpc.status` normalize + counts/speed; `clear_finished` / `remove_download` / `retry_download`
- Bridge `open_folder` (Explorer)
- Routes `/api/hg/downloads/*`
- UI WinUI-like list + poll

Backup: `Z:\PinelineV2_codebak\2026-11-08_downloads-winui\`

## Recheck

1. Hard refresh `/hongguo2` **và** `/static/ui/hongguo2.html` → tab Downloads.
2. Thấy meta `x.x MB/s` · `N active` · Clear finished; chips All/Active/Done/Failed.
3. Mỗi job: poster + title + quality pill + status xanh + Open folder + ×.
4. **Pass nếu:** layout khớp screenshot WinUI (không còn list `%` đơn giản).
5. **Fail nếu:** vẫn “Hongguo helper queue” / Cancel all cũ.

## Liên quan

- Chưa audit sâu Library/Link/Settings so với WinUI — làm tiếp khi có screenshot.

## Follow-up — Downloads sai tên

- **Date:** 2026-11-08
- **Triệu chứng:** List Downloads hiện sai tên / rỗng (snapshot `title=""` → UI fallback seriesId).
- **Root cause:** `downloads.snapshot` không điền title; normalize bỏ qua folder basename.
- **Fix:** `_normalize_dl_job` lấy tên từ folder (+ `series.detail` nếu thiếu); UI ưu tiên folder name. Cover enrich kèm.
- **Recheck:** `/api/hg/status` → `title` = basename folder; hard refresh Downloads khớp `D:\Lib\…`.
- Backup: `Z:\PinelineV2_codebak\2026-11-08_dl-title-folder\`
