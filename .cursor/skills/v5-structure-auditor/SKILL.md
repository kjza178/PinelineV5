---
name: v5-structure-auditor
description: >-
  Map PinelineV5 runtime vs pineline/ package (LIVE/TARGET). Use when cleaning
  V5 structure, reviewing architecture, or cross-checking declutter plans.
---

# V5 Structure Auditor (read-only)

Root: `Z:\PinelineV5`. **Do not modify files.**

## Checklist

1. Entry: `run_v5.bat`, `server.py`, `app_desktop.py`, sidecar `:8802`.
2. HTTP: `pineline.server.routes.*.attach` vs root `routes_*` vs leftover `@app` API.
3. `pineline/` each package → LIVE / TARGET / empty shell.
4. Top large `.py` files + where stages live (`WIRED_STAGES`).
5. Data: `work/`, `data/films.db`, locks, TEMP.
6. Diff docs (`ARCHITECTURE`, `MANIFEST_CONTRACT`, `DECISIONS`) vs disk.

## Output

Structure verdict · runtime map · hotspots · contradictions · incremental target tree · must-not-break constraints.

## Cross-check

Challenge dead-code hunter if they claim handlers “live in package” (bodies are still `server.py`). Challenge ops auditor if they treat aspirational docs as runtime.
