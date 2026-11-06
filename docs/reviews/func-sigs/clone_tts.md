# Clone TTS engine

- **Module:** `engines/clone_tts.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 38

## Signatures

### `resolve_engine_python` — L55

```python
def resolve_engine_python(engine: str) -> str
```

**Doc:** Tìm python.exe của engine. Config sai path (thường sau install) -> thử chỗ mặc định.

### `_load_registry` — L91

```python
def _load_registry() -> dict
```

### `list_clone_voices` — L97

```python
def list_clone_voices() -> list[str]
```

**Doc:** Tên các giọng clone đã có ref audio hợp lệ.

### `_resolve_ref` — L107

```python
def _resolve_ref(ref: str) -> Path | None
```

### `voice_ref_text` — L116

```python
def voice_ref_text(voice: str) -> tuple[Path, str] | None
```

**Doc:** (ref_path, ref_text) của 1 giọng, hoặc None.

### `enroll_voice` — L127

```python
def enroll_voice(name: str, ref_path: str | Path, ref_text: str) -> str
```

**Doc:** Đăng ký giọng clone vào voices/f5_voices.json (VieNeu + OmniVoice dùng chung).

### `_is_trivial_vi` — L149

```python
def _is_trivial_vi(text: str | None) -> bool
```

**Doc:** True nếu không có chữ thật (vd ',', '...', '!!!') — không nên gọi TTS.

### `vi_for_tts` — L155

```python
def vi_for_tts(text: str | None) -> str
```

**Doc:** Chuẩn bị chữ cho VieNeu/Omni: gộp số có dấu nghìn để đọc đúng.

### `_write_silence_wav` — L180

```python
def _write_silence_wav(path: Path, dur_sec: float, sr: int=48000) -> float
```

**Doc:** Ghi wav im lặng đúng độ dài timeline (tối thiểu 0.15s để qua kiểm tra dur).

### `_silence_entry` — L195

```python
def _silence_entry(s: dict, out_dir: Path, engine: str) -> dict
```

**Doc:** Placeholder im lặng cho câu vô nghĩa / wav hỏng — đủ slot timeline, không báo thiếu.

### `_dur` — L203

```python
def _dur(path: Path) -> float
```

**Doc:** Độ dài wav (giây). Ưu tiên wave; fallback ffprobe.

### `_entry_from_wav` — L221

```python
def _entry_from_wav(s: dict, path: Path, engine: str) -> dict | None
```

**Doc:** Tạo entry tts.json từ file wav đã có. None nếu file hỏng/quá ngắn.

### `_unlink_quiet` — L232

```python
def _unlink_quiet(path: Path) -> None
```

### `_drop_runaway_from_done` — L239

```python
def _drop_runaway_from_done(segments: list, done: dict[int, dict], out_dir: Path) -> int
```

**Doc:** Resume/recheck: bỏ clip hú khỏi done + xóa wav → TTS sẽ đọc lại.

### `_pack_clip` — L258

```python
def _pack_clip(s: dict, path: Path, engine: str, speed: float, skip_pp: bool) -> dict | None
```

**Doc:** Postprocess + entry. None nếu hỏng. Caller xử lý runaway.

### `_recheck_pack_and_retry` — L267

```python
def _recheck_pack_and_retry(engine: str, ref: Path, ref_text: str, out_dir: Path, speed: float, segments: list, done: dict[int, dict], packed_ids: list[int], pre_done: set[int], total_target: int, voice: str, m) -> tuple[int, int]
```

**Doc:** Đóng gói todo vừa TTS; runaway -> xóa -> retry tối đa N lần -> silence slot.

### `_clip_key` — L342

```python
def _clip_key(vi: str, voice: str, engine: str, speed: float) -> str
```

### `_load_keys` — L347

```python
def _load_keys(out_dir: Path) -> dict[str, str] | None
```

### `_save_keys` — L355

```python
def _save_keys(out_dir: Path, keys: dict[str, str]) -> None
```

### `_stamp_keys` — L365

```python
def _stamp_keys(done: dict[int, dict], keys: dict[int, str] | None) -> None
```

### `_scan_done_from_disk` — L371

```python
def _scan_done_from_disk(out_dir: Path, segments: list, engine: str, done: dict[int, dict], disk_keys: dict[str, str] | None=None, keyof: dict[int, str] | None=None) -> dict[int, dict]
```

**Doc:** Resume: nhận diện seg_XXXX.wav đã ghi (sau khi Dừng) dù chưa kịp ghi tts.json.

### `_postprocess_clip` — L392

```python
def _postprocess_clip(path: Path, engine: str, speed: float) -> None
```

### `_salvage_progress` — L403

```python
def _salvage_progress(m, segments, done, tts_path, out_dir, engine, voice, speed, pre_done: set[int], err: BaseException | None=None, keys: dict[int, str] | None=None) -> None
```

**Doc:** Khi dừng/crash: gom wav đã có -> tts.json, status pending (để bấm Tiếp tục).

### `run_clone_tts` — L462

```python
def run_clone_tts(work_dir: str | Path, engine: str, voice: str, speed: float=1.0, force: bool=False) -> dict
```

**Callers (spine):** server._do_tts

### `_cleanup_audio` — L616

```python
def _cleanup_audio(path: Path) -> None
```

**Doc:** Làm sạch clip gen ra:

### `_trim_onset` — L646

```python
def _trim_onset(path: Path) -> bool
```

**Doc:** Cắt 'âm rác đầu' của OmniVoice: nếu đoạn tiếng ĐẦU TIÊN ngắn (<0.45s) và có

### `_apply_speed` — L683

```python
def _apply_speed(path: Path, speed: float) -> None
```

**Doc:** Đổi tốc độ đọc bằng rubberband giữ formant (fallback atempo). speed>1 nhanh, <1 chậm.

### `_run_worker` — L711

```python
def _run_worker(engine: str, ref: Path, ref_text: str, out_dir: Path, speed: float, lines: list, on_prog=None) -> None
```

**Doc:** Chạy worker venv cho `lines`=[(i,text)], ghi out_dir/seg_XXXX.wav. Raise nếu lỗi.

### `synth_one` — L840

```python
def synth_one(engine: str, voice: str, text: str, out_path: str | Path, speed: float=1.0) -> Path
```

**Doc:** Đọc 1 câu bằng engine+giọng -> ghi ra out_path (dùng cho nghe thử / đọc lại 1 clip).

### `resynth_clip` — L865

```python
def resynth_clip(work_dir: str | Path, i: int, engine: str, voice: str, speed: float=1.0) -> dict
```

**Doc:** Đọc lại DUY NHẤT câu index i -> tts/seg_i.wav + vá tts.json. Trả entry.

### `_norm_txt` — L885

```python
def _norm_txt(s: str) -> str
```

**Doc:** Chuẩn hoá để so khớp: thường hoá, bỏ dấu câu, gộp khoảng trắng.

### `_similar` — L893

```python
def _similar(a: str, b: str) -> float
```

### `_asr_check` — L901

```python
def _asr_check(clips_texts: list, device: str=None)
```

**Doc:** Nghe ngược list [(wav_path, expected_vi)] -> [(score, transcript)]. Whisper small.

### `verify_and_fix` — L920

```python
def verify_and_fix(work_dir, engine: str, voice: str, speed: float=1.0, min_score: float=0.55, max_retries: int=2) -> dict
```

**Doc:** TỰ KIỂM & SỬA: ASR nghe ngược từng clip, câu nào lệch nhiều so với bản dịch

### `_roughness` — L975

```python
def _roughness(path: Path) -> float
```

**Doc:** Độ 'nhám/méo' của clip: HF-ratio ở các khung CÓ CAO ĐỘ (voiced) — loại âm gió

### `fix_glitches` — L1003

```python
def fix_glitches(work_dir, engine: str, voice: str, speed: float=1.0, retries: int=2, abs_thresh: float=0.06, rel: float=1.8) -> dict
```

**Doc:** TỰ PHÁT HIỆN & SỬA câu bị vỡ/méo (âm): đo độ nhám voiced-frame, câu nào nhám

### `_prog` — L1063

```python
def _prog(m, n_done, total, engine, phase, voice: str | None=None, speed: float | None=None)
```

### `_finalize` — L1079

```python
def _finalize(m, segments, done, tts_path, out_dir, engine, voice, speed, keys=None)
```
