# Translate engine — ZH→VI script batches

- **Module:** `engines/translate.py`
- **Date:** 2026-11-06
- **Source:** AST extract (`scripts/_tmp_extract_sigs.py`)
- **Count:** 42 signatures in this doc

## Signatures

### `_tmodel` — L59

```python
def _tmodel() -> str | None
```

**Doc:** TRANSLATE_MODEL đọc lúc gọi (server import module 1 lần — MODEL ở trên bị đóng băng).

### `_rmodel` — L64

```python
def _rmodel() -> str | None
```

### `_is_llama_local_model` — L68

```python
def _is_llama_local_model(m: str | None) -> bool
```

### `_meaning_rules` — L84

```python
def _meaning_rules() -> str
```

**Doc:** Quy tắc chống dịch đen / lệch ngữ cảnh (lồng tiếng phim).

### `_style_rules` — L147

```python
def _style_rules() -> str
```

**Doc:** Quy tắc Manhua / short-drama: cứng Hán Việt + mềm hiện đại + xưng hô.

### `_character_rules` — L179

```python
def _character_rules() -> str
```

**Doc:** Chống nhầm nhân vật / sai giới tính khi dịch thoại.

### `_is_ancient_fantasy_genre` — L201

```python
def _is_ancient_fantasy_genre(plan: dict | None) -> bool
```

**Doc:** True khi phương án/genre thuộc tu tiên·cổ trang·wuxia·xianxia (không mixed đô thị).

### `_is_mixed_genre` — L225

```python
def _is_mixed_genre(plan: dict | None) -> bool
```

### `_mixed_address_rules` — L239

```python
def _mixed_address_rules() -> str
```

**Doc:** Đô thị dị năng + võ/KH: xưng hô hiện đại + cổ phong Hán Việt.

### `_ancient_address_rules` — L260

```python
def _ancient_address_rules() -> str
```

**Doc:** Chỉ inject khi genre tu tiên/cổ — không áp cho đô thị hiện đại.

### `_translate_rules` — L281

```python
def _translate_rules(plan: dict | None=None) -> str
```

**Doc:** Gộp nghĩa + văn phong + nhân vật (+ xưng hô theo genre).

### `_ocr_name_hints` — L290

```python
def _ocr_name_hints(work_dir: Path | None) -> list[str]
```

**Doc:** Tên/chữ trên hình từ ocr.json (nếu có) — gợi ý cho PLAN.

### `_resolve_translate_mode` — L317

```python
def _resolve_translate_mode(mode: str | None, model: str | None, n_todo: int) -> str
```

**Doc:** Trả 'oneshot' | 'batch'.

### `_has_cjk` — L345

```python
def _has_cjk(text: str) -> bool
```

**Doc:** Còn ký tự Hán trong bản dịch = model dịch sót/hỏng (đặc biệt model nhỏ local).

### `_salvage_mixed_vi` — L373

```python
def _salvage_mixed_vi(vi: str, *, zh: str='', plan: dict | None=None) -> str
```

**Doc:** Cứu VI lẫn Hán (vd «Đạt được 100% 增幅.») — không thì trả '' để vá lại.

### `build_plan` — L420

```python
def build_plan(segments: list[dict], target: str='Tiếng Việt', model: str | None=None, name_hints: list[str] | None=None, series_plan: dict | None=None) -> dict
```

**Doc:** LLM đọc toàn transcript -> phương án dịch: nhân vật, thuật ngữ, XƯNG HÔ, PHÂN CẢNH, tone.

### `_plan_block` — L588

```python
def _plan_block(p: dict) -> str
```

**Doc:** Đổ plan ra text nhét vào mọi prompt dịch. CHỐNG LỖI: model đôi khi trả

### `_plan_block_for_qa` — L700

```python
def _plan_block_for_qa(p: dict) -> str
```

**Doc:** Plan block gọn cho pronoun-QA / GPT vá đỏ — chỉ genre+style+pronouns.

### `_resolve_scene_context` — L774

```python
def _resolve_scene_context(plan: dict | None, rows: list[dict]) -> str
```

**Doc:** Xác định phân cảnh hiện tại của lô câu thoại (Scene-based context injection).

### `_norm_zh_cue` — L867

```python
def _norm_zh_cue(zh: str) -> str
```

**Doc:** Chuẩn hóa cue ZH để khớp lock (bỏ dấu câu/space).

### `ensure_hard_terms` — L875

```python
def ensure_hard_terms(plan: dict | None) -> dict
```

**Doc:** Gắn seed chengyu/taunt vào glossary.terms (không đè bản tay đã có).

### `hard_term_lock_map` — L925

```python
def hard_term_lock_map(plan: dict | None) -> dict[str, str]
```

**Doc:** zh_norm → vi bắt buộc (từ glossary type chengyu/idiom/combat_taunt/lock + seed).

### `apply_hard_term_locks` — L964

```python
def apply_hard_term_locks(rows: list[dict], plan: dict | None=None) -> int
```

