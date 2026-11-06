# ASR engine — Whisper path

- **Module:** `engines/asr/asr.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 13

## Signatures

### `_audio_marker` — L46

```python
def _audio_marker(wav: Path) -> Path
```

### `_src_id` — L50

```python
def _src_id(src: Path) -> dict
```

### `extract_audio` — L56

```python
def extract_audio(src: str | Path, out_wav: str | Path) -> str
```

**Doc:** Tách audio về 16kHz mono PCM — chuẩn đầu vào Whisper. Ghi .partial rồi replace + marker nguồn.

### `_wav_seconds` — L78

```python
def _wav_seconds(p: Path) -> float
```

### `_probe_seconds` — L91

```python
def _probe_seconds(p: Path) -> float
```

### `audio_wav_stale` — L100

```python
def audio_wav_stale(src: str | Path, wav: str | Path, keep_legacy: bool=False) -> bool
```

**Doc:** audio.wav có sẵn không dùng được: rỗng, marker khác nguồn / khác filter mốc, hoặc (chưa có

### `ensure_audio_wav` — L130

```python
def ensure_audio_wav(src: str | Path, wav: str | Path, force: bool=False, keep_legacy: bool=False) -> bool
```

**Doc:** Trích audio.wav khi thiếu / hỏng / khác nguồn (hoặc force). True nếu vừa trích.

### `resolve_asr_source` — L144

```python
def resolve_asr_source(work_dir: str | Path, video_src: str | Path | None=None, force_demucs: bool=False, device: str='cuda') -> Path
```

**Doc:** Xác định nguồn audio sạch và chuẩn xác cho ASR.

### `_cut_wav_from` — L197

```python
def _cut_wav_from(src_wav: Path, out_wav: Path, start_sec: float) -> None
```

**Doc:** Cắt phần còn lại từ start_sec (resume ASR giữa chừng).

### `pick_device` — L206

```python
def pick_device(device: str) -> tuple[str, str]
```

**Doc:** Chọn cuda nếu có GPU, không thì cpu. Trả (device, compute_type).

### `_salvage_asr` — L219

```python
def _salvage_asr(m: Manifest, asr_path: Path, rows: list, wav: Path | None, total: float, err: BaseException | None=None) -> None
```

**Doc:** Crash/treo: giữ asr.json đã có, status pending để bấm Tiếp tục.

### `run_asr` — L247

```python
def run_asr(work_dir: str | Path, model_size: str='large-v3', lang: str='zh', device: str='auto', compute_type: str | None=None, force: bool=False) -> dict
```

**Callers (spine):** server._do_asr / _auto_gpu Whisper path

### `main` — L421

```python
def main(argv=None)
```
