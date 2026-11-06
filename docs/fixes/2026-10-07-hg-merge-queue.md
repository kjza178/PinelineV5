# Hongguo "Merge all": không thấy đang chạy gì, 16 series rất lâu mới ra 1

- **Ngày:** 2026-10-07
- **Nguồn:** user báo trên `/hongguo`: "chọn merge all … ko thấy báo đang chạy series/phim nào, ko biết có chạy hay ko, tao chọn 16 series nhưng chờ rất lâu mới đc 1 movie".
- **Mức:** P1 (mất hàng đợi, user không biết hệ thống có đang chạy không).

## Root cause

1. **Hàng đợi gộp chỉ nằm trong RAM** (`hongguo_bridge._merge_q`, giữ qua `importlib.reload` bằng `_g` nhưng không qua restart process). Agent restart :8801 lúc 03:22, 03:45, 04:25 ngày 7/10 (chỉ kiểm tra queue render, không kiểm tra hàng đợi gộp) → **hàng đợi 16 series của user bị xoá**, series đang gộp dở bỏ giữa chừng. Đây là lỗi của agent.
2. **Bấm Merge all bị treo request**: `merge_queue_add` xử lý đồng bộ các series đã có `(merged)` nhưng còn tập lẻ — ffprobe từng file, có thể re-encode cả file sang 1080p (`normalize_merged_file`, hàng chục phút/bộ) rồi dọn tập lẻ — **trước khi** xếp hàng. UI chờ request, không hiện gì.
3. **Không có trạng thái chi tiết**: UI chỉ hiện tên series hiện tại + hàng đợi, không biết đang ở bước nào (kiểm tra / Hongguo gộp % / chuẩn hoá % / dọn), không có tiến độ lô.
4. **Chậm thật** khi series có tập lệch độ phân giải: phải gộp + re-encode 1080p cả bộ (CPU/GPU), lâu hơn nhiều so với Hongguo gộp copy.

## Sửa

`hongguo_bridge.py`:
- Lưu trạng thái ra `work/logs/hg_merge_state.json` (ghi atomic, gọi khi giữ lock): queue, current, history, done, batch, base. Process mới → `_load_merge_state()`, series đang gộp dở được đưa lại đầu hàng đợi.
- `merge_resume()`: chạy tiếp worker khi hàng đợi còn, chưa có worker, không bị dừng và Hongguo đang mở (`_output_dir` có). Gọi khi server khởi động (`server._resume_hg_merge`) và mỗi lần UI hỏi trạng thái.
- `merge_queue_add` **chỉ xếp hàng** (bỏ series đã xong), trả về ngay; mọi việc nặng chuyển vào worker.
- `_set_phase(name, phase, pct)` ở từng bước của worker: kiểm tra, kiểm tra độ phân giải, chuẩn hoá → 1080p (%), chờ Hongguo, Hongguo gộp (%), dọn tập lẻ.
- Đếm lô: `batch.total/finished/errors`.

`hongguo.html`: dòng "● Đang làm «series» · bước · % · mm:ss", "⏸ Hàng đợi N series đang dừng — chờ Hongguo mở…", "Lô: x/y xong (n lỗi)", 6 kết quả gần nhất.

`restart_server.py`: **từ chối restart khi đang gộp Hongguo** (`GET /api/hg/merge-queue` có `current` hoặc worker + queue); `--ignore-hg` để ép (series đang gộp làm lại từ đầu).

Test `tests/test_hg_merge_queue.py` (5): add chỉ xếp hàng + lưu file, load đưa current lên đầu, resume cần Hongguo, finish đếm lô, phase hiện trong state. Pytest 103/103, `check_batch1–5` pass. (`tests/test_server_split.py` chạy riêng lẻ lỗi import vòng `routes_agent` — có sẵn từ HEAD trước, chạy cả bộ thì qua.)

Restart server 04:32 (queue render + hàng đợi gộp rảnh), PID 32156.

## UI theo user (04:35)

`/hongguo`: hàng đợi gộp chuyển thành **tab riêng** «🎞 Hàng đợi gộp» (cạnh Tìm / Bảng hot, có số series còn lại) — nút Gộp đã chọn / Tất cả chưa gộp / Xoá hàng chờ, khối Đang làm (bước · % · thời gian · thanh tiến độ), danh sách chờ đánh số, kết quả gần đây; bấm gộp tự mở tab này. Bỏ khối Merge queue ở cột thư viện. **Một log chung** «Trạng thái tải · log»: dòng `[tải]` + `[gộp]` xếp theo giờ (chuẩn hoá % chỉ giữ dòng mới nhất), Clear ẩn dòng cũ. Trang đọc từ file mỗi request → không restart (hàng đợi 17 series đang chạy). Backup `codebak\2026-10-07_hg_merge_tab\`.

Tiếp (04:46, user: gộp thư viện vào tab vừa làm): Khung **Thư viện Hongguo** chuyển vào tab «🎞 Hàng đợi gộp» (hàng đợi trái, thư viện phải 440px; màn < 980px xếp chồng), bỏ cột phải → Tìm / Bảng hot dùng hết chiều ngang. Series trong hàng đợi có nhãn «● đang gộp» / «chờ #n»; xếp hàng xong tự bỏ tick; nút «Chưa gộp» không tick series đã trong hàng đợi. Backup `codebak\2026-10-07_hg_lib_in_tab\`.

Tiếp (04:53, user: khung trên quá rộng, cần xem list phim tốt hơn): Thanh công cụ gọn: tab + công cụ của tab trên **1 hàng** (bỏ tiêu đề từng pane; Bảng hot 46px, Tìm 75px, Catalog 85px ở 1920px — trước ~6 hàng). Sửa lỗi ô tìm catalog hiện cả khi đang ở Leaderboard (`.exctl{display:flex}` đè `hidden`). Khung tải/log thành **dock thu gọn** ở đáy (mặc định 40px: trạng thái + dòng log mới nhất; «▴ Log» mở, nhớ trong localStorage). Thẻ phim 176px (10 cột ở 1920px). Backup `codebak\2026-10-07_hg_compact_top\`.

## Còn treo

Danh sách 16 series gốc đã mất (không có log lưu tên). Cần user cho xếp lại các series chưa gộp trong thư viện bằng Merge all.

## Recheck

`GET :8801/api/hg/merge-queue` có `phase`, `batch`; file `work/logs/hg_merge_state.json` xuất hiện sau lần xếp hàng đầu tiên. Restart server khi đang gộp → `restart_server.py` báo "đang gộp Hongguo … chờ xong hoặc chạy lại với --ignore-hg".

Backup: `Z:\PinelineV2_codebak\2026-10-07_hg_merge_q\` + zip `Z:\PinelineV2_backup_2026-10-07_0428.zip`.
