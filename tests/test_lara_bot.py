#!/usr/bin/env python3
"""
LARA BOT TEST SCRIPT
====================

Lara bot'unu test etmek ve konfigürasyonu doğrulamak için kullanılır.

Kullanım:
    python test_lara_bot.py --test-prompt     # Prompt testleri
    python test_lara_bot.py --test-handler    # Handler testleri
    python test_lara_bot.py --test-integration # Entegrasyon testleri
    python test_lara_bot.py --all             # Tüm testler
"""

import asyncio
import argparse
import sys
from datetime import datetime
from typing import Dict, Any

# Test imports
from gpt.prompts.larabot_prompt import LaraPromptUtils, LARA_SYSTEM_PROMPT, LARA_CHARACTER_CONFIG
from handlers.lara_integration import (
    validate_lara_config,
    get_lara_response_preview,
    create_lara_bot_profile,
    is_lara_bot,
    get_lara_integration_stats
)
from handlers.lara_bot_handler import LaraConfig, get_lara_stats

def print_header(title: str):
    """Test başlığı yazdır"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_test_result(test_name: str, success: bool, details: str = ""):
    """Test sonucunu yazdır"""
    status = "✅ BAŞARILI" if success else "❌ BAŞARISIZ"
    print(f"{status} - {test_name}")
    if details:
        print(f"    {details}")

async def test_prompt_system():
    """Prompt sistemi testleri"""
    print_header("LARA PROMPT SİSTEMİ TESTLERİ")
    
    total_tests = 0
    passed_tests = 0
    
    # Test 1: Basic prompt insertion
    total_tests += 1
    try:
        test_prompt = LaraPromptUtils.insertUserName("TestUser")
        success = "TestUser" in test_prompt and len(test_prompt) > 500
        print_test_result("Kullanıcı adı ekleme", success)
        if success:
            passed_tests += 1
    except Exception as e:
        print_test_result("Kullanıcı adı ekleme", False, str(e))
    
    # Test 2: Character config
    total_tests += 1
    try:
        config = LaraPromptUtils.getCharacterConfig()
        success = config.get("name") == "Lara" and config.get("age") == 24
        print_test_result("Karakter konfigürasyonu", success)
        if success:
            passed_tests += 1
            print(f"    Karakter: {config['name']}, Yaş: {config['age']}, Uyruk: {config['nationality']}")
    except Exception as e:
        print_test_result("Karakter konfigürasyonu", False, str(e))
    
    # Test 3: Version check
    total_tests += 1
    try:
        version = LaraPromptUtils.getVersion()
        success = version == "1.0.0"
        print_test_result("Versiyon kontrolü", success, f"Versiyon: {version}")
        if success:
            passed_tests += 1
    except Exception as e:
        print_test_result("Versiyon kontrolü", False, str(e))
    
    # Test 4: Prompt content validation
    total_tests += 1
    try:
        required_elements = ["🎭", "📝", "💰", "🎯", "⚠️", "🎨", "davay", "moya lyubov", "krasotka"]
        missing_elements = [elem for elem in required_elements if elem not in LARA_SYSTEM_PROMPT]
        success = len(missing_elements) == 0
        print_test_result("Prompt içerik kontrolü", success, 
                         f"Eksik öğeler: {missing_elements}" if missing_elements else "Tüm öğeler mevcut")
        if success:
            passed_tests += 1
    except Exception as e:
        print_test_result("Prompt içerik kontrolü", False, str(e))
    
    print(f"\nPrompt Testleri: {passed_tests}/{total_tests} başarılı")
    return passed_tests, total_tests

async def test_handler_system():
    """Handler sistemi testleri"""
    print_header("LARA HANDLER SİSTEMİ TESTLERİ")
    
    total_tests = 0
    passed_tests = 0
    
    # Test 1: LaraConfig validation
    total_tests += 1
    try:
        success = (
            len(LaraConfig.RUSSIAN_WORDS) > 0 and
            len(LaraConfig.LARA_EMOJIS) > 0 and
            len(LaraConfig.VIP_SERVICES) > 0 and
            LaraConfig.PAPARA_INFO.get("papara_no") is not None
        )
        print_test_result("LaraConfig doğrulama", success)
        if success:
            passed_tests += 1
            print(f"    Rusça kelimeler: {len(LaraConfig.RUSSIAN_WORDS)}")
            print(f"    Emoji havuzu: {len(LaraConfig.LARA_EMOJIS)}")
            print(f"    VIP hizmetler: {len(LaraConfig.VIP_SERVICES)}")
    except Exception as e:
        print_test_result("LaraConfig doğrulama", False, str(e))
    
    # Test 2: Response preview
    total_tests += 1
    try:
        preview = get_lara_response_preview("Merhaba", "TestUser")
        success = len(preview) > 10 and "TestUser" in preview
        print_test_result("Yanıt önizlemesi", success, f"Örnek: {preview[:50]}...")
        if success:
            passed_tests += 1
    except Exception as e:
        print_test_result("Yanıt önizlemesi", False, str(e))
    
    # Test 3: Stats system
    total_tests += 1
    try:
        stats = get_lara_stats()
        success = isinstance(stats, dict) and "total_conversations" in stats
        print_test_result("İstatistik sistemi", success)
        if success:
            passed_tests += 1
            print(f"    Toplam konuşma: {stats.get('total_conversations', 0)}")
    except Exception as e:
        print_test_result("İstatistik sistemi", False, str(e))
    
    print(f"\nHandler Testleri: {passed_tests}/{total_tests} başarılı")
    return passed_tests, total_tests

async def test_integration_system():
    """Entegrasyon sistemi testleri"""
    print_header("LARA ENTEGRASYON SİSTEMİ TESTLERİ")
    
    total_tests = 0
    passed_tests = 0
    
    # Test 1: Config validation
    total_tests += 1
    try:
        success = validate_lara_config()
        print_test_result("Konfigürasyon doğrulama", success)
        if success:
            passed_tests += 1
    except Exception as e:
        print_test_result("Konfigürasyon doğrulama", False, str(e))
    
    # Test 2: Bot detection
    total_tests += 1
    try:
        # Pozitif test
        lara_detected = is_lara_bot("lara_test_bot")
        # Negatif test
        normal_detected = is_lara_bot("normal_bot")
        
        success = lara_detected and not normal_detected
        print_test_result("Bot tespit sistemi", success)
        if success:
            passed_tests += 1
    except Exception as e:
        print_test_result("Bot tespit sistemi", False, str(e))
    
    # Test 3: Profile creation
    total_tests += 1
    try:
        profile = create_lara_bot_profile("test_lara", 12345)
        success = (
            profile.get("type") == "lara_bot" and
            profile.get("display_name") == "Lara" and
            "lara_config" in profile
        )
        print_test_result("Profil oluşturma", success)
        if success:
            passed_tests += 1
            print(f"    Tip: {profile.get('type')}")
            print(f"    İsim: {profile.get('display_name')}")
    except Exception as e:
        print_test_result("Profil oluşturma", False, str(e))
    
    # Test 4: Integration stats
    total_tests += 1
    try:
        stats = get_lara_integration_stats()
        success = (
            "integration_version" in stats and
            "prompt_version" in stats and
            "character_config" in stats
        )
        print_test_result("Entegrasyon istatistikleri", success)
        if success:
            passed_tests += 1
            print(f"    Entegrasyon v: {stats.get('integration_version')}")
            print(f"    Prompt v: {stats.get('prompt_version')}")
    except Exception as e:
        print_test_result("Entegrasyon istatistikleri", False, str(e))
    
    print(f"\nEntegrasyon Testleri: {passed_tests}/{total_tests} başarılı")
    return passed_tests, total_tests

def show_configuration():
    """Mevcut konfigürasyonu göster"""
    print_header("LARA BOT KONFIGÜRASYONU")
    
    try:
        config = LaraPromptUtils.getCharacterConfig()
        
        print("📋 Karakter Bilgileri:")
        print(f"   🏷️  İsim: {config['name']}")
        print(f"   🎂  Yaş: {config['age']}")
        print(f"   🌍  Uyruk: {config['nationality']}")
        print(f"   💬  Platform: {config['platform']}")
        print(f"   🗣️  Diller: {', '.join(config['languages'])}")
        
        print("\n✨ Kişilik Özellikleri:")
        for trait in config['personality']:
            print(f"   • {trait}")
        
        print(f"\n💼 VIP Hizmetler ({len(LaraConfig.VIP_SERVICES)} adet):")
        for service, info in LaraConfig.VIP_SERVICES.items():
            print(f"   💎 {service}: {info['price']} - {info['description']}")
        
        print(f"\n🇷🇺 Rusça Kelime Havuzu ({len(LaraConfig.RUSSIAN_WORDS)} adet):")
        print(f"   {', '.join(LaraConfig.RUSSIAN_WORDS)}")
        
        print(f"\n😊 Emoji Havuzu ({len(LaraConfig.LARA_EMOJIS)} adet):")
        print(f"   {''.join(LaraConfig.LARA_EMOJIS)}")
        
        print("\n💳 Ödeme Bilgileri:")
        print(f"   📱 Papara: {LaraConfig.PAPARA_INFO['papara_no']}")
        print(f"   🏦 IBAN: {LaraConfig.PAPARA_INFO['iban']}")
        print(f"   👤 Hesap: {LaraConfig.PAPARA_INFO['hesap_sahibi']}")
        
    except Exception as e:
        print(f"❌ Konfigürasyon gösterme hatası: {e}")

async def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="Lara Bot Test Script")
    parser.add_argument("--test-prompt", action="store_true", help="Prompt testlerini çalıştır")
    parser.add_argument("--test-handler", action="store_true", help="Handler testlerini çalıştır")
    parser.add_argument("--test-integration", action="store_true", help="Entegrasyon testlerini çalıştır")
    parser.add_argument("--all", action="store_true", help="Tüm testleri çalıştır")
    parser.add_argument("--config", action="store_true", help="Konfigürasyonu göster")
    
    args = parser.parse_args()
    
    print("🌹" + "="*50)
    print("   LARA BOT TEST SİSTEMİ")
    print(f"   Test zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*52)
    
    if args.config or not any([args.test_prompt, args.test_handler, args.test_integration, args.all]):
        show_configuration()
        return
    
    total_passed = 0
    total_tests = 0
    
    if args.test_prompt or args.all:
        passed, tests = await test_prompt_system()
        total_passed += passed
        total_tests += tests
    
    if args.test_handler or args.all:
        passed, tests = await test_handler_system()
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
        print("\n🎉 Tebrikler! Lara Bot sistemi tam çalışır durumda!")
        print("   Artık bot'u başlatabilirsiniz: python lara_bot_launcher.py")
    elif success_rate >= 70:
        print("\n⚠️  Lara Bot çoğunlukla çalışıyor, bazı hatalar var.")
        print("   Başarısız testleri kontrol edin.")
    else:
        print("\n❌ Lara Bot ciddi hatalarla karşılaşıyor!")
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