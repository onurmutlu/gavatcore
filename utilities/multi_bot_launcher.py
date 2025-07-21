#!/usr/bin/env python3
"""
🚀 GavatCore Multi-Bot Launcher v1.0 🚀

xxxgeisha, yayincilara ve babagavat botlarının 3'ünü birden çalıştırır.
✅ Session'ları otomatik bulur
✅ Spam kontrolü ile akıllı davranır  
✅ Gruplarda dikkat çekmez
✅ DM'lere anında cevap verir

Kullanım:
python multi_bot_launcher.py
"""

import os, sys
# Ensure project root is on sys.path for imports
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)
import asyncio
import json
import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from telethon import TelegramClient, events
from telethon.tl.types import User, Chat, Channel
import structlog

# Config import
from config import API_ID, API_HASH, AUTHORIZED_USERS

# Set up structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.WriteLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class BotInstance:
    """Tek bir bot instance'ını yönetir"""
    
    def __init__(self, username: str, persona_data: Dict[str, Any]):
        self.username = username
        self.persona = persona_data
        self.phone = persona_data.get("phone", "")
        self.display_name = persona_data.get("display_name", username)
        self.user_id = persona_data.get("user_id")
        
        # Session file path
        self.session_path = f"sessions/{username}_conversation.session"
        
        # Telegram client
        self.client: Optional[TelegramClient] = None
        
        # Spam control
        self.last_message_time = {}  # group_id -> timestamp
        self.message_count = {}      # group_id -> count
        self.cooldown_until = {}     # group_id -> timestamp
        
        # Settings from persona
        self.spam_interval_min = persona_data.get("spam_interval_min", 300)  # 5 min
        self.spam_interval_max = persona_data.get("spam_interval_max", 600)  # 10 min
        self.group_spam_enabled = persona_data.get("group_spam_enabled", True)
        self.group_spam_aggressive = persona_data.get("group_spam_aggressive", False)
        self.reply_probability = 0.3 if not self.group_spam_aggressive else 0.1  # Daha az agresif
        
        logger.info(f"🤖 {self.display_name} bot instance oluşturuldu", 
                   username=username, phone=self.phone)
    
    async def connect(self) -> bool:
        """Bot'u Telegram'a bağlar"""
        try:
            # Check if session exists
            if os.path.exists(self.session_path):
                logger.info(f"📁 {self.display_name} session bulundu: {self.session_path}")
                self.client = TelegramClient(self.session_path.replace('.session', ''), API_ID, API_HASH)
            else:
                logger.warning(f"⚠️ {self.display_name} session bulunamadı, yeni session oluşturulacak")
                self.client = TelegramClient(f"sessions/{self.username}_conversation", API_ID, API_HASH)
            
            await self.client.start(phone=self.phone)
            
            # Verify connection
            me = await self.client.get_me()
            logger.info(f"✅ {self.display_name} bağlandı!", 
                       username=me.username, user_id=me.id, phone=me.phone)
            
            # Setup event handlers
            self.setup_handlers()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ {self.display_name} bağlantı hatası: {e}")
            return False
    
    def setup_handlers(self):
        """Event handler'ları kurar"""
        
        @self.client.on(events.NewMessage(incoming=True))
        async def handle_message(event):
            """Gelen mesajları işler"""
            try:
                sender = await event.get_sender()
                if not sender:
                    return
                
                # Self mesajları ignore et
                if sender.id == (await self.client.get_me()).id:
                    return
                
                chat = await event.get_chat()
                is_private = isinstance(sender, User) and event.is_private
                is_group = isinstance(chat, (Chat, Channel)) and not event.is_private
                
                if is_private:
                    # DM'lerde anında cevap ver
                    await self.handle_private_message(event, sender)
                elif is_group and self.group_spam_enabled:
                    # Gruplarda dikkatli davran
                    await self.handle_group_message(event, sender, chat)
                    
            except Exception as e:
                logger.error(f"❌ {self.display_name} mesaj işleme hatası: {e}")
    
    async def handle_private_message(self, event, sender):
        """Private mesajları işler"""
        message = event.message.message
        
        logger.info(f"💬 {self.display_name} DM alındı", 
                   from_user=sender.username or sender.id, message_preview=message[:50])
        
        # Basit otomatik cevap (daha sonra GPT ile geliştirilecek)
        responses = [
            f"Merhaba! {self.display_name} burada 😊",
            "Selam, nasılsın? 💕",
            "Hey, ne yapıyorsun? 😘",
            "Merhaba canım 🌹"
        ]
        
        import random
        response = random.choice(responses)
        
        await asyncio.sleep(1)  # Natural delay
        await event.reply(response)
        
        logger.info(f"✅ {self.display_name} DM yanıtladı", response=response)
    
    async def handle_group_message(self, event, sender, chat):
        """Grup mesajlarını işler (spam kontrolü ile)"""
        
        chat_id = chat.id
        current_time = time.time()
        
        # Cooldown kontrolü
        if chat_id in self.cooldown_until and current_time < self.cooldown_until[chat_id]:
            return  # Cooldown'da
        
        # Mesaj sayısı kontrolü
        if chat_id not in self.message_count:
            self.message_count[chat_id] = 0
            self.last_message_time[chat_id] = 0
        
        # Son mesajdan ne kadar zaman geçti?
        time_since_last = current_time - self.last_message_time[chat_id]
        
        # Çok sık mesaj atma (minimum 5 dakika)
        if time_since_last < self.spam_interval_min:
            return
        
        # Rastgele cevap verme olasılığı (spam değil, doğal davranış)
        import random
        if random.random() > self.reply_probability:
            return  # Bu mesajı atlıyoruz
        
        # Mesaj içeriği analizi
        message = event.message.message.lower()
        
        # Bot'a mention varsa veya belirli kelimeler varsa cevap ver
        bot_mentioned = f"@{self.username}" in message or self.username.lower() in message
        trigger_words = ["selam", "merhaba", "hey", "nasıl", "naber"]
        has_trigger = any(word in message for word in trigger_words)
        
        if bot_mentioned or has_trigger or random.random() < 0.1:  # %10 rastgele
            await self.send_group_response(event, chat_id)
    
    async def send_group_response(self, event, chat_id):
        """Gruplara cevap gönderir"""
        
        # Doğal gecikme (1-3 saniye)
        import random
        delay = random.uniform(1, 3)
        await asyncio.sleep(delay)
        
        # Bot kişiliğine göre cevap
        responses = self.get_personality_responses()
        response = random.choice(responses)
        
        try:
            await event.reply(response)
            
            # Spam kontrolü güncelle
            current_time = time.time()
            self.last_message_time[chat_id] = current_time
            self.message_count[chat_id] += 1
            
            # 1 saatte 3'ten fazla mesaj attıysa 30 dakika cooldown
            if self.message_count[chat_id] >= 3:
                self.cooldown_until[chat_id] = current_time + 1800  # 30 min
                self.message_count[chat_id] = 0  # Reset
                
                logger.info(f"🕒 {self.display_name} cooldown başladı", 
                           chat_id=chat_id, duration="30 dakika")
            
            logger.info(f"💬 {self.display_name} grup mesajı gönderdi", 
                       chat_id=chat_id, response=response)
            
        except Exception as e:
            logger.error(f"❌ {self.display_name} grup mesaj hatası: {e}")
    
    def get_personality_responses(self) -> List[str]:
        """Bot kişiliğine göre cevaplar döner"""
        
        if self.username == "xxxgeisha":
            return [
                "😘✨", "Aşkım nasılsın? 💕", "Hey bebek 🌹", 
                "Müsait misin? 😏", "Özledim seni 💋"
            ]
        elif self.username == "yayincilara":
            return [
                "Merhabalar! 😊", "Selam canlar 💕", "Hey nasılsınız? 🌸",
                "Bugün nasıl geçti? ☀️", "İyi eğlenceler 🎉"
            ]
        elif self.username == "babagavat":
            return [
                "Selam kardeşim 😎", "Ne haber buralardan? 🚬", "Keyif nasıl? 💪",
                "Takılıyoruz işte 🔥", "Haşır neşir 😏", "Aslanım nasılsın? 🦁"
            ]
        else:
            return ["👋", "Selam! 😊", "Hey! 👍"]
    
    async def disconnect(self):
        """Bot bağlantısını keser"""
        if self.client:
            await self.client.disconnect()
            logger.info(f"👋 {self.display_name} bağlantısı kesildi")


