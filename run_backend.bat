@echo off
title TruthLens Backend - FastAPI (Port 8000)
cd /d "%~dp0backend"

echo ========================================================
echo   TruthLens Backend - Fake News Detection API
echo ========================================================
echo.

echo [1/2] Checking if port 8000 is occupied...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing existing process on port 8000 (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

echo [2/2] Starting Uvicorn Server on port 8000...
echo.
echo  Backend URL:      http://localhost:8000
echo  Interactive Docs: http://localhost:8000/docs
echo  Health Check:     http://localhost:8000/health
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
