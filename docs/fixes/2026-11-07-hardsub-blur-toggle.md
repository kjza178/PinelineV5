# Thêm bật/tắt che hardsub (blur)

- **Date:** 2026-11-07
- **Job / khu vực:** mux / batch_config / UI3 / Films Settings
- **Status:** fixed

## Triệu chứng

Không có lựa chọn turn on/off blur hardsub trên UI; mux luôn `hardsub_blur=True` mặc định dù batch_config đã có key.

## Root cause

`MuxReq` thiếu field `hardsub_blur`; `mux_job` không truyền vào `_do_render`. UI3/Films không expose checkbox.

## Evidence

- `MuxReq` trước: hết ở `vbitrate`; `_submit_claimed` dừng trước `speed_factor`/`hardsub_blur`.
- Sau: unit `tests/test_hardsub_blur_toggle.py`.

## Fix

- `server.py`: `MuxReq.hardsub_blur`; `mux_job` ghi `queue_opts` + truyền `1.0, hs_blur`.
- `index3.html`: `auto-hs-blur` / `mux-hs-blur` + BATCH_TO_AUTO / collectRunAllOpts / mux POST.
- `films_ui.html`: tab Render + lưu `/config` `hardsub_blur`.
- Backup: `Z:\PinelineV2_codebak\2026-11-07_hardsub-blur-toggle\`

## Recheck

1. Hard refresh UI3 + Films Settings → tab Render.
2. Tắt «Che hardsub (blur)» → Lưu / Nạp config batch → `GET :8802/config` thấy `hardsub_blur: false`.
3. Render mux 1 job với blur off → `queue_opts.hardsub_blur=false` trong manifest.
4. **Pass nếu:** config + mux tôn trọng off/on.
5. **Fail nếu:** tắt UI vẫn blur trên output / MuxReq bỏ field.

## Follow-up

- **P0 (bug hunt):** `RunAllReq` thiếu `hardsub_blur` → 1-click vẫn blur. Đã thêm field + `run_all` `render_kw` + `runAll()` dùng `collectRunAllOpts()`; `runOptsSummary` hiện blur; Films load `/config` trước early-return; `render_kwargs` dùng `_coerce` (tránh `bool("false")`).
- Recheck: uncheck blur → Chạy tự động → manifest `queue_opts.hardsub_blur=false`.

## Follow-up — bool("false") queue/render (P0)

- **Date:** 2026-11-07
- **Backup:** `Z:\PinelineV2_codebak\2026-11-07_hardsub-blur-coerce\`
- **Root cause:** `_queue_run_one` / `_auto_pipeline` dùng `bool(opts["hardsub_blur"])`; `render.py` `bool(user_hs_blur)` từ `queue_opts` — chuỗi `"false"` vẫn True.
- **Fix:** `batch_config.as_bool`; server queue/auto dùng `as_bool`; `render.py` parse string off/on; Films `loadSettings` nạp `/config` trước early-return `/api/settings`.
- **Recheck:** `pytest tests/test_hardsub_blur_toggle.py` → pass; `as_bool("false") is False`; sau restart :8801 queue với `"hardsub_blur":"false"` không blur.

## Follow-up — recheck P1/P2 ([Blur toggle recheck](7fc918a8-acb9-4745-b966-14b4caf643a7))

- **Date:** 2026-11-07
- **Backup:** `Z:\PinelineV2_codebak\2026-11-07_hardsub-blur-p1\`
- **Applied:**
  - Queue stamp `hardsub_blur: as_bool(...)` (không chỉ `**opts`).
  - V5 `core/batch_config.py` `as_bool` + `render_kwargs` `_coerce`; `engines/render.py` string-safe + meta `off`.
  - Root `render.py` log `hardsub=off` khi tắt; Films checkbox đã parse `"false"`/`"off"`.
- **P0 còn:** restart `:8801` khi idle (OpenAPI live thiếu field).

## Liên quan

- Swarm: [Blur toggle bug hunt](369526d0-2b88-4bb2-91d3-e203342b58e0).
- Cần **restart :8801** để nạp `RunAllReq`/`MuxReq` (khi idle).

## Follow-up

- **Date:** 2026-11-07 (~01:00)
- **UI audit** hardsub blur + combine/merge: `mux-hs-blur` panel luôn `checked` → bỏ qua `auto-hs-blur=false`. Fix: init từ `auto-hs-blur` khi dựng mux panel (`hsBlurOn`).
- `films_ui.html`: xoá `doCopyGptPrompt` trùng (bản cũ chết, bản `buildIntegratedMasterPrompt` thắng).
- `switchSettingsTab` đã có `'render'`; helpers combine/merge đủ; `/films/mergeable` trước catch-all OK.
- Backup: `Z:\PinelineV2_codebak\2026-11-07_hardsub-blur-toggle\`
- Sync V4/V5 (+ `static/films_ui.html`, `static/ui/films_ui.html` dup).
- **Recheck:** hard refresh UI3 → tắt Auto «Che hardsub» → mở bước Render → checkbox mux phải tắt; Copy Prompt Meta chỉ 1 hành vi master prompt.

## Follow-up — SAFE autofix (stale V5 static/ui + null guards)

- **Date:** 2026-11-07 (~00:50)
- **Backup:** `Z:\PinelineV2_codebak\2026-11-07_hardsub-blur-autofix\`
- **Applied:**
  - Sync live V5 UI: `static/ui/index3.html` + `static/ui/films_ui.html` ← root (had 0 `hardsub_blur` / no Render tab; routes serve `static/ui` first).
  - Null-guards: `films_ui` `loadSettings`/`saveSettings` cfg-* + `st-save-msg`; `index3` `queueBatchPush` `if(!el) return`.
  - Sync same UI files V2→V4→V5 (+ `static/films_ui.html`).
- **Skipped:** wholesale `engines/render.py` / `core/batch_config.py` (already have `hardsub_blur`; diff = package imports only). No separate V5 package `MuxReq`. Did **not** restart `:8801` (jobs busy).
- **Evidence live:** OpenAPI `:8801` MuxReq **chưa** có `hardsub_blur` → cần restart khi idle. Sidecar `:8802` `/config` đã có `hardsub_blur: true` — không cần restart.
- **Recheck:** hard refresh V5 `/` + `/films/ui` → thấy blur checkbox / tab Render; sau restart `:8801` POST mux `hardsub_blur:false` phải vào `queue_opts`.

## Follow-up — SAFE autofix (UI string-bool + run_all/mux as_bool)

- **Date:** 2026-11-07 (~00:55)
- **Backup:** `Z:\PinelineV2_codebak\2026-11-07_hardsub-blur-safefix2\`
- **Applied:**
  - `films_ui.html` `loadSettings`: coerce `"false"`/`"off"` → uncheck (không dùng `!== false`).
  - `index3.html` `autoPrefApply`: checkbox coerce string false; `runOptsSummary` nhận `'false'`/`0`.
  - `server.py` `run_all` + `mux_job`: `batch_config.as_bool(getattr(...))` thay `bool(...)`.
  - Tests mirror `as_bool`; 22 passed.
  - Sync V2→V4→V5 + `static/films_ui.html` + `static/ui/{index3,films_ui}.html`.
- **Skipped / leftover P0:** live OpenAPI `:8801` vẫn thiếu `MuxReq.hardsub_blur` / `RunAllReq.hardsub_blur` cho đến khi restart idle (không restart theo lệnh).
- **Recheck:** hard refresh UI3/Films; tắt blur → summary «blur off»; sau restart `:8801` mux/run-all `hardsub_blur:false` vào `queue_opts`.
