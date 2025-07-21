from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🚀 GavatCore Ultimate Run v4.0 🚀

3 Ana Bot Sistemi:
• 🎯 BabaGavat (Bilge Lider)
• 🎮 Yayıncı Lara (Streamer Energy)
• 🌸 XXXGeisha (Mysterious Elegant)

Sistem Bileşenleri:
• Flask API Server (localhost:5050)
• XP Token API (localhost:5051)
• Core GavatCore System
• GPT-4 Entegrasyonu
• Character & Persona System

Kullanım: python gavatcore_ultimate_run.py
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
# Threading, HTTP and monitoring deps
import threading
# Use requests if available, else fallback
try:
    import requests
except ImportError:
    requests = None
from urllib.request import urlopen
# psutil for process stats
try:
    import psutil
except ImportError:
    psutil = None
import structlog
from pathlib import Path
# Verify critical dependencies
missing = []
if requests is None:
    missing.append("requests")
if psutil is None:
    missing.append("psutil")
if missing:
    # Suggest activating project venv if present, else fall back to system pip
    venv_dir = Path(__file__).parent / '.venv'
    if venv_dir.exists():
        print(
            f"❌ Missing dependencies: {', '.join(missing)}.",
            f"Please activate the project venv and install: source .venv/bin/activate && pip install {' '.join(missing)}",
            file=sys.stderr
        )
    else:
        print(
            f"❌ Missing dependencies: {', '.join(missing)}.",
            f"Please install with: python3 -m pip install {' '.join(missing)}",
            file=sys.stderr
        )
    sys.exit(1)

# Configure structured logging
log_processors = [
    structlog.stdlib.filter_by_level,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.dev.ConsoleRenderer()
]

