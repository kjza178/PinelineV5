# Subtitle burn / SRT helpers

- **Module:** `engines/subs.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 34

## Signatures

### `_plain_len` — L27

```python
def _plain_len(text: str) -> int
```

### `_mask_number_dots` — L49

```python
def _mask_number_dots(text: str) -> str
```

**Doc:** Che dấu nghìn trong số để không bị tách câu tại «3.000» / «31,000».

### `_unmask_number_dots` — L55

```python
def _unmask_number_dots(text: str) -> str
```

### `glue_vi_names` — L101

```python
def glue_vi_names(text: str) -> str
```

**Doc:** Dán NBSP trong tên riêng — không xuống dòng giữa «Thiên Lang Tinh».

### `unglue_vi_names` — L113

```python
def unglue_vi_names(text: str) -> str
```

### `_is_compound_break` — L117

```python
def _is_compound_break(text: str, pos: int) -> bool
```

**Doc:** True nếu cắt tại pos đang tách đôi compound (…tấn| công…).

### `_snap_cut_to_vi_word` — L131

```python
def _snap_cut_to_vi_word(text: str, pos: int) -> int
```

**Doc:** Ưu tiên cắt tại khoảng trắng VI; không cắt giữa từ / giữa số / compound.

### `_snap_cut_outside_number` — L154

```python
def _snap_cut_outside_number(text: str, pos: int) -> int
```

**Doc:** Đẩy điểm cắt ra ngoài token số (tránh «31.» + «000 tỷ»).

### `split_text_by_punct` — L165

```python
def split_text_by_punct(text: str, max_chars: int=0, weak: bool=True) -> list[str]
```

**Doc:** Tách câu theo dấu câu. weak=True: mỗi mệnh đề sau ，、, là 1 đoạn (thoại TTS).

### `_join_clause` — L212

```python
def _join_clause(a: str, b: str) -> str
```

**Doc:** CJK dính liền; VI/Latin cần khoảng trắng («Đù,» + «thế…» → «Đù, thế…»).

### `_is_punct_only` — L222

```python
def _is_punct_only(text: str) -> bool
```

### `_split_for_display` — L226

```python
def _split_for_display(text: str, max_chars: int, force_weak: bool=False, hard: bool=False) -> list[str]
```

**Doc:** Tách text cho sub: dấu câu -> dấu phẩy; hard=True thì cắt cứng phần còn dài.

### `_slice_contiguous` — L263

```python
def _slice_contiguous(text: str, weights: list[int]) -> list[str]
```

**Doc:** Cắt 1 chuỗi thành N đoạn liên tiếp theo trọng số — không trộn với câu khác.

### `merge_tiny_segments` — L314

```python
def merge_tiny_segments(segments: list[dict], key: str='text', min_chars: int=4, min_dur: float=0.45) -> list[dict]
```

**Doc:** Gộp mảnh ASR vụn: chỉ dấu câu, cắt giữa từ, clip < 0.45s quá ngắn.

### `_merge_parts` — L360

```python
def _merge_parts(parts: list[str], n: int) -> list[str]
```

**Doc:** Gộp parts dư thành đúng n cụm (ghép các cụm ngắn nhất liên tiếp).

### `_expand_parts` — L379

```python
def _expand_parts(parts: list[str], n: int, max_chars: int) -> list[str]
```

**Doc:** Chia parts ít hơn n thành đủ n cụm.

### `_align_zh_vi` — L397

```python
def _align_zh_vi(zh_parts: list[str], vi_parts: list[str], max_zh: int, max_vi: int) -> list[tuple[str, str]]
```

**Doc:** Căn số cụm zh/vi; ưu tiên zh làm mốc thời gian.

### `_spread_time_pairs` — L410

```python
def _spread_time_pairs(pairs: list[tuple[str, str]], start: float, end: float, min_dur: float=0.35) -> list[tuple[str, str, float, float]]
```

**Doc:** Chia [start,end] theo độ dài vi (fallback zh).

### `_split_hard` — L433

```python
def _split_hard(text: str, max_chars: int) -> list[str]
```

**Doc:** Cắt cứng theo từ (Việt) hoặc ký tự (CJK) khi không còn dấu câu.

### `split_long_segments` — L527

```python
def split_long_segments(segments: list[dict], max_chars: int=18, key: str='text', min_dur: float=0.35, max_dur: float=4.0) -> list[dict]
```

**Doc:** Tách câu quá dài / quá lâu thành nhiều đoạn; chia thời gian theo độ dài chữ.

### `split_bilingual_rows` — L571

```python
def split_bilingual_rows(rows: list[dict], max_zh: int=18, max_vi: int=50, max_dur: float=4.0, min_dur: float=0.35) -> list[dict]
```

**Doc:** Sau dịch ZH→VI: tách sub dài (CUT). Ưu tiên cắt theo VI rồi cắt ZH liền mạch.

### `carry_tail_fragments` — L727

```python
def carry_tail_fragments(rows: list[dict], max_vi: int=37, max_gap: float=0.6) -> list[dict]
```

**Doc:** «…sáu mươi đứa. Đúng,» + «cùng lên…» → mảnh đầu câu sau sang cue kế tiếp.

### `merge_broken_vi_number_rows` — L755

```python
def merge_broken_vi_number_rows(rows: list[dict]) -> list[dict]
```

**Doc:** Gộp mảnh lệch số: «…31,» + «000 tỷ» / «当前血量31,» + «000亿» → 1 câu.

### `heal_script_broken_numbers` — L799

```python
def heal_script_broken_numbers(rows: list[dict]) -> tuple[list[dict], int]
```

**Doc:** Gộp số gãy trên script (giữ i của câu đầu) — trả (rows_mới, số_cặp_đã_gộp).

### `sub_split_cfg` — L805

```python
def sub_split_cfg() -> tuple[int, int, float]
```

### `_merge_short_orphans` — L813

```python
def _merge_short_orphans(parts: list[str], max_chars: int, orphan_max: int=12) -> list[str]
```

**Doc:** Gộp đuôi ngắn («này?», «Tinh,») — không nuốt lại «nhiều.» / «trường,».

### `wrap_subtitle_text` — L857

```python
def wrap_subtitle_text(text: str, max_chars: int=50, max_lines: int=1) -> str
```

**Doc:** Gói phụ đề tối đa max_lines dòng, mỗi dòng ≤ max_chars.

### `_wrap_cfg` — L942

```python
def _wrap_cfg(key: str='vi') -> tuple[int, int]
```

### `expand_placed_with_display` — L949

```python
def expand_placed_with_display(placed: list[dict], display: list[dict], key: str='vi') -> list[dict]
```

**Doc:** Tách mỗi câu TTS (script 1:1) theo mảnh CUT trong script.display (src_i).

### `_maybe_wrap` — L1017

```python
def _maybe_wrap(text: str, key: str) -> str
```

### `fmt_ts` — L1029

```python
def fmt_ts(sec: float) -> str
```

**Doc:** Giây (float) -> 'HH:MM:SS,mmm' theo chuẩn SRT.

### `to_srt` — L1040

```python
def to_srt(segments: list[dict], key: str='text') -> str
```

**Doc:** Đổ list câu ra chuỗi SRT. Bỏ câu rỗng, đánh số lại liên tục.

**Callers (spine):** server SRT export; translate.py; agent_pronoun_pass

### `to_srt_fit` — L1056

```python
def to_srt_fit(segments: list[dict], durs: dict, key: str='vi', margin: float=0.35, min_dur: float=0.8) -> str
```

**Doc:** SRT burn theo script + dur TTS gốc (KHÔNG biết đàn hồi assemble).

### `to_srt_placed` — L1084

```python
def to_srt_placed(placed: list[dict], key: str='vi', margin: float=0.12, min_dur: float=0.5) -> str
```

**Doc:** SRT burn khớp giọng sau assemble_fit: dùng start/end thật trên dub_fit.wav.
