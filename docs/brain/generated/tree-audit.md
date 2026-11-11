# Tree audit — PinelineV5

_Sinh bởi `scripts/tree_audit.py` lúc 2026-11-10 19:53. ERROR = sẽ hỏng khi chạy; WARN = nên xem._

**ERROR: 3** · import lỗi 7 · cổng lạ 9 · module trùng tên 1

## Import không resolve

| Mức | File | Dòng | Module |
|---|---|---:|---|
| WARN | `engines/translate.py` | 905 | `context_studio.schema` |
| WARN | `engines/translate.py` | 3613 | `context_studio.schema` |
| WARN | `server.py` | 4891 | `context_studio.analyzer` |
| WARN | `server.py` | 4892 | `context_studio.character_mapper` |
| WARN | `server.py` | 4893 | `context_studio.exporter` |
| WARN | `server.py` | 4894 | `context_studio.schema` |
| WARN | `server.py` | 4895 | `context_studio.srt_io` |

## Cổng của cây khác

| Mức | File | Dòng | Chi tiết |
|---|---|---:|---|
| ERROR | `agents/agent_autopilot.py` | 20 | :8801 (cây này 8805) — DEFAULT_BASE = "http://127.0.0.1:8801" |
| WARN | `agents/agent_tele_cmd.py` | 74 | :8801 (cây này 8805) — BASE = (os.getenv("PINELINE_BASE") or "http://127.0.0.1:8801").strip().rstrip("/") |
| WARN | `agents/agent_tool_loop.py` | 10 | :8801 (cây này 8805) — python agent_tool_loop.py --base http://127.0.0.1:8801 --job ID --stages translate --dry |
| WARN | `agents/agent_tool_loop.py` | 449 | :8801 (cây này 8805) — p.add_argument("--base", default=os.getenv("PINELINE_BASE") or "http://127.0.0.1:8801") |
| ERROR | `http_routes/routes_films.py` | 184 | :8804 (cây này 8805) — base = _get_base_url(req) if req else "http://127.0.0.1:8804" |
| WARN | `http_routes/routes_films.py` | 279 | :8804 (cây này 8805) — host = req.headers.get("host") or "127.0.0.1:8804" |
| WARN | `http_routes/routes_films.py` | 290 | :8804 (cây này 8805) — host = req.headers.get("host") or "127.0.0.1:8804" |
| WARN | `http_routes/routes_films.py` | 313 | :8804 (cây này 8805) — host = req.headers.get("host") or "127.0.0.1:8804" |
| ERROR | `tools/migrate_work.py` | 35 | :8801 (cây này 8805) — BASE = "http://127.0.0.1:8801" |

## Module trùng tên

| Mức | Tên | Bản [md5] |
|---|---|---|
| INFO | `test_channel` | agents/test_channel.py[519d19], tools/test_channel.py[519d19] |

## So với cây khác

- **WARN** `docs/STATE.md` GIỐNG HỆT PinelineV2 — có thể bị sync đè (file này nên riêng từng cây)
- **WARN** `docs/ARCHITECTURE.md` GIỐNG HỆT PinelineV2 — có thể bị sync đè (file này nên riêng từng cây)
- **INFO** so PinelineV2: root .py giống 0, khác 2 (restart_server.py, server.py)
- **WARN** `docs/STATE.md` GIỐNG HỆT PinelineV4 — có thể bị sync đè (file này nên riêng từng cây)
- **WARN** `docs/ARCHITECTURE.md` GIỐNG HỆT PinelineV4 — có thể bị sync đè (file này nên riêng từng cây)
- **INFO** so PinelineV4: root .py giống 0, khác 3 (app_desktop.py, restart_server.py, server.py)
