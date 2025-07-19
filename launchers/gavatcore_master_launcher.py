from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🚀 GAVATCORE MASTER LAUNCHER 🚀
================================

Tüm bot launcher'ları birleştiren merkezi sistem:
- Stripe webhook entegrasyonu
- 3 ana bot (gawatbaba, yayincilara, xxxgeisha)
- Monitoring API
- Session yönetimi
- Health check
- Graceful shutdown

PRODUCTION READY!
"""

import asyncio
import json
import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import structlog

# GAVATCore imports
from telethon import TelegramClient, events
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

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

logger = structlog.get_logger("gavatcore.master_launcher")

@dataclass
class BotConfig:
    """Bot konfigürasyon bilgileri"""
    name: str
    persona_file: str
    display_name: str
    expected_phone: str
    session_path: Optional[str] = None
    client: Optional[TelegramClient] = None
    status: str = "stopped"
    start_time: Optional[datetime] = None
    user_id: Optional[int] = None
    username: Optional[str] = None

@dataclass
class SystemStatus:
    """Sistem durumu"""
    bots_total: int = 0
    bots_running: int = 0
    api_running: bool = False
    startup_time: datetime = field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        return (self.bots_running / max(self.bots_total, 1)) * 100
    
    @property
    def is_healthy(self) -> bool:
        return self.bots_running > 0

class GavatCoreMasterLauncher:
    """Master Bot Launcher - Merkezi kontrol sistemi"""
    
    def __init__(self):
        self.bot_configs = {
            "gawatbaba": BotConfig(
                name="gawatbaba",
                persona_file="data/personas/gawatbaba.json",
                display_name="GawatBaba - Sistem Admin",
                expected_phone="+447832134241"
            ),
            "yayincilara": BotConfig(
                name="yayincilara",
                persona_file="data/personas/yayincilara.json", 
                display_name="Yayıncı Lara - Streamer",
                expected_phone="+905382617727"
            ),
            "xxxgeisha": BotConfig(
                name="xxxgeisha",
                persona_file="data/personas/xxxgeisha.json",
                display_name="XXX Geisha - VIP",
                expected_phone="+905486306226"
            )
        }
        
        self.api_process = None
        self.running = True
        self.status = SystemStatus()
        self.status.bots_total = len(self.bot_configs)
        
        logger.info("🔧 GavatCore Master Launcher başlatıldı")
    
    def load_persona_data(self, bot_config: BotConfig) -> Optional[Dict]:
        """Persona JSON dosyasından veri yükle"""
        try:
            if not os.path.exists(bot_config.persona_file):
                logger.error(f"❌ Persona dosyası bulunamadı: {bot_config.persona_file}")
                return None
            
            with open(bot_config.persona_file, 'r', encoding='utf-8') as f:
                persona = json.load(f)
            
            # Session path'i hesapla
            phone = persona.get('phone', bot_config.expected_phone)
            clean_phone = phone.replace('+', '')
            session_path = f"sessions/_{clean_phone}.session"
            
            # Persona'ya session path ekle
            persona['session_path'] = session_path
            bot_config.session_path = session_path
            
            return persona
            
        except Exception as e:
            logger.error(f"❌ Persona yükleme hatası ({bot_config.name}): {e}")
            return None
    
    def verify_session_files(self) -> bool:
        """Session dosyalarını kontrol et"""
        logger.info("🔍 Session dosyaları kontrol ediliyor...")
        
        all_valid = True
        
        for bot_name, bot_config in self.bot_configs.items():
            persona = self.load_persona_data(bot_config)
            if not persona:
                logger.error(f"❌ {bot_name}: Persona yüklenemedi")
                all_valid = False
                continue
            
            session_path = persona['session_path']
            
            if not os.path.exists(session_path):
                logger.error(f"❌ {bot_name}: Session dosyası bulunamadı - {session_path}")
                all_valid = False
                continue
            
            size_kb = os.path.getsize(session_path) / 1024
            
            if size_kb < 5:
                logger.warning(f"⚠️ {bot_name}: Session dosyası küçük ({size_kb:.1f}KB)")
                all_valid = False
            else:
                logger.info(f"✅ {bot_name}: Session hazır ({size_kb:.1f}KB)")
        
        return all_valid
    
    async def start_bot(self, bot_name: str) -> bool:
        """Belirli bir bot'u başlat"""
        try:
            bot_config = self.bot_configs[bot_name]
            logger.info(f"🤖 {bot_config.display_name} başlatılıyor...")
            
            # Persona verilerini yükle
            persona = self.load_persona_data(bot_config)
            if not persona:
                logger.error(f"❌ {bot_name}: Persona yüklenemedi")
                return False
            
            # Session dosyasını kontrol et
            session_path = persona['session_path']
            if not os.path.exists(session_path):
                logger.error(f"❌ {bot_name}: Session dosyası bulunamadı")
                return False
            
            # Telegram client oluştur
            session_name = session_path.replace('.session', '')
            
            client = TelegramClient(
                session_name,
                TELEGRAM_API_ID,
                TELEGRAM_API_HASH,
                device_model=f"{bot_config.display_name} Bot",
                system_version="GAVATCore Master v1.0",
                app_version="1.0.0"
            )
            
            # Client'ı başlat
            await client.start()
            
            # Bot bilgilerini al
            me = await client.get_me()
            bot_config.client = client
            bot_config.user_id = me.id
            bot_config.username = me.username or bot_name
            bot_config.status = "running"
            bot_config.start_time = datetime.now()
            
            # Event handler'ları kur
            await self._setup_handlers(client, bot_name, persona)
            
            self.status.bots_running += 1
            
            logger.info(f"✅ {bot_config.display_name} başlatıldı - @{bot_config.username}")
            return True
            
        except Exception as e:
            logger.error(f"❌ {bot_name} başlatma hatası: {e}")
            self.bot_configs[bot_name].status = "error"
            return False
    
    async def _setup_handlers(self, client: TelegramClient, bot_name: str, persona: Dict):
        """Event handler'ları kur"""
        
        @client.on(events.NewMessage(incoming=True))
        async def message_handler(event):
            try:
                # Kendi mesajlarını ignore et
                me = await client.get_me()
                if event.sender_id == me.id:
                    return
                
                sender = await event.get_sender()
                if not sender:
                    return
                
                # DM mesajları
                if event.is_private:
                    await self._handle_dm(event, sender, bot_name)
                
                # Grup mesajları
                elif event.is_group:
                    await self._handle_group_message(event, bot_name)
                    
            except Exception as e:
                logger.error(f"❌ {bot_name} mesaj handler hatası: {e}")
        
        logger.info(f"📡 {bot_name} event handler'ları kuruldu")
    
    async def _handle_dm(self, event, sender, bot_name: str):
        """DM mesajlarını işle"""
        try:
            user_name = sender.first_name or "Kullanıcı"
            message = event.raw_text
            
            logger.info(f"💬 {bot_name.upper()} DM: {user_name} -> {message[:50]}...")
            
            # Bot-specific handler'ları çağır
            if bot_name == "yayincilara":
                await self._handle_lara_dm(event, sender)
            elif bot_name == "xxxgeisha":
                await self._handle_geisha_dm(event, sender)
            elif bot_name == "gawatbaba":
                await self._handle_gawat_dm(event, sender)
            
        except Exception as e:
            logger.error(f"❌ {bot_name} DM handler hatası: {e}")
    
    async def _handle_group_message(self, event, bot_name: str):
        """Grup mesajlarını işle"""
        try:
            # Mention veya reply kontrolü
            if event.mentioned or event.is_reply:
                logger.info(f"🏟️ {bot_name.upper()} grup mesajı - mention/reply")
                
                # Bot-specific group handler'ları
                if bot_name == "yayincilara":
                    await self._handle_lara_group(event)
                elif bot_name == "xxxgeisha":
                    await self._handle_geisha_group(event)
                elif bot_name == "gawatbaba":
                    await self._handle_gawat_group(event)
            
        except Exception as e:
            logger.error(f"❌ {bot_name} grup handler hatası: {e}")
    
    # Bot-specific handler methods (placeholder implementations)
    async def _handle_lara_dm(self, event, sender):
        """Lara DM handler"""
        try:
            # Import real handler if available
            from services.telegram.lara_bot_handler import handle_lara_dm
            await handle_lara_dm(event, sender, self.bot_configs["yayincilara"].client, "yayincilara")
        except ImportError:
            # Fallback response
            await event.respond("💕 Merhaba canım! Lara burada... Biraz sabret sistemde güncelleme var!")
    
    async def _handle_geisha_dm(self, event, sender):
        """Geisha DM handler"""
        try:
            from services.telegram.geisha_handler import handle_geisha_dm
            await handle_geisha_dm(event, sender, self.bot_configs["xxxgeisha"].client, "xxxgeisha")
        except ImportError:
            await event.respond("🌸 Konnichiwa! Geisha şu an meditasyonda... Biraz sonra gel 💋")
    
    async def _handle_gawat_dm(self, event, sender):
        """Gawat DM handler"""
        try:
            from services.telegram.gawat_handler import handle_gawat_dm
            await handle_gawat_dm(event, sender, self.bot_configs["gawatbaba"].client, "gawatbaba")
        except ImportError:
            await event.respond("🔥 Evlat! Baba burada... Ne lazım? 💪")
    
    async def _handle_lara_group(self, event):
        """Lara grup handler"""
        try:
            from services.telegram.lara_bot_handler import handle_lara_group_message
            await handle_lara_group_message(event, self.bot_configs["yayincilara"].client, "yayincilara")
        except ImportError:
            await event.respond("🎮 Lara burada! Ne var ne yok? ✨")
    
    async def _handle_geisha_group(self, event):
        """Geisha grup handler"""
        await event.respond("🌸 Ara sıra suskunluk en güzel konuşmadır... 💫")
    
    async def _handle_gawat_group(self, event):
        """Gawat grup handler"""
        await event.respond("🎯 Baba şahit! Ne oluyor burada? 🔥")
    
    async def start_all_bots(self) -> Dict[str, bool]:
        """Tüm bot'ları başlat"""
        logger.info("🚀 Tüm bot'lar başlatılıyor...")
        
        results = {}
        
        for bot_name in self.bot_configs.keys():
            success = await self.start_bot(bot_name)
            results[bot_name] = success
            
            if success:
                logger.info(f"✅ {bot_name} başarıyla başlatıldı!")
            else:
                logger.error(f"❌ {bot_name} başlatılamadı!")
            
            await asyncio.sleep(1)  # Bot'lar arası bekle
        
        return results
    
    def start_monitoring_api(self) -> bool:
        """Monitoring API'sini başlat"""
        try:
            logger.info("🚀 Monitoring API başlatılıyor...")
            
            # gavatcore-api başlat
            api_script = "gavatcore-api/app/main.py"
            if os.path.exists(api_script):
                self.api_process = subprocess.Popen(
                    ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
                    cwd="gavatcore-api",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                time.sleep(3)
                
                if self.api_process.poll() is None:
                    self.status.api_running = True
                    logger.info("✅ GavatCore API başlatıldı (Port 8000)")
                    return True
                else:
                    logger.error("❌ GavatCore API başlatılamadı")
                    return False
            else:
                logger.warning("⚠️ GavatCore API script bulunamadı")
                return False
                
        except Exception as e:
            logger.error(f"❌ API başlatma hatası: {e}")
            return False
    
    async def stop_bot(self, bot_name: str) -> bool:
        """Belirli bir bot'u durdur"""
        try:
            bot_config = self.bot_configs[bot_name]
            
            if bot_config.client:
                await bot_config.client.disconnect()
                bot_config.client = None
                bot_config.status = "stopped"
                self.status.bots_running -= 1
                
                logger.info(f"🔴 {bot_config.display_name} durduruldu")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ {bot_name} durdurma hatası: {e}")
            return False
    
    async def stop_all_bots(self):
        """Tüm bot'ları durdur"""
        logger.info("🔴 Tüm bot'lar durduruluyor...")
        
        for bot_name in list(self.bot_configs.keys()):
            await self.stop_bot(bot_name)
    
    def stop_api(self):
        """API'yi durdur"""
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                self.status.api_running = False
                logger.info("🔴 API durduruldu")
            except:
                self.api_process.kill()
                logger.info("🔪 API zorla durduruldu")
    
    def show_status(self):
        """Sistem durumunu göster"""
        logger.info("📊 Sistem durumu:")
        
        # API durumu
        if self.status.api_running:
            logger.info("✅ GavatCore API: Çalışıyor (Port 8000)")
        else:
            logger.info("❌ GavatCore API: Çalışmıyor")
        
        # Bot durumları
        for bot_name, bot_config in self.bot_configs.items():
            if bot_config.status == "running":
                uptime = datetime.now() - bot_config.start_time if bot_config.start_time else None
                uptime_min = int(uptime.total_seconds() / 60) if uptime else 0
                logger.info(f"✅ {bot_config.display_name}: @{bot_config.username} (Uptime: {uptime_min}min)")
            else:
                logger.info(f"❌ {bot_config.display_name}: {bot_config.status}")
        
        logger.info(f"🎯 Toplam: {self.status.bots_running}/{self.status.bots_total} bot aktif")
        logger.info(f"📈 Success Rate: {self.status.success_rate:.1f}%")
    
    def stop_all(self):
        """Tüm servisleri durdur"""
        logger.info("🔴 Sistem durduruluyor...")
        
        # API'yi durdur
        self.stop_api()
        
        # Bot'lar async olarak durdurulacak
        logger.info("✅ Tüm servisler durdurma komutu verildi")
    
    def setup_signal_handlers(self):
        """Signal handler'ları kur"""
        def signal_handler(signum, frame):
            logger.info(f"🛑 Çıkış sinyali alındı: {signum}")
            self.running = False
            self.stop_all()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run_master_system(self):
        """Master sistem çalıştırma"""
        print(f"""
🔥🔥🔥 GAVATCORE MASTER LAUNCHER 🔥🔥🔥
==========================================
🤖 3 Bot Otomatik Başlatma
🌐 GavatCore API (Port 8000)
💳 Stripe Webhook Entegrasyonu
🎯 Session Yönetimi
==========================================
Başlatma: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """)
        
        try:
            # Signal handlers
            self.setup_signal_handlers()
            
            # 1. Session kontrolü
            if not self.verify_session_files():
                logger.error("❌ Session dosyaları eksik! Lütfen bot'ları önce authorize edin.")
                return False
            
            # 2. API başlat
            api_success = self.start_monitoring_api()
            
            # 3. Tüm bot'ları başlat
            bot_results = await self.start_all_bots()
            success_count = sum(bot_results.values())
            
            # 4. Durum raporu
            await asyncio.sleep(3)
            self.show_status()
            
            print(f"""
🔥 MASTER LAUNCHER BAŞLATMA TAMAMLANDI! 🔥
==========================================
🌐 GavatCore API: http://localhost:8000
📊 Monitoring API: {'✅ Aktif' if api_success else '❌ Pasif'}
🤖 {success_count}/3 bot aktif
🎯 Success Rate: {self.status.success_rate:.1f}%
🌍 Stripe Webhook: http://localhost:8000/api/payment/stripe/webhook
==========================================
Ctrl+C ile tüm sistemi durdur
            """)
            
            # 5. Ana loop - bot'ları çalıştır
            if success_count > 0:
                # Her bot için ayrı task oluştur
                tasks = []
                for bot_name, bot_config in self.bot_configs.items():
                    if bot_config.client and bot_config.status == "running":
                        task = asyncio.create_task(
                            bot_config.client.run_until_disconnected()
                        )
                        tasks.append(task)
                
                # Ana monitoring loop
                monitoring_task = asyncio.create_task(self._monitoring_loop())
                tasks.append(monitoring_task)
                
                # Tüm task'leri bekle
                await asyncio.gather(*tasks, return_exceptions=True)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Master sistem hatası: {e}")
            await self.stop_all_bots()
            self.stop_all()
            return False
    
    async def _monitoring_loop(self):
        """Monitoring döngüsü"""
        while self.running:
            try:
                await asyncio.sleep(300)  # 5 dakikada bir
                
                # Health check
                active_bots = sum(1 for config in self.bot_configs.values() if config.status == "running")
                
                if active_bots != self.status.bots_running:
                    self.status.bots_running = active_bots
                    logger.info(f"📊 Bot durumu güncellendi: {active_bots}/3 aktif")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Monitoring loop hatası: {e}")

# Global instance
master_launcher = GavatCoreMasterLauncher()

async def main():
    """Ana fonksiyon"""
    try:
        success = await master_launcher.run_master_system()
        if not success:
            logger.error("❌ Master sistem başlatılamadı!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Kullanıcı tarafından durduruldu")
        await master_launcher.stop_all_bots()
        master_launcher.stop_all()
    except Exception as e:
        logger.error(f"❌ Kritik hata: {e}")
        await master_launcher.stop_all_bots()
        master_launcher.stop_all()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 