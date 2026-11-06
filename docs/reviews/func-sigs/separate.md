# Audio separation (Demucs)

- **Module:** `engines/separate.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 8

## Signatures

### `_find_video` — L39

```python
def _find_video(work_dir: Path) -> Path | None
```

### `_probe_duration` — L50

```python
def _probe_duration(path: Path) -> float
```

**Doc:** Lấy thời lượng file media (giây) qua ffprobe.

### `_update_sep_progress` — L63

```python
def _update_sep_progress(m: Manifest, pct: float | None, cur_text: str) -> None
```

**Doc:** Cập nhật tiến độ vào stage 'separate' VÀ đồng bộ sang stage 'asr' nếu ASR đang chờ tách giọng.

### `_extract_audio` — L82

```python
def _extract_audio(video: Path, out_audio: Path) -> None
```

**Doc:** Tách audio GỐC chất lượng cao (stereo 44.1k) — khác audio.wav 16k mono của ASR.

### `_run_demucs_on_file` — L100

```python
def _run_demucs_on_file(src_audio: Path, tmp_out: Path, device: str, work_dir: Path, m: Manifest, chunk_idx: int=0, n_chunks: int=1) -> tuple[Path, Path]
```

**Doc:** Chạy Demucs trên 1 file audio (ngắn hoặc 1 chunk) và trả về (no_vocals_wav, vocals_wav).

### `_concat_wav_chunks` — L170

```python
def _concat_wav_chunks(chunk_files: list[Path], out_wav: Path, work_dir: Path) -> None
```

**Doc:** Ghép các chunk WAV thành 1 file WAV hoàn chỉnh (dùng -rf64 auto để hỗ trợ >4GB cho phim dài).

### `run_separate` — L194

```python
def run_separate(work_dir: str | Path, device: str='cuda', force: bool=False) -> dict
```

**Callers (spine):** server._auto_gpu if audio_mode demucs_* (spine §1)

### `main` — L360

```python
def main(argv=None)
```
