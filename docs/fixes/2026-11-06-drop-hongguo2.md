# Bỏ Hongguo2 — redirect về Hongguo gốc

- **Date:** 2026-11-06
- **Job / khu vực:** `/hongguo2` · Films UI seasons · v5-map · dual-tree V2/V4/V5
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-06_drop-hongguo2\`

## Triệu chứng

Hongguo2 UI thử nghiệm quá tệ; user yêu cầu bỏ và cập nhật V4–V5. Link Mùa mới / Map vẫn trỏ `/hongguo2`.

## Root cause

Trang thử `hongguo2.html` + route `GET /hongguo2` + nav «Thử Hongguo2» / Films UI `snHgUrl` → Hongguo2.

## Evidence

- Grep live UI: `hongguo.html` có «Thử Hongguo2»; `films_ui.html` `snHgUrl` → `:8801/hongguo2`.
- User: «bỏ hongguo 2 đi, quá tệ. update cả V4-5».

## Fix

- `routes_ui.py` (V2/V4/V5): `GET /hongguo2` → **302** `/hongguo` (file `hongguo2.html` giữ trên đĩa, không serve).
- `hongguo.html`: bỏ nút «Thử Hongguo2»; thêm `bootFromQuery` (`?sid=` / `?q=`) từ deep-link Films UI.
- `films_ui.html`: toolbar + `snHgUrl` → `/hongguo`.
- `v5-map.html`: link Hongguo (không còn Hongguo2).
- Sync V2 root + V4 root + V5 `static/ui/`.

## Recheck

1. **Restart :8801** (nạp redirect), hard refresh Films UI + `/hongguo`.
2. `curl -I http://127.0.0.1:8801/hongguo2` → **302** `Location: /hongguo` (hoặc absolute `/hongguo`).
3. Mở `/hongguo` — không còn nút «Thử Hongguo2».
4. Films UI tab Mùa mới → HG → `:8801/hongguo?sid=…` hoặc `?q=…`.
5. **Pass nếu:** redirect 302 + không còn nav Hongguo2 + deep-link mở tab Tìm / paste sid.
6. **Fail nếu:** `/hongguo2` vẫn trả HTML Hongguo2, hoặc Films UI còn link Hongguo2.

## Liên quan

- DECISIONS 11-06 drop Hongguo2
- Trước đó: `docs/fixes/2026-11-06-hongguo2-*.md` (lịch sử thử nghiệm)
