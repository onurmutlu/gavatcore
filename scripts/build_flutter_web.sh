#!/bin/bash

# 📱 Flutter Web Build Script for Production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📱 Building Flutter Web App for Production${NC}"
echo "=================================================="

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo -e "${RED}❌ Flutter is not installed${NC}"
    echo -e "${YELLOW}💡 Install Flutter from: https://docs.flutter.dev/get-started/install${NC}"
    exit 1
fi

# Change to Flutter project directory
cd gavatcore_panel

echo -e "${YELLOW}🔧 Cleaning previous builds...${NC}"
flutter clean

echo -e "${YELLOW}📦 Getting dependencies...${NC}"
flutter pub get

echo -e "${YELLOW}🏗️ Building for web...${NC}"
flutter build web --release --web-renderer html --base-href "/"

# Optimize web build
echo -e "${YELLOW}⚡ Optimizing web build...${NC}"

# Create optimized index.html
cat > web/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <!--
    If you are serving your web app in a path other than the root, change the
    href value below to reflect the base path you are serving from.

    The path provided below has to start and end with a slash "/" in order for
    it to work correctly.

    For more details:
    * https://developer.mozilla.org/en-US/docs/Web/HTML/Element/base

    This is a placeholder for base href that will be replaced by the value of
    the `--base-href` argument provided to `flutter build`.
  -->
  <base href="/">

  <meta charset="UTF-8">
  <meta content="IE=Edge" http-equiv="X-UA-Compatible">
  <meta name="description" content="GavatCore SaaS - GPT ile çalışan akıllı Telegram botları">
  <meta name="keywords" content="telegram bot, gpt, ai, saas, automation">
  
  <!-- iOS meta tags & icons -->
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black">
  <meta name="apple-mobile-web-app-title" content="GavatCore">
  <link rel="apple-touch-icon" href="icons/Icon-192.png">

  <!-- Favicon -->
  <link rel="icon" type="image/png" href="favicon.png"/>

  <title>🚀 GavatCore SaaS Panel</title>
  <link rel="manifest" href="manifest.json">

  <style>
    body {
      margin: 0;
      padding: 0;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      color: white;
    }
    
    .loading {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      flex-direction: column;
    }
    
    .loading-spinner {
      width: 50px;
      height: 50px;
      border: 3px solid rgba(255,255,255,0.3);
      border-radius: 50%;
      border-top-color: #fff;
      animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    
    .loading-text {
      margin-top: 20px;
      font-size: 18px;
      opacity: 0.8;
    }
  </style>
</head>
<body>
  <div id="loading" class="loading">
    <div class="loading-spinner"></div>
    <div class="loading-text">🚀 GavatCore yükleniyor...</div>
  </div>

  <script>
    window.addEventListener('flutter-first-frame', function () {
      const loading = document.getElementById('loading');
      if (loading) {
        loading.style.display = 'none';
      }
    });
    
    // Service Worker registration
    if ('serviceWorker' in navigator) {
      window.addEventListener('flutter-first-frame', function () {
        navigator.serviceWorker.register('flutter_service_worker.js');
      });
    }
  </script>
  
  <script src="main.dart.js" type="application/javascript"></script>
</body>
</html>
EOF

# Update manifest.json for production
cat > web/manifest.json << 'EOF'
{
    "name": "GavatCore SaaS Panel",
    "short_name": "GavatCore",
    "start_url": ".",
    "display": "standalone",
    "background_color": "#667eea",
    "theme_color": "#764ba2",
    "description": "GPT ile çalışan akıllı Telegram botları",
    "orientation": "portrait-primary",
    "prefer_related_applications": false,
    "icons": [
        {
            "src": "icons/Icon-192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "icons/Icon-512.png",
            "sizes": "512x512",
            "type": "image/png"
        },
        {
            "src": "icons/Icon-maskable-192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "maskable"
        },
        {
            "src": "icons/Icon-maskable-512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "maskable"
        }
    ]
}
EOF

echo -e "${GREEN}✅ Flutter web build completed successfully!${NC}"
echo -e "${BLUE}📁 Output directory: gavatcore_panel/build/web${NC}"

# Check build size
BUILD_SIZE=$(du -sh build/web | cut -f1)
echo -e "${YELLOW}📊 Build size: $BUILD_SIZE${NC}"

echo -e "${GREEN}🚀 Ready for deployment!${NC}"
echo ""
echo -e "${YELLOW}🔧 Next steps:${NC}"
echo "1. Deploy to Vercel: vercel --prod"
echo "2. Update API URLs in production"
echo "3. Setup custom domain"
echo ""

cd .. 