@echo off
chcp 65001 >nul
title Watch LoRA train progress
echo Dang theo doi log (Ctrl+C de thoat)...
echo File: Z:\Pineline\finetune_xuyenthanh\train_external.log
echo.
powershell -NoProfile -Command "Get-Content 'Z:\Pineline\finetune_xuyenthanh\train_external.log' -Wait -Tail 8"
pause
