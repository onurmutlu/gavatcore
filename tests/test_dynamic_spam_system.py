#!/usr/bin/env python3
"""
Dinamik Spam Sistemi Test Scripti
Bu script dinamik spam scheduler'ın çalışmasını test eder.
"""

import time
import random
from utilities.dynamic_spam_scheduler import (
    DynamicSpamScheduler,
    SPAM_FREQUENCIES,
    TRAFFIC_THRESHOLDS,
    get_dynamic_stats,
    reset_dynamic_stats
)

def test_group_activity_analysis():
    """Grup aktivite analizi testini yapar"""
    print("🧪 Grup Aktivite Analizi Testi")
    print("=" * 50)
    
    scheduler = DynamicSpamScheduler()
    
    # Test grupları oluştur
    test_groups = {
        -1001: "Çok Yoğun Grup",
        -1002: "Yoğun Grup", 
        -1003: "Orta Grup",
        -1004: "Sakin Grup",
        -1005: "Çok Sakin Grup"
    }
    
    # Farklı aktivite seviyelerini simüle et
    test_scenarios = [
        (-1001, 150, "very_high"),  # 150 mesaj -> çok yoğun
        (-1002, 75, "high"),        # 75 mesaj -> yoğun
        (-1003, 30, "medium"),      # 30 mesaj -> orta
        (-1004, 10, "low"),         # 10 mesaj -> sakin
        (-1005, 2, "very_low")      # 2 mesaj -> çok sakin
    ]
    
    for group_id, message_count, expected_level in test_scenarios:
        # Grup aktivitesini güncelle
        scheduler.update_group_activity(group_id, message_count)
        
        # Aktivite seviyesini analiz et
        actual_level = scheduler.analyze_group_activity(group_id)
        
        # Spam interval'ını al
        min_interval, max_interval = scheduler.get_spam_interval(group_id)
        interval_desc = SPAM_FREQUENCIES[actual_level]['description']
        
        # Sonucu yazdır
        status = "✅" if actual_level == expected_level else "❌"
        print(f"{status} {test_groups[group_id]}: {message_count} mesaj -> {actual_level} ({interval_desc})")
    
    print()

def test_spam_timing():
    """Spam timing testini yapar"""
    print("🧪 Spam Timing Testi")
    print("=" * 50)
    
    scheduler = DynamicSpamScheduler()
    group_id = -1001
    
    # İlk spam - yapılabilmeli
    can_spam1 = scheduler.should_spam_group(group_id)
    print(f"1. İlk spam: {'✅ SPAM' if can_spam1 else '❌ NO SPAM'}")
    
    if can_spam1:
        scheduler.mark_spam_sent(group_id)
    
    # Hemen ardından spam - yapılmamalı
    can_spam2 = scheduler.should_spam_group(group_id)
    print(f"2. Hemen ardından: {'❌ NO SPAM' if not can_spam2 else '✅ SPAM'}")
    
    # Grup aktivitesini yüksek yap
    scheduler.update_group_activity(group_id, 100)  # Çok yoğun grup
    
    # Yüksek aktiviteli grup için interval
    min_interval, max_interval = scheduler.get_spam_interval(group_id)
    print(f"3. Yoğun grup interval: {min_interval//60}-{max_interval//60} dakika")
    
    # Düşük aktiviteli grup
    low_group_id = -1002
    scheduler.update_group_activity(low_group_id, 3)  # Sakin grup
    min_interval2, max_interval2 = scheduler.get_spam_interval(low_group_id)
    print(f"4. Sakin grup interval: {min_interval2//60}-{max_interval2//60} dakika")
    
    print()

def test_stats_summary():
    """İstatistik özeti testini yapar"""
    print("🧪 İstatistik Özeti Testi")
    print("=" * 50)
    
    scheduler = DynamicSpamScheduler()
    
    # Test verilerini oluştur
    test_data = [
        (-1001, 120, "Çok Aktif Grup"),
        (-1002, 80, "Aktif Grup"),
        (-1003, 40, "Orta Grup"),
        (-1004, 15, "Sakin Grup"),
        (-1005, 3, "Çok Sakin Grup"),
        (-1006, 200, "Süper Aktif Grup")
    ]
    
    for group_id, message_count, name in test_data:
        scheduler.update_group_activity(group_id, message_count)
        scheduler.mark_spam_sent(group_id)
    
    # Bazı grupları banla
    scheduler.banned_groups.add(-1007)
    scheduler.banned_groups.add(-1008)
    
    # İstatistik özetini al
    stats = scheduler.get_group_stats_summary()
    
    print(f"Toplam grup: {stats['total_groups']}")
    print(f"Banlı grup: {stats['banned_groups']}")
    print("Aktivite seviyeleri:")
    for level, count in stats['activity_levels'].items():
        print(f"  {level}: {count} grup")
    
    print("\nEn aktif gruplar:")
    for i, group in enumerate(stats['top_active_groups'][:5], 1):
        print(f"  {i}. Grup {group['group_id']}: {group['recent_messages']} mesaj ({group['activity_level']})")
    
    print()

