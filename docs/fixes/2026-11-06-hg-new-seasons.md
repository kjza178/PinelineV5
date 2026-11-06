# Hongguo UI thiếu board Mùa mới (Added / Gợi ý / Sắp ra)

- **Date:** 2026-11-06
- **Job / khu vực:** `/hongguo` UI + `agents/hongguo_bridge` + `http_routes/routes_hg` (V2/V4/V5)
- **Status:** fixed
- **Backup zip/code:** `Z:\PinelineV2_codebak\2026-11-06_hg-new-seasons\`

## Triệu chứng

Trên Pineline `/hongguo` không có tab/board New seasons như Hongguo Downloader (Đã thêm / Gợi ý / Sắp ra + Thêm / Update all / Không tải).

## Root cause

Downloader đã trả `seasons` trong `/dl/status` sau Update all, nhưng Pineline bridge/routes/UI chưa expose:
- `submit` không gửi `scores`
- thiếu proxy `/dl/library/update` và `/dl/library/seasons/decline`
- `hongguo.html` không có tab + render board

## Evidence

- Probe `Z:\PinelineV5\work\logs\_probe_hg_seasons.json`: buckets auto/older/soon + fields sid/title/eps/season/score/base/album/short
- Downloader `downloader.html` ~2827–3002: `lsnTake`/`lsnRender`/`lsnSubmit` → `/dl/submit` + scores

## Fix

- Bridge: `submit(..., scores=)`; `library_update`; `seasons_decline`
- Routes: `HgSubmitIn.scores`; POST `/api/hg/library/update`; POST `/api/hg/library/seasons/decline`
- UI: tab 🆕 Mùa mới + board `libSeasons` (V2/V4/V5)

## Recheck

1. Hard refresh `/hongguo` → thấy tab **🆕 Mùa mới**
2. Python: `library_update` / `seasons_decline` tồn tại trên bridge modules
3. Restart server nếu process cũ chưa nạp routes; GET `/api/hg/status` có key `seasons` khi Downloader đã Update all
4. Bấm **Update all** (Downloader đang chạy) → board hiện Gợi ý / Sắp ra / Đã thêm; **+ Thêm** gọi submit có scores
5. **Pass nếu:** tab + `libSeasons`/`lsnUpdateAll` có trong 3 HTML; API update/decline không 404 sau restart
6. **Fail nếu:** tab không hiện / 404 trên `/api/hg/library/update` / board trống dù status đã có `seasons`

## Liên quan

- APIs: `/api/hg/status`, `/api/hg/submit`, `/api/hg/library/update`, `/api/hg/library/seasons/decline`
- Hongguo: `/dl/library/update`, `/dl/library/seasons/decline`, `/dl/submit`
