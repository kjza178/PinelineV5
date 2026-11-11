# Thuật ngữ PinelineV2

_Cập nhật: 2026-11-11. Thêm từ mới khi gặp; mỗi mục 1–2 câu + nơi trong code/docs._

| Thuật ngữ | Nghĩa | Ở đâu |
|---|---|---|
| **job** | 1 video cần lồng tiếng; thư mục `work/<job_id>/` (12 hex) chứa `manifest.json` + artifact từng stage | `manifest.py`, `server.py` |
| **stage** | Bước pipeline: `download → asr → translate → tts → mux` (assemble chạy trong mux/render) | [processes/job-pipeline.md](./processes/job-pipeline.md) |
| **manifest** | `work/<job>/manifest.json`: trạng thái từng stage (`status`, `cur_text`, `error`) + `agent`, opts. Writer chuẩn `Manifest.update` | `manifest.py` |
| **script.json** | Bản dịch theo câu (zh, vi, cờ `rv`, alt…). Đầu vào TTS | `translate.py` |
| **rv** | Cờ "câu đã được REVIEW". Còn câu chưa `rv` = `unrev > 0` → chưa được TTS theo Studio SOP | `translate.run_review` |
| **NMT** | Máy dịch zh→vi chuyên dụng làm bản nháp (`MT_ZH_VI=1`, `ROLE=primary`); LLM chỉ REVIEW/sửa | `mt_zh_vi.py`, DECISIONS 11-09 |
| **REVIEW / soát** | Lượt LLM rà bản dịch theo lô (`review_batch`), có fallback local | `translate.run_review` |
| **Pass1** | Lượt REVIEW đầu: GPT đọc **full file** SRT VI (upload, chunk nếu lớn) để bắt câu vô nghĩa/đuôi treo | `translate.run_review_pass1_full_vi`, fix 11-11 pass1-upload-size |
| **Aurora / Aurora∥** | Endpoint LLM cloud (:3377, `chatgpt/gpt-6`) dùng cho REVIEW; `∥` = fan-out song song `REVIEW_PARALLEL` worker | `translate._review_parallel_workers`, fix 11-11 studio-1job |
| **ghế (seat)** | Slot GPU chạy 1 job trọn pipeline tới Done rồi mới job kế | [processes/queue-studio-sop.md](./processes/queue-studio-sop.md) |
| **Studio SOP** | Quy tắc vận hành user khoá 11-11: 1 job/ghế, ASR→NMT→REVIEW→TTS→mux→Done→next | DECISIONS 11-11 |
| **HOLD** | Job bị giữ trước TTS/mux (QA high severity, `hold_after_translate`, `qa_blocked`) | `agent_qa_gate`, `agent_brain` |
| **park** | Queue giữ ghế cho job đang HOLD/`waiting_review` thay vì nhảy job kế | `job_queue.set_park_ready_hook`, fix 11-10 queue-park-held |
| **hang** | Câu VI "đuôi treo"/nửa câu — QA high; xử lý bởi `agent_hang_fix` (trace → plan → `hang_ack`) | `agent_quality`, `agent_hang_fix` |
| **heal (safe/aggressive)** | Tự chữa job lỗi: safe = stale running, dịch trống, TTS thiếu clip, mux lại; aggressive = thêm ASR/TTS force | `agent_heal.py` |
| **L0–L3** | Lớp sự cố của agent_brain: infra / ops / quality / nặng | `docs/design/2026-11-09-second-brain-agent.md` |
| **split / `_p01`** | Job dài được cắt thành job con `<id>_p01…`; xong thì merge `output.mp4` về job cha | `split_parts.py` |
| **hardsub** | Phụ đề Trung cháy sẵn trong hình; che bằng `HARDSUB_MODE=track`, `STYLE=stretch`/blur | `render.py`, `hardsub_asr.py` |
| **duck_bgm / sfx_lib** | Chế độ âm thanh khi mux: hạ nền dưới giọng / giọng Việt + tiếng động gốc (CDX23) + nhạc kho | `render.py`, `sfx_lib.py` |
| **assemble / fit** | Co giãn clip TTS vào khung thời gian câu → `dub_fit.wav`, `tts_fit.json` | `assemble.py` |
| **AAC priming / media_ts** | Lệch tiếng do padding đầu AAC; xử lý timestamp | `media_ts.py`, worklog 10-05 |
| **CONFIG BATCH** | Cấu hình dùng chung cho autopilot/agent/Telegram/UI: `work/logs/batch_config.json` | `batch_config.py` |
| **sidecar** | Process `agent_tele_cmd.py` :8802 — Telegram, autopilot, feeder, film_db; gọi HTTP về server | [agents/runtime-agents.md](./agents/runtime-agents.md) |
| **Hongguo (HG)** | App tải phim ngắn :8000 (không kill) + bridge/merge queue | `hongguo_bridge.py`, `routes_hg.py` |
| **feeder / autopilot** | Tự thêm job khi hàng trống (lib_merged, auto_merge, hongguo…) / tick ~90s queue + heal | `agent_feeder.py`, `agent_autopilot.py` |
| **codebak / snapshot** | Backup trước khi sửa: zip `snapshot.py` + bản gốc file vào `Z:\PinelineV2_codebak\<ngày>_<slug>\` | `.cursor/rules/docs-on-change.mdc` |
| **V2 / V4 / V5** | Các bản cây code song song (cổng 8801 / 8804 / 8805); thay đổi thường được "sync" giữa chúng | `docs/STATE.md` |
