#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utilities.scheduler_utils import spam_loop
from telethon import TelegramClient

async def test_spam_loop():
    print("🧪 Spam loop test başlıyor...")
    
    # Geisha session'ını kullan
    session_path = "sessions/bot_geishaniz.session"
    if not os.path.exists(session_path):
        print(f"❌ Session dosyası bulunamadı: {session_path}")
        return
    
    # Telethon client oluştur
    client = TelegramClient(session_path, api_id=123456, api_hash="dummy")
    
    try:
        await client.connect()
        print("✅ Client bağlandı")
        
        # Spam loop'u çağır
        print("🚀 Spam loop çağrılıyor...")
        await spam_loop(client)
        
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_spam_loop()) 