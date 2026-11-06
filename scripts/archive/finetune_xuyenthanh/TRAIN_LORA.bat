@echo off
chcp 65001 >nul
title Train LoRA Res (VieNeu 0.3B)
setlocal EnableExtensions

set "ROOT=Z:\VieNeu-TTS"
set "PY=%ROOT%\.venv\Scripts\python.exe"
set "PIN=Z:\Pineline\finetune_xuyenthanh"
set "LOG=%PIN%\train_lora.log"
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
set "PYTHONWARNINGS=ignore"

set "HF_HOME=D:\AI_CACHE"
set "HUGGINGFACE_HUB_CACHE=D:\AI_CACHE\hub"
set "TRANSFORMERS_CACHE=D:\AI_CACHE\hub"
if exist "D:\AI_CACHE\token" for /f "usebackq delims=" %%A in ("D:\AI_CACHE\token") do set "HF_TOKEN=%%A"
set "HUGGING_FACE_HUB_TOKEN=%HF_TOKEN%"
set "HF_TOKEN=%HF_TOKEN%"

echo.
echo  ============================================
echo   Train LoRA - Res
echo   Source : Z:\Pineline\rvc_data\Res.wav
echo   Output : %ROOT%\finetune\output\Res-LoRA-v1
echo   Log    : %LOG%
echo  ============================================
echo.
echo   1^) Train ngay (dung dataset da encode)
echo   2^) Cat + ASR + encode + train lai tu dau
echo   3^) Chi prepare (khong train)
echo   4^) Train TIEP tu checkpoint (max_steps moi trong lora_config.py)
echo   0^) Thoat
echo.
set /p CHOICE=Chon [1/2/3/4/0]: 

if "%CHOICE%"=="0" exit /b 0
if "%CHOICE%"=="1" goto TRAIN_ONLY
if "%CHOICE%"=="2" goto FULL
if "%CHOICE%"=="3" goto PREPARE_ONLY
if "%CHOICE%"=="4" goto TRAIN_RESUME
echo Lua chon khong hop le.
pause
exit /b 1

:PREPARE_ONLY
call :CHECK_PY
call :PREPARE
echo [OK] Prepare xong.
pause
exit /b 0

:FULL
call :CHECK_PY
call :PREPARE
goto TRAIN

:TRAIN_ONLY
call :CHECK_PY
if not exist "%ROOT%\finetune\dataset\metadata_encoded.csv" (
  echo [WARN] Chua co metadata_encoded.csv - tu dong prepare...
  call :PREPARE
)
set "TRAIN_ARGS="
goto TRAIN

:TRAIN_RESUME
call :CHECK_PY
if not exist "%ROOT%\finetune\dataset\metadata_encoded.csv" (
  echo [ERR] Chua co metadata_encoded.csv - chay option 2 hoac 3 truoc.
  pause
  exit /b 1
)
set "TRAIN_ARGS=--resume"
goto TRAIN

:TRAIN
cd /d "%ROOT%"
echo.
if defined TRAIN_ARGS (
  echo [TRAIN] Tiep tu checkpoint moi nhat - max_steps lay tu lora_config.py
) else (
  echo [TRAIN] Bat dau tu dau...
)
echo [TRAIN] Log: %LOG%
echo ===== TRAIN %DATE% %TIME% =====>> "%LOG%"
"%PY%" -u finetune\train.py %TRAIN_ARGS% 2>&1 | "%PY%" -u "%PIN%\tee_log.py" "%LOG%"
if errorlevel 1 goto FAIL
echo.
echo [OK] Xong. Adapter: %ROOT%\finetune\output\
dir /b "%ROOT%\finetune\output\"
echo ===== DONE %DATE% %TIME% =====>> "%LOG%"
pause
exit /b 0

:PREPARE
cd /d "%ROOT%"
echo.
echo [1/3] Cat + Whisper ASR tu file dai...
echo ===== PREPARE %DATE% %TIME% =====>> "%LOG%"
"%PY%" -u "%PIN%\prepare_long_xuyenthanh.py" 2>&1 | "%PY%" -u "%PIN%\tee_log.py" "%LOG%"
if errorlevel 1 goto FAIL
echo [2/3] Filter...
"%PY%" -u finetune\data_scripts\filter_data.py 2>&1 | "%PY%" -u "%PIN%\tee_log.py" "%LOG%"
if errorlevel 1 goto FAIL
echo [3/3] Encode NeuCodec...
"%PY%" -u finetune\data_scripts\encode_data.py 2>&1 | "%PY%" -u "%PIN%\tee_log.py" "%LOG%"
if errorlevel 1 goto FAIL
echo [OK] Dataset san sang.
exit /b 0

:CHECK_PY
if not exist "%PY%" (
  echo [ERR] Thieu venv: %PY%
  pause
  exit /b 1
)
exit /b 0

:FAIL
echo.
echo [FAIL] Xem log: %LOG%
pause
exit /b 1
