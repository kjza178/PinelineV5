# Index module

_Sinh tự động bởi `scripts/brain_build.py` lúc 2026-11-11 02:38. Đừng sửa tay — chạy lại script._


Tổng: **160 module** (+32 test), **100,512 dòng**. Cột *Manual* = thẻ đã có phần viết tay (✅) hay chưa (·).

## control (17)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [server](../modules/server.md) | 6602 | 176 | 68 | 33 | 7 | · | server.py — Backend web Phase 1 (FastAPI). Bọc engine (download -> asr -> translate) thành |
| [routes_hg](../modules/routes_hg.md) | 1018 | 56 | 58 | 6 | ❌ | · | Cầu nối Hongguo Downloader (local :8000): /api/hg/*. Tách từ server.py (đợt 7). Chỉ được n |
| [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | 993 | 56 | 58 | 6 | 1 | · | Cầu nối Hongguo Downloader (local :8000): /api/hg/*. Tách từ server.py (đợt 7). Chỉ được n |
| [job_queue](../modules/job_queue.md) | 658 | 32 |  | 12 | 2 | · |  |
| [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | 658 | 29 | 36 | 3 | ❌ | · | routes_uploader_settings.py — API Router cho Quản lý Cài đặt (Settings) & YouTube Uploader |
| [routes_agent](../modules/routes_agent.md) | 645 | 40 | 16 | 4 | ❌ | · | AI Agent nhúng (agent_core): hook cho Runtime + /api/agent/*. Tách từ server.py (đợt 7). C |
| [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | 638 | 40 | 16 | 4 | 1 | · | AI Agent nhúng (agent_core): hook cho Runtime + /api/agent/*. Tách từ server.py (đợt 7). C |
| [routes_films](../modules/routes_films.md) | 370 | 31 | 31 | 1 | ❌ | · | FastAPI Router cho Thư viện Phim & Database (đồng bộ trực tiếp trong Pineline V4). Thay vì |
| [http_routes.routes_films](../modules/http_routes.routes_films.md) | 370 | 31 | 31 | 1 | 1 | · | FastAPI Router cho Thư viện Phim & Database (đồng bộ trực tiếp trong Pineline V4). Thay vì |
| [batch_config](../modules/batch_config.md) | 295 | 14 |  | 4 | 1 | · | Cấu hình batch dùng chung — 1 nguồn duy nhất cho Auto-pilot, Agent (queue_add), Telegram ( |
| [restart_server](../modules/restart_server.md) | 250 | 8 |  | 7 |  | · | Restart server Pineline (giữ sidecar), khôi phục hàng đợi + Auto-pilot. Port mặc định V5:  |
| [config](../modules/config.md) | 188 | 8 |  | 3 |  | · | config.py — Cấu hình/đường dẫn PORTABLE cho Pineline. Thứ tự ưu tiên khi lấy 1 giá trị: bi |
| [app_desktop](../modules/app_desktop.md) | 147 | 4 |  |  |  | · | app_desktop.py — Desktop App Studio cho Pineline V4. Sử dụng Microsoft Edge WebView2 (nati |
| [tools.context_studio.app_streamlit](../modules/tools.context_studio.app_streamlit.md) | 108 | 0 |  |  |  | · | Streamlit UI stub — Context Detection trước khi dịch Pineline. Chạy: pip install streamlit |
| [routes_ui](../modules/routes_ui.md) | 107 | 10 | 14 | 2 |  | · | Trang UI: /, /ui3, /ui4, /hongguo, /hongguo2, /films/ui, /studio, /v5-map. /hongguo2 = ski |
| [fileio](../modules/fileio.md) | 104 | 4 |  | 3 |  | · | Ghi file an toàn giữa nhiều tiến trình (server :8801, sidecar :8802, script). atomic_write |
| [http_routes.routes_ui](../modules/http_routes.routes_ui.md) | 102 | 9 | 10 | 2 | 1 | · | Trang UI chính thức V5: /, /ui3, /hongguo, /hongguo2, /workflow, /v5-map. /hongguo2 = skin |

## agent (18)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [agent_core](../modules/agent_core.md) | 2072 | 30 |  | 6 | ❌ | · | agent_core.py — AI Agent nhúng trong Pineline V2. Không gọi HTTP self. Tools gọi runtime đ |
| [agents.agent_core](../modules/agents.agent_core.md) | 2038 | 30 |  | 6 | 3 | · | agent_core.py — AI Agent nhúng trong Pineline V4. Không gọi HTTP self. Tools gọi runtime đ |
| [agents.agent_hongguo](../modules/agents.agent_hongguo.md) | 1570 | 36 |  | 3 | ❌ | · | agent_hongguo.py — Tích hợp bộ tool Hongguo Downloader & Auto-chain cho Pineline AI Agent. |
| [agent_brain](../modules/agent_brain.md) | 1221 | 34 |  | 1 | ❌ | · | Second Brain — daemon nền full-silent. Sensors → incidents → policy → actuators. Bật: AGEN |
| [agents.agent_heal](../modules/agents.agent_heal.md) | 665 | 10 |  | 1 | ❌ | · | agent_heal.py — Chẩn đoán + heal job lỗi (an toàn theo cấp). safe: heal stale running, vá  |
| [agents.agent_av_sync](../modules/agents.agent_av_sync.md) | 567 | 11 |  | 3 | ❌ | · | AV sync diagnose + heal — phát hiện lệch sub/audio / audio cụt sau mux. Các class chính: a |
| [agent_tool_loop](../modules/agent_tool_loop.md) | 475 | 11 |  |  | 1 | · | Tool loop — điều khiển pipeline theo bước, chờ kết quả thật. Khác `pineline_run_stage` (fi |
| [agents.agent_tool_loop](../modules/agents.agent_tool_loop.md) | 475 | 11 |  |  | 1 | · | Tool loop — điều khiển pipeline theo bước, chờ kết quả thật. Khác `pineline_run_stage` (fi |
| [agents.agent_watch](../modules/agents.agent_watch.md) | 375 | 19 |  | 1 | ❌ | · | Watcher A: định kỳ scan → heal safe + log + Telegram (tuỳ chọn). Env: AGENT_WATCH=1 |
| [agent_hang_fix](../modules/agent_hang_fix.md) | 368 | 9 |  | 1 | ❌ | · | Second Brain — pass LLM trace + xử lý high `hang` (đuôi treo / nửa câu). Không chỉ merge m |
| [agent_quality](../modules/agent_quality.md) | 356 | 6 |  | 1 | 1 | · | Deterministic VI quality scan + safe heals (Second Brain L2). Port từ D:\PinelineV2_tmp\_q |
| [agents.agent_stage_io](../modules/agents.agent_stage_io.md) | 286 | 14 |  |  |  | · | Peek / tóm tắt từng stage — chỉ đọc disk (an toàn). |
| [agent_brain_context](../modules/agent_brain_context.md) | 256 | 5 |  |  |  | · | System snapshot cho Second Brain LLM — toàn hệ, không chỉ 1 job. |
| [agents.agent_pronoun_pass](../modules/agents.agent_pronoun_pass.md) | 256 | 4 |  | 2 |  | · | Rà XƯNG HÔ trong bản dịch theo glossary.pronouns + genre. 1. Quét deterministic (cùng appl |
| [agent_qa_gate](../modules/agent_qa_gate.md) | 226 | 8 |  |  |  | · | Gate QA: translate → review → diff → mới cho TTS. |
| [agents.agent_qa_gate](../modules/agents.agent_qa_gate.md) | 201 | 8 |  |  |  | · | Gate QA: translate → review → diff → mới cho TTS. |
| [agents.agent_name_pass](../modules/agents.agent_name_pass.md) | 134 | 5 |  | 1 |  | · | Rà TÊN NHÂN VẬT trong bản dịch theo bảng nhân vật (glossary.json). 1. Quét: câu nào zh có  |
| [agents.agent_error_class](../modules/agents.agent_error_class.md) | 121 | 3 |  |  |  | · | Phân loại lỗi theo log / cur_text / error (ASR · TTS · mux · …). |

## sidecar (5)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [agent_tele_cmd](../modules/agent_tele_cmd.md) | 2333 | 37 |  | 12 | ❌ | · | Sidecar: Telegram lệnh + Auto-pilot + HTTP :8802 KHÔNG restart Pineline server — chỉ gọi A |
| [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md) | 2328 | 37 |  | 12 | ❌ | · | Sidecar: Telegram lệnh + Auto-pilot + HTTP :8802 KHÔNG restart Pineline server — chỉ gọi A |
| [agent_feeder](../modules/agent_feeder.md) | 2065 | 68 |  | 7 | ❌ | · | Feeder + Run-watch cho Auto-pilot (chạy trong sidecar :8802, chỉ gọi API :8801). Feeder —  |
| [agents.agent_feeder](../modules/agents.agent_feeder.md) | 2065 | 68 |  | 7 | ❌ | · | Feeder + Run-watch cho Auto-pilot (chạy trong sidecar :8802, chỉ gọi API :8801). Feeder —  |
| [agents.agent_autopilot](../modules/agents.agent_autopilot.md) | 331 | 16 |  | 4 | ❌ | · | Auto-pilot — queue need_queue + heal safe qua HTTP Pineline (PORT / PINELINE_BASE). Chạy t |

## source (9)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [hongguo_bridge](../modules/hongguo_bridge.md) | 4216 | 118 |  | 14 | ❌ | · | hongguo_bridge.py — client mỏng gọi Hongguo Downloader local API (:8000). App Hongguo phải |
| [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md) | 4210 | 118 |  | 14 | 1 | · | hongguo_bridge.py — client mỏng gọi Hongguo Downloader local API (:8000). App Hongguo phải |
| [hongguo_rpc](../modules/hongguo_rpc.md) | 1449 | 57 |  | 10 | ❌ | · | hongguo_rpc.py — JSON-RPC stdio client cho Hongguo WinUI 2.x helper.jar. Không dùng HTTP : |
| [agents.hongguo_rpc](../modules/agents.hongguo_rpc.md) | 1449 | 57 |  | 10 | ❌ | · | hongguo_rpc.py — JSON-RPC stdio client cho Hongguo WinUI 2.x helper.jar. Không dùng HTTP : |
| [engines.download](../modules/engines.download.md) | 692 | 20 |  | 2 | 1 | · | download.py — STAGE 1: Tải video (Douyin / Bilibili / TikTok / ...). Engine: yt-dlp. Tự re |
| [hongguo_license_ensure](../modules/hongguo_license_ensure.md) | 285 | 11 |  |  |  | · | Ensure Hongguo 2.x helper is license-proved (same process as hongguo_rpc). Uses DPAPI key  |
| [agents.hongguo_license_ensure](../modules/agents.hongguo_license_ensure.md) | 270 | 11 |  |  |  | · | Ensure Hongguo 2.x helper is license-proved (same process as hongguo_rpc). Uses DPAPI key  |
| [engines.playlist](../modules/engines.playlist.md) | 214 | 5 |  |  |  | · | playlist.py — Bóc 1 link thành DANH SÁCH video rồi tải hàng loạt. Vì sao tách riêng: Pinel |
| [hg_ui_ctx](../modules/hg_ui_ctx.md) | 46 | 4 |  | 2 |  | · | Per-request Hongguo UI backend context (không reload — tránh mất override). Hongguo1 vs Ho |

## asr (16)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [engines.asr.fun_asr_nano](../modules/engines.asr.fun_asr_nano.md) | 597 | 11 |  | 1 | ❌ | · | fun_asr_nano.py — STAGE ASR bằng Fun-ASR-Nano (chất lượng tiếng Trung cao nhất). Model : F |
| [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md) | 546 | 16 |  |  | ❌ | · | asr_repair.py — Hậu kỳ Hybrid: A lấp lỗ + B sửa nghe sai + FA. A) Gap: Para có thoại, bản  |
| [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md) | 464 | 14 |  |  | ❌ | · | asr_spam.py — Chặn ASR nuốt tiếng nền (cười/rên 哈·啊·呃 lặp). Không dựa vào check tay: sau m |
| [engines.asr.hardsub_asr](../modules/engines.asr.hardsub_asr.md) | 452 | 12 |  |  | ❌ | · | hardsub_asr.py — OCR hardsub chỉ để RÀ SOÁT / SỬA sub ZH (asr · srt). Một nhiệm vụ: RapidO |
| [engines.asr.asr](../modules/engines.asr.asr.md) | 442 | 13 |  | 1 | 1 | · | asr.py — STAGE 2 (phần đầu): tách audio + nhận diện lời (Whisper). Đầu vào : work/<job>/so |
| [engines.asr.asr_align_nano_para](../modules/engines.asr.asr_align_nano_para.md) | 384 | 10 |  |  | ❌ | · | asr_align_nano_para.py — Hybrid A: chữ Fun-ASR-Nano + timestamp Paraformer (char-ts). Đầu  |
| [engines.separate](../modules/engines.separate.md) | 370 | 8 |  |  | 1 | · | separate.py — STAGE 6 (Tách nền): dùng Demucs bỏ GIỌNG NÓI (tiếng Trung) khỏi audio gốc, G |
| [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md) | 346 | 5 |  | 1 | ❌ | · | firered_asr.py — STAGE ASR bằng FireRedASR2-AED (system VAD+LID+ASR+Punc). Cần clone repo  |
| [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md) | 337 | 5 |  |  | ❌ | · | nano_fa_asr.py — SOTA ASR: Fun-ASR-Nano (Chữ chuẩn nhất) + Direct Qwen3-ForcedAligner (Mốc |
| [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md) | 330 | 7 |  |  | ❌ | · | asr_fix_align.py — Phương án 3: fix monotonic_fix Bước 1 (fallback): chỗ timing bịa/đảo →  |
| [engines.asr.paraformer_zh](../modules/engines.asr.paraformer_zh.md) | 309 | 2 |  | 1 | ❌ | · | paraformer_zh.py — STAGE ASR bằng FunASR Paraformer-zh (timestamp tốt cho phụ đề/TTS). Mod |
| [engines.ocr](../modules/engines.ocr.md) | 273 | 8 |  |  | 1 | · | ocr.py — STAGE OCR: đọc chữ TRÊN HÌNH (tên nhân vật / địa danh / caption / thẻ) mà KHÔNG n |
| [engines.asr.sensevoice_asr](../modules/engines.asr.sensevoice_asr.md) | 255 | 4 |  | 1 |  | · | sensevoice_asr.py — STAGE ASR bằng FunASR SenseVoiceSmall (nhanh, đa ngôn ngữ). Model : ii |
| [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md) | 202 | 3 |  |  |  | · | hybrid_asr.py — ASR chốt: Nano chữ + Para timing + ForcedAlign + Repair. Pipeline (sidecar |
| [engines.asr.asr_vad_utils](../modules/engines.asr.asr_vad_utils.md) | 158 | 5 |  |  |  | · | asr_vad_utils.py — VAD kwargs FunASR thật + pad/overlap khi cắt đoạn. FunASR fsmn-vad (1.4 |
| [engines.asr.asr_hybrid_progress](../modules/engines.asr.asr_hybrid_progress.md) | 144 | 5 |  |  |  | · | asr_hybrid_progress.py — Đưa tiến độ sidecar (Nano/Para) vào stages.asr cho UI Hybrid. UI  |

## translate (15)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [translate](../modules/translate.md) | 4083 | 74 |  | 20 | 2 | · | translate.py — STAGE dịch: "lập phương án" (hồ sơ nhân vật + XƯNG HÔ) rồi dịch CÓ NGỮ CẢNH |
| [engines.translate](../modules/engines.translate.md) | 2992 | 53 |  | 20 | 3 | · | translate.py — STAGE dịch: "lập phương án" (hồ sơ nhân vật + XƯNG HÔ) rồi dịch CÓ NGỮ CẢNH |
| [llm](../modules/llm.md) | 894 | 23 |  | 4 | ❌ | · | llm.py — Gọi LLM qua 9router API (tương thích chuẩn OpenAI). Cấu hình qua config.json / pi |
| [engines.llm](../modules/engines.llm.md) | 872 | 23 |  | 4 | 2 | · | llm.py — Gọi LLM qua 9router API (tương thích chuẩn OpenAI). Cấu hình qua config.json / pi |
| [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) | 870 | 30 |  | 2 | 1 | · | Đồng nhất xưng hô không cần diarization (A–C + vá câu đỏ). A) analyze_full_zh: quét TOÀN B |
| [hv_auditor](../modules/hv_auditor.md) | 475 | 15 |  | 1 | ❌ | · | Hán-Việt auditor — chống glossary khóa sai âm (vd 逆→Nghị thay vì Nghịch). 1) Unihan kVietn |
| [engines.hv_auditor](../modules/engines.hv_auditor.md) | 457 | 15 |  | 1 | ❌ | · | Hán-Việt auditor — chống glossary khóa sai âm (vd 逆→Nghị thay vì Nghịch). 1) Unihan kVietn |
| [engines.translate_alts](../modules/engines.translate_alts.md) | 377 | 5 |  | 1 | ❌ | · | Phương án dịch tối ưu — ngữ cảnh + văn phong (trọng tâm Pineline). Quét câu dễ lệch / đa n |
| [mt_zh_vi](../modules/mt_zh_vi.md) | 302 | 14 |  | 1 | ❌ | · | NMT ZH→VI (HachimiMT) — DỊCH CHÍNH; LLM chỉ rà soát (run_review). Config: MT_ZH_VI=1       |
| [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md) | 302 | 14 |  | 1 | ❌ | · | NMT ZH→VI (HachimiMT) — DỊCH CHÍNH; LLM chỉ rà soát (run_review). Config: MT_ZH_VI=1       |
| [pronoun_register_policy](../modules/pronoun_register_policy.md) | 243 | 8 |  |  |  | · | Policy xưng hô tổng quát cho mix #1+#3 — không gắn 1 job/phim. Mục tiêu: - Phát hiện cửa s |
| [series_glossary](../modules/series_glossary.md) | 199 | 11 |  | 4 |  | · | Bảng nhân vật / thuật ngữ / xưng hô dùng chung cho CẢ BỘ (mọi mùa). - apply(work_dir, plan |
| [engines.series_glossary](../modules/engines.series_glossary.md) | 176 | 10 |  | 4 |  | · | Bảng nhân vật / thuật ngữ / xưng hô dùng chung cho CẢ BỘ (mọi mùa). - apply(work_dir, plan |
| [engines.title_mt](../modules/engines.title_mt.md) | 172 | 6 |  | 2 |  | · | Dịch thô tiêu đề Trung → Việt (Google gtx, không cần API key). Chỉ để duyệt Hongguo cho bi |
| [engines.script_lint](../modules/engines.script_lint.md) | 170 | 10 |  |  |  | · | Soát lỗi máy móc bản dịch VI (script.json) — chạy SAU review/polish, trước TTS. autofix_ro |

## tts (3)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [engines.clone_tts](../modules/engines.clone_tts.md) | 1115 | 38 |  | 1 | 1 | · | clone_tts.py — STAGE Lồng tiếng bằng TTS zero-shot clone tiếng Việt. Hai engine, cùng regi |
| [rvc_bridge.vieneu_batch](../modules/rvc_bridge.vieneu_batch.md) | 183 | 5 |  | 1 |  | · | Worker VieNeu-TTS v3-Turbo (chạy trong D:/vieneu_env). Đọc job json: {out_dir, ref, text,  |
| [rvc_bridge.omnivoice_batch](../modules/rvc_bridge.omnivoice_batch.md) | 47 | 1 |  | 1 |  | · | Worker omnivoice-vietnamese (chạy trong D:/OmniVoiceStudio-v2/.venv). Đọc job json: {out_d |

## render (10)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [render](../modules/render.md) | 3079 | 72 |  | 14 | 1 | · | render.py — STAGE 7 (Ghép + xuất): ráp video lồng tiếng "sạch như bản localize". Video (1  |
| [engines.render](../modules/engines.render.md) | 3079 | 72 |  | 14 | 3 | · | render.py — STAGE 7 (Ghép + xuất): ráp video lồng tiếng "sạch như bản localize". Video (1  |
| [engines.subs](../modules/engines.subs.md) | 1106 | 34 |  |  | ❌ | · | subs.py — Sinh phụ đề .srt từ danh sách câu có timestamp. Dùng chung: asr.json (tiếng Trun |
| [engines.split_parts](../modules/engines.split_parts.md) | 845 | 19 |  | 6 | 1 | · | split_parts.py — Tự động tính toán và chia video dài (3h-12h+) thành các Part 2-2.5h để ch |
| [split_parts](../modules/split_parts.md) | 828 | 17 |  | 6 | ❌ | · | split_parts.py — Tự động tính toán và chia video dài (3h-12h+) thành các Part 2-2.5h để ch |
| [engines.render_fx](../modules/engines.render_fx.md) | 564 | 32 |  |  | 1 | · | Helpers: uniqueness filters + library BGM paths (copyright-safe audio). |
| [engines.sfx_lib](../modules/engines.sfx_lib.md) | 438 | 21 |  | 1 | 2 | · | sfx_lib.py — chế độ audio `sfx_lib`: giọng Việt + TIẾNG ĐỘNG gốc + NHẠC KHO SẠCH theo mức. |
| [engines.assemble](../modules/engines.assemble.md) | 417 | 16 |  | 2 | 1 | · | assemble.py — Ghép clip TTS thành MỘT track + kiểm khớp SRT. Hai chế độ: - assemble()      |
| [engines.media_ts](../modules/engines.media_ts.md) | 304 | 14 |  | 3 | ❌ | · | Mốc thời gian tiếng của file nguồn — sửa tiếng "dồn mẫu" ở file ghép nhiều tập. File ghép  |
| [engines.mux](../modules/engines.mux.md) | 135 | 5 |  | 3 |  | · | mux.py — STAGE cuối: ghép track lồng tiếng vào video -> output.mp4 (thuyết minh). Kiểu thu |

## publish (11)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [meta_studio](../modules/meta_studio.md) | 1918 | 32 |  | 3 | ❌ | · | meta_studio.py — Module sinh Metadata YouTube (Title / Description / Tags / AI Image Promp |
| [agents.meta_studio](../modules/agents.meta_studio.md) | 1897 | 30 |  | 3 | 1 | · | meta_studio.py — Module sinh Metadata YouTube (Title / Description / Tags / AI Image Promp |
| [auto_publisher](../modules/auto_publisher.md) | 1567 | 36 |  | 6 | ❌ | · | auto_publisher.py — Tự động hoá toàn trình: Sau khi render xong → Tự tạo Metadata SEO & Th |
| [agents.auto_publisher](../modules/agents.auto_publisher.md) | 1555 | 36 |  | 6 | 3 | · | auto_publisher.py — Tự động hoá toàn trình: Sau khi render xong → Tự tạo Metadata SEO & Th |
| [test_channel](../modules/test_channel.md) | 1435 | 38 |  | 3 | ❌ | · | test_channel.py — Quản lý Kênh Phụ Test (Burner Channel) độc lập trong Pineline. Chức năng |
| [agents.test_channel](../modules/agents.test_channel.md) | 1283 | 32 |  | 3 | ❌ | · | test_channel.py — Quản lý Kênh Phụ Test (Burner Channel) độc lập trong Pineline. Chức năng |
| [tools.test_channel](../modules/tools.test_channel.md) | 1283 | 32 |  | 3 | ❌ | · | test_channel.py — Quản lý Kênh Phụ Test (Burner Channel) độc lập trong Pineline. Chức năng |
| [film_db](../modules/film_db.md) | 1091 | 42 |  | 5 | ❌ | · | Database phim đã làm (SQLite) — nguồn sự thật lâu dài, không mất khi xoá thư mục job. film |
| [uploader_settings_api](../modules/uploader_settings_api.md) | 670 | 31 |  | 2 | ❌ | · | Settings + YouTube Uploader API — dùng được từ sidecar :8802 (stdlib) và FastAPI. Trả về ( |
| [agents.canva_client](../modules/agents.canva_client.md) | 406 | 12 |  |  | ❌ | · | canva_client.py — Tích hợp Canva Connect API chính thức cho Pineline. Quản lý OAuth2 (PKCE |
| [films_merge_api](../modules/films_merge_api.md) | 174 | 10 |  | 1 |  | · | Gộp parts (split jobs) + scan job đã làm sẵn sàng merge — dùng từ sidecar :8802. |

## core (8)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [core.film_db](../modules/core.film_db.md) | 1064 | 41 |  | 5 | 3 | · | Database phim đã làm (SQLite) — nguồn sự thật lâu dài, không mất khi xoá thư mục job. film |
| [core.job_queue](../modules/core.job_queue.md) | 658 | 32 |  | 12 | 4 | ✅ |  |
| [core.batch_config](../modules/core.batch_config.md) | 282 | 13 |  | 4 |  | · | Cấu hình batch dùng chung — 1 nguồn duy nhất cho Auto-pilot, Agent (queue_add), Telegram ( |
| [core.manifest](../modules/core.manifest.md) | 242 | 4 |  | 3 | 2 | ✅ | manifest.py — Trạng thái/checkpoint cho pipeline. Mỗi job (mỗi video) có một thư mục làm v |
| [core.config](../modules/core.config.md) | 201 | 9 |  | 3 | 2 | ✅ | config.py — Cấu hình/đường dẫn PORTABLE cho Pineline. Thứ tự ưu tiên khi lấy 1 giá trị: bi |
| [core.job_meta](../modules/core.job_meta.md) | 164 | 5 |  | 1 | 1 | · | Parse metadata hàng chờ (series/season UI) — dùng chung film_db sync + job_queue. |
| [core.fileio](../modules/core.fileio.md) | 104 | 4 |  | 3 |  | · | Ghi file an toàn giữa nhiều tiến trình (server :8801, sidecar :8802, script). atomic_write |
| [core.__init__](../modules/core.__init__.md) | 1 | 0 |  |  |  | · | PinelineV5 app core: config, queue, DB, manifest, fileio. |

## ops (28)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [scripts.brain_build](../modules/scripts.brain_build.md) | 857 | 23 |  |  | ❌ | · | brain_build.py — Sinh/làm mới phần TỰ ĐỘNG của Second Brain (docs/brain/). Đọc mã nguồn bằ |
| [scripts.check_batch4](../modules/scripts.check_batch4.md) | 457 | 6 |  | 2 | ❌ | · | Kiểm thử đợt 4 (tranh chấp ghi manifest, claim endpoint, single-instance, worker khởi động |
| [tools.lib_check](../modules/tools.lib_check.md) | 411 | 9 |  |  | ❌ | · | lib_check.py — Kiểm tra bản quyền / Block YouTube cho Phim trong Thư viện gốc (D:\Lib) trư |
| [engines.check_block](../modules/engines.check_block.md) | 350 | 4 |  |  | ❌ | · | check_block.py — Module kiểm tra trạng thái Bản quyền / Block YouTube (Cơ chế 1: Không cần |
| [scripts.check_batch5](../modules/scripts.check_batch5.md) | 347 | 6 |  | 1 | ❌ | · | Kiểm thử đợt 5 (agent an toàn): lệnh / bắt buộc, phân tầng tool + xác nhận ✅/❌, hg_auto_fl |
| [scripts._patch_hongguo2_update_ux](../modules/scripts._patch_hongguo2_update_ux.md) | 327 | 0 |  |  | ❌ | · | One-shot: hongguo2 Update UX when seasons is null + layout. |
| [scripts.check_batch2](../modules/scripts.check_batch2.md) | 327 | 9 | 2 | 2 | ❌ | · | Kiểm thử đợt 2 (bảo mật + config 1 nguồn + LLM lỗi dừng stage). KHÔNG chạm server/sidecar  |
| [scripts.check_batch1](../modules/scripts.check_batch1.md) | 307 | 11 |  | 2 | ❌ | · | Test đợt 1 (chặn mất dữ liệu) — chỉ dùng thư mục tạm, không đụng job/queue/thư viện thật. |
| [tools.migrate_work](../modules/tools.migrate_work.md) | 299 | 12 |  | 1 | 1 | · | Chuyển Z:\PinelineV5\work sang ổ khác (mặc định D:\PinelineV5_work) giữa 2 job, không mất  |
| [scripts.tree_audit](../modules/scripts.tree_audit.md) | 226 | 9 |  |  |  | · | tree_audit.py — Kiểm tra sức khoẻ cây code Pineline (V2/V4/V5) sau mỗi lần sync/port. Chỉ  |
| [scripts._patch_hongguo2_discover_only](../modules/scripts._patch_hongguo2_discover_only.md) | 221 | 0 |  |  |  | · | Hongguo2: Tìm mùa mới (info-only) + làm rõ Update thư viện tải tập thiếu. |
| [tools.preset_switcher](../modules/tools.preset_switcher.md) | 209 | 4 |  |  |  | · | preset_switcher.py — Tự động chuyển đổi Preset Model trên llama-server (:8083) Quản lý bộ  |
| [tools.pick_dirs_dialog](../modules/tools.pick_dirs_dialog.md) | 204 | 4 |  |  |  | · | Hộp thoại chọn NHIỀU folder cùng lúc (Listbox multi-select). Chạy: python tools/pick_dirs_ |
| [scripts.check_batch3](../modules/scripts.check_batch3.md) | 202 | 1 |  | 3 |  | · | Kiểm thử đợt 3 (opts một nguồn X1, config file-first X2, ghi nguyên tử + khoá S13). Chạy t |
| [scripts._tmp_extract_sigs_batch2](../modules/scripts._tmp_extract_sigs_batch2.md) | 191 | 5 |  |  |  | · | One-shot AST signature extract for func-sigs batch2. Delete after use OK. |
| [scripts.check_cookies](../modules/scripts.check_cookies.md) | 172 | 5 |  |  |  | · | check_cookies.py — Soi file cookie: còn hạn không, đã ĐĂNG NHẬP chưa, và có lấy được HD kh |
| [scripts._rebuild_v5_map_funcs](../modules/scripts._rebuild_v5_map_funcs.md) | 147 | 0 |  |  |  | · | Rebuild MODULE_FUNCS + funcKeys in static/ui/v5-map.html from func-sigs/*.md. |
| [scripts._patch_hongguo2_discover_api](../modules/scripts._patch_hongguo2_discover_api.md) | 113 | 0 |  |  |  | · | Replace client-side lsnDiscoverNew with API /api/hg/library/seasons/discover. |
| [scripts.gen_sample_assets](../modules/scripts.gen_sample_assets.md) | 108 | 4 |  |  |  | · | Tạo sample assets cho Pineline (grain / LUT / BGM). Chạy:  python scripts/gen_sample_asset |
| [engines.vram](../modules/engines.vram.md) | 89 | 4 |  |  |  | · | vram.py — Nhả VRAM trước MỖI bước dùng GPU. Ollama (Gemma ctx 128k), FunASR, Demucs, TTS,  |
| [scripts._port_hg_watchlist_bridge](../modules/scripts._port_hg_watchlist_bridge.md) | 41 | 0 |  |  |  | · |  |
| [scripts._port_hg_watchlist_film_db](../modules/scripts._port_hg_watchlist_film_db.md) | 38 | 0 |  |  |  | · |  |
| [scripts._tmp_inspect_films_db2](../modules/scripts._tmp_inspect_films_db2.md) | 35 | 0 |  |  |  | · |  |
| [scripts.check_sidecar_lock](../modules/scripts.check_sidecar_lock.md) | 29 | 0 |  |  |  | · |  |
| [scripts.download_firered_models](../modules/scripts.download_firered_models.md) | 29 | 1 |  |  |  | · | Download FireRedASR2S models into FIRERED_MODELS (default D:/AI_CACHE/firered). |
| [scripts._hg_watchlist_snippet](../modules/scripts._hg_watchlist_snippet.md) | 26 | 0 |  |  |  | · | Snippet appended into film_db.py — hg_watchlist helpers. |
| [scripts._tmp_inspect_films_db](../modules/scripts._tmp_inspect_films_db.md) | 26 | 0 |  |  |  | · |  |
| [scripts._tmp_count_sigs](../modules/scripts._tmp_count_sigs.md) | 17 | 0 |  |  |  | · |  |

## misc (20)

| Module | Dòng | Hàm | Routes | Fix | Test | Manual | Tóm tắt |
|---|---:|---:|---:|---:|---:|:-:|---|
| [tools.context_studio.character_mapper](../modules/tools.context_studio.character_mapper.md) | 353 | 10 |  |  | ❌ | · | 02 — Character + relation map: ai tự xưng gì khi nói với ai. |
| [tools.context_studio.address_lexicon](../modules/tools.context_studio.address_lexicon.md) | 338 | 4 |  |  | ❌ | · | Kho xưng hô cổ trang / võ hiệp / tu tiên (VN dịch Trung). Nguồn tham chiếu (quy ước văn họ |
| [tools.context_studio.analyzer](../modules/tools.context_studio.analyzer.md) | 264 | 5 |  |  |  | · | 01 — Context analyzer: SRT Trung → glossary draft (+ style_lock). |
| [tools.context_studio.schema](../modules/tools.context_studio.schema.md) | 129 | 3 |  |  |  | · | Heuristic number / name flags — không sửa transcript. |
| [tools.context_studio.srt_io](../modules/tools.context_studio.srt_io.md) | 99 | 4 |  |  |  | · | Parse SRT / asr.json → list[{i, start, end, text}]. |
| [pineline.server.routes.jobs](../modules/pineline.server.routes.jobs.md) | 79 | 1 |  | 1 | 1 | · | Jobs API: /api/jobs/* — LIVE registry trong khung pineline V5. Thân handler vẫn trong root |
| [tools.context_studio.exporter](../modules/tools.context_studio.exporter.md) | 73 | 1 |  |  |  | · | 05 — Export context pack vào thư mục job Pineline (hoặc out/). |
| [tools.context_studio.__main__](../modules/tools.context_studio.__main__.md) | 67 | 1 |  |  |  | · | CLI: python -m tools.context_studio analyze <srt/asr.json> -o work/<job> Chỉ PRE-SCAN — kh |
| [pineline.server.routes.queue](../modules/pineline.server.routes.queue.md) | 38 | 1 |  | 5 | 1 | · | Queue API: /api/queue/* (+ alias /api/jobs/group) — LIVE registry. Thân handler giữ trong  |
| [pineline.server.routes.assets](../modules/pineline.server.routes.assets.md) | 32 | 1 |  | 1 |  | · | Assets + LLM models: cookies / voices / frames / brand / clone — LIVE registry. Thân handl |
| [pineline.server.routes.fs](../modules/pineline.server.routes.fs.md) | 23 | 1 |  | 1 |  | · | FS picker: /api/fs/* — LIVE registry (body trong server.py). |
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
| `tests/test_agent_core_smoke.py` | [agents.agent_core](../modules/agents.agent_core.md), [core.manifest](../modules/core.manifest.md) |
| `tests/test_agent_parser.py` | [agents.agent_core](../modules/agents.agent_core.md) |
| `tests/test_agent_quality.py` | [agent_quality](../modules/agent_quality.md) |
| `tests/test_agent_tool_loop.py` | [agent_tool_loop](../modules/agent_tool_loop.md), [agents.agent_tool_loop](../modules/agents.agent_tool_loop.md) |
| `tests/test_asr_demucs.py` | [core.manifest](../modules/core.manifest.md), [engines.asr.asr](../modules/engines.asr.asr.md) |
| `tests/test_auto_publisher_dedup.py` | [agents.auto_publisher](../modules/agents.auto_publisher.md), [core.film_db](../modules/core.film_db.md) |
| `tests/test_chatgpt_route.py` | [core.config](../modules/core.config.md), [engines.llm](../modules/engines.llm.md) |
| `tests/test_film_db_queue_meta.py` | [core.film_db](../modules/core.film_db.md), [core.job_meta](../modules/core.job_meta.md), [core.job_queue](../modules/core.job_queue.md) |
| `tests/test_hardsub_blur_toggle.py` | [batch_config](../modules/batch_config.md), [server](../modules/server.md) |
| `tests/test_hg_merge_queue.py` | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md) |
| `tests/test_job_queue.py` | [core.job_queue](../modules/core.job_queue.md) |
| `tests/test_job_queue_worker.py` | [job_queue](../modules/job_queue.md) |
| `tests/test_layout_paths.py` | [agents.agent_core](../modules/agents.agent_core.md), [core.config](../modules/core.config.md), [core.job_queue](../modules/core.job_queue.md), [engines.assemble](../modules/engines.assemble.md), [engines.clone_tts](../modules/engines.clone_tts.md), [engines.download](../modules/engines.download.md), [engines.llm](../modules/engines.llm.md), [engines.ocr](../modules/engines.ocr.md), [engines.render](../modules/engines.render.md), [engines.render_fx](../modules/engines.render_fx.md), [engines.separate](../modules/engines.separate.md), [engines.sfx_lib](../modules/engines.sfx_lib.md), [engines.translate](../modules/engines.translate.md), [http_routes.routes_films](../modules/http_routes.routes_films.md), [http_routes.routes_ui](../modules/http_routes.routes_ui.md), [job_queue](../modules/job_queue.md), [render](../modules/render.md), [server](../modules/server.md) |
| `tests/test_meta_and_thumb.py` | [agents.auto_publisher](../modules/agents.auto_publisher.md), [agents.meta_studio](../modules/agents.meta_studio.md) |
| `tests/test_pronoun_consistency.py` | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) |
| `tests/test_pronoun_postpass.py` | [engines.translate](../modules/engines.translate.md) |
| `tests/test_pronoun_qa_slim_plan.py` | [engines.translate](../modules/engines.translate.md) |
| `tests/test_queue_http_state.py` | [core.film_db](../modules/core.film_db.md), [core.job_queue](../modules/core.job_queue.md), [pineline.server.routes.jobs](../modules/pineline.server.routes.jobs.md), [pineline.server.routes.queue](../modules/pineline.server.routes.queue.md) |
| `tests/test_queue_jobs_api.py` | [server](../modules/server.md) |
| `tests/test_queue_run_one.py` | [server](../modules/server.md) |
| `tests/test_render_expr.py` | [engines.render](../modules/engines.render.md) |
| `tests/test_restart_guard.py` | [tools.migrate_work](../modules/tools.migrate_work.md) |
| `tests/test_review_batches.py` | — |
| `tests/test_review_parallel_workers.py` | [translate](../modules/translate.md) |
| `tests/test_review_pass1_upload.py` | [translate](../modules/translate.md) |
| `tests/test_server_split.py` | [http_routes.routes_agent](../modules/http_routes.routes_agent.md), [http_routes.routes_hg](../modules/http_routes.routes_hg.md), [server](../modules/server.md) |
| `tests/test_sfx_lib.py` | [engines.render](../modules/engines.render.md), [engines.sfx_lib](../modules/engines.sfx_lib.md) |
| `tests/test_source_link.py` | [server](../modules/server.md) |
| `tests/test_split_enospc_guard.py` | [engines.split_parts](../modules/engines.split_parts.md) |
| `tests/test_translate_force_default.py` | [server](../modules/server.md) |
| `tests/test_upload_limit_stop.py` | [agents.auto_publisher](../modules/agents.auto_publisher.md) |
