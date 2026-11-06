# Job metadata

- **Module:** `core/job_meta.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 5

## Signatures

### `parse_season_from_text` — L12

```python
def parse_season_from_text(*texts: str) -> int | None
```

**Doc:** Bóc số phần/mùa từ title (Phần N / P N / 第N季).

### `norm_series_key` — L41

```python
def norm_series_key(name: str) -> str
```

**Doc:** Chuẩn hoá tên bộ để sort.

### `extract_ui_meta` — L55

```python
def extract_ui_meta(*, job_id: str='', title_vi: str='', req_title: str='', title_zh: str='', group_id: Any=None, group_title: Any=None, group_index: Any=None) -> dict[str, Any]
```

**Doc:** Trả title/series/season/group_* theo semantics hàng chờ (VI).

### `info_from_manifest_dict` — L121

```python
def info_from_manifest_dict(job_id: str, data: dict) -> dict[str, Any]
```

### `info_from_film_row` — L134

```python
def info_from_film_row(row: dict | None) -> dict[str, Any] | None
```

**Doc:** Map films.db row → shape get_job_info. None nếu row thiếu title.
