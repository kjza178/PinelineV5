# Hongguo2 CTA submit nhầm + selectedIds lẫn detail

- **Date:** 2026-11-06
- **Job / khu vực:** `/hongguo2` UI — `hongguo2.html`
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-06_hongguo2-review\`

## Triệu chứng

CTA «Thêm vào hàng đợi» gọi `/api/hg/submit` thay vì chỉ enqueue; `selectedIds`/`selectAllVisible` gồm checkbox trong detail panel; hint catalog ghi nhầm vào rank/search; double-start queue dễ xảy ra.

## Root cause

`doDownload` dùng chung path submit với tải ngay; selector `input.res:checked` không giới hạn `#results`; `loadCatalog` ghi `#rank-hint`; thiếu inflight guard / clear queue sau submit.

## Evidence

- Multi-agent review: CTA semantics, scope, hints, busy flags.
- Grep trước fix: `doDownload` chứa `/api/hg/submit`; `selectedIds` = toàn page `input.res:checked`.

## Fix

- `doDownload` → enqueue-only (`onResCheckboxChange` + `renderQueueList` / badges / `setOpsQueue('dl')` + `#cta-status`).
- Submit giữ ở `startDlQueue` / `dlGroup` / `dlDetailMain` / `dlDetailRelated` (+ `_submitBusy`; queue clear sau start).
- `selectedIds` / `selectAllVisible` / `pickGroup` chỉ `#results`.
- `closeDetail` clear `#detail-panel` + `updateDlBtn`.
- `#catalog-hint`, `#cta-status`; bỏ nút nhảy queue trùng, `btn-start-queue-body`, CSS wrap chết; UX label VN + ops flex; `rankSeq`; `_mergeBusy` / delete disable.
- Sync V4 `hongguo2.html`, V5 `static/ui/hongguo2.html`.

## Recheck

1. Hard refresh `/hongguo2` → tick vài card → bấm «Thêm vào hàng đợi».
2. Grep: `doDownload` không có submit; `startDlQueue` vẫn submit; `selectedIds` có `#results`; `catalog-hint` tồn tại; không `floating-q-bar`.
3. **Pass nếu:** CTA chỉ thêm queue (không gọi Downloader ngay); Queues bên phải mở; detail đóng không còn ảnh hưởng sel-count; Start queue lần 2 không gửi lại cùng list (queue đã clear).
4. **Fail nếu:** CTA vẫn submit; sel-count tăng khi tick related trong detail; catalog status ghi vào search/rank hint.

## Liên quan

- Config: localStorage `pineline_hg_dl_queue_v1`
- Ports: static HTML — hard refresh; không cần restart server trừ khi route `/hongguo2` chưa nạp.
