# Auto-publish tiếp tục upload khi YouTube uploadLimitExceeded

- **Date:** 2026-11-05
- **Job / khu vực:** `agents/auto_publisher.py` — publish queue drain
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-05_upload-limit-stop\`

## Triệu chứng

Khi YouTube trả `uploadLimitExceeded`, auto-publish vẫn dequeue job lỗi và drain job tiếp theo → fail hàng loạt, queue trống dù chưa upload được.

## Root cause

`publish_job` `finally` luôn `_dequeue_job_record` + `_drain_publish_queue_async`. `_drain_publish_queue_loop` / `_publish_job_internal` không nhận diện hạn mức ngày → không `stop_queue`.

## Evidence

- HttpError mẫu: `reason: uploadLimitExceeded` / «exceeded the number of videos they may upload»
- V2 đã vá cùng logic; V5 thiếu port

## Fix

- Thêm `_is_yt_upload_limit_error`
- `_publish_job_internal` trả `upload_limit_exceeded` + `stop_queue` khi match
- `publish_job` finally: nếu `stop_queue` → không dequeue / không drain tiếp
- `_drain_publish_queue_loop`: break khi `res.stop_queue` hoặc exception limit

## Recheck

1. `cd Z:\PinelineV5 && python -m pytest tests/test_upload_limit_stop.py -q`
2. **Pass nếu:** 4 tests OK; helper nhận diện chuỗi HttpError limit, reject lỗi khác
3. **Fail nếu:** helper miss `uploadLimitExceeded` hoặc positive trên `quotaExceeded` readonly
4. Runtime (không restart lần này): khi gặp limit thật, log «DỪNG hàng đợi» / «Không dequeue», job còn trong `data/auto_publish_queue.json`

## Liên quan

- Port từ `Z:\PinelineV2\auto_publisher.py`
- Fix log V2: `docs/fixes/2026-11-05-upload-limit-stop-queue.md`
