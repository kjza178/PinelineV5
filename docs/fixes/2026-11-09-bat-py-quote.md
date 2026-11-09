# Launcher bat: `'C:\Python312\python.exe" set "PY' is not recognized`

- **Date:** 2026-11-09
- **Job / khu vực:** `run_tele_cmd.bat` / `run_v2.bat` / `run.bat` + V4/V5 launchers
- **Status:** fixed
- **Codebak:** `Z:\PinelineV2_codebak\2026-11-09_bat-py-quote\`

## Triệu chứng

Chạy bat báo:
` 'C:\Python312\python.exe" set "PY' is not recognized ...`
`[loi] Khong thay C:\Python312\python.exe`
dù `C:\Python312\python.exe` tồn tại.

## Root cause

Dạng một dòng `if exist "path" set "PY=..."` dễ bị cmd tách quote sai (file LF-only / ngữ cảnh call). Kết quả cmd cố chạy chuỗi `python.exe" set "PY` như lệnh.

## Fix

Đổi sang khối ngoặc:

```bat
if exist "C:\Python312\python.exe" (
  set "PY=C:\Python312\python.exe"
)
```

+ fallback `where python`; ép CRLF. Sync V2/V4/V5.

## Recheck

1. Double-click `Z:\PinelineV2\run_tele_cmd.bat`
2. **Pass nếu:** in `Python: C:\Python312\python.exe` (hoặc sidecar báo đã giữ cổng)
3. **Fail nếu:** còn lỗi `python.exe" set "PY`
