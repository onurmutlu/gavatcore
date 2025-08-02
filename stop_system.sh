#!/bin/bash

# GavatCore System Stop Script
echo "🛑 Stopping GavatCore System..."

# Change to the project directory
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Kill processes by PID if files exist
if [ -f ".auth_api_pid" ]; then
    AUTH_PID=$(cat .auth_api_pid)
    if kill -0 $AUTH_PID 2>/dev/null; then
        kill $AUTH_PID
        print_status "Stopped Auth API (PID: $AUTH_PID)"
    fi
    rm .auth_api_pid
fi

if [ -f ".flutter_pid" ]; then
    FLUTTER_PID=$(cat .flutter_pid)
    if kill -0 $FLUTTER_PID 2>/dev/null; then
        kill $FLUTTER_PID
        print_status "Stopped Flutter App (PID: $FLUTTER_PID)"
    fi
    rm .flutter_pid
fi

# Kill any remaining processes
print_status "Cleaning up remaining processes..."
pkill -f "telegram_auth_api.py" 2>/dev/null
pkill -f "flutter run" 2>/dev/null
pkill -f "dart" 2>/dev/null

print_status "✅ All services stopped!"