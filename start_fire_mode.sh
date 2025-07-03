#!/bin/bash
# 🚀 GavatCore Fire Mode Start Script
# Sistemi production'a hazır halde başlat

echo "🚀 GAVATCORE BAŞLATILIYOR - FIRE MODE!"
echo "====================================="

# Virtual environment aktif et
echo "🐍 Virtual environment aktif ediliyor..."
source .venv/bin/activate

# Ana sistemi başlat
echo "⚡ Ana sistem başlatılıyor..."
echo "Logs takip etmek için: tail -f logs/run.log"
echo ""

# Background'da çalıştır ve PID'leri kaydet
echo "🤖 Bot motorları başlatılıyor..."

# 1. Ana sistem (main.py)
nohup python3 main.py > logs/main_$(date +%Y%m%d_%H%M%S).log 2>&1 &
MAIN_PID=$!
echo "✅ Main system PID: $MAIN_PID"

# 2. Spam-aware bot system  
nohup python3 spam_aware_full_bot_system.py > logs/spam_aware_$(date +%Y%m%d_%H%M%S).log 2>&1 &
SPAM_PID=$!
echo "✅ Spam-aware bot PID: $SPAM_PID"

# 3. Production bot API
nohup python3 production_bot_api.py > logs/prod_api_$(date +%Y%m%d_%H%M%S).log 2>&1 &
API_PID=$!
echo "✅ Production API PID: $API_PID"

# PID'leri dosyaya kaydet
echo "$MAIN_PID" > gavatcore_main.pid
echo "$SPAM_PID" > gavatcore_spam.pid  
echo "$API_PID" > gavatcore_api.pid

echo ""
echo "🔥 GAVATCORE BAŞLATILDI!"
echo "========================"
echo "📊 İzleme komutları:"
echo "  - tail -f logs/main_*.log"
echo "  - tail -f logs/spam_aware_*.log" 
echo "  - tail -f logs/prod_api_*.log"
echo ""
echo "🛑 Durdurma: ./stop_fire_mode.sh"
echo ""
echo "📱 Mobile App için:"
echo "  cd gavatcore_mobile && flutter run -d web-server --web-port=3000"
echo ""
echo "🎯 Test URL'leri:"
echo "  - API: http://localhost:8000"
echo "  - Mobile: http://localhost:3000"

# 5 saniye bekle ve status kontrol et
sleep 5
echo ""
echo "📈 Sistem durumu (5s sonra):"
ps aux | grep -E "(python.*main|python.*spam_aware|python.*production_bot)" | grep -v grep | head -3 