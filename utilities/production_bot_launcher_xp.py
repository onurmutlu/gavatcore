from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🎯 Production Multi-Bot Launcher with XP/Token Integration v4.0 🎯

Güncel aktif bot'lar + GavatCoin Token Economy:
• yayincilara (@yayincilara) - Lara
• babagavat (@babagavat) - Gavat Baba  
• xxxgeisha (@xxxgeisha) - Geisha

🆕 YENİ ÖZELLİKLER:
✅ Her etkileşimde XP kazanma
✅ Otomatik XP → Token dönüşümü 
✅ /stats komutu
✅ Token harcama sistemi
✅ Günlük bonus sistem
"""

import asyncio
import json
import os
import time
import random
import logging
import re
from typing import Dict, List, Optional, Any
from telethon import TelegramClient, events
from telethon.tl.types import User, Chat, Channel
from telethon.errors import SessionPasswordNeededError, FloodWaitError

# Config import
from config import API_ID, API_HASH

# VIP Campaign Module import
from vip_campaign_module import get_campaign_message, get_short_campaign_message, vip_campaign

# XP/Token Integration
from xp_token_engine.bot_integration import award_user_xp, handle_user_stats, handle_user_spend

# Session lock management
import glob
import sqlite3

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def cleanup_session_locks():
    """Session lock dosyalarını temizler"""
    try:
        # Journal, WAL ve SHM dosyalarını sil
        lock_patterns = [
            "sessions/*.session-journal",
            "sessions/*.session-wal", 
            "sessions/*.session-shm",
            "*.session-journal",
            "*.session-wal",
            "*.session-shm"
        ]
        
        removed_count = 0
        for pattern in lock_patterns:
            for lock_file in glob.glob(pattern):
                try:
                    os.remove(lock_file)
                    removed_count += 1
                    logger.info(f"🗑️ Session lock temizlendi: {lock_file}")
                except:
                    pass
        
        if removed_count > 0:
            logger.info(f"✅ {removed_count} session lock dosyası temizlendi")
        
        return True
    except Exception as e:
        logger.error(f"❌ Session lock cleanup hatası: {e}")
        return False

def validate_session_file(session_path: str) -> bool:
    """Session dosyasının geçerli olup olmadığını kontrol eder"""
    try:
        if not os.path.exists(session_path):
            return False
        
        # SQLite dosyasının corrupt olmadığını kontrol et
        conn = sqlite3.connect(session_path, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions';")
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    except Exception as e:
        logger.warning(f"⚠️ Session validation hatası {session_path}: {e}")
        return False

class XPProductionBotInstance:
    """Production-ready bot instance with XP/Token integration"""
    
    def __init__(self, bot_config: Dict[str, Any]):
        self.username = bot_config["username"]
        self.display_name = bot_config["display_name"] 
        self.phone = bot_config["phone"]
        self.telegram_handle = bot_config["telegram_handle"]
        
        # Session paths (multiple fallbacks)
        self.session_paths = [
            f"sessions/{self.username}_conversation.session",
            f"sessions/{self.username}.session",
            f"sessions/_{self.phone.replace('+', '')}.session"
        ]
        
        self.client: Optional[TelegramClient] = None
        self.active_session_path = None
        
        # 1-1 Conversation tracking
        self.dm_conversations = {}        # user_id -> conversation_state
        self.waiting_for_reply = {}       # user_id -> bool
        self.last_dm_response = {}        # user_id -> timestamp
        
        # Group management
        self.last_group_message = {}      # chat_id -> timestamp
        self.group_engaging_timer = {}    # chat_id -> last_engaging_message
        self.mentioned_in_group = {}      # chat_id -> last_mention_time
        
        # Bot personality settings
        self.reply_probability = bot_config.get("reply_probability", 0.12)
        self.cooldown_minutes = bot_config.get("cooldown_minutes", 8)
        self.max_daily_messages = bot_config.get("max_daily_messages", 15)
        self.engaging_interval = 300      # 5 dakika engaging message
        self.engaging_variance = 120      # ±2 dakika random
        
        logger.info(f"🤖 {self.display_name} XP-enabled production instance hazırlandı")
    
    def find_existing_session(self) -> Optional[str]:
        """En uygun session dosyasını bulur"""
        for session_path in self.session_paths:
            if os.path.exists(session_path):
                logger.info(f"📁 {self.display_name} session bulundu: {session_path}")
                return session_path
        return None
    
    async def connect(self) -> bool:
        """Production-grade bağlantı"""
        try:
            # Session lock temizliği
            cleanup_session_locks()
            
            # Session dosyasını bul
            existing_session = self.find_existing_session()
            
            if existing_session:
                # Session dosyasını validate et
                if not validate_session_file(existing_session):
                    logger.warning(f"⚠️ {self.display_name} session corrupt, yeniden oluşturuluyor...")
                    existing_session = None
                
            if existing_session:
                session_name = existing_session.replace('.session', '')
                self.client = TelegramClient(session_name, API_ID, API_HASH)
                self.active_session_path = existing_session
            else:
                # Yeni session oluştur
                session_name = f"sessions/{self.username}_conversation"
                self.client = TelegramClient(session_name, API_ID, API_HASH)
                logger.warning(f"⚠️ {self.display_name} yeni session oluşturuluyor...")
            
            # Bağlantıyı dene
            try:
                if existing_session:
                    await self.client.start()
                else:
                    await self.client.start(phone=self.phone)
                
                # Kimlik doğrulama
                me = await self.client.get_me()
                
                # Beklenen hesapla eşleşiyor mu kontrol et
                if me.username != self.telegram_handle.replace('@', ''):
                    logger.warning(f"⚠️ {self.display_name} hesap uyuşmazlığı: beklenen @{self.telegram_handle}, bulunan @{me.username}")
                
                logger.info(f"✅ {self.display_name} bağlandı! @{me.username} (ID: {me.id})")
                
                # Event handler'ları kur
                self.setup_handlers()
                
                # Engaging message scheduler başlat
                asyncio.create_task(self.start_engaging_scheduler())
                
                return True
                
            except SessionPasswordNeededError:
                logger.error(f"❌ {self.display_name} 2FA gerekli!")
                return False
            except FloodWaitError as e:
                logger.error(f"❌ {self.display_name} flood wait: {e.seconds} saniye")
                return False
            except Exception as e:
                if "database is locked" in str(e).lower():
                    logger.warning(f"⚠️ {self.display_name} database lock detected, temizleniyor...")
                    cleanup_session_locks()
                    await asyncio.sleep(2)
                    return False
                logger.error(f"❌ {self.display_name} bağlantı hatası: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ {self.display_name} genel hata: {e}")
            return False
    
    def setup_handlers(self):
        """Event handler'ları kur - XP integration ile"""
        
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
        """1-1 DM konuşma mantığı - XP Integration ile"""
        message = event.message.message or ""
        user_id = sender.id
        current_time = time.time()
        
        logger.info(f"💬 {self.display_name} DM: {sender.username or sender.id} -> {message[:40]}...")
        
        # Command handling
        if message.lower().strip() == "/stats":
            stats_response = await handle_user_stats(user_id)
            await event.reply(stats_response)
            return
        
        if message.lower().startswith("/start"):
            # /start komutuna XP ver
            success, tokens, xp_message = await award_user_xp(user_id, "start_command")
            if success:
                welcome_msg = f"🚀 Hoş geldin! {self.display_name} ile konuşmaya başladın!\n\n{xp_message}\n\n💡 /stats yazarak durumunu görebilirsin!"
                await event.reply(welcome_msg)
                return
        
        # Token spending commands
        spend_match = re.match(r'/spend (\w+)(?:\s+(.+))?', message.lower())
        if spend_match:
            service = spend_match.group(1)
            content_id = spend_match.group(2)
            spend_response = await handle_user_spend(user_id, service, content_id)
            await event.reply(spend_response)
            return
        
        # Conversation state'i kontrol et
        if user_id not in self.dm_conversations:
            self.dm_conversations[user_id] = {
                "started": False,
                "waiting_reply": False,
                "last_user_message": current_time,
                "message_count": 0
            }
        
        conv_state = self.dm_conversations[user_id]
        conv_state["last_user_message"] = current_time
        conv_state["message_count"] += 1
        
        # First DM XP
        if not conv_state["started"]:
            success, tokens, xp_message = await award_user_xp(user_id, "first_dm")
            conv_state["started"] = True
            if success:
                logger.info(f"🎮 {self.display_name} first DM XP: {user_id} -> {tokens} tokens")
        else:
            # DM reply XP
            success, tokens, xp_message = await award_user_xp(user_id, "dm_reply")
            if success:
                logger.info(f"🎮 {self.display_name} DM reply XP: {user_id} -> {tokens} tokens")
        
        # Eğer cevap bekliyorsak - kullanıcı yanıt verdi
        if conv_state["waiting_reply"]:
            conv_state["waiting_reply"] = False
            logger.info(f"✅ {self.display_name} kullanıcı yanıt verdi, devam ediliyor")
            
            # Kullanıcı cevabını analiz et ve ona göre yanıt ver
            response = await self.analyze_and_respond(message, conv_state)
        else:
            # İlk temas veya yeni konuşma
            response = await self.analyze_and_respond(message, conv_state)
        
        # Natural response delay
        await asyncio.sleep(random.uniform(3, 8))
        
        try:
            await event.reply(response)
            
            # Conversation state'i güncelle
            conv_state["waiting_reply"] = True
            self.last_dm_response[user_id] = current_time
            
            logger.info(f"✅ {self.display_name} DM yanıtı: {response}")
            logger.info(f"⏳ {self.display_name} kullanıcı yanıtı bekleniyor...")
            
        except FloodWaitError as e:
            logger.warning(f"⚠️ {self.display_name} DM flood wait: {e.seconds}s")
            # Flood wait durumunda state'i geri al
            conv_state["waiting_reply"] = False
        except Exception as e:
            logger.error(f"❌ {self.display_name} DM yanıt hatası: {e}")
            conv_state["waiting_reply"] = False
    
    async def analyze_and_respond(self, message: str, conv_state: dict) -> str:
        """Kullanıcı mesajını analiz edip ona göre yanıt ver - XP hints ile"""
        message_lower = message.lower()
        
        # XP system hints
        xp_hints = [
            "\n💡 /stats ile durumunu kontrol et!",
            "\n🎁 Günlük bonusunu kaçırma!",
            "\n💰 Token biriktirerek özel içeriklere eriş!",
            "\n🎮 Her konuşma XP kazandırır!"
        ]
        
        # Basit analiz ve yanıt
        if any(word in message_lower for word in ["merhaba", "selam", "hey", "hi"]):
            responses = self.get_greeting_responses()
        elif any(word in message_lower for word in ["nasıl", "ne haber", "naber"]):
            responses = self.get_status_responses()
        elif any(word in message_lower for word in ["ne yapıyorsun", "n'apıyorsun"]):
            responses = self.get_activity_responses()
        elif "?" in message:
            responses = self.get_question_responses()
        elif any(word in message_lower for word in ["token", "xp", "puan"]):
            responses = self.get_token_responses()
        else:
            responses = self.get_general_responses()
        
        base_response = random.choice(responses)
        
        # Random XP hint ekleme (30% şans)
        if random.random() < 0.3:
            base_response += random.choice(xp_hints)
        
        return base_response
    
    async def handle_group_message(self, event, sender, chat):
        """Grup mesajlarını işle - XP integration ile"""
        chat_id = chat.id
        current_time = time.time()
        message = event.message.message or ""
        
        # Son grup mesajını güncelle
        self.last_group_message[chat_id] = current_time
        
        # Mention veya reply kontrolü
        me = await self.client.get_me()
        is_mentioned = f"@{me.username}" in message or f"@{self.username}" in message
        is_reply_to_me = False
        
        if event.is_reply:
            try:
                replied_msg = await event.get_reply_message()
                if replied_msg and replied_msg.sender_id == me.id:
                    is_reply_to_me = True
            except:
                pass
        
        # Mention veya reply'a TEK yanıt döndür + XP ver
        if is_mentioned or is_reply_to_me:
            # XP award
            action = "group_mention" if is_mentioned else "group_reply"
            success, tokens, xp_message = await award_user_xp(sender.id, action)
            
            await self.send_single_group_reply(event, chat_id, current_time, xp_message if success else None)
            self.mentioned_in_group[chat_id] = current_time
    
    async def send_single_group_reply(self, event, chat_id, current_time, xp_message=None):
        """Mention/reply'a tek yanıt gönder + XP notification"""
        # Flood protection
        if chat_id in self.mentioned_in_group:
            time_since_last = current_time - self.mentioned_in_group[chat_id]
            if time_since_last < 60:  # Son mention'dan 1 dakika geçmedi
                logger.info(f"🔒 {self.display_name} grup flood protection - mention yakın")
                return
        
        # Natural delay
        delay = random.uniform(3, 8)
        await asyncio.sleep(delay)
        
        response = self.get_group_response()
        
        # XP message ekleme (bazen)
        if xp_message and random.random() < 0.5:
            response += f"\n\n{xp_message}"
        
        try:
            await event.reply(response)
            logger.info(f"💬 {self.display_name} grup mention yanıtı: {response}")
        except FloodWaitError as e:
            logger.warning(f"⚠️ {self.display_name} grup flood wait: {e.seconds}s")
        except Exception as e:
            logger.error(f"❌ {self.display_name} grup yanıt hatası: {e}")
    
    async def start_engaging_scheduler(self):
        """5-7 dakikada bir engaging message scheduler"""
        while True:
            try:
                # 5-7 dakika arası random bekleme (300-420 saniye)
                wait_time = random.uniform(300, 420)
                await asyncio.sleep(wait_time)
                
                # Aktif gruplara engaging message gönder
                await self.send_engaging_messages()
                
            except Exception as e:
                logger.error(f"❌ {self.display_name} engaging scheduler hatası: {e}")
                await asyncio.sleep(300)  # Hata durumunda 5 dakika bekle
    
    async def send_engaging_messages(self):
        """Gruplara engaging message gönder"""
        try:
            current_time = time.time()
            
            # Tüm diyaloglarda dön
            async for dialog in self.client.iter_dialogs():
                if not dialog.is_group:
                    continue
                
                chat_id = dialog.id
                
                # Son mesajdan en az 5 dakika geçmiş mi?
                if chat_id in self.last_group_message:
                    time_since_last = current_time - self.last_group_message[chat_id]
                    if time_since_last < 300:  # 5 dakika
                        continue
                
                # Son engaging mesajdan en az 30 dakika geçmiş mi?
                if chat_id in self.group_engaging_timer:
                    time_since_engaging = current_time - self.group_engaging_timer[chat_id]
                    if time_since_engaging < 1800:  # 30 dakika
                        continue
                
                # Random chance - her grupta her seferinde mesaj atmasın
                if random.random() > 0.3:  # 30% şans
                    continue
                
                # VIP campaign message ile engaging message karıştır
                if random.random() < 0.7:  # 70% VIP campaign
                    message = get_short_campaign_message()
                else:  # 30% normal engaging
                    message = self.get_engaging_message()
                
                try:
                    await self.client.send_message(dialog, message)
                    self.group_engaging_timer[chat_id] = current_time
                    logger.info(f"🎯 {self.display_name} engaging message: {dialog.name}")
                    
                    # Engaging message gönderen bot'lara premium XP (kendi kendine değil)
                    # await award_user_xp(me.id, "premium_interaction")
                    
                except Exception as e:
                    logger.error(f"❌ {self.display_name} engaging message hatası {dialog.name}: {e}")
                
                # Mesajlar arası delay
                await asyncio.sleep(random.uniform(10, 30))
                
        except Exception as e:
            logger.error(f"❌ {self.display_name} engaging messages genel hatası: {e}")
    
    def get_greeting_responses(self) -> List[str]:
        return [
            "Merhaba! Nasılsın? 😊",
            "Selam! Ne var ne yok? 👋",
            "Hey! Hoş geldin! ✨",
            "Merhaba canım, nasıl gidiyor? 💫"
        ]
    
    def get_status_responses(self) -> List[str]:
        return [
            "İyiyim, teşekkürler! Sen nasılsın? 😊",
            "Harika! Sen ne yapıyorsun? ✨",
            "İyi gidiyor, seninle konuşmak güzel 💭",
            "Mükemmel! Bugün nasıl geçiyor? 🌟"
        ]
    
    def get_activity_responses(self) -> List[str]:
        return [
            "Burada seninle sohbet ediyorum! 💬",
            "Yeni insanlarla tanışıyorum 😊",
            "Güzel konuşmalar yapıyorum ✨",
            "Seninle vakit geçiriyorum! 💫"
        ]
    
    def get_question_responses(self) -> List[str]:
        return [
            "İlginç bir soru! 🤔",
            "Hmm, düşünmem lazım 💭",
            "Bu konuda ne düşünüyorsun? 🌟",
            "Güzel soru! Bana daha fazlasını anlat 😊"
        ]
    
    def get_token_responses(self) -> List[str]:
        return [
            "🪙 Token sistemi harika! Her konuşmada XP kazanıyorsun!",
            "💰 Token biriktir, özel içeriklere eriş! /stats ile kontrol et",
            "🎮 XP kazanmak çok kolay! Benimle konuşmaya devam et!",
            "🎁 Günlük bonusunu aldın mı? /stats ile bakabilirsin!"
        ]
    
    def get_general_responses(self) -> List[str]:
        return [
            "Anlıyorum 😊",
            "İlginç! Devam et 💭",
            "Çok güzel! ✨",
            "Katılıyorum seninle 🌟",
            "Ne düşünüyorsun bu konuda? 💫",
            "Bana daha fazlasını anlat 😊"
        ]
    
    def get_group_response(self) -> str:
        responses = [
            "Selam! 👋",
            "Merhaba! 😊",
            "Hey! Ne var? ✨",
            "Nasılsınız? 💫",
            "İyi günler! 🌟"
        ]
        return random.choice(responses)
    
    def get_engaging_message(self) -> str:
        messages = [
            "Bugün nasıl geçiyor arkadaşlar? 😊",
            "Keyifler nasıl? ✨",
            "Neler yapıyorsunuz? 💭",
            "Güzel bir gün! 🌟",
            "Herkese iyi günler! 💫"
        ]
        return random.choice(messages)

