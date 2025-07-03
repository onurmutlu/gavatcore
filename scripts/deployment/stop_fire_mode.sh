#!/bin/bash
# 🛑 GavatCore Fire Mode Stop Script

echo "🛑 GAVATCORE DURDURULUYOR..."
echo "=========================="

# PID dosyalarından süreçleri durdur
if [ -f gavatcore_main.pid ]; then
    MAIN_PID=$(cat gavatcore_main.pid)
    kill $MAIN_PID 2>/dev/null && echo "✅ Main system durduruldu ($MAIN_PID)" || echo "⚠️ Main system zaten durmuş"
    rm gavatcore_main.pid
fi

if [ -f gavatcore_spam.pid ]; then
    SPAM_PID=$(cat gavatcore_spam.pid)
    kill $SPAM_PID 2>/dev/null && echo "✅ Spam-aware bot durduruldu ($SPAM_PID)" || echo "⚠️ Spam-aware bot zaten durmuş"
    rm gavatcore_spam.pid
fi

if [ -f gavatcore_api.pid ]; then
    API_PID=$(cat gavatcore_api.pid)
    kill $API_PID 2>/dev/null && echo "✅ Production API durduruldu ($API_PID)" || echo "⚠️ Production API zaten durmuş"
    rm gavatcore_api.pid
fi

# Kalan süreçleri zorla durdur
echo "🔍 Kalan süreçler kontrol ediliyor..."
pkill -f "python.*main.py" 2>/dev/null
pkill -f "python.*spam_aware" 2>/dev/null  
pkill -f "python.*production_bot" 2>/dev/null

echo ""
echo "✅ GAVATCORE DURDURULDU!"
echo "Yeniden başlatmak için: ./start_fire_mode.sh" 