#!/bin/bash
# 🚀 GAVATCORE ROKET BOT BAŞLATMA SCRIPT'İ
# Tüm 3 karakteri roket gibi başlatır!

echo "🚀🚀🚀 GAVATCORE ROKET BAŞLATILIYOR! 🚀🚀🚀"
echo ""

# API'nin hazır olmasını bekle
echo "⏳ API hazır mı kontrol ediliyor..."
for i in {1..10}; do
    if curl -s http://localhost:5004/health > /dev/null 2>&1; then
        echo "✅ API hazır!"
        break
    fi
    echo "   API bekleniyor... ($i/10)"
    sleep 2
done

echo ""
echo "🔥 BOTLAR ROKET GİBİ BAŞLATILIYOR..."

# BabaGavat - Sokak Lideri
echo "👑 BabaGavat başlatılıyor..."
curl -X POST http://localhost:5004/api/bot/babagavat/start 2>/dev/null
sleep 1

# Lara - Premium Yayıncı
echo "💋 Lara başlatılıyor..."
curl -X POST http://localhost:5004/api/bot/lara/start 2>/dev/null
sleep 1

# Geisha - Baştan Çıkarıcı
echo "🌸 Geisha başlatılıyor..."
curl -X POST http://localhost:5004/api/bot/geisha/start 2>/dev/null
sleep 1

echo ""
echo "📊 BOT DURUMLARI:"
echo "=================="

# Bot durumlarını kontrol et
curl -s http://localhost:5004/api/bots | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    bots = data.get('bots', [])
    for bot in bots:
        status = bot.get('status', 'unknown')
        name = bot.get('name', 'Unknown')
        handle = bot.get('telegram_handle', '')
        
        if status == 'running':
            icon = '🟢'
        elif status == 'stopped':
            icon = '🟡'
        else:
            icon = '🔴'
            
        print(f'{icon} {name} ({handle}) - {status.upper()}')
except:
    print('API yanıt alamadı, manuel kontrol edin')
"

echo ""
echo "🚀 ROKET BAŞLATMA TAMAMLANDI!"
echo "📱 Flutter Dashboard: http://localhost:9095"
echo "🌐 Bot API: http://localhost:5004"

# Flutter dashboard'u başlat (opsiyonel)
read -p "Flutter dashboard'u da başlatmak ister misin? (y/N): " start_flutter
if [[ $start_flutter =~ ^[Yy]$ ]]; then
    echo "📱 Flutter dashboard başlatılıyor..."
    cd gavatcore_mobile
    flutter run -d web-server --web-port 9095 &
    echo "✅ Flutter başlatıldı: http://localhost:9095"
fi

echo ""
echo "🎯 TÜM SİSTEM AKTİF - ROKET MOD! 🚀" 