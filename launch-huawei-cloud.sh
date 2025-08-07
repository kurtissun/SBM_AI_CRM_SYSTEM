#!/bin/bash

# SBM AI CRM System - Huawei Cloud Deployment Script
# Runs frontend on port 4000 and backend on port 8080

echo "🚀 Starting SBM AI CRM System on Huawei Cloud..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${RED}❌ Port $1 is already in use${NC}"
        echo "Please stop the service using port $1 or choose a different port"
        return 1
    else
        echo -e "${GREEN}✅ Port $1 is available${NC}"
        return 0
    fi
}

# Check required ports
echo -e "\n${YELLOW}Checking port availability...${NC}"
PORTS_OK=true

if ! check_port 4000; then PORTS_OK=false; fi
if ! check_port 8080; then PORTS_OK=false; fi
if ! check_port 5432; then 
    echo -e "${YELLOW}⚠️  Port 5432 (PostgreSQL) is in use - will use existing database${NC}"
fi

if [ "$PORTS_OK" = false ]; then
    echo -e "\n${RED}Cannot proceed - required ports are in use${NC}"
    echo "Run 'sudo lsof -i -P -n | grep LISTEN' to see which processes are using the ports"
    exit 1
fi

# Check Docker installation
echo -e "\n${YELLOW}Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose are installed${NC}"

# Option to run with or without Docker
echo -e "\n${YELLOW}Select deployment method:${NC}"
echo "1) Docker deployment (recommended for production)"
echo "2) Direct deployment (for development)"
read -p "Enter your choice (1 or 2): " DEPLOY_CHOICE

if [ "$DEPLOY_CHOICE" = "1" ]; then
    # Docker deployment
    echo -e "\n${GREEN}Starting Docker deployment...${NC}"
    
    # Stop any existing containers
    echo "Stopping any existing containers..."
    docker-compose -f docker-compose.china.yml down 2>/dev/null
    
    # Pull images using Chinese mirrors
    echo -e "\n${YELLOW}Pulling Docker images from Chinese mirrors...${NC}"
    docker pull docker.m.daocloud.io/library/postgres:15
    docker pull docker.m.daocloud.io/library/redis:7-alpine
    
    # Start services
    echo -e "\n${GREEN}Starting services...${NC}"
    docker-compose -f docker-compose.china.yml up -d
    
    # Wait for services to be ready
    echo -e "\n${YELLOW}Waiting for services to start...${NC}"
    sleep 10
    
    # Check service status
    echo -e "\n${GREEN}Service Status:${NC}"
    docker-compose -f docker-compose.china.yml ps
    
else
    # Direct deployment
    echo -e "\n${GREEN}Starting direct deployment...${NC}"
    
    # Create log files
    mkdir -p logs
    
    # Start PostgreSQL if not running
    if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        echo -e "${YELLOW}Starting PostgreSQL...${NC}"
        if command -v systemctl &> /dev/null; then
            sudo systemctl start postgresql
        else
            echo -e "${RED}Please start PostgreSQL manually${NC}"
        fi
    fi
    
    # Start Redis if not running
    if ! redis-cli ping > /dev/null 2>&1; then
        echo -e "${YELLOW}Starting Redis...${NC}"
        redis-server --daemonize yes --appendonly yes
    fi
    
    # Start Backend on port 8080
    echo -e "\n${GREEN}Starting Backend on port 8080...${NC}"
    cd backend
    
    # Install Python dependencies if needed
    if [ ! -d "venv" ]; then
        echo "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    
    # Set environment variables
    export HOST=0.0.0.0
    export PORT=8080
    export DATABASE_URL=postgresql://postgres:superbrandmall@localhost:5432/sbm_crm
    export REDIS_URL=redis://localhost:6379/0
    
    # Start backend
    nohup python run_server.py > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    
    cd ..
    
    # Start Frontend on port 4000
    echo -e "\n${GREEN}Starting Frontend on port 4000...${NC}"
    cd frontend
    
    # Install Node dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "Installing Node dependencies..."
        npm install
    fi
    
    # Set environment variables
    export VITE_API_URL=http://localhost:8080
    export PORT=4000
    
    # Start frontend
    nohup npm run dev -- --host 0.0.0.0 --port 4000 > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    
    cd ..
    
    # Save PIDs for shutdown script
    echo "BACKEND_PID=$BACKEND_PID" > .pids
    echo "FRONTEND_PID=$FRONTEND_PID" >> .pids
fi

# Display access information
echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}🎉 SBM AI CRM System is running!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Access the application:"
echo -e "  Frontend:  ${YELLOW}http://localhost:4000${NC}"
echo -e "  Backend:   ${YELLOW}http://localhost:8080${NC}"
echo -e "  API Docs:  ${YELLOW}http://localhost:8080/docs${NC}"
echo ""
echo "From other machines on the network, replace 'localhost' with your server IP"
echo ""
echo "To stop the services:"
if [ "$DEPLOY_CHOICE" = "1" ]; then
    echo "  Run: docker-compose -f docker-compose.china.yml down"
else
    echo "  Run: ./stop-services.sh"
fi
echo ""
echo -e "${YELLOW}Logs:${NC}"
if [ "$DEPLOY_CHOICE" = "1" ]; then
    echo "  docker-compose -f docker-compose.china.yml logs -f"
else
    echo "  Backend:  tail -f logs/backend.log"
    echo "  Frontend: tail -f logs/frontend.log"
fi