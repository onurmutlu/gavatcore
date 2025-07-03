#!/bin/bash
# 🔥 GavatCore Fire Mode Deploy Script
# 2 günde yayına giriş planı

echo "🔥 GAVATCORE FIRE MODE BAŞLIYOR! 🔥"
echo "=================================="

# Gün 1 - Session Fix ve Temizlik
echo "📅 GÜN 1: SESSION FIX VE TEMİZLİK"

# 1. Log dosyalarını backup'la ve temizle
echo "🧹 Log temizliği..."
mkdir -p backups/logs_$(date +%Y%m%d_%H%M%S)
cp -r logs/*.log.*.bak backups/logs_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
find logs/ -name "*.log.*.bak" -size +50M -delete
echo "✅ Log temizliği tamamlandı"

# 2. Session durumunu kontrol et
echo "🔍 Session durumu kontrol ediliyor..."
python3 -c "
import sqlite3
import os
for f in os.listdir('sessions/'):
    if f.endswith('.session'):
        try:
            conn = sqlite3.connect(f'sessions/{f}', timeout=1)
            conn.execute('SELECT 1')
            conn.close()
            print(f'✅ {f} - OK')
        except Exception as e:
            print(f'❌ {f} - HATA: {e}')
"

# 3. Redis connection test
echo "🔌 Redis bağlantı testi..."
redis-cli ping && echo "✅ Redis OK" || echo "❌ Redis FAIL"

# 4. Python dependencies check
echo "📦 Dependencies kontrol..."
python3 -c "
try:
    import telethon, redis, motor, structlog, aiofiles
    print('✅ Ana paketler OK')
except ImportError as e:
    print(f'❌ Eksik paket: {e}')
"

# 5. Environment variables check
echo "🔧 Environment variables kontrol..."
python3 -c "
from config import validate_config
if validate_config():
    print('✅ Config OK')
else:
    print('❌ Config hatası')
"

echo ""
echo "🚀 GÜN 1 TAMAMLANDI - GÜN 2 İÇİN HAZIR!"
echo "Şimdi çalıştır: ./start_fire_mode.sh" 