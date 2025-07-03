#!/bin/bash

echo "🚀 GAVATCORE BOT ROCKET LAUNCHER 🚀"
echo "==================================="

# Port kontrolü
echo "📡 Port kontrolü yapılıyor..."
if lsof -i :5005 > /dev/null 2>&1; then
    echo "✅ API zaten çalışıyor (Port 5005)"
    API_RUNNING=true
else
    echo "🔧 API başlatılıyor..."
    python3 real_bot_api_no_mock.py &
    API_PID=$!
    echo "⏳ API'nin başlaması bekleniyor (3 saniye)..."
    sleep 3
    API_RUNNING=true
fi

# API health check
echo "🏥 API sağlık kontrolü..."
if curl -s http://localhost:5005/health > /dev/null; then
    echo "✅ API sağlıklı!"
else
    echo "❌ API yanıt vermiyor, tekrar deneniyor..."
    sleep 2
    if ! curl -s http://localhost:5005/health > /dev/null; then
        echo "💀 API başlatılamadı! Manuel başlatın:"
        echo "   python3 real_bot_api_no_mock.py"
        exit 1
    fi
fi

echo ""
echo "🤖 BOT'LARI BAŞLATILIYOR..."
echo "=========================="

# Tüm botları başlat
echo "🚀 Tüm botları API üzerinden başlatıyorum..."
START_RESULT=$(curl -s -X POST http://localhost:5005/api/system/start)

if echo "$START_RESULT" | grep -q '"success": true'; then
    echo "✅ Bot başlatma komutu başarılı!"
else
    echo "⚠️ Bot başlatma hatası, manuel başlatılıyor..."
    
    # Lara bot'u başlat (telefon numarası sorabilir)
    echo "🌹 Lara Bot başlatılıyor..."
    python3 lara_bot_launcher.py &
    LARA_PID=$!
    
    echo "⏳ Lara için 3 saniye bekleniyor..."
    sleep 3
fi

echo ""
echo "📊 BOT DURUM RAPORU"
echo "=================="

# Bot durumlarını al
STATUS_RESULT=$(curl -s http://localhost:5005/api/bots)

if [ $? -eq 0 ]; then
    echo "✅ API'den durum alındı:"
    echo "$STATUS_RESULT" | python3 -m json.tool 2>/dev/null || echo "$STATUS_RESULT"
else
    echo "❌ API'den durum alınamadı"
    
    # Manuel process kontrolü
    echo ""
    echo "🔍 Manuel Process Kontrolü:"
    echo "------------------------"
    
    if pgrep -f "lara_bot_launcher" > /dev/null; then
        LARA_PID=$(pgrep -f "lara_bot_launcher")
        echo "🟢 Lara Bot çalışıyor (PID: $LARA_PID)"
    else
        echo "🔴 Lara Bot çalışmıyor"
    fi
    
    if pgrep -f "babagavat.*launcher" > /dev/null; then
        BABAGAVAT_PID=$(pgrep -f "babagavat.*launcher")
        echo "🟢 BabaGavat Bot çalışıyor (PID: $BABAGAVAT_PID)"
    else
        echo "🔴 BabaGavat Bot çalışmıyor"
    fi
    
    if pgrep -f "real_bot_api" > /dev/null; then
        API_PID=$(pgrep -f "real_bot_api")
        echo "🟢 API çalışıyor (PID: $API_PID)"
    else
        echo "🔴 API çalışmıyor"
    fi
fi

echo ""
echo "🎯 ERİŞİM LİNKLERİ"
echo "=================="
echo "🌐 Bot Management API: http://localhost:5005"
echo "📊 Health Check: http://localhost:5005/health"
echo "🤖 Bot Status: http://localhost:5005/api/bots"

echo ""
echo "🛠️ MANUEL KOMUTLAR"
echo "=================="
echo "Bot başlat: curl -X POST http://localhost:5005/api/system/start"
echo "Bot durdur: curl -X POST http://localhost:5005/api/system/stop"
echo "Durum göster: curl http://localhost:5005/api/bots | python3 -m json.tool"

echo ""
echo "🔥 ROCKET LAUNCHER TAMAMLANDI! 🔥"

# Sürekli monitoring isterse
read -p "📊 Canlı monitoring başlatılsın mı? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Canlı monitoring başlatılıyor (Ctrl+C ile dur)..."
    
    while true; do
        clear
        echo "🤖 CANLI BOT MONİTORİNG - $(date '+%H:%M:%S')"
        echo "========================================"
        
        curl -s http://localhost:5005/api/bots | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if 'bots' in data:
        for bot in data['bots']:
            status_emoji = {'running': '🟢', 'stopped': '🔴', 'crashed': '💥'}.get(bot.get('status', 'unknown'), '❓')
            print(f\"{status_emoji} {bot.get('name', 'Unknown'):<12} | PID: {str(bot.get('pid', 'N/A')):<8} | RAM: {bot.get('memory_usage', 0):>6.1f}MB | CPU: {bot.get('cpu_usage', 0):>5.1f}% | Uptime: {int(bot.get('uptime', 0)):>3}min\")
    else:
        print('❌ API'den veri alınamadı')
except:
    print('⚠️ JSON parse hatası')
" 2>/dev/null || echo "❌ API'ye bağlanılamadı"
        
        echo "========================================"
        echo "🌐 API: http://localhost:5005 | 🔄 Her 5s güncelleniyor"
        sleep 5
    done
fi 