# Stop lúc soát vẫn nhảy TTS / job không dừng

- **Date:** 2026-11-09
- **Job / khu vực:** `05670cbf7c1c` (Cao Võ Phần 9); `translate.run_review` / `run_translate` / `server._run_stage`
- **Status:** fixed
- **Backup zip:** (đợt review-fullvi) `Z:\PinelineV2_backup_2026-11-09_2130.zip`
- **Codebak:** `Z:\PinelineV2_codebak\2026-11-09_review-stop-honor\`

## Triệu chứng

User Stop all / Stop job khi đang «soát ~30%» — UI vẫn chạy, rồi nhảy TTS dù soát chưa xong.

## Root cause

1. Vòng `run_review` **không đọc** `.stop` giữa các lô → Stop chỉ ghi cờ, LLM vẫn soát hết lô đang gọi.
2. `run_translate` bắt mọi lỗi review (kể cả `stopped by user`) rồi **mark_done translate** + tiếp pipeline → TTS.
3. `translate_ready_for_tts` chỉ kiểm VI đủ, **không** kiểm `rv` → pipeline coi là xong dịch.

## Evidence

- Job `05670cbf7c1c`: script 3900 câu, `rv=1240` (~31%) khi UI soát 30.8%; sau Stop queue `current` vẫn busy rồi `stages.tts=running`.

## Fix

- `run_review`: check `.stop` mỗi lô → `RuntimeError("stopped by user")`.
- `run_translate`: stop lúc review → re-raise, không mark_done.
- `_translate_flow` / `_run_stage` / auto pipeline: coi stop như `_Stopped`, không nhảy TTS.
- Auto: nếu `AUTO_REVIEW` và còn câu chưa `rv` → dừng, không TTS.
- `review_only` API: `force=True` để soát lại từ đầu.

## Recheck

1. Chạy soát job dài → Stop giữa chừng.
2. **Pass nếu:** translate/tts không running; không tạo wav mới; `.stop` được tôn trọng trong vòng soát.
3. **Fail nếu:** sau Stop vẫn tăng `review_done` nhiều lô hoặc TTS `running`.

## Liên quan

- Job `05670cbf7c1c` đã clear `rv`, backup `script.before_rereview_*.json`, restart :8801, POST `review_only` force.
- Cần restart :8801 (đã) để nạp fix.
