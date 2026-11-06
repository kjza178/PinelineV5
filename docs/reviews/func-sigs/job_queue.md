# Job queue + worker loop

- **Module:** `core/job_queue.py`
- **Date:** 2026-11-06
- **Source:** AST extract (`scripts/_tmp_extract_sigs.py`)
- **Count:** 30 signatures in this doc

## Signatures

### `get_job_info` — L23

```python
def get_job_info(job_id: str, *, prefer_db: bool=True) -> dict
```

**Doc:** Metadata hàng chờ: ưu tiên films.db (series_ui/season_ui), fallback manifest.

### `get_jobs_info` — L83

```python
def get_jobs_info(job_ids: list[str]) -> dict[str, dict]
```

**Doc:** Batch metadata cho nhiều job — 1 query DB + fallback file từng id thiếu.

### `job_sort_key` — L108

```python
def job_sort_key(job_id: str) -> tuple
```

**Doc:** Khóa sắp xếp: (group_id|series_norm, season P1..Pn, title).

### `_reset_for_tests` — L126

```python
def _reset_for_tests(load_disk: bool=False) -> None
```

**Doc:** Chỉ dùng trong pytest.

### `set_runner` — L149

```python
def set_runner(fn: Callable[[str, dict], tuple[str, str]]) -> None
```

### `is_wired_done` — L154

```python
def is_wired_done(work_dir: Path) -> bool
```

**Callers (spine):** queue_add; _queue_run_one; _worker_loop

### `_persist_path` — L167

```python
def _persist_path() -> Path
```

### `_save` — L171

```python
def _save() -> None
```

### `_load` — L188

```python
def _load() -> None
```

### `_hist_push` — L216

```python
def _hist_push(job_id: str, status: str, detail: str='') -> None
```

### `queue_busy` — L223

```python
def queue_busy() -> bool
```

**Doc:** True nếu worker đang chạy hoặc còn job trong hàng — dùng GPU gate heal/watch.

### `current_detail` — L229

```python
def current_detail(job_id: str | None, *, work_root: Path | None=None) -> dict | None
```

**Doc:** Stage/progress/ETA thô — đọc manifest của đúng 1 job (live).

### `build_queue_items` — L285

```python
def build_queue_items(job_ids: list[str]) -> list[dict]
```

**Doc:** Metadata pending — 1 batch films.db (+ fallback), không N lần parse manifest.

### `queue_state` — L307

```python
def queue_state(*, enrich: bool=True) -> dict
```

**Doc:** Trạng thái hàng chờ. enrich=True → queue_items/current_info qua batch DB.

### `http_queue_state` — L331

```python
def http_queue_state(*, work_root: Path | None=None) -> dict
```

**Doc:** Payload GET /api/queue/jobs: state + live current_detail + labels ngắn.

### `queue_add` — L350

```python
def queue_add(job_ids: list[str], opts: dict | None=None, skip_done: bool=True, sort_first: bool=True) -> dict
```

**Callers (spine):** api_queue_jobs_add; split_job_to_subjobs; maybe_auto_split

### `queue_sort` — L402

```python
def queue_sort(by: str='series_season') -> dict
```

**Doc:** Sắp xếp lại các job đang chờ trong hàng:

### `queue_move` — L419

```python
def queue_move(job_id: str, action: str) -> dict
```

**Doc:** Di chuyển vị trí của 1 job trong hàng chờ:

### `queue_reorder` — L449

```python
def queue_reorder(new_order: list[str]) -> dict
```

**Doc:** Gán lại toàn bộ thứ tự cho hàng chờ theo danh sách client gửi.

### `queue_add_group` — L461

```python
def queue_add_group(group_id: str, opts: dict | None=None, skip_done: bool=True) -> dict
```

**Doc:** Enqueue mọi member của group theo group_index tăng dần.

### `queue_front` — L500

```python
def queue_front(job_id: str) -> None
```

### `queue_remove` — L508

```python
def queue_remove(job_ids: list[str]) -> dict
```

**Doc:** Bỏ job khỏi hàng chờ (không stop current).

### `queue_update_opts` — L521

```python
def queue_update_opts(updates: dict[str, dict]) -> dict
```

**Doc:** Đổi opts của job ĐANG CHỜ tại chỗ (giữ thứ tự, không đụng current) — thay cho remove+add.

### `queue_clear` — L533

```python
def queue_clear() -> dict
```

### `queue_stop` — L541

```python
def queue_stop() -> dict
```

**Doc:** Clear queue + báo worker dừng; gọi _stop_job(current) nếu server đã wire.

### `set_stop_hook` — L563

```python
def set_stop_hook(fn: Callable[[str], None] | None) -> None
```

### `set_clear_stop_hook` — L567

```python
def set_clear_stop_hook(fn: Callable[[str], None] | None) -> None
```

### `_ensure_worker_unlocked` — L572

```python
def _ensure_worker_unlocked() -> None
```

**Callers (spine):** queue_add

### `_ensure_worker` — L583

```python
def _ensure_worker() -> None
```

### `_worker_loop` — L588

```python
def _worker_loop() -> None
```

**Callers (spine):** _ensure_worker_unlocked Thread
