---
name: v5-docs-generator
description: >-
  Generate or refresh PinelineV5 docs from live code (LAYOUT, ARCHITECTURE,
  RUNBOOK snippets, review reports). Use when docs drift or user asks gen docs.
---

# V5 Docs Generator

Root: `Z:\PinelineV5`. Prefer **append/update** existing docs; do not invent APIs.

## Checklist

1. Diff `docs/LAYOUT.md` / `ARCHITECTURE.md` / `STATE.md` vs disk.
2. Draft missing pieces into `docs/reviews/YYYY-MM-DD-*.md` or update CHANGELOG/worklog.
3. Never write secrets. Follow `docs-on-change` / fix-log rules when code also changes.

## Output

List of docs written/updated + 5-line summary of drift fixed.
