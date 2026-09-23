@echo off
echo ╔═══════════════════════════════════════════════════════╗
echo ║        TruthLens — Fake News Detection System        ║
echo ║          Intra-IIT Hackathon 2026 · Starting         ║
echo ╚═══════════════════════════════════════════════════════╝
echo.

cd backend

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo [1/4] Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo [3/4] Installing dependencies (this may take a few minutes)...
pip install -r requirements.txt -q

REM Start server
echo [4/4] Starting FastAPI server...
echo.
echo ✓ Backend starting at: http://localhost:8000
echo ✓ API Docs available at: http://localhost:8000/docs
echo ✓ Model will auto-train on startup if not already trained
echo.
echo Open frontend\index.html in your browser to use the application!
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
