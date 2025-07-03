#!/usr/bin/env python3
# handlers/spam_handler.py

import asyncio
from datetime import datetime
from telethon import TelegramClient, events
from handlers.safe_spam_handler import safe_spam_handler
from utilities.log_utils import log_event
from core.db.connection import get_db_session
from core.profile_manager import profile_manager
import structlog

logger = structlog.get_logger("gavatcore.spam_handler")

async def setup_spam_handlers(client: TelegramClient, username: str):
    """Spam handler'ları setup et"""
    try:
        logger.info(f"🚀 Spam handler'lar kurulumu başlatıldı: {username}")
        
        # Profil bilgisini al
        profile = await profile_manager.get_profile(username)
        
        if not profile:
            logger.warning(f"⚠️ Profil bulunamadı: {username}")
            return
        
        # Spam aktif mi kontrol et
        if profile.get("is_spam_active", False):
            # Safe spam loop'u başlat
            await safe_spam_handler.start_safe_spam_loop(client, username, profile)
            logger.info(f"✅ Spam döngüsü başlatıldı: {username}")
        else:
            logger.info(f"ℹ️ Spam deaktif: {username}")
        
        # Event handler'ları ekle
        @client.on(events.ChatAction)
        async def chat_action_handler(event):
            """Chat action handler (ban, kick vs.)"""
            try:
                # Ban kontrolü - ChatBannedRights veya UserBannedInChannelError
                if hasattr(event, 'action_message') and event.action_message:
                    if hasattr(event.action_message, 'action') and event.action_message.action:
                        if getattr(event.action_message.action, 'banned_rights', None):
                            from utilities.anti_spam_guard import anti_spam_guard
                            anti_spam_guard.add_spam_warning(username, "banned_from_group")
                            log_event(username, f"🚫 Gruptan banlandı: {event.chat_id}")
                            
                            # CRM'e kaydet
                            from core.crm_database import crm_db
                            await crm_db.add_customer({
                                "id": event.chat_id,
                                "username": f"banned_group_{event.chat_id}",
                                "type": "banned_group",
                                "status": "banned",
                                "last_interaction": datetime.now()
                            })
                    
            except Exception as e:
                logger.error(f"Chat action handler error: {e}")
        
        logger.info(f"✅ Spam handler'lar başarıyla kuruldu: {username}")
        
    except Exception as e:
        logger.error(f"❌ Spam handler kurulum hatası ({username}): {e}")
        log_event(username, f"❌ Spam handler kurulum hatası: {e}")

async def stop_spam_handler(username: str):
    """Spam handler'ı durdur"""
    try:
        await safe_spam_handler.stop_safe_spam_loop(username)
        logger.info(f"✅ Spam handler durduruldu: {username}")
    except Exception as e:
        logger.error(f"❌ Spam handler durdurma hatası ({username}): {e}")

async def get_spam_stats(username: str):
    """Spam istatistiklerini al"""
    return safe_spam_handler.get_spam_statistics(username) 