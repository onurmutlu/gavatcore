from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
BabaGAVAT Launcher - Sokak Zekası ile Güçlendirilmiş AI Kullanıcı Analiz Sistemi
Telegram gruplarında güvenilir şovcu tespiti ve dolandırıcı filtreleme sistemi
BabaGAVAT'ın sokak tecrübesi ile güçlendirilmiş ana kontrol merkezi
"""

import asyncio
import json
import time
import signal
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import structlog
from telethon import TelegramClient
from telethon.sessions import StringSession

# Core imports - BabaGAVAT'ın modülleri
from core.user_analyzer import babagavat_user_analyzer
from core.database_manager import database_manager
from core.telegram_broadcaster import TelegramBroadcaster
from config import Config

# Logging setup - BabaGAVAT teması
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("babagavat.launcher")

class BabaGAVATLauncher:
    """BabaGAVAT Ana Launcher - Sokak Zekası Kontrol Merkezi"""
    
    def __init__(self):
        self.clients: Dict[str, TelegramClient] = {}
        self.broadcaster: Optional[TelegramBroadcaster] = None
        self.is_running = False
        self.startup_time = None
        
        # BabaGAVAT'ın bot konfigürasyonları
        self.bot_configs = {
            "babagavat": {  # Ana BabaGAVAT hesabı
                "api_id": Config.TELEGRAM_API_ID,
                "api_hash": Config.TELEGRAM_API_HASH,
                "session_string": Config.BABAGAVAT_SESSION,
                "phone": Config.BABAGAVAT_PHONE,
                "role": "main_analyzer"  # Ana analiz botu
            },
            "xxxgeisha": {  # Destek hesabı
                "api_id": Config.TELEGRAM_API_ID,
                "api_hash": Config.TELEGRAM_API_HASH,
                "session_string": Config.XXXGEISHA_SESSION,
                "phone": Config.XXXGEISHA_PHONE,
                "role": "support_monitor"  # Destek monitör
            },
            "yayincilara": {  # Broadcast hesabı
                "api_id": Config.TELEGRAM_API_ID,
                "api_hash": Config.TELEGRAM_API_HASH,
                "session_string": Config.YAYINCILARA_SESSION,
                "phone": Config.YAYINCILARA_PHONE,
                "role": "broadcaster"  # Broadcast botu
            }
        }
        
        logger.info("💪 BabaGAVAT Launcher başlatıldı - Sokak zekası aktif!")
    
    async def initialize(self) -> None:
        """BabaGAVAT sistemini başlat"""
        try:
            self.startup_time = datetime.now()
            logger.info("🚀 BabaGAVAT sistemi başlatılıyor - Sokak kontrolü başlıyor...")
            
            # 1. Database'i başlat
            await self._initialize_database()
            
            # 2. Telegram client'larını başlat
            await self._initialize_telegram_clients()
            
            # 3. Broadcaster'ı başlat
            await self._initialize_broadcaster()
            
            # 4. BabaGAVAT User Analyzer'ı başlat
            await self._initialize_babagavat_analyzer()
            
            # 5. Background tasks başlat
            await self._start_background_tasks()
            
            # 6. Signal handler'ları kaydet
            self._register_signal_handlers()
            
            self.is_running = True
            startup_duration = (datetime.now() - self.startup_time).total_seconds()
            
            logger.info(f"""
