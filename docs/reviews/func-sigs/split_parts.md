# Auto-split / merge parent parts

- **Module:** `engines/split_parts.py`
- **Date:** 2026-11-06
- **Source:** AST extract (`scripts/_tmp_extract_sigs.py`)
- **Count:** 19 signatures in this doc

## Signatures

### `_is_disk_full_text` — L36

```python
def _is_disk_full_text(*chunks: str | None) -> bool
```

### `free_bytes` — L41

```python
def free_bytes(path: str | Path) -> int
```

**Doc:** Dung lượng trống trên volume chứa `path` (tạo parent nếu chưa có).

### `estimate_split_need_bytes` — L50

```python
def estimate_split_need_bytes(video_path: str | Path) -> int
```

**Doc:** Ước lượng chỗ cần cho split copy-mode (= gần bằng size nguồn + margin).

### `assert_enough_space_for_split` — L56

```python
def assert_enough_space_for_split(video_path: str | Path, out_dir: str | Path) -> None
```

### `_unlink_quiet` — L66

```python
def _unlink_quiet(path: Path) -> None
```

### `probe_duration` — L74

```python
def probe_duration(video_path: str | Path) -> float
```

**Doc:** Lấy thời lượng video tính bằng giây.

### `calculate_part_plan` — L90

```python
def calculate_part_plan(total_sec: float, target_hours: float=DEFAULT_TARGET_HOURS) -> list[tuple[float, float]]
```

**Doc:** Tính toán danh sách (start_sec, end_sec) cho từng part.

### `find_best_cut_point` — L111

```python
def find_best_cut_point(video_path: str | Path, target_cut_sec: float, search_radius_sec: float=90.0) -> float
```

**Doc:** Tìm điểm khoảng lặng (silence) gần nhất với target_cut_sec trong phạm vi ±search_radius_sec.

### `compute_smart_plan` — L152

```python
def compute_smart_plan(video_path: str | Path, target_hours: float=DEFAULT_TARGET_HOURS) -> list[dict]
```

**Doc:** Tính plan hoàn chỉnh có điểm cắt thông minh (tránh đứt câu thoại).

### `split_video_to_parts` — L194

```python
def split_video_to_parts(video_path: str | Path, out_dir: str | Path, target_hours: float=DEFAULT_TARGET_HOURS, prefix: str='part') -> list[dict]
```

**Doc:** Cắt video thành các part theo smart plan (lossless copy).

### `_hardlink_alias` — L331

```python
def _hardlink_alias(primary: Path, alias: Path) -> bool
```

**Doc:** Tạo alias cùng inode với primary. Không bao giờ copy2 (tránh nhân đôi GB).

### `cleanup_split_parts_dir` — L361

```python
def cleanup_split_parts_dir(parts_dir: str | Path) -> None
```

**Doc:** Xoá thư mục `_split_parts` dở (orphan GB sau fail / ENOSPC).

### `merge_parts_to_full` — L373

```python
def merge_parts_to_full(part_videos: list[str | Path], out_full_mp4: str | Path) -> Path
```

**Doc:** Nối danh sách các part đã render hoàn chỉnh thành 1 file full (lossless copy 30s).

### `split_job_to_subjobs` — L412

```python
def split_job_to_subjobs(job_id: str, target_hours: float=DEFAULT_TARGET_HOURS, work_root: str | Path='work') -> dict
```

**Doc:** Tự động chia một job video dài thành các sub-jobs (Part 1, Part 2...).

**Callers (spine):** maybe_auto_split_job

### `merge_job_parts` — L576

```python
def merge_job_parts(job_id: str, work_root: str | Path='work') -> dict
```

**Doc:** Kiểm tra các sub-job của job_id, nếu tất cả đã render xong thì ghép thành output_full.mp4.

**Callers (spine):** try_auto_merge_parent

### `is_split_subjob` — L675

```python
def is_split_subjob(work_dir: str | Path) -> bool
```

**Doc:** Part đã tách (…_p01) — không auto-split lần nữa.

### `maybe_auto_split_job` — L688

```python
def maybe_auto_split_job(job_id: str, *, work_root: str | Path='work', enabled: bool=True, target_hours: float=DEFAULT_TARGET_HOURS, min_hours: float | None=None) -> dict
```

**Doc:** Tự detect thời lượng video sau khi có source:

**Callers (spine):** _maybe_auto_split_guarded

### `try_auto_merge_parent` — L792

```python
def try_auto_merge_parent(job_id: str, *, work_root: str | Path='work', enabled: bool=True) -> dict | None
```

**Doc:** Sau khi một part mux xong: nếu mọi part done → merge output_full trên job cha.

**Callers (spine):** _queue_run_one after done

### `main` — L818

```python
def main()
```
