# Studio SOP: 1 job / ghế — ASR→NMT→Aurora∥ REVIEW→TTS→mux→Done→next

- **Date:** 2026-11-11
- **Job / khu vực:** `server._auto_gpu` · `translate.run_review` · `job_queue` park
- **Status:** fixed
- **Backup:** codebak `Z:\PinelineV2_codebak\2026-11-11_studio-1job-pipeline\` (+ zip park `…_2357.zip` đêm 10/11)

## Triệu chứng

Vận hành lệch: soát CLI ngoài hàng / `_auto_gpu` return sớm khi còn `rv` → worker lấy job khác trong khi job cũ chưa TTS/mux.

## Root cause

Studio cần **một ghế** chạy trọn pipeline; review phải là stage **trong** `_auto_gpu`/`run_translate`, không phải tiến trình ngoài queue. `aurora_parallel` trước chỉ đổi model, chưa fan-out; unrev>0 → return (dù đã park).

## Evidence

- User SOP: ASR → NMT → Aurora∥ (fallback local) → TTS → mux → Done → next.
- Bench fan-out ~6.8× (`docs/reviews/2026-11-10-review-parallel-aurora.md`) chưa vào production.

## Fix

- `_auto_gpu`: còn câu chưa `rv` → **gọi `run_review` trong ghế**; chỉ PARK nếu sau REVIEW vẫn dở / HOLD.
- `translate.run_review`: `REVIEW_BACKUP=aurora_parallel` / `REVIEW_PARALLEL` → ThreadPool fan-out lô; cloud lỗi → fallback local (`REVIEW_PRESET`).
- Config: `REVIEW_PARALLEL=6`. Queue park (10/11) giữ ghế khi HOLD.
- Sync V2/V4/V5.

## Recheck

1. Xếp 1 job queue, `review_backup=aurora_parallel` → log `[review] Aurora∥ fan-out workers=…`; không có job 2 `current` khi job 1 còn translate/tts.
2. Cắt Aurora (timeout) → log Fallback local; vẫn cùng job → TTS.
3. `pytest tests/test_review_parallel_workers.py tests/test_job_queue_worker.py`
4. **Pass nếu:** 1 job tới `output.mp4` rồi mới job kế; parallel chỉ chia lô REVIEW.
5. **Fail nếu:** CLI/out-of-band review + queue cùng lúc, hoặc held vẫn nhảy job kế.

## Liên quan

- DECISIONS 11-11 Studio SOP · park `2026-11-10-queue-park-held.md`
- Keys: `REVIEW_BACKUP`, `REVIEW_PARALLEL`, `AURORA_REVIEW_MODEL`, `REVIEW_PRESET`
