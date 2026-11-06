# Job Manifest JSON

- **Module:** `core/manifest.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 15

## Signatures

### `_now` — L26

```python
def _now() -> str
```

### `_lock_for` — L39

```python
def _lock_for(path: Path) -> threading.Lock
```

### `_merge3` — L52

```python
def _merge3(base, mine, theirs)
```

**Doc:** Gộp 3 chiều dict JSON. Key mình không đổi so với lúc load → lấy bản đĩa (người khác

### `_xproc_lock` — L77

```python
def _xproc_lock(path: Path)
```

**Doc:** Khoá liên tiến trình (server + subprocess asr/tts cùng ghi). Không lấy được thì vẫn ghi

### `Manifest.__init__` — L97

```python
def __init__(self, work_dir: str | Path)
```

### `Manifest.load` — L104

```python
def load(self) -> None
```

### `Manifest._read_disk` — L124

```python
def _read_disk(self) -> dict | None
```

### `Manifest.update` — L135

```python
def update(self, fn) -> bool
```

**Doc:** Đọc lại từ đĩa → fn(data) → ghi, trong khoá (thread + liên tiến trình).

### `Manifest.save` — L148

```python
def save(self) -> None
```

**Callers (spine):** spine stamp queue_opts / stages

### `Manifest._write_locked` — L164

```python
def _write_locked(self, data: dict) -> None
```

**Doc:** Ghi atomic; gọi khi đang giữ _lock_for(self.path).

### `Manifest.stage` — L201

```python
def stage(self, name: str) -> dict | None
```

### `Manifest.is_done` — L204

```python
def is_done(self, name: str) -> bool
```

### `Manifest.mark_running` — L208

```python
def mark_running(self, name: str) -> None
```

**Doc:** Giữ config cũ (voice/speed/engine/n_done...) — chỉ đổi status/started_at.

### `Manifest.mark_done` — L220

```python
def mark_done(self, name: str, **payload) -> dict
```

### `Manifest.mark_failed` — L232

```python
def mark_failed(self, name: str, error) -> None
```
