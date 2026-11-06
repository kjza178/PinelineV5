# Hongguo2 UI redesign (thử nghiệm)

- **Date:** 2026-11-06
- **Status:** implementing
- **Route thử:** `/hongguo2` — giữ `/hongguo` cũ đến khi user duyệt thay

## Vấn đề

`hongguo.html` hiện 5 tab ngang trộn Discover (Tìm / Hot) với Ops (Hàng đợi tải / Mùa mới / Gộp). Thư viện chỉ hiện trong tab Gộp; CTA Chọn/Tải/Queue trùng nhiều chỗ + floating bar.

## IA

Hai cột cố định:

| Trái (~55%) Discover | Phải (~45%) Ops |
|---|---|
| Segment: Tìm \| Hot \| Catalog | Mùa mới (board + Update all) |
| Kết quả / lưới | Thư viện (luôn hiện) |
| CTA: chọn + vào hàng đợi tải | Tab phụ: Hàng đợi tải \| Hàng đợi gộp |
| | + Job → UI3 |

Dock đáy 1 dòng: status tải Hongguo. Không floating-q-bar.

## Kỹ thuật

- File: `hongguo2.html` (V2/V4 root; V5 `static/ui/`)
- API reuse: `/api/hg/*` hiện có (search, rank, status, submit, library, merge, library/update, seasons/decline)
- Khi duyệt: `ui_hongguo` → `hongguo2.html`, archive bản cũ

## Ngoài phạm vi

Feeder, Telegram, UI3, đổi bridge trừ thiếu API.
