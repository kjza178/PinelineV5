# `server`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-11 02:38. Đừng sửa tay khối này. -->
**File:** `server.py` · **Lớp:** `control` · **6602 dòng** (5766 code) · **176 hàm**, **28 class** · sha1 `5d1ac8d5ab`

> server.py — Backend web Phase 1 (FastAPI). Bọc engine (download -> asr -> translate) thành app web: - Phục vụ trang dashboard (web/index.html)

### Phụ thuộc

- **Gọi tới (import nội bộ):** [agent_brain](./agent_brain.md), [agent_qa_gate](./agent_qa_gate.md), [agent_quality](./agent_quality.md), [auto_publisher](./auto_publisher.md), [batch_config](./batch_config.md), [config](./config.md), [hg_ui_ctx](./hg_ui_ctx.md), [hongguo_bridge](./hongguo_bridge.md), [job_queue](./job_queue.md), [llm](./llm.md), [render](./render.md), [routes_agent](./routes_agent.md), [routes_hg](./routes_hg.md), [routes_ui](./routes_ui.md), [series_glossary](./series_glossary.md), [split_parts](./split_parts.md), [translate](./translate.md)
- **Được dùng bởi:** [http_routes.routes_agent](./http_routes.routes_agent.md), [http_routes.routes_hg](./http_routes.routes_hg.md), [routes_agent](./routes_agent.md), [routes_hg](./routes_hg.md), [scripts.check_batch3](./scripts.check_batch3.md), [scripts.check_batch4](./scripts.check_batch4.md), [scripts.check_batch5](./scripts.check_batch5.md)
- **Được nhắc tên file `.py` (subprocess/script) bởi:** [agent_core](./agent_core.md), [agent_feeder](./agent_feeder.md), [agents.agent_core](./agents.agent_core.md), [agents.agent_feeder](./agents.agent_feeder.md), [app_desktop](./app_desktop.md), [http_routes.routes_agent](./http_routes.routes_agent.md), [http_routes.routes_films](./http_routes.routes_films.md), [http_routes.routes_hg](./http_routes.routes_hg.md), [http_routes.routes_ui](./http_routes.routes_ui.md), [pineline.server.__init__](./pineline.server.__init__.md), [pineline.server.routes.__init__](./pineline.server.routes.__init__.md), [pineline.server.routes.assets](./pineline.server.routes.assets.md), [pineline.server.routes.fs](./pineline.server.routes.fs.md), [pineline.server.routes.jobs](./pineline.server.routes.jobs.md), [pineline.server.routes.queue](./pineline.server.routes.queue.md), [restart_server](./restart_server.md), [routes_agent](./routes_agent.md), [routes_films](./routes_films.md), [routes_hg](./routes_hg.md), [routes_ui](./routes_ui.md), [scripts.check_batch1](./scripts.check_batch1.md), [scripts.check_batch2](./scripts.check_batch2.md), [scripts.check_batch3](./scripts.check_batch3.md), [scripts.check_batch4](./scripts.check_batch4.md), [scripts.tree_audit](./scripts.tree_audit.md), [tools.migrate_work](./tools.migrate_work.md)
- **Test:** `tests/test_hardsub_blur_toggle.py`, `tests/test_layout_paths.py`, `tests/test_queue_jobs_api.py`, `tests/test_queue_run_one.py`, `tests/test_server_split.py`, `tests/test_source_link.py`, `tests/test_translate_force_default.py`
- **Thư viện ngoài:** `agent_name_pass`, `agent_pronoun_pass`, `agent_watch`, `asr`, `asr_hybrid_progress`, `asr_spam`, `assemble`, `clone_tts`, `context_studio`, `download`, `fastapi`, `faster_whisper`, `hardsub_asr`, `huggingface_hub`, `manifest`, `ocr`, `playlist`, `psutil`, `pydantic`, `render_fx`, `separate`, `subs`, `translate_alts`, `uvicorn`, `vram`

```mermaid
flowchart LR
  server[[server]]
  http_routes_routes_agent[http_routes.routes_agent] --> server
  http_routes_routes_hg[http_routes.routes_hg] --> server
  routes_agent[routes_agent] --> server
  routes_hg[routes_hg] --> server
  scripts_check_batch3[scripts.check_batch3] --> server
  scripts_check_batch4[scripts.check_batch4] --> server
  scripts_check_batch5[scripts.check_batch5] --> server
  server --> agent_brain[agent_brain]
  server --> agent_qa_gate[agent_qa_gate]
  server --> agent_quality[agent_quality]
  server --> auto_publisher[auto_publisher]
  server --> batch_config[batch_config]
  server --> config[config]
  server --> hg_ui_ctx[hg_ui_ctx]
  server --> hongguo_bridge[hongguo_bridge]
  server --> job_queue[job_queue]
  server --> llm[llm]
  server --> render[render]
  server --> routes_agent[routes_agent]
  server --> routes_hg[routes_hg]
  server --> routes_ui[routes_ui]
  server --> series_glossary[series_glossary]
```

### API routes (68)

