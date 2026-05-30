from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🚀 GavatCore OnlyVips v6.0 Entry Point 🚀

Sistem bileşenlerini başlatır:
• Flask API Server (localhost:5050) 
• XP Token API (localhost:5051) - NEW!
• XP-enabled Production Bots
• GavatCoin Token Economy

Enhanced Features:
- Type annotations ve comprehensive error handling
- Structured logging ve monitoring
- Process management ve graceful shutdown
- Health checks ve status monitoring

Kullanım: python3 run.py
"""

import subprocess
import sys
import time
import signal
import logging
import os
import json
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import threading
import requests
from pathlib import Path
import structlog

# Configure structured logging
log_processors = [
    structlog.stdlib.filter_by_level,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.dev.ConsoleRenderer() if os.getenv("DEBUG_MODE", "false").lower() == "true" 
    else structlog.processors.JSONRenderer()
]

structlog.configure(
    processors=log_processors,
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("gavatcore.launcher")

@dataclass
class ProcessInfo:
    """Process information data structure."""
    name: str
    process: subprocess.Popen
    start_time: datetime = field(default_factory=datetime.now)
    pid: Optional[int] = None
    status: str = "starting"
    health_url: Optional[str] = None
    
    def __post_init__(self):
        """Set PID after initialization."""
        if self.process:
            self.pid = self.process.pid

@dataclass
class SystemStatus:
    """System status information."""
    total_components: int = 0
    successful_components: int = 0
    failed_components: int = 0
    processes: List[ProcessInfo] = field(default_factory=list)
    startup_time: datetime = field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        return (self.successful_components / max(self.total_components, 1)) * 100
    
    @property
    def is_healthy(self) -> bool:
        """Check if system is healthy."""
        return self.successful_components > 0

class GavatCoreSystemLauncher:
    """
    🚀 GavatCore sistem entry point
    
    Enhanced launcher with comprehensive process management,
    health monitoring, and graceful shutdown capabilities.
    """
    
    def __init__(self):
        self.processes: List[ProcessInfo] = []
        self.running: bool = True
        self.status = SystemStatus()
        self._shutdown_lock = threading.Lock()
        
        logger.info("🔧 GavatCore System Launcher initialized")
        
    def _check_service_health(self, url: str, timeout: int = 2) -> bool:
        """
        Check if a service is healthy by making HTTP request.
        
        Args:
            url: Health check URL
            timeout: Request timeout in seconds
            
        Returns:
            bool: True if service is healthy, False otherwise
        """
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code in [200, 201]
        except (requests.RequestException, requests.Timeout):
            return False
        except Exception as e:
            logger.warning("⚠️ Health check error", url=url, error=str(e))
            return False
    
    def start_flask_api(self) -> bool:
        """
        Flask API server'ı başlat.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            self.status.total_components += 1
            logger.info("🌐 Flask API Server başlatılıyor (localhost:5050)...")
            
            # Check if already running
            if self._check_service_health("http://localhost:5050/api/system/status"):
                logger.info("✅ Flask API zaten çalışıyor!")
                self.status.successful_components += 1
                return True
            
            # Start new process
            process = subprocess.Popen(
                [sys.executable, "apis/production_bot_api.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            process_info = ProcessInfo(
                name="Flask API",
                process=process,
                health_url="http://localhost:5050/api/system/status"
            )
            
            self.processes.append(process_info)
            self.status.processes.append(process_info)
            
            # Wait and verify startup
            time.sleep(3)
            
            if self._check_service_health(process_info.health_url):
                process_info.status = "running"
                self.status.successful_components += 1
                logger.info("✅ Flask API Server başlatıldı!",
                          pid=process_info.pid,
                          health_url=process_info.health_url)
                return True
            else:
                process_info.status = "failed"
                self.status.failed_components += 1
                logger.error("❌ Flask API başlatılamadı - health check başarısız")
                return False
            
        except Exception as e:
            self.status.failed_components += 1
            logger.error("❌ Flask API başlatma hatası", error=str(e), exc_info=True)
            return False
    
    def start_xp_token_api(self) -> bool:
        """
        XP Token API server'ı başlat.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            self.status.total_components += 1
            logger.info("🪙 XP Token API Server başlatılıyor (localhost:5051)...")
            
            # Check if already running
            if self._check_service_health("http://localhost:5051/health"):
                logger.info("✅ XP Token API zaten çalışıyor!")
                self.status.successful_components += 1
                return True
            
            # Check if script exists
            script_path = Path("apis/xp_token_api_sync.py")
            if not script_path.exists():
                logger.warning("⚠️ XP Token API script bulunamadı, atlanıyor",
                             script=str(script_path))
                self.status.failed_components += 1
                return False
            
            # Start new process
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            process_info = ProcessInfo(
                name="XP Token API",
                process=process,
                health_url="http://localhost:5051/health"
            )
            
            self.processes.append(process_info)
            self.status.processes.append(process_info)
            
            # Wait and verify startup
            time.sleep(4)
            
            if self._check_service_health(process_info.health_url):
                process_info.status = "running"
                self.status.successful_components += 1
                logger.info("✅ XP Token API Server başlatıldı!",
                          pid=process_info.pid,
                          health_url=process_info.health_url)
                return True
            else:
                process_info.status = "failed"
                self.status.failed_components += 1
                logger.error("❌ XP Token API başlatılamadı - health check başarısız")
                return False
            
        except Exception as e:
            self.status.failed_components += 1
            logger.error("❌ XP Token API başlatma hatası", error=str(e), exc_info=True)
            return False
    
    def start_production_bots(self) -> bool:
        """
        Auto-session production botları başlat.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            self.status.total_components += 1
            logger.info("🤖 Auto-Session Production Bots başlatılıyor...")
            
            # Yeni bot sistemi kullan
            bot_system_path = Path("services/telegram/bot_manager/bot_system.py")
            
            if bot_system_path.exists():
                logger.info("🚀 Yeni unified bot sistemi kullanılıyor...")
                
                # Master bot automation'ı başlat
                process = subprocess.Popen(
                    [sys.executable, "-m", "services.telegram.bot_manager.bot_system"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True
                )
                
                process_info = ProcessInfo(
                    name="Production Bots (Unified System)",
                    process=process
                )
                
                self.processes.append(process_info)
                self.status.processes.append(process_info)
                
                # Bot başlatma için daha uzun bekle
                logger.info("⏳ Bot sistemi başlatılıyor...")
                time.sleep(10)
                
                # Check if process is still running
                if process.poll() is None:
                    process_info.status = "running"
                    self.status.successful_components += 1
                    logger.info("✅ Production Bots başlatıldı!",
                              pid=process_info.pid,
                              script="services.telegram.bot_manager.bot_system")
                    return True
                else:
                    process_info.status = "failed"
                    self.status.failed_components += 1
                    logger.error("❌ Production Bots başlatılamadı - process terminated")
                    
                    # Hata mesajını göster
                    stdout, stderr = process.communicate(timeout=1)
                    if stderr:
                        logger.error("Bot sistem hatası", error=stderr.decode())
                    return False
                    
            else:
                # Eski sistem - fallback
                logger.warning("⚠️ Yeni bot sistemi bulunamadı, eski launcher kullanılıyor...")
                
                # Bot konfigürasyonları
                bot_configs = {
                    "lara": {
                        "persona_file": "data/personas/yayincilara.json",
                        "phone": "+905382617727",
                        "display_name": "Lara - Flörtöz Yayıncı"
                    },
                    "babagavat": {
                        "persona_file": "data/personas/babagavat.json", 
                        "phone": "+905513272355",
                        "display_name": "BabaGavat - Pavyon Lideri"
                    },
                    "geisha": {
                        "persona_file": "data/personas/xxxgeisha.json",
                        "phone": "+905486306226",
                        "display_name": "Geisha - Vamp Moderatör"
                    }
                }
                
                # Session dosyalarını kontrol et
                logger.info("🔍 Session dosyaları kontrol ediliyor...")
                valid_bots = 0
                
                for bot_name, config in bot_configs.items():
                    # Persona dosyasından telefon al
                    if Path(config["persona_file"]).exists():
                        try:
                            import json
                            with open(config["persona_file"], 'r', encoding='utf-8') as f:
                                persona = json.load(f)
                            phone = persona.get('phone', config['phone'])
                        except:
                            phone = config['phone']
                    else:
                        phone = config['phone']
                    
                    # Session dosyasını kontrol et
                    clean_phone = phone.replace('+', '')
                    session_path = f"sessions/_{clean_phone}.session"
                    
                    if Path(session_path).exists():
                        size_kb = Path(session_path).stat().st_size / 1024
                        if size_kb > 10:
                            logger.info(f"✅ {bot_name}: Session hazır ({size_kb:.1f}KB)")
                            valid_bots += 1
                        else:
                            logger.warning(f"⚠️ {bot_name}: Session küçük ({size_kb:.1f}KB)")
                    else:
                        logger.error(f"❌ {bot_name}: Session bulunamadı: {session_path}")
                
                if valid_bots == 0:
                    logger.error("❌ Hiç geçerli session bulunamadı!")
                    self.status.failed_components += 1
                    return False
                
                # Ultimate launcher kullan
                if Path("launchers/gavatcore_ultimate_launcher.py").exists():
                    script_path = "launchers/gavatcore_ultimate_launcher.py"
                    bot_name = "Ultimate Launcher"
                elif Path("launchers/lara_bot_launcher.py").exists():
                    script_path = "launchers/lara_bot_launcher.py"
                    bot_name = "Lara Bot"
                else:
                    logger.error("❌ Hiçbir launcher bulunamadı!")
                    self.status.failed_components += 1
                    return False
                
                # Start new process
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True
                )
                
                process_info = ProcessInfo(
                    name=f"Production Bots ({bot_name})",
                    process=process
                )
                
                self.processes.append(process_info)
                self.status.processes.append(process_info)
                
                # Wait for startup
                logger.info("⏳ Bot başlatma bekleniyor...")
                time.sleep(5)
                
                # Check if process is still running
                if process.poll() is None:
                    process_info.status = "running"
                    self.status.successful_components += 1
                    logger.info("✅ Production Bots başlatıldı!",
                              pid=process_info.pid,
                              script=script_path,
                              valid_sessions=valid_bots)
                    return True
                else:
                    process_info.status = "failed"
                    self.status.failed_components += 1
                    logger.error("❌ Production Bots başlatılamadı - process terminated")
                    return False
            
        except Exception as e:
            self.status.failed_components += 1
            logger.error("❌ Production bots başlatma hatası", error=str(e), exc_info=True)
            return False

    def show_startup_info(self) -> None:
        """Başlangıç bilgilerini göster."""
        print("\n" + "🎮" + "="*60 + "🎮")
        print("🚀 GavatCore OnlyVips v6.0 System")
        print("💰 XP/Token Economy + Multi-Bot + API")
        print("🎮" + "="*60 + "🎮")
        print()
        print("📊 COMPONENTS:")
        print("   🌐 Flask API Server    → localhost:5050")
        print("   🪙 XP Token API Server → localhost:5051 (NEW!)")
        print("   🤖 Production Bots (3) → Telegram")
        print("   💰 GavatCoin Token Engine → SQLite")
        print()
        print("🎯 ACTIVE BOTS:")
        print("   🌟 @yayincilara (Lara)")
        print("   🦁 @babagavat (Gavat Baba)")
        print("   🌸 @xxxgeisha (Geisha)")
        print()
        print("🪙 TOKEN FEATURES:")
        print("   • XP → Token conversion (1:1)")
        print("   • /stats command for users")
        print("   • Token spending system")
        print("   • Daily bonus rewards")
        print()
        print("⚡ QUICK ACCESS:")
        print("   • Bot API Status: http://localhost:5050/api/system/status")
        print("   • Token API Status: http://localhost:5051/api/system/status")
        print("   • API Documentation: http://localhost:5051/api/docs")
        print("   • Bot Stats: /stats (Telegram DM)")
        print("   • Token spending: /spend content")
        print()
    
    def setup_signal_handlers(self) -> None:
        """Signal handler'ları kur."""
        def signal_handler(signum: int, frame) -> None:
            logger.info("🛑 Çıkış sinyali alındı", 
                       signal=signum, 
                       signal_name=signal.Signals(signum).name)
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def shutdown(self) -> None:
        """
        Tüm bileşenleri güvenli şekilde kapat.
        
        Graceful shutdown with proper process termination.
        """
        with self._shutdown_lock:
            if not self.running:
                return
                
            logger.info("🔄 Sistem kapatılıyor...")
            self.running = False
            
            for process_info in self.processes:
                try:
                    logger.info("🛑 Process kapatılıyor...", 
                              name=process_info.name,
                              pid=process_info.pid)
                    
                    # Graceful termination
                    process_info.process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        process_info.process.wait(timeout=10)
                        process_info.status = "stopped"
                        logger.info("✅ Process kapatıldı", 
                                  name=process_info.name,
                                  pid=process_info.pid)
                    except subprocess.TimeoutExpired:
                        # Force kill if necessary
                        logger.warning("⚠️ Process zorla kapatılıyor...",
                                     name=process_info.name,
                                     pid=process_info.pid)
                        process_info.process.kill()
                        process_info.process.wait()
                        process_info.status = "killed"
                        
                except Exception as e:
                    logger.error("❌ Process kapatma hatası", 
                               name=process_info.name,
                               pid=process_info.pid,
                               error=str(e))
            
            # Final status report
            stopped_count = sum(1 for p in self.processes if p.status in ["stopped", "killed"])
            logger.info("🏁 Shutdown tamamlandı",
                       total_processes=len(self.processes),
                       stopped_processes=stopped_count)
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status.
        
        Returns:
            Dict with current system status information
        """
        return {
            "system_health": self.status.is_healthy,
            "success_rate": self.status.success_rate,
            "total_components": self.status.total_components,
            "successful_components": self.status.successful_components,
            "failed_components": self.status.failed_components,
            "uptime_seconds": (datetime.now() - self.status.startup_time).total_seconds(),
            "processes": [
                {
                    "name": p.name,
                    "pid": p.pid,
                    "status": p.status,
                    "uptime_seconds": (datetime.now() - p.start_time).total_seconds(),
                    "health_url": p.health_url
                }
                for p in self.processes
            ]
        }
    
    def run(self) -> None:
        """
        Ana launcher fonksiyonu.
        
        Orchestrates the entire system startup process.
        """
        self.show_startup_info()
        
        # Signal handlers
        self.setup_signal_handlers()
        
        logger.info("🚀 Sistem başlatılıyor...")
        
        # Component startup sequence
        components = [
            ("Flask API", self.start_flask_api),
            ("XP Token API", self.start_xp_token_api),
            ("Production Bots", self.start_production_bots)
        ]
        
        for component_name, start_func in components:
            try:
                logger.info("🔄 Component başlatılıyor", component=component_name)
                success = start_func()
                
                if success:
                    logger.info("✅ Component başarılı", component=component_name)
                else:
                    logger.warning("⚠️ Component başarısız", component=component_name)
                    
                # Small delay between components
                time.sleep(1)
                
            except Exception as e:
                logger.error("❌ Component başlatma hatası",
                           component=component_name,
                           error=str(e),
                           exc_info=True)
        
        # Final status report
        status = self.get_system_status()
        
        print("\n" + "🎉" + "="*50 + "🎉")
        print(f"🚀 Sistem başlatıldı! {status['successful_components']}/{status['total_components']} bileşen aktif")
        print(f"📊 Başarı oranı: {status['success_rate']:.1f}%")
        print("🎉" + "="*50 + "🎉")
        
        if status['successful_components'] > 0:
            print("\n📊 SYSTEM STATUS:")
            for process in status['processes']:
                status_emoji = "✅" if process['status'] == "running" else "❌"
                print(f"   {status_emoji} {process['name']} - PID: {process['pid']} - Status: {process['status']}")
            
            if status['system_health']:
                print("\n🚀 Sistem sağlıklı çalışıyor! Ctrl+C ile durdurabilirsiniz.")
                
                # Keep running until interrupted
                try:
                    while self.running:
                        time.sleep(5)
                        
                        # Health check every 30 seconds
                        if int(time.time()) % 30 == 0:
                            healthy_count = 0
                            for process_info in self.processes:
                                if (process_info.health_url and 
                                    self._check_service_health(process_info.health_url)):
                                    healthy_count += 1
                                elif process_info.process.poll() is None:
                                    healthy_count += 1
                            
                            logger.debug("💓 Health check",
                                       healthy_services=healthy_count,
                                       total_services=len(self.processes))
                            
                except KeyboardInterrupt:
                    logger.info("⌨️ Keyboard interrupt received")
            else:
                print("\n❌ Sistem başlatılamadı!")
                sys.exit(1)
        else:
            print("\n❌ Hiçbir bileşen başlatılamadı!")
            sys.exit(1)

def main() -> None:
    """Ana entry point fonksiyonu."""
    try:
        launcher = GavatCoreSystemLauncher()
        launcher.run()
    except KeyboardInterrupt:
        logger.info("\n⌨️ Program kullanıcı tarafından durduruldu.")
    except Exception as e:
        logger.error("\n❌ Kritik hata", error=str(e), exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
