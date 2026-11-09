# Auto-split: part xong mà job gốc vẫn pending (không ghép Full)

- **Date:** 2026-11-08
- **Job / khu vực:** auto-split parent `2cd10c3fa86d` («4») + parts `_p01`/`_p02`; `server.py` `_check_and_run_auto_split_parts` / merge heal
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-08_split-parent-merge-heal\` (`server.py`)

## Triệu chứng

Hai part «4 - Phần 1/2» và «4 - Phần 2/2» đã mux/output xong, nhưng job gốc «4» vẫn treo (mux pending / `split_info` chưa `merged`), không tự trả về bản Full.

## Root cause

Luồng auto-split chỉ gọi `merge_job_parts` **cuối vòng** `_check_and_run_auto_split_parts` trong cùng process. Khi server restart (hoặc worker chết) sau khi parts đã xong, `_AUTO_SPLIT_ACTIVE` mất → không còn ai gọi merge. Part hoàn tất độc lập cũng không báo parent.

## Evidence

- Trước heal tay: parent `2cd10c3fa86d` `split_info.status=split_done`, mux còn text kiểu Part 1/2; `2cd10c3fa86d_p01`/`_p02` mux `done` + `output.mp4` ~3.4GB mỗi part.
- Heal tay: `POST /api/jobs/2cd10c3fa86d/merge-parts` → `ok`, Full ~6925MB, `split_info=merged`, mux `done`.

## Fix

- `server.py`: `_queue_split_parent_merge_if_ready` + `_notify_parent_after_part_done`
  - Khi mọi part `_part_pipeline_complete` mà parent chưa Full → xếp `merge_job_parts` trên `_misc` (idempotent `_SPLIT_MERGE_QUEUED`).
  - Gọi từ: kết thúc `_auto_gpu` (part xong), `GET /api/jobs/{id}`, và đầu `_check_and_run_auto_split_parts` (entry heal).
- Job `2cd10c3fa86d` đã merge tay trước khi ship heal code.

## Recheck

1. Có parent auto-split: mọi part mux done, xoá/đổi tên `output.mp4`+`output_full.mp4` parent (hoặc dùng job mới), `split_info.status` ≠ `merged`.
2. `GET http://127.0.0.1:8801/api/jobs/<parent>` hoặc đợi part cuối xong pipeline.
3. Log `[auto-split-heal] … parts ready → merge Full` rồi `Full OK`.
4. **Pass nếu:** parent `split_info.status=merged`, mux `done` + `is_full_merged`, có `output.mp4`/`output_full.mp4` đủ lớn.
5. **Fail nếu:** parts done mà parent mux vẫn pending > vài phút sau GET (và không có log heal).

## Liên quan

- Job `2cd10c3fa86d` / `_p01` / `_p02`
- API sẵn có: `POST /api/jobs/{id}/merge-parts`
- Sync: V2 → V4/V5 `server.py`
