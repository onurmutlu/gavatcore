#!/bin/bash

# GavatCore Complete System with Bot Integration Startup Script
echo "🚀 Starting GavatCore Complete System with Bot Integration..."

# Change to the project directory
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

print_success() {
    echo -e "${PURPLE}[SUCCESS]${NC} $1"
}

# Kill any existing processes
print_status "Stopping existing services..."
pkill -f "telegram_auth_api.py" 2>/dev/null
pkill -f "flutter run" 2>/dev/null
pkill -f "bot_system.py" 2>/dev/null
pkill -f "main.py" 2>/dev/null
pkill -f "run.py" 2>/dev/null
sleep 3

# Check if .env exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    exit 1
fi

print_header "========================================="
print_header "🔥 GAVATCORE COMPLETE SYSTEM STARTUP 🔥"
print_header "========================================="

# Step 1: Start Telegram Auth API
print_status "Starting Telegram Authentication API server..."

if [ ! -d "gavatcore_panel/auth_api_venv" ]; then
    print_warning "Creating virtual environment for Auth API..."
    python3 -m venv gavatcore_panel/auth_api_venv
    source gavatcore_panel/auth_api_venv/bin/activate
    pip install flask flask-cors telethon python-dotenv cryptography
else
    source gavatcore_panel/auth_api_venv/bin/activate
fi

# Start Auth API in background
nohup python3 apis/telegram_auth_api.py > logs/auth_api.log 2>&1 &
AUTH_API_PID=$!
print_success "Auth API started (PID: $AUTH_API_PID)"

# Wait for API to start
sleep 4

# Test API
if curl -s http://localhost:5050/api/system/status >/dev/null; then
    print_success "✅ Telegram Auth API is running on http://localhost:5050"
else
    print_error "❌ Failed to start Telegram Auth API"
    cat logs/auth_api.log
    exit 1
fi

# Step 2: Start Main GavatCore Bot System
print_status "Starting GavatCore Bot System..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Start main GavatCore system
nohup python3 run.py > logs/gavatcore_system.log 2>&1 &
GAVATCORE_PID=$!
print_success "GavatCore Bot System started (PID: $GAVATCORE_PID)"

sleep 3

# Step 3: Build and Start Flutter Panel
print_status "Building Flutter web application..."
cd gavatcore_panel

# Install Flutter dependencies if needed
if [ ! -d ".dart_tool" ] || [ ! -f "pubspec.lock" ]; then
    print_warning "Installing Flutter dependencies..."
    flutter pub get
fi

# Generate code
print_status "Generating Flutter code..."
flutter pub run build_runner build --delete-conflicting-outputs >/dev/null 2>&1

# Step 4: Start Flutter Web App
print_status "Starting Flutter web panel..."
nohup flutter run -d chrome --web-port=3000 > ../logs/flutter_web.log 2>&1 &
FLUTTER_PID=$!

cd ..

print_success "Flutter panel started (PID: $FLUTTER_PID)"

# Wait for Flutter to start
sleep 8

print_header "========================================="
print_header "✅ COMPLETE SYSTEM STARTUP SUCCESS!"
print_header "========================================="

print_success "🌐 Services Running:"
print_success "  ┌─ Telegram Auth API: http://localhost:5050"
print_success "  ├─ Flutter Web Panel: http://localhost:3000"
print_success "  ├─ GavatCore Bot System: Running"
print_success "  └─ Main Production API: http://localhost:5050"
print_success ""
print_success "📱 Bot Status:"

# Check bot personas
if [ -f "data/personas/yayincilara.json" ]; then
    print_success "  ├─ 💋 Lara (Flirty Streamer): Configured"
else
    print_warning "  ├─ 💋 Lara: Persona file missing"
fi

if [ -f "data/personas/babagavat.json" ]; then
    print_success "  ├─ 🍸 BabaGavat (Club Leader): Configured" 
else
    print_warning "  ├─ 🍸 BabaGavat: Persona file missing"
fi

if [ -f "data/personas/xxxgeisha.json" ]; then
    print_success "  └─ 🌸 Geisha (Sophisticated Mod): Configured"
else
    print_warning "  └─ 🌸 Geisha: Persona file missing"
fi

print_success ""
print_success "📋 Authentication Endpoints:"
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
print_success "  ├─ GavatCore System: logs/gavatcore_system.log"
print_success "  └─ Flutter Panel: logs/flutter_web.log"
print_success ""
print_success "🛑 To stop all services:"
print_success "  ./stop_complete_system.sh"

# Store PIDs for later cleanup
echo "$AUTH_API_PID" > .auth_api_pid
echo "$GAVATCORE_PID" > .gavatcore_pid
echo "$FLUTTER_PID" > .flutter_pid

print_header "========================================="
print_header "🎯 READY FOR TELEGRAM AUTHENTICATION!"
print_header "🎯 READY FOR BOT MANAGEMENT!"
print_header "========================================="

print_success "1. 🌐 Open http://localhost:3000 in your browser"
print_success "2. 📱 Enter your phone number for Telegram authentication"
print_success "3. ✅ Verify SMS code and 2FA if enabled"
print_success "4. 💬 Start sending messages through the panel"
print_success "5. 🤖 Monitor your bots and automation"

# Monitor services
print_status "Monitoring services (press Ctrl+C to stop)..."
while true; do
    sleep 15
    
    # Check if services are still running
    services_running=0
    
    if kill -0 $AUTH_API_PID 2>/dev/null; then
        services_running=$((services_running + 1))
    else
        print_error "❌ Auth API has stopped!"
    fi
    
    if kill -0 $GAVATCORE_PID 2>/dev/null; then
        services_running=$((services_running + 1))
    else
        print_error "❌ GavatCore system has stopped!"
    fi
    
    if kill -0 $FLUTTER_PID 2>/dev/null; then
        services_running=$((services_running + 1))
    else
        print_error "❌ Flutter panel has stopped!"
    fi
    
    if [ $services_running -lt 3 ]; then
        print_error "Some services have stopped. Check logs for details."
        break
    fi
done