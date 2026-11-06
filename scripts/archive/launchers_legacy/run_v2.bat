@echo off
REM Pineline V2 — doc lap voi Z:\Pineline (work/ rieng)
cd /d "%~dp0"

REM LLM job (dich/soat) + key: CHI trong pineline.config.json (file-first, khong dat o day)
set "LOCAL_LLM_BASE_URL=http://localhost:11434/v1"
REM Agent chat: base/key lay tu AGENT_*/LLM_* trong pineline.config.json; loi -> openclaw
set "AGENT_MODEL=ollama/gemma4:31b-cloud"
set "AGENT_FALLBACK_MODEL=openclaw"
set "VIENEU_DEVICE=cuda"
set "PYTHONIOENCODING=utf-8"
set "PORT=8801"
REM file tam (ghep tap Hongguo, wav ASR...) o D, khong ghi vao o chay Windows
set "TEMP=D:\PinelineV2_tmp"
set "TMP=D:\PinelineV2_tmp"
if not exist "%TEMP%" mkdir "%TEMP%"
REM Agent A/B/C
set "AGENT_QA_GATE=1"
set "AGENT_WATCH=1"
set "AGENT_WATCH_SEC=300"
set "AGENT_WATCH_COOLDOWN=1800"
set "AGENT_WATCH_SKIP_PREFIX=agenttest"
set "AGENT_TELEGRAM=1"
set "AGENT_TELEGRAM_STARTUP=0"
chcp 65001 >nul

echo Pineline V2 — http://127.0.0.1:8801/ui3  (ops) ^| /ui3 (classic)
echo Work: %cd%\work
echo Agent: QA_GATE=%AGENT_QA_GATE% WATCH=%AGENT_WATCH% TELEGRAM=%AGENT_TELEGRAM%
echo Agent LLM: %AGENT_MODEL% (fallback %AGENT_FALLBACK_MODEL%)
echo Job LLM: xem pineline.config.json
python server.py --host 127.0.0.1 --port 8801
pause
