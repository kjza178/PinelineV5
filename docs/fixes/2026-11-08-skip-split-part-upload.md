# Auto-split part (Phần N/N) bị đưa vào upload

- **Date:** 2026-11-08
- **Job / khu vực:** auto_publisher · Films uploader banner · `ad50b61b4050_p02`
- **Status:** fixed

## Triệu chứng

Banner upload hiện `«高武：我成为了全系武者第八季 - Phần 2/2» · 60%`. Part auto-split (`…_pNN`, title `Phần N/N`) bị xếp upload YouTube — chỉ nên upload bản Full sau merge.

## Root cause

`_collect_and_enqueue_done_jobs` / `enqueue_publish` / `publish_job` không loại job có `parent_job_id` hoặc id `_p\d{2,}`. Scanner đưa mọi `status=done` vào `auto_publish_queue.json`.

## Evidence

- Queue trước fix: `ad50b61b4050_p02` đứng đầu.
- Manifest part: `request.parent_job_id=ad50b61b4050`, title `… - Phần 2/2`.

## Fix

- `auto_publisher.is_auto_split_part` — id `_pNN` / `parent_job_id` / title `Phần N/N`.
- Chặn `_enqueue_job_record`, `enqueue_publish`, `publish_job`; purge queue trong `_collect_and_enqueue_done_jobs`.
- Đã dequeue `ad50b61b4050_p02` khỏi queue live.
- Backup: `Z:\PinelineV2_codebak\2026-11-08_hongguo2-design-part-upload\`

## Recheck

1. `python -c "from auto_publisher import is_auto_split_part, enqueue_publish; print(is_auto_split_part('ad50b61b4050_p02'), enqueue_publish('ad50b61b4050_p02'))"`
2. Đọc `data/auto_publish_queue.json` — không còn `*_pNN`.
3. **Pass nếu:** `skipped_split_part=True`; queue không có part; parent Full vẫn enqueue được.
4. **Fail nếu:** part lại xuất hiện trên banner upload / queue sau scan.

## Liên quan

- `split_parts.py` title `Phần {k}/{total}`
- Hongguo2 UI redesign cùng đợt (không đổi upload logic UI)

## Follow-up (~01:45)

- Restart `:8802` — nạp skip-part; clear state `current=ad50b61b4050_p02` (60%).
- Cùng đợt: `/api/hg/img` 422 do UI gửi `?u=` trong khi route bắt `url` → nhận cả hai; CDN 403 khi RPC (base stdio) → `covers.get` đọc file local.
- **Lưu ý:** `last_published` còn `ad50b61b4050_p01` đã lên YT trước fix — không rollback; chỉ chặn part mới.
