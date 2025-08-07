#!/bin/bash

# Install both Docker Compose v1 and v2 for Huawei Cloud server
# This ensures maximum compatibility

echo "🚀 Installing Docker Compose (both v1 and v2)..."
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        SUDO=""
    else
        SUDO="sudo"
    fi
}

check_root

# Step 1: Install Docker Compose v1 (standalone binary)
echo -e "\n${BLUE}Step 1: Installing Docker Compose v1 (standalone)${NC}"
echo "================================================"

# Get latest version number
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
echo -e "${YELLOW}Latest Docker Compose version: ${COMPOSE_VERSION}${NC}"

# Download from GitHub (with fallback to Chinese mirror if GitHub fails)
echo "Downloading Docker Compose v1..."
if ! $SUDO curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose 2>/dev/null; then
    echo -e "${YELLOW}GitHub download failed, trying Chinese mirror...${NC}"
    $SUDO curl -L "https://get.daocloud.io/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
fi

# Make executable
$SUDO chmod +x /usr/local/bin/docker-compose

# Create symlink for system-wide access
$SUDO ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# Verify v1 installation
if docker-compose --version 2>/dev/null; then
    echo -e "${GREEN}✅ Docker Compose v1 installed successfully${NC}"
    docker-compose --version
else
    echo -e "${RED}❌ Docker Compose v1 installation failed${NC}"
fi

# Step 2: Install Docker Compose v2 (Docker plugin)
echo -e "\n${BLUE}Step 2: Installing Docker Compose v2 (Docker plugin)${NC}"
echo "===================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Installing Docker first...${NC}"
    
    # Install Docker
    echo "Installing Docker..."
    $SUDO apt-get update
    $SUDO apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    $SUDO mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | $SUDO gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Set up repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | $SUDO tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    $SUDO apt-get update
    $SUDO apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Add current user to docker group
    $SUDO usermod -aG docker $USER
    
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${GREEN}Docker is already installed${NC}"
    
    # Install just the compose plugin
    echo "Installing Docker Compose plugin..."
    
    # Create plugin directory
    DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
    mkdir -p $DOCKER_CONFIG/cli-plugins
    
    # Download compose v2 plugin
    echo "Downloading Docker Compose v2 plugin..."
    COMPOSE_V2_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    
    if ! curl -SL "https://github.com/docker/compose/releases/download/${COMPOSE_V2_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o $DOCKER_CONFIG/cli-plugins/docker-compose 2>/dev/null; then
        echo -e "${YELLOW}GitHub download failed, trying alternative method...${NC}"
        $SUDO apt-get update
        $SUDO apt-get install -y docker-compose-plugin
    else
        chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
    fi
fi

# Verify v2 installation
if docker compose version 2>/dev/null; then
    echo -e "${GREEN}✅ Docker Compose v2 installed successfully${NC}"
    docker compose version
else
    echo -e "${YELLOW}⚠️  Docker Compose v2 not available as 'docker compose'${NC}"
fi

# Step 3: Create convenience script
echo -e "\n${BLUE}Step 3: Creating convenience script${NC}"
echo "======================================="

cat > /tmp/dc << 'EOF'
#!/bin/bash
# Convenience wrapper for docker-compose commands
# Automatically uses the China-optimized compose file

COMPOSE_FILE="docker-compose.china.yml"

# Check if China compose file exists
if [ -f "$COMPOSE_FILE" ]; then
    # Try docker compose v2 first
    if docker compose version &>/dev/null; then
        docker compose -f $COMPOSE_FILE "$@"
    # Fall back to docker-compose v1
    elif docker-compose --version &>/dev/null; then
        docker-compose -f $COMPOSE_FILE "$@"
    else
        echo "Error: Docker Compose not found"
        exit 1
    fi
else
    # Use default behavior if no China file
    if docker compose version &>/dev/null; then
        docker compose "$@"
    elif docker-compose --version &>/dev/null; then
        docker-compose "$@"
    else
        echo "Error: Docker Compose not found"
        exit 1
    fi
fi
EOF

$SUDO mv /tmp/dc /usr/local/bin/dc
$SUDO chmod +x /usr/local/bin/dc

echo -e "${GREEN}✅ Convenience script created at /usr/local/bin/dc${NC}"

# Final verification
echo -e "\n${BLUE}Installation Summary${NC}"
echo "===================="

echo -e "\n${YELLOW}Available commands:${NC}"

# Check docker-compose (v1)
if command -v docker-compose &> /dev/null; then
    echo -e "  ${GREEN}✅${NC} docker-compose (v1): $(docker-compose --version 2>/dev/null)"
fi

# Check docker compose (v2)
if docker compose version &> /dev/null 2>&1; then
    echo -e "  ${GREEN}✅${NC} docker compose (v2): $(docker compose version 2>/dev/null)"
fi

# Check dc convenience script
if command -v dc &> /dev/null; then
    echo -e "  ${GREEN}✅${NC} dc (convenience): Uses China-optimized config automatically"
fi

echo -e "\n${GREEN}Installation complete!${NC}"
echo ""
echo "You can now use any of these commands:"
echo -e "  ${BLUE}docker-compose -f docker-compose.china.yml up -d${NC}  # Using v1"
echo -e "  ${BLUE}docker compose -f docker-compose.china.yml up -d${NC}  # Using v2"
echo -e "  ${BLUE}dc up -d${NC}                                         # Using convenience script"
echo ""
echo -e "${YELLOW}Note: You may need to log out and back in for Docker group changes to take effect${NC}"