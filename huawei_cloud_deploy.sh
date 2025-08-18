#!/bin/bash

set -e

echo "==================================="
echo "SBM AI CRM - Huawei Cloud Deployment"
echo "==================================="

if [ $# -lt 3 ]; then
    echo "Usage: $0 <server-ip> <username> <remote-directory>"
    echo "Example: $0 192.168.1.100 ubuntu /home/ubuntu/sbm_crm"
    exit 1
fi

SERVER_IP=$1
USERNAME=$2
REMOTE_DIR=$3
LOCAL_DIR=$(pwd)
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="${REMOTE_DIR}_backup_${TIMESTAMP}"

echo "Server: $SERVER_IP"
echo "Username: $USERNAME"  
echo "Remote Directory: $REMOTE_DIR"
echo ""

echo "Creating deployment package..."
tar -czf sbm_crm_deploy.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='node_modules' \
    --exclude='.env.local' \
    --exclude='*.log' \
    --exclude='venv' \
    --exclude='.DS_Store' \
    --exclude='sbm_crm_deploy.tar.gz' \
    .

echo "Package created: sbm_crm_deploy.tar.gz"
echo ""

echo "Connecting to server and preparing deployment..."
ssh -t ${USERNAME}@${SERVER_IP} bash << ENDSSH
    echo "Creating backup of existing deployment..."
    if [ -d "${REMOTE_DIR}" ]; then
        mv "${REMOTE_DIR}" "${BACKUP_DIR}"
        echo "Backup created at: ${BACKUP_DIR}"
    fi
    
    echo "Creating deployment directory..."
    mkdir -p "${REMOTE_DIR}"
    cd "${REMOTE_DIR}"
    
    echo "Installing system dependencies..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv nodejs npm docker.io docker-compose nginx certbot python3-certbot-nginx
    
    echo "Server preparation complete!"
ENDSSH

echo ""
echo "Uploading deployment package..."
scp sbm_crm_deploy.tar.gz ${USERNAME}@${SERVER_IP}:${REMOTE_DIR}/

echo "Extracting and setting up application..."
ssh -t ${USERNAME}@${SERVER_IP} bash << ENDSSH
    cd "${REMOTE_DIR}"
    tar -xzf sbm_crm_deploy.tar.gz
    rm sbm_crm_deploy.tar.gz
    
    echo "Setting up Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r backend/requirements.txt
    
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    npm run build
    cd ..
    
    echo "Setting permissions..."
    chmod +x *.sh
    chmod +x backend/*.sh 2>/dev/null || true
    chmod +x frontend/*.sh 2>/dev/null || true
    
    echo "Application setup complete!"
ENDSSH

echo ""
echo "Cleaning up local package..."
rm sbm_crm_deploy.tar.gz

echo ""
echo "==================================="
echo "Deployment Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. SSH into server: ssh ${USERNAME}@${SERVER_IP}"
echo "2. Navigate to: cd ${REMOTE_DIR}"
echo "3. Configure environment variables in .env files"
echo "4. Run: ./huawei_cloud_launch.sh"
echo ""