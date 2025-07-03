#!/usr/bin/env python3
# handlers/gpt_messaging_handler.py - GPT destekli mesajlaşma işleyicisi

import asyncio
import random
from datetime import datetime
from typing import Optional, List, Dict, Any
from telethon.tl.types import Channel, Chat
from gpt.flirt_generator import generate_flirty_message
from gpt.group_reply_agent import generate_mention_reply, detect_mention
from utilities.message_context_collector import extract_group_context, format_context_for_prompt
from utilities.log_utils import log_event
from core.analytics_logger import log_analytics
from config import OPENAI_API_KEY

class GPTMessagingHandler:
    def __init__(self):
        self.recent_messages_cache = {}  # {dialog_id: [messages]}
        self.last_context_analysis = {}  # {dialog_id: context}
        self.message_history_limit = 20
        
        # Anti-spam ayarları
        self.min_message_interval = 30  # saniye
        self.max_messages_per_hour = 10
        self.message_timestamps = {}  # {dialog_id: [timestamps]}
        
        # GPT availability check
        self.gpt_enabled = bool(OPENAI_API_KEY)
        if self.gpt_enabled:
            log_event("gpt_messaging", "✅ GPT messaging handler aktif")
        else:
            log_event("gpt_messaging", "⚠️ OpenAI API key yok, sadece fallback mesajlar kullanılacak")
    
    async def start_gpt_messaging_loop(
        self, 
        client, 
        username: str, 
        profile: Dict
    ):
        """
        GPT messaging loop'unu başlatır
        
        Args:
            client: Telegram client
            username: Bot kullanıcı adı
            profile: Bot profil bilgileri
        """
        
        if not self.gpt_enabled:
            log_event("gpt_messaging", f"⚠️ {username} için GPT devre dışı")
            return
        
        # GPT özelliklerini kontrol et
        gpt_enhanced = profile.get("gpt_enhanced", False)
        if not gpt_enhanced:
            log_event("gpt_messaging", f"ℹ️ {username} için GPT enhanced aktif değil")
            return
        
        log_event("gpt_messaging", f"🚀 {username} için GPT messaging loop başlatıldı")
        
        # Background task olarak çalıştır
        asyncio.create_task(self._gpt_messaging_background_loop(client, username, profile))
    
    async def _gpt_messaging_background_loop(
        self, 
        client, 
        username: str, 
        profile: Dict
    ):
        """GPT messaging background loop"""
        
        while True:
            try:
                # Profile'ı yeniden yükle
                from pathlib import Path
                import json
                
                profile_path = Path(f"data/personas/{username}.json")
                if profile_path.exists():
                    with open(profile_path, "r", encoding="utf-8") as f:
                        current_profile = json.load(f)
                    
                    # GPT enhanced hala aktif mi?
                    if not current_profile.get("gpt_enhanced", False):
                        log_event("gpt_messaging", f"🛑 {username} GPT enhanced kapatıldı")
                        break
                    
                    profile = current_profile
                else:
                    log_event("gpt_messaging", f"⚠️ {username} profil dosyası bulunamadı")
                    break
                
                # Dialogs'ları al ve GPT mesajları gönder
                dialogs = await client.get_dialogs()
                
                for dialog in dialogs:
                    if not dialog.is_group:
                        continue
                    
                    # GPT mesajı gönder
                    await self.safe_gpt_message_loop(
                        bot=client,
                        dialog=dialog,
                        username=username,
                        bot_profile=profile
                    )
                    
                    # Dialogs arası bekleme
                    await asyncio.sleep(random.uniform(5, 15))
                
                # Döngü arası bekleme (30-60 dakika)
                await asyncio.sleep(random.uniform(1800, 3600))
                
            except Exception as e:
                log_event("gpt_messaging", f"❌ {username} GPT background loop hatası: {e}")
                await asyncio.sleep(300)  # 5 dakika bekle
    
    async def safe_gpt_message_loop(
        self, 
        bot, 
        dialog, 
        username: str,
        bot_profile: Optional[Dict] = None
    ) -> bool:
        """
        Güvenli GPT mesaj gönderme döngüsü
        
        Args:
            bot: Telegram client
            dialog: Hedef dialog
            username: Bot kullanıcı adı
            bot_profile: Bot profil bilgileri
        
        Returns:
            Mesaj gönderildi mi
        """
        
        try:
            dialog_id = dialog.id
            
            # Anti-spam kontrolü
            if not self._check_anti_spam_limits(dialog_id):
                log_event("gpt_messaging", f"⚠️ Anti-spam limiti: {dialog.title}")
                return False
            
            # Grup bağlamını analiz et
            group_context = await self._analyze_group_context(bot, dialog, dialog_id)
            
            # Zaman bağlamını belirle
            time_context = self._get_time_context()
            
            # Mention kontrolü - son mesajlarda bot mention'ı var mı
            has_mention = await self._check_recent_mentions(bot, dialog, username)
            
            if has_mention:
                # Mention'a yanıt ver
                success = await self._handle_mention_reply(
                    bot, dialog, username, group_context
                )
            else:
                # Normal flört mesajı gönder
                success = await self._send_flirty_message(
                    bot, dialog, username, time_context, group_context, bot_profile
                )
            
            if success:
                # Timestamp'i kaydet
                self._record_message_timestamp(dialog_id)
                
                log_event("gpt_messaging", f"✅ GPT mesaj gönderildi: {dialog.title}")
                log_analytics(username, "gpt_message_sent", {
                    "dialog_title": dialog.title,
                    "dialog_id": dialog_id,
                    "message_type": "mention_reply" if has_mention else "flirty",
                    "time_context": time_context,
                    "group_context": group_context.get("dominant_theme") if group_context else None
                })
                
                return True
            
        except Exception as e:
            log_event("gpt_messaging", f"❌ GPT mesaj hatası: {e}")
            log_analytics(username, "gpt_message_failed", {
                "dialog_title": getattr(dialog, 'title', 'Unknown'),
                "error": str(e)
            })
        
        return False
    
    async def _analyze_group_context(
        self, 
        bot, 
        dialog, 
        dialog_id: int
    ) -> Optional[Dict[str, Any]]:
        """Grup bağlamını analiz eder"""
        
        try:
            # Cache'den kontrol et
            if dialog_id in self.last_context_analysis:
                last_analysis_time = self.last_context_analysis[dialog_id].get("timestamp", 0)
                # 10 dakikadan eski değilse cache'i kullan
                if datetime.now().timestamp() - last_analysis_time < 600:
                    return self.last_context_analysis[dialog_id]["context"]
            
            # Son mesajları al
            recent_messages = []
            async for message in bot.iter_messages(dialog, limit=self.message_history_limit):
                if message.text:
                    recent_messages.append(message.text)
            
            # Cache'e kaydet
            self.recent_messages_cache[dialog_id] = recent_messages
            
            # Bağlam analizi
            if recent_messages:
                context = await extract_group_context(recent_messages)
                
                # Cache'e timestamp ile kaydet
                self.last_context_analysis[dialog_id] = {
                    "context": context,
                    "timestamp": datetime.now().timestamp()
                }
                
                return context
            
        except Exception as e:
            log_event("gpt_messaging", f"⚠️ Bağlam analizi hatası: {e}")
        
        return None
    
    async def _check_recent_mentions(
        self, 
        bot, 
        dialog, 
        username: str,
        check_limit: int = 5
    ) -> bool:
        """Son mesajlarda mention var mı kontrol eder"""
        
        try:
            async for message in bot.iter_messages(dialog, limit=check_limit):
                if message.text and detect_mention(message.text, username):
                    # Mention bulundu ve 5 dakikadan yeni
                    if (datetime.now() - message.date).total_seconds() < 300:
                        return True
            
        except Exception as e:
            log_event("gpt_messaging", f"⚠️ Mention kontrolü hatası: {e}")
        
        return False
    
    async def _handle_mention_reply(
        self, 
        bot, 
        dialog, 
        username: str, 
        group_context: Optional[Dict]
    ) -> bool:
        """Mention'a yanıt verir"""
        
        try:
            # Son mention'ı bul
            mention_message = None
            sender_name = None
            
            async for message in bot.iter_messages(dialog, limit=10):
                if message.text and detect_mention(message.text, username):
                    mention_message = message.text
                    sender_name = message.sender.first_name if message.sender else None
                    break
            
            if not mention_message:
                return False
            
            # Grup bağlamını formatla
            context_prompt = None
            if group_context:
                context_prompt = format_context_for_prompt(group_context)
            
            # GPT ile yanıt üret
            reply = await generate_mention_reply(
                message=mention_message,
                bot_name=username,
                sender_name=sender_name,
                group_context=context_prompt
            )
            
            # Yanıtı gönder
            await bot.send_message(dialog, reply)
            
            log_event("gpt_messaging", f"💬 Mention yanıtı: {reply[:50]}...")
            return True
            
        except Exception as e:
            log_event("gpt_messaging", f"❌ Mention yanıt hatası: {e}")
            return False
    
    async def _send_flirty_message(
        self, 
        bot, 
        dialog, 
        username: str, 
        time_context: str,
        group_context: Optional[Dict],
        bot_profile: Optional[Dict]
    ) -> bool:
        """Flört mesajı gönderir"""
        
        try:
            # Grup bağlamını formatla
            context_prompt = None
            if group_context:
                context_prompt = format_context_for_prompt(group_context)
            
            # Son gönderilen mesajları al (tekrar önlemek için)
            dialog_id = dialog.id
            recent_messages = self.recent_messages_cache.get(dialog_id, [])
            avoid_phrases = []
            
            # Son 3 mesajdan anahtar kelimeleri çıkar
            for msg in recent_messages[:3]:
                words = msg.lower().split()
                avoid_phrases.extend([word for word in words if len(word) > 4])
            
            # GPT ile flört mesajı üret
            flirty_message = await generate_flirty_message(
                username=username,
                time_context=time_context,
                group_context=context_prompt,
                avoid_phrases=avoid_phrases[:10]  # İlk 10 kelime
            )
            
            # Mesajı gönder
            await bot.send_message(dialog, flirty_message)
            
            log_event("gpt_messaging", f"💕 Flört mesajı: {flirty_message[:50]}...")
            return True
            
        except Exception as e:
            log_event("gpt_messaging", f"❌ Flört mesajı hatası: {e}")
            return False
    
    def _get_time_context(self) -> str:
        """Zaman bağlamını döndürür"""
        now = datetime.now()
        hour = now.hour
        
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "midday"
        elif 18 <= hour < 23:
            return "evening"
        else:
            return "late_night"
    
    def _check_anti_spam_limits(self, dialog_id: int) -> bool:
        """Anti-spam limitlerini kontrol eder"""
        
        current_time = datetime.now().timestamp()
        
        # Dialog için timestamp listesi
        if dialog_id not in self.message_timestamps:
            self.message_timestamps[dialog_id] = []
        
        timestamps = self.message_timestamps[dialog_id]
        
        # 1 saat öncesinden eski timestamp'leri temizle
        timestamps[:] = [ts for ts in timestamps if current_time - ts < 3600]
        
        # Saatlik limit kontrolü
        if len(timestamps) >= self.max_messages_per_hour:
            return False
        
        # Son mesajdan beri geçen süre kontrolü
        if timestamps and current_time - timestamps[-1] < self.min_message_interval:
            return False
        
        return True
    
    def _record_message_timestamp(self, dialog_id: int):
        """Mesaj timestamp'ini kaydet"""
        current_time = datetime.now().timestamp()
        
        if dialog_id not in self.message_timestamps:
            self.message_timestamps[dialog_id] = []
        
        self.message_timestamps[dialog_id].append(current_time)
    
    async def handle_group_message_event(
        self, 
        event, 
        bot, 
        username: str
    ) -> bool:
        """
        Grup mesajı event'ini işler (mention kontrolü için)
        
        Args:
            event: Telegram message event
            bot: Telegram client
            username: Bot kullanıcı adı
        
        Returns:
            Yanıt verildi mi
        """
        
        try:
            # Sadece grup mesajları
            if not event.is_group:
                return False
            
            # Bot mention'ı var mı
            if not event.text or not detect_mention(event.text, username):
                return False
            
            # Kendi mesajımız değil
            me = await bot.get_me()
            if event.sender_id == me.id:
                return False
            
            # Yanıt üret ve gönder
            sender_name = None
            if event.sender:
                sender_name = event.sender.first_name
            
            reply = await generate_mention_reply(
                message=event.text,
                bot_name=username,
                sender_name=sender_name
            )
            
            # Kısa bir gecikme (doğal görünmek için)
            await asyncio.sleep(random.uniform(1, 3))
            
            await event.respond(reply)
            
            log_event("gpt_messaging", f"🎯 Event mention yanıtı: {reply[:50]}...")
            log_analytics(username, "gpt_mention_reply", {
                "group_id": event.chat_id,
                "sender_name": sender_name,
                "original_message": event.text[:100],
                "reply": reply
            })
            
            return True
            
        except Exception as e:
            log_event("gpt_messaging", f"❌ Event işleme hatası: {e}")
            return False
    
    def get_dialog_stats(self, dialog_id: int) -> Dict[str, Any]:
        """Dialog istatistiklerini döndürür"""
        
        timestamps = self.message_timestamps.get(dialog_id, [])
        current_time = datetime.now().timestamp()
        
        # Son 1 saat içindeki mesajlar
        recent_messages = [ts for ts in timestamps if current_time - ts < 3600]
        
        # Son mesajdan beri geçen süre
        last_message_ago = None
        if timestamps:
            last_message_ago = int(current_time - timestamps[-1])
        
        return {
            "total_messages": len(timestamps),
            "messages_last_hour": len(recent_messages),
            "last_message_seconds_ago": last_message_ago,
            "can_send_message": self._check_anti_spam_limits(dialog_id)
        }

# Global GPT messaging handler instance
gpt_messaging_handler = GPTMessagingHandler()

async def safe_gpt_message_loop(
    bot, 
    dialog, 
    username: str,
    bot_profile: Optional[Dict] = None
) -> bool:
    """
    Global GPT mesaj gönderme fonksiyonu
    
    Args:
        bot: Telegram client
        dialog: Hedef dialog
        username: Bot kullanıcı adı
        bot_profile: Bot profil bilgileri
    
    Returns:
        Mesaj gönderildi mi
    """
    return await gpt_messaging_handler.safe_gpt_message_loop(
        bot=bot,
        dialog=dialog,
        username=username,
        bot_profile=bot_profile
    )

async def handle_group_message_event(
    event, 
    bot, 
    username: str
) -> bool:
    """
    Global grup mesajı event işleyici
    
    Args:
        event: Telegram message event
        bot: Telegram client
        username: Bot kullanıcı adı
    
    Returns:
        Yanıt verildi mi
    """
    return await gpt_messaging_handler.handle_group_message_event(
        event=event,
        bot=bot,
        username=username
    ) 