#!/bin/bash

# 🎨 GavatCore Panel - Demo Environment Setup
echo "🎨 Setting up GavatCore Panel Demo Environment..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}
  ██████╗  █████╗ ██╗   ██╗ █████╗ ████████╗ ██████╗ ██████╗ ██████╗ ███████╗
  ██╔══██╗██╔══██╗██║   ██║██╔══██╗╚══██╔══╝██╔════╝██╔═══██╗██╔══██╗██╔════╝
  ██║  ██║███████║██║   ██║███████║   ██║   ██║     ██║   ██║██████╔╝█████╗  
  ██║  ██║██╔══██║╚██╗ ██╔╝██╔══██║   ██║   ██║     ██║   ██║██╔══██╗██╔══╝  
  ██████╔╝██║  ██║ ╚████╔╝ ██║  ██║   ██║   ╚██████╗╚██████╔╝██║  ██║███████╗
  ╚═════╝ ╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
                                                                               
                               🚀 DEMO PANEL 🚀
${NC}"

# Demo configuration
DEMO_API_URL="https://demo-api.gavatcore.com"
DEMO_WS_URL="wss://demo-api.gavatcore.com/ws"
DEMO_USER="demo@gavatcore.com"
DEMO_PASS="supergavat123"

echo -e "${BLUE}🎯 Demo Configuration:${NC}"
echo -e "  API URL: ${YELLOW}$DEMO_API_URL${NC}"
echo -e "  WebSocket: ${YELLOW}$DEMO_WS_URL${NC}"
echo -e "  Demo User: ${YELLOW}$DEMO_USER${NC}"
echo -e "  Demo Pass: ${YELLOW}$DEMO_PASS${NC}"
echo -e "  Mock Data: ${GREEN}ENABLED${NC}"
echo ""

# Clean and setup
echo -e "${BLUE}🧹 Cleaning project...${NC}"
flutter clean
flutter pub get

echo -e "${BLUE}🔧 Generating demo code...${NC}"
dart run build_runner build --delete-conflicting-outputs

# Create demo config file
cat > lib/config/demo_config.dart << EOF
// 🎨 GavatCore Panel - Demo Configuration
class DemoConfig {
  static const String demoUser = '$DEMO_USER';
  static const String demoPassword = '$DEMO_PASS';
  static const bool isDemoMode = true;
  
  static const Map<String, dynamic> demoData = {
    'features': [
      '🚀 Real-time Dashboard',
      '💬 Advanced Message Management', 
      '🧠 AI Prompt Blending',
      '⏰ Smart Scheduling',
      '📊 Analytics & Insights',
      '🔒 Admin Override Panel',
    ],
    'stats': {
      'totalUsers': 15847,
      'activeProjects': 342,
      'successRate': 94.8,
    }
  };
}
EOF

# Build demo version
echo -e "${BLUE}🏗️ Building demo version...${NC}"
flutter build web \
    --release \
    --web-renderer canvaskit \
    --dart-define=API_BASE_URL="$DEMO_API_URL" \
    --dart-define=WS_URL="$DEMO_WS_URL" \
    --dart-define=USE_MOCK_DATA=true \
    --dart-define=ENVIRONMENT=demo \
    --dart-define=DEBUG_API=true

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Demo build failed!${NC}"
    exit 1
fi

# Create demo landing page
cd build/web

