# Pass1 413 — chặn upload theo số cue, fallback chat phình

- **Date:** 2026-11-11
- **Job / khu vực:** `translate.run_review_pass1_full_vi` · `365baf` (~4439 cue, SRT ~590KB)
- **Status:** fixed
- **Backup:** zip `Z:\PinelineV2_backup_2026-11-11_0033.zip` · codebak `Z:\PinelineV2_codebak\2026-11-11_pass1-upload-size\`

## Triệu chứng

Pass1 log `fallback chat lỗi: Aurora/ChatGPT 413 input_too_large` trên phim 4–5k cue dù file chỉ ~0.2–0.6MB. `brief=False`, `pairs=0`.

## Root cause

1. `REVIEW_PASS1_MAX_UPLOAD=800` đếm **câu** → skip upload khi >800 cue (dù SRT nhỏ).
2. Fallback chat nhét mọi heuristic flag ±1 → ~900 cue / message → Aurora 413.

## Evidence

- `365baf` `sub.review_pair.srt` ~590KB; `would skip upload? True` với trần 800 cue.
- Simulate fallback: flags~332 → pick_idx~944 → ~53KB chat (+ prompt) → 413.

## Fix

- Upload theo **`REVIEW_PASS1_MAX_UPLOAD_BYTES`** (mặc định 2MB); legacy cue cap = soft-warn (`MAX_UPLOAD=0` tắt).
- Fallback sample cứng `REVIEW_PASS1_FALLBACK_CUES=120`.
- Helpers `_pass1_should_upload` / `_pass1_fallback_sample_lines` + tests.
- Sync V2/V4/V5.

## Recheck

1. Job ≥2000 cue, SRT <2MB: log `[review-pass1] upload file (ok size=…)` (không `skip upload … câu >`).
2. Ép `REVIEW_PASS1_FORCE_SAMPLE=1`: log `fallback chat sample≤120`.
3. `pytest tests/test_review_pass1_upload.py`
4. **Pass nếu:** Pass1 có `brief=True` hoặc upload OK; fallback không 413 vì sample phình.
5. **Fail nếu:** vẫn skip chỉ vì số cue >800 khi file < MAX_UPLOAD_BYTES.

## Liên quan

- Keys: `REVIEW_PASS1_MAX_UPLOAD_BYTES`, `REVIEW_PASS1_FALLBACK_CUES`, `REVIEW_PASS1_FORCE_SAMPLE`
- Job đang REVIEW giữa chừng: Pass1 chỉ chạy lại ở lần `run_review` mới (không đụng lô hiện tại).
