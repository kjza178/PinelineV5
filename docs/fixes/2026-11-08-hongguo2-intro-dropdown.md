# Hongguo2: intro chưa VI + dropdown filter không đọc được

- **Date:** 2026-11-08
- **Job / khu vực:** `hongguo2.html` detail intro + Browse `<select class="filter">`
- **Status:** fixed

## Triệu chứng

1. Detail: tiêu đề có VI nhưng đoạn tóm tắt vẫn Hán.
2. Dropdown facet (Any setting…): mở list chữ gần như trắng trên nền trắng.

## Root cause

1. `renderDetailChrome` chỉ `intro_vi || intro` — không gọi `/api/hg/translate-titles` cho intro (classic `hongguo.html` có).
2. `select{color:inherit}` + dark text trên popup option nền trắng (Win native).

## Fix

- Backup: `Z:\PinelineV2_codebak\2026-11-08_hongguo2-intro-dropdown\`
- `applyIntroViDetail` → translate `series_id:intro`; hiện VI chính + ZH phụ `#dIntroZh`
- CSS: `color-scheme:dark` + `option{background;color}`; bỏ inherit color trên select; tag contrast cao hơn
- Sync `static/ui` + V4/V5

## Recheck

1. Hard refresh `/hongguo2` → mở phim có intro Hán → vài giây có VI; ZH nhỏ bên dưới.
2. Browse mở dropdown Setting → chữ đọc rõ trên nền tối.
3. **Pass nếu:** intro VI hiện; option list đọc được.
4. **Fail nếu:** chỉ ZH; hoặc option vẫn trắng trên trắng.

## Liên quan

- Không cần restart (HTML static). Hard refresh.