def test_frequency_optimization():
    """Frequency optimizasyon testini yapar"""
    print("🧪 Frequency Optimizasyon Testi")
    print("=" * 50)
    
    # Farklı aktivite seviyelerinin interval'larını göster
    print("Spam Frequency Ayarları:")
    for level, config in SPAM_FREQUENCIES.items():
        min_min = config['interval'][0] // 60
        max_min = config['interval'][1] // 60
        print(f"  {level}: {min_min}-{max_min} dakika - {config['description']}")
    
    print("\nTrafik Eşikleri:")
    for level, threshold in TRAFFIC_THRESHOLDS.items():
        print(f"  {level}: {threshold}+ mesaj/saat")
    
    print("\n🎯 Optimizasyon Mantığı:")
    print("- Çok yoğun gruplar (100+ mesaj/saat): 5-7 dakikada bir spam")
    print("- Yoğun gruplar (50+ mesaj/saat): 7-10 dakikada bir spam")
    print("- Orta gruplar (20+ mesaj/saat): 10-15 dakikada bir spam")
    print("- Sakin gruplar (5+ mesaj/saat): 15-30 dakikada bir spam")
    print("- Çok sakin gruplar (<5 mesaj/saat): 30-60 dakikada bir spam")
    
    print()

def simulate_real_scenario():
    """Gerçek senaryo simülasyonu"""
    print("🧪 Gerçek Senaryo Simülasyonu")
    print("=" * 50)
    
    scheduler = DynamicSpamScheduler()
    
    # Gerçek grup senaryoları
    scenarios = [
        {"name": "ARAYIŞ GRUBU", "id": -1001, "hourly_messages": 150},
        {"name": "Sohbet Grubu", "id": -1002, "hourly_messages": 80},
        {"name": "Arkadaş Grubu", "id": -1003, "hourly_messages": 25},
        {"name": "Eski Grup", "id": -1004, "hourly_messages": 8},
        {"name": "Ölü Grup", "id": -1005, "hourly_messages": 1}
    ]
    
    print("Grup Analizi ve Spam Stratejisi:")
    print("-" * 60)
    
    for scenario in scenarios:
        group_id = scenario["id"]
        message_count = scenario["hourly_messages"]
        name = scenario["name"]
        
        # Grup aktivitesini güncelle
        scheduler.update_group_activity(group_id, message_count)
        
        # Analiz yap
        activity_level = scheduler.analyze_group_activity(group_id)
        min_interval, max_interval = scheduler.get_spam_interval(group_id)
        
        # Spam yapılabilir mi?
        can_spam = scheduler.should_spam_group(group_id)
        
        print(f"📊 {name}:")
        print(f"   Mesaj/saat: {message_count}")
        print(f"   Aktivite: {activity_level}")
        print(f"   Spam interval: {min_interval//60}-{max_interval//60} dakika")
        print(f"   Spam durumu: {'✅ Yapılabilir' if can_spam else '❌ Beklemede'}")
        print()
    
    # Genel istatistik
    stats = scheduler.get_group_stats_summary()
    print("📈 Genel İstatistikler:")
    for level, count in stats['activity_levels'].items():
        if count > 0:
            desc = SPAM_FREQUENCIES[level]['description']
            print(f"   {level}: {count} grup ({desc})")

def main():
    """Ana test fonksiyonu"""
    print("🚀 Dinamik Spam Sistemi Test Başlıyor")
    print("=" * 60)
    print()
    
    # İstatistikleri sıfırla
    reset_dynamic_stats()
    
    # Testleri çalıştır
    test_group_activity_analysis()
    test_spam_timing()
    test_stats_summary()
    test_frequency_optimization()
    simulate_real_scenario()
    
    print("✅ Tüm testler tamamlandı!")
    print()
    print("📋 Dinamik Spam Sistemi Özellikleri:")
    print("- ✅ Grup trafiği analizi (1 saatlik pencere)")
    print("- ✅ 5 farklı aktivite seviyesi")
    print("- ✅ Dinamik spam frequency (5-60 dakika)")
    print("- ✅ Akıllı spam timing")
    print("- ✅ Grup prioritization (aktif gruplar önce)")
    print("- ✅ Otomatik ban detection")
    print("- ✅ Real-time istatistikler")
    print()
    print("🎯 Sonuç: Kalabalık gruplara 5-7 dakikada bir spam atılacak!")

if __name__ == "__main__":
    main() 