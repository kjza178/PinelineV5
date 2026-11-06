# Agent core

- **Module:** `agents/agent_core.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 30

## Signatures

### `_films_tool` — L852

```python
def _films_tool(args: dict) -> str
```

### `_sidecar_cmd` — L866

```python
def _sidecar_cmd(text: str) -> str
```

### `_truthy` — L919

```python
def _truthy(v: Any) -> bool
```

### `tool_tier` — L923

```python
def tool_tier(name: str, args: dict | None) -> str
```

**Doc:** read | mutate | confirm. confirm = phá huỷ/tốn lâu, cần user bấm ✅ khi gọi từ Telegram.

### `describe_action` — L954

```python
def describe_action(name: str, args: dict | None) -> str
```

### `_prune_pending` — L962

```python
def _prune_pending(now: float) -> None
```

### `park_action` — L967

```python
def park_action(name: str, args: dict) -> dict
```

**Doc:** Giữ tool call lại chờ user xác nhận; trùng (name, args) chưa hết hạn thì dùng lại id cũ.

### `pending_actions` — L982

```python
def pending_actions() -> list[dict]
```

### `confirm_action` — L988

```python
def confirm_action(cid: str, approve: bool) -> dict
```

### `bind` — L1035

```python
def bind(runtime: Runtime) -> None
```

### `_require_rt` — L1040

```python
def _require_rt() -> Runtime
```

### `summarize_job` — L1046

```python
def summarize_job(j: dict, work_root: Path) -> dict
```

### `_load_script` — L1076

```python
def _load_script(work_root: Path, job_id: str) -> list[dict]
```

### `_line_brief` — L1086

```python
def _line_brief(r: dict) -> dict
```

### `_read_hold` — L1097

```python
def _read_hold(work_root: Path, job_id: str) -> dict
```

### `script_peek` — L1114

```python
def script_peek(work_root: Path, job_id: str, sample: int=5) -> dict
```

### `script_search` — L1136

```python
def script_search(work_root: Path, job_id: str, query: str='', missing_only: bool=False, limit: int=20) -> dict
```

### `script_get_lines` — L1163

```python
def script_get_lines(work_root: Path, job_id: str, i_from: int, i_to: int) -> dict
```

### `classify_jobs` — L1179

```python
def classify_jobs(jobs: list[dict], work_root: Path) -> dict
```

### `default_yt_draft` — L1207

```python
def default_yt_draft(work_root: Path, job_id: str, max_lines: int=12) -> dict
```

### `_dispatch` — L1247

```python
def _dispatch(name: str, args: dict, allow_mutate: bool) -> str
```

### `_llm_cfg` — L1640

```python
def _llm_cfg() -> tuple[str, str, str]
```

**Doc:** Cấu hình LLM cho Agent chat (có thể tách khỏi job translate) — config.agent_llm().

### `_chat_turn` — L1647

```python
def _chat_turn(messages: list[dict], use_tools: bool=True) -> dict
```

**Doc:** Một turn OpenAI chat/completions. Trả message dict (content + tool_calls).

### `_chat_turn_model` — L1665

```python
def _chat_turn_model(messages: list[dict], use_tools: bool, model: str) -> dict
```

### `_chat_turn_text_protocol` — L1697

```python
def _chat_turn_text_protocol(messages: list[dict], model: str | None=None) -> dict
```

**Doc:** Fallback khi model không tool-call: ép JSON {tool,args} hoặc {final}.

### `_parse_pycall_tool_calls` — L1772

```python
def _parse_pycall_tool_calls(content: str) -> list[dict]
```

**Doc:** Model hay in «Action: `hg_auto_flow(query_or_id="…", auto_run=True)`» thay vì gọi tool.

### `_parse_text_tool_calls` — L1818

```python
def _parse_text_tool_calls(content: str) -> list[dict]
```

**Doc:** Model qua proxy đôi khi in tool call dạng text (```json [{"name":..,"arguments":..}]```).

### `clip_tool_result` — L1859

```python
def clip_tool_result(result: str, limit: int=TOOL_RESULT_MAX) -> str
```

### `run_agent` — L1874

```python
def run_agent(message: str, *, history: list[dict] | None=None, allow_mutate: bool=False, max_steps: int=8, require_confirm: bool=False) -> AgentResult
```

**Doc:** Chạy agent. history = [{role, content}, ...] (user/assistant only).

### `status_snapshot` — L1950

```python
def status_snapshot() -> dict
```
