# File/artifact & cổng — ai đụng tới

_Sinh tự động bởi `scripts/brain_build.py` lúc 2026-11-17 19:05. Đừng sửa tay — chạy lại script._


Dùng để trả lời: *file `X.json` do ai ghi/đọc?* (chỉ là chuỗi literal xuất hiện trong code). Artifact dùng bởi ≥2 module là điểm có thể race khi ghi.

## Cổng

| Cổng | Module |
|---|---|
| 3377 | [agents.agent_brain](../modules/agents.agent_brain.md), [agents.agent_brain_context](../modules/agents.agent_brain_context.md), [agents.meta_studio](../modules/agents.meta_studio.md), [core.machine](../modules/core.machine.md), [engines.llm](../modules/engines.llm.md) |
| 8000 | [agents.agent_brain_context](../modules/agents.agent_brain_context.md), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md), [core.machine](../modules/core.machine.md), [server](../modules/server.md) |
| 8083 | [agents.agent_brain](../modules/agents.agent_brain.md), [agents.agent_brain_context](../modules/agents.agent_brain_context.md), [agents.uploader_settings_api](../modules/agents.uploader_settings_api.md), [core.config](../modules/core.config.md), [core.machine](../modules/core.machine.md), [engines.llm](../modules/engines.llm.md), [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) |
| 8801 | [agents.agent_autopilot](../modules/agents.agent_autopilot.md), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md), [agents.agent_tool_loop](../modules/agents.agent_tool_loop.md), [scripts.check_batch2](../modules/scripts.check_batch2.md), [scripts.check_batch3](../modules/scripts.check_batch3.md), [scripts.check_batch5](../modules/scripts.check_batch5.md), [tools.migrate_work](../modules/tools.migrate_work.md) |
| 8802 | [agents.agent_brain](../modules/agents.agent_brain.md), [agents.agent_brain_context](../modules/agents.agent_brain_context.md), [agents.agent_core](../modules/agents.agent_core.md), [agents.agent_feeder](../modules/agents.agent_feeder.md), [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md), [agents.canva_client](../modules/agents.canva_client.md), [restart_server](../modules/restart_server.md), [scripts.check_batch2](../modules/scripts.check_batch2.md), [tools.migrate_work](../modules/tools.migrate_work.md) |
| 8804 | [http_routes.routes_films](../modules/http_routes.routes_films.md) |
| 11434 | [engines.llm](../modules/engines.llm.md), [scripts.check_batch2](../modules/scripts.check_batch2.md) |

## Artifact

