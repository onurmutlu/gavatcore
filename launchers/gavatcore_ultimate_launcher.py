#!/usr/bin/env python3
"""
🔥 GAVATCORE ULTIMATE LAUNCHER 🔥
=================================

Tam otomatik sistem:
- Persona JSON'lardan telefon numaraları otomatik
- Session dosyaları otomatik kullanılır  
- 3 bot + API + monitoring
- Telefon numarası sormaz
- Graceful shutdown
- Health monitoring

ÇATIR ÇUTUR OTOMASYON!
"""

import subprocess
import sys
import time
import signal
import logging
import os
import json
import asyncio
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import threading
import requests
from pathlib import Path
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("gavatcore.ultimate_launcher")

@dataclass
class BotConfig:
    """Bot konfigürasyon bilgileri"""
    name: str
    persona_file: str
    expected_phone: str
    display_name: str
    process: Optional[subprocess.Popen] = None
    pid: Optional[int] = None
    status: str = "stopped"
    start_time: Optional[datetime] = None

@dataclass
class SystemStatus:
    """Sistem durumu"""
    bots_total: int = 0
    bots_running: int = 0
    api_running: bool = False
    monitoring_running: bool = False
    startup_time: datetime = field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        return (self.bots_running / max(self.bots_total, 1)) * 100
    
    @property
    def is_healthy(self) -> bool:
        return self.bots_running > 0 or self.api_running

