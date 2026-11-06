@echo off
REM Pineline desktop — uu tien pineline_env; khong co thi dung python he thong.

cd /d "%~dp0"

set "PYTHONIOENCODING=utf-8"
chcp 65001 >nul

set "PY="
if exist "%~dp0pineline_env\Scripts\python.exe" set "PY=%~dp0pineline_env\Scripts\python.exe"
if not defined PY if exist "%~dp0..\pineline_env\Scripts\python.exe" set "PY=%~dp0..\pineline_env\Scripts\python.exe"
if not defined PY if exist "%~dp0.venv\Scripts\python.exe" set "PY=%~dp0.venv\Scripts\python.exe"
if not defined PY if exist "%~dp0start.bat" (
  call "%~dp0start.bat" %*
  exit /b %ERRORLEVEL%
)

REM Fallback: may nay dang dung C:\Python312 (khong co pineline_env)
if not defined PY where python >nul 2>&1 && set "PY=python"
if not defined PY where py >nul 2>&1 && set "PY=py -3"

if not defined PY (
  echo [loi] Khong thay python.
  echo Cai Python 3.12+ hoac chay: python install.py --gpu
  pause
  exit /b 1
)

echo Dung: %PY%
"%PY%" "%~dp0app.py" %*
set "EC=%ERRORLEVEL%"
if not "%EC%"=="0" (
  echo.
  echo [loi] app.py thoat ma %EC%
  pause
)
exit /b %EC%
