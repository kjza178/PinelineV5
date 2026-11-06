---
name: v5-func-signer
description: >-
  Generate per-module signature docs under docs/reviews/func-sigs/<module>.md
  with full AST signatures + docstrings for PinelineV5. Use when user asks for
  deep function signatures, func-sigs, or module API surface docs.
---

# V5 Function Signer

Root: `Z:\PinelineV5`. Output: `docs/reviews/func-sigs/<module>.md`.

## When to use

- User asks for deep / full signatures of a module
- Expanding the func-sigs batch after catalog updates
- Agent needs call-surface docs before refactor

## Steps

1. Resolve module path (examples):
   - `translate` → `engines/translate.py`
   - `job_queue` → `core/job_queue.py`
   - `hongguo_bridge` → `agents/hongguo_bridge.py`
   - `server_orchestration` → key funcs only from `server.py` (spine helpers, not every route)
2. Parse with `ast` (module-level + class methods; skip nested defs).
3. For each def, emit:
   - Full signature (`ast.unparse` args/annotations/defaults/return)
   - First line of docstring (or note missing)
   - Line number
   - **Callers** if known from spine catalog (`docs/reviews/2026-11-06-v5-func-catalog.md` §1) or grep — else omit
4. Write `docs/reviews/func-sigs/<slug>.md` using template below.
5. Append/update `docs/reviews/func-sigs/README.md` index row.
6. Brief CHANGELOG + worklog lines (docs-on-change). **No secrets.**

## Template

```markdown
# <Title>

- **Module:** `<rel/path.py>`
- **Date:** YYYY-MM-DD
- **Source:** AST
- **Count:** N

## Signatures

### `name` — L123

```python
def name(a: T, b: U = None) -> R
```

**Doc:** first line…

**Callers (spine):** optional
```

## Parallel batch

Independent modules can be signed in parallel subagents. Prefer one file per module. Cap `server_orchestration` to ~40 spine helpers (`create_job`, `_queue_run_one`, `_auto_gpu`, `_do_tts`, `_do_render`, …).

## Do not

- Dump all 2118 catalog rows into one file
- Invent callers — only spine/catalog/grep evidence
- Commit secrets from docstrings
