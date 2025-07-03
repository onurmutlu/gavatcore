#!/usr/bin/env python3
"""
🧪 SPAM-AWARE SYSTEM TEST LAUNCHER 🧪

Bu script, SPAM-aware sistemini test eder ve nasıl çalıştığını kontrol eder.
"""

import asyncio
import sys
from datetime import datetime
from spam_aware_full_bot_system import SpamAwareFullBotSystem

async def test_system():
    """Sistemi test et"""
    print("🧪 SPAM-Aware System Test Başlatılıyor...")
    print("=" * 50)
    
    system = SpamAwareFullBotSystem()
    
    try:
        # Sistemi başlat
        print("🚀 Sistem başlatılıyor...")
        if await system.initialize():
            print("✅ Sistem başarıyla başlatıldı!")
            
            # Bot durumlarını göster
            print("\n📊 Bot Durumları:")
            for bot_name, bot_data in system.bot_clients.items():
                status = bot_data["status"]
                me = bot_data["me"]
                personality = bot_data["config"]["personality"]
                
                status_emoji = "✅" if status == "active" else "⚠️"
                print(f"  {status_emoji} {bot_name}: @{me.username} - {status}")
                print(f"     Personality: {personality}")
            
            # SPAM durumlarını göster
            print(f"\n🛡️ SPAM Durumları:")
            for bot_name, spam_status in system.spam_status.items():
                banned = spam_status.get("banned", False)
                emoji = "🔴" if banned else "🟢"
                print(f"  {emoji} {bot_name}: {'SPAM Kısıtlaması' if banned else 'Temiz'}")
            
            print("\n💡 Sistem Özellikleri:")
            print("  🔹 Tüm botlar aktif ve hazır")
            print("  🔹 SPAM-aware contact management")
            print("  🔹 'DM' reply'i ile otomatik contact ekleme")
            print("  🔹 GPT-4o ile akıllı sohbet")
            print("  🔹 Grup içinde yönlendirme mesajları")
            
            print("\n📋 Kullanım Talimatları:")
            print("  1. Grup'ta bir bot'a reply yapın")
            print("  2. Mesajda 'DM' veya 'mesaj' yazın")
            print("  3. Bot sizi otomatik contact'a ekleyecek")
            print("  4. 'Ekledim, DM başlat' mesajı alacaksınız")
            print("  5. Bot'a DM atarak sohbet edebilirsiniz")
            
            print(f"\n🎯 Target Groups:")
            for group in system.target_groups:
                print(f"  📢 {group}")
            
            print(f"\n📱 Contact Database: {system.contact_database}")
            
            print("\n🚀 Sistem çalışıyor... (Ctrl+C ile durdurun)")
            print("=" * 50)
            
            # Sistemi çalıştır (test modunda 30 saniye)
            try:
                await asyncio.wait_for(system.run_system(), timeout=30)
            except asyncio.TimeoutError:
                print("\n⏰ Test tamamlandı (30 saniye)")
                await system._cleanup()
                
        else:
            print("❌ Sistem başlatılamadı!")
            return False
            
    except KeyboardInterrupt:
        print("\n👋 Test kullanıcı tarafından durduruldu")
        await system._cleanup()
    except Exception as e:
        print(f"\n❌ Test hatası: {e}")
        return False
    
    print("\n✅ Test tamamlandı!")
    return True

async def quick_contact_test():
    """Hızlı contact ekleme testi"""
    print("\n🔬 Hızlı Contact Test...")
    
    # Bu test gerçek contact ekleme API'sini test etmez
    # Sadece sistem mantığını kontrol eder
    
    system = SpamAwareFullBotSystem()
    
    # Mock user data
    class MockUser:
        def __init__(self):
            self.id = 123456789
            self.first_name = "Test"
            self.last_name = "User"
            self.access_hash = 123456789
    
    mock_user = MockUser()
    
    print(f"  📝 Mock User: {mock_user.first_name} ({mock_user.id})")
    print("  🧪 Contact ekleme mantığı test ediliyor...")
    
    # Mock bot configurations için contact response test
    bot_configs = {
        "babagavat": {"personality": "BabaGAVAT - Sokak zekası uzmanı, güvenilir rehber"},
        "xxxgeisha": {"personality": "XXXGeisha - Zarif, akıllı, çekici sohbet uzmanı"},
        "yayincilara": {"personality": "YayıncıLara - Enerjik, eğlenceli, popüler kişilik"}
    }
    
    # Mock bot_clients için test
    for bot_name, config in bot_configs.items():
        system.bot_clients[bot_name] = {"config": config}
        response = await system._generate_contact_added_response(mock_user, bot_name)
        print(f"  💬 {bot_name}: {response[:60]}...")
    
    print("  ✅ Contact test tamamlandı!")
    
    # Contact ekleme akışını simüle et
    print("\n🔄 Contact Ekleme Akışı:")
    print("  1. 👤 Kullanıcı grup'ta bot'a reply yapar: 'DM'")
    print("  2. 📞 Bot kullanıcıyı contact listesine eklemeye çalışır")
    print("  3. ✅ Başarılıysa: 'Ekledim, DM başlat' mesajı")
    print("  4. ❌ Başarısızsa: 'Engel var, bana DM yaz' mesajı")
    print("  5. 💬 Kullanıcı DM başlattığında normal sohbet")
    
    print("\n🎯 SPAM-Aware Logic:")
    print("  🔹 Bot SPAM kısıtlamasında değilse: Normal group + contact ekleme")
    print("  🔹 Bot SPAM kısıtlamasındaysa: Sadece DM yönlendirme")
    print("  🔹 Contact ekleme başarısızsa: DM başlatma talimatı")
    print("  🔹 24 saat sonra otomatik cleanup")
    
    print("\n📊 Expected Database Schema:")
    print("  contacts: user_id, bot_name, group_id, contact_added, dm_started")
    print("  spam_tracking: bot_name, is_banned, ban_until, last_check")

if __name__ == "__main__":
    print("🔥 SPAM-AWARE FULL BOT SYSTEM TEST 🔥")
    print("ONUR METODU - Contact Management Test")
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        asyncio.run(quick_contact_test())
    else:
        asyncio.run(test_system()) 