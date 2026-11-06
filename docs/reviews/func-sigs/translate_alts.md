# Translate alternatives

- **Module:** `engines/translate_alts.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 5

## Signatures

### `_heuristic_ambiguous` — L35

```python
def _heuristic_ambiguous(row: dict) -> str | None
```

**Doc:** Trả lý do ngắn nếu câu nên đưa phương án; None = bỏ qua.

### `_alts_batch` — L65

```python
def _alts_batch(rows: list[dict], plan_block: str, prev_ctx: list[dict], next_ctx: list[dict], model: str | None, plan: dict | None) -> dict[int, dict]
```

**Doc:** Trả {i: {alts[], pick, reason}} — tối ưu theo ngữ cảnh + văn phong.

### `run_ambiguous_alts` — L164

```python
def run_ambiguous_alts(work_dir: str | Path, *, batch: int=20, model: str | None=None, force: bool=False, limit: int | None=None, apply_pick: bool=False) -> dict
```

**Doc:** Quét script → vi_alts.json (phương án tối ưu theo ngữ cảnh + văn phong).

**Callers (spine):** server.run_translate_alts_api

### `analyze_pack_report` — L305

```python
def analyze_pack_report(work_dir: str | Path) -> dict
```

**Doc:** Checklist pack Context Studio có đủ để dịch chunk không.

**Callers (spine):** server.run_translate_alts_api

### `main` — L353

```python
def main(argv=None)
```
