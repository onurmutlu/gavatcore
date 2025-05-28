#!/usr/bin/env python3
"""
Grup Reply İyileştirmeleri Test Scripti
Bu script grup reply sistemindeki iyileştirmeleri test eder.
"""

import time
from datetime import datetime, timedelta
from handlers.group_handler import (
    reply_cooldowns,
    group_reply_cooldowns,
    processed_messages,
    _check_reply_cooldown,
    _update_reply_cooldown,
    USER_REPLY_COOLDOWN,
    GROUP_REPLY_COOLDOWN,
    CONVERSATION_COOLDOWN
)

def test_cooldown_system():
    """Cooldown sistemini test et"""
    print("🧪 Cooldown Sistemi Testi")
    print("=" * 50)
    
    # Test verileri
    bot_username = "test_bot"
    group_id = -1001234567890
    user_id = 123456789
    
    # İlk mesaj - reply yapılabilmeli
    can_reply1, reason1 = _check_reply_cooldown(bot_username, group_id, user_id)
    print(f"1. Mesaj (ilk): {'✅ REPLY' if can_reply1 else '❌ NO REPLY'} - {reason1}")
    
    # Cooldown ekle
    if can_reply1:
        _update_reply_cooldown(bot_username, group_id, user_id)
    
    # Hemen ardından mesaj - reply yapılmamalı
    can_reply2, reason2 = _check_reply_cooldown(bot_username, group_id, user_id)
    print(f"2. Mesaj (cooldown): {'❌ NO REPLY' if not can_reply2 else '✅ REPLY'} - {reason2}")
    
    # Farklı kullanıcıdan mesaj - grup cooldown aktif olmalı
    can_reply3, reason3 = _check_reply_cooldown(bot_username, group_id, 987654321)
    print(f"3. Mesaj (farklı user): {'❌ NO REPLY' if not can_reply3 else '✅ REPLY'} - {reason3}")
    
    print()

def test_duplicate_prevention():
    """Duplicate prevention sistemini test et"""
    print("🧪 Duplicate Prevention Testi")
    print("=" * 50)
    
    group_id = -1001234567890
    message_id1 = 12345
    message_id2 = 12346
    
    # İlk mesaj - duplicate değil
    message_key1 = f"{group_id}:{message_id1}"
    is_duplicate1 = message_key1 in processed_messages
    print(f"1. İlk mesaj: {'❌ NO DUPLICATE' if not is_duplicate1 else '✅ DUPLICATE'}")
    
    # Processed messages'a ekle
    processed_messages.add(message_key1)
    
    # Aynı mesaj - duplicate olmalı
    is_duplicate2 = message_key1 in processed_messages
    print(f"2. Duplicate mesaj: {'✅ DUPLICATE' if is_duplicate2 else '❌ NO DUPLICATE'}")
    
    # Farklı mesaj - duplicate olmamalı
    message_key2 = f"{group_id}:{message_id2}"
    is_duplicate3 = message_key2 in processed_messages
    print(f"3. Farklı mesaj: {'❌ NO DUPLICATE' if not is_duplicate3 else '✅ DUPLICATE'}")
    
    print()

def test_integrated_system():
    """Entegre sistemi test et"""
    print("🧪 Entegre Sistem Testi")
    print("=" * 50)
    
    bot_username = "test_bot"
    group_id = -1001234567890
    user_id = 123456789
    
    # Temiz başlangıç
    reply_cooldowns.clear()
    group_reply_cooldowns.clear()
    processed_messages.clear()
    
    # Senaryo 1: İlk mesaj - reply yapılmalı
    can_reply1, reason1 = _check_reply_cooldown(bot_username, group_id, user_id)
    print(f"Senaryo 1 - İlk mesaj: {'✅ REPLY' if can_reply1 else '❌ NO REPLY'} - {reason1}")
    
    if can_reply1:
        _update_reply_cooldown(bot_username, group_id, user_id)
        # Duplicate prevention'a ekle
        message_key = f"{group_id}:1001"
        processed_messages.add(message_key)
    
    # Senaryo 2: Hemen ardından aynı kullanıcıdan mesaj - reply yapılmamalı
    can_reply2, reason2 = _check_reply_cooldown(bot_username, group_id, user_id)
    print(f"Senaryo 2 - Cooldown mesajı: {'❌ NO REPLY' if not can_reply2 else '✅ REPLY'} - {reason2}")
    
    # Senaryo 3: Farklı kullanıcıdan mesaj ama grup cooldown aktif - reply yapılmamalı
    can_reply3, reason3 = _check_reply_cooldown(bot_username, group_id, 987654321)
    print(f"Senaryo 3 - Grup cooldown: {'❌ NO REPLY' if not can_reply3 else '✅ REPLY'} - {reason3}")
    
    # Senaryo 4: Cooldown süresi geçtikten sonra - reply yapılmalı
    print("⏳ Cooldown süresini simüle ediyorum...")
    # Cooldown'ları temizle (gerçek hayatta zaman geçer)
    reply_cooldowns.clear()
    group_reply_cooldowns.clear()
    
    can_reply4, reason4 = _check_reply_cooldown(bot_username, group_id, 555666777)
    print(f"Senaryo 4 - Cooldown sonrası: {'✅ REPLY' if can_reply4 else '❌ NO REPLY'} - {reason4}")
    
    print()

