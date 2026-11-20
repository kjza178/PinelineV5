# Park «còn 1 câu có chữ Hán» — backup soát không vá CJK đã rv

- **Date:** 2026-11-20
- **Job / khu vực:** `233da4eb69fb` i=882; `translate_simple` repair/gate
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-20_cjk-backup-repair\`

## Triệu chứng

Sau vá DeepSeek vẫn park: `cổng=park · còn 1 câu có chữ Hán` → `review_failed` sau vài lượt. Ví dụ VI còn `投影` dù đã rv=1.

## Root cause

`review_backup` / `backup_model` chỉ làm lại câu **chưa rv** (lô API lỗi). Câu đã soát nhưng còn CJK vẫn chỉ qua `repair.run(model=DeepSeek)` → hết round → gate park. Không có lượt Aurora cho cờ cứng.

## Evidence

- Log: `[simple] cổng=park · ['còn 1 câu có chữ Hán']` · job `233da4eb69fb`
- script i=882: `Tạm thời cắt lấy một投影 của Ngân Hoài Hư,` · `backup_model=chatgpt/gpt-6` đã bật nhưng không được gọi ở bước vá

## Fix

- Sau vá chính: nếu còn cờ `cjk`/`empty` và có `backup_model` → `repair.run(..., model=backup, rounds=1)`.
- Ops job này: sửa tay `投影`→`hình chiếu`, gỡ HOLD, resume ghế.
- Test `tests/test_cjk_backup_repair.py`.

## Recheck

1. `python -m pytest -q tests/test_cjk_backup_repair.py`
2. Job mới/soát lại: log có `[simple] N câu cjk/empty sau vá … → dự phòng chatgpt/gpt-6`
3. **Pass nếu:** hết CJK cứng thì không park chỉ vì 1 chữ Hán sót sau DeepSeek.
4. **Fail nếu:** vẫn park CJK mà không thấy dòng dự phòng (và server chưa restart).

## Liên quan

- Quyết định main+backup 11-20; `PLAN_MODEL_BACKUP` / review aurora.
- **Cần restart :8801** để nạp pipeline mới.
