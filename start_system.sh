#!/bin/bash

# GavatCore Complete System Startup Script
echo "🚀 Starting GavatCore Complete System..."

# Change to the project directory
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Kill any existing processes
print_status "Stopping existing services..."
pkill -f "telegram_auth_api.py" 2>/dev/null
pkill -f "flutter run" 2>/dev/null
sleep 2

# Check if .env exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    exit 1
fi

print_header "=================================="
print_header "🔥 GAVATCORE SYSTEM STARTUP 🔥"
print_header "=================================="

# Step 1: Start Telegram Auth API
print_status "Starting Telegram Auth API server..."

if [ ! -d "gavatcore_panel/auth_api_venv" ]; then
    print_warning "Creating virtual environment..."
    python3 -m venv gavatcore_panel/auth_api_venv
    source gavatcore_panel/auth_api_venv/bin/activate
    pip install flask flask-cors telethon python-dotenv cryptography
else
    source gavatcore_panel/auth_api_venv/bin/activate
fi

# Start Auth API in background
nohup python3 apis/telegram_auth_api.py > auth_api.log 2>&1 &
AUTH_API_PID=$!
print_status "Auth API started (PID: $AUTH_API_PID) - Logs: auth_api.log"

# Wait for API to start
sleep 3

# Test API
if curl -s http://localhost:5050/api/system/status >/dev/null; then
    print_status "✅ Telegram Auth API is running on http://localhost:5050"
else
    print_error "❌ Failed to start Telegram Auth API"
    exit 1
fi

# Step 2: Build Flutter app
print_status "Building Flutter web app..."
cd gavatcore_panel

# Install Flutter dependencies if needed
if [ ! -d ".dart_tool" ]; then
    print_warning "Installing Flutter dependencies..."
    flutter pub get
fi

# Generate code
print_status "Generating Flutter code..."
flutter pub run build_runner build --delete-conflicting-outputs

# Step 3: Start Flutter Web App
print_status "Starting Flutter web application..."
nohup flutter run -d chrome --web-port=3000 > ../flutter_web.log 2>&1 &
FLUTTER_PID=$!

cd ..

print_status "Flutter app started (PID: $FLUTTER_PID) - Logs: flutter_web.log"

# Wait for Flutter to start
sleep 8

print_header "=================================="
print_header "✅ SYSTEM STARTUP COMPLETE!"
print_header "=================================="

print_status "🌐 Services Running:"
print_status "  - Telegram Auth API: http://localhost:5050"
print_status "  - Flutter Web Panel: http://localhost:3000"
print_status ""
print_status "📋 Available API Endpoints:"
print_status "  POST /api/telegram/send-code - Send verification code"
print_status "  POST /api/telegram/verify-code - Verify SMS code"
print_status "  POST /api/telegram/verify-2fa - Verify 2FA password"
print_status "  POST /api/telegram/send-message - Send messages"
print_status "  GET  /api/telegram/messages - Get message history"
print_status "  GET  /api/telegram/chats - Get chat list"
print_status "  GET  /api/system/status - System status"
print_status ""
print_status "📂 Log Files:"
print_status "  - API Logs: auth_api.log"
print_status "  - Flutter Logs: flutter_web.log"
print_status ""
print_status "🛑 To stop services:"
print_status "  kill $AUTH_API_PID $FLUTTER_PID"
print_status "  or run: ./stop_system.sh"

# Store PIDs for later cleanup
echo "$AUTH_API_PID" > .auth_api_pid
echo "$FLUTTER_PID" > .flutter_pid

print_header "=================================="
print_header "🎯 READY FOR TELEGRAM AUTH!"
print_header "=================================="

# Keep script running to monitor services
while true; do
    sleep 10
    if ! kill -0 $AUTH_API_PID 2>/dev/null; then
        print_error "❌ Auth API has stopped!"
        break
    fi
    if ! kill -0 $FLUTTER_PID 2>/dev/null; then
        print_error "❌ Flutter app has stopped!"
        break
    fi
done