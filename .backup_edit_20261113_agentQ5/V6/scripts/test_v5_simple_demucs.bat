@echo off
rem test_v5_simple_demucs.bat - agent F5 2026-11-12: kiem tra port translate_simple + Demucs-truoc-ASR sang Z:\PinelineV5
rem + agent P5 2026-11-12: Second Brain (events/notify/HOLD tay) + dong dau luong dich theo job (F2).
rem Chi chay pytest (mock, khong LLM/GPU that, khong HTTP, khong restart server). ASCII + CRLF.
rem P5: chay tren BAN SAO %TEMP%\pv5_test (test V5 ghi data\films.db + work\ cua cay) - cay that khong bi dung.
rem
rem KY VONG (ban sao Linux, stub fastapi/soundfile/yt_dlp):
rem   [1] 9 file simple+demucs+brain+hold : 160 passed, 4 skipped, 0 failed
rem         test_translate_simple.py            32 passed, 1 skipped  (P5: +6 test_f2_* job-stamping)
rem         test_translate_simple_next.py       27 passed, 2 skipped
rem         test_translate_simple_next_review   7 passed, 1 skipped
rem         test_translate_simple_scenarios.py  19 passed
rem         test_separate_demucs_chunks.py      19 passed
rem         test_asr_demucs.py                  3 passed
rem         test_agent_brain_events.py          11 passed  (P5 moi)
rem         test_agent_brain_notify.py          28 passed  (P5 moi)
rem         test_agent_hold_telegram.py         14 passed  (P5 moi, I2)
rem       (skip: golden end-to-end can Z:\PinelineV6\data\golden + D:\PinelineV2_work; 3 skip can backup agentB cua V2)
rem   [2] Toan bo tests V5: so FAILED KHONG duoc tang so voi truoc port.
rem       Ban sao Linux P5: truoc 27 failed / 241 passed / 4 skipped -> sau 27 failed / 300 passed / 4 skipped (cung danh sach).
rem       Drift da biet: test_translate_force_default.py x3, test_layout_paths, test_sfx_lib, test_review_batches...
rem       Windows (sau F5 ~18 failed / ~273 passed) -> ky vong sau P5: 18 failed (cung ten) / ~332 passed.
setlocal
set AGENT_BRAIN=0
set PYTHONIOENCODING=utf-8
set SRC=Z:\PinelineV5
set DST=%TEMP%\pv5_test
echo === Chep ban sao %SRC% -^> %DST% (bo work/data/node_modules/models/vendor/...) ===
robocopy "%SRC%" "%DST%" /MIR /XJ /NFL /NDL /NJH /NJS /NP /XD work data node_modules vendor models src-tauri _to_delete .git __pycache__ voices voice_samples .backup_edit_* .backup_sync_* >nul
if %ERRORLEVEL% GEQ 8 (echo robocopy loi & exit /b 2)
rem data: chep ban sao (films.db, lexicon...) tru token/secret; work: thu muc rong (test_agent_core_smoke co the khac cay that)
robocopy "%SRC%\data" "%DST%\data" /MIR /XJ /NFL /NDL /NJH /NJS /NP /XF *token* *.expired canva_* tele_chat_history.json >nul
if not exist "%DST%\work" mkdir "%DST%\work"
cd /d "%DST%" || (echo Khong vao duoc %DST% & exit /b 2)
echo.
echo === [1] simple + demucs + brain (ky vong: 160 passed, 4 skipped, 0 failed) ===
python -m pytest -q tests\test_translate_simple.py tests\test_translate_simple_next.py tests\test_translate_simple_next_review.py tests\test_translate_simple_scenarios.py tests\test_separate_demucs_chunks.py tests\test_asr_demucs.py tests\test_agent_brain_events.py tests\test_agent_brain_notify.py tests\test_agent_hold_telegram.py
set RC1=%ERRORLEVEL%
echo.
echo === [2] toan bo tests V5 (ky vong: khong them FAILED so voi truoc port) ===
python -m pytest -q tests -rf
set RC2=%ERRORLEVEL%
echo.
echo [1] exit=%RC1% (0 = dat)   [2] exit=%RC2% (khac 0 neu con drift da biet - xem danh sach FAILED)
echo Rollback dich: set TRANSLATE_PIPELINE=legacy  ^|  Rollback ASR: set ASR_USE_DEMUCS=0
echo Brain Telegram: AGENT_BRAIN_TELEGRAM=events, AGENT_BRAIN_TG_SEC=600 (config.json + pineline.config.json)
endlocal & exit /b %RC1%
