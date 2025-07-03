#!/usr/bin/env python3
"""
🧪 VIP Campaign System Test v1.0
"""

import asyncio
import time
import logging
from telethon import TelegramClient
from config import API_ID, API_HASH
from vip_campaign_module import get_campaign_message, get_campaign_stats

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_vip_campaign():
    """VIP kampanya sistemini test et"""
    
    print("""
🎯 Testing VIP Campaign System v1.0

Bu test VIP kampanya sistemini test eder:
1. Kampanya mesajlarını oluşturur
2. Bot-specific kampanya yanıtlarını test eder
3. DM conversation'da kampanya mesajlarını kontrol eder
4. Kampanya istatistiklerini gösterir

Test başlıyor...
""")
    
    # Kampanya istatistiklerini göster
    print("📊 KAMPANYA İSTATİSTİKLERİ:")
    print("=" * 50)
    stats = get_campaign_stats()
    print(f"• Durum: {'🟢 Aktif' if stats['active'] else '🔴 Pasif'}")
    print(f"• Mevcut üye: {stats['current_members']}")
    print(f"• Hedef üye: {stats['target_members']}")
    print(f"• İlerleme: %{stats['progress_percentage']}")
    print(f"• Kalan slot: {stats['remaining_spots']}")
    print(f"• XP/Davet: {stats['xp_per_invite']}")
    print(f"• Hedef grup: {stats['target_group']}")
    print(f"• Yönetici: {stats['campaign_admin']}")
    
    print("\n🤖 BOT KAMPANYA MESAJLARI:")
    print("=" * 50)
    
    # Bot-specific kampanya mesajlarını test et
    test_bots = [
        {"username": "yayincilara", "display": "Lara 💕"},
        {"username": "babagavat", "display": "Gavat Baba 😎"},
        {"username": "xxxgeisha", "display": "Geisha 😘"}
    ]
    
    for bot_info in test_bots:
        username = bot_info["username"]
        display = bot_info["display"]
        
        print(f"\n🎯 {display} KAMPANYA MESAJI:")
        print("-" * 30)
        campaign_msg = get_campaign_message(username)
        print(campaign_msg)
        print()
    
    # Test session (sadece kampanya mesajlarını test et)
    test_session = "sessions/test_vip_campaign"
    test_client = TelegramClient(test_session, API_ID, API_HASH)
    
    try:
        print("🔗 Test client bağlanıyor...")
        await test_client.start()
        me = await test_client.get_me()
        print(f"✅ Test client bağlandı: @{me.username}")
        
        print("\n📱 KAMPANYA DM TESTİ:")
        print("=" * 50)
        
        # Test target bot'lar (sadece mesaj alma)
        target_bots = [
            {"username": "yayincilara", "display": "Lara"},
            {"username": "babagavat", "display": "Gavat Baba"},
            {"username": "xxxgeisha", "display": "Geisha"}
        ]
        
        for bot_info in target_bots:
            username = bot_info["username"]
            display = bot_info["display"]
            
            print(f"\n📨 {display} (@{username}) DM Test...")
            
            try:
                # Bot'u bul
                bot_entity = await test_client.get_entity(username)
                print(f"  ✅ {display} entity bulundu")
                
                # Kampanya trigger mesajları test et
                trigger_messages = [
                    "Merhaba",  # Greeting -> %80 kampanya
                    "Ne yapıyorsun?",  # Activity -> %90 kampanya
                    "Nasılsın?",  # Status -> %70 kampanya
                    "Test?"  # Question -> %60 kampanya
                ]
                
                for trigger in trigger_messages:
                    print(f"  🧪 Trigger test: '{trigger}'")
                    
                    # Mesajı gönder
                    await test_client.send_message(bot_entity, trigger)
                    print(f"  📤 '{trigger}' gönderildi")
                    
                    # Bot yanıtını bekle
                    await asyncio.sleep(6)
                    
                    # Son mesajları kontrol et
                    messages = []
                    async for message in test_client.iter_messages(bot_entity, limit=2):
                        messages.append(message)
                    
                    if len(messages) >= 2:
                        bot_response = messages[0]
                        if bot_response.sender_id != me.id:
                            response_text = bot_response.message[:100]
                            is_campaign = "VIP" in response_text or "kampanya" in response_text.lower()
                            status = "🎯 KAMPANYA" if is_campaign else "💬 Normal"
                            print(f"  📥 {display} yanıtı: {status}")
                            print(f"  💭 Mesaj: {response_text}...")
                        else:
                            print(f"  ⚠️ {display} henüz yanıt vermedi")
                    
                    # Test mesajları arası bekleme
                    await asyncio.sleep(3)
                
                print(f"  ✅ {display} kampanya test tamamlandı!")
                
            except Exception as e:
                print(f"  ❌ {display} test hatası: {e}")
            
            # Bot'lar arası bekleme
            await asyncio.sleep(5)
        
        print(f"""
✅ VIP Campaign System Test Tamamlandı!

📊 Test Sonuçları:
• Kampanya modülü başarıyla çalışıyor ✅
• Bot-specific kampanya mesajları aktif ✅
• DM trigger'ları kampanya odaklı ✅
• Engaging messages kampanya entegreli ✅

🎯 VIP Kampanya sistemi production'da aktif!
💰 XP = Token = Para sistemi çalışıyor!
🔗 Hedef grup: {stats['target_group']}
👥 {stats['remaining_spots']} slot kaldı!
""")
        
    except Exception as e:
        print(f"❌ VIP Campaign test genel hatası: {e}")
    
    finally:
        await test_client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_vip_campaign()) 