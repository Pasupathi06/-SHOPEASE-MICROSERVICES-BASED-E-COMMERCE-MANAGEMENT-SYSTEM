@echo off
title ShopEase User Service - Port 8002
echo ===================================================
echo Starting ShopEase User Management Service on Port 8002...
echo ===================================================
cd /d "%~dp0"
"C:\Users\pasup\AppData\Local\Programs\Python\Python314\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
pause
