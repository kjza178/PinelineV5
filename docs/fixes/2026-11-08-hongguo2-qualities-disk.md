# Hongguo2: qualities 502 + /api/disk 404

- **Date:** 2026-11-08
- **Job / khu vực:** hongguo2 detail Play/Download, sidebar disk
- **Status:** fixed
- **Backup code:** `Z:\PinelineV2_codebak\2026-11-08_qualities-disk\`

## Triệu chứng

Console đỏ: `GET /api/hg/series/<id>/qualities` → 502 («catalog service didn't answer» / helper chết); `GET /api/disk` → 404. Detail vẫn mở nhờ try/catch nhưng XHR fail và quality ladder trống.

## Root cause

1. RPC `series.qualities` trên helper 0.3.x hay timeout/crash → bridge/`_hg_err` trả 502.
2. UI gọi `/api/disk` cho free space nhưng server chưa có route.

## Evidence

- Console: `502` trên `…/qualities`, `404` trên `/api/disk`.
- Curl ping `:8801` OK (backend rpc); `/api/disk` 404 trước fix.

## Fix

- `hongguo_rpc.series_qualities` — không gọi RPC flaky; trả ladder `1080p…360p` (`fallback: true`).
- `hongguo_bridge.series_qualities` + attach trong `series()` — luôn có ladder; catch → default.
- `routes_hg` `GET /api/disk` — `shutil.disk_usage` trên `saveFolder`/ổ.
- `hongguo2.html` — client fallback ladder + ưu tiên quality settings; bỏ `allowfullscreen` trùng `allow`.

## Recheck

1. Restart server `:8801`, hard refresh `/hongguo2`.
2. Mở 1 series detail → console **không** còn 502 qualities; Quality dropdown có 1080p…360p.
3. `GET http://127.0.0.1:8801/api/hg/series/<id>/qualities` → 200 + `qualities` + `"fallback":true`.
4. `GET http://127.0.0.1:8801/api/disk` → 200 + `free_gb` / `used_pct`.
5. **Pass nếu:** không 502/404 trên 2 endpoint trên; Play vẫn chuẩn bị được.
6. **Fail nếu:** qualities vẫn 502 hoặc disk vẫn 404.

## Liên quan

- `HG_BACKEND=rpc`, helper `hongguo-helper-0.3.14`
- Console screenshot session (qualities 502 / disk 404)
