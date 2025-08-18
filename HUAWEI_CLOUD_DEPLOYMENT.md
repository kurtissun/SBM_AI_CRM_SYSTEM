# SBM AI CRM - Huawei Cloud Deployment Guide

## Prerequisites

1. **Huawei Cloud ECS Instance**
   - Ubuntu 20.04 or 22.04 LTS
   - Minimum: 2 vCPUs, 4GB RAM, 40GB disk
   - Recommended: 4 vCPUs, 8GB RAM, 100GB disk
   - Security group with ports: 22 (SSH), 80 (HTTP), 443 (HTTPS), 8000 (API), 4000 (Frontend)

2. **Local Requirements**
   - SSH client
   - rsync (for efficient file sync)
   - Your SSH key added to the server

## Quick Deployment Steps

### 1. Initial Full Deployment
```bash
# Make scripts executable
chmod +x huawei_*.sh

# Deploy everything (uploads files, installs dependencies, sets up services)
./huawei_cloud_deploy.sh <server-ip> <username> <remote-directory>

# Example:
./huawei_cloud_deploy.sh 192.168.1.100 ubuntu /home/ubuntu/sbm_crm
```

### 2. SSH into Server and Complete Setup
```bash
# Connect to server
ssh ubuntu@192.168.1.100

# Navigate to deployment directory
cd /home/ubuntu/sbm_crm

# Run the remote setup script
./huawei_remote_setup.sh

# Update configuration files
nano backend/.env  # Add your database credentials, API keys, etc.
nano frontend/.env # Update VITE_API_URL with your server's public IP

# Launch the application
./huawei_cloud_launch.sh
```

### 3. Quick Updates (After Initial Deployment)
```bash
# For quick code updates without full reinstall
./huawei_ssh_upload.sh <server-ip> <username> <remote-directory>

# Then SSH in and restart services
ssh ubuntu@192.168.1.100
cd /home/ubuntu/sbm_crm
./huawei_cloud_launch.sh stop
./huawei_cloud_launch.sh
```

## Deployment Scripts Overview

### 1. `huawei_cloud_deploy.sh`
- Complete deployment script
- Creates tarball of project
- Uploads to server
- Installs all system dependencies
- Sets up Python and Node.js environments

### 2. `huawei_ssh_upload.sh`
- Quick sync using rsync
- Excludes unnecessary files (node_modules, venv, etc.)
- Faster than full deployment for code updates

### 3. `huawei_remote_setup.sh`
- Run ON THE SERVER after upload
- Installs dependencies
- Sets up PostgreSQL database
- Configures Nginx
- Creates Supervisor configs
- Sets up firewall

### 4. `huawei_cloud_launch.sh`
- Starts/stops/manages services
- Multiple launch modes:
  - `manual`: Direct process launch (default)
  - `docker`: Docker Compose launch
  - `supervisor`: Supervisor managed launch
  - `stop`: Stop all services
  - `status`: Check service status
  - `logs`: View service logs

## Service Management

### Start Services
```bash
# Manual start (simple, good for testing)
./huawei_cloud_launch.sh manual

# With Supervisor (recommended for production)
./huawei_cloud_launch.sh supervisor

# With Docker
./huawei_cloud_launch.sh docker
```

### Check Status
```bash
./huawei_cloud_launch.sh status
```

### View Logs
```bash
./huawei_cloud_launch.sh logs

# Or specific logs
tail -f logs/backend.log
tail -f logs/frontend.log
```

### Stop Services
```bash
./huawei_cloud_launch.sh stop
```

## Production Configuration

### 1. SSL/HTTPS Setup
```bash
# After domain is pointed to server
sudo certbot --nginx -d yourdomain.com
```

### 2. Environment Variables
Update `/home/ubuntu/sbm_crm/backend/.env`:
```env
DATABASE_URL=postgresql://sbm_user:secure_password@localhost/sbm_crm
REDIS_URL=redis://localhost:6379
SECRET_KEY=generate-a-secure-secret-key
JWT_SECRET=generate-another-secure-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com
```

Update `/home/ubuntu/sbm_crm/frontend/.env`:
```env
VITE_API_URL=https://yourdomain.com
VITE_APP_NAME=SBM AI CRM
VITE_APP_VERSION=1.0.0
```

### 3. Database Backup
```bash
# Create backup
pg_dump sbm_crm > backup_$(date +%Y%m%d).sql

# Restore backup
psql sbm_crm < backup_20240118.sql
```

### 4. Monitoring
```bash
# Check system resources
htop

# Check service logs
sudo journalctl -u nginx -f
sudo supervisorctl tail -f sbm_backend
sudo supervisorctl tail -f sbm_frontend

# Check disk usage
df -h

# Check database connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
sudo lsof -i:8000
sudo lsof -i:4000

# Kill process
sudo fuser -k 8000/tcp
sudo fuser -k 4000/tcp
```

### Permission Issues
```bash
# Fix file permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/sbm_crm
chmod +x *.sh
```

### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check database exists
sudo -u postgres psql -l
```

### Nginx Issues
```bash
# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

## Security Recommendations

1. **Firewall Configuration**
   ```bash
   sudo ufw status
   sudo ufw allow from <your-ip> to any port 22
   sudo ufw deny 22  # Block SSH from other IPs
   ```

2. **Fail2ban Setup**
   ```bash
   sudo apt-get install fail2ban
   sudo systemctl enable fail2ban
   ```

3. **Regular Updates**
   ```bash
   sudo apt-get update && sudo apt-get upgrade
   ```

4. **Backup Strategy**
   - Daily database backups
   - Weekly full system backups
   - Store backups in Huawei OBS (Object Storage Service)

## Scaling Options

### Horizontal Scaling
1. Set up Huawei Cloud Load Balancer
2. Deploy to multiple ECS instances
3. Use Huawei RDS for PostgreSQL
4. Use Huawei DCS for Redis

### Vertical Scaling
1. Resize ECS instance through Huawei Console
2. Increase disk size as needed
3. Add more RAM for better performance

## Support

For issues or questions:
1. Check logs: `./huawei_cloud_launch.sh logs`
2. Check service status: `./huawei_cloud_launch.sh status`
3. Review Nginx logs: `sudo tail -f /var/log/nginx/error.log`
4. Check system resources: `htop`

## Quick Commands Reference

```bash
# Deploy
./huawei_cloud_deploy.sh 192.168.1.100 ubuntu /home/ubuntu/sbm_crm

# Quick sync
./huawei_ssh_upload.sh 192.168.1.100 ubuntu /home/ubuntu/sbm_crm

# SSH to server
ssh ubuntu@192.168.1.100

# On server - setup
./huawei_remote_setup.sh

# On server - launch
./huawei_cloud_launch.sh

# On server - check status
./huawei_cloud_launch.sh status

# On server - view logs
./huawei_cloud_launch.sh logs

# On server - stop services
./huawei_cloud_launch.sh stop
```