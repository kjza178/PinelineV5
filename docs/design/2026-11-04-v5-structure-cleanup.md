# V5 structure cleanup — cross-check synthesis

_Date: 2026-11-04 · 3 auditors: structure / dead-code / ops-docs_

## Consensus (3/3)

1. **Runtime = root.** `server.py` ~5.2k lines holds handler bodies; `pineline.server.routes.{queue,jobs,assets,fs}` = path registries only.
2. **Route decorator SSOT done on disk** (no `@app` API). Process `:8805` may still be pre-strip until restart.
3. **Do not big-bang** move engines into `pineline/pipeline`. Keep TARGET maps.
4. **Keep dual** V2/V4/V5 trees and `:8802` films/meta unless user decides otherwise.
5. **Next value ≠ more attach:** fix docs drift, footguns (`run_v4` from V5 tree), dead `static/app.js`, `check_batch1/2` V2 paths.

## Disagreements resolved

| Claim | Winner |
|---|---|
| «Handlers live in pineline» | Dead-code + Structure: **bodies in server.py** |
| «assets still TARGET» | Ops + routes README: **LIVE on disk**; ARCHITECTURE mermaid stale |
| «archive still heavy» | Dead-code: ~0.3 MB after node_modules delete |
| Production films DB | Ops: **V2**; V5 DB = sandbox |

## Target shape (incremental)

```
pineline/server/routes/   # registries LIVE today
pineline/server/services/ # next: carve helpers from server.py
routes_* → pineline later # same include pattern
pipeline engines          # last, one stage at a time
```

## Auditor skills (reusable)

- `.cursor/skills/v5-structure-auditor/SKILL.md`
- `.cursor/skills/v5-deadcode-hunter/SKILL.md`
- `.cursor/skills/v5-ops-docs-auditor/SKILL.md`

Plan thực thi: `docs/superpowers/plans/2026-11-04-v5-codebase-cleanup.md`
