# Phim đã xoá thư mục vẫn tồn đọng trong films/ui và thiếu chức năng xoá phim

- **Date:** 2026-10-09
- **Job / khu vực:** `data/films.db`, `http://127.0.0.1:8802/films/ui`, `film_db.py`, `agent_tele_cmd.py`, `films_ui.html`
- **Status:** fixed

## Triệu chứng

Trên giao diện Quản lý Phim `http://127.0.0.1:8802/films/ui` (tab Đã làm), xuất hiện hàng loạt job (94 job) hiển thị nhãn `(đã xoá thư mục)` và trạng thái `pending`/`download` tồn đọng từ các lần tải/test cũ. Không có chức năng xoá phim, không thể dọn dẹp các job đã mất thư mục, và không có bộ lọc để ẩn các job này.

## Root cause

- `film_db.py` thiết kế giữ lại lịch sử mọi job ngay cả khi thư mục work bị xoá (`work_exists=0`), nhưng không cung cấp bất kỳ hàm nào để xoá job (`DELETE`) hay dọn dẹp các job mất thư mục (`purge`).
- `agent_tele_cmd.py` không có route API cho việc xoá film hoặc dọn dẹp missing.
- `films_ui.html` không có nút xoá, không có hộp thoại xác nhận, không có bộ lọc theo `work_exists`, và không có chức năng chọn hàng loạt.

## Evidence

- Truy vấn database `data/films.db`: có 114 job, trong đó tới 94 job có `work_exists = 0`, chiếm phần lớn danh sách (tiêu biểu: `b87209ff091b`, `c85b365634a8`, `dc5dcba11ecc`... từ 29/09).
- Trước fix: gọi `POST http://127.0.0.1:8802/films/delete` trả `HTTP 404 Not Found`.

## Fix

- **`film_db.py`**:
  - `query()`: thêm tham số `work_exists` (`"1"` = chỉ còn thư mục, `"0"` = đã xoá thư mục).
  - Thêm `delete_film(job_id, delete_work=True)` và `delete_films(job_ids, delete_work=True)` để xoá job khỏi database (`films`, `events`) và tuỳ chọn xoá cả thư mục `work/` trên ổ đĩa.
  - Thêm `purge_missing(only_pending_failed=False)` để dọn dẹp hàng loạt các job mất thư mục.
  - `stats()`: bổ sung `work_exists` và `work_missing` để thống kê chi tiết.
- **`agent_tele_cmd.py`**:
  - Route `POST /films/delete`: nhận `job_id` hoặc danh sách `job_ids` và cờ `delete_work`.
  - Route `POST /films/purge-missing`: nhận `only_pending_failed`.
  - Route `POST /films/sync`: kích hoạt đồng bộ manifest thủ công.
  - Lệnh Telegram: `/delfilm <job_id> [work]`.
- **`films_ui.html`**:
  - Thêm cột thao tác với nút `🗑️ Xoá` cho từng dòng, kèm modal xác nhận trực quan (hỏi rõ có xoá cả file `work/` trên đĩa hay chỉ xoá DB).
  - Thêm thanh thao tác hàng loạt (chọn nhiều job qua checkbox).
  - Thêm bộ lọc `Thư mục` (Tất cả / Chỉ còn thư mục / Đã xoá) và checkbox `Ẩn đã xoá thư mục`.
  - Thêm thanh cảnh báo khi phát hiện job mất folder kèm 2 nút dọn dẹp nhanh (`🧹 Xoá sạch toàn bộ` hoặc `Chỉ xoá pending/failed`).

## Recheck

1. Kiểm tra API qua script Python:
   - `GET http://127.0.0.1:8802/films?work_exists=0&limit=3` $\rightarrow$ Trả đúng danh sách job mất folder.
   - `POST http://127.0.0.1:8802/films/delete` $\rightarrow$ Endpoint phản hồi `{ok: False, error: 'Danh sách rỗng'}` thay vì 404.
2. Kiểm tra giao diện `http://127.0.0.1:8802/films/ui`:
   - Giao diện nạp đầy đủ modal xoá `#del-modal`, banner cảnh báo `#alert-missing`, thanh batch `#f-batch-bar`.
3. **Pass nếu:** API trả về đúng kết quả HTTP 200, giao diện hiển thị bộ lọc thư mục, nút xoá hoạt động với modal xác nhận.
4. **Fail nếu:** API 404 hoặc không xoá được dữ liệu trong `data/films.db`.

## Liên quan

- Backup: `Z:\PinelineV2_backup_2026-10-09_0124.zip`
- Codebak: `Z:\PinelineV2_codebak\2026-10-09_films-ui-delete\` (`film_db.py`, `agent_tele_cmd.py`, `films_ui.html`)
