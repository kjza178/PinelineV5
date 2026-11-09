# Hongguo2 Ranking/New lệch WinUI 2.x

- **Date:** 2026-11-08
- **Job / khu vực:** `/hongguo2` Ranking · New
- **Status:** fixed

## Triệu chứng

Ranking dùng tab/board giả (`recommend/hot` + All/Female… cố định). New gọi `board=new` (chart) và **bỏ qua** chip 7/14/30/90 days.

## Root cause

1. WinUI Ranking = RPC `rank.page` → `charts[]` (8 bảng) + `boards[]` theo chart — không phải alias Explorer.
2. WinUI New = `feed.page` với `select.online_time=days_N` + `sort=online_time`.

## Evidence

- `rank.page` trả 8 chart: `ranklist_hot_sc`…`ranklist_hot_search_sc` + boards `gender_female` / `cate_*`.
- DLL labels: Recommended / Trending / Top rated / Comic / New / Must-watch / Most saved / Hot search.
- `feed.page` + `online_time=days_7` đổi danh sách New.

## Fix

- `hongguo_bridge.rank_page` + localize chart/board EN
- `GET /api/hg/rank?chart=&board=`
- UI Ranking: tabs = charts, chips = boards động; New: days → `/api/hg/feed?...`

Backup: `Z:\PinelineV2_codebak\2026-11-08_rank-new-winui\`

## Recheck

1. Hard refresh `/hongguo2` **và** `/static/ui/hongguo2.html`.
2. Ranking: 8 tab EN; chip All/Female/Male/… đổi theo chart; subtitle = desc EN.
3. New: chọn 7/14/30/90 → grid đổi; empty hiện “No dramas came out…” + Show 90 days.
4. **Pass nếu:** tab Trending ≠ Recommended; days chip thật sự filter New.
5. **Fail nếu:** vẫn tab `recommend/hot` cũ hoặc New bỏ qua days.

## Liên quan

- Sync V2/V4/V5 + `static/ui/hongguo2.html`

## Follow-up — Ranking max 100 + route Film/Studio

- **Date:** 2026-11-08
- **Triệu chứng:** Ranking chỉ ~8 item/lần (`rank.page`); thiếu route Film/Studio trên :8801.
- **Fix:** `hongguo_rpc.rank` gom `rank.more` đến max 100; UI `size=100`; routes `/films|/film|/films/ui` → `films_ui.html`, `/studio` → `index3.html`; sidebar hongguo2 link Film/Studio.
- **Recheck:** `/api/hg/rank?size=100` → n≫8 (tới khi hết board, ≤100); `GET /films/ui` + `/studio` = 200.
- Backup: `Z:\PinelineV2_codebak\2026-11-08_rank-max100-routes\`
