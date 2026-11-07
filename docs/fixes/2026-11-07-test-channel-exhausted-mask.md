# Kênh Test báo token Kênh 3 chết dù đã Reset Quota

- **Date:** 2026-11-07
- **Job / khu vực:** `test_channel.get_available_service`, `data/test_channel/exhausted.json`
- **Status:** fixed
- **Backup:** zip `Z:\PinelineV2_backup_2026-11-07_0251.zip`; codebak `Z:\PinelineV2_codebak\2026-11-07_tc-exhausted-hint\`

## Triệu chứng

User bấm Reset Quota / vẫn thấy: «Không thể khởi tạo YouTube API… Kênh 3 (Acc Mới 2): token hết hạn/bị thu hồi».

## Root cause

1. `exhausted.json` còn gắn `proj_1` + `proj_2` = UTC hôm nay → pool **chỉ thử** `proj_3`.
2. `proj_3` lúc đó `invalid_grant` → message chỉ nhắc Kênh 3, che việc 1/2 chỉ bị **cờ local** (không phải token chết).
3. Reset Quota xóa cờ, nhưng upload Content-ID / 429 sau đó có thể gắn lại; hoặc user chỉ reset 1 project.

## Evidence

- Trước: `exhausted.json` `{"proj_1":"2026-11-06","proj_2":"2026-11-06"}`; `get_available_service` FAIL chỉ nêu Kênh 3.
- Auth riêng: `proj_1`/`proj_2` refresh OK (Sai Kira / Cuong Nguyen).
- Sau `reset_exhausted_projects(None)` → `available -> proj_1`.

## Fix

- `test_channel.get_available_service`: ưu tiên project chưa exhausted; **fallback** sang project còn cờ exhausted nếu auth fail hết phía còn quota (tránh kẹt Acc token chết).
- Refresh sớm để bắt `invalid_grant`; message nêu đã thử cả nhóm exhausted.
- Sync V2→V4/V5 `test_channel.py`. Xóa cờ live `exhausted.json` = `{}`.

## Recheck

1. `Get-Content Z:\PinelineV2\data\test_channel\exhausted.json` → `{}` hoặc không có key hôm nay.
2. `python -c "import sys; sys.path.insert(0,r'Z:\\PinelineV2'); import importlib,test_channel as t; t=importlib.reload(t); print(t.get_available_service()[1])"` → `proj_1` (hoặc 2).
3. Gắn giả: mark exhausted 1+2, revoke giả 3 → phải fallback 1/2 thay vì chỉ báo lỗi 3.
4. **Pass nếu:** pool khởi tạo được khi ≥1 project auth OK.
5. **Fail nếu:** còn cờ 1+2 mà lỗi chỉ nhắc Kênh 3 token chết (bản cũ).

## Liên quan

- `docs/fixes/2026-11-07-test-channel-doi-kenh.md`
- GCP Video Uploads quota ≠ cờ `exhausted.json`
