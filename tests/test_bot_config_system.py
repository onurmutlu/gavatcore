#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utilities.bot_config_manager import bot_config_manager
from utilities.log_utils import log_event

async def test_bot_config_system():
    """Bot konfigürasyon sistemini test et"""
    
    print("🔧 BOT KONFİGÜRASYON SİSTEMİ TESİ")
    print("=" * 60)
    
    # Test edilecek bot'lar
    test_bots = ["yayincilara", "babagavat", "nonexistent_bot"]
    
    for bot_username in test_bots:
        print(f"\n🤖 {bot_username.upper()} KONFİGÜRASYON TESİ:")
        print("-" * 40)
        
        # 1. DM Davet Ayarları
        dm_enabled, dm_reason = bot_config_manager.is_dm_invite_enabled(bot_username)
        dm_chance = bot_config_manager.get_dm_invite_chance(bot_username)
        target_group = bot_config_manager.get_target_group(bot_username)
        
        print(f"📤 DM Davet Durumu: {'✅ Aktif' if dm_enabled else '❌ Devre Dışı'}")
        print(f"📝 DM Davet Sebebi: {dm_reason}")
        print(f"🎲 DM Davet Şansı: {dm_chance*100:.0f}%")
        print(f"🎯 Hedef Grup: {target_group}")
        
        # 2. Spam Koruması Ayarları
        spam_enabled = bot_config_manager.is_spam_protection_enabled(bot_username)
        spam_type = bot_config_manager.get_spam_protection_type(bot_username)
        max_msg_per_min = bot_config_manager.get_max_messages_per_minute(bot_username)
        
        print(f"🛡️ Spam Koruması: {'✅ Aktif' if spam_enabled else '❌ Devre Dışı'}")
        print(f"🔧 Spam Koruması Türü: {spam_type}")
        print(f"⏱️ Max Mesaj/Dakika: {max_msg_per_min}")
        
        # 3. Yanıt ve Menü Ayarları
        reply_mode = bot_config_manager.get_reply_mode(bot_username)
        auto_menu_enabled, auto_menu_threshold = bot_config_manager.get_auto_menu_settings(bot_username)
        vip_price = bot_config_manager.get_vip_price(bot_username)
        
        print(f"💬 Yanıt Modu: {reply_mode}")
        print(f"🍽️ Otomatik Menü: {'✅ Aktif' if auto_menu_enabled else '❌ Devre Dışı'} (eşik: {auto_menu_threshold})")
        print(f"💎 VIP Fiyat: {vip_price}₺")
        
        # 4. Özel Kısıtlamalar
        restrictions = bot_config_manager.get_special_restrictions(bot_username)
        print(f"🚫 Özel Kısıtlamalar:")
        if restrictions:
            for key, value in restrictions.items():
                print(f"   - {key}: {value}")
        else:
            print("   - Kısıtlama yok")
    
    # ===== KONFİGÜRASYON GÜNCELLEMESİ TESTİ =====
    print(f"\n🔄 KONFİGÜRASYON GÜNCELLEMESİ TESTİ:")
    print("-" * 50)
    
    # Test bot için yeni ayarlar
    test_bot = "test_bot"
    test_updates = {
        "dm_invite_enabled": False,
        "dm_invite_reason": "Test amaçlı devre dışı",
        "spam_protection_type": "enhanced",
        "max_messages_per_minute": 1,
        "reply_mode": "gpt",
        "vip_price": "500"
    }
    
    print(f"🤖 {test_bot} için yeni ayarlar uygulanıyor...")
    success = bot_config_manager.update_bot_config(test_bot, test_updates)
    
    if success:
        print("✅ Konfigürasyon güncelleme başarılı!")
        
        # Güncellenmiş ayarları kontrol et
        print(f"\n📋 {test_bot.upper()} GÜNCELLENMİŞ AYARLAR:")
        dm_enabled, dm_reason = bot_config_manager.is_dm_invite_enabled(test_bot)
        spam_type = bot_config_manager.get_spam_protection_type(test_bot)
        max_msg = bot_config_manager.get_max_messages_per_minute(test_bot)
        reply_mode = bot_config_manager.get_reply_mode(test_bot)
        vip_price = bot_config_manager.get_vip_price(test_bot)
        
        print(f"📤 DM Davet: {dm_enabled} ({dm_reason})")
        print(f"🔧 Spam Türü: {spam_type}")
        print(f"⏱️ Max Mesaj: {max_msg}")
        print(f"💬 Yanıt Modu: {reply_mode}")
        print(f"💎 VIP Fiyat: {vip_price}₺")
    else:
        print("❌ Konfigürasyon güncelleme başarısız!")
    
    # ===== CACHE TESTİ =====
    print(f"\n💾 CACHE TESTİ:")
    print("-" * 30)
    
    # İlk okuma
    start_time = time.time()
    config1 = bot_config_manager.get_bot_config("babagavat")
    first_read_time = time.time() - start_time
    
    # İkinci okuma (cache'den)
    start_time = time.time()
    config2 = bot_config_manager.get_bot_config("babagavat")
    second_read_time = time.time() - start_time
    
    print(f"📖 İlk okuma süresi: {first_read_time*1000:.2f}ms")
    print(f"💨 Cache okuma süresi: {second_read_time*1000:.2f}ms")
    print(f"⚡ Hızlanma: {first_read_time/second_read_time:.1f}x")
    
    # ===== TÜM BOT KONFİGÜRASYONLARI =====
    print(f"\n📊 TÜM BOT KONFİGÜRASYONLARI:")
    print("-" * 40)
    
    all_configs = bot_config_manager.get_all_bot_configs()
    print(f"📋 Toplam {len(all_configs)} bot konfigürasyonu:")
    
    for bot_name, config in all_configs.items():
        dm_enabled = config.get("dm_invite_enabled", True)
        spam_type = config.get("spam_protection_type", "standard")
        reply_mode = config.get("reply_mode", "manualplus")
        
        status_icon = "✅" if dm_enabled else "❌"
        spam_icon = "🔥" if spam_type == "enhanced" else "🛡️"
        
        print(f"   {status_icon} {bot_name}: {spam_icon} {spam_type}, 💬 {reply_mode}")
    
    print(f"\n🎉 BOT KONFİGÜRASYON SİSTEMİ TESİ TAMAMLANDI!")

if __name__ == "__main__":
    import time
    asyncio.run(test_bot_config_system()) 