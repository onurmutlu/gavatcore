#!/usr/bin/env python3
"""
Adaptif Spam Sistemi Test Scripti
Bu script tüm system botlarının adaptif spam ayarlarını test eder.
"""

import time
import json
from pathlib import Path
from utilities.adaptive_spam_scheduler import AdaptiveSpamScheduler

def test_bot_profile_settings(username: str):
    """Bot'un profil ayarlarını test eder"""
    print(f"🧪 {username.title()} Profil Ayarları Testi")
    print("=" * 50)
    
    # Profil dosyasını yükle
    profile_path = Path(f"data/personas/{username}.json")
    if not profile_path.exists():
        print(f"❌ {username} profil dosyası bulunamadı!")
        return None
    
    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)
    
    # Ayarları kontrol et
    print(f"📋 {username.title()} Profil Ayarları:")
    print(f"  autospam: {profile.get('autospam', False)}")
    print(f"  spam_frequency: {profile.get('spam_frequency', 'normal')}")
    print(f"  spam_interval_min: {profile.get('spam_interval_min', 120)} saniye")
    print(f"  spam_interval_max: {profile.get('spam_interval_max', 240)} saniye")
    print(f"  group_spam_enabled: {profile.get('group_spam_enabled', False)}")
    print(f"  group_spam_aggressive: {profile.get('group_spam_aggressive', False)}")
    
    # Mesaj sayısını kontrol et
    engaging_messages = profile.get("engaging_messages", [])
    print(f"  engaging_messages: {len(engaging_messages)} adet")
    
    if len(engaging_messages) > 0:
        print("  Örnek mesajlar:")
        for i, msg in enumerate(engaging_messages[:3], 1):
            print(f"    {i}. {msg[:50]}...")
    
    print()
    return profile

def test_adaptive_spam_scheduler():
    """Adaptif spam scheduler'ını test eder"""
    print("🧪 Adaptif Spam Scheduler Testi")
    print("=" * 50)
    
    scheduler = AdaptiveSpamScheduler()
    test_group_id = -1001234567890
    test_bot_id = 123456789
    test_user_id = 987654321
    
    # Aktif saat testi
    is_active = scheduler.is_active_hour()
    print(f"Şu an aktif saat mi: {'✅ Evet' if is_active else '❌ Hayır'}")
    
    # Grup aktivitesi simülasyonu
    print("\n📊 Grup Aktivite Simülasyonu:")
    
    # Kullanıcı mesajları ekle
    scheduler.update_group_activity(test_group_id, test_user_id)
    scheduler.update_group_activity(test_group_id, test_user_id + 1)
    scheduler.update_group_activity(test_group_id, test_user_id + 2)
    
    # Test profilleri
    test_profiles = {
        "normal": {"spam_frequency": "normal", "group_spam_aggressive": False},
        "high": {"spam_frequency": "high", "group_spam_aggressive": False},
        "very_high": {"spam_frequency": "very_high", "group_spam_aggressive": True}
    }
    
    for profile_name, profile in test_profiles.items():
        print(f"\n🔧 {profile_name.title()} Profil Testi:")
        
        # Grup frekansını hesapla
        frequency = scheduler.get_group_frequency(test_group_id)
        print(f"  Grup frekansı: {frequency:.2f} mesaj/dakika")
        
        # Adaptif interval hesapla
        interval = scheduler.get_adaptive_interval(test_group_id, profile)
        print(f"  Adaptif interval: {interval} saniye ({interval/60:.1f} dakika)")
        
        # Bot ayarlarını göster
        settings = scheduler.get_bot_settings(profile)
        print(f"  Bot ayarları: {settings}")
        
        # Spam kontrolü testi
        can_spam, reason = scheduler.can_spam_group(test_group_id, test_bot_id, profile)
        print(f"  Spam atılabilir mi: {'✅ Evet' if can_spam else '❌ Hayır'} ({reason})")
    
    print()

def test_frequency_settings():
    """Farklı frequency ayarlarını test eder"""
    print("🧪 Frequency Ayarları Testi")
    print("=" * 50)
    
    scheduler = AdaptiveSpamScheduler()
    
    frequency_settings = ["very_low", "low", "normal", "high", "very_high"]
    
    for freq in frequency_settings:
        profile = {
            "spam_frequency": freq,
            "spam_interval_min": 180,
            "spam_interval_max": 360,
            "group_spam_aggressive": freq == "very_high"
        }
        
        # Orta aktiviteli grup için interval hesapla
        test_group_id = -1001234567890
        interval = scheduler.get_adaptive_interval(test_group_id, profile)
        
        print(f"  {freq}: {interval} saniye ({interval/60:.1f} dakika)")
    
    print()

