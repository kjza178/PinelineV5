---
name: v5-autofix-safe
description: >-
  Apply only SAFE autofixes from V5 eng-swarm findings (null-guards, slim
  payloads, dead CSS, docs sync). Use after swarm triage when user allows fix.
---

# V5 Autofix Safe

Root: `Z:\PinelineV5` (+ port V2/V4 if shared).

## Allowed

- Null-guards / missing DOM id / hint pane fixes
- Dead CSS removal / label polish
- Docs CHANGELOG/worklog/fix-log
- Clearly marked SAFE items from vuln/bug hunters

## Forbidden without explicit user yes

- Restart mid-job, delete work dirs, change auth/token flow, enlarge attack surface

## Process

1. Backup `Z:\PinelineV2_codebak\<date>_v5-swarm-autofix\`
2. Patch → sync trees if needed → tests for touched area → docs
