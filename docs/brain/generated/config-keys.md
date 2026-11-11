# Config & env keys

_Sinh tự động bởi `scripts/brain_build.py` lúc 2026-11-11 02:38. Đừng sửa tay — chạy lại script._


Thứ tự ưu tiên xem `config.py` (LLM keys: file thắng env; còn lại env → file → default) và `docs/ARCHITECTURE.md#config`. Bảng này chỉ cho biết **key được đọc ở đâu**.

**241 key.**

| Key | Đọc ở (số lần) |
|---|---|
| `AGENT_API_KEY` | [config](../modules/config.md) (1) |
| `AGENT_BASE_URL` | [config](../modules/config.md) (1) |
| `AGENT_BRAIN` | [agent_brain](../modules/agent_brain.md) (1) |
| `AGENT_BRAIN_LLM` | [agent_brain](../modules/agent_brain.md) (1) |
| `AGENT_BRAIN_LLM_SEC` | [agent_brain](../modules/agent_brain.md) (1) |
| `AGENT_BRAIN_LLM_STEPS` | [agent_brain](../modules/agent_brain.md) (1) |
| `AGENT_BRAIN_MODE` | [agent_brain](../modules/agent_brain.md) (2) |
| `AGENT_BRAIN_SEC` | [agent_brain](../modules/agent_brain.md) (1) |
| `AGENT_BRAIN_TELEGRAM` | [agent_brain](../modules/agent_brain.md) (1) |
| `AGENT_BRAIN_TG_SEC` | [agent_brain](../modules/agent_brain.md) (1) |
| `AGENT_FALLBACK_MODEL` | [config](../modules/config.md) (1) |
| `AGENT_MODEL` | [config](../modules/config.md) (1) |
| `AGENT_QA_GATE` | [server](../modules/server.md) (1) |
| `AGENT_TELEGRAM` | [agent_tele_cmd](../modules/agent_tele_cmd.md) (2), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md) (2), [agents.agent_watch](../modules/agents.agent_watch.md) (1), [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) (1), [restart_server](../modules/restart_server.md) (1), [tools.migrate_work](../modules/tools.migrate_work.md) (1) |
| `AGENT_TELEGRAM_STARTUP` | [agents.agent_watch](../modules/agents.agent_watch.md) (1) |
| `AGENT_TOOL_RESULT_MAX` | [agent_core](../modules/agent_core.md) (1), [agents.agent_core](../modules/agents.agent_core.md) (1) |
| `AGENT_WATCH` | [agents.agent_watch](../modules/agents.agent_watch.md) (1) |
| `AGENT_WATCH_COOLDOWN` | [agents.agent_watch](../modules/agents.agent_watch.md) (1) |
| `AGENT_WATCH_MAX_JOBS` | [agent_core](../modules/agent_core.md) (1), [agents.agent_core](../modules/agents.agent_core.md) (1), [agents.agent_watch](../modules/agents.agent_watch.md) (1), [http_routes.routes_agent](../modules/http_routes.routes_agent.md) (1), [routes_agent](../modules/routes_agent.md) (1) |
| `AGENT_WATCH_SEC` | [agents.agent_watch](../modules/agents.agent_watch.md) (1) |
| `AGENT_WATCH_SKIP_PREFIX` | [agents.agent_watch](../modules/agents.agent_watch.md) (1) |
| `ASR_FA_PAD_S` | [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md) (1), [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md) (1) |
| `ASR_VAD_CHUNK_S` | [engines.asr.fun_asr_nano](../modules/engines.asr.fun_asr_nano.md) (1) |
| `ASR_VAD_MAX_SEGMENT_S` | [engines.asr.asr_vad_utils](../modules/engines.asr.asr_vad_utils.md) (1) |
| `ASR_VAD_MAX_SINGLE_SEGMENT_MS` | [engines.asr.sensevoice_asr](../modules/engines.asr.sensevoice_asr.md) (1) |
| `ASR_VAD_MERGE_GAP_S` | [engines.asr.asr_vad_utils](../modules/engines.asr.asr_vad_utils.md) (1) |
| `ASR_VAD_OVERLAP_S` | [engines.asr.asr_vad_utils](../modules/engines.asr.asr_vad_utils.md) (1) |
| `ASR_VAD_PAD_S` | [engines.asr.asr_vad_utils](../modules/engines.asr.asr_vad_utils.md) (1) |
| `ASSEMBLE_FIT_MODE` | [engines.assemble](../modules/engines.assemble.md) (1) |
| `ASSEMBLE_MAX_SPEED` | [engines.assemble](../modules/engines.assemble.md) (1) |
| `AURORA_BASE_URL` | [agents.meta_studio](../modules/agents.meta_studio.md) (2), [config](../modules/config.md) (1) |
| `AURORA_REVIEW_MODEL` | [translate](../modules/translate.md) (1) |
| `AUTOPILOT_HOST` | [agent_tele_cmd](../modules/agent_tele_cmd.md) (1), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md) (1) |
| `AUTOPILOT_PORT` | [agent_tele_cmd](../modules/agent_tele_cmd.md) (1), [agents.agent_hongguo](../modules/agents.agent_hongguo.md) (1), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md) (1), [scripts.check_sidecar_lock](../modules/scripts.check_sidecar_lock.md) (1) |
| `AUTOPILOT_TICK_SEC` | [agent_tele_cmd](../modules/agent_tele_cmd.md) (1), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md) (1) |
| `AUTOPILOT_URL` | [agent_core](../modules/agent_core.md) (1), [agents.agent_core](../modules/agents.agent_core.md) (1) |
| `AUTO_REVIEW` | [engines.translate](../modules/engines.translate.md) (1), [server](../modules/server.md) (1), [translate](../modules/translate.md) (1) |
| `AUTO_SWITCH_PRESETS` | [engines.translate](../modules/engines.translate.md) (2), [translate](../modules/translate.md) (2) |
| `BRAIN_HANG_FIX` | [agent_hang_fix](../modules/agent_hang_fix.md) (1) |
| `BYPASS_SPEED` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `CANVA_CLIENT_ID` | [agents.canva_client](../modules/agents.canva_client.md) (1) |
| `CANVA_CLIENT_SECRET` | [agents.canva_client](../modules/agents.canva_client.md) (1) |
| `CANVA_REDIRECT_URI` | [agents.canva_client](../modules/agents.canva_client.md) (2) |
| `CENSOR_BLUR` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `CENSOR_RANGES` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `CHATGPT_ACCESS_TOKEN` | [agents.meta_studio](../modules/agents.meta_studio.md) (1), [engines.llm](../modules/engines.llm.md) (1), [llm](../modules/llm.md) (2) |
| `CHATGPT_API_KEY` | [engines.llm](../modules/engines.llm.md) (1), [llm](../modules/llm.md) (2) |
| `CHATGPT_BASE_URL` | [agents.meta_studio](../modules/agents.meta_studio.md) (2), [config](../modules/config.md) (1) |
| `CHATGPT_FORCE_TOKEN` | [engines.llm](../modules/engines.llm.md) (2), [llm](../modules/llm.md) (4) |
| `CHATGPT_MODEL` | [config](../modules/config.md) (2), [engines.llm](../modules/engines.llm.md) (1), [llm](../modules/llm.md) (2) |
| `CHATGPT_TIMEOUT` | [llm](../modules/llm.md) (3), [meta_studio](../modules/meta_studio.md) (1), [translate](../modules/translate.md) (2) |
| `CLONE_CLEANUP` | [engines.clone_tts](../modules/engines.clone_tts.md) (2) |
| `CLONE_HISHELF` | [engines.clone_tts](../modules/engines.clone_tts.md) (1) |
| `CLOUD_LLM_API_KEY` | [llm](../modules/llm.md) (1) |
| `CLOUD_LLM_BASE_URL` | [llm](../modules/llm.md) (1) |
| `DEMUCS_CHUNK_SEC` | [engines.separate](../modules/engines.separate.md) (1) |
| `DEMUCS_LONG_THRESHOLD_SEC` | [engines.separate](../modules/engines.separate.md) (1) |
| `DL_WORKERS` | [server](../modules/server.md) (1) |
| `DOWNLOAD_MAX_HEIGHT` | [engines.download](../modules/engines.download.md) (2) |
| `DOWNLOAD_PREFER_HEVC` | [engines.download](../modules/engines.download.md) (2) |
| `FALLBACK_MODEL` | [engines.translate](../modules/engines.translate.md) (1), [translate](../modules/translate.md) (1) |
| `FILMDB_SEC` | [agent_tele_cmd](../modules/agent_tele_cmd.md) (1), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md) (1) |
| `FILM_DB` | [core.film_db](../modules/core.film_db.md) (1), [film_db](../modules/film_db.md) (1) |
| `FIRERED_MODELS` | [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md) (2), [scripts.download_firered_models](../modules/scripts.download_firered_models.md) (1) |
| `FIRERED_ROOT` | [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md) (2) |
| `FIRERED_SLICE_SEC` | [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md) (1) |
| `FIRERED_USE_HALF` | [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md) (2) |
| `HANG_FIX_MODEL` | [agent_hang_fix](../modules/agent_hang_fix.md) (2) |
| `HARDSUB_BAR_ALPHA` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HARDSUB_BAR_RADIUS` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HARDSUB_BLUR` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HARDSUB_BLUR_MARGIN` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HARDSUB_BLUR_MAX_H` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HARDSUB_BLUR_R` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HARDSUB_BLUR_W` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HARDSUB_COVER_FULLW` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HARDSUB_FIXED_BOTTOM` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HARDSUB_FORCE_BLUR` | [engines.render](../modules/engines.render.md) (2), [render](../modules/render.md) (2) |
| `HARDSUB_FULL_COVER_RATIO` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HARDSUB_GAP_FILL_SEC` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HARDSUB_MODE` | [engines.render](../modules/engines.render.md) (2), [render](../modules/render.md) (2) |
| `HARDSUB_PAD_BOTTOM` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HARDSUB_PAD_TOP` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HARDSUB_REDETECT` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HARDSUB_STRETCH_FULLW` | [engines.render](../modules/engines.render.md) (2), [render](../modules/render.md) (2) |
| `HARDSUB_STRETCH_SIGMA` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HARDSUB_STRETCH_SIGMA_V` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HARDSUB_STYLE` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HARDSUB_TRACK_MAX_SAMPLES` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `HF_HOME` | [config](../modules/config.md) (1) |
| `HF_HUB_DISABLE_SYMLINKS` | [config](../modules/config.md) (1), [core.config](../modules/core.config.md) (1), [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md) (1), [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md) (1), [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md) (1), [engines.asr.fun_asr_nano](../modules/engines.asr.fun_asr_nano.md) (1), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md) (1), [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md) (1), [engines.asr.paraformer_zh](../modules/engines.asr.paraformer_zh.md) (1), [engines.asr.sensevoice_asr](../modules/engines.asr.sensevoice_asr.md) (1), [server](../modules/server.md) (1) |
| `HF_HUB_DISABLE_SYMLINKS_WARNING` | [config](../modules/config.md) (1), [core.config](../modules/core.config.md) (1), [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md) (1), [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md) (1), [engines.asr.fun_asr_nano](../modules/engines.asr.fun_asr_nano.md) (1), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md) (1), [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md) (1), [engines.asr.paraformer_zh](../modules/engines.asr.paraformer_zh.md) (1), [engines.asr.sensevoice_asr](../modules/engines.asr.sensevoice_asr.md) (1), [server](../modules/server.md) (1) |
| `HG_BACKEND` | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md) (1), [hongguo_bridge](../modules/hongguo_bridge.md) (1), [server](../modules/server.md) (1) |
| `HG_ENGINE_DIR` | [agents.hongguo_rpc](../modules/agents.hongguo_rpc.md) (1), [hongguo_rpc](../modules/hongguo_rpc.md) (1) |
| `HG_HELPER_PIDFILE` | [agents.hongguo_rpc](../modules/agents.hongguo_rpc.md) (1), [hongguo_rpc](../modules/hongguo_rpc.md) (1) |
| `HG_HELPER_SINGLETON` | [agents.hongguo_rpc](../modules/agents.hongguo_rpc.md) (1), [hongguo_rpc](../modules/hongguo_rpc.md) (1), [server](../modules/server.md) (1) |
| `HG_LIC_ACTIVATE_EXE` | [agents.hongguo_license_ensure](../modules/agents.hongguo_license_ensure.md) (1), [hongguo_license_ensure](../modules/hongguo_license_ensure.md) (1) |
| `HG_RPC_IDLE_SEC` | [agents.hongguo_rpc](../modules/agents.hongguo_rpc.md) (1), [hongguo_rpc](../modules/hongguo_rpc.md) (1) |
| `HG_RPC_TIMEOUT` | [agents.hongguo_rpc](../modules/agents.hongguo_rpc.md) (1), [hongguo_rpc](../modules/hongguo_rpc.md) (1) |
| `HG_UI_TOKEN` | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md) (1), [hongguo_bridge](../modules/hongguo_bridge.md) (1) |
| `HOST` | [server](../modules/server.md) (1) |
| `JOB_WORKERS` | [server](../modules/server.md) (1) |
| `LIB_ROOT` | [tools.lib_check](../modules/tools.lib_check.md) (1) |
| `LLAMA_BASE_URL` | [engines.llm](../modules/engines.llm.md) (2), [llm](../modules/llm.md) (3) |
| `LLM_API_KEY` | [config](../modules/config.md) (2), [engines.llm](../modules/engines.llm.md) (1), [llm](../modules/llm.md) (1) |
| `LLM_BASE_URL` | [config](../modules/config.md) (2), [engines.llm](../modules/engines.llm.md) (1), [llm](../modules/llm.md) (1) |
| `LLM_ENABLE_THINKING` | [agent_core](../modules/agent_core.md) (1), [agents.agent_core](../modules/agents.agent_core.md) (1), [engines.llm](../modules/engines.llm.md) (2), [llm](../modules/llm.md) (2) |
| `LLM_MODEL` | [config](../modules/config.md) (3), [engines.llm](../modules/engines.llm.md) (1), [engines.translate](../modules/engines.translate.md) (1), [llm](../modules/llm.md) (1), [scripts.check_batch3](../modules/scripts.check_batch3.md) (1), [tools.context_studio.analyzer](../modules/tools.context_studio.analyzer.md) (1), [translate](../modules/translate.md) (1) |
| `LLM_NUM_CTX` | [engines.llm](../modules/engines.llm.md) (1), [llm](../modules/llm.md) (1) |
| `LOCALAPPDATA` | [agents.agent_hongguo](../modules/agents.agent_hongguo.md) (1), [agents.hongguo_license_ensure](../modules/agents.hongguo_license_ensure.md) (2), [agents.hongguo_rpc](../modules/agents.hongguo_rpc.md) (3), [hongguo_license_ensure](../modules/hongguo_license_ensure.md) (2), [hongguo_rpc](../modules/hongguo_rpc.md) (3) |
| `LOCAL_LLM_BASE_URL` | [engines.llm](../modules/engines.llm.md) (1), [llm](../modules/llm.md) (1) |
| `MODEL_PRESETS_DIR` | [tools.preset_switcher](../modules/tools.preset_switcher.md) (1) |
| `MT_ZH_VI` | [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md) (2), [mt_zh_vi](../modules/mt_zh_vi.md) (2) |
| `MT_ZH_VI_BATCH` | [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md) (1), [mt_zh_vi](../modules/mt_zh_vi.md) (1) |
| `MT_ZH_VI_BEAM` | [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md) (1), [mt_zh_vi](../modules/mt_zh_vi.md) (1) |
| `MT_ZH_VI_DEVICE` | [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md) (1), [mt_zh_vi](../modules/mt_zh_vi.md) (1) |
| `MT_ZH_VI_LOCAL` | [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md) (1), [mt_zh_vi](../modules/mt_zh_vi.md) (1) |
| `MT_ZH_VI_MAX_TOKENS` | [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md) (1), [mt_zh_vi](../modules/mt_zh_vi.md) (1) |
| `MT_ZH_VI_MODEL` | [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md) (1), [mt_zh_vi](../modules/mt_zh_vi.md) (1) |
| `MT_ZH_VI_MODEL_BASE` | [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md) (1), [mt_zh_vi](../modules/mt_zh_vi.md) (1) |
| `MT_ZH_VI_MODEL_QT` | [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md) (1), [mt_zh_vi](../modules/mt_zh_vi.md) (1) |
| `MT_ZH_VI_ONLY` | [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md) (1), [mt_zh_vi](../modules/mt_zh_vi.md) (1) |
| `MT_ZH_VI_ROLE` | [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md) (1), [mt_zh_vi](../modules/mt_zh_vi.md) (1) |
| `NAME_MODEL` | [config](../modules/config.md) (2) |
| `OAUTHLIB_RELAX_TOKEN_SCOPE` | [agents.test_channel](../modules/agents.test_channel.md) (1), [test_channel](../modules/test_channel.md) (1), [tools.test_channel](../modules/tools.test_channel.md) (1) |
| `OMNI_CWD` | [config](../modules/config.md) (1) |
| `OMNI_DEVICE` | [config](../modules/config.md) (1) |
| `OMNI_GUIDANCE` | [engines.clone_tts](../modules/engines.clone_tts.md) (1) |
| `OMNI_MODEL` | [config](../modules/config.md) (1) |
| `OMNI_NUM_STEP` | [engines.clone_tts](../modules/engines.clone_tts.md) (1) |
| `OMNI_PY` | [config](../modules/config.md) (1) |
| `PATH` | [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md) (2) |
| `PINELINE_BASE` | [agent_tele_cmd](../modules/agent_tele_cmd.md) (1), [agents.agent_autopilot](../modules/agents.agent_autopilot.md) (1), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md) (1), [tools.migrate_work](../modules/tools.migrate_work.md) (1) |
| `PINELINE_OMNI_ENV` | [config](../modules/config.md) (1) |
| `PINELINE_VIENEU_ENV` | [config](../modules/config.md) (1) |
| `PLAN_FILE_TIMEOUT` | [engines.translate](../modules/engines.translate.md) (1), [translate](../modules/translate.md) (1) |
| `PLAN_MODE` | [engines.translate](../modules/engines.translate.md) (1), [translate](../modules/translate.md) (1) |
| `PLAN_MODEL` | [engines.translate](../modules/engines.translate.md) (1), [translate](../modules/translate.md) (2) |
| `PORT` | [agents.agent_autopilot](../modules/agents.agent_autopilot.md) (1), [agents.agent_hongguo](../modules/agents.agent_hongguo.md) (4), [agents.canva_client](../modules/agents.canva_client.md) (2), [app_desktop](../modules/app_desktop.md) (1), [restart_server](../modules/restart_server.md) (1), [server](../modules/server.md) (1), [tools.migrate_work](../modules/tools.migrate_work.md) (1) |
| `PRONOUN_ANALYZE` | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) (1) |
| `PRONOUN_ANALYZE_CHUNK` | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) (1) |
| `PRONOUN_ANALYZE_EARLY_STOP` | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) (1) |
| `PRONOUN_ANALYZE_MAX_CHUNKS` | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) (1) |
| `PRONOUN_ANALYZE_MIN_CHUNKS` | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) (1) |
| `PRONOUN_ANALYZE_MODE` | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) (1) |
| `PRONOUN_ANALYZE_MODEL` | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) (1) |
| `PRONOUN_MODEL` | [agent_hang_fix](../modules/agent_hang_fix.md) (2), [config](../modules/config.md) (2) |
| `PRONOUN_TITLE_POLICY` | [agents.agent_pronoun_pass](../modules/agents.agent_pronoun_pass.md) (1) |
| `PYTHONEXECUTABLE` | [rvc_bridge.vieneu_batch](../modules/rvc_bridge.vieneu_batch.md) (1) |
| `PYTHONIOENCODING` | [server](../modules/server.md) (1) |
| `QA_ASR_DEVICE` | [engines.clone_tts](../modules/engines.clone_tts.md) (1) |
| `QA_ASR_MODEL` | [engines.clone_tts](../modules/engines.clone_tts.md) (1) |
| `QUEUE_LIVE_CONFIG` | [agent_tele_cmd](../modules/agent_tele_cmd.md) (1), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md) (1) |
| `QUEUE_PARK_POLL_SEC` | [core.job_queue](../modules/core.job_queue.md) (1), [job_queue](../modules/job_queue.md) (1) |
| `QWEN3_FORCED_ALIGNER` | [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md) (1), [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md) (1) |
| `REF_ASR` | [server](../modules/server.md) (1) |
| `REF_ASR_DEVICE` | [server](../modules/server.md) (2) |
| `REF_ASR_MODEL` | [server](../modules/server.md) (3) |
| `RENDER_BGM_FILE` | [engines.render_fx](../modules/engines.render_fx.md) (2) |
| `RENDER_BGM_VOL` | [engines.render_fx](../modules/engines.render_fx.md) (2) |
| `RENDER_BRAND` | [engines.render_fx](../modules/engines.render_fx.md) (2) |
| `RENDER_BRAND_LOGO` | [engines.render_fx](../modules/engines.render_fx.md) (2) |
| `RENDER_BRAND_LOGO_FILE` | [engines.render_fx](../modules/engines.render_fx.md) (2) |
| `RENDER_BRAND_MODE` | [engines.render_fx](../modules/engines.render_fx.md) (2) |
| `RENDER_BRAND_OPACITY` | [engines.render_fx](../modules/engines.render_fx.md) (2) |
| `RENDER_BRAND_TEXT` | [engines.render_fx](../modules/engines.render_fx.md) (2) |
| `RENDER_DUB_VOL` | [engines.render_fx](../modules/engines.render_fx.md) (2) |
| `RENDER_ENCODER` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `RENDER_EQ_BRIGHTNESS` | [engines.render_fx](../modules/engines.render_fx.md) (1) |
| `RENDER_EQ_CONTRAST` | [engines.render_fx](../modules/engines.render_fx.md) (1) |
| `RENDER_EQ_SATURATION` | [engines.render_fx](../modules/engines.render_fx.md) (1) |
| `RENDER_FRAME` | [engines.render_fx](../modules/engines.render_fx.md) (2) |
| `RENDER_FRAME_FILE` | [engines.render_fx](../modules/engines.render_fx.md) (2) |
| `RENDER_GRAIN_FILE` | [engines.render_fx](../modules/engines.render_fx.md) (2) |
| `RENDER_LIB_BGM_VOL` | [engines.sfx_lib](../modules/engines.sfx_lib.md) (1) |
| `RENDER_LUT_FILE` | [engines.render_fx](../modules/engines.render_fx.md) (2) |
| `RENDER_SFX_VOICE_BOOST` | [engines.sfx_lib](../modules/engines.sfx_lib.md) (1) |
| `RENDER_SFX_VOL` | [engines.sfx_lib](../modules/engines.sfx_lib.md) (1) |
| `RENDER_SPEED` | [engines.render](../modules/engines.render.md) (2), [render](../modules/render.md) (2) |
| `REVIEW_BACKUP` | [translate](../modules/translate.md) (1) |
| `REVIEW_MODEL` | [config](../modules/config.md) (2), [engines.translate](../modules/engines.translate.md) (2), [translate](../modules/translate.md) (3) |
| `REVIEW_PARALLEL` | [translate](../modules/translate.md) (1) |
| `REVIEW_PARALLEL_DEFAULT` | [translate](../modules/translate.md) (1) |
| `REVIEW_PARALLEL_MAX` | [translate](../modules/translate.md) (1) |
| `REVIEW_PASS1_ALLOW_CHAT_FALLBACK` | [translate](../modules/translate.md) (1) |
| `REVIEW_PASS1_CHUNK_CUES` | [translate](../modules/translate.md) (1) |
| `REVIEW_PASS1_FALLBACK_CUES` | [translate](../modules/translate.md) (1) |
| `REVIEW_PASS1_FULL_VI` | [translate](../modules/translate.md) (1) |
| `REVIEW_PASS1_MAX_UPLOAD_BYTES` | [translate](../modules/translate.md) (1) |
| `REVIEW_PASS1_MODEL` | [translate](../modules/translate.md) (1) |
| `REVIEW_PASS1_TIMEOUT` | [translate](../modules/translate.md) (1) |
| `REVIEW_PRESET` | [agent_brain](../modules/agent_brain.md) (1), [engines.translate](../modules/engines.translate.md) (2), [translate](../modules/translate.md) (2) |
| `REVIEW_PRONOUN_MASK` | [translate](../modules/translate.md) (1) |
| `RUNWATCH_MAX_HEAL` | [agent_feeder](../modules/agent_feeder.md) (1), [agents.agent_feeder](../modules/agents.agent_feeder.md) (1) |
| `RUNWATCH_SEC` | [agent_tele_cmd](../modules/agent_tele_cmd.md) (1), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md) (1) |
| `RUNWATCH_STUCK_MIN` | [agent_feeder](../modules/agent_feeder.md) (1), [agents.agent_feeder](../modules/agents.agent_feeder.md) (1) |
| `SFX_CDX_HQ` | [engines.sfx_lib](../modules/engines.sfx_lib.md) (1) |
| `SFX_CDX_MODEL_DIR` | [engines.sfx_lib](../modules/engines.sfx_lib.md) (1) |
| `SFX_LIB_DIR` | [engines.sfx_lib](../modules/engines.sfx_lib.md) (1) |
| `SKIP_VRAM_FREE` | [engines.vram](../modules/engines.vram.md) (1) |
| `SOURCE_DIRECT_ROOTS` | [server](../modules/server.md) (1) |
| `SUB_ALIGN` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `SUB_BOLD` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `SUB_COLOR` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `SUB_FOLLOW_HARDSUB` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `SUB_FONT` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `SUB_FONT_SIZE` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `SUB_MARGIN_L` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `SUB_MARGIN_R` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `SUB_MARGIN_V` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `SUB_OUTLINE` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `SUB_OUTLINE_COLOR` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `SUB_SHADOW` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `TELEGRAM_ALLOWED_USERS` | [agents.agent_watch](../modules/agents.agent_watch.md) (1), [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) (2) |
| `TELEGRAM_BOT_TOKEN` | [agents.agent_watch](../modules/agents.agent_watch.md) (1), [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) (2) |
| `TELEGRAM_POLL_SEC` | [agent_tele_cmd](../modules/agent_tele_cmd.md) (1), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md) (1) |
| `TEMP` | [agent_tele_cmd](../modules/agent_tele_cmd.md) (1), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md) (1), [agents.hongguo_license_ensure](../modules/agents.hongguo_license_ensure.md) (1), [agents.hongguo_rpc](../modules/agents.hongguo_rpc.md) (2), [app_desktop](../modules/app_desktop.md) (1), [hongguo_license_ensure](../modules/hongguo_license_ensure.md) (1), [hongguo_rpc](../modules/hongguo_rpc.md) (2), [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) (1), [uploader_settings_api](../modules/uploader_settings_api.md) (1) |
| `TEST_YT_SECRET` | [agents.test_channel](../modules/agents.test_channel.md) (1), [test_channel](../modules/test_channel.md) (1), [tools.test_channel](../modules/tools.test_channel.md) (1) |
| `TMP` | [agent_tele_cmd](../modules/agent_tele_cmd.md) (1), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md) (1), [agents.hongguo_rpc](../modules/agents.hongguo_rpc.md) (2), [hongguo_rpc](../modules/hongguo_rpc.md) (2) |
| `TRANSLATE_BATCH` | [engines.translate](../modules/engines.translate.md) (2), [server](../modules/server.md) (2), [translate](../modules/translate.md) (2) |
| `TRANSLATE_CTX_LINES` | [engines.translate](../modules/engines.translate.md) (1), [translate](../modules/translate.md) (1) |
| `TRANSLATE_FILL_ROUNDS` | [engines.translate](../modules/engines.translate.md) (1), [translate](../modules/translate.md) (1) |
| `TRANSLATE_MODE` | [engines.translate](../modules/engines.translate.md) (2), [translate](../modules/translate.md) (2) |
| `TRANSLATE_MODEL` | [config](../modules/config.md) (1), [engines.translate](../modules/engines.translate.md) (2), [server](../modules/server.md) (1), [tools.context_studio.analyzer](../modules/tools.context_studio.analyzer.md) (1), [translate](../modules/translate.md) (2) |
| `TRANSLATE_ONESHOT_MAX` | [engines.translate](../modules/engines.translate.md) (1), [translate](../modules/translate.md) (1) |
| `TRANSLATE_PRESET` | [agent_brain](../modules/agent_brain.md) (1), [engines.translate](../modules/engines.translate.md) (1), [translate](../modules/translate.md) (1) |
| `TTS_RUNAWAY_RETRIES` | [engines.clone_tts](../modules/engines.clone_tts.md) (1) |
| `VIENEU_BATCH` | [engines.clone_tts](../modules/engines.clone_tts.md) (1), [rvc_bridge.vieneu_batch](../modules/rvc_bridge.vieneu_batch.md) (1) |
| `VIENEU_BOOT_SEC` | [engines.clone_tts](../modules/engines.clone_tts.md) (1), [server](../modules/server.md) (1) |
| `VIENEU_CPU_THREADS` | [rvc_bridge.vieneu_batch](../modules/rvc_bridge.vieneu_batch.md) (1) |
| `VIENEU_DEVICE` | [config](../modules/config.md) (1) |
| `VIENEU_LOW_PRIORITY` | [rvc_bridge.vieneu_batch](../modules/rvc_bridge.vieneu_batch.md) (1) |
| `VIENEU_PY` | [config](../modules/config.md) (1) |
| `VIENEU_STALL_SEC` | [engines.clone_tts](../modules/engines.clone_tts.md) (1) |
| `WM_FORCE_CORNERS` | [engines.render](../modules/engines.render.md) (2), [render](../modules/render.md) (2) |
| `WM_MAX_SAMPLES` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `WM_SAMPLE_SEC` | [engines.render](../modules/engines.render.md) (1), [render](../modules/render.md) (1) |
| `WORK_DIR` | [films_merge_api](../modules/films_merge_api.md) (1) |
| `YT_UPLOADER_DIR` | [agents.auto_publisher](../modules/agents.auto_publisher.md) (1), [auto_publisher](../modules/auto_publisher.md) (1), [core.film_db](../modules/core.film_db.md) (1), [film_db](../modules/film_db.md) (1), [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) (1), [tools.lib_check](../modules/tools.lib_check.md) (1), [uploader_settings_api](../modules/uploader_settings_api.md) (1) |
| `ZZ_ENVSET` | [scripts.check_batch3](../modules/scripts.check_batch3.md) (1) |
| `ZZ_FROMFILE` | [scripts.check_batch3](../modules/scripts.check_batch3.md) (1) |
