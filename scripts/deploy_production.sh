#!/bin/bash

# 🚀 GavatCore Production Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="api-gavatcore.siyahkare.com"
IMAGE_NAME="ghcr.io/gavatcore/gavatcore-api"
VERSION="latest"
DEPLOY_DIR="/opt/gavatcore"

echo -e "${BLUE}🚀 Starting GavatCore Production Deployment${NC}"
echo "===================================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ This script should not be run as root${NC}"
   exit 1
fi

# Check required tools
check_dependencies() {
    local deps=("podman" "curl" "systemctl")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            echo -e "${RED}❌ $dep is not installed${NC}"
            exit 1
        fi
    done
    echo -e "${GREEN}✅ All dependencies found${NC}"
}

# Create directories
setup_directories() {
    echo -e "${YELLOW}📁 Setting up directories...${NC}"
    
    sudo mkdir -p "$DEPLOY_DIR"/{data,logs,sessions}
    sudo chown -R $USER:$USER "$DEPLOY_DIR"
    
    # Copy quadlet service file
    mkdir -p ~/.config/containers/systemd
    cp infrastructure/quadlet/gavatcore-api.container ~/.config/containers/systemd/
    
    echo -e "${GREEN}✅ Directories created${NC}"
}

# Build and push image
build_image() {
    echo -e "${YELLOW}🏗️ Building Docker image...${NC}"
    
    cd gavatcore-api
    
    # Build image
    podman build -f Dockerfile.production -t "$IMAGE_NAME:$VERSION" .
    
    # Tag as latest
    podman tag "$IMAGE_NAME:$VERSION" "$IMAGE_NAME:latest"
    
    echo -e "${GREEN}✅ Image built successfully${NC}"
    
    # Push to registry (if configured)
    if [[ -n "$GITHUB_TOKEN" ]]; then
        echo -e "${YELLOW}📤 Pushing to registry...${NC}"
        echo "$GITHUB_TOKEN" | podman login ghcr.io -u "$GITHUB_USERNAME" --password-stdin
        podman push "$IMAGE_NAME:$VERSION"
        podman push "$IMAGE_NAME:latest"
        echo -e "${GREEN}✅ Image pushed to registry${NC}"
    else
        echo -e "${YELLOW}⚠️ GITHUB_TOKEN not set, skipping registry push${NC}"
    fi
    
    cd ..
}

# Setup environment file
setup_environment() {
    echo -e "${YELLOW}🔧 Setting up environment...${NC}"
    
    if [[ ! -f "$DEPLOY_DIR/.env" ]]; then
        echo -e "${YELLOW}📝 Creating environment file...${NC}"
        cat > "$DEPLOY_DIR/.env" << EOF
# Environment
ENVIRONMENT=production
DEBUG=false

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/gavatcore.db

# API
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=["https://$DOMAIN","https://panel-gavatcore.siyahkare.com"]

# Stripe (CHANGE THESE TO YOUR PRODUCTION KEYS)
STRIPE_SECRET_KEY=sk_live_CHANGEME
STRIPE_WEBHOOK_SECRET=whsec_CHANGEME

# OpenAI
OPENAI_API_KEY=sk-CHANGEME

# Telegram
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef123456
TELEGRAM_BOT_TOKEN=1234567890:CHANGEME

# Logging
LOG_LEVEL=INFO
EOF
        
        echo -e "${RED}⚠️ Edit $DEPLOY_DIR/.env with your production credentials!${NC}"
        echo -e "${YELLOW}⏸️ Pausing for manual editing... Press Enter when done.${NC}"
        read -r
    else
        echo -e "${GREEN}✅ Environment file already exists${NC}"
    fi
}

# Deploy service
deploy_service() {
    echo -e "${YELLOW}🔄 Deploying service...${NC}"
    
    # Reload systemd
    systemctl --user daemon-reload
    
    # Stop existing service
    systemctl --user stop gavatcore-api || true
    
    # Start service
    systemctl --user enable --now gavatcore-api
    
    # Wait for service to start
    echo -e "${YELLOW}⏳ Waiting for service to start...${NC}"
    sleep 10
    
    # Check service status
    if systemctl --user is-active --quiet gavatcore-api; then
        echo -e "${GREEN}✅ Service is running${NC}"
    else
        echo -e "${RED}❌ Service failed to start${NC}"
        systemctl --user status gavatcore-api
        exit 1
    fi
}

# Health check
health_check() {
    echo -e "${YELLOW}🏥 Performing health check...${NC}"
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -sf http://localhost:8000/health > /dev/null; then
            echo -e "${GREEN}✅ Health check passed${NC}"
            
            # Show API info
            echo -e "${BLUE}📊 API Information:${NC}"
            curl -s http://localhost:8000/health | jq .
            
            return 0
        fi
        
        echo -e "${YELLOW}⏳ Attempt $attempt/$max_attempts failed, retrying...${NC}"
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}❌ Health check failed after $max_attempts attempts${NC}"
    return 1
}

# Setup SSL and domain
setup_domain() {
    echo -e "${YELLOW}🌐 Domain setup instructions:${NC}"
    echo "============================================="
    echo "1. Add DNS record in Cloudflare:"
    echo "   Type: A"
    echo "   Name: api-gavatcore"
    echo "   Content: $(curl -s ifconfig.me)"
    echo "   Proxy: ON (orange cloud)"
    echo ""
    echo "2. SSL will be handled by Cloudflare automatically"
    echo ""
    echo "3. Test your API:"
    echo "   https://$DOMAIN/health"
    echo ""
}

# Main deployment function
main() {
    echo -e "${BLUE}Starting deployment process...${NC}"
    
    check_dependencies
    setup_directories
    build_image
    setup_environment
    deploy_service
    
    if health_check; then
        setup_domain
        echo ""
        echo -e "${GREEN}🎉 Deployment successful!${NC}"
        echo -e "${GREEN}🔗 API URL: https://$DOMAIN${NC}"
        echo -e "${GREEN}📚 API Docs: https://$DOMAIN/docs${NC}"
        echo -e "${GREEN}🏥 Health: https://$DOMAIN/health${NC}"
        echo ""
        echo -e "${YELLOW}🔧 Next steps:${NC}"
        echo "1. Update DNS records in Cloudflare"
        echo "2. Test Stripe webhooks"
        echo "3. Deploy frontend to Vercel"
        echo "4. Setup Telegram bot"
    else
        echo -e "${RED}❌ Deployment failed during health check${NC}"
        exit 1
    fi
}

# Run main function
main "$@" 