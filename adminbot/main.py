#!/usr/bin/env python3
# adminbot/main.py

import asyncio
import logging
import sys
import os

# Path düzeltmesi - parent directory'yi ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telethon import TelegramClient, events
from config import ADMIN_BOT_TOKEN, TELEGRAM_API_ID, TELEGRAM_API_HASH

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Admin bot ana fonksiyonu"""
    print("🤖 GAVATCORE Admin Bot Başlatılıyor...")
    
    # Bot client oluştur
    bot = TelegramClient('adminbot', TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    # Bot token ile bağlan
    await bot.start(bot_token=ADMIN_BOT_TOKEN)
    
    print("✅ Admin Bot başarıyla başlatıldı!")
    print("📱 Bot hazır ve komutları bekliyor...")
    
    # Event handler'ları ekle
    @bot.on(events.NewMessage)
    async def message_handler(event):
        try:
            # Basit echo bot olarak çalıştır
            if event.raw_text.startswith('/start'):
                await event.respond("🤖 GAVATCORE Admin Bot aktif!\n\n✅ @GavatBaba_BOT çalışıyor")
            elif event.raw_text.startswith('/status'):
                await event.respond("📊 Sistem durumu: Aktif\n🤖 Bot türü: Admin Bot (Token)")
            else:
                await event.respond(f"📝 Mesaj alındı: {event.raw_text}")
        except Exception as e:
            print(f"❌ Admin bot hata: {e}")
            await event.respond(f"❌ Hata oluştu: {str(e)}")
    
    # Bot'u çalıştır
    print("🔄 Admin Bot çalışıyor... (Ctrl+C ile durdur)")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Admin Bot durduruldu.")
    except Exception as e:
        print(f"❌ Admin Bot hatası: {e}") 