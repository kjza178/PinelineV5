---
name: v5-deadcode-hunter
description: >-
  Find dead/duplicate clutter in PinelineV5 (UI twins, V2-hardcoded scripts,
  footgun launchers). Use for declutter reviews; cross-check structure claims.
---

# V5 Dead-code Hunter (read-only)

Root: `Z:\PinelineV5`. **Do not modify files.**

## Hunt

1. Dup logic / UI twins (`static/app.js` vs `index3.html`).
2. Never-imported modules vs string-spawned ASR engines (false positive).
3. `scripts/` live vs oneshot vs archive.
4. `check_batch*` / restart / migrate hardcoding V2/V4 paths.
5. Stale LIVE/TARGET in README vs `pineline/server/routes/README.md`.

## Output

Findings table (id, severity P0–P2, evidence, action, `:8805` risk) · top 5 archives · false positives · notes challenging Structure Auditor overclaims.

## Cross-check

Do not propose deleting empty `pineline/*` TARGET maps or dual `/films`+`/meta` without product decision. Attach registries ≠ duplicate handler bodies.
