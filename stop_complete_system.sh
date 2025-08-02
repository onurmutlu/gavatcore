#!/bin/bash

# GavatCore Complete System Stop Script
echo "🛑 Stopping GavatCore Complete System..."

# Change to the project directory
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

print_header "🛑 STOPPING GAVATCORE COMPLETE SYSTEM"
print_header "======================================"

# Kill processes by PID if files exist
if [ -f ".auth_api_pid" ]; then
    AUTH_PID=$(cat .auth_api_pid)
    if kill -0 $AUTH_PID 2>/dev/null; then
        kill $AUTH_PID
        print_status "Stopped Auth API (PID: $AUTH_PID)"
    fi
    rm .auth_api_pid
fi

if [ -f ".gavatcore_pid" ]; then
    GAVATCORE_PID=$(cat .gavatcore_pid)
    if kill -0 $GAVATCORE_PID 2>/dev/null; then
        kill $GAVATCORE_PID
        print_status "Stopped GavatCore System (PID: $GAVATCORE_PID)"
    fi
    rm .gavatcore_pid
fi

if [ -f ".flutter_pid" ]; then
    FLUTTER_PID=$(cat .flutter_pid)
    if kill -0 $FLUTTER_PID 2>/dev/null; then
        kill $FLUTTER_PID
        print_status "Stopped Flutter Panel (PID: $FLUTTER_PID)"
    fi
    rm .flutter_pid
fi

# Kill any remaining processes
print_status "Cleaning up remaining processes..."
pkill -f "telegram_auth_api.py" 2>/dev/null
pkill -f "flutter run" 2>/dev/null
pkill -f "bot_system.py" 2>/dev/null
pkill -f "main.py" 2>/dev/null
pkill -f "run.py" 2>/dev/null
pkill -f "dart" 2>/dev/null

# Wait a moment for processes to clean up
sleep 2

print_status "✅ All GavatCore services stopped!"
print_status "💡 You can restart with: ./start_complete_system.sh"