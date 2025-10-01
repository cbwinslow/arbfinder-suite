#!/bin/bash
# Start all ArbFinder services

echo "🚀 Starting ArbFinder Suite..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run:"
    echo "   python3 -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r backend/requirements.txt"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend dependencies not installed. Run:"
    echo "   cd frontend && npm install"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Start API server in background
echo "📡 Starting API server on port 8080..."
uvicorn backend.api.main:app --reload --port 8080 &
API_PID=$!
sleep 2

# Start frontend in background
echo "🎨 Starting frontend on port 3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Services started!"
echo ""
echo "🌐 Frontend:    http://localhost:3000"
echo "📡 API:         http://localhost:8080"
echo "📚 API Docs:    http://localhost:8080/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "echo ''; echo '🛑 Stopping services...'; kill $API_PID $FRONTEND_PID; exit 0" INT

wait
