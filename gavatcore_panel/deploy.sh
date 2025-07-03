#!/bin/bash

# 🚀 GavatCore Panel Deployment Script
echo "🚀 Starting GavatCore Panel deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL=${API_BASE_URL:-"https://api.gavatcore.com"}
WS_URL=${WS_URL:-"wss://api.gavatcore.com/ws"}
ENVIRONMENT=${ENVIRONMENT:-"production"}
USE_MOCK_DATA=${USE_MOCK_DATA:-"false"}

echo -e "${BLUE}Configuration:${NC}"
echo -e "  API Base URL: ${YELLOW}$API_BASE_URL${NC}"
echo -e "  WebSocket URL: ${YELLOW}$WS_URL${NC}"
echo -e "  Environment: ${YELLOW}$ENVIRONMENT${NC}"
echo -e "  Use Mock Data: ${YELLOW}$USE_MOCK_DATA${NC}"
echo ""

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo -e "${RED}❌ Flutter is not installed or not in PATH${NC}"
    echo -e "${YELLOW}💡 Please install Flutter: https://flutter.dev/docs/get-started/install${NC}"
    exit 1
fi

# Check Flutter version
echo -e "${BLUE}🐦 Checking Flutter version...${NC}"
flutter --version

# Clean and get dependencies
echo -e "${BLUE}📋 Getting dependencies...${NC}"
flutter clean
flutter pub get

# Generate code
echo -e "${BLUE}🔧 Generating code...${NC}"
dart run build_runner build --delete-conflicting-outputs

# Run tests (optional)
if [ "$1" != "--skip-tests" ]; then
    echo -e "${BLUE}🧪 Running tests...${NC}"
    flutter test
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Tests failed! Use --skip-tests to skip tests.${NC}"
        exit 1
    fi
fi

# Build web app
echo -e "${BLUE}🏗️ Building web app...${NC}"
flutter build web \
    --release \
    --web-renderer canvaskit \
    --dart-define=API_BASE_URL="$API_BASE_URL" \
    --dart-define=WS_URL="$WS_URL" \
    --dart-define=USE_MOCK_DATA="$USE_MOCK_DATA" \
    --dart-define=ENVIRONMENT="$ENVIRONMENT" \
    --dart-define=DEBUG_API=false

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

# Create deployment info
echo -e "${BLUE}📁 Creating deployment package...${NC}"
cd build/web

# Create CNAME for custom domain (GitHub Pages)
echo "panel.gavatcore.com" > CNAME

# Create deployment info file
cat > deployment_info.txt << EOF
# GavatCore Panel Deployment
Build Date: $(date)
Git Commit: $(git rev-parse HEAD 2>/dev/null || echo "unknown")
Git Branch: $(git branch --show-current 2>/dev/null || echo "unknown")
API Base URL: $API_BASE_URL
WebSocket URL: $WS_URL
Environment: $ENVIRONMENT
Use Mock Data: $USE_MOCK_DATA
EOF

cd ../..

echo -e "${GREEN}✅ Build completed successfully!${NC}"
echo -e "${YELLOW}📁 Build output is in: build/web${NC}"

# Deployment options
echo ""
echo -e "${BLUE}🌐 Deployment Options:${NC}"
echo ""
echo -e "${YELLOW}1. GitHub Pages:${NC}"
echo "   git add build/web"
echo "   git commit -m 'Deploy: $(date)'"
echo "   git subtree push --prefix build/web origin gh-pages"
echo ""
echo -e "${YELLOW}2. Firebase Hosting:${NC}"
echo "   firebase deploy --only hosting"
echo ""
echo -e "${YELLOW}3. Cloudflare Pages:${NC}"
echo "   wrangler pages publish build/web"
echo ""
echo -e "${YELLOW}4. Netlify:${NC}"
echo "   netlify deploy --prod --dir=build/web"
echo ""
echo -e "${YELLOW}5. Simple HTTP Server (for testing):${NC}"
echo "   cd build/web && python3 -m http.server 8080"

# Auto-deploy options
echo ""
echo -e "${BLUE}🤖 Auto-deploy?${NC}"
read -p "Deploy to GitHub Pages? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🚀 Deploying to GitHub Pages...${NC}"
    
    # Check if gh-pages branch exists
    if git show-ref --verify --quiet refs/heads/gh-pages; then
        echo -e "${YELLOW}📁 Updating gh-pages branch...${NC}"
        git subtree push --prefix build/web origin gh-pages
    else
        echo -e "${YELLOW}📁 Creating gh-pages branch...${NC}"
        git subtree push --prefix build/web origin gh-pages
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Deployed successfully to GitHub Pages!${NC}"
        echo -e "${YELLOW}🌐 Your site will be available at: https://panel.gavatcore.com${NC}"
    else
        echo -e "${RED}❌ Deployment failed!${NC}"
    fi
fi

echo ""
echo -e "${GREEN}🎉 Deployment script completed!${NC}" 