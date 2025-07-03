#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telethon import TelegramClient
from utils.scheduler_utils import spam_loop

# API bilgileri
API_ID = 29830823
API_HASH = "0016dc6411c9e6f11e5cf0be3dd0b4f3"

async def test_spam_loop():
    print("🧪 Spam loop await testi başlıyor...")
    
    # Geisha session'ını kullan
    session_path = "sessions/bot_geishaniz.session"
    if not os.path.exists(session_path):
        print(f"❌ Session dosyası bulunamadı: {session_path}")
        return
    
    # Telethon client oluştur
    client = TelegramClient(session_path, API_ID, API_HASH)
    
    try:
        await client.connect()
        print("✅ Client bağlandı")
        
        if not await client.is_user_authorized():
            print("❌ Kullanıcı yetkilendirilmemiş!")
            return
            
        me = await client.get_me()
        print(f"👤 Bağlı kullanıcı: {me.username}")
        
        # Spam loop'u başlat
        print("🚀 Spam loop çağrılıyor...")
        # 5 dakika çalıştır
        spam_task = asyncio.create_task(spam_loop(client))
        await asyncio.sleep(300)  # 5 dakika bekle
        spam_task.cancel()
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()
        print("🔌 Bağlantı kapatıldı")

if __name__ == "__main__":
    asyncio.run(test_spam_loop()) 