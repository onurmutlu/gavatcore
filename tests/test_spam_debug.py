#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.anti_spam_guard import anti_spam_guard
from utils.log_utils import log_event

async def test_spam_debug():
    """Anti-spam guard debug testi"""
    
    print("🔍 ANTI-SPAM GUARD DEBUG TESİ")
    print("=" * 50)
    
    # Test edilecek bot'lar
    test_bots = ["yayincilara", "babagavat"]
    
    for username in test_bots:
        print(f"\n🤖 {username.upper()} ANALİZİ:")
        print("-" * 30)
        
        # Hesap yaşını kontrol et
        age_hours = anti_spam_guard.get_account_age_hours(username)
        print(f"📅 Hesap yaşı: {age_hours:.1f} saat ({age_hours/24:.1f} gün)")
        
        # Uyarı sayısını kontrol et
        warnings = anti_spam_guard.spam_warnings.get(username, [])
        print(f"⚠️ Uyarı sayısı: {len(warnings)}")
        
        if warnings:
            for i, warning in enumerate(warnings[-3:]):  # Son 3 uyarı
                print(f"   {i+1}. {warning.get('type', 'unknown')} - {warning.get('date', 'unknown')}")
        
        # Genel spam güvenlik kontrolü
        safe_general, reason_general = anti_spam_guard.is_safe_to_spam(username, 0)
        print(f"🛡️ Genel spam güvenliği: {safe_general}")
        print(f"📝 Sebep: {reason_general}")
        
        # Test grup için kontrol
        test_group_id = -1001234567890  # Örnek grup ID
        safe_group, reason_group = anti_spam_guard.is_safe_to_spam(username, test_group_id)
        print(f"🏠 Grup spam güvenliği: {safe_group}")
        print(f"📝 Grup sebep: {reason_group}")
        
        # Hesap durumu raporu
        status = anti_spam_guard.get_account_status(username)
        print(f"📊 Hesap durumu:")
        print(f"   - Yaş durumu: {status['age_status']}")
        print(f"   - Risk seviyesi: {status['risk_level']}")
        print(f"   - Spam güvenli: {status['spam_safe']}")
        print(f"   - Toplam mesaj: {status['total_messages']}")
    
    # ===== YENİ: ENHANCED SPAM KORUMASI TESTİ =====
    print(f"\n🔥 ENHANCED SPAM KORUMASI TESTİ:")
    print("-" * 50)
    
    test_group_id = -1001234567890
    
    # Babagavat için enhanced spam koruması testi
    print(f"\n🤖 BABAGAVAT ENHANCED SPAM TESTİ:")
    
    # 1. İlk mesaj - geçmeli
    safe1, reason1 = anti_spam_guard.check_enhanced_spam_protection("babagavat", test_group_id)
    print(f"1️⃣ İlk mesaj: {safe1} - {reason1}")
    
    if safe1:
        anti_spam_guard.record_enhanced_spam_message("babagavat", test_group_id)
    
    # 2. İkinci mesaj - geçmeli
    safe2, reason2 = anti_spam_guard.check_enhanced_spam_protection("babagavat", test_group_id)
    print(f"2️⃣ İkinci mesaj: {safe2} - {reason2}")
    
    if safe2:
        anti_spam_guard.record_enhanced_spam_message("babagavat", test_group_id)
    
    # 3. Üçüncü mesaj - ENGELLENMELİ
    safe3, reason3 = anti_spam_guard.check_enhanced_spam_protection("babagavat", test_group_id)
    print(f"3️⃣ Üçüncü mesaj: {safe3} - {reason3}")
    
    # 4. Dördüncü mesaj - ENGELLENMELİ
    safe4, reason4 = anti_spam_guard.check_enhanced_spam_protection("babagavat", test_group_id)
    print(f"4️⃣ Dördüncü mesaj: {safe4} - {reason4}")
    
    # 5. Yayincilara için test (enhanced değil, etkilenmemeli)
    safe_lara, reason_lara = anti_spam_guard.check_enhanced_spam_protection("yayincilara", test_group_id)
    print(f"5️⃣ Yayincilara testi: {safe_lara} - {reason_lara}")
    
    print(f"\n✅ ENHANCED SPAM KORUMASI SONUCU:")
    if not safe3 and not safe4 and safe_lara:
        print("🎯 Başarılı! Babagavat enhanced spam koruması ile 1 dakikada 2 mesajdan sonra engellendi")
        print("🎯 Yayincilara enhanced spam koruması yok, etkilenmedi")
    else:
        print("❌ Başarısız! Enhanced spam koruması çalışmıyor")
    
    # ===== BOT KONFİGÜRASYON TESTİ =====
    print(f"\n⚙️ BOT KONFİGÜRASYON TESTİ:")
    print("-" * 50)
    
    from utils.bot_config_manager import bot_config_manager
    
    for username in test_bots:
        print(f"\n🤖 {username.upper()} KONFİGÜRASYON:")
        
        # DM davet ayarları
        dm_enabled, dm_reason = bot_config_manager.is_dm_invite_enabled(username)
        dm_chance = bot_config_manager.get_dm_invite_chance(username)
        target_group = bot_config_manager.get_target_group(username)
        
        print(f"📤 DM Davet: {dm_enabled} ({dm_reason})")
        print(f"🎲 DM Şans: {dm_chance*100:.0f}%")
        print(f"🎯 Hedef Grup: {target_group}")
        
        # Spam koruması ayarları
        spam_enabled = bot_config_manager.is_spam_protection_enabled(username)
        spam_type = bot_config_manager.get_spam_protection_type(username)
        max_msg_per_min = bot_config_manager.get_max_messages_per_minute(username)
        
        print(f"🛡️ Spam Koruması: {spam_enabled}")
        print(f"🔧 Spam Türü: {spam_type}")
        print(f"⏱️ Max Mesaj/Dakika: {max_msg_per_min}")
        
        # Diğer ayarlar
        reply_mode = bot_config_manager.get_reply_mode(username)
        auto_menu_enabled, auto_menu_threshold = bot_config_manager.get_auto_menu_settings(username)
        vip_price = bot_config_manager.get_vip_price(username)
        
        print(f"💬 Yanıt Modu: {reply_mode}")
        print(f"🍽️ Otomatik Menü: {auto_menu_enabled} (eşik: {auto_menu_threshold})")
        print(f"💎 VIP Fiyat: {vip_price}₺")
    
    # Metadata kontrolü
    print(f"\n🔧 SORUN TESPİTİ:")
    print("-" * 30)
    
    # Metadata dosyası var mı?
    from pathlib import Path
    metadata_file = Path("data/account_metadata.json")
    if metadata_file.exists():
        import json
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        print(f"📁 Metadata dosyası mevcut: {len(metadata)} hesap")
        for username, data in metadata.items():
            print(f"   ✅ {username}: {data}")
    else:
        print("❌ Metadata dosyası bulunamadı")
    
    print(f"\n💡 ÖNERİLER:")
    print("-" * 30)
    print("1. Hesap yaşları 24 saatten büyük olmalı")
    print("2. Uyarı sayısı 3'ten az olmalı")
    print("3. Metadata dosyası doğru olmalı")
    print("4. Bot profillerinde created_at doğru olmalı")

if __name__ == "__main__":
    asyncio.run(test_spam_debug()) 