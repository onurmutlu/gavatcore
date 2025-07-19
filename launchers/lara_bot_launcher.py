from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
LARA BOT LAUNCHER - Flörtöz Şovcu AI Sistemi
============================================

Lara karakteri bot'unu başlatır ve çalıştırır.
GAVATCore sistemi üzerinde çalışan özel karakter implementation'ı.

Kullanım:
    python lara_bot_launcher.py

Özellikler:
- Telethon ile Telegram entegrasyonu
- OpenAI ile AI yanıtlar
- Flörtöz karakter davranışları
- VIP hizmet tanıtımları
- Analytics ve monitoring
"""

import asyncio
import os
import signal
import sys
import json
from datetime import datetime
from typing import Optional

# Path setup for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Setup environment
os.environ.setdefault('PYTHONPATH', os.path.dirname(__file__))

# Path setup for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Core imports
from telethon import TelegramClient, events
from telethon.tl.types import User, Chat, Channel
import structlog

# GAVATCore imports
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
# Character Engine V2 handler kullan
try:
    from services.telegram.lara_bot_handler_v2 import handle_lara_dm, handle_lara_group_message, get_lara_stats
    logger = structlog.get_logger("lara_bot_launcher")
    logger.info("✅ Character Engine V2 handler yüklendi")
except ImportError:
    logger = structlog.get_logger("lara_bot_launcher")
    logger.warning("⚠️ V2 handler bulunamadı, V1 kullanılıyor")
    from services.telegram.lara_bot_handler import handle_lara_dm, handle_lara_group_message, get_lara_stats
from utilities.logger import log_event, log_analytics
from core.database_manager import database_manager

logger = structlog.get_logger("lara_bot_launcher")

class LaraBotLauncher:
    """Lara Bot Launcher - Ana kontrol sınıfı"""
    
    def __init__(self):
        self.client: Optional[TelegramClient] = None
        self.is_running = False
        self.bot_username = "lara_bot"  # Default, gerçek username login'de alınır
        
    async def initialize(self):
        """Bot'u başlat ve yapılandır"""
        try:
            logger.info("🌹 Lara Bot başlatılıyor...")
            
            # Persona dosyasından telefon numarasını al
            persona_file = "data/personas/yayincilara.json"
            if os.path.exists(persona_file):
                with open(persona_file, 'r', encoding='utf-8') as f:
                    persona = json.load(f)
                phone = persona.get('phone', '+905382617727')
                clean_phone = phone.replace('+', '')
                session_file = f"sessions/_{clean_phone}"
                logger.info(f"📱 Persona telefon: {phone} -> Session: {session_file}")
            else:
                session_file = "sessions/_905382617727"
                logger.info(f"📱 Default session kullanılıyor: {session_file}")
            
            os.makedirs("sessions", exist_ok=True)
            
            self.client = TelegramClient(
                session_file,
                TELEGRAM_API_ID,
                TELEGRAM_API_HASH,
                device_model="Lara Bot v2.0",
                system_version="GAVATCore",
                app_version="2.0.1"
            )
            
            # Bot'u başlat (session kullanarak - telefon sormaz!)
            await self.client.start()
            
            # Bot bilgilerini al
            me = await self.client.get_me()
            self.bot_username = me.username or "lara_bot"
            
            logger.info(f"✅ Lara Bot giriş yapıldı: @{self.bot_username} (ID: {me.id})")
            
            # Event handler'ları kur
            await self._setup_handlers()
            
            # Database bağlantısını başlat
            await database_manager.initialize()
            
            logger.info("🔥 Lara Bot hazır - mesajları dinliyor...")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Lara Bot başlatma hatası: {e}")
            return False
    
    async def _setup_handlers(self):
        """Event handler'ları kur"""
        
        @self.client.on(events.NewMessage(incoming=True))
        async def message_handler(event):
            """Gelen mesajları işle"""
            try:
                # Kendi mesajlarını ignore et
                me = await self.client.get_me()
                if event.sender_id == me.id:
                    return
                
                sender = await event.get_sender()
                if not sender:
                    return
                
                # DM mesajları
                if event.is_private and isinstance(sender, User):
                    await self._handle_dm(event, sender)
                
                # Grup mesajları (mention/reply)
                elif event.is_group:
                    await self._handle_group_message(event)
                    
            except Exception as e:
                logger.error(f"❌ Mesaj handler hatası: {e}")
        
        logger.info("📡 Event handler'lar kuruldu")
    
    async def _handle_dm(self, event, sender):
        """DM mesajlarını işle"""
        try:
            message_text = event.raw_text or ""
            
            # Bot kontrolü
            if hasattr(sender, 'bot') and sender.bot:
                return
            
            logger.info(f"💬 Lara DM alındı: {sender.first_name} -> {message_text[:50]}...")
            
            # Lara handler'ına yönlendir
            success = await handle_lara_dm(self.client, sender, message_text)
            
            if success:
                log_analytics("lara_bot", "dm_handled", {
                    "user_id": sender.id,
                    "user_name": sender.first_name,
                    "message_length": len(message_text)
                })
            
        except Exception as e:
            logger.error(f"❌ DM işleme hatası: {e}")
    
    async def _handle_group_message(self, event):
        """Grup mesajlarını işle"""
        try:
            # Sadece mention/reply'larda çalış
            sender = await event.get_sender()
            if not sender:
                return
            
            # Bot kontrolü
            if hasattr(sender, 'bot') and sender.bot:
                return
            
            # Lara mention kontrolü
            if not (event.is_reply or f"@{self.bot_username}" in event.raw_text.lower()):
                return
            
            logger.info(f"👥 Lara grup mention: {sender.first_name} -> {event.raw_text[:50]}...")
            
            # Lara handler'ına yönlendir
            success = await handle_lara_group_message(self.client, event, self.bot_username)
            
            if success:
                log_analytics("lara_bot", "group_mention_handled", {
                    "chat_id": event.chat_id,
                    "user_id": sender.id,
                    "user_name": sender.first_name
                })
            
        except Exception as e:
            logger.error(f"❌ Grup mesajı işleme hatası: {e}")
    
    async def run(self):
        """Bot'u çalıştır"""
        try:
            self.is_running = True
            
            # İstatistik gösterme
            await self._show_startup_stats()
            
            # Ana loop
            logger.info("🌹 Lara Bot çalışıyor - Ctrl+C ile durdurun")
            await self.client.run_until_disconnected()
            
        except KeyboardInterrupt:
            logger.info("⏹️ Kullanıcı tarafından durduruldu")
        except Exception as e:
            logger.error(f"❌ Bot çalışma hatası: {e}")
        finally:
            await self.cleanup()
    
    async def _show_startup_stats(self):
        """Başlangıç istatistiklerini göster"""
        try:
            stats = get_lara_stats()
            
            logger.info("📊 Lara Bot İstatistikleri:")
            logger.info(f"   👥 Toplam konuşma: {stats['total_conversations']}")
            logger.info(f"   🔥 Aktif konuşma: {stats['active_conversations']}")
            logger.info(f"   💎 Yüksek ilgi: {stats['high_interest_users']}")
            logger.info(f"   💳 Ödeme sorgusu: {stats['payment_inquiries']}")
            logger.info(f"   💬 Ortalama mesaj: {stats.get('average_message_count', 0):.1f}")
            
        except Exception as e:
            logger.warning(f"⚠️ İstatistik gösterme hatası: {e}")
    
    async def cleanup(self):
        """Temizleme işlemleri"""
        try:
            self.is_running = False
            
            if self.client:
                await self.client.disconnect()
                logger.info("🔌 Telegram bağlantısı kapatıldı")
            
            # Final stats
            stats = get_lara_stats()
            log_analytics("lara_bot", "shutdown", {
                "total_conversations": stats.get("total_conversations", 0),
                "uptime_minutes": "unknown"
            })
            
            logger.info("👋 Lara Bot kapandı")
            
        except Exception as e:
            logger.error(f"❌ Cleanup hatası: {e}")

# ==================== MAIN FUNCTION ====================

async def main():
    """Ana fonksiyon"""
    print("🌹" + "="*50)
    print("   LARA BOT - Flörtöz Şovcu AI Sistemi")
    print("   GAVATCore AI Infrastructure")
    print(f"   Başlatma zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*52)
    
    # Launcher oluştur
    launcher = LaraBotLauncher()
    
    # Signal handler'lar (graceful shutdown)
    def signal_handler(sig, frame):
        logger.info("🛑 Shutdown sinyali alındı...")
        if launcher.is_running:
            asyncio.create_task(launcher.cleanup())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Bot'u başlat
        if await launcher.initialize():
            # Bot'u çalıştır
            await launcher.run()
        else:
            logger.error("❌ Bot başlatılamadı")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"💥 Kritik hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Lara Bot kapatıldı!")
    except Exception as e:
        print(f"💥 Fatal hata: {e}")
        sys.exit(1) 