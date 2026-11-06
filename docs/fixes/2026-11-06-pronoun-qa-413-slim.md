# Pronoun-QA GPT vá đỏ → Aurora 413 (payload quá lớn)

- **Date:** 2026-11-06
- **Job / khu vực:** `run_post_translate_consistency` / `agent_pronoun_pass` / `llm._chatgpt_chat` (Aurora)
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-06_pronoun-qa-slim\` (+ zip snapshot nếu chạy)

## Triệu chứng

Sau dịch, bước pronoun-QA gọi ChatGPT/Aurora với full `_plan_block` inline → HTTP **413**; retry cùng payload vô ích, log spam, jumps không được vá.

## Root cause

`pronoun_consistency.run_post_translate_consistency` và `agent_pronoun_pass.run_pronoun_pass` nhét toàn bộ `_plan_block` (characters + terms + pronouns + style + scenes…) vào `_chatgpt_chat`. Analyze đã dùng file upload; QA chỉ cần pronouns + style. Job `4041cc3bb069_p02`: full ≈ **72KB** chars, slim ≈ **20KB**.

## Evidence

- Đo trên `D:\PinelineV2_work\4041cc3bb069_p02\glossary.json` (235 chars / 276 pronouns / 130 terms):
  - `_plan_block` = 72424
  - `_plan_block_for_qa` = 20119 (ratio ~0.28; không còn `NHÂN VẬT`)
- Log trước: `[llm] chatgpt lỗi … 413 …` rồi sleep/retry.

## Fix

- `translate._plan_block_for_qa` — genre/tone + STYLE LOCK + pronouns + pronoun_notes + `lock_banner` (1 lần); **không** dump characters/terms.
- `pronoun_consistency` + `agent_pronoun_pass` (V2/V4/V5) dùng slim block.
- `llm._chatgpt_chat`: status **400/413/422** → `LLMUnavailable` ngay, **không** sleep/retry.
- Test: `tests/test_pronoun_qa_slim_plan.py`.

## Recheck

1. Restart :8801 khi queue idle (nạp translate/llm/pronoun).
2. `python -m pytest tests/test_pronoun_qa_slim_plan.py -q` → 2 passed.
3. Đo lại: `from translate import _plan_block, _plan_block_for_qa` trên glossary job lớn → slim << full, có `XƯNG HÔ`.
4. Chạy pronoun-QA / post-translate consistency trên job có jumps → không còn chuỗi retry 413 cùng payload.
5. **Pass nếu:** slim < 50% full; 413 (nếu còn) fail ngay 1 lần; pronouns vẫn trong prompt.
6. **Fail nếu:** vẫn gửi `NHÂN VẬT`/`THUẬT NGỮ` trong QA; hoặc 413 bị retry 2–3 lần.

## Liên quan

- Job mẫu: `4041cc3bb069_p02`
- Sync V2 / V4 / V5
- `_plan_block` giữ nguyên cho translate batches
