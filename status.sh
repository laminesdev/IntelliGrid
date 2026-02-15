#!/bin/bash

echo "🔍 IntelliGrid Status Check"
echo "=========================="
echo ""

# Check Backend
echo "🔧 Backend Status:"
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "  ✅ Running on http://localhost:8000"
    curl -s http://localhost:8000/health 2>/dev/null | grep -q "healthy" && echo "  ✅ Health check: OK" || echo "  ⚠️  Health check: Failed"
else
    echo "  ❌ Not running (port 8000 free)"
fi
echo ""

# Check Frontend
echo "🎨 Frontend Status:"
if lsof -ti:3000 > /dev/null 2>&1; then
    echo "  ✅ Running on http://localhost:3000"
    curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null | grep -q "200" && echo "  ✅ Page loads: OK" || echo "  ⚠️  Page load: Issues detected"
else
    echo "  ❌ Not running (port 3000 free)"
fi
echo ""

# Check configuration files
echo "📁 Configuration Files:"
[ -f "/home/lamine/Projects/IntelliGrid/frontend/postcss.config.mjs" ] && echo "  ✅ PostCSS config (ES Module)" || echo "  ❌ PostCSS config missing"
[ -f "/home/lamine/Projects/IntelliGrid/frontend/tailwind.config.ts" ] && echo "  ✅ Tailwind config" || echo "  ❌ Tailwind config missing"
[ -f "/home/lamine/Projects/IntelliGrid/backend/venv/bin/activate" ] && echo "  ✅ Python venv" || echo "  ❌ Python venv missing"
echo ""

echo "💡 Quick Start Commands:"
echo "  ./start-dev.sh          # Start both services"
echo "  ./setup.sh              # Full setup (install dependencies)"
echo "  ./status.sh             # Check this status again"
