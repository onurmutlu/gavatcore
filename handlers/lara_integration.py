#!/usr/bin/env python3
"""
LARA BOT INTEGRATION - GAVATCore Entegrasyonu
============================================

Lara bot'unu mevcut GAVATCore sistemiyle entegre eder.
Mevcut dm_handler ve group_handler yapısına Lara karakterini ekler.

Bu dosya ile:
- Mevcut bot sistemlerine Lara karakteri eklenir
- Lara prompt'u kullanılır
- Flörtöz davranışlar aktif olur
- VIP satış sistemi çalışır
"""

import asyncio
import random
from typing import Dict, Any, Optional
import structlog

# Core imports
from handlers.lara_bot_handler import (
    handle_lara_dm, 
    handle_lara_group_message, 
    get_lara_stats,
    LaraConfig
)
from gpt.prompts.larabot_prompt import LaraPromptUtils
from utils.log_utils import log_event
try:
    from core.analytics_logger import log_analytics
except ImportError:
    # Fallback fonksiyon
    def log_analytics(source: str, event: str, data: dict = None):
        log_event(source, f"{event}: {data}")

logger = structlog.get_logger("lara_integration")

# ==================== BOT PROFILE DETECTION ====================

def is_lara_bot(bot_username: str, bot_profile: Optional[Dict] = None) -> bool:
    """Bir bot'un Lara karakteri olup olmadığını kontrol et"""
    
    # Username kontrolü
    if "lara" in bot_username.lower():
        return True
    
    # Profile kontrolü
    if bot_profile:
        # Persona tipine bak
        if bot_profile.get("type") == "lara_bot":
            return True
        
        # Display name kontrolü
        display_name = bot_profile.get("display_name", "").lower()
        if "lara" in display_name:
            return True
        
        # Karakter özelliği kontrolü
        personality = bot_profile.get("personality", [])
        if any("lara" in trait.lower() for trait in personality):
            return True
    
    return False

# ==================== DM INTEGRATION ====================

async def integrate_lara_dm_handler(
    client, 
    sender, 
    message_text: str, 
    bot_username: str,
    bot_profile: Optional[Dict] = None
) -> bool:
    """
    DM handler'a Lara entegrasyonu
    
    Args:
        client: Telegram client
        sender: Mesaj gönderen kullanıcı
        message_text: Mesaj içeriği
        bot_username: Bot kullanıcı adı
        bot_profile: Bot profil bilgileri
    
    Returns:
        Lara tarafından işlendi mi
    """
    try:
        # Lara bot kontrolü
        if not is_lara_bot(bot_username, bot_profile):
            return False
        
        logger.info(f"🌹 Lara DM entegrasyonu: {sender.first_name} -> {message_text[:30]}...")
        
        # Lara handler'ını çağır
        success = await handle_lara_dm(client, sender, message_text)
        
        if success:
            log_analytics("lara_integration", "dm_handled", {
                "bot_username": bot_username,
                "user_id": sender.id,
                "user_name": sender.first_name or sender.username,
                "integration_type": "dm"
            })
            
            logger.info(f"✅ Lara DM başarıyla işlendi: {sender.first_name}")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Lara DM entegrasyon hatası: {e}")
        return False

# ==================== GROUP INTEGRATION ====================

async def integrate_lara_group_handler(
    client,
    event, 
    bot_username: str,
    bot_profile: Optional[Dict] = None
) -> bool:
    """
    Grup handler'a Lara entegrasyonu
    
    Args:
        client: Telegram client
        event: Telegram event
        bot_username: Bot kullanıcı adı
        bot_profile: Bot profil bilgileri
    
    Returns:
        Lara tarafından işlendi mi
    """
    try:
        # Lara bot kontrolü
        if not is_lara_bot(bot_username, bot_profile):
            return False
        
        # Mention/reply kontrolü
        if not (event.is_reply or f"@{bot_username}" in event.raw_text.lower()):
            return False
        
        sender = event.sender or await event.get_sender()
        if not sender:
            return False
        
        logger.info(f"🌹 Lara grup entegrasyonu: {sender.first_name} -> {event.raw_text[:30]}...")
        
        # Lara handler'ını çağır
        success = await handle_lara_group_message(client, event, bot_username)
        
        if success:
            log_analytics("lara_integration", "group_handled", {
                "bot_username": bot_username,
                "chat_id": event.chat_id,
                "user_id": sender.id,
                "user_name": sender.first_name or sender.username,
                "integration_type": "group"
            })
            
            logger.info(f"✅ Lara grup mesajı başarıyla işlendi: {sender.first_name}")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Lara grup entegrasyon hatası: {e}")
        return False

# ==================== PROFILE MANAGEMENT ====================

