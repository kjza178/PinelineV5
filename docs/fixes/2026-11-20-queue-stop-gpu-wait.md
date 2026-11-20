# Queue Stop treo ghế khi job xếp sau TTS trên `_gpu`

- **Date:** 2026-11-20
- **Job / khu vực:** `d386ff2fbe96` ghost `queue.current` trong khi `72450cea31aa_p01` TTS out-of-band; `server._queue_run_one` + `_gpu`
- **Status:** fixed (code trên đĩa; **cần restart :8801** mới có hiệu lực)
- **Backup:** `Z:\PinelineV2_backup_2026-11-20_0235.zip` (server.py + job_queue.py) · codebak `Z:\PinelineV2_codebak\2026-11-20_queue-stop-gpu-wait\server.py`

## Triệu chứng

Stop / `queue_stop` job đang `current` nhưng stage null, không tiến ASR — ghế không nhường job kế. TTS job khác vẫn chạy trên `_gpu`.

## Root cause

`_queue_run_one` làm `_gpu.submit(_gpu_job)` rồi `done_event.wait()` **vô hạn**. Với `JOB_WORKERS=1`, nếu TTS/ASR job khác đang giữ executor, future của job ghế chỉ xếp hàng. Stop ghi `_STOP_JOBS` / `.stop` nhưng `_gpu_job` chưa chạy → `done_event` không set → worker giữ `_current` mãi.

## Evidence

- `GET /api/queue/jobs` → `current=d386ff2fbe96`, `stage=null`, asr vẫn `pending`
- `72450cea31aa_p01` TTS `running`, wav tăng; remove/`queue_stop` không đổi `current` đến khi nhả `_gpu`
- Sau stop p01 (nhả GPU) → future d386 chạy → thấy stop → `current` về `None` (~28 s)

## Fix

- `server._queue_run_one`: poll `done_event.wait(1s)`; nếu job trong `_STOP_JOBS` và `fut.cancel()` được (chưa chạy) → `_release_stage(__all__)` + heal + return `"stopped"`
- Future đã chạy: chờ `_gpu_job` thoát như cũ (stop_hook kill subprocess)
- Test `tests/test_queue_run_one.py::test_stop_cancels_pending_gpu_future`

## Recheck

1. (Sau restart :8801, queue rảnh) xếp job A ASR; riêng POST TTS job B (giữ `_gpu`); A thành `current` stage null.
2. `POST /api/jobs/{A}/stop` (hoặc queue stop).
3. Trong ≤ vài giây: `current` ≠ A (hoặc None / job kế); A không còn claim `__all__`.
4. **Pass nếu:** ghế nhường khi future A còn pending trên `_gpu`.
5. **Fail nếu:** `current` A treo > ~5 s sau stop trong khi B vẫn TTS.

## Liên quan

- Studio SOP 1 ghế; tránh POST TTS out-of-band khi queue đã có `current` khác
- Job live lúc vá: `72450cea31aa_p01` TTS tiếp (~15%+); queue để trống đến khi p01 xong rồi xếp parent merge
