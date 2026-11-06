# LLM providers (ChatGPT / Gemini / local)

- **Module:** `engines/llm.py`
- **Date:** 2026-11-06
- **Source:** AST extract (`scripts/_tmp_extract_sigs.py`)
- **Count:** 23 signatures in this doc

## Signatures

### `_settings` — L58

```python
def _settings() -> tuple[str, str, str]
```

**Doc:** (base, key, model) đọc LÚC GỌI (file config trước env) — sửa pineline.config.json

### `_llama_base` — L69

```python
def _llama_base() -> str
```

### `get_llama_models` — L77

```python
def get_llama_models(llama_base: str | None=None) -> list[str]
```

**Doc:** Lấy danh sách các model đang load trên llama-server (:8083).

### `get_ollama_models` — L95

```python
def get_ollama_models(ollama_base: str | None=None) -> list[str]
```

**Doc:** Lấy danh sách model trên Ollama (:11434).

### `list_available_models` — L108

```python
def list_available_models() -> dict
```

**Doc:** Trả về toàn bộ model khả dụng (llama-server 8083, ollama 11434, config).

### `_is_loopback_base` — L158

```python
def _is_loopback_base(url: str) -> bool
```

### `is_local` — L163

```python
def is_local(model: str | None) -> bool
```

### `is_chatgpt` — L170

```python
def is_chatgpt(model: str | None) -> bool
```

**Doc:** Model route qua Aurora / Chat2Api (pool account Free). Tiền tố chatgpt/ hoặc aurora/.

### `_chatgpt_settings` — L176

```python
def _chatgpt_settings() -> tuple[list[str], str, str]
```

**Doc:** (bases, key, default_model) cho Aurora pool.

### `_jwt_expired` — L204

```python
def _jwt_expired(token: str) -> bool
```

**Doc:** True nếu JWT có claim exp đã qua (token local hết hạn không được đè Aurora pool).

### `_chatgpt_token_file` — L219

```python
def _chatgpt_token_file() -> str
```

**Doc:** Đọc access token tùy chọn từ data/chatgpt_token.txt (bỏ qua nếu JWT hết hạn).

### `_chatgpt_chat` — L238

```python
def _chatgpt_chat(model: str, messages: list[dict], temperature: float, max_tokens: int, json_mode: bool, retries: int, timeout: int) -> str
```

**Doc:** Gọi Aurora/Chat2Api (OpenAI-compatible). Pool Free xoay phía server Aurora.

### `aurora_upload_file` — L315

```python
def aurora_upload_file(path: str | Path, purpose: str='assistants') -> dict
```

**Doc:** Upload file lên Aurora `POST /v1/files` (cần ChatGPT access_token thật).

### `_file_unread_response` — L391

```python
def _file_unread_response(text: str) -> bool
```

**Doc:** GPT trả JSON/text báo không đọc được file đã upload (thường do lệch account pool).

### `chatgpt_chat_with_file` — L411

```python
def chatgpt_chat_with_file(file_id: str, prompt: str, model: str | None=None, temperature: float=0.1, max_tokens: int=8192, json_mode: bool=True, timeout: int=300, base: str | None=None, account_id: str | None=None) -> str
```

**Doc:** Hỏi GPT kèm file đã upload (`type: input_file` + `file_id`) — 1 lần đọc file.

### `ensure_ollama_model` — L513

```python
def ensure_ollama_model(name: str) -> None
```

**Doc:** Model Ollama chưa pull -> TỰ pull (lần đầu, có thể vài GB). Auto cho bước dịch.

### `free_ollama_vram` — L535

```python
def free_ollama_vram(reason: str='') -> None
```

**Doc:** Alias — nhả VRAM (Ollama + torch) trước/sau bước GPU.

### `unload_local` — L541

```python
def unload_local(model: str | None) -> None
```

**Doc:** Nhả model Ollama khỏi VRAM (RTX 3060 12GB không chứa nổi LLM + TTS cùng

### `_ollama_num_ctx` — L550

```python
def _ollama_num_ctx() -> int
```

**Doc:** Gemma3/4 mặc định context 131072. Cấp KV 128k trên RTX 3060 12GB -> tràn

### `_ollama_chat` — L560

```python
def _ollama_chat(model, messages, temperature, max_tokens, json_mode, retries, timeout) -> str
```

**Doc:** Gọi Ollama qua endpoint GỐC /api/chat + TẮT thinking (think=False).

### `chat` — L612

```python
def chat(messages: list[dict], model: str | None=None, temperature: float=0.3, max_tokens: int=8192, json_mode: bool=False, retries: int=4, timeout: int=300, **kwargs) -> str
```

**Doc:** Gửi messages, trả về text của assistant. Tự retry khi lỗi mạng/429/5xx.

**Callers (spine):** translate batches; pronoun_consistency; agents

### `chat_with_meta` — L765

```python
def chat_with_meta(messages: list[dict], model: str | None=None, temperature: float=0.3, max_tokens: int=8192, json_mode: bool=False, timeout: int=300) -> tuple[str, dict]
```

**Doc:** Giống chat() OpenAI-path nhưng trả (content, meta) gồm usage/timings/TPS.

### `parse_json` — L822

```python
def parse_json(text: str)
```

**Doc:** Bóc JSON kể cả khi model bọc trong ```json ... ```, trailing commas hoặc kèm chữ thừa.