| File | Số module | Module |
|---|---:|---|
| `manifest.json` | 36 | [agents.agent_autopilot](../modules/agents.agent_autopilot.md), [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_brain](../modules/agents.agent_brain.md), [agents.agent_brain_context](../modules/agents.agent_brain_context.md), [agents.agent_core](../modules/agents.agent_core.md), [agents.agent_feeder](../modules/agents.agent_feeder.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_hold](../modules/agents.agent_hold.md), [agents.agent_qa_ask](../modules/agents.agent_qa_ask.md), [agents.agent_retry](../modules/agents.agent_retry.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [agents.agent_tool_loop](../modules/agents.agent_tool_loop.md), [agents.agent_watch](../modules/agents.agent_watch.md), [agents.auto_publisher](../modules/agents.auto_publisher.md), [agents.films_merge_api](../modules/agents.films_merge_api.md), [agents.meta_studio](../modules/agents.meta_studio.md), [core.film_db](../modules/core.film_db.md), [core.job_queue](../modules/core.job_queue.md), [core.manifest](../modules/core.manifest.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.series_glossary](../modules/engines.series_glossary.md), [engines.source_preflight](../modules/engines.source_preflight.md), [engines.split_parts](../modules/engines.split_parts.md), [engines.translate_simple.cfg](../modules/engines.translate_simple.cfg.md), [engines.translate_simple.pipeline](../modules/engines.translate_simple.pipeline.md), [http_routes.routes_agent](../modules/http_routes.routes_agent.md), [restart_server](../modules/restart_server.md), [scripts.check_batch1](../modules/scripts.check_batch1.md), [scripts.check_batch3](../modules/scripts.check_batch3.md), [scripts.check_batch4](../modules/scripts.check_batch4.md), [server](../modules/server.md), [tools.asr_boundary_scan](../modules/tools.asr_boundary_scan.md), [tools.collect_manual_edits](../modules/tools.collect_manual_edits.md), [tools.migrate_work](../modules/tools.migrate_work.md), [tools.preflight_scan](../modules/tools.preflight_scan.md), [tools.simple_stats](../modules/tools.simple_stats.md) |
| `script.json` | 32 | [agents.agent_brain](../modules/agents.agent_brain.md), [agents.agent_brain_context](../modules/agents.agent_brain_context.md), [agents.agent_core](../modules/agents.agent_core.md), [agents.agent_feeder](../modules/agents.agent_feeder.md), [agents.agent_hang_fix](../modules/agents.agent_hang_fix.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_name_pass](../modules/agents.agent_name_pass.md), [agents.agent_pronoun_pass](../modules/agents.agent_pronoun_pass.md), [agents.agent_qa_ask](../modules/agents.agent_qa_ask.md), [agents.agent_qa_fix](../modules/agents.agent_qa_fix.md), [agents.agent_qa_gate](../modules/agents.agent_qa_gate.md), [agents.agent_quality](../modules/agents.agent_quality.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [agents.meta_studio](../modules/agents.meta_studio.md), [core.job_queue](../modules/core.job_queue.md), [engines.asr.hardsub_asr](../modules/engines.asr.hardsub_asr.md), [engines.clone_tts](../modules/engines.clone_tts.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md), [engines.render](../modules/engines.render.md), [engines.script_lint](../modules/engines.script_lint.md), [engines.translate](../modules/engines.translate.md), [engines.translate_alts](../modules/engines.translate_alts.md), [engines.translate_simple.cfg](../modules/engines.translate_simple.cfg.md), [engines.translate_simple.pipeline](../modules/engines.translate_simple.pipeline.md), [engines.translate_simple.script_store](../modules/engines.translate_simple.script_store.md), [http_routes.routes_agent](../modules/http_routes.routes_agent.md), [scripts.check_batch1](../modules/scripts.check_batch1.md), [scripts.check_batch4](../modules/scripts.check_batch4.md), [server](../modules/server.md), [tools.collect_manual_edits](../modules/tools.collect_manual_edits.md), [tools.simple_stats](../modules/tools.simple_stats.md) |
| `asr.json` | 21 | [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.asr.asr](../modules/engines.asr.asr.md), [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md), [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md), [engines.asr.fun_asr_nano](../modules/engines.asr.fun_asr_nano.md), [engines.asr.hardsub_asr](../modules/engines.asr.hardsub_asr.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md), [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md), [engines.asr.paraformer_zh](../modules/engines.asr.paraformer_zh.md), [engines.asr.sensevoice_asr](../modules/engines.asr.sensevoice_asr.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.ocr](../modules/engines.ocr.md), [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md), [engines.split_parts](../modules/engines.split_parts.md), [engines.translate](../modules/engines.translate.md), [engines.translate_simple.pipeline](../modules/engines.translate_simple.pipeline.md), [scripts.test_deepseek_plan](../modules/scripts.test_deepseek_plan.md), [server](../modules/server.md), [tools.asr_boundary_scan](../modules/tools.asr_boundary_scan.md) |
| `output.mp4` | 17 | [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_brain](../modules/agents.agent_brain.md), [agents.agent_brain_context](../modules/agents.agent_brain_context.md), [agents.agent_core](../modules/agents.agent_core.md), [agents.agent_feeder](../modules/agents.agent_feeder.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_hold](../modules/agents.agent_hold.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [agents.auto_publisher](../modules/agents.auto_publisher.md), [agents.films_merge_api](../modules/agents.films_merge_api.md), [agents.meta_studio](../modules/agents.meta_studio.md), [core.job_queue](../modules/core.job_queue.md), [engines.mux](../modules/engines.mux.md), [engines.render](../modules/engines.render.md), [engines.split_parts](../modules/engines.split_parts.md), [scripts.check_batch1](../modules/scripts.check_batch1.md), [server](../modules/server.md) |
| `glossary.json` | 16 | [agents.agent_name_pass](../modules/agents.agent_name_pass.md), [agents.agent_pronoun_pass](../modules/agents.agent_pronoun_pass.md), [agents.agent_qa_gate](../modules/agents.agent_qa_gate.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md), [engines.script_lint](../modules/engines.script_lint.md), [engines.series_glossary](../modules/engines.series_glossary.md), [engines.translate](../modules/engines.translate.md), [engines.translate_alts](../modules/engines.translate_alts.md), [engines.translate_simple.pipeline](../modules/engines.translate_simple.pipeline.md), [engines.translate_simple.stage_draft](../modules/engines.translate_simple.stage_draft.md), [engines.translate_simple.zh_source](../modules/engines.translate_simple.zh_source.md), [server](../modules/server.md), [tools.collect_manual_edits](../modules/tools.collect_manual_edits.md), [tools.context_studio.app_streamlit](../modules/tools.context_studio.app_streamlit.md), [tools.context_studio.exporter](../modules/tools.context_studio.exporter.md) |
| `sub.vi.srt` | 14 | [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_feeder](../modules/agents.agent_feeder.md), [agents.agent_hang_fix](../modules/agents.agent_hang_fix.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_pronoun_pass](../modules/agents.agent_pronoun_pass.md), [agents.agent_qa_ask](../modules/agents.agent_qa_ask.md), [agents.agent_qa_fix](../modules/agents.agent_qa_fix.md), [agents.meta_studio](../modules/agents.meta_studio.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.render](../modules/engines.render.md), [engines.script_lint](../modules/engines.script_lint.md), [engines.translate](../modules/engines.translate.md), [engines.translate_simple.pipeline](../modules/engines.translate_simple.pipeline.md), [server](../modules/server.md) |
| `audio.wav` | 13 | [agents.agent_heal](../modules/agents.agent_heal.md), [engines.asr.asr](../modules/engines.asr.asr.md), [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md), [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md), [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md), [engines.asr.fun_asr_nano](../modules/engines.asr.fun_asr_nano.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md), [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md), [engines.asr.paraformer_zh](../modules/engines.asr.paraformer_zh.md), [engines.asr.sensevoice_asr](../modules/engines.asr.sensevoice_asr.md), [engines.media_ts](../modules/engines.media_ts.md), [scripts.check_batch1](../modules/scripts.check_batch1.md), [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `sub.zh.srt` | 13 | [agents.agent_heal](../modules/agents.agent_heal.md), [engines.asr.asr](../modules/engines.asr.asr.md), [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md), [engines.asr.fun_asr_nano](../modules/engines.asr.fun_asr_nano.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md), [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md), [engines.asr.paraformer_zh](../modules/engines.asr.paraformer_zh.md), [engines.asr.sensevoice_asr](../modules/engines.asr.sensevoice_asr.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md), [engines.split_parts](../modules/engines.split_parts.md), [server](../modules/server.md) |
| `tts.json` | 12 | [agents.agent_brain](../modules/agents.agent_brain.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.assemble](../modules/engines.assemble.md), [engines.clone_tts](../modules/engines.clone_tts.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.mux](../modules/engines.mux.md), [engines.render](../modules/engines.render.md), [http_routes.routes_agent](../modules/http_routes.routes_agent.md), [scripts.check_batch1](../modules/scripts.check_batch1.md), [scripts.check_batch4](../modules/scripts.check_batch4.md), [server](../modules/server.md) |
| `dub_fit.wav` | 9 | [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_brain](../modules/agents.agent_brain.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.assemble](../modules/engines.assemble.md), [engines.mux](../modules/engines.mux.md), [engines.render](../modules/engines.render.md), [scripts.check_batch4](../modules/scripts.check_batch4.md), [server](../modules/server.md) |
| `script.display.json` | 8 | [agents.agent_heal](../modules/agents.agent_heal.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.render](../modules/engines.render.md), [engines.script_lint](../modules/engines.script_lint.md), [engines.translate](../modules/engines.translate.md), [engines.translate_simple.pipeline](../modules/engines.translate_simple.pipeline.md), [scripts.check_batch1](../modules/scripts.check_batch1.md), [server](../modules/server.md) |
| `tts_config.json` | 7 | [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_hongguo](../modules/agents.agent_hongguo.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.clone_tts](../modules/engines.clone_tts.md), [engines.split_parts](../modules/engines.split_parts.md), [scripts.check_batch4](../modules/scripts.check_batch4.md), [server](../modules/server.md) |
| `asr.fun_nano.json` | 6 | [engines.asr.asr_align_nano_para](../modules/engines.asr.asr_align_nano_para.md), [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md), [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md), [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md), [server](../modules/server.md) |
| `context_pack.json` | 6 | [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.translate](../modules/engines.translate.md), [engines.translate_alts](../modules/engines.translate_alts.md), [engines.translate_simple.stage_draft](../modules/engines.translate_simple.stage_draft.md), [server](../modules/server.md), [tools.context_studio.exporter](../modules/tools.context_studio.exporter.md) |
| `output.partial.mp4` | 6 | [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_brain](../modules/agents.agent_brain.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_retry](../modules/agents.agent_retry.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [server](../modules/server.md) |
| `vocals.wav` | 6 | [engines.asr.asr](../modules/engines.asr.asr.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.render](../modules/engines.render.md), [engines.separate](../modules/engines.separate.md), [scripts.check_batch4](../modules/scripts.check_batch4.md), [server](../modules/server.md) |
| `asr.paraformer_zh.json` | 5 | [engines.asr.asr_align_nano_para](../modules/engines.asr.asr_align_nano_para.md), [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md), [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md), [server](../modules/server.md) |
| `no_vocals.wav` | 5 | [engines.media_ts](../modules/engines.media_ts.md), [engines.render](../modules/engines.render.md), [engines.separate](../modules/engines.separate.md), [scripts.check_batch4](../modules/scripts.check_batch4.md), [server](../modules/server.md) |
| `ocr.json` | 5 | [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.ocr](../modules/engines.ocr.md), [engines.render](../modules/engines.render.md), [engines.translate](../modules/engines.translate.md), [server](../modules/server.md) |
| `style_lock.json` | 5 | [agents.agent_qa_gate](../modules/agents.agent_qa_gate.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.translate](../modules/engines.translate.md), [engines.translate_simple.stage_draft](../modules/engines.translate_simple.stage_draft.md), [tools.context_studio.exporter](../modules/tools.context_studio.exporter.md) |
| `sub.vi.burn.srt` | 5 | [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_heal](../modules/agents.agent_heal.md), [agents.meta_studio](../modules/agents.meta_studio.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.render](../modules/engines.render.md) |
| `tts_fit.json` | 5 | [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_heal](../modules/agents.agent_heal.md), [engines.assemble](../modules/engines.assemble.md), [engines.render](../modules/engines.render.md), [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `.progress.json` | 4 | [engines.asr.asr_hybrid_progress](../modules/engines.asr.asr_hybrid_progress.md), [engines.asr.fun_asr_nano](../modules/engines.asr.fun_asr_nano.md), [engines.asr.paraformer_zh](../modules/engines.asr.paraformer_zh.md), [engines.asr.sensevoice_asr](../modules/engines.asr.sensevoice_asr.md) |
| `asr.aligned.json` | 4 | [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md), [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md), [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [server](../modules/server.md) |
| `asr.aligned_fa.json` | 4 | [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md), [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md), [server](../modules/server.md) |
| `asr.aligned_fix.json` | 4 | [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md), [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md), [server](../modules/server.md) |
| `client_secret.json` | 4 | [agents.auto_publisher](../modules/agents.auto_publisher.md), [agents.test_channel](../modules/agents.test_channel.md), [scripts.check_env](../modules/scripts.check_env.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `config.json` | 4 | [core.config](../modules/core.config.md), [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md), [scripts.check_batch2](../modules/scripts.check_batch2.md), [scripts.check_env](../modules/scripts.check_env.md) |
| `dub_tts.wav` | 4 | [agents.agent_brain](../modules/agents.agent_brain.md), [engines.assemble](../modules/engines.assemble.md), [engines.render](../modules/engines.render.md), [server](../modules/server.md) |
| `hardsub_band.json` | 4 | [engines.asr.hardsub_asr](../modules/engines.asr.hardsub_asr.md), [engines.hs_ocr_fast](../modules/engines.hs_ocr_fast.md), [engines.render](../modules/engines.render.md), [engines.translate_simple.zh_source](../modules/engines.translate_simple.zh_source.md) |
| `meta.json` | 4 | [engines.download](../modules/engines.download.md), [engines.render](../modules/engines.render.md), [server](../modules/server.md), [tools.collect_manual_edits](../modules/tools.collect_manual_edits.md) |
| `mixed_audio.partial.wav` | 4 | [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_brain](../modules/agents.agent_brain.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.render](../modules/engines.render.md) |
| `mixed_audio.wav` | 4 | [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_brain](../modules/agents.agent_brain.md), [engines.media_ts](../modules/engines.media_ts.md), [engines.render](../modules/engines.render.md) |
| `output_full.mp4` | 4 | [agents.agent_hold](../modules/agents.agent_hold.md), [agents.films_merge_api](../modules/agents.films_merge_api.md), [engines.split_parts](../modules/engines.split_parts.md), [server](../modules/server.md) |
| `pineline.config.json` | 4 | [agents.uploader_settings_api](../modules/agents.uploader_settings_api.md), [core.config](../modules/core.config.md), [scripts.check_batch3](../modules/scripts.check_batch3.md), [scripts.check_env](../modules/scripts.check_env.md) |
| `qa_flags.json` | 4 | [agents.agent_qa_gate](../modules/agents.agent_qa_gate.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [server](../modules/server.md), [tools.context_studio.exporter](../modules/tools.context_studio.exporter.md) |
| `queue_state.json` | 4 | [agents.uploader_settings_api](../modules/agents.uploader_settings_api.md), [core.film_db](../modules/core.film_db.md), [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md), [tools.lib_check](../modules/tools.lib_check.md) |
| `source.mp4` | 4 | [agents.agent_av_sync](../modules/agents.agent_av_sync.md), [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [engines.download](../modules/engines.download.md), [server](../modules/server.md) |
| `upload_history.jsonl` | 4 | [agents.auto_publisher](../modules/agents.auto_publisher.md), [agents.uploader_settings_api](../modules/agents.uploader_settings_api.md), [core.film_db](../modules/core.film_db.md), [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) |
| `.series.json` | 3 | [agents.agent_feeder](../modules/agents.agent_feeder.md), [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md), [agents.meta_studio](../modules/agents.meta_studio.md) |
| `_filter_complex.txt` | 3 | [agents.agent_brain](../modules/agents.agent_brain.md), [agents.agent_heal](../modules/agents.agent_heal.md), [engines.render](../modules/engines.render.md) |
| `asr.aligned_repaired.json` | 3 | [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md), [server](../modules/server.md) |
| `asr.hardsub.json` | 3 | [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [engines.asr.hardsub_asr](../modules/engines.asr.hardsub_asr.md), [server](../modules/server.md) |
| `asr.paraformer_zh.chars.json` | 3 | [engines.asr.asr_align_nano_para](../modules/engines.asr.asr_align_nano_para.md), [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md), [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md) |
| `hardsub_cues.json` | 3 | [engines.asr.hardsub_asr](../modules/engines.asr.hardsub_asr.md), [engines.hs_ocr_fast](../modules/engines.hs_ocr_fast.md), [server](../modules/server.md) |
| `qa_brain.json` | 3 | [agents.agent_brain_context](../modules/agents.agent_brain_context.md), [agents.agent_hold](../modules/agents.agent_hold.md), [agents.agent_quality](../modules/agents.agent_quality.md) |
| `script.pre_review.json` | 3 | [agents.agent_heal](../modules/agents.agent_heal.md), [agents.agent_qa_gate](../modules/agents.agent_qa_gate.md), [engines.media_ts](../modules/engines.media_ts.md) |
| `token.json` | 3 | [agents.auto_publisher](../modules/agents.auto_publisher.md), [agents.test_channel](../modules/agents.test_channel.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `.meta.json` | 2 | [engines.asr.asr_align_nano_para](../modules/engines.asr.asr_align_nano_para.md), [engines.asr.asr_repair](../modules/engines.asr.asr_repair.md) |
| `.partial.mp4` | 2 | [agents.agent_feeder](../modules/agents.agent_feeder.md), [engines.render](../modules/engines.render.md) |
| `.tmp.mp4` | 2 | [agents.hg_merge_check](../modules/agents.hg_merge_check.md), [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md) |
| `.upload.lock` | 2 | [agents.auto_publisher](../modules/agents.auto_publisher.md), [core.film_db](../modules/core.film_db.md) |
| `_job_queue.json` | 2 | [core.job_queue](../modules/core.job_queue.md), [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `_keys.json` | 2 | [engines.clone_tts](../modules/engines.clone_tts.md), [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `active.json` | 2 | [core.machine](../modules/core.machine.md), [tools.preset_switcher](../modules/tools.preset_switcher.md) |
| `agent_brain.log` | 2 | [agents.agent_brain](../modules/agents.agent_brain.md), [agents.agent_hold](../modules/agents.agent_hold.md) |
| `asr.consensus.json` | 2 | [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [server](../modules/server.md) |
| `asr.firered.json` | 2 | [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [server](../modules/server.md) |
| `asr.nano_fa.json` | 2 | [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md), [server](../modules/server.md) |
| `asr.sensevoice.json` | 2 | [engines.asr.asr_spam](../modules/engines.asr.asr_spam.md), [server](../modules/server.md) |
| `audio.ts.wav` | 2 | [engines.media_ts](../modules/engines.media_ts.md), [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `audio.wav.json` | 2 | [agents.agent_heal](../modules/agents.agent_heal.md), [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `autopilot_state.json` | 2 | [agents.agent_autopilot](../modules/agents.agent_autopilot.md), [scripts.check_batch3](../modules/scripts.check_batch3.md) |
| `batch_config.json` | 2 | [core.batch_config](../modules/core.batch_config.md), [scripts.check_batch3](../modules/scripts.check_batch3.md) |
| `brain.json` | 2 | [scripts.brain_export](../modules/scripts.brain_export.md), [scripts.build_workflow_html](../modules/scripts.build_workflow_html.md) |
| `channel.json` | 2 | [agents.test_channel](../modules/agents.test_channel.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `channel_limit.json` | 2 | [agents.test_channel](../modules/agents.test_channel.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `chatgpt_token.txt` | 2 | [agents.meta_studio](../modules/agents.meta_studio.md), [engines.llm](../modules/engines.llm.md) |
| `code_verifier.txt` | 2 | [agents.test_channel](../modules/agents.test_channel.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `current_oauth_project.txt` | 2 | [agents.test_channel](../modules/agents.test_channel.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `exhausted.json` | 2 | [agents.test_channel](../modules/agents.test_channel.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `feeder_state.json` | 2 | [agents.agent_feeder](../modules/agents.agent_feeder.md), [tools.lib_check](../modules/tools.lib_check.md) |
| `hardsub_track.json` | 2 | [engines.render](../modules/engines.render.md), [engines.translate_simple.zh_source](../modules/engines.translate_simple.zh_source.md) |
| `list.txt` | 2 | [agents.hg_merge_check](../modules/agents.hg_merge_check.md), [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md) |
| `merge_check.json` | 2 | [agents.hg_merge_check](../modules/agents.hg_merge_check.md), [engines.lib_normalize](../modules/engines.lib_normalize.md) |
| `merged.mp4` | 2 | [engines.lib_normalize](../modules/engines.lib_normalize.md), [http_routes.routes_hg](../modules/http_routes.routes_hg.md) |
| `mixed_audio.json` | 2 | [engines.render](../modules/engines.render.md), [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `models.json` | 2 | [core.machine](../modules/core.machine.md), [tools.preset_switcher](../modules/tools.preset_switcher.md) |
| `orig_audio.wav` | 2 | [engines.media_ts](../modules/engines.media_ts.md), [engines.separate](../modules/engines.separate.md) |
| `plan_inferred.json` | 2 | [engines.translate_simple.pipeline](../modules/engines.translate_simple.pipeline.md), [tools.simple_stats](../modules/tools.simple_stats.md) |
| `plan_suggestions.json` | 2 | [engines.translate_simple.suggest](../modules/engines.translate_simple.suggest.md), [tools.simple_stats](../modules/tools.simple_stats.md) |
| `projects.json` | 2 | [agents.test_channel](../modules/agents.test_channel.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `projects_health.json` | 2 | [agents.test_channel](../modules/agents.test_channel.md), [tools.test_channel](../modules/tools.test_channel.md) |
| `relation_matrix.json` | 2 | [agents.agent_stage_io](../modules/agents.agent_stage_io.md), [tools.context_studio.exporter](../modules/tools.context_studio.exporter.md) |
| `script.pre_agent_review.json` | 2 | [agents.agent_heal](../modules/agents.agent_heal.md), [server](../modules/server.md) |
| `seg_0000.wav` | 2 | [engines.clone_tts](../modules/engines.clone_tts.md), [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `settings.json` | 2 | [agents.uploader_settings_api](../modules/agents.uploader_settings_api.md), [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) |
| `trace.1.jsonl` | 2 | [engines.translate_simple.script_store](../modules/engines.translate_simple.script_store.md), [tools.collect_manual_edits](../modules/tools.collect_manual_edits.md) |
| `trace.jsonl` | 2 | [engines.translate_simple.script_store](../modules/engines.translate_simple.script_store.md), [tools.collect_manual_edits](../modules/tools.collect_manual_edits.md) |
| `vi_alts.json` | 2 | [engines.translate_alts](../modules/engines.translate_alts.md), [server](../modules/server.md) |
| `.alt.wav` | 1 | [engines.media_ts](../modules/engines.media_ts.md) |
| `.audio_ts_fixed.json` | 1 | [engines.media_ts](../modules/engines.media_ts.md) |
| `.audio_ts_pending.json` | 1 | [engines.media_ts](../modules/engines.media_ts.md) |
| `.auto_publish_global.lock` | 1 | [agents.auto_publisher](../modules/agents.auto_publisher.md) |
| `.bak.json` | 1 | [server](../modules/server.md) |
| `.chars.json` | 1 | [engines.asr.paraformer_zh](../modules/engines.asr.paraformer_zh.md) |
| `.cl.wav` | 1 | [engines.clone_tts](../modules/engines.clone_tts.md) |
| `.concat.txt` | 1 | [engines.media_ts](../modules/engines.media_ts.md) |
| `.follow.ass` | 1 | [engines.render](../modules/engines.render.md) |
| `.norm.partial.mp4` | 1 | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md) |
| `.norm.tmp.mp4` | 1 | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md) |
| `.nvenc_state.json` | 1 | [engines.render](../modules/engines.render.md) |
| `.preflight.lock` | 1 | [engines.source_preflight](../modules/engines.source_preflight.md) |
| `.server_test.lock` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `.sidecar_18902.lock` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `.sp.wav` | 1 | [engines.clone_tts](../modules/engines.clone_tts.md) |
| `.tmp.txt` | 1 | [agents.hongguo_license_ensure](../modules/agents.hongguo_license_ensure.md) |
| `_audio.m4a` | 1 | [engines.render](../modules/engines.render.md) |
| `_chunks.txt` | 1 | [engines.render](../modules/engines.render.md) |
| `_cookies.txt` | 1 | [server](../modules/server.md) |
| `_f5.wav` | 1 | [server](../modules/server.md) |
| `_hg_title_cache.json` | 1 | [engines.title_mt](../modules/engines.title_mt.md) |
| `_job.json` | 1 | [engines.clone_tts](../modules/engines.clone_tts.md) |
| `_meta.json` | 1 | [scripts.brain_build](../modules/scripts.brain_build.md) |
| `_sample90s.mp4` | 1 | [agents.agent_feeder](../modules/agents.agent_feeder.md) |
| `_vieneu_job.json` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `a.json` | 1 | [scripts.check_batch3](../modules/scripts.check_batch3.md) |
| `a.wav` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `agent_brain_last_snapshot.json` | 1 | [agents.agent_brain](../modules/agents.agent_brain.md) |
| `agent_brain_state.json` | 1 | [agents.agent_brain](../modules/agents.agent_brain.md) |
| `agent_watch.log` | 1 | [agents.agent_watch](../modules/agents.agent_watch.md) |
| `agent_watch_state.json` | 1 | [agents.agent_watch](../modules/agents.agent_watch.md) |
| `asr.aligned_fa.meta.json` | 1 | [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md) |
| `asr.aligned_fix.meta.json` | 1 | [engines.asr.asr_fix_align](../modules/engines.asr.asr_fix_align.md) |
| `asr.aligned_n1.json` | 1 | [server](../modules/server.md) |
| `asr.chars.json` | 1 | [engines.asr.paraformer_zh](../modules/engines.asr.paraformer_zh.md) |
| `asr.fun_nano_retry.json` | 1 | [server](../modules/server.md) |
| `asr.zhsource.json` | 1 | [engines.translate_simple.zh_source](../modules/engines.translate_simple.zh_source.md) |
| `asr16k.wav` | 1 | [engines.asr.firered_asr](../modules/engines.asr.firered_asr.md) |
| `audio.partial.wav` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `audio_resume.wav` | 1 | [engines.asr.asr](../modules/engines.asr.asr.md) |
| `audio_seek.m4a` | 1 | [engines.media_ts](../modules/engines.media_ts.md) |
| `auto_publish_config.json` | 1 | [agents.auto_publisher](../modules/agents.auto_publisher.md) |
| `auto_publish_queue.json` | 1 | [agents.auto_publisher](../modules/agents.auto_publisher.md) |
| `auto_publish_state.json` | 1 | [agents.auto_publisher](../modules/agents.auto_publisher.md) |
| `b.wav` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `batch_config2.json` | 1 | [scripts.check_batch3](../modules/scripts.check_batch3.md) |
| `bgm.wav` | 1 | [server](../modules/server.md) |
| `brain_pending_decisions.json` | 1 | [agents.agent_brain](../modules/agents.agent_brain.md) |
| `c.wav` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `canva_config.json` | 1 | [agents.canva_client](../modules/agents.canva_client.md) |
| `canva_pkce.json` | 1 | [agents.canva_client](../modules/agents.canva_client.md) |
| `canva_token.json` | 1 | [agents.canva_client](../modules/agents.canva_client.md) |
| `censor.json` | 1 | [engines.render](../modules/engines.render.md) |
| `characters.json` | 1 | [tools.collect_manual_edits](../modules/tools.collect_manual_edits.md) |
| `cnt.txt` | 1 | [scripts.check_batch3](../modules/scripts.check_batch3.md) |
| `concat.txt` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `dub.wav` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `dub_fit.partial.wav` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `f5_voices.json` | 1 | [engines.clone_tts](../modules/engines.clone_tts.md) |
| `films.db` | 1 | [core.film_db](../modules/core.film_db.md) |
| `final.mp4` | 1 | [agents.auto_publisher](../modules/agents.auto_publisher.md) |
| `full_merged.mp4` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `generation_config.json` | 1 | [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md) |
| `glossary.plan_failed.json` | 1 | [engines.translate_simple.stage_draft](../modules/engines.translate_simple.stage_draft.md) |
| `hardsub_cues.progress.json` | 1 | [engines.hs_ocr_fast](../modules/engines.hs_ocr_fast.md) |
| `hardsub_ocr.log` | 1 | [engines.hs_ocr_fast](../modules/engines.hs_ocr_fast.md) |
| `head.wav` | 1 | [engines.media_ts](../modules/engines.media_ts.md) |
| `hg_merge_state.json` | 1 | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md) |
| `hg_seasons_declined.json` | 1 | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md) |
| `hg_title_cache.json` | 1 | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md) |
| `hongguo_feed_labels.json` | 1 | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md) |
| `hongguo_play_cache.json` | 1 | [agents.hongguo_rpc](../modules/agents.hongguo_rpc.md) |
| `idioms_zh_vi.json` | 1 | [engines.translate_simple.lexicon](../modules/engines.translate_simple.lexicon.md) |
| `input.mp4` | 1 | [agents.meta_studio](../modules/agents.meta_studio.md) |
| `kVietnamese.json` | 1 | [engines.hv_auditor](../modules/engines.hv_auditor.md) |
| `lib_normalize.log` | 1 | [engines.lib_normalize](../modules/engines.lib_normalize.md) |
| `lines.gold.jsonl` | 1 | [tools.collect_manual_edits](../modules/tools.collect_manual_edits.md) |
| `list_mp4.txt` | 1 | [agents.agent_feeder](../modules/agents.agent_feeder.md) |
| `list_ts.txt` | 1 | [agents.agent_feeder](../modules/agents.agent_feeder.md) |
| `loudness.json` | 1 | [engines.render](../modules/engines.render.md) |
| `migrate_work.log` | 1 | [tools.migrate_work](../modules/tools.migrate_work.md) |
| `migrate_work.prev.log` | 1 | [tools.migrate_work](../modules/tools.migrate_work.md) |
| `migrate_work_plan.json` | 1 | [tools.migrate_work](../modules/tools.migrate_work.md) |
| `nope.mp4` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `norm_audio.wav` | 1 | [engines.source_preflight](../modules/engines.source_preflight.md) |
| `orig.wav` | 1 | [engines.separate](../modules/engines.separate.md) |
| `output.merging.mp4` | 1 | [engines.split_parts](../modules/engines.split_parts.md) |
| `pairs.json` | 1 | [tools.collect_manual_edits](../modules/tools.collect_manual_edits.md) |
| `plan.json` | 1 | [engines.separate](../modules/engines.separate.md) |
| `pronoun_lock.json` | 1 | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) |
| `pronoun_qa.json` | 1 | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) |
| `pronoun_rules_zh_vi.json` | 1 | [engines.translate_simple.pair_rules](../modules/engines.translate_simple.pair_rules.md) |
| `qa_ask.json` | 1 | [agents.agent_qa_ask](../modules/agents.agent_qa_ask.md) |
| `qa_ask_index.json` | 1 | [agents.agent_qa_ask](../modules/agents.agent_qa_ask.md) |
| `qa_fix_trace.json` | 1 | [agents.agent_qa_fix](../modules/agents.agent_qa_fix.md) |
| `qa_hang_trace.json` | 1 | [agents.agent_hang_fix](../modules/agents.agent_hang_fix.md) |
| `ref.wav` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `restart_pending.json` | 1 | [restart_server](../modules/restart_server.md) |
| `review_pass1.json` | 1 | [engines.translate](../modules/engines.translate.md) |
| `s.json` | 1 | [scripts.check_batch3](../modules/scripts.check_batch3.md) |
| `s.mp4` | 1 | [tools.lib_check](../modules/tools.lib_check.md) |
| `seg_0001.wav` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `sfx_levels.json` | 1 | [engines.sfx_lib](../modules/engines.sfx_lib.md) |
| `sfx_lib.json` | 1 | [engines.sfx_lib](../modules/engines.sfx_lib.md) |
| `source.info.json` | 1 | [engines.download](../modules/engines.download.md) |
| `source.m4a` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `split_manifest.json` | 1 | [engines.split_parts](../modules/engines.split_parts.md) |
| `sub.review_pair.srt` | 1 | [engines.translate](../modules/engines.translate.md) |
| `sub.vi.aligned.srt` | 1 | [agents.meta_studio](../modules/agents.meta_studio.md) |
| `sub.vi.burn.follow.ass` | 1 | [agents.agent_heal](../modules/agents.agent_heal.md) |
| `sub.zh.aligned_fa.srt` | 1 | [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md) |
| `sub.zh.aligned_fix.srt` | 1 | [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md) |
| `sub.zh.aligned_repaired.srt` | 1 | [engines.asr.hybrid_asr](../modules/engines.asr.hybrid_asr.md) |
| `sub.zh.analyze.txt` | 1 | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) |
| `sub.zh.hardsub.srt` | 1 | [engines.asr.hardsub_asr](../modules/engines.asr.hardsub_asr.md) |
| `sub.zh.nano_fa.srt` | 1 | [engines.asr.nano_fa_asr](../modules/engines.asr.nano_fa_asr.md) |
| `summary.json` | 1 | [tools.collect_manual_edits](../modules/tools.collect_manual_edits.md) |
| `sync_report.json` | 1 | [scripts.sync_from_v2](../modules/scripts.sync_from_v2.md) |
| `tele_chat_history.json` | 1 | [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md) |
| `tokenizer_config.json` | 1 | [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md) |
| `trailer.mp4` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `v.mp4` | 1 | [scripts.check_batch4](../modules/scripts.check_batch4.md) |
| `video.mp4` | 1 | [agents.meta_studio](../modules/agents.meta_studio.md) |
| `vocab.json` | 1 | [engines.mt_zh_vi](../modules/engines.mt_zh_vi.md) |
| `x.json` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `zh_full_for_pronoun.txt` | 1 | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) |
| `zh_source.json` | 1 | [engines.translate_simple.zh_source](../modules/engines.translate_simple.zh_source.md) |
| `第001集.mp4` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
| `第002集.mp4` | 1 | [scripts.check_batch1](../modules/scripts.check_batch1.md) |
