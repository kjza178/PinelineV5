# File I/O helpers

- **Module:** `core/fileio.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 4

## Signatures

### `atomic_write_text` — L16

```python
def atomic_write_text(path: str | Path, text: str, encoding: str='utf-8', fsync: bool=True) -> None
```

### `atomic_write_json` — L39

```python
def atomic_write_json(path: str | Path, obj, indent: int | None=2, fsync: bool=True) -> None
```

**Callers (spine):** engines/translate.py script checkpoints

### `read_json_checkpoint` — L43

```python
def read_json_checkpoint(path: str | Path, default=None)
```

**Doc:** Đọc checkpoint JSON. Hỏng → đổi tên thành .corrupt-<ts> (giữ để cứu) và trả default,

### `file_lock` — L60

```python
def file_lock(path: str | Path, timeout: float=15.0, stale_sec: float=60.0)
```
