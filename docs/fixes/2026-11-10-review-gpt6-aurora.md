# UI «backup Aurora» không rà — Gemma bỏ sót NMT vô nghĩa

- **Date:** 2026-11-10
- **Job / khu vực:** `60892cc63cb7_p01/p02` · REVIEW · Aurora/:3377
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-10_review-gpt6\`

## Triệu chứng

User chọn UI «backup Aurora∥» nhưng VI vẫn sai nặng (分手补偿→Chia thường, 脆皮→da mỏng, 运动员→vận hành viên). Job `review_model` = Gemma26b.

## Root cause

1. `review_backup=aurora_parallel` chỉ lưu `queue_opts` — **không** đổi model trong `run_review`.
2. `REVIEW_MODEL` production = `llama/gemma4-26b…` (sau quyết định local nhanh).
3. NMT primary + Gemma review không bắt calque/sai nghĩa loại trên.

## Evidence

- `queue_opts.review_backup=aurora_parallel` trên 60892; `stages.translate.review_model=llama/gemma4-26b…`
- Smoke `chatgpt/gpt-6` sửa đúng 3 câu mẫu.

## Fix

- Config: `REVIEW_MODEL=chatgpt/gpt-6`, `AURORA_REVIEW_MODEL=chatgpt/gpt-6`, `REVIEW_BACKUP=aurora_parallel`
- `translate._resolve_review_model`: aurora_parallel → GPT Aurora
- UI label → «Aurora GPT∥»; stamp `review_model` khi POST translate
- Force re-review CLI p01/p02 bằng `chatgpt/gpt-6`

## Recheck

1. Manifest `review_model` chứa `chatgpt/gpt-6` khi đang soát.
2. Sau xong: i=15/47/50 không còn «Chia thường» / «da mỏng» / «vận hành viên».
3. **Pass nếu:** REVIEW log `Model=chatgpt/gpt-6`; 3 cue trên đúng nghĩa.
4. **Fail nếu:** vẫn Gemma hoặc UI Aurora không đổi model.

## Liên quan

- User chọn `chatgpt/gpt-6`. DECISIONS 11-10.
