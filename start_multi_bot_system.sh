#!/bin/bash

# GavatCore Multi-Bot Authentication System Startup Script
echo "🚀 Starting GavatCore Multi-Bot Authentication System..."

cd "$(dirname "$0")"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

print_header "========================================="
print_header "🤖 GAVATCORE MULTI-BOT SYSTEM STARTUP 🤖"
print_header "========================================="

# Stop existing processes
print_info "Stopping existing services..."
pkill -f telegram_auth_api 2>/dev/null
pkill -f flutter 2>/dev/null
sleep 2

# Start API Server
print_info "Starting Multi-Bot API Server..."
python3 apis/telegram_auth_api_minimal.py &
API_PID=$!
sleep 3

# Test API
if curl -s http://localhost:5050/api/system/status > /dev/null; then
    print_success "✅ API Server running on http://localhost:5050"
else
    echo "❌ API Server failed to start"
    exit 1
fi

# Start Flutter Web App
print_info "Starting Flutter Web Panel..."
cd gavatcore_panel
flutter run -d chrome --web-port 3000 &
FLUTTER_PID=$!
cd ..
sleep 5

# Test Flutter
if curl -s http://localhost:3000 > /dev/null; then
    print_success "✅ Flutter Panel running on http://localhost:3000"
else
    echo "❌ Flutter Panel failed to start"
    exit 1
fi

print_header "========================================="
print_header "✅ MULTI-BOT SYSTEM READY!"
print_header "========================================="

print_success "🌐 Services Running:"
print_success "   ├─ API Server: http://localhost:5050"
print_success "   └─ Web Panel: http://localhost:3000"

print_success "🤖 Available Bots:"
print_success "   ├─ Lara - Flirty Streamer (+905382617727)"
print_success "   ├─ BabaGavat - Club Leader (+447832134241)"
print_success "   └─ Geisha - Sophisticated Moderator (+905486306226)"

print_success "📱 How to Use:"
print_success "   1. Open http://localhost:3000 in your browser"
print_success "   2. Select a bot from the dropdown"
print_success "   3. Click 'Send Code' to authenticate"
print_success "   4. Enter SMS verification code"
print_success "   5. Start messaging through your bot!"

print_success "🛑 To stop: pkill -f telegram_auth && pkill -f flutter"

echo ""
print_header "🎉 READY FOR MULTI-BOT AUTHENTICATION!"
print_header "========================================="

# Keep script running to monitor
echo "Press Ctrl+C to stop all services..."
trap 'echo "Stopping services..."; kill $API_PID $FLUTTER_PID 2>/dev/null; exit' INT
wait