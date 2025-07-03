#!/bin/bash

echo "🔧 GavatCore Panel - Build Runner Script"
echo "========================================"

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter is not installed or not in PATH"
    echo "💡 Please install Flutter: https://flutter.dev/docs/get-started/install"
    exit 1
fi

echo "✅ Flutter found: $(flutter --version | head -n 1)"

# Navigate to project directory
cd "$(dirname "$0")"

echo ""
echo "📦 Installing dependencies..."
flutter pub get

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🏗️  Running build runner..."
flutter packages pub run build_runner build --delete-conflicting-outputs

if [ $? -ne 0 ]; then
    echo "❌ Build runner failed"
    exit 1
fi

echo ""
echo "🎉 Build completed successfully!"
echo ""
echo "🚀 To run the app:"
echo "   flutter run -d chrome  # For web"
echo "   flutter run -d macos   # For macOS"
echo "   flutter run            # For connected device" 