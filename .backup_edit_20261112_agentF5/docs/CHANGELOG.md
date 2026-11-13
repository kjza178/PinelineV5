# Changelog

Mới nhất trên cùng. Mỗi mục: file/hàm — thay đổi — cần restart gì. Chi tiết bug: docs/fixes/. Nhật ký phiên: docs/worklog/.

## 2026-11-11

- machine-config: mới `core/machine.py` — cổng/thư mục phụ thuộc máy thành key config (mặc định = máy gốc): LLAMA_BASE_URL,
  AUTO_SWITCH_PRESETS, MODEL_PRESETS_DIR, MODEL_START_SCRIPT, MODEL_START_CMD, CHATGPT/AURORA_BASE_URL, AURORA_FALLBACK_URLS,
  CLOUD_LLM_BASE_URL, HONGGUO_BASE_URL, MT_MODEL_DIR, LIBRARY_DIR, YT_UPLOADER_DIR, LIB_SAMPLE_DIR. preset_switcher bỏ qua
  (không lỗi) khi thiếu presets/AUTO_SWITCH_PRESETS=0; Aurora hỏng → lỗi rõ + gợi ý đổi PLAN/REVIEW model. Doctor
  `scripts/check_env.py`, `docs/SETUP_MAY_MOI.md`. Restart server để module đọc lại (đa số key đọc lúc gọi).
  docs/fixes/2026-11-11-machine-config.md

- **[V5] Chạy lại được — bố cục package** (~03:00). `scripts/sync_from_v2.py --apply`: 77 file vào core/engines/agents/http_routes/tools, 531 import viết lại, 35 bản trùng root → `_to_delete\root_dupes_20261111_0252\`; kèm mọi fix B1–B10 của V2. `tree_audit` ERROR 51 → 0; smoke import 85/85; test 12/12 (VM). Fix `docs/fixes/2026-11-11-v5-package-sync.md`. Bak `.backup_sync_20261111_*\`. **Chạy pytest + start :8805 trên Windows để xác nhận.**

- **[V5] Review port — V5 KHÔNG khởi động được** (~02:45). `server.py` V5 == V2 (import phẳng không có trong bố cục package) + 21 cặp module root/package lệch. **Chưa sửa code — chờ user chốt hướng A/B/C** (`docs/reviews/2026-11-11-v4-v5-port-review.md`). Tooling: `scripts/brain_build.py`, `scripts/tree_audit.py` (ERROR=51), `docs/brain/`, `claude_setup/`, `CLAUDE.md`. **Không restart.**

- **Studio SOP 1 job/ghế + Aurora∥ REVIEW** (~00:10). User khóa: ASR→NMT→REVIEW (Aurora∥ / local fallback)→TTS→mux→Done→next. `_auto_gpu` chạy hết `run_review` trong ghế (không nhả sớm); `translate` fan-out `REVIEW_PARALLEL=6`; config keys. Bak `…_studio-1job-pipeline\`. Fix `docs/fixes/2026-11-11-studio-1job-pipeline.md`. Sync V2/V4/V5. **Restart :8801** để nạp (cắt `365baf` nếu đang dịch).

## 2026-11-10

- **Queue park HOLD/soát — không nhảy job** (~23:57). Studio invariant: 1 job→output. `_worker_loop` park khi `held`/`waiting_review`; `_auto_gpu` stamp `held_at=waiting_review`; QA gate stamp HOLD; `set_park_ready_hook`. Bak zip `…_2357.zip` + codebak `…_queue-park-held\`. Fix `docs/fixes/2026-11-10-queue-park-held.md`. Sync V2/V4/V5. **Restart :8801** (cắt current `365baf` nếu restart ngay — hỏi user).

- **REVIEW voice loosen (Aurora)** (~19:28). User chọn nới REVIEW: văn phong tự nhiên khi vá lỗi, không full rewrite. `review_batch` + `_style_voice_banner`; restart CLI gpt-6 60892. Bak `…_review-voice-loosen`. Fix `docs/fixes/2026-11-10-review-voice-loosen.md`. **Không cần restart server** (CLI).

- **REVIEW = chatgpt/gpt-6 (Aurora thật)** (~19:20). User chọn gpt-6; UI Aurora trước chỉ lưu queue_opts. Wire `_resolve_review_model`; config REVIEW_MODEL/AURORA_REVIEW_MODEL; stop Gemma; CLI force re-review 60892 p01+p02. Bak codebak `…_review-gpt6`. Fix `docs/fixes/2026-11-10-review-gpt6-aurora.md`. Sync V2/V4/V5. **Restart :8801** khi rảnh (CLI đang review).

- **Brain hang LLM trace+fix** (~19:00). User B: không chỉ merge — LLM hiểu root/plan rồi mới mở HOLD. `agent_hang_fix.py` (+ wire `scan_and_heal_job`, cuối `run_review`); `hang_ack` cho dialogue_trail; skip khi review đang ghi. Config `BRAIN_HANG_FIX=1`. Job `60892` p01 clear HOLD + TTS; p02 chờ review. Bak zip `…_1857.zip` + codebak `…_hang-llm-fix`. Fix `docs/fixes/2026-11-10-brain-hang-llm-fix.md`. Sync V2/V4/V5. **Restart :8801** khi rảnh để nạp in-process (CLI/review subprocess đã thấy module mới).

- **Brain TG report** (~13:27). AGENT_BRAIN_TELEGRAM=report + digest ~120s; standalone D:\\PinelineV2_tmp\\_run_brain_tg_report.py (không restart :8801 đang ASR). **Restart :8801** sau để nạp in-process.

- **FireRed BF16 forced_align** (~13:20). Cast logits→float32 trước torchaudio align (BF16 decode giữ). Vendor fireredasr_aed.py V2/V4/V5. Fix docs/fixes/2026-11-10-firered-bf16-align.md. **Không cần restart server** nếu ASR là subprocess mới.

- **FIRERED_ROOT + _check_stopped** (~13:13). Config FIRERED_ROOT sai path cũ Z:/Pineline/vendor/... → Z:/PinelineV2/vendor/FireRedASR2S. Thêm server._check_stopped (ASR split ≥3h NameError). Fix docs/fixes/2026-11-10-firered-root-path.md. **Restart :8801** nếu env còn FIRERED_ROOT cũ.



- **Mix #1+#3 title→ngươi + UI REVIEW backup** (~08:50). Bak zip `…_0847.zip` + codebak `…_mix13-review-backup`. `pronoun_register_policy.py`; `agent_pronoun_pass` #3; `review_batch` mask #1; config `PRONOUN_TITLE_POLICY=1` `REVIEW_PRONOUN_MASK=1`; UI/batch `review_backup=off|aurora_parallel`. Sync V2/V4/V5. Fix `docs/fixes/2026-11-10-mix13-title-nguoi.md`. **Restart:** :8801 để nạp translate/pronoun/UI.
- **NMT GPU** — MT_ZH_VI_DEVICE=cuda + MT_ZH_VI_BATCH=256 (bench 800 cue: CPU~200 → CUDA~1089 cue/s). Bak Z:\\PinelineV2_codebak\\2026-11-10_mt-cuda-batch\\ + zip Z:\\PinelineV2_backup_2026-11-10_0841.zip. Sync V2/V4/V5 config. **Restart:** :8801 nếu process đã load NMT trên CPU.\n- **firered_asr.py** — mặc định `use_half=True` (BF16 trên 3060) khi GPU; tắt bằng `FIRERED_USE_HALF=0`. Bak `Z:\PinelineV2_codebak\2026-11-10_firered-use-half\` + zip `Z:\PinelineV2_backup_2026-11-10_0827.zip`. **Restart:** server :8801.
- **run_v2.bat / run.bat / run_tele_cmd.bat** — LF→CRLF fix (CMD `if not exist`); bak `Z:\PinelineV2_codebak\2026-11-10_run-v2-crlf\`. **Restart:** `run_v2.bat`.
- **Restart :8801 nạp Brain C** (~00:36). `restart_server.py --clean-env` PID **4652**; tắt standalone. Sau restart TTS `05670` lọt ~104 câu (HOLD/override mất) → stop + HOLD lại + sửa cue i=34 trùng VI với i=35. Queue bị clear (requeued 0). **Không cần restart lại.**

## 2026-11-09

- **Brain C = LLM tool-loop** (~00:15 10/11). Backup zip `…_0007.zip` + codebak `…_brain-force-tool\`. User chọn C: Brain điều phối `agent_core` 24/7. `agent_brain_context` snapshot; `llm_tick` bind FS/HTTP Runtime + `force_first_tool=pineline_status` + deep `pineline_job`; `agent_core.run_agent` nhận `force_first_tool`/`force_first_args`; chat API field tương ứng. Smoke: 7 tools (status→job→hold→running_check), HOLD `05670`. Fix `docs/fixes/2026-11-09-brain-llm-tool-loop.md`. Sync V2/V4/V5. Standalone loop nạp code mới. **Restart :8801** khi 05670 idle để nạp in-process brain + force_first_tool vào server.

- **Second Brain Agent (full silent)** (~23:49). Backup `…_second-brain\`. Module `agent_quality.py` + `agent_brain.py`; QA gate xét `qa_brain.json` high; auto TTS HOLD trước khi lồng; startup `_start_agent_brain`; config `AGENT_BRAIN=1`. Design `docs/design/2026-11-09-second-brain-agent.md`. Tests `tests/test_agent_quality.py` 4 passed. Sync V2/V4/V5. Standalone loop tạm `D:\PinelineV2_tmp\_run_brain_standalone.py` (tránh restart giữa review 05670). **Restart :8801** khi queue/review rảnh để nạp thread trong server.

- **REVIEW → Gemma4 26b** (~22:18). User yes đổi luôn. Config `REVIEW_MODEL`/`REVIEW_PRESET=gemma4-26b-qat-uncen-mtp` (V2/V4/V5). Stop 12B mid-job → restart :8801 → force `review_only` `05670cbf7c1c`. Runtime :8083 = `gemma4-26b-qat-uncen-mtp-131k`. Lúc chuyển: `script.json` mất (đã restore từ `script.before_rereview_20261109_215318.json` + heal 没大没小). **Restart :8801** (đã).

- **QA watch 05670 + Gemma12 vs 26** (~22:12). Watcher deterministic `D:\PinelineV2_tmp\_qa_watch_05670.py` → `qa_watch_05670/REPORT.md`. Verdict review: 12B = cổng nhanh, không tin thành ngữ — `docs/reviews/2026-11-09-gemma12-vs-26-review.md`. **Không restart.**

- **没大没小 calque** (~22:05). Backup `…_2205.zip` + `…_meidameixiao-calque\`. NMT+review để `Cậu còn chưa lớn không nhỏ.` (`05670` i=8, `rv=1`). Polish + style term + Pass1 heuristic + prompt; heal live + watcher. Sync V2/V4/V5. Fix `docs/fixes/2026-11-09-meidameixiao-calque.md`. **Restart :8801** khi queue rảnh (job hiện heal ngoài process).

- **hg-rpc idle `_last_used`** (~21:53). `hongguo_rpc._idle_watch` thiếu `global _last_used` → crash thread idle. Sync V2/V4/V5. **Restart :8801** (đã).

- **Stop lúc soát → nhảy TTS** (~21:50). Tôn trọng `.stop` trong `run_review`; không mark_done/TTS khi stop; chặn TTS nếu còn câu chưa `rv`. Job `05670cbf7c1c` clear rv + `review_only` force. Fix `docs/fixes/2026-11-09-stop-during-review-tts.md`. **Restart :8801** (đã).

- **REVIEW Pass1 full VI + duty F** (~21:35). Backup `…_2130.zip` + `…_review-fullvi-pass`. Pass1 đọc pair SRT; duty F; heal đuôi «trước đó»; test 26 cue — i=0 sửa. Kết quả `docs/reviews/2026-11-09-review-pass1-halfcue/`. Sync V2/V4/V5. **Restart :8801** khi queue rảnh.

- **Sandbox retranslate job 9c3af (6×90s)** (~21:20). SenseVoice→NMT+Gemma; COMPARE 149/194 improved, 0 worse. `docs/reviews/2026-11-09-job5-retranslate-compare.md`. **Không restart.**

- **Audit VI job 9c3af (video 5)** (~20:52). YT VTT → 4132 cue; verdict poor (tên/xưng hô/calque/ASR-TTS). Report `docs/reviews/2026-11-09-job5-vi-audit.md`. Sandbox retranslate còn chạy. **Không restart.**

- **ASR-heal follow-up (onomat + pre-review)** (~20:40). Codebak `…_review-asr-merge\translate.py.before-onomat-followup`. `heal_obvious_internal_stutter` không cắt `叮当叮当`/`哈哈…`; `run_review` gọi `apply_asr_stutter_heal` trước LLM; prompt E có ví dụ; `review_batch` mặc định `_rmodel()`. Sandbox: heal i=17, giữ i=109; filter synthetic E PASS; Gemma vẫn hay bỏ sót E nên deterministic heal là lưới chính. Sync V2/V4/V5. **Restart :8801** khi queue rảnh.

- **REVIEW chữa ASR cut/repeat** (~20:25). Backup zip `Z:\PinelineV2_backup_2026-11-09_2016.zip` + codebak `Z:\PinelineV2_codebak\2026-11-09_review-asr-merge\`. `translate.py`: duty E rà stutter/tail→head; filter giữ sửa merge có bằng chứng; post-pass gỡ lặp nội bộ rõ ràng; làm mềm `吃醋` (`ghen` thường đúng nhưng `uống giấm` không tự động là hard error). Probe sandbox i=17 + sample i=582 + tail-head PASS; pytest 2 passed. Sync V2/V4/V5. **Restart :8801** khi queue rảnh.

- **REVIEW → Gemma4 12b local** (~20:07). Backup zip `…_2007.zip` + `…_review-gemma12b\`. `REVIEW_MODEL`/`REVIEW_PRESET=gemma4-12b-qat-mtp-fast` (cùng preset dịch cũ). Sync V2/V4/V5. **Không restart** (config hot). Job review tiếp theo auto-switch gemma.

- **REVIEW → local qwen36-turbo** (~14:20). Backup zip `…_1419.zip` + `…_review-qwen36\`. `REVIEW_MODEL=llama/qwen36-turbo` (pineline.config + config.json). Smoke review_batch OK ~15s. Sync V2/V4/V5. **Không restart** (config hot). Lần review đầu có thể mất ~70s nạp GGUF nếu đang gemma translate. *(superseded ~20:07 → Gemma4 12b)*

- **Poster hg 502 junk name** (~14:05). Backup zip `…_1402.zip` + `…_hg-poster-502\`. `hg_name` part/job/`downloads` → derive parent Lib; poster missing/junk **404** không 502; Films UI `resolveFilmPosterName`; heal 6 hàng DB. Fix `docs/fixes/2026-11-09-hg-poster-502-junk-name.md`. Sync V2/V4/V5. **Restart :8801** (chờ yes — `1e2379edb4fe_p01` running) để nạp `routes_hg` 404; hard refresh Films UI.

- **Meta AI image → :3377** (~13:58). Backup zip `…_1358.zip` + `…_meta-chatgpt-3377\`. `meta_studio` đọc config `CHATGPT_*` (không chỉ env); ưu tiên local; Bearer `sk-local`; timeout ảnh theo config; `/api/meta/ai-image` 300s. Smoke ~23s / 1.5MB. Fix `docs/fixes/2026-11-09-meta-ai-image-3377.md`. Sync V2/V4/V5. **Không bắt buộc restart** (sidecar reload `meta_studio`); restart :8802 chỉ để nạp timeout 300 trong handler.

- **ChatGPT timeout 900s** (~13:55). Backup `…_chatgpt-timeout\`. Bỏ trần 120s; `CHATGPT_TIMEOUT=900` (+ PLAN_FILE 900, trần 1800). Sync. **Restart :8801** (chờ yes) — đang có job thì đợi idle.

- **Restart :8801 nạp ChatGPT :3377** (~08:07). `restart_server.py --clean-env` · PID **34240**. Job `9c3af49061a2_p01` mux bị đứt giữa chừng (TTS đã đủ 2122). **Không cần restart lại.**

- **ChatGPT → local :3377** (~07:40). Backup `…_chatgpt-local-3377\`. `CHATGPT_BASE_URL=http://127.0.0.1:3377/v1` + `CHATGPT_API_KEY=sk-local`; fallback Aurora 5005. Smoke `PONG-LOCAL` OK. Sync V2/V4/V5.

