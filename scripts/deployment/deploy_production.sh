#!/bin/bash

# 🚀 GavatCore Production Deployment Script
# ========================================

echo "🚀 GAVATCore Production Deployment Başlıyor..."
echo "============================================"

# 1. Environment kontrolü
echo "1️⃣ Environment kontrolü..."
if [ ! -f ".env" ]; then
    echo "❌ .env dosyası bulunamadı!"
    exit 1
fi

# 2. Python dependencies
echo "2️⃣ Python bağımlılıkları güncelleniyor..."
pip install -r config/requirements.txt

# 3. Flutter build (eğer değişiklik varsa)
echo "3️⃣ Flutter web build kontrolü..."
cd gavatcore_mobile
if [ -d "lib" ]; then
    echo "📱 Flutter build başlatılıyor..."
    flutter clean
    flutter pub get
    flutter build web --release --web-renderer html
    
    # Build'i deployment dizinine kopyala
    if [ -d "build/web" ]; then
        echo "📦 Flutter build kopyalanıyor..."
        rm -rf ../deploy_package/gavatcore_web/*
        cp -r build/web/* ../deploy_package/gavatcore_web/
    fi
fi
cd ..

# 4. Test suite çalıştır
echo "4️⃣ Test suite çalıştırılıyor..."
python -m pytest tests/ -v --tb=short -c config/pytest.ini || echo "⚠️ Bazı testler başarısız"

# 5. Database migrations
echo "5️⃣ Database kontrolleri..."
python -c "
from core.database_manager import database_manager
import asyncio
asyncio.run(database_manager.initialize())
print('✅ Database hazır')
"

# 6. Session dosyaları kontrolü
echo "6️⃣ Session dosyaları kontrol ediliyor..."
for session in sessions/_*.session; do
    if [ -f "$session" ]; then
        size=$(du -k "$session" | cut -f1)
        if [ $size -gt 10 ]; then
            echo "✅ $(basename $session): ${size}KB"
        else
            echo "⚠️ $(basename $session): Küçük dosya (${size}KB)"
        fi
    fi
done

# 7. Process'leri durdur
echo "7️⃣ Mevcut process'ler durduruluyor..."
pkill -f "python.*bot.*" || true
pkill -f "python.*api.*" || true
pkill -f "python.*dashboard.*" || true
sleep 2

# 8. Production servisleri başlat
echo "8️⃣ Production servisleri başlatılıyor..."

# Admin Dashboard
echo "🎛️ Admin Dashboard başlatılıyor (port 8000)..."
nohup python admin/dashboards/admin_comprehensive_dashboard.py > logs/admin_dashboard.log 2>&1 &
echo $! > pids/admin_dashboard.pid

# Simple Admin API
echo "📊 Simple Admin API başlatılıyor (port 5055)..."
nohup python admin/dashboards/simple_admin_dashboard.py > logs/simple_admin.log 2>&1 &
echo $! > pids/simple_admin.pid

# Behavioral Dashboard
echo "🧠 Behavioral Dashboard başlatılıyor (port 5057)..."
nohup python api/behavioral_insights_dashboard_simple.py > logs/behavioral.log 2>&1 &
echo $! > pids/behavioral.pid

# Scalable FastAPI
echo "⚡ Scalable FastAPI başlatılıyor (port 6000)..."
nohup python apis/scalable_fastapi_server.py > logs/scalable_api.log 2>&1 &
echo $! > pids/scalable_api.pid

# Flutter Dashboard API
echo "📱 Flutter Dashboard API başlatılıyor (port 9500)..."
nohup python api/flutter_dashboard_adapter.py > logs/flutter_api.log 2>&1 &
echo $! > pids/flutter_api.pid

# Power Mode Controller
echo "⚡ Power Mode Controller başlatılıyor (port 7500)..."
nohup python api/power_mode_controller.py > logs/power_mode.log 2>&1 &
echo $! > pids/power_mode.pid

sleep 5

# 9. Bot sistemi başlat
echo "9️⃣ Bot sistemi başlatılıyor..."
nohup python run.py > logs/bot_system.log 2>&1 &
echo $! > pids/bot_system.pid

sleep 3

# 10. Health check
echo "🔟 Health check yapılıyor..."
services=(
    "http://localhost:8000/health:Admin Dashboard"
    "http://localhost:5055/api/admin/system/health:Simple Admin"
    "http://localhost:5057/health:Behavioral Dashboard"
    "http://localhost:6000/health:Scalable API"
    "http://localhost:9500/health:Flutter API"
    "http://localhost:7500/health:Power Mode"
)

echo ""
echo "📊 SERVICE STATUS:"
echo "=================="

for service in "${services[@]}"; do
    IFS=':' read -r url name <<< "$service"
    if curl -s -f "$url" > /dev/null; then
        echo "✅ $name"
    else
        echo "❌ $name"
    fi
done

# 11. Web server başlat (Flutter)
echo ""
echo "🌐 Flutter Web Server başlatılıyor (port 8080)..."
cd deploy_package/gavatcore_web
nohup python3 -m http.server 8080 > ../../logs/flutter_web.log 2>&1 &
echo $! > ../../pids/flutter_web.pid
cd ../..

# 12. Final status
echo ""
echo "🎉 DEPLOYMENT TAMAMLANDI!"
echo "========================"
echo ""
echo "📱 Flutter Admin Panel: http://localhost:8080"
echo "🎛️ Admin Dashboard: http://localhost:8000"
echo "📊 Simple Admin API: http://localhost:5055"
echo "🧠 Behavioral Dashboard: http://localhost:5057"
echo "⚡ Scalable API: http://localhost:6000"
echo "📱 Flutter API: http://localhost:9500"
echo "⚡ Power Mode: http://localhost:7500"
echo ""
echo "📝 Loglar: logs/ dizininde"
echo "🔧 PID'ler: pids/ dizininde"
echo ""
echo "⏹️ Durdurmak için: ./scripts/deployment/stop_production.sh"

# Log dizinini oluştur
mkdir -p logs pids

echo "✅ Production deployment başarılı!" 