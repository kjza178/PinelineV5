@echo off
REM Dong goi Pineline V4 thanh .msi / .exe voi Tauri v2
cd /d "%~dp0"
chcp 65001 >nul

echo Dang build release package voi Tauri v2...
npm run tauri:build
pause
