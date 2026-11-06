# Agent QA gate

- **Module:** `agents/agent_qa_gate.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 8

## Signatures

### `_now` — L11

```python
def _now() -> str
```

### `_load_rows` — L15

```python
def _load_rows(path: Path) -> list[dict]
```

### `snapshot_pre_review` — L25

```python
def snapshot_pre_review(work_dir: Path) -> Path | None
```

### `review_diff` — L34

```python
def review_diff(work_dir: Path | str, job_id: str | None=None) -> dict
```

**Doc:** So script.json vs script.pre_review.json + thống kê rv / missing.

### `_fail_reasons` — L106

```python
def _fail_reasons(n: int, missing_ratio: float, review_ran: bool, pack: dict) -> list[str]
```

### `evaluate_qa_gate` — L119

```python
def evaluate_qa_gate(work_dir: Path) -> dict
```

### `run_qa_gate` — L123

```python
def run_qa_gate(work_dir: Path, *, run_review_fn, target: str='Tiếng Việt', review_model: str | None=None) -> dict
```

**Doc:** Snapshot → run_review (sync) → diff → quyết định pass/block.

**Callers (spine):** server._auto_gpu HOLD/QA before TTS (spine §1)

### `set_qa_gate` — L185

```python
def set_qa_gate(work_dir: Path, enabled: bool, *, override_pass: bool | None=None) -> dict
```
