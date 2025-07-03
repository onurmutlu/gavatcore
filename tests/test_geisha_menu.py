#!/usr/bin/env python3
# test_geisha_menu.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import asyncio
from telethon import TelegramClient
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

async def test_geisha_menu():
    """Geisha bot'una test mesajı gönder ve show menü sistemini test et"""
    
    # Test client oluştur
    client = TelegramClient('test_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    try:
        await client.start()
        print("✅ Test client başlatıldı")
        
        # Geisha bot'unu bul
        geisha_bot = await client.get_entity("@geishaniz")
        print(f"✅ Geisha bot bulundu: {geisha_bot.username}")
        
        # Test mesajları gönder
        test_messages = [
            "Merhaba",
            "fiyat",
            "show menü",
            "hizmet"
        ]
        
        for msg in test_messages:
            print(f"📤 Mesaj gönderiliyor: {msg}")
            await client.send_message(geisha_bot, msg)
            await asyncio.sleep(3)  # 3 saniye bekle
            
            # Son mesajları al
            messages = await client.get_messages(geisha_bot, limit=5)
            print(f"📥 Son {len(messages)} mesaj:")
            for i, message in enumerate(messages):
                if message.text:
                    preview = message.text[:100] + "..." if len(message.text) > 100 else message.text
                    print(f"   {i+1}. {preview}")
            print("-" * 50)
        
        print("✅ Test tamamlandı!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_geisha_menu()) 