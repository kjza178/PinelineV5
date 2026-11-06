---
name: v5-unity-auditor
description: >-
  Cross-check PinelineV5 structure unity (one story: app core + packages +
  attach registries). Use after layout changes or before claiming cleanup done.
---

# V5 Unity Auditor (read-only)

## Canonical story (post 2026-11-05 core/)

1. **Entry (root):** `server.py`, `app_desktop.py`, `restart_server.py`
2. **App core package:** `core/` — `config.py`, `batch_config.py`, `job_queue.py`, `job_meta.py`, `film_db.py`, `manifest.py`, `fileio.py`
3. **Packages:** `engines/`, `agents/`, `http_routes/` (router bodies), `tools/`, `apps/`, `static/ui/`
4. **Attach registries only:** `pineline.server.routes.{queue,jobs,assets,fs}` — path maps; bodies in `server.py`
5. **No** empty TARGET shells under `pineline/{agents,pipeline,…}`
6. **No** root shims; imports are `core.*` / `engines.*` / `agents.*` / `http_routes.*` / `tools.*`

## Checklist

- Disk vs `docs/LAYOUT.md` + `ARCHITECTURE.md`
- No stale “engines at root” / “config at root” / “routes_ui at root” in READMEs
- `tests/test_layout_paths.py` green (root must NOT have `config.py`/`job_queue.py`; must HAVE `core/config.py`)
- Glossary: bodies (`http_routes`) ≠ registry (`pineline.server.routes`)

## Output

Unity PASS/FAIL · P0 lies · recommended next
