#!/usr/bin/env python3
"""
Working Bot - Kesinlikle çalışan bot
"""

import asyncio
import os
import sys
from telethon.sync import TelegramClient, events
from datetime import datetime

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

# Global client
client = None

def main():
    global client
    
    print("🚀 WORKING BOT BAŞLIYOR...")
    print(f"API ID: {TELEGRAM_API_ID}")
    print(f"API HASH: {TELEGRAM_API_HASH[:10]}...")
    
    # Session kontrolü
    session_file = "sessions/_905382617727.session"
    if not os.path.exists(session_file):
        print(f"❌ Session dosyası bulunamadı: {session_file}")
        print("💡 İpucu: Önce create_fresh_session.py çalıştırın")
        return
    
    print(f"✅ Session bulundu: {session_file}")
    
    # Sync client oluştur
    client = TelegramClient('sessions/_905382617727', TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    # Başlat
    client.start()
    
    me = client.get_me()
    print(f"\n✅ Bot aktif!")
    print(f"👤 Hesap: {me.first_name} (@{me.username})")
    print(f"🆔 ID: {me.id}")
    
    # Test mesajı
    print("\n📤 Test mesajı gönderiliyor...")
    client.send_message('me', f"""
🤖 **Working Bot Aktif!**

✅ Bot başarıyla başlatıldı
🕐 Zaman: {datetime.now().strftime('%H:%M:%S')}

_Mesaj göndermek için hazır!_
    """)
    print("✅ Test mesajı gönderildi!")
    
    # Handler
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        try:
            if event.is_private:
                sender = await event.get_sender()
                if sender and not sender.bot:
                    # Terminal'e yazdır
                    print(f"\n" + "="*50)
                    print(f"💬 YENİ MESAJ!")
                    print(f"👤 Gönderen: {sender.first_name} (@{sender.username or 'username yok'})")
                    print(f"📝 Mesaj: {event.raw_text}")
                    print("="*50)
                    
                    # Hızlı yanıt
                    yanit = f"""
🌹 Merhaba {sender.first_name}!

Mesajını aldım: "{event.raw_text[:100]}"

✨ Ben GAVATCore Working Bot
🕐 Saat: {datetime.now().strftime('%H:%M:%S')}

_Otomatik yanıt_
                    """
                    
                    await event.respond(yanit)
                    print("✅ Yanıt gönderildi!")
                    
        except Exception as e:
            print(f"❌ Handler hatası: {e}")
    
    print("\n" + "🎯"*20)
    print("🎯 BOT HAZIR! MESAJ BEKLENİYOR...")
    print("🎯 Test için başka hesaptan DM gönderin")
    print("🎯 Durdurmak için Ctrl+C")
    print("🎯"*20 + "\n")
    
    # Çalışmaya devam et
    try:
        client.run_until_disconnected()
    except KeyboardInterrupt:
        print("\n⏹️ Bot durduruluyor...")
    finally:
        client.disconnect()
        print("👋 Bot kapatıldı")

if __name__ == "__main__":
    main() 