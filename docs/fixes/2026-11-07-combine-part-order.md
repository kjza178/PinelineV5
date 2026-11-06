# Gộp job đã làm nối sai thứ tự Phần

- **Date:** 2026-11-07
- **Job / khu vực:** Films UI `/films/combine` · `openCombineJobsModal` · `combine_rendered_jobs`
- **Status:** fixed

## Triệu chứng

Modal «Gộp job đã làm» hiện `Phần 4 · Phần 2 · Phần 3 · (không số)` — nối theo thứ tự tick checkbox, không theo số phần.

## Root cause

`openCombineJobsModal` lấy `.film-pick:checked` theo DOM/tick; `combine_rendered_jobs` nối đúng `job_ids` client gửi, không sort Phần.

## Evidence

Screenshot user 2026-11-07: tiêu đề liệt kê Phần 4→2→3→không số.

## Fix

- `films_ui.html`: `parsePartNumber` + sort season/part trước preview và POST; cảnh báo >11.5h YTB; nút Skip đang upload trên batch Done.
- `agent_feeder.combine_rendered_jobs`: sort `_part_sort_key` (mặc định); `preserve_order=true` nếu cần giữ tay.
- `agent_tele_cmd` truyền `preserve_order` từ body.
- Backup: `Z:\PinelineV2_codebak\2026-11-07_combine-part-order\`

## Recheck

1. Hard refresh Films Done → chọn 4 phần cùng series (tick lộn xộn).
2. Mở «Gộp job đã làm» → list phải `1. Phần1 … 2. Phần2 …`.
3. Gộp → output nối đúng thứ tự phần.
4. **Pass nếu:** preview + file gộp theo Phần tăng dần.
5. **Fail nếu:** vẫn theo thứ tự tick.

## Liên quan

- Skip upload: tab Uploader + batch Done; API `/api/uploader/skip-current` (swarm UX follow-up).

## Follow-up (~01:25) — harden parser + numbered ↑↓ list

### Root cause (bổ sung)

Parser đầu chỉ bắt `\d+` (sót `第十一季`); sort dùng `(season, part, title)` thay vì `(part, created_at, job_id)`; thiếu ↑↓ + `preserve_order` khi user chỉnh tay.

### Fix

- **Missing part → 0** (xếp trước Phần 1). Documented.
- UI: `parsePartNumber` + CN int; `LAST_FILMS`/`created_at`; numbered list + ↑↓; POST `preserve_order`/`explicit_order` khi thủ công.
- Backend: `_combine_part_num` / `_part_sort_key` → `(part, created_at, job_id)`; cập nhật `clean_ids` sau sort; `explicit_order` alias.
- Backup zip `Z:\PinelineV2_backup_2026-11-07_0108.zip` + codebak `…_combine-part-order\` (feeder/tele/ui).
- Sync V4 + V5 (`static/ui/films_ui.html`, `agents/agent_feeder.py`).

### Recheck

1. Hard refresh Films → tick Phần 4,2,3,(no part) lộn xộn.
2. Modal: `1. (no part) … 2. Phần 1 …` hoặc `1. Phần1 … 2. Phần2 …` nếu đủ số.
3. `python -c "from agent_feeder import _combine_part_num; assert _combine_part_num('第十一季')==11"`
4. **Pass nếu:** preview tăng dần; gộp concat cùng thứ tự (feeder reload mỗi POST — không cần restart :8801).
5. **Fail nếu:** vẫn tick-order hoặc `第十一季` = 0.
6. ↑↓ thủ công: cần **restart :8802** để `preserve_order` trên tele_cmd process cũ có hiệu lực (sort-by-part vẫn OK nhờ `importlib.reload(feeder)`).
