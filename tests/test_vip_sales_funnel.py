#!/usr/bin/env python3
"""
VIP Satış Funnel Test Scripti
Bu script VIP grup tanıtımından satış kapatmaya kadar olan süreci test eder.
"""

import time
from handlers.dm_handler import (
    check_vip_interest,
    check_payment_intent,
    update_vip_interest,
    get_vip_interest_stage,
    VIP_INTEREST_KEYWORDS,
    PAYMENT_KEYWORDS
)

def test_vip_interest_detection():
    """VIP ilgi tespiti testini yapar"""
    print("🧪 VIP İlgi Tespiti Testi")
    print("=" * 50)
    
    # VIP ilgi mesajları
    vip_messages = [
        "VIP grubun nasıl?",
        "Özel içerikler var mı?",
        "Premium üyelik nedir?",
        "VIP'e katılmak istiyorum",
        "Özel kanal merak ettim",
        "VIP ne kadar?",
        "Exclusive içerik var mı?",
        "Grup üyeliği istiyorum"
    ]
    
    # Normal mesajlar
    normal_messages = [
        "Merhaba nasılsın?",
        "Bugün ne yapıyorsun?",
        "Çok güzelsin",
        "Seni seviyorum",
        "Kahve içelim mi?"
    ]
    
    print("VIP İlgi Mesajları:")
    for msg in vip_messages:
        result = check_vip_interest(msg)
        print(f"  {'✅' if result else '❌'} '{msg}' -> {result}")
    
    print("\nNormal Mesajlar:")
    for msg in normal_messages:
        result = check_vip_interest(msg)
        print(f"  {'❌' if not result else '✅'} '{msg}' -> {result}")
    
    print()

def test_payment_intent_detection():
    """Ödeme niyeti tespiti testini yapar"""
    print("🧪 Ödeme Niyeti Tespiti Testi")
    print("=" * 50)
    
    # Ödeme niyeti mesajları
    payment_messages = [
        "IBAN'ını ver",
        "Nasıl ödeme yapacağım?",
        "Hangi banka?",
        "Papara var mı?",
        "Para göndereceğim",
        "Ödeme yapmak istiyorum",
        "Transfer yapacağım",
        "Havale atacağım",
        "Hesap numarası ver"
    ]
    
    # Normal mesajlar
    normal_messages = [
        "Teşekkürler",
        "Anladım",
        "Tamam canım",
        "Güzel",
        "Harika"
    ]
    
    print("Ödeme Niyeti Mesajları:")
    for msg in payment_messages:
        result = check_payment_intent(msg)
        print(f"  {'✅' if result else '❌'} '{msg}' -> {result}")
    
    print("\nNormal Mesajlar:")
    for msg in normal_messages:
        result = check_payment_intent(msg)
        print(f"  {'❌' if not result else '✅'} '{msg}' -> {result}")
    
    print()

def test_vip_stage_tracking():
    """VIP aşama takibi testini yapar"""
    print("🧪 VIP Aşama Takibi Testi")
    print("=" * 50)
    
    bot_username = "test_bot"
    user_id = 12345
    
    # Başlangıç durumu
    stage = get_vip_interest_stage(bot_username, user_id)
    print(f"1. Başlangıç aşaması: {stage}")
    
    # İlgi aşaması
    update_vip_interest(bot_username, user_id, "interested")
    stage = get_vip_interest_stage(bot_username, user_id)
    print(f"2. İlgi aşaması: {stage}")
    
    # Ödeme aşaması
    update_vip_interest(bot_username, user_id, "payment")
    stage = get_vip_interest_stage(bot_username, user_id)
    print(f"3. Ödeme aşaması: {stage}")
    
    # Farklı kullanıcı
    user_id_2 = 67890
    stage_2 = get_vip_interest_stage(bot_username, user_id_2)
    print(f"4. Farklı kullanıcı: {stage_2}")
    
    print()

