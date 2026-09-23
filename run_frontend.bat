@echo off
title TruthLens Frontend - React + Vite (Port 5173)
cd /d "%~dp0frontend"

set PATH=C:\Program Files\nodejs;%PATH%

echo ========================================================
echo   TruthLens Frontend - Modern React Single Page App
echo ========================================================
echo.

if not exist node_modules (
    echo Installing npm dependencies...
    call npm install
)

echo Starting Vite React Dev Server...
echo.
echo  Frontend UI: http://localhost:5173
echo.

call npm run dev
pause
