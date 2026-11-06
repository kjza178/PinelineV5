@echo off
chcp 65001 >nul
title VieNeu LoRA train - XuyenThanh
setlocal

set ROOT=Z:\VieNeu-TTS
set PY=%ROOT%\.venv\Scripts\python.exe
set PIN=Z:\Pineline\finetune_xuyenthanh
set LOG=%PIN%\train_external.log
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set PYTHONWARNINGS=ignore

set HF_HOME=D:\AI_CACHE
set HUGGINGFACE_HUB_CACHE=D:\AI_CACHE\hub
set TRANSFORMERS_CACHE=D:\AI_CACHE\hub
if exist "D:\AI_CACHE\token" for /f "usebackq delims=" %%A in ("D:\AI_CACHE\token") do set "HF_TOKEN=%%A"
set HUGGING_FACE_HUB_TOKEN=%HF_TOKEN%

if not exist "%PY%" (
  echo [ERR] Missing venv: %PY%
  pause
  exit /b 1
)

cd /d "%ROOT%"
echo ==== XuyenThanh LoRA (external) ====
echo Log: %LOG%
echo Tip: mo them cua so CMD:  powershell Get-Content "%LOG%" -Wait -Tail 5
echo Started %DATE% %TIME% > "%LOG%"

if not exist "finetune\dataset\metadata_encoded.csv" (
  echo [1/2] Prepare long wav + ASR + encode...
  "%PY%" -u "%PIN%\prepare_long_xuyenthanh.py" 2>&1 | "%PY%" -u "%PIN%\tee_log.py" "%LOG%"
  if errorlevel 1 goto fail
  "%PY%" -u finetune\data_scripts\filter_data.py 2>&1 | "%PY%" -u "%PIN%\tee_log.py" "%LOG%"
  if errorlevel 1 goto fail
  "%PY%" -u finetune\data_scripts\encode_data.py 2>&1 | "%PY%" -u "%PIN%\tee_log.py" "%LOG%"
  if errorlevel 1 goto fail
) else (
  echo [1/2] Skip prepare - metadata_encoded.csv exists
)

echo [2/2] Training... (thanh %% hien o day + trong log)
"%PY%" -u finetune\train.py 2>&1 | "%PY%" -u "%PIN%\tee_log.py" "%LOG%"
if errorlevel 1 goto fail

echo [OK] Done. See %ROOT%\finetune\output\
echo Ended %DATE% %TIME% >> "%LOG%"
pause
exit /b 0

:fail
echo [FAIL] See %LOG%
powershell -NoProfile -Command "Get-Content '%LOG%' -Tail 40"
pause
exit /b 1
