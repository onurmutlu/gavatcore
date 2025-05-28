#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telethon import TelegramClient
from pathlib import Path
import json

# API bilgileri (config.py'den alınmalı ama test için sabit)
API_ID = 29830823
API_HASH = "0016dc6411c9e6f11e5cf0be3dd0b4f3"

async def test_spam():
    print("🧪 Spam test başlıyor...")
    
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
        
        # Dialog'ları al
        print("🔍 Dialog'lar alınıyor...")
        dialogs = await client.get_dialogs()
        print(f"📋 Toplam {len(dialogs)} dialog bulundu")
        
        # Grupları say
        groups = [d for d in dialogs if d.is_group]
        print(f"👥 Toplam {len(groups)} grup bulundu")
        
        # İlk 5 grubu listele
        print("\n🏠 İlk 5 grup:")
        for i, group in enumerate(groups[:5]):
            print(f"  {i+1}. {group.name} (ID: {group.id})")
        
        # Test mesajı gönder
        if groups:
            test_group = groups[0]
            test_message = "🤖 Test mesajı - Spam sistemi çalışıyor mu?"
            print(f"\n📤 Test mesajı gönderiliyor: {test_group.name}")
            
            try:
                await client.send_message(test_group.id, test_message)
                print(f"✅ Mesaj başarıyla gönderildi!")
            except Exception as e:
                print(f"❌ Mesaj gönderilemedi: {e}")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()
        print("🔌 Bağlantı kapatıldı")

if __name__ == "__main__":
    asyncio.run(test_spam()) 