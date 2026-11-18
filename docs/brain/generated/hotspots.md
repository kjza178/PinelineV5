# Hotspots — nơi nên soi bug/refactor trước

_Sinh tự động bởi `scripts/brain_build.py` lúc 2026-11-17 19:05. Đừng sửa tay — chạy lại script._


Điểm = LOC/500 + 2×fix log + 0.15×nhắc CHANGELOG + 1×hàm dài + 0.1×`except Exception` + 1×bare except + 0.5×nuốt lỗi (`except: pass`) + 0.5×Thread + 0.3×`global` + 3 nếu >800 dòng mà không test.
Đây là **heuristic để ưu tiên**, không phải kết luận có bug.

| # | Module | Điểm | Dòng | Fix | Hàm dài | broad/bare/swallow except | Thread | Test |
|---:|---|---:|---:|---:|---:|---|---:|---|
| 1 | [server](../modules/server.md) | 166.1 | 7322 | 40 | 6 | 235/0/74 | 0 | ✅ |
| 2 | [engines.translate](../modules/engines.translate.md) | 79.1 | 5172 | 23 | 7 | 71/0/14 | 0 | ✅ |
| 3 | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md) | 61.1 | 3676 | 14 | 4 | 66/0/23 | 1 | ✅ |
| 4 | [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md) | 58.6 | 2469 | 15 | 4 | 61/0/10 | 12 | ✅ |
| 5 | [engines.render](../modules/engines.render.md) | 57.2 | 3148 | 15 | 7 | 34/0/15 | 1 | ✅ |
| 6 | [agents.agent_feeder](../modules/agents.agent_feeder.md) | 40.5 | 2066 | 7 | 4 | 40/0/20 | 0 | ❌ |
| 7 | [agents.hongguo_rpc](../modules/agents.hongguo_rpc.md) | 36.9 | 1435 | 10 | 0 | 21/0/8 | 5 | ❌ |
| 8 | [agents.auto_publisher](../modules/agents.auto_publisher.md) | 35.4 | 1567 | 6 | 1 | 44/0/25 | 2 | ✅ |
| 9 | [core.job_queue](../modules/core.job_queue.md) | 33.7 | 667 | 13 | 0 | 10/0/2 | 1 | ✅ |
| 10 | [agents.agent_brain](../modules/agents.agent_brain.md) | 32.1 | 2201 | 5 | 3 | 65/0/13 | 1 | ✅ |
| 11 | [agents.meta_studio](../modules/agents.meta_studio.md) | 30.7 | 2084 | 4 | 5 | 39/0/18 | 0 | ✅ |
| 12 | [agents.test_channel](../modules/agents.test_channel.md) | 25.9 | 1444 | 3 | 0 | 35/0/16 | 2 | ❌ |
| 13 | [tools.test_channel](../modules/tools.test_channel.md) | 25.9 | 1444 | 3 | 0 | 35/0/16 | 2 | ❌ |
| 14 | [agents.agent_hongguo](../modules/agents.agent_hongguo.md) | 24.4 | 1570 | 3 | 1 | 33/0/12 | 1 | ❌ |
| 15 | [engines.split_parts](../modules/engines.split_parts.md) | 22.1 | 1105 | 7 | 3 | 14/0/2 | 0 | ✅ |
| 16 | [core.film_db](../modules/core.film_db.md) | 22.0 | 1091 | 6 | 0 | 19/0/11 | 0 | ✅ |
| 17 | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | 21.9 | 1107 | 6 | 0 | 56/0/3 | 0 | ✅ |
| 18 | [agents.agent_core](../modules/agents.agent_core.md) | 20.6 | 2115 | 6 | 1 | 6/0/1 | 0 | ✅ |
| 19 | [engines.llm](../modules/engines.llm.md) | 20.6 | 1167 | 5 | 1 | 31/0/5 | 0 | ✅ |
| 20 | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | 19.7 | 815 | 6 | 0 | 33/0/4 | 0 | ✅ |
| 21 | [restart_server](../modules/restart_server.md) | 19.2 | 263 | 8 | 0 | 6/0/0 | 0 | ❌ |
| 22 | [agents.agent_heal](../modules/agents.agent_heal.md) | 18.8 | 830 | 3 | 3 | 22/0/11 | 0 | ✅ |
| 23 | [agents.agent_autopilot](../modules/agents.agent_autopilot.md) | 14.6 | 348 | 6 | 0 | 6/0/0 | 0 | ✅ |
| 24 | [engines.asr.asr](../modules/engines.asr.asr.md) | 14.5 | 493 | 4 | 1 | 11/0/4 | 1 | ✅ |
| 25 | [engines.clone_tts](../modules/engines.clone_tts.md) | 14.2 | 1115 | 1 | 2 | 19/0/10 | 1 | ✅ |
| 26 | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | 13.3 | 662 | 3 | 0 | 18/0/8 | 0 | ❌ |
| 27 | [agents.uploader_settings_api](../modules/agents.uploader_settings_api.md) | 13.2 | 675 | 3 | 0 | 22/0/7 | 0 | ❌ |
| 28 | [engines.media_ts](../modules/engines.media_ts.md) | 12.7 | 1019 | 4 | 2 | 1/0/0 | 0 | ✅ |
| 29 | [agents.agent_av_sync](../modules/agents.agent_av_sync.md) | 12.1 | 569 | 4 | 1 | 9/0/1 | 0 | ❌ |
| 30 | [scripts.tree_audit](../modules/scripts.tree_audit.md) | 11.5 | 226 | 5 | 0 | 1/0/1 | 0 | ❌ |
| 31 | [engines.series_glossary](../modules/engines.series_glossary.md) | 11.3 | 199 | 4 | 0 | 8/0/4 | 0 | ✅ |
| 32 | [core.batch_config](../modules/core.batch_config.md) | 10.6 | 295 | 4 | 0 | 2/0/0 | 0 | ✅ |
| 33 | [engines.download](../modules/engines.download.md) | 10.3 | 711 | 3 | 1 | 11/0/0 | 1 | ✅ |
| 34 | [pineline.server.routes.queue](../modules/pineline.server.routes.queue.md) | 10.1 | 38 | 5 | 0 | 0/0/0 | 0 | ✅ |
| 35 | [agents.agent_watch](../modules/agents.agent_watch.md) | 9.9 | 408 | 2 | 0 | 16/0/5 | 1 | ✅ |
| 36 | [http_routes.routes_films](../modules/http_routes.routes_films.md) | 9.7 | 370 | 3 | 0 | 17/0/2 | 0 | ✅ |
| 37 | [engines.pronoun_consistency](../modules/engines.pronoun_consistency.md) | 9.6 | 872 | 2 | 1 | 11/0/3 | 0 | ✅ |
| 38 | [agents.agent_brain_context](../modules/agents.agent_brain_context.md) | 9.3 | 287 | 3 | 0 | 9/0/3 | 0 | ✅ |
| 39 | [engines.mux](../modules/engines.mux.md) | 8.9 | 137 | 4 | 0 | 2/0/0 | 0 | ✅ |
| 40 | [engines.separate](../modules/engines.separate.md) | 8.4 | 575 | 2 | 1 | 7/0/2 | 0 | ✅ |
