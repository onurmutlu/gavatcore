#!/usr/bin/env python3
"""
🔧 BabaGAVAT Session Fixer
"""

import asyncio
import os
import shutil
from datetime import datetime
from telethon import TelegramClient
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, GAVATCORE_SYSTEM_PHONE

async def fix_babagavat_session():
    """BabaGAVAT session'ı onar"""
    
    print("""
🔧 BABAGAVAT SESSION FIX
💀 Session sorununu çözüyoruz...
    """)
    
    session_path = "sessions/babagavat_conversation"
    
    # 1. Önce mevcut session'ın yedeğini al
    if os.path.exists(f"{session_path}.session"):
        backup_name = f"{session_path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.session"
        shutil.copy(f"{session_path}.session", backup_name)
        print(f"✅ Yedek alındı: {backup_name}")
    
    # 2. Eski session dosyalarını temizle
    try:
        if os.path.exists(f"{session_path}.session"):
            os.remove(f"{session_path}.session")
        if os.path.exists(f"{session_path}.session-journal"):
            os.remove(f"{session_path}.session-journal")
        print("✅ Eski session dosyaları temizlendi")
    except Exception as e:
        print(f"⚠️ Temizleme hatası: {e}")
    
    # 3. Yeni session oluştur
    try:
        print("\n📱 Yeni session oluşturuluyor...")
        print(f"   Telefon: {GAVATCORE_SYSTEM_PHONE}")
        
        client = TelegramClient(session_path, TELEGRAM_API_ID, TELEGRAM_API_HASH)
        
        await client.start(phone=GAVATCORE_SYSTEM_PHONE)
        
        me = await client.get_me()
        print(f"\n✅ Session başarıyla oluşturuldu!")
        print(f"👤 Hesap: @{me.username} ({me.first_name})")
        print(f"🆔 ID: {me.id}")
        
        # SpamBot kontrolü
        print("\n🔍 Spam durumu kontrol ediliyor...")
        spambot = await client.get_entity("@SpamBot")
        await client.send_message(spambot, "/start")
        await asyncio.sleep(2)
        
        messages = await client.get_messages(spambot, limit=1)
        if messages and messages[0].text:
            if "no limits" in messages[0].text.lower():
                print("✅ Hesap temiz! Sınırlama yok.")
            elif "limited" in messages[0].text.lower():
                print("⚠️ Hesap sınırlı! Mesaj gönderemez.")
                # Ban süresi bilgisini parse et
                if "until" in messages[0].text:
                    print(f"\n📅 Ban detayı: {messages[0].text}")
        
        await client.disconnect()
        
        print("\n✅ BabaGAVAT session başarıyla düzeltildi!")
        print("🚀 Artık EXTREME MODE'u çalıştırabilirsiniz!")
        
    except Exception as e:
        print(f"❌ Session oluşturma hatası: {e}")
        print("\nÇözüm önerileri:")
        print("1. Telefon numarasını kontrol edin")
        print("2. 2FA varsa şifreyi girin")
        print("3. Telegram'dan gelen kodu girin")

if __name__ == "__main__":
    asyncio.run(fix_babagavat_session()) 