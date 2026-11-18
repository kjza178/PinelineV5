# Index module

_Sinh tự động bởi `scripts/brain_build.py` lúc 2026-11-17 19:05. Đừng sửa tay — chạy lại script._


Tổng: **171 module** (+67 test), **84,732 dòng**. Cột *Manual* = thẻ đã có phần viết tay (✅) hay chưa (·).

## control (9)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [server](../modules/server.md) | 7322 | 198 | 68 | 40 | 11 | · | server.py — Backend web Phase 1 (FastAPI). Bọc engine (download -> asr -> translate) thành |
| [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | 1107 | 58 | 62 | 6 | 1 | · | Cầu nối Hongguo 2.x (helper RPC stdio): /api/hg/* (= /api/hg2/*). Tách từ server.py (đợt 7 |
| [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | 815 | 47 | 18 | 6 | 1 | · | AI Agent nhúng (agent_core): hook cho Runtime + /api/agent/*. Tách từ server.py (đợt 7). C |
| [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | 662 | 29 | 36 | 3 | ❌ | · | routes_uploader_settings.py — API Router cho Quản lý Cài đặt (Settings) & YouTube Uploader |
| [http_routes.routes_films](../modules/http_routes.routes_films.md) | 370 | 31 | 31 | 3 | 1 | · | FastAPI Router cho Thư viện Phim & Database (đồng bộ trực tiếp trong Pineline V4). Thay vì |
| [restart_server](../modules/restart_server.md) | 263 | 9 |  | 8 |  | · | Restart server Pineline (giữ sidecar), khôi phục hàng đợi + Auto-pilot. Port mặc định V5:  |
| [app_desktop](../modules/app_desktop.md) | 147 | 4 |  | 1 |  | · | app_desktop.py — Desktop App Studio cho Pineline V4. Sử dụng Microsoft Edge WebView2 (nati |
| [http_routes.routes_ui](../modules/http_routes.routes_ui.md) | 108 | 10 | 14 | 2 | 1 | · | Trang UI: /, /ui3, /ui4, /hongguo, /hongguo2, /films/ui, /studio, /v5-map. /hongguo2 = ski |
| [tools.context_studio.app_streamlit](../modules/tools.context_studio.app_streamlit.md) | 108 | 0 |  |  |  | · | Streamlit UI stub — Context Detection trước khi dịch Pineline. Chạy: pip install streamlit |

## agent (20)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [agents.agent_brain](../modules/agents.agent_brain.md) | 2201 | 82 |  | 5 | 6 | · | Second Brain — daemon nền full-silent. Sensors → incidents → policy → actuators. Bật: AGEN |
| [agents.agent_core](../modules/agents.agent_core.md) | 2115 | 32 |  | 6 | 4 | · | agent_core.py — AI Agent nhúng trong Pineline V2. Không gọi HTTP self. Tools gọi runtime đ |
| [agents.agent_hongguo](../modules/agents.agent_hongguo.md) | 1570 | 36 |  | 3 | ❌ | · | agent_hongguo.py — Tích hợp bộ tool Hongguo Downloader & Auto-chain cho Pineline AI Agent. |
| [agents.agent_heal](../modules/agents.agent_heal.md) | 830 | 15 |  | 3 | 5 | · | agent_heal.py — Chẩn đoán + heal job lỗi (an toàn theo cấp). safe: heal stale running, vá  |
| [agents.agent_qa_ask](../modules/agents.agent_qa_ask.md) | 777 | 44 |  |  | 1 | · | Second Brain — HOLD QA hỏi người qua Telegram + tự xử lý khi quá hạn (2026-11-17 qaask). V |
| [agents.agent_av_sync](../modules/agents.agent_av_sync.md) | 569 | 11 |  | 4 | ❌ | · | AV sync diagnose + heal — phát hiện lệch sub/audio / audio cụt sau mux. Các class chính: a |
| [agents.agent_brain_notify](../modules/agents.agent_brain_notify.md) | 485 | 17 |  | 2 | 2 | · | Mẫu tin Telegram của Second Brain — do CODE dựng, không dùng văn tự do của LLM (fix 2026-1 |
| [agents.agent_tool_loop](../modules/agents.agent_tool_loop.md) | 481 | 11 |  | 1 | 1 | · | Tool loop — điều khiển pipeline theo bước, chờ kết quả thật. Khác `pineline_run_stage` (fi |
| [agents.agent_hold](../modules/agents.agent_hold.md) | 432 | 21 |  | 2 | 3 | · | agent_hold.py — gỡ HOLD khi người dùng CHẠY TAY 1 bước + chặn brain/auto đặt lại HOLD (fix |
| [agents.agent_watch](../modules/agents.agent_watch.md) | 408 | 20 |  | 2 | 1 | · | Watcher A: định kỳ scan → heal safe + log + Telegram (tuỳ chọn). Env: AGENT_WATCH=1 |
| [agents.agent_quality](../modules/agents.agent_quality.md) | 389 | 6 |  | 2 | 3 | · | Deterministic VI quality scan + safe heals (Second Brain L2). Port từ D:\PinelineV2_tmp\_q |
| [agents.agent_hang_fix](../modules/agents.agent_hang_fix.md) | 368 | 9 |  | 2 | 4 | · | Second Brain — pass LLM trace + xử lý high `hang` (đuôi treo / nửa câu). Không chỉ merge m |
| [agents.agent_brain_context](../modules/agents.agent_brain_context.md) | 287 | 8 |  | 3 | 1 | · | System snapshot cho Second Brain LLM — toàn hệ, không chỉ 1 job. |
| [agents.agent_stage_io](../modules/agents.agent_stage_io.md) | 286 | 14 |  |  |  | · | Peek / tóm tắt từng stage — chỉ đọc disk (an toàn). |
| [agents.agent_pronoun_pass](../modules/agents.agent_pronoun_pass.md) | 258 | 4 |  | 2 | 2 | · | Rà XƯNG HÔ trong bản dịch theo glossary.pronouns + genre. 1. Quét deterministic (cùng appl |
| [agents.agent_qa_gate](../modules/agents.agent_qa_gate.md) | 226 | 8 |  |  |  | · | Gate QA: translate → review → diff → mới cho TTS. |
| [agents.agent_qa_fix](../modules/agents.agent_qa_fix.md) | 202 | 9 |  |  | 1 | · | Second Brain — xử lý cờ QA HIGH loại khác `hang` (2026-11-17). Vì sao: trước đây chỉ `hang |
| [agents.agent_retry](../modules/agents.agent_retry.md) | 196 | 8 |  |  | 1 | · | Second Brain — tự thử lại stage FAILED (2026-11-17). Vì sao: L1 heal của brain chỉ chạy kh |
| [agents.agent_name_pass](../modules/agents.agent_name_pass.md) | 138 | 5 |  | 1 | 2 | · | Rà TÊN NHÂN VẬT trong bản dịch theo bảng nhân vật (glossary.json). 1. Quét: câu nào zh có  |
| [agents.agent_error_class](../modules/agents.agent_error_class.md) | 121 | 3 |  |  |  | · | Phân loại lỗi theo log / cur_text / error (ASR · TTS · mux · …). |

## sidecar (3)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md) | 2469 | 42 |  | 15 | 1 | · | Sidecar: Telegram lệnh + Auto-pilot + HTTP :8802 KHÔNG restart Pineline server — chỉ gọi A |
| [agents.agent_feeder](../modules/agents.agent_feeder.md) | 2066 | 68 |  | 7 | ❌ | · | Feeder + Run-watch cho Auto-pilot (chạy trong sidecar :8802, chỉ gọi API :8801). Feeder —  |
| [agents.agent_autopilot](../modules/agents.agent_autopilot.md) | 348 | 17 |  | 6 | 1 | · | Auto-pilot — queue need_queue + heal safe qua HTTP Pineline (:8801). Chạy trong sidecar (a |

## source (6)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md) | 3676 | 110 |  | 14 | 2 | · | hongguo_bridge.py — client Hongguo 2.x qua helper RPC (hongguo_rpc). 2026-11-16: bỏ hẳn Do |
| [agents.hongguo_rpc](../modules/agents.hongguo_rpc.md) | 1435 | 57 |  | 10 | ❌ | · | hongguo_rpc.py — JSON-RPC stdio client cho Hongguo WinUI 2.x helper.jar. Không dùng HTTP : |
| [engines.download](../modules/engines.download.md) | 711 | 20 |  | 3 | 1 | · | download.py — STAGE 1: Tải video (Douyin / Bilibili / TikTok / ...). Engine: yt-dlp. Tự re |
| [agents.hg_merge_check](../modules/agents.hg_merge_check.md) | 480 | 17 |  | 1 | 1 | · | hg_merge_check.py — kiểm tra + chuẩn hoá các tập TRƯỚC khi gộp, và kiểm file SAU khi gộp ( |
| [agents.hongguo_license_ensure](../modules/agents.hongguo_license_ensure.md) | 285 | 11 |  |  |  | · | Ensure Hongguo 2.x helper is license-proved (same process as hongguo_rpc). Uses DPAPI key  |
| [engines.playlist](../modules/engines.playlist.md) | 219 | 5 |  |  |  | · | playlist.py — Bóc 1 link thành DANH SÁCH video rồi tải hàng loạt. Vì sao tách riêng: Pinel |

## asr (17)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [engines.asr.fun_asr_nano](../modules/engines.asr.fun_asr_nano.md) | 602 | 11 |  | 1 | ❌ | · | fun_asr_nano.py — STAGE ASR bằng Fun-ASR-Nano (chất lượng tiếng Trung cao nhất). Model : F |
| [engines.separate](../modules/engines.separate.md) | 575 | 18 |  | 2 | 5 | · | separate.py — Tách giọng/nền bằng Demucs (htdemucs --two-stems=vocals). Đầu vào : work/<jo |
| [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md) | 570 | 14 |  | 2 | 2 | · | firered_asr.py — STAGE ASR bằng FireRedASR2-AED (system VAD+LID+ASR+Punc). Cần clone repo  |
| [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md) | 551 | 16 |  |  | ❌ | · | asr_repair.py — Hậu kỳ Hybrid: A lấp lỗ + B sửa nghe sai + FA. A) Gap: Para có thoại, bản  |
| [engines.asr.asr](../modules/engines.asr.asr.md) | 493 | 16 |  | 4 | 3 | · | asr.py — STAGE 2 (phần đầu): tách audio + nhận diện lời (Whisper). Đầu vào : work/<job>/so |
| [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md) | 469 | 14 |  |  | ❌ | · | asr_spam.py — Chặn ASR nuốt tiếng nền (cười/rên 哈·啊·呃 lặp). Không dựa vào check tay: sau m |
| [engines.asr.hardsub_asr](../modules/engines.asr.hardsub_asr.md) | 452 | 12 |  | 1 | 2 | · | hardsub_asr.py — OCR hardsub chỉ để RÀ SOÁT / SỬA sub ZH (asr · srt). Một nhiệm vụ: RapidO |
| [engines.asr.asr_align_nano_para](../modules/engines.asr.asr_align_nano_para.md) | 389 | 10 |  |  | ❌ | · | asr_align_nano_para.py — Hybrid A: chữ Fun-ASR-Nano + timestamp Paraformer (char-ts). Đầu  |
| [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md) | 342 | 5 |  |  | ❌ | · | nano_fa_asr.py — SOTA ASR: Fun-ASR-Nano (Chữ chuẩn nhất) + Direct Qwen3-ForcedAligner (Mốc |
| [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md) | 335 | 7 |  |  | ❌ | · | asr_fix_align.py — Phương án 3: fix monotonic_fix Bước 1 (fallback): chỗ timing bịa/đảo →  |
| [engines.asr.paraformer_zh](../modules/engines.asr.paraformer_zh.md) | 314 | 2 |  | 1 | ❌ | · | paraformer_zh.py — STAGE ASR bằng FunASR Paraformer-zh (timestamp tốt cho phụ đề/TTS). Mod |
| [engines.ocr](../modules/engines.ocr.md) | 273 | 8 |  | 1 | 1 | · | ocr.py — STAGE OCR: đọc chữ TRÊN HÌNH (tên nhân vật / địa danh / caption / thẻ) mà KHÔNG n |
| [engines.asr.sensevoice_asr](../modules/engines.asr.sensevoice_asr.md) | 260 | 4 |  | 1 |  | · | sensevoice_asr.py — STAGE ASR bằng FunASR SenseVoiceSmall (nhanh, đa ngôn ngữ). Model : ii |
| [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md) | 207 | 3 |  |  |  | · | hybrid_asr.py — ASR chốt: Nano chữ + Para timing + ForcedAlign + Repair. Pipeline (sidecar |
| [engines.asr.asr_vad_utils](../modules/engines.asr.asr_vad_utils.md) | 158 | 5 |  |  |  | · | asr_vad_utils.py — VAD kwargs FunASR thật + pad/overlap khi cắt đoạn. FunASR fsmn-vad (1.4 |
| [tools.asr_boundary_scan](../modules/tools.asr_boundary_scan.md) | 147 | 4 |  | 1 |  | · | tools/asr_boundary_scan.py — CHỈ ĐỌC: tìm câu ASR nghi bị cắt ở biên slice cứng k×1200 s.  |
| [engines.asr.asr_hybrid_progress](../modules/engines.asr.asr_hybrid_progress.md) | 144 | 5 |  |  |  | · | asr_hybrid_progress.py — Đưa tiến độ sidecar (Nano/Para) vào stages.asr cho UI Hybrid. UI  |

## translate (10)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [engines.translate](../modules/engines.translate.md) | 5172 | 104 |  | 23 | 19 | · | translate.py — STAGE dịch: "lập phương án" (hồ sơ nhân vật + XƯNG HÔ) rồi dịch CÓ NGỮ CẢNH |
| [engines.llm](../modules/engines.llm.md) | 1167 | 29 |  | 5 | 12 | · | llm.py — Gọi LLM qua 9router API (tương thích chuẩn OpenAI). Cấu hình qua config.json / pi |
| [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) | 872 | 30 |  | 2 | 5 | · | Đồng nhất xưng hô không cần diarization (A–C + vá câu đỏ). A) analyze_full_zh: quét TOÀN B |
| [engines.hv_auditor](../modules/engines.hv_auditor.md) | 475 | 15 |  | 1 | ❌ | · | Hán-Việt auditor — chống glossary khóa sai âm (vd 逆→Nghị thay vì Nghịch). 1) Unihan kVietn |
| [engines.translate_alts](../modules/engines.translate_alts.md) | 382 | 5 |  | 1 | ❌ | · | Phương án dịch tối ưu — ngữ cảnh + văn phong (trọng tâm Pineline). Quét câu dễ lệch / đa n |
| [engines.pronoun_register_policy](../modules/engines.pronoun_register_policy.md) | 307 | 10 |  | 1 | 2 | · | Policy xưng hô tổng quát cho mix #1+#3 — không gắn 1 job/phim. Mục tiêu: - Phát hiện cửa s |
| [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md) | 302 | 14 |  | 2 | 6 | · | NMT ZH→VI (HachimiMT) — DỊCH CHÍNH; LLM chỉ rà soát (run_review). Config: MT_ZH_VI=1       |
| [engines.series_glossary](../modules/engines.series_glossary.md) | 199 | 11 |  | 4 | 7 | · | Bảng nhân vật / thuật ngữ / xưng hô dùng chung cho CẢ BỘ (mọi mùa). - apply(work_dir, plan |
| [engines.script_lint](../modules/engines.script_lint.md) | 175 | 10 |  |  |  | · | Soát lỗi máy móc bản dịch VI (script.json) — chạy SAU review/polish, trước TTS. autofix_ro |
| [engines.title_mt](../modules/engines.title_mt.md) | 172 | 6 |  | 2 |  | · | Dịch thô tiêu đề Trung → Việt (Google gtx, không cần API key). Chỉ để duyệt Hongguo cho bi |

## tts (3)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [engines.clone_tts](../modules/engines.clone_tts.md) | 1115 | 38 |  | 1 | 2 | · | clone_tts.py — STAGE Lồng tiếng bằng TTS zero-shot clone tiếng Việt. Hai engine, cùng regi |
| [rvc_bridge.vieneu_batch](../modules/rvc_bridge.vieneu_batch.md) | 183 | 5 |  | 1 |  | · | Worker VieNeu-TTS v3-Turbo (chạy trong D:/vieneu_env). Đọc job json: {out_dir, ref, text,  |
| [rvc_bridge.omnivoice_batch](../modules/rvc_bridge.omnivoice_batch.md) | 47 | 1 |  | 1 |  | · | Worker omnivoice-vietnamese (chạy trong D:/OmniVoiceStudio-v2/.venv). Đọc job json: {out_d |

## render (8)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [engines.render](../modules/engines.render.md) | 3148 | 75 |  | 15 | 6 | · | render.py — STAGE 7 (Ghép + xuất): ráp video lồng tiếng "sạch như bản localize". Video (1  |
| [engines.subs](../modules/engines.subs.md) | 1106 | 34 |  |  | ❌ | · | subs.py — Sinh phụ đề .srt từ danh sách câu có timestamp. Dùng chung: asr.json (tiếng Trun |
| [engines.split_parts](../modules/engines.split_parts.md) | 1105 | 27 |  | 7 | 4 | · | split_parts.py — Tự động tính toán và chia video dài (3h-12h+) thành các Part 2-2.5h để ch |
| [engines.media_ts](../modules/engines.media_ts.md) | 1019 | 32 |  | 4 | 3 | · | Mốc thời gian tiếng của file nguồn — sửa tiếng "dồn mẫu" ở file ghép nhiều tập. File ghép  |
| [engines.render_fx](../modules/engines.render_fx.md) | 564 | 32 |  |  | 1 | · | Helpers: uniqueness filters + library BGM paths (copyright-safe audio). |
| [engines.sfx_lib](../modules/engines.sfx_lib.md) | 443 | 21 |  | 2 | 2 | · | sfx_lib.py — chế độ audio `sfx_lib`: giọng Việt + TIẾNG ĐỘNG gốc + NHẠC KHO SẠCH theo mức. |
| [engines.assemble](../modules/engines.assemble.md) | 422 | 16 |  | 2 | 1 | · | assemble.py — Ghép clip TTS thành MỘT track + kiểm khớp SRT. Hai chế độ: - assemble()      |
| [engines.mux](../modules/engines.mux.md) | 137 | 5 |  | 4 | 1 | · | mux.py — STAGE cuối: ghép track lồng tiếng vào video -> output.mp4 (thuyết minh). Kiểu thu |

## publish (7)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [agents.meta_studio](../modules/agents.meta_studio.md) | 2084 | 33 |  | 4 | 2 | · | meta_studio.py — Module sinh Metadata YouTube (Title / Description / Tags / AI Image Promp |
| [agents.auto_publisher](../modules/agents.auto_publisher.md) | 1567 | 36 |  | 6 | 3 | · | auto_publisher.py — Tự động hoá toàn trình: Sau khi render xong → Tự tạo Metadata SEO & Th |
| [agents.test_channel](../modules/agents.test_channel.md) | 1444 | 38 |  | 3 | ❌ | · | test_channel.py — Quản lý Kênh Phụ Test (Burner Channel) độc lập trong Pineline. Chức năng |
| [tools.test_channel](../modules/tools.test_channel.md) | 1444 | 38 |  | 3 | ❌ | · | test_channel.py — Quản lý Kênh Phụ Test (Burner Channel) độc lập trong Pineline. Chức năng |
| [agents.uploader_settings_api](../modules/agents.uploader_settings_api.md) | 675 | 31 |  | 3 | ❌ | · | Settings + YouTube Uploader API — dùng được từ sidecar :8802 (stdlib) và FastAPI. Trả về ( |
| [agents.canva_client](../modules/agents.canva_client.md) | 394 | 12 |  |  | ❌ | · | canva_client.py — Tích hợp Canva Connect API chính thức cho Pineline. Quản lý OAuth2 (PKCE |
| [agents.films_merge_api](../modules/agents.films_merge_api.md) | 174 | 10 |  | 2 |  | · | Gộp parts (split jobs) + scan job đã làm sẵn sàng merge — dùng từ sidecar :8802. |

## core (10)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [core.film_db](../modules/core.film_db.md) | 1091 | 42 |  | 6 | 5 | · | Database phim đã làm (SQLite) — nguồn sự thật lâu dài, không mất khi xoá thư mục job. film |
| [core.job_queue](../modules/core.job_queue.md) | 667 | 33 |  | 13 | 6 | ✅ |  |
| [core.batch_config](../modules/core.batch_config.md) | 295 | 14 |  | 4 | 1 | · | Cấu hình batch dùng chung — 1 nguồn duy nhất cho Auto-pilot, Agent (queue_add), Telegram ( |
| [core.manifest](../modules/core.manifest.md) | 262 | 4 |  | 3 | 6 | ✅ | manifest.py — Trạng thái/checkpoint cho pipeline. Mỗi job (mỗi video) có một thư mục làm v |
| [core.machine](../modules/core.machine.md) | 255 | 24 |  | 1 |  | · | machine.py — Cấu hình PHỤ THUỘC MÁY (cổng dịch vụ ngoài, thư mục model/thư viện, lệnh đổi  |
| [core.config](../modules/core.config.md) | 194 | 8 |  | 3 | 3 | ✅ | config.py — Cấu hình/đường dẫn PORTABLE cho Pineline. Thứ tự ưu tiên khi lấy 1 giá trị: bi |
| [core.job_meta](../modules/core.job_meta.md) | 164 | 5 |  | 1 | 1 | · | Parse metadata hàng chờ (series/season UI) — dùng chung film_db sync + job_queue. |
| [core.fileio](../modules/core.fileio.md) | 104 | 4 |  | 3 |  | · | Ghi file an toàn giữa nhiều tiến trình (server :8801, sidecar :8802, script). atomic_write |
| [core.timeutil](../modules/core.timeutil.md) | 42 | 3 |  |  | 1 | · | core/timeutil.py — MỘT kiểu mốc thời gian cho manifest (port từ V6). Quy ước (fix 2026-11- |
| [core.__init__](../modules/core.__init__.md) | 1 | 0 |  |  |  | · | PinelineV5 app core: config, queue, DB, manifest, fileio. |

## ops (33)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [scripts.brain_build](../modules/scripts.brain_build.md) | 857 | 23 |  |  | ❌ | · | brain_build.py — Sinh/làm mới phần TỰ ĐỘNG của Second Brain (docs/brain/). Đọc mã nguồn bằ |
| [scripts.check_batch4](../modules/scripts.check_batch4.md) | 457 | 6 |  | 2 | ❌ | · | Kiểm thử đợt 4 (tranh chấp ghi manifest, claim endpoint, single-instance, worker khởi động |
| [tools.lib_check](../modules/tools.lib_check.md) | 411 | 9 |  |  | ❌ | · | lib_check.py — Kiểm tra bản quyền / Block YouTube cho Phim trong Thư viện gốc (D:\Lib) trư |
| [scripts.sync_from_v2](../modules/scripts.sync_from_v2.md) | 368 | 12 |  | 3 | ❌ | · | sync_from_v2.py — Đồng bộ code từ cây nguồn (V2, bố cục phẳng) sang cây đích. Thay cho việ |
| [engines.check_block](../modules/engines.check_block.md) | 350 | 4 |  |  | ❌ | · | check_block.py — Module kiểm tra trạng thái Bản quyền / Block YouTube (Cơ chế 1: Không cần |
| [scripts.check_batch5](../modules/scripts.check_batch5.md) | 347 | 6 |  | 1 | ❌ | · | Kiểm thử đợt 5 (agent an toàn): lệnh / bắt buộc, phân tầng tool + xác nhận ✅/❌, hg_auto_fl |
| [scripts._patch_hongguo2_update_ux](../modules/scripts._patch_hongguo2_update_ux.md) | 327 | 0 |  |  | ❌ | · | One-shot: hongguo2 Update UX when seasons is null + layout. |
| [scripts.check_batch2](../modules/scripts.check_batch2.md) | 327 | 9 | 2 | 2 | ❌ | · | Kiểm thử đợt 2 (bảo mật + config 1 nguồn + LLM lỗi dừng stage). KHÔNG chạm server/sidecar  |
| [scripts.check_env](../modules/scripts.check_env.md) | 319 | 15 |  | 1 | ❌ | · | check_env.py — "Doctor" kiểm tra máy trước khi chạy Pineline (máy mới / máy khác cấu hình) |
| [scripts.check_batch1](../modules/scripts.check_batch1.md) | 307 | 11 |  | 2 | ❌ | · | Test đợt 1 (chặn mất dữ liệu) — chỉ dùng thư mục tạm, không đụng job/queue/thư viện thật. |
| [tools.migrate_work](../modules/tools.migrate_work.md) | 297 | 12 |  | 2 | 1 | · | Chuyển Z:\PinelineV2\work sang ổ khác (mặc định D:\PinelineV2_work) giữa 2 job, không mất  |
| [tools.preset_switcher](../modules/tools.preset_switcher.md) | 242 | 6 |  | 2 | 5 | · | preset_switcher.py — Tự động chuyển đổi Preset Model trên llama-server (:8083) Quản lý bộ  |
| [scripts.tree_audit](../modules/scripts.tree_audit.md) | 226 | 9 |  | 5 |  | · | tree_audit.py — Kiểm tra sức khoẻ cây code Pineline (V2/V4/V5) sau mỗi lần sync/port. Chỉ  |
| [scripts._patch_hongguo2_discover_only](../modules/scripts._patch_hongguo2_discover_only.md) | 221 | 0 |  |  |  | · | Hongguo2: Tìm mùa mới (info-only) + làm rõ Update thư viện tải tập thiếu. |
| [tools.pick_dirs_dialog](../modules/tools.pick_dirs_dialog.md) | 209 | 4 |  |  |  | · | Hộp thoại chọn NHIỀU folder cùng lúc (Listbox multi-select). Chạy: python pick_dirs_dialog |
| [scripts.check_batch3](../modules/scripts.check_batch3.md) | 202 | 1 |  | 3 |  | · | Kiểm thử đợt 3 (opts một nguồn X1, config file-first X2, ghi nguyên tử + khoá S13). Chạy t |
| [scripts._tmp_extract_sigs_batch2](../modules/scripts._tmp_extract_sigs_batch2.md) | 191 | 5 |  |  |  | · | One-shot AST signature extract for func-sigs batch2. Delete after use OK. |
| [scripts.check_cookies](../modules/scripts.check_cookies.md) | 172 | 5 |  |  |  | · | check_cookies.py — Soi file cookie: còn hạn không, đã ĐĂNG NHẬP chưa, và có lấy được HD kh |
| [scripts._rebuild_v5_map_funcs](../modules/scripts._rebuild_v5_map_funcs.md) | 147 | 0 |  |  |  | · | Rebuild MODULE_FUNCS + funcKeys in static/ui/v5-map.html from func-sigs/*.md. |
| [scripts._patch_hongguo2_discover_api](../modules/scripts._patch_hongguo2_discover_api.md) | 113 | 0 |  |  |  | · | Replace client-side lsnDiscoverNew with API /api/hg/library/seasons/discover. |
| [scripts.gen_sample_assets](../modules/scripts.gen_sample_assets.md) | 108 | 4 |  |  |  | · | Tạo sample assets cho Pineline (grain / LUT / BGM). Chạy:  python scripts/gen_sample_asset |
| [scripts.test_deepseek_plan](../modules/scripts.test_deepseek_plan.md) | 103 | 3 |  |  |  | · | Thử lập plan cả phim (A7) bằng DeepSeek cho 1 job — KHÔNG đụng job (chạy trên bản sao asr. |
| [engines.vram](../modules/engines.vram.md) | 89 | 4 |  |  |  | · | vram.py — Nhả VRAM trước MỖI bước dùng GPU. Ollama (Gemma ctx 128k), FunASR, Demucs, TTS,  |
| [scripts.brain_export](../modules/scripts.brain_export.md) | 67 | 2 |  |  |  | · | brain_export.py — Xuất dữ liệu Second Brain ra JSON gọn cho trang workflow (docs/brain/wor |
| [scripts.build_workflow_html](../modules/scripts.build_workflow_html.md) | 47 | 1 |  |  |  | · | build_workflow_html.py — Dựng docs/brain/workflow.html (trang workflow động) từ brain.json |
| [scripts._port_hg_watchlist_bridge](../modules/scripts._port_hg_watchlist_bridge.md) | 41 | 0 |  |  |  | · |  |
| [scripts._port_hg_watchlist_film_db](../modules/scripts._port_hg_watchlist_film_db.md) | 38 | 0 |  |  |  | · |  |
| [scripts._tmp_inspect_films_db2](../modules/scripts._tmp_inspect_films_db2.md) | 35 | 0 |  |  |  | · |  |
| [scripts.check_sidecar_lock](../modules/scripts.check_sidecar_lock.md) | 29 | 0 |  |  |  | · |  |
| [scripts.download_firered_models](../modules/scripts.download_firered_models.md) | 29 | 1 |  |  |  | · | Download FireRedASR2S models into FIRERED_MODELS (default D:/AI_CACHE/firered). |
| [scripts._hg_watchlist_snippet](../modules/scripts._hg_watchlist_snippet.md) | 26 | 0 |  |  |  | · | Snippet appended into film_db.py — hg_watchlist helpers. |
| [scripts._tmp_inspect_films_db](../modules/scripts._tmp_inspect_films_db.md) | 26 | 0 |  |  |  | · |  |
| [scripts._tmp_count_sigs](../modules/scripts._tmp_count_sigs.md) | 17 | 0 |  |  |  | · |  |

## misc (45)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [engines.source_preflight](../modules/engines.source_preflight.md) | 556 | 22 |  | 1 | 1 | · | Preflight + chuẩn hoá video nguồn TRƯỚC asr/separate/ocr/render (2026-11-12, agentK). Vì s |
| [engines.cloud_retry](../modules/engines.cloud_retry.md) | 520 | 16 |  | 1 | 8 | · | cloud_retry.py — fix 2026-11-11 translate-b2 (Việc A): THỬ LẠI model cloud (Aurora/GPT…) k |
| [engines.translate_simple.pipeline](../modules/engines.translate_simple.pipeline.md) | 497 | 15 |  | 1 | 6 | · | Điểm vào luồng dịch simple: `run(work_dir, target, *, progress, stop_check) -> dict`. Ghi: |
| [engines.hs_ocr_fast](../modules/engines.hs_ocr_fast.md) | 412 | 14 |  |  | 2 | · | hs_ocr_fast.py — OCR hardsub NHANH cho luồng simple (SIMPLE_ZH_SOURCE) — fix 2026-11-13. V |
| [engines.translate_simple.stage_review](../modules/engines.translate_simple.stage_review.md) | 372 | 9 |  |  | 6 | · | Bước 3: REVIEW cloud theo lô — MỘT lần gọi/lô làm hết: sửa nghĩa, áp xưng hô theo cặp plan |
| [engines.translate_simple.cfg](../modules/engines.translate_simple.cfg.md) | 367 | 45 |  | 2 | 4 | · | Cấu hình luồng simple — mọi khoá prefix SIMPLE_ đọc qua config.get (env > pineline.config. |
| [engines.translate_simple.zh_source](../modules/engines.translate_simple.zh_source.md) | 353 | 11 |  |  | 2 | · | Bước 1 (2026-11-12 next) — chọn NGUỒN chữ ZH cho luồng simple (cờ SIMPLE_ZH_SOURCE=1, mặc  |
| [tools.context_studio.character_mapper](../modules/tools.context_studio.character_mapper.md) | 353 | 10 |  |  | ❌ | · | 02 — Character + relation map: ai tự xưng gì khi nói với ai. |
| [engines.translate_simple.stage_draft](../modules/engines.translate_simple.stage_draft.md) | 349 | 7 |  | 1 | 4 | · | Bước 2: Plan (cloud) ∥ NMT nháp (GPU) — chạy SONG SONG bằng 2 thread. Plan: dùng lại gloss |
| [tools.context_studio.address_lexicon](../modules/tools.context_studio.address_lexicon.md) | 338 | 4 |  |  | ❌ | · | Kho xưng hô cổ trang / võ hiệp / tu tiên (VN dịch Trung). Nguồn tham chiếu (quy ước văn họ |
| [engines.lib_normalize](../modules/engines.lib_normalize.md) | 303 | 17 |  |  | 1 | · | Chuẩn hóa video thư viện (D:\Lib\<mùa>) — hàng đợi NỀN trong sidecar :8802 (2026-11-17/18) |
| [engines.translate_simple.pair_rules](../modules/engines.translate_simple.pair_rules.md) | 295 | 15 |  |  | 2 | · | Bước 2 (2026-11-12 next) — điền cặp xưng hô CÒN TRỐNG theo bảng quy tắc quan hệ (cờ SIMPLE |
| [engines.translate_simple.zh_ocr_target](../modules/engines.translate_simple.zh_ocr_target.md) | 279 | 11 |  |  |  | · | OCR hardsub CÓ CHỌN LỌC cho luồng simple — SIMPLE_ZH_OCR_MODE=targeted (mặc định) — 2026-1 |
| [tools.context_studio.analyzer](../modules/tools.context_studio.analyzer.md) | 264 | 5 |  |  |  | · | 01 — Context analyzer: SRT Trung → glossary draft (+ style_lock). |
| [engines.translate_simple.validate](../modules/engines.translate_simple.validate.md) | 236 | 8 |  |  | 4 | · | Bộ kiểm tất định — chỉ ĐÁNH CỜ, không sửa. Cờ (row["s_flags"] = list mã): empty    vi trốn |
| [engines.translate_simple.plan_view](../modules/engines.translate_simple.plan_view.md) | 215 | 5 |  |  | 7 | · | Đọc plan (glossary.json) cho luồng simple: nhân vật, cặp xưng hô, cảnh, thuật ngữ — và khố |
| [tools.collect_manual_edits](../modules/tools.collect_manual_edits.md) | 192 | 8 |  |  |  | · | Gom câu NGƯỜI SỬA TAY (manual) trong work dir thành ỨNG VIÊN golden (định dạng golden V6)  |
| [engines.translate_simple.script_store](../modules/engines.translate_simple.script_store.md) | 184 | 3 |  |  | 6 | · | Một cửa đọc/ghi script.json + trace.jsonl cho luồng simple. - Ghi atomic (fileio.atomic_wr |
| [engines.translate_simple.pair_fill](../modules/engines.translate_simple.pair_fill.md) | 134 | 6 |  |  | 1 | · | Bước 6 (2026-11-12 next) — bổ sung cặp xưng hô THIẾU bằng 1 lần gọi model (cờ SIMPLE_PAIR_ |
| [tools.context_studio.schema](../modules/tools.context_studio.schema.md) | 129 | 3 |  |  |  | · | Heuristic number / name flags — không sửa transcript. |
| [tools.simple_stats](../modules/tools.simple_stats.md) | 116 | 4 |  |  |  | · | Thống kê luồng dịch simple THEO JOB — CHỈ ĐỌC work dir (2026-11-12 next, Bước 8c). Mỗi job |
| [engines.translate_simple.lexicon](../modules/engines.translate_simple.lexicon.md) | 110 | 4 |  |  | 3 | · | Gợi ý thành ngữ / lóng ZH→VI cho prompt review (dò chuỗi con trong ZH của lô). Nguồn: data |
| [tools.context_studio.srt_io](../modules/tools.context_studio.srt_io.md) | 99 | 4 |  |  |  | · | Parse SRT / asr.json → list[{i, start, end, text}]. |
| [engines.translate_simple.suggest](../modules/engines.translate_simple.suggest.md) | 94 | 4 |  |  |  | · | Đề xuất cặp xưng hô CHƯA có trong plan (review 2026-11-12) → work_dir/plan_suggestions.jso |
| [tools.preflight_scan](../modules/tools.preflight_scan.md) | 87 | 2 |  | 1 |  | · | Quét CHỈ-ĐỌC các job trong work dir: nguồn video nào có vấn đề (preflight). Không ghi mani |
| [pineline.server.routes.jobs](../modules/pineline.server.routes.jobs.md) | 79 | 1 |  | 1 | 1 | · | Jobs API: /api/jobs/* — LIVE registry trong khung pineline V5. Thân handler vẫn trong root |
| [engines.translate_simple.post](../modules/engines.translate_simple.post.md) | 76 | 3 |  |  | 1 | · | Hậu kỳ tất định của luồng simple — KHÔNG regex đổi đại từ: 1) chuẩn dấu nghìn (translate.n |
| [tools.context_studio.exporter](../modules/tools.context_studio.exporter.md) | 73 | 1 |  |  |  | · | 05 — Export context pack vào thư mục job Pineline (hoặc out/). |
| [tools.context_studio.__main__](../modules/tools.context_studio.__main__.md) | 67 | 1 |  |  |  | · | CLI: python -m tools.context_studio analyze <srt/asr.json> -o work/<job> Chỉ PRE-SCAN — kh |
| [engines.translate_simple.repair](../modules/engines.translate_simple.repair.md) | 56 | 1 |  |  |  | · | Bước 5: vá ĐÚNG các câu bị bộ kiểm đánh cờ — tối đa SIMPLE_REPAIR_ROUNDS (≤2) lượt. Mỗi lư |
| [engines.translate_simple.gate](../modules/engines.translate_simple.gate.md) | 49 | 1 |  |  | 2 | · | Bước 6: cổng của luồng simple (hàm thuần — test được). done  : đủ câu so ASR (translate_co |
| [pineline.server.routes.queue](../modules/pineline.server.routes.queue.md) | 38 | 1 |  | 5 | 1 | · | Queue API: /api/queue/* (+ alias /api/jobs/group) — LIVE registry. Thân handler giữ trong  |
| [pineline.server.routes.assets](../modules/pineline.server.routes.assets.md) | 32 | 1 |  | 1 |  | · | Assets + LLM models: cookies / voices / frames / brand / clone — LIVE registry. Thân handl |
| [engines.text_junk](../modules/engines.text_junk.md) | 26 | 1 |  | 1 | 1 | · | Nhận diện câu ASR «rác» (fix 2026-11-13 agentM, sự cố 60892cc63cb7_p01 i=1039 zh="None."). |
| [pineline.server.routes.fs](../modules/pineline.server.routes.fs.md) | 23 | 1 |  | 1 |  | · | FS picker: /api/fs/* — LIVE registry (body trong server.py). |
| [engines.translate_simple.__init__](../modules/engines.translate_simple.__init__.md) | 18 | 0 |  |  |  | · | translate_simple — luồng dịch ZH→VI gọn (2026-11-12, chủ dự án duyệt). V5 (port 2026-11-12 |
| [tools.context_studio.__init__](../modules/tools.context_studio.__init__.md) | 6 | 0 |  |  |  | · | Context Studio — PRE-SCAN SRT Trung → context pack cho Pineline dịch. Không dịch. Chỉ phân |
| [pineline.__init__](../modules/pineline.__init__.md) | 3 | 0 |  |  |  | · | PinelineV5 package khung — xem pineline/README.md. |
| [agents.__init__](../modules/agents.__init__.md) | 1 | 0 |  |  |  | · | Agent / sidecar modules (Phase B layout). |
| [engines.__init__](../modules/engines.__init__.md) | 1 | 0 |  |  |  | · | Pipeline engines (Phase C+D). |
| [engines.asr.__init__](../modules/engines.asr.__init__.md) | 1 | 0 |  |  |  | · | ASR engine variants. |
| [http_routes.__init__](../modules/http_routes.__init__.md) | 1 | 0 |  |  |  | · | HTTP route modules (Phase B layout). |
| [pineline.server.__init__](../modules/pineline.server.__init__.md) | 1 | 0 |  |  |  | · | HTTP server layer (FastAPI). Entry runtime vẫn là root `server.py` trong giai đoạn chuyển. |
| [pineline.server.routes.__init__](../modules/pineline.server.routes.__init__.md) | 1 | 0 |  |  |  | · | APIRouter modules. Nạp từ cuối `server.py` qua `app.include_router`. |
| [tools.__init__](../modules/tools.__init__.md) | 1 | 0 |  |  |  | · | Ops / helper tools (lib_check, test_channel, migrate_work, context_studio, …). |

## test

| Test | Kiểm module |
|---|---|
| `tests/__init__.py` | — |
| `tests/test_agent_brain_events.py` | [agents.agent_brain](../modules/agents.agent_brain.md), [agents.agent_brain_context](../modules/agents.agent_brain_context.md), [agents.agent_heal](../modules/agents.agent_heal.md) |
| `tests/test_agent_brain_notify.py` | [agents.agent_brain](../modules/agents.agent_brain.md), [agents.agent_brain_notify](../modules/agents.agent_brain_notify.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_hold](../modules/agents.agent_hold.md), [agents.agent_watch](../modules/agents.agent_watch.md), [core.manifest](../modules/core.manifest.md) |
| `tests/test_agent_core_smoke.py` | [agents.agent_core](../modules/agents.agent_core.md), [core.manifest](../modules/core.manifest.md) |
| `tests/test_agent_hold_telegram.py` | [agents.agent_autopilot](../modules/agents.agent_autopilot.md), [agents.agent_hold](../modules/agents.agent_hold.md), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md), [core.manifest](../modules/core.manifest.md) |
| `tests/test_agent_parser.py` | [agents.agent_core](../modules/agents.agent_core.md) |
| `tests/test_agent_quality.py` | [agents.agent_quality](../modules/agents.agent_quality.md) |
| `tests/test_agent_tool_loop.py` | [agents.agent_tool_loop](../modules/agents.agent_tool_loop.md) |
| `tests/test_asr_demucs.py` | [core.manifest](../modules/core.manifest.md), [engines.asr.asr](../modules/engines.asr.asr.md) |
| `tests/test_auto_publisher_dedup.py` | [agents.auto_publisher](../modules/agents.auto_publisher.md), [core.film_db](../modules/core.film_db.md) |
| `tests/test_autosplit_conflict_guards.py` | — |
| `tests/test_brain_finished_hold.py` | [agents.agent_brain](../modules/agents.agent_brain.md), [agents.agent_brain_notify](../modules/agents.agent_brain_notify.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_hold](../modules/agents.agent_hold.md) |
| `tests/test_brain_qa_ask.py` | [agents.agent_brain](../modules/agents.agent_brain.md), [agents.agent_core](../modules/agents.agent_core.md), [agents.agent_qa_ask](../modules/agents.agent_qa_ask.md), [agents.agent_quality](../modules/agents.agent_quality.md) |
| `tests/test_brain_qa_fix_retry.py` | [agents.agent_qa_fix](../modules/agents.agent_qa_fix.md), [agents.agent_quality](../modules/agents.agent_quality.md), [agents.agent_retry](../modules/agents.agent_retry.md) |
| `tests/test_brain_qa_hold_timeout.py` | [agents.agent_brain](../modules/agents.agent_brain.md) |
| `tests/test_chatgpt_route.py` | [agents.meta_studio](../modules/agents.meta_studio.md), [core.config](../modules/core.config.md), [engines.llm](../modules/engines.llm.md) |
| `tests/test_deepseek_empty_and_brain_idle.py` | [agents.agent_brain](../modules/agents.agent_brain.md), [engines.cloud_retry](../modules/engines.cloud_retry.md), [engines.llm](../modules/engines.llm.md), [engines.translate_simple.stage_draft](../modules/engines.translate_simple.stage_draft.md) |
| `tests/test_extract_pcm_robust.py` | [engines.media_ts](../modules/engines.media_ts.md) |
| `tests/test_extract_pcm_timing.py` | [engines.media_ts](../modules/engines.media_ts.md) |
| `tests/test_film_db_queue_meta.py` | [core.film_db](../modules/core.film_db.md), [core.job_meta](../modules/core.job_meta.md), [core.job_queue](../modules/core.job_queue.md) |
| `tests/test_firered_slice_silence.py` | [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md), [engines.separate](../modules/engines.separate.md) |
| `tests/test_hardsub_blur_toggle.py` | [core.batch_config](../modules/core.batch_config.md), [server](../modules/server.md) |
| `tests/test_hardsub_detection.py` | [engines.render](../modules/engines.render.md) |
| `tests/test_hg_merge_check.py` | [agents.hg_merge_check](../modules/agents.hg_merge_check.md) |
| `tests/test_hg_merge_queue.py` | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md) |
| `tests/test_job_queue.py` | [core.job_queue](../modules/core.job_queue.md) |
| `tests/test_job_queue_worker.py` | [core.job_queue](../modules/core.job_queue.md) |
| `tests/test_layout_paths.py` | [agents.agent_core](../modules/agents.agent_core.md), [core.config](../modules/core.config.md), [core.job_queue](../modules/core.job_queue.md), [engines.assemble](../modules/engines.assemble.md), [engines.clone_tts](../modules/engines.clone_tts.md), [engines.download](../modules/engines.download.md), [engines.llm](../modules/engines.llm.md), [engines.ocr](../modules/engines.ocr.md), [engines.render](../modules/engines.render.md), [engines.render_fx](../modules/engines.render_fx.md), [engines.separate](../modules/engines.separate.md), [engines.sfx_lib](../modules/engines.sfx_lib.md), [engines.translate](../modules/engines.translate.md), [http_routes.routes_films](../modules/http_routes.routes_films.md), [http_routes.routes_ui](../modules/http_routes.routes_ui.md), [server](../modules/server.md) |
| `tests/test_lib_normalize.py` | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md), [engines.lib_normalize](../modules/engines.lib_normalize.md) |
| `tests/test_meta_and_thumb.py` | [agents.auto_publisher](../modules/agents.auto_publisher.md), [agents.meta_studio](../modules/agents.meta_studio.md) |
| `tests/test_optimize_b5_b6.py` | [engines.translate](../modules/engines.translate.md), [server](../modules/server.md) |
| `tests/test_parent_rerun_after_done.py` | [agents.agent_heal](../modules/agents.agent_heal.md), [core.job_queue](../modules/core.job_queue.md), [engines.render](../modules/engines.render.md), [engines.split_parts](../modules/engines.split_parts.md) |
| `tests/test_park_review_retry.py` | [server](../modules/server.md) |
| `tests/test_pronoun_consistency.py` | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) |
| `tests/test_pronoun_postpass.py` | [engines.translate](../modules/engines.translate.md) |
| `tests/test_pronoun_qa_slim_plan.py` | [engines.translate](../modules/engines.translate.md) |
| `tests/test_queue_http_state.py` | [core.film_db](../modules/core.film_db.md), [core.job_queue](../modules/core.job_queue.md), [pineline.server.routes.jobs](../modules/pineline.server.routes.jobs.md), [pineline.server.routes.queue](../modules/pineline.server.routes.queue.md) |
| `tests/test_queue_jobs_api.py` | [server](../modules/server.md) |
| `tests/test_queue_run_one.py` | [server](../modules/server.md) |
| `tests/test_render_expr.py` | [engines.render](../modules/engines.render.md) |
| `tests/test_restart_guard.py` | [tools.migrate_work](../modules/tools.migrate_work.md) |
| `tests/test_review_batches.py` | — |
| `tests/test_review_fail_not_rv.py` | [engines.translate](../modules/engines.translate.md) |
| `tests/test_review_parallel_workers.py` | [engines.translate](../modules/engines.translate.md) |
| `tests/test_review_pass1_upload.py` | [engines.translate](../modules/engines.translate.md) |
| `tests/test_seat_lock_heal.py` | [agents.agent_heal](../modules/agents.agent_heal.md) |
| `tests/test_separate_demucs_chunks.py` | [core.manifest](../modules/core.manifest.md), [engines.asr.asr](../modules/engines.asr.asr.md), [engines.separate](../modules/engines.separate.md), [engines.split_parts](../modules/engines.split_parts.md) |
| `tests/test_server_split.py` | [http_routes.routes_agent](../modules/http_routes.routes_agent.md), [http_routes.routes_hg](../modules/http_routes.routes_hg.md), [server](../modules/server.md) |
| `tests/test_sfx_lib.py` | [engines.render](../modules/engines.render.md), [engines.sfx_lib](../modules/engines.sfx_lib.md) |
| `tests/test_simple_junk_park.py` | [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md), [engines.clone_tts](../modules/engines.clone_tts.md), [engines.llm](../modules/engines.llm.md), [engines.separate](../modules/engines.separate.md), [engines.split_parts](../modules/engines.split_parts.md), [engines.text_junk](../modules/engines.text_junk.md), [engines.translate](../modules/engines.translate.md), [engines.translate_simple.cfg](../modules/engines.translate_simple.cfg.md), [engines.translate_simple.pipeline](../modules/engines.translate_simple.pipeline.md), [engines.translate_simple.plan_view](../modules/engines.translate_simple.plan_view.md), [engines.translate_simple.script_store](../modules/engines.translate_simple.script_store.md), [engines.translate_simple.stage_review](../modules/engines.translate_simple.stage_review.md), [engines.translate_simple.validate](../modules/engines.translate_simple.validate.md), [tests.test_translate_simple](../modules/tests.test_translate_simple.md) |
| `tests/test_simple_r1_bugs.py` | [core.timeutil](../modules/core.timeutil.md), [engines.translate](../modules/engines.translate.md), [engines.translate_simple.gate](../modules/engines.translate_simple.gate.md), [engines.translate_simple.pipeline](../modules/engines.translate_simple.pipeline.md), [engines.translate_simple.plan_view](../modules/engines.translate_simple.plan_view.md), [engines.translate_simple.script_store](../modules/engines.translate_simple.script_store.md), [engines.translate_simple.stage_draft](../modules/engines.translate_simple.stage_draft.md), [engines.translate_simple.stage_review](../modules/engines.translate_simple.stage_review.md), [engines.translate_simple.validate](../modules/engines.translate_simple.validate.md) |
| `tests/test_source_link.py` | [server](../modules/server.md) |
| `tests/test_split_enospc_guard.py` | [engines.split_parts](../modules/engines.split_parts.md) |
| `tests/test_translate_b1.py` | [agents.agent_hang_fix](../modules/agents.agent_hang_fix.md), [agents.agent_name_pass](../modules/agents.agent_name_pass.md), [agents.agent_pronoun_pass](../modules/agents.agent_pronoun_pass.md), [engines.llm](../modules/engines.llm.md), [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md), [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md), [engines.pronoun_register_policy](../modules/engines.pronoun_register_policy.md), [engines.series_glossary](../modules/engines.series_glossary.md), [engines.translate](../modules/engines.translate.md), [tools.preset_switcher](../modules/tools.preset_switcher.md) |
| `tests/test_translate_b1_scenarios.py` | [agents.agent_hang_fix](../modules/agents.agent_hang_fix.md), [engines.llm](../modules/engines.llm.md), [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md), [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md), [engines.pronoun_register_policy](../modules/engines.pronoun_register_policy.md), [engines.series_glossary](../modules/engines.series_glossary.md), [engines.translate](../modules/engines.translate.md), [tools.preset_switcher](../modules/tools.preset_switcher.md) |
| `tests/test_translate_b2.py` | [agents.agent_hang_fix](../modules/agents.agent_hang_fix.md), [engines.cloud_retry](../modules/engines.cloud_retry.md), [engines.llm](../modules/engines.llm.md), [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md), [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md), [engines.series_glossary](../modules/engines.series_glossary.md), [engines.translate](../modules/engines.translate.md), [tools.preset_switcher](../modules/tools.preset_switcher.md) |
| `tests/test_translate_b2_review.py` | [agents.agent_hang_fix](../modules/agents.agent_hang_fix.md), [engines.cloud_retry](../modules/engines.cloud_retry.md), [engines.llm](../modules/engines.llm.md), [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md), [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md), [engines.translate](../modules/engines.translate.md), [tests.test_translate_b2](../modules/tests.test_translate_b2.md), [tools.preset_switcher](../modules/tools.preset_switcher.md) |
| `tests/test_translate_b3.py` | [engines.cloud_retry](../modules/engines.cloud_retry.md), [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md), [engines.translate](../modules/engines.translate.md), [tests.test_translate_b2](../modules/tests.test_translate_b2.md), [tests.test_translate_b2_review](../modules/tests.test_translate_b2_review.md) |
| `tests/test_translate_force_default.py` | [server](../modules/server.md) |
| `tests/test_translate_missing.py` | [engines.translate](../modules/engines.translate.md) |
| `tests/test_translate_simple.py` | [agents.agent_name_pass](../modules/agents.agent_name_pass.md), [agents.agent_pronoun_pass](../modules/agents.agent_pronoun_pass.md), [core.config](../modules/core.config.md), [engines.cloud_retry](../modules/engines.cloud_retry.md), [engines.llm](../modules/engines.llm.md), [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md), [engines.series_glossary](../modules/engines.series_glossary.md), [engines.translate](../modules/engines.translate.md), [engines.translate_simple.cfg](../modules/engines.translate_simple.cfg.md), [engines.translate_simple.gate](../modules/engines.translate_simple.gate.md), [engines.translate_simple.lexicon](../modules/engines.translate_simple.lexicon.md), [engines.translate_simple.pipeline](../modules/engines.translate_simple.pipeline.md), [engines.translate_simple.plan_view](../modules/engines.translate_simple.plan_view.md), [engines.translate_simple.script_store](../modules/engines.translate_simple.script_store.md), [engines.translate_simple.stage_draft](../modules/engines.translate_simple.stage_draft.md), [engines.translate_simple.stage_review](../modules/engines.translate_simple.stage_review.md), [engines.translate_simple.validate](../modules/engines.translate_simple.validate.md), [server](../modules/server.md), [tools.preset_switcher](../modules/tools.preset_switcher.md) |
| `tests/test_translate_simple_a7_a8.py` | [engines.translate_simple.cfg](../modules/engines.translate_simple.cfg.md), [engines.translate_simple.plan_view](../modules/engines.translate_simple.plan_view.md), [engines.translate_simple.script_store](../modules/engines.translate_simple.script_store.md), [engines.translate_simple.stage_draft](../modules/engines.translate_simple.stage_draft.md), [engines.translate_simple.stage_review](../modules/engines.translate_simple.stage_review.md) |
| `tests/test_translate_simple_next.py` | [engines.asr.hardsub_asr](../modules/engines.asr.hardsub_asr.md), [engines.cloud_retry](../modules/engines.cloud_retry.md), [engines.hs_ocr_fast](../modules/engines.hs_ocr_fast.md), [engines.llm](../modules/engines.llm.md), [engines.series_glossary](../modules/engines.series_glossary.md), [engines.translate](../modules/engines.translate.md), [engines.translate_simple.cfg](../modules/engines.translate_simple.cfg.md), [engines.translate_simple.lexicon](../modules/engines.translate_simple.lexicon.md), [engines.translate_simple.pair_fill](../modules/engines.translate_simple.pair_fill.md), [engines.translate_simple.pair_rules](../modules/engines.translate_simple.pair_rules.md), [engines.translate_simple.pipeline](../modules/engines.translate_simple.pipeline.md), [engines.translate_simple.plan_view](../modules/engines.translate_simple.plan_view.md), [engines.translate_simple.stage_review](../modules/engines.translate_simple.stage_review.md), [engines.translate_simple.zh_source](../modules/engines.translate_simple.zh_source.md), [tests.test_translate_simple](../modules/tests.test_translate_simple.md) |
| `tests/test_translate_simple_next_review.py` | [core.film_db](../modules/core.film_db.md), [engines.asr.hardsub_asr](../modules/engines.asr.hardsub_asr.md), [engines.cloud_retry](../modules/engines.cloud_retry.md), [engines.hs_ocr_fast](../modules/engines.hs_ocr_fast.md), [engines.llm](../modules/engines.llm.md), [engines.series_glossary](../modules/engines.series_glossary.md), [engines.translate](../modules/engines.translate.md), [engines.translate_simple.pair_rules](../modules/engines.translate_simple.pair_rules.md), [engines.translate_simple.pipeline](../modules/engines.translate_simple.pipeline.md), [engines.translate_simple.plan_view](../modules/engines.translate_simple.plan_view.md), [engines.translate_simple.post](../modules/engines.translate_simple.post.md), [engines.translate_simple.script_store](../modules/engines.translate_simple.script_store.md), [engines.translate_simple.zh_source](../modules/engines.translate_simple.zh_source.md), [tests](../modules/tests.md), [tests.test_translate_simple](../modules/tests.test_translate_simple.md), [tests.test_translate_simple_next](../modules/tests.test_translate_simple_next.md) |
| `tests/test_translate_simple_scenarios.py` | [core.film_db](../modules/core.film_db.md), [engines.cloud_retry](../modules/engines.cloud_retry.md), [engines.llm](../modules/engines.llm.md), [engines.series_glossary](../modules/engines.series_glossary.md), [engines.translate](../modules/engines.translate.md), [engines.translate_simple.lexicon](../modules/engines.translate_simple.lexicon.md), [engines.translate_simple.pipeline](../modules/engines.translate_simple.pipeline.md), [engines.translate_simple.plan_view](../modules/engines.translate_simple.plan_view.md), [engines.translate_simple.script_store](../modules/engines.translate_simple.script_store.md), [engines.translate_simple.stage_review](../modules/engines.translate_simple.stage_review.md), [engines.translate_simple.validate](../modules/engines.translate_simple.validate.md), [tests.test_translate_simple](../modules/tests.test_translate_simple.md) |
| `tests/test_upload_limit_stop.py` | [agents.auto_publisher](../modules/agents.auto_publisher.md) |
| `tests/test_video_preflight.py` | [core.manifest](../modules/core.manifest.md), [engines.asr.asr](../modules/engines.asr.asr.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.mux](../modules/engines.mux.md), [engines.render](../modules/engines.render.md), [engines.separate](../modules/engines.separate.md), [engines.source_preflight](../modules/engines.source_preflight.md), [server](../modules/server.md) |
