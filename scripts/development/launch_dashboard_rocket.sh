#!/bin/bash
# 🚀 FLUTTER DASHBOARD ROKET LAUNCHER

echo "📱🚀 FLUTTER DASHBOARD ROKET BAŞLATILIYOR! 🚀📱"
echo ""

# Port kontrolü
if lsof -Pi :9095 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Port 9095 kullanımda, temizleniyor..."
    lsof -ti:9095 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Storage service hatası düzeltmesi
echo "🔧 Storage service kontrol ediliyor..."
cd gavatcore_mobile

# Flutter clean & pub get
echo "🧹 Flutter cache temizleniyor..."
flutter clean > /dev/null 2>&1
flutter pub get > /dev/null 2>&1

echo "🚀 Flutter dashboard başlatılıyor..."
echo "📱 URL: http://localhost:9095"
echo "🔑 Login: demo@gavatcore.com / demo123"
echo ""

flutter run -d web-server --web-port 9095 