cat > demo.html << EOF
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GavatCore Panel - Live Demo</title>
    <style>
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 40px;
            min-height: 100vh;
        }
        .demo-container {
            max-width: 1200px;
            margin: 0 auto;
            text-align: center;
        }
        .demo-header {
            margin-bottom: 40px;
        }
        .demo-title {
            font-size: 3em;
            margin-bottom: 20px;
            text-shadow: 0 0 20px rgba(255,255,255,0.5);
        }
        .demo-subtitle {
            font-size: 1.2em;
            opacity: 0.9;
            margin-bottom: 30px;
        }
        .demo-button {
            display: inline-block;
            padding: 15px 30px;
            background: linear-gradient(45deg, #9C27B0, #E91E63);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.1em;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
            margin: 10px;
        }
        .demo-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        }
        .demo-features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }
        .feature-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .demo-credentials {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 20px;
            margin: 30px auto;
            max-width: 400px;
        }
        .pulse {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="demo-container">
        <div class="demo-header">
            <h1 class="demo-title pulse">🚀 GavatCore Panel</h1>
            <p class="demo-subtitle">Production-Ready Admin Panel with Neon Glassmorphic Design</p>
            
            <a href="./index.html" class="demo-button">
                🎯 Launch Demo Panel
            </a>
            
            <a href="https://github.com/gavatcore/panel" class="demo-button">
                📱 View Source Code
            </a>
        </div>

        <div class="demo-credentials">
            <h3>🔑 Demo Credentials</h3>
            <p><strong>Email:</strong> $DEMO_USER</p>
            <p><strong>Password:</strong> $DEMO_PASS</p>
            <p><em>Full access to all features</em></p>
        </div>

        <div class="demo-features">
            <div class="feature-card">
                <h3>📊 Real-time Dashboard</h3>
                <p>Live statistics, interactive charts, system monitoring</p>
            </div>
            <div class="feature-card">
                <h3>💬 Message Management</h3>
                <p>Advanced filtering, bulk operations, AI enhancement</p>
            </div>
            <div class="feature-card">
                <h3>🧠 AI Prompt Blending</h3>
                <p>GPT-4o integration, prompt templates, cost control</p>
            </div>
            <div class="feature-card">
                <h3>⚙️ Admin Controls</h3>
                <p>System management, bot controls, fail-safe features</p>
            </div>
            <div class="feature-card">
                <h3>🎨 Glassmorphic UI</h3>
                <p>Neon design, smooth animations, responsive layout</p>
            </div>
            <div class="feature-card">
                <h3>🚀 Production Ready</h3>
                <p>Flutter web, state management, API integration</p>
            </div>
        </div>

        <div style="margin-top: 40px; opacity: 0.8;">
            <p>Built with Flutter 💙 | Powered by Riverpod 🎯 | Designed with ❤️</p>
            <p><em>This is a live demo with mock data - No real data is modified</em></p>
        </div>
    </div>

    <script>
        // Add some sparkle effects
        function createSparkle() {
            const sparkle = document.createElement('div');
            sparkle.style.position = 'fixed';
            sparkle.style.width = '4px';
            sparkle.style.height = '4px';
            sparkle.style.background = 'white';
            sparkle.style.borderRadius = '50%';
            sparkle.style.pointerEvents = 'none';
            sparkle.style.left = Math.random() * window.innerWidth + 'px';
            sparkle.style.top = Math.random() * window.innerHeight + 'px';
            sparkle.style.animation = 'sparkle 2s linear infinite';
            document.body.appendChild(sparkle);
            
            setTimeout(() => sparkle.remove(), 2000);
        }
        
        setInterval(createSparkle, 300);
        
        // Add sparkle animation
        const style = document.createElement('style');
        style.textContent = \`
            @keyframes sparkle {
                0% { opacity: 0; transform: scale(0) rotate(0deg); }
                50% { opacity: 1; transform: scale(1) rotate(180deg); }
                100% { opacity: 0; transform: scale(0) rotate(360deg); }
            }
        \`;
        document.head.appendChild(style);
    </script>
</body>
</html>
EOF

# Update index.html to add demo info
sed -i '' 's/<title>gavatcore_panel<\/title>/<title>GavatCore Panel - Live Demo<\/title>/' index.html

# Create demo info file
cat > demo_info.json << EOF
{
  "title": "GavatCore Panel - Live Demo",
  "version": "1.0.0-demo",
  "build_date": "$(date)",
  "features": [
    "Real-time Dashboard",
    "Message Pool Management",
    "AI Prompt Blending",
    "Scheduler Configuration",
    "Admin Panel",
    "Glassmorphic Design"
  ],
  "demo_credentials": {
    "email": "$DEMO_USER",
    "password": "$DEMO_PASS"
  },
  "mock_data": true,
  "api_endpoints": {
    "base": "$DEMO_API_URL",
    "websocket": "$DEMO_WS_URL"
  }
}
EOF

cd ../..

echo -e "${GREEN}✅ Demo build completed!${NC}"
echo ""
echo -e "${PURPLE}🎨 GavatCore Panel Demo Ready!${NC}"
echo ""
echo -e "${YELLOW}📁 Demo files created:${NC}"
echo -e "  • build/web/demo.html - Demo landing page"
echo -e "  • build/web/index.html - Main panel application"
echo -e "  • build/web/demo_info.json - Demo configuration"
echo ""
echo -e "${BLUE}🌐 Deployment options:${NC}"
echo -e "  1. Local testing: ${GREEN}cd build/web && python3 -m http.server 8080${NC}"
echo -e "  2. GitHub Pages: ${GREEN}git subtree push --prefix build/web origin gh-pages${NC}"
echo -e "  3. Netlify: ${GREEN}netlify deploy --prod --dir=build/web${NC}"
echo -e "  4. Vercel: ${GREEN}vercel --prod build/web${NC}"
echo ""
echo -e "${YELLOW}🔑 Demo Access:${NC}"
echo -e "  URL: ${GREEN}https://panel.gavatcore.com/demo.html${NC}"
echo -e "  User: ${GREEN}$DEMO_USER${NC}"
echo -e "  Pass: ${GREEN}$DEMO_PASS${NC}"
echo ""
echo -e "${PURPLE}🎉 Ready to showcase! The panel looks absolutely stunning! 🔥${NC}" 