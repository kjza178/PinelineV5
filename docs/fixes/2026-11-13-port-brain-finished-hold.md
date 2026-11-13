# Port V2→V5: Brain — job đã xong không heal + park tự động ≠ HOLD cần người

- **Ngày:** 2026-11-13 · **Agent:** R5 · **Cây:** `Z:\PinelineV5` (bố cục package) · **Nguồn:** `Z:\PinelineV2` (chỉ đọc)
- **Nguồn V2:** `docs/fixes/2026-11-13-brain-finished-hold.md` (agent N) — triệu chứng, gốc lỗi, bảng vòng đời tạm dừng xem ở đó.
- **Backup:** `Z:\PinelineV5\.backup_edit_20261113_agentR5\` (bản gốc giữ đường dẫn; `_md5_before.txt`, `_md5_after.txt`; `V6\` = bat trước sửa; `_transfer\` = gói chuyển bản sao test). File mới không có bản gốc.
- **Status:** trên đĩa V5. **Cần restart :8805** (brain/watch/heal chạy trong tiến trình server; bot `agent_tele_cmd` nếu chạy từ V5).

## Cách port
3-way merge (`diff3 -m`) từng file: base = `Z:\PinelineV2\.backup_edit_20261113_agentN\` (trước agent N), ours = V5, theirs = V2 hiện tại; base/theirs đều đi qua `scripts/sync_from_v2.rewrite_imports` + `rewrite_file_paths`. 0 xung đột.

| V2 | V5 | Kết quả |
|---|---|---|
| `agent_hold.py` | `agents/agent_hold.py` | V5 == base → lấy V2: `job_finished`, `hold_class`/`hold_info`/`AUTO_PARK`/`NEED_BY_HOLD`/`PARK_KEYS`, `manual_override` gỡ khoá park |
| `agent_heal.py` | `agents/agent_heal.py` | merge (giữ `core.job_queue` của V5): `diagnose_job` finished, 3 detector `tts_not_started`/`asr_bad`/`tts_missing_clips` |
| `agent_brain.py` | `agents/agent_brain.py` | merge (giữ `core.machine` URL): `_hold_event` park_set/hold_set, sense/apply/`_deep_focus`/remind/`clear_stale_holds` bỏ job xong |
| `agent_brain_notify.py` | `agents/agent_brain_notify.py` | V5 == base → lấy V2: `park_text`, «⏸ … tạm dừng …» / «⛔ … HOLD: … Cần bạn» |
| `agent_brain_context.py` | `agents/agent_brain_context.py` | merge (giữ `core.machine`): snapshot `hold_class`, `finished` |
| `routes_agent.py::_agent_resume` | `http_routes/routes_agent.py` | V5 == base → lấy V2: «Chạy tiếp» gỡ `review_retries/review_retry_at/simple_park/split_wait_parts` |
| `tests/test_agent_brain_notify.py` | như cũ | merge (giữ patch `agents.agent_core`/`core.*` của V5): `test_snapshot_hold_set` kỳ vọng ⛔ |
| MỚI `tests/test_brain_finished_hold.py` | `tests/` | 23 ca, import `agents.*` |

`server.py` V5 KHÔNG đổi (như V2). Không hàm nào bị xoá/đổi chữ ký (so AST).

## Evidence / Recheck
- Bản sao Linux (Python 3.13, stub fastapi/soundfile/yt_dlp/google), `AGENT_BRAIN=0`, toàn bộ `tests/`: trước **25 failed / 403 passed / 4 skipped / 3 errors** → sau **25 failed / 426 passed / 4 skipped / 3 errors**, danh sách FAILED/ERROR y hệt. Nhóm [1] bat (15 file): **271 passed / 4 skipped**. `test_brain_finished_hold` 23 passed; `test_agent_brain_notify` 28 passed.
- md5 file ghi trên đĩa == bản đã test. `tree_audit` ERROR=0; import `server` OK.
- Windows: `Z:\PinelineV6\scripts\test_v5_simple_demucs.bat` — [1] kỳ vọng **271 passed / 4 skipped / 0 failed**; [2] FAILED không tăng.
- Recheck: **Pass** (bản sao) · **chờ** Windows + restart :8805.

## Recheck sau restart :8805
1. Job V5 đã xong (output.mp4 / đã đăng) mà thiếu `asr.json`/`tts.json` → `agent_brain.log` không còn «heal thất bại», route `scan_failed` không liệt kê.
2. Job simple park (`held_at=waiting_review`) → Telegram «⏸ … tạm dừng soát dở N câu, tự thử lại lúc HH:MM (lần k/max)», không «Cần bạn».
3. Park vượt max → `review_failed` → 1 tin «⛔ … HOLD: … Cần bạn: …».
4. Bấm «Chạy tiếp» → manifest không còn `review_retries/review_retry_at/simple_park`.

## Liên quan
V2: `docs/fixes/2026-11-13-brain-finished-hold.md`. V5: `2026-11-12-port-brain-hold-pipeline.md` (P5), `2026-11-13-port-preflight-slice-junk.md` (Q5). V4/V6 chưa port.
