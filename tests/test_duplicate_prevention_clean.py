#!/usr/bin/env python3
"""
Çift Mesaj Gönderimi ve Grup Üyelik Kontrolü Test Sistemi - Temiz Test
Bu test dosyası Redis'i temizleyerek invite_manager sistemlerini test eder.
"""

import asyncio
import time
import hashlib
from datetime import datetime
from core.invite_manager import invite_manager
from utilities.group_invite_strategy import group_invite_strategy
from utilities.log_utils import log_event
from utilities.redis_client import redis_client, init_redis

class DuplicatePreventionTester:
    def __init__(self):
        self.test_bot_username = "test_bot_clean"
        self.test_user_id = 987654321
        self.test_group_id = -1009876543210
        self.test_results = []
    
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Test sonucunu kaydet"""
        result = {
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ GEÇTI" if passed else "❌ BAŞARISIZ"
        print(f"{status} - {test_name}: {details}")
    
    async def cleanup_test_data(self):
        """Test verilerini temizle"""
        try:
            if not redis_client:
                await init_redis()
            
            # Test bot'un tüm verilerini temizle
            patterns = [
                f"gavatcore:*{self.test_bot_username}*",
                f"gavatcore:*{self.test_user_id}*",
                f"gavatcore:*{self.test_group_id}*",
                f"*{self.test_bot_username}*",
                f"*{self.test_user_id}*",
                f"*{self.test_group_id}*"
            ]
            
            for pattern in patterns:
                keys = await redis_client.keys(pattern)
                if keys:
                    await redis_client.delete(*keys)
                    print(f"🧹 Temizlendi: {len(keys)} key ({pattern})")
            
            print("✅ Test verileri temizlendi")
            
        except Exception as e:
            print(f"❌ Test verisi temizleme hatası: {e}")
    
    async def test_dm_cooldown_system(self):
        """DM cooldown sistemini test et"""
        print("\n🧪 DM Cooldown Sistemi Testi")
        print("=" * 50)
        
        # Test 1: İlk DM gönderimi - izin verilmeli
        can_send, reason = await invite_manager.can_send_dm(self.test_bot_username, self.test_user_id)
        self.log_test_result(
            "İlk DM Gönderimi", 
            can_send, 
            f"İlk DM gönderilmeli: {reason}"
        )
        
        if can_send:
            # DM gönderimini kaydet
            await invite_manager.record_dm_sent(self.test_bot_username, self.test_user_id)
            
            # Test 2: Hemen ardından ikinci DM - cooldown nedeniyle engellenmeli
            can_send_2, reason_2 = await invite_manager.can_send_dm(self.test_bot_username, self.test_user_id)
            self.log_test_result(
                "Cooldown Kontrolü", 
                not can_send_2, 
                f"İkinci DM engellenmeli: {reason_2}"
            )
        
        # Test 3: DM istatistiklerini kontrol et
        stats = await invite_manager.get_dm_stats(self.test_bot_username)
        expected_daily = 1 if can_send else 0
        self.log_test_result(
            "DM İstatistikleri", 
            stats["daily_sent"] == expected_daily,
            f"Günlük gönderim: {stats['daily_sent']}/{stats['daily_limit']}"
        )
    
    async def test_duplicate_message_detection(self):
        """Duplicate mesaj tespit sistemini test et"""
        print("\n🧪 Duplicate Mesaj Tespit Testi")
        print("=" * 50)
        
        test_message = "Bu bir temiz test mesajıdır"
        message_hash = hashlib.md5(test_message.encode()).hexdigest()[:8]
        
        # Test 1: İlk mesaj - duplicate olmamalı
        is_duplicate_1 = await invite_manager.check_duplicate_message(
            self.test_bot_username, self.test_user_id, message_hash
        )
        self.log_test_result(
            "İlk Mesaj Kontrolü", 
            not is_duplicate_1, 
            "İlk mesaj duplicate olmamalı"
        )
        
        # Test 2: Aynı mesaj tekrar - duplicate olmalı
        is_duplicate_2 = await invite_manager.check_duplicate_message(
            self.test_bot_username, self.test_user_id, message_hash
        )
        self.log_test_result(
            "Duplicate Mesaj Kontrolü", 
            is_duplicate_2, 
            "Aynı mesaj duplicate olarak tespit edilmeli"
        )
        
        # Test 3: Farklı mesaj - duplicate olmamalı
        different_message = "Bu farklı bir temiz test mesajıdır"
        different_hash = hashlib.md5(different_message.encode()).hexdigest()[:8]
        is_duplicate_3 = await invite_manager.check_duplicate_message(
            self.test_bot_username, self.test_user_id, different_hash
        )
        self.log_test_result(
            "Farklı Mesaj Kontrolü", 
            not is_duplicate_3, 
            "Farklı mesaj duplicate olmamalı"
        )
    
    async def test_group_invite_cooldown(self):
        """Grup davet cooldown sistemini test et"""
        print("\n🧪 Grup Davet Cooldown Testi")
        print("=" * 50)
        
        # Test 1: İlk grup daveti - izin verilmeli
        can_invite, reason = await invite_manager.can_send_group_invite(
            self.test_bot_username, self.test_user_id, self.test_group_id
        )
        self.log_test_result(
            "İlk Grup Daveti", 
            can_invite, 
            f"İlk davet gönderilmeli: {reason}"
        )
        
        if can_invite:
            # Grup davetini kaydet
            await invite_manager.record_group_invite(
                self.test_bot_username, self.test_user_id, self.test_group_id
            )
            
            # Test 2: Hemen ardından ikinci davet - cooldown nedeniyle engellenmeli
            can_invite_2, reason_2 = await invite_manager.can_send_group_invite(
                self.test_bot_username, self.test_user_id, self.test_group_id
            )
            self.log_test_result(
                "Grup Davet Cooldown", 
                not can_invite_2, 
                f"İkinci davet engellenmeli: {reason_2}"
            )
    
    async def test_invite_rejection_system(self):
        """Davet reddetme sistemini test et"""
        print("\n🧪 Davet Reddetme Sistemi Testi")
        print("=" * 50)
        
        test_group_2 = -1009876543211
        test_user_2 = self.test_user_id + 100  # Farklı kullanıcı
        
        # Test 1: Normal davet - izin verilmeli
        can_invite, reason = await invite_manager.can_send_group_invite(
            self.test_bot_username, test_user_2, test_group_2
        )
        self.log_test_result(
            "Normal Davet", 
            can_invite, 
            f"Normal davet izin verilmeli: {reason}"
        )
        
        # Daveti reddet olarak işaretle
        await invite_manager.mark_invite_rejected(test_user_2, test_group_2)
        
        # Test 2: Reddedilen davet - engellenmeli
        can_invite_2, reason_2 = await invite_manager.can_send_group_invite(
            self.test_bot_username, test_user_2, test_group_2
        )
        self.log_test_result(
            "Reddedilen Davet", 
            not can_invite_2, 
            f"Reddedilen davet engellenmeli: {reason_2}"
        )
    
    def print_test_summary(self):
        """Test özetini yazdır"""
        print("\n📊 TEST ÖZETİ")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        
        print(f"Toplam Test: {total_tests}")
        print(f"✅ Geçen: {passed_tests}")
        print(f"❌ Başarısız: {failed_tests}")
        print(f"📈 Başarı Oranı: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ BAŞARISIZ TESTLER:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 SONUÇ:", "TÜM TESTLER BAŞARILI!" if failed_tests == 0 else f"{failed_tests} TEST BAŞARISIZ!")
    
    async def run_all_tests(self):
        """Tüm testleri çalıştır"""
        print("🚀 Çift Mesaj Gönderimi ve Grup Üyelik Kontrolü Test Sistemi - Temiz Test")
        print("=" * 80)
        
        try:
            # Önce test verilerini temizle
            await self.cleanup_test_data()
            
            # Testleri çalıştır
            await self.test_dm_cooldown_system()
            await self.test_duplicate_message_detection()
            await self.test_group_invite_cooldown()
            await self.test_invite_rejection_system()
            
        except Exception as e:
            print(f"❌ Test çalıştırma hatası: {e}")
            self.log_test_result("Test Sistemi", False, f"Hata: {e}")
        
        finally:
            self.print_test_summary()
            # Test sonrası temizlik
            await self.cleanup_test_data()

async def main():
    """Ana test fonksiyonu"""
    tester = DuplicatePreventionTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 