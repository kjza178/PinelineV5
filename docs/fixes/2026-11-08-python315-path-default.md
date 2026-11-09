# run_v2.bat / sidecar: ModuleNotFoundError fastapi / requests sau update Python

- **Date:** 2026-11-08
- **Job / khu vực:** môi trường Windows Python PATH; `run_v2.bat` / `run_tele_cmd.bat` / V4+V5 launchers
- **Status:** fixed
- **Backup zip:** `Z:\PinelineV2_backup_2026-11-08_0610.zip`
- **Backup code:** `Z:\PinelineV2_codebak\2026-11-08_run-v2-python312\`

## Triệu chứng

Sau update Python, `run_v2.bat` / sidecar báo `No module named 'fastapi'` / `requests`. Mọi project gọi `python` trần dễ vỡ tương tự.

## Root cause

Installer Python **3.15.2** ghi `C:\Python315` lên đầu **Machine PATH**. `python` → 3.15 (trống deps). Packages Pineline nằm ở **C:\Python312**.

## Evidence

- `py -0p` trước: `3.15 *` default; `where python` → `C:\Python315\python.exe`
- `C:\Python312\python.exe -c "import fastapi"` OK; 3.15 FAIL

## Fix

1. **A+B hệ thống:** bỏ `C:\Python315` (+ Scripts) khỏi Machine PATH; đặt `C:\Python312` (+ Scripts) đầu PATH; `PY_PYTHON=3.12` (User + Machine). 3.15 vẫn cài tại `C:\Python315\` nếu cần gọi full path.
2. **Phòng thủ launcher:** `run_v2.bat` / `run_2.bat` (alias) / `run_tele_cmd.bat` / `run.bat` + V4 `run_v4.bat`/`run_tele_cmd.bat` + V5 `apps/run_v5.bat`/`apps/run_tele_cmd.bat` pin `C:\Python312\python.exe`.

## Recheck

1. Mở **terminal mới** (PATH cũ trong cửa sổ cũ vẫn stale).
2. `where python` → `C:\Python312\python.exe` (không còn 315).
3. `python --version` → `3.12.x`; `py --version` → `3.12.x`; `py -0p` có `3.12 *`.
4. `python -c "import fastapi,requests; print('ok')"`.
5. Chạy `Z:\PinelineV2\run_v2.bat` (khi không có server) — không còn ModuleNotFoundError.
6. **Pass nếu:** mọi bước trên OK.
7. **Fail nếu:** `python` vẫn 3.15 hoặc thiếu fastapi.

## Liên quan

- User chọn phương án A+B (default 3.12 + bỏ 3.15 khỏi PATH).
- TTS job `2cd10c3fa86d_p01` giữ chạy trên server cũ (không restart giữa chừng).
