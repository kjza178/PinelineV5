---
name: v5-test-coverage
description: >-
  Find PinelineV5 test gaps and propose/add pytest coverage for critical
  paths (split, pronoun-qa slim, queue, layout). Use when improving tests.
---

# V5 Test Coverage

Root: `Z:\PinelineV5`. Default **report only**; write tests only if user said add/autofix.

## Focus

- `tests/` inventory vs `engines/`, `core/`, `http_routes/`
- Must-cover: split merge hardlink, ENOSPC, pronoun `_plan_block_for_qa`, queue sort, layout paths
- Run: `python -m pytest tests/ -q --tb=no` (subset if slow)

## Output

Gap table + proposed test names. If allowed to write: add tests + run them.
