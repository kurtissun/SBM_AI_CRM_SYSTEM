#!/bin/bash

set -e

echo "==================================="
echo "SBM AI CRM - Simple Huawei Deployment"
echo "==================================="

SERVER_IP="116.63.211.198"
USERNAME="root"
REMOTE_DIR="/opt/sbm_crm"

echo "Deploying to: ${USERNAME}@${SERVER_IP}:${REMOTE_DIR}"
echo ""

echo "Step 1: Creating deployment package..."
rm -f sbm_deploy.tar.gz
tar -czf sbm_deploy.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='node_modules' \
    --exclude='.env.local' \
    --exclude='*.log' \
    --exclude='venv' \
    --exclude='.DS_Store' \
    --exclude='sbm_deploy.tar.gz' \
    --exclude='*.tar.gz' \
    .

echo "Package created: sbm_deploy.tar.gz ($(du -h sbm_deploy.tar.gz | cut -f1))"
echo ""

echo "Step 2: Preparing server..."
ssh ${USERNAME}@${SERVER_IP} << 'EOF'
    echo "Creating application directory..."
    mkdir -p /opt/sbm_crm
    cd /opt/sbm_crm
    
    echo "Cleaning previous deployment..."
    rm -rf backend frontend *.sh *.md
    
    echo "Installing system packages..."
    apt-get update
    apt-get install -y python3 python3-pip python3-venv nodejs npm nginx
    
    echo "Server prepared!"
EOF

echo ""
echo "Step 3: Uploading application..."
scp sbm_deploy.tar.gz ${USERNAME}@${SERVER_IP}:/opt/sbm_crm/

echo ""
echo "Step 4: Extracting and setting up..."
ssh ${USERNAME}@${SERVER_IP} << 'EOF'
    cd /opt/sbm_crm
    tar -xzf sbm_deploy.tar.gz
    rm sbm_deploy.tar.gz
    
    echo "Setting up Python environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r backend/requirements.txt
    
    echo "Setting up Frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
    
    echo "Setting permissions..."
    chmod +x *.sh
    
    echo "Setup complete!"
EOF

echo ""
echo "Step 5: Creating launch script on server..."
ssh ${USERNAME}@${SERVER_IP} << 'EOF'
cat > /opt/sbm_crm/start_services.sh << 'SCRIPT'
#!/bin/bash
cd /opt/sbm_crm

echo "Starting Backend API..."
source venv/bin/activate
nohup python backend/main.py > backend.log 2>&1 &
echo $! > backend.pid

echo "Starting Frontend..."
cd frontend
nohup npm run preview -- --port 4000 --host 0.0.0.0 > ../frontend.log 2>&1 &
echo $! > ../frontend.pid
cd ..

sleep 3
echo ""
echo "Services started!"
echo "Frontend: http://$(hostname -I | awk '{print $1}'):4000"
echo "Backend API: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "To stop: kill $(cat backend.pid) $(cat frontend.pid)"
SCRIPT

chmod +x /opt/sbm_crm/start_services.sh
EOF

echo ""
echo "Step 6: Cleaning up..."
rm sbm_deploy.tar.gz

echo ""
echo "==================================="
echo "Deployment Complete!"
echo "==================================="
echo ""
echo "To start the application:"
echo "1. SSH to server: ssh root@${SERVER_IP}"
echo "2. cd /opt/sbm_crm"
echo "3. ./start_services.sh"
echo ""
echo "Access URLs:"
echo "  Frontend: http://${SERVER_IP}:4000"
echo "  Backend API: http://${SERVER_IP}:8000"
echo ""