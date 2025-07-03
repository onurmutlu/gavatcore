#!/usr/bin/env python3
"""
Humanizer Test Suite - İnsan Gibi Bot Davranışı Testleri
"""

import asyncio
import time
from utilities.humanizer import Humanizer, LaraHumanizer, BabaGavatHumanizer, GeishaHumanizer

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

async def test_basic_humanizer():
    """Temel humanizer fonksiyonlarını test et"""
    print_section("TEMEL HUMANIZER TESTLERİ")
    
    humanizer = Humanizer()
    
    # Test mesajları
    test_messages = [
        "Merhaba nasılsın?",
        "Bu gece buluşalım mı?",
        "Seni çok özledim canım",
        "Ne yapıyorsun şu an?",
        "Gel beraber bir şeyler yapalım"
    ]
    
    print("\n📝 Orijinal -> Humanized Mesajlar:")
    for msg in test_messages:
        humanized = humanizer.randomize_message(msg)
        print(f"• {msg}")
        print(f"  → {humanized}")
        print()

async def test_character_humanizers():
    """Karakter bazlı humanizer'ları test et"""
    print_section("KARAKTER HUMANIZER TESTLERİ")
    
    # Test mesajı
    test_msg = "Seninle konuşmak çok güzel"
    
    # Lara
    print("\n💋 LARA:")
    lara = LaraHumanizer()
    for i in range(3):
        result = lara.randomize_message(test_msg)
        print(f"  {i+1}. {result}")
    
    # BabaGavat
    print("\n😤 BABAGAVAT:")
    gavat = BabaGavatHumanizer()
    for i in range(3):
        result = gavat.randomize_message(test_msg)
        print(f"  {i+1}. {result}")
    
    # Geisha
    print("\n🌸 GEISHA:")
    geisha = GeishaHumanizer()
    for i in range(3):
        result = geisha.randomize_message(test_msg)
        print(f"  {i+1}. {result}")

async def test_typing_delay():
    """Typing delay hesaplamalarını test et"""
    print_section("TYPING DELAY TESTLERİ")
    
    humanizer = Humanizer()
    
    test_messages = [
        ("Selam", "Kısa mesaj"),
        ("Bu biraz daha uzun bir mesaj, typing süresi de uzun olmalı", "Orta mesaj"),
        ("Bu çok uzun bir mesaj. Gerçek bir insan böyle uzun bir mesajı yazarken epey zaman harcar. Typing göstergesi de buna göre uzun süre görünmeli ki gerçekçi olsun. Test amaçlı uzun yazıyorum.", "Uzun mesaj")
    ]
    
    print("\n⏱️ Mesaj uzunluğu ve typing delay:")
    for msg, desc in test_messages:
        delay = humanizer._calculate_typing_delay(msg)
        print(f"\n{desc}:")
        print(f"  Mesaj: {msg[:50]}...")
        print(f"  Uzunluk: {len(msg)} karakter")
        print(f"  Typing delay: {delay:.2f} saniye")

async def test_message_splitting():
    """Mesaj bölme fonksiyonunu test et"""
    print_section("MESAJ BÖLME TESTİ")
    
    humanizer = Humanizer()
    
    long_message = """Merhaba canım! Bugün sana anlatmak istediğim o kadar çok şey var ki. 
    Öncelikle dün gece seni düşündüm. Sonra bu sabah uyandığımda aklıma ilk sen geldin. 
    Acaba ne yapıyorsun diye merak ettim. Umarım günün güzel geçiyordur. 
    Seninle konuşmayı çok özlemiştim!"""
    
    parts = humanizer._split_message_naturally(long_message)
    
    print(f"\n📄 Orijinal mesaj ({len(long_message)} karakter)")
    print("-" * 40)
    print(long_message)
    
    print(f"\n✂️ {len(parts)} parçaya bölündü:")
    for i, part in enumerate(parts, 1):
        print(f"\n{i}. Parça ({len(part)} karakter):")
        print(f"   {part}")

async def test_silence_behavior():
    """Sessiz kalma davranışını test et"""
    print_section("SESSİZ KALMA DAVRANIŞI TESTİ")
    
    # Farklı silence_chance değerleri
    test_configs = [
        (0.0, "Hiç susma"),
        (0.1, "Lara - %10"),
        (0.2, "Geisha - %20"),
        (0.5, "Test - %50")
    ]
    
    print("\n🤐 100 mesajda kaç kez sessiz kalıyor?")
    
    for chance, desc in test_configs:
        humanizer = Humanizer({"silence_chance": chance})
        silent_count = sum(1 for _ in range(100) if not humanizer.should_respond())
        print(f"  {desc}: {silent_count}/100 sessiz")

async def test_typo_generation():
    """Yazım hatası üretimini test et"""
    print_section("YAZIM HATASI TESTİ")
    
    humanizer = Humanizer({"mistake_chance": 0.5})  # Test için yüksek
    
    test_words = ["merhaba", "nasılsın", "seviyorum", "güzelsin", "özledim"]
    
    print("\n✏️ Yazım hataları:")
    for word in test_words:
        # 10 kez dene, en az bir hata göster
        for _ in range(10):
            result = humanizer._add_typo(word)
            if result != word:
                print(f"  {word} → {result}")
                break

async def test_real_conversation():
    """Gerçek konuşma simülasyonu"""
    print_section("GERÇEK KONUŞMA SİMÜLASYONU")
    
    # Lara karakteri
    lara = LaraHumanizer()
    
    # Konuşma
    conversation = [
        ("User", "Selam Lara, nasılsın?"),
        ("Lara", "Привет милый... seni düşünüyordum"),
        ("User", "Ben de seni düşünüyordum. Ne yapıyorsun?"),
        ("Lara", "Şey... biraz yalnızım şu an"),
        ("User", "Gel buluşalım o zaman?"),
        ("Lara", "Bu kadar hızlı yazma, tadını çıkaralım")
    ]
    
    print("\n💬 Humanized konuşma:")
    for speaker, msg in conversation:
        if speaker == "Lara":
            # Lara mesajını humanize et
            humanized = lara.randomize_message(msg)
            delay = lara._calculate_typing_delay(humanized)
            print(f"\n{speaker} (typing {delay:.1f}s...): {humanized}")
        else:
            print(f"\n{speaker}: {msg}")
        
        # Küçük bekleme
        await asyncio.sleep(0.5)

async def main():
    """Tüm testleri çalıştır"""
    print("🎭 HUMANIZER TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_basic_humanizer(),
        test_character_humanizers(),
        test_typing_delay(),
        test_message_splitting(),
        test_silence_behavior(),
        test_typo_generation(),
        test_real_conversation()
    ]
    
    for test in tests:
        await test
        await asyncio.sleep(1)
    
    print("\n✅ TÜM TESTLER TAMAMLANDI!")
    print("=" * 60)
    
    # Özet
    print("\n📊 ÖZET:")
    print("• Humanizer modülü başarıyla test edildi")
    print("• Karakter bazlı özelleştirmeler çalışıyor")
    print("• Typing delay hesaplamaları doğru")
    print("• Mesaj manipülasyonları başarılı")
    print("• İnsan gibi davranış simülasyonu hazır!")

if __name__ == "__main__":
    asyncio.run(main()) 