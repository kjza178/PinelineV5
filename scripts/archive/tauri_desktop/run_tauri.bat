@echo off
REM Chay Pineline V4 Desktop voi Tauri v2
cd /d "%~dp0"
chcp 65001 >nul

echo Dang khoi chay Tauri v2 dev mode...
npm run tauri:dev
pause
