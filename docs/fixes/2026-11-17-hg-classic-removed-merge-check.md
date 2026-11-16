# 2026-11-17 — Xoá Hongguo classic + kiểm tra/chuẩn hoá tập khi gộp

## Vì sao
- Downloader 1.x (:8000) đã chết; mọi chức năng phải chạy qua helper RPC (hongguo2).
- Gộp cũ lặng lẽ bỏ qua/ghép tập hỏng → nhiều file gộp lỗi (đứng hình, lệch tiếng, thiếu đoạn).

## Chức năng khôi phục trên hongguo2 (RPC không có lệnh tương ứng → làm cục bộ)
| Chức năng | Cách làm |
|---|---|
| Gộp tập + hàng đợi | `_merge_worker` → `hg_merge_check.run_merge` (ffmpeg cục bộ) |
| Cập nhật mùa mới | `discover_new_seasons` (quét) + `library.downloadNewSeasons` / `submit` (tải) |
| Từ chối mùa | `hg_seasons_declined.json` cạnh merge state; `undo` để bỏ |
| Tra Baike / web | `search_via_baike`, `baike_deep`, `web_expand_into` (không phụ thuộc :8000) |
| Thêm job Pineline | UI gọi `/api/jobs/local-path` (move=false) + tuỳ chọn `/api/queue/jobs` |

## Quy trình gộp (hg_merge_check.run_merge)
1. `check_all`: từng tập → `fatal` (dừng) / `fix` (chuẩn hoá) / `warn`.
   - Tải cụt faststart: so `max(pts+dur)` của packet hình với thời lượng khai báo.
2. `make_plan`: `stop` | `copy` | `normalize`; đích = res/fps/tiếng của số đông.
3. Ghép (`concat` copy hoặc chuẩn hoá từng tập rồi ghép) → file tạm → `os.replace`.
4. `verify_merged`: tổng thời lượng (dung sai max(2s, 0.5%, 0.08s×số tập)) + giải mã ±2s mỗi mối nối.
5. `merge_check.json` trong thư mục series: từng tập, kế hoạch, kết quả kiểm.

## Biến môi trường
- `HG_MERGE_ON_BAD=stop|skip` (mặc định stop) · `HG_MERGE_CHECK=deep` · `HG_MERGE_CHECK_WORKERS=4`.

## Restart
- Server :8801. Sidecar không cần.
