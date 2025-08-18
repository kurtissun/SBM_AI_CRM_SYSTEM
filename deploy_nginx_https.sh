#!/bin/bash

# Nginx deployment script for HTTPS configuration with SSL
# Run this script on your server as root or with sudo

set -e  # Exit on error

echo "Starting Nginx HTTPS configuration setup..."

# Variables - Update these according to your setup
DOMAIN="your_domain.com"  # Replace with your actual domain
FRONTEND_PORT="3000"       # Replace with your frontend port
BACKEND_PORT="8080"        # Replace with your backend port
SSL_CERT_PATH="/path/to/your/certificate.crt"  # Update with actual path
SSL_KEY_PATH="/path/to/your/certificate.key"    # Update with actual path

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

# Test Nginx configuration first
echo "Testing current Nginx configuration..."
nginx -t

# Create Nginx configuration file with HTTPS
echo "Creating Nginx HTTPS configuration..."
cat > /etc/nginx/sites-available/$DOMAIN << EOF
# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$host\$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL configuration
    ssl_certificate $SSL_CERT_PATH;
    ssl_certificate_key $SSL_KEY_PATH;
    
    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
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

echo "Nginx HTTPS configuration complete!"
echo "Your site should now be accessible at:"
echo "  https://$DOMAIN"
echo "  API endpoint: https://$DOMAIN/api"