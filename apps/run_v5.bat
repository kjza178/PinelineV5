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

if "%choice%"=="1" (
    echo Starting desktop...
    python app_desktop.py
) else if "%choice%"=="3" (
    echo Starting sidecar - PINELINE_BASE -^> :8805 ...
    set "PINELINE_BASE=http://127.0.0.1:8805"
    call "%~dp0run_tele_cmd.bat"
) else (
    echo Starting server http://127.0.0.1:8805 ...
    python server.py --host 127.0.0.1 --port 8805
)
pause
