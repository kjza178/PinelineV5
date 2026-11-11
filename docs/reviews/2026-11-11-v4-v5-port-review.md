# Review port V4 + V5 — subagent · bug · auto-fix · hướng phát triển

- **Date:** 2026-11-11 ~02:45
- **Phạm vi:** `Z:\PinelineV4` (:8804), `Z:\PinelineV5` (:8805), so với `Z:\PinelineV2` (:8801). Đọc code + AST + hash; không restart, không đụng `work/`.
- **Công cụ mới (cả 3 cây):** `scripts/tree_audit.py` (import vỡ / cổng lạ / module trùng / file bị sync đè), `scripts/brain_build.py` (hiểu bố cục package, trang `generated/duplicates.md`), subagent `port-sync-guardian` + lệnh `/sync-check`.
- **Báo cáo gốc V2:** `Z:\PinelineV2\docs\reviews\2026-11-11-codebase-overview-bugs-improve.md` (B1–B11 — áp dụng cho V4 vì code giống).

## 1. Kết luận

| Cây | Trạng thái trước | Sau lượt này |
|---|---|---|
| **V4** | Chạy được nhưng: Brain điều khiển nhầm **V2 :8801**; mất router `/films` + uploader settings; B1/B2/B3/B4/B7 như V2 | **Đã sửa** (chờ restart :8804). `tree_audit` ERROR = 0 |
| **V5** | **Không khởi động được**: `server.py` bị chép đè bằng bản V2 (import phẳng không tồn tại trong bố cục package); 21 cặp module root/package lệch nội dung | **Chưa sửa — cần user chốt hướng** (mục 4). `tree_audit` ERROR = 51 |

Nguyên nhân gốc chung: quy trình "Sync V2/V4/V5" = **chép nguyên file root của V2** sang cây khác. Với V4 (phẳng) gần như ổn trừ phần riêng của V4; với V5 (package) phá vỡ cấu trúc. `docs/STATE.md`, `docs/ARCHITECTURE.md` 3 cây giống hệt nhau (V5 STATE ghi "Hiện trạng PinelineV4").

## 2. Bug V4 + V5

| # | Mức | Cây | Bug | Bằng chứng | Trạng thái |
|---|---|---|---|---|---|
| P1 | **P0** | V5 | `server.py` V5 == V2 (md5 `46a60f8c`), import `manifest, download, asr, vram, ocr, separate, render_fx, clone_tts, playlist, subs…` không có ở root V5 → `ModuleNotFoundError` khi start | `tree_audit` V5: 51 ERROR | Chờ quyết định |
| P2 | **P0** | V4, V5 | `agent_brain` cứng `http://127.0.0.1:8801` (10 chỗ) + `agent_brain_context` → Brain của V4/V5 **xếp/dừng queue, chạy stage, reset job trên V2** | `agent_brain.py:620-710, 796, 1016, 1055` | **V4 fixed** |
| P3 | P1 | V4 | `server.py` (bản V2) không include `routes_films`/`routes_uploader_settings` → API films/meta/uploader trên :8804 mất (chỉ còn trang HTML) | `routes_films.py:4` "gắn trực tiếp vào server.py (port 8804)"; server không có `include_router` | **Fixed** |
| P4 | P1 | V5 | 21 cặp module root ↔ package khác nội dung (`config`, `batch_config`, `translate`, `agent_core`, `routes_*`…) — sửa V2 sync vào root, package (theo LAYOUT là bản sống) đứng yên từ 04–09/11 | `generated/duplicates.md` V5 | Chờ quyết định |
| P5 | P2 | V4, V5 | `meta_studio`, `agent_tele_cmd` poster URL cứng :8801; `agent_tool_loop --base` mặc định :8801 | `tree_audit` | **V4 fixed** |
| P6 | P2 | 3 cây | `docs/STATE.md`, `docs/ARCHITECTURE.md` giống hệt giữa 3 cây; CHANGELOG V4/V5 chứa mục chỉ thuộc V2 | `tree_audit --peers` | Ghi chú; tách khi user duyệt |
| B1 | **P0** | V4 (=V2) | Lô REVIEW lỗi vẫn bị đánh `rv=1` | xem báo cáo V2 | **V4 fixed** |
| B2 | **P0** | V4 (=V2) | Park `waiting_review` treo hàng đợi vĩnh viễn | xem báo cáo V2 | **V4 fixed** |
| B3 | P1 | V4 | `switch_preset` không khoá (24 thread + Brain) | | **V4 fixed** |
| B4 | P1 | V4 | Fix REVIEW áp vượt biên lô | | **V4 fixed** |
| B7 | P2 | V4 | QA gate soát lần 2 chạy lại pronoun GPT + hang LLM | | **V4 fixed** |
| B5, B6, B8–B11 | P2–P3 | V4 | Như V2 | | Chưa sửa (xem báo cáo V2) |

## 3. Đã sửa ở V4 (auto-fix)

