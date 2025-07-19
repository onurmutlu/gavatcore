from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🛡️ Safe Spam Handler - Spam koruma sistemi
"""
from telethon import events
from core.controller import Controller
from core.anti_spam_system import AntiSpamSystem
import structlog

class SafeSpamHandler:
    def __init__(self, controller: Controller, anti_spam: AntiSpamSystem):
        self.controller = controller
        self.anti_spam = anti_spam
        
    async def handle_message(self, event: events.NewMessage.Event):
        """Mesajları spam kontrolünden geçir"""
        try:
            # Spam kontrolü
            if await self.anti_spam.is_spam(event):
                await self.handle_spam(event)
                return False
                
            return True
            
        except Exception as e:
            print(f"Spam Handler Error: {e}")
            return True
            
    async def handle_spam(self, event: events.NewMessage.Event):
        """Spam mesajlarını işle"""
        try:
            # Spam işleme mantığı
            await event.delete()
            await event.respond("Spam tespit edildi! Mesaj silindi.")
            
        except Exception as e:
            print(f"Spam Processing Error: {e}")
            
    async def update_spam_rules(self):
        """Spam kurallarını güncelle"""
        try:
            # Kural güncelleme mantığı
            pass
        except Exception as e:
            print(f"Spam Rules Update Error: {e}")

logger = structlog.get_logger("gavatcore.safe_spam_handler")

async def safe_spam_handler(message: str, user_id: int) -> bool:
    """
    Mesajın spam olup olmadığını kontrol eder.
    
    Args:
        message (str): Kontrol edilecek mesaj
        user_id (int): Kullanıcı ID'si
        
    Returns:
        bool: Mesaj güvenli ise True, değilse False
    """
    try:
        # Spam kelimeleri listesi
        spam_keywords = [
            "spam", "reklam", "kazan", "bedava", "ücretsiz",
            "fırsat", "indirim", "kampanya", "lottery", "çekiliş"
        ]
        
        # Mesajı küçük harfe çevir
        message_lower = message.lower()
        
        # Spam kelimelerini kontrol et
        for keyword in spam_keywords:
            if keyword in message_lower:
                logger.warning(f"Spam tespit edildi: {keyword} - User: {user_id}")
                return False
        
        # Mesaj uzunluğu kontrolü
        if len(message) > 1000:  # 1000 karakterden uzun mesajlar
            logger.warning(f"Çok uzun mesaj: {len(message)} karakter - User: {user_id}")
            return False
            
        # Mesaj güvenli
        return True
        
    except Exception as e:
        logger.error(f"Spam kontrolü hatası: {e}")
        return False 