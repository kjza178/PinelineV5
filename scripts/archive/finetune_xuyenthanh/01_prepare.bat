@echo off
chcp 65001 >nul
set ROOT=Z:\VieNeu-TTS
set PY=%ROOT%\.venv\Scripts\python.exe
cd /d %ROOT%

if not exist "%PY%" (
  echo Missing finetune venv: %PY%
  exit /b 1
)

echo === Seed XuyenThanh from Pineline ===
"%PY%" "%~dp0seed_xuyenthanh.py"
if errorlevel 1 exit /b 1

echo === Filter ===
"%PY%" finetune\data_scripts\filter_data.py
if errorlevel 1 exit /b 1

echo === Encode (NeuCodec) ===
"%PY%" finetune\data_scripts\encode_data.py
if errorlevel 1 exit /b 1

echo OK. Next: 02_train.bat
