# OCR engine

- **Module:** `engines/ocr.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 8

## Signatures

### `_meaningful` — L39

```python
def _meaningful(t: str) -> bool
```

**Doc:** Giữ chữ CÓ NGHĨA: ≥2 chữ Hán, hoặc số ≥3 chữ số (ID). Bỏ rác latin / 1 chữ đơn.

### `_find_video` — L54

```python
def _find_video(work_dir: Path) -> Path | None
```

### `_probe_size` — L65

```python
def _probe_size(video: Path) -> tuple[int, int]
```

### `extract_keyframes` — L77

```python
def extract_keyframes(video: Path, out_dir: Path, dur: float | None=None, stride: int=1) -> list[tuple[Path, float]]
```

**Doc:** Trích KEYFRAME + mốc giờ. Giải mã chỉ I-frame nên nhanh. stride: lấy cách quãng.

### `_classify_zone` — L113

```python
def _classify_zone(cx: float, cy: float, text: str) -> str
```

**Doc:** Trả 'wm' (watermark), 'sub' (hardsub thoại), hoặc 'cand' (ứng viên).

### `run_ocr` — L128

```python
def run_ocr(work_dir: str | Path, dur: float | None=None, stride: int=1, model: str | None=None, force: bool=False) -> dict
```

**Callers (spine):** server._auto_gpu if use_ocr (spine §1)

### `_translate_entries` — L243

```python
def _translate_entries(entries: list[dict], model: str | None) -> None
```

**Doc:** Dịch danh sách chữ trên hình sang tiếng Việt (1 lời gọi LLM).

### `main` — L262

```python
def main(argv=None)
```
