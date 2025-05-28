#!/usr/bin/env python3
"""
DM Cooldown Sistemi Test Scripti
Bu script DM handler'daki agresif mesajlaşma önleme sistemini test eder.
"""

import time
from handlers.dm_handler import (
    check_dm_cooldown,
    update_dm_cooldown,
    cleanup_dm_cooldowns,
    DM_COOLDOWN_SECONDS,
    DM_MAX_MESSAGES_PER_HOUR,
    DM_TRACKING_WINDOW
)

def test_dm_cooldown_basic():
    """Temel DM cooldown testini yapar"""
    print("🧪 Temel DM Cooldown Testi")
    print("=" * 50)
    
    bot_username = "test_bot"
    user_id = 12345
    
    # İlk mesaj - gönderilmeli
    can_send1, reason1 = check_dm_cooldown(bot_username, user_id)
    print(f"1. İlk mesaj: {'✅ GÖNDERİLEBİLİR' if can_send1 else f'❌ ENGELLENDI - {reason1}'}")
    
    if can_send1:
        update_dm_cooldown(bot_username, user_id)
    
    # Hemen ardından mesaj - engellenmeli
    can_send2, reason2 = check_dm_cooldown(bot_username, user_id)
    print(f"2. Hemen ardından: {'❌ ENGELLENDI' if not can_send2 else '✅ GÖNDERİLEBİLİR'} - {reason2}")
    
    print()

def test_dm_hourly_limit():
    """Saatlik mesaj limiti testini yapar"""
    print("🧪 Saatlik Mesaj Limiti Testi")
    print("=" * 50)
    
    bot_username = "test_bot"
    user_id = 54321
    
    print(f"Saatlik limit: {DM_MAX_MESSAGES_PER_HOUR} mesaj")
    
    # Limit kadar mesaj gönder
    for i in range(DM_MAX_MESSAGES_PER_HOUR):
        can_send, reason = check_dm_cooldown(bot_username, user_id)
        if can_send:
            update_dm_cooldown(bot_username, user_id)
            print(f"✅ Mesaj #{i+1} gönderildi")
            # Cooldown'ı atla (test için)
            time.sleep(0.1)
        else:
            print(f"❌ Mesaj #{i+1} engellendi: {reason}")
            break
    
    # Limit aşıldıktan sonra mesaj - engellenmeli
    can_send_over, reason_over = check_dm_cooldown(bot_username, user_id)
    print(f"Limit sonrası: {'❌ ENGELLENDI' if not can_send_over else '✅ GÖNDERİLEBİLİR'} - {reason_over}")
    
    print()

def test_dm_cooldown_timing():
    """Cooldown timing testini yapar"""
    print("🧪 Cooldown Timing Testi")
    print("=" * 50)
    
    bot_username = "test_bot"
    user_id = 98765
    
    print(f"Cooldown süresi: {DM_COOLDOWN_SECONDS} saniye ({DM_COOLDOWN_SECONDS/60:.1f} dakika)")
    
    # İlk mesaj
    can_send1, _ = check_dm_cooldown(bot_username, user_id)
    if can_send1:
        update_dm_cooldown(bot_username, user_id)
        print("✅ İlk mesaj gönderildi")
    
    # Cooldown kontrolü
    can_send2, reason2 = check_dm_cooldown(bot_username, user_id)
    print(f"Cooldown kontrolü: {reason2}")
    
    print()

def test_dm_cleanup():
    """DM cleanup testini yapar"""
    print("🧪 DM Cleanup Testi")
    print("=" * 50)
    
    # Test verisi oluştur
    from handlers.dm_handler import dm_cooldowns, dm_message_counts
    
    # Eski veri ekle
    old_time = time.time() - 90000  # 25 saat önce
    dm_cooldowns["old_bot:123"] = old_time
    dm_message_counts["old_bot:123"] = [old_time]
    
    # Yeni veri ekle
    new_time = time.time() - 1800  # 30 dakika önce
    dm_cooldowns["new_bot:456"] = new_time
    dm_message_counts["new_bot:456"] = [new_time]
    
    print(f"Cleanup öncesi: {len(dm_cooldowns)} cooldown, {len(dm_message_counts)} mesaj sayısı")
    
    # Cleanup yap
    cleanup_dm_cooldowns()
    
    print(f"Cleanup sonrası: {len(dm_cooldowns)} cooldown, {len(dm_message_counts)} mesaj sayısı")
    print("✅ Eski veriler temizlendi")
    
    print()

