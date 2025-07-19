from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🔥 AUTO-SESSION BOT LAUNCHER 🔥
==============================

Persona JSON dosyalarından telefon numaralarını alır,
mevcut session'ları kullanarak bot'ları otomatik başlatır.
Telefon numarası sormaz - direkt çalışır!
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
import structlog

# GAVATCore imports
from telethon import TelegramClient, events
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
from services.telegram.lara_bot_handler import handle_lara_dm, handle_lara_group_message
from services.telegram.babagavat_handler import handle_babagavat_dm, handle_babagavat_group_message
from services.telegram.geisha_handler import handle_geisha_dm, handle_geisha_group_message
from utilities.logger import log_event, log_analytics

logger = structlog.get_logger("auto_session_launcher")

class AutoSessionBotLauncher:
    """Otomatik session kullanarak bot'ları başlatır"""
    
    def __init__(self):
        self.personas = {}
        self.clients = {}
        self.running_bots = {}
        
    def load_persona_data(self, bot_name: str) -> Optional[Dict]:
        """Persona JSON dosyasından bot bilgilerini yükle"""
        persona_file = f"data/personas/{bot_name}.json"
        
        if not os.path.exists(persona_file):
            logger.error(f"❌ Persona dosyası bulunamadı: {persona_file}")
            return None
        
        try:
            with open(persona_file, 'r', encoding='utf-8') as f:
                persona_data = json.load(f)
            
            logger.info(f"✅ {bot_name} persona verisi yüklendi")
            return persona_data
            
        except Exception as e:
            logger.error(f"❌ {bot_name} persona yükleme hatası: {e}")
            return None
    
    def get_session_path(self, phone: str) -> str:
        """Telefon numarasından session dosya yolunu oluştur"""
        # +905513272355 -> _905513272355.session
        clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
        session_path = f"sessions/_{clean_phone}.session"
        return session_path
    
    async def start_bot(self, bot_name: str) -> bool:
        """Belirli bir bot'u başlat"""
        try:
            print(f"\n🚀 {bot_name.upper()} BOT BAŞLATILIYOR...")
            print("=" * 50)
            
            # 1. Persona verilerini yükle
            persona = self.load_persona_data(bot_name)
            if not persona:
                print(f"❌ {bot_name} persona yüklenemedi")
                return False
            
            phone = persona.get('phone')
            username = persona.get('username', bot_name)
            
            if not phone:
                print(f"❌ {bot_name} için telefon numarası bulunamadı")
                return False
            
            print(f"📱 Telefon: {phone}")
            print(f"👤 Username: {username}")
            
            # 2. Session dosyasını kontrol et
            session_path = self.get_session_path(phone)
            if not os.path.exists(session_path):
                print(f"❌ Session dosyası bulunamadı: {session_path}")
                return False
            
            session_size = os.path.getsize(session_path) / 1024  # KB
            print(f"💾 Session: {session_path} ({session_size:.1f}KB)")
            
            if session_size < 10:  # 10KB'den küçükse problem var
                print(f"⚠️ Session dosyası çok küçük, problem olabilir")
            
            # 3. Telegram client oluştur
            session_name = session_path.replace('.session', '')
            
            client = TelegramClient(
                session_name,
                TELEGRAM_API_ID,
                TELEGRAM_API_HASH,
                device_model=f"{bot_name.upper()} Bot",
                system_version="1.0",
                app_version="GAVATCore v2.0"
            )
            
            print(f"🔗 Telegram'a bağlanıyor...")
            
            # 4. Client'ı başlat (session kullanarak - telefon sormaz)
            await client.start()
            
            # 5. Bot bilgilerini al
            me = await client.get_me()
            actual_username = me.username or username
            
            print(f"✅ Giriş başarılı!")
            print(f"   User ID: {me.id}")
            print(f"   Username: @{actual_username}")
            print(f"   İsim: {me.first_name}")
            
            # 6. Event handler'ları kur
            await self._setup_handlers(client, bot_name, actual_username)
            
            # 7. Client'ı kaydet
            self.clients[bot_name] = client
            self.personas[bot_name] = persona
            self.running_bots[bot_name] = {
                "client": client,
                "username": actual_username,
                "phone": phone,
                "user_id": me.id,
                "start_time": datetime.now(),
                "status": "running"
            }
            
            print(f"🔥 {bot_name.upper()} bot aktif - mesajları dinliyor!")
            return True
            
        except Exception as e:
            print(f"❌ {bot_name} başlatma hatası: {e}")
            logger.error(f"{bot_name} başlatma hatası", error=str(e))
            return False
    
    async def _setup_handlers(self, client: TelegramClient, bot_name: str, username: str):
        """Bot'a özel event handler'ları kur"""
        
        @client.on(events.NewMessage(incoming=True))
        async def message_handler(event):
            """Gelen mesajları bot'a göre yönlendir"""
            try:
                # Kendi mesajlarını ignore et
                me = await client.get_me()
                if event.sender_id == me.id:
                    return
                
                sender = await event.get_sender()
                if not sender:
                    return
                
                # Bot kontrolü
                if hasattr(sender, 'bot') and sender.bot:
                    return
                
                message_text = event.raw_text or ""
                
                # DM mesajları
                if event.is_private:
                    await self._handle_dm(bot_name, client, event, sender, message_text)
                
                # Grup mesajları (mention/reply)
                elif event.is_group:
                    await self._handle_group_message(bot_name, client, event, username)
                    
            except Exception as e:
                logger.error(f"{bot_name} mesaj handler hatası", error=str(e))
        
        logger.info(f"📡 {bot_name} event handler'ları kuruldu")
    
    async def _handle_dm(self, bot_name: str, client: TelegramClient, event, sender, message_text: str):
        """DM mesajlarını bot'a göre yönlendir"""
        try:
            logger.info(f"💬 {bot_name} DM alındı: {sender.first_name} -> {message_text[:50]}...")
            
            success = False
            
            if bot_name == "babagavat":
                success = await handle_babagavat_dm(client, sender, message_text)
            elif bot_name == "yayincilara":
                success = await handle_lara_dm(client, sender, message_text)
            elif bot_name == "xxxgeisha":
                success = await handle_geisha_dm(client, sender, message_text)
            else:
                logger.warning(f"⚠️ {bot_name} için handler bulunamadı")
                return
            
            if success:
                log_analytics(f"{bot_name}_bot", "dm_handled", {
                    "user_id": sender.id,
                    "user_name": sender.first_name,
                    "message_length": len(message_text)
                })
            
        except Exception as e:
            logger.error(f"❌ {bot_name} DM işleme hatası", error=str(e))
    
    async def _handle_group_message(self, bot_name: str, client: TelegramClient, event, username: str):
        """Grup mesajlarını bot'a göre yönlendir"""
        try:
            sender = await event.get_sender()
            if not sender:
                return
            
            # Bot kontrolü
            if hasattr(sender, 'bot') and sender.bot:
                return
            
            # Mention kontrolü
            if not (event.is_reply or f"@{username}" in event.raw_text.lower()):
                return
            
            logger.info(f"👥 {bot_name} grup mention: {sender.first_name} -> {event.raw_text[:50]}...")
            
            success = False
            
            if bot_name == "babagavat":
                success = await handle_babagavat_group_message(client, event, username)
            elif bot_name == "yayincilara":
                success = await handle_lara_group_message(client, event, username)
            elif bot_name == "xxxgeisha":
                success = await handle_geisha_group_message(client, event, username)
            else:
                logger.warning(f"⚠️ {bot_name} için grup handler bulunamadı")
                return
            
            if success:
                log_analytics(f"{bot_name}_bot", "group_mention_handled", {
                    "chat_id": event.chat_id,
                    "user_id": sender.id,
                    "user_name": sender.first_name
                })
            
        except Exception as e:
            logger.error(f"❌ {bot_name} grup mesajı işleme hatası", error=str(e))
    
    async def start_all_bots(self) -> Dict[str, bool]:
        """Tüm bot'ları başlat"""
        bot_names = ["babagavat", "yayincilara", "xxxgeisha"]
        results = {}
        
        print(f"""
🚀 AUTO-SESSION BOT LAUNCHER BAŞLADI!
=====================================
📱 Telefon numaraları persona JSON'larından alınıyor
💾 Mevcut session'lar kullanılıyor
🤖 3 bot başlatılacak: {', '.join(bot_names)}
=====================================
        """)
        
        for bot_name in bot_names:
            print(f"\n⏳ {bot_name} başlatılıyor...")
            success = await self.start_bot(bot_name)
            results[bot_name] = success
            
            if success:
                print(f"✅ {bot_name} başarıyla başlatıldı!")
            else:
                print(f"❌ {bot_name} başlatılamadı!")
        
        return results
    
    async def stop_bot(self, bot_name: str) -> bool:
        """Belirli bir bot'u durdur"""
        if bot_name not in self.clients:
            print(f"❌ {bot_name} çalışmıyor")
            return False
        
        try:
            await self.clients[bot_name].disconnect()
            del self.clients[bot_name]
            del self.running_bots[bot_name]
            print(f"🔴 {bot_name} durduruldu")
            return True
            
        except Exception as e:
            print(f"❌ {bot_name} durdurma hatası: {e}")
            return False
    
    async def stop_all_bots(self):
        """Tüm bot'ları durdur"""
        for bot_name in list(self.clients.keys()):
            await self.stop_bot(bot_name)
    
    def get_status(self) -> Dict:
        """Bot durumlarını al"""
        status = {
            "running_bots": len(self.running_bots),
            "bots": {}
        }
        
        for bot_name, bot_info in self.running_bots.items():
            uptime = datetime.now() - bot_info["start_time"]
            status["bots"][bot_name] = {
                "username": bot_info["username"],
                "phone": bot_info["phone"],
                "user_id": bot_info["user_id"],
                "uptime_minutes": int(uptime.total_seconds() / 60),
                "status": bot_info["status"]
            }
        
        return status
    
    async def run_forever(self):
        """Bot'ları sürekli çalıştır"""
        try:
            print("\n🔄 Bot'lar sürekli çalışma modunda...")
            print("Ctrl+C ile durdurun")
            
            # Her bot için ayrı task oluştur
            tasks = []
            for bot_name, client in self.clients.items():
                task = asyncio.create_task(client.run_until_disconnected())
                tasks.append(task)
            
            # Tüm task'leri bekle
            await asyncio.gather(*tasks)
            
        except KeyboardInterrupt:
            print("\n⏹️ Kullanıcı tarafından durduruldu")
            await self.stop_all_bots()
        except Exception as e:
            print(f"\n❌ Runtime hatası: {e}")
            await self.stop_all_bots()

