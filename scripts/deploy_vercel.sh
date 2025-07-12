#!/bin/bash

# 🚀 Vercel Deployment Script for GavatCore Panel

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploying GavatCore Panel to Vercel${NC}"
echo "============================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}❌ Vercel CLI is not installed${NC}"
    echo -e "${YELLOW}💡 Install with: npm i -g vercel${NC}"
    exit 1
fi

# Check if we're logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo -e "${YELLOW}🔐 Logging into Vercel...${NC}"
    vercel login
fi

# Build Flutter web app
echo -e "${YELLOW}📱 Building Flutter web app...${NC}"
./scripts/build_flutter_web.sh

# Change to Flutter project directory
cd gavatcore_panel

# Copy build files to deployment directory
echo -e "${YELLOW}📦 Preparing deployment files...${NC}"
rm -rf deploy_web
mkdir -p deploy_web
cp -r build/web/* deploy_web/
cp vercel.json deploy_web/

# Deploy to Vercel
echo -e "${YELLOW}🚀 Deploying to Vercel...${NC}"
cd deploy_web

# Deploy with custom settings
vercel --prod \
    --name "gavatcore-panel" \
    --regions "iad1" \
    --build-env FLUTTER_WEB=true \
    --yes

# Get deployment URL
DEPLOYMENT_URL=$(vercel --prod --yes | grep -o 'https://[^[:space:]]*' | tail -1)

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}🔗 Production URL: $DEPLOYMENT_URL${NC}"
echo ""

# Setup custom domain instructions
echo -e "${YELLOW}🌐 Custom Domain Setup:${NC}"
echo "============================================="
echo "1. Add custom domain in Vercel dashboard:"
echo "   Domain: panel-gavatcore.siyahkare.com"
echo ""
echo "2. Add DNS record in Cloudflare:"
echo "   Type: CNAME"
echo "   Name: panel-gavatcore"
echo "   Content: cname.vercel-dns.com"
echo "   Proxy: ON (orange cloud)"
echo ""
echo "3. Verify SSL certificate:"
echo "   https://panel-gavatcore.siyahkare.com"
echo ""

# Test deployment
echo -e "${YELLOW}🧪 Testing deployment...${NC}"
if curl -f "$DEPLOYMENT_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Deployment is live and responding${NC}"
else
    echo -e "${RED}❌ Deployment test failed${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Flutter panel deployed successfully!${NC}"
echo -e "${BLUE}📱 Panel URL: $DEPLOYMENT_URL${NC}"
echo -e "${BLUE}🔗 Custom Domain: https://panel-gavatcore.siyahkare.com${NC}"

cd ../.. 