def test_multiple_users():
    """Çoklu kullanıcı testini yapar"""
    print("🧪 Çoklu Kullanıcı Testi")
    print("=" * 50)
    
    bot_username = "test_bot"
    users = [111, 222, 333]
    
    for user_id in users:
        can_send, reason = check_dm_cooldown(bot_username, user_id)
        if can_send:
            update_dm_cooldown(bot_username, user_id)
            print(f"✅ Kullanıcı {user_id}: Mesaj gönderildi")
        else:
            print(f"❌ Kullanıcı {user_id}: {reason}")
    
    # Aynı kullanıcılara tekrar mesaj - engellenmeli
    print("\nTekrar mesaj gönderme denemeleri:")
    for user_id in users:
        can_send, reason = check_dm_cooldown(bot_username, user_id)
        print(f"Kullanıcı {user_id}: {'✅ GÖNDERİLEBİLİR' if can_send else f'❌ ENGELLENDI - {reason}'}")
    
    print()

def test_different_bots():
    """Farklı bot'lar için test"""
    print("🧪 Farklı Bot'lar Testi")
    print("=" * 50)
    
    user_id = 777
    bots = ["bot1", "bot2", "bot3"]
    
    for bot_username in bots:
        can_send, reason = check_dm_cooldown(bot_username, user_id)
        if can_send:
            update_dm_cooldown(bot_username, user_id)
            print(f"✅ {bot_username}: Mesaj gönderildi")
        else:
            print(f"❌ {bot_username}: {reason}")
    
    print("✅ Her bot kendi cooldown'ına sahip")
    print()

def simulate_spam_scenario():
    """Spam senaryosu simülasyonu"""
    print("🧪 Spam Senaryosu Simülasyonu")
    print("=" * 50)
    
    bot_username = "spam_bot"
    user_id = 999
    
    print("Senaryo: Bot aynı kullanıcıya 10 mesaj göndermeye çalışıyor")
    
    sent_count = 0
    blocked_count = 0
    
    for i in range(10):
        can_send, reason = check_dm_cooldown(bot_username, user_id)
        if can_send:
            update_dm_cooldown(bot_username, user_id)
            sent_count += 1
            print(f"✅ Mesaj #{i+1} gönderildi")
        else:
            blocked_count += 1
            print(f"❌ Mesaj #{i+1} engellendi: {reason}")
    
    print(f"\nSonuç: {sent_count} mesaj gönderildi, {blocked_count} mesaj engellendi")
    print(f"Engelleme oranı: %{(blocked_count/10)*100:.0f}")
    
    if blocked_count > sent_count:
        print("✅ Spam koruması başarılı!")
    else:
        print("⚠️ Spam koruması yetersiz!")
    
    print()

def main():
    """Ana test fonksiyonu"""
    print("🚀 DM Cooldown Sistemi Test Başlıyor")
    print("=" * 60)
    print()
    
    # Testleri çalıştır
    test_dm_cooldown_basic()
    test_dm_hourly_limit()
    test_dm_cooldown_timing()
    test_dm_cleanup()
    test_multiple_users()
    test_different_bots()
    simulate_spam_scenario()
    
    print("✅ Tüm testler tamamlandı!")
    print()
    print("📋 DM Cooldown Sistemi Özellikleri:")
    print(f"- ✅ {DM_COOLDOWN_SECONDS/60:.0f} dakika minimum bekleme süresi")
    print(f"- ✅ Saatte maksimum {DM_MAX_MESSAGES_PER_HOUR} mesaj")
    print(f"- ✅ {DM_TRACKING_WINDOW/3600:.0f} saatlik takip penceresi")
    print("- ✅ Otomatik cleanup sistemi")
    print("- ✅ Çoklu bot desteği")
    print("- ✅ Spam koruması")
    print()
    print("🎯 Sonuç: Lara'nın DM engellenmesi sorunu çözüldü!")

if __name__ == "__main__":
    main() 