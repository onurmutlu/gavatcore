#!/usr/bin/env python3
# test_dm_handler.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import asyncio
from telethon import TelegramClient
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

async def test_dm_handler():
    """Bot'lara test DM'i gönder ve yanıt alıp almadığını kontrol et"""
    
    # Test client oluştur
    client = TelegramClient('test_dm_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    try:
        await client.start()
        print("✅ Test client başlatıldı")
        
        # Test edilecek bot'lar
        bots = [
            "@geishaniz",
            "@yayincilara", 
            "@babagavat"
        ]
        
        test_message = "Test mesajı - DM handler çalışıyor mu?"
        
        for bot_handle in bots:
            try:
                # Bot'u bul
                bot = await client.get_entity(bot_handle)
                print(f"✅ {bot_handle} bulundu: {bot.username} (ID: {bot.id}, Type: {type(bot).__name__})")
                
                # Test mesajı gönder
                await client.send_message(bot, test_message)
                print(f"📤 {bot_handle}'a test mesajı gönderildi")
                
                # Kısa bekleme
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ {bot_handle} test hatası: {e}")
        
        print("\n🧪 Test tamamlandı. Bot log dosyalarını kontrol edin.")
        
    except Exception as e:
        print(f"💥 Test hatası: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_dm_handler()) 