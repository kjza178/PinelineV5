# Nhật ký Films UI tự hiện lại sau khi bấm ✕

- **Date:** 2026-11-20
- **Job / khu vực:** `films_ui.html` `#opsLogBox` (Gộp done `1a6301366b65`…)
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_backup_2026-11-20_0415_ops-log.zip` · codebak `Z:\PinelineV2_codebak\2026-11-20_ops-log-no-auto-show\`

## Triệu chứng

User bấm ✕ ẩn khung «📋 Nhật ký» nhưng khung tự hiện lại (đặc biệt khi gộp job đã done còn log trên đĩa).

## Root cause

Poll `combineTick` / `normTick` / test progress gọi `opsLogShow()` hoặc `opsLogPush`/`opsLogIngestServerLines` gán `OPS_LOG_HIDDEN=false` mỗi lần cập nhật — xoá cờ ẩn.

## Evidence

- Screenshot: status `🔗 Gộp job done 100%` + bảng log combine vẫn mở sau ✕
- `combineRender` luôn `opsLogShow()` khi còn phase/log (kể cả `done`)

## Fix

- `opsLogHide()` + `sessionStorage.opsLogHidden`
- Push/ingest/poll chỉ `opsLogRender()` — không unhide
- `opsLogShow()` chỉ khi user bắt đầu gộp/chuẩn hóa hoặc bấm «📋 Nhật ký»

## Recheck

1. Hard refresh Films UI
2. Để poll combine (job done còn log) — khung có thể hiện lần đầu nếu chưa ✕
3. Bấm ✕
4. Đợi ≥10 s (poll)
5. **Pass nếu:** khung không tự hiện lại
6. **Fail nếu:** khung mở lại không cần bấm
7. Bấm bắt đầu gộp mới hoặc «📋 Nhật ký» → khung hiện lại (đúng)

## Liên quan

- DECISIONS 11-19: 1 bảng Nhật ký
- Follow-up unified log `docs/fixes` / CHANGELOG 2026-11-19
