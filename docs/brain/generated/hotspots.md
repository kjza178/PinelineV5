# Hotspots — nơi nên soi bug/refactor trước

_Sinh tự động bởi `scripts/brain_build.py` lúc 2026-11-11 02:38. Đừng sửa tay — chạy lại script._


Điểm = LOC/500 + 2×fix log + 0.15×nhắc CHANGELOG + 1×hàm dài + 0.1×`except Exception` + 1×bare except + 0.5×nuốt lỗi (`except: pass`) + 0.5×Thread + 0.3×`global` + 3 nếu >800 dòng mà không test.
Đây là **heuristic để ưu tiên**, không phải kết luận có bug.

| # | Module | Điểm | Dòng | Fix | Hàm dài | broad/bare/swallow except | Thread | Test |
|---:|---|---:|---:|---:|---:|---|---:|---|
| 1 | [server](../modules/server.md) | 144.5 | 6602 | 33 | 5 | 205/0/72 | 0 | ✅ |
| 2 | [hongguo_bridge](../modules/hongguo_bridge.md) | 69.2 | 4216 | 14 | 5 | 89/0/25 | 1 | ❌ |
| 3 | [translate](../modules/translate.md) | 67.7 | 4083 | 20 | 6 | 60/0/12 | 0 | ✅ |
| 4 | [agents.hongguo_bridge](../modules/agents.hongguo_bridge.md) | 66.2 | 4210 | 14 | 5 | 89/0/25 | 1 | ✅ |
| 5 | [engines.translate](../modules/engines.translate.md) | 60.4 | 2992 | 20 | 3 | 49/0/10 | 0 | ✅ |
| 6 | [render](../modules/render.md) | 55.5 | 3079 | 14 | 7 | 34/0/16 | 1 | ✅ |
| 7 | [engines.render](../modules/engines.render.md) | 55.5 | 3079 | 14 | 7 | 34/0/16 | 1 | ✅ |
| 8 | [agent_tele_cmd](../modules/agent_tele_cmd.md) | 54.2 | 2333 | 12 | 4 | 58/0/10 | 11 | ❌ |
| 9 | [agents.agent_tele_cmd](../modules/agents.agent_tele_cmd.md) | 54.2 | 2328 | 12 | 4 | 58/0/10 | 11 | ❌ |
| 10 | [agent_feeder](../modules/agent_feeder.md) | 40.5 | 2065 | 7 | 4 | 40/0/20 | 0 | ❌ |
| 11 | [agents.agent_feeder](../modules/agents.agent_feeder.md) | 40.5 | 2065 | 7 | 4 | 40/0/20 | 0 | ❌ |
| 12 | [auto_publisher](../modules/auto_publisher.md) | 38.4 | 1567 | 6 | 1 | 44/0/25 | 2 | ❌ |
| 13 | [hongguo_rpc](../modules/hongguo_rpc.md) | 37.3 | 1449 | 10 | 0 | 22/0/9 | 5 | ❌ |
| 14 | [agents.hongguo_rpc](../modules/agents.hongguo_rpc.md) | 37.3 | 1449 | 10 | 0 | 22/0/9 | 5 | ❌ |
| 15 | [agents.auto_publisher](../modules/agents.auto_publisher.md) | 35.3 | 1555 | 6 | 1 | 43/0/25 | 2 | ✅ |
| 16 | [job_queue](../modules/job_queue.md) | 31.7 | 658 | 12 | 0 | 10/0/2 | 1 | ✅ |
| 17 | [core.job_queue](../modules/core.job_queue.md) | 31.7 | 658 | 12 | 0 | 10/0/2 | 1 | ✅ |
| 18 | [meta_studio](../modules/meta_studio.md) | 30.5 | 1918 | 3 | 5 | 36/0/17 | 0 | ❌ |
| 19 | [agents.meta_studio](../modules/agents.meta_studio.md) | 26.8 | 1897 | 3 | 5 | 34/0/16 | 0 | ✅ |
| 20 | [test_channel](../modules/test_channel.md) | 25.3 | 1435 | 3 | 0 | 34/0/15 | 2 | ❌ |
| 21 | [agents.test_channel](../modules/agents.test_channel.md) | 24.7 | 1283 | 3 | 0 | 31/0/15 | 2 | ❌ |
| 22 | [tools.test_channel](../modules/tools.test_channel.md) | 24.7 | 1283 | 3 | 0 | 31/0/15 | 2 | ❌ |
| 23 | [agents.agent_hongguo](../modules/agents.agent_hongguo.md) | 24.4 | 1570 | 3 | 1 | 33/0/12 | 1 | ❌ |
| 24 | [routes_hg](../modules/routes_hg.md) | 24.3 | 1018 | 6 | 0 | 53/0/3 | 0 | ❌ |
| 25 | [agent_core](../modules/agent_core.md) | 23.4 | 2072 | 6 | 1 | 5/0/1 | 0 | ❌ |
| 26 | [film_db](../modules/film_db.md) | 23.0 | 1091 | 5 | 0 | 19/0/11 | 0 | ❌ |
| 27 | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | 20.6 | 993 | 6 | 0 | 52/0/2 | 0 | ✅ |
| 28 | [agents.agent_core](../modules/agents.agent_core.md) | 20.3 | 2038 | 6 | 1 | 5/0/1 | 0 | ✅ |
| 29 | [llm](../modules/llm.md) | 19.8 | 894 | 4 | 1 | 22/0/5 | 0 | ❌ |
| 30 | [split_parts](../modules/split_parts.md) | 19.8 | 828 | 6 | 2 | 8/0/0 | 0 | ❌ |
| 31 | [agent_brain](../modules/agent_brain.md) | 19.0 | 1221 | 1 | 3 | 36/0/8 | 1 | ❌ |
| 32 | [core.film_db](../modules/core.film_db.md) | 18.3 | 1064 | 5 | 0 | 17/0/8 | 0 | ✅ |
| 33 | [engines.split_parts](../modules/engines.split_parts.md) | 17.3 | 845 | 6 | 2 | 8/0/1 | 0 | ✅ |
| 34 | [restart_server](../modules/restart_server.md) | 17.1 | 250 | 7 | 0 | 5/0/0 | 0 | ❌ |
| 35 | [engines.llm](../modules/engines.llm.md) | 16.5 | 872 | 4 | 1 | 19/0/5 | 0 | ✅ |
| 36 | [engines.clone_tts](../modules/engines.clone_tts.md) | 14.2 | 1115 | 1 | 2 | 19/0/10 | 1 | ✅ |
| 37 | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | 13.3 | 658 | 3 | 0 | 18/0/8 | 0 | ❌ |
| 38 | [routes_agent](../modules/routes_agent.md) | 11.8 | 645 | 4 | 0 | 24/0/0 | 0 | ❌ |
| 39 | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | 11.7 | 638 | 4 | 0 | 23/0/0 | 0 | ✅ |
| 40 | [series_glossary](../modules/series_glossary.md) | 11.3 | 199 | 4 | 0 | 8/0/4 | 0 | ❌ |