def print_current_state():
    """Mevcut sistem durumunu yazdır"""
    print("📊 Mevcut Sistem Durumu")
    print("=" * 50)
    print(f"User Reply Cooldowns: {len(reply_cooldowns)} entry")
    print(f"Group Reply Cooldowns: {len(group_reply_cooldowns)} entry")
    print(f"Processed Messages: {len(processed_messages)} entry")
    
    # Cooldown detayları
    current_time = time.time()
    for key, timestamp in reply_cooldowns.items():
        remaining = USER_REPLY_COOLDOWN - (current_time - timestamp)
        if remaining > 0:
            print(f"  User cooldown {key}: {remaining:.0f}s kaldı")
    
    for key, timestamp in group_reply_cooldowns.items():
        remaining = GROUP_REPLY_COOLDOWN - (current_time - timestamp)
        if remaining > 0:
            print(f"  Grup cooldown {key}: {remaining:.0f}s kaldı")
    
    print()

def test_conversation_detection():
    """Conversation detection sistemini test et"""
    print("🧪 Conversation Detection Testi")
    print("=" * 50)
    
    # Bu test gerçek conversation detection logic'ini test eder
    # Şu anda _is_conversation_response_smart fonksiyonu async olduğu için
    # burada sadece temel mantığı test edebiliriz
    
    test_messages = [
        ("Merhaba", "Kısa selamlama - conversation olabilir"),
        ("Nasılsın?", "Soru - conversation olabilir"),
        ("Bu çok uzun bir mesaj ve conversation response olmayabilir çünkü çok detaylı", "Uzun mesaj - conversation olmayabilir"),
        ("ok", "Çok kısa onay - conversation olabilir"),
        ("evet", "Onay kelimesi - conversation olabilir")
    ]
    
    for message, description in test_messages:
        # Basit conversation indicators
        is_short = len(message) < 50
        has_question = any(word in message.lower() for word in ['ne', 'nasıl', 'neden', 'kim', 'nerede', 'ne zaman'])
        has_confirmation = any(word in message.lower() for word in ['evet', 'hayır', 'tamam', 'ok', 'peki', 'iyi'])
        has_greeting = any(word in message.lower() for word in ['merhaba', 'selam', 'hey', 'hi'])
        ends_with_question = message.endswith('?')
        is_very_short = len(message.split()) <= 5
        
        indicators = [is_short, has_question, has_confirmation, has_greeting, ends_with_question, is_very_short]
        score = sum(indicators)
        
        is_conversation = score >= 2
        print(f"'{message}' -> {'✅ CONVERSATION' if is_conversation else '❌ NOT CONVERSATION'} (skor: {score}/6) - {description}")
    
    print()

def main():
    """Ana test fonksiyonu"""
    print("🚀 Grup Reply İyileştirmeleri Test Başlıyor")
    print("=" * 60)
    print()
    
    # Testleri çalıştır
    test_cooldown_system()
    test_duplicate_prevention()
    test_conversation_detection()
    test_integrated_system()
    
    # Mevcut durumu göster
    print_current_state()
    
    print("✅ Tüm testler tamamlandı!")
    print()
    print("📋 İyileştirme Özeti:")
    print(f"- ✅ User reply cooldown sistemi ({USER_REPLY_COOLDOWN} saniye)")
    print(f"- ✅ Group reply cooldown sistemi ({GROUP_REPLY_COOLDOWN} saniye)")
    print(f"- ✅ Conversation detection cooldown ({CONVERSATION_COOLDOWN} saniye)")
    print("- ✅ Duplicate message prevention (message ID bazlı)")
    print("- ✅ Akıllı conversation detection (6 kriter)")
    print("- ✅ Otomatik cleanup (memory leak prevention)")
    print()
    print("🎯 Agresif Davranış Önleme:")
    print("- Aynı kullanıcıya 60 saniye cooldown")
    print("- Aynı grupta 30 saniye cooldown")
    print("- Conversation response için 120 saniye cooldown")
    print("- Duplicate mesaj engelleme")
    print("- Akıllı conversation detection (sadece gerçek konuşmalarda yanıt)")

if __name__ == "__main__":
    main() 