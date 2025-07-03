#!/usr/bin/env python3
"""
Instant Message Bot - Anında mesaj gönderir
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
    print("⚡ INSTANT MESSAGE BOT")
    
    # Client oluştur
    client = TelegramClient('sessions/_905382617727', TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    await client.start()
    me = await client.get_me()
    print(f"✅ Giriş yapıldı: @{me.username}")
    
    # Belirli bir kullanıcıya mesaj gönder
    target_username = input("\n📱 Mesaj göndermek istediğiniz kullanıcı adı (@olmadan): @")
    
    if target_username:
        try:
            # Kullanıcıyı bul
            user = await client.get_entity(f"@{target_username}")
            print(f"✅ Kullanıcı bulundu: {user.first_name}")
            
            # Mesaj gönder
            message = f"""
🤖 GAVATCore Test Mesajı

Merhaba {user.first_name}! 👋
Bu otomatik bir test mesajıdır.

🕐 Gönderim zamanı: {datetime.now().strftime('%H:%M:%S')}
✨ Bot: @{me.username}

Lütfen bu mesaja yanıt verin, bot yanıtınızı alacak.
            """
            
            await client.send_message(user, message)
            print(f"✅ Mesaj gönderildi!")
            
            # Handler ekle
            @client.on(events.NewMessage(from_users=user.id))
            async def handler(event):
                print(f"\n💬 YANIT ALINDI!")
                print(f"📝 Mesaj: {event.raw_text}")
                
                # Otomatik yanıt
                await event.respond(f"Teşekkürler! Mesajınızı aldım: '{event.raw_text[:50]}'")
                print("✅ Otomatik yanıt gönderildi!")
            
            print(f"\n⏳ {user.first_name}'den yanıt bekleniyor...")
            print("⛔ Durdurmak için Ctrl+C\n")
            
            # 5 dakika bekle
            await asyncio.sleep(300)
            
        except Exception as e:
            print(f"❌ Hata: {e}")
    
    await client.disconnect()
    print("\n👋 Bot kapatıldı")

if __name__ == "__main__":
    asyncio.run(main()) 