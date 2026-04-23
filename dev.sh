#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"

cleanup() {
    echo ""
    echo "Остановка процессов..."
    kill $(jobs -p) 2>/dev/null || true
    wait 2>/dev/null
    echo "Готово."
}
trap cleanup EXIT INT TERM

source "$VENV_DIR/bin/activate"

echo "Запуск бэкенда (FastAPI :8000)..."
python -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Запуск фронтенда (Vite :5173)..."
cd "$PROJECT_ROOT/frontend"
npm run dev -- --host &
FRONTEND_PID=$!

echo ""
echo "═══════════════════════════════════════"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  API:      http://localhost:8000/docs"
echo "═══════════════════════════════════════"
echo ""
echo "Ctrl+C для остановки"

wait
