# Nút Dừng không tắt được mux/ffmpeg

- **Date:** 2026-09-24
- **Job / khu vực:** `server.py` `_kill_job_children` / `render._ffmpeg_progress`
- **Status:** fixed

## Triệu chứng

Bấm ⏹ Dừng khi đang mux — UI “dừng” nhưng ffmpeg vẫn encode; API `/stop` hay timeout.

## Root cause

Mux ffmpeg cmdline dạng `-i source.mp4 … output.partial.mp4` (**không có job_id**).  
`_kill_job_children` chỉ `kill` nếu `job_id in cmdline` → **bỏ sót ffmpeg**.  
Heal còn quét wmic chậm → API stop timeout.

## Fix

1. Kill ffmpeg/aria2 theo **cwd = work/<job_id>** (child + orphan).
2. Ghi `work/<job>/.stop` + `_ffmpeg_progress` đọc → `proc.kill()`.
3. Stop API: xóa partial, heal không dùng wmic.

## Recheck

1. Bắt mux đang chạy (`ffmpeg` cwd = `work/<job>`).
2. `POST /api/jobs/<id>/stop` — trả `< 2s`, `{"stopped":true}`.
3. Không còn `ffmpeg.exe` với cwd đó; có `.stop` hoặc đã xóa sau clear.
4. `mux` không kẹt `running` mãi (heal → done nếu còn output.mp4).

**Pass nếu:** stop giết ffmpeg trong vài giây.  
**Fail nếu:** ffmpeg vẫn sống sau stop.
