#!/bin/bash

echo "🚀 IntelliGrid Setup Script"
echo "=========================="
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Must run from project root (where backend/ and frontend/ directories exist)"
    exit 1
fi

echo "✅ Found backend/ and frontend/ directories"
echo ""

# Step 1: Setup Backend
echo "📦 Step 1: Setting up Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3.13 -m venv venv
fi

source venv/bin/activate
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

echo "✅ Backend setup complete"
cd ..
echo ""

# Step 2: Setup Frontend
echo "📦 Step 2: Setting up Frontend..."
cd frontend

echo "Installing Bun dependencies..."
bun install

echo "Clearing Next.js cache..."
rm -rf .next node_modules/.cache

echo "✅ Frontend setup complete"
cd ..
echo ""

# Step 3: Create .env file if it doesn't exist
echo "📄 Step 3: Setting up environment..."
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file - you can customize it if needed"
else
    echo "✅ .env file already exists"
fi
echo ""

# Step 4: Test Backend
echo "🧪 Step 4: Testing Backend..."
cd backend
source venv/bin/activate
python -m pytest tests/ -q --tb=short 2>&1 | tail -5
cd ..
echo ""

# Step 5: Instructions
echo "✨ Setup Complete!"
echo ""
echo "🎯 Next Steps - Run both services:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd /home/lamine/Projects/IntelliGrid/backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd /home/lamine/Projects/IntelliGrid/frontend"
echo "  bun run dev"
echo ""
echo "📱 Access Points:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Or use the convenience script:"
echo "  ./start-dev.sh"
