# Auto-split / ASR promote chồng luồng (parent 80% + TTS lại sau mux)

- **Date:** 2026-11-05
- **Job / khu vực:** `server.py` auto-split / `_auto_gpu` / `_promote_asr_source`; V4/V5 thêm `maybe_auto_split_job`
- **Status:** fixed (cần **restart** server để nạp)

## Triệu chứng

Phim dài đã merge Full + part đã `output.mp4`, UI parent kẹt **80% Part k/N**; part quay lại **TTS/dịch** dù mux xanh.

## Root cause

1. V2 `_check_and_run_auto_split_parts` không skip khi `split_info=merged` → pass 2 chạy lại mọi part.
2. `_promote_asr_source` luôn `_invalidate_translate_for_asr` kể cả cùng nguồn → TTS stale.
3. V4/V5 `maybe_auto_split_job` trả `already` vẫn `split=True` → caller xếp lại toàn bộ part.

## Evidence

- Job `d01dbbc2d703`: merged 19:11; mux UI `running Part 5/5 @80`; p05 TTS pass 2 sau mux 18:59.

## Fix

- V2: early-return merged+Full; lock `_AUTO_SPLIT_ACTIVE`; skip part `_part_pipeline_complete`; promote cùng nguồn → không invalidate.
- V4/V5: `_part_pipeline_complete` + promote same-source; `maybe_auto_split`: `already_merged` / chỉ enqueue part chưa wired-done.
- Backup: `Z:\PinelineV2_codebak\2026-11-05_autosplit-conflict-guards\`

## Recheck

1. Restart :8801 / :8804 / :8805 (khi không đang encode quan trọng).
2. Trigger run-all parent đã `merged` → log `skip (chống luồng chồng)` / `already_merged`; không TTS lại part mux-done.
3. **Pass nếu:** parent không còn 80% giả; part mux-done không vào `_auto_gpu`.
4. **Fail nếu:** promote cùng nguồn vẫn stale TTS / pass 2 chạy đủ 5 part.

## Liên quan

- ENOSPC split guard riêng: `2026-11-05-split-enospc-guard.md`
