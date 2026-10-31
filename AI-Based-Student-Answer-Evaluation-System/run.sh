#!/usr/bin/env bash
# AI-Based Student Answer Evaluation System - Unix Launcher

echo "======================================================================"
echo "   Starting AI-Based Student Answer Evaluation System"
echo "======================================================================"

if ! command -v python3 &> /dev/null; then
    echo "[WARNING] python3 could not be found."
    echo "Opening web interface directly in your default browser..."
    if command -v xdg-open &> /dev/null; then
        xdg-open static/index.html
    elif command -v open &> /dev/null; then
        open static/index.html
    fi
    exit 0
fi

echo "[1/3] Installing dependencies..."
python3 -m pip install -r requirements.txt --quiet

echo "[2/3] Launching Flask Server..."
python3 app.py &
SERVER_PID=$!

sleep 1.5

echo "[3/3] Opening browser..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://127.0.0.1:5000
elif command -v open &> /dev/null; then
    open http://127.0.0.1:5000
fi

wait $SERVER_PID
