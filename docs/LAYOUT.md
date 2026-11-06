# PinelineV5 — bố cục thư mục (Phase F + unity + core/)

_Cập nhật: 2026-11-05 (app kernel → `core/`)_

## Explorer nên thấy

| Thư mục / file | Nội dung |
|---|---|
| **Entry (root `.py`)** | Đúng **3** file: `server.py`, `app_desktop.py`, `restart_server.py` |
| **`core/`** | App kernel: `config.py`, `batch_config.py`, `job_queue.py`, `job_meta.py`, `film_db.py`, `manifest.py`, `fileio.py` (+ `__init__.py`) |
| `apps/` | Launchers thật: `run_v5.bat`, `run_tele_cmd.bat`, `build_desktop.bat` (root chỉ stub `call apps\…`) |
| **Desktop** | WebView2: `app_desktop.py` / `build_desktop.bat`. **Tauri:** `src-tauri/` + `run_tauri.bat` / `build_tauri.bat` + `package.json` (devUrl `:8805`); `desktop/tauri_www/` = frontendDist |
| `static/ui/` | `index3.html`, `films_ui.html`, `hongguo.html`, `workflow.html`, … |
| `agents/` | Telegram / autopilot / meta / hongguo / publisher (code live) |
| `http_routes/` | Router bodies: `routes_ui`, `routes_hg`, `routes_agent`, `routes_films`, `routes_uploader_settings` |
| `engines/` | download, translate, render, tts, mux, … |
| `engines/asr/` | toàn bộ ASR engines |
| `tools/` | `lib_check`, `test_channel`, `preset_switcher`, `pick_dirs_dialog`, `migrate_work`, `context_studio/` |
| `config/` | preset JSON mẫu; **`pineline.config.json` giữ ở ROOT** |
| `scripts/install/` | `install.py` + reqs + bat + `INSTALL.md` |
| `pineline/server/routes/` | **Attach registries** (path map → `server.py` handlers); không body UI/hg |
| `docs/`, `tests/`, `scripts/` | tài liệu / test / ops |
| `data/`, `work/` | runtime |

## Glossary

| Thuật ngữ | Nghĩa trên disk |
|---|---|
| **App core** | Package `core/` — config / queue / DB / manifest / fileio. Entry HTTP vẫn `server.py` ở root. |
| **Attach registry** | `pineline.server.routes.*.attach` — bảng path → tên hàm; thân handler vẫn trong `server.py`. |
| **Router body** | Module FastAPI có route thật — sống ở `http_routes/routes_*.py` (không trong `pineline/`). |
| **Package live** | `core/`, `agents/`, `engines/`, `http_routes/`, `tools/` — import trực tiếp. |
| **TARGET shell (đã xoá)** | `pineline/{agents,pipeline,sidecar,desktop,ops,server/services}` — chỉ `__init__`+README; unity xoá. |

## Root shim?

**Không còn** — Phase E xoá ~58 root shim; Phase F dọn tools/install/config khỏi root; 2026-11-05 chuyển kernel vào `core/` (không để shim root). Import phải dùng package:

- `import core.config as config` / `from core.manifest import Manifest`
- `import core.job_queue as job_queue` / `import core.film_db as film_db`
- `import engines.render as render`
- `import agents.agent_core as agent_core`
- `import http_routes.routes_ui as routes_ui`
- `import tools.lib_check as lib_check` / `import tools.test_channel as test_channel`
- `import tools.preset_switcher as preset_switcher`
- `from tools.context_studio…`
- ASR: `import engines.asr.asr as asr` / `engines.asr.fun_asr_nano` …

CLI: `python scripts/install/install.py`; `python -m tools.migrate_work`; `python -m tools.context_studio`; sidecar `python -m agents.agent_tele_cmd`.

## Không đụng

- V2 `:8801` / V4 `:8804` trees  
- Dual `/films` trên sidecar `:8802` (product)  
- `.nvenc_state.json` (giữ root) · `pineline.config.json` (giữ root)  
- Không merge `http_routes` bodies vào `pineline`
