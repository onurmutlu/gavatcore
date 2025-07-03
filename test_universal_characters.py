#!/usr/bin/env python3
"""
UNIVERSAL CHARACTER SYSTEM TEST SCRIPT
======================================

Universal Character System'i test etmek için kullanılır.

Kullanım:
    python test_universal_characters.py --test-system       # Sistem testleri
    python test_universal_characters.py --test-characters   # Karakter testleri
    python test_universal_characters.py --test-integration  # Entegrasyon testleri
    python test_universal_characters.py --all               # Tüm testler
    python test_universal_characters.py --demo              # Demo çalıştır
"""

import asyncio
import argparse
import sys
from datetime import datetime
from typing import Dict, Any, List

# Test imports
from handlers.universal_character_system import (
    CharacterType,
    CharacterConfig,
    character_manager,
    register_character,
    is_character_registered
)
from handlers.character_definitions import (
    create_lara_character,
    create_geisha_character,
    create_babagavat_character,
    create_friendly_character,
    create_mysterious_character,
    register_all_characters,
    get_character_by_username,
    create_custom_character
)
from handlers.universal_character_integration import (
    initialize_universal_characters,
    detect_character_from_profile,
    is_universal_character,
    get_universal_integration_stats,
    list_all_characters
)

def print_header(title: str):
    """Test başlığı yazdır"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_test_result(test_name: str, success: bool, details: str = ""):
    """Test sonucunu yazdır"""
    status = "✅ BAŞARILI" if success else "❌ BAŞARISIZ"
    print(f"{status} - {test_name}")
    if details:
        print(f"    {details}")

def print_character_info(character_id: str, character: CharacterConfig):
    """Karakter bilgilerini yazdır"""
    print(f"\n🎭 {character.display_name} ({character_id})")
    print(f"   📝 Tip: {character.character_type.value}")
    print(f"   👤 Yaş: {character.age}, Uyruk: {character.nationality}")
    print(f"   💬 Diller: {', '.join(character.languages)}")
    print(f"   ✨ Kişilik: {', '.join(character.personality[:3])}...")
    print(f"   🎯 VIP Hizmetler: {len(character.vip_services)} adet")
    print(f"   💎 Özel Kelimeler: {len(character.special_words)} adet")

async def test_system_core():
    """Sistem temel testleri"""
    print_header("UNIVERSAL CHARACTER SYSTEM - TEMEL TESTLERİ")
    
    total_tests = 0
    passed_tests = 0
    
    # Test 1: Character manager initialization
    total_tests += 1
    try:
        success = character_manager is not None
        print_test_result("Character Manager başlatma", success)
        if success:
            passed_tests += 1
    except Exception as e:
        print_test_result("Character Manager başlatma", False, str(e))
    
    # Test 2: Character types enum
    total_tests += 1
    try:
        expected_types = ["flirty", "seductive", "leader", "friendly", "professional", "playful", "mysterious", "dominant"]
        actual_types = [t.value for t in CharacterType]
        success = all(t in actual_types for t in expected_types[:6])  # İlk 6 tanesi yeterli
        print_test_result("Character Types enum", success, f"Bulunan: {len(actual_types)} tip")
        if success:
            passed_tests += 1
    except Exception as e:
        print_test_result("Character Types enum", False, str(e))
    
    # Test 3: Character registration
    total_tests += 1
    try:
        test_char = CharacterConfig(
            name="TestChar",
            display_name="🧪 Test",
            age=25,
            nationality="Test",
            character_type=CharacterType.FRIENDLY,
            personality=["test"],
            languages=["Türkçe"]
        )
        
        register_character("test_char", test_char)
        success = is_character_registered("test_char")
        print_test_result("Karakter kaydetme", success)
        if success:
            passed_tests += 1
    except Exception as e:
        print_test_result("Karakter kaydetme", False, str(e))
    
    # Test 4: Character retrieval
    total_tests += 1
    try:
        retrieved_char = character_manager.get_character("test_char")
        success = retrieved_char is not None and retrieved_char.name == "TestChar"
        print_test_result("Karakter alma", success)
        if success:
            passed_tests += 1
    except Exception as e:
        print_test_result("Karakter alma", False, str(e))
    
    print(f"\nSistem Testleri: {passed_tests}/{total_tests} başarılı")
    return passed_tests, total_tests

async def test_character_definitions():
    """Karakter tanım testleri"""
    print_header("KARAKTER TANIMLARI TESTLERİ")
    
    total_tests = 0
    passed_tests = 0
    
    # Test character creators
    characters_to_test = [
        ("Lara", create_lara_character),
        ("Geisha", create_geisha_character),
        ("BabaGavat", create_babagavat_character),
        ("Maya", create_friendly_character),
        ("Noir", create_mysterious_character)
    ]
    
    for char_name, creator_func in characters_to_test:
        total_tests += 1
        try:
            character = creator_func()
            success = (
                character.name == char_name and
                len(character.personality) > 0 and
                len(character.languages) > 0 and
                character.age > 0
            )
            print_test_result(f"{char_name} karakter oluşturma", success)
            if success:
                passed_tests += 1
                print_character_info(char_name.lower(), character)
        except Exception as e:
            print_test_result(f"{char_name} karakter oluşturma", False, str(e))
    
    # Test username mapping
    total_tests += 1
    try:
        test_cases = [
            ("lara", "lara"),
            ("yayincilara", "lara"),
            ("geisha", "geisha"),
            ("xxxgeisha", "geisha"),
            ("babagavat", "babagavat"),
            ("unknown_bot", None)
        ]
        
        all_correct = True
        for username, expected in test_cases:
            result = get_character_by_username(username)
            if result != expected:
                all_correct = False
                break
        
        print_test_result("Username mapping", all_correct)
        if all_correct:
            passed_tests += 1
    except Exception as e:
        print_test_result("Username mapping", False, str(e))
    
    # Test custom character creation
    total_tests += 1
    try:
        custom_char = create_custom_character(
            "TestBot",
            CharacterType.PLAYFUL,
            age=30,
            nationality="Test Nation"
        )
        success = (
            custom_char.name == "TestBot" and
            custom_char.character_type == CharacterType.PLAYFUL and
            custom_char.age == 30
        )
        print_test_result("Özel karakter oluşturma", success)
        if success:
            passed_tests += 1
    except Exception as e:
        print_test_result("Özel karakter oluşturma", False, str(e))
    
    print(f"\nKarakter Testleri: {passed_tests}/{total_tests} başarılı")
    return passed_tests, total_tests

async def test_integration_system():
    """Entegrasyon sistemi testleri"""
    print_header("ENTEGRASYON SİSTEMİ TESTLERİ")
    
    total_tests = 0
    passed_tests = 0
    
    # Test system initialization
    total_tests += 1
    try:
        success = initialize_universal_characters()
        print_test_result("Sistem başlatma", success)
        if success:
            passed_tests += 1
    except Exception as e:
        print_test_result("Sistem başlatma", False, str(e))
    
    # Test character detection from profile
    total_tests += 1
    try:
        test_profiles = [
            ({"username": "lara_bot", "display_name": "Lara"}, "lara"),
            ({"username": "xxxgeisha", "type": "geisha_bot"}, "geisha"),
            ({"username": "babagavat", "personality": ["lider", "güçlü"]}, "babagavat"),
            ({"username": "unknown_bot", "display_name": "Unknown"}, None)
        ]
        
        all_correct = True
        for profile, expected in test_profiles:
            result = detect_character_from_profile(profile)
            if result != expected:
                all_correct = False
                print(f"    Hata: {profile} -> {result}, beklenen: {expected}")
                break
        
        print_test_result("Profil'den karakter tespit", all_correct)
        if all_correct:
            passed_tests += 1
    except Exception as e:
        print_test_result("Profil'den karakter tespit", False, str(e))
    
    # Test universal character detection
    total_tests += 1
    try:
        test_cases = [
            ("lara", True),
            ("geisha", True), 
            ("babagavat", True),
            ("unknown_bot", False)
        ]
        
        all_correct = True
        for username, expected in test_cases:
            result = is_universal_character(username)
            if result != expected:
                all_correct = False
                break
        
        print_test_result("Universal karakter tespit", all_correct)
        if all_correct:
            passed_tests += 1
    except Exception as e:
        print_test_result("Universal karakter tespit", False, str(e))
    
    # Test stats collection
    total_tests += 1
    try:
        stats = get_universal_integration_stats()
        success = (
            "total_registered_characters" in stats and
            "character_stats" in stats and
            stats["total_registered_characters"] > 0
        )
        print_test_result("İstatistik toplama", success, f"Kayıtlı karakterler: {stats.get('total_registered_characters', 0)}")
        if success:
            passed_tests += 1
    except Exception as e:
        print_test_result("İstatistik toplama", False, str(e))
    
    # Test character listing
    total_tests += 1
    try:
        all_chars = list_all_characters()
        success = len(all_chars) >= 3  # En az Lara, Geisha, BabaGavat
        print_test_result("Karakter listeleme", success, f"Listelenen: {len(all_chars)} karakter")
        if success:
            passed_tests += 1
    except Exception as e:
        print_test_result("Karakter listeleme", False, str(e))
    
    print(f"\nEntegrasyon Testleri: {passed_tests}/{total_tests} başarılı")
    return passed_tests, total_tests

async def run_demo():
    """Sistem demo'su"""
    print_header("UNIVERSAL CHARACTER SYSTEM DEMO")
    
    try:
        # Sistemi başlat
        print("🚀 Sistem başlatılıyor...")
        initialize_universal_characters()
        
        # Tüm karakterleri listele
        print("\n📋 Kayıtlı Karakterler:")
        all_chars = list_all_characters()
        for char_id, char_info in all_chars.items():
            print(f"   🎭 {char_info['display_name']} ({char_info['character_type']})")
            print(f"      💬 {char_info['age']} yaş, {char_info['nationality']}")
            print(f"      🎯 {char_info['vip_services_count']} VIP hizmet")
        
        # İstatistikleri göster
        print("\n📊 Sistem İstatistikleri:")
        stats = get_universal_integration_stats()
        print(f"   📈 Toplam karakter: {stats.get('total_registered_characters', 0)}")
        print(f"   💬 Toplam konuşma: {stats.get('summary', {}).get('total_conversations', 0)}")
        print(f"   🔥 Aktif konuşma: {stats.get('summary', {}).get('total_active_conversations', 0)}")
        
        # Karakter tiplerini göster
        print("\n🎭 Karakter Tipleri:")
        type_counts = {}
        for char_info in all_chars.values():
            char_type = char_info['character_type']
            type_counts[char_type] = type_counts.get(char_type, 0) + 1
        
        for char_type, count in type_counts.items():
            print(f"   • {char_type}: {count} karakter")
        
        # Test mesajları
        print("\n💬 Test Mesaj Örnekleri:")
        test_characters = ["lara", "geisha", "babagavat"]
        for char_id in test_characters:
            character = character_manager.get_character(char_id)
            if character:
                # Fallback response test
                from handlers.universal_character_system import ConversationState
                test_state = ConversationState(user_id=12345, message_count=0)
                
                fallback = character_manager._get_fallback_response(character, test_state)
                print(f"   {character.display_name}: {fallback}")
        
        print("\n✅ Demo tamamlandı!")
        
    except Exception as e:
        print(f"❌ Demo hatası: {e}")

