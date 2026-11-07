# Gộp job encode lại cả loạt dù chỉ 1 phần lệch resolution

- **Date:** 2026-11-07
- **Job / khu vực:** `agent_feeder._concat_videos_smart` (Films `/films/combine`)
- **Status:** fixed
- **Backup:** zip `Z:\PinelineV2_backup_2026-11-07_0413.zip`; codebak `Z:\PinelineV2_codebak\2026-11-07_concat-partial-norm\`

## Triệu chứng

Gộp 6 phần Thiên phú: 5×1920×1080 + 1×1882×1080 → ffmpeg re-encode **cả 6** (hàng giờ) dù chỉ Phần 3 lệch.

## Root cause

Fallback `normalized_canvas` luôn scale+encode mọi input khi `uniform=False`, không phân biệt phần đã khớp canvas đích.

## Evidence

- Probe: `4b5f294e547a` = 1882×1080; các phần còn lại 1920×1080 h264.
- Live job: `norm_0000`… encode lần lượt từ mọi `output.mp4`.

## Fix

- Phần đúng `tw×th` + h264 → `-c:v copy` (chỉ AAC chuẩn hoá).
- Phần lệch → scale+pad encode như cũ.
- Copy fail → fallback encode phần đó.
- `mode`: `normalized_canvas_partial` + `parts_reencoded` / `parts_copied`.
- Sync V2→V4/V5 (+ `agents/agent_feeder.py`).

## Recheck

1. Tạo 2 clip 1s: 1920×1080 + 1882×1080 → `_concat_videos_smart` → `mode=normalized_canvas_partial`, `parts_reencoded=1`, `parts_copied=1`.
2. Gộp lại series lệch 1 phần → chỉ thấy 1 ffmpeg dài (encode), các phần khác xong trong giây/phút (copy).
3. **Pass nếu:** không encode lại phần đã 1920×1080.
4. **Fail nếu:** vẫn `norm_*` encode đủ N phần khi chỉ 1 lệch.

## Liên quan

- Job gộp Thiên phú đang chạy (trước fix) vẫn dùng logic cũ tới khi xong — lần gộp sau mới hưởng.
