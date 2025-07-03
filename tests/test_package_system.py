#!/usr/bin/env python3
# test_package_system.py - Paket Sistemi Test Script

import asyncio
from datetime import datetime
from core.package_manager import package_manager, PackageType
from core.crm_database import crm_db
from core.user_segmentation import user_segmentation
from core.dynamic_delivery_optimizer import delivery_optimizer
from utils.log_utils import log_event

async def test_package_features():
    """Paket özelliklerini test et"""
    print("\n" + "="*60)
    print("🧪 PAKET SİSTEMİ TESTİ")
    print("="*60)
    
    # Test kullanıcıları
    basic_user_id = 123456789  # Test Basic kullanıcı
    enterprise_user_id = 987654321  # Test Enterprise kullanıcı
    
    print("\n1️⃣ Paket Ataması Testi")
    print("-" * 40)
    
    # Basic paket ata
    package_manager.set_user_package(basic_user_id, PackageType.BASIC)
    print(f"✅ User {basic_user_id} -> Basic paket atandı")
    
    # Enterprise paket ata
    package_manager.set_user_package(enterprise_user_id, PackageType.ENTERPRISE)
    print(f"✅ User {enterprise_user_id} -> Enterprise paket atandı")
    
    # Paketleri kontrol et
    basic_package = package_manager.get_user_package(basic_user_id)
    enterprise_package = package_manager.get_user_package(enterprise_user_id)
    
    print(f"\n📦 Basic kullanıcı paketi: {basic_package.value}")
    print(f"📦 Enterprise kullanıcı paketi: {enterprise_package.value}")
    
    print("\n2️⃣ Paket Limitleri Testi")
    print("-" * 40)
    
    # Basic limitleri
    print("\nBasic Paket Limitleri:")
    print(f"  Günlük mesaj: {package_manager.get_limit(basic_user_id, 'daily_messages')}")
    print(f"  Grup limiti: {package_manager.get_limit(basic_user_id, 'groups')}")
    print(f"  Cooldown: {package_manager.get_limit(basic_user_id, 'cooldown_minutes')} dakika")
    
    # Enterprise limitleri
    print("\nEnterprise Paket Limitleri:")
    print(f"  Günlük mesaj: {package_manager.get_limit(enterprise_user_id, 'daily_messages')}")
    print(f"  Grup limiti: {package_manager.get_limit(enterprise_user_id, 'groups')}")
    print(f"  Cooldown: {package_manager.get_limit(enterprise_user_id, 'cooldown_minutes')} dakika")
    print(f"  CRM kullanıcı: {package_manager.get_limit(enterprise_user_id, 'crm_users')}")
    print(f"  Segment sayısı: {package_manager.get_limit(enterprise_user_id, 'segments')}")
    
    print("\n3️⃣ Özellik Erişim Kontrolü")
    print("-" * 40)
    
    modules_to_test = [
        "basic_spam",
        "group_handler",
        "dm_handler",
        "crm_database",
        "user_segmentation",
        "dynamic_delivery_optimizer"
    ]
    
    print("\nBasic Kullanıcı Erişimleri:")
    for module in modules_to_test:
        access = package_manager.is_feature_enabled(basic_user_id, module)
        print(f"  {module}: {'✅ Erişim var' if access else '❌ Erişim yok'}")
    
    print("\nEnterprise Kullanıcı Erişimleri:")
    for module in modules_to_test:
        access = package_manager.is_feature_enabled(enterprise_user_id, module)
        print(f"  {module}: {'✅ Erişim var' if access else '❌ Erişim yok'}")
    
    print("\n4️⃣ CRM Test (Sadece Enterprise)")
    print("-" * 40)
    
    # Test kullanıcı profili oluştur
    test_user_profile = await crm_db.create_user_profile(
        user_id=1234567,
        username="test_user",
        first_name="Test",
        last_name="User",
        is_premium=True
    )
    
    print(f"✅ Test kullanıcı profili oluşturuldu: {test_user_profile.username}")
    
    # Segmentasyon testi
    if package_manager.is_feature_enabled(enterprise_user_id, "user_segmentation"):
        segments = await user_segmentation.segment_user(test_user_profile)
        
        if segments:
            print(f"\n🎯 Kullanıcı segmentleri ({len(segments)} adet):")
            for seg in segments[:3]:
                print(f"  • {seg.segment.value} (Güven: {seg.confidence:.2f})")
                print(f"    Özellikler: {', '.join(seg.characteristics[:2])}")
        else:
            print("❌ Segmentasyon başarısız")
    else:
        print("❌ Enterprise özelliği - Basic kullanıcı erişemez")
    
    print("\n5️⃣ Paket Yükseltme/Düşürme Testi")
    print("-" * 40)
    
    # Basic'i Enterprise'a yükselt
    if package_manager.upgrade_package(basic_user_id):
        print(f"✅ User {basic_user_id} Enterprise'a yükseltildi")
        new_package = package_manager.get_user_package(basic_user_id)
        print(f"   Yeni paket: {new_package.value}")
    
    # Enterprise'ı Basic'e düşür
    if package_manager.downgrade_package(enterprise_user_id):
        print(f"✅ User {enterprise_user_id} Basic'e düşürüldü")
        new_package = package_manager.get_user_package(enterprise_user_id)
        print(f"   Yeni paket: {new_package.value}")
    
    print("\n6️⃣ Paket Bilgileri")
    print("-" * 40)
    
    # Basic paket bilgileri
    basic_info = package_manager.get_package_info(PackageType.BASIC)
    print("\n📦 BASIC Paket:")
    print("Özellikler:")
    for feature in basic_info["features"]:
        print(f"  • {feature}")
    
    # Enterprise paket bilgileri
    enterprise_info = package_manager.get_package_info(PackageType.ENTERPRISE)
    print("\n🏢 ENTERPRISE Paket:")
    print("Özellikler:")
    for feature in enterprise_info["features"][:5]:  # İlk 5 özellik
        print(f"  • {feature}")
    print(f"  ... ve {len(enterprise_info['features']) - 5} özellik daha")
    
    print("\n✅ Paket sistemi testi tamamlandı!")

