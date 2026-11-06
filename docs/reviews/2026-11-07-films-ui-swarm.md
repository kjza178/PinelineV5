# Eng-swarm — Films UI `:8802/films/ui`

- **Date:** 2026-11-07
- **Live:** `Z:\PinelineV2\films_ui.html` via `agent_tele_cmd`
- **Agents:** [syntax](6939184b-2a3e-4735-82d4-9f4e7d315072) · [runtime](5385f328-c05f-4219-b393-f7985f7316d1) · [autofix](1bc7229f-4d24-48f2-afb7-e9a67c8d9f6f) + parent P0 `jq` HTML-escape

## Verdict

**onclick/syntax P0 fixed** (verified: Test modal `display:flex`).  
**Settings + Uploader vẫn 404** trên sidecar — cần port API, không phải HTML.

| Check | Result |
|-------|--------|
| Live HTML == disk | Yes |
| `node --check` script | PASS |
| `jq` HTML-safe | PASS (Test click works) |
| Studio/UI3/Hongguo :8801 | OK |
| Poster | OK |
| Auto-publish load flat config | Fixed |
| `/api/settings`, `/api/uploader/*` | **404** (open) |

## Applied fixes

1. `jq` → stringify + `&amp;`/`&quot;`
2. Autopub GET flat/config dual shape
3. Clearer 404 toasts for Settings/Uploader
4. Canva create null-guard
5. Sync 4 copies identical

## Still open

| Sev | Item |
|-----|------|
| P0 | Port/wire uploader+settings routes on :8802 |
| P1 | XSS: `promptDeleteSingle` raw title in innerHTML |
| P2 | baike 500 vs 404 |

## Recheck

Hard refresh Films UI → bấm Test → modal mở.  
Fix log: `docs/fixes/2026-11-07-films-ui-syntax.md`
