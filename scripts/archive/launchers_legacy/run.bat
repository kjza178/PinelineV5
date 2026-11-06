@echo off
REM ============================================================
REM  Pineline - chay server long tieng.
REM  Nhay doi file nay de mo app o http://127.0.0.1:8800
REM  LLM mac dinh: llama-server local :8083 (xem config.json).
REM ============================================================

cd /d "%~dp0"

REM --- Endpoint LLM (llama.cpp OpenAI-compatible) ---
set "LLM_BASE_URL=http://127.0.0.1:8083/v1"
set "LLM_API_KEY=sk-local"
set "LLM_MODEL=qwen36-tq3"
set "TRANSLATE_MODEL=qwen36-tq3"
REM Ollama (tuy chon, khi chon model local/gemma* tren UI)
set "LOCAL_LLM_BASE_URL=http://localhost:11434/v1"

REM --- TTS chay tren GPU ---
set "VIENEU_DEVICE=cuda"

REM --- In tieng Viet ra console khong loi (Windows cp1252) ---
set "PYTHONIOENCODING=utf-8"
chcp 65001 >nul

echo Mo http://127.0.0.1:8800
echo LLM: %LLM_BASE_URL% model=%TRANSLATE_MODEL%
python server.py --port 8800

pause