💪 BabaGAVAT Sistemi Hazır - Sokak Zekası Aktif! 
⏱️ Başlatma süresi: {startup_duration:.2f} saniye
🤖 Aktif botlar: {len(self.clients)}
🕵️ Monitoring: BAŞLADI
🔍 Analiz: AKTİF
🎯 Sokak Kontrolü: DEVREDE
            """)
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT başlatma hatası: {e}")
            raise
    
    async def _initialize_database(self) -> None:
        """Database'i başlat"""
        try:
            await database_manager.initialize()
            logger.info("✅ BabaGAVAT Database hazır - Sokak dosyaları açıldı! 📋")
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Database başlatma hatası: {e}")
            raise
    
    async def _initialize_telegram_clients(self) -> None:
        """Telegram client'larını başlat"""
        try:
            for bot_name, config in self.bot_configs.items():
                try:
                    # Session string varsa kullan, yoksa telefon ile giriş yap
                    if config.get("session_string"):
                        session = StringSession(config["session_string"])
                    else:
                        session = f"sessions/{bot_name}"
                    
                    client = TelegramClient(
                        session,
                        config["api_id"],
                        config["api_hash"]
                    )
                    
                    await client.start(phone=config["phone"])
                    
                    # Client'ı test et
                    me = await client.get_me()
                    role = config.get("role", "unknown")
                    
                    if bot_name == "babagavat":
                        logger.info(f"💪 {bot_name} bağlandı: @{me.username} - BabaGAVAT Ana Kontrol!")
                    else:
                        logger.info(f"✅ {bot_name} bağlandı: @{me.username} - {role}")
                    
                    self.clients[bot_name] = client
                    
                except Exception as e:
                    logger.warning(f"⚠️ {bot_name} bağlantı hatası: {e}")
            
            if not self.clients:
                raise Exception("Hiçbir Telegram client başlatılamadı!")
            
            logger.info(f"✅ {len(self.clients)} BabaGAVAT client hazır - Sokak ağı kuruldu! 🕸️")
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Telegram client başlatma hatası: {e}")
            raise
    
    async def _initialize_broadcaster(self) -> None:
        """Broadcaster'ı başlat"""
        try:
            self.broadcaster = TelegramBroadcaster()
            await self.broadcaster.initialize(self.clients)
            logger.info("✅ BabaGAVAT Broadcaster hazır - Sokak mesajları aktif! 📢")
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Broadcaster başlatma hatası: {e}")
            raise
    
    async def _initialize_babagavat_analyzer(self) -> None:
        """BabaGAVAT User Analyzer'ı başlat"""
        try:
            await babagavat_user_analyzer.initialize(self.clients)
            logger.info("✅ BabaGAVAT User Analyzer hazır - Sokak zekası devrede! 🧠")
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Analyzer başlatma hatası: {e}")
            raise
    
    async def _start_background_tasks(self) -> None:
        """Background task'ları başlat"""
        try:
            # BabaGAVAT'ın özel görevleri
            asyncio.create_task(self._babagavat_status_reporter())
            asyncio.create_task(self._babagavat_performance_monitor())
            asyncio.create_task(self._babagavat_daily_report_generator())
            asyncio.create_task(self._babagavat_intelligence_coordinator())
            
            logger.info("✅ BabaGAVAT Background tasks başlatıldı - Sokak görevleri aktif! 🎯")
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Background tasks başlatma hatası: {e}")
    
    def _register_signal_handlers(self) -> None:
        """Signal handler'ları kaydet"""
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            logger.info("✅ BabaGAVAT Signal handlers kaydedildi")
        except Exception as e:
            logger.warning(f"⚠️ BabaGAVAT Signal handler kayıt hatası: {e}")
    
    def _signal_handler(self, signum, frame):
        """Signal handler"""
        logger.info(f"🛑 BabaGAVAT Signal alındı: {signum}")
        asyncio.create_task(self.shutdown())
    
    async def _babagavat_status_reporter(self) -> None:
        """BabaGAVAT sistem durumu raporu"""
        while self.is_running:
            try:
                await asyncio.sleep(1800)  # Her 30 dakika
                
                # BabaGAVAT'ın sistem durumu raporu
                status_report = await self._generate_babagavat_status_report()
                logger.info(f"📊 BabaGAVAT Sistem Durumu: {json.dumps(status_report, indent=2)}")
                
            except Exception as e:
                logger.error(f"❌ BabaGAVAT Status reporter hatası: {e}")
                await asyncio.sleep(300)
    
    async def _babagavat_performance_monitor(self) -> None:
        """BabaGAVAT performans monitörü"""
        while self.is_running:
            try:
                await asyncio.sleep(3600)  # Her saat
                
                # BabaGAVAT'ın performans metrikleri
                performance_data = await self._collect_babagavat_performance_metrics()
                logger.info(f"⚡ BabaGAVAT Performans: {json.dumps(performance_data, indent=2)}")
                
            except Exception as e:
                logger.error(f"❌ BabaGAVAT Performance monitor hatası: {e}")
                await asyncio.sleep(300)
    
    async def _babagavat_daily_report_generator(self) -> None:
        """BabaGAVAT günlük rapor oluşturucu"""
        while self.is_running:
            try:
                await asyncio.sleep(86400)  # Her 24 saat
                
                # BabaGAVAT'ın günlük raporu
                daily_report = await self._generate_babagavat_daily_report()
                
                # Raporu kaydet
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_file = f"babagavat_daily_report_{timestamp}.json"
                
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(daily_report, f, indent=2, ensure_ascii=False, default=str)
                
                logger.info(f"📋 BabaGAVAT Günlük rapor oluşturuldu: {report_file}")
                
            except Exception as e:
                logger.error(f"❌ BabaGAVAT Daily report generator hatası: {e}")
                await asyncio.sleep(3600)
    
    async def _babagavat_intelligence_coordinator(self) -> None:
        """BabaGAVAT istihbarat koordinatörü"""
        while self.is_running:
            try:
                await asyncio.sleep(2700)  # Her 45 dakika
                
                # BabaGAVAT'ın özel istihbarat analizi
                await self._run_babagavat_intelligence_analysis()
                
                logger.info("🕵️ BabaGAVAT istihbarat koordinasyonu tamamlandı")
                
            except Exception as e:
                logger.error(f"❌ BabaGAVAT Intelligence coordinator hatası: {e}")
                await asyncio.sleep(300)
    
    async def _generate_babagavat_status_report(self) -> Dict[str, Any]:
        """BabaGAVAT sistem durumu raporu oluştur"""
        try:
            uptime = (datetime.now() - self.startup_time).total_seconds()
            
            # BabaGAVAT'ın özel istatistikleri
            user_stats = await babagavat_user_analyzer.get_user_analysis_report()
            invite_stats = await babagavat_user_analyzer.get_invite_candidates_report()
            suspicious_stats = await babagavat_user_analyzer.get_suspicious_users_report()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "babagavat_uptime_seconds": uptime,
                "active_clients": len(self.clients),
                "monitored_groups": len(babagavat_user_analyzer.monitored_groups),
                "street_smart_analysis": {
                    "user_statistics": user_stats.get("statistics", []),
                    "invite_candidates": len(invite_stats.get("recent_candidates", [])),
                    "suspicious_users": suspicious_stats.get("total_count", 0)
                },
                "babagavat_status": "sokak_kontrolu_aktif" if self.is_running else "devre_disi",
                "street_intelligence_level": "yuksek"
            }
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Status report oluşturma hatası: {e}")
            return {"error": str(e)}
    
    async def _collect_babagavat_performance_metrics(self) -> Dict[str, Any]:
        """BabaGAVAT performans metrikleri topla"""
        try:
            import psutil
            
            # Sistem metrikleri
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # BabaGAVAT'ın özel metrikleri
            uptime = (datetime.now() - self.startup_time).total_seconds()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "babagavat_uptime_hours": uptime / 3600,
                "system_performance": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_used_gb": memory.used / (1024**3),
                    "disk_percent": disk.percent
                },
                "babagavat_metrics": {
                    "active_clients": len(self.clients),
                    "monitored_groups": len(babagavat_user_analyzer.monitored_groups),
                    "street_smart_level": "maksimum"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Performance metrics toplama hatası: {e}")
            return {"error": str(e)}
    
    async def _generate_babagavat_daily_report(self) -> Dict[str, Any]:
        """BabaGAVAT günlük rapor oluştur"""
        try:
            # BabaGAVAT'ın detaylı istatistikleri
            user_report = await babagavat_user_analyzer.get_user_analysis_report()
            invite_report = await babagavat_user_analyzer.get_invite_candidates_report()
            suspicious_report = await babagavat_user_analyzer.get_suspicious_users_report()
            
            return {
                "report_date": datetime.now().isoformat(),
                "report_type": "babagavat_daily_street_analysis",
                "babagavat_summary": {
                    "total_monitored_users": user_report.get("total_monitored_users", 0),
                    "monitored_groups": user_report.get("monitored_groups", 0),
                    "invite_candidates": len(invite_report.get("recent_candidates", [])),
                    "suspicious_users": suspicious_report.get("total_count", 0),
                    "street_smart_level": "yuksek"
                },
                "street_intelligence": {
                    "user_statistics": user_report.get("statistics", []),
                    "invite_candidates": invite_report,
                    "suspicious_users": suspicious_report
                },
                "babagavat_system_info": await self._collect_babagavat_performance_metrics()
            }
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Daily report oluşturma hatası: {e}")
            return {"error": str(e)}
    
    async def _run_babagavat_intelligence_analysis(self) -> None:
        """BabaGAVAT'ın özel istihbarat analizi"""
        try:
            # Yüksek potansiyelli kullanıcıları tespit et
            async with database_manager._get_connection() as db:
                cursor = await db.execute("""
                    SELECT COUNT(*) as total_users,
                           SUM(CASE WHEN trust_level = 'trusted' THEN 1 ELSE 0 END) as trusted_users,
                           SUM(CASE WHEN trust_level = 'suspicious' THEN 1 ELSE 0 END) as suspicious_users,
                           AVG(trust_score) as avg_trust_score
                    FROM babagavat_user_profiles
                """)
                stats = await cursor.fetchone()
                
                if stats:
                    total_users, trusted_users, suspicious_users, avg_trust_score = stats
                    
                    # BabaGAVAT'ın istihbarat değerlendirmesi
                    intelligence_level = "yuksek" if avg_trust_score > 0.6 else "orta" if avg_trust_score > 0.4 else "dusuk"
                    
                    logger.info(f"""
🕵️ BabaGAVAT İstihbarat Raporu:
👥 Toplam Kullanıcı: {total_users}
🟢 Güvenilir: {trusted_users}
🔴 Şüpheli: {suspicious_users}
📊 Ortalama Güven: {avg_trust_score:.2f}
🧠 İstihbarat Seviyesi: {intelligence_level}
                    """)
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Intelligence analysis hatası: {e}")
    
    # ==================== BABAGAVAT ADMIN COMMANDS ====================
    
    async def get_babagavat_system_status(self) -> Dict[str, Any]:
        """BabaGAVAT sistem durumu getir"""
        return await self._generate_babagavat_status_report()
    
    async def get_babagavat_user_analysis(self, user_id: str = None) -> Dict[str, Any]:
        """BabaGAVAT kullanıcı analizi getir"""
        return await babagavat_user_analyzer.get_user_analysis_report(user_id)
    
    async def get_babagavat_invite_candidates(self) -> Dict[str, Any]:
        """BabaGAVAT davet adayları getir"""
        return await babagavat_user_analyzer.get_invite_candidates_report()
    
    async def get_babagavat_suspicious_users(self) -> Dict[str, Any]:
        """BabaGAVAT şüpheli kullanıcılar getir"""
        return await babagavat_user_analyzer.get_suspicious_users_report()
    
    async def babagavat_manual_trust_override(self, user_id: str, trust_score: float, reason: str) -> bool:
        """BabaGAVAT manuel güven puanı değişikliği"""
        return await babagavat_user_analyzer.manual_trust_override(user_id, trust_score, f"BabaGAVAT Override: {reason}")
    
    async def babagavat_send_invite_to_candidate(self, candidate_id: int) -> bool:
        """BabaGAVAT davet adayına mesaj gönder"""
        try:
            # BabaGAVAT'ın özel davet sistemi
            logger.info(f"💪 BabaGAVAT davet gönderiyor: candidate_id={candidate_id}")
            
            # Burada gerçek davet gönderme işlemi yapılabilir
            # BabaGAVAT'ın kişiselleştirilmiş mesajları ile
            
            return True
        except Exception as e:
            logger.error(f"❌ BabaGAVAT davet gönderme hatası: {e}")
            return False
    
    async def babagavat_broadcast_street_message(self, message: str, target_type: str = "all") -> Dict[str, Any]:
        """BabaGAVAT sokak mesajı broadcast et"""
        try:
            if not self.broadcaster:
                return {"error": "Broadcaster hazır değil"}
            
            # BabaGAVAT'ın sokak teması ile mesaj
            babagavat_message = f"""
💪 BabaGAVAT'tan Sokak Mesajı:

{message}

🎯 Sokak zekası ile güçlendirilmiş sistem
🔥 #BabaGAVAT #SokakZekası #GavatCore
            """.strip()
            
            # Broadcast gönder
            result = await self.broadcaster.send_broadcast(
                message=babagavat_message,
                target_type=target_type,
                message_type="babagavat_street_message"
            )
            
            logger.info(f"📢 BabaGAVAT sokak mesajı gönderildi: {target_type}")
            return result
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT broadcast hatası: {e}")
            return {"error": str(e)}
    
    async def shutdown(self) -> None:
        """BabaGAVAT sistemini kapat"""
        try:
            logger.info("🛑 BabaGAVAT sistemi kapatılıyor - Sokak kontrolü sonlandırılıyor...")
            
            self.is_running = False
            
            # BabaGAVAT analyzer'ı durdur
            babagavat_user_analyzer.is_monitoring = False
            
            # Telegram client'larını kapat
            for bot_name, client in self.clients.items():
                try:
                    await client.disconnect()
                    if bot_name == "babagavat":
                        logger.info(f"💪 {bot_name} bağlantısı kapatıldı - BabaGAVAT offline!")
                    else:
                        logger.info(f"✅ {bot_name} bağlantısı kapatıldı")
                except Exception as e:
                    logger.warning(f"⚠️ {bot_name} kapatma hatası: {e}")
            
            logger.info("✅ BabaGAVAT sistemi kapatıldı - Sokak zekası devre dışı!")
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Shutdown hatası: {e}")
    
    async def run_forever(self) -> None:
        """BabaGAVAT sistemini sürekli çalıştır"""
        try:
            logger.info("🔄 BabaGAVAT sistemi çalışıyor - Sokak kontrolü devam ediyor...")
            
            while self.is_running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("⌨️ BabaGAVAT Keyboard interrupt alındı")
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Runtime hatası: {e}")
        finally:
            await self.shutdown()

async def main():
    """BabaGAVAT Ana fonksiyonu"""
    try:
        # BabaGAVAT Launcher'ı oluştur ve başlat
        launcher = BabaGAVATLauncher()
        await launcher.initialize()
        
        # BabaGAVAT sistemini çalıştır
        await launcher.run_forever()
        
    except KeyboardInterrupt:
        logger.info("⌨️ BabaGAVAT Program sonlandırıldı")
    except Exception as e:
        logger.error(f"❌ BabaGAVAT Ana program hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # BabaGAVAT Event loop'u çalıştır
    try:
        print("""
💪 BabaGAVAT - Sokak Zekası ile Güçlendirilmiş AI Kullanıcı Analiz Sistemi

🎯 Özellikler:
✅ Sokak zekası ile spam tespiti
✅ Güvenilir şovcu analizi  
✅ Dolandırıcı filtreleme
✅ Otomatik davet sistemi
✅ Real-time monitoring
✅ Intelligence coordination

🚀 Sistem başlatılıyor...
        """)
        
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 BabaGAVAT Program sonlandırıldı")
    except Exception as e:
        print(f"❌ BabaGAVAT Fatal error: {e}")
        sys.exit(1) 