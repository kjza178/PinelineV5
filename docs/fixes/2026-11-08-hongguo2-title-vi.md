# Hongguo2 thiếu dòng tiếng Việt dưới tiêu đề Trung

- **Date:** 2026-11-08
- **Job / khu vực:** `hongguo2.html` Browse / Ranking / New / Search / Library / Detail
- **Status:** fixed

## Triệu chứng

Trên `/hongguo2` card chỉ hiện tiêu đề Trung (hoặc `title_vi` nếu API đã có sẵn), không gọi dịch thô như `hongguo.html` → thiếu dòng VI dưới poster.

## Root cause

`cardHTML` đọc `title_vi` nếu có nhưng UI **không** gọi `POST /api/hg/translate-titles` sau khi load grid. Classic `hongguo.html` có `applyTitleVi` + `.tvi`.

## Evidence

- Grep `hongguo2.html` trước fix: không có `translate-titles` / `applyTitleVi`.
- `hongguo.html` L755+: `applyTitleVi` sau rank/search/feed.
- API sống: `POST :8801/api/hg/translate-titles` → `title_mt.translate_titles` (OK).

## Fix

- Backup: `Z:\PinelineV2_codebak\2026-11-08_hongguo2-title-vi\`, zip `Z:\PinelineV2_backup_2026-11-08_0528.zip`
- `hongguo2.html`: CSS `.tvi` / `.detail-tvi`; card `data-title-zh` + slot `.tvi`; `applyTitleVi` + `applyTitleViDetail`
- Gọi sau Browse / Search / Rank / New / Library; detail hiện ZH + `#dTitleVi`
- Sync `static/ui` + V4/V5

## Recheck

1. Hard refresh `/hongguo2` (hoặc `/static/ui/hongguo2.html`)
2. Mở Browse / Ranking / New — dưới tiêu đề ZH xuất hiện dòng VI (màu accent)
3. Mở 1 phim — `#dTitle` = ZH, `#dTitleVi` = VI
4. `POST /api/hg/translate-titles` body `{"items":[{"series_id":"x","title":"庆余年"}]}` → `title_vi` không rỗng
5. **Pass nếu:** lưới có `.tvi` text sau vài giây; detail có VI
6. **Fail nếu:** chỉ ZH, hoặc Network không có `translate-titles`, hoặc 404/5xx

## Liên quan

- API: `routes_hg.hg_translate_titles` → `title_mt`
- Parity: `hongguo.html` `applyTitleVi`
