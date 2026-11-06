# Auto publisher daemon

- **Module:** `agents/auto_publisher.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 34

## Signatures

### `get_auto_state` — L60

```python
def get_auto_state() -> dict[str, Any]
```

**Doc:** Lấy trạng thái tiến trình tự động xuất bản (đồng bộ liên tiến trình qua file).

### `update_auto_state` — L83

```python
def update_auto_state(**kwargs) -> dict[str, Any]
```

**Doc:** Cập nhật trạng thái tiến trình và ghi đồng bộ ra file cho các tiến trình khác đọc.

### `_read_publish_queue` — L106

```python
def _read_publish_queue() -> list[dict[str, Any]]
```

### `_write_publish_queue` — L116

```python
def _write_publish_queue(items: list[dict[str, Any]]) -> None
```

### `_enqueue_job_record` — L124

```python
def _enqueue_job_record(job_id: str, privacy: str | None=None, schedule_hours: float | None=None, force: bool=False) -> list[dict[str, Any]]
```

**Doc:** Thêm job vào hàng chờ upload liên tiến trình (data/auto_publish_queue.json).

### `_dequeue_job_record` — L176

```python
def _dequeue_job_record(job_id: str) -> list[dict[str, Any]]
```

**Doc:** Xoá job khỏi hàng chờ upload sau khi đã xử lý xong.

### `_sync_queue_state_badge` — L191

```python
def _sync_queue_state_badge() -> None
```

**Doc:** Đồng bộ số lượng và danh sách job đang chờ upload vào auto_publish_state.json.

### `touch_active_locks` — L203

```python
def touch_active_locks() -> None
```

**Doc:** Làm mới mtime của các file lock đang giữ khi upload chunk lớn (tránh bị coi là stale).

### `is_pid_alive` — L214

```python
def is_pid_alive(pid: int) -> bool
```

**Doc:** Kiểm tra xem PID có đang thực sự chạy trên Windows không.

### `get_job_lock_path` — L231

```python
def get_job_lock_path(job_id: str) -> Path
```

**Doc:** Xác định đường dẫn file lock của job (ưu tiên trong thư mục work/<job_id>).

### `acquire_job_lock` — L239

```python
def acquire_job_lock(job_id: str, stale_sec: float=14400.0) -> tuple[int | None, Path, int | None]
```

**Doc:** Chiếm lock liên tiến trình cho job_id.

### `release_job_lock` — L277

```python
def release_job_lock(fd: int | None, lock_path: Path | None) -> None
```

**Doc:** Giải phóng lock liên tiến trình cho job.

### `acquire_global_publish_lock` — L293

```python
def acquire_global_publish_lock(job_id: str, wait_timeout: float=14400.0, stale_sec: float=14400.0) -> tuple[int | None, Path]
```

**Doc:** Chiếm khoá upload toàn cục liên tiến trình để đảm bảo tại mọi thời điểm

### `release_global_publish_lock` — L349

```python
def release_global_publish_lock(fd: int | None, lock_path: Path | None) -> None
```

**Doc:** Giải phóng khoá upload toàn cục liên tiến trình.

### `is_any_job_uploading` — L365

```python
def is_any_job_uploading(stale_sec: float=14400.0) -> tuple[bool, str | None]
```

**Doc:** Kiểm tra xem có bất kỳ job nào đang trong quá trình tự động xuất bản không.

### `is_job_uploading` — L390

```python
def is_job_uploading(job_id: str) -> bool
```

**Doc:** Kiểm tra job có đang được xử lý upload ở bất kỳ tiến trình nào không.

### `load_config` — L408

```python
def load_config() -> dict[str, Any]
```

**Doc:** Tải cấu hình tự động upload.

### `save_config` — L429

```python
def save_config(cfg: dict[str, Any]) -> dict[str, Any]
```

**Doc:** Lưu cấu hình tự động upload.

### `get_youtube_service` — L438

```python
def get_youtube_service(account_id: str='default')
```

**Doc:** Lấy YouTube API service từ tài khoản trong Z:\yt_uploader\accounts.

### `format_youtube_title` — L456

```python
def format_youtube_title(ai_title: str, clean_name: str='', season: int | None=None) -> str
```

**Doc:** Chuẩn hoá tiêu đề YouTube theo format chuẩn: Phần X | [Tên phim] - [Hook].

### `upload_to_youtube` — L510

```python
def upload_to_youtube(video_path: str | Path, title: str, description: str, tags: list[str] | str, thumb_path: str | Path | None=None, privacy: str='unlisted', publish_at: str | None=None, account_id: str='default', category_id: str='24') -> dict[str, Any]
```

**Doc:** Upload trực tiếp video + thumbnail lên YouTube qua API v3.

### `_revert_job_to_done` — L629

```python
def _revert_job_to_done(job_id: str, error_msg: str | None=None) -> None
```

**Doc:** Hoàn trả trạng thái job về 'done' khi quá trình upload bị lỗi hoặc gián đoạn để không bị kẹt ở 'uploading'.

### `enqueue_publish` — L655

```python
def enqueue_publish(job_id: str, privacy: str | None=None, schedule_hours: float | None=None, force: bool=False) -> dict[str, Any]
```

**Doc:** Đưa job vừa hoàn thành vào hàng đợi xuất bản tuần tự (không làm đứt quãng job đang upload).

### `_drain_publish_queue_async` — L680

```python
def _drain_publish_queue_async() -> None
```

**Doc:** Khởi chạy luồng nền xử lý tuần tự từng job trong hàng đợi nếu chưa có luồng drain nào đang chạy.

### `_is_yt_upload_limit_error` — L694

```python
def _is_yt_upload_limit_error(err: Any) -> bool
```

**Doc:** True nếu YouTube báo hết hạn mức upload ngày (uploadLimitExceeded).

### `_drain_publish_queue_loop` — L704

```python
def _drain_publish_queue_loop() -> None
```

**Doc:** Vòng lặp lấy từng job từ hàng đợi ra xuất bản tuần tự cho đến khi hết.

### `publish_job` — L749

```python
def publish_job(job_id: str, privacy: str | None=None, schedule_hours: float | None=None, force: bool=False) -> dict[str, Any]
```

**Doc:** Quy trình toàn diện: Sinh Metadata qua Aurora → Dựng Thumbnail 16:9 → Upload lên YouTube.

**Callers (spine):** auto_publisher daemon thread

### `_publish_job_internal` — L827

```python
def _publish_job_internal(job_id: str, privacy: str | None=None, schedule_hours: float | None=None, force: bool=False) -> dict[str, Any]
```

### `_collect_and_enqueue_done_jobs` — L1191

```python
def _collect_and_enqueue_done_jobs() -> list[dict[str, Any]]
```

**Doc:** Đồng bộ films.db, tự động giải cứu các job bị kẹt trạng thái 'uploading' mồ côi (không còn tiến trình giữ lock),

### `scan_and_publish_completed_jobs` — L1252

```python
def scan_and_publish_completed_jobs() -> dict[str, Any]
```

**Doc:** Quét và tự động xuất bản tất cả các job đã xong (done) nhưng chưa upload.

### `_scan_and_publish_impl` — L1311

```python
def _scan_and_publish_impl() -> int
```

### `_auto_publish_worker_loop` — L1353

```python
def _auto_publish_worker_loop()
```

**Doc:** Vòng lặp chạy ngầm tự động quét sau mỗi 60 giây.

### `start_worker` — L1364

```python
def start_worker()
```

**Doc:** Khởi động worker ngầm nếu chưa chạy.

### `stop_worker` — L1375

```python
def stop_worker()
```

**Doc:** Dừng worker ngầm.
