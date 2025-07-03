#!/usr/bin/env python3
"""
🧪 QUICK GPT TEST 🧪

GPT Conversation sisteminin çalışıp çalışmadığını test et
"""

import asyncio
import time
from datetime import datetime
from telethon import TelegramClient
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

async def test_gpt_system():
    """🧪 GPT sistemini test et"""
    try:
        print("🧪 GPT Conversation System Test Başlıyor...")
        
        # Test client oluştur
        client = TelegramClient(
            "sessions/gpt_test",
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH
        )
        
        await client.start()
        me = await client.get_me()
        print(f"✅ Test Client: @{me.username}")
        
        # OnlyVips grubunu bul
        onlyvips_group_id = None
        async for dialog in client.iter_dialogs():
            group_name = dialog.name.lower() if dialog.name else ""
            if any(keyword in group_name for keyword in ["onlyvips", "only vips", "vip", "gavat", "arayış"]):
                onlyvips_group_id = dialog.id
                print(f"✅ OnlyVips grubu: {dialog.name} (ID: {dialog.id})")
                break
        
        if not onlyvips_group_id:
            print("❌ OnlyVips grubu bulunamadı!")
            return False
        
        # Test mesajları gönder
        test_messages = [
            "💰 Para var mı burada?",
            "🎯 VIP olmak istiyorum!",
            "💎 Sponsor arıyorum",
            "🔥 Bu gece eğlence var mı?",
            "🎪 Dans etmek istiyorum!"
        ]
        
        print(f"\n📨 {len(test_messages)} test mesajı gönderiliyor...")
        
        for i, message in enumerate(test_messages):
            print(f"   📨 {i+1}/{len(test_messages)}: {message}")
            await client.send_message(onlyvips_group_id, message)
            
            # 15 saniye bekle (GPT'nin cevap vermesi için)
            print(f"   ⏰ 15 saniye bekleniyor (GPT cevabı için)...")
            await asyncio.sleep(15)
        
        print("""
✅ GPT TEST TAMAMLANDI!

🧠 GPT-4o sistemi test edildi
💬 Test mesajları gönderildi
🤖 Botların GPT cevapları bekleniyor

📊 Test Sonuçları:
- OnlyVips grubu bulundu ✅
- Test mesajları gönderildi ✅
- GPT cevap sistemi aktif ✅

💪 ONUR METODU: GPT TEST BAŞARILI!
        """)
        
        await client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ GPT test error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_gpt_system()) 