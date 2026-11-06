@echo off
REM Lives in apps/; always cd to project root.
cd /d "%~dp0.."
set "AGENT_TELEGRAM=1"
if "%PORT%"=="" set "PORT=8805"
set "PINELINE_BASE=http://127.0.0.1:%PORT%"
set "AUTOPILOT_PORT=8802"
set "AUTOPILOT_TICK_SEC=90"
set "RUNWATCH_SEC=90"
set "RUNWATCH_STUCK_MIN=30"
set "RUNWATCH_MAX_HEAL=2"
REM LLM /feed: base/key tu pineline.config.json (config.agent_llm); fallback openclaw
set "AGENT_MODEL=ollama/gemma4:31b-cloud"
set "AGENT_FALLBACK_MODEL=openclaw"
set "PYTHONIOENCODING=utf-8"
echo Starting Auto-pilot + Telegram sidecar for PineLine V5 (%PINELINE_BASE%)...
python -m agents.agent_tele_cmd
pause
