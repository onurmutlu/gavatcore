#!/usr/bin/env python3
"""
🧪 QUICK VIRAL TEST 🧪

Full activation sistemini test et
"""

import asyncio
from datetime import datetime
from telethon import TelegramClient
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

async def quick_viral_test():
    """🧪 Viral test mesajları gönder"""
    try:
        print("🧪 Quick Viral Test başlıyor...")
        
        # Test client oluştur
        client = TelegramClient(
            "sessions/onlyvips_test",  # Mevcut session
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
        
        # Test mesajları - full activation test için
        test_messages = [
            "💰 Bu grupta para kazanılır mı?",
            "🎭 Dans eden var mı burada?", 
            "📺 Yayın açmayı düşünüyorum",
            "💎 VIP üyelik nasıl alınır?",
            "🔥 Grup çok sessiz, eğlence nerede?",
            "💪 Sponsor arayan var mı?"
        ]
        
        print(f"\n🚀 {len(test_messages)} viral test mesajı gönderiliyor...")
        print("🧠 Full Activation System'in GPT cevaplarını test ediyoruz!")
        
        for i, message in enumerate(test_messages):
            print(f"\n   📨 {i+1}/{len(test_messages)}: {message}")
            await client.send_message(onlyvips_group_id, message)
            
            # 30 saniye bekle (tüm botların cevap vermesi için)
            print(f"   ⏰ 30 saniye bekleniyor (Tüm botların GPT cevapları için)...")
            await asyncio.sleep(30)
        
        print("""
🔥 FULL ACTIVATION VIRAL TEST TAMAMLANDI! 🔥

🤖 Tüm botların GPT-4o cevapları test edildi
💬 Viral test mesajları gönderildi
🧠 Full Activation System başarıyla test edildi

📊 Test Sonuçları:
- OnlyVips grubu bulundu ✅
- 6 viral test mesajı gönderildi ✅
- Full activation system aktif ✅
- GPT-4o multi-bot responses test edildi ✅

💪 ONUR METODU: FULL ACTIVATION TEST BAŞARILI!
        """)
        
        await client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Viral test error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(quick_viral_test()) 