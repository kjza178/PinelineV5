---
name: v5-invariants-monitor
description: >-
  Monitor PinelineV5 engineering invariants (ports, core/ imports, no root
  shims, attach vs http_routes, work root, dual-tree). Use for invariant checks.
---

# V5 Invariants Monitor (read-only)

## Invariants (must hold)

1. Root entry `.py` = exactly `server.py`, `app_desktop.py`, `restart_server.py` (+ stubs ok).
2. App kernel lives in `core/` — no root `config.py` shim.
3. HTTP bodies in `http_routes/`; `pineline.server.routes.*.attach` are registries only.
4. Ports: V5 `:8805`, V2 `:8801`, V4 `:8804`; sidecar `:8802` may dual `/films`.
5. `WORK_ROOT` / TEMP per tree; no silent write into another tree's `work/`.
6. Merge split: never `copy2` full video for `output_full` alias (hardlink only).
7. Pronoun-QA GPT path uses slim plan (`_plan_block_for_qa`), not full characters dump.
8. Docs on change: CHANGELOG + worklog when code changes.

## Output

Pass/fail per invariant + evidence path. Failures → P0/P1.
