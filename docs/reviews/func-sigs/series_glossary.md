# Series glossary

- **Module:** `engines/series_glossary.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 10

## Signatures

### `_core_of` — L22

```python
def _core_of(title: str) -> str
```

### `series_key` — L32

```python
def series_key(work_dir: Path | str) -> str | None
```

### `_path` — L43

```python
def _path(core: str) -> Path
```

### `load` — L48

```python
def load(core: str | None) -> dict | None
```

### `_valid_char` — L73

```python
def _valid_char(c: dict) -> bool
```

### `_merge_list` — L77

```python
def _merge_list(base: list, top: list, key) -> list
```

**Doc:** top đè base theo key; giữ thứ tự: mục của top trước, mục chỉ có ở base sau.

### `_zh` — L93

```python
def _zh(x) -> str
```

### `_pron` — L97

```python
def _pron(x) -> str
```

### `apply` — L101

```python
def apply(work_dir: Path | str, plan: dict) -> dict
```

### `save_from` — L124

```python
def save_from(work_dir: Path | str, reason: str='duyệt trước TTS') -> dict
```
