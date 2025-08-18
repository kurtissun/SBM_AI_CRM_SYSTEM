#!/bin/bash

# Nginx deployment script for HTTP configuration
# Run this script on your server as root or with sudo

set -e  # Exit on error

echo "Starting Nginx configuration setup..."

# Variables - Update these according to your setup
DOMAIN="your_domain"  # Replace with your domain or public IP
FRONTEND_PORT="3000"  # Replace with your frontend port
BACKEND_PORT="8080"   # Replace with your backend port

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

# Test Nginx configuration first
echo "Testing current Nginx configuration..."
nginx -t

# Create Nginx configuration file
echo "Creating Nginx configuration..."
cat > /etc/nginx/sites-available/$DOMAIN << EOF
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;
    
    # Frontend
    location / {
        proxy_pass http://localhost:$FRONTEND_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:$BACKEND_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable the site
echo "Enabling site..."
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/

# Test new configuration
echo "Testing new Nginx configuration..."
nginx -t

# Restart Nginx
echo "Restarting Nginx..."
systemctl restart nginx

# Check Nginx status
echo "Checking Nginx status..."
systemctl status nginx --no-pager

echo "Nginx configuration complete!"
echo "You can test your setup with:"
echo "  curl http://localhost:$FRONTEND_PORT"
echo "  curl http://localhost:$BACKEND_PORT/api"