# Task 4 report — UI chọn job + thanh queue

- **Status:** completed
- **Date:** 2026-09-24

## Files changed

- `index3.html`: thêm nút chạy/dừng queue vào `#qbar`, thu thập cấu hình run-all, enqueue/stop, hiển thị và poll trạng thái queue.
- `index.html`: mirror đầy đủ cùng hành vi vì file có sẵn `listSel`, `.jchk` và `#qbar`.

## Implementation notes

- Tái sử dụng `listSel` và checkbox `.jchk`; không thêm class checkbox thứ hai.
- `collectRunAllOpts()` đọc toàn bộ field run-all hiện có, gồm `auto-ovol` cho **Tiếng gốc nền**.
- `runJobQueue()` yêu cầu ít nhất một job, xác nhận trước khi chạy, yêu cầu voice trước khi POST `/api/queue/jobs`, và gửi `skip_done: true`.
- `stopJobQueue()` POST `/api/queue/jobs/stop`.
- `paintQueueStatus()` hiển thị job hiện tại/số job còn lại, bật poll 2 giây khi queue hoạt động và được gọi ở cuối `refresh()`.

## Verification

1. JavaScript inline của `index3.html` và `index.html` đã được compile bằng `node:vm`: pass.
2. IDE lint cho cả hai HTML: không có lỗi.
3. Grep bắt buộc trong `index3.html`: `runJobQueue` và `Chạy hàng chờ` đều tồn tại.
4. Browser: mở `/ui3`, chọn một job để hiện thanh 1-click và chọn giọng; tick ít nhất hai `.jchk`; bấm **▶ Chạy hàng chờ**, xác nhận, kiểm tra trạng thái `Queue: … · còn …`; bấm **⏹ Dừng hàng chờ** để dừng.

## Notes

- Không tạo git commit theo yêu cầu.
- Workspace hiện không có metadata Git, nên không thể chạy `git diff --check`; kiểm tra cú pháp và lint đều pass.
