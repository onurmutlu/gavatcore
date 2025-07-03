#!/usr/bin/env python3
# test_dm_debug.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import asyncio
import sys
import os
from telethon import TelegramClient
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

async def test_dm_debug():
    """Sadece bir bot'u başlatıp DM test et"""
    
    # Gavat Baba bot'unu test et
    client = TelegramClient('sessions/babagavat', TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    try:
        await client.start()
        me = await client.get_me()
        print(f"✅ Bot başlatıldı: {me.username} (ID: {me.id})")
        
        # DM handler'ı import et
        from handlers.dm_handler import handle_message
        from datetime import datetime
        
        # Test mesajı simüle et
        class MockSender:
            def __init__(self):
                self.id = 123456789
                self.username = "test_user"
                self.first_name = "Test"
        
        sender = MockSender()
        message_text = "Test mesajı - DM handler çalışıyor mu?"
        session_created_at = datetime.now()
        
        print(f"🧪 DM handler test başlıyor...")
        print(f"📤 Mesaj: {message_text}")
        print(f"👤 Sender: {sender.username} (ID: {sender.id})")
        
        # DM handler'ı çağır
        await handle_message(client, sender, message_text, session_created_at)
        
        print(f"✅ DM handler test tamamlandı")
        
        # 15 saniye bekle (manualplus timeout + 5 saniye)
        print(f"⏰ 15 saniye bekleniyor (manualplus timeout test)...")
        await asyncio.sleep(15)
        
    except Exception as e:
        print(f"💥 Test hatası: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_dm_debug()) 