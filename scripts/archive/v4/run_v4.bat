@echo off
REM Pineline V4 — Desktop App Studio & Server
cd /d "%~dp0"
chcp 65001 >nul

set "PORT=8804"
set "TEMP=D:\PinelineV4_tmp"
set "TMP=D:\PinelineV4_tmp"
if not exist "%TEMP%" mkdir "%TEMP%"

echo ========================================================
echo   PineLine Studio V4 — High Performance Pipeline
echo ========================================================
echo.
echo [1] Chạy chế độ App Desktop (.exe native window mượt mà)
echo [2] Chạy chế độ Web Server (mở qua trình duyệt web)
echo.
set /p choice="Chọn chế độ [1/2] (mặc định 1): "
if "%choice%"=="" set choice=1

if "%choice%"=="1" (
    echo Đang khởi động PineLine Studio Desktop...
    python app_desktop.py
) else (
    echo Đang khởi động PineLine V4 Web Server...
    set "PORT=8804"
    python server.py --host 127.0.0.1 --port 8804
)
pause
