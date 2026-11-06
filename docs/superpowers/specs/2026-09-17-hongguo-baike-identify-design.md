# Design: Hongguo search qua duanjubaike

## Goal
Tìm/nhận diện series bằng [duanjubaike](https://www.duanjubaike.net) (rõ version + tên), rồi map sang Hongguo Downloader để tải — loại kết quả lạc họ.

## Flow
1. `GET /so.html?keyword=Q` → hit(s) `info-{series_id}`
2. Mở `info-{id}` → meta + mục 同系列 (lọc theo `franchise_core` / stem chung với phim gốc — bỏ ranking nhiễu)
3. Danh sách version A1…An (title + series_id + eps)
4. Với mỗi version: `lookup_series(id)` trên Hongguo; nếu fail thì search đúng title và chỉ giữ match gần đúng
5. UI `/hongguo`: mode mặc định «Baike → Hongguo», hiện N version + tick tải

## Files
- `hongguo_bridge.py` — scrape + `search_via_baike`
- `server.py` — `/api/hg/baike-search`
- `hongguo.html` — UI cards

## Non-goals
Không thay Downloader; không scrape ranking trừ khi sau này cần.
