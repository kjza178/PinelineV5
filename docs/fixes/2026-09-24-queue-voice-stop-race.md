# Queue dùng sai giọng hoặc bỏ qua lệnh dừng

- **Date:** 2026-09-24
- **Job / khu vực:** Queue worker, `_queue_run_one`, `job_queue._worker_loop`
- **Status:** fixed

## Triệu chứng

Job queue chưa chọn giọng vẫn có thể chạy bằng giọng clone đầu tiên toàn cục.
Lệnh dừng gửi lúc runner đang preflight cũng có thể bị xóa và job tiếp tục chạy.

## Root cause

`server._queue_run_one` dùng `_resolve_voice`, hàm có fallback sang
`list_clone_voices()[0]`. Cùng runner đó gọi `_clear_stop(job_id)` sau khi worker
đã công bố job là `_current` và sau claim, nên có thể xóa stop mới từ
`queue_stop()` trong cửa sổ race.

## Evidence

- Review: `docs/superpowers/sdd/reports/task-2-review.md`.
- RED test: `tests/test_queue_run_one.py` có 2 fail, 1 pass trước fix:
  missing voice trả `done` và stop-after-claim trả `failed` thay vì `stopped`.
- Stop test xác nhận stop flag từng bị xóa sau claim.

## Fix

- `server.py`: thêm resolver riêng cho queue, không fallback giọng toàn cục;
  bỏ clear-stop sau claim; trả `stopped` khi download lỗi trong lúc đã dừng.
- `job_queue.py`: thêm clear-stop hook chạy lúc pop, trước khi đặt `_current`.
- `tests/test_queue_run_one.py`, `tests/test_job_queue_worker.py`: khóa các hành
  vi missing voice, stop race, done fast-path và thứ tự clear hook.

## Recheck

1. Chạy queue runner test với job không có voice, stop được đặt ngay sau claim,
   và job đã hoàn tất.
2. Lệnh kiểm tra:
   `python -m pytest tests/test_queue_run_one.py tests/test_job_queue_worker.py tests/test_job_queue.py -q`
3. **Pass nếu:** 9 test pass; missing voice trả `failed`; stop-after-claim trả
   `stopped` và flag còn hiệu lực; done fast-path không claim GPU.
4. **Fail nếu:** bất kỳ test nào fail, runner claim job thiếu voice, stop flag bị
   xóa sau claim, hoặc job done vẫn claim GPU.

## Liên quan

- Task 2 report: `docs/superpowers/sdd/reports/task-2-report.md`
- Không có job id production hoặc commit.

## Follow-up — Stop rồi enqueue bị kẹt và lỗi queue không hiện nguyên nhân

- **Date:** 2026-09-24
- **Job / khu vực:** `job_queue.py`, `_queue_run_one`, queue status UI
- **Status:** fixed

### Triệu chứng

Enqueue ngay sau Stop có thể nhận job nhưng không chạy. Duplicate enqueue có
thể đổi giọng của queue cũ; lỗi runner không có chi tiết, có thể để stage ở
`running`; lịch sử lỗi không hiện trên UI; file queue có thể hỏng nếu tiến trình
dừng giữa lúc ghi.

### Root cause

`queue_add` không hủy `_stop`, còn `_ensure_worker_unlocked` chỉ kiểm tra
`Thread.is_alive()` dù worker có thể đã quyết định thoát. `_opts` được ghi trước
dedupe; runner chỉ trả status; các early return sau `mark_running` không finalize
stage; UI bỏ qua `history`; `_save` ghi đè trực tiếp file đích.

### Evidence

- Review và repro: `docs/superpowers/sdd/reports/whole-branch-review.md`.
- Trước fix: Stop → enqueue để `queue=['new']`, `worker=false`; duplicate đổi
  voice dù không append; runner failure có `detail=""`.

### Fix

- `job_queue.py`: enqueue mới hủy stop; worker xóa thread reference dưới lock;
  chỉ cập nhật options khi có ID mới; history nhận tuple status/detail; persist
  bằng temp + flush/fsync + `os.replace`.
- `server.py`: runner trả `(status, detail)` và finalize/heal manifest khi lỗi.
- `index3.html`, `index.html`: hiện tối đa ba history entries gần nhất.
- Thêm regression tests cho race, dedupe/options, failure paths và atomic save.

### Recheck

1. Chạy Stop khi fake runner đang giữ job, enqueue job mới ngay lập tức rồi thả
   runner; enqueue duplicate với voice khác; chạy các failure-path runner tests.
2. Lệnh:
   `python -m pytest tests/test_job_queue.py tests/test_job_queue_worker.py tests/test_queue_run_one.py tests/test_queue_jobs_api.py -q`
3. **Pass nếu:** 19 test pass; job mới chạy; duplicate trả `queued=[]` và giữ
   voice cũ; stage lỗi không còn `running`; history có detail; JSON đọc hợp lệ
   và replace nhận source `._job_queue.json.tmp`.
4. **Fail nếu:** job mới bị kẹt, options đổi bởi duplicate, history trống,
   manifest còn `running`, file JSON lỗi, hoặc bất kỳ test nào fail.

### Liên quan

- Final review: `docs/superpowers/sdd/reports/whole-branch-review.md`
- Không có job id production hoặc commit.
