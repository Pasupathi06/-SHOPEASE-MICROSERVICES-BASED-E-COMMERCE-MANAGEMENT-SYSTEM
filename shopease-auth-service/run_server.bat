@echo off
title ShopEase Auth Service - Port 8001
echo ===================================================
echo Starting ShopEase Authentication Service on Port 8001...
echo ===================================================
cd /d "%~dp0"
"C:\Users\pasup\AppData\Local\Programs\Python\Python314\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
pause
