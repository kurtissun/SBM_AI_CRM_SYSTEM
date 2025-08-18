#!/bin/bash

set -e

echo "==================================="
echo "SBM AI CRM - SSH Quick Upload"
echo "==================================="

if [ $# -lt 3 ]; then
    echo "Usage: $0 <server-ip> <username> <remote-directory>"
    echo "Example: $0 192.168.1.100 ubuntu /home/ubuntu/sbm_crm"
    exit 1
fi

SERVER_IP=$1
USERNAME=$2
REMOTE_DIR=$3

echo "Uploading files via rsync..."
echo "Server: $SERVER_IP"
echo "Username: $USERNAME"
echo "Remote Directory: $REMOTE_DIR"
echo ""

rsync -avz --progress \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude 'node_modules' \
    --exclude '.env.local' \
    --exclude '*.log' \
    --exclude 'venv' \
    --exclude '.DS_Store' \
    --exclude '*.db' \
    --exclude 'dist' \
    --exclude 'build' \
    . ${USERNAME}@${SERVER_IP}:${REMOTE_DIR}/

echo ""
echo "Upload complete!"
echo ""
echo "To connect to server:"
echo "ssh ${USERNAME}@${SERVER_IP}"
echo "cd ${REMOTE_DIR}"