**Doc:** Post-pass: cue ZH khớp lock → ghi đè VI (chuẩn, không phụ thuộc LLM).

### `normalize_vi_thousands` — L1011

```python
def normalize_vi_thousands(text: str) -> str
```

**Doc:** Dấu nghìn chuẩn Việt: 31 000 / 31,000 → 31.000.

### `apply_style_polish` — L1027

```python
def apply_style_polish(rows: list[dict], plan: dict | None=None) -> int
```

**Doc:** Post-pass deterministic: sửa calque / văn mẫu thường gặp (mixed short-drama).

### `_is_modernish_genre` — L1278

```python
def _is_modernish_genre(plan: dict | None) -> bool
```

**Doc:** Đô thị / mixed / hiện đại — cấm Ta–Ngươi cổ.

### `_char_aliases` — L1302

```python
def _char_aliases(plan: dict | None) -> dict[str, set[str]]
```

**Doc:** vi_name_lower → {zh, vi, aliases…} để khớp tên trong câu.

### `_pronoun_pairs` — L1320

```python
def _pronoun_pairs(plan: dict | None) -> list[dict]
```

### `_detox_modern_pronouns` — L1336

```python
def _detox_modern_pronouns(vi: str, zh: str) -> str
```

**Doc:** Ép Ta/Ngươi → Tôi/Cậu cho thoại đô thị (giữ «ông ta/cô ta/chúng ta»).

### `apply_pronoun_postpass` — L1362

```python
def apply_pronoun_postpass(rows: list[dict], plan: dict | None=None) -> int
```

**Doc:** Post-pass deterministic xưng hô — không phụ thuộc LLM nhớ ma trận.

### `_salvage_items` — L1428

```python
def _salvage_items(text: str) -> dict
```

**Doc:** Vớt từng object {"i":.., "vi":..} kể cả khi JSON TỔNG THỂ hỏng (model

### `translate_oneshot` — L1453

```python
def translate_oneshot(rows: list[dict], plan_block: str, target: str='Tiếng Việt', model: str | None=None, plan: dict | None=None) -> dict
```

**Doc:** Dịch TOÀN BỘ danh sách câu trong 1 lần gọi LLM (llama-server ctx lớn).

### `translate_batch` — L1521

```python
def translate_batch(rows: list[dict], plan_block: str, prev_ctx: list[dict], target: str='Tiếng Việt', model: str | None=None, plan: dict | None=None) -> dict
```

**Doc:** LƯỢT 1 — DỊCH NGHĨA KỊCH BẢN CHUẨN XÁC (Semantic Accuracy) theo Phân Cảnh (Scene) + Series Glossary. Trả {i: vi}.

### `_translate_safe` — L1596

```python
def _translate_safe(rows: list[dict], plan_block: str, prev_ctx: list[dict], target: str, model: str | None, plan: dict | None=None) -> dict
```

**Doc:** Dịch 1 lô CÓ CHỐNG LỖI: nếu parse hỏng hoặc LLM nuốt câu, CHIA ĐÔI lô rồi thử lại.

### `review_batch` — L1624

```python
def review_batch(rows: list[dict], plan_block: str, prev_ctx: list[dict], target: str='Tiếng Việt', model: str | None=None, plan: dict | None=None) -> dict
```

**Doc:** LƯỢT 2 — BẢN ĐỊA HÓA LỜI THOẠI LỒNG TIẾNG & KHỚP NHỊP PHỤ ĐỀ (Voice Dubbing Localization).

### `run_review` — L1697

```python
def run_review(work_dir: str | Path, batch: int=40, target: str='Tiếng Việt', model: str | None=None, force: bool=False) -> dict
```

**Doc:** LƯỢT 2: soát bản dịch nháp (script.json) bằng model chính xác (minimax) rồi

### `count_script_missing` — L1894

```python
def count_script_missing(work_dir: str | Path) -> int
```

**Doc:** Đếm câu trống trong script.json (nguồn sự thật cho UI / auto-vá).

**Callers (spine):** _auto_gpu fill pass

### `_trivial_vi` — L1906

```python
def _trivial_vi(zh: str) -> str | None
```

**Doc:** Câu chỉ cười/thán từ — không cần LLM (model hay trả lại chữ Hán → _has_cjk xoá).

### `_compress_zh_for_llm` — L1947

```python
def _compress_zh_for_llm(zh: str) -> str
```

**Doc:** Rút chuỗi cười/spam trước khi gửi LLM (tránh timeout / trả Hán).

### `clean_zh_spam` — L1952

```python
def clean_zh_spam(zh: str, max_rep: int=3, max_len: int=0) -> str
```

**Doc:** Rút 哈/呃/嗯/啊 spam + cụm chữ lặp (区域的区域的…) từ ASR.

### `run_translate` — L1989

```python
def run_translate(work_dir: str | Path, batch: int=20, target: str='Tiếng Việt', force: bool=False, model: str | None=None, mode: str | None=None) -> dict
```

**Callers (spine):** engines/translate.py __main__ via _run_engine

### `main` — L2502

```python
def main(argv=None)
```
