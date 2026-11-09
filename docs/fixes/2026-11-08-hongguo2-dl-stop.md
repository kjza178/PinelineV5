# Hongguo2: không Stop được download đang chạy (× → 502)

- **Date:** 2026-11-08
- **Job / khu vực:** Downloads UI + `downloads.remove` / cancel
- **Status:** fixed
- **Backup code:** `Z:\PinelineV2_codebak\2026-11-08_dl-stop\`

## Triệu chứng

Bấm × trên download đang tải → console `POST /api/hg/downloads/remove` 502: «that download is still under way; cancel it instead». UI không có nút Stop.

## Root cause

Helper 0.3.x chỉ expose `downloads.cancelAll` + `downloads.remove`. `remove` từ chối job còn active; không có `downloads.cancel(seriesId)`.

## Evidence

- API: remove active → `Invalid params: that download is still under way; cancel it instead`
- Jar `EngineApi`: methods `downloads.cancelAll` / `remove` / `retry` / `clearFinished` (không có cancel one)

## Fix

- `hongguo_rpc.cancel_download(sid)`: snapshot active → `cancelAll` → `downloads.add` lại các series khác (giữ quality)
- `remove_download`: nếu lỗi under way → gọi `cancel_download`
- Route `POST /api/hg/downloads/cancel`
- UI: nút **Stop** (active), **Stop all**, × trên active = stop; Retry trên failed

## Recheck

1. Hard refresh `/hongguo2` → Downloads
2. Có ≥1 job Active → bấm **Stop** → biến mất khỏi Active; job khác (nếu có) vẫn còn / được re-queue
3. **Stop all** → hết Active
4. Done/Failed: × → remove 200 (không 502)
5. **Pass nếu:** không còn 502 under way; có Stop / Stop all
6. **Fail nếu:** Stop one làm mất hết queue khác không restore

## Liên quan

- Console: `POST …/downloads/remove 502`
- User: «ko có chức năng stop download»

## Follow-up — Retry 502

- **Triệu chứng:** `POST /api/hg/downloads/retry` 502 (`Waiting for the licence check` / helper không sẵn sàng).
- **Fix:** `retry_download` prove license (force nếu helper báo chờ licence); hot-reload `_DL_STOP_V=3`; UI ensure license trước Retry.
- **Recheck:** Retry job Failed → 200, state → waiting/active. Hard refresh.
