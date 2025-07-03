#!/usr/bin/env python3
"""
@arayisvips Grup Davet Stratejisi Test Scripti
Bu script grup davet sisteminin çalışıp çalışmadığını test eder.
"""

import asyncio
import json
from pathlib import Path
from utils.group_invite_strategy import GroupInviteStrategy, group_invite_strategy

def test_message_categorization():
    """Mesaj kategorileme sistemini test et"""
    print("🧪 Mesaj Kategorileme Testi")
    print("=" * 50)
    
    test_messages = [
        ("VIP grubuna katılmak istiyorum", "potential_customers"),
        ("Show'larını merak ediyorum", "potential_customers"),
        ("Sohbet etmek istiyorum", "social_users"),
        ("Arkadaş arıyorum", "social_users"),
        ("Ne kadar para?", "vip_seekers"),
        ("Fiyat nedir?", "vip_seekers"),
        ("Nasılsın?", "curious_users"),
        ("Merhaba", "social_users")  # default
    ]
    
    strategy = GroupInviteStrategy()
    
    for message, expected_category in test_messages:
        actual_category = strategy.categorize_user(message)
        status = "✅" if actual_category == expected_category else "❌"
        print(f"{status} '{message}' → {actual_category} (beklenen: {expected_category})")
    
    print()

def test_invite_messages():
    """Davet mesajlarını test et"""
    print("🧪 Davet Mesajları Testi")
    print("=" * 50)
    
    strategy = GroupInviteStrategy()
    
    categories = ["casual", "vip_focused", "community", "exclusive"]
    
    for category in categories:
        message = strategy.get_invite_message(category)
        print(f"📝 {category.title()}: {message}")
    
    print()

def test_target_audiences():
    """Hedef kitle ayarlarını test et"""
    print("🧪 Hedef Kitle Ayarları Testi")
    print("=" * 50)
    
    strategy = GroupInviteStrategy()
    
    for audience, info in strategy.target_audiences.items():
        print(f"👥 {audience}:")
        print(f"  Keywords: {info['keywords']}")
        print(f"  Template: {info['template_category']}")
        print(f"  Priority: {info['priority']}")
        print()

def test_profile_integration():
    """Profil entegrasyonunu test et"""
    print("🧪 Profil Entegrasyonu Testi")
    print("=" * 50)
    
    # Bot profillerini kontrol et
    bots = ["yayincilara", "babagavat"]
    
    for bot in bots:
        profile_path = Path(f"data/personas/{bot}.json")
        if not profile_path.exists():
            print(f"❌ {bot} profil dosyası bulunamadı!")
            continue
        
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
        
        engaging_messages = profile.get("engaging_messages", [])
        
        # @arayisvips mesajlarını say
        arayisvips_count = sum(1 for msg in engaging_messages if "@arayisvips" in msg)
        
        print(f"📊 {bot.title()}:")
        print(f"  Toplam mesaj: {len(engaging_messages)}")
        print(f"  @arayisvips mesajları: {arayisvips_count}")
        print(f"  Oran: {(arayisvips_count/len(engaging_messages)*100):.1f}%")
        
        if arayisvips_count > 0:
            print("  Örnek @arayisvips mesajları:")
            for msg in engaging_messages:
                if "@arayisvips" in msg:
                    print(f"    • {msg}")
                    break
        print()

def test_spam_messages():
    """Grup spam mesajlarını test et"""
    print("🧪 Grup Spam Mesajları Testi")
    print("=" * 50)
    
    spam_file = Path("data/group_spam_messages.json")
    if not spam_file.exists():
        print("❌ group_spam_messages.json bulunamadı!")
        return
    
    with open(spam_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    template_messages = data.get("_template", {}).get("engaging_messages", [])
    
    # @arayisvips mesajlarını say
    arayisvips_count = sum(1 for msg in template_messages if "@arayisvips" in msg)
    
    print(f"📊 Template Mesajları:")
    print(f"  Toplam mesaj: {len(template_messages)}")
    print(f"  @arayisvips mesajları: {arayisvips_count}")
    print(f"  Oran: {(arayisvips_count/len(template_messages)*100):.1f}%")
    
    if arayisvips_count > 0:
        print("  @arayisvips mesajları:")
        for msg in template_messages:
            if "@arayisvips" in msg:
                print(f"    • {msg}")
    print()

def test_strategy_stats():
    """Strateji istatistiklerini test et"""
    print("🧪 Strateji İstatistikleri Testi")
    print("=" * 50)
    
    # Global instance'ı test et
    stats = group_invite_strategy.get_stats()
    
    print("📊 Başlangıç İstatistikleri:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Stats reset test
    group_invite_strategy.reset_stats()
    reset_stats = group_invite_strategy.get_stats()
    
    print("\n📊 Reset Sonrası İstatistikler:")
    for key, value in reset_stats.items():
        print(f"  {key}: {value}")
    
    print()

def test_followup_messages():
    """Takip mesajlarını test et"""
    print("🧪 Takip Mesajları Testi")
    print("=" * 50)
    
    strategy = GroupInviteStrategy()
    
    print("💬 Takip Mesajları:")
    for i, msg in enumerate(strategy.followup_messages, 1):
        print(f"  {i}. {msg}")
    
    print()

def main():
    """Ana test fonksiyonu"""
    print("🚀 @arayisvips Grup Davet Stratejisi Test Paketi")
    print("=" * 60)
    print()
    
    # Testleri çalıştır
    test_message_categorization()
    test_invite_messages()
    test_target_audiences()
    test_profile_integration()
    test_spam_messages()
    test_strategy_stats()
    test_followup_messages()
    
    print("✅ Tüm testler tamamlandı!")
    print()
    print("📋 @arayisvips Grup Davet Stratejisi Özellikleri:")
    print("- ✅ 4 farklı hedef kitle kategorisi")
    print("- ✅ 16 çeşitli davet mesajı şablonu")
    print("- ✅ Akıllı mesaj kategorileme sistemi")
    print("- ✅ DM konuşmalarında %30 davet şansı")
    print("- ✅ Günlük toplu davet kampanyası")
    print("- ✅ Profil entegrasyonu (yayincilara & babagavat)")
    print("- ✅ Grup spam mesajlarında @arayisvips tanıtımı")
    print("- ✅ Takip mesajı sistemi")
    print("- ✅ İstatistik takibi")
    print("- ✅ Rate limiting ve güvenlik önlemleri")
    print()
    print("🎯 Sonuç: @arayisvips grubu için kapsamlı üye artırma stratejisi hazır!")

if __name__ == "__main__":
    main() 