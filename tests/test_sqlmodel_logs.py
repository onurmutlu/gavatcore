#!/usr/bin/env python3
# tests/test_sqlmodel_logs.py - PostgreSQL/SQLAlchemy Tests

import asyncio
import pytest
from datetime import datetime, timedelta
from core.db.connection import init_postgres, close_postgres
from core.db.crud import (
    log_event, get_events, search_events,
    log_sale, get_sales, update_sale_status,
    log_message, get_message_stats,
    create_or_update_session, get_active_sessions
)

class TestSQLModelLogs:
    """PostgreSQL/SQLAlchemy test sınıfı"""
    
    @classmethod
    def setup_class(cls):
        """Test sınıfı başlangıcı"""
        print("\n🧪 PostgreSQL/SQLAlchemy testleri başlıyor...")
    
    async def test_postgres_connection(self):
        """PostgreSQL bağlantı testi"""
        result = await init_database()
        assert result == True, "PostgreSQL bağlantısı başarısız"
        print("✅ PostgreSQL bağlantısı başarılı")
    
    async def test_event_logging(self):
        """Event log testi"""
        # Event kaydet
        result = await log_event(
            user_id="test_user_123",
            event_type="test_event",
            message="Test mesajı",
            context={"test": "data"},
            level="INFO",
            username="test_user"
        )
        assert result == True, "Event log kaydedilemedi"
        
        # Event'leri getir
        events = await get_events(user_id="test_user_123", limit=10)
        assert len(events) > 0, "Event'ler getirilemedi"
        assert events[0].event_type == "test_event", "Event type yanlış"
        
        print("✅ Event logging testi başarılı")
    
    async def test_event_search(self):
        """Event arama testi"""
        # Arama yap
        events = await search_events("test", user_id="test_user_123")
        assert len(events) > 0, "Event arama başarısız"
        
        print("✅ Event search testi başarılı")
    
    async def test_sale_logging(self):
        """Satış log testi"""
        # Satış kaydet
        result = await log_sale(
            user_id="test_user_123",
            product_type="vip_membership",
            amount=250.0,
            customer_id="customer_456",
            bot_username="test_bot",
            product_name="VIP Üyelik",
            payment_method="papara"
        )
        assert result == True, "Sale log kaydedilemedi"
        
        # Satışları getir
        sales = await get_sales(user_id="test_user_123")
        assert len(sales) > 0, "Satışlar getirilemedi"
        assert sales[0].amount == 250.0, "Satış miktarı yanlış"
        
        # Satış durumunu güncelle
        sale_id = sales[0].id
        update_result = await update_sale_status(sale_id, "completed", "Test tamamlandı")
        assert update_result == True, "Satış durumu güncellenemedi"
        
        print("✅ Sale logging testi başarılı")
    
    async def test_message_logging(self):
        """Mesaj log testi"""
        # Mesaj kaydet
        result = await log_message(
            bot_username="test_bot",
            message_type="spam",
            target_type="group",
            target_id="group_789",
            message_content="Test spam mesajı",
            success=True,
            response_time_ms=150,
            target_name="Test Grup"
        )
        assert result == True, "Message log kaydedilemedi"
        
        # Mesaj istatistikleri
        stats = await get_message_stats(bot_username="test_bot", hours_back=1)
        assert stats["total_messages"] > 0, "Mesaj istatistikleri alınamadı"
        assert "spam" in stats["by_type"], "Mesaj tipi istatistiği yok"
        
        print("✅ Message logging testi başarılı")
    
    async def test_user_sessions(self):
        """Kullanıcı session testi"""
        # Session oluştur
        result = await create_or_update_session(
            user_id="test_user_123",
            username="test_user",
            bot_type="producer",
            extra_data={"test": "session_data"}
        )
        assert result == True, "Session oluşturulamadı"
        
        # Aktif session'ları getir
        sessions = await get_active_sessions(bot_type="producer")
        assert len(sessions) > 0, "Aktif session'lar getirilemedi"
        
        print("✅ User sessions testi başarılı")
    
    async def test_bulk_operations(self):
        """Toplu işlem testi"""
        # Birden fazla event kaydet
        tasks = []
        for i in range(5):
            task = log_event(
                user_id=f"bulk_user_{i}",
                event_type="bulk_test",
                message=f"Bulk test mesajı {i}",
                level="INFO"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        assert all(results), "Bulk event logging başarısız"
        
        # Bulk event'leri getir
        events = await get_events(event_type="bulk_test", limit=10)
        assert len(events) >= 5, "Bulk event'ler getirilemedi"
        
        print("✅ Bulk operations testi başarılı")
    
    async def test_performance(self):
        """Performans testi"""
        import time
        
        start_time = time.time()
        
        # 10 event kaydet
        tasks = []
        for i in range(10):
            task = log_event(
                user_id="perf_user",
                event_type="performance_test",
                message=f"Performance test {i}"
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert duration < 2.0, f"Performance testi çok yavaş: {duration:.2f}s"
        print(f"✅ Performance testi başarılı: {duration:.2f}s")
    
    @classmethod
    def teardown_class(cls):
        """Test sınıfı sonu"""
        print("🧪 PostgreSQL/SQLAlchemy testleri tamamlandı")

# Test runner
async def run_tests():
    """Testleri çalıştır"""
    test_instance = TestSQLModelLogs()
    
    try:
        # Setup
        test_instance.setup_class()
        
        # Tests
        await test_instance.test_postgres_connection()
        await test_instance.test_event_logging()
        await test_instance.test_event_search()
        await test_instance.test_sale_logging()
        await test_instance.test_message_logging()
        await test_instance.test_user_sessions()
        await test_instance.test_bulk_operations()
        await test_instance.test_performance()
        
        # Teardown
        test_instance.teardown_class()
        
        print("\n🎉 Tüm PostgreSQL testleri başarılı!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test hatası: {e}")
        return False
    
    finally:
        await close_database()

if __name__ == "__main__":
    result = asyncio.run(run_tests())
    exit(0 if result else 1) 