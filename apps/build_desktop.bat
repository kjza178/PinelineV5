@echo off
REM Build PineLine Studio exe (PyInstaller). Lives in apps/; cd to project root.
cd /d "%~dp0.."
chcp 65001 >nul

echo Dang build PineLine_Studio_V5.exe voi PyInstaller...
pyinstaller --noconfirm --onedir --windowed --name "PineLine_Studio_V5" --add-data "static\ui\index3.html;." --add-data "static;static" app_desktop.py

echo.
echo Build hoan tat tai thu muc dist/PineLine_Studio_V5/
pause
