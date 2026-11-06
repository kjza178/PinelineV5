# Hàng chờ: sort/move không đổi thứ tự thật

- **Date:** 2026-11-04
- **Job / khu vực:** `job_queue.py` + `index3.html` / `index.html` (V2/V4/V5)
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-04_queue-sort-move\`

## Triệu chứng

Bấm «Sắp xếp Phần 1→Pn» / ↑↓ / đẩy đầu — danh sách vẫn lệch (P3,P4,P5,P7,P6…). Nút vàng không phản ánh trạng thái đã sort.

## Root cause

1. UI **không gọi** `/api/queue/jobs/sort|move|reorder` — chỉ `_requeueFallback` (remove hết + add lại → `sort_first` xếp theo key sai).
2. `get_job_info` **ưu tiên `group_index`** hơn «Phần N» trên title → badge/season lệch.
3. Tên series lệch chữ → không gom cùng bộ khi thiếu `group_id` ổn định trong key.

## Fix

- Frontend: `sortQueueJobs` → `POST .../sort`; `moveQueueJob` → `POST .../move` (add trước nếu chưa trong hàng).
- Backend: season ưu tiên title; `job_sort_key` dùng `group_id` hoặc series đã normalize.
- Test: `test_queue_sort_prefers_title_phan_over_group_index`.

## Recheck

1. Hard refresh UI3 (`Ctrl+F5`).
2. Mở «Quản lý hàng chờ» → bấm «Sắp xếp Phần 1→Pn».
3. **Pass nếu:** cùng series xếp P1→Pn theo title; ↑↓ đổi vị trí ngay không đảo lung tung.
4. **Fail nếu:** thứ tự vẫn theo `group_index` sai hoặc bấm move không đổi queue.

## Liên quan

- Pytest 14 passed (`test_job_queue` + `test_queue_jobs_api`).
- **Restart :8801** để nạp `job_queue.py` (HTML tĩnh chỉ cần hard refresh).
