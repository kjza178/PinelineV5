# Đồng nhất xưng hô A–C (analyze full ZH → lock → ledger → QA)

- **Date:** 2026-11-02
- **Job / khu vực:** V2 / V4 / V5 — `pronoun_consistency.py` + `translate`
- **Status:** fixed (partial vs diarization — không 100%)
- **Backup:** `Z:\PinelineV2_codebak\2026-11-02_pronoun-consistency-abc\`

## Triệu chứng

Câu trước anh–em, câu sau ông–tôi / cậu–tôi — lệch xuyên phim dù đã có post-pass mỏng.

## Root cause

Ma trận pronouns không quét full ZH + không lock; mỗi lô dịch tự chọn thanh ngữ; không QA nhảy ngôi.

## Evidence

- Pytest `tests/test_pronoun_consistency.py` + postpass: 7 passed (V2/V4/V5).

## Fix

- Module `pronoun_consistency.py`: analyze full ZH (lô+memory qua Aurora), lock, ledger, QA jumps, GPT vá đỏ.
- `translate`: analyze sau plan; inject lock/ledger vào batch; post consistency sau polish/review.
- Config: `PRONOUN_ANALYZE=1`, `PRONOUN_ANALYZE_MODEL=chatgpt/gpt-5-6-mini`, chunk 120.

## Recheck

1. Restart :8801 / :8804 / :8805.
2. Job mới: log `[pronoun-analyze] … LOCK` rồi dịch; có `pronoun_lock.json`.
3. Sau dịch: `pronoun_qa.json` (jumps).
4. **Pass nếu:** glossary `style_lock.pronouns_locked=true`; ít nhảy anh/em↔ông trong cùng đoạn.
5. **Fail nếu:** analyze skip khi chưa lock; hoặc vẫn nhảy ngôi hàng loạt.

## Liên quan

- User: làm hết 3 bản; Aurora files API công khai chưa có → analyze = chat lô + memory (xuất `zh_full_for_pronoun.txt`).
