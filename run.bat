@echo off
title Veritas AI - Detector and Humanizer
echo ====================================================
echo Starting Veritas AI Detector and Humanizer on Localhost...
echo URL: http://localhost:8000
echo ====================================================
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
pause
