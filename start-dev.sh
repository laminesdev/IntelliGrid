#!/bin/bash

echo "🚀 Starting IntelliGrid Development Environment"
echo "================================================"
echo ""

# Check if processes are already running
echo "Checking for existing processes..."

# Kill existing processes on ports 3000 and 8000
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null

sleep 1

echo "✅ Cleared existing processes"
echo ""

# Terminal 1: Backend
echo "🔧 Starting Backend (FastAPI) on port 8000..."
cd /home/lamine/Projects/IntelliGrid/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "✅ Backend started with PID: $BACKEND_PID"
echo "   API available at: http://localhost:8000"
echo "   API docs at: http://localhost:8000/docs"
echo ""

# Terminal 2: Frontend
echo "🎨 Starting Frontend (Next.js) on port 3000..."
cd /home/lamine/Projects/IntelliGrid/frontend
bun run dev &
FRONTEND_PID=$!

echo "✅ Frontend started with PID: $FRONTEND_PID"
echo "   App available at: http://localhost:3000"
echo ""

# Wait a moment for services to start
sleep 3

echo "🎉 Both services are running!"
echo ""
echo "📱 Access Points:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

trap cleanup INT

# Keep script running
wait
