# File/artifact & cổng — ai đụng tới

_Sinh tự động bởi `scripts/brain_build.py` lúc 2026-11-11 02:38. Đừng sửa tay — chạy lại script._


Dùng để trả lời: *file `X.json` do ai ghi/đọc?* (chỉ là chuỗi literal xuất hiện trong code). Artifact dùng bởi ≥2 module là điểm có thể race khi ghi.

## Cổng

| Cổng | Module |
|---|---|
| 3377 | [agent_brain](../modules/agent_brain.md), [agent_brain_context](../modules/agent_brain_context.md), [llm](../modules/llm.md), [meta_studio](../modules/meta_studio.md) |
| 8000 | [agent_brain_context](../modules/agent_brain_context.md), [agent_tele_cmd](../modules/agent_tele_cmd.md), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md), [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md), [hongguo_bridge](../modules/hongguo_bridge.md), [server](../modules/server.md) |
| 8083 | [agent_brain](../modules/agent_brain.md), [agent_brain_context](../modules/agent_brain_context.md), [config](../modules/config.md), [core.config](../modules/core.config.md), [engines.llm](../modules/engines.llm.md), [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md), [llm](../modules/llm.md), [uploader_settings_api](../modules/uploader_settings_api.md) |
| 8801 | [agent_brain](../modules/agent_brain.md), [agent_brain_context](../modules/agent_brain_context.md), [agent_tele_cmd](../modules/agent_tele_cmd.md), [agent_tool_loop](../modules/agent_tool_loop.md), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md), [agents.agent_tool_loop](../modules/agents.agent_tool_loop.md), [agents.meta_studio](../modules/agents.meta_studio.md), [meta_studio](../modules/meta_studio.md), [scripts.check_batch2](../modules/scripts.check_batch2.md), [scripts.check_batch3](../modules/scripts.check_batch3.md), [scripts.check_batch5](../modules/scripts.check_batch5.md) |
| 8802 | [agent_brain](../modules/agent_brain.md), [agent_brain_context](../modules/agent_brain_context.md), [agent_core](../modules/agent_core.md), [agent_feeder](../modules/agent_feeder.md), [agent_tele_cmd](../modules/agent_tele_cmd.md), [agents.agent_core](../modules/agents.agent_core.md), [agents.agent_feeder](../modules/agents.agent_feeder.md), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md), [restart_server](../modules/restart_server.md), [scripts.check_batch2](../modules/scripts.check_batch2.md), [tools.migrate_work](../modules/tools.migrate_work.md) |
| 8804 | [http_routes.routes_films](../modules/http_routes.routes_films.md), [routes_films](../modules/routes_films.md) |
| 11434 | [engines.llm](../modules/engines.llm.md), [llm](../modules/llm.md), [scripts.check_batch2](../modules/scripts.check_batch2.md) |

## Artifact

