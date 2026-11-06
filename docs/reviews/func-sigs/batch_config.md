# Batch config / job opts

- **Module:** `core/batch_config.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 12

## Signatures

### `_now` — L90

```python
def _now() -> str
```

### `_coerce` — L94

```python
def _coerce(key: str, val: Any) -> Any
```

### `load` — L117

```python
def load() -> dict[str, Any]
```

**Doc:** File hỏng/đang ghi dở → trả bản đọc tốt gần nhất (không rơi về DEFAULTS: Auto-pilot

### `resolve_job_opts` — L141

```python
def resolve_job_opts(*layers: dict[str, Any] | None, fill_voice: bool=True) -> dict[str, Any]
```

**Doc:** Opts của 1 job = config batch hiện tại ⊕ từng lớp (lớp sau đè lớp trước, bỏ None/pin_opts).

**Callers (spine):** create_job / queue; load() + merge layers (spine §1)

### `_norm_zoom` — L155

```python
def _norm_zoom(v: Any) -> float
```

### `render_kwargs` — L168

```python
def render_kwargs(o: dict[str, Any]) -> dict[str, Any]
```

**Doc:** Tham số render (_do_render / MuxReq) từ opts đã resolve.

### `meta` — L194

```python
def meta() -> dict[str, Any]
```

### `_write` — L204

```python
def _write(opts: dict[str, Any], by: str) -> None
```

### `update` — L213

```python
def update(patch: dict[str, Any], by: str='api') -> dict[str, Any]
```

**Doc:** Gộp patch vào config hiện tại. Key lạ / giá trị sai → ValueError.

### `reset` — L233

```python
def reset(by: str='api') -> dict[str, Any]
```

### `parse_kv` — L239

```python
def parse_kv(text: str) -> dict[str, str]
```

**Doc:** 'audio_mode=voice_bgm orig_vol=0.3 brand_text="Kênh A"' → dict.

### `describe` — L251

```python
def describe(opts: dict[str, Any] | None=None) -> str
```
