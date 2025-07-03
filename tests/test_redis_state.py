#!/usr/bin/env python3
# tests/test_redis_state.py - Redis State Tests

import asyncio
import pytest
import time
from utils.redis_client import (
    init_redis, close_redis,
    set_state, get_state, delete_state, clear_state, get_all_user_states,
    set_cooldown, check_cooldown, clear_cooldown,
    set_global_state, get_global_state,
    increment_counter, get_counter, reset_counter,
    add_to_list, get_list,
    get_redis_stats
)

class TestRedisState:
    """Redis state test sınıfı"""
    
    @classmethod
    def setup_class(cls):
        """Test sınıfı başlangıcı"""
        print("\n🧪 Redis state testleri başlıyor...")
    
    async def test_redis_connection(self):
        """Redis bağlantı testi"""
        result = await init_redis()
        assert result == True, "Redis bağlantısı başarısız"
        print("✅ Redis bağlantısı başarılı")
    
    async def test_basic_state_operations(self):
        """Temel state işlemleri testi"""
        user_id = "test_user_123"
        
        # String state
        result = await set_state(user_id, "test_string", "test_value")
        assert result == True, "String state kaydedilemedi"
        
        value = await get_state(user_id, "test_string")
        assert value == "test_value", "String state getirilemedi"
        
        # Dict state
        test_dict = {"key1": "value1", "key2": 123, "key3": True}
        result = await set_state(user_id, "test_dict", test_dict)
        assert result == True, "Dict state kaydedilemedi"
        
        value = await get_state(user_id, "test_dict")
        assert value == test_dict, "Dict state getirilemedi"
        
        # List state
        test_list = ["item1", "item2", 123, True]
        result = await set_state(user_id, "test_list", test_list)
        assert result == True, "List state kaydedilemedi"
        
        value = await get_state(user_id, "test_list")
        assert value == test_list, "List state getirilemedi"
        
        print("✅ Basic state operations testi başarılı")
    
    async def test_state_expiration(self):
        """State expiration testi"""
        user_id = "test_user_expire"
        
        # 2 saniye TTL ile state kaydet
        result = await set_state(user_id, "expire_test", "will_expire", expire_seconds=2)
        assert result == True, "Expire state kaydedilemedi"
        
        # Hemen kontrol et
        value = await get_state(user_id, "expire_test")
        assert value == "will_expire", "Expire state getirilemedi"
        
        # 3 saniye bekle
        await asyncio.sleep(3)
        
        # Expire olmuş olmalı
        value = await get_state(user_id, "expire_test", default="expired")
        assert value == "expired", "State expire olmadı"
        
        print("✅ State expiration testi başarılı")
    
    async def test_state_deletion(self):
        """State silme testi"""
        user_id = "test_user_delete"
        
        # State kaydet
        await set_state(user_id, "delete_test", "to_be_deleted")
        
        # Var olduğunu kontrol et
        value = await get_state(user_id, "delete_test")
        assert value == "to_be_deleted", "State kaydedilmedi"
        
        # Sil
        result = await delete_state(user_id, "delete_test")
        assert result == True, "State silinemedi"
        
        # Silindiğini kontrol et
        value = await get_state(user_id, "delete_test", default="deleted")
        assert value == "deleted", "State silinmedi"
        
        print("✅ State deletion testi başarılı")
    
    async def test_bulk_state_operations(self):
        """Toplu state işlemleri testi"""
        user_id = "test_user_bulk"
        
        # Birden fazla state kaydet
        states = {
            "state1": "value1",
            "state2": {"nested": "dict"},
            "state3": [1, 2, 3],
            "state4": True,
            "state5": 42
        }
        
        tasks = []
        for key, value in states.items():
            task = set_state(user_id, key, value)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        assert all(results), "Bulk state kaydetme başarısız"
        
        # Tüm state'leri getir
        all_states = await get_all_user_states(user_id)
        assert len(all_states) >= 5, "Tüm state'ler getirilemedi"
        
        for key, expected_value in states.items():
            assert key in all_states, f"State {key} bulunamadı"
            assert all_states[key] == expected_value, f"State {key} değeri yanlış"
        
        # Tüm state'leri temizle
        cleared_count = await clear_state(user_id)
        assert cleared_count >= 5, "State'ler temizlenemedi"
        
        # Temizlendiğini kontrol et
        all_states = await get_all_user_states(user_id)
        assert len(all_states) == 0, "State'ler temizlenmedi"
        
        print("✅ Bulk state operations testi başarılı")
    
    async def test_cooldown_operations(self):
        """Cooldown işlemleri testi"""
        user_id = "test_user_cooldown"
        action = "spam_message"
        
        # Cooldown ayarla (3 saniye)
        result = await set_cooldown(user_id, action, 3)
        assert result == True, "Cooldown ayarlanamadı"
        
        # Cooldown kontrol et
        remaining = await check_cooldown(user_id, action)
        assert remaining is not None, "Cooldown kontrol edilemedi"
        assert remaining <= 3, "Cooldown süresi yanlış"
        
        # 1 saniye bekle
        await asyncio.sleep(1)
        
        # Tekrar kontrol et
        remaining = await check_cooldown(user_id, action)
        assert remaining is not None, "Cooldown hala aktif olmalı"
        assert remaining <= 2, "Cooldown azalmadı"
        
        # Cooldown temizle
        result = await clear_cooldown(user_id, action)
        assert result == True, "Cooldown temizlenemedi"
        
        # Temizlendiğini kontrol et
        remaining = await check_cooldown(user_id, action)
        assert remaining is None, "Cooldown temizlenmedi"
        
        print("✅ Cooldown operations testi başarılı")
    
    async def test_global_state(self):
        """Global state testi"""
        # Global state kaydet
        global_data = {
            "system_status": "active",
            "maintenance_mode": False,
            "active_bots": ["bot1", "bot2", "bot3"]
        }
        
        result = await set_global_state("system_config", global_data)
        assert result == True, "Global state kaydedilemedi"
        
        # Global state getir
        value = await get_global_state("system_config")
        assert value == global_data, "Global state getirilemedi"
        
        # Expire ile global state
        result = await set_global_state("temp_config", {"temp": True}, expire_seconds=2)
        assert result == True, "Expire global state kaydedilemedi"
        
        # Hemen kontrol et
        value = await get_global_state("temp_config")
        assert value["temp"] == True, "Expire global state getirilemedi"
        
        # 3 saniye bekle
        await asyncio.sleep(3)
        
        # Expire olmuş olmalı
        value = await get_global_state("temp_config", default={"expired": True})
        assert value["expired"] == True, "Global state expire olmadı"
        
        print("✅ Global state testi başarılı")
    
    async def test_counter_operations(self):
        """Counter işlemleri testi"""
        user_id = "test_user_counter"
        
        # Counter başlangıç değeri
        count = await get_counter(user_id, "messages")
        assert count == 0, "Counter başlangıç değeri yanlış"
        
        # Counter artır
        new_count = await increment_counter(user_id, "messages")
        assert new_count == 1, "Counter artırılamadı"
        
        # Birden fazla artır
        new_count = await increment_counter(user_id, "messages", amount=5)
        assert new_count == 6, "Counter toplu artırılamadı"
        
        # Counter değerini getir
        count = await get_counter(user_id, "messages")
        assert count == 6, "Counter değeri yanlış"
        
        # Counter sıfırla
        result = await reset_counter(user_id, "messages")
        assert result == True, "Counter sıfırlanamadı"
        
        # Sıfırlandığını kontrol et
        count = await get_counter(user_id, "messages")
        assert count == 0, "Counter sıfırlanmadı"
        
        print("✅ Counter operations testi başarılı")
    
    async def test_list_operations(self):
        """Liste işlemleri testi"""
        user_id = "test_user_list"
        list_name = "message_history"
        
        # Liste'ye eleman ekle
        items = ["mesaj1", "mesaj2", {"type": "special", "content": "mesaj3"}]
        
        for item in items:
            result = await add_to_list(user_id, list_name, item)
            assert result == True, f"Liste'ye eleman eklenemedi: {item}"
        
        # Liste'yi getir
        retrieved_items = await get_list(user_id, list_name)
        assert len(retrieved_items) == 3, "Liste uzunluğu yanlış"
        
        # Redis LPUSH kullandığı için ters sırada olacak
        assert retrieved_items[0] == {"type": "special", "content": "mesaj3"}, "Liste elemanı yanlış"
        assert retrieved_items[1] == "mesaj2", "Liste elemanı yanlış"
        assert retrieved_items[2] == "mesaj1", "Liste elemanı yanlış"
        
        # Max length ile test
        for i in range(5):
            await add_to_list(user_id, "limited_list", f"item_{i}", max_length=3)
        
        limited_items = await get_list(user_id, "limited_list")
        assert len(limited_items) == 3, "Max length çalışmadı"
        
        print("✅ List operations testi başarılı")
    
    async def test_concurrent_operations(self):
        """Eşzamanlı işlemler testi"""
        user_id = "test_user_concurrent"
        
        # Eşzamanlı counter artırma
        tasks = []
        for i in range(10):
            task = increment_counter(user_id, "concurrent_test")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Son değer 10 olmalı
        final_count = await get_counter(user_id, "concurrent_test")
        assert final_count == 10, f"Concurrent counter yanlış: {final_count}"
        
        # Eşzamanlı state kaydetme
        tasks = []
        for i in range(5):
            task = set_state(user_id, f"concurrent_state_{i}", f"value_{i}")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        assert all(results), "Concurrent state kaydetme başarısız"
        
        # Tüm state'leri kontrol et
        all_states = await get_all_user_states(user_id)
        concurrent_states = {k: v for k, v in all_states.items() if k.startswith("concurrent_state_")}
        assert len(concurrent_states) == 5, "Concurrent state'ler eksik"
        
        print("✅ Concurrent operations testi başarılı")
    
    async def test_redis_stats(self):
        """Redis istatistik testi"""
        stats = await get_redis_stats()
        
        assert "connected_clients" in stats, "Redis stats eksik"
        assert "used_memory_human" in stats, "Memory stats eksik"
        assert "total_keys" in stats, "Key count eksik"
        
        assert stats["total_keys"] >= 0, "Key count negatif"
        
        print(f"✅ Redis stats testi başarılı - {stats['total_keys']} keys, {stats['used_memory_human']} memory")
    
    async def test_performance(self):
        """Performans testi"""
        user_id = "test_user_performance"
        
        start_time = time.time()
        
        # 20 state kaydet
        tasks = []
        for i in range(20):
            task = set_state(user_id, f"perf_state_{i}", f"value_{i}")
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # 20 state getir
        tasks = []
        for i in range(20):
            task = get_state(user_id, f"perf_state_{i}")
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Temizlik
        await clear_state(user_id)
        
        assert duration < 2.0, f"Performance testi çok yavaş: {duration:.2f}s"
        print(f"✅ Performance testi başarılı: {duration:.2f}s")
    
    @classmethod
    def teardown_class(cls):
        """Test sınıfı sonu"""
        print("🧪 Redis state testleri tamamlandı")

# Test runner
async def run_tests():
    """Testleri çalıştır"""
    test_instance = TestRedisState()
    
    try:
        # Setup
        test_instance.setup_class()
        
        # Tests
        await test_instance.test_redis_connection()
        await test_instance.test_basic_state_operations()
        await test_instance.test_state_expiration()
        await test_instance.test_state_deletion()
        await test_instance.test_bulk_state_operations()
        await test_instance.test_cooldown_operations()
        await test_instance.test_global_state()
        await test_instance.test_counter_operations()
        await test_instance.test_list_operations()
        await test_instance.test_concurrent_operations()
        await test_instance.test_redis_stats()
        await test_instance.test_performance()
        
        # Teardown
        test_instance.teardown_class()
        
        print("\n🎉 Tüm Redis testleri başarılı!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test hatası: {e}")
        return False
    
    finally:
        await close_redis()

if __name__ == "__main__":
    result = asyncio.run(run_tests())
    exit(0 if result else 1) 