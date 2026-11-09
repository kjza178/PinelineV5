# Restore Hongguo1 nguyên bản + tách Hongguo2

- **Date:** 2026-11-08
- **Job / khu vực:** `/hongguo` vs `/hongguo2`, backend bridge
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-08_hg1-isolate\` + `…_hongguo1-boot\`

## Triệu chứng

User: sửa Hongguo2 làm `/hongguo` (classic) có vẻ hỏng; muốn restore nguyên bản và làm Hongguo2 riêng, không đụng.

## Root cause

Cùng `HG_BACKEND=rpc` + helper singleton → Hongguo2 (poll/library/qualities/stop) tranh lock với Hongguo1. Đã sửa tạm `hongguo.html` (boot song song) — lệch bản gốc.

## Fix

1. **Restore** `hongguo.html` từ `2026-11-08_hongguo1-boot` (trước patch boot).
2. **`hg_ui_ctx.py`**: per-request backend theo `X-HG-UI` / Referer (module không reload).
3. **Hongguo2** `jget/jpost/jdel` gửi `X-HG-UI: 2` → luôn **RPC**.
4. **Hongguo1** (Referer `/hongguo`) → **http_first** (:8000 Downloader 1.x; fallback RPC nếu :8000 chết).
5. `server.py` default `HG_BACKEND=auto` (không ép rpc toàn cục).
6. **Quy ước:** không sửa `hongguo.html` cho feature Hongguo2 — chỉ `hongguo2.html` + bridge/rpc/routes.

## Recheck

1. Hard refresh `/hongguo` — HTML không chứa `hongguo board` / patch parallel.
2. `GET /api/hg/ping` + header `X-HG-UI: 2` → `backend: rpc`.
3. `GET /api/hg/ping` + `Referer: …/hongguo` → `http` nếu :8000 sống, else `rpc` fallback.
4. `/hongguo2` vẫn Browse/Downloads/Play.

## Liên quan

- Quyết định: `docs/DECISIONS.md` (tách UI1/UI2)
