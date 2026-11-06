@echo off
REM Pineline 5060 Ti — venv mac dinh: CANH thu muc Pineline (D:\pineline_env)
cd /d "%~dp0"
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"

if not exist "pineline.config.rtx5060ti.json" (
  echo [loi] Thieu pineline.config.rtx5060ti.json
  pause
  exit /b 1
)

set "PY="
if exist "%~dp0pineline_env\Scripts\python.exe" set "PY=%~dp0pineline_env\Scripts\python.exe"
if not defined PY if exist "%~dp0..\pineline_env\Scripts\python.exe" set "PY=%~dp0..\pineline_env\Scripts\python.exe"
if not defined PY if exist "%~dp0.venv\Scripts\python.exe" set "PY=%~dp0.venv\Scripts\python.exe"

if not defined PY (
  if exist "%~dp0start.bat" (
    echo [info] Dung start.bat
    if exist "%~dp0..\pineline_env\Scripts\python.exe" "%~dp0..\pineline_env\Scripts\python.exe" "%~dp0_merge_5060ti_config.py"
    call "%~dp0start.bat" %*
    exit /b %ERRORLEVEL%
  )
  echo.
  echo [loi] Khong thay pineline_env.
  echo Mac dinh install.py:  %~dp0..\pineline_env\Scripts\python.exe
  echo.
  dir "%~dp0..\pineline_env\Scripts\python.exe"
  echo.
  echo Chay lai: python install.py --gpu
  pause
  exit /b 1
)

echo Dung Python: %PY%
"%PY%" "%~dp0_merge_5060ti_config.py"

"%PY%" -c "import uvicorn" 1>nul 2>nul
if errorlevel 1 (
  echo [loi] Thieu uvicorn. Chay:
  echo   "%PY%" -m pip install -U "uvicorn[standard]" fastapi pywebview
  pause
  exit /b 1
)

"%PY%" "%~dp0app.py" %*
pause
