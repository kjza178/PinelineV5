# Films UI thiếu nút gộp job đã làm (combine)

- **Date:** 2026-11-07
- **Job / khu vực:** Films UI :8802 tab Đã làm · `/films/combine` · merge-parts
- **Status:** fixed

## Triệu chứng

API `POST /films/combine` (`combine_rendered_jobs`) đã có trên sidecar nhưng UI không có nút → không gộp được ≥2 job đã render thành 1 video Trọn Bộ. Thư viện cũng khó tick mùa `need_merge` để ghép hàng loạt.

## Root cause

Backend đã wire (`agent_tele_cmd` → `feeder.combine_rendered_jobs`) nhưng `films_ui.html` batch bar chỉ có Check Block / Xoá — thiếu entry point combine. Mùa `need_merge` không có checkbox.

## Evidence

- `POST /films/combine` với 1 id → `"Cần chọn ít nhất 2 job đã xong để gộp"` (API sống).
- Trước fix: grep UI không có `combine` / «Gộp job».

## Fix

- Batch bar: **🔗 Gộp job đã làm** → modal tiêu đề VI + auto-publish → `POST /films/combine`.
- Thêm `films_merge_api.py`: `/films/mergeable`, `/films/merge-parts`, `/api/jobs/{id}/merge-parts` (split parts).
- Lib: tick được `need_merge`; **Ghép mùa đã chọn** / **Ghép tất cả chờ ghép**.
- Sync V4/V5. Sidecar restart PID 35972.

## Recheck

1. Hard refresh `:8802/films/ui` → tab Đã làm.
2. Tick ≥2 job `done` còn thư mục → **Gộp job đã làm** → Gộp ngay → job mới xuất hiện.
3. Tab Thư viện: tick mùa chờ ghép → **Ghép mùa đã chọn**.
4. **Pass nếu:** toast OK + job gộp trong danh sách; lib merge xếp hàng.
5. **Fail nếu:** 404 combine / không có nút / gộp lỗi thiếu output.

## Liên quan

- `agent_feeder.combine_rendered_jobs`, `split_parts.merge_job_parts`
- Backup: `Z:\PinelineV2_codebak\2026-11-07_films-combine-ui\`
