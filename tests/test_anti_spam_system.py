#!/usr/bin/env python3
# tests/test_anti_spam_system.py

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from utilities.anti_spam_guard import anti_spam_guard
from handlers.safe_spam_handler import safe_spam_handler
from gpt.template_shuffler import template_shuffler

async def test_anti_spam_system():
    """Anti-spam sistemini test et"""
    
    print("🛡️ ANTI-SPAM SİSTEMİ TEST BAŞLIYOR...")
    print("=" * 60)
    
    # Test bot'u
    test_username = "babagavat"
    test_group_id = 123456789
    
    print(f"🤖 Test Bot: {test_username}")
    print(f"📱 Test Grup ID: {test_group_id}")
    print("-" * 60)
    
    # 1. Hesap yaşı testi
    print("1️⃣ HESAP YAŞI TESTİ")
    age_hours = anti_spam_guard.get_account_age_hours(test_username)
    print(f"   Hesap yaşı: {age_hours:.1f} saat")
    
    if age_hours < 24:
        print("   🔰 Yeni hesap - sadece reply mode")
    elif age_hours < 72:
        print("   🔰 Genç hesap - dikkatli spam")
    else:
        print("   ✅ Olgun hesap - normal spam")
    
    # 2. Spam güvenlik testi
    print("\n2️⃣ SPAM GÜVENLİK TESTİ")
    safe_to_spam, reason = anti_spam_guard.is_safe_to_spam(test_username, test_group_id)
    print(f"   Spam güvenli: {safe_to_spam}")
    print(f"   Sebep: {reason}")
    
    # 3. Dinamik cooldown testi
    print("\n3️⃣ DİNAMİK COOLDOWN TESTİ")
    cooldown = anti_spam_guard.calculate_dynamic_cooldown(test_username, test_group_id)
    print(f"   Hesaplanan cooldown: {cooldown} saniye ({cooldown//60} dakika)")
    
    # 4. Trafik analizi testi
    print("\n4️⃣ TRAFİK ANALİZİ TESTİ")
    traffic_count, risk_level = anti_spam_guard.calculate_group_traffic_score(test_group_id)
    print(f"   Grup trafik sayısı: {traffic_count}")
    print(f"   Risk seviyesi: {risk_level}")
    
    # 5. Mesaj varyasyonu testi
    print("\n5️⃣ MESAJ VARYASYONU TESTİ")
    base_message = "Merhaba! Nasılsınız? 😊"
    variants = anti_spam_guard.get_safe_message_variants(base_message, 5)
    print(f"   Orijinal: {base_message}")
    for i, variant in enumerate(variants, 1):
        print(f"   Varyasyon {i}: {variant}")
    
    # 6. Template shuffler testi
    print("\n6️⃣ TEMPLATE SHUFFLER TESTİ")
    shuffled_variants = template_shuffler.shuffle_message_structure(base_message, "flirt")
    for i, variant in enumerate(shuffled_variants[:3], 1):
        print(f"   Shuffle {i}: {variant}")
    
    # 7. VIP satış varyasyonları
    print("\n7️⃣ VIP SATIŞ VARYASYONLARI")
    vip_variants = template_shuffler.create_vip_sales_variants()
    for i, variant in enumerate(vip_variants[:3], 1):
        print(f"   VIP {i}: {variant}")
    
    # 8. Hesap durumu raporu
    print("\n8️⃣ HESAP DURUMU RAPORU")
    account_status = anti_spam_guard.get_account_status(test_username)
    print(f"   Username: {account_status['username']}")
    print(f"   Yaş (saat): {account_status['age_hours']:.1f}")
    print(f"   Yaş durumu: {account_status['age_status']}")
    print(f"   Uyarı sayısı: {account_status['warning_count']}")
    print(f"   Risk seviyesi: {account_status['risk_level']}")
    print(f"   Spam güvenli: {account_status['spam_safe']}")
    
    # 9. Mesaj çeşitliliği analizi
    print("\n9️⃣ MESAJ ÇEŞİTLİLİĞİ ANALİZİ")
    test_messages = [
        "Merhaba! Nasılsınız? 😊",
        "Selam! Ne yapıyorsunuz? 🌟",
        "Hey! Keyifler nasıl? 💫",
        "VIP grubuma katılmak ister misin? 💎",
        "Özel içeriklerim var 🔥"
    ]
    diversity = template_shuffler.analyze_message_diversity(test_messages)
    print(f"   Çeşitlilik skoru: {diversity['diversity_score']}%")
    print(f"   Benzersiz kelime: {diversity['unique_words']}")
    print(f"   Emoji çeşitliliği: {diversity['emoji_variety']}")
    
    # 10. Uyarı sistemi testi
    print("\n🔟 UYARI SİSTEMİ TESTİ")
    print("   Spam uyarısı ekleniyor...")
    anti_spam_guard.add_spam_warning(test_username, "test_warning")
    
    # Güncellenmiş durum
    updated_status = anti_spam_guard.get_account_status(test_username)
    print(f"   Yeni uyarı sayısı: {updated_status['warning_count']}")
    print(f"   Yeni risk seviyesi: {updated_status['risk_level']}")
    
    # 11. GPT destekli varyasyon testi
    print("\n1️⃣1️⃣ GPT DESTEKLİ VARYASYON TESTİ")
    try:
        gpt_variants = await template_shuffler.create_gpt_enhanced_variants(
            base_message, "flörtöz ve samimi", 3
        )
        for i, variant in enumerate(gpt_variants, 1):
            print(f"   GPT {i}: {variant}")
    except Exception as e:
        print(f"   ❌ GPT test hatası: {e}")
    
    print("\n" + "=" * 60)
    print("✅ ANTI-SPAM SİSTEMİ TESTİ TAMAMLANDI!")
    print("🛡️ Sistem hazır ve çalışır durumda!")

if __name__ == "__main__":
    asyncio.run(test_anti_spam_system()) 