#!/usr/bin/env python3
"""
Fresh Session Creator - Yeni session oluşturur ve test mesajı gönderir
"""

import asyncio
import os
import sys
from telethon import TelegramClient, events
from datetime import datetime

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

async def main():
    print("🔄 YENİ SESSION OLUŞTURULUYOR...")
    print(f"API ID: {TELEGRAM_API_ID}")
    print(f"API HASH: {TELEGRAM_API_HASH[:10]}...")
    
    # Eski session'ı sil
    session_name = "sessions/test_bot_fresh"
    old_files = [
        f"{session_name}.session",
        f"{session_name}.session-journal",
        "sessions/_905382617727.session",
        "sessions/_905382617727.session-journal"
    ]
    
    for file in old_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🗑️ Silindi: {file}")
            except:
                pass
    
    # Yeni client oluştur
    client = TelegramClient(
        session_name,
        TELEGRAM_API_ID,
        TELEGRAM_API_HASH
    )
    
    print("\n📱 Telegram'a giriş yapılıyor...")
    print("Not: Telefon numaranızı +90 ile başlayarak girin")
    
    try:
        # Başlat (interaktif login)
        await client.start()
        
        me = await client.get_me()
        print(f"\n✅ Giriş başarılı!")
        print(f"👤 Kullanıcı: {me.first_name} {me.last_name or ''}")
        print(f"🆔 ID: {me.id}")
        print(f"📱 Telefon: {me.phone}")
        print(f"🔗 Username: @{me.username}" if me.username else "Username yok")
        
        # Test mesajı gönder
        print("\n📤 Test mesajı gönderiliyor...")
        
        # Kendine mesaj gönder
        await client.send_message('me', f"""
🤖 **GAVATCore Test Bot Aktif!**

✅ Session başarıyla oluşturuldu
🕐 Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🆔 Bot ID: {me.id}

_Bu bir test mesajıdır._
        """)
        
        print("✅ Test mesajı gönderildi! Saved Messages'ı kontrol edin.")
        
        # Basit handler ekle
        @client.on(events.NewMessage(incoming=True))
        async def handler(event):
            if event.is_private:
                sender = await event.get_sender()
                if sender and not getattr(sender, 'bot', False):
                    print(f"\n💬 Mesaj alındı!")
                    print(f"👤 Gönderen: {sender.first_name}")
                    print(f"📝 Mesaj: {event.raw_text}")
                    
                    # Otomatik yanıt
                    response = f"🌹 Merhaba {sender.first_name}! Ben GAVATCore test botu. Mesajını aldım: '{event.raw_text[:50]}...'"
                    await event.respond(response)
                    print(f"✅ Yanıt gönderildi!")
        
        print("\n🎯 Bot hazır! Mesaj bekleniyor...")
        print("📌 Botu test etmek için başka bir hesaptan bu hesaba DM gönderin")
        print("⛔ Durdurmak için Ctrl+C")
        
        # Çalışmaya devam et
        await client.run_until_disconnected()
        
    except KeyboardInterrupt:
        print("\n⏹️ Bot durduruluyor...")
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()
        print("👋 Bot kapatıldı")

if __name__ == "__main__":
    asyncio.run(main()) 