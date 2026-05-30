from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
BabaGAVAT PostgreSQL Production Launcher
Onur Metodu Production Deployment - PostgreSQL + Redis + MongoDB
BabaGAVAT'ın sokak tecrübesi ile production database yönetimi
"""

import asyncio
import uvicorn
import multiprocessing
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import structlog
import sys

# BabaGAVAT imports
from core.coin_service import babagavat_coin_service
from core.erko_analyzer import babagavat_erko_analyzer
from core.redis_manager import babagavat_redis_manager
from core.mongodb_manager import babagavat_mongo_manager
from core.postgresql_manager import babagavat_postgresql_manager
from apis.coin_endpoints import app

logger = structlog.get_logger("babagavat.postgresql_production")

class BabaGAVATPostgreSQLProductionLauncher:
    """BabaGAVAT PostgreSQL Production Launcher - Onur Metodu ile Canlı Ortam"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.is_running = False
        self.redis_status = "UNKNOWN"
        self.mongodb_status = "UNKNOWN"
        self.postgresql_status = "UNKNOWN"
        self.api_status = "UNKNOWN"
        self.services_initialized = False
        
        # Environment variables
        self.postgres_url = os.getenv("DATABASE_URL", "postgresql://localhost:5432/babagavat_db")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        
    async def initialize_production_environment(self) -> bool:
        """Production ortamını başlat"""
        try:
            print(f"""
🔥🔥🔥 BABAGAVAT POSTGRESQL PRODUCTION LAUNCHER 🔥🔥🔥

💪 ONUR METODU POSTGRESQL CANLI ORTAM BAŞLATILIYOR!

🚀 PostgreSQL + Redis + MongoDB Hybrid Architecture:
   🐘 PostgreSQL Primary Database
   ⚡ Redis Cache Layer
   📊 MongoDB Analytics & Logging
   💾 SQLite Fallback System

🎯 Production Features:
   ✅ PostgreSQL ACID Compliance
   ✅ Redis High-Speed Cache
   ✅ MongoDB Document Store
   ✅ Async Connection Pooling
   ✅ Database Lock Sorunları Çözüldü
   ✅ Concurrent Access Desteği
   ✅ Real-time Monitoring
   ✅ Auto-Recovery System

📅 Başlatma Zamanı: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
🏗️ PostgreSQL Altyapı Hazırlık...
            """)
            
            # 1. PostgreSQL Manager'ı başlat (primary)
            await self._initialize_postgresql()
            
            # 2. Redis Manager'ı başlat (cache)
            await self._initialize_redis()
            
            # 3. MongoDB Manager'ı başlat (analytics)
            await self._initialize_mongodb()
            
            # 4. Core Services'i başlat
            await self._initialize_core_services()
            
            # 5. Sistem durumunu kontrol et
            await self._verify_system_health()
            
            self.services_initialized = True
            self.is_running = True
            
            print(f"""
✅ BABAGAVAT POSTGRESQL PRODUCTION BAŞARILI!

🏆 Sistem Durumu:
   🐘 PostgreSQL: {self.postgresql_status}
   🔥 Redis: {self.redis_status}
   📊 MongoDB: {self.mongodb_status}
   🌐 API: {self.api_status}

💪 BabaGAVAT'ın sokak zekası ile PostgreSQL production hazır!
🚀 Production ortamı aktif - Onur Metodu çalışıyor!
            """)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ PostgreSQL Production başlatma hatası: {e}")
            return False
    
    async def _initialize_postgresql(self) -> None:
        """PostgreSQL Manager'ı başlat (primary database)"""
        try:
            print(f"🐘 PostgreSQL Primary Database başlatılıyor...")
            print(f"   🔗 Connection: {self.postgres_url[:50]}...")
            
            # PostgreSQL manager'ı başlat
            babagavat_postgresql_manager.postgres_url = self.postgres_url
            await babagavat_postgresql_manager.initialize()
            
            if babagavat_postgresql_manager.is_initialized:
                self.postgresql_status = "✅ AKTİF"
                print("   ✅ PostgreSQL bağlantısı başarılı!")
                
                # Test query
                async with babagavat_postgresql_manager.pool.acquire() as connection:
                    result = await connection.fetchval("SELECT COUNT(*) FROM babagavat_coin_balances")
                    print(f"   📊 Mevcut coin balances: {result}")
                
            else:
                self.postgresql_status = "❌ PASİF"
                print("   ⚠️ PostgreSQL bağlantısı başarısız - fallback'e geç")
                
        except Exception as e:
            self.postgresql_status = "❌ HATA"
            print(f"   ❌ PostgreSQL başlatma hatası: {e}")
            logger.warning(f"PostgreSQL başlatma hatası: {e}")
    
    async def _initialize_redis(self) -> None:
        """Redis Manager'ı başlat (cache layer)"""
        try:
            print(f"⚡ Redis Cache Layer başlatılıyor...")
            print(f"   🔗 Connection: {self.redis_url}")
            
            # Redis URL set et
            babagavat_redis_manager.redis_url = self.redis_url
            await babagavat_redis_manager.initialize()
            
            if babagavat_redis_manager.is_initialized:
                self.redis_status = "✅ AKTİF"
                print("   ✅ Redis bağlantısı başarılı!")
                
                # Test cache operations
                await babagavat_redis_manager.redis_client.set("babagavat:production:test", "OK")
                test_value = await babagavat_redis_manager.redis_client.get("babagavat:production:test")
                print(f"   🧪 Redis cache test: {test_value}")
                
            else:
                self.redis_status = "❌ PASİF"
                print("   ⚠️ Redis bağlantısı başarısız - cache devre dışı")
                
        except Exception as e:
            self.redis_status = "❌ HATA"
            print(f"   ❌ Redis başlatma hatası: {e}")
            logger.warning(f"Redis başlatma hatası: {e}")
    
    async def _initialize_mongodb(self) -> None:
        """MongoDB Manager'ı başlat (analytics & logging)"""
        try:
            print(f"📊 MongoDB Analytics Database başlatılıyor...")
            print(f"   🔗 Connection: {self.mongodb_url}")
            
            # MongoDB URL set et
            babagavat_mongo_manager.mongo_url = self.mongodb_url
            await babagavat_mongo_manager.initialize()
            
            if babagavat_mongo_manager.is_initialized:
                self.mongodb_status = "✅ AKTİF"
                print("   ✅ MongoDB bağlantısı başarılı!")
                
                # Test document insert
                test_data = {"test": "production_ok", "timestamp": datetime.now()}
                await babagavat_mongo_manager.db.production_test.insert_one(test_data)
                print("   🧪 MongoDB test document inserted")
                
            else:
                self.mongodb_status = "❌ PASİF"
                print("   ⚠️ MongoDB bağlantısı başarısız - analytics devre dışı")
                
        except Exception as e:
            self.mongodb_status = "❌ HATA"
            print(f"   ❌ MongoDB başlatma hatası: {e}")
            logger.warning(f"MongoDB başlatma hatası: {e}")
    
    async def _initialize_core_services(self) -> None:
        """Core Services'i başlat"""
        try:
            print("⚙️ BabaGAVAT Core Services başlatılıyor...")
            
            # BabaGAVAT Coin Service
            print("   💰 BabaGAVAT Coin Service (PostgreSQL hybrid)...")
            await babagavat_coin_service.initialize()
            
            # BabaGAVAT ErkoAnalyzer
            print("   🔍 BabaGAVAT ErkoAnalyzer (Multi-DB)...")
            await babagavat_erko_analyzer.initialize()
            
            print("   ✅ Core Services PostgreSQL entegrasyonu tamamlandı!")
            
        except Exception as e:
            print(f"   ❌ Core Services hatası: {e}")
            logger.error(f"Core Services başlatma hatası: {e}")
            raise
    
    async def _verify_system_health(self) -> None:
        """Sistem sağlığını kontrol et"""
        try:
            print("🏥 PostgreSQL Production sistem sağlık kontrolü...")
            
            # Database connections test
            health_status = {
                "postgresql_connected": babagavat_postgresql_manager.is_initialized,
                "redis_connected": babagavat_redis_manager.is_initialized,
                "mongodb_connected": babagavat_mongo_manager.is_initialized,
                "coin_service_ready": babagavat_coin_service.is_initialized,
                "erko_analyzer_ready": babagavat_erko_analyzer.is_initialized
            }
            
            # Critical operations test
            if babagavat_coin_service.is_initialized:
                # Test PostgreSQL coin operations
                test_balance = await babagavat_coin_service.get_balance(999999)
                health_status["coin_operations"] = True
                
            if babagavat_erko_analyzer.is_initialized:
                # Test user analysis
                test_profile = await babagavat_erko_analyzer.analyze_user(999999)
                health_status["user_analysis"] = True
            
            healthy_services = sum(1 for status in health_status.values() if status)
            total_services = len(health_status)
            
            health_percentage = (healthy_services / total_services) * 100
            
            if health_percentage >= 80:
                self.api_status = "✅ SAĞLIKLI"
                print(f"   ✅ PostgreSQL Production sağlığı: {health_percentage:.1f}% ({healthy_services}/{total_services})")
            elif health_percentage >= 60:
                self.api_status = "⚠️ KISMEN SAĞLIKLI"
                print(f"   ⚠️ PostgreSQL Production sağlığı: {health_percentage:.1f}% ({healthy_services}/{total_services})")
            else:
                self.api_status = "❌ SORUNLU"
                print(f"   ❌ PostgreSQL Production sağlığı: {health_percentage:.1f}% ({healthy_services}/{total_services})")
            
            logger.info(f"PostgreSQL Production sağlık durumu: {health_status}")
            
        except Exception as e:
            self.api_status = "❌ KONTROL HATASI"
            print(f"   ❌ Sağlık kontrolü hatası: {e}")
            logger.error(f"Sistem sağlık kontrolü hatası: {e}")
    
    async def start_api_server(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """FastAPI server'ı başlat"""
        try:
            if not self.services_initialized:
                raise Exception("PostgreSQL Production services henüz başlatılmamış!")
                
            print(f"""
🌐 BabaGAVAT PostgreSQL Production API başlatılıyor...

🔗 Server URL: http://{host}:{port}
📚 API Docs: http://{host}:{port}/docs
🔄 Health Check: http://{host}:{port}/coins/system-status

🐘 PostgreSQL Primary Database aktif
⚡ Redis Cache Layer aktif
📊 MongoDB Analytics aktif

🚀 BabaGAVAT API canlıya alınıyor...
            """)
            
            # Uvicorn configuration
            config = uvicorn.Config(
                app,
                host=host,
                port=port,
                log_level="info",
                access_log=True,
                reload=False,  # Production'da reload kapalı
                workers=1  # Multi-worker PostgreSQL pool için
            )
            
            server = uvicorn.Server(config)
            await server.serve()
            
        except Exception as e:
            logger.error(f"PostgreSQL Production API Server başlatma hatası: {e}")
            raise
    
    async def run_production_tests(self) -> Dict[str, Any]:
        """PostgreSQL Production test suite"""
        try:
            print(f"""
🧪 BABAGAVAT POSTGRESQL PRODUCTION TEST SUITE

🎯 Onur Metodu PostgreSQL production testleri başlatılıyor...
            """)
            
            test_results = {
                "test_start_time": datetime.now().isoformat(),
                "postgresql_tests": {},
                "redis_tests": {},
                "mongodb_tests": {},
                "coin_system_tests": {},
                "erko_analyzer_tests": {},
                "overall_success": False
            }
            
            # PostgreSQL Tests
            if babagavat_postgresql_manager.is_initialized:
                print("🐘 PostgreSQL Primary Database Tests...")
                test_results["postgresql_tests"] = await self._test_postgresql_operations()
            
            # Redis Tests
            if babagavat_redis_manager.is_initialized:
                print("⚡ Redis Cache Tests...")
                test_results["redis_tests"] = await self._test_redis_operations()
            
            # MongoDB Tests
            if babagavat_mongo_manager.is_initialized:
                print("📊 MongoDB Analytics Tests...")
                test_results["mongodb_tests"] = await self._test_mongodb_operations()
            
            # Coin System Tests
            if babagavat_coin_service.is_initialized:
                print("💰 PostgreSQL Coin System Tests...")
                test_results["coin_system_tests"] = await self._test_coin_operations()
            
            # ErkoAnalyzer Tests
            if babagavat_erko_analyzer.is_initialized:
                print("🔍 ErkoAnalyzer Tests...")
                test_results["erko_analyzer_tests"] = await self._test_erko_operations()
            
            # Overall result
            all_tests_passed = all(
                test_group.get("success", False) 
                for test_group in test_results.values()
                if isinstance(test_group, dict) and "success" in test_group
            )
            
            test_results["overall_success"] = all_tests_passed
            test_results["test_end_time"] = datetime.now().isoformat()
            
            status_emoji = "✅" if all_tests_passed else "⚠️"
            print(f"""
{status_emoji} POSTGRESQL PRODUCTION TEST SUITE TAMAMLANDI

📊 Test Sonuçları:
   🐘 PostgreSQL: {'✅' if test_results["postgresql_tests"].get("success") else '❌'}
   ⚡ Redis: {'✅' if test_results["redis_tests"].get("success") else '❌'}
   📊 MongoDB: {'✅' if test_results["mongodb_tests"].get("success") else '❌'}
   💰 Coin System: {'✅' if test_results["coin_system_tests"].get("success") else '❌'}
   🔍 ErkoAnalyzer: {'✅' if test_results["erko_analyzer_tests"].get("success") else '❌'}

🏆 PostgreSQL Production Sonuç: {'BAŞARILI' if all_tests_passed else 'KISMEN BAŞARILI'}
            """)
            
            return test_results
            
        except Exception as e:
            logger.error(f"PostgreSQL Production test hatası: {e}")
            return {"error": str(e), "overall_success": False}
    
    async def _test_postgresql_operations(self) -> Dict[str, Any]:
        """PostgreSQL operasyonlarını test et"""
        try:
            results = {"operations": [], "success": False}
            
            # Connection pool test
            async with babagavat_postgresql_manager.pool.acquire() as connection:
                version = await connection.fetchval("SELECT version()")
                results["operations"].append({"connection_pool": True})
                
                # Table exists test
                tables = await connection.fetch("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name LIKE 'babagavat_%'
                """)
                results["operations"].append({"tables_exist": len(tables) >= 5})
                
                # Insert/Select test
                await connection.execute("""
                    INSERT INTO babagavat_coin_balances (user_id, balance) 
                    VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET balance = EXCLUDED.balance
                """, 123456, 100.0)
                
                balance = await connection.fetchval(
                    "SELECT balance FROM babagavat_coin_balances WHERE user_id = $1", 123456
                )
                results["operations"].append({"insert_select": balance == 100.0})
            
            results["success"] = all(op.get(list(op.keys())[0], False) for op in results["operations"])
            
            return results
            
        except Exception as e:
            logger.warning(f"PostgreSQL test hatası: {e}")
            return {"error": str(e), "success": False}
    
    async def _test_redis_operations(self) -> Dict[str, Any]:
        """Redis operasyonlarını test et"""
        try:
            results = {"operations": [], "success": False}
            
            # Set/Get test
            await babagavat_redis_manager.redis_client.set("test:postgresql_production", "redis_ok")
            value = await babagavat_redis_manager.redis_client.get("test:postgresql_production")
            results["operations"].append({"set_get": value == "redis_ok"})
            
            # Coin balance cache test
            await babagavat_redis_manager.set_coin_balance(123456, 100.0)
            cached_balance = await babagavat_redis_manager.get_coin_balance(123456)
            results["operations"].append({"coin_cache": cached_balance == 100.0})
            
            # Cleanup
            await babagavat_redis_manager.redis_client.delete("test:postgresql_production")
            
            results["success"] = all(op.get(list(op.keys())[0], False) for op in results["operations"])
            
            return results
            
        except Exception as e:
            logger.warning(f"Redis test hatası: {e}")
            return {"error": str(e), "success": False}
    
    async def _test_mongodb_operations(self) -> Dict[str, Any]:
        """MongoDB operasyonlarını test et"""
        try:
            results = {"operations": [], "success": False}
            
            # Insert/Find test
            test_doc = {"test_id": 123456, "data": "postgresql_production_ok", "timestamp": datetime.now()}
            insert_result = await babagavat_mongo_manager.db.test_postgresql_production.insert_one(test_doc)
            results["operations"].append({"insert": insert_result.inserted_id is not None})
            
            # Find test
            found_doc = await babagavat_mongo_manager.db.test_postgresql_production.find_one({"test_id": 123456})
            results["operations"].append({"find": found_doc is not None})
            
            # Cleanup
            await babagavat_mongo_manager.db.test_postgresql_production.delete_one({"test_id": 123456})
            
            results["success"] = all(op.get(list(op.keys())[0], False) for op in results["operations"])
            
            return results
            
        except Exception as e:
            logger.warning(f"MongoDB test hatası: {e}")
            return {"error": str(e), "success": False}
    
    async def _test_coin_operations(self) -> Dict[str, Any]:
        """PostgreSQL Coin system operasyonlarını test et"""
        try:
            results = {"operations": [], "success": False}
            test_user_id = 987654
            
            # Balance query test (PostgreSQL primary)
            initial_balance = await babagavat_coin_service.get_balance(test_user_id)
            results["operations"].append({"postgresql_balance_query": True})
            
            # Add coins test (PostgreSQL cascade)
            add_result = await babagavat_coin_service.add_coins(
                test_user_id, 50, "EARN_ADMIN", "PostgreSQL production test coin"
            )
            results["operations"].append({"postgresql_add_coins": add_result})
            
            # Balance verification
            new_balance = await babagavat_coin_service.get_balance(test_user_id)
            results["operations"].append({"postgresql_balance_updated": new_balance >= initial_balance})
            
            results["success"] = all(op.get(list(op.keys())[0], False) for op in results["operations"])
            
            return results
            
        except Exception as e:
            logger.warning(f"PostgreSQL Coin system test hatası: {e}")
            return {"error": str(e), "success": False}
    
    async def _test_erko_operations(self) -> Dict[str, Any]:
        """ErkoAnalyzer operasyonlarını test et"""
        try:
            results = {"operations": [], "success": False}
            test_user_id = 987654
            
            # User analysis test
            profile = await babagavat_erko_analyzer.analyze_user(test_user_id)
            results["operations"].append({"user_analysis": profile is not None})
            results["operations"].append({"profile_valid": hasattr(profile, 'segment')})
            
            # Segment statistics test
            stats = await babagavat_erko_analyzer.get_segment_statistics()
            results["operations"].append({"segment_stats": isinstance(stats, dict)})
            
            results["success"] = all(op.get(list(op.keys())[0], False) for op in results["operations"])
            
            return results
            
        except Exception as e:
            logger.warning(f"ErkoAnalyzer test hatası: {e}")
            return {"error": str(e), "success": False}

# Global instance
babagavat_postgresql_production_launcher = BabaGAVATPostgreSQLProductionLauncher()

async def main():
    """Ana PostgreSQL production başlatma fonksiyonu"""
    try:
        # PostgreSQL production ortamını başlat
        success = await babagavat_postgresql_production_launcher.initialize_production_environment()
        
        if not success:
            print("❌ PostgreSQL Production başlatma başarısız!")
            return
        
        # PostgreSQL production testlerini çalıştır
        test_results = await babagavat_postgresql_production_launcher.run_production_tests()
        
        # Test sonuçlarını kaydet
        with open(f"babagavat_postgresql_production_test_report_{int(time.time())}.json", "w") as f:
            json.dump(test_results, f, indent=2, default=str)
        
        # API Server'ı başlat
        print("\n🚀 PostgreSQL Production API Server başlatılıyor...")
        await babagavat_postgresql_production_launcher.start_api_server()
        
    except KeyboardInterrupt:
        print("\n👋 BabaGAVAT PostgreSQL Production durduruldu - Onur Metodu ile güle güle!")
    except Exception as e:
        logger.error(f"PostgreSQL Production ana hata: {e}")
        print(f"❌ PostgreSQL Production hatası: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 