class GavatCoreUltimateLauncher:
    """Ultimate Bot Launcher - Tam Otomatik"""
    
    def __init__(self):
        self.bot_configs = {
            "lara": BotConfig(
                name="lara",
                persona_file="data/personas/yayincilara.json",
                expected_phone="+905382617727",
                display_name="Lara - Flörtöz Yayıncı"
            ),
            "babagavat": BotConfig(
                name="babagavat", 
                persona_file="data/personas/babagavat.json",
                expected_phone="+905513272355",
                display_name="BabaGavat - Pavyon Lideri"
            ),
            "geisha": BotConfig(
                name="geisha",
                persona_file="data/personas/xxxgeisha.json",
                expected_phone="+905486306226",
                display_name="Geisha - Vamp Moderatör"
            )
        }
        
        self.api_process = None
        self.monitoring_process = None
        self.running = True
        self.status = SystemStatus()
        self.status.bots_total = len(self.bot_configs)
        
        logger.info("🔧 GavatCore Ultimate Launcher başlatıldı")
    
    def load_persona_data(self, bot_config: BotConfig) -> Dict:
        """Persona JSON dosyasından bot bilgilerini yükle"""
        if not os.path.exists(bot_config.persona_file):
            logger.error(f"❌ Persona dosyası bulunamadı: {bot_config.persona_file}")
            return {}
        
        try:
            with open(bot_config.persona_file, 'r', encoding='utf-8') as f:
                persona_data = json.load(f)
            
            phone = persona_data.get('phone', bot_config.expected_phone)
            clean_phone = phone.replace('+', '')
            session_path = f"sessions/_{clean_phone}.session"
            
            return {
                "phone": phone,
                "session_path": session_path,
                "username": persona_data.get('username', bot_config.name),
                "display_name": persona_data.get('display_name', bot_config.display_name),
                "persona_data": persona_data
            }
            
        except Exception as e:
            logger.error(f"❌ Persona yükleme hatası: {e}")
            return {}
    
    def verify_session_files(self) -> bool:
        """Tüm session dosyalarını kontrol et"""
        logger.info("🔍 Session dosyaları kontrol ediliyor...")
        
        all_valid = True
        
        for bot_name, bot_config in self.bot_configs.items():
            persona = self.load_persona_data(bot_config)
            if not persona:
                logger.error(f"❌ {bot_name}: Persona yüklenemedi")
                all_valid = False
                continue
            
            session_path = persona["session_path"]
            
            if not os.path.exists(session_path):
                logger.error(f"❌ {bot_name}: Session dosyası bulunamadı!")
                all_valid = False
                continue
            
            size_kb = os.path.getsize(session_path) / 1024
            
            if size_kb < 10:
                logger.warning(f"⚠️ {bot_name}: Session dosyası küçük ({size_kb:.1f}KB)")
            else:
                logger.info(f"✅ {bot_name}: Session hazır ({size_kb:.1f}KB)")
        
        return all_valid
    
    def create_bot_script(self, bot_name: str, persona: Dict) -> str:
        """Bot için geçici script oluştur"""
        script_content = f'''#!/usr/bin/env python3
import asyncio
import json
import os
from telethon import TelegramClient, events
from telethon.tl.types import User
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
from datetime import datetime

class {bot_name.title()}AutoLauncher:
    def __init__(self):
        self.client = None
        
    async def start(self):
        print("🤖 {persona['display_name']} başlatılıyor...")
        
        phone = "{persona['phone']}"
        session_path = "{persona['session_path'].replace('.session', '')}"
        
        print(f"📱 Telefon: {{phone}}")
        print(f"💾 Session: {{session_path}}")
        
        self.client = TelegramClient(
            session_path, TELEGRAM_API_ID, TELEGRAM_API_HASH,
            device_model="{persona['display_name']} Bot",
            system_version="GAVATCore v2.0"
        )
        
        try:
            await self.client.start()
            me = await self.client.get_me()
            print(f"✅ {persona['display_name']} aktif: @{{me.username}} (ID: {{me.id}})")
            
            @self.client.on(events.NewMessage(incoming=True))
            async def handler(event):
                if event.is_private:
                    sender = await event.get_sender()
                    if sender and not getattr(sender, 'bot', False):
                        print(f"💬 {bot_name.title()} DM: {{sender.first_name}} -> {{event.raw_text[:30]}}...")
            
            print("🔥 {persona['display_name']} hazır - mesajları dinliyor!")
            await self.client.run_until_disconnected()
            
        except Exception as e:
            print(f"❌ {persona['display_name']} hata: {{e}}")

if __name__ == "__main__":
    launcher = {bot_name.title()}AutoLauncher()
    asyncio.run(launcher.start())
'''
        
        script_path = f"auto_{bot_name}_launcher.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        return script_path
    
    def start_monitoring_api(self) -> bool:
        """Monitoring API'sini başlat"""
        try:
            logger.info("🚀 Monitoring API başlatılıyor...")
            
            # API script'i kontrol et
            api_script = "apis/real_bot_api_no_mock.py"
            if not os.path.exists(api_script):
                # Alternatif API'leri dene
                alternatives = [
                    "apis/real_bot_management_api.py",
                    "apis/production_bot_api.py"
                ]
                for alt in alternatives:
                    if os.path.exists(alt):
                        api_script = alt
                        break
                else:
                    logger.error("❌ Monitoring API script bulunamadı")
                    return False
            
            self.api_process = subprocess.Popen(
                ["python3", api_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # API'nin başlaması için bekle
            time.sleep(3)
            
            # Process çalışıyor mu kontrol et
            if self.api_process.poll() is None:
                logger.info(f"✅ Monitoring API başlatıldı (Script: {api_script})")
                return True
            else:
                logger.error("❌ Monitoring API başlatılamadı")
                return False
                
        except Exception as e:
            logger.error(f"❌ Monitoring API başlatma hatası: {e}")
            return False
    
    def start_bot(self, bot_name: str) -> bool:
        """Tek bot başlat"""
        bot_config = self.bot_configs[bot_name]
        
        logger.info(f"🤖 {bot_config.display_name} başlatılıyor...")
        
        # Persona verilerini yükle
        persona = self.load_persona_data(bot_config)
        if not persona:
            logger.error(f"❌ {bot_name}: Persona yüklenemedi")
            return False
        
        # Geçici script oluştur
        script_path = self.create_bot_script(bot_name, persona)
        
        try:
            # Bot process'ini başlat
            process = subprocess.Popen(
                ["python3", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            bot_config.process = process
            bot_config.pid = process.pid
            bot_config.start_time = datetime.now()
            
            time.sleep(2)
            
            # Process çalışıyor mu kontrol et
            if process.poll() is None:
                bot_config.status = "running"
                self.status.bots_running += 1
                logger.info(f"✅ {bot_config.display_name} başlatıldı (PID: {process.pid})")
                return True
            else:
                bot_config.status = "failed"
                logger.error(f"❌ {bot_config.display_name} başlatılamadı")
                return False
                
        except Exception as e:
            bot_config.status = "error"
            logger.error(f"❌ {bot_config.display_name} başlatma hatası: {e}")
            return False
    
    def start_all_bots(self) -> Dict[str, bool]:
        """Tüm bot'ları başlat"""
        logger.info("🚀 Tüm bot'lar başlatılıyor...")
        
        results = {}
        
        for bot_name in self.bot_configs.keys():
            success = self.start_bot(bot_name)
            results[bot_name] = success
            time.sleep(1)  # Bot'lar arası bekle
        
        return results
    
    def show_status(self):
        """Sistem durumunu göster"""
        logger.info("📊 Sistem durumu:")
        
        # API durumu
        if self.status.api_running:
            logger.info("✅ Monitoring API: Çalışıyor (Port 5005)")
        else:
            logger.info("❌ Monitoring API: Çalışmıyor")
        
        # Bot durumları
        for bot_name, bot_config in self.bot_configs.items():
            if bot_config.status == "running":
                uptime = datetime.now() - bot_config.start_time if bot_config.start_time else None
                uptime_min = int(uptime.total_seconds() / 60) if uptime else 0
                logger.info(f"✅ {bot_config.display_name}: Çalışıyor (PID: {bot_config.pid}, Uptime: {uptime_min}min)")
            else:
                logger.info(f"❌ {bot_config.display_name}: {bot_config.status}")
        
        logger.info(f"🎯 Toplam: {self.status.bots_running}/{self.status.bots_total} bot aktif")
    
    def stop_all(self):
        """Tüm servisleri durdur"""
        logger.info("🔴 Sistem durduruluyor...")
        
        # Bot'ları durdur
        for bot_name, bot_config in self.bot_configs.items():
            if bot_config.process:
                try:
                    bot_config.process.terminate()
                    bot_config.process.wait(timeout=5)
                    bot_config.status = "stopped"
                    logger.info(f"🔴 {bot_config.display_name} durduruldu")
                except:
                    bot_config.process.kill()
                    logger.info(f"🔪 {bot_config.display_name} zorla durduruldu")
        
        # API'yi durdur
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                logger.info("🔴 Monitoring API durduruldu")
            except:
                self.api_process.kill()
        
        # Geçici script'leri temizle
        for bot_name in self.bot_configs.keys():
            script_path = f"auto_{bot_name}_launcher.py"
            if os.path.exists(script_path):
                os.remove(script_path)
        
        logger.info("✅ Tüm servisler durduruldu")
    
    def setup_signal_handlers(self):
        """Signal handler'ları kur"""
        def signal_handler(signum, frame):
            logger.info(f"🛑 Çıkış sinyali alındı: {signum}")
            self.running = False
            self.stop_all()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def run_ultimate_automation(self):
        """ULTIMATE AUTOMATION - Tam otomatik sistem"""
        print(f"""
🔥🔥🔥 GAVATCORE ULTIMATE LAUNCHER 🔥🔥🔥
==========================================
🤖 3 Bot Otomatik (Session'lı)
📊 Monitoring API Otomatik
❌ HİÇ MANUEL İŞLEM YOK!
==========================================
Başlatma: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """)
        
        try:
            # Signal handlers
            self.setup_signal_handlers()
            
            # 1. Session kontrolü
            if not self.verify_session_files():
                logger.error("❌ Session dosyaları eksik!")
                return False
            
            # 2. Monitoring API başlat
            api_success = self.start_monitoring_api()
            
            # 3. Tüm bot'ları başlat
            bot_results = self.start_all_bots()
            success_count = sum(bot_results.values())
            
            # 4. Durum raporu
            time.sleep(3)
            self.show_status()
            
            print(f"""
🔥 ULTIMATE LAUNCHER TAMAMLANDI! 🔥
===================================
📊 Monitoring: http://localhost:5005
🤖 {success_count}/3 bot aktif
🎯 Success Rate: {self.status.success_rate:.1f}%
===================================
Ctrl+C ile tüm sistemi durdur
            """)
            
            # 5. Ana loop
            while self.running:
                time.sleep(10)
                # İsteğe bağlı health check
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ultimate automation hatası: {e}")
            self.stop_all()
            return False

# Global instance
ultimate_launcher = GavatCoreUltimateLauncher()

def main():
    """Ana fonksiyon"""
    try:
        success = ultimate_launcher.run_ultimate_automation()
        if not success:
            logger.error("❌ Sistem başlatılamadı!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Kullanıcı tarafından durduruldu")
        ultimate_launcher.stop_all()
    except Exception as e:
        logger.error(f"❌ Kritik hata: {e}")
        ultimate_launcher.stop_all()
        sys.exit(1)

if __name__ == "__main__":
    main() 