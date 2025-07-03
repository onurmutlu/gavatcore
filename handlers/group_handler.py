#!/usr/bin/env python3
"""
👥 Group Handler - Grup yönetimi
"""
from telethon import events
from core.controller import Controller
import structlog
import time
from handlers.gpt_messaging_handler import gpt_messaging_handler

logger = structlog.get_logger("gavatcore.group_handler")

# Cooldown ayarları
GROUP_COOLDOWN_SECONDS = 60  # 1 dakika
GROUP_MAX_MESSAGES_PER_HOUR = 5
GROUP_TRACKING_WINDOW = 3600  # 1 saat

USER_REPLY_COOLDOWN = 60  # 1 dakika
GROUP_REPLY_COOLDOWN = 60  # 1 dakika

# Cooldown takibi
reply_cooldowns = {}  # {group_id: last_message_time}
group_message_counts = {}  # {group_id: [timestamps]}

group_reply_cooldowns = reply_cooldowns

processed_messages = set()  # İşlenmiş mesaj ID'lerini tutar

CONVERSATION_COOLDOWN = 300  # 5 dakika

class GroupHandler:
    def __init__(self, controller: Controller):
        self.controller = controller
        
    async def handle_group_message(self, event: events.NewMessage.Event):
        """Grup mesajlarını işle"""
        try:
            # Mesaj içeriğini al
            message = event.message.text
            
            # Komut kontrolü
            if message.startswith('/'):
                await self.handle_group_command(event)
                return
                
            # Normal mesaj işleme
            await self.process_group_message(event)
            
        except Exception as e:
            print(f"Group Handler Error: {e}")
            
    async def handle_group_command(self, event: events.NewMessage.Event):
        """Grup komutlarını işle"""
        try:
            # Komut işleme mantığı
            pass
        except Exception as e:
            print(f"Group Command Error: {e}")
            
    async def process_group_message(self, event: events.NewMessage.Event):
        """Grup mesajlarını işle"""
        try:
            # Mesaj işleme mantığı
            pass
        except Exception as e:
            print(f"Group Message Processing Error: {e}")
            
    async def handle_group_action(self, event: events.ChatAction.Event):
        """Grup aksiyonlarını işle (katılma, ayrılma vb.)"""
        try:
            # Aksiyon işleme mantığı
            pass
        except Exception as e:
            print(f"Group Action Error: {e}")

async def handle_group_message(group_id: int, message: str) -> str:
    """Grup mesajını işler ve yanıt döndürür."""
    try:
        # Cooldown kontrolü
        current_time = time.time()
        last_message_time = reply_cooldowns.get(group_id, 0)
        if current_time - last_message_time < GROUP_COOLDOWN_SECONDS:
            return ""
            
        # Mesaj sayısı kontrolü
        if group_id not in group_message_counts:
            group_message_counts[group_id] = []
        group_message_counts[group_id].append(current_time)
        
        # Eski mesajları temizle
        group_message_counts[group_id] = [
            t for t in group_message_counts[group_id]
            if current_time - t < GROUP_TRACKING_WINDOW
        ]
        
        if len(group_message_counts[group_id]) > GROUP_MAX_MESSAGES_PER_HOUR:
            return ""
            
        # Cooldown'ı güncelle
        reply_cooldowns[group_id] = current_time
        
        # GPT yanıtı oluştur
        return await gpt_messaging_handler(message)
        
    except Exception as e:
        logger.error(f"Grup mesajı işleme hatası: {e}")
        return ""

def _check_reply_cooldown(group_id: int) -> bool:
    """Grup için reply cooldown kontrolü yapar."""
    current_time = time.time()
    last_message_time = reply_cooldowns.get(group_id, 0)
    if current_time - last_message_time < GROUP_COOLDOWN_SECONDS:
        return False
    return True

def _update_reply_cooldown(group_id: int):
    """Grup için reply cooldown'ı günceller."""
    reply_cooldowns[group_id] = time.time() 