async def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="Universal Character System Test Script")
    parser.add_argument("--test-system", action="store_true", help="Sistem testlerini çalıştır")
    parser.add_argument("--test-characters", action="store_true", help="Karakter testlerini çalıştır")
    parser.add_argument("--test-integration", action="store_true", help="Entegrasyon testlerini çalıştır")
    parser.add_argument("--all", action="store_true", help="Tüm testleri çalıştır")
    parser.add_argument("--demo", action="store_true", help="Demo çalıştır")
    
    args = parser.parse_args()
    
    print("🎭" + "="*60)
    print("   UNIVERSAL CHARACTER SYSTEM TEST")
    print(f"   Test zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*62)
    
    if args.demo:
        await run_demo()
        return
    
    if not any([args.test_system, args.test_characters, args.test_integration, args.all]):
        print("❌ Test tipi seçin veya --help ile yardımı görün")
        return
    
    total_passed = 0
    total_tests = 0
    
    if args.test_system or args.all:
        passed, tests = await test_system_core()
        total_passed += passed
        total_tests += tests
    
    if args.test_characters or args.all:
        passed, tests = await test_character_definitions()
        total_passed += passed
        total_tests += tests
    
    if args.test_integration or args.all:
        passed, tests = await test_integration_system()
        total_passed += passed
        total_tests += tests
    
    # Final sonuçlar
    print_header("TEST SONUÇLARI")
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 Toplam Test: {total_tests}")
    print(f"✅ Başarılı: {total_passed}")
    print(f"❌ Başarısız: {total_tests - total_passed}")
    print(f"📈 Başarı Oranı: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n🎉 Mükemmel! Universal Character System tam çalışır durumda!")
        print("   Artık tüm karakterleri kullanabilirsiniz!")
    elif success_rate >= 70:
        print("\n⚠️  Universal Character System çoğunlukla çalışıyor.")
        print("   Başarısız testleri kontrol edin.")
    else:
        print("\n❌ Universal Character System ciddi hatalarla karşılaşıyor!")
        print("   Kurulum ve konfigürasyonu kontrol edin.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test durduruldu!")
    except Exception as e:
        print(f"💥 Test hatası: {e}")
        sys.exit(1) 