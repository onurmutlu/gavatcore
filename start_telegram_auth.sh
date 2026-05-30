#!/bin/bash

# GavatCore Telegram Authentication System Startup
echo "🚀 Starting GavatCore Telegram Authentication System..."

# Change to the project directory
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_success() {
    echo -e "${PURPLE}[SUCCESS]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Kill any existing processes
print_status "Stopping existing services..."
pkill -f "telegram_auth_api.py" 2>/dev/null
pkill -f "flutter run" 2>/dev/null
sleep 2

print_header "========================================="
print_header "🔥 TELEGRAM AUTH SYSTEM STARTUP 🔥"
print_header "========================================="

# Step 1: Start Telegram Auth API
print_status "Starting Telegram Authentication API server..."

if [ ! -d "gavatcore_panel/auth_api_venv" ]; then
    print_status "Creating virtual environment for Auth API..."
    python3 -m venv gavatcore_panel/auth_api_venv
    source gavatcore_panel/auth_api_venv/bin/activate
    pip install flask flask-cors telethon python-dotenv cryptography
else
    source gavatcore_panel/auth_api_venv/bin/activate
fi

# Create logs directory
mkdir -p logs

# Start Auth API in background
nohup python3 apis/telegram_auth_api.py > logs/auth_api.log 2>&1 &
AUTH_API_PID=$!
print_success "Auth API started (PID: $AUTH_API_PID)"

# Wait for API to start
sleep 4

# Test API
if curl -s http://localhost:5050/api/system/status >/dev/null 2>&1; then
    print_success "✅ Telegram Auth API is running on http://localhost:5050"
else
    echo "❌ Failed to start Telegram Auth API"
    cat logs/auth_api.log
    exit 1
fi

# Step 2: Build and Start Flutter Panel  
print_status "Starting Flutter web application..."
cd gavatcore_panel

# Install Flutter dependencies if needed
if [ ! -d ".dart_tool" ]; then
    print_status "Installing Flutter dependencies..."
    flutter pub get
fi

# Start Flutter Web App (without build_runner)
print_status "Starting Flutter web panel..."
nohup flutter run -d chrome --web-port=3000 > ../logs/flutter_web.log 2>&1 &
FLUTTER_PID=$!

cd ..

print_success "Flutter panel started (PID: $FLUTTER_PID)"

# Wait for Flutter to start
sleep 8

print_header "========================================="
print_header "✅ TELEGRAM AUTH SYSTEM READY!"
print_header "========================================="

print_success "🌐 Services Running:"
print_success "  ├─ Telegram Auth API: http://localhost:5050"
print_success "  └─ Flutter Web Panel: http://localhost:3000"
print_success ""
print_success "📱 Ready for Authentication:"
print_success "  ├─ Phone number authentication"
print_success "  ├─ SMS verification"
print_success "  ├─ 2FA support"
print_success "  └─ Message sending"
print_success ""
print_success "📋 API Endpoints:"
print_success "  ├─ POST /api/telegram/send-code - Send verification code"
print_success "  ├─ POST /api/telegram/verify-code - Verify SMS code"
print_success "  ├─ POST /api/telegram/verify-2fa - Verify 2FA password"
print_success "  ├─ POST /api/telegram/send-message - Send messages"
print_success "  ├─ GET  /api/telegram/messages - Get message history"
print_success "  ├─ GET  /api/telegram/chats - Get chat list"
print_success "  └─ GET  /api/system/status - System status"
print_success ""
print_success "📂 Log Files:"
print_success "  ├─ Auth API: logs/auth_api.log"
print_success "  └─ Flutter Panel: logs/flutter_web.log"

# Store PIDs for cleanup
echo "$AUTH_API_PID" > .auth_api_pid
echo "$FLUTTER_PID" > .flutter_pid

print_header "========================================="
print_header "🎯 READY FOR TELEGRAM AUTHENTICATION!"
print_header "========================================="

print_success "🎉 Quick Start Guide:"
print_success "1. 🌐 Open http://localhost:3000 in your browser"
print_success "2. 📱 Enter your phone number (with country code)"
print_success "3. ✅ Enter SMS verification code from Telegram"
print_success "4. 🔐 Enter 2FA password if enabled"
print_success "5. 💬 Start sending messages through the panel!"
print_success ""
print_success "🛑 To stop services: ./stop_telegram_auth.sh"

# Monitor services
print_status "System is ready! Press Ctrl+C to stop monitoring..."
trap 'echo "Stopping services..."; kill $AUTH_API_PID $FLUTTER_PID 2>/dev/null; exit 0' INT

while true; do
    sleep 10
    
    # Check if services are still running
    if ! kill -0 $AUTH_API_PID 2>/dev/null; then
        echo "❌ Auth API has stopped!"
        break
    fi
    
    if ! kill -0 $FLUTTER_PID 2>/dev/null; then
        echo "❌ Flutter panel has stopped!"
        break
    fi
done