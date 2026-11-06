# Hàng đợi render đứng khi ổ D: đầy

- **Ngày:** 2026-10-08
- **Mức:** P1 (queue im lặng dừng, không báo).
- **Trạng thái:** đã xử lý tay; **chưa sửa code** (cần user đồng ý, có hiệu lực sau restart server).

## Triệu chứng

01:20 D: còn 0 GB (gộp 问鼎仙途 6,9 GB + render). Mux 0be257b1594b lỗi `Error muxing a packet`, 9a78abb17ad5 lỗi ngay đầu ASR, hai job còn lại nằm trong hàng đợi nhưng không chạy; `/api/queue/jobs` báo `worker: false`.

## Root cause

`job_queue._worker_loop` gọi `_save()` (ghi `work/_job_queue.json` + `fsync`) trong `with _lock` ở 4 chỗ mà không bắt lỗi. Ổ đầy → `OSError` thoát khỏi vòng lặp → thread chết. `enqueue` chỉ khởi động lại worker khi có job **mới** được thêm, nên job đang chờ đứng im tới khi có người thêm job.

## Xử lý tay

1. Xoá `mixed_audio.wav` + `dub_fit.wav` của 13 job đã render xong (26 file, 52,1 GB; user đồng ý).
2. Xoá rồi thêm lại job chờ để `enqueue` dựng lại worker (`Z:\PinelineV3\tools\kick_v2_queue.py`).

## Đề xuất sửa

Trong `_worker_loop` gọi `_save` qua hàm bọc bắt `OSError` (log stderr, tiếp tục chạy); thêm test giả lập `_save` ném `OSError` và kiểm worker vẫn chạy job kế. Cân nhắc kiểm tra dung lượng trống trước mux/gộp (cảnh báo Telegram khi < 20 GB).

## Recheck

`GET /api/queue/jobs` → `worker: true` khi `queue` không rỗng. Ổ D: còn ≥ 20 GB trong lúc render.
