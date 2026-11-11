# V5 không khởi động được → chuyển về bố cục package bằng sync_from_v2

- **Date:** 2026-11-11
- **Job / khu vực:** toàn cây V5 (`server.py`, `core/`, `engines/`, `agents/`, `http_routes/`, `tools/`)
- **Status:** fixed (chờ chạy pytest + restart :8805 trên Windows)
- **Backup:** `.backup_sync_20261111_0252\` (+ `_0253`, …) giữ mọi file bị ghi; bản trùng root dời vào `_to_delete\root_dupes_20261111_0252\`

## Triệu chứng

`server.py` V5 không chạy (`ModuleNotFoundError: manifest`), 35 file root trùng package và lệch nội dung.

## Root cause

"Sync V2/V4/V5" chép nguyên file root V2 (import phẳng) sang V5 (bố cục package theo `docs/LAYOUT.md`).

## Fix

- Mới `scripts/sync_from_v2.py`: đặt module V2 vào đúng chỗ package, viết lại 531 import phẳng → package, đổi 36 chỗ `Path(__file__).parent` về gốc theo độ sâu, bootstrap `sys.path` cho script chạy trực tiếp, dời bản trùng root vào `_to_delete/`.
- Module mới trong package: `agents/agent_brain.py`, `agent_brain_context.py`, `agent_hang_fix.py`, `agent_quality.py`, `films_merge_api.py`, `hg_ui_ctx.py`, `uploader_settings_api.py`, `engines/pronoun_register_policy.py`.
- `http_routes/routes_films.py`: base URL mặc định theo `PINELINE_PORT` (trước cứng :8804).
- Root còn đúng 3 entry: `server.py`, `app_desktop.py`, `restart_server.py`.

## Evidence / Recheck

1. `python scripts\tree_audit.py --peers Z:\PinelineV2 Z:\PinelineV4` → ERROR **0** (trước 51).
2. Import smoke (VM, thư viện ngoài giả lập): 85/85 module gồm `server` import được.
3. `python -m pytest -q tests\test_review_fail_not_rv.py tests\test_park_review_retry.py tests\test_optimize_b5_b6.py` (VM: 12/12 pass).
4. `python server.py --port 8805` → `/api/agent/status` 200; log `[startup] router http_routes.routes_films ON`.
5. Chạy 1 job thử: ASR subprocess khởi động được (`engines/asr/*.py`, `PYTHONPATH`).
6. **Pass nếu:** 1–5 đúng. **Fail nếu:** ImportError khi start/ASR, hoặc đường dẫn file dữ liệu sai (`voices/`, `static/`, `pineline.config.json`).

## Liên quan

- Lần sync sau: `python scripts\sync_from_v2.py --src Z:\PinelineV2` (dry-run) → `--apply` → `tree_audit`. Không chép tay nữa.


---

# Tối ưu đợt 11/11: dừng REVIEW song song chậm · audio run-all/mux lệch queue · restart chờ vô hạn · ghi plan không atomic

- **Date:** 2026-11-11
- **Job / khu vực:** `translate.run_review` · `server.run_all` / `mux_job` · `restart_server` · `server._run_engine`
- **Status:** fixed (V2, V4, V5) — chờ restart từng cổng
- **Backup:** `.backup_edit_20261111_optimize\` (V2, V4); V5 qua `.backup_sync_*`

## Triệu chứng

1. B5: bấm Dừng khi REVIEW chạy 24 luồng → job chỉ dừng khi request LLM đang bay xong (tới `CHATGPT_TIMEOUT` 900 s).
2. B6: bấm Run-all / Mux từ UI mà client không gửi `audio_mode` → ra `voice_bgm` 0.6, khác queue (`sfx_lib`).
3. B8: `restart_server --after-current` chờ mãi khi job hiện tại đang park HOLD.
4. B10: `glossary.json` / `style_lock.json` / `script.display.json` ghi bằng `write_text` (12 module đọc) → đọc trúng lúc ghi = plan rỗng.

## Root cause

1. `with ThreadPoolExecutor` chờ mọi thread khi thoát; `.stop` chỉ kiểm khi một future xong.
2. `MuxReq` / `RunAllReq` mặc định cứng; `run_all` / `mux_job` truyền thẳng `req.audio_mode`.
3. Vòng chờ yêu cầu `not current`, job park giữ `current`.
4. Không dùng `atomic_write_json` đã có.

## Fix

- `translate.py`: `_fut_wait(..., timeout=2, FIRST_COMPLETED)` + `ex.shutdown(wait=False, cancel_futures=True)`; 8 chỗ ghi → `atomic_write_json(..., fsync=False)`.
- `server.py`: `_req_audio(work_dir, req)` — trường client gửi (`model_fields_set`) → `queue_opts` đã pin → config batch.
- `server.py` (cho V5): `_engine_script_path()` tìm script engine ở root hoặc `engines/asr`, …; `PYTHONPATH` = gốc dự án cho tiến trình con; router tuỳ cây thử thêm `http_routes.*`.
- `restart_server.py`: `_job_parked()` → job park HOLD/soát coi là rảnh để restart.
- `agent_autopilot.py`, `migrate_work.py`: base URL theo `PINELINE_BASE`.

## Recheck

1. `python -m pytest -q tests\test_optimize_b5_b6.py tests\test_review_fail_not_rv.py tests\test_park_review_retry.py tests\test_review_parallel_workers.py tests\test_job_queue_worker.py tests\test_queue_run_one.py`
2. `python scripts\tree_audit.py` → ERROR=0.
3. Restart cổng → REVIEW song song, bấm Dừng → log `DỪNG lúc soát` trong < 10 s.
4. Bấm Mux từ UI (không chọn audio) trên job queue `sfx_lib` → output dùng `sfx_lib`.
5. **Pass nếu:** cả 4 điểm trên đúng. **Fail nếu:** dừng > 10 s, audio khác `queue_opts`, restart treo khi job park.

## Liên quan

- `docs/reviews/2026-11-11-codebase-overview-bugs-improve.md` (V2) · `docs/reviews/2026-11-11-v4-v5-port-review.md`
