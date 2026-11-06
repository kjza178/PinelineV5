# Agent pronoun pass

- **Module:** `agents/agent_pronoun_pass.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 4

## Signatures

### `_fold` — L22

```python
def _fold(s: str) -> str
```

### `find_pronoun_issues` — L27

```python
def find_pronoun_issues(rows: list[dict], plan: dict) -> list[dict]
```

### `_fix_batch` — L92

```python
def _fix_batch(chunk: list[dict], plan_block: str, model: str | None) -> dict[int, str]
```

### `run_pronoun_pass` — L123

```python
def run_pronoun_pass(work_dir: str | Path, model: str | None=None) -> dict
```

**Callers (spine):** server._run_requested_review (spine §1)
