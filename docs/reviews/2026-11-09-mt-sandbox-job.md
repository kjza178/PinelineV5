# Sandbox translate — job slice 120 cues

- **Date:** 2026-11-09 ~04:20
- **Source job:** `0a5f60aead18` (slice 120 câu đầu non-empty)
- **Work dir:** `D:\PinelineV2_tmp\mt_sandbox_job`
- **Cmd:** `python translate.py … --force --batch 20` (V2 code, không restart :8801)

## Kết quả

| Bước | Kết quả |
|------|---------|
| PLAN_MODE=file | Aurora upload OK nhưng **parse JSON fail** (14.9k chars) → fallback **sample** |
| Sample plan | cloud gemma 429 → local gemma → 2 NV / 6 terms (mỏng) rồi **series_glossary** đổ 68 NV |
| Pronoun-analyze file | parse JSON fail → fallback **fast** → LOCK 42 cặp |
| NMT primary | **base** (`robebo116__60-zh-vi` local) · **119/119** câu · 0 còn LLM vá |
| Review GPT mini | 6 lô ×20 · sửa ~16–18 câu/lô · missing=0 |
| Runtime | ~14 phút |

## Follow-up ~05:07 (keep-NMT filter)

Re-run sau `_filter_cosmetic_nmt_fixes`: NMT↔final **82 same / 38 changed (32%)** (trước 87% đổi); review bỏ **47** cosmetic, apply **5**; i=48 giữ «Lão tử…». Tổng kết: `docs/reviews/2026-11-09-mt-keepnmt-final.md`.

## Ghi chú

1. **Bug vận hành:** `chatgpt_chat_with_file` trả text dài nhưng `parse_json` fail (plan + pronoun file). Cần salvage JSON / `json_mode` cứng hơn trước khi tin PLAN_MODE=file production.
2. Series memory cứu glossary khi plan sample mỏng.
3. NMT primary + GPT rà **chạy end-to-end OK** trên sandbox.
4. Lệch còn lại chủ yếu style polish `ngươi→cậu`, không phải review GPT.

## Recheck

```bat
python translate.py D:\PinelineV2_tmp\mt_sandbox_job --force --batch 20
```

Pass nếu: log `[mt-zh-vi] PRIMARY` + `NMT chính … còn 0` + `[pipeline] ✅ XONG: NMT dịch chính + LLM rà soát` + `script.json` đủ vi.
