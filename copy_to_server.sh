#!/bin/bash

# Script to help copy deployment files to your server
# This assumes you have your SSH key properly configured

SERVER_IP="116.63.211.198"
SERVER_USER="root"
SSH_KEY="~/.ssh/ecs-kurtis-123"  # Update this path to your actual key location

echo "Copying deployment scripts to server..."

# Copy all deployment scripts
scp -i $SSH_KEY deploy_nginx.sh $SERVER_USER@$SERVER_IP:/root/
scp -i $SSH_KEY deploy_nginx_https.sh $SERVER_USER@$SERVER_IP:/root/
scp -i $SSH_KEY docker_deploy.sh $SERVER_USER@$SERVER_IP:/root/

echo "Files copied successfully!"
echo ""
echo "Now SSH into your server and run:"
echo "  ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP"
echo "  sudo bash deploy_nginx.sh"