#!/usr/bin/env python3
# test_integration.py - Multi-database entegrasyon testi

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time
from datetime import datetime

# Database sistemleri
from core.db.connection import init_database, close_database
from core.db.crud import log_event, get_events, search_events
from core.profile_store import init_profile_store, close_profile_store, create_or_update_profile, get_profile_by_username
from utils.redis_client import init_redis, close_redis, set_state, get_state, set_cooldown, check_cooldown

# Updated handlers
from utils.log_utils import log_event_async
from core.profile_loader import load_profile_async, save_profile_async

async def test_postgresql_logs():
    """PostgreSQL/SQLite log sistemi testi"""
    print("📊 PostgreSQL/SQLite log sistemi test ediliyor...")
    
    try:
        # Event log kaydet
        success = await log_event(
            user_identifier="test_user_123",
            event_type="dm_received",
            message="Test mesajı alındı",
            level="INFO"
        )
        
        if success:
            print("✅ Event log kaydedildi")
        else:
            print("❌ Event log kaydedilemedi")
            return False
        
        # Event'leri getir
        events = await get_events(user_identifier="test_user_123", limit=5)
        if events:
            print(f"✅ {len(events)} event getirildi")
            for event in events:
                print(f"   - {event.timestamp}: {event.message}")
        else:
            print("❌ Event'ler getirilemedi")
            return False
        
        # Event arama
        search_results = await search_events(
            keyword="test",
            user_identifier="test_user_123",
            limit=5
        )
        if search_results:
            print(f"✅ {len(search_results)} arama sonucu bulundu")
        else:
            print("❌ Arama sonucu bulunamadı")
        
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL test hatası: {e}")
        return False

