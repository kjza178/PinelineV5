@echo off
chcp 65001 >nul
title Test LoRA Res
setlocal EnableExtensions

set "PY=Z:\VieNeu-TTS\.venv\Scripts\python.exe"
set "SCRIPT=Z:\Pineline\finetune_xuyenthanh\test_lora_infer.py"
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
set "HF_HOME=D:\AI_CACHE"
set "HUGGINGFACE_HUB_CACHE=D:\AI_CACHE\hub"
set "TRANSFORMERS_CACHE=D:\AI_CACHE\hub"
if exist "D:\AI_CACHE\token" for /f "usebackq delims=" %%A in ("D:\AI_CACHE\token") do set "HF_TOKEN=%%A"

if not exist "%PY%" (
  echo [ERR] Thieu venv: %PY%
  pause
  exit /b 1
)

echo.
echo  Nghe thu LoRA Res (VieNeu 0.3B - KHONG phai v3 Pineline)
echo  Mac dinh: finetune\output\Res-LoRA-v1
echo  Output  : finetune_xuyenthanh\test_outputs\
echo.
echo  Vi du:
echo    03_test_lora.bat --lora Z:\VieNeu-TTS\finetune\output\Res-LoRA-v1\checkpoint-5000
echo.

"%PY%" -u "%SCRIPT%" %*
if errorlevel 1 (
  echo [FAIL]
  pause
  exit /b 1
)
pause
