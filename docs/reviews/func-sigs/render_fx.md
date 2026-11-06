# Render FX

- **Module:** `engines/render_fx.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 32

## Signatures

### `_esc_movie` — L21

```python
def _esc_movie(path: Path) -> str
```

**Doc:** Escape path for ffmpeg movie= / lut3d= file=.

### `resolve_lut_file` — L27

```python
def resolve_lut_file() -> Path | None
```

### `resolve_grain_file` — L41

```python
def resolve_grain_file() -> Path | None
```

### `list_bgm_files` — L50

```python
def list_bgm_files() -> list[Path]
```

### `pick_bgm` — L63

```python
def pick_bgm(job_key: str | None=None) -> Path | None
```

### `default_audio_mode` — L75

```python
def default_audio_mode() -> str
```

**Doc:** voice_bgm nếu có thư viện BGM; không thì voice_only (không nhạc gốc).

### `clamp_zoom` — L80

```python
def clamp_zoom(zoom: float | str | None) -> float
```

### `normalize_grain` — L98

```python
def normalize_grain(level: str | None) -> str
```

### `_eq_fallback` — L109

```python
def _eq_fallback() -> str
```

### `build_motion_zoompan` — L116

```python
def build_motion_zoompan(W: int, H: int, zoom: float, fps: float) -> str
```

**Doc:** Ken Burns nhẹ + Drift: scale cố định theo zoom + crop sin(t).

### `build_static_zoom` — L135

```python
def build_static_zoom(W: int, H: int, zoom: float) -> str | None
```

### `lut3d_filter_arg` — L142

```python
def lut3d_filter_arg(lut: Path, work_dir: Path | None=None) -> str
```

**Doc:** Đường dẫn LUT an toàn cho filtergraph Windows.

### `_read_cube` — L163

```python
def _read_cube(path: Path) -> tuple[int, list[tuple[float, float, float]]]
```

### `separable_lutrgb` — L180

```python
def separable_lutrgb(lut: Path, tol: float=0.0001) -> str | None
```

**Doc:** LUT 3D mà mỗi kênh ra chỉ phụ thuộc kênh vào cùng tên → lutrgb 1D tương đương.

### `append_lut_filters` — L217

```python
def append_lut_filters(parts: list[str], enabled: bool, work_dir: Path | None=None) -> str
```

**Doc:** Thêm LUT hoặc eq. Trả nhãn dùng thực tế.

### `grain_noise_alls` — L234

```python
def grain_noise_alls(level: str) -> float
```

### `append_inline_noise_grain` — L243

```python
def append_inline_noise_grain(parts: list[str], level: str) -> str
```

**Doc:** Film grain qua noise= (ổn định). PNG trong assets dùng khi blend input riêng.

### `grain_blend_fragment` — L255

```python
def grain_blend_fragment(vlabel: str, out_label: str, level: str, W: int, H: int) -> tuple[str | None, str]
```

**Doc:** PNG blend tắt mặc định (movie loop dễ treo). Giữ API cho phase sau.

### `bgm_volume` — L261

```python
def bgm_volume() -> float
```

### `dub_volume` — L268

```python
def dub_volume() -> float
```

**Doc:** Âm lượng giọng Việt khi mix (VieNeu đã chuẩn hoá ~0.9 → boost vừa phải 1.25 tránh vỡ tiếng).

### `list_frame_files` — L277

```python
def list_frame_files() -> list[Path]
```

**Doc:** PNG/WebP khung trong assets/overlays/frames (+ overlays gốc).

**Callers (spine):** server frame picker API

### `pick_frame` — L312

```python
def pick_frame(choice: str | None=None, job_key: str | None=None) -> Path | None
```

**Doc:** choice: off | auto | tên file | đường dẫn.

### `prepare_frame_file` — L342

```python
def prepare_frame_file(frame: Path, work_dir: Path) -> str
```

**Doc:** Copy khung vào job → basename cho movie= (cwd=work_dir).

### `brand_text_value` — L360

```python
def brand_text_value(override: str | None=None) -> str
```

### `normalize_brand_mode` — L367

```python
def normalize_brand_mode(mode: str | None=None, enabled: bool | None=None) -> str
```

**Doc:** off | drift | corners | drift_seed.

### `brand_enabled` — L390

```python
def brand_enabled(flag: bool | None=None) -> bool
```

### `brand_xy_expr` — L397

```python
def brand_xy_expr(mode: str, job_key: str | None=None) -> tuple[str, str]
```

**Doc:** Biểu thức ffmpeg x/y cho chữ/logo brand.

### `list_brand_logo_files` — L430

```python
def list_brand_logo_files() -> list[Path]
```

**Callers (spine):** server brand logo API

### `pick_brand_logo` — L462

```python
def pick_brand_logo(choice: str | None=None, job_key: str | None=None) -> Path | None
```

### `prepare_brand_logo` — L487

```python
def prepare_brand_logo(logo: Path, work_dir: Path) -> str
```

### `brand_drawtext_filter` — L503

```python
def brand_drawtext_filter(text: str, H: int, fontfile: str, x_expr: str, y_expr: str) -> str
```

**Doc:** Chữ kênh với x/y expression đã chọn.

### `apply_brand_overlay` — L527

```python
def apply_brand_overlay(body: str, *, W: int, H: int, fontfile: str, work_dir: Path | None, mode: str | None=None, enabled: bool | None=None, text: str | None=None, logo: str | None=None, job_key: str | None=None) -> tuple[str, dict]
```

**Doc:** Ghép brand (chữ ± logo) vào filter chain. Trả (body, meta).
