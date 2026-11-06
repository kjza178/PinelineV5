@echo off
REM Cai dat Rust Toolchain cho Tauri v2 (V5)
cd /d "%~dp0"
chcp 65001 >nul

echo ========================================================
echo   Cai dat Rust cho Tauri v2 (PineLine V5)
echo ========================================================
echo.
echo Dang cai dat qua winget...
winget install --id Rustlang.Rustup -e

echo.
echo Neu da cai xong: mo Terminal moi roi kiem tra:
echo   cargo --version
echo   rustc --version
echo Sau do: run_tauri.bat
pause
