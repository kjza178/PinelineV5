# Playlist expand / yt-dlp

- **Module:** `engines/playlist.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 5

## Signatures

### `_build_url_from_entry` — L37

```python
def _build_url_from_entry(entry: dict, platform: str) -> str | None
```

**Doc:** Lấy URL đầy đủ từ một entry playlist. extract_flat có khi chỉ trả id.

### `expand_meta` — L53

```python
def expand_meta(url: str, cookies: str | None=None, cookies_dir: str | Path | None='cookies', cookies_from_browser: str | None=None, proxy: str | None=None) -> dict
```

**Doc:** Như expand nhưng trả THÊM metadata để gom nhóm:

**Callers (spine):** yt-dlp playlist probe (spine §1)

### `expand` — L106

```python
def expand(url: str, cookies: str | None=None, cookies_dir: str | Path | None='cookies', cookies_from_browser: str | None=None, proxy: str | None=None) -> list[str]
```

**Doc:** Đọc link, trả danh sách URL video. Video đơn -> [url]; playlist -> [nhiều].

**Callers (spine):** server import; job create playlist expand

### `batch_download` — L119

```python
def batch_download(url: str, work_root: str | Path='work', workers: int=2, conn: int=3, cookies: str | None=None, cookies_dir: str | Path | None='cookies', cookies_from_browser: str | None=None, proxy: str | None=None, force: bool=False, on_done=None) -> list[dict]
```

**Doc:** Tải tất cả video của 1 link. Trả list kết quả {url, job_id, ok, error}.

### `main` — L176

```python
def main(argv=None)
```
