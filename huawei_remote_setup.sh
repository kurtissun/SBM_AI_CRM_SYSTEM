#!/bin/bash

set -e

echo "==================================="
echo "SBM AI CRM - Remote Server Setup"
echo "==================================="
echo "Run this script ON THE REMOTE SERVER after uploading files"
echo ""

cd "$(dirname "$0")"

echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx \
    postgresql \
    postgresql-contrib \
    redis-server \
    supervisor

echo ""
echo "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

echo ""
echo "Setting up frontend..."
cd frontend
npm install
npm run build
cd ..

echo ""
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p data
mkdir -p uploads
mkdir -p backups

echo ""
echo "Setting up PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

sudo -u postgres psql << EOF
CREATE DATABASE sbm_crm;
CREATE USER sbm_user WITH ENCRYPTED PASSWORD 'sbm_secure_password';
GRANT ALL PRIVILEGES ON DATABASE sbm_crm TO sbm_user;
\q
EOF

echo ""
echo "Setting up Redis..."
sudo systemctl start redis-server
sudo systemctl enable redis-server

echo ""
echo "Creating environment files..."
if [ ! -f "backend/.env" ]; then
    cat > backend/.env << 'EOF'
DATABASE_URL=postgresql://sbm_user:sbm_secure_password@localhost/sbm_crm
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
DEBUG=False
ALLOWED_HOSTS=*
CORS_ORIGINS=http://localhost:3000,http://localhost:4000
EOF
    echo "Created backend/.env - PLEASE UPDATE WITH YOUR VALUES"
fi

if [ ! -f "frontend/.env" ]; then
    cat > frontend/.env << 'EOF'
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=SBM AI CRM
VITE_APP_VERSION=1.0.0
EOF
    echo "Created frontend/.env - PLEASE UPDATE WITH YOUR SERVER IP"
fi

echo ""
echo "Setting up Nginx configuration..."
sudo tee /etc/nginx/sites-available/sbm_crm << 'EOF'
server {
    listen 80;
    server_name _;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://localhost:4000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/sbm_crm /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo ""
echo "Setting up Supervisor for process management..."
sudo tee /etc/supervisor/conf.d/sbm_crm.conf << EOF
[program:sbm_backend]
command=$(pwd)/venv/bin/python backend/main.py
directory=$(pwd)/backend
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$(pwd)/logs/backend.log
environment=PATH="$(pwd)/venv/bin",PYTHONPATH="$(pwd)/backend"

[program:sbm_frontend]
command=npm run preview -- --port 4000
directory=$(pwd)/frontend
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$(pwd)/logs/frontend.log
environment=NODE_ENV="production"
EOF

sudo supervisorctl reread
sudo supervisorctl update

echo ""
echo "Setting up firewall..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 3000
sudo ufw allow 4000
sudo ufw allow 8000
echo "y" | sudo ufw enable

echo ""
echo "Setting permissions..."
chmod +x *.sh
sudo chown -R $USER:$USER .

echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "IMPORTANT NEXT STEPS:"
echo "1. Update backend/.env with your actual database credentials and secrets"
echo "2. Update frontend/.env with your server's public IP"
echo "3. Run database migrations: source venv/bin/activate && cd backend && python manage.py migrate"
echo "4. Create superuser: python manage.py createsuperuser"
echo "5. Start services: sudo supervisorctl start all"
echo "6. For HTTPS, run: sudo certbot --nginx -d yourdomain.com"
echo ""
echo "To check service status: sudo supervisorctl status"
echo "To view logs: tail -f logs/*.log"