async def test_mongodb_profiles():
    """MongoDB/File-based profil sistemi testi"""
    print("👤 MongoDB/File-based profil sistemi test ediliyor...")
    
    try:
        # Test profili oluştur
        test_profile = {
            "username": "test_bot_123",
            "display_name": "Test Bot",
            "type": "bot",
            "reply_mode": "hybrid",
            "autospam": True,
            "services_menu": "Test hizmet menüsü",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Profil kaydet
        success = await create_or_update_profile("test_bot_123", test_profile)
        if success:
            print("✅ Profil kaydedildi")
        else:
            print("❌ Profil kaydedilemedi")
            return False
        
        # Profil getir
        retrieved_profile = await get_profile_by_username("test_bot_123")
        if retrieved_profile:
            print(f"✅ Profil getirildi: {retrieved_profile['display_name']}")
            print(f"   - Type: {retrieved_profile.get('type')}")
            print(f"   - Reply Mode: {retrieved_profile.get('reply_mode')}")
            print(f"   - Autospam: {retrieved_profile.get('autospam')}")
        else:
            print("❌ Profil getirilemedi")
            return False
        
        # Updated profile loader test
        try:
            profile_via_loader = await load_profile_async("test_bot_123")
            if profile_via_loader:
                print("✅ Profile loader ile profil getirildi")
            else:
                print("⚠️ Profile loader ile profil getirilemedi (normal olabilir)")
        except Exception as e:
            print(f"⚠️ Profile loader hatası: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB test hatası: {e}")
        return False

async def test_redis_state():
    """Redis state management testi"""
    print("🔄 Redis state management sistemi test ediliyor...")
    
    try:
        # State kaydet
        dm_key = "dm:test_bot_123:test_user_456"
        conversation_state = {
            "last_bot_message": time.time(),
            "user_responded": False,
            "conversation_active": True,
            "phase": "initial_contact",
            "auto_message_count": 2,
            "manual_mode_active": False
        }
        
        await set_state(dm_key, "conversation_state", conversation_state, expire_seconds=3600)
        print("✅ Conversation state kaydedildi")
        
        # State getir
        retrieved_state = await get_state(dm_key, "conversation_state")
        if retrieved_state:
            print(f"✅ State getirildi: phase={retrieved_state.get('phase')}")
            print(f"   - Auto message count: {retrieved_state.get('auto_message_count')}")
            print(f"   - Manual mode: {retrieved_state.get('manual_mode_active')}")
        else:
            print("❌ State getirilemedi")
            return False
        
        # Cooldown test
        await set_cooldown("test_user_456", "spam", 60)  # 60 saniye cooldown
        print("✅ Cooldown kaydedildi")
        
        # Cooldown kontrol
        remaining_time = await check_cooldown("test_user_456", "spam")
        if remaining_time is not None and remaining_time > 0:
            print(f"✅ Cooldown aktif (kalan: {remaining_time}s)")
        else:
            print("❌ Cooldown aktif değil")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Redis test hatası: {e}")
        return False

async def test_log_utils_integration():
    """Log utils entegrasyon testi"""
    print("📝 Log utils entegrasyon testi...")
    
    try:
        # Async log event
        await log_event_async(
            user_id_or_username="test_integration_user",
            text="Entegrasyon testi log mesajı",
            level="INFO",
            event_type="integration_test"
        )
        print("✅ Async log event başarılı")
        
        # Biraz bekle
        await asyncio.sleep(0.5)
        
        # Log'ları kontrol et
        events = await get_events(user_identifier="test_integration_user", limit=5)
        if events:
            print(f"✅ {len(events)} log event bulundu")
            for event in events:
                if "entegrasyon" in event.message.lower():
                    print(f"   - ✅ Entegrasyon log'u bulundu: {event.message}")
                    break
        else:
            print("⚠️ Log event'ler bulunamadı")
        
        return True
        
    except Exception as e:
        print(f"❌ Log utils entegrasyon hatası: {e}")
        return False

async def test_dm_handler_state_integration():
    """DM handler state entegrasyon testi"""
    print("💬 DM handler state entegrasyon testi...")
    
    try:
        from handlers.dm_handler import get_conversation_state, update_conversation_state
        
        # Test DM key
        dm_key = "dm:integration_bot:integration_user"
        
        # İlk state'i getir (otomatik oluşturulmalı)
        initial_state = await get_conversation_state(dm_key)
        if initial_state:
            print("✅ İlk conversation state oluşturuldu")
            print(f"   - Phase: {initial_state.get('phase')}")
            print(f"   - Conversation active: {initial_state.get('conversation_active')}")
        else:
            print("❌ İlk conversation state oluşturulamadı")
            return False
        
        # State güncelle - bot mesaj gönderdi
        updated_state = await update_conversation_state(dm_key, bot_sent_message=True)
        if updated_state:
            print("✅ State güncellendi - bot mesaj gönderdi")
            print(f"   - Auto message count: {updated_state.get('auto_message_count')}")
        
        # State güncelle - manuel müdahale
        manual_state = await update_conversation_state(dm_key, manual_intervention=True)
        if manual_state:
            print("✅ State güncellendi - manuel müdahale")
            print(f"   - Phase: {manual_state.get('phase')}")
            print(f"   - Manual mode active: {manual_state.get('manual_mode_active')}")
        
        return True
        
    except Exception as e:
        print(f"❌ DM handler state entegrasyon hatası: {e}")
        return False

async def run_integration_tests():
    """Tüm entegrasyon testlerini çalıştır"""
    print("🚀 GAVATCORE MULTI-DATABASE ENTEGRASYON TESTİ")
    print("=" * 60)
    
    # Database'leri başlat
    print("🗄️ Database sistemleri başlatılıyor...")
    await init_database()
    await init_profile_store()
    await init_redis()
    print("✅ Tüm database sistemleri başlatıldı\n")
    
    # Test sonuçları
    test_results = []
    
    # PostgreSQL/SQLite test
    result1 = await test_postgresql_logs()
    test_results.append(("PostgreSQL/SQLite Logs", result1))
    print()
    
    # MongoDB/File-based test
    result2 = await test_mongodb_profiles()
    test_results.append(("MongoDB/File-based Profiles", result2))
    print()
    
    # Redis test
    result3 = await test_redis_state()
    test_results.append(("Redis State Management", result3))
    print()
    
    # Log utils entegrasyon
    result4 = await test_log_utils_integration()
    test_results.append(("Log Utils Integration", result4))
    print()
    
    # DM handler state entegrasyon
    result5 = await test_dm_handler_state_integration()
    test_results.append(("DM Handler State Integration", result5))
    print()
    
    # Sonuçları özetle
    print("📊 TEST SONUÇLARI")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{test_name:<35} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 ÖZET: {passed}/{total} test başarılı ({(passed/total)*100:.1f}%)")
    
    # Database'leri kapat
    print("\n🔒 Database bağlantıları kapatılıyor...")
    await close_database()
    await close_profile_store()
    await close_redis()
    print("✅ Tüm bağlantılar kapatıldı")
    
    if passed == total:
        print("\n🎉 TÜM TESTLER BAŞARILI! Multi-database sistemi production'a hazır!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test başarısız. Lütfen hataları kontrol edin.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_integration_tests())
    exit(0 if success else 1) 