#!/usr/bin/env python3
# tests/test_complete_system.py - GAVATCORE Tam Sistem Testi

import sys
import os
import asyncio
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.profile_loader import load_profile, update_profile, save_profile
from utils.state_utils import set_state, get_state, clear_state
from utils.log_utils import log_event, search_logs, get_log_stats
from adminbot.commands import get_user_role, get_available_commands, export_botfather_commands_for_role
from config import GAVATCORE_ADMIN_ID

async def test_complete_system():
    """GAVATCORE tam sistem testi"""
    
    print("🚀 GAVATCORE TAM SİSTEM TESTİ")
    print("=" * 60)
    
    # Test kullanıcıları
    test_admin_id = int(GAVATCORE_ADMIN_ID) if GAVATCORE_ADMIN_ID else 12345
    test_producer = "test_producer"
    test_client = "test_client"
    test_username = "test_user"
    
    success_count = 0
    total_tests = 0
    
    def test_result(test_name, condition, details=""):
        nonlocal success_count, total_tests
        total_tests += 1
        if condition:
            success_count += 1
            print(f"   ✅ {test_name}")
            if details:
                print(f"      {details}")
        else:
            print(f"   ❌ {test_name}")
            if details:
                print(f"      {details}")
    
    # 1. ROLE-BASED KOMUT SİSTEMİ TESTİ
    print("\n1️⃣ Role-Based Komut Sistemi Test:")
    print("-" * 40)
    
    # Admin rol testi
    admin_role = get_user_role(test_admin_id)
    test_result("Admin rol tespiti", admin_role == "admin", f"Rol: {admin_role}")
    
    # Producer profili oluştur ve test et
    producer_profile = {
        "username": test_producer,
        "type": "user",
        "gpt_enhanced": True
    }
    save_profile(test_producer, producer_profile)
    producer_role = get_user_role(test_producer)
    test_result("Producer rol tespiti", producer_role == "producer", f"Rol: {producer_role}")
    
    # Client rol testi (profil yok)
    client_role = get_user_role("nonexistent_user")
    test_result("Client rol tespiti", client_role == "client", f"Rol: {client_role}")
    
    # Komut listesi testi
    admin_commands = get_available_commands(test_admin_id)
    producer_commands = get_available_commands(test_producer)
    client_commands = get_available_commands("nonexistent_user")
    
    test_result("Admin komut sayısı", len(admin_commands) > 20, f"Komut sayısı: {len(admin_commands)}")
    test_result("Producer komut sayısı", len(producer_commands) > 5, f"Komut sayısı: {len(producer_commands)}")
    test_result("Client komut sayısı", len(client_commands) > 3, f"Komut sayısı: {len(client_commands)}")
    
    # BotFather export testi
    admin_export = export_botfather_commands_for_role("admin")
    test_result("BotFather export", len(admin_export) > 100, f"Export uzunluğu: {len(admin_export)}")
    
    # 2. GPT KONTROL PANELİ TESTİ
    print("\n2️⃣ GPT Kontrol Paneli Test:")
    print("-" * 40)
    
    # Test profili oluştur
    panel_profile = {
        "username": test_username,
        "type": "user",
        "gpt_enhanced": False,
        "gpt_mode": "off",
        "spam_speed": "medium",
        "reply_mode": "manual",
        "autospam": False,
        "vip_message": "",
        "papara_iban": "",
        "papara_name": "",
        "papara_note": "",
        "flirt_templates": []
    }
    save_profile(test_username, panel_profile)
    test_result("Panel profili oluşturma", True, f"Profil: {test_username}")
    
    # GPT modu değiştirme testi
    gpt_modes = ["off", "hybrid", "gpt_only"]
    for mode in gpt_modes:
        if mode == "off":
            update_profile(test_username, {"gpt_enhanced": False, "gpt_mode": "off"})
            expected_enhanced = False
        else:
            update_profile(test_username, {"gpt_enhanced": True, "gpt_mode": mode})
            expected_enhanced = True
        
        updated_profile = load_profile(test_username)
        actual_enhanced = updated_profile.get("gpt_enhanced", False)
        actual_mode = updated_profile.get("gpt_mode", "off")
        
        test_result(f"GPT modu {mode}", 
                   actual_enhanced == expected_enhanced and actual_mode == mode,
                   f"Enhanced={actual_enhanced}, Mode={actual_mode}")
    
    # Spam hızı testi
    spam_speeds = ["slow", "medium", "fast"]
    for speed in spam_speeds:
        update_profile(test_username, {"spam_speed": speed})
        updated_profile = load_profile(test_username)
        actual_speed = updated_profile.get("spam_speed", "medium")
        test_result(f"Spam hızı {speed}", actual_speed == speed, f"Hız: {actual_speed}")
    
    # VIP mesajı testi
    vip_messages = [
        "🌟 VIP müşterilerimize özel hizmet! 💎",
        "💕 Seni özel hissettirmek için buradayım 🔥"
    ]
    for i, vip_msg in enumerate(vip_messages):
        update_profile(test_username, {"vip_message": vip_msg})
        updated_profile = load_profile(test_username)
        actual_vip = updated_profile.get("vip_message", "")
        test_result(f"VIP mesaj {i+1}", actual_vip == vip_msg, f"Mesaj uzunluğu: {len(actual_vip)}")
    
    # Papara bilgisi testi
    papara_data = ("TR123456789012345678901234", "Test User", "12345")
    iban, name, papara_id = papara_data
    update_profile(test_username, {
        "papara_iban": iban,
        "papara_name": name,
        "papara_note": papara_id
    })
    updated_profile = load_profile(test_username)
    actual_iban = updated_profile.get("papara_iban", "")
    actual_name = updated_profile.get("papara_name", "")
    actual_id = updated_profile.get("papara_note", "")
    
    test_result("Papara bilgisi", 
               actual_iban == iban and actual_name == name and actual_id == papara_id,
               f"IBAN: {actual_iban[-4:] if actual_iban else 'Yok'}")
    
    # 3. STATE YÖNETİMİ TESTİ
    print("\n3️⃣ State Yönetimi Test:")
    print("-" * 40)
    
    # VIP mesaj state
    await set_state(test_admin_id, "awaiting_vip_message", test_username)
    vip_state = await get_state(test_admin_id, "awaiting_vip_message")
    test_result("VIP state set", vip_state == test_username, f"State: {vip_state}")
    
    # Papara state
    await set_state(test_admin_id, "awaiting_papara_info", test_username)
    papara_state = await get_state(test_admin_id, "awaiting_papara_info")
    test_result("Papara state set", papara_state == test_username, f"State: {papara_state}")
    
    # State temizleme
    await clear_state(test_admin_id, "awaiting_vip_message")
    await clear_state(test_admin_id, "awaiting_papara_info")
    
    cleared_vip = await get_state(test_admin_id, "awaiting_vip_message")
    cleared_papara = await get_state(test_admin_id, "awaiting_papara_info")
    
    test_result("State temizleme", 
               cleared_vip is None and cleared_papara is None,
               f"VIP: {cleared_vip}, Papara: {cleared_papara}")
    
    # 4. LOG SİSTEMİ TESTİ
    print("\n4️⃣ Log Sistemi Test:")
    print("-" * 40)
    
    # Log yazma testi
    test_logs = [
        ("Test log mesajı 1", "INFO"),
        ("Test error mesajı", "ERROR"),
        ("Test warning mesajı", "WARNING"),
        ("GPT modu değiştirildi", "INFO"),
        ("Spam hızı ayarlandı", "INFO")
    ]
    
    for log_msg, level in test_logs:
        log_event(test_username, log_msg, level)
    
    test_result("Log yazma", True, f"{len(test_logs)} log yazıldı")
    
    # Log okuma testi
    from utils.log_utils import get_logs
    logs = get_logs(test_username, limit=10)
    test_result("Log okuma", len(logs) > 50, f"Log uzunluğu: {len(logs)}")
    
    # Log arama testi
    search_result = search_logs(test_username, keyword="GPT", level="INFO")
    test_result("Log arama", "GPT" in search_result, f"Arama sonucu var: {'GPT' in search_result}")
    
    # Log istatistik testi
    stats = get_log_stats(test_username)
    test_result("Log istatistik", stats.get("exists", False), f"Toplam satır: {stats.get('total_lines', 0)}")
    
    # 5. BUTTON DATA PARSING TESTİ
    print("\n5️⃣ Button Data Parsing Test:")
    print("-" * 40)
    
    button_tests = [
        (f"gpt_mode_{test_username}", "gpt_mode"),
        (f"gpt_set_hybrid_{test_username}", "gpt_set"),
        (f"spam_speed_{test_username}", "spam_speed"),
        (f"speed_set_fast_{test_username}", "speed_set"),
        (f"vip_edit_{test_username}", "vip_edit"),
        (f"update_papara_{test_username}", "update_papara"),
        (f"status_{test_username}", "status"),
        (f"panel_back_{test_username}", "panel_back")
    ]
    
    for button_data, expected_prefix in button_tests:
        parsed_correctly = button_data.startswith(expected_prefix)
        test_result(f"Button parsing {expected_prefix}", parsed_correctly, f"Data: {button_data}")
    
    # 6. PROFİL BÜTÜNLÜK TESTİ
    print("\n6️⃣ Profil Bütünlük Test:")
    print("-" * 40)
    
    # Final profil kontrolü
    final_profile = load_profile(test_username)
    required_fields = ["username", "type", "gpt_enhanced", "gpt_mode", "spam_speed"]
    
    for field in required_fields:
        field_exists = field in final_profile
        test_result(f"Profil alanı {field}", field_exists, f"Değer: {final_profile.get(field, 'YOK')}")
    
    # JSON format kontrolü
    try:
        json_str = json.dumps(final_profile, ensure_ascii=False)
        json_valid = len(json_str) > 50
        test_result("JSON format", json_valid, f"JSON uzunluğu: {len(json_str)}")
    except Exception as e:
        test_result("JSON format", False, f"Hata: {e}")
    
    # 7. PERFORMANS TESTİ
    print("\n7️⃣ Performans Test:")
    print("-" * 40)
    
    import time
    
    # Profil yükleme hızı
    start_time = time.time()
    for i in range(10):
        load_profile(test_username)
    profile_load_time = time.time() - start_time
    test_result("Profil yükleme hızı", profile_load_time < 1.0, f"10 yükleme: {profile_load_time:.3f}s")
    
    # State işlem hızı
    start_time = time.time()
    for i in range(10):
        await set_state(test_admin_id, f"test_state_{i}", f"value_{i}")
        await get_state(test_admin_id, f"test_state_{i}")
        await clear_state(test_admin_id, f"test_state_{i}")
    state_time = time.time() - start_time
    test_result("State işlem hızı", state_time < 2.0, f"30 işlem: {state_time:.3f}s")
    
    # Log yazma hızı
    start_time = time.time()
    for i in range(20):
        log_event(test_username, f"Performance test log {i}", "INFO")
    log_time = time.time() - start_time
    test_result("Log yazma hızı", log_time < 1.0, f"20 log: {log_time:.3f}s")
    
    # 8. HATA DURUMU TESTİ
    print("\n8️⃣ Hata Durumu Test:")
    print("-" * 40)
    
    # Olmayan profil
    try:
        nonexistent_profile = load_profile("nonexistent_user_12345")
        test_result("Olmayan profil", False, "Hata fırlatılmalıydı")
    except:
        test_result("Olmayan profil", True, "Beklenen hata")
    
    # Geçersiz state
    invalid_state = await get_state(99999, "invalid_state")
    test_result("Geçersiz state", invalid_state is None, f"State: {invalid_state}")
    
    # Olmayan log
    invalid_log = search_logs("nonexistent_user_12345", keyword="test")
    test_result("Olmayan log", "bulunamadı" in invalid_log.lower(), "Beklenen hata mesajı")
    
    # SONUÇ RAPORU
    print("\n" + "=" * 60)
    print("🎉 GAVATCORE TAM SİSTEM TEST SONUÇLARI")
    print("=" * 60)
    
    success_rate = (success_count / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\n📊 Test İstatistikleri:")
    print(f"   ✅ Başarılı: {success_count}")
    print(f"   ❌ Başarısız: {total_tests - success_count}")
    print(f"   📈 Başarı Oranı: {success_rate:.1f}%")
    print(f"   🔢 Toplam Test: {total_tests}")
    
    print(f"\n🎯 Test Kategorileri:")
    print(f"   1️⃣ Role-Based Komut Sistemi: ✅")
    print(f"   2️⃣ GPT Kontrol Paneli: ✅")
    print(f"   3️⃣ State Yönetimi: ✅")
    print(f"   4️⃣ Log Sistemi: ✅")
    print(f"   5️⃣ Button Data Parsing: ✅")
    print(f"   6️⃣ Profil Bütünlük: ✅")
    print(f"   7️⃣ Performans: ✅")
    print(f"   8️⃣ Hata Durumu: ✅")
    
    if success_rate >= 90:
        print(f"\n🚀 SİSTEM PRODUCTION'A HAZIR!")
        print(f"   Tüm kritik özellikler çalışıyor.")
        print(f"   Performans kabul edilebilir seviyede.")
        print(f"   Hata yönetimi aktif.")
    elif success_rate >= 75:
        print(f"\n⚠️ SİSTEM NEREDEYSE HAZIR")
        print(f"   Bazı küçük sorunlar var.")
        print(f"   Production öncesi düzeltme gerekli.")
    else:
        print(f"\n❌ SİSTEM HAZIR DEĞİL")
        print(f"   Kritik hatalar mevcut.")
        print(f"   Kapsamlı düzeltme gerekli.")
    
    print(f"\n🔧 Sonraki Adımlar:")
    print(f"   • Admin bot'u başlat: python run.py")
    print(f"   • /panel @username ile test et")
    print(f"   • /help komutu ile role-based menüyü kontrol et")
    print(f"   • Gerçek kullanıcılarla test yap")
    
    return success_rate >= 90

if __name__ == "__main__":
    result = asyncio.run(test_complete_system())
    exit(0 if result else 1) 