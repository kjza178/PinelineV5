@echo off
REM PineLine V5 — cửa sổ Tauri (webview) trỏ http://127.0.0.1:8805
cd /d "%~dp0"
chcp 65001 >nul
set PORT=8805

REM Nếu chưa có server :8805 thì mở backend nền
powershell -NoProfile -Command "try { (New-Object Net.Sockets.TcpClient('127.0.0.1',%PORT%)).Close(); exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
  echo [Tauri] Chua co server :%PORT% — khoi dong server.py nen...
  start "PinelineV5-server" /MIN cmd /c "set PORT=%PORT%&& python server.py --host 127.0.0.1 --port %PORT%"
  timeout /t 3 /nobreak >nul
) else (
  echo [Tauri] Server :%PORT% dang chay — dung luon.
)

echo [Tauri] Mo cua so PineLine Studio V5...
call npm run tauri:dev
pause
