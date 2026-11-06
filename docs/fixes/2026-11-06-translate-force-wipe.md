# Bấm lồng tiếng / dịch xong rồi lại «force: dịch lại từ đầu»

- **Date:** 2026-11-06
- **Job / khu vực:** `88d80ba0be0f` · `POST /translate` · `_translate_flow`
- **Status:** fixed (code) / script đã khôi phục
- **Backup:** `Z:\PinelineV2_codebak\2026-11-06_translate-force-default\` · `…_restore-script-88\`

## Triệu chứng

Dịch xong (4342 VI) → chuẩn bị / bấm lồng tiếng → UI nhảy về `force: dịch lại từ đầu…`, `script.json` biến mất.

## Root cause

1. `_translate_flow` **hardcode** `run_translate(..., force=True)` — mọi `POST /api/jobs/{id}/translate` đều xoá `script.json` rồi dịch lại, kể cả khi body không có `force`.
2. UI nút «↻ Dịch lại toàn bộ» (`doTranslate('single')`) gọi đúng endpoint này; nút gần panel TTS dễ bấm nhầm / confirm qua.
3. TTS **không** tự gọi translate — nhưng sau wipe UI hiện bước Dịch đang chạy nên trông như «bấm TTS lại ra dịch».

## Evidence

- Sau done @ 22:18: `script.json` 4342 VI; ~22:21 `translate` lại `running` + `force: dịch lại từ đầu…`; `script.json` missing; còn `script.display.json` 6612 dòng.
- Code: `server._translate_flow` → `run_translate(..., True, ...)`.

## Fix

- `TranslateReq.force` (mặc định `False`); `_translate_flow(..., force=)`; chỉ wipe khi `force=true`.
- UI `doTranslate` single/2pass gửi `force:true` khi user xác nhận «Dịch LẠI».
- Khôi phục job: map `script.display.json` → `script.json` theo time overlap ASR (**4334/4342** VI); mark translate done; TTS → pending (bản cũ 527 lệch).
- Sync V2/V4/V5. **Cần restart :8801** để nạp server fix.

## Recheck

1. Hard refresh UI3 job `88d80ba0be0f` — Dịch = done, có bản Việt; không còn force-running.
2. Bấm **▶ Tạo giọng** (không bấm «Dịch lại toàn bộ») → TTS chạy, `script.json` vẫn còn.
3. **Pass nếu:** TTS tiến triển trên ~4342 câu; script không bị xoá.
4. **Fail nếu:** lại thấy `force: dịch lại từ đầu` sau khi chỉ bấm TTS.

## Liên quan

- Follow-up ghost `.stop`: `docs/fixes/2026-11-06-translate-stop-ghost.md`
- 8 câu VI trống sau restore → có thể `translate-fill` (không force).

## Follow-up

- **2026-11-06 ~23:57 (test-coverage):** V5 `_translate_flow` vẫn hardcode `force=True` (V2/V4 đã `bool(force)`). Sửa → `force=bool(force)` qua `_run_translate_engine`. Pytest `tests/test_translate_force_default.py` (4 passed). Backup `Z:\PinelineV2_codebak\2026-11-06_v5-swarm-test\`. **Cần restart :8805** (hoặc process V5) để nạp — không restart trong pass này.
- Recheck test: `python -m pytest tests/test_translate_force_default.py -q` → **Pass nếu** 4 passed; **Fail nếu** draft call còn `force is True` khi `force=False`.