async def simulate_package_usage():
    """Paket kullanım simülasyonu"""
    print("\n" + "="*60)
    print("🎮 PAKET KULLANIM SİMÜLASYONU")
    print("="*60)
    
    # Basic kullanıcı simülasyonu
    basic_user_id = 111111111
    package_manager.set_user_package(basic_user_id, PackageType.BASIC)
    
    print("\n📦 BASIC Kullanıcı Senaryosu:")
    print("-" * 40)
    
    daily_limit = package_manager.get_limit(basic_user_id, "daily_messages")
    cooldown = package_manager.get_limit(basic_user_id, "cooldown_minutes")
    
    print(f"Günlük limit: {daily_limit} mesaj")
    print(f"Cooldown: {cooldown} dakika")
    print("\nMesaj gönderimi simülasyonu:")
    
    for i in range(5):
        if i < daily_limit:
            print(f"  ✅ Mesaj {i+1}/{daily_limit} gönderildi")
        else:
            print(f"  ❌ Mesaj {i+1} - Günlük limit aşıldı!")
            break
    
    # Enterprise kullanıcı simülasyonu
    enterprise_user_id = 222222222
    package_manager.set_user_package(enterprise_user_id, PackageType.ENTERPRISE)
    
    print("\n\n🏢 ENTERPRISE Kullanıcı Senaryosu:")
    print("-" * 40)
    
    if package_manager.is_feature_enabled(enterprise_user_id, "dynamic_delivery_optimizer"):
        print("✅ Dinamik gönderim optimizer aktif")
        print("📊 Segmentlere göre otomatik mesaj gönderimi")
        print("🎯 GPT destekli kişiselleştirme")
        print("📈 Performans analizi ve öğrenme")
    
    print("\n✅ Simülasyon tamamlandı!")

if __name__ == "__main__":
    print("🚀 Paket Sistemi Test Script Başlatılıyor...")
    
    async def main():
        # Paket özelliklerini test et
        await test_package_features()
        
        # Kullanım simülasyonu
        await simulate_package_usage()
        
        print("\n🎉 Tüm testler tamamlandı!")
    
    asyncio.run(main()) 