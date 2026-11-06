# Download engine — yt-dlp source fetch

- **Module:** `engines/download.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 20

## Signatures

### `_request_stop` — L54

```python
def _request_stop(work_dir) -> None
```

### `_is_stopped` — L59

```python
def _is_stopped(work_dir) -> bool
```

### `_clear_stop` — L64

```python
def _clear_stop(work_dir) -> None
```

### `_kill_job_aria2c` — L69

```python
def _kill_job_aria2c(work_dir) -> None
```

**Doc:** Kill tiến trình aria2c đang tải cho ĐÚNG job này (nhận diện qua job_id/đường

### `_aria2_downloaded` — L91

```python
def _aria2_downloaded(ctrl_path) -> int
```

**Doc:** Byte ĐÃ TẢI THẬT theo file điều khiển .aria2. Khi tải đa kết nối, file .part

### `_clean_incomplete_fragments` — L113

```python
def _clean_incomplete_fragments(work_dir) -> list
```

**Doc:** Xoá RIÊNG các mảnh tải DỞ (file .part + control .aria2) để tải lại sạch bằng

### `_delete_sources` — L127

```python
def _delete_sources(work_dir) -> bool
```

**Doc:** Xoá mọi source.* ; trả True nếu SẠCH (không còn file nào kẹt/khoá).

### `_format_sel` — L141

```python
def _format_sel(max_height: int | None=None, *, hevc: bool=False) -> str
```

**Doc:** Selector yt-dlp. max_height giới hạn chiều cao; hevc=True ưu tiên H.265 cùng độ phân giải.

### `_cfg_max_height` — L172

```python
def _cfg_max_height() -> int | None
```

**Doc:** DOWNLOAD_MAX_HEIGHT từ env/config (vd 720/480). 0/off = không giới hạn.

### `_cfg_prefer_hevc` — L190

```python
def _cfg_prefer_hevc() -> bool
```

**Doc:** DOWNLOAD_PREFER_HEVC=1 → ưu tiên H.265 cùng độ phân giải (file nhẹ, CDN đỡ đứt).

### `_auto_height_for_duration` — L202

```python
def _auto_height_for_duration(duration_sec: float | None, cap: int | None) -> int | None
```

**Doc:** Phim rất dài (Bilibili multi-season) → 720p AVC dễ ~3GB+, CDN hay đứt.

### `_probe_duration` — L216

```python
def _probe_duration(url: str, base_opts: dict) -> float | None
```

**Doc:** Lấy duration nhanh (không tải) để chọn format.

### `detect_platform` — L232

```python
def detect_platform(url: str) -> str
```

### `normalize_url` — L243

```python
def normalize_url(url: str) -> str
```

**Doc:** Chuyển link Bilibili kiểu mới về format yt-dlp hiểu (từ code Galaxy).

### `job_id_from_url` — L252

```python
def job_id_from_url(url: str) -> str
```

**Doc:** Job id mặc định = hash URL. Chạy lại cùng URL -> cùng thư mục -> resume.

**Callers (spine):** server._create / create_job

### `find_cookie_file` — L257

```python
def find_cookie_file(platform: str, cookies_dir: str | Path | None) -> str | None
```

**Doc:** Tìm file cookie theo nền tảng trong cookies_dir (vd bilibili_cookies.txt).

### `get_aria2c_path` — L271

```python
def get_aria2c_path() -> str | None
```

**Doc:** Tìm aria2c -> trả ĐƯỜNG DẪN TUYỆT ĐỐI (yt-dlp tìm external_downloader trong

### `apply_speed_opts` — L281

```python
def apply_speed_opts(opts: dict, conn: int=4) -> dict
```

**Doc:** Tải mảnh song song + aria2c nếu có (args tune từ code Galaxy).

### `download_video` — L305

```python
def download_video(url: str, work_dir: str | Path, cookies: str | None=None, cookies_dir: str | Path | None='cookies', cookies_from_browser: str | None=None, proxy: str | None=None, force: bool=False, conn: int=4, fresh: bool=False) -> dict
```

**Doc:** Tải 1 video về work_dir. Trả về dict trạng thái stage (video_path + metadata).

**Callers (spine):** server._auto_pipeline / _queue_run_one download stage

### `main` — L659

```python
def main(argv=None)
```
