# Simple A/V mux (ffmpeg copy)

- **Module:** `engines/mux.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 5

## Signatures

### `_find_video` — L31

```python
def _find_video(work_dir: Path, m: Manifest) -> Path | None
```

### `_pick_dub` — L40

```python
def _pick_dub(work_dir: Path, m: Manifest) -> Path
```

**Doc:** Chọn track lồng tiếng: audio ngoài > dub_fit.wav > (tự ghép fit).

### `_has_audio` — L59

```python
def _has_audio(path: Path) -> bool
```

**Doc:** Video gốc có luồng audio không (để biết có ducking được không).

### `run_mux` — L72

```python
def run_mux(work_dir: str | Path, orig_vol: float=0.35, out_name: str='output.mp4', force: bool=False) -> dict
```

**Callers (spine):** simple mux; queue uses run_render instead

### `main` — L124

```python
def main(argv=None)
```
