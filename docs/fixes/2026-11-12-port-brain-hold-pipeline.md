# Port V2→V5: Second Brain (Telegram events + gỡ HOLD khi chạy tay) + đóng dấu luồng dịch theo job

- **Ngày:** 2026-11-12 · **Agent:** P5 · **Cây:** `Z:\PinelineV5` (bố cục package) · **Nguồn (chỉ đọc):** `Z:\PinelineV2`
- **Nguồn V2:** `docs/fixes/2026-11-12-brain-telegram-hold.md` (G), `2026-11-12-brain-notify-v2.md` (H), `2026-11-12-translate-simple-default.md` (F2). Diff lấy từ `.backup_edit_20261112_agent{G,H,F2}\` (bản gốc) → bản V2 hiện tại.
- **Backup V5:** `Z:\PinelineV5\.backup_edit_20261112_agentP5\` (giữ đường dẫn; `pineline.config.json.bak`; `V6\scripts\test_v5_simple_demucs.bat`; `docs\`). md5 trước/sau: `_md5_before_after.tsv`; bản mới: `_new\`; nguồn đã chuyển: `_transfer\`.
- **Cần restart:** :8805 (server V5 — brain/watcher/hold chạy in-process). Không cần restart :8802. Không đụng :8000 / :8083.

## Triệu chứng (ở V2, V5 cùng code cũ)
Brain gửi «Brain báo cáo» mỗi 2' + «Brain DECISION» (văn LLM, markdown/`<badge>`) mỗi tick; HOLD cũ không gỡ khi job đã xong / khi người dùng chạy tay TTS/mux; heal lúc khởi động đụng job đang chạy; engine lỗi không để lại log. Dịch: job dở luồng cũ có thể bị chuyển sang simple giữa chừng (không có dấu luồng theo job).

## Cách port
3-way merge từng file: `base = V2 trước sửa`, `theirs = V2 hiện tại`, `ours = V5` — cả base/theirs đi qua `scripts/sync_from_v2.py` (`rewrite_imports`, `rewrite_file_paths`) để import đúng package rồi `git merge-file` (chỉ dùng như công cụ diff3, không đụng repo). Xung đột giải tay (dưới).

| V2 | V5 | Nội dung |
|---|---|---|
| `agent_brain.py` (G+H) | `agents/agent_brain.py` | `AGENT_BRAIN_TELEGRAM` mặc định `events`, `AGENT_BRAIN_TG_SEC` ≥600, sự kiện stage, `clear_stale_holds`, deep tick chỉ job có vấn đề, tin dựng theo mẫu, hoãn heal/LLM sau start; giữ `core.machine` (URL llama/aurora) của V5 |
| `agent_heal.py` | `agents/agent_heal.py` | `job_active`, `start_delay_sec`, note plan rỗng; **V5:** `job_active` đọc `sys.modules["core.job_queue"]` (V2: `job_queue`) |
| `agent_watch.py` | `agents/agent_watch.py` | hoãn heal đầu `AGENT_HEAL_START_DELAY_SEC`, bỏ job đang chạy, tin theo mẫu |
| MỚI `agent_brain_notify.py`, `agent_hold.py` | `agents/` | render tin; gỡ HOLD khi chạy tay / `hold_suppressed` |
| `routes_agent.py` | `http_routes/routes_agent.py` | `_HEAL_HOOKS.job_active`, `_agent_set_hold` tôn trọng override |
| `server.py` (H) | `server.py` | `Request` import, `_manual_hold_override` + 5 route (`run_stage`, `translate_fill`, `regen_tts`, `retranslate_job`, `mux_job`), `_auto_gpu` qa_brain + `hold_suppressed`, `_run_engine` + `_save_engine_tail` |
| `server.py` (F2) | `server.py` | `_translate_pipeline_simple(wd, fresh=)` → `cfg.job_pipeline`; điểm gọi `_process_gpu`, `_run_requested_review`, `_auto_gpu`, `_run_stage("translate")` (force=fresh), `translate_fill` (theo luồng job, trả `pipeline`), `_translate_flow`, `retranslate_job` (chốt luồng trước khi đánh running) |
| `translate_simple/cfg.py` (F2) | `engines/translate_simple/cfg.py` | `pipeline_default`, `LEGACY_VALUES` thêm off/0/false/no, `_infer_job_pipeline`, `job_pipeline` (ghi `Manifest.update`) |
| tests | `tests/test_agent_brain_events.py` (11), `test_agent_brain_notify.py` (28), `test_agent_hold_telegram.py` (14, I2) mới; `test_translate_simple.py` +6 `test_f2_*` | V5: `sys.modules["agents.agent_core"]`, `core.job_queue`, `core.config`, `http_routes/routes_agent.py` |
| config (G) | `config.json` + `pineline.config.json` | chỉ 2 dòng: `AGENT_BRAIN_TELEGRAM` report→**events**, `AGENT_BRAIN_TG_SEC` 120→**600** (V5 đặt tường minh ở cả 2 file → đè mặc định code; sửa tại chỗ, giữ CRLF) |

**Khác biệt so với V2 (cố ý):**
- Không port `_fill_pending_park_on/_n_fill_pending*/_park_fill_pending` (translate-b3, xung đột trong cùng hunk) — V5 chưa có translate-b2/b3 (như F5).
- `_translate_pipeline_simple` lỗi import → luồng cũ (theo V2 F2; F5 cũ dùng env).
- Mục 3 (flake `test_translate_simple_next.py`: `_VOLATILE` có `applied_at`, `glossary.json` qua `_strip`) — **V5 đã có sẵn** (F5 port bản V2 mới), không sửa.
- **I2 (lệnh Telegram người dùng = chạy tay → gỡ HOLD): ĐÃ port** (đợt 2, sau khi V2 xong; base `.backup_edit_20261112_agentI2\`): `agents/agent_hold.py` (`user_context`, `user_caller`, `request_source`, `manual_source`), `http_routes/routes_agent.py` (`_agent_user_ctx`, `_as_auto` bọc `_HEAL_HOOKS`/`_AV_SYNC_HOOKS`, `api_agent_chat`/`api_agent_confirm` nhận `request`, `_agent_run_stage` đặt `qa_override` qua `Manifest.update`), `agents/agent_autopilot.py` (`caller_headers`, `agent_chat/agent_confirm(caller=, source=)`), `agents/agent_tele_cmd.py` (`_agent_ask` có uid + `_confirm_callback` gắn `X-Pineline-Caller: user`, `X-Pineline-Source: telegram`); test MỚI `tests/test_agent_hold_telegram.py` (14; đọc `http_routes/routes_agent.py`). Merge sạch, không xung đột. Hiệu lực: restart :8805 + bot `agent_tele_cmd` NẾU bot chạy từ cây V5 (`run_tele_cmd.bat` của V5); bot chạy từ V2 thì không liên quan V5.

## Test (bản sao cloud Linux, `AGENT_BRAIN=0`, stub fastapi/soundfile/yt_dlp; KHÔNG chạy trên cây thật)
- Toàn bộ `tests/`: trước **27 failed / 241 passed / 4 skipped / 6 error** → sau G+H+F2 **27 failed / 286 passed / 4 skipped / 6 error**, danh sách FAILED y hệt (drift đã biết + môi trường; 6 error = thiếu `google.oauth2`/`fastapi.testclient`).
- 9 file simple+demucs+brain+hold_telegram: **160 passed / 4 skipped**. Sau I2 toàn bộ: **27 failed / 300 passed / 4 skipped / 6 error** (cùng danh sách FAILED).
- Máy user: `Z:\PinelineV6\scripts\test_v5_simple_demucs.bat` (nay chạy trên BẢN SAO `%TEMP%\pv5_test`, có thêm 2 file brain).

## Recheck (sau restart :8805)
- Pass nếu: `agent_brain.log` có `brain start … tg=events heal_delay=180s`; `agent_watch.log` có `hoãn heal 180s sau khởi động`; Telegram chỉ tin theo mẫu (không «Brain báo cáo» 2', không «Brain DECISION»); bấm chạy tay TTS/mux trên job HOLD → manifest `agent.hold_override` + 1 tin «🔓 … Đã gỡ HOLD vì bạn chạy tay …»; job mới có `translate_pipeline=simple` (`_why=default`); job dở luồng cũ → `legacy` (`inferred`).
- Fail nếu: còn tin mỗi 2–3'; job đã gỡ HOLD tay bị HOLD lại khi QA không có high mới; job dở luồng cũ bị đổi sang simple khi chưa bấm «Dịch LẠI».

## Rollback
Chép lại file từ `.backup_edit_20261112_agentP5\` (cùng đường dẫn; `pineline.config.json.bak` → `pineline.config.json`); chuyển `agents\agent_brain_notify.py`, `agents\agent_hold.py`, 3 test mới (brain_events, brain_notify, hold_telegram) vào `_to_delete\`. `_i2_before\` = bản trung gian sau đợt G+H+F2 (trước I2). Chỉ Telegram: `AGENT_BRAIN_TELEGRAM=report`. Chỉ dịch: `TRANSLATE_PIPELINE=legacy`.
