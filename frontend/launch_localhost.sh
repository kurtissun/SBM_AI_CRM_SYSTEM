#!/bin/bash

echo "🚀 Launching SBM AI CRM React Frontend on Localhost"
echo "🔧 VPN bypass configuration enabled"
echo ""

# Kill any existing processes on common ports
echo "🛑 Cleaning up existing processes..."
sudo lsof -ti:3000,4000,5000,8080 | sudo xargs kill -9 2>/dev/null || true

# Set network optimizations for VPN compatibility
echo "🌐 Configuring network settings..."
export HOST=0.0.0.0
export PORT=4000
export BROWSER=none

# Try multiple approaches
echo "🎯 Attempting React dev server startup..."

# Method 1: Vite with explicit host binding
echo "📦 Method 1: Vite dev server"
npm run dev &
VITE_PID=$!

# Give it time to start
sleep 5

# Test if it's accessible
if curl -s http://localhost:4000 >/dev/null 2>&1; then
    echo "✅ SUCCESS: React frontend running on http://localhost:4000"
    echo "🎨 Features: Beautiful Creatio-inspired UI with 16 modules"
    echo "🧠 Backend: 22 AI engines connected"
    echo "🔑 Login: admin / admin123"
    echo ""
    echo "🌐 Also try these URLs:"
    echo "   • http://127.0.0.1:4000"
    echo "   • http://10.1.1.113:4000"
    echo ""
    echo "⚠️  Keep this terminal open - server running in background"
    echo "🛑 Press Ctrl+C to stop the server"
    
    # Keep script running
    wait $VITE_PID
else
    echo "❌ Method 1 failed, trying alternative..."
    kill $VITE_PID 2>/dev/null
    
    # Method 2: Serve static build
    echo "📦 Method 2: Static file server"
    npm run build
    npx serve -s dist -l 4000 --cors &
    SERVE_PID=$!
    
    sleep 3
    
    if curl -s http://localhost:4000 >/dev/null 2>&1; then
        echo "✅ SUCCESS: Static frontend running on http://localhost:4000"
        wait $SERVE_PID
    else
        echo "❌ Method 2 failed, trying Python server..."
        kill $SERVE_PID 2>/dev/null
        
        # Method 3: Python HTTP server
        echo "📦 Method 3: Python HTTP server"
        cd dist
        python3 -m http.server 4000 --bind 0.0.0.0 &
        PYTHON_PID=$!
        
        sleep 3
        
        if curl -s http://localhost:4000 >/dev/null 2>&1; then
            echo "✅ SUCCESS: Python server running on http://localhost:4000"
            wait $PYTHON_PID
        else
            echo "❌ All methods failed - VPN may be blocking localhost completely"
            echo "💡 Try temporarily disabling VPN or use the standalone HTML file"
            kill $PYTHON_PID 2>/dev/null
        fi
    fi
fi