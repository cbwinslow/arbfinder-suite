#!/bin/bash
# ArbFinder Suite Setup Script

set -e

echo "🚀 ArbFinder Suite Setup"
echo "========================"
echo ""

# Check for required tools
echo "Checking for required tools..."
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Aborting." >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm is required but not installed. Aborting." >&2; exit 1; }

echo "✅ All required tools found"
echo ""

# Ask for setup type
echo "Select setup type:"
echo "1) Full setup (Python + Frontend + Cloudflare)"
echo "2) Backend only (Python API)"
echo "3) Frontend only (Next.js Dashboard)"
echo "4) Docker Compose (All services)"
read -p "Enter choice [1-4]: " choice
echo ""

case $choice in
  1)
    echo "📦 Installing Python dependencies..."
    pip install -e ".[dev]"
    
    echo "📦 Installing Frontend dependencies..."
    cd frontend
    npm install
    cd ..
    
    echo "📦 Installing Cloudflare Worker dependencies..."
    cd cloudflare
    npm install
    cd ..
    
    echo "📝 Setting up environment..."
    if [ ! -f .env ]; then
      cp .env.example .env
      echo "⚠️  Please edit .env with your configuration"
    fi
    
    echo "✅ Full setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env with your database and API keys"
    echo "2. Run 'npx prisma generate' to generate Prisma client"
    echo "3. Run 'npx prisma db push' to create database tables"
    echo "4. Start backend: uvicorn backend.api.main:app --reload"
    echo "5. Start frontend: cd frontend && npm run dev"
    ;;
    
  2)
    echo "📦 Installing Python dependencies..."
    pip install -e ".[dev]"
    
    echo "📝 Setting up environment..."
    if [ ! -f .env ]; then
      cp .env.example .env
      echo "⚠️  Please edit .env with your configuration"
    fi
    
    echo "✅ Backend setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env with your database and API keys"
    echo "2. Run 'npx prisma generate' to generate Prisma client"
    echo "3. Run 'npx prisma db push' to create database tables"
    echo "4. Start backend: uvicorn backend.api.main:app --reload"
    ;;
    
  3)
    echo "📦 Installing Frontend dependencies..."
    cd frontend
    npm install
    cd ..
    
    echo "✅ Frontend setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Make sure backend is running on port 8080"
    echo "2. Start frontend: cd frontend && npm run dev"
    echo "3. Visit http://localhost:3000/dashboard"
    ;;
    
  4)
    echo "🐳 Setting up Docker Compose..."
    
    if [ ! -f .env ]; then
      cp .env.example .env
      echo "⚠️  Please edit .env with your configuration"
    fi
    
    echo "Building and starting services..."
    docker-compose up -d
    
    echo "✅ Docker setup complete!"
    echo ""
    echo "Services running:"
    echo "- PostgreSQL: localhost:5432"
    echo "- MinIO: localhost:9000 (Console: localhost:9001)"
    echo "- Backend API: localhost:8080"
    echo "- Frontend: localhost:3000"
    echo ""
    echo "View logs: docker-compose logs -f"
    echo "Stop services: docker-compose down"
    ;;
    
  *)
    echo "❌ Invalid choice"
    exit 1
    ;;
esac

echo ""
echo "📚 For more information, see:"
echo "- README.md - General overview"
echo "- PLATFORM_GUIDE.md - Detailed platform guide"
echo "- DEVELOPER.md - Development guide"
