# Hongguo2 Browse chỉ hiện 1 trang — thiếu load-on-scroll WinUI

- **Date:** 2026-11-08
- **Job / khu vực:** `/hongguo2` Browse · `GET /api/hg/feed` session/nextOffset
- **Status:** fixed
- **Backup code:** `Z:\PinelineV2_codebak\2026-11-08_hongguo2-browse-scroll\`

## Triệu chứng

Browse chỉ hiện ~24–48 card rồi hết; WinUI cuộn xuống vẫn tải thêm.

## Root cause

UI `loadBrowse` gọi một lần `size=48&offset=0`, không dùng `hasMore` / `nextOffset` / `sessionId` để trang tiếp.

## Evidence

- `feed?size=20` → `hasMore=true`, `nextOffset=20`
- Trang 2 với `session_id` + `offset=20` → 20 card mới, overlap 0

## Fix

- `hongguo2.html`: `BROWSE_PAGE=24`; `loadBrowse({reset})` + `browseSeen` dedupe; sentinel + `IntersectionObserver` trên `.content` (`rootMargin` 320px); filter/reset → session mới.
- Sync `static/ui` + V4/V5.

## Recheck

1. Hard refresh `/hongguo2` Browse.
2. Cuộn gần đáy → thấy «Loading more…» rồi thêm poster (không trùng).
3. Đổi filter → grid reset từ đầu, cuộn lại vẫn load thêm.
4. **Pass nếu:** cuộn liên tục tới khi «End of list» / hết `hasMore`.
5. **Fail nếu:** dừng cứng sau trang đầu.

## Liên quan

- `docs/fixes/2026-11-08-hongguo2-browse-pagesize.md` (gom trang RPC)
- `sessionId` + `nextOffset` từ `hongguo_rpc.feed`

## Follow-up

- **2026-11-08 ~07:10:** User vẫn chỉ thấy 2 hàng (24). IO sentinel `visibility:hidden` + không fill viewport. Đổi sang scroll listener + `maybeBrowseMore` + auto-fill sau mỗi trang; sentinel luôn đo được. Cùng đợt `hongguo2-play-button`.
