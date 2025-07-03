#!/bin/bash

# ====================================
# GavatCore Flutter Admin Panel Launcher
# ====================================

echo "🚀 GavatCore Flutter Admin Panel Başlatılıyor..."
echo "=============================================="

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter bulunamadı! Lütfen Flutter SDK yükleyin."
    echo "📖 https://flutter.dev/docs/get-started/install"
    exit 1
fi

# Check Flutter version
echo "📱 Flutter versiyonu kontrol ediliyor..."
flutter --version

# Navigate to Flutter project
cd gavatcore_mobile

# Get dependencies
echo ""
echo "📦 Bağımlılıklar yükleniyor..."
flutter pub get

# Check if backend is running
echo ""
echo "🔍 Backend API kontrol ediliyor..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Production API (port 8000) aktif"
    API_URL="http://localhost:8000"
elif curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Flutter Test API (port 8001) aktif"
    API_URL="http://localhost:8001"
else
    echo "⚠️ Backend API bulunamadı!"
    echo ""
    echo "Backend'i başlatmak için:"
    echo "1. Production API: python production_bot_api.py"
    echo "2. Test API: python api/flutter_endpoints.py"
    echo ""
    read -p "Backend olmadan devam etmek istiyor musunuz? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Select platform
echo ""
echo "📱 Platform seçin:"
echo "1. Web (Chrome)"
echo "2. iOS Simulator"
echo "3. Android Emulator"
echo "4. Tüm cihazları listele"
read -p "Seçim (1-4): " platform

case $platform in
    1)
        echo ""
        echo "🌐 Flutter Web başlatılıyor..."
        echo "URL: http://localhost:3000"
        flutter run -d chrome --web-port=3000
        ;;
    2)
        echo ""
        echo "📱 iOS Simulator başlatılıyor..."
        flutter run -d iphone
        ;;
    3)
        echo ""
        echo "🤖 Android Emulator başlatılıyor..."
        flutter run -d android
        ;;
    4)
        echo ""
        echo "📱 Mevcut cihazlar:"
        flutter devices
        echo ""
        read -p "Device ID girin: " device_id
        flutter run -d $device_id
        ;;
    *)
        echo "❌ Geçersiz seçim!"
        exit 1
        ;;
esac 