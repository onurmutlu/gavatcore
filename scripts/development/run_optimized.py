from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
# run_optimized.py - Optimize Edilmiş Gavatcore Çalıştırma Scripti

import asyncio
import os
import sys
import signal
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Core imports
from core.integrated_optimizer import (
    integrated_optimizer, start_integrated_optimization, stop_integrated_optimization,
    get_integrated_stats, force_system_optimization,
    BAMGUM_CONFIG, PRODUCTION_CONFIG, DEVELOPMENT_CONFIG, OptimizationConfig
)

# Bot imports
from handlers.dm_handler import setup_dm_handlers
from handlers.group_handler import setup_group_handlers
from handlers.spam_handler import setup_spam_handlers
from core.account_monitor import account_monitor
from utilities.anti_spam_guard import anti_spam_guard
from core.session_manager import get_active_sessions

# Performance monitoring
import structlog
logger = structlog.get_logger("gavatcore.main")

class OptimizedGavatcore:
    """Optimize edilmiş Gavatcore sistemi"""
    
    def __init__(self):
        self.clients = {}
        self.optimization_config = None
        self.is_running = False
        self.startup_time = None
        self.shutdown_handlers = []
        
        # Performance metrics
        self.performance_metrics = {
            "startup_time": 0,
            "total_messages": 0,
            "total_spam_sent": 0,
            "total_dm_replies": 0,
            "total_group_replies": 0,
            "optimization_runs": 0,
            "cache_hits": 0,
            "db_queries": 0
        }
    
    async def initialize(self, config_name: str = "bamgum") -> None:
        """Sistemi başlat"""
        startup_start = time.time()
        
        try:
            logger.info("🚀 Optimize edilmiş Gavatcore başlatılıyor...")
            
            # Optimization config seç
            self.optimization_config = self._get_optimization_config(config_name)
            
            # Entegre optimizasyon sistemini başlat
            logger.info("🔧 Optimizasyon sistemi başlatılıyor...")
            await start_integrated_optimization(self.optimization_config)
            
            # Session'ları al
            logger.info("📱 Session'lar yükleniyor...")
            sessions = await get_active_sessions()
            
            if not sessions:
                logger.error("❌ Aktif session bulunamadı!")
                return False
            
            # Bot client'larını başlat
            logger.info(f"🤖 {len(sessions)} bot başlatılıyor...")
            await self._initialize_bots(sessions)
            
            # Handler'ları setup et
            logger.info("⚙️ Handler'lar kurulumu...")
            await self._setup_handlers()
            
            # Monitoring sistemlerini başlat
            logger.info("📊 Monitoring sistemleri başlatılıyor...")
            await self._start_monitoring_systems()
            
            # Shutdown handler'ları kaydet
            self._register_shutdown_handlers()
            
            # Startup metrics
            self.startup_time = time.time() - startup_start
            self.performance_metrics["startup_time"] = self.startup_time
            
            self.is_running = True
            
            logger.info(f"✅ Gavatcore başarıyla başlatıldı! ({self.startup_time:.2f}s)")
            logger.info(f"🎯 Optimizasyon modu: {config_name.upper()}")
            logger.info(f"🤖 Aktif bot sayısı: {len(self.clients)}")
            
            # Başlangıç optimizasyonu çalıştır
            await self._run_initial_optimization()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Başlatma hatası: {e}")
            await self.shutdown()
            return False
    
    def _get_optimization_config(self, config_name: str) -> OptimizationConfig:
        """Optimizasyon config'ini al"""
        configs = {
            "bamgum": BAMGUM_CONFIG,
            "production": PRODUCTION_CONFIG,
            "development": DEVELOPMENT_CONFIG
        }
        
        return configs.get(config_name.lower(), BAMGUM_CONFIG)
    
    async def _initialize_bots(self, sessions: Dict[str, Any]) -> None:
        """Bot'ları başlat"""
        from telethon import TelegramClient
        
        for username, session_data in sessions.items():
            try:
                # Client oluştur
                client = TelegramClient(
                    session_data["session_file"],
                    session_data["api_id"],
                    session_data["api_hash"]
                )
                
                # Connect
                await client.connect()
                
                if await client.is_user_authorized():
                    self.clients[username] = {
                        "client": client,
                        "session_data": session_data,
                        "stats": {
                            "messages_sent": 0,
                            "messages_received": 0,
                            "spam_sent": 0,
                            "dm_replies": 0,
                            "group_replies": 0,
                            "errors": 0
                        }
                    }
                    logger.info(f"✅ Bot başlatıldı: {username}")
                else:
                    logger.warning(f"⚠️ Bot yetkilendirilmemiş: {username}")
                    await client.disconnect()
                    
            except Exception as e:
                logger.error(f"❌ Bot başlatma hatası ({username}): {e}")
    
    async def _setup_handlers(self) -> None:
        """Handler'ları setup et"""
        for username, bot_data in self.clients.items():
            client = bot_data["client"]
            
            try:
                # DM handlers
                await setup_dm_handlers(client, username)
                
                # Group handlers
                await setup_group_handlers(client, username)
                
                # Spam handlers
                await setup_spam_handlers(client, username)
                
                logger.info(f"✅ Handler'lar kuruldu: {username}")
                
            except Exception as e:
                logger.error(f"❌ Handler kurulum hatası ({username}): {e}")
    
    async def _start_monitoring_systems(self) -> None:
        """Monitoring sistemlerini başlat"""
        try:
            # Account monitoring - zaten singleton instance
            logger.info("✅ Account monitor hazır")
            
            # Anti-spam guard - zaten singleton instance
            logger.info("✅ Anti-spam guard hazır")
            
            logger.info("✅ Monitoring sistemleri başlatıldı")
            
        except Exception as e:
            logger.error(f"❌ Monitoring başlatma hatası: {e}")
    
    def _register_shutdown_handlers(self) -> None:
        """Shutdown handler'ları kaydet"""
        def signal_handler(signum, frame):
            logger.info(f"🛑 Signal alındı: {signum}")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def _run_initial_optimization(self) -> None:
        """Başlangıç optimizasyonu"""
        try:
            logger.info("🔧 Başlangıç optimizasyonu çalıştırılıyor...")
            
            result = await force_system_optimization()
            
            if result.get("success"):
                logger.info(f"✅ Başlangıç optimizasyonu tamamlandı ({result['duration']:.2f}s)")
                self.performance_metrics["optimization_runs"] += 1
            else:
                logger.warning(f"⚠️ Başlangıç optimizasyonu hatası: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Başlangıç optimizasyonu hatası: {e}")
    
    async def run(self) -> None:
        """Ana çalışma döngüsü"""
        if not self.is_running:
            logger.error("❌ Sistem başlatılmamış!")
            return
        
        logger.info("🏃 Ana çalışma döngüsü başlatıldı")
        
        try:
            # Performance monitoring loop
            monitoring_task = asyncio.create_task(self._performance_monitoring_loop())
            
            # Status reporting loop
            status_task = asyncio.create_task(self._status_reporting_loop())
            
            # Health check loop
            health_task = asyncio.create_task(self._health_check_loop())
            
            # Ana loop - bot'ları çalışır durumda tut
            while self.is_running:
                await asyncio.sleep(1)
                
                # Bot'ların durumunu kontrol et
                await self._check_bot_health()
            
            # Tasks'ları temizle
            monitoring_task.cancel()
            status_task.cancel()
            health_task.cancel()
            
            await asyncio.gather(
                monitoring_task, status_task, health_task, 
                return_exceptions=True
            )
            
        except Exception as e:
            logger.error(f"❌ Ana döngü hatası: {e}")
        finally:
            await self.shutdown()
    
    async def _performance_monitoring_loop(self) -> None:
        """Performance monitoring loop"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # 5 dakika interval
                
                # Performance stats al
                stats = await get_integrated_stats()
                
                # Metrics güncelle
                await self._update_performance_metrics(stats)
                
                # Critical threshold kontrolü
                await self._check_critical_thresholds(stats)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _status_reporting_loop(self) -> None:
        """Status reporting loop"""
        while self.is_running:
            try:
                await asyncio.sleep(1800)  # 30 dakika interval
                
                # Status raporu oluştur
                await self._generate_status_report()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Status reporting error: {e}")
                await asyncio.sleep(300)
    
    async def _health_check_loop(self) -> None:
        """Health check loop"""
        while self.is_running:
            try:
                await asyncio.sleep(600)  # 10 dakika interval
                
                # Sistem health check
                health_status = await self._perform_health_check()
                
                if not health_status["healthy"]:
                    logger.warning(f"⚠️ Health check uyarısı: {health_status['issues']}")
                    
                    # Auto-recovery dene
                    await self._attempt_auto_recovery(health_status)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(120)
    
    async def _check_bot_health(self) -> None:
        """Bot'ların sağlığını kontrol et"""
        for username, bot_data in self.clients.items():
            try:
                client = bot_data["client"]
                
                if not client.is_connected():
                    logger.warning(f"⚠️ Bot bağlantısı kopmuş: {username}")
                    
                    # Yeniden bağlan
                    await client.connect()
                    
                    if await client.is_user_authorized():
                        logger.info(f"✅ Bot yeniden bağlandı: {username}")
                    else:
                        logger.error(f"❌ Bot yetkilendirme hatası: {username}")
                        bot_data["stats"]["errors"] += 1
                
            except Exception as e:
                logger.error(f"Bot health check error ({username}): {e}")
                bot_data["stats"]["errors"] += 1
    
    async def _update_performance_metrics(self, stats: Dict[str, Any]) -> None:
        """Performance metrics güncelle"""
        try:
            # Cache stats
            cache_stats = stats.get("system_state", {}).get("cache", {})
            total_cache_hits = 0
            
            for cache_name, cache_data in cache_stats.items():
                if isinstance(cache_data, dict) and "performance" in cache_data:
                    total_cache_hits += cache_data["performance"].get("hits", 0)
            
            self.performance_metrics["cache_hits"] = total_cache_hits
            
            # Database stats
            db_stats = stats.get("system_state", {}).get("database", {})
            total_db_queries = 0
            
            for pool_name, pool_data in db_stats.items():
                if isinstance(pool_data, dict) and "performance" in pool_data:
                    total_db_queries += pool_data["performance"].get("total_queries", 0)
            
            self.performance_metrics["db_queries"] = total_db_queries
            
            # Bot stats
            for bot_data in self.clients.values():
                bot_stats = bot_data["stats"]
                self.performance_metrics["total_messages"] += bot_stats.get("messages_sent", 0)
                self.performance_metrics["total_spam_sent"] += bot_stats.get("spam_sent", 0)
                self.performance_metrics["total_dm_replies"] += bot_stats.get("dm_replies", 0)
                self.performance_metrics["total_group_replies"] += bot_stats.get("group_replies", 0)
            
        except Exception as e:
            logger.error(f"Performance metrics update error: {e}")
    
    async def _check_critical_thresholds(self, stats: Dict[str, Any]) -> None:
        """Critical threshold kontrolü"""
        try:
            integrated_stats = stats.get("integrated_optimizer", {})
            
            # Memory threshold
            avg_memory = integrated_stats.get("avg_memory_mb", 0)
            if avg_memory > self.optimization_config.memory_threshold_mb * 1.5:
                logger.critical(f"🔥 CRITICAL: Memory usage çok yüksek: {avg_memory:.1f}MB")
                await force_system_optimization()
            
            # CPU threshold
            avg_cpu = integrated_stats.get("avg_cpu_percent", 0)
            if avg_cpu > self.optimization_config.cpu_threshold_percent * 1.2:
                logger.critical(f"⚡ CRITICAL: CPU usage çok yüksek: {avg_cpu:.1f}%")
                await asyncio.sleep(10)  # Throttle
            
            # Error rate threshold
            total_errors = sum(bot_data["stats"]["errors"] for bot_data in self.clients.values())
            if total_errors > 50:
                logger.critical(f"❌ CRITICAL: Çok fazla hata: {total_errors}")
                await self._attempt_auto_recovery({"issues": ["high_error_rate"]})
            
        except Exception as e:
            logger.error(f"Critical threshold check error: {e}")
    
    async def _generate_status_report(self) -> None:
        """Status raporu oluştur"""
        try:
            uptime = time.time() - (self.startup_time or time.time())
            
            # Comprehensive stats al
            stats = await get_integrated_stats()
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "uptime_hours": uptime / 3600,
                "active_bots": len(self.clients),
                "performance_metrics": self.performance_metrics,
                "system_stats": stats.get("integrated_optimizer", {}),
                "bot_stats": {
                    username: bot_data["stats"] 
                    for username, bot_data in self.clients.items()
                }
            }
            
            # Log raporu
            logger.info(f"📊 STATUS REPORT:")
            logger.info(f"   Uptime: {uptime/3600:.1f} hours")
            logger.info(f"   Active bots: {len(self.clients)}")
            logger.info(f"   Total messages: {self.performance_metrics['total_messages']}")
            logger.info(f"   Total spam sent: {self.performance_metrics['total_spam_sent']}")
            logger.info(f"   Cache hits: {self.performance_metrics['cache_hits']}")
            logger.info(f"   DB queries: {self.performance_metrics['db_queries']}")
            
            # Raporu dosyaya kaydet
            report_file = f"logs/status_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs("logs", exist_ok=True)
            
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Status report generation error: {e}")
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """Sistem health check"""
        issues = []
        
        try:
            # Bot health
            disconnected_bots = []
            for username, bot_data in self.clients.items():
                if not bot_data["client"].is_connected():
                    disconnected_bots.append(username)
            
            if disconnected_bots:
                issues.append(f"Disconnected bots: {disconnected_bots}")
            
            # System resources
            import psutil
            memory_percent = psutil.virtual_memory().percent
            cpu_percent = psutil.cpu_percent()
            
            if memory_percent > 85:
                issues.append(f"High memory usage: {memory_percent:.1f}%")
            
            if cpu_percent > 90:
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            # Database health
            from core.db_pool_manager import health_check_pools
            db_health = await health_check_pools()
            
            unhealthy_dbs = [name for name, healthy in db_health.items() if not healthy]
            if unhealthy_dbs:
                issues.append(f"Unhealthy databases: {unhealthy_dbs}")
            
            return {
                "healthy": len(issues) == 0,
                "issues": issues,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "issues": [f"Health check error: {e}"],
                "timestamp": time.time()
            }
    
    async def _attempt_auto_recovery(self, health_status: Dict[str, Any]) -> None:
        """Auto-recovery dene"""
        try:
            logger.info("🔧 Auto-recovery başlatılıyor...")
            
            issues = health_status.get("issues", [])
            
            for issue in issues:
                if "Disconnected bots" in issue:
                    # Bot'ları yeniden bağla
                    await self._reconnect_bots()
                
                elif "High memory usage" in issue:
                    # Memory optimization
                    await force_system_optimization()
                
                elif "High CPU usage" in issue:
                    # CPU throttling
                    await asyncio.sleep(30)
                
                elif "Unhealthy databases" in issue:
                    # Database reconnection
                    from core.db_pool_manager import pool_manager
                    await pool_manager.health_check_all()
                
                elif "high_error_rate" in issue:
                    # Error rate reduction
                    await self._reduce_activity_temporarily()
            
            logger.info("✅ Auto-recovery tamamlandı")
            
        except Exception as e:
            logger.error(f"Auto-recovery error: {e}")
    
    async def _reconnect_bots(self) -> None:
        """Bot'ları yeniden bağla"""
        for username, bot_data in self.clients.items():
            try:
                client = bot_data["client"]
                
                if not client.is_connected():
                    await client.connect()
                    logger.info(f"✅ Bot yeniden bağlandı: {username}")
                    
            except Exception as e:
                logger.error(f"Bot reconnection error ({username}): {e}")
    
    async def _reduce_activity_temporarily(self) -> None:
        """Geçici olarak aktiviteyi azalt"""
        logger.info("⏸️ Aktivite geçici olarak azaltılıyor...")
        
        # Spam handler'ları geçici olarak durdur
        # Bu implementation spam handler'lara bağlı
        
        await asyncio.sleep(300)  # 5 dakika bekle
        
        logger.info("▶️ Normal aktivite devam ediyor")
    
    async def shutdown(self) -> None:
        """Sistemi kapat"""
        if not self.is_running:
            return
        
        logger.info("🛑 Gavatcore kapatılıyor...")
        
        self.is_running = False
        
        try:
            # Bot'ları kapat
            for username, bot_data in self.clients.items():
                try:
                    await bot_data["client"].disconnect()
                    logger.info(f"✅ Bot kapatıldı: {username}")
                except Exception as e:
                    logger.error(f"Bot kapatma hatası ({username}): {e}")
            
            # Optimizasyon sistemini kapat
            await stop_integrated_optimization()
            
            # Final status raporu
            await self._generate_final_report()
            
            logger.info("✅ Gavatcore başarıyla kapatıldı")
            
        except Exception as e:
            logger.error(f"Kapatma hatası: {e}")
    
    async def _generate_final_report(self) -> None:
        """Final rapor oluştur"""
        try:
            uptime = time.time() - (self.startup_time or time.time())
            
            final_report = {
                "shutdown_timestamp": datetime.now().isoformat(),
                "total_uptime_hours": uptime / 3600,
                "final_metrics": self.performance_metrics,
                "bot_final_stats": {
                    username: bot_data["stats"] 
                    for username, bot_data in self.clients.items()
                }
            }
            
            # Final raporu kaydet
            report_file = f"logs/final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs("logs", exist_ok=True)
            
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(final_report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📊 Final rapor kaydedildi: {report_file}")
            
        except Exception as e:
            logger.error(f"Final report error: {e}")

async def main():
    """Ana başlatma fonksiyonu"""
    logger.info("=" * 80)
    logger.info("GAVATCORE OPTIMIZE SISTEM BAŞLATILIYOR")
    logger.info("=" * 80)
    
    # Test modu için özel ayarlar
    test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
    config_name = os.getenv("OPTIMIZATION_CONFIG", "bamgum")
    
    if test_mode:
        logger.info("🧪 TEST MODU AKTİF")
        config_name = "development"  # Test için development config kullan
    
    # Gavatcore instance oluştur
    gavatcore = OptimizedGavatcore()
    
    # Sistemi başlat
    success = await gavatcore.initialize(config_name)
    
    if not success:
        logger.error("❌ Sistem başlatılamadı!")
        return 1
    
    # Ana döngüyü çalıştır
    try:
        await gavatcore.run()
    except KeyboardInterrupt:
        logger.info("⚠️ Klavyeden durdurma sinyali alındı")
    except Exception as e:
        logger.error(f"❌ Ana döngü hatası: {e}")
    finally:
        await gavatcore.shutdown()
    
    return 0

if __name__ == "__main__":
    # Python version kontrolü
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 veya üzeri gerekli!")
        sys.exit(1)
    
    # Event loop oluştur ve çalıştır
    try:
        # Test modu için log seviyesini ayarla
        if os.getenv("TEST_MODE", "false").lower() == "true":

        else:

        # Asyncio debug mode
        if os.getenv("ASYNCIO_DEBUG", "false").lower() == "true":
            asyncio.set_debug(True)
        
        # Ana event loop
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1) 