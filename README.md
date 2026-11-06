# PinelineV5 — khung refactor

**V4** (`Z:\PinelineV4`, :8804) = bản ổn định / production.  
**V5** (thư mục này, :8805) = làm lại cấu trúc cho dễ đọc; có thể xóa nếu fail.

## Chạy / Run

```bat
run_v5.bat
```

(stub → `apps/run_v5.bat`)

- Server: `http://127.0.0.1:8805`
- Temp: `D:\PinelineV5_tmp` · Work mặc định: `D:\PinelineV5_work`
- Sidecar vẫn :8802 nhưng `PINELINE_BASE` → :8805 (`apps/run_tele_cmd.bat`)

## Layout (Phase F + unity)

```
apps/            # launchers thật (run_v5, run_tele_cmd, build_desktop)
agents/          # agent_*, hongguo_bridge, auto_publisher, meta_studio, …
http_routes/     # router bodies: routes_ui / routes_hg / routes_films / …
engines/         # pipeline flat (render, llm, translate, …) + engines/asr/
tools/           # lib_check, test_channel, migrate_work, context_studio, …
static/ui/       # HTML live: index3, hongguo, films_ui, workflow
pineline/        # attach registries only: server/routes/{queue,jobs,assets,fs}
```

**App core** — đúng 10 file `.py` root (không gói `core/` tuần này):

`server.py` · `app_desktop.py` · `config.py` · `batch_config.py` · `job_queue.py` · `job_meta.py` · `film_db.py` · `manifest.py` · `fileio.py` · `restart_server.py`

Không còn shim. Import: `engines.*` / `agents.*` / `http_routes.*` / `tools.*`.

Chi tiết: **`docs/LAYOUT.md`**, **`docs/ARCHITECTURE.md`**, **`pineline/README.md`**.

## Restore

- Zip: `Z:\PinelineV2_backup_2026-11-02_0418.zip` (+ snapshot ngày layout)
- Codebak: `Z:\PinelineV2_codebak\2026-11-04_v5-unity\` (+ `v5-layout-*`)
- Fail V5 → xóa/đổi tên tree này; **không đụng V4**

Quyết định: `docs/DECISIONS.md` · Runbook: `docs/RUNBOOK.md`
