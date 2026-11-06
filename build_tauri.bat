@echo off
REM Dong goi PineLine V5 thanh .msi / .exe voi Tauri v2
cd /d "%~dp0"
chcp 65001 >nul

echo Dang build release package Tauri v2 (V5 / :8805)...
call npm run tauri:build
pause
