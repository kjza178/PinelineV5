@echo off
REM Pineline V5 — khung refactor (không đụng V4 :8804)
REM Lives in apps/; always cd to project root.
cd /d "%~dp0.."
chcp 65001 >nul

set "PORT=8805"
set "TEMP=D:\PinelineV5_tmp"
set "TMP=D:\PinelineV5_tmp"
if not exist "%TEMP%" mkdir "%TEMP%"
if not exist "D:\PinelineV5_work" mkdir "D:\PinelineV5_work"

echo ========================================================
echo   PineLine V5 — refactor workspace  (port 8805)
echo ========================================================
echo.
echo [1] App Desktop (WebView2)
echo [2] Web Server only
echo [3] Sidecar Telegram/Auto-pilot (:8802) — gọi BASE :8805
echo.
set /p choice="Chọn [1/2/3] (mac dinh 2): "
if "%choice%"=="" set choice=2

REM Pin Python 3.12 — PATH uu tien 3.15 sau update → thieu fastapi/requests
set "PY="
if exist "C:\Python312\python.exe" (
  set "PY=C:\Python312\python.exe"
)
if not defined PY if exist "%~dp0pineline_env\Scripts\python.exe" (
  set "PY=%~dp0pineline_env\Scripts\python.exe"
)
if not defined PY if exist "%~dp0.venv\Scripts\python.exe" (
  set "PY=%~dp0.venv\Scripts\python.exe"
)
if not defined PY (
  where python >nul 2>&1 && for /f "delims=" %%I in ('where python') do (
    if not defined PY set "PY=%%I"
  )
)
if not defined PY (
  echo [loi] Khong thay C:\Python312\python.exe
  pause
  exit /b 1
)

if "%choice%"=="1" (
    echo Starting desktop...
    echo Python: %PY%
    "%PY%" app_desktop.py
) else if "%choice%"=="3" (
    echo Starting sidecar - PINELINE_BASE -^> :8805 ...
    set "PINELINE_BASE=http://127.0.0.1:8805"
    call "%~dp0run_tele_cmd.bat"
) else (
    echo Starting server http://127.0.0.1:8805 ...
    echo Python: %PY%
    "%PY%" server.py --host 127.0.0.1 --port 8805
)
pause

