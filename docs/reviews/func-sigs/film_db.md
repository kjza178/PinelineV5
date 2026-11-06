# Films SQLite DB

- **Module:** `core/film_db.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 35

## Signatures

### `_utc` — L109

```python
def _utc() -> str
```

### `norm_path` — L113

```python
def norm_path(p: str | None) -> str
```

### `connect` — L117

```python
def connect() -> sqlite3.Connection
```

### `log_event` — L153

```python
def log_event(job_id: str, kind: str, detail: Any='') -> None
```

### `_status_of` — L163

```python
def _status_of(stages: dict) -> tuple[str, str]
```

### `_series_season` — L177

```python
def _series_season(title: str, series_id: str | None) -> tuple[str, int | None]
```

### `_num` — L187

```python
def _num(v, cast=float)
```

### `_is_upload_lock_active` — L194

```python
def _is_upload_lock_active(job_id: str) -> bool
```

**Doc:** Kiểm tra nhanh xem .upload.lock của job còn thuộc về tiến trình đang sống không.

### `row_from_manifest` — L216

```python
def row_from_manifest(job_id: str, m: dict) -> dict
```

### `sync_one` — L282

```python
def sync_one(job_id: str) -> dict | None
```

**Doc:** Đồng bộ tức thì 1 job từ work/<job_id>/manifest.json vào films.db.

### `sync` — L322

```python
def sync(hg_library: list[dict] | None=None) -> dict
```

**Doc:** Quét manifest → upsert films; ghi event khi trạng thái đổi. Trả {new, changed, total}.

### `needs_series_ids` — L381

```python
def needs_series_ids() -> bool
```

### `sync_uploads` — L387

```python
def sync_uploads() -> int
```

**Doc:** Link YouTube từ Z:\yt_uploader\upload_history.jsonl và queue_state.json.

### `source_keys` — L473

```python
def source_keys() -> set[str]
```

### `series_ids` — L478

```python
def series_ids() -> set[str]
```

### `update_block_status` — L483

```python
def update_block_status(job_id: str, status: str, reason: str='') -> dict
```

**Doc:** Cập nhật trạng thái bản quyền (clean/blocked/claim/private/unknown) và lý do cho 1 phim.

### `query` — L503

```python
def query(q: str='', status: str='', limit: int=50, order: str='recent', work_exists: str | int | None=None, block_status: str='') -> list[dict]
```

### `get` — L537

```python
def get(job_id: str) -> dict | None
```

### `get_lite` — L548

```python
def get_lite(job_id: str) -> dict | None
```

**Doc:** 1 row films, không kèm events — cho queue/sort.

### `get_many` — L555

```python
def get_many(job_ids: list[str]) -> dict[str, dict]
```

**Doc:** Batch SELECT films theo job_id (không events). Giữ thứ tự ưu tiên theo input.

### `delete_film` — L578

```python
def delete_film(job_id: str, delete_work: bool=True) -> dict
```

**Doc:** Xoá 1 film khỏi database và tuỳ chọn xoá thư mục work trên ổ đĩa.

### `delete_films` — L599

```python
def delete_films(job_ids: list[str], delete_work: bool=True) -> dict
```

**Doc:** Xoá nhiều film theo danh sách job_id.

### `purge_missing` — L622

```python
def purge_missing(only_pending_failed: bool=False) -> dict
```

**Doc:** Xoá toàn bộ hoặc các job chưa hoàn thành mà thư mục work đã bị xoá (work_exists = 0).

### `stats` — L637

```python
def stats() -> dict
```

### `to_csv` — L657

```python
def to_csv(rows: list[dict]) -> str
```

### `_dur` — L669

```python
def _dur(sec) -> str
```

### `format_stats` — L676

```python
def format_stats() -> str
```

### `format_rows` — L690

```python
def format_rows(rows: list[dict]) -> str
```

### `format_detail` — L704

```python
def format_detail(job_id: str) -> str
```

### `upsert_library_block` — L726

```python
def upsert_library_block(name: str, core: str='', title_vi: str='', video_path: str='', status: str='unknown', reason: str='', test_yt_url: str='', test_yt_id: str='', test_sample_path: str='', recheck_at: str | None=None) -> dict[str, Any]
```

**Doc:** Lưu hoặc cập nhật trạng thái bản quyền phim trong Thư viện gốc.

### `get_library_block` — L792

```python
def get_library_block(name: str) -> dict[str, Any] | None
```

### `list_pending_rechecks` — L798

```python
def list_pending_rechecks() -> list[dict[str, Any]]
```

**Doc:** Lấy danh sách các bản ghi đang chờ recheck (status='testing').

### `list_library_blocks` — L807

```python
def list_library_blocks() -> dict[str, dict[str, Any]]
```

**Doc:** Trả về dict name -> record của tất cả các bộ đã check trong Thư viện.

### `delete_library_block` — L814

```python
def delete_library_block(name: str) -> bool
```

### `sync_library_blocks_from_yt_queue` — L820

```python
def sync_library_blocks_from_yt_queue(check_live: bool=False) -> list[dict[str, Any]]
```

**Doc:** Đồng bộ trạng thái bản quyền từ Z:\yt_uploader\queue_state.json cho các video D:\Lib.