- **Launcher bat pin Python quote** (~07:30). `if exist … ( set PY= )` + CRLF + fallback where; V2/V4/V5. Fix `docs/fixes/2026-11-09-bat-py-quote.md`. **Không restart.**

- **Test Block chọn account** (~05:42). Backup `…_tc-pick-account\`. Modal dropdown Project; `test-one` + `upload_test_sample(project_id=)`; clear cờ local. Sync. **Hard refresh** Films UI (sidecar reload module).

- **Test Block quota false-positive** (~05:25). Backup `…_0521.zip` + `…_tc-quota-stale\`. `test_channel`: ngày Pacific; classify lỗi chặt; purge cờ legacy; UI lý do hết hạn. Live `available 3/3`. Fix `docs/fixes/2026-11-09-tc-quota-false-positive.md`. Sync V2/V4/V5. **Không restart** (sidecar reload module). Hard refresh Films UI.

- **Restart :8801** (~05:16). `restart_server.py --clean-env` · queue rỗng · nạp keep-NMT + NMT primary + PLAN file + hv_auditor. Sidecar :8802 giữ. **Không cần restart lại.**

- **Filter bỏ polish GPT** (~04:52). Backup zip `…_0452.zip` + `…_review-keep-nmt2\`. `_filter_cosmetic_nmt_fixes`: mặc định DROP; chỉ giữ CJK/tên-lock/TTS rút thật (từ mới ≤15%); cấm đổi xưng hô miệng. Probe i=48 → giữ NMT. Fix `docs/fixes/2026-11-09-review-keep-nmt.md`. Sync V2/V4/V5. **Restart :8801** (chờ yes).

- **GPT rà tối thiểu** (~04:46). Backup `…_review-keep-nmt\`. User: NMT đã tốt mà GPT đổi thừa (vd Lão tử→Tôi). `review_batch` mặc định giữ NMT; chỉ vá A–D; temp 0.1. Sync V2/V4/V5. **Restart :8801** (chờ yes).

- **Văn phong linh hoạt + giữ NMT primary** (~04:15). Backup `…_flex-style-nmt-primary\`. Bỏ khóa register; mixed→MT base. Sync. **Restart :8801** (chờ yes).

- **P1 harden plan-file + A/B** (~04:10). Vá null-list; scene `[i=N]`; timeout PLAN. A/B report. Sync. **Restart :8801** (chờ yes).

- **Plan file + review style** (~04:05). Backup `…_plan-file-review-style\`. `PLAN_MODE=file`: upload full SRT → GPT glossary; review style_lock+mẫu. Follow-up fix `docs/fixes/2026-11-09-mt-draft-slim-gloss.md`. Sync V2/V4/V5. **Restart :8801** (chờ yes).

- **NMT dịch chính / LLM rà** (~03:35). Backup `…_mt-primary-llm-review\`. User đảo: `MT_ZH_VI_ROLE=primary` — HachimiMT ghi VI; gemma chỉ vá sót; GPT mini `run_review`. Follow-up `docs/fixes/2026-11-09-mt-draft-slim-gloss.md`. Sync V2/V4/V5. **Restart :8801** (chờ yes).

- **MT auto theo genre** (~02:45). Backup `…_mt-genre-auto\`. `MT_ZH_VI_MODEL=auto`: modern/mixed → base; xianxia → QT. Follow-up fix `docs/fixes/2026-11-09-mt-draft-slim-gloss.md`. Sync V2/V4/V5. **Restart :8801** (chờ yes).

- **NMT draft + slim glossary + REVIEW GPT mini** (~02:40). Backup `…_mt-draft-slim-gloss\`. Sau sandbox VERDICT: gắn lại `mt_zh_vi.py` làm **nháp** `mt_vi` → LLM; lock/name-pass/series chỉ `type=lock`; `REVIEW_MODEL=chatgpt/gpt-5-6-mini`. Config `MT_ZH_VI=1`. Fix `docs/fixes/2026-11-09-mt-draft-slim-gloss.md`. Sync V2/V4/V5. **Restart :8801** (chờ yes).

- **NMT bench sandbox** (~01:30). Revert hook tạm; bench `D:\PinelineV2_tmp\mt_bench\` job `0a5f60aead18` (base+QT). Verdict → merge draft (mục trên).

- **HV Auditor (phương án A)** (~01:15). Backup `…_hv-auditor\`. Module `hv_auditor.py` + Unihan `data/unihan/kVietnamese.json`; trap-fix 逆; warn không đè tên riêng; series hygiene apply/save; gắn `ensure_hard_terms`. Fix `docs/fixes/2026-11-09-hv-auditor.md`. Sync V4/V5. **Restart :8801** (chờ yes).

## 2026-11-08

- **逆天而行 → Nghịch (không Nghị)** (~22:30). Backup `…_nghich-thien-heal\`. Heal series + 3 job glossary/script; seed lock trong `ensure_hard_terms`. Fix `docs/fixes/2026-11-08-nghich-thien-ni-hanh.md`. Sync V4/V5. **Restart :8801** để nạp seed (glossary đã heal trên đĩa).

- **Auto-split parent merge heal** (~19:18, restart ~19:21). Backup `…_split-parent-merge-heal\`. Parts xong mà parent treo (sau restart) → `_queue_split_parent_merge_if_ready` / notify sau part / GET job / entry auto-split. Job `2cd10c3fa86d` Full ~6925MB. Fix `docs/fixes/2026-11-08-split-parent-merge-heal.md`. Sync V4/V5. **Restart :8801** (đã).

- **Hongguo classic full split** (~10:10). Backup `…_hg1-full-split\`. Restore `hongguo.html` pre-WinUI; `/api/hg`=HTTP only; `/api/hg2`=RPC; hongguo2 → `/api/hg2/*`. Fix `docs/fixes/2026-11-08-hongguo1-full-split.md`. **Restart :8801** (đã). Hard refresh `/hongguo` + `/hongguo2`.

- **Merge frag naming + corrupt skip** (~09:20). Backup `…_merge-frag-re\`. `_FRAG_RE` nhận `S01E001`; `_MERGED_RE` nhận `merged.mp4`; dedupe/skip tập hỏng (NVENC -22). Fix `docs/fixes/2026-11-08-merge-frag-naming.md`. Sync. **Không bắt buộc restart** (bridge reload) — nên restart :8801 nếu worker merge đang chạy code cũ.

- **Hongguo1 restore + isolate hg2** (~08:55). Backup `…_hg1-isolate\`. Restore `hongguo.html` gốc; `hg_ui_ctx` + `X-HG-UI:2` (RPC) / hg1 `http_first`; `HG_BACKEND=auto`. Fix `docs/fixes/2026-11-08-hongguo1-restore-isolate.md`. **Restart :8801** (đã). Hard refresh `/hongguo` + `/hongguo2`.

- **Hongguo1 kẹt bảng hot** (~08:45). Backup `…_hongguo1-boot\`. *(superseded 08:55 — đã restore HTML gốc, không giữ patch parallel trong hongguo.html.)* Fix `docs/fixes/2026-11-08-hongguo1-boot-stuck.md`.

- **Hongguo2 Retry 502 license** (~08:25). `downloads.retry` prove license (force nếu helper chờ licence); UI Retry trên Failed. Follow-up `docs/fixes/2026-11-08-hongguo2-dl-stop.md`. **Hard refresh** (bridge hot-reload).

- **Hongguo2 Stop download** (~08:16). Backup `…_dl-stop\`. Helper chỉ có `cancelAll` → `cancel_download(sid)` = cancelAll + requeue others; UI **Stop** / **Stop all**; × trên active = stop. Fix `docs/fixes/2026-11-08-hongguo2-dl-stop.md`. Sync V4/V5. **Restart :8801** (đã). Hard refresh.

- **Hongguo2 qualities 502 + /api/disk 404** (~08:10). Backup `…_qualities-disk\`. `series.qualities` không gọi RPC flaky (helper crash) → ladder mặc định; thêm `GET /api/disk` (free_gb). Fix `docs/fixes/2026-11-08-hongguo2-qualities-disk.md`. Sync V4/V5. **Restart :8801**. Hard refresh.

- **Hongguo2 Play nhanh (480p + cache + %)** (~07:50). Backup `…_hongguo2-play-fast\`. Preview không dùng 1080p; async start/job hiện progress; cache hit tức thì. **Restart :8801** (đã). Hard refresh.

- **Hongguo2 Play RPC playback** (~07:30). Backup `…_hongguo2-play-rpc\`. Preview không cần :8000: `playback.prepare` + `/api/hg/playback/stream`; license ensure; UI `<video>` local. **Restart :8801** (đã). Hard refresh.

- **Hongguo2 Play + scroll fill** (~07:10). Backup `…_hongguo2-play-scroll\`. Nút Play cạnh Quality + preview modal (`/api/hg/preview`). Browse: scroll/IO/`maybeBrowseMore` fill viewport (hết kẹt 24). Fix `docs/fixes/2026-11-08-hongguo2-play-button.md`. Sync V4/V5. **Hard refresh**.

- **Hongguo2 Browse load-on-scroll** (~07:05). Backup `…_hongguo2-browse-scroll\`. Infinite scroll qua `sessionId`+`nextOffset`+sentinel IO; page 24; dedupe `series_id`. Fix `docs/fixes/2026-11-08-hongguo2-browse-scroll.md`. Sync V4/V5. **Hard refresh** (không restart).

- **Hongguo2 dropdown WinUI + filter RPC** (~06:22). Backup `…_hongguo2-dropdown-winui\` + zip `…_0622.zip`. Custom dd menu (pill/accent/menu tối); `feed.select` wrap `List[str]` (helper bỏ string đơn). Hot-reload rpc qua marker `list[str]`. Fix `docs/fixes/2026-11-08-hongguo2-dropdown-winui.md`. Sync V4/V5. **Hard refresh** (bridge reload mỗi request — không bắt buộc restart :8801).

- **Python default 3.12 (A+B)** (~06:12). Backup `…_run-v2-python312\` + zip `…_0610.zip`. Machine PATH bỏ `Python315`; đầu PATH = `C:\Python312`; `PY_PYTHON=3.12`. Launcher pin 312: `run_v2.bat`/`run_2.bat`/`run_tele_cmd.bat`/`run.bat` + V4/V5. Fix `docs/fixes/2026-11-08-python315-path-default.md`. **Mở terminal mới** (không bắt buộc restart :8801 — TTS đang chạy).

- **Hongguo2 intro VI + dropdown đọc được** (~06:05). Backup `…_hongguo2-intro-dropdown\`. Detail dịch intro qua translate-titles; CSS select option dark (hết chữ trắng trên trắng). Fix `docs/fixes/2026-11-08-hongguo2-intro-dropdown.md`. Sync V4/V5. **Hard refresh** (không restart).

- **Hongguo2 Browse chỉ 20 / No results · feed** (~06:00–06:10). Backup `…_hongguo2-browse-pagesize\`. `feed(limit)` gom trang; follow-up `_rpc_mod` hot-reload giữ `_proc` (hết TypeError limit → empty). Fix `docs/fixes/2026-11-08-hongguo2-browse-pagesize.md`. Sync V4/V5. **Hard refresh** (không bắt buộc restart).

- **Dịch dừng → nhảy TTS dở** (~05:40). Backup `…_translate-partial-tts-jump\`. Salvage dịch ghi đủ khung ASR; `translate_ready_for_tts` / coverage ≥90%; `_auto_gpu`+`_do_tts` không TTS khi script ngắn hơn ASR. Heal job `2cd10c3fa86d_p01` `n_total` 398→2616. Fix `docs/fixes/2026-11-08-translate-partial-tts-jump.md`. Sync V4/V5. **Restart :8801**.

- **Hongguo2 title VI** (~05:30). Backup `…_hongguo2-title-vi\` + zip `…_0528.zip`. `applyTitleVi` / `.tvi` + detail `#dTitleVi` gọi `POST /api/hg/translate-titles` sau Browse/Search/Rank/New/Library. Fix `docs/fixes/2026-11-08-hongguo2-title-vi.md`. Sync V2/V4/V5 + `static/ui`. **Hard refresh** (không restart — HTML static).

- **REVIEW local → qwen36-turbo** (~05:30). `REVIEW_PRESET=qwen36-turbo` (Huihui Qwen3.6 35B TurboQuant v0.4); dịch vẫn `gemma4-12b-qat-mtp-fast`. Job `2cd10c3fa86d_p01` (4–Phần 1/2) dừng vì **vieneu exit 15** @64/398 + claim `__all__` stale — resume TTS. **Không restart** (config/translate hot).

- **Ranking max 100 + route Film/Studio** (~05:15). Backup `…_rank-max100-routes\`. `rank.page`+`rank.more` gom ≤100; UI size=100; `/films|/film|/films/ui` → films_ui; `/studio` → index3; sidebar link. Follow-up `docs/fixes/2026-11-08-hongguo2-rank-new.md`. **Restart :8801** (đã). Hard refresh.

- **Hongguo2 Library = WinUI** (~05:00). Backup `…_library-winui\`. Update info / Select / Open folder; chips All downloads / New seasons / Lib path; card badge+hover Folder/Play + `N eps · size`; `POST /api/hg/library/update-info`. Fix `docs/fixes/2026-11-08-hongguo2-library-winui.md`. Sync + **restart :8801**. Hard refresh.

- **Hongguo settings merge+delete mảnh** (~04:55). `settings.update` `merge=true`, `deleteAfterMerge=true` (giống cũ: merge xong xóa episode lẻ). UI default Delete-after-merge = on. **Không restart.** Hard refresh Settings thấy toggle ON.

- **Hongguo2 Downloads sai tên** (~04:50). Backup `…_dl-title-folder\`. Snapshot `title=""` → hiện seriesId. Normalize lấy tên folder (+ series.detail); UI ưu tiên folder. Follow-up `docs/fixes/2026-11-08-hongguo2-downloads-winui.md`. **Restart :8801** (đã) + hard refresh.

- **Hongguo2 Settings Change folder** (~04:45). Backup `…_settings-pick-folder\`. Nút Change dùng `POST /api/fs/pick-dir` (dialog Windows) thay `prompt`. Follow-up trong `docs/fixes/2026-11-08-hongguo2-settings-winui.md`. **Hard refresh** (không cần restart).

- **Hongguo2 Settings = WinUI + license prove** (~04:40). Backup zip `…_0435.zip` + `…_settings-winui\`. UI Downloads/Output (save/quality/at-once/connections/file names/merge toggles); `POST /api/hg/settings` → `settings.update`; License block + auto-prove khi mở Settings / trước download. Fix `docs/fixes/2026-11-08-hongguo2-settings-winui.md`. Sync + **restart :8801**. Hard refresh `/hongguo2`.

- **Helper singleton + WinUI parity (giữ spawn riêng)** (~04:30). Backup zip `…_0428.zip` + `…_helper-singleton\`. Sau attach FAIL: không chung pipe WinUI. Siết 1 MainKt Pineline (`HG_HELPER_SINGLETON`, reap orphan mỗi ensure, không reload RPC, tele bỏ reload bridge). `/api/hg/settings` + hongguo2 boot quality/`D:\Lib`. Fix `docs/fixes/2026-11-08-helper-singleton-winui-parity.md`. Sync V2/V4/V5 + `static/ui`. **Restart :8801** (đã). Hard refresh `/hongguo2`.

- **Hongguo2 Downloads = WinUI** (~03:00). Backup `…_downloads-winui\`. List thumb/quality/Done line/Open folder/×; tabs All/Active/Done/Failed; Clear finished + speed. RPC clear/remove + open_folder. Fix `docs/fixes/2026-11-08-hongguo2-downloads-winui.md`. Sync + restart :8801. **Hard refresh** (cả `/static/ui/`).

- **Hongguo2 Ranking/New = WinUI** (~02:45). Backup `…_rank-new-winui\`. Ranking: `rank.page` charts/boards (8 tab EN + chip động). New: `feed` `online_time=days_N` + sort. Fix `docs/fixes/2026-11-08-hongguo2-rank-new.md`. Sync V2/V4/V5 + `static/ui`. **Restart :8801** + hard refresh.

- **Hongguo2 static/ui stale** (~02:35). User còn mở `/static/ui/hongguo2.html` (3 dropdown cũ). Chép đè root `hongguo2.html` → `static/ui/`. **Hard refresh** URL static hoặc dùng `/hongguo2`.

- **Hongguo2 Browse = WinUI 7 facets** (~02:35). Backup zip `…_0229.zip` + `…_browse-feed-facets\`. Đọc screenshot + `feed.page?panel` + `FilterText` DLL. UI 7 dropdown (All genres…Any time); `select` map RPC; `hongguo_feed_labels.json` ZH→EN. Routes `/api/hg/feed` nhận facet query. Fix `docs/fixes/2026-11-08-hongguo2-browse-facets.md`. Sync V2/V4/V5. **Restart :8801** + hard refresh `/hongguo2`.

- **Hongguo2 Browse filters → feed/catalog** (~02:10). Backup `…_hg2-browse-filters\`. Bỏ toast «map API khi có catalog». Filter Genre/Sort/Status: `board=browse` → RPC `feed.page`; `catalog_*` → Explorer (fallback rank + alias ZH/EN). Routes `/api/hg/genres|catalog|feed` (sau reload :8801). **Hard refresh `/hongguo2`**.

- **Hongguo2 Download all seasons (2.x dialog)** (~01:55). Backup `…_hg2-download-all-seasons\`. Dialog chi tiết: S1…Sn, quality, episode grid, **Download all N seasons** → `POST /api/hg/submit` multi-id. RPC `series.seasons`/`qualities`; `lookup_series` đính kèm; submit +`quality`. Routes `/series/{id}/seasons|qualities` (cần reload :8801 để đăng ký; payload seasons đã có qua detail). Sync V2/V4/V5. **Hard refresh `/hongguo2`**.

- **Hongguo2 img 422/403 + restart :8802** (~01:45). Backup `…_hg-img-u-param\`. `/api/hg/img` nhận `?u=` lẫn `?url=`; `fetch_img_proxy` dùng RPC `covers.get` (CDN fqnovel 403 khi fetch thẳng). UI hongguo2 → `?url=`. Restart sidecar PID mới; clear state upload part `p02`. **Hard refresh `/hongguo2`**. :8801 không restart (bridge reload mỗi request).

- **Hongguo2 design match WinUI + skip split-part upload** (~01:40). Backup `…_hongguo2-design-part-upload\`. `hongguo2.html` gần app 2.x (logo, filters, rank pills trắng, disk/Yearly Unlimited, theme). `auto_publisher.is_auto_split_part` chặn enqueue/publish `…_pNN` / `Phần N/N`; purge queue (`ad50b61b4050_p02`). Fix `docs/fixes/2026-11-08-skip-split-part-upload.md`. Sync V2/V4/V5. **Hard refresh `/hongguo2`**. **Restart :8802 khi idle** để nạp `auto_publisher` (sidecar); :8801 không bắt buộc (HTML static).

## 2026-11-07

- **Hongguo2 UI 2.x skin (option B)** (~22:45). Backup `…_hongguo2-ui-2x\`. Revive `/hongguo2` → `hongguo2.html` (sidebar Browse/Ranking/New/Link/Downloads/Library + Settings license). Wire `/api/hg/*` + `/api/hg/license/*`; hot-path `@@license@@status|store|prove|clear` trong `hongguo_bridge` search/resolve (process chưa reload route). Sync V2/V4/V5 + `static/ui/hongguo2.html`. DECISIONS revive B. **Restart :8801** (đã hẹn `--after-current`) để `/hongguo2` hết 302; tạm: `/static/ui/hongguo2.html`.

- **Hongguo 2.x UI plan (docs)** (~21:56). Spec `docs/superpowers/specs/2026-11-07-hongguo-2x-ui-plan.md` — screens↔`/api/hg/*`, license UX (no key echo), download gates, portability, P0/P1/P2; khuyến nghị extend `/hongguo` (không revive skin trừ khi user chọn). **Không restart.**

- **Hongguo 2.x license prove (download unlock)** (~21:45). Backup `…_hg-license-prove\`. Key DPAPI `%LOCALAPPDATA%\Pineline\hg_typed_key.dpapi` (không log). `hongguo_license_ensure.ensure_licensed` + HTTP proof bridge → `Hongguo.Licensing` Activate → `license.prove` cùng helper `hongguo_rpc`. Hook `submit` / `library_download_new_seasons`. Host `%TEMP%\HgLicActivate_patch\HgLicActivate.exe`. Review cập nhật. Sync V2/V4/V5. **Restart :8801** (hoặc reload `/api/hg/*`).

- **Hotfix mux `No module named 'core'`** (~21:18). Sync nhầm V5 `engines/render` → V2 flat `render.py`. Khôi phục V2/V4 từ bak `…_mux-heal-hstrack\V2_render.py`. Follow-up `docs/fixes/2026-11-07-mux-heal-hardsub-ocr.md`. **Không restart** (reload render mỗi mux). Remux `ad50b61b4050_p01`.

- **Hongguo 2.x JSON-RPC bridge** (~21:10). Backup zip `…_2107.zip` + `…_hongguo-rpc\`. Thêm `hongguo_rpc.py` (stdio helper.jar); `hongguo_bridge` `HG_BACKEND=rpc|http|auto` map search/rank/library/status/submit/… → RPC, giữ shape `/api/hg/*`. Spec `docs/superpowers/specs/2026-11-07-hongguo-rpc-bridge-design.md`. Sync V2/V4/V5. **Restart :8801** để nạp module (reload importlib khi gọi `/api/hg/*` cũng được nếu bridge reload).

- **Heal mux giả «Sẵn sàng» lúc OCR hardsub** (~18:20). Backup zip `…_1817.zip` + `…_mux-heal-hstrack\`. `_job_lineage_busy` (parent auto-split) + bỏ heal khi còn `_hstrack`; phase/`cur_text` hardsub trước encode. Fix `docs/fixes/2026-11-07-mux-heal-hardsub-ocr.md`. Sync V2/V4/V5. **Không restart :8801** (P3 đang `encode×3`) — nạp heal khi idle (cùng đợt hardsub_blur).

- **Concat chỉ encode phần lệch resolution** (~04:13). Backup zip `…_0413.zip` + `…_concat-partial-norm\`. `_concat_videos_smart` fallback: khớp W×H → `-c:v copy`; lệch → scale+pad. Mode `normalized_canvas_partial`. Fix `docs/fixes/2026-11-07-concat-partial-norm.md`. Sync V4/V5. **Không restart** (feeder reload theo request; job gộp đang chạy vẫn logic cũ).

- **Kênh Test exhausted che token Kênh 3** (~02:52). Backup zip `…_0251.zip` + `…_tc-exhausted-hint\`. `get_available_service` fallback project còn cờ exhausted khi auth phía còn quota fail; refresh sớm; xóa live `exhausted.json`. Fix `docs/fixes/2026-11-07-test-channel-exhausted-mask.md`. Sync V2→V4/V5. **Không restart** (:8802 reload module).

- **Kênh Test Đổi kênh poll giả** (~02:40). Backup `…_tc-doi-kenh-poll\`. Poll chờ `connected_at` mới; OAuth `replace_identity`; bỏ ghi đè CHANNEL từ pool count. Fix `docs/fixes/2026-11-07-test-channel-doi-kenh.md`. **Hard refresh Films** (tele reload `test_channel`).

- **Restart sidecar :8802** (~01:40). User yes. PID 35972→**28936**. Nạp preserve_order + oversized/skip Python. Smoke: `/config`, `/api/uploader/status`, `/api/settings` OK. **Không đụng :8801.**

- **Uploader Skip UX + oversized guard** (~01:15). Backup zip `…_0109.zip` + codebak `…_skip-upload-ux\`. Sticky `#up-skip-banner` + header Skip + Done/batch Skip; poll status 4s; `queue||items`; enqueue/auto-publish refuse >11.5h / ≥64GiB trừ confirm. Sync V4/V5 UI + `agents/auto_publisher`. Fix `docs/fixes/2026-11-07-uploader-skip-ux.md`. **Hard refresh Films**. **Không restart :8802** (auto-pub stage còn uploading / chưa idle) — restart khi idle để nạp Python API.

- **Combine part-order harden** (~01:25). Backup zip `…_0108.zip` + `…_combine-part-order\`. CN `第N季/集`, missing→0, secondary `created_at`/`job_id`, numbered ↑↓ + `preserve_order`/`explicit_order`. Sync V4/V5. Follow-up `docs/fixes/2026-11-07-combine-part-order.md`. **Hard refresh Films**. Sort-by-part: feeder reload (không cần :8801). **Hỏi restart :8802** nếu cần ↑↓ preserve_order trên process tele_cmd cũ.

- **Combine sort Phần 1→N** (~01:20). Backup `…_combine-part-order\`. Modal/API không nối theo thứ tự tick; cảnh báo >11.5h; Skip đang upload trên batch Done. Fix `docs/fixes/2026-11-07-combine-part-order.md`. **Hard refresh Films** (feeder reload mỗi POST).

- **SAFE autofix hardsub_blur UI/as_bool** (~00:55). Backup `…_hardsub-blur-safefix2\`. `films_ui` loadSettings coerce `"false"`; `index3` autoPrefApply + runOptsSummary; `run_all`/`mux_job` → `as_bool`; tests 22 OK. Sync V4/V5 + `static/ui`. Follow-up `docs/fixes/2026-11-07-hardsub-blur-toggle.md`. **Hard refresh UI**. **Không restart** (:8801 vẫn cần restart idle để nạp field).

- **hardsub_blur recheck P1** (~01:15). Backup `…_hardsub-blur-p1\`. Queue stamp `as_bool`; V5 `core/batch_config` + `engines/render` parity; log `hardsub=off`. Follow-up fix log. **Restart :8801 khi idle** (P0 live schema).

- **hardsub_blur coerce P0** (~01:10). Backup `…_hardsub-blur-coerce\`. `batch_config.as_bool`; `_queue_run_one`/`_auto_pipeline` + `render.py` queue_opts không còn `bool("false")`; Films load `/config` trước early-return. Tests ≥21. Sync V4/V5. Follow-up `docs/fixes/2026-11-07-hardsub-blur-toggle.md`. **Restart :8801 khi idle**.

- **SAFE autofix hardsub_blur stale V5 UI** (~00:50). Backup `…_hardsub-blur-autofix\`. Sync `static/ui/index3.html`+`films_ui.html` (live V5) ← root; null-guards settings/`queueBatchPush`; V2→V4→V5. Follow-up `docs/fixes/2026-11-07-hardsub-blur-toggle.md`. **Hard refresh V5 UI**. **Restart :8801 khi idle** (OpenAPI live chưa có MuxReq.hardsub_blur). :8802 không cần.

- **UI audit hardsub/combine SAFE** (~01:00). Backup `…_hardsub-blur-toggle\`. `index3.html`: `mux-hs-blur` sync từ `auto-hs-blur`. `films_ui.html`: bỏ `doCopyGptPrompt` trùng. Route `/films/mergeable` OK. Sync V4/V5. Follow-up `docs/fixes/2026-11-07-hardsub-blur-toggle.md`. **Hard refresh UI3/Films** (không restart).

- **hardsub_blur on/off** (~00:55). `MuxReq.hardsub_blur` + `mux_job` truyền `_do_render`; UI3 `auto-hs-blur`/`mux-hs-blur`; Films Settings tab Render → `/config`. Test `tests/test_hardsub_blur_toggle.py`. Swarm check/test/autofix. Fix `docs/fixes/2026-11-07-hardsub-blur-toggle.md`. **Restart :8801** khi idle để nạp MuxReq. Hard refresh UI3/Films.

- **Films UI gộp job đã làm** (~00:50). API `/films/combine` đã có nhưng thiếu nút. Batch **🔗 Gộp job đã làm** + modal; `films_merge_api` mergeable/merge-parts; lib tick `need_merge` + ghép hàng loạt. Fix `docs/fixes/2026-11-07-films-combine-ui.md`. **Sidecar :8802 restarted** (PID 35972). Hard refresh Films UI.

- **Port Settings+Uploader → :8802 + skip upload** (~00:40). Backup zip `…_0034.zip` + codebak `…_uploader-settings-8802\`. Module `uploader_settings_api.py`; wire `agent_tele_cmd` GET/POST; Films UI skip-current / skip-item / move / priority / auto-launch / clear-skipped; `yt_uploader` đọc `skip_current.flag`. Sync V4/V5 (+ V5 FastAPI bridge skip). Fix `docs/fixes/2026-11-07-uploader-settings-8802.md`. **Đã restart sidecar :8802** (PID 16628). Hard refresh Films UI.

- **Films UI jq onclick leftovers** (~00:10). Backup `Z:\PinelineV2_codebak\2026-11-07_films-ui-syntax\` + zip `…_0006.zip`. `films_ui.html`: thay `'${…}'`/`'${esc(…)}'` còn sót bằng `${jq(…)}` (OAuth id, job_id, titles, hooks; merge names → `JSON.parse(${jq(JSON.stringify(…))})`). jq 27→37; leftover unsafe string-ish=0. Sync V4/V5 + `static/ui`. Fix `docs/fixes/2026-11-07-films-ui-syntax.md`. **Hard refresh Films UI** (không restart).

## 2026-11-07

- **Tool loop pipeline** (~00:30). `agent_tool_loop.py` + `pineline_run_stage_wait` / `pineline_pipeline_loop`. CLI HTTP smoke. Tests 4 passed. Review `docs/reviews/2026-11-07-tool-loop.md`. **Restart :8801** khi idle.

- **Films UI jq HTML-escape + swarm** (~00:05). Backup `…_films-ui-jq-html\`. `jq` stringify + `&quot;` (onclick không còn cắt attribute); autopub load flat config; Settings/Uploader toast 404 rõ. Sync V4/V5. Fix `docs/fixes/2026-11-07-films-ui-syntax.md` · review `docs/reviews/2026-11-07-films-ui-swarm.md`. **Hard refresh `/films/ui`** (không restart). Còn mở: port `/api/settings` + `/api/uploader` vào :8802.

## 2026-11-06

- **Eng-swarm translate force** (~23:55). Báo cáo `docs/reviews/2026-11-06-v5-eng-swarm-translate-force.md`. Early-stop worker → translate `pending` (tránh ghost running). V5 đã `force=bool(force)` + 4 unit tests. **Cần restart :8801**.

- **Translate force-wipe mặc định** (~22:25). Backup `…_translate-force-default\` + restore `…_restore-script-88\`. `_translate_flow` hardcode `force=True` → mọi `/translate` xoá script; user thấy nhảy về «dịch lại từ đầu» lúc chuẩn bị TTS. Thêm `TranslateReq.force` (default false); UI «Dịch lại» gửi `force:true`. Khôi phục `88d80ba0be0f` từ `script.display.json` (4334/4342). Sync V4/V5. Fix `docs/fixes/2026-11-06-translate-force-wipe.md`. **Cần restart :8801**.

- **Translate stop dual-path + retranslate live** (~21:25). Backup `Z:\PinelineV2_codebak\2026-11-06_clear-stop-dual\`. Restart :8801 + force translate `88d80ba0be0f` (user «có»); live `script.json` + progress tăng, không ghost `.stop`. Harden `_clear_stop` (WORK_ROOT + `D:\PinelineV2_work`) + `_run_translate` clear trước flow. Sync V4/V5. Follow-up `docs/fixes/2026-11-06-translate-stop-ghost.md`. **Cần restart :8801 sau khi job 88d8 dịch xong** để nạp harden (đang chạy process cũ vẫn clear_stop một path — đủ vì junction).

- **Hongguo2 seasons banner + Ops tabs** (~16:30). Backup `Z:\PinelineV2_codebak\2026-11-06_hongguo2-layout2\`. Bỏ clip `max-height:72px`; Mùa mới full-width banner; Ops `Thư viện|Hàng đợi`; progress VN + card khi Update all. Sync V4/V5. Fix `docs/fixes/2026-11-06-hongguo2-seasons-layout.md`. **Hard refresh `/hongguo2`** (không restart).

- **Pronoun-QA slim plan (Aurora 413)** (~15:30). Backup `Z:\PinelineV2_codebak\2026-11-06_pronoun-qa-slim\`. `translate._plan_block_for_qa` (genre+style+pronouns only); `pronoun_consistency` + `agent_pronoun_pass` dùng slim; `llm._chatgpt_chat` no-retry 400/413/422. Đo `4041_p02`: full 72424 → slim 20119. Test `tests/test_pronoun_qa_slim_plan.py`. Sync V4/V5. Fix `docs/fixes/2026-11-06-pronoun-qa-413-slim.md`. **Cần restart :8801** (translate/llm/pronoun) khi queue idle — chưa restart (job `4041` đang ASR/translate).

- **Hongguo2 Ops hẹp** (~15:16). Backup `Z:\PinelineV2_codebak\2026-11-06_hongguo2-ops-narrow\`. CSS: Discover `1fr` | Ops `minmax(280px, min(34vw, 380px))`; seasons max ~120px; ops padding 6×10. Sync V4/V5. **Hard refresh `/hongguo2`** (không restart).

- **Hongguo2 review pass** (~08:30). Backup `Z:\PinelineV2_codebak\2026-11-06_hongguo2-review\`. CTA `doDownload` enqueue-only; submit chỉ `startDlQueue`/`dlGroup`/`dlDetail*`; `#results` scope; `catalog-hint`/`cta-status`; inflight guards; UX ops/labels; sync V4/V5. Fix `docs/fixes/2026-11-06-hongguo2-review.md`. **Hard refresh `/hongguo2`** (không restart).

- **Hongguo2 redesign** (~08:20). Backup `Z:\PinelineV2_codebak\2026-11-06_0818_hongguo2\`. Thêm `hongguo2.html` (IA 2 cột Discover 55% | Ops 45%: Tìm/Hot/Catalog + seasons/library/queues; không floating-q-bar). Route `GET /hongguo2` → `ui_hongguo2` trong `routes_ui.py` + re-export `server.py`. Link «Thử Hongguo2» trên `hongguo.html`. Sync V4/V5. **Restart :8801** để nạp route; hard refresh `/hongguo2`.

- **Hongguo New seasons board** (~08:00). Backup `Z:\PinelineV2_codebak\2026-11-06_hg-new-seasons\`. Bridge `submit(scores=)` + `library_update`/`seasons_decline`; routes `/api/hg/library/update` + `/seasons/decline`; `HgSubmitIn.scores`; UI tab 🆕 Mùa mới trên `hongguo.html`. Port V4/V5. Fix `docs/fixes/2026-11-06-hg-new-seasons.md`. **Hard refresh `/hongguo`**; **restart :8801** nếu cần nạp bridge/routes (HTML static không cần).

- **Merge no-dup output** (~03:00). Backup `Z:\PinelineV2_codebak\2026-11-06_merge-no-dup-output\`. `merge_job_parts`: ghi 1 lần `output.mp4`; `output_full` chỉ hardlink (`_hardlink_alias`, không `copy2`); cleanup `_split_parts`. Port V4/V5. Fix `docs/fixes/2026-11-06-merge-no-dup-output.md`. **Restart :8801** để nạp merge mới (job đã merge không cần remux).

## 2026-11-05

- **Split part sai giọng** (~21:40). Backup `…_split-voice-queue-opts\`. `_resolve_voice/speed/engine` đọc `queue_opts` trước fallback list[0]; `split_job_to_subjobs` seed `stages.tts`+`tts_config`. Port V4/V5. Fix `docs/fixes/2026-11-05-split-voice-queue-opts.md`. **Restart :8801/:8804/:8805**.

- **Stop heal mux merged** (~21:25). `_stop_job`: parent đã merge+Full → mux done 100% (không pending/80%); stop part heal parent. Heal tay `d01dbbc2d703` → overall 100. Follow-up fix `autosplit-conflict-guards`. **Restart** để nạp stop mới.

- **Auto-split conflict guards** (~21:20). Backup `Z:\PinelineV2_codebak\2026-11-05_autosplit-conflict-guards\`. `server.py`: merged+Full → skip; `_AUTO_SPLIT_ACTIVE` lock; skip part mux-done; promote cùng ASR nguồn → không invalidate TTS. Port V4/V5 (`_auto_gpu` + `maybe_auto_split_job`). Fix `docs/fixes/2026-11-05-autosplit-conflict-guards.md`. **Restart :8801/:8804/:8805** để nạp (không restart lúc encode nếu user chưa cho).

- **Split ENOSPC guard** (~01:20). Backup `Z:\PinelineV2_codebak\2026-11-05_split-enospc\`. `split_parts.py`: check free trước split; ENOSPC → `DiskFullError` **không** re-encode; fail mid-way xoá `_split_parts`; sub-job ưu tiên `move`. Test `tests/test_split_enospc_guard.py` (3 passed). Fix `docs/fixes/2026-11-05-split-enospc-guard.md`. **Restart :8801 sau** khi job `d01dbbc2d703` xong (không restart lúc đang chạy).

- **UI3 404/stages null-safe** (~01:09). Backup `Z:\PinelineV2_codebak\2026-11-05_ui3-404-stages\`. Sync từ V5: `renderDetail` guard `!j.job_id||!j.stages`; `refresh` check `detRes.ok`, clear selection + strip `?job=`. Fix `docs/fixes/2026-11-05-ui3-404-stages.md`. **Không restart** (hard refresh HTML).

- **Upload limit stop-queue** (~00:43). Backup `Z:\PinelineV2_codebak\2026-11-05_upload-limit-stop\`. `auto_publisher`: `_is_yt_upload_limit_error`; `stop_queue`/`upload_limit_exceeded` từ `_publish_job_internal`; `publish_job` finally không dequeue/drain khi limit; drain loop break. Test `tests/test_upload_limit_stop.py`. Fix `docs/fixes/2026-11-05-upload-limit-stop-queue.md`. Port V5 `agents/auto_publisher.py`. **Không restart**.

## 2026-11-04

- **Queue sort/move** (16:57). Backup `Z:\PinelineV2_codebak\2026-11-04_queue-sort-move\`. UI gọi `/api/queue/jobs/sort|move`; season ưu tiên «Phần N» trên title; `job_sort_key` dùng `group_id`/series normalize. Sync V2/V4/V5 (`job_queue.py` + `index3.html`). Fix `docs/fixes/2026-11-04-queue-sort-move.md`. **Restart :8801 done 17:11** (PID 35380; hard refresh UI vẫn nên).

- **Title YT cấm tên nhân vật** (05:36). Backup `Z:\PinelineV2_codebak\2026-11-04_title-no-charname\`. Prompt: chỉ premise/hệ thống/«Ta» — không Hứa Hoa/Lão Lục…. Sync V2/V4/V5. **Restart** nếu meta in-process.

- **Title YT công thức Premise + Ta** (04:20). Backup `Z:\PinelineV2_codebak\2026-11-04_title-prompt-ta\`. `generate_youtube_titles`: `Phần N | PREMISE: HOOK, Ta PAYOFF` (user mẫu xuyên không / thức tỉnh / Ta…). Sync V2/V4/V5. Dump `docs/prompts/title_youtube_prompt_filled.txt`. **Restart** nếu meta in-process.

- **Thumb Latin + title YT prompt** (04:05). Backup `Z:\PinelineV2_codebak\2026-11-04_thumb-latin-title\`. `vi_to_image_latin` — chữ nung ảnh ASCII không dấu; `generate_youtube_titles` CTR bám Baike, cấm template/sáo. Sync V2/V4/V5. Fix follow-up `docs/fixes/2026-11-04-thumb-hardcoded-prompt.md`. **Restart :8801/:8804/:8805** nếu auto-publish/meta in-process; regener title+thumb job cũ nếu cần.

- **Thumb: badge NEW/HOT, giữ AI typography** (03:55). Backup `Z:\PinelineV2_codebak\2026-11-04_thumb-prompt-fix\`. Bỏ scene-only/Pillow; AI vẫn nung chữ 3D; cấm badge «TRỌN BỘ THUYẾT MINH»; hook neo tên. Sync V2/V4/V5. Fix `docs/fixes/2026-11-04-thumb-hardcoded-prompt.md`. **Restart server** nếu auto-publish in-process; regener thumb cũ nếu cần.

- **Hardsub hở theo thời gian** (00:29). Backup `Z:\PinelineV2_codebak\2026-11-04_hardsub-gap-fill\`. Job `50ba645d468b` track chỉ che ~42% (OCR miss). Wire `HARDSUB_FIXED_BOTTOM`; full-cover ratio 0.40; gap-fill. Sync V2/V4/V5. Fix `docs/fixes/2026-11-04-hardsub-temporal-gaps.md`. **Restart :8801/:8804/:8805 + remux** (đang TTS Mùa 5 trên :8801 — hỏi trước khi restart).

- **Hardsub che hở 2 mép** (00:10). Backup `Z:\PinelineV2_codebak\2026-11-04_hardsub-fullw\`. OCR x0/x1 ~52% → ép full ngang + pad dọc; sync V2/V4/V5. Fix `docs/fixes/2026-11-04-hardsub-partial-cover.md`. **Remux job** (không cần restart nếu CLI; server mux cần restart :8801/:8804/:8805).

## 2026-11-03

- **Split parent false-failed** (16:00). Backup `Z:\PinelineV2_codebak\2026-11-03_split-parent-done\`. V2 `merge_job_parts` đánh done đủ stage; queue heal parent đã có Full; V4 clear running khi `return "split"`. Heal `09537b974243`/`b04b8b957d9f`. Fix `docs/fixes/2026-11-03-split-parent-false-failed.md`. **Restart :8801/:8804/:8805.**

- **Aurora file sticky account** (01:43). Upload có `file_id` nhưng chat lấy account pool khác → GPT «không đọc được file» → analyze fallback 8 lô. Vá Aurora `X-Aurora-Account-Id` + sticky `GetByID`; Pineline gửi lại header + cùng host upload. Binary mới `Z:\aurora\aurora` (bak `aurora.bak_before_sticky`). **Cần restart Aurora :5005 trên .244/.247 + Pineline :8801/:8804/:8805.**

- **Aurora file = pool session sống** (01:15). Backup `Z:\PinelineV2_codebak\2026-11-03_aurora-pool-file\`. JWT `data/chatgpt_token.txt` hết hạn bị bỏ qua; upload + chat `input_file` ưu tiên noauth pool (`192.168.31.247:5005`). Smoke OK ~27s. Sync V2/V4/V5. Fix `docs/fixes/2026-11-03-aurora-pool-file-upload.md`. **Restart :8801/:8804/:8805** để process nạp `llm.py`.

## 2026-11-02

- **Pronoun-analyze = upload SRT** (01:10). Mode `file`: Aurora POST /v1/files + chat input_file (API.md). Token local hết hạn → fallback fast (sau đó 2026-11-03 dùng pool). Restart :8804.

- **Pronoun-analyze nhanh** (01:06). PRONOUN_ANALYZE_MODE=fast + chunk 220 + early-stop. **Restart :8804** (job đang 8/28 cần dừng/re-run analyze hoặc chờ xong rồi job sau).

- **Review 31B không phá xưng hô đã lock** (23:55). Backup `Z:\PinelineV2_codebak\2026-11-02_review-pronoun-lock\`. **Restart :8804.**
  - `review_batch`: `review_lock_rules` + `filter_review_fixes_for_lock` (prompt + lọc fix đổi anh/em→ông).
- **Pronoun consistency A–C** (22:21, 3 bản). Backup `Z:\PinelineV2_codebak\2026-11-02_pronoun-consistency-abc\`. **Restart :8804.**
  - `pronoun_consistency.py`: analyze full ZH + lock + ledger + QA jumps + GPT vá.
  - Hook translate plan/batch/post; config `PRONOUN_ANALYZE=1`.
  - Fix log `docs/fixes/2026-11-02-pronoun-consistency-abc.md`.


- **REVIEW_MODEL = gemma4:31b-cloud** (18:36, user yes). Backup `Z:\PinelineV2_codebak\2026-11-02_review-31b\`. **Restart :8804** (nạp `llm.py` cloud route).
  - `CLOUD_LLM_BASE_URL` / `CLOUD_LLM_API_KEY` (từ V2, không ghi key vào docs).
  - `llm.chat` route `ollama/*`/`*-cloud` → 9router thay vì nuốt `:8083`.
- **Aurora GPT cho name/pronoun pass** (18:18, user thử pool Free). Backup `Z:\PinelineV2_codebak\2026-11-02_aurora-name-pronoun\`. **Restart :8804** để server nạp `llm.py`/config (file config GPT keys có hiệu lực ngay cho CLI).
  - `llm.is_chatgpt` + `_chatgpt_chat` (Aurora `:5005`); `config.pass_llm_model`.
  - `NAME_MODEL`/`PRONOUN_MODEL`=`chatgpt/gpt-5-6-mini`; TRANSLATE/REVIEW vẫn local.
  - Test `tests/test_chatgpt_route.py` + smoke PONG qua Aurora OK.
- **Improve xưng hô translate** (13:24, user Cosk làm V4+V5). Backup `Z:\PinelineV2_codebak\2026-11-02_v4-pronoun-pass\`. **Cần restart :8804** (V5 :8805).
  - `translate.apply_pronoun_postpass` + inject pronouns theo scene; siết prompt batch.
  - `agent_pronoun_pass.py`; hook `_run_requested_review` (tên → xưng hô → style).
  - Test `tests/test_pronoun_postpass.py` 3 passed.
- **V5 workspace** (04:17–04:23, quyết định user). Snapshot `Z:\PinelineV2_backup_2026-11-02_0418.zip`. **V4 runtime không đổi** (chỉ docs DECISIONS). Refactor ở `Z:\PinelineV5` — xem CHANGELOG/DECISIONS bên V5.
- **Đồng bộ cấu trúc V4** (04:10). Review `docs/reviews/2026-11-02-v4-structure-sync.md`. Backup `Z:\PinelineV2_codebak\2026-11-02_v4-sync\`. **Cần restart :8804** (+ Ctrl+F5 UI).
  - Vá nhãn/cổng còn V2·8801 trên `index3`, agent_*, `server`/`routes_*`, `fileio`, `migrate_work` docstring, `workflow.html`.
  - `build_desktop.bat` đóng gói `index3.html`; tests Host → `:8804` (4 passed).
  - Còn cố ý: heal/feeder/restart legacy path·port 8801; `scripts/check_batch*`; STATE job history V2.
- **Cleanup thừa + RUNBOOK/ARCHITECTURE V4** (04:05). Backup `Z:\PinelineV2_codebak\2026-11-02_v4-cleanup\`. **Cần restart :8804.**
  - Archive Tauri stack → `scripts/archive/tauri_desktop/`; `index.html` → `ui_legacy/`; `scratch/` → `scratch_oneshot/`.
  - Launcher + `PineLine/` đã trong `launchers_legacy/` (root sạch: chỉ `run_v4` + `run_tele_cmd` + `build_desktop` + install ASR/ORT).
  - `routes_ui`: chỉ `index3.html`. Viết lại `docs/RUNBOOK.md` + `docs/ARCHITECTURE.md` cổng 8804.
- **Audit trùng/thừa + vá** (03:55, user kiểm tra codebase). Review `docs/reviews/2026-11-02-v4-duplication-audit.md`. Backup `Z:\PinelineV2_codebak\2026-11-02_v4-dedupe\`. **Cần restart :8804.**
  - Archive launcher V1/V2: `scripts/archive/launchers_legacy/` (`run_v2`, `run.bat`, `Pineline.bat`, `app.py`, …).
  - `routes_ui`: `/` và `/ui3` ưu tiên **`index3.html`** (hết orphan sau port V2).
  - Canva redirect mặc định `:8804`; `lib_check` sample → `data/samples` V4.
  - Archive `docs/workflow.html` stale; `restart_server`/`migrate_work` bỏ fallback `run_v2`; lock message `PinelineV4`.
- **Auto-split phim dài** (03:21–03:25, user: detect → cắt → đánh số → làm lần lượt → file cuối). Backup `Z:\PinelineV2_codebak\2026-11-02_v4-auto-split\`. **Cần restart :8804.**
  - `batch_config`: `auto_split=true`, `auto_split_min_h=3`, `auto_split_hours=2.5`, `auto_merge=true`.
  - Queue/run-all: probe ≥3h → `{id}_p01…pN` (title «Phần k/N»), xếp **đúng thứ tự**, worker 1 job/lần = part 1 xong mới part 2…
  - Part cuối mux xong → merge → job cha có **`output.mp4`** (+ `output_full.mp4`), stages wired = done.
  - `GET .../split-plan` → `will_auto_split`.
- **Queue sort + meta title + split_parts** (03:15, user: lệch sub phim 12h + làm 1+2+3). Backup `Z:\PinelineV2_codebak\2026-11-02_v4-split-queue\`. Fix log `docs/fixes/2026-11-02-longfilm-sub-drift-split.md`. **Cần restart :8804.**
  - `server.py`: `POST /api/queue/jobs/{sort,move,reorder}`; `GET/POST .../split-plan|split-parts|merge-parts`.
  - `split_parts.py` (port V2): chia ~2.5h/part (smart silence cut), merge `output_full.mp4`.
  - `routes_hg.py`: `POST /meta/generate-title` (giữ ai-image/baike).
  - Pytest `tests/test_queue_jobs_api.py` 2 passed.
- **Follow-up stale port V4** (sau review structure): port `preset_switcher.py`; default `PORT=8804` / `PINELINE_BASE` cho `agent_autopilot`, `agent_hongguo`, `agent_feeder`, `agent_heal` (+`D:\PinelineV4_work`), `meta_studio` poster, `migrate_work`, `restart_server` (start `server.py`/`run_v4.bat`). Codebak `…\2026-11-02_v4-port-v2\followup\`. **Cần restart :8804 + :8802.**
- **Review V4 + port cập nhật từ V2** (02:05–02:20, user yêu cầu). Chi tiết: `docs/reviews/2026-11-02-v4-structure-and-v2-port.md`. Backup codebak `Z:\PinelineV2_codebak\2026-11-02_v4-port-v2\` + zip snapshot `Z:\PinelineV2_backup_2026-11-02_0209.zip`. **Cần restart server :8804 + sidecar :8802** để nạp module mới.
  - Port wholesale từ V2: pipeline (`separate` chunk Demucs dài, `asr.resolve_asr_source`, `nano_fa_asr`, `render` hardsub ngưỡng, `clone_tts` rubberband, `job_queue.get_job_info`, `translate`/`llm`/`series_glossary`, `batch_config`, `film_db` sync_one/upload-lock, `auto_publisher` queue/lock, `meta_studio`, `agent_feeder`, `agent_tele_cmd`, `index3`/`static/app.js`, …).
  - `server.py` (merge): ASR `nano_fa` mặc định; `/api/queue/jobs` thêm `queue_items`; **giữ** `routes_films` + `routes_uploader_settings`.
  - Vá V4: `routes_films.library_action` → feeder (fix log `docs/fixes/2026-11-02-library-action-missing-api.md`); `config` file-first `RENDER_DUB_VOL`/`RENDER_BGM_VOL` (giữ `save_config`); sidecar `BASE` theo `PORT`; poster `films_ui` relative.
  - Kiểm: py_compile OK; pytest job_queue+render_expr+sfx_lib **37 passed**.

- **Cải tiến `/films/ui` & thêm chức năng xoá film** (03:30, user yêu cầu):
  - **`film_db.py`**: thêm `query(work_exists=...)`, `delete_film(job_id, delete_work=...)`, `delete_films(job_ids, delete_work=...)`, `purge_missing(only_pending_failed=...)`, cập nhật `stats()` trả `work_exists` và `work_missing`.
  - **`agent_tele_cmd.py`**: thêm endpoints `POST /films/delete`, `POST /films/purge-missing`, `POST /films/sync`, lệnh Telegram `/delfilm <job_id> [work]`, nhận tham số `work_exists` trong `GET /films`. **Đã restart sidecar :8802.**
  - **`films_ui.html`**: giao diện quản lý phim trực quan với cột thao tác nút `🗑️ Xoá` (kèm modal tuỳ chọn xoá file `work/` hoặc chỉ xoá DB), thanh chọn nhiều job để xoá hàng loạt, bộ lọc thư mục (tất cả / chỉ còn thư mục / đã xoá), toggle "Ẩn đã xoá thư mục", banner cảnh báo job mất thư mục kèm nút `🧹 Xoá sạch toàn bộ` / `Chỉ xoá pending/failed`.
  - Backup: `Z:\PinelineV2_backup_2026-10-09_0124.zip`, codebak `Z:\PinelineV2_codebak\2026-10-09_films-ui-delete\`. Fix log: `docs/fixes/2026-10-09-films-ui-delete-missing.md`.

## 2026-10-08

- **PineLine V3 portable** (00:00-01:50, user yêu cầu): bản mang đi ở `Z:\PinelineV3` (~10,8 GB), chạy bằng `PineLine.exe` (launcher tkinter, PyInstaller). V2 không đổi. Chi tiết: `Z:\PinelineV3\README_V3.md`.
  - `app\` = clone V2 `ea7b881` (bỏ remote, nhánh `v3`) + asset (cdx23, bgm_yt, voices, `data/films.db`); không chép secret/token/cookie.
  - `runtime\python` 8,3 GB: Python 3.12 + torch 2.8.0 cu128 (RTX 20xx-50xx, driver ≥ 570) + 192 gói, `pip check` sạch; chạy với `PYTHONNOUSERSITE=1`. `runtime\ffmpeg` 8.1, `runtime\llama` (llama-server CUDA 12), `apps\hongguo` (bản quyền riêng, máy mới có thể phải kích hoạt lại). 9router không đi kèm.
  - Model (~8-9 GB) tải lần đầu từ launcher (`launcher\setup_models.py`: Fun-ASR-Nano, fsmn-vad, paraformer-zh, ct-punc, Qwen3-ForcedAligner, VieNeu v3 Turbo, MOSS tokenizer).
  - LLM mặc định Ollama Cloud (`https://ollama.com/v1`, `gemma4:31b`, dự phòng `gpt-oss:120b`), key nhập trong launcher, ghi vào `pineline.config.json` (gitignore).
  - GPU tự dò (`nvidia-smi`): CUDA nếu driver ≥ 570, batch VieNeu theo VRAM; không NVIDIA → CPU + x264.
  - Sửa code cho portable (chỉ ở V3): `agent_hongguo` (`HONGGUO_DIR`), `server`/`pick_dirs_dialog`/`agent_feeder` (`PINELINE_LIB` thay `D:\Lib` cứng), `migrate_work` (`PINELINE_BASE`/`PORT`/`AUTOPILOT_PORT`), `restart_server` (`PINELINE_TMP`, cổng theo env), `run_v2.bat`/`run_tele_cmd.bat` (runtime portable + `v3_env.bat`).
  - Kiểm: import + CUDA, VieNeu tổng hợp trên GPU, Fun-ASR-Nano, server V3 cổng 9801 (UI/API 200), tải paraformer qua launcher, exe nhận dịch vụ V2 là "ngoài launcher".
- **Sự cố ổ D: đầy 0 GB** (01:20-01:35): gộp 问鼎仙途 6,9 GB + render → mux 0be257b1594b lỗi `Error muxing a packet`, 9a78abb17ad5 lỗi đầu ASR, worker hàng đợi chết (`_save` OSError). User cho xoá `mixed_audio.wav` + `dub_fit.wav` của 13 job đã render xong (26 file, 52,1 GB). Kích lại hàng đợi (xoá + thêm lại job chờ). Chưa sửa code. Fix log `fixes/2026-10-08-queue-worker-disk-full.md`.

## 2026-10-07

- **Sơ đồ workflow toàn hệ thống** (12:50): `docs/workflow.html` — trang tĩnh mở bằng trình duyệt, 7 tầng (giao diện, AI agent, nguồn phim, job/hàng đợi, pipeline, đầu ra, hạ tầng), 33 khối + 54 đường nối, bấm khối xem chi tiết/file/kết nối; kèm bảng 3 cách điều khiển và chốt an toàn.
- **Hongguo: tạo job UI3 từ thư viện** (06:03–06:10, user yêu cầu): `/hongguo` tab Hàng đợi gộp → thư viện: nút **«＋ Job»** mỗi series (tạo job UI3 từ file `(merged)` qua `POST /api/jobs/local-path`, title = tên folder, đọc thẳng `D:\Lib`), **«＋ Job đã chọn»** + ô «chạy luôn» (xếp `POST /api/queue/jobs` theo CONFIG BATCH, mặc định tắt). Series đã có job (khớp `download.video_path` hoặc `title_zh` bỏ « (merged)») hiện **«↗ UI3»** mở thẳng job; khoá nút khi chưa gộp hoặc đang trong hàng đợi gộp; hỏi lại nếu tạo trùng. Log chung thêm dòng `[job]`. UI3 nhận `?job=<id>` để mở thẳng job. Chỉ sửa `hongguo.html` + 1 dòng `index3.html`, không restart. Backup `codebak\2026-10-07_hg_add_job\`.
- **Hongguo: thanh công cụ gọn + log dạng dock** (04:53–04:58, user yêu cầu): Thanh công cụ gọn: tab + công cụ của tab trên **1 hàng** (bỏ tiêu đề từng pane; Bảng hot 46px, Tìm 75px, Catalog 85px ở 1920px — trước ~6 hàng). Sửa lỗi ô tìm catalog hiện cả khi đang ở Leaderboard (`.exctl{display:flex}` đè `hidden`). Khung tải/log thành **dock thu gọn** ở đáy (mặc định 40px: trạng thái + dòng log mới nhất; «▴ Log» mở, nhớ trong localStorage). Thẻ phim 176px (10 cột ở 1920px). Không restart. Backup `codebak\2026-10-07_hg_compact_top\`.
- **Hongguo: thư viện vào tab Hàng đợi gộp** (04:46–04:50, user yêu cầu): Khung **Thư viện Hongguo** chuyển vào tab «🎞 Hàng đợi gộp» (hàng đợi trái, thư viện phải 440px; màn < 980px xếp chồng), bỏ cột phải → Tìm / Bảng hot dùng hết chiều ngang. Series trong hàng đợi có nhãn «● đang gộp» / «chờ #n»; xếp hàng xong tự bỏ tick; nút «Chưa gộp» không tick series đã trong hàng đợi. Không restart. Backup `codebak\2026-10-07_hg_lib_in_tab\`.
- **Hongguo: tab Hàng đợi gộp + 1 log chung** (04:35–04:40, user yêu cầu): `/hongguo`: hàng đợi gộp chuyển thành **tab riêng** «🎞 Hàng đợi gộp» (cạnh Tìm / Bảng hot, có số series còn lại) — nút Gộp đã chọn / Tất cả chưa gộp / Xoá hàng chờ, khối Đang làm (bước · % · thời gian · thanh tiến độ), danh sách chờ đánh số, kết quả gần đây; bấm gộp tự mở tab này. Bỏ khối Merge queue ở cột thư viện. **Một log chung** «Trạng thái tải · log»: dòng `[tải]` + `[gộp]` xếp theo giờ (chuẩn hoá % chỉ giữ dòng mới nhất), Clear ẩn dòng cũ. Không restart. Backup `codebak\2026-10-07_hg_merge_tab\`.
- **Hongguo Merge all bền + hiện tiến độ** (04:28–04:32): hàng đợi gộp lưu `work/logs/hg_merge_state.json`, server khởi động/UI hỏi trạng thái thì chạy tiếp; `merge_queue_add` chỉ xếp hàng (chuẩn hoá/dọn chuyển vào worker); UI hiện series · bước · % · thời gian, tiến độ lô, 6 kết quả gần nhất; `restart_server.py` từ chối restart khi đang gộp (`--ignore-hg` để ép). Test 5 mới, pytest 103/103, check_batch1–5 pass. Backup `codebak\2026-10-07_hg_merge_q\` + zip 04:28. Restart server PID 32156. Fix log `fixes/2026-10-07-hg-merge-queue.md`.
- **Job đọc video thẳng từ `D:\Lib`** (04:00–04:25, user chọn): import file trong `SOURCE_DIRECT_ROOTS` (mặc định `D:\Lib`) → manifest `video_path` = đường dẫn thư viện, không đặt file vào job; ngoài thư viện vẫn hard link/copy. Ghi `source_mode`/`video_size`/`video_mtime`; heal báo `source_changed`; `agent_av_sync`, `media_ts --check` đọc `video_path`. Test 5, liên quan 17/17, check_batch1–5 pass. Backup `codebak\2026-10-07_source_direct\`. Restart server PID 22868.
- **Source video không chép 2 bản** (03:40–03:46): `server._link_or_copy` — hard link trước, chỉ copy khi khác ổ (có log); dùng cho import thư viện và `/api/jobs/{id}/source-path` (trước luôn copy). Test `tests/test_source_link.py`, pytest 96/96. Backup `codebak\2026-10-07_source_link\` + zip 03:42. Restart server (queue rảnh) PID 28108. Fix log `fixes/2026-10-07-source-duplicate-copy.md`.
- **Restart server + sidecar** (03:22, queue rảnh): sidecar nạp `batch_config` có `sfx_lib` (trước đó Telegram `/set audio_mode=sfx_lib` bị từ chối). Server PID 56888, sidecar PID 27392.
- **Docs** (03:02): RUNBOOK thêm bảng 7 chế độ âm thanh; kho `bgm_yt` đã dò không có bài nào có lời.
- **CONFIG BATCH → `sfx_lib`** (02:52, user duyệt mẫu). Chỉnh theo user (nhạc nhỏ hơn, tiếng động to vừa phải, giọng to hơn): `RENDER_SFX_VOL` 0,62, `RENDER_LIB_BGM_VOL` 0,25, key mới `RENDER_SFX_VOICE_BOOST` 1,25 (× `RENDER_DUB_VOL`), limiter −1 dBFS. Sửa hụt đuôi pass 1 (`fixes/2026-10-07-sfxlib-sidechain-short.md`). Backup `codebak\2026-10-07_sfxlib_tune\` + zip 02:45. Pytest 93/93. Mẫu `E2_sfx_lib_chinh.mp4` (−15,8 LUFS, peak −0,9 dBFS).
- **Chế độ audio `sfx_lib`** (02:10–02:36): giọng Việt + tiếng động gốc (CDX23) + nhạc kho YouTube theo mức. Backup `codebak\2026-10-07_sfxlib\` + zip. Render tự chuẩn bị (tiến trình con, ~14 phút/phim 2,6 h lần đầu, cache sau). Server cần restart cho `batch_config`/`agent_core` (danh sách chế độ); render/sfx_lib nạp lại mỗi lần render.
  - Mới: `sfx_lib.py`, `models/cdx23/` (3 checkpoint, MIT, `.gitignore` thêm `*.th`), `tests/test_sfx_lib.py` (11 test). Pytest 92/92.
  - `render.py`: mode `sfx_lib` (alias `sfx_library`/`sfx_yt`/`yt_lib`; `sfx_bgm` vẫn là `duck_bgm`), two-pass sidechain, gọi `sfx_lib.run_subprocess` trước pass 1, ghi tiến độ vào `cur_text`.
  - `batch_config.py`, `agent_core.py`, `index.html`, `index3.html`, `static/app.js`: thêm lựa chọn `sfx_lib`. `restart_server.py`: precheck thêm `sfx_lib.py`.
  - CONFIG BATCH **không đổi** (vẫn `duck`).

- **Kho nhạc YouTube Audio Library** (02:40). `assets/bgm_yt/{calm,mid,intense}/` 45 bài (Attribution not required, Ambient/Cinematic) + `assets/bgm_yt/manifest.json` (license từng bài). Chưa có code dùng; `assets/bgm/` giữ nguyên. Không cần restart.

- **M20 — `voice_bgm` thêm `apad` cho dub** (01:50). `render.py` `_build_audio_filter`. Cần restart server cho render mới; CONFIG BATCH không đổi. Test mới trong `tests/test_render_expr.py`, pytest 81/81. Fix log `fixes/2026-10-07-m20-voice-bgm-apad.md`. Backup `codebak\2026-10-07_m20\` + zip 0147.

- **Restart văng lần 2 → sửa root cause thật** (01:27–01:40). Fix log `fixes/2026-10-06-restart-killed-itself.md` (mục cập nhật 07/10). Backup `Z:\PinelineV2_codebak\2026-10-07_restartfix2\` + `2026-10-07_restartfix3\` + zip 0135.
  - `migrate_work.kill_with_parent_cmd`: mọi lời gọi psutil trên tiến trình đã chết được bỏ qua (`procs()` trả cả `cmd.exe` bọc server, cmd tự thoát khi python bị kill → `NoSuchProcess`).
  - `tests/test_restart_guard.py`: thêm `test_kill_dead_process_is_noop`, `test_kill_wrapper_after_child`. Pytest 80/80.
  - Đã restart bằng `restart_server.py --clean-env --sidecar` (queue rảnh): server PID 59488, sidecar PID 57748 — **đợt 7 đã có hiệu lực**. Auto-pilot vẫn tắt.

## 2026-10-06

- **Đợt 7 — gỡ UI cũ, tách server.py** (14:50–15:20). **Cần restart server** mới có hiệu lực (chỉ khi hàng đợi rảnh / user đồng ý). Backup zip 1455 + `Z:\PinelineV2_codebak\2026-10-06_batch7\`. Fix log `fixes/2026-10-06-batch7-ui-split.md`.
  - Xoá `index1.html`, `index2.html`, route `/ui1` `/ui2` `/index1.html` `/index2.html`; bỏ link trong `index.html`, `index3.html`; `hongguo.html` nút UI1 → `/ui3` (HTML có hiệu lực ngay).
  - `server.py` 6221 → 5372 dòng: `routes_ui.py`, `routes_hg.py`, `routes_agent.py` (`APIRouter`, gọi server qua `S.<tên>`, `server` re-export tên cũ, alias `sys.modules["server"]` khi chạy `python server.py`). OpenAPI 108 route giống hệt.
  - `restart_server.py`: precheck compile thêm `routes_*.py`. `tests/test_server_split.py`. Pytest 78/78.

- **Restart hẹn giờ chết giữa chừng** (13:58, phát hiện 14:31, sửa 14:35–14:50). Fix log `fixes/2026-10-06-restart-killed-itself.md`. Backup `Z:\PinelineV2_codebak\2026-10-06_restartfix\` + zip 1435.
  - `migrate_work.kill_with_parent_cmd`: không kill chính mình / tổ tiên (psutil duyệt con đệ quy chỉ so thời điểm tạo với gốc → PID tái dùng làm tiến trình gọi thành "cháu").
  - `restart_server.py`: log từng bước sau khi job xong; `try/except` ở `main` ghi traceback + báo Telegram.
  - `tests/test_restart_guard.py`. Pytest 76/76.
  - Đã start tay server (PID 25032) + sidecar (PID 13400) bằng code mới, xếp lại 3a2e. Đợt 1–6 giờ đã có hiệu lực.
  - `D:\PinelineV2_tmp\snapshot.py`: bỏ qua file đang bị khoá.

- **Đợt 6 review — bảo trì** (10:26–10:40). Pytest 75/75. Backup zip 1028 + `Z:\PinelineV2_codebak\2026-10-06_batch6\`. Fix log `fixes/2026-10-06-batch6-maintenance.md`.
  - Git local: `git init` (không remote), `.gitignore` (secret, `work/`, `data/`, voices, lock, log, media), `core.autocrlf=false`, `pineline.config.example.json` (key để rỗng). Commit gốc `7657fea`, quét secret trước khi commit.
  - `pytest.ini`; `tests/test_review_batches.py` (chạy `check_batch1–5`), `tests/test_agent_parser.py`, `tests/test_render_expr.py`. Sửa kỳ vọng sai trong `test_hardsub_asr.py`.
  - `render.py` (M3): `_sum_expr` / `_pw_expr` dựng cây khi trên 64 đoạn, vì ffmpeg lỗi khi `if()` lồng ≥100 tầng hoặc tổng `between` >100 hạng tử. ≤64 đoạn: filter giống hệt bản cũ. Hiệu lực ngay ở lần mux tới.
  - Chuyển 29 script một lần / UI dump ở gốc sang `codebak\2026-10-06_batch6\attic\`. Giữ `_read_hg_ui_token.py`.
  - `requirements.txt`: thêm `psutil`, `rapidocr-onnxruntime`, `pytest`.
- **Đợt 5 review — agent an toàn hơn** (10:09–10:25). Test `scripts/check_batch5.py` (128). Backup zip 1009 + `Z:\PinelineV2_codebak\2026-10-06_batch5\`. Fix log `fixes/2026-10-06-batch5-agent-safety.md`.
  - `agent_tele_cmd.py`:
    - `_slash_hint`: chữ trơn đổi trạng thái (`stop`, `reset`, `set`, `feed on`, `hg auto`/`hg 2`/`hg clean`, `lib add`…) chỉ trả gợi ý "gõ /…"; câu dài thì chuyển cho agent.
    - Bỏ nhánh đoán "auto"+"pilot".
    - Nút ✅/❌ cho thao tác agent đang chờ (`agc:`).
    - Worker FIFO cho tin Telegram, `/stop` `/off` `/status` chạy ngay.
    - `/hg` auto chạy nền, chống trùng.
    - `/agent` giữ nguyên hoa/thường.

    **Restart sidecar.**
  - `agent_core.py`: `tool_tier` (read/mutate/confirm), `park_action`/`confirm_action` (hết hạn 15 phút), `run_agent(require_confirm=...)`, `clip_tool_result` (6000 ký tự), SYSTEM bỏ tool ma `qa_override` và thêm quy tắc 15, hết bước thì liệt kê thao tác đã chạy, `Runtime.notify`. **Restart server.**
  - `agent_hongguo.py`: `detect_flow_mode` (chỉ nhận cả chuỗi), `tool_hg_auto_flow(mode=name|lib|rank)`, `start_auto_flow_bg` (chạy nền + chống trùng), agent gọi `hg_auto_flow` → chạy nền. **Restart server + sidecar.**
  - `server.py`: `AgentChatReq.require_confirm`, `/api/agent/chat` trả `confirms`, `GET /api/agent/pending`, `POST /api/agent/confirm`, `_agent_notify`. **Restart server.**
  - `agent_autopilot.py` (`agent_chat(require_confirm)`, `agent_confirm`), `agent_feeder.py` (`lib_verb`). **Restart sidecar.**
  - Xoá `agent_v2/` (bản cũ lệch, không ai import; bản sao trong backup batch5).
- **Đợt 4 review — tranh chấp ghi, một bản tiến trình, checkpoint an toàn** (09:44–10:10). Test `scripts/check_batch4.py` (56). Backup zip 0944 + `Z:\PinelineV2_codebak\2026-10-06_batch4\`. Fix log `fixes/2026-10-06-batch4-write-races.md`.
  - `manifest.py`: `save()` gộp 3 chiều với bản đĩa trong khoá liên tiến trình; `update(fn)`. **Restart server** (subprocess dùng ngay ở lần spawn kế).
  - `server.py`: `_patch_*_fields` qua `Manifest.update`; claim cho `tts`/`mux`/`translate`/`translate/fill`/`assemble` (409 khi đang chạy); khớp/kill engine theo đường dẫn job; `mark-done` 409 khi job trong hàng đợi; worker hàng đợi khởi động sau startup reset; khoá một bản `.server_{port}.lock`; `POST /api/queue/jobs/opts`. **Restart server.**
  - `job_queue.py` `queue_update_opts`. **Restart server.**
  - `agent_autopilot.py`: đồng bộ opts qua `/opts` thay remove+add, không xếp lại job failed; `agent_core.py` `need_queue` bỏ failed/HOLD/QA. **Restart server + sidecar.**
  - `agent_tele_cmd.py`: khoá một bản `.sidecar_{port}.lock`, bind độc quyền trước khi chạy loop. **Restart sidecar.**
  - `fileio.py`: `atomic_write_json`, `read_json_checkpoint`; `file_lock` bắt `PermissionError` (Windows). **Restart server + sidecar.**
  - `asr.py` + 4 engine ASR: `ensure_audio_wav` / marker `audio.wav.json`, `asr.json` nguyên tử. Hiệu lực lần ASR kế tiếp.
  - `translate.py`: `script.json` nguyên tử. `clone_tts.py`: key clip (lời/giọng/engine/tốc độ), `tts/_keys.json`. **Restart server.**
  - `assemble.py` (`dub_fit.partial.wav`), `render.py` (`mixed_audio.json`): hiệu lực ngay lần mux tới.
  - `restart_server.py`: precheck thêm module mới.
- **Đợt 3 review — một nguồn opts/config, ghi nguyên tử** (09:37–10:00). Test `scripts/check_batch3.py` (35). Backup zip 0937 + `Z:\PinelineV2_codebak\2026-10-06_batch3\`. Fix log `fixes/2026-10-06-batch3-single-source.md`.
  - `fileio.py` (mới): `atomic_write_text`, `file_lock`.
  - `batch_config.py`: ghi nguyên tử + khoá, `load()` giữ bản tốt gần nhất, `resolve_job_opts`, `render_kwargs`. **Restart server + sidecar.**
  - `agent_autopilot.py`: state ghi nguyên tử, `update_state` trong khoá. **Restart sidecar.**
  - `server.py`: API xếp hàng lấy trường thiếu theo config batch; `_queue_run_one`, `_agent_mux_run`, `run_stage mux`, `_agent_resume` dùng `resolve_job_opts` (giọng không lấy từ config batch); `config.inject_env()`. **Restart server.**
  - `config.py`: `inject_env()`, `get()` đọc file trước cho key chép từ file. `llm.py`, `app.py` dùng `inject_env()`. `render.py` `RENDER_ENCODER` qua `config.get`. `config.py`/`render.py` có hiệu lực ngay (nạp lại mỗi lần mux).
- **`restart_server.py`** (09:30) — thêm `--hold-file`/`--hold-max-h`, `--clean-env` (start bằng `start_8801.py` với env chụp từ server cũ), `--sidecar`. Thêm py_compile + import thử trước khi kill; lỗi thì không restart và xếp lại job. Ghi `work/logs/restart_pending.json`. Backup `Z:\PinelineV2_codebak\2026-10-06_restart\`. Đã chạy hẹn giờ lúc 09:34 (rút 3a2e). Không cần restart.
- **Đợt 2 review — bảo mật + config một nguồn + LLM sập** (09:10–09:35). Test `scripts/check_batch2.py` (69 kiểm tra). Backup trước: zip 0908 + `Z:\PinelineV2_codebak\2026-10-06_batch2\`. Fix log `fixes/2026-10-06-batch2-security.md`.
  - `server.py`: middleware `_local_only_guard` chặn Host/Origin/Referer lạ (S4); `_hg_base` bỏ `base` từ client (H4); dịch tiêu đề đọc `TRANSLATE_MODEL` qua config. **Cần restart server.**
  - `hongguo_bridge.py`: `safe_child` cho preview/poster/merge (H5). **Cần restart server.**
  - `index.html`, `index3.html`, `static/app.js`: `escapeHtml` thoát `'`, tên nhóm/`group_id` trong onclick qua escape (H6). Có hiệu lực ngay (Ctrl+F5).
  - `agent_tele_cmd.py`: `_blocked()` + CORS chỉ origin local (A2). **Cần restart sidecar.**
  - `config.py`: `AGENT_*` file-first, `llm_settings()`, `agent_llm()`; `agent_core.py`/`agent_feeder.py` dùng `agent_llm()`. **Cần restart server + sidecar.**
  - `llm.py`: đọc base/key/model lúc gọi (M8), `LOCAL_LLM_BASE_URL` mặc định Ollama 11434 (M9), `LLMUnavailable` khi LLM sập, 400/413/422 không retry (M7); bỏ key trong docstring. **Cần restart server.**
  - `translate.py`, `translate_alts.py`: `_tmodel()/_rmodel()` đọc lúc gọi; `LLMUnavailable` dừng stage (salvage → pending) thay vì để trống câu (M7). **Cần restart server.**
  - Secret (H7): bỏ key khỏi `run_v2.bat` (cùng `LLM_*` chết), `run_tele_cmd.bat`, `config.json`, `.claude\settings.local.json`; `D:\PinelineV2_tmp\redact.py` + `snapshot.py` che secret trong zip. Có hiệu lực ngay.
  - `tests/test_queue_jobs_api.py`: TestClient dùng Host `127.0.0.1:8801`.
- **Đợt 1 review — chặn mất dữ liệu** (08:34–09:10). Test `scripts/check_batch1.py` (mới, 44 kiểm tra trên thư mục tạm). Backup trước: `Z:\PinelineV2_backup_2026-10-06_0834.zip` + `Z:\PinelineV2_codebak\2026-10-06_batch1\`. Fix log `fixes/2026-10-06-batch1-data-loss.md`.
  - `assemble.py` `assemble_fit`: cắt câu runaway theo `dur/ratio` (M5). **Không cần restart** — có hiệu lực ở lần render kế tiếp.
  - `media_ts.py` `ensure_job_audio_ts`: 2 pha + `.audio_ts_pending.json`, `_commit_retime`, `_backup_once` (M2). **Không cần restart** (render reload).
  - `server.py`:
    - `_stage_complete_on_disk`, `_path_key`.
    - `read_job` không heal.
    - Heal dùng kiểm tra đủ (S1).
    - So cwd ffmpeg bằng realpath (S3).
    - Stamp đủ `queue_opts` (S7).

    **Cần restart server.**
  - `job_queue.py`: giữ opts job đang chạy tới khi xong (S6). **Cần restart server.**
  - `restart_server.py`: job thiếu snapshot opts → opts toàn cục + `queue_opts` manifest. Không cần restart.
  - `hongguo_bridge.py`: `merged_covers_fragments`, `cleanup_fragments` (chỉ tập đúng mẫu, ≥98% thời lượng, vào `D:\Lib_trash`, giữ 7 ngày), `purge_trash`, gộp lại khi có tập mới, poll gộp bám tên series, chuẩn hoá lỗi không dọn (H1/H2/H3/H11). **Cần restart server.**
  - `agent_hongguo.py`: số trần không có danh sách → hỏi lại; `_pick_lib_item` (trùng tên → series_id → chuỗi con duy nhất); hết giờ tải / thiếu tập → dừng (A3/A4). **Cần restart server + sidecar.**
  - `agent_feeder.py`: `_downloading_sids` đọc khoá `sid` của `/dl/status`. **Cần restart server + sidecar.**
- **`agent_core.py`** (06:00) — Siết parser tool call dạng chữ: chỉ nhận lời gọi đứng riêng hoặc sau nhãn `Action:`; bắt `TypeError` (giá trị `...`); `run_agent` chỉ parse dạng chữ khi lượt chưa chạy tool nào. Fix log `fixes/2026-10-06-agent-text-toolcall-overmatch.md`. **Cần restart server** (cùng đợt với các sửa agent khác).
- **docs/reviews/2026-10-06-code-review.md** — Review toàn bộ code V2 + agent (4 mảng).
- **docs/** — Dựng hệ thống markdown (`README`, `STATE`, `ARCHITECTURE`, `RUNBOOK`, `DECISIONS`, `CHANGELOG`, `worklog/`, `reviews/`). `PROJECT_STATE.md` thành trang trỏ; bản cũ khôi phục từ backup 5/10 tại `docs/archive_PROJECT_STATE_2026-10-05.md`. Rule mới `.cursor/rules/docs-on-change.mdc`.
- **`agent_core.py`** — `_parse_pycall_tool_calls()`: bắt tool call dạng `tool(key=value)` (tên thuộc `_TOOL_NAMES` hoặc tiền tố `pineline_`, chỉ keyword args, `ast.literal_eval`); `_parse_text_tool_calls` fallback sang nó. SYSTEM: folder trong `D:\Lib` chưa có job → `library add`/`hg_auto_flow`, `queue_add` chỉ cho job có sẵn; quy tắc 14 "hành động = gọi tool". **Cần restart server.**
- **`agent_hongguo.py`** — `tool_hg_library(query="")` lọc theo query, trả đủ (trước cắt `[:30]` → 77 bộ chỉ thấy 30). `tool_hg_merge` gọi `POST /api/hg/merge` của server (fallback `merge_queue_add` nếu server không lên). **Server cần restart; sidecar đã restart.**
- **`hongguo_bridge.py`** — State hàng đợi gộp (`_merge_lock/_q/_cur/_hist/_stop/_thread/_done`) giữ qua `importlib.reload` bằng `globals()`. **Cần restart server.**
- **`render.py`** — Che hardsub `HARDSUB_STYLE=stretch` mặc định: lấy hàng ảnh ngay trên vùng chữ kéo giãn xuống (1 lớp), gộp nhiều vị trí đồng thời thành 1 dải, `HARDSUB_STRETCH_SIGMA`/`_V` mặc định 0/0 (không `gblur`), đệm 15/13 px, phủ hết ngang. Không cần restart.

## 2026-10-05

- **`render.py`** — Render chia khúc `RENDER_CHUNK_SEC` (300) × `RENDER_CHUNK_PAR` (3, tối đa 6): `-copyts -ss … -to …`, điểm cắt giữa 2 khung, tránh vùng mốc nén, `-enc_time_base demux`, concat demuxer + inpoint/outpoint `-c copy`, khúc lỗi → render lại 1 lượt. Bỏ `RENDER_CHUNKS` cũ.
- **`media_ts.py`** (mới) — `AUDIO_TS_FIX` (aresample async) dùng trong `asr.py`, `separate.py`, `mux.py`, `render.py`; `ensure_job_audio_ts()` chỉnh mốc job cũ (backup `_pre_audio_ts/`, đánh dấu `.audio_ts_fixed.json`); CLI `--check`. `agent_av_sync.py` thêm check `audio_ts_drift`.
- **`assemble.py`** — Khớp thời gian thích ứng: nền 1,12×, tăng tới 1,30× khi trễ, vào sớm ≤0,15 s, câu phình tới 1,6×; đánh dấu `.fit_mode`, job ghép bằng code cũ tự ghép lại khi render. `ASSEMBLE_FIT_MODE=off` để tắt. `render.py` reload kéo theo `assemble`/`media_ts`.
- **`server.py`, `job_queue.py`** — Không tự load queue / khởi worker khi chạy dưới pytest (23/23 test qua, 4 s).
- **`config.py`** — Key LLM ưu tiên `pineline.config.json` hơn env; model dịch/review/agent = gemma4 qua 9router. `start_8801.py` start server sạch env.

## 2026-10-04

- **`render.py`** — `HARDSUB_MODE=track` mặc định: dò dải hardsub theo đoạn (~300 khung OCR, `hardsub_track.json`), blur đúng vùng trước zoom, bỏ lớp đen (`HARDSUB_MODE=bar` để dùng lại). Sub Việt bám dải hardsub. Audio AAC encode song song với hình (ghép cuối ~1 phút thay ~50 phút). `_boxblur_r` tính theo chiều cao chẵn + kênh màu nửa kích thước (fix watermark mỏng 16–17 px làm job 12032 fail). `duck`: tiếng gốc chạy hết độ dài video.
- **Cắt video** — 0281 `output.mp4` 14,5 h → `output_part1/2.mp4` (copy, cắt tại keyframe trong khoảng nghỉ thoại).

## 2026-10-03

- **`render.py`** — Chia 2 đoạn render song song + ghép copy + gắn audio 1 lần (fallback 1 mạch); sửa tập 25 fps hỏng mốc (trải lại khung); LUT `lut3d` → `lutrgb` (giống từng bit, nhanh hơn ~43%). Sửa cách tính % pass 2.
- **ffmpeg** — Nâng lên 8.1.2 full_build (NVENC OK). Thử libplacebo LUT: không dùng.
- **`agent_hongguo.py`, `agent_tele_cmd.py`** — Hongguo preview (`/dl/preview`, episodes), `/hg rank` (leaderboard 3 tab), `/hg catalog`, nút 👁 xem thử.

## 2026-09-30

- **`yt_uploader`** — Xử lý HTTP 308 resumable (không dừng sau khúc đầu); khúc 256 MB + log tốc độ; xoá dòng bằng Delete/chuột phải kể cả khi đang upload; bỏ file trung gian khi thêm folder job; lấy tên Việt từ `films.db`.
- **`translate.py` / `context_studio`** — Phân tích mạch truyện/xưng hô: bỏ cặp mặc định, "ngươi" → "mày", tăng cửa sổ mẫu (`n_win=12`, `win=70`). cc52: ghép `sub.vi.srt` user sửa vào `script.json`, sửa 17 lỗi 他/她, TTS lại.
- **`E:\models\presets`** — Preset gemma4-26b-qat-mtp chuyển `--fit` 131k.

## 2026-09-29

- **`agent_feeder.py`** (mới), **`agent_autopilot.py`**, **`agent_tele_cmd.py`** — Theo dõi job treo (tiến độ + file + CPU, 30/45 phút → stop + xếp lại đầu, tối đa 2 lần/stage); feeder tự thêm phim khi rảnh (`/feed`, mặc định OFF); `/lib` thư viện có nút Thêm/Ưu tiên/Bỏ/Ghép.
- **`film_db.py`** (mới), `films_ui.html` — SQLite `data/films.db`, sync 2 phút, `/films/ui` (fix trùng `window.status`).
- **`agent_name_pass.py`**, `agent_core.py` — Yêu cầu rà tên/văn phong trước TTS: job đang dịch thì hẹn, xong dịch tự rà → QA gate → TTS.
- **`yt_uploader`** — Đa tài khoản + proxy, khoá IP từng request (upload, chunk, refresh token, thumbnail), chặn proxy rò.

## 2026-09-28

- **`yt_uploader`** — Mô tả mẫu biến, thumbnail tự ghép tên/chọn nhiều, chuyển ra `Z:\yt_uploader`, sửa hàng loạt, đặt tên tài khoản + hiện kênh/email.
- **Hệ thống** — Dọn `C:\temp\sslkey.log` 9 GB, tắt `SSLKEYLOGFILE`.

## 2026-09-27

- **`server.py`, `job_queue.py`** — Ép snapshot opts cho mọi job khi đến lượt, lưu `queue_opts` vào manifest. STOP tắt Auto-pilot.
- **`batch_config.py`** (mới) — `work/logs/batch_config.json` dùng chung; Telegram `/config` `/set` `/reset`; agent tool đọc/sửa config batch; UI3/UI4 nút "Lưu làm config batch".
- **`agent_core.py`** — Tool `queue_add` nhận `group_id` + đủ opts; fallback parse tool call JSON dạng chữ.
- **`index3.html`** — Âm nền + các ô batch nhớ qua localStorage; tiêu đề nhóm không vẽ lại mỗi 2 s; hộp xác nhận tóm tắt config. `index4.html`: ▶ Group.
- **`migrate_work.py`** — Chuyển `work` sang `D:` + junction, retry khi server chậm.
- **`run_v2.bat`, `agent_core.py`** — Tách `AGENT_*` (9router) và `LLM_*` (local).
- **`yt_uploader/`** (mới) — App tkinter upload YouTube OAuth, chọn trình duyệt/copy URL.

## 2026-09-26

- **`render.py`, `agent_av_sync.py`, `agent_core.py`, `server.py`** — Port duck/duck_bgm two-pass sang V2; AV scan/heal_batch (`docs/fixes/2026-09-26-duck-bgm-twopass-port.md`).
- **P0 quản lý job** — opts theo job, chạy cả series, dashboard queue (stage/%/ETA), GPU gate heal/watch (`docs/fixes/2026-09-26-p0-job-management.md`).
- **`index4.html`** (mới) — UI4 Ops (`docs/fixes/2026-09-26-ui4-ops.md`), form + Job, nút stage, panel Agent kéo resize.
- **`index3.html`, `server.py`, `pick_dirs_dialog.py`** — Sửa `compose-on`; `POST /api/jobs/local-batch` nhiều folder; hộp thoại chọn nhiều folder.
- **`agent_autopilot.py`, `agent_tele_cmd.py`** (mới) — Sidecar :8802, Auto-pilot, Telegram `/on /off /status /heal /tick /stop /agent`.

## 2026-09-24 → 25

Xem `docs/fixes/` (stop mux, hardsub hwaccel/drawbox, run-all stale mux, queue voice stop race, duck bgm truncate) và `docs/superpowers/` (job queue tuần tự).