# Global instance
auto_launcher = AutoSessionBotLauncher()

async def main():
    """Ana fonksiyon"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            if len(sys.argv) > 2:
                # Tek bot başlat
                bot_name = sys.argv[2]
                success = await auto_launcher.start_bot(bot_name)
                if success:
                    await auto_launcher.run_forever()
            else:
                # Tüm bot'ları başlat
                results = await auto_launcher.start_all_bots()
                success_count = sum(results.values())
                
                print(f"\n🎯 BAŞLATMA SONUCU: {success_count}/3 bot başarılı")
                
                if success_count > 0:
                    await auto_launcher.run_forever()
        
        elif command == "status":
            status = auto_launcher.get_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))
        
        elif command == "stop":
            await auto_launcher.stop_all_bots()
            print("🔴 Tüm bot'lar durduruldu")
        
        else:
            print("Kullanım: python3 auto_session_bot_launcher.py [start|status|stop] [bot_name]")
    
    else:
        print("""
🚀 AUTO-SESSION BOT LAUNCHER
===========================

Komutlar:
  python3 auto_session_bot_launcher.py start           # Tüm bot'ları başlat
  python3 auto_session_bot_launcher.py start lara      # Sadece lara'yı başlat
  python3 auto_session_bot_launcher.py status          # Durumları göster
  python3 auto_session_bot_launcher.py stop            # Tüm bot'ları durdur

Özellikler:
  ✅ Persona JSON'larından telefon numaraları alır
  ✅ Mevcut session'ları kullanır (telefon sormaz)
  ✅ Gerçek Telegram bot'ları çalıştırır
  ✅ Her bot için özel handler'lar
        """)

if __name__ == "__main__":
    asyncio.run(main()) 