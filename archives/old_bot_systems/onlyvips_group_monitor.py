from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🔥🔥🔥 ONLYVIPS GROUP MONITOR 🔥🔥🔥

💪 GERÇEK TELEGRAM GRUP MESAJLARI - REAL TIME!

Features:
- OnlyVips grubundaki mesajları real-time izleme
- Tüm mesajları console'da gösterme
- User analizi ve profilleme
- BabaGAVAT sokak zekası

🎯 HEDEF: ONLYVIPS GROUP FULL MONITORING!
"""

import asyncio
import sys
import json
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import User, Chat, Channel
import structlog

logger = structlog.get_logger("onlyvips.monitor")

# Config
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

class OnlyVipsGroupMonitor:
    """🔥 OnlyVips Grup Monitörü - Real Time Message Tracking"""
    
    def __init__(self):
        self.client = None
        self.is_running = False
        self.onlyvips_group_id = None
        self.session_name = "sessions/onlyvips_monitor"
        
        print("""
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
🔥                                                               🔥
🔥          👁️ ONLYVIPS GROUP MONITOR 👁️                       🔥
🔥                                                               🔥
🔥               📡 REAL TIME MESSAGE TRACKING 📡               🔥
🔥                    💪 ONUR METODU MONITORING! 💪              🔥
🔥                                                               🔥
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥

🎯 HEDEF: ONLYVIPS GRUBUNDAKI TÜM MESAJLARI GÖRMEK!
💰 YAŞASIN SPONSORLAR! REAL TIME! 💰
        """)
    
    async def initialize(self):
        """🚀 Telegram client'ı başlat"""
        try:
            print("🚀 OnlyVips Monitor başlatılıyor...")
            
            # Sessions klasörünü oluştur
            import os
            os.makedirs("sessions", exist_ok=True)
            
            # Telegram client oluştur
            self.client = TelegramClient(
                self.session_name,
                TELEGRAM_API_ID,
                TELEGRAM_API_HASH
            )
            
            print("📡 Telegram'a bağlanıyor...")
            await self.client.start()
            
            # Bot bilgilerini al
            me = await self.client.get_me()
            print(f"✅ Bağlantı başarılı: @{me.username} (ID: {me.id})")
            
            # OnlyVips grubunu bul
            await self._find_onlyvips_group()
            
            # Event handler'ları kur
            await self._setup_event_handlers()
            
            self.is_running = True
            print("✅ OnlyVips Monitor hazır! Real-time mesaj izleme başladı! 👁️")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Monitor initialization error: {e}")
            return False
    
    async def _find_onlyvips_group(self):
        """🔍 OnlyVips grubunu bul"""
        try:
            print("🔍 OnlyVips grubunu arıyor...")
            
            # Tüm dialogları tara
            async for dialog in self.client.iter_dialogs():
                group_name = dialog.name.lower() if dialog.name else ""
                
                # OnlyVips grubunu ara
                if any(keyword in group_name for keyword in ["onlyvips", "only vips", "vip", "gavat"]):
                    self.onlyvips_group_id = dialog.id
                    print(f"✅ OnlyVips grubu bulundu: {dialog.name} (ID: {dialog.id})")
                    print(f"   📊 Grup tipi: {type(dialog.entity).__name__}")
                    print(f"   👥 Üye sayısı: {getattr(dialog.entity, 'participants_count', 'Bilinmiyor')}")
                    return
            
            print("⚠️ OnlyVips grubu bulunamadı!")
            print("📋 Mevcut gruplar:")
            async for dialog in self.client.iter_dialogs():
                if dialog.is_group or dialog.is_channel:
                    print(f"   📱 {dialog.name} (ID: {dialog.id})")
            
        except Exception as e:
            logger.error(f"❌ Group search error: {e}")
    
    async def _setup_event_handlers(self):
        """📡 Event handler'ları kur"""
        try:
            @self.client.on(events.NewMessage)
            async def handle_new_message(event):
                """💬 Yeni mesaj handler'ı"""
                try:
                    # Sadece OnlyVips grubundaki mesajları işle
                    if self.onlyvips_group_id and event.chat_id == self.onlyvips_group_id:
                        await self._process_onlyvips_message(event)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Message handler error: {e}")
            
            print("✅ Event handlers kuruldu!")
            
        except Exception as e:
            logger.error(f"❌ Event handler setup error: {e}")
    
    async def _process_onlyvips_message(self, event):
        """💬 OnlyVips mesajını işle"""
        try:
            # Mesaj bilgileri
            message_text = event.text or ""
            message_time = datetime.now().strftime("%H:%M:%S")
            
            # Gönderen bilgileri
            sender = await event.get_sender()
            if isinstance(sender, User):
                sender_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
                sender_username = f"@{sender.username}" if sender.username else "Kullanıcı adı yok"
                sender_id = sender.id
            else:
                sender_name = "Bilinmeyen Gönderen"
                sender_username = ""
                sender_id = "unknown"
            
            # Chat bilgileri
            chat = await event.get_chat()
            chat_name = getattr(chat, 'title', 'OnlyVips')
            
            # Real-time konsol çıktısı
            print(f"""
🔥🔥🔥 ONLYVIPS MESAJ! 🔥🔥🔥
⏰ Zaman: {message_time}
👤 Gönderen: {sender_name} ({sender_username})
🆔 User ID: {sender_id}
📱 Grup: {chat_name}
💬 Mesaj: {message_text}
════════════════════════════════════════════════════
            """)
            
            # JSON format log
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "chat_name": chat_name,
                "chat_id": event.chat_id,
                "sender_name": sender_name,
                "sender_username": sender_username,
                "sender_id": sender_id,
                "message_text": message_text,
                "message_id": event.id
            }
            
            logger.info(f"📱 OnlyVips Message: {json.dumps(log_data, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"❌ Message processing error: {e}")
    
    async def run_monitor(self):
        """🚀 Monitörü çalıştır"""
        try:
            print("🚀 OnlyVips Real-Time Monitor başladı!")
            print("💬 Grup mesajları için bekliyor...")
            print("🛑 Durdurmak için Ctrl+C kullanın")
            
            # Sürekli dinle
            while self.is_running:
                try:
                    await asyncio.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Kullanıcı tarafından durduruldu")
                    break
                    
        except Exception as e:
            logger.error(f"❌ Monitor run error: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """🛑 Monitörü kapat"""
        try:
            print("\n🛑 OnlyVips Monitor kapatılıyor...")
            
            self.is_running = False
            
            if self.client:
                await self.client.disconnect()
                print("✅ Telegram bağlantısı kapatıldı")
            
            print("✅ OnlyVips Monitor kapatıldı!")
            
        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")

async def main():
    """🚀 Ana fonksiyon"""
    try:
        # Monitor oluştur
        monitor = OnlyVipsGroupMonitor()
        
        # Başlat
        if await monitor.initialize():
            # Çalıştır
            await monitor.run_monitor()
        else:
            print("❌ Monitor başlatılamadı")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"❌ Main error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Logging setup
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'onlyvips_monitor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )
    
    # Çalıştır
    asyncio.run(main()) 