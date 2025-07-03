#!/usr/bin/env python3
"""
GavatCore Engine Test Script
===========================

Bu script GavatCore Engine'in kurulumunu ve çalışmasını test eder.
"""

import asyncio
import json
import sys
import os
from pathlib import Path
import aiohttp
import time

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_BOT_ID = "yayincilara"  # Test için kullanılacak bot
TEST_CHAT_ID = None  # Bu kendi chat ID'niz olmalı (test için)

class GavatCoreEngineTest:
    """GavatCore Engine test sınıfı."""
    
    def __init__(self):
        self.session = None
        self.tests_passed = 0
        self.tests_failed = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health_check(self):
        """Health check endpoint'ini test et."""
        print("🔍 Health check testi...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Health check başarılı: {data['status']}")
                    print(f"   📊 Redis: {data['redis']}")
                    print(f"   🤖 Legacy Adapter: {data['legacy_adapter']['running']}")
                    print(f"   👥 Active Bots: {data['legacy_adapter']['active_bots']}")
                    self.tests_passed += 1
                    return True
                else:
                    print(f"   ❌ Health check başarısız: {response.status}")
                    self.tests_failed += 1
                    return False
        except Exception as e:
            print(f"   ❌ Health check hatası: {e}")
            self.tests_failed += 1
            return False
    
    async def test_bot_status(self):
        """Bot status endpoint'ini test et."""
        print("🤖 Bot status testi...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/bots") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Bot status alındı")
                    print(f"   📊 Toplam bot: {data['total_bots']}")
                    print(f"   🟢 Aktif bot: {data['active_bots']}")
                    
                    for bot_name, bot_info in data['bots'].items():
                        status_icon = "✅" if bot_info['connected'] else "❌"
                        print(f"   {status_icon} {bot_info['display_name']} (@{bot_info['username']})")
                    
                    self.tests_passed += 1
                    return True
                else:
                    print(f"   ❌ Bot status başarısız: {response.status}")
                    self.tests_failed += 1
                    return False
        except Exception as e:
            print(f"   ❌ Bot status hatası: {e}")
            self.tests_failed += 1
            return False
    
    async def test_ai_generation(self):
        """AI response generation'ı test et."""
        print("🧠 AI generation testi...")
        
        try:
            payload = {
                "bot_username": TEST_BOT_ID,
                "user_message": "Merhaba, nasılsın?",
                "conversation_context": {},
                "user_profile": {"user_id": 123456789}
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/ai/generate",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ AI response oluşturuldu")
                    print(f"   💬 Response: {data['response']['content'][:100]}...")
                    self.tests_passed += 1
                    return True
                else:
                    print(f"   ❌ AI generation başarısız: {response.status}")
                    self.tests_failed += 1
                    return False
        except Exception as e:
            print(f"   ❌ AI generation hatası: {e}")
            self.tests_failed += 1
            return False
    
    async def test_message_queueing(self):
        """Message queueing'i test et."""
        print("📬 Message queueing testi...")
        
        try:
            payload = {
                "bot_id": TEST_BOT_ID,
                "content": "Test mesajı - GavatCore Engine'den gönderildi!",
                "target_chat_id": TEST_CHAT_ID or 123456789,  # Dummy ID if not provided
                "message_type": "direct_message",
                "priority": "normal"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/send-message",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Mesaj kuyruğa eklendi")
                    print(f"   🆔 Message ID: {data['message_id']}")
                    print(f"   📊 Status: {data['status']}")
                    self.tests_passed += 1
                    return True
                else:
                    print(f"   ❌ Message queueing başarısız: {response.status}")
                    self.tests_failed += 1
                    return False
        except Exception as e:
            print(f"   ❌ Message queueing hatası: {e}")
            self.tests_failed += 1
            return False
    
    async def test_stats(self):
        """System stats'ı test et."""
        print("📊 System stats testi...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Stats alındı")
                    print(f"   📬 Message Pool: {data['message_pool']}")
                    print(f"   ⏰ Scheduler: {data['scheduler']}")
                    print(f"   👷 Worker: Running={data['worker']['is_running']}")
                    self.tests_passed += 1
                    return True
                else:
                    print(f"   ❌ Stats başarısız: {response.status}")
                    self.tests_failed += 1
                    return False
        except Exception as e:
            print(f"   ❌ Stats hatası: {e}")
            self.tests_failed += 1
            return False
    
    async def test_schedule_message(self):
        """Message scheduling'i test et."""
        print("⏰ Message scheduling testi...")
        
        try:
            from datetime import datetime, timedelta
            
            # 1 dakika sonra için zamanla
            schedule_time = (datetime.utcnow() + timedelta(minutes=1)).isoformat()
            
            payload = {
                "bot_id": TEST_BOT_ID,
                "content": "Zamanlanmış test mesajı!",
                "target_chat_id": TEST_CHAT_ID or 123456789,
                "schedule_time": schedule_time,
                "recurring": False
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/schedule-message",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Mesaj zamanlandı")
                    print(f"   🆔 Task ID: {data['task_id']}")
                    print(f"   📊 Status: {data['status']}")
                    self.tests_passed += 1
                    return True
                else:
                    print(f"   ❌ Message scheduling başarısız: {response.status}")
                    self.tests_failed += 1
                    return False
        except Exception as e:
            print(f"   ❌ Message scheduling hatası: {e}")
            self.tests_failed += 1
            return False
    
    async def run_all_tests(self):
        """Tüm testleri çalıştır."""
        print("🚀 GavatCore Engine Test Başlıyor...\n")
        print("="*60)
        
        # Test sırası
        tests = [
            self.test_health_check,
            self.test_bot_status,
            self.test_ai_generation,
            self.test_message_queueing,
            self.test_stats,
            self.test_schedule_message,
        ]
        
        for test in tests:
            await test()
            print()  # Boş satır
            await asyncio.sleep(1)  # Test'ler arası kısa bekleme
        
        # Sonuçları göster
        print("="*60)
        print("📊 TEST SONUÇLARI")
        print("="*60)
        print(f"✅ Başarılı: {self.tests_passed}")
        print(f"❌ Başarısız: {self.tests_failed}")
        print(f"📊 Toplam: {self.tests_passed + self.tests_failed}")
        
        if self.tests_failed == 0:
            print("🎉 TÜM TESTLER BAŞARILI!")
            print("🚀 GavatCore Engine hazır ve çalışıyor!")
        else:
            print("⚠️ Bazı testler başarısız oldu.")
            print("🔧 Lütfen log'ları kontrol edin.")
        
        print("="*60)


