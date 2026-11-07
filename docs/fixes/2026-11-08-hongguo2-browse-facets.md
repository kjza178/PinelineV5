# Hongguo2 Browse filters lệch WinUI 2.x (3 dropdown giả)

- **Date:** 2026-11-08
- **Job / khu vực:** `/hongguo2` Browse · `feed.page` selector panel
- **Status:** fixed

## Triệu chứng

Browse chỉ có Genre / Sort / Status — không giống app Hongguo Downloader 2.x (All genres / Any theme / Any setting / Any background / Recommended / Everyone / Any time).

## Root cause

1. UI tự chế 3 filter Explorer-style, không đọc selector panel từ RPC.
2. `feed.page` chỉ gọi với `offset` — thiếu `panel=true` + `select` map (`genre`, `category_dim_theme`, `category_dim_role`, `category_dim_epoch`, `sort`, `gender`, `online_time`).
3. Facet EN labels nằm trong WinUI `FilterText` / `Hongguo.Presentation.dll`, không phải Explorer `/genres`.

## Evidence

- Screenshot WinUI Browse: 7 chip dropdown + grid poster.
- `rpc.call('feed.page', {'panel': True})` → `rows` length 7, types đúng thứ tự trên.
- `select={'genre':'short_play'}` / `category_dim_theme=cate_*` đổi tập `cards`.

## Fix

- `hongguo_rpc.feed(panel/select/sessionId)`
- `hongguo_bridge.feed_browse` + `hongguo_feed_labels.json` (ZH→EN)
- `GET /api/hg/feed?...` nhận đủ facet query
- `hongguo2.html` render 7 `<select>` từ `facets`

Backup: `Z:\PinelineV2_backup_2026-11-08_0229.zip` · `Z:\PinelineV2_codebak\2026-11-08_browse-feed-facets\`

## Recheck

1. Hard refresh `http://127.0.0.1:8801/hongguo2` (sau restart :8801).
2. Hàng filter phải thấy: All genres · Any theme · Any setting · Any background · Recommended · Everyone · Any time.
3. Mở All genres → Live action / Comic drama / AI drama; chọn Comic drama → grid đổi.
4. `GET /api/hg/feed?panel=1` → `facets` length 7, mỗi item có `label` EN.
5. **Pass nếu:** 7 dropdown đúng label + filter đổi kết quả.
6. **Fail nếu:** vẫn 3 dropdown Genre/Sort/Status, hoặc `facets: []`.

## Liên quan

- RPC `feed.page` · landpage `need_selector_panel` / `select_items`
- Sync V4/V5 (+ `static/ui/hongguo2.html`, `agents/`)

## Follow-up

- **2026-11-08 ~02:35:** User mở `/static/ui/hongguo2.html` — bản stale vẫn 3 dropdown (`Any status`). Root `/hongguo2` đã đúng. Đã chép đè `hongguo2.html` → `static/ui/` (V2/V4/V5). **Recheck:** hard refresh URL static → 7 facet (Any theme / Any setting / …).
