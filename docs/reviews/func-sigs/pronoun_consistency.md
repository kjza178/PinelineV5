# Pronoun / name consistency QA

- **Module:** `engines/pronoun_consistency.py`
- **Date:** 2026-11-06
- **Source:** AST extract (`scripts/_tmp_extract_sigs.py`)
- **Count:** 30 signatures in this doc

## Signatures

### `_cfg` — L30

```python
def _cfg(key: str, default: str | None=None) -> str | None
```

### `analyze_enabled` — L38

```python
def analyze_enabled() -> bool
```

### `analyze_model` — L43

```python
def analyze_model() -> str
```

### `chunk_size` — L54

```python
def chunk_size() -> int
```

### `analyze_mode` — L61

```python
def analyze_mode() -> str
```

**Doc:** file = upload SRT ZH 1 lần (Aurora /v1/files). fast = mẫu+lô. full = quét hết.

### `max_chunks` — L66

```python
def max_chunks() -> int
```

### `min_chunks_before_stop` — L73

```python
def min_chunks_before_stop() -> int
```

### `early_stop_enabled` — L80

```python
def early_stop_enabled() -> bool
```

### `is_pronouns_locked` — L85

```python
def is_pronouns_locked(plan: dict | None) -> bool
```

### `mark_locked` — L94

```python
def mark_locked(plan: dict, source: str='analyze_full_zh') -> dict
```

### `export_zh_lines` — L110

```python
def export_zh_lines(segments_or_rows: list[dict]) -> list[dict]
```

**Doc:** Chuẩn hoá [{i, zh}] từ asr segments hoặc script rows.

### `write_zh_export` — L128

```python
def write_zh_export(work_dir: Path, lines: list[dict]) -> Path
```

### `write_zh_srt` — L138

```python
def write_zh_srt(work_dir: Path, lines: list[dict], segments: list[dict] | None=None) -> Path
```

**Doc:** Xuất sub.zh.srt để Aurora upload (API.md: POST /v1/files).

### `_apply_analyze_delta_to_plan` — L174

```python
def _apply_analyze_delta_to_plan(plan: dict, data: dict, source: str) -> dict
```

### `analyze_via_srt_file` — L193

```python
def analyze_via_srt_file(work_dir: Path, plan: dict, lines: list[dict], segments: list[dict] | None=None, model: str | None=None) -> dict
```

**Doc:** Upload sub.zh.srt → GPT đọc 1 lần → glossary pronouns (Aurora file QA).

### `select_analyze_lines` — L281

```python
def select_analyze_lines(lines: list[dict], mode: str | None=None) -> list[dict]
```

**Doc:** fast: phủ đầu/giữa/cuối + câu có hô ngữ — ít lô hơn full scan.

### `_slim_memory` — L323

```python
def _slim_memory(memory: dict) -> dict
```

**Doc:** Giảm token gửi Aurora mỗi lô.

### `_merge_pronouns` — L347

```python
def _merge_pronouns(base: list, incoming: list) -> list
```

### `_merge_chars` — L375

```python
def _merge_chars(base: list, incoming: list) -> list
```

### `_analyze_chunk` — L393

```python
def _analyze_chunk(chunk: list[dict], memory: dict, model: str, genre_hint: str) -> dict
```

### `analyze_full_zh` — L430

```python
def analyze_full_zh(work_dir: str | Path, plan: dict | None=None, segments: list[dict] | None=None, model: str | None=None, force: bool=False) -> dict
```

**Doc:** A) Quét toàn bộ ZH theo lô + memory → cập nhật plan + lock pronouns.

### `lock_banner` — L597

```python
def lock_banner(plan: dict | None) -> str
```

**Doc:** Block inject vào plan_block / batch khi đã lock.

### `review_lock_rules` — L623

```python
def review_lock_rules(plan: dict | None) -> str
```

**Doc:** Prompt ép 31B review: khi đã lock thì CẤM đổi self/call.

### `fix_preserves_locked_register` — L639

```python
def fix_preserves_locked_register(vi_nhap: str, vi_fix: str) -> bool
```

**Doc:** True nếu bản sửa không đổi thanh ngữ chính so với nháp (khi đang lock).

### `filter_review_fixes_for_lock` — L658

```python
def filter_review_fixes_for_lock(fixes: dict[int, str], rows: list[dict], plan: dict | None) -> dict[int, str]
```

**Doc:** Khi pronouns_locked: loại fix làm đổi thanh ngữ so với vi_nhap.

### `ledger_from_prev` — L681

```python
def ledger_from_prev(prev_ctx: list[dict] | None) -> str
```

**Doc:** B) Ledger từ vài câu VI trước — nhắc model giữ thanh ngữ đang dùng.

### `_forms_in` — L706

```python
def _forms_in(vi: str) -> set[str]
```

### `find_pronoun_jumps` — L718

```python
def find_pronoun_jumps(rows: list[dict], window: int=JUMP_WINDOW) -> list[dict]
```

**Doc:** C) QA: trong cửa sổ gần nhau, vừa có {anh,em} vừa có {ông} ngôi hô / tôi lệch kiểu.

### `ensure_analyze_before_translate` — L761

```python
def ensure_analyze_before_translate(work_dir: str | Path, plan: dict, segments: list[dict] | None=None, force: bool=False) -> tuple[dict, dict]
```

**Doc:** Gọi từ translate.run_translate sau khi có plan.

### `run_post_translate_consistency` — L784

```python
def run_post_translate_consistency(work_dir: str | Path, rows: list[dict], plan: dict | None, fix_with_gpt: bool=True) -> dict
```

**Doc:** C+D sau dịch/polish: post-pass + QA jumps + GPT vá đỏ.
