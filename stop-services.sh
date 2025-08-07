#!/bin/bash

# Stop services script for non-Docker deployment

echo "🛑 Stopping SBM AI CRM System services..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker services are running
if docker-compose -f docker-compose.china.yml ps 2>/dev/null | grep -q "Up"; then
    echo -e "${YELLOW}Stopping Docker services...${NC}"
    docker-compose -f docker-compose.china.yml down
    echo -e "${GREEN}✅ Docker services stopped${NC}"
fi

# Check for PIDs file (direct deployment)
if [ -f ".pids" ]; then
    echo -e "${YELLOW}Stopping direct deployment services...${NC}"
    source .pids
    
    if [ ! -z "$BACKEND_PID" ]; then
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo "Stopping backend (PID: $BACKEND_PID)..."
            kill $BACKEND_PID
            echo -e "${GREEN}✅ Backend stopped${NC}"
        fi
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo "Stopping frontend (PID: $FRONTEND_PID)..."
            kill $FRONTEND_PID
            echo -e "${GREEN}✅ Frontend stopped${NC}"
        fi
    fi
    
    rm .pids
fi

# Kill any remaining processes on our ports
echo -e "\n${YELLOW}Checking for processes on ports...${NC}"

# Port 4000 (Frontend)
if lsof -Pi :4000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Killing process on port 4000..."
    lsof -ti:4000 | xargs kill -9 2>/dev/null
fi

# Port 8080 (Backend)
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Killing process on port 8080..."
    lsof -ti:8080 | xargs kill -9 2>/dev/null
fi

echo -e "\n${GREEN}✅ All services stopped${NC}"