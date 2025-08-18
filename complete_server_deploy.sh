#!/bin/bash

# Complete server deployment script for SBM CRM System
# Run this on your server after copying the project files

set -e  # Exit on error

echo "=== SBM CRM Complete Server Deployment ==="
echo ""

# Variables
SERVER_IP="116.63.211.198"
FRONTEND_PORT="3000"
BACKEND_PORT="8080"

# Step 1: Update system
echo "Step 1: Updating system packages..."
apt-get update -y

# Step 2: Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo "Step 2: Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl start docker
    systemctl enable docker
else
    echo "Step 2: Docker already installed"
fi

# Step 3: Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo "Step 3: Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo "Step 3: Docker Compose already installed"
fi

# Step 4: Create .env file if not exists
if [ ! -f .env ]; then
    echo "Step 4: Creating .env file..."
    cat > .env << EOF
# Environment variables
DATABASE_URL=postgresql://postgres:password@postgres:5432/sbm_crm
REDIS_URL=redis://redis:6379/0
JWT_SECRET=your-secret-jwt-key-change-this
NODE_ENV=production
FRONTEND_PORT=$FRONTEND_PORT
BACKEND_PORT=$BACKEND_PORT
API_BASE_URL=http://localhost:$BACKEND_PORT
EOF
    echo ".env file created. Please update it with your actual values if needed."
else
    echo "Step 4: .env file already exists"
fi

# Step 5: Stop existing containers
echo "Step 5: Stopping existing containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

# Step 6: Pull images with China mirror
echo "Step 6: Pulling Docker images..."
docker-compose pull || docker compose pull

# Step 7: Start Docker containers
echo "Step 7: Starting Docker containers..."
docker-compose up -d || docker compose up -d

# Step 8: Wait for containers to start
echo "Step 8: Waiting for containers to start..."
sleep 10

# Step 9: Check container status
echo "Step 9: Checking container status..."
docker ps

# Step 10: Configure Nginx for reverse proxy
echo "Step 10: Configuring Nginx..."
if ! command -v nginx &> /dev/null; then
    echo "Installing Nginx..."
    apt-get install -y nginx
fi

# Create Nginx configuration
cat > /etc/nginx/sites-available/sbm-crm << EOF
server {
    listen 80;
    listen [::]:80;
    server_name $SERVER_IP;
    
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
ln -sf /etc/nginx/sites-available/sbm-crm /etc/nginx/sites-enabled/

# Remove default site if exists
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo "Testing Nginx configuration..."
nginx -t

# Restart Nginx
echo "Restarting Nginx..."
systemctl restart nginx

# Step 11: Test endpoints
echo ""
echo "Step 11: Testing endpoints..."
sleep 5

echo "Testing frontend..."
if curl -f -s -o /dev/null -w "%{http_code}" http://localhost:$FRONTEND_PORT | grep -q "200\|301\|302"; then
    echo "✓ Frontend is running on port $FRONTEND_PORT"
else
    echo "✗ Frontend not responding on port $FRONTEND_PORT"
fi

echo "Testing backend API..."
if curl -f -s -o /dev/null -w "%{http_code}" http://localhost:$BACKEND_PORT/api | grep -q "200\|301\|302\|404"; then
    echo "✓ Backend API is running on port $BACKEND_PORT"
else
    echo "✗ Backend API not responding on port $BACKEND_PORT"
fi

echo "Testing Nginx proxy..."
if curl -f -s -o /dev/null -w "%{http_code}" http://$SERVER_IP | grep -q "200\|301\|302"; then
    echo "✓ Nginx proxy is working"
else
    echo "✗ Nginx proxy not working"
fi

# Step 12: Show summary
echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Your SBM CRM system should now be accessible at:"
echo "  Main URL: http://$SERVER_IP"
echo "  API endpoint: http://$SERVER_IP/api"
echo ""
echo "Container status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "Useful commands:"
echo "  docker-compose logs -f          # View all logs"
echo "  docker-compose restart          # Restart all services"
echo "  docker exec -it <container> sh  # Enter container"
echo "  systemctl status nginx          # Check Nginx status"
echo ""
echo "If services are not running, check logs with:"
echo "  docker-compose logs sbm-api"
echo "  docker-compose logs sbm-frontend"
echo "  journalctl -u nginx"