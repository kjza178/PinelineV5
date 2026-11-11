# REVIEW lỗi bị coi là đã soát · park treo hàng đợi · Brain V4 điều khiển nhầm V2

- **Date:** 2026-11-11
- **Job / khu vực:** `translate.run_review` · `server._auto_gpu` / `_queue_park_ready` · `preset_switcher` · `agent_brain` · router V4
- **Status:** fixed (V2, V4, V5) — chờ restart từng cổng
- **Backup:** `Z:\PinelineV4\.backup_edit_20261111_fix-batch\` (không truy cập được `Z:\PinelineV2_codebak` / `snapshot.py` từ phiên này)

## Triệu chứng

1. Aurora/local lỗi giữa lượt REVIEW → job vẫn đi TTS với câu chưa soát.
2. Sau REVIEW còn câu chưa `rv` → job park `waiting_review`, hàng đợi đứng mãi (phải kill CLI + queue stop bằng tay, vd p02 00:52 11/11).
3. Brain chạy trong V4 gọi `http://127.0.0.1:8801` → thao tác queue/job của V2.
4. `/films` API, uploader settings không có trên :8804.

## Root cause

1. `_review_chunk_with_fallback` trả `{}` khi lỗi; `_apply_result` đánh `rv=1` cả lô bất kể.
2. `_queue_park_ready` chỉ True khi `unrev==0`, mà trong lúc park không tác nhân nào soát.
3. `agent_brain.py`/`agent_brain_context.py` chép từ V2 với URL cứng :8801.
4. `server.py` chép từ V2 (không include router riêng của V4).
Thêm: `switch_preset` không khoá; fix áp vượt `chunk_exp`; QA gate gọi `run_review` lần 2 chạy lại hậu kỳ LLM.

## Evidence

- `translate.py` (trước fix) `:195-201`, `:3174-3176`, `:3224-3229`; `server.py:6362-6390`; `agent_brain.py:620-1055`; `routes_films.py:4`.
- `scripts/tree_audit.py` V4: ERROR 10 (cổng) trước → 0 sau.

## Fix

- `translate.py`: lô lỗi → `None`, không `rv`, thử lại tuần tự (`REVIEW_RETRY_BACKOFF_SEC`), còn lỗi → `RuntimeError`; lọc fix theo `chunk_exp`; trả sớm khi đã soát đủ.
- `server.py`: `review_retries`/`review_retry_at`, `QUEUE_REVIEW_RETRY_SEC`=300, `QUEUE_REVIEW_RETRY_MAX`=3 → quá thì HOLD `review_failed`; include router tuỳ cây; `PINELINE_PORT`.
- `preset_switcher.py`: `_SWITCH_LOCK`.
- `agent_brain*.py`, `meta_studio.py`, `agent_tele_cmd.py`, `agent_tool_loop.py`: URL theo cổng thật.

## Recheck

1. `python -m pytest -q tests\test_review_fail_not_rv.py tests\test_park_review_retry.py tests\test_job_queue_worker.py tests\test_queue_run_one.py tests\test_review_parallel_workers.py`
2. `python scripts\tree_audit.py --peers Z:\PinelineV2 Z:\PinelineV5` → ERROR=0.
3. Restart :8804 → log `[startup] router routes_films ON`, `router routes_uploader_settings ON`; `GET :8804/api/agent/status` ok; Brain log không còn request tới :8801.
4. Job thử: cắt mạng Aurora giữa REVIEW → log `lô … lỗi — giữ chưa rv`, `Thử lại N lô`, rồi `PARK ghế`; sau 300 s job chạy lại cùng ghế.
5. **Pass nếu:** không câu nào `rv=1` mà chưa được LLM trả kết quả; queue không đứng quá `RETRY_SEC × RETRY_MAX`; không request :8801 từ V4.
6. **Fail nếu:** TTS chạy khi còn lô lỗi; job park `waiting_review` không tự chạy lại; Brain V4 đổi queue V2.

## Liên quan

- `docs/reviews/2026-11-11-v4-v5-port-review.md`; V2: `Z:\PinelineV2\docs\reviews\2026-11-11-codebase-overview-bugs-improve.md` (B1–B4, B7). Đã áp V2 (chép 7 file đã sửa, giống hệt bản gốc V2) + V5 (qua sync_from_v2).