# Production bot configurations
PRODUCTION_BOTS_XP = [
    {
        "username": "yayincilara",
        "display_name": "🌟 Lara (XP)",
        "phone": "+905382617727",
        "telegram_handle": "@yayincilara",
        "reply_probability": 0.12,
        "cooldown_minutes": 8,
        "max_daily_messages": 15
    },
    {
        "username": "babagavat", 
        "display_name": "🦁 Gavat Baba (XP)",
        "phone": "+905513272355",
        "telegram_handle": "@babagavat",
        "reply_probability": 0.10,
        "cooldown_minutes": 10,
        "max_daily_messages": 12
    },
    {
        "username": "xxxgeisha",
        "display_name": "🌸 Geisha (XP)",
        "phone": "+905486306226",
        "telegram_handle": "@xxxgeisha",
        "reply_probability": 0.15,
        "cooldown_minutes": 6,
        "max_daily_messages": 18
    }
]

async def main():
    """Ana program - XP enabled production bots"""
    logger.info("🚀 XP/Token Enabled Production Multi-Bot Launcher v4.0 başlatılıyor...")
    
    # Session locks temizle
    cleanup_session_locks()
    
    # Bot instance'larını oluştur
    bot_instances = []
    for bot_config in PRODUCTION_BOTS_XP:
        bot = XPProductionBotInstance(bot_config)
        bot_instances.append(bot)
    
    # Bot'ları paralel olarak başlat
    connected_bots = []
    for bot in bot_instances:
        try:
            logger.info(f"🔗 {bot.display_name} bağlanıyor...")
            success = await bot.connect()
            if success:
                connected_bots.append(bot)
                logger.info(f"✅ {bot.display_name} başarıyla bağlandı!")
            else:
                logger.error(f"❌ {bot.display_name} bağlanamadı!")
        except Exception as e:
            logger.error(f"❌ {bot.display_name} bağlantı hatası: {e}")
    
    if not connected_bots:
        logger.error("❌ Hiçbir bot bağlanamadı! Çıkılıyor...")
        return
    
    logger.info(f"🎉 {len(connected_bots)}/{len(bot_instances)} bot başarıyla çalışıyor!")
    logger.info("🪙 XP/Token sistemi aktif!")
    logger.info("📊 Kullanıcılar /stats komutuyla durumlarını görebilir")
    logger.info("💰 Token harcama: /spend service_name")
    logger.info("🎁 Günlük bonus sistemi aktif")
    
    # Sonsuz döngü - bot'ları çalışır durumda tut
    try:
        while True:
            await asyncio.sleep(60)  # Her dakika kontrol
            
            # Bot durumlarını kontrol et
            for bot in connected_bots:
                try:
                    if bot.client and not bot.client.is_connected():
                        logger.warning(f"⚠️ {bot.display_name} bağlantısı koptu, yeniden bağlanıyor...")
                        await bot.connect()
                except Exception as e:
                    logger.error(f"❌ {bot.display_name} durumu kontrol hatası: {e}")
    
    except KeyboardInterrupt:
        logger.info("🛑 Çıkış sinyali alındı, bot'lar kapatılıyor...")
        
        # Bot'ları kapat
        for bot in connected_bots:
            try:
                if bot.client:
                    await bot.client.disconnect()
                    logger.info(f"👋 {bot.display_name} kapatıldı")
            except Exception as e:
                logger.error(f"❌ {bot.display_name} kapatma hatası: {e}")
        
        logger.info("✅ Tüm bot'lar kapatıldı!")

if __name__ == "__main__":
    asyncio.run(main()) 