@echo off
REM Cai dat Rust Toolchain cho Tauri v2
cd /d "%~dp0"
chcp 65001 >nul

echo ========================================================
echo   Cai dat Rust cho Tauri v2 tren Windows
echo ========================================================
echo.
echo Dang cai dat qua winget...
winget install --id Rustlang.Rustup -e

echo.
echo Neu da cai dat xong, vui long khoi dong lai Terminal va kiem tra:
echo   cargo --version
echo   rustc --version
pause
