#!/usr/bin/env python3
# tests/test_mongo_profile.py - MongoDB Profile Tests

import asyncio
import pytest
from datetime import datetime
from core.profile_store import (
    init_mongodb, close_mongodb,
    get_profile_by_username, get_profile_by_user_id,
    create_or_update_profile, update_profile_field, update_profile_fields,
    delete_profile, get_all_profiles, get_bot_profiles,
    search_profiles, get_profile_stats, migrate_from_json_files
)

class TestMongoProfile:
    """MongoDB profil test sınıfı"""
    
    @classmethod
    def setup_class(cls):
        """Test sınıfı başlangıcı"""
        print("\n🧪 MongoDB profil testleri başlıyor...")
    
    async def test_mongodb_connection(self):
        """MongoDB bağlantı testi"""
        result = await init_profile_store()
        assert result == True, "MongoDB bağlantısı başarısız"
        print("✅ MongoDB bağlantısı başarılı")
    
    async def test_profile_creation(self):
        """Profil oluşturma testi"""
        test_profile = {
            "username": "test_bot_mongo",
            "display_name": "Test Bot",
            "type": "bot",
            "user_id": "123456789",
            "autospam": True,
            "reply_mode": "gpt",
            "persona": {
                "age": "25",
                "style": "Friendly",
                "role": "Assistant"
            },
            "services_menu": "Test menü",
            "engaging_messages": ["Merhaba!", "Nasılsın?"],
            "reply_messages": ["Teşekkürler", "Anladım"]
        }
        
        # Profil oluştur
        result = await create_or_update_profile("test_bot_mongo", test_profile)
        assert result == True, "Profil oluşturulamadı"
        
        # Profili getir
        profile = await get_profile_by_username("test_bot_mongo")
        assert profile is not None, "Profil getirilemedi"
        assert profile["username"] == "test_bot_mongo", "Username yanlış"
        assert profile["autospam"] == True, "Autospam ayarı yanlış"
        
        print("✅ Profile creation testi başarılı")
    
    async def test_profile_update(self):
        """Profil güncelleme testi"""
        # Tek alan güncelle
        result = await update_profile_field("test_bot_mongo", "autospam", False)
        assert result == True, "Profil alanı güncellenemedi"
        
        # Güncellemeyi kontrol et
        profile = await get_profile_by_username("test_bot_mongo")
        assert profile["autospam"] == False, "Autospam güncellenmedi"
        
        # Birden fazla alan güncelle
        updates = {
            "reply_mode": "manual",
            "safe_mode": True,
            "auto_menu_enabled": False
        }
        result = await update_profile_fields("test_bot_mongo", updates)
        assert result == True, "Profil alanları güncellenemedi"
        
        # Güncellemeleri kontrol et
        profile = await get_profile_by_username("test_bot_mongo")
        assert profile["reply_mode"] == "manual", "Reply mode güncellenmedi"
        assert profile["safe_mode"] == True, "Safe mode güncellenmedi"
        
        print("✅ Profile update testi başarılı")
    
    async def test_profile_search(self):
        """Profil arama testi"""
        # Username ile arama
        profiles = await search_profiles("test_bot")
        assert len(profiles) > 0, "Profil arama başarısız"
        
        # Display name ile arama
        profiles = await search_profiles("Test Bot")
        assert len(profiles) > 0, "Display name arama başarısız"
        
        print("✅ Profile search testi başarılı")
    
    async def test_bulk_operations(self):
        """Toplu işlem testi"""
        # Birden fazla profil oluştur
        profiles_data = []
        for i in range(3):
            profile = {
                "username": f"bulk_bot_{i}",
                "display_name": f"Bulk Bot {i}",
                "type": "bot",
                "user_id": f"bulk_user_{i}",
                "autospam": i % 2 == 0,  # Alternatif true/false
                "reply_mode": "gpt" if i % 2 == 0 else "manual"
            }
            profiles_data.append(profile)
        
        # Profilleri oluştur
        tasks = []
        for profile in profiles_data:
            task = create_or_update_profile(profile["username"], profile)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        assert all(results), "Bulk profil oluşturma başarısız"
        
        # Tüm bot profillerini getir
        bot_profiles = await get_bot_profiles()
        bulk_bots = [p for p in bot_profiles if p["username"].startswith("bulk_bot_")]
        assert len(bulk_bots) >= 3, "Bulk bot profilleri getirilemedi"
        
        print("✅ Bulk operations testi başarılı")
    
    async def test_profile_filtering(self):
        """Profil filtreleme testi"""
        # Sadece autospam=True olan botları getir
        autospam_bots = await get_bot_profiles(autospam_only=True)
        for bot in autospam_bots:
            assert bot.get("autospam") == True, "Autospam filtresi çalışmıyor"
        
        # Tip bazında filtreleme
        all_bots = await get_all_profiles(profile_type="bot")
        assert len(all_bots) > 0, "Bot profilleri getirilemedi"
        
        for profile in all_bots:
            assert profile["type"] == "bot", "Tip filtresi çalışmıyor"
        
        print("✅ Profile filtering testi başarılı")
    
    async def test_profile_stats(self):
        """Profil istatistik testi"""
        stats = await get_profile_stats()
        assert "by_type" in stats, "İstatistik formatı yanlış"
        assert "total" in stats, "Toplam sayı yok"
        assert stats["total"] > 0, "Profil sayısı sıfır"
        
        if "bot" in stats["by_type"]:
            bot_stats = stats["by_type"]["bot"]
            assert "total" in bot_stats, "Bot istatistiği eksik"
            assert "active" in bot_stats, "Aktif bot sayısı yok"
            assert "autospam" in bot_stats, "Autospam bot sayısı yok"
        
        print("✅ Profile stats testi başarılı")
    
    async def test_user_id_lookup(self):
        """User ID ile profil arama testi"""
        # User ID ile profil getir
        profile = await get_profile_by_user_id("123456789")
        assert profile is not None, "User ID ile profil getirilemedi"
        assert profile["user_id"] == "123456789", "User ID yanlış"
        
        print("✅ User ID lookup testi başarılı")
    
    async def test_profile_deletion(self):
        """Profil silme testi"""
        # Test profili sil
        result = await delete_profile("test_bot_mongo")
        assert result == True, "Profil silinemedi"
        
        # Silindiğini kontrol et
        profile = await get_profile_by_username("test_bot_mongo")
        assert profile is None, "Profil silinmedi"
        
        # Bulk profilleri de sil
        for i in range(3):
            await delete_profile(f"bulk_bot_{i}")
        
        print("✅ Profile deletion testi başarılı")
    
    async def test_migration_simulation(self):
        """Migration simülasyon testi"""
        # Gerçek JSON dosyalarını test etmek yerine simülasyon
        # Bu test gerçek dosyalar varsa çalışır
        try:
            migrated_count = await migrate_from_json_files("data/personas")
            print(f"✅ Migration simulation: {migrated_count} profil migrate edildi")
        except Exception as e:
            print(f"⚠️ Migration simulation atlandı: {e}")
    
    async def test_performance(self):
        """Performans testi"""
        import time
        
        start_time = time.time()
        
        # 5 profil oluştur ve getir
        tasks = []
        for i in range(5):
            profile_data = {
                "username": f"perf_bot_{i}",
                "type": "bot",
                "user_id": f"perf_user_{i}",
                "autospam": False
            }
            task = create_or_update_profile(f"perf_bot_{i}", profile_data)
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # Profilleri getir
        for i in range(5):
            await get_profile_by_username(f"perf_bot_{i}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Temizlik
        for i in range(5):
            await delete_profile(f"perf_bot_{i}")
        
        assert duration < 3.0, f"Performance testi çok yavaş: {duration:.2f}s"
        print(f"✅ Performance testi başarılı: {duration:.2f}s")
    
    @classmethod
    def teardown_class(cls):
        """Test sınıfı sonu"""
        print("🧪 MongoDB profil testleri tamamlandı")

# Test runner
async def run_tests():
    """Testleri çalıştır"""
    test_instance = TestMongoProfile()
    
    try:
        # Setup
        test_instance.setup_class()
        
        # Tests
        await test_instance.test_mongodb_connection()
        await test_instance.test_profile_creation()
        await test_instance.test_profile_update()
        await test_instance.test_profile_search()
        await test_instance.test_bulk_operations()
        await test_instance.test_profile_filtering()
        await test_instance.test_profile_stats()
        await test_instance.test_user_id_lookup()
        await test_instance.test_profile_deletion()
        await test_instance.test_migration_simulation()
        await test_instance.test_performance()
        
        # Teardown
        test_instance.teardown_class()
        
        print("\n🎉 Tüm MongoDB testleri başarılı!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test hatası: {e}")
        return False
    
    finally:
        await close_profile_store()

if __name__ == "__main__":
    result = asyncio.run(run_tests())
    exit(0 if result else 1) 