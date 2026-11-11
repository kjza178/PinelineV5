# REVIEW Pass1 full VI + duty F nửa câu vô nghĩa

- **Date:** 2026-11-09
- **Job / khu vực:** `translate.py` run_review / review_batch / filter; test `D:\PinelineV2_tmp\job5_review_pass1_test`
- **Status:** fixed
- **Backup zip:** `Z:\PinelineV2_backup_2026-11-09_2130.zip`
- **Codebak:** `Z:\PinelineV2_codebak\2026-11-09_review-fullvi-pass\`

## Triệu chứng

Soát LLM chỉ thấy lô nhỏ + giữ NMT tối thiểu → bỏ sót câu VI vô nghĩa / đuôi treo do ASR cắt (vd «Tôi cũng vậy, trước đó.» + cue sau mới có nội dung).

## Root cause

- Không có pass đọc full VI trước khi rà từng câu.
- Duty review A–E không phủ nửa câu/vô nghĩa; filter cosmetic drop mọi viết lại mạch ý.
- Gemma thường bỏ sót dù đã flag.

## Evidence

- User example + sandbox win_01 (26 cue). Pass1 flag `nonsense_i` gồm 0,1 + pair [0,1].
- Trước siết: Gemma chỉ sửa 1 câu (i=14), bỏ i=0/1.
- Sau `apply_halfcue_dangling_heal` + must-fix prompt: i=0 `Tôi cũng vậy, trước đó.` → `Tôi cũng vậy.`; 7 diffs.

## Fix

- Pass1 `run_review_pass1_full_vi` (upload pair SRT / fallback text) → `review_pass1.json`.
- Duty **(F)** + filter giữ F; batch mở ±1 cue.
- Deterministic `apply_halfcue_dangling_heal` (đuôi «trước đó» khi ZH cắt 之前).
- Config `REVIEW_PASS1_FULL_VI=1`.

## Recheck

1. `python -c` heuristic flags [0,1] + filter giữ fix F.
2. `run_review(D:\PinelineV2_tmp\job5_review_pass1_test, force=True)`.
3. **Pass nếu:** i=0 không còn đuôi «trước đó»; `DIFF.md` có thay đổi; `review_pass1.json` tồn tại.
4. **Fail nếu:** i=0 vẫn `…trước đó.` sau review.

## Liên quan

- Kết quả: `docs/reviews/2026-11-09-review-pass1-halfcue/` + `D:\PinelineV2_tmp\job5_review_pass1_test\`
- Cần restart :8801 khi queue rảnh.
