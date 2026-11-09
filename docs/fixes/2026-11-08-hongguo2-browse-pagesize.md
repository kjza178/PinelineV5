# Hongguo2 Browse chỉ hiện ~20 phim

- **Date:** 2026-11-08
- **Job / khu vực:** `/hongguo2` Browse · `hongguo_rpc.feed` / `feed_browse`
- **Status:** fixed (cần restart :8801)

## Triệu chứng

Browse UI gọi `size=48` nhưng lưới chỉ ~20 card (đôi khi ít hơn nếu helper lỗi).

## Root cause

Helper `feed.page` cố định **~20 card/trang**; `limit`/`size` bị bỏ qua. `hongguo_rpc.feed` chỉ gọi 1 lần → cắt 20. `hasMore=true` + `nextOffset` không được gom tiếp.

## Evidence

- `GET /api/hg/feed?size=48` trước fix: `n=20`.
- RPC: trang 0 = 20, `hasMore=true`, `nextOffset=20`; trang session+offset=20 = 20 card khác.
- Sau fix (direct): `feed(limit=48)` → `n=48`.

## Fix

- Backup: `Z:\PinelineV2_codebak\2026-11-08_hongguo2-browse-pagesize\`
- `hongguo_rpc.feed(limit=…)`: lặp `feed.page` theo `sessionId`+`nextOffset` đến đủ limit (≤200).
- `hongguo_bridge.feed_browse`: truyền `limit=size_n`.
- Sync V4/V5 (+ `agents/` nếu có).

## Recheck

1. Restart :8801 → hard refresh `/hongguo2` Browse.
2. `GET /api/hg/feed?size=48&panel=1` → `n≈48`, `hasMore` true nếu còn.
3. **Pass nếu:** lưới ≥40 card (thường 48).
4. **Fail nếu:** vẫn ~20.

## Follow-up

- **Triệu chứng:** «No results · feed» + dropdown không item — bridge mới gọi `feed(..., limit=)` trong khi `hongguo_rpc` cũ trong memory → TypeError → results=[] → không facets; có filter thì không rank_fallback.
- **Fix:** `_rpc_mod()` hot-reload code khi `feed` thiếu `limit`, **giữ** `_proc`/`_lock` (không leak MainKt). API sau đó: `n=48`, `facets=7`.
- **Recheck:** Hard refresh Browse — lưới ~48 + dropdown có option; đổi Genre có kết quả.

## Liên quan

- Restart :8801 vẫn tốt (nạp sạch); hot-reload đủ để hết «No results» không restart.
