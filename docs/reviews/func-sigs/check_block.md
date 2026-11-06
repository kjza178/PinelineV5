# Block check / QA blocks

- **Module:** `engines/check_block.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 4

## Signatures

### `_utc_now` — L21

```python
def _utc_now() -> str
```

### `extract_video_id` — L25

```python
def extract_video_id(url_or_id: str) -> str
```

**Doc:** Trích xuất Video ID (11 ký tự) từ link YouTube bất kỳ hoặc ID thô.

### `check_youtube_block` — L52

```python
def check_youtube_block(url_or_id: str, timeout: int=12) -> dict[str, Any]
```

**Doc:** Kiểm tra video YouTube có bị Block hay dính bản quyền không (không cần cookie/đăng nhập).

### `check_film_by_job` — L319

```python
def check_film_by_job(job_id: str) -> dict[str, Any]
```

**Doc:** Kiểm tra trạng thái bản quyền của một phim theo job_id và lưu kết quả vào film_db.