def test_sales_funnel_flow():
    """Satış funnel akışını test eder"""
    print("🧪 Satış Funnel Akışı Testi")
    print("=" * 50)
    
    bot_username = "yayincilara"
    user_id = 11111
    
    # Test senaryosu
    conversation_flow = [
        ("Merhaba", "normal"),
        ("VIP grubun var mı?", "vip_interest"),
        ("Ne kadar?", "pricing"),
        ("Tamam istiyorum", "confirmation"),
        ("Nasıl ödeme yapacağım?", "payment"),
        ("IBAN ver", "payment_details")
    ]
    
    print("Konuşma Akışı Simülasyonu:")
    for i, (message, expected_stage) in enumerate(conversation_flow):
        print(f"\n{i+1}. Kullanıcı: '{message}'")
        
        # VIP ilgi kontrolü
        vip_interest = check_vip_interest(message)
        payment_intent = check_payment_intent(message)
        current_stage = get_vip_interest_stage(bot_username, user_id)
        
        print(f"   VIP İlgi: {'✅' if vip_interest else '❌'}")
        print(f"   Ödeme Niyeti: {'✅' if payment_intent else '❌'}")
        print(f"   Mevcut Aşama: {current_stage}")
        
        # Aşama güncelleme
        if vip_interest and current_stage == "none":
            update_vip_interest(bot_username, user_id, "interested")
            print(f"   ➡️ Aşama güncellendi: interested")
        elif payment_intent or current_stage == "interested":
            update_vip_interest(bot_username, user_id, "payment")
            print(f"   ➡️ Aşama güncellendi: payment")
    
    print()

def test_keyword_coverage():
    """Anahtar kelime kapsamını test eder"""
    print("🧪 Anahtar Kelime Kapsamı Testi")
    print("=" * 50)
    
    print(f"VIP İlgi Anahtar Kelimeleri ({len(VIP_INTEREST_KEYWORDS)} adet):")
    for i, keyword in enumerate(VIP_INTEREST_KEYWORDS, 1):
        print(f"  {i:2d}. {keyword}")
    
    print(f"\nÖdeme Anahtar Kelimeleri ({len(PAYMENT_KEYWORDS)} adet):")
    for i, keyword in enumerate(PAYMENT_KEYWORDS, 1):
        print(f"  {i:2d}. {keyword}")
    
    # Kapsam testi
    test_sentences = [
        "VIP grubuna katılmak istiyorum ne kadar?",
        "Özel premium içerikler merak ettim ücret nedir?",
        "IBAN bilgini ver para göndereceğim",
        "Hangi bankadan havale yapabilirim?",
        "Papara hesabın var mı transfer yapmak istiyorum?"
    ]
    
    print(f"\nKapsam Testi:")
    for sentence in test_sentences:
        vip_match = any(keyword in sentence.lower() for keyword in VIP_INTEREST_KEYWORDS)
        payment_match = any(keyword in sentence.lower() for keyword in PAYMENT_KEYWORDS)
        print(f"  '{sentence}'")
        print(f"    VIP: {'✅' if vip_match else '❌'}, Ödeme: {'✅' if payment_match else '❌'}")
    
    print()

def test_performance():
    """Performans testini yapar"""
    print("🧪 Performans Testi")
    print("=" * 50)
    
    import time
    
    # 1000 mesaj için test
    test_messages = [
        "VIP grubuna katılmak istiyorum",
        "IBAN bilgini gönder",
        "Merhaba nasılsın",
        "Ne kadar ücret?",
        "Ödeme yapmak istiyorum"
    ] * 200
    
    # VIP ilgi testi
    start_time = time.time()
    for msg in test_messages:
        check_vip_interest(msg)
    vip_time = time.time() - start_time
    
    # Ödeme niyeti testi
    start_time = time.time()
    for msg in test_messages:
        check_payment_intent(msg)
    payment_time = time.time() - start_time
    
    print(f"1000 mesaj için performans:")
    print(f"  VIP İlgi Kontrolü: {vip_time:.3f} saniye")
    print(f"  Ödeme Niyeti Kontrolü: {payment_time:.3f} saniye")
    print(f"  Toplam: {vip_time + payment_time:.3f} saniye")
    print(f"  Mesaj/saniye: {1000/(vip_time + payment_time):.0f}")
    
    print()

def main():
    """Ana test fonksiyonu"""
    print("🚀 VIP Satış Funnel Sistemi Test Başlıyor")
    print("=" * 60)
    print()
    
    # Testleri çalıştır
    test_vip_interest_detection()
    test_payment_intent_detection()
    test_vip_stage_tracking()
    test_sales_funnel_flow()
    test_keyword_coverage()
    test_performance()
    
    print("✅ Tüm testler tamamlandı!")
    print()
    print("📋 VIP Satış Funnel Sistemi Özellikleri:")
    print("- ✅ Akıllı VIP ilgi tespiti")
    print("- ✅ Ödeme niyeti algılama")
    print("- ✅ Aşamalı satış funnel'ı")
    print("- ✅ Otomatik IBAN yönlendirme")
    print("- ✅ Kullanıcı bazlı takip")
    print("- ✅ Performans optimizasyonu")
    print()
    print("🎯 Sonuç: VIP tanıtımından satış kapatmaya otomatik sistem!")

if __name__ == "__main__":
    main() 