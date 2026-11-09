# Restore Hongguo classic + tách hoàn toàn Hongguo2

- **Date:** 2026-11-08
- **Job / khu vực:** `/hongguo` vs `/hongguo2`, `/api/hg` vs `/api/hg2`
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-08_hg1-full-split\`

## Triệu chứng

User: classic bị kéo license prove / RPC WinUI; yêu cầu restore đúng **trước khi làm Hongguo theo WinUI**, tách biệt hoàn toàn với hongguo2.

## Root cause

Chung `/api/hg/*` + fallback RPC (`http_first` / `HG_BACKEND`) → submit/retry classic gọi helper → `ensure_licensed` / HgLicActivate (alert `too_many_activations`).

## Fix

1. Restore `hongguo.html` từ `2026-11-06_drop-hongguo2` (pre WinUI revive); bỏ nút «Thử Hongguo2».
2. **Namespace tách:**
   - `/api/hg/*` → **HTTP only** (Downloader :8000), không license
   - `/api/hg2/*` → rewrite → `/api/hg/*` + **RPC** (WinUI helper + license)
3. `hongguo2.html` chỉ gọi `/api/hg2/…` (và `/api/hg2/disk`).
4. Middleware `server._hg1_hg2_split` + `hg_ui_ctx.force`.

## Recheck

1. Hard refresh `/hongguo` — không nút Hongguo2; ping pill không đụng license alert.
2. `GET /api/hg/ping` → `backend: http`
3. `GET /api/hg2/ping` → `backend: rpc`
4. Submit từ classic → lỗi Downloader/queue, **không** `ChallengeAsync` / `too_many_activations`
5. `/hongguo2` Browse/Downloads vẫn RPC

## Liên quan

- DECISIONS 11-08 full split
- Supersede isolate một phần (`hongguo1-restore-isolate`)