| Method | Path | Handler | Dòng |
|---|---|---|---:|
| POST | `/api/agent/brain/tick` | `api_agent_brain_tick` | 6557 |
| GET | `/api/brand-logos` | `list_brand_logos` | 5539 |
| POST | `/api/clone-voice` | `clone_voice` | 5666 |
| GET | `/api/cookies` | `cookies_status` | 5180 |
| POST | `/api/cookies` | `import_cookies` | 5206 |
| GET | `/api/frames` | `list_frames` | 5529 |
| GET | `/api/fs/list-dirs` | `api_fs_list_dirs` | 2995 |
| POST | `/api/fs/pick-dir` | `api_fs_pick_dir` | 3049 |
| POST | `/api/fs/pick-dirs` | `api_fs_pick_dirs` | 3123 |
| GET | `/api/jobs` | `list_jobs` | 5252 |
| POST | `/api/jobs` | `create_job` | 2441 |
| POST | `/api/jobs/group` | `jobs_group` | 2532 |
| POST | `/api/jobs/local` | `create_local_job_upload` | 3189 |
| POST | `/api/jobs/local-batch` | `create_local_job_batch` | 2912 |
| POST | `/api/jobs/local-path` | `create_local_job_path` | 2841 |
| DELETE | `/api/jobs/{job_id}` | `delete_job` | 6329 |
| GET | `/api/jobs/{job_id}` | `job_detail` | 5266 |
| POST | `/api/jobs/{job_id}/apply-alt` | `apply_alt_pick` | 5055 |
| POST | `/api/jobs/{job_id}/asr-engine` | `set_asr_engine` | 4515 |
| POST | `/api/jobs/{job_id}/asr-select` | `select_asr_source` | 4831 |
| GET | `/api/jobs/{job_id}/asr-sources` | `list_asr_sources` | 4813 |
| POST | `/api/jobs/{job_id}/assemble` | `assemble_job` | 6182 |
| DELETE | `/api/jobs/{job_id}/audio` | `delete_audio` | 6014 |
| POST | `/api/jobs/{job_id}/audio` | `upload_audio` | 5980 |
| GET | `/api/jobs/{job_id}/context-studio` | `get_context_studio` | 4919 |
| POST | `/api/jobs/{job_id}/context-studio` | `run_context_studio_api` | 4975 |
| GET | `/api/jobs/{job_id}/file/{path:path}` | `job_file` | 6276 |
| GET | `/api/jobs/{job_id}/hardsub-asr` | `get_hardsub_asr` | 5144 |
| POST | `/api/jobs/{job_id}/hardsub-asr` | `run_hardsub_asr_api` | 5114 |
| POST | `/api/jobs/{job_id}/mark-done` | `mark_job_done` | 3933 |
| POST | `/api/jobs/{job_id}/merge-parts` | `api_merge_job_parts` | 6237 |
| POST | `/api/jobs/{job_id}/mux` | `mux_job` | 6147 |
| POST | `/api/jobs/{job_id}/reveal` | `reveal_job` | 6248 |
| POST | `/api/jobs/{job_id}/run-all` | `run_all` | 4196 |
| POST | `/api/jobs/{job_id}/run/{stage}` | `run_stage` | 3849 |
| POST | `/api/jobs/{job_id}/script-clean-spam` | `clean_script_spam` | 4142 |
| POST | `/api/jobs/{job_id}/script-line` | `edit_script_line` | 4038 |
| POST | `/api/jobs/{job_id}/source` | `upload_source` | 5902 |
| POST | `/api/jobs/{job_id}/source-path` | `import_source_path` | 5940 |
| POST | `/api/jobs/{job_id}/split-parts` | `api_split_job_parts` | 6226 |
| GET | `/api/jobs/{job_id}/split-plan` | `get_split_plan` | 6204 |
| GET | `/api/jobs/{job_id}/srt/{lang}` | `job_srt` | 5867 |
| POST | `/api/jobs/{job_id}/start` | `start_job` | 3227 |
| POST | `/api/jobs/{job_id}/stop` | `stop_job` | 3912 |
| POST | `/api/jobs/{job_id}/translate` | `retranslate_job` | 6075 |
| GET | `/api/jobs/{job_id}/translate-alts` | `get_translate_alts` | 5010 |
| POST | `/api/jobs/{job_id}/translate-alts` | `run_translate_alts_api` | 5029 |
| POST | `/api/jobs/{job_id}/translate-fill` | `translate_fill` | 3991 |
| POST | `/api/jobs/{job_id}/tts` | `regen_tts` | 5756 |
| POST | `/api/jobs/{job_id}/tts-clip` | `regen_clip` | 5850 |
| POST | `/api/jobs/{job_id}/tts-voice` | `set_tts_voice` | 4181 |
| GET | `/api/jobs/{job_id}/tts-wav-ok` | `tts_wav_ok` | 5740 |
| GET|HEAD | `/api/jobs/{job_id}/video` | `job_video` | 5437 |
| GET | `/api/llm/models` | `get_available_llm_models` | 6571 |
| GET | `/api/models` | `get_available_llm_models` | 6571 |
| POST | `/api/queue/group` | `jobs_group` | 2532 |
| GET | `/api/queue/jobs` | `api_queue_jobs_state` | 2803 |
| POST | `/api/queue/jobs` | `api_queue_jobs_add` | 2648 |
| POST | `/api/queue/jobs/clear` | `api_queue_jobs_clear` | 2836 |
| POST | `/api/queue/jobs/group` | `api_queue_jobs_add_group` | 2665 |
| POST | `/api/queue/jobs/move` | `api_queue_jobs_move` | 2774 |
| POST | `/api/queue/jobs/opts` | `api_queue_jobs_opts` | 2681 |
| POST | `/api/queue/jobs/remove` | `api_queue_jobs_remove` | 2702 |
| POST | `/api/queue/jobs/reorder` | `api_queue_jobs_reorder` | 2790 |
| POST | `/api/queue/jobs/sort` | `api_queue_jobs_sort` | 2765 |
| POST | `/api/queue/jobs/stop` | `api_queue_jobs_stop` | 2831 |
| GET | `/api/voice-sample` | `voice_sample` | 5699 |
| GET | `/api/voices` | `list_voices` | 5521 |

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| **class `_Stopped`** | 721 | 0 method | | Người dùng bấm Dừng — không phải lỗi. |
| **class `NewJob`** | 1167 | 0 method | |  |
| **class `LocalJobIn`** | 1173 | 0 method | | Tạo job từ video local — không cần URL. |
| **class `LocalBatchIn`** | 1184 | 0 method | | Import nhiều path (file và/hoặc folder), 1 dòng = 1 path. |
| **class `HgSubmitIn`** | 1194 | 0 method | |  |
| **class `HgMergeIn`** | 1201 | 0 method | |  |
| **class `JobGroupReq`** | 1207 | 0 method | | Gom / sửa nhóm series trên hàng chờ. |
| **class `HgBaseIn`** | 1217 | 0 method | |  |
| **class `TTSReq`** | 1221 | 0 method | |  |
| **class `ClipReq`** | 1228 | 0 method | |  |
| **class `MuxReq`** | 1234 | 0 method | |  |
| **class `TranslateReq`** | 1259 | 0 method | |  |
| **class `ScriptLineEdit`** | 1269 | 0 method | | Sửa tay 1 câu trong script.json (zh và/hoặc vi). |
| **class `TTSVoiceReq`** | 1276 | 0 method | |  |
| **class `RunAllReq`** | 1282 | 0 method | |  |
| **class `JobQueueReq`** | 1310 | 0 method | |  |
| **class `JobQueueGroupReq`** | 1316 | 0 method | | Enqueue cả series theo group_id (sort group_index). |
| **class `JobQueueRemoveReq`** | 1322 | 0 method | |  |
| **class `AgentChatReq`** | 1326 | 0 method | | Pineline V2 — chat với AI Agent nhúng. |
| **class `AgentConfirmReq`** | 1336 | 0 method | |  |
| **class `AsrEngineReq`** | 1341 | 0 method | |  |
| **class `AsrSelectReq`** | 1345 | 0 method | | Chọn file ASR sidecar → promote thành asr.json (vd asr.fun_nano.json). |
| **class `ContextStudioReq`** | 1350 | 0 method | | PRE-SCAN Context Studio trước dịch. |
| **class `TranslateAltsReq`** | 1356 | 0 method | | Quét câu → phương án dịch tối ưu (ngữ cảnh + văn phong). |
| **class `ApplyAltReq`** | 1363 | 0 method | |  |
| **class `MarkDoneReq`** | 1368 | 0 method | |  |
| **class `HardsubAsrReq`** | 5106 | 0 method | |  |
| **class `SourcePathIn`** | 5896 | 0 method | |  |
| `_mux_output_ok` | 93 | 6 | `work_dir, min_bytes` |  |
| `_part_pipeline_complete` | 101 | 19 | `work_dir` | Part đã mux + output đủ lớn và không bị đánh stale → không chạy lại pipeline. |
| `_ensure_parent_mux_merged_done` | 122 | 25 | `work_dir, n_parts` | Heal UI parent: đã có Full/merged mà mux còn running@80%. |
| `_parent_full_output_ok` | 149 | 9 | `work_dir, sub_ids` |  |
| `_all_split_parts_complete` | 160 | 14 | `parent_id` | True nếu parent có sub_job_ids và mọi part đã mux/output xong. |
| `_queue_split_parent_merge_if_ready` | 176 | 89 | `parent_id, reason` | Parts đã xong mà parent chưa Full (worker auto-split chết/restart) → xếp ghép nền. |
| `_notify_parent_after_part_done` | 267 | 9 | `part_job_id` | Part mux xong → nếu mọi part xong thì xếp merge về job gốc. |
| `_split_parent_id` | 278 | 5 | `job_id` | d693…_p03 → d693… ; job thường → None. |
| `_job_any_busy` | 285 | 7 | `job_id` | Trả tên stage đang claim, hoặc None. |
| `_job_lineage_busy` | 294 | 15 | `job_id` | Busy của job hoặc parent auto-split (part chạy dưới claim của parent). |
| `_claim_stage` | 311 | 7 | `job_id, stage` | Giữ chỗ trước khi submit thread — chống bấm 2-3 lần tạo nhiều task. |
| `_release_stage` | 320 | 5 | `job_id, stage` |  |
| `_busy_response` | 327 | 9 | `job_id, work_dir` | 409 nếu job đang có claim hoặc stage 'running' trong manifest, ngược lại None. |
| `_submit_claimed` | 338 | 17 | `executor, job_id, stage, fn, *args, **kwargs` | Claim (job, stage) rồi submit; nhả claim khi xong. Trả 409 nếu đã có claim. |
| `_manifest_running` | 357 | 10 | `work_dir` | Stage đang 'running' trong manifest (nếu có). |
| `_job_proc_alive` | 369 | 6 | `job_id` | True nếu còn subprocess engine/ffmpeg đăng ký cho job. |
| `_path_key` | 377 | 10 | `p` | Khoá so đường dẫn: work là junction → D:, psutil.cwd() trả đường Z: chưa resolve. |
| `_json_rows` | 389 | 6 | `p` |  |
| `_stage_complete_on_disk` | 397 | 26 | `work_dir, stage` | Artifact ĐỦ (không phải bản dở sau Dừng/crash) — điều kiện để tự nâng stage lên done. |
| `_stage_has_artifact` | 425 | 22 | `work_dir, stage` | Artifact đĩa đủ để coi stage đã xong (dùng heal stale running). |
| `_heal_stale_running` | 449 | 106 | `work_dir` | Sửa stage status=running mồ côi (kill/crash/skip không mark_done). |
| `_next_incomplete_stage` | 557 | 8 | `work_dir` | Bước WIRED đầu tiên chưa done (để mark_running đúng — không ép lại ASR). |
| `_run_engine` | 567 | 74 | `script, work_dir, *args` | Chạy engine NẶNG (ASR/TTS) ở TIẾN TRÌNH RIÊNG. |
| `_iter_job_engine_procs` | 651 | 41 | `job_id, script_name` | Quét toàn hệ thống process Python đang chạy engine cho job_id (kể cả orphan). |
| `_kill_job_engine_procs` | 694 | 13 | `job_id, script_name, exclude_pid` | Kill process engine trùng job (system-wide). Trả số process đã kill. |
| `_noisy_log` | 713 | 6 | `line` | Lọc log rác TTS (ref_text dài, tqdm...). Giữ gen_text + [ok]/[tts]/lỗi. |
| `_kill_job_children` | 725 | 73 | `job_id` | Kill MỌI tiến trình liên quan job (asr/clone_tts/demucs/ffmpeg/aria2c), |
| `_stop_job` | 800 | 83 | `job_id` | Dừng mọi việc đang chạy của 1 job + đưa stage 'running' về 'pending'. |
| `_clear_stop` | 885 | 12 | `job_id` | Xoá cờ Stop in-memory + file .stop (cả WORK_ROOT lẫn D:\PinelineV2_work). |
| `_check_stopped` | 899 | 11 | `job_id` | True nếu user bấm Dừng (in-memory hoặc file .stop). |
| `_stage_artifact_payload` | 918 | 58 | `work_dir, stage` | Nếu đĩa đã có kết quả bước → payload để mark_done. None = chưa có artifact. |
| `_heal_stages_from_disk` | 978 | 20 | `m` | Misclick/Dừng giữa chừng: file đã ĐỦ mà status còn pending/failed → đánh done. |
| `_force_mark_stage` | 1000 | 15 | `m, stage, require_artifact` | Đánh dấu 1 bước done ngay (không chạy lại). |
| `_url_host` | 1030 | 6 | `v` |  |
| async `_local_only_guard` | 1039 | 14 | `request, call_next` | Chỉ phục vụ máy này: Host lạ = DNS rebinding; Origin/Referer lạ trên /api = trang web |
| async `_quiet_conn_reset` | 1056 | 14 | `` | Trên Windows, khi client (UI poll) đóng kết nối đột ngột giữa request, event |
| `_reset_stale_running` | 1073 | 38 | `` | Khi server khởi động, KHÔNG có thread nào đang chạy. Vậy mọi stage còn ghi |
| `_start_queue_worker` | 1114 | 5 | `` | Worker hàng đợi chỉ chạy SAU khi reset stage treo + kill engine orphan; chạy lúc import |
| `_resume_hg_merge` | 1122 | 10 | `` | Hàng đợi gộp Hongguo nạp lại từ work/logs/hg_merge_state.json → chạy tiếp nếu Hongguo đang mở |
| `_startup_fix_tts` | 1134 | 31 | `work_dir, st` | Khôi phục voice/progress TTS sau crash — không mất cấu hình. |
| `_process_gpu` | 1374 | 25 | `job_id, target` | Phần NẶNG (GPU/LLM): ASR -> Dịch. Chạy ở hàng đợi _gpu (tuần tự). |
| `run_pipeline` | 1401 | 16 | `job_id, url, target, cookies_from_browser` | TẢI (hàng đợi _dl, song song). Tải xong -> đẩy ASR+Dịch sang hàng đợi _gpu |
| `_check_and_run_auto_split_parts` | 1419 | 145 ⚠️ | `job_id, target, audio_mode, voice_vol, orig_vol, use_ocr, fit, reso…` | Tự động phát hiện video dài (>= 3.0h): |
| `_auto_pipeline` | 1566 | 49 | `job_id, audio_mode, voice_vol, orig_vol, use_ocr, fit, resolution, …` | 1-CLICK (chạy ở hàng _dl): tải (nếu cần) -> đẩy phần GPU sang hàng _gpu. |
| `_run_requested_review` | 1617 | 59 | `wd, target` | Rà soát do Agent/user yêu cầu (manifest.agent.review_request): rà tên nhân vật theo bảng |
| `_save_series_glossary` | 1678 | 9 | `wd` |  |
| `_auto_gpu` | 1689 | 305 ⚠️ | `job_id, target, audio_mode, voice_vol, orig_vol, use_ocr, fit, reso…` | Phần GPU của 1-click (hàng _gpu, tuần tự): ASR -> Dịch -> TTS -> [Tách nền] |
| `_has_cjk` | 2002 | 2 | `s` |  |
| `_extract_vi_title` | 2006 | 28 | `raw` | Bóc tách tên tiếng Việt từ response LLM có thể dài dòng / giải thích. |
| `_translate_title` | 2036 | 45 | `job_id` | Dịch tiêu đề gốc (Trung) sang tiếng Việt bằng gemma4 local, lưu title_vi. |
| `_maybe_translate_title` | 2083 | 13 | `job_id, title` | Kích hoạt dịch tiêu đề (lazy) nếu còn tiếng Trung. Bỏ qua khi ASR/TTS đang |
| `_asr_labels_from_source` | 2101 | 16 | `src_name` | Suy engine + model từ tên file sidecar (nguồn sự thật). |
| `_sync_asr_labels` | 2119 | 36 | `work_dir, asr` | Ép engine/model khớp asr_source (+ n_segments từ asr.json nếu có). |
| `_apply_hybrid_asr_overlay` | 2157 | 23 | `work_dir, result` | Hybrid FA: UI đọc stages.asr — overlay % từ asr.*.progress.json nếu sidecar đang chạy. |
| `read_job` | 2182 | 131 ⚠️ | `work_dir` |  |
| `_create` | 2325 | 14 | `url, target, cookies_from_browser, group` | Tạo 1 job ở trạng thái CHỜ (chưa chạy). Người dùng bấm ▶ Bắt đầu mới chạy. |
| `_job_id_local` | 2341 | 2 | `key` |  |
| `_create_local_shell` | 2345 | 20 | `target, job_key, title, orig_path, group` | Tạo job local (không URL). job_key ổn định theo path để resume cùng file. |
| `_list_local_videos` | 2367 | 24 | `root, recursive, limit` | Liệt kê file video trong folder (sắp tên tự nhiên). |
| `_import_local_video_file` | 2393 | 45 | `src, target, move, title, group` | Copy/move 1 file video → job local. Trả dict ok/job_id hoặc error. |
| `create_job` | 2441 | 24 | `job` | Thêm link -> tạo job CHỜ. 1 link ra NHIỀU video (multi-P/playlist) -> gom |
| `_patch_job_group` | 2467 | 28 | `job_id, group_id, group_title, group_index, group_total, part_title` | Ghi/xoá group_* trong manifest.request. Trả False nếu job không tồn tại. |
| `_renumber_group` | 2497 | 31 | `group_id, title` | Sắp lại group_index 1..N theo index cũ (hoặc created). Trả job_ids còn trong nhóm. |
| `jobs_group` | 2532 | 113 | `body` | Gom job thành series / thêm vào nhóm / đổi tên / tách. |
| `api_queue_jobs_add` | 2648 | 14 | `req` |  |
| `api_queue_jobs_add_group` | 2665 | 13 | `req` |  |
| `api_queue_jobs_opts` | 2681 | 18 | `body` | {"opts_by_job": {job_id: opts}} — đổi opts job đang chờ tại chỗ (nguyên tử, giữ thứ tự). |
| `api_queue_jobs_remove` | 2702 | 5 | `req` |  |
| `_queue_current_detail` | 2709 | 53 | `job_id` | Stage/progress/ETA thô cho dashboard queue. |
| `api_queue_jobs_sort` | 2765 | 6 | `body` |  |
| `api_queue_jobs_move` | 2774 | 13 | `body` |  |
| `api_queue_jobs_reorder` | 2790 | 10 | `body` |  |
| `api_queue_jobs_state` | 2803 | 25 | `` |  |
| `api_queue_jobs_stop` | 2831 | 2 | `` |  |
| `api_queue_jobs_clear` | 2836 | 2 | `` |  |
| `create_local_job_path` | 2841 | 68 | `body` | Tạo job từ file HOẶC folder video local. |
| `create_local_job_batch` | 2912 | 80 | `body` | Import nhiều path (file + folder). Mỗi folder → 1 group riêng. |
| `api_fs_list_dirs` | 2995 | 51 | `path, count_videos, only_with_video` | Liệt kê folder con trực tiếp (1 cấp) để tick chọn import. |
| `api_fs_pick_dir` | 3049 | 71 | `title, initial` | Mở hộp thoại Windows chọn folder (native). Chạy process riêng để không kẹt uvicorn. |
| `api_fs_pick_dirs` | 3123 | 63 | `initial` | Hộp thoại chọn NHIỀU folder cùng lúc (Ctrl/Shift). Trả paths[]. |
| async `create_local_job_upload` | 3189 | 35 | `file, target` | Tạo job từ upload video (không cần link). File lớn nên dùng /local-path. |
| `start_job` | 3227 | 73 | `job_id` | Chạy tự động các bước còn lại (download -> asr -> dịch) cho 1 job. |
| `_run_stage` | 3302 | 105 | `job_id, stage, target, force, voice, speed, engine` | Chạy ĐÚNG 1 bước (người dùng tự chọn). download -> hàng _dl; còn lại -> _gpu. |
| `_save_tts_voice` | 3409 | 3 | `work_dir, voice` | Lưu giọng vào manifest + sidecar — KHÔNG được wipe stages khác. |
| `_save_tts_speed` | 3414 | 2 | `work_dir, speed` |  |
| `_save_tts_engine` | 3418 | 2 | `work_dir, engine` |  |
| `_patch_tts_fields` | 3422 | 41 | `work_dir, **fields` | Ghi field TTS an toàn: đọc đĩa trực tiếp, merge, atomic write. Không dùng |
| `_job_cfg_opts` | 3465 | 9 | `work_dir` | Gộp opts + queue_opts (queue_opts thắng) — dùng khi resolve voice/speed/engine. |
| `_resolve_voice` | 3476 | 24 | `work_dir, voice` | Giọng: arg → stages.tts → tts_config → queue_opts/opts → list[0] (cuối cùng). |
| `_resolve_queue_voice` | 3502 | 22 | `work_dir, voice` | Queue chỉ dùng giọng được chọn rõ ràng hoặc đã lưu cho chính job. |
| `_resolve_speed` | 3526 | 23 | `work_dir, speed` |  |
| `_asr_script` | 3567 | 2 | `engine` |  |
| `_patch_asr_fields` | 3571 | 31 | `work_dir, **fields` | Ghi field ASR an toàn (không wipe stages khác). |
| `_save_asr_engine` | 3604 | 27 | `work_dir, engine` | Lưu engine. Nếu đã có sidecar tương ứng → promote luôn (tránh lệch nhãn/nội dung). |
| `_resolve_asr_engine` | 3633 | 10 | `work_dir, engine` |  |
| `_resolve_tts_engine` | 3645 | 23 | `work_dir, engine` |  |
| `_do_tts` | 3670 | 21 | `work_dir, voice, speed, engine, force` | Chạy TTS clone tiếng Việt (vieneu/omnivoice). Điều phối worker venv riêng |
| `_do_render` | 3693 | 153 ⚠️ | `work_dir, force, audio_mode, voice_vol, orig_vol, add_sub, fit, res…` | Ghép giọng (assemble nếu chưa) rồi render video localize (che+sub+trộn nền). |
| `run_stage` | 3849 | 60 | `job_id, stage, force, voice, speed, engine` | Chạy riêng 1 bước của job (chủ động chọn bước nào làm). Kiểm tra điều kiện |
| `stop_job` | 3912 | 18 | `job_id` | DỪNG mọi việc đang chạy của job (kill subprocess asr/tts/demucs/ffmpeg/aria2c |
| `mark_job_done` | 3933 | 55 | `job_id, body` | Đánh dấu bước (hoặc cả job) = done NGAY — không chạy lại / không chờ. |
| `translate_fill` | 3991 | 44 | `job_id` | VÁ câu trống ở bước Dịch: chạy lại dịch với LÔ NHỎ (25) — run_translate tự |
| `edit_script_line` | 4038 | 101 | `job_id, req` | Sửa tay zh và/hoặc vi: ghi script.json + regen SRT. Không đụng TTS clip |
| `clean_script_spam` | 4142 | 36 | `job_id` | Rút chuỗi 哈/呃 spam trong script.json (ASR lỗi) + prefill vi trivial nếu trống. |
| `set_tts_voice` | 4181 | 12 | `job_id, req` | Lưu giọng TTS đã chọn vào manifest (để nút Chạy / tự động dùng đúng giọng). |
| `run_all` | 4196 | 78 | `job_id, req` | 1-CLICK: chạy tự động toàn bộ pipeline từ bước còn thiếu tới hết. |
| `_queue_run_one` | 4276 | 236 ⚠️ | `job_id, opts` | Run one queued job synchronously through mux and return status + detail. |
| `set_asr_engine` | 4515 | 9 | `job_id, req` | Lưu engine ASR (hybrid_fa / fun_asr_nano / …) cho job. |
| `_list_asr_sources` | 4544 | 51 | `work_dir` | Liệt kê asr.json + asr.*.json có dữ liệu (bỏ progress/meta/chars/bak). |
| `_promote_asr_source` | 4597 | 119 | `work_dir, source` | Copy sidecar → asr.json + sub.zh.srt; backup asr.json cũ. |
| `_invalidate_translate_for_asr` | 4718 | 43 | `work_dir, asr_source, n_asr` | Backup script + đánh dấu translate lệch khi đổi asr_source. |
| `_translate_asr_sync_info` | 4763 | 47 | `work_dir` | UI: script có khớp asr.json không? |
| `list_asr_sources` | 4813 | 15 | `job_id` | Danh sách file ASR có sẵn để chọn (Nano / FireRed / …). |
| `select_asr_source` | 4831 | 13 | `job_id, req` | Promote file ASR (vd asr.fun_nano.json) → asr.json + sub.zh.srt. |
| `_context_studio_input` | 4846 | 7 | `work_dir` | Ưu tiên asr.json → sub.zh.srt. |
| `_do_context_studio` | 4855 | 61 | `work_dir, use_llm` | Chạy PRE-SCAN → ghi pack vào work_dir. |
| `get_context_studio` | 4919 | 53 | `job_id` | Xem pack Context Studio (summary + style_lock + characters). |
| `run_context_studio_api` | 4975 | 32 | `job_id, req` | Chạy Context Studio PRE-SCAN → glossary/style_lock/qa_flags trong work/<job>. |
| `get_translate_alts` | 5010 | 16 | `job_id` | Pack analyze checklist + danh sách câu đa nghĩa (vi_alts.json). |
| `run_translate_alts_api` | 5029 | 23 | `job_id, req` | Quét câu đa nghĩa theo chunk + pack analyze → vi_alts.json. |
| `apply_alt_pick` | 5055 | 49 | `job_id, req` | Chốt một phương án alts[pick] → vi (+ regen SRT). |
| `run_hardsub_asr_api` | 5114 | 27 | `job_id, req` | OCR hardsub → rà/sửa chữ ZH trên ASR (giữ timing). Không thay bước dịch. |
| `get_hardsub_asr` | 5144 | 15 | `job_id` |  |
| `_cookie_info` | 5165 | 12 | `path` | Đếm cookie + kiểm định dạng Netscape của 1 file cookie. |
| `cookies_status` | 5180 | 3 | `` |  |
| `_header_to_netscape` | 5189 | 14 | `header, plat` | Chuyển chuỗi header 'name=value; name2=value2' (copy từ DevTools) -> Netscape. |
| async `import_cookies` | 5206 | 43 | `file, text, platform` | Nhập cookies bằng FILE (.txt Netscape từ extension) HOẶC dán TEXT vào popup. |
| `list_jobs` | 5252 | 11 | `` |  |
| `job_detail` | 5266 | 15 | `job_id` |  |
| `_audio_dur` | 5287 | 11 | `path` | Đo độ dài audio (giây) bằng ffprobe. Lỗi -> 0. |
| `_probe_video` | 5300 | 22 | `path` | Rút width/height/duration/vcodec bằng ffprobe. Lỗi -> {}. |
| `_clear_job_sources` | 5324 | 10 | `work_dir` | Xoá source.* / mảnh .part cũ trước khi import. |
| `_link_or_copy` | 5336 | 9 | `src, dest` | Hard link nếu được (cùng ổ — không tốn thêm dung lượng); khác ổ / FS không hỗ trợ mới copy. |
| `_direct_source_roots` | 5347 | 3 | `` |  |
| `_is_direct_source` | 5352 | 13 | `src` | File trong thư viện (SOURCE_DIRECT_ROOTS) → job đọc thẳng video_path, không đặt file vào job. |
| `_place_source` | 5367 | 11 | `src, work_dir, move` | Trả (đường dẫn video job dùng, cách đặt: direct/move/link/copy). |
| `_finalize_imported_source` | 5380 | 42 | `work_dir, dest, orig_name, source_kind, source_mode` | Ghi meta + mark download done. `dest` có thể nằm ngoài job (source_mode=direct: file thư viện). |
| `_find_video` | 5424 | 10 | `work_dir` | Tìm file video đã tải: ưu tiên video_path trong manifest, fallback glob. |
| `job_video` | 5437 | 12 | `job_id` | Stream video đã tải để preview. FileResponse tự xử lý Range -> tua được. |
| `_write_srt` | 5459 | 54 | `work_dir, lang` | Sinh .srt từ json nguồn, ghi ra sub.<lang>.srt. Trả (path, nội dung) hoặc |
| `_clone_voice_list` | 5515 | 3 | `` | Giọng clone dùng chung cho cả 2 engine (registry voices/f5_voices.json). |
| `list_voices` | 5521 | 5 | `` | Giọng clone (ref audio + lời) dùng chung — cả vieneu lẫn omnivoice đều |
| `list_frames` | 5529 | 7 | `` | Danh sách PNG khung trong assets/overlays/frames. |
| `list_brand_logos` | 5539 | 7 | `` | Logo kênh (assets/overlays/logos hoặc brand). |
| `_ref_asr_enabled` | 5555 | 20 | `` | ASR mẫu: mặc định tắt nếu chưa có model (tránh treo tải Whisper 2GB lúc Thêm giọng). |
| `_probe_audio_dur` | 5577 | 10 | `path` |  |
| `_transcribe_ref` | 5589 | 12 | `path` | Lấy transcript của clip mẫu (F5 cần ref_text). Model medium int8 nhẹ VRAM. |
| `_prep_ref` | 5603 | 60 | `raw, max_dur` | Chuẩn hoá clip mẫu: cắt ≤max_dur, xuất wav 24k mono. Trả (wav, ref_text, dur). |
| `clone_voice` | 5666 | 25 | `name, file` | Clone 1 giọng từ file mẫu (3-8s). Đăng ký vào registry chung (VieNeu/OmniVoice). |
| `voice_sample` | 5699 | 38 | `engine, voice, speed` | Đọc câu mẫu bằng engine+giọng (+ tốc độ) để nghe thử. Cache trên đĩa. |
| `tts_wav_ok` | 5740 | 13 | `job_id` | Danh sách index seg_*.wav còn trên đĩa (size OK) — UI khỏi báo thiếu oan khi chưa có tts.json. |
| `regen_tts` | 5756 | 91 | `job_id, req` | Lồng tiếng: mặc định RESUME (chỉ đọc câu thiếu). force=true -> đọc lại toàn bộ. |
| `regen_clip` | 5850 | 14 | `job_id, req` | Đọc lại DUY NHẤT 1 câu (index i) khi clip đó lỗi. Nhanh, không đụng câu khác. |
| `job_srt` | 5867 | 13 | `job_id, lang` | Sinh .srt từ asr.json (zh) / script.json (vi), ghi ra file trong job rồi |
| `_reveal_path` | 5882 | 12 | `target` | Mở trình quản lý file, bôi sẵn đúng file (nếu target là file) hoặc mở thư mục. |
| async `upload_source` | 5902 | 35 | `job_id, file` | Import source video qua upload (stream, không nhét cả file vào RAM). |
| `import_source_path` | 5940 | 37 | `job_id, body` | Import source từ đường dẫn local (cùng máy server) — phù hợp file multi-GB. |
| async `upload_audio` | 5980 | 31 | `job_id, file` | Nhập 1 file audio lồng tiếng LÀM SẴN ở ngoài (từ SRT) để dùng cho mux. |
| `delete_audio` | 6014 | 14 | `job_id` | Bỏ audio ngoài đã nhập -> quay lại dùng TTS nội bộ. |
| `_translate_batch_size` | 6030 | 10 | `` | Cỡ lô dịch — đọc TRANSLATE_BATCH (mặc định 20). Không hardcode 100. |
| `_translate_flow` | 6042 | 30 | `work_dir, target, model, review_model, review_only, mode, force` | Luồng dịch: (tùy chọn) DỊCH NHÁP rồi (tùy chọn) SOÁT lại lượt 2. |
| `retranslate_job` | 6075 | 69 | `job_id, req` | Dịch job: 1 lượt, HOẶC 2 lượt (nháp + soát), HOẶC chỉ soát bản có sẵn. |
| `mux_job` | 6147 | 32 | `job_id, req` | Render video localize -> output.mp4 (che watermark/hardsub + sub Việt + OCR |
| `assemble_job` | 6182 | 19 | `job_id, fit, max_speed` | Ghép clip TTS thành 1 track. |
| `get_split_plan` | 6204 | 19 | `job_id, target_hours` | Xem trước kế hoạch chia part thông minh cho video dài (trước khi chia). |
| `api_split_job_parts` | 6226 | 8 | `job_id, target_hours` | Chia video dài thành các sub-jobs (Part 1, Part 2...) để chạy pipeline độc lập chống lệch time. |
| `api_merge_job_parts` | 6237 | 8 | `job_id` | Ghép các sub-jobs đã render hoàn chỉnh thành bản Full output_full.mp4 (lossless concat 30s). |
| `reveal_job` | 6248 | 25 | `job_id, file` | Mở thư mục job trong Explorer, chọn sẵn 1 file. Không truyền file -> chọn |
| `job_file` | 6276 | 50 | `job_id, path` | Phục vụ 1 file BÊN TRONG work/<job_id>/ (asr.json, script.json, mp3...). |
| `delete_job` | 6329 | 16 | `job_id` | Xoá 1 job = xoá cả thư mục work/<job_id>/ (video, audio, manifest...). |
| `_queue_park_ready` | 6362 | 30 | `job_id` | True khi job đang park (HOLD/soát) có thể chạy tiếp TTS — không nhảy job khác. |
| async `_hg1_hg2_split` | 6495 | 29 | `request, call_next` | Tách hoàn toàn Hongguo1 / Hongguo2. |
| `_start_agent_watch` | 6527 | 10 | `` |  |
| `_start_agent_brain` | 6540 | 14 | `` | Second Brain — daemon full-silent (ops + quality + infra). |
| `api_agent_brain_tick` | 6557 | 10 | `` | Chạy 1 tick Second Brain thủ công (ops/debug). |
| `get_available_llm_models` | 6571 | 7 | `` | Trả về danh sách toàn bộ các model LLM khả dụng (llama-server :8083, Ollama, 9router). |

**Hàm dài ≥120 dòng:** `_auto_gpu` (305, L1689), `_queue_run_one` (236, L4276), `_do_render` (153, L3693), `_check_and_run_auto_split_parts` (145, L1419), `read_job` (131, L2182)

### Config / env keys (18)

`AGENT_QA_GATE`, `AUTO_REVIEW`, `DL_WORKERS`, `HF_HUB_DISABLE_SYMLINKS`, `HF_HUB_DISABLE_SYMLINKS_WARNING`, `HG_BACKEND`, `HG_HELPER_SINGLETON`, `HOST`, `JOB_WORKERS`, `PORT`, `PYTHONIOENCODING`, `REF_ASR`, `REF_ASR_DEVICE`, `REF_ASR_MODEL`, `SOURCE_DIRECT_ROOTS`, `TRANSLATE_BATCH`, `TRANSLATE_MODEL`, `VIENEU_BOOT_SEC`

**Cổng nhắc tới:** 8000

**File/artifact nhắc tới:** `.bak.json`, `_cookies.txt`, `_f5.wav`, `asr.aligned.json`, `asr.aligned_fa.json`, `asr.aligned_fix.json`, `asr.aligned_n1.json`, `asr.aligned_repaired.json`, `asr.consensus.json`, `asr.firered.json`, `asr.fun_nano.json`, `asr.fun_nano_retry.json`, `asr.hardsub.json`, `asr.json`, `asr.nano_fa.json`, `asr.paraformer_zh.json`, `asr.sensevoice.json`, `bgm.wav`, `context_pack.json`, `dub_fit.wav`, `dub_tts.wav`, `glossary.json`, `hardsub_cues.json`, `manifest.json`, `meta.json`, `no_vocals.wav`, `ocr.json`, `output.mp4`, `output.partial.mp4`, `output_full.mp4`, `qa_flags.json`, `script.display.json`, `script.json`, `script.pre_agent_review.json`, `source.mp4`, `sub.vi.srt`, `sub.zh.srt`, `tts.json`, `tts_config.json`, `vi_alts.json` … (+1)

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=205 · file_writes=23 · global_stmt=2 · pools=3 · subprocess=10 · swallow_except=72

### Lịch sử (từ docs/)

- **Fix logs (33):**
  - [Studio SOP: 1 job / ghế — ASR→NMT→Aurora∥ REVIEW→TTS→mux→Done→next](../../fixes/2026-11-11-studio-1job-pipeline.md)
  - [REVIEW CLI song song + heal làm UI mất/soát % tụt](../../fixes/2026-11-10-review-heal-parallel.md)
  - [Queue nhảy job khi còn HOLD/soát dở — mất invariant studio 1 job→output](../../fixes/2026-11-10-queue-park-held.md)
  - [Stop lúc soát vẫn nhảy TTS / job không dừng](../../fixes/2026-11-09-stop-during-review-tts.md)
  - [Dịch dừng giữa chừng → nhảy TTS với số câu dở (vd 64/398 vs ASR 2698)](../../fixes/2026-11-08-translate-partial-tts-jump.md)
  - [Auto-split: part xong mà job gốc vẫn pending (không ghép Full)](../../fixes/2026-11-08-split-parent-merge-heal.md)
  - [Restore Hongguo1 nguyên bản + tách Hongguo2](../../fixes/2026-11-08-hongguo1-restore-isolate.md)
  - [Restore Hongguo classic + tách hoàn toàn Hongguo2](../../fixes/2026-11-08-hongguo1-full-split.md)
  - [Hongguo1 kẹt «Đang tải bảng hot…»](../../fixes/2026-11-08-hongguo1-boot-stuck.md)
  - [Helper Pineline leak / lệch WinUI (spawn riêng)](../../fixes/2026-11-08-helper-singleton-winui-parity.md)
  - [Part mux hiện «Sẵn sàng» trong lúc dò hardsub OCR](../../fixes/2026-11-07-mux-heal-hardsub-ocr.md)
  - [Thêm bật/tắt che hardsub (blur)](../../fixes/2026-11-07-hardsub-blur-toggle.md)
  - [V5 split hết ổ vẫn re-encode / thiếu ENOSPC guard](../../fixes/2026-11-06-v5-enospc-port.md)
  - [Phần 6 «đang dịch» nhưng không thấy tiếng Việt (script.json 404)](../../fixes/2026-11-06-translate-stop-ghost.md)
  - [Bấm lồng tiếng / dịch xong rồi lại «force: dịch lại từ đầu»](../../fixes/2026-11-06-translate-force-wipe.md)
  - [Auto-split / ASR promote chồng luồng (parent 80% + TTS lại sau mux)](../../fixes/2026-11-05-autosplit-conflict-guards.md)
  - [V5: queue/jobs dual-route + queue_state đọc N lần](../../fixes/2026-11-04-v5-queue-ssot.md)
  - [Queue metadata từ films.db (V5) — bớt đọc manifest](../../fixes/2026-11-04-film-db-queue-meta.md)
  - [Lệch xưng hô sau dịch (Ta–Ngươi / sai self–call)](../../fixes/2026-11-02-pronoun-xung-ho.md)
  - [Video nguồn bị chép thành 2 bản (thư viện + job)](../../fixes/2026-10-07-source-duplicate-copy.md)
  - [Hongguo "Merge all": không thấy đang chạy gì, 16 series rất lâu mới ra 1](../../fixes/2026-10-07-hg-merge-queue.md)
  - [Restart hẹn giờ chết giữa chừng, server :8801 nằm chết](../../fixes/2026-10-06-restart-killed-itself.md)
  - [Đợt 7: gỡ UI cũ, tách server.py](../../fixes/2026-10-06-batch7-ui-split.md)
  - [2026-10-06 — Đợt 6 review: bảo trì (git, pytest, M3, dọn script chết)](../../fixes/2026-10-06-batch6-maintenance.md)
  - [2026-10-06 — Đợt 5 review: agent an toàn hơn](../../fixes/2026-10-06-batch5-agent-safety.md)
  - … +8 file nữa
- **Reviews:** [_atoms_core_server](../../reviews/_atoms_core_server.md), [2026-11-09-plan-file-review-style-code](../../reviews/2026-11-09-plan-file-review-style-code.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md), [2026-11-06-v5-eng-swarm](../../reviews/2026-11-06-v5-eng-swarm.md), [2026-11-06-v5-eng-swarm-translate-force](../../reviews/2026-11-06-v5-eng-swarm-translate-force.md), [2026-11-04-v5-declutter-pass2](../../reviews/2026-11-04-v5-declutter-pass2.md), [2026-11-02-v4-structure-sync](../../reviews/2026-11-02-v4-structure-sync.md), [2026-11-02-v4-structure-and-v2-port](../../reviews/2026-11-02-v4-structure-and-v2-port.md), [2026-11-02-v4-duplication-audit](../../reviews/2026-11-02-v4-duplication-audit.md)
- Nhắc trong CHANGELOG: **21** lần · DECISIONS: **9** lần

<!-- AUTO:END -->

<!-- MANUAL:START -->
## Vai trò (viết tay)

_Chưa viết. 2–4 câu: module này chịu trách nhiệm gì trong pipeline, ai gọi nó, nó KHÔNG làm gì._

## Luồng chính

_Các hàm vào (entry) → bước chính → output/side effect. Ghi tên hàm thật._

## Bất biến & hợp đồng

_Điều luôn phải đúng (vd: chỉ ghi manifest qua `Manifest.update`; 1 job / ghế). Vi phạm = bug._

## Bẫy đã biết

_Lỗi từng gặp + link `docs/fixes/...`. Những chỗ dễ sửa sai._

## Ghi chú vận hành

_Config key quan trọng, cần restart gì khi sửa (:8801 / :8802 / hot-reload), cách test._
<!-- MANUAL:END -->
