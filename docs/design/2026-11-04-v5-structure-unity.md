# V5 structure unity — auditor consensus

_Date: 2026-11-04 · Docs-first unity (post Phase F)_

## Decision (locked)

1. **Docs-first unity** — một câu chuyện layout; root ~10 `.py` = intentional **app core** (không tạo `core/` tuần này).
2. **Keep** `pineline.server.routes` attach registries LIVE (`queue` / `jobs` / `assets` / `fs`).
3. **Keep** `http_routes/` for router bodies (UI / hg / agent / films / uploader).
4. **DELETE** empty TARGET shells: `pineline/agents`, `pineline/pipeline`, `pineline/sidecar`, `pineline/desktop`, `pineline/ops`, `pineline/server/services` (chỉ `__init__`+README).
5. **Do NOT** move `job_queue` into `core/`.
6. **Do NOT** merge `http_routes` bodies into `pineline`.

## Why

3-auditor consensus (structure / dead-code / ops-docs): runtime packages đã là `agents/` + `engines/` + `http_routes/` + `tools/`; khung `pineline/*` TARGET rỗng gây docs drift («handlers live in package»). Unity = xoá shell + viết lại docs; không big-bang move.

## Out of scope this week

- Package `core/` / relocate `job_queue`
- Body move `server.py` → `pineline.server.services`
- Merge `http_routes` → `pineline.server.routes`

## Related

- Prior synthesis: `docs/design/2026-11-04-v5-structure-cleanup.md`
- Layout SSOT: `docs/LAYOUT.md`
- Decision log: `docs/DECISIONS.md` (11-04 unity)
