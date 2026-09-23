#!/bin/bash
echo "╔═══════════════════════════════════════════════════════╗"
echo "║        TruthLens — Fake News Detection System        ║"
echo "║          Intra-IIT Hackathon 2026 · Starting         ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

cd backend

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "[1/4] Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "[2/4] Activating virtual environment..."
source venv/bin/activate

echo "[3/4] Installing dependencies..."
pip install -r requirements.txt -q

echo "[4/4] Starting FastAPI server..."
echo ""
echo "✓ Backend starting at: http://localhost:8000"
echo "✓ API Docs: http://localhost:8000/docs"
echo "✓ Open frontend/index.html in your browser!"
echo ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
