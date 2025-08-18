#!/bin/bash

set -e

echo "==================================="
echo "SBM AI CRM - Launch Services"
echo "==================================="
echo "Starting all services on Huawei Cloud server..."
echo ""

cd "$(dirname "$0")"

function check_service() {
    if lsof -i:$1 > /dev/null 2>&1; then
        echo "⚠️  Port $1 is already in use. Stopping existing service..."
        sudo fuser -k $1/tcp 2>/dev/null || true
        sleep 2
    fi
}

function start_backend() {
    echo "Starting Backend API..."
    check_service 8000
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        echo "Creating Python virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r backend/requirements.txt
    fi
    
    cd backend
    nohup python main.py > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    echo "Backend started with PID: $BACKEND_PID"
    echo $BACKEND_PID > logs/backend.pid
}

function start_frontend() {
    echo "Starting Frontend..."
    check_service 4000
    
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    
    if [ ! -d "dist" ]; then
        echo "Building frontend..."
        npm run build
    fi
    
    nohup npm run preview -- --port 4000 --host 0.0.0.0 > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    echo "Frontend started with PID: $FRONTEND_PID"
    echo $FRONTEND_PID > logs/frontend.pid
}

function start_with_docker() {
    echo "Starting with Docker Compose..."
    
    if ! command -v docker-compose &> /dev/null; then
        echo "Installing Docker Compose..."
        sudo apt-get update
        sudo apt-get install -y docker-compose
    fi
    
    docker-compose down 2>/dev/null || true
    docker-compose up -d
    
    echo "Services started with Docker Compose"
    echo "View logs: docker-compose logs -f"
}

function start_with_supervisor() {
    echo "Starting with Supervisor..."
    
    if ! command -v supervisorctl &> /dev/null; then
        echo "Installing Supervisor..."
        sudo apt-get update
        sudo apt-get install -y supervisor
    fi
    
    sudo supervisorctl start all
    echo "Services started with Supervisor"
    echo "Check status: sudo supervisorctl status"
}

function stop_all() {
    echo "Stopping all services..."
    
    if [ -f "logs/backend.pid" ]; then
        kill $(cat logs/backend.pid) 2>/dev/null || true
        rm logs/backend.pid
    fi
    
    if [ -f "logs/frontend.pid" ]; then
        kill $(cat logs/frontend.pid) 2>/dev/null || true
        rm logs/frontend.pid
    fi
    
    sudo supervisorctl stop all 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    
    sudo fuser -k 8000/tcp 2>/dev/null || true
    sudo fuser -k 4000/tcp 2>/dev/null || true
    
    echo "All services stopped"
}

function check_status() {
    echo ""
    echo "Checking service status..."
    echo "------------------------"
    
    if lsof -i:8000 > /dev/null 2>&1; then
        echo "✅ Backend API: Running on port 8000"
    else
        echo "❌ Backend API: Not running"
    fi
    
    if lsof -i:4000 > /dev/null 2>&1; then
        echo "✅ Frontend: Running on port 4000"
    else
        echo "❌ Frontend: Not running"
    fi
    
    if command -v supervisorctl &> /dev/null; then
        echo ""
        echo "Supervisor status:"
        sudo supervisorctl status 2>/dev/null || echo "Supervisor not configured"
    fi
    
    if command -v docker &> /dev/null; then
        echo ""
        echo "Docker status:"
        docker ps --filter "name=sbm" 2>/dev/null || echo "Docker not running"
    fi
}

function show_logs() {
    echo ""
    echo "Viewing logs (Ctrl+C to exit)..."
    echo "------------------------"
    tail -f logs/*.log
}

mkdir -p logs

case "${1:-manual}" in
    manual)
        echo "Starting services manually..."
        start_backend
        sleep 3
        start_frontend
        ;;
    docker)
        start_with_docker
        ;;
    supervisor)
        start_with_supervisor
        ;;
    stop)
        stop_all
        exit 0
        ;;
    status)
        check_status
        exit 0
        ;;
    logs)
        show_logs
        exit 0
        ;;
    *)
        echo "Usage: $0 [manual|docker|supervisor|stop|status|logs]"
        echo "  manual     - Start services manually (default)"
        echo "  docker     - Start with Docker Compose"
        echo "  supervisor - Start with Supervisor"
        echo "  stop       - Stop all services"
        echo "  status     - Check service status"
        echo "  logs       - View service logs"
        exit 1
        ;;
esac

sleep 5
check_status

echo ""
echo "==================================="
echo "Services Launched Successfully!"
echo "==================================="
echo ""
echo "Access points:"
echo "  Frontend: http://$(hostname -I | awk '{print $1}'):4000"
echo "  Backend API: http://$(hostname -I | awk '{print $1}'):8000"
echo "  API Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "Commands:"
echo "  Check status: ./huawei_cloud_launch.sh status"
echo "  View logs: ./huawei_cloud_launch.sh logs"
echo "  Stop services: ./huawei_cloud_launch.sh stop"
echo ""
echo "For production with HTTPS:"
echo "  sudo certbot --nginx -d yourdomain.com"