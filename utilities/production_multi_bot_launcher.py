from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🎯 Production Multi-Bot Launcher v3.0 🎯

Güncel aktif bot'lar:
• yayincilara (@yayincilara) - Lara
• babagavat (@babagavat) - Gavat Baba  
• xxxgeisha (@xxxgeisha) - Geisha

✅ geishaniz banlandı, sistem temizlendi
✅ Session'ları otomatik bulur
✅ Spam kontrolü aktif
✅ DM'lere anında cevap
✅ Gruplarda natural davranış
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
from telethon.errors import SessionPasswordNeededError, FloodWaitError

# Config import
from config import API_ID, API_HASH

# VIP Campaign Module import
from vip_campaign_module import get_campaign_message, get_short_campaign_message, vip_campaign

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

class ProductionBotInstance:
    """Production-ready bot instance"""
    
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
        
        logger.info(f"🤖 {self.display_name} production instance hazırlandı")
    
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
        """1-1 DM konuşma mantığı"""
        message = event.message.message or ""
        user_id = sender.id
        current_time = time.time()
        
        logger.info(f"💬 {self.display_name} DM: {sender.username or sender.id} -> {message[:40]}...")
        
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
        
        # Eğer cevap bekliyorsak - kullanıcı yanıt verdi
        if conv_state["waiting_reply"]:
            conv_state["waiting_reply"] = False
            logger.info(f"✅ {self.display_name} kullanıcı yanıt verdi, devam ediliyor")
            
            # Kullanıcı cevabını analiz et ve ona göre yanıt ver
            response = await self.analyze_and_respond(message, conv_state)
        else:
            # İlk temas veya yeni konuşma
            if not conv_state["started"]:
                conv_state["started"] = True
                response = self.get_dm_response()
            else:
                # Kullanıcı beklemeden yazdı, ona yanıt ver
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
        """Kullanıcı mesajını analiz edip ona göre yanıt ver"""
        message_lower = message.lower()
        
        # Basit analiz ve yanıt
        if any(word in message_lower for word in ["merhaba", "selam", "hey", "hi"]):
            responses = self.get_greeting_responses()
        elif any(word in message_lower for word in ["nasıl", "ne haber", "naber"]):
            responses = self.get_status_responses()
        elif any(word in message_lower for word in ["ne yapıyorsun", "n'apıyorsun"]):
            responses = self.get_activity_responses()
        elif "?" in message:
            responses = self.get_question_responses()
        else:
            responses = self.get_general_responses()
        
        return random.choice(responses)
    
    async def handle_group_message(self, event, sender, chat):
        """Grup mesajlarını işle - sadece mention/reply + engaging messages"""
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
        
        # Mention veya reply'a TEK yanıt döndür
        if is_mentioned or is_reply_to_me:
            await self.send_single_group_reply(event, chat_id, current_time)
            self.mentioned_in_group[chat_id] = current_time
    
    async def send_single_group_reply(self, event, chat_id, current_time):
        """Mention/reply'a tek yanıt gönder"""
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
                if random.random() > 0.3:  # %30 şans
                    continue
                
                # Engaging message gönder
                engaging_msg = self.get_engaging_message()
                
                try:
                    await self.client.send_message(chat_id, engaging_msg)
                    self.group_engaging_timer[chat_id] = current_time
                    logger.info(f"✨ {self.display_name} engaging message: {engaging_msg}")
                    
                    # Gruplar arası delay - flood protection için artırdım
                    await asyncio.sleep(random.uniform(45, 90))  # 30-60'tan 45-90'a çıkardım
                    
                except Exception as e:
                    if "banned" in str(e).lower() or "restricted" in str(e).lower():
                        logger.warning(f"🚫 {self.display_name} grup'ta engelli: {chat_id}")
                    elif "flood" in str(e).lower():
                        logger.warning(f"⚠️ {self.display_name} engaging flood wait")
                        await asyncio.sleep(120)  # Flood durumunda 2 dakika bekle
                    else:
                        logger.error(f"❌ {self.display_name} engaging mesaj hatası: {e}")
                
        except Exception as e:
            logger.error(f"❌ {self.display_name} engaging messages genel hata: {e}")
    
    def get_dm_response(self) -> str:
        """VIP Kampanya odaklı DM yanıtları"""
        return get_campaign_message(self.username)
    
    def get_greeting_responses(self) -> List[str]:
        """Selamlama yanıtları - kampanya odaklı"""
        # %80 şansla kampanya mesajı, %20 normal selamlama
        if random.random() < 0.8:
            return [get_campaign_message(self.username)]
        
        return {
            "yayincilara": ["Selam canım! 💕", "Merhaba tatlım! 😊", "Hey nasılsın? 🌸"],
            "babagavat": ["Selam kardeşim! 😎", "Hey aslanım! 🔥", "Selamlar baba! 💪"],
            "xxxgeisha": ["Merhaba aşkım! 😘", "Selam bebek! 💋", "Hey canım! 🌹"]
        }.get(self.username, ["Selam! 👋"])
    
    def get_status_responses(self) -> List[str]:
        """Nasılsın yanıtları - kampanya odaklı"""
        # %70 şansla kampanya mesajı
        if random.random() < 0.7:
            return [get_campaign_message(self.username)]
            
        return {
            "yayincilara": ["Çok iyiyim canım, sen nasılsın? 💕", "İyi tatlım, sen ne yapıyorsun? 😊"],
            "babagavat": ["İyiyim aslanım, sen nasılsın? 🔥", "Her şey yolunda kardeşim, sen? 💪"],
            "xxxgeisha": ["Harikayım aşkım, sen nasılsın? 😘", "Çok iyiyim canım, sen? 💋"]
        }.get(self.username, ["İyiyim, sen nasılsın? 😊"])
    
    def get_activity_responses(self) -> List[str]:
        """Ne yapıyorsun yanıtları - kampanya odaklı"""
        # %90 şansla kampanya mesajı (çünkü aktivite sorusu kampanya için ideal)
        if random.random() < 0.9:
            return [get_campaign_message(self.username)]
            
        return {
            "yayincilara": ["Seni düşünüyordum 💕", "Burada senle konuşuyorum 😊", "Yayın hazırlığındaydım 🌸"],
            "babagavat": ["Takılıyorum işte 😎", "Sohbet ediyorum 🔥", "Yayın izliyordum 💪"],
            "xxxgeisha": ["Seni bekliyordum 😘", "Sıkılıyordum, iyi geldin 💋", "Buradayım canım 🌹"]
        }.get(self.username, ["Buradayım 😊"])
    
    def get_question_responses(self) -> List[str]:
        """Soru yanıtları - kampanya odaklı"""
        # %60 şansla kampanya mesajı
        if random.random() < 0.6:
            return [get_campaign_message(self.username)]
            
        return {
            "yayincilara": ["Ne merak ettin canım? 💕", "Sor bakalım tatlım 😊", "Ne var ne yok? 🌸"],
            "babagavat": ["Sor bakalım aslanım 🔥", "Ne merak ettin kardeşim? 😎", "Buyur baba 💪"],
            "xxxgeisha": ["Sor canım ne istersen 😘", "Ne merak ettin aşkım? 💋", "Buyur bebek 🌹"]
        }.get(self.username, ["Sor bakalım 😊"])
    
    def get_general_responses(self) -> List[str]:
        """Genel yanıtlar - kampanya odaklı"""
        # %75 şansla kampanya mesajı
        if random.random() < 0.75:
            return [get_campaign_message(self.username)]
            
        return {
            "yayincilara": ["Anladım canım 💕", "Çok güzel 😊", "Gerçekten mi? 🌸", "İlginç tatlım 💖"],
            "babagavat": ["Anladım kardeşim 😎", "İyi aslanım 🔥", "Doğru baba 💪", "Evet öyle 🦁"],
            "xxxgeisha": ["Anladım aşkım 😘", "Çok tatlısın 💋", "Gerçekten mi canım? 🌹", "İlginç bebek 💕"]
        }.get(self.username, ["Anladım 😊"])
    
    def get_group_response(self) -> str:
        """Grup mention/reply yanıtları"""
        responses = {
            "yayincilara": ["Selam! 😊", "Merhabalar 💕", "Hey nasılsınız? 🌸", "👋✨"],
            "babagavat": ["Selam kardeşler 😎", "Ne haber? 🔥", "Keyif nasıl? 💪", "👋"],
            "xxxgeisha": ["😘✨", "💕", "🌹", "Hey 😏", "Merhaba canlar 💋"]
        }
        
        bot_responses = responses.get(self.username, ["👋"])
        return random.choice(bot_responses)
    
    def get_engaging_message(self) -> str:
        """VIP kampanya odaklı engaging mesajlar"""
        # %70 şansla kampanya mesajı, %30 normal engaging
        if random.random() < 0.7:
            return vip_campaign.get_engaging_campaign_message(self.username)
        
        # Fallback engaging messages
        engaging_templates = {
            "yayincilara": [
                "Bugün çok güzel bir gün! ☀️💕",
                "Herkese güzel günler! 😊🌸", 
                "Nasıl geçiyor günler canlar? 💖",
                "Selam sevgili takipçilerim! ✨💕"
            ],
            "babagavat": [
                "Selamlar kardeşler! 😎🔥",
                "Keyifler nasıl aslanlar? 💪",
                "Güzel günler dilerim! 🦁",
                "Takılın bakalım! 😎✨"
            ],
            "xxxgeisha": [
                "Canlarım nasılsınız? 😘💕",
                "Güzel günler! 🌹✨",
                "Herkese sevgiler! 💋💖",
                "Buradayım canlar! 🌹😘"
            ]
        }
        
        templates = engaging_templates.get(self.username, ["Selam! 👋"])
        return random.choice(templates)
    
    async def disconnect(self):
        """Güvenli bağlantı kesme"""
        if self.client:
            await self.client.disconnect()
            logger.info(f"👋 {self.display_name} bağlantısı kesildi")


