# Video nguồn bị chép thành 2 bản (thư viện + job)

- **Ngày:** 2026-10-07
- **Nguồn:** user báo "đang copy 2 file source mà không dùng 1".
- **Mức:** P2 (tốn ổ D, không sai output).

## Triệu chứng

`D:\Lib\<bộ>\<bộ> (merged).mp4` và `D:\PinelineV2_work\<job>\source.mp4` cùng nội dung nhưng là 2 file riêng. Đo 07/10:

| Job | Kích thước | Trạng thái |
|---|---|---|
| 05361, 2ef87, 3a2e, 77a8, f9fe | 4,4–16,3 GiB | hard link với file `(merged)` → không tốn thêm |
| 0281 | 23,7 GiB | bản sao riêng của `我都元婴期了，你跟我说开学第二季 (merged).mp4` (khớp đầu/cuối 8 MB) |
| dccc | 13,0 GiB | bản sao riêng của `我都元婴期了，你跟我说开学 (merged).mp4` |
| 244f, 7bbf | 0,8 / 1,1 GiB | không còn bản trong `D:\Lib` |

## Root cause

`server.py` có 2 đường đưa video vào job:

- `_import_local_video_file` (import thư viện/đường dẫn): thử `os.link`, lỗi thì `shutil.copy2` **không log** — không biết khi nào rơi về copy.
- `POST /api/jobs/{id}/source-path` (nút nhập đường dẫn trên UI): **luôn `shutil.copy2`**, không thử hard link.

## Sửa

Helper `_link_or_copy(src, dest)`: hard link trước (cùng ổ — không tốn dung lượng), chỉ copy khi không link được (khác ổ / FS không hỗ trợ) và in lý do. Dùng cho cả 2 đường. `move=True` giữ nguyên `shutil.move`.

An toàn với hard link: pipeline chỉ đọc `source.*`; `normalize_merged_file` (Hongguo) thay file bằng rename nên chỉ tách link, không ghi đè dữ liệu job; xoá job/thư viện chỉ gỡ 1 link.

Test `tests/test_source_link.py` (3): link cùng ổ, rơi về copy khi `os.link` lỗi, endpoint `/source-path` tạo hard link. Pytest 96/96, `check_batch1–5` pass. Restart server 03:45 (queue rảnh), PID 28108.

## Đổi tiếp theo user (04:20): đọc thẳng từ `D:\Lib`

User chọn lấy nguồn trực tiếp từ thư viện thay vì hard link. Không tạo symlink được (WinError 1314 — Developer Mode tắt), nhưng mọi module (ASR, OCR, separate, render, mux, sfx_lib, heal…) đã ưu tiên `download.video_path` trong manifest, chỉ glob `source.*` khi thiếu. Nên chỉ sửa **chỗ chọn đường dẫn lúc import**:

- `server._place_source`: file nằm trong `SOURCE_DIRECT_ROOTS` (mặc định `D:\Lib`, nhiều thư mục ngăn `;`) và không `move` → `video_path` = đường dẫn thư viện, **không đặt file nào vào job** (`source_mode=direct`). Ngoài thư viện → hard link / copy như trên.
- `_finalize_imported_source` ghi thêm `source_mode`, `video_size`, `video_mtime`.
- Import lại job đã trỏ đúng file → bỏ qua; import file thư viện vào job đang có bản sao → xoá bản sao trong job.
- `agent_av_sync`, CLI `media_ts --check`: đọc `video_path` trước `source.mp4`.
- `agent_heal`: báo `source_changed` khi file thư viện đổi kích thước sau khi import (Hongguo gộp lại khi có tập mới sẽ cất merged cũ vào thùng rác, tạo file mới cùng tên).

Đánh đổi: dọn/đổi tên/chuyển bộ phim trong `D:\Lib` trước khi job xong → job mất nguồn (heal báo `no_source`).

Test `tests/test_source_link.py` (5): thư viện → direct, ngoài thư viện → hard link, import lại xoá bản sao cũ, link/copy. Theo user không chạy lại toàn bộ: chạy test liên quan (17/17) + `check_batch1–5` pass. Restart server 04:25 (queue rảnh), PID 22868. Backup `codebak\2026-10-07_source_direct\`.

## Còn treo

2 bản trùng sẵn có (0281, dccc ≈ 36,7 GiB) — user quyết giữ nguyên, cách mới chỉ áp dụng cho job tạo sau 04:25 7/10.

## Recheck

`fsutil hardlink list D:\PinelineV2_work\<job>\source.mp4` → có cả đường dẫn trong `D:\Lib`. Log server có `[import] không hard link được` là đang copy.

Backup: `Z:\PinelineV2_codebak\2026-10-07_source_link\` + zip `Z:\PinelineV2_backup_2026-10-07_0342.zip`.
