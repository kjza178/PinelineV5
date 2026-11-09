# Hongguo2: dropdown filter chữ mờ + chọn không đổi grid

- **Date:** 2026-11-08
- **Job / khu vực:** `/hongguo2` Browse facets · `hongguo_rpc.feed` select
- **Status:** fixed
- **Backup zip:** `Z:\PinelineV2_backup_2026-11-08_0622.zip`
- **Backup code:** `Z:\PinelineV2_codebak\2026-11-08_hongguo2-dropdown-winui\`

## Triệu chứng

1. Mở dropdown Browse: chữ gần như không thấy (trắng trên trắng / xám thấp contrast).
2. Chọn genre/theme… grid gần như không đổi («chức năng không hoạt động»).

## Root cause

1. Native `<select>` trên Windows: `color-scheme:dark` + option CSS không áp được → popup nền trắng / chữ mờ. Không đạt WinUI.
2. Helper `JsonKt.select` = `Map<String, List<String>>` (landpage `select_items`). RPC gửi `{"genre":"ai_series"}` (string) → bị bỏ qua; mọi filter trả cùng feed.

## Evidence

- RPC probe: `select={'genre':'ai_series'}` cùng titles với default; `select={'genre':['ai_series']}` đổi hẳn list (AI ≠ comic ≠ short).
- `MobileCatalogApi` body: `"select_items":{…}` + `need_selector_panel`.

## Fix

- `hongguo_rpc.feed`: wrap mỗi value select → `list[str]`.
- `hongguo_bridge._rpc_mod`: hot-reload khi source chưa có `list[str]` (giữ `_proc`).
- `hongguo2.html`: dropdown custom WinUI (pill tối, chữ sáng, active accent cam, menu `#2a2723` + item hover/on); nút Reset filters.
- Sync `static/ui` + V4/V5 (+ `agents/`).

## Recheck

1. Hard refresh `http://127.0.0.1:8801/hongguo2`.
2. Mở Any theme / All genres → menu nền tối, chữ trắng đọc rõ; mục đang chọn màu cam.
3. Chọn Comic drama → grid đổi; Reset filters → về mặc định.
4. `GET /api/hg/feed?size=5&panel=1&genre=comic_series` vs `ai_series` → titles khác nhau.
5. **Pass nếu:** menu WinUI đọc được + filter đổi kết quả.
6. **Fail nếu:** chữ mờ / mọi genre cùng list.

## Liên quan

- Follow-up của `hongguo2-intro-dropdown` (CSS native thất bại) + `hongguo2-browse-facets` (select format).