class ProductionMultiBotLauncher:
    """Production-grade multi-bot yöneticisi"""
    
    def __init__(self):
        self.bots: Dict[str, ProductionBotInstance] = {}
        self.active_bots: List[str] = []
        
        # GÜNCEL BOT KONFİGÜRASYONLARI
        self.bot_configs = [
            {
                "username": "yayincilara", 
                "display_name": "Lara",
                "phone": "+905382617727",
                "telegram_handle": "@yayincilara",
                "reply_probability": 0.10,
                "cooldown_minutes": 8,
                "max_daily_messages": 18
            },
            {
                "username": "babagavat",
                "display_name": "Gavat Baba",
                "phone": "+905513272355", 
                "telegram_handle": "@babagavat",
                "reply_probability": 0.08,  # Daha az agresif
                "cooldown_minutes": 12,
                "max_daily_messages": 12
            },
            {
                "username": "xxxgeisha",
                "display_name": "Geisha",
                "phone": "+905486306226",
                "telegram_handle": "@xxxgeisha", 
                "reply_probability": 0.15,
                "cooldown_minutes": 6,
                "max_daily_messages": 20
            }
        ]
        
        logger.info("🎯 Production Multi-Bot Launcher v3.0 başlatılıyor...")
    
    async def initialize_all_bots(self) -> int:
        """Tüm bot'ları production-grade başlatır"""
        
        success_count = 0
        
        for config in self.bot_configs:
            username = config["username"]
            
            try:
                bot = ProductionBotInstance(config)
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
        """Production-grade sürekli çalıştırma"""
        
        logger.info(f"🔄 {len(self.active_bots)} bot production modunda")
        logger.info(f"👥 Aktif bot'lar: {', '.join([self.bots[name].display_name for name in self.active_bots])}")
        
        try:
            while True:
                # Her 15 dakikada healthcheck (production)
                await asyncio.sleep(900)
                
                alive_count = 0
                for bot_name in self.active_bots:
                    bot = self.bots[bot_name]
                    if bot.client and bot.client.is_connected():
                        alive_count += 1
                    else:
                        logger.warning(f"⚠️ {bot.display_name} reconnecting...")
                        try:
                            await bot.connect()
                        except:
                            pass
                
                logger.info(f"💓 Production Healthcheck: {alive_count}/{len(self.active_bots)} bot aktif")
                
        except KeyboardInterrupt:
            logger.info("🛑 Production shutdown...")
        except Exception as e:
            logger.error(f"❌ Production loop hatası: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Production-grade güvenli kapatma"""
        logger.info("🛑 Production bot'lar kapatılıyor...")
        
        for bot in self.bots.values():
            try:
                await bot.disconnect()
            except:
                pass
        
        logger.info("👋 Production bot'lar güvenli şekilde kapatıldı")


async def main():
    """Production ana fonksiyon"""
    
    print("""
🎯 Production Multi-Bot Launcher v3.0 🎯

Güncel Aktif Bot'lar:
• yayincilara (@yayincilara) - Lara 💕
• babagavat (@babagavat) - Gavat Baba 😎  
• xxxgeisha (@xxxgeisha) - Geisha 😘

✅ geishaniz banlandı, sistem temizlendi
✅ Session'ları otomatik bulur ve bağlanır
✅ Production-grade spam kontrolü
✅ DM'lere anında cevap
✅ Gruplarda natural davranış
✅ Flood protection & error handling
✅ Database lock protection

Başlatılıyor...
""")
    
    # İlk session cleanup
    print("🧹 Session lock'ları temizleniyor...")
    cleanup_session_locks()
    
    launcher = ProductionMultiBotLauncher()
    
    # Bot'ları başlat
    success_count = await launcher.initialize_all_bots()
    
    if success_count > 0:
        print(f"✅ {success_count}/{len(launcher.bot_configs)} bot production'da!")
        print("💬 Bot'lar DM bekleniyor ve gruplarda natural takılıyor...")
        print("🛑 Durdurmak için Ctrl+C")
        
        # Production mode
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
        print("\n👋 Production bot'lar güvenli şekilde kapatıldı!")
        exit(0)
    except Exception as e:
        print(f"❌ Production fatal hata: {e}")
        exit(1) 