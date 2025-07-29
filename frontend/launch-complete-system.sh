#!/bin/bash

# SBM AI CRM - Complete System Launcher
# This script launches both backend and frontend with all features

echo "🚀 SBM AI CRM - Complete System Launcher"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is already running on port 8000
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${GREEN}✅ Backend already running on port 8000${NC}"
else
    echo -e "${BLUE}🔧 Starting backend server...${NC}"
    cd ../backend
    python3 start_server.py &
    BACKEND_PID=$!
    sleep 3
    echo -e "${GREEN}✅ Backend started with PID: $BACKEND_PID${NC}"
    cd ../frontend
fi

# Check if frontend is already running on port 4000
if lsof -Pi :4000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${GREEN}✅ Frontend already running on port 4000${NC}"
    echo -e "${YELLOW}📱 Opening browser...${NC}"
    open http://localhost:4000
else
    echo -e "${BLUE}🔧 Starting frontend development server...${NC}"
    npm run dev &
    FRONTEND_PID=$!
    sleep 5
    echo -e "${GREEN}✅ Frontend started with PID: $FRONTEND_PID${NC}"
    echo -e "${YELLOW}📱 Opening browser...${NC}"
    open http://localhost:4000
fi

echo ""
echo -e "${GREEN}🎉 SBM AI CRM System is now running!${NC}"
echo ""
echo -e "${BLUE}📊 Available Features:${NC}"
echo "   1. Customer Intelligence Hub - 360° customer insights"
echo "   2. AI Campaign Command Center - ROI optimization & A/B testing"
echo "   3. Intelligent Segmentation Studio - ML-powered segments"
echo "   4. Analytics & Insights Center - Predictive analytics & forecasting"
echo "   5. Journey & Automation Control - Customer lifecycle management"
echo "   6. AI Assistant & Chat Suite - Natural language database queries"
echo "   7. Real-time Operations Center - Live monitoring & alerts"
echo "   8. Reports & Visualization Studio - 18+ chart types"
echo "   9. Mall Operations Analytics - Traffic patterns & store performance"
echo "   10. Camera Intelligence Dashboard - Footfall & demographics"
echo "   11. Chinese Market & Competition Suite - WeChat/Alipay integration"
echo "   12. Loyalty & VIP Management - Tier progression & rewards"
echo "   13. Retail Intelligence Engine - Inventory & price optimization"
echo "   14. Economic & What-If Simulator - Scenario planning"
echo "   15. Voice of Customer Analytics - Social listening & sentiment"
echo "   16. Configuration & Admin Center - User & system management"
echo ""
echo -e "${YELLOW}🌐 Access URLs:${NC}"
echo "   Frontend: http://localhost:4000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo -e "${BLUE}🔑 Features Included:${NC}"
echo "   ✅ All 22 Original AI Engines"
echo "   ✅ 7 Additional SBM-Specific Features"
echo "   ✅ Creatio-Inspired Modern UI"
echo "   ✅ Real-time API Integration"
echo "   ✅ Chinese Market Localization"
echo "   ✅ Mall-Specific Analytics"
echo ""
echo -e "${GREEN}Press Ctrl+C to stop both services${NC}"

# Wait for user input to stop
wait