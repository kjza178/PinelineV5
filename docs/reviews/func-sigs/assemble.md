# Assemble / fit dub audio

- **Module:** `engines/assemble.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 16

## Signatures

### `_read_mono` — L31

```python
def _read_mono(path: str, target_sr: int) -> np.ndarray
```

**Doc:** Đọc 1 clip về mono float32 @ target_sr (bounded — chỉ 1 clip trong RAM).

### `_compress_to_file` — L65

```python
def _compress_to_file(in_path: str, ratio: float) -> str
```

**Doc:** Nén 'ratio'× bằng rubberband giữ formant -> file tạm. ratio<=1 trả nguyên in_path.

### `_load_clips` — L86

```python
def _load_clips(work_dir: Path) -> list[dict]
```

### `_slot_sec` — L95

```python
def _slot_sec(c: dict) -> float
```

### `_natural_max_sec` — L99

```python
def _natural_max_sec(vi: str, slot: float) -> float
```

**Doc:** Trần độ dài đọc hợp lý (không phải câu TTS runaway).

### `_runaway_cap_sec` — L105

```python
def _runaway_cap_sec(c: dict, dur: float) -> float | None
```

**Doc:** VieNeu đôi khi hú 15–23s cho câu 1–2 tiếng. Cắt trần, không đẩy cả film.

### `is_runaway_tts` — L120

```python
def is_runaway_tts(c: dict, dur: float) -> bool
```

**Doc:** True nếu wav quá dài bất thường so với slot/chữ (VieNeu hú).

### `_resolve_max_speed` — L125

```python
def _resolve_max_speed(explicit: float | None) -> float
```

**Doc:** UI/API thắng. Env ASSEMBLE_MAX_SPEED chỉ khi không truyền (None).

### `_fit_mode` — L139

```python
def _fit_mode(max_speed: float) -> str
```

**Doc:** fixed (max_speed>1 từ UI/API) | adaptive (mặc định) | off (ASSEMBLE_FIT_MODE=off).

### `_is_bloated` — L147

```python
def _is_bloated(c: dict, dur: float) -> bool
```

**Doc:** TTS kéo dài bất thường so với số chữ, hoặc ASR dồn mốc (khe ≤0.25s mà đọc >0.6s).

### `_place` — L153

```python
def _place(c: dict, dur: float, orig: float, nxt: float, cursor: float, gap: float, mode: str, max_speed: float) -> tuple[float, float]
```

**Doc:** (start, ratio) của một câu theo chế độ khớp.

### `compute_fit_placements` — L173

```python
def compute_fit_placements(clips: list[dict], max_speed: float=1.0, gap: float=0.06) -> list[dict]
```

**Doc:** Đủ câu + khớp hình theo khoảng trống (KHÔNG cắt, nén theo _place).

### `write_fit_timings` — L219

```python
def write_fit_timings(work_dir: str | Path, max_speed: float | None=None, gap: float=0.06) -> Path
```

**Doc:** Ghi tts_fit.json từ tts.json (không cần ghép lại audio).

### `assemble` — L238

```python
def assemble(work_dir: str | Path, sr: int=48000, out_name: str='dub_tts.wav') -> dict
```

**Doc:** NAIVE: báo cáo độ khớp (từ metadata, mọi độ dài). Dựng file chỉ khi ngắn.

**Callers (spine):** server assemble stage (short / fit=False)

### `assemble_fit` — L284

```python
def assemble_fit(work_dir: str | Path, sr: int=48000, max_speed: float | None=None, gap: float=0.06, out_name: str='dub_fit.wav') -> dict
```

**Doc:** Đủ câu + ghép cạnh + bắt kịp khoảng trống (đúng yêu cầu user).

**Callers (spine):** server assemble stage (default / long)

### `main` — L396

```python
def main(argv=None)
```
