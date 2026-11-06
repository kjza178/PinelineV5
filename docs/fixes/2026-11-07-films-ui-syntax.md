# Films UI :8802 — onclick/`jq` chết + Settings/Uploader 404

- **Date:** 2026-11-07
- **Job / khu vực:** `http://127.0.0.1:8802/films/ui` · `films_ui.html` · sidecar
- **Status:** fixed (syntax/onclick + autopub load) | partial (Settings/Uploader API chưa port)
- **Backup:** `Z:\PinelineV2_codebak\2026-11-07_films-ui-jq-html\` (+ prior `…_films-ui-syntax\`)

## Triệu chứng

UI «lỗi quá»: nhiều nút Test / Meta / Xoá / Copy không chạy; Cài đặt / Đăng YT trống hoặc báo lỗi; auto-publish toggle không load.

## Root cause

1. **P0:** `jq=JSON.stringify` nhét vào `onclick="…"` → dấu `"` cắt attribute HTML → handler truncate / no-op. (Fix trước dùng `jq` để tránh `'`, nhưng quên HTML-escape.)
2. **P1:** `loadAutoPublishConfig` đòi `res.ok && res.config` trong khi GET :8802 trả **flat** `{enabled,…}`.
3. **P0 (API):** `/api/settings*` và `/api/uploader*` **404** trên `agent_tele_cmd` :8802 (routes chỉ có trên FastAPI V4/V5) — không phải lỗi cú pháp HTML.

## Evidence

- Syntax audit: `node --check` script OK; Chromium: attr trước fix thành `fn(` cắt ngang.
- Sau fix: `getAttribute('onclick')` decode đúng `openTestBlockModal("…", …)`; probe `jq` + DOMParser PASS.
- API: `GET /api/auto-publish/config` 200 flat; `/api/uploader/status` + `/api/settings` 404.

## Fix

- `jq`: `JSON.stringify(…).replace(/&/g,'&amp;').replace(/"/g,'&quot;')`
- `loadAutoPublishConfig`: nhận flat **hoặc** `{config}`
- `loadUploader` / `loadSettings`: báo rõ 404 trên :8802
- `doCreateCanvaDesign`: null-guard nút thiếu DOM
- Sync V2 → V4 → V5 → `static/ui`
- Swarm: syntax audit + runtime audit + autofix leftover `'${…}'`

## Recheck

1. Hard refresh `http://127.0.0.1:8802/films/ui` (Ctrl+F5).
2. Bấm **🛡️ Test** trên 1 mùa — modal mở, không silent fail.
3. Tab Done: auto-pub checkbox phản ánh config server.
4. **Pass nếu:** Test/Meta/Xoá onclick chạy; autopub load đúng.
5. **Fail nếu:** nút động không phản hồi; hoặc Settings/Uploader vẫn 404 (chưa port API — expected).

## Liên quan

- `docs/fixes/2026-11-06-films-ui-studio-test.md`
- Review: `docs/reviews/2026-11-07-films-ui-swarm.md`
- Còn mở: port `routes_uploader_settings` vào :8802 **hoặc** proxy sang :8801/:8804.
