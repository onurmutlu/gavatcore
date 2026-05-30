from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🧠 Smart Multi-Bot Launcher v2.0 🧠

✅ Session'ları otomatik bulur
✅ Kod sormaz (session varsa)
✅ Akıllı spam kontrolü
✅ DM'lere anında cevap
✅ Gruplarda natural davranış

xxxgeisha, yayincilara, babagavat botlarını birden çalıştırır.
"""

import asyncio
import json
import os
import time
import random
import logging
from typing import Dict, List, Optional, Any
from telethon import TelegramClient, events
from telethon.tl.types import User, Chat, Channel
from telethon.errors import SessionPasswordNeededError

# Config import
from config import API_ID, API_HASH

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SmartBotInstance:
    """Akıllı bot instance - session'ları otomatik yönetir"""
    
    def __init__(self, bot_config: Dict[str, Any]):
        self.username = bot_config["username"]
        self.display_name = bot_config["display_name"]
        self.phone = bot_config["phone"]
        self.persona_path = bot_config.get("persona_path")
        
        # Session paths to try
        self.session_paths = [
            f"sessions/{self.username}_conversation.session",
            f"sessions/{self.username}.session",
            f"sessions/_{self.phone.replace('+', '')}.session"
        ]
        
        self.client: Optional[TelegramClient] = None
        self.active_session_path = None
        
        # Spam control
        self.last_group_message = {}  # chat_id -> timestamp
        self.message_cooldowns = {}   # chat_id -> cooldown_until
        self.daily_message_count = {} # chat_id -> count
        
        # Personality settings
        self.load_personality()
        
        logger.info(f"🤖 {self.display_name} bot instance hazırlandı")
    
    def load_personality(self):
        """Persona dosyasından kişilik ayarlarını yükler"""
        
        if self.persona_path and os.path.exists(self.persona_path):
            try:
                with open(self.persona_path, 'r', encoding='utf-8') as f:
                    persona = json.load(f)
                    
                self.reply_probability = 0.15  # %15 grup mesajlarına cevap
                self.cooldown_minutes = 5      # Minimum 5 dakika bekleme
                self.max_daily_messages = 20   # Günde max 20 mesaj per grup
                
                logger.info(f"📖 {self.display_name} persona yüklendi")
            except Exception as e:
                logger.warning(f"⚠️ {self.display_name} persona hatası: {e}")
                self.set_default_personality()
        else:
            self.set_default_personality()
    
    def set_default_personality(self):
        """Varsayılan kişilik ayarları"""
        self.reply_probability = 0.1   # %10 daha az agresif
        self.cooldown_minutes = 10     # 10 dakika bekleme
        self.max_daily_messages = 15   # Günde max 15 mesaj
    
    def find_existing_session(self) -> Optional[str]:
        """Mevcut session dosyasını bulur"""
        for session_path in self.session_paths:
            if os.path.exists(session_path):
                logger.info(f"📁 {self.display_name} session bulundu: {session_path}")
                return session_path
        return None
    
    async def connect(self) -> bool:
        """Telegram'a akıllı bağlantı"""
        try:
            # Önce mevcut session'ı dene
            existing_session = self.find_existing_session()
            
            if existing_session:
                session_name = existing_session.replace('.session', '')
                self.client = TelegramClient(session_name, API_ID, API_HASH)
                self.active_session_path = existing_session
            else:
                # Yeni session oluştur
                session_name = f"sessions/{self.username}_conversation"
                self.client = TelegramClient(session_name, API_ID, API_HASH)
                logger.warning(f"⚠️ {self.display_name} yeni session oluşturuluyor...")
            
            # Bağlan
            try:
                if existing_session:
                    # Session varsa kod sorma
                    await self.client.start()
                else:
                    # Yeni session için telefon gerekli
                    await self.client.start(phone=self.phone)
                
                # Bağlantıyı doğrula
                me = await self.client.get_me()
                logger.info(f"✅ {self.display_name} bağlandı! @{me.username} (ID: {me.id})")
                
                # Event handler'ları kur
                self.setup_handlers()
                return True
                
            except SessionPasswordNeededError:
                logger.error(f"❌ {self.display_name} 2FA gerekli!")
                return False
            except Exception as e:
                logger.error(f"❌ {self.display_name} bağlantı hatası: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ {self.display_name} genel hata: {e}")
            return False
    
    def setup_handlers(self):
        """Event handler'ları kur"""
        
        @self.client.on(events.NewMessage(incoming=True))
        async def handle_message(event):
            try:
                sender = await event.get_sender()
                if not sender:
                    return
                
                # Kendi mesajlarını ignore et
                me = await self.client.get_me()
                if sender.id == me.id:
                    return
                
                chat = await event.get_chat()
                is_private = isinstance(sender, User) and event.is_private
                is_group = isinstance(chat, (Chat, Channel)) and not event.is_private
                
                if is_private:
                    await self.handle_private_message(event, sender)
                elif is_group:
                    await self.handle_group_message(event, sender, chat)
                    
            except Exception as e:
                logger.error(f"❌ {self.display_name} mesaj handler hatası: {e}")
    
    async def handle_private_message(self, event, sender):
        """DM mesajlarını işle"""
        message = event.message.message
        
        logger.info(f"💬 {self.display_name} DM: {sender.username or sender.id} -> {message[:30]}...")
        
        # Doğal gecikme
        await asyncio.sleep(random.uniform(1, 3))
        
        # Bot-specific responses
        response = self.get_dm_response()
        
        try:
            await event.reply(response)
            logger.info(f"✅ {self.display_name} DM yanıtı: {response}")
        except Exception as e:
            logger.error(f"❌ {self.display_name} DM yanıt hatası: {e}")
    
    async def handle_group_message(self, event, sender, chat):
        """Grup mesajlarını akıllı işle"""
        
        chat_id = chat.id
        current_time = time.time()
        
        # Cooldown kontrolü
        if chat_id in self.message_cooldowns:
            if current_time < self.message_cooldowns[chat_id]:
                return  # Hala cooldown'da
        
        # Günlük mesaj limiti
        today = time.strftime("%Y-%m-%d")
        daily_key = f"{chat_id}_{today}"
        
        if daily_key not in self.daily_message_count:
            self.daily_message_count[daily_key] = 0
        
        if self.daily_message_count[daily_key] >= self.max_daily_messages:
            return  # Günlük limit doldu
        
        # Son mesajdan ne kadar zaman geçti?
        if chat_id in self.last_group_message:
            time_since_last = current_time - self.last_group_message[chat_id]
            if time_since_last < (self.cooldown_minutes * 60):
                return  # Çok erken
        
        # Mesaj analizi
        message = event.message.message.lower()
        should_reply = self.should_reply_to_message(message)
        
        if should_reply:
            await self.send_group_reply(event, chat_id, current_time)
    
    def should_reply_to_message(self, message: str) -> bool:
        """Mesaja cevap verilip verilmeyeceğini belirle"""
        
        # Bot'a mention
        if f"@{self.username}" in message or self.username.lower() in message:
            return True
        
        # Trigger kelimeler
        triggers = ["selam", "merhaba", "hey", "nasıl", "naber", "selamlar"]
        if any(trigger in message for trigger in triggers):
            return random.random() < 0.6  # %60 şans
        
        # Rastgele cevap
        return random.random() < self.reply_probability
    
    async def send_group_reply(self, event, chat_id, current_time):
        """Gruba cevap gönder"""
        
        # Doğal gecikme
        delay = random.uniform(2, 8)
        await asyncio.sleep(delay)
        
        response = self.get_group_response()
        
        try:
            await event.reply(response)
            
            # Spam kontrolü güncelle
            self.last_group_message[chat_id] = current_time
            self.message_cooldowns[chat_id] = current_time + (self.cooldown_minutes * 60)
            
            # Günlük sayaç güncelle
            today = time.strftime("%Y-%m-%d")
            daily_key = f"{chat_id}_{today}"
            self.daily_message_count[daily_key] += 1
            
            logger.info(f"💬 {self.display_name} grup mesajı gönderdi: {response}")
            
        except Exception as e:
            logger.error(f"❌ {self.display_name} grup mesaj hatası: {e}")
    
    def get_dm_response(self) -> str:
        """DM cevapları"""
        responses = {
            "xxxgeisha": [
                "Merhaba aşkım 😘",
                "Selam bebek, nasılsın? 💕", 
                "Hey canım, ne yapıyorsun? 🌹",
                "Aşkım burada, yazmaya devam et 💋"
            ],
            "yayincilara": [
                "Merhabalar! Nasılsın? 😊",
                "Selam canım! Ne haber? 💕",
                "Hey! Bugün nasıl geçiyor? 🌸",
                "Merhaba! İyi misin? ☀️"
            ],
            "babagavat": [
                "Selam kardeşim! 😎",
                "Ne haber aslanım? 🔥",
                "Selam baba, keyif nasıl? 💪",
                "Hey! Nasıl gidiyor? 🚬"
            ]
        }
        
        bot_responses = responses.get(self.username, ["Selam! 👋"])
        return random.choice(bot_responses)
    
    def get_group_response(self) -> str:
        """Grup cevapları"""
        responses = {
            "xxxgeisha": [
                "😘✨", "💕", "🌹", "Hey 😏", "Merhaba canlar 💋"
            ],
            "yayincilara": [
                "Selam! 😊", "Merhabalar 💕", "Hey nasılsınız? 🌸", "👋✨"
            ],
            "babagavat": [
                "Selam kardeşler 😎", "Ne haber? 🔥", "Keyif nasıl? 💪", "👋"
            ]
        }
        
        bot_responses = responses.get(self.username, ["👋"])
        return random.choice(bot_responses)
    
    async def disconnect(self):
        """Bağlantıyı kes"""
        if self.client:
            await self.client.disconnect()
            logger.info(f"👋 {self.display_name} bağlantısı kesildi")


