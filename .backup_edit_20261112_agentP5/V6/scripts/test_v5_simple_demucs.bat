@echo off
rem test_v5_simple_demucs.bat - agent F5 2026-11-12: kiem tra port translate_simple + Demucs-truoc-ASR sang Z:\PinelineV5
rem Chi chay pytest (mock, khong LLM/GPU that, khong HTTP, khong restart server). ASCII + CRLF.
rem
rem KY VONG (do tren ban sao Linux, stub fastapi/google/soundfile/yt_dlp):
rem   [1] 6 file simple+demucs : 101 passed, 4 skipped, 0 failed
rem       (skip: golden end-to-end can Z:\PinelineV6\data\golden + D:\PinelineV2_work + eval_translation.py
rem        -> tren may that co the thanh passed: 102 passed / 3 skipped; 3 skip con lai can backup agentB cua V2)
rem         test_translate_simple.py            26 passed, 1 skipped
rem         test_translate_simple_next.py       27 passed, 2 skipped
rem         test_translate_simple_next_review   7 passed, 1 skipped
rem         test_translate_simple_scenarios.py  19 passed
rem         test_separate_demucs_chunks.py      19 passed
rem         test_asr_demucs.py                  3 passed
rem   [2] Toan bo tests V5: so FAILED KHONG duoc tang so voi truoc port.
rem       Ban sao Linux: truoc 35 failed / 158 passed -> sau 35 failed / 256 passed / 4 skipped (cung danh sach FAILED).
rem       Drift da biet (fail ca truoc port): test_translate_force_default.py x3 (server khong co _run_translate_engine).
rem       Windows (Z:\PinelineV6\scratch\baseline_v5.log 11-11): 18 failed / 175 passed
rem       -> ky vong sau port: 18 failed (cung ten) / ~273 passed / 3-4 skipped.
setlocal
set AGENT_BRAIN=0
set PYTHONIOENCODING=utf-8
cd /d Z:\PinelineV5 || (echo Khong vao duoc Z:\PinelineV5 & exit /b 2)
echo.
echo === [1] simple + demucs (ky vong: 101 passed, 4 skipped, 0 failed) ===
python -m pytest -q tests\test_translate_simple.py tests\test_translate_simple_next.py tests\test_translate_simple_next_review.py tests\test_translate_simple_scenarios.py tests\test_separate_demucs_chunks.py tests\test_asr_demucs.py
set RC1=%ERRORLEVEL%
echo.
echo === [2] toan bo tests V5 (ky vong: khong them FAILED so voi truoc port) ===
python -m pytest -q tests -rf
set RC2=%ERRORLEVEL%
echo.
echo [1] exit=%RC1% (0 = dat)   [2] exit=%RC2% (khac 0 neu con drift da biet - xem danh sach FAILED)
echo Rollback dich: set TRANSLATE_PIPELINE=legacy  ^|  Rollback ASR: set ASR_USE_DEMUCS=0
endlocal & exit /b %RC1%