def create_lara_bot_profile(bot_username: str, user_id: int) -> Dict[str, Any]:
    """Lara bot profili oluştur"""
    
    character_config = LaraPromptUtils.getCharacterConfig()
    
    profile = {
        "username": bot_username,
        "telegram_handle": f"@{bot_username}",
        "display_name": "Lara",
        "type": "lara_bot",
        "user_id": user_id,
        "created_at": "2025-01-30",
        
        # Karakter özellikleri
        "personality": character_config["personality"],
        "languages": character_config["languages"],
        "nationality": character_config["nationality"],
        "age": character_config["age"],
        
        # Bot ayarları
        "reply_mode": "gpt_enhanced",
        "gpt_enhanced": True,
        "gpt_mode": "lara_personality",
        "auto_menu_enabled": True,
        "auto_menu_threshold": 2,
        
        # Lara özel ayarları
        "lara_config": {
            "flirt_level": "professional",
            "sales_focus": True,
            "russian_words": True,
            "emoji_usage": True,
            "vip_services": LaraConfig.VIP_SERVICES,
            "papara_info": LaraConfig.PAPARA_INFO
        },
        
        # Hizmet ayarları
        "services_menu": {
            "özel_mesaj": "50₺ - Kişisel sohbet ve özel fotoğraflar 💋",
            "vip_grup": "100₺ - VIP grup üyeliği, günlük özel içerik 🔥",
            "özel_video": "200₺ - Talep üzerine kişiselleştirilmiş video 🎬",
            "canlı_yayın": "150₺ - Telegram'da özel yayın 📺"
        },
        
        # Ödeme sistemi
        "papara_accounts": {
            "Lara K.": LaraConfig.PAPARA_INFO["iban"]
        }
    }
    
    return profile

def update_existing_bot_to_lara(bot_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Mevcut bot profilini Lara karakterine çevir"""
    
    # Mevcut profili koru, Lara özelliklerini ekle
    lara_profile = create_lara_bot_profile(
        bot_profile.get("username", "lara_bot"),
        bot_profile.get("user_id", 0)
    )
    
    # Mevcut ayarları koru
    for key in ["created_at", "customer_info", "owner_id"]:
        if key in bot_profile:
            lara_profile[key] = bot_profile[key]
    
    # Lara tipini ekle
    lara_profile["type"] = "lara_bot"
    lara_profile["original_type"] = bot_profile.get("type", "unknown")
    
    return lara_profile

# ==================== ANALYTICS & MONITORING ====================

def get_lara_integration_stats() -> Dict[str, Any]:
    """Lara entegrasyon istatistiklerini getir"""
    
    # Base Lara stats
    base_stats = get_lara_stats()
    
    # Entegrasyon özel stats
    integration_stats = {
        "integration_version": "1.0.0",
        "prompt_version": LaraPromptUtils.getVersion(),
        "character_config": LaraPromptUtils.getCharacterConfig(),
        "services_available": len(LaraConfig.VIP_SERVICES),
        "russian_words_count": len(LaraConfig.RUSSIAN_WORDS),
        "emoji_pool_size": len(LaraConfig.LARA_EMOJIS)
    }
    
    # Birleştir
    return {**base_stats, **integration_stats}

# ==================== UTILITY FUNCTIONS ====================

def get_lara_response_preview(message: str, user_name: str) -> str:
    """Lara yanıtının önizlemesini al (test amaçlı)"""
    
    # Basit fallback yanıtları
    responses = [
        f"Merhaba {user_name}! 😘 Ben Lara, seninle konuşmaya bayılırım!",
        f"Hey krasotka {user_name}! 🔥 Bana ne söylemek istersin?",
        f"Davay {user_name}! 💋 Seni dinliyorum tatlım!"
    ]
    
    return random.choice(responses)

def validate_lara_config() -> bool:
    """Lara konfigürasyonunu doğrula"""
    
    try:
        # Prompt kontrolü
        prompt = LaraPromptUtils.insertUserName("test")
        if not prompt or len(prompt) < 100:
            return False
        
        # Karakter config kontrolü
        config = LaraPromptUtils.getCharacterConfig()
        if not config.get("name") == "Lara":
            return False
        
        # Services kontrolü
        if len(LaraConfig.VIP_SERVICES) == 0:
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Lara config doğrulama hatası: {e}")
        return False

# ==================== EXPORT FUNCTIONS ====================

__all__ = [
    "is_lara_bot",
    "integrate_lara_dm_handler",
    "integrate_lara_group_handler",
    "create_lara_bot_profile",
    "update_existing_bot_to_lara",
    "get_lara_integration_stats",
    "get_lara_response_preview",
    "validate_lara_config"
] 