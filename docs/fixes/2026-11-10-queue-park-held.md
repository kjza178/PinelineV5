# Queue nhảy job khi còn HOLD/soát dở — mất invariant studio 1 job→output

- **Date:** 2026-11-10
- **Job / khu vực:** `job_queue._worker_loop` · `_auto_gpu` · `_queue_run_one` · `60892cc63cb7_p01` / `365baf19df54`
- **Status:** fixed
- **Backup:** zip `Z:\PinelineV2_backup_2026-11-10_2357.zip` · codebak `Z:\PinelineV2_codebak\2026-11-10_queue-park-held\`

## Triệu chứng

Studio trước đây: 1 job xử lý tới `output.mp4` rồi mới job kế. Sau Brain/review: `_auto_gpu` dừng sớm (soát dở / HOLD QA) nhưng worker coi lượt xong → lấy job khác (vd `365baf` dịch) trong khi `60892_p01` đã dịch xong, TTS pending, không báo lỗi.

## Root cause

1. `_auto_gpu` `return` sớm khi còn câu chưa `rv` / HOLD / QA block — **không giữ ghế** hàng đợi.
2. `_queue_run_one` trả `"held"` (hoặc trước đó fail «output chưa hoàn chỉnh») → `_worker_loop` set `_current=None` và `pop` job kế.
3. Soát CLI ngoài queue không chiếm `_current` → ghế trống → job mới vào trong khi job cũ còn thiếu TTS/mux.
4. Brain quan sát `pre_tts` nhưng không phải hàng đợi — không chặn jump.

## Evidence

- Queue live: `current=365baf19df54` (translate) trong khi `60892cc63cb7_p01`: translate=done, tts=pending, unrev=0.
- Code: `job_queue._worker_loop` luôn nhả `_current` sau mọi status trừ khi park.
- `_auto_gpu` stamp «soát dở» rồi `return` không set `held_at` (trước fix) → dễ thành fail generic.

## Fix

- `job_queue.py`: status `held`/`parked`/`waiting_review` → **đưa job lại đầu `_q`**, giữ `_current`, poll `_park_ready` — **không** lấy job kế đến khi sẵn sàng / stop / remove.
- `server.py` `_auto_gpu`: stamp `held_at=waiting_review` khi còn unrev; clear khi unrev=0; QA gate fail → stamp HOLD; wire `set_park_ready_hook`.
- `_queue_run_one`: soft return `"held"` khi HOLD/soát (không fail nhảy job).
- Test: `tests/test_job_queue_worker.py::test_worker_parks_held_job_before_next`.
- Sync V2/V4/V5 (`job_queue` + `server`; V5 thêm `core/job_queue.py`).

## Recheck

1. Xếp 2 job; job1 dừng soát dở / HOLD → queue `current` vẫn job1, job2 còn trong `queue` (không thành current).
2. Soát xong unrev=0 (hoặc resume clear HOLD) → cùng job1 chạy TTS→mux rồi mới job2.
3. `pytest tests/test_job_queue_worker.py` → pass (gồm park).
4. **Pass nếu:** không còn nhảy job kế khi status held/waiting_review.
5. **Fail nếu:** sau held, `current` đổi sang job khác trước khi job1 `output.mp4` / remove / stop.

## Liên quan

- Invariant studio: 1 job → output → job tiếp (`docs/ARCHITECTURE.md`).
- Resume: `routes_agent._agent_resume` (clear HOLD + queue_front) — tương thích park_ready.
- Cần **restart :8801** để nạp worker mới (đang chạy `365baf` sẽ bị cắt nếu restart ngay).