| File | Số module | Module |
|---|---:|---|
| `manifest.json` | 34 | [agent_brain](../modules/agent_brain.md), [agent_brain_context](../modules/agent_brain_context.md), [agent_core](../modules/agent_core.md), [agent_feeder](../modules/agent_feeder.md), [agent_tool_loop](../modules/agent_tool_loop.md), [agents.agent_autopilot](../modules/agents.agent_autopilot.md), [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_core](../modules/agents.agent_core.md), [agents.agent_feeder](../modules/agents.agent_feeder.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [agents.agent_tool_loop](../modules/agents.agent_tool_loop.md), [agents.agent_watch](../modules/agents.agent_watch.md), [agents.auto_publisher](../modules/agents.auto_publisher.md), [agents.meta_studio](../modules/agents.meta_studio.md), [auto_publisher](../modules/auto_publisher.md), [core.film_db](../modules/core.film_db.md), [core.job_queue](../modules/core.job_queue.md), [core.manifest](../modules/core.manifest.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.series_glossary](../modules/engines.series_glossary.md), [film_db](../modules/film_db.md), [films_merge_api](../modules/films_merge_api.md), [http_routes.routes_agent](../modules/http_routes.routes_agent.md), [job_queue](../modules/job_queue.md), [meta_studio](../modules/meta_studio.md), [restart_server](../modules/restart_server.md), [routes_agent](../modules/routes_agent.md), [scripts.check_batch1](../modules/scripts.check_batch1.md), [scripts.check_batch3](../modules/scripts.check_batch3.md), [scripts.check_batch4](../modules/scripts.check_batch4.md), [series_glossary](../modules/series_glossary.md), [server](../modules/server.md), [tools.migrate_work](../modules/tools.migrate_work.md) |
| `script.json` | 33 | [agent_brain](../modules/agent_brain.md), [agent_brain_context](../modules/agent_brain_context.md), [agent_core](../modules/agent_core.md), [agent_feeder](../modules/agent_feeder.md), [agent_hang_fix](../modules/agent_hang_fix.md), [agent_qa_gate](../modules/agent_qa_gate.md), [agent_quality](../modules/agent_quality.md), [agents.agent_core](../modules/agents.agent_core.md), [agents.agent_feeder](../modules/agents.agent_feeder.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_name_pass](../modules/agents.agent_name_pass.md), [agents.agent_pronoun_pass](../modules/agents.agent_pronoun_pass.md), [agents.agent_qa_gate](../modules/agents.agent_qa_gate.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [agents.meta_studio](../modules/agents.meta_studio.md), [core.job_queue](../modules/core.job_queue.md), [engines.asr.hardsub_asr](../modules/engines.asr.hardsub_asr.md), [engines.clone_tts](../modules/engines.clone_tts.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md), [engines.render](../modules/engines.render.md), [engines.script_lint](../modules/engines.script_lint.md), [engines.translate](../modules/engines.translate.md), [engines.translate_alts](../modules/engines.translate_alts.md), [http_routes.routes_agent](../modules/http_routes.routes_agent.md), [job_queue](../modules/job_queue.md), [meta_studio](../modules/meta_studio.md), [render](../modules/render.md), [routes_agent](../modules/routes_agent.md), [scripts.check_batch1](../modules/scripts.check_batch1.md), [scripts.check_batch4](../modules/scripts.check_batch4.md), [server](../modules/server.md), [translate](../modules/translate.md) |
| `output.mp4` | 22 | [agent_brain_context](../modules/agent_brain_context.md), [agent_core](../modules/agent_core.md), [agent_feeder](../modules/agent_feeder.md), [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_core](../modules/agents.agent_core.md), [agents.agent_feeder](../modules/agents.agent_feeder.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [agents.auto_publisher](../modules/agents.auto_publisher.md), [agents.meta_studio](../modules/agents.meta_studio.md), [auto_publisher](../modules/auto_publisher.md), [core.job_queue](../modules/core.job_queue.md), [engines.mux](../modules/engines.mux.md), [engines.render](../modules/engines.render.md), [engines.split_parts](../modules/engines.split_parts.md), [films_merge_api](../modules/films_merge_api.md), [job_queue](../modules/job_queue.md), [meta_studio](../modules/meta_studio.md), [render](../modules/render.md), [scripts.check_batch1](../modules/scripts.check_batch1.md), [server](../modules/server.md), [split_parts](../modules/split_parts.md) |
| `asr.json` | 19 | [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.asr.asr](../modules/engines.asr.asr.md), [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md), [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md), [engines.asr.fun_asr_nano](../modules/engines.asr.fun_asr_nano.md), [engines.asr.hardsub_asr](../modules/engines.asr.hardsub_asr.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md), [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md), [engines.asr.paraformer_zh](../modules/engines.asr.paraformer_zh.md), [engines.asr.sensevoice_asr](../modules/engines.asr.sensevoice_asr.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.ocr](../modules/engines.ocr.md), [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md), [engines.translate](../modules/engines.translate.md), [server](../modules/server.md), [split_parts](../modules/split_parts.md), [translate](../modules/translate.md) |
| `glossary.json` | 15 | [agent_qa_gate](../modules/agent_qa_gate.md), [agents.agent_name_pass](../modules/agents.agent_name_pass.md), [agents.agent_pronoun_pass](../modules/agents.agent_pronoun_pass.md), [agents.agent_qa_gate](../modules/agents.agent_qa_gate.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md), [engines.script_lint](../modules/engines.script_lint.md), [engines.series_glossary](../modules/engines.series_glossary.md), [engines.translate](../modules/engines.translate.md), [engines.translate_alts](../modules/engines.translate_alts.md), [series_glossary](../modules/series_glossary.md), [server](../modules/server.md), [tools.context_studio.app_streamlit](../modules/tools.context_studio.app_streamlit.md), [tools.context_studio.exporter](../modules/tools.context_studio.exporter.md), [translate](../modules/translate.md) |
| `sub.vi.srt` | 15 | [agent_feeder](../modules/agent_feeder.md), [agent_hang_fix](../modules/agent_hang_fix.md), [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_feeder](../modules/agents.agent_feeder.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_pronoun_pass](../modules/agents.agent_pronoun_pass.md), [agents.meta_studio](../modules/agents.meta_studio.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.render](../modules/engines.render.md), [engines.script_lint](../modules/engines.script_lint.md), [engines.translate](../modules/engines.translate.md), [meta_studio](../modules/meta_studio.md), [render](../modules/render.md), [server](../modules/server.md), [translate](../modules/translate.md) |
| `audio.wav` | 14 | [agents.agent_heal](../modules/agents.agent_heal.md), [engines.asr.asr](../modules/engines.asr.asr.md), [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md), [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md), [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md), [engines.asr.fun_asr_nano](../modules/engines.asr.fun_asr_nano.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md), [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md), [engines.asr.paraformer_zh](../modules/engines.asr.paraformer_zh.md), [engines.asr.sensevoice_asr](../modules/engines.asr.sensevoice_asr.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.separate](../modules/engines.separate.md), [scripts.check_batch1](../modules/scripts.check_batch1.md), [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `sub.zh.srt` | 13 | [agents.agent_heal](../modules/agents.agent_heal.md), [engines.asr.asr](../modules/engines.asr.asr.md), [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md), [engines.asr.fun_asr_nano](../modules/engines.asr.fun_asr_nano.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md), [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md), [engines.asr.paraformer_zh](../modules/engines.asr.paraformer_zh.md), [engines.asr.sensevoice_asr](../modules/engines.asr.sensevoice_asr.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md), [server](../modules/server.md), [split_parts](../modules/split_parts.md) |
| `tts.json` | 13 | [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.assemble](../modules/engines.assemble.md), [engines.clone_tts](../modules/engines.clone_tts.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.mux](../modules/engines.mux.md), [engines.render](../modules/engines.render.md), [http_routes.routes_agent](../modules/http_routes.routes_agent.md), [render](../modules/render.md), [routes_agent](../modules/routes_agent.md), [scripts.check_batch1](../modules/scripts.check_batch1.md), [scripts.check_batch4](../modules/scripts.check_batch4.md), [server](../modules/server.md) |
| `dub_fit.wav` | 9 | [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.assemble](../modules/engines.assemble.md), [engines.mux](../modules/engines.mux.md), [engines.render](../modules/engines.render.md), [render](../modules/render.md), [scripts.check_batch4](../modules/scripts.check_batch4.md), [server](../modules/server.md) |
| `script.display.json` | 9 | [agents.agent_heal](../modules/agents.agent_heal.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.render](../modules/engines.render.md), [engines.script_lint](../modules/engines.script_lint.md), [engines.translate](../modules/engines.translate.md), [render](../modules/render.md), [scripts.check_batch1](../modules/scripts.check_batch1.md), [server](../modules/server.md), [translate](../modules/translate.md) |
| `tts_config.json` | 8 | [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_hongguo](../modules/agents.agent_hongguo.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.clone_tts](../modules/engines.clone_tts.md), [engines.split_parts](../modules/engines.split_parts.md), [scripts.check_batch4](../modules/scripts.check_batch4.md), [server](../modules/server.md), [split_parts](../modules/split_parts.md) |
| `ocr.json` | 7 | [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.ocr](../modules/engines.ocr.md), [engines.render](../modules/engines.render.md), [engines.translate](../modules/engines.translate.md), [render](../modules/render.md), [server](../modules/server.md), [translate](../modules/translate.md) |
| `sub.vi.burn.srt` | 7 | [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.meta_studio](../modules/agents.meta_studio.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.render](../modules/engines.render.md), [meta_studio](../modules/meta_studio.md), [render](../modules/render.md) |
| `vocals.wav` | 7 | [engines.asr.asr](../modules/engines.asr.asr.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.render](../modules/engines.render.md), [engines.separate](../modules/engines.separate.md), [render](../modules/render.md), [scripts.check_batch4](../modules/scripts.check_batch4.md), [server](../modules/server.md) |
| `.series.json` | 6 | [agent_feeder](../modules/agent_feeder.md), [agents.agent_feeder](../modules/agents.agent_feeder.md), [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md), [agents.meta_studio](../modules/agents.meta_studio.md), [hongguo_bridge](../modules/hongguo_bridge.md), [meta_studio](../modules/meta_studio.md) |
| `asr.fun_nano.json` | 6 | [engines.asr.asr_align_nano_para](../modules/engines.asr.asr_align_nano_para.md), [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md), [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md), [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md), [server](../modules/server.md) |
| `context_pack.json` | 6 | [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.translate](../modules/engines.translate.md), [engines.translate_alts](../modules/engines.translate_alts.md), [server](../modules/server.md), [tools.context_studio.exporter](../modules/tools.context_studio.exporter.md), [translate](../modules/translate.md) |
| `no_vocals.wav` | 6 | [engines.media_ts](../modules/engines.media_ts.md), [engines.render](../modules/engines.render.md), [engines.separate](../modules/engines.separate.md), [render](../modules/render.md), [scripts.check_batch4](../modules/scripts.check_batch4.md), [server](../modules/server.md) |
| `style_lock.json` | 6 | [agent_qa_gate](../modules/agent_qa_gate.md), [agents.agent_qa_gate](../modules/agents.agent_qa_gate.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.translate](../modules/engines.translate.md), [tools.context_studio.exporter](../modules/tools.context_studio.exporter.md), [translate](../modules/translate.md) |
| `tts_fit.json` | 6 | [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_heal](../modules/agents.agent_heal.md), [engines.assemble](../modules/engines.assemble.md), [engines.render](../modules/engines.render.md), [render](../modules/render.md), [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `upload_history.jsonl` | 6 | [agents.auto_publisher](../modules/agents.auto_publisher.md), [auto_publisher](../modules/auto_publisher.md), [core.film_db](../modules/core.film_db.md), [film_db](../modules/film_db.md), [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md), [uploader_settings_api](../modules/uploader_settings_api.md) |
| `asr.paraformer_zh.json` | 5 | [engines.asr.asr_align_nano_para](../modules/engines.asr.asr_align_nano_para.md), [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md), [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md), [server](../modules/server.md) |
| `client_secret.json` | 5 | [agents.auto_publisher](../modules/agents.auto_publisher.md), [agents.test_channel](../modules/agents.test_channel.md), [auto_publisher](../modules/auto_publisher.md), [test_channel](../modules/test_channel.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `config.json` | 5 | [config](../modules/config.md), [core.config](../modules/core.config.md), [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md), [mt_zh_vi](../modules/mt_zh_vi.md), [scripts.check_batch2](../modules/scripts.check_batch2.md) |
| `qa_flags.json` | 5 | [agent_qa_gate](../modules/agent_qa_gate.md), [agents.agent_qa_gate](../modules/agents.agent_qa_gate.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [server](../modules/server.md), [tools.context_studio.exporter](../modules/tools.context_studio.exporter.md) |
| `queue_state.json` | 5 | [core.film_db](../modules/core.film_db.md), [film_db](../modules/film_db.md), [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md), [tools.lib_check](../modules/tools.lib_check.md), [uploader_settings_api](../modules/uploader_settings_api.md) |
| `token.json` | 5 | [agents.auto_publisher](../modules/agents.auto_publisher.md), [agents.test_channel](../modules/agents.test_channel.md), [auto_publisher](../modules/auto_publisher.md), [test_channel](../modules/test_channel.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `.partial.mp4` | 4 | [agent_feeder](../modules/agent_feeder.md), [agents.agent_feeder](../modules/agents.agent_feeder.md), [engines.render](../modules/engines.render.md), [render](../modules/render.md) |
| `.progress.json` | 4 | [engines.asr.asr_hybrid_progress](../modules/engines.asr.asr_hybrid_progress.md), [engines.asr.fun_asr_nano](../modules/engines.asr.fun_asr_nano.md), [engines.asr.paraformer_zh](../modules/engines.asr.paraformer_zh.md), [engines.asr.sensevoice_asr](../modules/engines.asr.sensevoice_asr.md) |
| `.upload.lock` | 4 | [agents.auto_publisher](../modules/agents.auto_publisher.md), [auto_publisher](../modules/auto_publisher.md), [core.film_db](../modules/core.film_db.md), [film_db](../modules/film_db.md) |
| `asr.aligned.json` | 4 | [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md), [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md), [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [server](../modules/server.md) |
| `asr.aligned_fa.json` | 4 | [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md), [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md), [server](../modules/server.md) |
| `asr.aligned_fix.json` | 4 | [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md), [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md), [server](../modules/server.md) |
| `chatgpt_token.txt` | 4 | [agents.meta_studio](../modules/agents.meta_studio.md), [engines.llm](../modules/engines.llm.md), [llm](../modules/llm.md), [meta_studio](../modules/meta_studio.md) |
| `dub_tts.wav` | 4 | [engines.assemble](../modules/engines.assemble.md), [engines.render](../modules/engines.render.md), [render](../modules/render.md), [server](../modules/server.md) |
| `meta.json` | 4 | [engines.download](../modules/engines.download.md), [engines.render](../modules/engines.render.md), [render](../modules/render.md), [server](../modules/server.md) |
| `mixed_audio.partial.wav` | 4 | [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.render](../modules/engines.render.md), [render](../modules/render.md) |
| `mixed_audio.wav` | 4 | [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.render](../modules/engines.render.md), [render](../modules/render.md) |
| `output.partial.mp4` | 4 | [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [server](../modules/server.md) |
| `output_full.mp4` | 4 | [engines.split_parts](../modules/engines.split_parts.md), [films_merge_api](../modules/films_merge_api.md), [server](../modules/server.md), [split_parts](../modules/split_parts.md) |
| `pineline.config.json` | 4 | [config](../modules/config.md), [core.config](../modules/core.config.md), [scripts.check_batch3](../modules/scripts.check_batch3.md), [uploader_settings_api](../modules/uploader_settings_api.md) |
| `script.pre_review.json` | 4 | [agent_qa_gate](../modules/agent_qa_gate.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_qa_gate](../modules/agents.agent_qa_gate.md), [engines.media_ts](../modules/engines.media_ts.md) |
| `source.mp4` | 4 | [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.download](../modules/engines.download.md), [server](../modules/server.md) |
| `_filter_complex.txt` | 3 | [agents.agent_heal](../modules/agents.agent_heal.md), [engines.render](../modules/engines.render.md), [render](../modules/render.md) |
| `_job_queue.json` | 3 | [core.job_queue](../modules/core.job_queue.md), [job_queue](../modules/job_queue.md), [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `asr.aligned_repaired.json` | 3 | [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md), [server](../modules/server.md) |
| `asr.hardsub.json` | 3 | [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [engines.asr.hardsub_asr](../modules/engines.asr.hardsub_asr.md), [server](../modules/server.md) |
| `asr.paraformer_zh.chars.json` | 3 | [engines.asr.asr_align_nano_para](../modules/engines.asr.asr_align_nano_para.md), [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md) |
| `batch_config.json` | 3 | [batch_config](../modules/batch_config.md), [core.batch_config](../modules/core.batch_config.md), [scripts.check_batch3](../modules/scripts.check_batch3.md) |
| `channel.json` | 3 | [agents.test_channel](../modules/agents.test_channel.md), [test_channel](../modules/test_channel.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `channel_limit.json` | 3 | [agents.test_channel](../modules/agents.test_channel.md), [test_channel](../modules/test_channel.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `code_verifier.txt` | 3 | [agents.test_channel](../modules/agents.test_channel.md), [test_channel](../modules/test_channel.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `current_oauth_project.txt` | 3 | [agents.test_channel](../modules/agents.test_channel.md), [test_channel](../modules/test_channel.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `exhausted.json` | 3 | [agents.test_channel](../modules/agents.test_channel.md), [test_channel](../modules/test_channel.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `feeder_state.json` | 3 | [agent_feeder](../modules/agent_feeder.md), [agents.agent_feeder](../modules/agents.agent_feeder.md), [tools.lib_check](../modules/tools.lib_check.md) |
| `hardsub_band.json` | 3 | [engines.asr.hardsub_asr](../modules/engines.asr.hardsub_asr.md), [engines.render](../modules/engines.render.md), [render](../modules/render.md) |
| `mixed_audio.json` | 3 | [engines.render](../modules/engines.render.md), [render](../modules/render.md), [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `projects.json` | 3 | [agents.test_channel](../modules/agents.test_channel.md), [test_channel](../modules/test_channel.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `projects_health.json` | 3 | [agents.test_channel](../modules/agents.test_channel.md), [test_channel](../modules/test_channel.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `.auto_publish_global.lock` | 2 | [agents.auto_publisher](../modules/agents.auto_publisher.md), [auto_publisher](../modules/auto_publisher.md) |
| `.follow.ass` | 2 | [engines.render](../modules/engines.render.md), [render](../modules/render.md) |
| `.meta.json` | 2 | [engines.asr.asr_align_nano_para](../modules/engines.asr.asr_align_nano_para.md), [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md) |
| `.norm.partial.mp4` | 2 | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md), [hongguo_bridge](../modules/hongguo_bridge.md) |
| `.norm.tmp.mp4` | 2 | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md), [hongguo_bridge](../modules/hongguo_bridge.md) |
| `.nvenc_state.json` | 2 | [engines.render](../modules/engines.render.md), [render](../modules/render.md) |
| `.tmp.mp4` | 2 | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md), [hongguo_bridge](../modules/hongguo_bridge.md) |
| `.tmp.txt` | 2 | [agents.hongguo_license_ensure](../modules/agents.hongguo_license_ensure.md), [hongguo_license_ensure](../modules/hongguo_license_ensure.md) |
| `_audio.m4a` | 2 | [engines.render](../modules/engines.render.md), [render](../modules/render.md) |
| `_chunks.txt` | 2 | [engines.render](../modules/engines.render.md), [render](../modules/render.md) |
| `_keys.json` | 2 | [engines.clone_tts](../modules/engines.clone_tts.md), [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `_sample90s.mp4` | 2 | [agent_feeder](../modules/agent_feeder.md), [agents.agent_feeder](../modules/agents.agent_feeder.md) |
| `asr.consensus.json` | 2 | [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [server](../modules/server.md) |
| `asr.firered.json` | 2 | [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [server](../modules/server.md) |
| `asr.nano_fa.json` | 2 | [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md), [server](../modules/server.md) |
| `asr.sensevoice.json` | 2 | [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [server](../modules/server.md) |
| `audio.ts.wav` | 2 | [engines.media_ts](../modules/engines.media_ts.md), [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `audio.wav.json` | 2 | [agents.agent_heal](../modules/agents.agent_heal.md), [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `auto_publish_config.json` | 2 | [agents.auto_publisher](../modules/agents.auto_publisher.md), [auto_publisher](../modules/auto_publisher.md) |
| `auto_publish_queue.json` | 2 | [agents.auto_publisher](../modules/agents.auto_publisher.md), [auto_publisher](../modules/auto_publisher.md) |
| `auto_publish_state.json` | 2 | [agents.auto_publisher](../modules/agents.auto_publisher.md), [auto_publisher](../modules/auto_publisher.md) |
| `autopilot_state.json` | 2 | [agents.agent_autopilot](../modules/agents.agent_autopilot.md), [scripts.check_batch3](../modules/scripts.check_batch3.md) |
| `censor.json` | 2 | [engines.render](../modules/engines.render.md), [render](../modules/render.md) |
| `films.db` | 2 | [core.film_db](../modules/core.film_db.md), [film_db](../modules/film_db.md) |
| `final.mp4` | 2 | [agents.auto_publisher](../modules/agents.auto_publisher.md), [auto_publisher](../modules/auto_publisher.md) |
| `generation_config.json` | 2 | [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md), [mt_zh_vi](../modules/mt_zh_vi.md) |
| `hardsub_cues.json` | 2 | [engines.asr.hardsub_asr](../modules/engines.asr.hardsub_asr.md), [server](../modules/server.md) |
| `hardsub_track.json` | 2 | [engines.render](../modules/engines.render.md), [render](../modules/render.md) |
| `hg_merge_state.json` | 2 | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md), [hongguo_bridge](../modules/hongguo_bridge.md) |
| `hg_title_cache.json` | 2 | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md), [hongguo_bridge](../modules/hongguo_bridge.md) |
| `hongguo_feed_labels.json` | 2 | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md), [hongguo_bridge](../modules/hongguo_bridge.md) |
| `hongguo_play_cache.json` | 2 | [agents.hongguo_rpc](../modules/agents.hongguo_rpc.md), [hongguo_rpc](../modules/hongguo_rpc.md) |
| `input.mp4` | 2 | [agents.meta_studio](../modules/agents.meta_studio.md), [meta_studio](../modules/meta_studio.md) |
| `kVietnamese.json` | 2 | [engines.hv_auditor](../modules/engines.hv_auditor.md), [hv_auditor](../modules/hv_auditor.md) |
| `list.txt` | 2 | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md), [hongguo_bridge](../modules/hongguo_bridge.md) |
| `list_mp4.txt` | 2 | [agent_feeder](../modules/agent_feeder.md), [agents.agent_feeder](../modules/agents.agent_feeder.md) |
| `list_ts.txt` | 2 | [agent_feeder](../modules/agent_feeder.md), [agents.agent_feeder](../modules/agents.agent_feeder.md) |
| `orig_audio.wav` | 2 | [engines.media_ts](../modules/engines.media_ts.md), [engines.separate](../modules/engines.separate.md) |
| `qa_brain.json` | 2 | [agent_brain_context](../modules/agent_brain_context.md), [agent_quality](../modules/agent_quality.md) |
| `relation_matrix.json` | 2 | [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [tools.context_studio.exporter](../modules/tools.context_studio.exporter.md) |
| `script.pre_agent_review.json` | 2 | [agents.agent_heal](../modules/agents.agent_heal.md), [server](../modules/server.md) |
| `seg_0000.wav` | 2 | [engines.clone_tts](../modules/engines.clone_tts.md), [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `settings.json` | 2 | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md), [uploader_settings_api](../modules/uploader_settings_api.md) |
| `split_manifest.json` | 2 | [engines.split_parts](../modules/engines.split_parts.md), [split_parts](../modules/split_parts.md) |
| `sub.vi.aligned.srt` | 2 | [agents.meta_studio](../modules/agents.meta_studio.md), [meta_studio](../modules/meta_studio.md) |
| `tele_chat_history.json` | 2 | [agent_tele_cmd](../modules/agent_tele_cmd.md), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md) |
| `tokenizer_config.json` | 2 | [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md), [mt_zh_vi](../modules/mt_zh_vi.md) |
| `vi_alts.json` | 2 | [engines.translate_alts](../modules/engines.translate_alts.md), [server](../modules/server.md) |
| `video.mp4` | 2 | [agents.meta_studio](../modules/agents.meta_studio.md), [meta_studio](../modules/meta_studio.md) |
| `vocab.json` | 2 | [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md), [mt_zh_vi](../modules/mt_zh_vi.md) |
| `.audio_ts_fixed.json` | 1 | [engines.media_ts](../modules/engines.media_ts.md) |
| `.audio_ts_pending.json` | 1 | [engines.media_ts](../modules/engines.media_ts.md) |
| `.bak.json` | 1 | [server](../modules/server.md) |
| `.chars.json` | 1 | [engines.asr.paraformer_zh](../modules/engines.asr.paraformer_zh.md) |
| `.cl.wav` | 1 | [engines.clone_tts](../modules/engines.clone_tts.md) |
| `.partial.wav` | 1 | [engines.separate](../modules/engines.separate.md) |
| `.server_test.lock` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `.sidecar_18902.lock` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `.sp.wav` | 1 | [engines.clone_tts](../modules/engines.clone_tts.md) |
| `_cookies.txt` | 1 | [server](../modules/server.md) |
| `_f5.wav` | 1 | [server](../modules/server.md) |
| `_hg_title_cache.json` | 1 | [engines.title_mt](../modules/engines.title_mt.md) |
| `_job.json` | 1 | [engines.clone_tts](../modules/engines.clone_tts.md) |
| `_meta.json` | 1 | [scripts.brain_build](../modules/scripts.brain_build.md) |
| `_vieneu_job.json` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `a.json` | 1 | [scripts.check_batch3](../modules/scripts.check_batch3.md) |
| `a.wav` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `active.json` | 1 | [tools.preset_switcher](../modules/tools.preset_switcher.md) |
| `agent_brain.log` | 1 | [agent_brain](../modules/agent_brain.md) |
| `agent_brain_last_snapshot.json` | 1 | [agent_brain](../modules/agent_brain.md) |
| `agent_brain_state.json` | 1 | [agent_brain](../modules/agent_brain.md) |
| `agent_watch.log` | 1 | [agents.agent_watch](../modules/agents.agent_watch.md) |
| `agent_watch_state.json` | 1 | [agents.agent_watch](../modules/agents.agent_watch.md) |
| `asr.aligned_fa.meta.json` | 1 | [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md) |
| `asr.aligned_fix.meta.json` | 1 | [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md) |
| `asr.aligned_n1.json` | 1 | [server](../modules/server.md) |
| `asr.chars.json` | 1 | [engines.asr.paraformer_zh](../modules/engines.asr.paraformer_zh.md) |
| `asr.fun_nano_retry.json` | 1 | [server](../modules/server.md) |
| `audio.partial.wav` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `audio_resume.wav` | 1 | [engines.asr.asr](../modules/engines.asr.asr.md) |
| `b.wav` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `batch_config2.json` | 1 | [scripts.check_batch3](../modules/scripts.check_batch3.md) |
| `bgm.wav` | 1 | [server](../modules/server.md) |
| `brain_pending_decisions.json` | 1 | [agent_brain](../modules/agent_brain.md) |
| `c.wav` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `canva_config.json` | 1 | [agents.canva_client](../modules/agents.canva_client.md) |
| `canva_pkce.json` | 1 | [agents.canva_client](../modules/agents.canva_client.md) |
| `canva_token.json` | 1 | [agents.canva_client](../modules/agents.canva_client.md) |
| `chunks_meta.json` | 1 | [engines.separate](../modules/engines.separate.md) |
| `cnt.txt` | 1 | [scripts.check_batch3](../modules/scripts.check_batch3.md) |
| `concat.txt` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `dub.wav` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `dub_fit.partial.wav` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `f5_voices.json` | 1 | [engines.clone_tts](../modules/engines.clone_tts.md) |
| `full_merged.mp4` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `migrate_work.log` | 1 | [tools.migrate_work](../modules/tools.migrate_work.md) |
| `migrate_work.prev.log` | 1 | [tools.migrate_work](../modules/tools.migrate_work.md) |
| `migrate_work_plan.json` | 1 | [tools.migrate_work](../modules/tools.migrate_work.md) |
| `models.json` | 1 | [tools.preset_switcher](../modules/tools.preset_switcher.md) |
| `nope.mp4` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `pronoun_lock.json` | 1 | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) |
| `pronoun_qa.json` | 1 | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) |
| `qa_hang_trace.json` | 1 | [agent_hang_fix](../modules/agent_hang_fix.md) |
| `ref.wav` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `restart_pending.json` | 1 | [restart_server](../modules/restart_server.md) |
| `review_pass1.json` | 1 | [translate](../modules/translate.md) |
| `s.json` | 1 | [scripts.check_batch3](../modules/scripts.check_batch3.md) |
| `s.mp4` | 1 | [tools.lib_check](../modules/tools.lib_check.md) |
| `seg_0001.wav` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `sfx_levels.json` | 1 | [engines.sfx_lib](../modules/engines.sfx_lib.md) |
| `sfx_lib.json` | 1 | [engines.sfx_lib](../modules/engines.sfx_lib.md) |
| `source.info.json` | 1 | [engines.download](../modules/engines.download.md) |
| `source.m4a` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `sub.review_pair.srt` | 1 | [translate](../modules/translate.md) |
| `sub.vi.burn.follow.ass` | 1 | [agents.agent_heal](../modules/agents.agent_heal.md) |
| `sub.zh.aligned_fa.srt` | 1 | [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md) |
| `sub.zh.aligned_fix.srt` | 1 | [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md) |
| `sub.zh.aligned_repaired.srt` | 1 | [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md) |
| `sub.zh.analyze.txt` | 1 | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) |
| `sub.zh.hardsub.srt` | 1 | [engines.asr.hardsub_asr](../modules/engines.asr.hardsub_asr.md) |
| `sub.zh.nano_fa.srt` | 1 | [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md) |
| `trailer.mp4` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `v.mp4` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `x.json` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `zh_full_for_pronoun.txt` | 1 | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) |
| `第001集.mp4` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `第002集.mp4` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
