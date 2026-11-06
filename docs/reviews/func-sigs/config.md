# Config / env inject

- **Module:** `core/config.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 9

## Signatures

### `_load_cfg` — L20

```python
def _load_cfg(force: bool=False) -> None
```

**Doc:** Nạp lại pineline.config.json khi file đổi (tránh setdefault env khóa giá trị cũ).

### `save_config` — L44

```python
def save_config(updates: dict) -> dict
```

**Doc:** Cập nhật pineline.config.json an toàn + đồng bộ runtime.

### `_from_file_keys` — L85

```python
def _from_file_keys() -> set[str]
```

### `inject_env` — L89

```python
def inject_env() -> None
```

**Doc:** Chép pineline.config.json (rồi config.json) vào os.environ để tiến trình con kế thừa.

### `get` — L115

```python
def get(key: str, default: str | None=None) -> str | None
```

**Doc:** env var  >  config.json  >  default.

### `llm_settings` — L140

```python
def llm_settings() -> dict
```

**Doc:** LLM cho job (dịch/review) — đọc lúc gọi để sửa pineline.config.json có hiệu lực không cần restart.

### `pass_llm_model` — L155

```python
def pass_llm_model(kind: str='pronoun') -> str | None
```

**Doc:** Model cho pass ngắn (name/pronoun). Ưu tiên NAME_MODEL/PRONOUN_MODEL → CHATGPT_* → REVIEW → LLM.

### `agent_llm` — L172

```python
def agent_llm() -> dict
```

**Doc:** LLM cho agent chat / feeder: AGENT_* rồi LLM_* (cả hai file trước env).

### `venv_python` — L185

```python
def venv_python(venv_dir: str | Path) -> str
```

**Doc:** Đường dẫn python trong venv, đúng theo OS.