Backup bản gốc: `Z:\PinelineV4\.backup_edit_20261111_fix-batch\` (translate, server, preset_switcher, agent_brain, agent_brain_context, meta_studio, agent_tele_cmd, agent_tool_loop). Fix log: `docs/fixes/2026-11-11-review-fail-park-port.md`.

| File | Thay đổi |
|---|---|
| `translate.py` | `_review_chunk_with_fallback` trả `None` khi lô lỗi (kể cả không mở được local); `_apply_result` không đánh `rv` lô lỗi + chỉ nhận fix trong `chunk_exp`; thử lại tuần tự các lô lỗi (`REVIEW_RETRY_BACKOFF_SEC`, mặc định 20 s), còn lỗi → `RuntimeError` (job park); `run_review` trả sớm khi không còn câu chưa `rv` (bỏ hậu kỳ LLM lặp) |
| `server.py` | Park `waiting_review` có `review_retries` + `review_retry_at`; `_queue_park_ready` chạy lại job khi tới hạn (`QUEUE_REVIEW_RETRY_SEC`=300, `QUEUE_REVIEW_RETRY_MAX`=3) → quá lượt thành HOLD `review_failed` cần người; include router tuỳ cây `routes_films`, `routes_uploader_settings` (thiếu file thì bỏ qua → server.py vẫn dùng chung được với V2); `os.environ["PINELINE_PORT"]` = cổng thật lúc start |
| `preset_switcher.py` | `_SWITCH_LOCK` — chỉ 1 lượt switch llama tại một thời điểm |
| `agent_brain.py`, `agent_brain_context.py` | `_self_base()` (env `PINELINE_BASE` → `PINELINE_PORT` → 8801) thay 11 URL cứng |
| `meta_studio.py`, `agent_tele_cmd.py`, `agent_tool_loop.py` | URL poster / `--base` theo cổng thật |

**Kiểm chứng (trên VM, stub thư viện ngoài vì VM không có fastapi/pytest):**
- `tests/test_review_fail_not_rv.py` (mới) 4/4 pass · `tests/test_park_review_retry.py` (mới) 4/4 pass.
- Test cũ liên quan: `test_review_parallel_workers` 4/4, `test_review_pass1_upload` 4/4.
- `switch_preset` 8 thread → tối đa 1 lượt đồng thời.
- `tree_audit` V4: ERROR 10 → **0**. AST + kiểm import đủ cho 8 file sửa.
- **Trên Windows cần chạy:** `python -m pytest -q tests\test_review_fail_not_rv.py tests\test_park_review_retry.py tests\test_job_queue_worker.py tests\test_queue_run_one.py tests\test_review_parallel_workers.py`
- **Có hiệu lực sau restart :8804** (V4 hiện không chạy theo STATE).

## 4. V5 — cần chốt hướng

| Hướng | Làm gì | Ưu | Nhược | Công |
|---|---|---|---|---|
| **A. Giữ package (đúng LAYOUT.md)** | Viết lại import `server.py` + root agent sang `core.*`/`engines.*`/`agents.*`; port thay đổi V2 (04→11/11) vào bản package; dời ~40 file root vào `_to_delete/`; viết `scripts/sync_from_v2.py` có bảng ánh xạ | Kiến trúc sạch, đúng mục tiêu V5 | Nhiều việc; phải port tay ~1 tuần thay đổi | L |
| **B. V5 quay về phẳng như V2** | Chép đủ module phẳng còn thiếu từ V2 (manifest, asr, subs…), bỏ package | Chạy được nhanh, sync đơn giản | Bỏ công tái cấu trúc V5; V5 ≈ V4 | S |
| **C. Đóng băng V5** | Ghi rõ V5 hỏng, không sync tới khi có thời gian | Không tốn công | V5 tiếp tục lệch | — |

## 5. Hướng phát triển

1. **Một nguồn code, nhiều instance** (giải pháp gốc): V2/V4/V5 khác nhau chủ yếu ở cổng, TEMP, thư mục work, vài router/desktop. Gom về **một cây** + `instances/v2.json`, `v4.json`… (port, work_root, temp, routers bật) → hết "sync". Nếu chưa gộp được: `scripts/sync_from_v2.py` có allowlist file + bảng ánh xạ package, luôn chạy `tree_audit` trước/sau (ERROR phải = 0).
2. **Code không biết mình là cây nào**: mọi URL nội bộ qua `PINELINE_BASE/PINELINE_PORT`; router/feature tuỳ cây qua config, không qua chép file.
3. **Docs theo cây**: STATE/ARCHITECTURE/CHANGELOG riêng; CHANGELOG ghi "Sync tới V4/V5" kèm kết quả `tree_audit`.
4. **Second Brain (dev) cho từng cây** đã cài; thêm `/sync-check` vào workflow sync; brain-keeper viết MANUAL cho hotspot.
5. **AI agent runtime** (từ báo cáo V2): một chủ heal, audit log hành động, giới hạn quyền mutate của Brain LLM tick, eval set trước khi đổi model, circuit breaker LLM.
6. **Git**: 3 cây = 3 repo không có git → dùng git với branch/worktree mỗi instance là bước rẻ nhất để sync có diff thay vì chép đè.