def check_prerequisites():
    """Ön koşulları kontrol et."""
    print("🔍 Ön koşul kontrolü...")
    
    # Redis kontrolü
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("   ✅ Redis bağlantısı başarılı")
    except Exception as e:
        print(f"   ❌ Redis bağlantısı başarısız: {e}")
        print("   💡 Redis'i başlatın: brew services start redis")
        return False
    
    # GavatCore Engine dosyalarını kontrol et
    engine_dir = Path("gavatcore_engine")
    if not engine_dir.exists():
        print(f"   ❌ GavatCore Engine dizini bulunamadı: {engine_dir}")
        return False
    else:
        print("   ✅ GavatCore Engine dizini bulundu")
    
    # Session dosyalarını kontrol et
    sessions_dir = Path("sessions")
    if not sessions_dir.exists():
        print("   ⚠️ Sessions dizini bulunamadı")
        print("   💡 Session dosyalarınızı sessions/ dizinine koyun")
    else:
        session_files = list(sessions_dir.glob("*.session"))
        print(f"   ✅ {len(session_files)} session dosyası bulundu")
    
    # Persona dosyalarını kontrol et
    personas_dir = Path("data/personas")
    if not personas_dir.exists():
        print("   ⚠️ Personas dizini bulunamadı")
    else:
        persona_files = list(personas_dir.glob("*.json"))
        print(f"   ✅ {len(persona_files)} persona dosyası bulundu")
    
    return True


async def main():
    """Ana test fonksiyonu."""
    print("🔥 GavatCore Engine Test Script")
    print("="*60)
    
    # Ön koşulları kontrol et
    if not check_prerequisites():
        print("❌ Ön koşullar karşılanmıyor. Lütfen kurulumu tamamlayın.")
        return
    
    print("\n💡 GavatCore Engine'in çalıştığından emin olun:")
    print("   python gavatcore_engine/integrations/production_launcher.py")
    print("\n⏳ 5 saniye bekleniyor...\n")
    
    await asyncio.sleep(5)
    
    # Test'leri çalıştır
    async with GavatCoreEngineTest() as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test iptal edildi.")
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        sys.exit(1) 