class MultiBotLauncher:
    """3 bot'u birden yönetir"""
    
    def __init__(self):
        self.bots: Dict[str, BotInstance] = {}
        self.active_bots: List[str] = []
        
        # Bot isimleri
        self.bot_names = ["xxxgeisha", "yayincilara", "babagavat"]
        
        logger.info("🚀 Multi-Bot Launcher başlatılıyor...")
    
    def load_persona(self, username: str) -> Optional[Dict[str, Any]]:
        """Persona dosyasını yükler"""
        persona_path = f"data/personas/{username}.json"
        
        try:
            with open(persona_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"📖 {username} persona yüklendi", path=persona_path)
                return data
        except Exception as e:
            logger.error(f"❌ {username} persona yüklenemedi: {e}")
            return None
    
    async def initialize_bots(self) -> bool:
        """Tüm bot'ları başlatır"""
        
        success_count = 0
        
        for bot_name in self.bot_names:
            try:
                # Persona yükle
                persona_data = self.load_persona(bot_name)
                if not persona_data:
                    continue
                
                # Bot instance oluştur
                bot = BotInstance(bot_name, persona_data)
                self.bots[bot_name] = bot
                
                # Bağlan
                if await bot.connect():
                    self.active_bots.append(bot_name)
                    success_count += 1
                    logger.info(f"✅ {bot.display_name} aktif!")
                else:
                    logger.error(f"❌ {bot.display_name} başlatılamadı")
                
            except Exception as e:
                logger.error(f"❌ {bot_name} init hatası: {e}")
        
        logger.info(f"🎯 Bot Launcher Sonuç: {success_count}/{len(self.bot_names)} bot aktif")
        return success_count > 0
    
    async def run_forever(self):
        """Bot'ları sürekli çalıştırır"""
        
        logger.info("🔄 Bot'lar süreli çalıştırma moduna geçti")
        logger.info(f"👥 Aktif bot'lar: {', '.join(self.active_bots)}")
        
        try:
            # Ana loop - bot'lar event handler'larda çalışıyor
            while True:
                # Heartbeat - her 5 dakikada durum kontrolü
                await asyncio.sleep(300)
                
                alive_count = 0
                for bot_name in self.active_bots:
                    bot = self.bots[bot_name]
                    if bot.client and bot.client.is_connected():
                        alive_count += 1
                    else:
                        logger.warning(f"⚠️ {bot.display_name} bağlantısı koptu, yeniden bağlanıyor...")
                        try:
                            await bot.connect()
                        except:
                            pass
                
                logger.info(f"💓 Heartbeat: {alive_count}/{len(self.active_bots)} bot hayatta")
                
        except KeyboardInterrupt:
            logger.info("🛑 Keyboard interrupt alındı, bot'lar kapatılıyor...")
        except Exception as e:
            logger.error(f"❌ Ana loop hatası: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Tüm bot'ları güvenli şekilde kapatır"""
        
        logger.info("🛑 Bot'lar kapatılıyor...")
        
        for bot_name, bot in self.bots.items():
            try:
                await bot.disconnect()
            except:
                pass
        
        logger.info("👋 Tüm bot'lar kapatıldı")


async def main():
    """Ana fonksiyon"""
    
    print("""
🚀 GavatCore Multi-Bot Launcher v1.0 🚀

Starting bots:
• xxxgeisha (Geisha) 
• yayincilara (Lara)
• babagavat (Gavat Baba)

✅ Session'lar otomatik bulunacak
✅ Spam kontrolü aktif
✅ DM'lere anında cevap
✅ Gruplarda dikkatli davranış

Başlatılıyor...
""")
    
    launcher = MultiBotLauncher()
    
    # Bot'ları başlat
    if await launcher.initialize_bots():
        print(f"✅ {len(launcher.active_bots)} bot başarıyla başlatıldı!")
        print("💬 Bot'lar DM bekleniyor ve gruplarda takılıyor...")
        print("🛑 Durdurmak için Ctrl+C")
        
        # Sonsuz loop
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
        print("\n👋 Bot'lar kapatıldı!")
        exit(0)
    except Exception as e:
        print(f"❌ Fatal hata: {e}")
        exit(1) 
