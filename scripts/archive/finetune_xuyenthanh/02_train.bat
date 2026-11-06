@echo off
chcp 65001 >nul
set ROOT=Z:\VieNeu-TTS
set PY=%ROOT%\.venv\Scripts\python.exe
cd /d %ROOT%

if not exist finetune\dataset\metadata_encoded.csv (
  echo Missing metadata_encoded.csv - run 01_prepare.bat first.
  exit /b 1
)

echo === Train LoRA (XuyenThanh) ===
"%PY%" finetune\train.py
if errorlevel 1 exit /b 1

echo Done. Check: %ROOT%\finetune\output\