class SmartMultiBotLauncher:
    """Akıllı multi-bot yöneticisi"""
    
    def __init__(self):
        self.bots: Dict[str, SmartBotInstance] = {}
        self.active_bots: List[str] = []
        
        # Bot konfigürasyonları
        self.bot_configs = [
            {
                "username": "xxxgeisha",
                "display_name": "Geisha",
                "phone": "+905486306226",
                "persona_path": "data/personas/xxxgeisha.json"
            },
            {
                "username": "yayincilara", 
                "display_name": "Lara",
                "phone": "+905382617727",
                "persona_path": "data/personas/yayincilara.json"
            },
            {
                "username": "babagavat",
                "display_name": "Gavat Baba", 
                "phone": "+905513272355",
                "persona_path": "data/personas/babagavat.json"
            }
        ]
        
        logger.info("🧠 Smart Multi-Bot Launcher başlatılıyor...")
    
    async def initialize_all_bots(self) -> int:
        """Tüm bot'ları başlat"""
        
        success_count = 0
        
        for config in self.bot_configs:
            username = config["username"]
            
            try:
                bot = SmartBotInstance(config)
                self.bots[username] = bot
                
                logger.info(f"🔄 {bot.display_name} bağlanıyor...")
                
                if await bot.connect():
                    self.active_bots.append(username)
                    success_count += 1
                    logger.info(f"✅ {bot.display_name} aktif!")
                else:
                    logger.error(f"❌ {bot.display_name} bağlanamadı")
                
            except Exception as e:
                logger.error(f"❌ {username} init hatası: {e}")
        
        return success_count
    
    async def run_forever(self):
        """Bot'ları sürekli çalıştır"""
        
        logger.info(f"🔄 {len(self.active_bots)} bot süreli çalıştırma modunda")
        logger.info(f"👥 Aktif bot'lar: {', '.join([self.bots[name].display_name for name in self.active_bots])}")
        
        try:
            while True:
                # Her 10 dakikada healthcheck
                await asyncio.sleep(600)
                
                alive_count = 0
                for bot_name in self.active_bots:
                    bot = self.bots[bot_name]
                    if bot.client and bot.client.is_connected():
                        alive_count += 1
                    else:
                        logger.warning(f"⚠️ {bot.display_name} yeniden bağlanıyor...")
                        try:
                            await bot.connect()
                        except:
                            pass
                
                logger.info(f"💓 Healthcheck: {alive_count}/{len(self.active_bots)} bot aktif")
                
        except KeyboardInterrupt:
            logger.info("🛑 Kapatılıyor...")
        except Exception as e:
            logger.error(f"❌ Ana loop hatası: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Tüm bot'ları kapat"""
        logger.info("🛑 Bot'lar kapatılıyor...")
        
        for bot in self.bots.values():
            try:
                await bot.disconnect()
            except:
                pass
        
        logger.info("👋 Tüm bot'lar kapatıldı")


async def main():
    """Ana fonksiyon"""
    
    print("""
🧠 Smart Multi-Bot Launcher v2.0 🧠

✅ Session'ları otomatik bulur ve bağlanır
✅ Kod sormaz (session varsa)  
✅ Akıllı spam kontrolü
✅ DM'lere anında cevap
✅ Gruplarda natural davranış

Starting bots:
• xxxgeisha (Geisha)
• yayincilara (Lara)  
• babagavat (Gavat Baba)

Başlatılıyor...
""")
    
    launcher = SmartMultiBotLauncher()
    
    # Bot'ları başlat
    success_count = await launcher.initialize_all_bots()
    
    if success_count > 0:
        print(f"✅ {success_count}/{len(launcher.bot_configs)} bot başlatıldı!")
        print("💬 Bot'lar DM bekleniyor ve gruplarda takılıyor...")
        print("🛑 Durdurmak için Ctrl+C")
        
        # Sonsuz çalıştır
        await launcher.run_forever()
    else:
        print("❌ Hiç bot başlatılamadı!")
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit(result)
    except KeyboardInterrupt:
        print("\n👋 Bot'lar güvenli şekilde kapatıldı!")
        exit(0)
    except Exception as e:
        print(f"❌ Fatal hata: {e}")
        exit(1) 