structlog.configure(
    processors=log_processors,
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("gavatcore.ultimate")

@dataclass
class ProcessInfo:
    """Process information data structure."""
    name: str
    process: subprocess.Popen
    start_time: datetime = field(default_factory=datetime.now)
    pid: Optional[int] = None
    status: str = "starting"
    health_url: Optional[str] = None
    character: Optional[str] = None
    description: str = ""
    
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
    character_bots: int = 0
    system_components: int = 0
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

class GavatCoreUltimateSystem:
    """
    🚀 GavatCore Ultimate System Launcher
    
    3 Ana Bot + Full System Management
    """
    
    def __init__(self):
        self.processes: List[ProcessInfo] = []
        self.running: bool = True
        self.status = SystemStatus()
        self._shutdown_lock = threading.Lock()
        
        # 3 Ana Bot Konfigürasyonu
        self.character_bots = {
            "babagavat": {
                "name": "🎯 BabaGavat",
                "session": "sessions/babagavat_conversation.session",
                "character": {
                    "name": "Baba Gavat",
                    "personality": "Bilge, tecrübeli, komik. Gruplarda lider, herkesi yönlendirir. Bazen argo kullanır.",
                    "style": "Abi tavrı, öğüt verici, bazen ironik. 'Evlat', 'oğlum' gibi hitaplar.",
                    "mood": "wise_leader",
                    "trigger_words": ["baba", "gavat", "abi", "hocam", "tavsiye", "yardım"]
                },
                "priority": 1,
                "description": "Ana lider bot - Grup yönetimi ve DM handling"
            },
            "yayincilara": {
                "name": "🎮 Yayıncı Lara",
                "session": "sessions/yayincilara_conversation.session",
                "character": {
                    "name": "Yayıncı Lara",
                    "personality": "Enerjik, eğlenceli, yayın odaklı. Streaming kültürüne hakim, trending konularda aktif.",
                    "style": "Genç, dinamik dil. Gaming ve streaming terimleri kullanır.",
                    "mood": "streamer_energy",
                    "trigger_words": ["yayın", "stream", "game", "chat", "live", "twitch"]
                },
                "priority": 2,
                "description": "Streaming ve gaming odaklı bot"
            },
            "xxxgeisha": {
                "name": "🌸 XXXGeisha",
                "session": "sessions/xxxgeisha_conversation.session",
                "character": {
                    "name": "Geisha",
                    "personality": "Gizemli, çekici, sofistike. Derin konuşmalar yapar, sanatsal yaklaşımlar.",
                    "style": "Zarif, akıllı dil. Metaforlar ve felsefi yaklaşımlar kullanır.",
                    "mood": "mysterious_elegant",
                    "trigger_words": ["sanat", "güzellik", "felsefe", "geisha", "zen", "estetik"]
                },
                "priority": 3,
                "description": "Sofistike ve gizemli karakter bot"
            }
        }
        
        # Sistem bileşenleri
        self.system_components = {
            "core_system": {
                "name": "🏗️ GavatCore System",
                "command": ["python", "main.py"],
                "health_url": None,
                "priority": 0,
                "description": "Core sistem - Contact management, DM handling"
            },
            "flask_api": {
                "name": "🌐 Flask API Server",
                "command": ["python", "apis/production_bot_api.py"],
                "health_url": "http://localhost:5050/api/system/status",
                "priority": 4,
                "description": "REST API server (port 5050)"
            },
            "xp_token_api": {
                "name": "🪙 XP Token API",
                "command": ["python", "apis/xp_token_api_sync.py"],
                "health_url": "http://localhost:5051/health",
                "priority": 5,
                "description": "Token economy API (port 5051)"
            }
        }
        
        logger.info("🔧 GavatCore Ultimate System initialized")
        
    def print_ultimate_banner(self):
        """Ultimate system banner"""
        banner = f"""
🔥═══════════════════════════════════════════════════════════════🔥
██╗   ██╗██╗  ████████╗██╗███╗   ███╗ █████╗ ████████╗███████╗
██║   ██║██║  ╚══██╔══╝██║████╗ ████║██╔══██╗╚══██╔══╝██╔════╝
██║   ██║██║     ██║   ██║██╔████╔██║███████║   ██║   █████╗  
██║   ██║██║     ██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██╔══╝  
╚██████╔╝███████╗██║   ██║██║ ╚═╝ ██║██║  ██║   ██║   ███████╗
 ╚═════╝ ╚══════╝╚═╝   ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝
🔥═══════════════════════════════════════════════════════════════🔥
        🚀 GAVATCORE ULTIMATE SYSTEM v4.0 🚀
        💎 3 ANA BOT + FULL GPT SYSTEM 💎
🔥═══════════════════════════════════════════════════════════════🔥

🎯 3 ANA BOT:
   • BabaGavat (Bilge Lider) - Grup yönetimi & DM handling
   • Yayıncı Lara (Streamer Energy) - Gaming & streaming odaklı
   • XXXGeisha (Mysterious Elegant) - Sofistike & gizemli

✨ SİSTEM BİLEŞENLERİ:
   • GavatCore System (Core functionality)
   • Flask API Server (REST API - port 5050)
   • XP Token API (Token economy - port 5051)

🔥═══════════════════════════════════════════════════════════════🔥
        """
        print(banner)
    
    def _check_service_health(self, url: str, timeout: int = 2) -> bool:
        """Check if a service is healthy by making HTTP request."""
        try:
            if requests:
                resp = requests.get(url, timeout=timeout)
                code = resp.status_code
            else:
                resp = urlopen(url, timeout=timeout)
                code = resp.getcode()
            return code in (200, 201)
        except Exception:
            return False
    
    def start_system_component(self, comp_key: str, config: Dict) -> bool:
        """Start a system component."""
        try:
            self.status.total_components += 1
            logger.info(f"🚀 {config['name']} başlatılıyor...")
            
            # Check if already running
            if config.get('health_url') and self._check_service_health(config['health_url']):
                logger.info(f"✅ {config['name']} zaten çalışıyor!")
                self.status.successful_components += 1
                self.status.system_components += 1
                return True
            
            # Start new process
            process = subprocess.Popen(
                config['command'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            process_info = ProcessInfo(
                name=config['name'],
                process=process,
                health_url=config.get('health_url'),
                description=config['description']
            )
            
            self.processes.append(process_info)
            self.status.processes.append(process_info)
            
            # Wait and verify startup
            time.sleep(3)
            
            # Health check if URL provided
            if config.get('health_url'):
                if self._check_service_health(config['health_url']):
                    process_info.status = "running"
                    self.status.successful_components += 1
                    self.status.system_components += 1
                    logger.info(f"✅ {config['name']} başlatıldı!",
                              pid=process_info.pid,
                              health_url=config['health_url'])
                    return True
                else:
                    process_info.status = "failed"
                    self.status.failed_components += 1
                    logger.error(f"❌ {config['name']} health check başarısız")
                    return False
            else:
                # No health check, assume success if process is running
                if process.poll() is None:
                    process_info.status = "running"
                    self.status.successful_components += 1
                    self.status.system_components += 1
                    logger.info(f"✅ {config['name']} başlatıldı!", pid=process_info.pid)
                    return True
                else:
                    process_info.status = "failed"
                    self.status.failed_components += 1
                    logger.error(f"❌ {config['name']} başlatılamadı")
                    return False
            
        except Exception as e:
            self.status.failed_components += 1
            logger.error(f"❌ {config['name']} başlatma hatası", error=str(e), exc_info=True)
            return False
    
    def start_character_bot(self, bot_key: str, config: Dict) -> bool:
        """Start a character bot."""
        try:
            self.status.total_components += 1
            logger.info(f"🤖 {config['name']} başlatılıyor...")
            
            # Set environment variables for character
            env = os.environ.copy()
            env['GAVATCORE_BOT_MODE'] = bot_key
            env['GAVATCORE_CHARACTER'] = json.dumps(config['character'])
            
            # Start multi bot launcher with character config
            # Launch character bot interactively to allow Telegram code prompts
            process = subprocess.Popen(
                ["python", "multi_bot_launcher.py"],
                start_new_session=True,
                env=env
            )
            
            process_info = ProcessInfo(
                name=config['name'],
                process=process,
                character=bot_key,
                description=config['description']
            )
            
            self.processes.append(process_info)
            self.status.processes.append(process_info)
            
            # Wait longer for character bots
            time.sleep(5)
            
            if process.poll() is None:
                process_info.status = "running"
                self.status.successful_components += 1
                self.status.character_bots += 1
                logger.info(f"✅ {config['name']} aktif!",
                          pid=process_info.pid,
                          character=config['character']['name'])
                return True
            else:
                process_info.status = "failed"
                self.status.failed_components += 1
                logger.error(f"❌ {config['name']} başlatılamadı")
                return False
            
        except Exception as e:
            self.status.failed_components += 1
            logger.error(f"❌ {config['name']} başlatma hatası", error=str(e), exc_info=True)
            return False
    
    def start_all_systems(self) -> Dict[str, int]:
        """Start all systems."""
        logger.info("🔥 ULTIMATE GAVATCORE BAŞLATILIYOR! 🔥")
        
        results = {
            'system_components': 0,
            'character_bots': 0,
            'total_success': 0,
            'total_attempted': 0
        }
        
        # 1. Start system components first
        logger.info("🏗️ Sistem bileşenleri başlatılıyor...")
        sorted_components = sorted(
            self.system_components.items(),
            key=lambda x: x[1]['priority']
        )
        
        for comp_key, config in sorted_components:
            if self.start_system_component(comp_key, config):
                results['system_components'] += 1
            time.sleep(2)
        
        # 2. Start character bots
        logger.info("🤖 Karakter botları başlatılıyor...")
        sorted_bots = sorted(
            self.character_bots.items(),
            key=lambda x: x[1]['priority']
        )
        
        for bot_key, config in sorted_bots:
            if self.start_character_bot(bot_key, config):
                results['character_bots'] += 1
            time.sleep(3)
        
        results['total_success'] = self.status.successful_components
        results['total_attempted'] = self.status.total_components
        
        return results
    
    def show_system_status(self) -> None:
        """Show comprehensive system status."""
        print("\n" + "="*80)
        print("📊 GAVATCORE ULTIMATE SYSTEM STATUS")
        print("="*80)
        
        if not self.processes:
            print("❌ Hiçbir bileşen çalışmıyor")
            return
        
        # System components
        system_procs = [p for p in self.processes if not p.character]
        character_procs = [p for p in self.processes if p.character]
        
        if system_procs:
            print("\n🏗️ SİSTEM BİLEŞENLERİ:")
            print("-" * 50)
            for i, proc in enumerate(system_procs, 1):
                try:
                    process = psutil.Process(proc.pid)
                    status = "🟢 ÇALIŞIYOR" if process.is_running() else "🔴 DURDU"
                    uptime = datetime.now() - proc.start_time
                    memory_mb = process.memory_info().rss / (1024 * 1024)
                    cpu_percent = process.cpu_percent()
                    
                    print(f"{i:2d}. {proc.name}")
                    print(f"    Status: {status}")
                    print(f"    PID: {proc.pid}")
                    print(f"    Uptime: {str(uptime).split('.')[0]}")
                    print(f"    Memory: {memory_mb:.1f}MB")
                    print(f"    CPU: {cpu_percent:.1f}%")
                    print(f"    📝 {proc.description}")
                    if proc.health_url:
                        health = "🟢 HEALTHY" if self._check_service_health(proc.health_url) else "🔴 UNHEALTHY"
                        print(f"    Health: {health}")
                    print()
                    
                except psutil.NoSuchProcess:
                    print(f"{i:2d}. {proc.name} - 🔴 PROCESS BULUNAMADI")
                    print()
        
        if character_procs:
            print("🤖 KARAKTER BOTLARI:")
            print("-" * 50)
            for i, proc in enumerate(character_procs, 1):
                try:
                    process = psutil.Process(proc.pid)
                    status = "🟢 ÇALIŞIYOR" if process.is_running() else "🔴 DURDU"
                    uptime = datetime.now() - proc.start_time
                    memory_mb = process.memory_info().rss / (1024 * 1024)
                    cpu_percent = process.cpu_percent()
                    
                    # Get character info
                    char_config = self.character_bots.get(proc.character, {})
                    char_name = char_config.get('character', {}).get('name', proc.character)
                    
                    print(f"{i:2d}. {proc.name}")
                    print(f"    🎭 Karakter: {char_name}")
                    print(f"    Status: {status}")
                    print(f"    PID: {proc.pid}")
                    print(f"    Uptime: {str(uptime).split('.')[0]}")
                    print(f"    Memory: {memory_mb:.1f}MB")
                    print(f"    CPU: {cpu_percent:.1f}%")
                    print(f"    📝 {proc.description}")
                    print(f"    📁 Session: {char_config.get('session', 'N/A')}")
                    print()
                    
                except psutil.NoSuchProcess:
                    print(f"{i:2d}. {proc.name} - 🔴 PROCESS BULUNAMADI")
                    print()
        
        # Summary
        total_uptime = datetime.now() - self.status.startup_time
        running_count = sum(1 for p in self.processes 
                          if psutil.Process(p.pid).is_running())
        total_memory = sum(
            psutil.Process(p.pid).memory_info().rss / (1024 * 1024)
            for p in self.processes
            if psutil.Process(p.pid).is_running()
        )
        
        print("📈 SISTEM ÖZETİ:")
        print("-" * 50)
        print(f"🟢 Çalışan Bileşenler: {running_count}/{len(self.processes)}")
        print(f"🤖 Karakter Botları: {len(character_procs)}")
        print(f"🏗️ Sistem Bileşenleri: {len(system_procs)}")
        print(f"⏱️ Sistem Uptime: {str(total_uptime).split('.')[0]}")
        print(f"💾 Toplam Memory: {total_memory:.1f}MB")
        print(f"📊 Başarı Oranı: {self.status.success_rate:.1f}%")
    
    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum: int, frame) -> None:
            logger.info("🛑 Shutdown signal received", 
                       signal=signum, 
                       signal_name=signal.Signals(signum).name)
            self.shutdown()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def shutdown(self) -> None:
        """Graceful shutdown of all components."""
        with self._shutdown_lock:
            if not self.running:
                return
            
            self.running = False
            logger.info("🛑 GavatCore Ultimate System kapatılıyor...")
            
            # Stop all processes
            for proc_info in self.processes:
                try:
                    process = psutil.Process(proc_info.pid)
                    if process.is_running():
                        logger.info(f"🔴 {proc_info.name} durduruluyor...")
                        process.terminate()
                        
                        # Wait for graceful shutdown
                        try:
                            process.wait(timeout=10)
                            logger.info(f"✅ {proc_info.name} durduruldu")
                        except psutil.TimeoutExpired:
                            logger.warning(f"💀 {proc_info.name} zorla kapatılıyor...")
                            process.kill()
                            process.wait()
                            logger.info(f"💀 {proc_info.name} zorla kapatıldı")
                            
                except psutil.NoSuchProcess:
                    logger.info(f"⚠️ {proc_info.name} zaten durmuş")
                except Exception as e:
                    logger.error(f"❌ {proc_info.name} kapatma hatası", error=str(e))
            
            logger.info("✅ Tüm bileşenler durduruldu!")
            logger.info("👋 GavatCore Ultimate System kapatıldı!")
    
    def run(self) -> None:
        """Main run method."""
        self.print_ultimate_banner()
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        logger.info("🔧 Sistem başlatılıyor...")
        
        # Start all systems
        results = self.start_all_systems()
        
        # Show results
        print(f"\n🎉 BAŞLATMA SONUÇLARI:")
        print(f"   🏗️ Sistem Bileşenleri: {results['system_components']}")
        print(f"   🤖 Karakter Botları: {results['character_bots']}")
        print(f"   ✅ Toplam Başarılı: {results['total_success']}/{results['total_attempted']}")
        print(f"   📊 Başarı Oranı: {self.status.success_rate:.1f}%")
        
        if self.status.is_healthy:
            print("\n🔥 GAVATCORE ULTIMATE SYSTEM AKTİF! 🔥")
            print("📊 Sistem durumu için: Ctrl+C sonra 's' tuşu")
            print("🛑 Kapatmak için: Ctrl+C")
            
            try:
                # Keep running and show periodic status
                while self.running:
                    time.sleep(30)  # Check every 30 seconds
                    
                    # Check if any process died
                    dead_processes = []
                    for proc in self.processes:
                        try:
                            if not psutil.Process(proc.pid).is_running():
                                dead_processes.append(proc)
                        except psutil.NoSuchProcess:
                            dead_processes.append(proc)
                    
                    if dead_processes:
                        logger.warning(f"⚠️ {len(dead_processes)} bileşen durdu!")
                        for proc in dead_processes:
                            logger.warning(f"💀 {proc.name} durdu")
                            
            except KeyboardInterrupt:
                print("\n\n🛑 Ctrl+C ile kapatma...")
                choice = input("Sistem durumunu görmek ister misiniz? (s/n): ").lower()
                if choice == 's':
                    self.show_system_status()
                    input("\nDevam etmek için Enter'a basın...")
                self.shutdown()
        else:
            logger.error("❌ Sistem başlatılamadı!")
            self.shutdown()
            sys.exit(1)

def main() -> None:
    """Main entry point."""
    try:
        system = GavatCoreUltimateSystem()
        system.run()
    except Exception as e:
        logger.error("❌ Fatal error", error=str(e), exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
