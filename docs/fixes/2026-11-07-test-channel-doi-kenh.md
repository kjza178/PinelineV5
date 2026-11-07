# Đổi kênh Test báo thành công nhưng proj_1 không đổi

- **Date:** 2026-11-07
- **Job / khu vực:** Films `Kênh Test` · `pollForTestChannelAuth` · `finish_oauth`
- **Status:** fixed

## Triệu chứng

Bấm 🔄 Đổi kênh (proj_1) → toast thành công nhưng list vẫn «Sai Kira», token/kênh không đổi.

## Root cause

1. `pollForTestChannelAuth` chỉ check `res.connected` — session cũ đã connected → báo OK ngay, đóng modal, OAuth mới chưa xong.
2. `finish_oauth` / `get_status` / health fallback cứng `"Sai Kira"`; `update_project_health` giữ title cũ nếu title mới rỗng.

## Fix

- Poll chờ `connected_at` đổi (và khớp `last_connected_project` khi có).
- OAuth health `replace_identity=True`; bỏ fallback cứng Sai Kira.
- Backup: `Z:\PinelineV2_codebak\2026-11-07_tc-doi-kenh-poll\`

## Recheck

1. Hard refresh Films → Kênh Test → 🔄 Đổi kênh ở **Kênh 1**.
2. Google: chọn Gmail **khác** (không phải kira178 nếu muốn đổi).
3. Đợi callback; list proj_1 đổi tên kênh/email.
4. **Fail nếu:** toast OK trong <3s mà chưa xong Google / proj_1 vẫn Sai Kira sau OAuth Gmail khác.
