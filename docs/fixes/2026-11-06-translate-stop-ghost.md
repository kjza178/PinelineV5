# Phần 6 «đang dịch» nhưng không thấy tiếng Việt (script.json 404)

- **Date:** 2026-11-06
- **Job / khu vực:** `88d80ba0be0f` · translate · `.stop`
- **Status:** fixed
- **Backup:** (patch nhỏ `server.retranslate_job`)

## Triệu chứng

Job *Thiên phú vô song… Phần 6* UI báo dịch (`force: dịch lại từ đầu…` 0%) nhưng không có bản Việt; `GET …/file/script.json` → 404.

## Root cause

1. User Stop lúc mux → `ffmpeg lỗi: stopped by user` + file `.stop`.
2. `POST /api/jobs/{id}/translate` **không** gọi `_clear_stop` (khác mux/TTS).
3. Worker vào `run_translate(force=…)` → xoá `script.json` rồi gặp `.stop` → `stopped by user`.
4. Manifest kẹt `translate=running` progress 0; không process nào chạy. Queue rỗng.

## Evidence

- Log: `[trans] 88d80ba0be0f: nhận .stop → dừng dịch` lặp sau mỗi `POST /translate`.
- Disk: `script.json` missing; `.stop` còn; `n_total=4342`; backup chỉ 527/795 câu.

## Fix

- `server.retranslate_job`: `_clear_stop(job_id)` trước `_claim_stage`.
- Job này: xoá `.stop`; đánh `translate=failed` + error rõ (hết ghost running).
- **Cần:** chạy lại dịch (force) — bản full đã bị xoá, bak không đủ 4342 câu.

## Recheck

1. Hard refresh job `88d80ba0be0f` — không còn «đang dịch» 0% giả.
2. `POST /translate` (force) → `.stop` không còn; progress tăng; `script.json` xuất hiện.
3. **Pass nếu:** script.json có ~4342 câu VI; UI hiện bản dịch.
4. **Fail nếu:** lại `[trans] nhận .stop` ngay sau khi bấm dịch (không Stop tay).

## Liên quan

- Mux fail trước đó: `stopped by user` @ 73%.
- TTS/ASR đã done; chỉ thiếu bản dịch sau force.

## Follow-up

- **Date:** 2026-11-06 ~21:25
- **User:** «có» → restart :8801 + dịch lại `88d80ba0be0f`.
- **Live:** sau restart, `POST /translate` force chạy ổn — `script.json` xuất hiện; progress tăng (~227/4342 @ 21:27); không còn ghost `.stop` trong cửa sổ theo dõi.
- **Done @ 22:18:** `translate=done`, `script.json` **4342/4342** có `vi`; cur=`đủ bản dịch`; không `.stop`.
- **Harden (disk, chờ restart):** `_clear_stop` unlink cả `WORK_ROOT` + `D:\PinelineV2_work`; `_run_translate` clear lại ngay trước `_translate_flow`. Backup `Z:\PinelineV2_codebak\2026-11-06_clear-stop-dual\`. Sync V4/V5.
- **Watchdog:** `D:\PinelineV2_tmp\_tr_watch_88.py` (auto-clear `.stop` nếu tái xuất hiện) — kết thúc sạch, không thấy STOP ghost.
