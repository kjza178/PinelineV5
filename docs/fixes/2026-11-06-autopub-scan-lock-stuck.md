# Auto-publish banner stuck 41% sau restart sidecar

- **Date:** 2026-11-06
- **Job / khu vực:** `auto_publisher` · `:8802` · job `4041cc3bb069_p01`
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-06_autopub-stuck\`

## Triệu chứng

UI «🚀 ĐANG TỰ ĐỘNG XUẤT BẢN YOUTUBE» kẹt ~41% (`uploading`) hàng giờ; hàng chờ không chạy tiếp.

## Root cause

1. Sidecar restart (~19:14) giết PID upload **5360** giữa chừng.
2. Còn file lock: `.auto_publish_scan.lock` / global / `.upload.lock` của PID chết.
3. `file_lock(SCAN_LOCK_FILE, stale_sec=14400)` chỉ xem mtime, **không** check PID chết → scan Timeout → luôn trả `busy` “tiến trình khác” tới 4 giờ.
4. `auto_publish_state.json` giữ `current_stage=uploading` → banner giả.

## Evidence

- State mtime 17:38, progress 41%, PID 5360 không sống.
- `POST /api/auto-publish/scan` → `busy` + message «Tiến trình quét đang được xử lý ở tiến trình khác».
- `is_any_job_uploading()` = False (PID chết) nhưng scan vẫn kẹt vì scan lock.

## Fix

- Gỡ lock chết + reset state → `idle`; giữ queue 4 job.
- `auto_publisher`: scan `stale_sec` 14400 → **180**.
- `fileio.file_lock`: nếu nội dung có PID và PID chết → xoá lock (không chờ stale).
- Worker sidecar (PID 11756) đã resume `4041cc3bb069_p01` (stage metadata).

## Recheck

1. `GET :8802/api/auto-publish/state` — `current_stage` đổi metadata→thumbnail→uploading; `%` tăng; hoặc xong có `yt_url`.
2. `POST /api/auto-publish/scan` khi idle không còn message «tiến trình khác» vì lock chết.
3. **Pass nếu:** progress tăng hoặc job có `yt_url`; queue giảm.
4. **Fail nếu:** stage uploading đứng im >15 phút + PID lock chết.

## Liên quan

- Job ~3.7 GB `4041cc3bb069_p01`; queue: `_p02`, `4041cc3bb069`, `d01dbbc2d703`.
