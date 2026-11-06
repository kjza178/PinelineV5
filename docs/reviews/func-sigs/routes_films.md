# Films HTTP routes

- **Module:** `http_routes/routes_films.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 31

## Signatures

### `_get_base_url` — L25

```python
def _get_base_url(req: Request) -> str
```

### `films_ui` — L31

```python
def films_ui()
```

### `list_films` — L39

```python
def list_films(q: str=Query('', description='Tìm theo tên/mã'), status: str=Query('', description='Lọc theo trạng thái'), limit: int=Query(5000, description='Giới hạn số lượng'), order: str=Query('recent', description='Thứ tự sắp xếp'), work_exists: Optional[str]=Query(None), block_status: str=Query(''))
```

### `export_films_csv` — L68

```python
def export_films_csv(q: str=Query(''), status: str=Query(''), limit: int=Query(5000), order: str=Query('recent'), work_exists: Optional[str]=Query(None), block_status: str=Query(''))
```

### `get_film` — L93

```python
def get_film(job_id: str)
```

### `sync_films` — L101

```python
def sync_films()
```

### `delete_films` — L110

```python
def delete_films(payload: Dict[str, Any]=Body(...), req: Request=None)
```

### `purge_missing` — L126

```python
def purge_missing(payload: Dict[str, Any]=Body(...))
```

### `check_block_films` — L133

```python
def check_block_films(payload: Dict[str, Any]=Body(...))
```

### `check_block_all` — L146

```python
def check_block_all()
```

### `get_library` — L160

```python
def get_library(req: Request)
```

### `library_accounts` — L169

```python
def library_accounts()
```

### `library_action` — L178

```python
def library_action(payload: Dict[str, Any]=Body(...), req: Request=None)
```

**Doc:** Ủy thác feeder (skip/priority/add/merge/…) — không gọi film_db.mark_library_* (API không tồn tại).

### `library_set_block_status` — L198

```python
def library_set_block_status(payload: Dict[str, Any]=Body(...))
```

### `library_clear_samples` — L207

```python
def library_clear_samples()
```

### `library_cut_sample` — L216

```python
def library_cut_sample(payload: Dict[str, Any]=Body(...))
```

### `library_enqueue_test` — L227

```python
def library_enqueue_test(payload: Dict[str, Any]=Body(...))
```

### `library_test_url` — L239

```python
def library_test_url(payload: Dict[str, Any]=Body(...))
```

### `library_scan_queue` — L249

```python
def library_scan_queue()
```

### `tc_status` — L262

```python
def tc_status()
```

### `tc_reset_quota` — L267

```python
def tc_reset_quota(project_id: Optional[str]=Query(None))
```

### `tc_recheck_health` — L272

```python
def tc_recheck_health()
```

### `tc_auth_url` — L278

```python
def tc_auth_url(req: Request, redirect_uri: Optional[str]=Query(None), project_id: Optional[str]=Query(None))
```

### `tc_callback` — L289

```python
def tc_callback(req: Request, code: str=Query(''), state: str=Query(''))
```

### `tc_finish_auth` — L311

```python
def tc_finish_auth(req: Request, payload: Dict[str, Any]=Body(...))
```

### `tc_disconnect` — L323

```python
def tc_disconnect()
```

### `tc_test_one` — L329

```python
def tc_test_one(payload: Dict[str, Any]=Body(...))
```

### `tc_batch_start` — L341

```python
def tc_batch_start(payload: Dict[str, Any]=Body(...))
```

### `tc_batch_progress` — L351

```python
def tc_batch_progress()
```

### `tc_recheck_one` — L356

```python
def tc_recheck_one(payload: Dict[str, Any]=Body(...))
```

### `tc_recheck_pending` — L363

```python
def tc_recheck_pending(payload: Dict[str, Any]=Body(...))
```
