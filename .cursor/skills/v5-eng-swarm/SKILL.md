---
name: v5-eng-swarm
description: >-
  Orchestrate parallel PinelineV5 engineering subagents (vuln, bugs, docs,
  tests, PR review, autofix, invariants, part-atomizer). Use when user asks
  for full eng review, swarm audit, or cross-check V5 quality.
---

# V5 Engineering Swarm

Root: `Z:\PinelineV5`. Launch **parallel** Task agents (one skill each). Do not serialize unless a fix depends on prior findings.

## Swarm roster

| Agent skill | Role | Write? |
|---|---|---|
| `v5-vuln-hunter` | Security / SSRF / secrets / auth | no (report only) |
| `v5-critical-bug-hunter` | Runtime P0/P1 bugs | no |
| `v5-docs-generator` | Docs gaps + draft markdown | yes under `docs/` |
| `v5-test-coverage` | Missing tests + draft pytest | yes under `tests/` only if asked |
| `v5-pr-reviewer` | Diff/PR style review | no |
| `v5-autofix-safe` | Apply **safe** autofixes from swarm | yes (narrow) |
| `v5-invariants-monitor` | Engineering invariants | no |
| `v5-part-atomizer` | Finest-grain map of each subsystem | yes `docs/reviews/` |
| Existing: `v5-structure-auditor`, `v5-unity-auditor`, `v5-ops-docs-auditor`, `v5-deadcode-hunter` | structure/ops/deadcode | no |

## Protocol

1. Mark todos: spawn → collect → triage → optional autofix → report.
2. Spawn all read-only hunters **in one parallel batch**.
3. Merge into `docs/reviews/YYYY-MM-DD-v5-eng-swarm.md` (P0/P1/P2 + owners).
4. Autofix **only** items marked SAFE by vuln+bug hunters (no restart during active :8805 encode unless user allows).
5. Cross-challenge: structure vs deadcode vs ops docs (same as structure skill).

## Hard rules

- Never kill llama / mid-job :8801 without ask.
- No secrets in docs.
- Autofix requires backup `Z:\PinelineV2_codebak\<date>_v5-swarm\`.
