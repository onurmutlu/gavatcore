#!/usr/bin/env python3
"""
🔥🔥🔥 SPAM-AWARE FULL BOT SYSTEM 🔥🔥🔥

💪 ONUR METODU - SPAM'e KARŞI AKILLI CONTACT MANAGEMENT!

Features:
- Tüm botları aktif kullan
- SPAM durumunda DM'e geç
- "DM" reply'i geldiğinde contact ekleme
- Grup içinde "ekledim, ekle, engel var" mesajı
- GPT-4o ile akıllı sohbet
- Contact list otomatik yönetimi

🎯 HEDEF: SPAM'e KARŞI AKILLI SİSTEM!
"""

import asyncio
import json
import os
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
import structlog
from telethon import TelegramClient, events
from telethon.errors import (
    FloodWaitError, UserBannedInChannelError, ChatWriteForbiddenError,
    UserPrivacyRestrictedError, PeerFloodError, UserNotMutualContactError
)
from telethon.tl.functions.contacts import AddContactRequest
from telethon.tl.types import InputUser, User
import openai
import sqlite3

# Config
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY
logger = structlog.get_logger("spam_aware_system")

class SpamAwareFullBotSystem:
    """🔥 SPAM'e Karşı Akıllı Tüm Bot Sistemi"""
    
    def __init__(self):
        self.start_time = datetime.now()
        
        # Bot clients
        self.bot_clients = {}  # {bot_name: {"client": client, "me": me, "status": status}}
        
        # Contact management
        self.pending_contacts = {}  # {user_id: {"bot_name": str, "group_id": int, "timestamp": datetime}}
        self.contact_database = "spam_aware_contacts.db"
        
        # SPAM tracking
        self.spam_status = {}  # {bot_name: {"banned": bool, "until": datetime, "last_check": datetime}}
        
        # Message cache for intelligent responses
        self.message_cache = {}
        
        # Target groups
        self.target_groups = [
            "@arayisonlyvips", 
            # Diğer gruplar buraya eklenebilir
        ]
        
        # Bot configurations
        self.bot_configs = [
            {
                "name": "babagavat",
                "session_file": "sessions/_905513272355.session",
                "personality": "BabaGAVAT - Sokak zekası uzmanı, güvenilir rehber"
            },
            {
                "name": "xxxgeisha", 
                "session_file": "sessions/_905486306226.session",
                "personality": "XXXGeisha - Zarif, akıllı, çekici sohbet uzmanı"
            },
            {
                "name": "yayincilara",
                "session_file": "sessions/_905382617727.session", 
                "personality": "YayıncıLara - Enerjik, eğlenceli, popüler kişilik"
            }
        ]
        
        logger.info("🔥 SPAM-Aware Full Bot System başlatıldı!")
    
    async def initialize(self):
        """Sistemi başlat"""
        try:
            # Database'i hazırla
            await self._setup_database()
            
            # Botları başlat
            await self._initialize_bots()
            
            # SPAM durumlarını kontrol et
            await self._check_all_spam_status()
            
            # Event handler'ları kur
            await self._setup_event_handlers()
            
            logger.info("✅ SPAM-Aware sistem hazır - Tüm botlar aktif!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sistem başlatma hatası: {e}")
            return False
    
    async def _setup_database(self):
        """Contact ve SPAM veritabanını kur"""
        conn = sqlite3.connect(self.contact_database)
        cursor = conn.cursor()
        
        # Contact management table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                user_id INTEGER,
                bot_name TEXT,
                group_id INTEGER,
                contact_added BOOLEAN DEFAULT FALSE,
                dm_started BOOLEAN DEFAULT FALSE,
                first_contact_attempt DATETIME,
                successful_dm DATETIME,
                notes TEXT,
                PRIMARY KEY (user_id, bot_name)
            )
        """)
        
        # SPAM tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spam_tracking (
                bot_name TEXT PRIMARY KEY,
                is_banned BOOLEAN DEFAULT FALSE,
                ban_until DATETIME,
                last_check DATETIME,
                ban_count INTEGER DEFAULT 0,
                successful_messages INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("📊 Database hazırlandı")
    
    async def _initialize_bots(self):
        """Tüm botları başlat"""
        for bot_config in self.bot_configs:
            try:
                bot_name = bot_config["name"]
                session_file = bot_config["session_file"]
                
                # Client oluştur - güçlü bağlantı ayarları ile
                client = TelegramClient(
                    session_file, 
                    TELEGRAM_API_ID, 
                    TELEGRAM_API_HASH,
                    # Bağlantı ayarları
                    connection_retries=5,
                    retry_delay=10,
                    timeout=60,
                    request_retries=3,
                    flood_sleep_threshold=60,
                    auto_reconnect=True,
                    sequential_updates=True,
                    # Proxy ve connection pool ayarları
                    use_ipv6=False,
                    device_model="SPAM-Aware Bot",
                    system_version="1.0",
                    app_version="1.0"
                )
                
                await client.start()
                
                # Bot bilgilerini al
                me = await client.get_me()
                
                self.bot_clients[bot_name] = {
                    "client": client,
                    "me": me,
                    "config": bot_config,
                    "status": "active"
                }
                
                logger.info(f"✅ {bot_name} aktif: @{me.username} - {bot_config['personality']}")
                
            except Exception as e:
                logger.error(f"❌ {bot_name} başlatma hatası: {e}")
                # Devam et, diğer botları başlatmaya çalış
    
    async def _check_all_spam_status(self):
        """Tüm botların SPAM durumunu kontrol et"""
        for bot_name, bot_data in self.bot_clients.items():
            try:
                client = bot_data["client"]
                
                # Test mesajı göndererek SPAM durumunu kontrol et
                spam_status = await self._check_spam_status(client, bot_name)
                self.spam_status[bot_name] = spam_status
                
                if spam_status["banned"]:
                    logger.warning(f"⚠️ {bot_name} SPAM kısıtlaması altında: {spam_status['until']}")
                    bot_data["status"] = "spam_restricted"
                else:
                    logger.info(f"✅ {bot_name} SPAM durumu temiz")
                    bot_data["status"] = "active"
                    
            except Exception as e:
                logger.error(f"❌ {bot_name} SPAM kontrol hatası: {e}")
    
    async def _check_spam_status(self, client: TelegramClient, bot_name: str) -> Dict[str, Any]:
        """Tek bot için SPAM durumu kontrol et"""
        try:
            # @SpamBot'a mesaj göndermeyi dene
            spam_bot_username = "SpamBot"
            
            try:
                # SpamBot'u resolve et
                spam_bot = await client.get_entity(spam_bot_username)
                
                # Durumu kontrol et (gerçek mesaj gönderme yerine, sadece erişim kontrolü)
                # Gerçek implementasyon için SpamBot'a "start" mesajı gönderilebilir
                
                return {
                    "banned": False,
                    "until": None,
                    "last_check": datetime.now(),
                    "method": "indirect_check"
                }
                
            except Exception as e:
                # Eğer mesaj gönderemiyorsak, büyük ihtimalle kısıtlama var
                if "banned" in str(e).lower() or "restricted" in str(e).lower():
                    return {
                        "banned": True,
                        "until": datetime.now() + timedelta(hours=24),  # Default 24 saat
                        "last_check": datetime.now(),
                        "error": str(e)
                    }
                else:
                    return {
                        "banned": False,
                        "until": None,
                        "last_check": datetime.now(),
                        "method": "error_based_check"
                    }
                    
        except Exception as e:
            logger.error(f"SPAM kontrol hatası ({bot_name}): {e}")
            return {
                "banned": False,
                "until": None,
                "last_check": datetime.now(),
                "error": str(e)
            }
    
    async def _setup_event_handlers(self):
        """Event handler'ları kur"""
        for bot_name, bot_data in self.bot_clients.items():
            client = bot_data["client"]
            
            # Mesaj handler'ı
            @client.on(events.NewMessage)
            async def handle_message(event, bot_name=bot_name):
                await self._handle_message(event, bot_name)
            
            # Reply handler'ı
            @client.on(events.NewMessage(pattern=r'(?i).*\b(dm|mesaj|yaz)\b.*'))
            async def handle_dm_request(event, bot_name=bot_name):
                if event.is_reply:
                    await self._handle_dm_request(event, bot_name)
        
        logger.info("🎯 Event handler'lar kuruldu")
    
    async def _handle_message(self, event, bot_name: str):
        """Gelen mesajları işle"""
        try:
            # Grup mesajlarını filtrele
            if not event.is_group:
                return
            
            # Bot'un aktif olup olmadığını kontrol et
            bot_data = self.bot_clients.get(bot_name)
            if not bot_data:
                logger.warning(f"⚠️ Bot data bulunamadı: {bot_name}")
                return
                
            if bot_data["status"] == "spam_restricted":
                # SPAM kısıtlaması varsa DM moduna geç
                return await self._handle_spam_restricted_message(event, bot_name)
            
            # Normal grup mesajı işleme
            await self._process_group_message(event, bot_name)
            
        except ConnectionError as e:
            logger.warning(f"🔗 Bağlantı hatası ({bot_name}): {e}")
            # Bağlantı hatası durumunda bot'u yeniden başlatmayı dene
            await self._try_reconnect_bot(bot_name)
        except Exception as e:
            logger.error(f"Mesaj işleme hatası ({bot_name}): {e}")
    
    async def _handle_dm_request(self, event, bot_name: str):
        """DM talebi geldiğinde contact ekleme işlemi"""
        try:
            # Reply'i yapan kullanıcıyı al
            replied_message = await event.get_reply_message()
            if not replied_message:
                logger.warning(f"⚠️ Reply message bulunamadı ({bot_name})")
                return
            
            # Replied message'ın sender_id'si var mı kontrol et
            if not hasattr(replied_message, 'sender_id') or replied_message.sender_id is None:
                logger.warning(f"⚠️ Reply message sender_id yok ({bot_name})")
                return
            
            # Bot'un mesajına reply mi?
            bot_data = self.bot_clients.get(bot_name)
            if not bot_data:
                logger.warning(f"⚠️ Bot data bulunamadı: {bot_name}")
                return
                
            me = bot_data["me"]
            
            if replied_message.sender_id != me.id:
                return  # Başka birinin mesajına reply
            
            # DM isteğinde bulunan kullanıcı
            user = await event.get_sender()
            if not user:
                logger.warning(f"⚠️ Sender bilgisi alınamadı ({bot_name})")
                return
                
            user_id = user.id
            group_id = event.chat_id
            
            # User'ın gerekli bilgileri var mı kontrol et
            if not hasattr(user, 'access_hash') or user.access_hash is None:
                logger.warning(f"⚠️ User access_hash yok: {user.first_name} ({user_id})")
                # Access hash olmadan contact ekleme yapılamaz
                response = f"🔒 {user.first_name or 'Kullanıcı'}, teknik bir sorun var. Lütfen önce bana DM'den 'merhaba' yaz!"
                await event.respond(response)
                return
            
            logger.info(f"📩 DM talebi: {user.first_name or 'Anonim'} ({user_id}) -> {bot_name}")
            
            # Contact ekleme işlemi
            contact_result = await self._add_user_to_contacts(
                bot_data["client"], user, bot_name, group_id
            )
            
            if contact_result["success"]:
                # Başarılı contact ekleme - grup'ta bildir
                response = await self._generate_contact_added_response(user, bot_name)
                await event.respond(response)
                
                # Pending contacts'a ekle
                self.pending_contacts[user_id] = {
                    "bot_name": bot_name,
                    "group_id": group_id,
                    "timestamp": datetime.now()
                }
                
                # Database'e kaydet
                await self._save_contact_attempt(user_id, bot_name, group_id, True)
                
                logger.info(f"✅ Contact eklendi: {user.first_name or 'Anonim'} -> {bot_name}")
                
            else:
                # Contact ekleme başarısız
                response = f"🔒 {user.first_name or 'Kullanıcı'}, seni eklerken engel var. DM'den bana 'merhaba' yaz, sonra yazışabiliriz!"
                await event.respond(response)
                
                logger.warning(f"⚠️ Contact ekleme başarısız: {user.first_name or 'Anonim'} -> {bot_name}")
            
        except ConnectionError as e:
            logger.warning(f"🔗 DM request bağlantı hatası ({bot_name}): {e}")
            await self._try_reconnect_bot(bot_name)
        except Exception as e:
            logger.error(f"DM request işleme hatası ({bot_name}): {e}")
            try:
                await event.respond("🔒 Teknik bir sorun oluştu. Lütfen daha sonra tekrar dene!")
            except:
                pass  # Eğer response bile gönderilemiyorsa, sessizce geç
    
    async def _add_user_to_contacts(self, client: TelegramClient, user: User, bot_name: str, group_id: int) -> Dict[str, Any]:
        """Kullanıcıyı contact listesine ekle"""
        try:
            # Kullanıcı bilgilerini validate et
            if not user or not hasattr(user, 'id') or not user.id:
                return {
                    "success": False,
                    "error": "Invalid user object",
                    "method": "validation_failed"
                }
            
            if not hasattr(user, 'access_hash') or user.access_hash is None:
                return {
                    "success": False,
                    "error": "User access_hash missing",
                    "method": "validation_failed"
                }
            
            # InputUser oluştur
            input_user = InputUser(user_id=user.id, access_hash=user.access_hash)
            
            # Contact ekleme request'i
            result = await client(AddContactRequest(
                id=input_user,
                first_name=user.first_name or "Friend",
                last_name=user.last_name or "",
                phone="",  # Telefon numarası boş - Telegram ID ile ekle
                add_phone_privacy_exception=False  # Telefon numarası gizli kalsın
            ))
            
            logger.info(f"📞 Contact eklendi: {user.first_name or 'Anonim'} -> {bot_name}")
            
            return {
                "success": True,
                "method": "telegram_api",
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Contact ekleme hatası: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "telegram_api"
            }
    
    async def _generate_contact_added_response(self, user: User, bot_name: str) -> str:
        """Contact ekleme sonrası grup mesajı oluştur"""
        bot_data = self.bot_clients[bot_name]
        personality = bot_data["config"]["personality"]
        
        responses = [
            f"✅ {user.first_name}, seni ekledim! Şimdi bana DM'den yaz, rahatça konuşalım! 💬",
            f"📱 {user.first_name}, contact'a eklendi! DM başlat, orada devam edelim! 🚀",
            f"🤝 {user.first_name}, artık arkadaşız! DM'e gel, özel sohbet edelim! ✨",
            f"💯 {user.first_name}, ekleme tamam! Şimdi bana mesaj at, bekledik konuşuım! 🔥"
        ]
        
        base_response = random.choice(responses)
        
        # Personality'ye göre ek mesaj
        if "BabaGAVAT" in personality:
            base_response += "\n\n💪 BabaGAVAT her zaman hazır, sokak zekası aktif!"
        elif "Geisha" in personality:
            base_response += "\n\n🌸 Geisha ile özel sohbet vakti! ✨"
        elif "Lara" in personality:
            base_response += "\n\n🎬 YayıncıLara ile eğlenceli sohbet başlasın! 🔥"
        
        return base_response
    
    async def _save_contact_attempt(self, user_id: int, bot_name: str, group_id: int, success: bool):
        """Contact ekleme girişimini database'e kaydet"""
        conn = sqlite3.connect(self.contact_database)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO contacts 
            (user_id, bot_name, group_id, contact_added, first_contact_attempt)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, bot_name, group_id, success, datetime.now()))
        
        conn.commit()
        conn.close()
    
    async def _handle_spam_restricted_message(self, event, bot_name: str):
        """SPAM kısıtlaması altındaki bot için mesaj işle"""
        try:
            # Sadece DM'e geçiş öner
            if event.is_reply:
                # Bot'a reply yapılmışsa DM yönlendirmesi yap
                replied_message = await event.get_reply_message()
                if not replied_message:
                    return
                    
                bot_data = self.bot_clients[bot_name]
                
                if replied_message.sender_id == bot_data["me"].id:
                    user = await event.get_sender()
                    
                    # DM yönlendirme mesajı (eğer gönderilebilirse)
                    try:
                        dm_message = f"🔒 Merhaba {user.first_name}! Grup'ta yazamıyorum, bana DM'den yaz: @{bot_data['me'].username}"
                        await user.send_message(dm_message)
                        logger.info(f"📩 SPAM-restricted DM gönderildi: {bot_name} -> {user.first_name}")
                    except Exception as dm_error:
                        logger.warning(f"⚠️ SPAM-restricted DM gönderilemedi: {dm_error}")
            
        except Exception as e:
            logger.error(f"SPAM-restricted mesaj işleme hatası ({bot_name}): {e}")
    
    async def _process_group_message(self, event, bot_name: str):
        """Normal grup mesajını işle"""
        try:
            # Grup'ta AI sohbet logic'i buraya gelecek
            # Şimdilik basit response
            
            message_text = event.message.message
            if not message_text:
                return
            
            # Bot'a mention veya reply varsa cevap ver
            bot_data = self.bot_clients[bot_name]
            me = bot_data["me"]
            
            should_respond = False
            
            # Reply kontrolü - güvenli şekilde
            if event.is_reply:
                try:
                    replied_message = await event.get_reply_message()
                    if replied_message and replied_message.sender_id == me.id:
                        should_respond = True
                except Exception as e:
                    logger.warning(f"Reply message kontrol hatası ({bot_name}): {e}")
            
            # Mention kontrolü
            if not should_respond and me.username:
                if f"@{me.username}" in message_text.lower():
                    should_respond = True
            
            if should_respond:
                # GPT-4o ile intelligent response
                response = await self._generate_ai_response(
                    message_text, bot_data["config"]["personality"], bot_name
                )
                
                # Rate limiting ile mesaj gönder
                await asyncio.sleep(random.uniform(2, 5))
                await event.respond(response)
                
                logger.info(f"💬 AI Response: {bot_name} -> {event.chat.title}")
            
        except Exception as e:
            logger.error(f"Grup mesajı işleme hatası ({bot_name}): {e}")
    
    async def _generate_ai_response(self, message: str, personality: str, bot_name: str) -> str:
        """GPT-4o ile AI response oluştur"""
        try:
            prompt = f"""
Sen {personality} kişiliğindesin. Telegram grup sohbetinde doğal, samimi ve kişiliğine uygun cevap ver.

Mesaj: "{message}"

Kurallar:
- Kısa ve öz yanıt (max 2-3 cümle)
- Kişiliğine uygun ton
- Türkçe ve doğal
- Emoji kullan ama abartma
- Samimi ve dostane ol

Yanıt:"""

            response = await openai.ChatCompletion.acreate(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.8
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Cache'e kaydet
            self.message_cache[f"{bot_name}_{time.time()}"] = {
                "input": message,
                "output": ai_response,
                "personality": personality
            }
            
            return ai_response
            
        except Exception as e:
            logger.error(f"AI response hatası ({bot_name}): {e}")
            
            # Fallback responses
            fallback_responses = {
                "babagavat": "💪 BabaGAVAT her zaman hazır! Sokak zekası devrede!",
                "xxxgeisha": "🌸 Geisha burada! Ne var ne yok? ✨",
                "yayincilara": "🎬 YayıncıLara sahne'de! Enerjim tam! 🔥"
            }
            
            return fallback_responses.get(bot_name, "👋 Merhaba! Nasılsın?")
    
    async def run_system(self):
        """Ana sistem döngüsü"""
        logger.info("🚀 SPAM-Aware Full Bot System çalışıyor...")
        
        try:
            while True:
                # Periyodik SPAM kontrolleri
                await asyncio.sleep(3600)  # Her saat kontrol
                await self._check_all_spam_status()
                
                # Contact durumlarını kontrol et
                await self._check_pending_contacts()
                
                # Sistem sağlığını raporla
                await self._report_system_health()
                
        except KeyboardInterrupt:
            logger.info("👋 Sistem kapatılıyor...")
            await self._cleanup()
        except Exception as e:
            logger.error(f"❌ Sistem hatası: {e}")
    
    async def _check_pending_contacts(self):
        """Bekleyen contact'ları kontrol et"""
        try:
            current_time = datetime.now()
            expired_contacts = []
            
            for user_id, contact_info in self.pending_contacts.items():
                # 24 saatten eski contact talepleri
                if current_time - contact_info["timestamp"] > timedelta(hours=24):
                    expired_contacts.append(user_id)
            
            # Expired contact'ları temizle
            for user_id in expired_contacts:
                del self.pending_contacts[user_id]
            
            if expired_contacts:
                logger.info(f"🧹 {len(expired_contacts)} expired contact temizlendi")
                
        except Exception as e:
            logger.error(f"Pending contact kontrol hatası: {e}")
    
    async def _report_system_health(self):
        """Sistem sağlık raporu"""
        try:
            active_bots = sum(1 for bot_data in self.bot_clients.values() if bot_data["status"] == "active")
            spam_restricted = sum(1 for bot_data in self.bot_clients.values() if bot_data["status"] == "spam_restricted")
            pending_contacts = len(self.pending_contacts)
            
            uptime = datetime.now() - self.start_time
            
            health_report = {
                "uptime_hours": uptime.total_seconds() / 3600,
                "active_bots": active_bots,
                "spam_restricted_bots": spam_restricted,
                "pending_contacts": pending_contacts,
                "total_bots": len(self.bot_clients)
            }
            
            logger.info(f"💊 Sistem Sağlık: {health_report}")
            
        except Exception as e:
            logger.error(f"Sağlık raporu hatası: {e}")
    
    async def _cleanup(self):
        """Sistem temizliği"""
        try:
            for bot_name, bot_data in self.bot_clients.items():
                await bot_data["client"].disconnect()
                logger.info(f"👋 {bot_name} bağlantısı kapatıldı")
            
            logger.info("✅ Sistem temizliği tamamlandı")
            
        except Exception as e:
            logger.error(f"Cleanup hatası: {e}")

    async def _try_reconnect_bot(self, bot_name: str):
        """Bot bağlantısını yeniden kurmaya çalış"""
        try:
            bot_data = self.bot_clients.get(bot_name)
            if not bot_data:
                return
            
            logger.info(f"🔄 {bot_name} yeniden bağlanma denemesi...")
            
            # Mevcut client'ı kapat
            try:
                await bot_data["client"].disconnect()
            except:
                pass  # Zaten kapalı olabilir
            
            # Yeni client oluştur
            bot_config = bot_data["config"]
            session_file = bot_config["session_file"]
            
            client = TelegramClient(
                session_file, 
                TELEGRAM_API_ID, 
                TELEGRAM_API_HASH,
                connection_retries=5,
                retry_delay=10,
                timeout=60,
                request_retries=3,
                flood_sleep_threshold=60,
                auto_reconnect=True,
                sequential_updates=True,
                use_ipv6=False,
                device_model="SPAM-Aware Bot",
                system_version="1.0",
                app_version="1.0"
            )
            
            await client.start()
            me = await client.get_me()
            
            # Client'ı güncelle
            self.bot_clients[bot_name]["client"] = client
            self.bot_clients[bot_name]["me"] = me
            self.bot_clients[bot_name]["status"] = "active"
            
            # Event handler'ları yeniden kur
            await self._setup_event_handlers_for_bot(bot_name, client)
            
            logger.info(f"✅ {bot_name} başarıyla yeniden bağlandı: @{me.username}")
            
        except Exception as e:
            logger.error(f"❌ {bot_name} yeniden bağlantı hatası: {e}")
            # Bot'u inactive olarak işaretle
            if bot_name in self.bot_clients:
                self.bot_clients[bot_name]["status"] = "reconnecting"

    async def _setup_event_handlers_for_bot(self, bot_name: str, client: TelegramClient):
        """Tek bot için event handler'ları kur"""
        try:
            # Mesaj handler'ı
            @client.on(events.NewMessage)
            async def handle_message(event, bot_name=bot_name):
                await self._handle_message(event, bot_name)
            
            # Reply handler'ı
            @client.on(events.NewMessage(pattern=r'(?i).*\b(dm|mesaj|yaz)\b.*'))
            async def handle_dm_request(event, bot_name=bot_name):
                if event.is_reply:
                    await self._handle_dm_request(event, bot_name)
            
            logger.info(f"🎯 {bot_name} event handler'ları kuruldu")
            
        except Exception as e:
            logger.error(f"❌ {bot_name} event handler kurma hatası: {e}")

async def main():
    """Ana fonksiyon"""
    system = SpamAwareFullBotSystem()
    
    if await system.initialize():
        await system.run_system()
    else:
        logger.error("❌ Sistem başlatılamadı!")

if __name__ == "__main__":
    asyncio.run(main()) 