# Hongguo1 kẹt «Đang tải bảng hot…»

- **Date:** 2026-11-08
- **Job / khu vực:** `/hongguo` (classic) boot
- **Status:** fixed
- **Backup code:** `Z:\PinelineV2_codebak\2026-11-08_hongguo1-boot\`

## Triệu chứng

Mở `http://127.0.0.1:8801/hongguo` — pill «Hongguo online» nhưng giữa màn hình mãi «Đang tải bảng hot…». Tưởng Hongguo1 chết.

## Root cause

`refreshAll()` chờ `Promise.all(status, library, merge)` **xong mới** `loadRank()`. Với `HG_BACKEND=rpc` (helper 1 process + lock), `/api/hg/library` thường 5–15s → UI nằm placeholder HTML ban đầu. Không phải xóa Hongguo1; không phải route 404.

## Evidence

- `/hongguo` 200; `/api/hg/rank?size=100` 200 (~1–2s khi rảnh)
- Parallel: library ~11s, status ~3s, rank ~2s
- Gọi tay `loadRank()` trong console → 98 cards ngay

## Fix

- `hongguo.html` `refreshAll`: chạy `loadRank`/`loadCatalog` **song song** với status/library/merge (không await library trước).

## Recheck

1. Hard refresh `/hongguo`
2. **Pass nếu:** trong vài giây thấy lưới Leaderboard (không kẹt placeholder)
3. **Fail nếu:** vẫn «Đang tải bảng hot…» >15s trong khi `/api/hg/rank` 200

## Liên quan

- Default `HG_BACKEND=rpc` (server.py) — chung helper với hongguo2