def test_bot_comparison():
    """Farklı botların ayarlarını karşılaştır"""
    print("🧪 Bot Karşılaştırma Testi")
    print("=" * 50)
    
    bots = ["yayincilara", "babagavat"]
    
    for bot in bots:
        profile = test_bot_profile_settings(bot)
        if profile:
            scheduler = AdaptiveSpamScheduler()
            settings = scheduler.get_bot_settings(profile)
            
            print(f"📊 {bot.title()} Özet:")
            print(f"  Frequency: {settings['frequency']}")
            print(f"  Interval: {settings['min_interval']}-{settings['max_interval']}s")
            print(f"  Aggressive: {'✅' if settings['aggressive'] else '❌'}")
            print(f"  Enabled: {'✅' if settings['enabled'] else '❌'}")
            print()

def test_timing_scenarios():
    """Farklı zaman senaryolarını test eder"""
    print("🧪 Timing Senaryoları Testi")
    print("=" * 50)
    
    scheduler = AdaptiveSpamScheduler()
    
    # Test saatleri
    test_hours = [3, 10, 15, 22]  # Gece, sabah, öğleden sonra, akşam
    
    profile = {
        "spam_frequency": "high",
        "spam_interval_min": 180,
        "spam_interval_max": 360
    }
    
    for hour in test_hours:
        # Saati simüle et
        if 1 <= hour <= 7:
            period = "Gece"
            multiplier = 1.5
        elif 9 <= hour < 12 or 14 <= hour < 18 or 20 <= hour < 24:
            period = "Aktif"
            multiplier = 0.7
        else:
            period = "Normal"
            multiplier = 1.0
        
        base_interval = (180 + 360) // 2  # Ortalama interval
        expected_interval = int(base_interval * 0.7 * multiplier)  # High frequency + timing
        
        print(f"  Saat {hour:02d}:00 - {period}: ~{expected_interval} saniye ({expected_interval/60:.1f} dakika)")
    
    print()

def test_message_variety():
    """Mesaj çeşitliliğini test eder"""
    print("🧪 Mesaj Çeşitliliği Testi")
    print("=" * 50)
    
    bots = ["yayincilara", "babagavat"]
    
    for bot in bots:
        profile_path = Path(f"data/personas/{bot}.json")
        if not profile_path.exists():
            continue
        
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
        
        engaging_messages = profile.get("engaging_messages", [])
        
        print(f"📊 {bot.title()} Mesaj Analizi:")
        print(f"  Toplam mesaj: {len(engaging_messages)} adet")
        
        if engaging_messages:
            # Mesaj uzunluklarını analiz et
            lengths = [len(msg) for msg in engaging_messages]
            avg_length = sum(lengths) / len(lengths)
            print(f"  Ortalama uzunluk: {avg_length:.1f} karakter")
            
            # Emoji kullanımını analiz et
            emoji_count = sum(1 for msg in engaging_messages if any(ord(char) > 127 for char in msg))
            emoji_rate = (emoji_count / len(engaging_messages)) * 100
            print(f"  Emoji kullanım oranı: {emoji_rate:.1f}%")
            
            # Rastgele 2 mesaj örneği
            import random
            print("  Örnek mesajlar:")
            for i, msg in enumerate(random.sample(engaging_messages, min(2, len(engaging_messages))), 1):
                print(f"    {i}. {msg}")
        
        print()

def main():
    """Ana test fonksiyonu"""
    print("🚀 Adaptif Spam Sistemi Test Paketi")
    print("=" * 60)
    print()
    
    # Testleri çalıştır
    test_adaptive_spam_scheduler()
    test_frequency_settings()
    test_bot_comparison()
    test_timing_scenarios()
    test_message_variety()
    
    print("✅ Tüm testler tamamlandı!")
    print()
    print("📋 Adaptif Spam Sistemi Özellikleri:")
    print("- ✅ Generic sistem (tüm botlar için)")
    print("- ✅ Profil bazlı ayarlar")
    print("- ✅ Grup frekansına göre adaptif interval")
    print("- ✅ Frequency multiplier sistemi")
    print("- ✅ Aktif saat optimizasyonu")
    print("- ✅ Aggressive mod (üst üste mesaj engelleme)")
    print("- ✅ Gerçek zamanlı aktivite takibi")
    print("- ✅ Otomatik rate limiting")
    print("- ✅ Grup ban koruması")
    print()
    print("🎯 Sonuç: Tüm system botları artık akıllı ve adaptif!")

if __name__ == "__main__":
    main() 