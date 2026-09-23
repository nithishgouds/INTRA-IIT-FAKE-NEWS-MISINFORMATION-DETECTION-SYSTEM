@echo off
title TruthLens - Master Launcher
cd /d "%~dp0"

echo ========================================================
echo   Launching TruthLens: AI Misinformation Detection
echo ========================================================
echo.

echo [1/2] Launching Backend on http://localhost:8000 ...
start "TruthLens Backend" cmd /c "run_backend.bat"

timeout /t 3 /nobreak >nul

echo [2/2] Launching React Frontend on http://localhost:5173 ...
start "TruthLens React Frontend" cmd /c "run_frontend.bat"

timeout /t 2 /nobreak >nul

echo Opening browser at http://localhost:5173 ...
start http://localhost:5173

echo.
echo Both servers are now running!
echo   * React Web UI:  http://localhost:5173
echo   * FastAPI Docs:  http://localhost:8000/docs
echo.
pause
