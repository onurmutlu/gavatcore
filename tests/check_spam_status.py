#!/usr/bin/env python3
"""
🔍 Telegram SpamBot Ban Durumu Kontrolü
"""

import asyncio
import os
from telethon import TelegramClient
from telethon.tl.functions.messages import StartBotRequest
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

async def check_spam_status(session_file: str):
    """SpamBot ile ban durumunu kontrol et"""
    
    client = TelegramClient(session_file, TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    try:
        await client.start()
        me = await client.get_me()
        print(f"\n🤖 Kontrol edilen hesap: @{me.username}")
        
        # SpamBot'a mesaj gönder
        print("📨 @SpamBot'a /start gönderiliyor...")
        
        # SpamBot entity'sini al
        spambot = await client.get_entity("@SpamBot")
        
        # /start komutu gönder
        await client.send_message(spambot, "/start")
        
        print("⏳ SpamBot cevabı bekleniyor...")
        await asyncio.sleep(3)
        
        # Son mesajları al
        messages = await client.get_messages(spambot, limit=5)
        
        print("\n📊 SpamBot Cevabı:")
        print("-" * 50)
        
        for msg in messages:
            if msg.text:
                print(msg.text)
                print("-" * 50)
                
                # Ban durumu kontrolü
                if "no limits" in msg.text.lower() or "sınırlama yok" in msg.text.lower():
                    print("\n✅ HESAP TEMİZ! Sınırlama yok.")
                elif "restricted" in msg.text.lower() or "sınırlı" in msg.text.lower():
                    print("\n⚠️ HESAP SINIRLI! Gruplara mesaj gönderemez.")
                    print("\n🔧 Çözüm:")
                    print("1. SpamBot'a '/start' yazın")
                    print("2. 'This is a mistake' veya 'But I didn't spam' tıklayın")
                    print("3. Formu doldurun ve bekleyin")
                
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        await client.disconnect()

async def main():
    """Tüm botları kontrol et"""
    print("""
🔍 TELEGRAM SPAM BAN KONTROLÜ
💀 Tüm botların durumu kontrol ediliyor...
    """)
    
    sessions = [
        "sessions/babagavat_conversation",
        "sessions/_905382617727",  # YayıncıLara
        "sessions/_905486306226",  # XXXGeisha
    ]
    
    for session in sessions:
        if os.path.exists(f"{session}.session"):
            await check_spam_status(session)
            print("\n" + "="*60 + "\n")
        else:
            print(f"❌ Session bulunamadı: {session}")

if __name__ == "__main__":
    asyncio.run(main()) 