#!/bin/bash

# Docker deployment script with China mirror registry support
# Run this script on your server

set -e  # Exit on error

echo "Starting Docker deployment..."

# Variables
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Function to replace DockerHub images with Daocloud mirror
replace_with_mirror() {
    if [ -f "$COMPOSE_FILE" ]; then
        echo "Updating docker-compose.yml to use China mirror registry..."
        # Backup original file
        cp $COMPOSE_FILE ${COMPOSE_FILE}.backup
        
        # Replace image references with Daocloud mirror
        # This handles common patterns like "image: nginx:latest" or "image: postgres:14"
        sed -i 's|image: \([^/]*\):|image: docker.m.daocloud.io/library/\1:|g' $COMPOSE_FILE
        
        echo "Docker images updated to use Daocloud mirror"
    fi
}

# Check if .env file exists, if not create it
if [ ! -f "$ENV_FILE" ]; then
    echo "Creating .env file..."
    cat > $ENV_FILE << EOF
# Environment variables
# Update these values according to your setup
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
JWT_SECRET=your-secret-key
NODE_ENV=production
FRONTEND_PORT=3000
BACKEND_PORT=8080
EOF
    echo ".env file created. Please update it with your actual values."
fi

# Replace images with China mirror if needed
read -p "Use China mirror registry (Daocloud)? (y/n): " use_mirror
if [ "$use_mirror" = "y" ]; then
    replace_with_mirror
fi

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

# Pull latest images
echo "Pulling latest images..."
docker-compose pull 2>/dev/null || docker compose pull

# Start containers in detached mode
echo "Starting containers..."
docker-compose up -d 2>/dev/null || docker compose up -d

# Wait for containers to start
echo "Waiting for containers to start..."
sleep 5

# Check container status
echo "Checking container status..."
docker ps

# Test endpoints
echo "Testing endpoints..."
FRONTEND_PORT=$(grep FRONTEND_PORT .env | cut -d '=' -f2)
BACKEND_PORT=$(grep BACKEND_PORT .env | cut -d '=' -f2)

echo "Testing frontend on port $FRONTEND_PORT..."
curl -I http://localhost:${FRONTEND_PORT:-3000} 2>/dev/null && echo "Frontend is running" || echo "Frontend not responding"

echo "Testing backend on port $BACKEND_PORT..."
curl -I http://localhost:${BACKEND_PORT:-8080}/api 2>/dev/null && echo "Backend is running" || echo "Backend not responding"

echo "Docker deployment complete!"
echo ""
echo "Useful commands:"
echo "  docker ps                    - List running containers"
echo "  docker logs <container_id>   - View container logs"
echo "  docker exec -it <container_id> sh - Enter container shell"
echo "  docker-compose logs -f       - Follow all container logs"