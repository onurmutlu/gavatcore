#!/usr/bin/env python3
"""
UNIVERSAL CHARACTER INTEGRATION - Mevcut Sistem Entegrasyonu
===========================================================

Universal Character System'i mevcut GAVATCore bot sistemlerine entegre eder.
Tüm karakterler (Lara, Geisha, BabaGavat, vs.) bu sistem üzerinden çalışabilir.

Bu dosya ile:
- Mevcut dm_handler ve group_handler'lara entegrasyon
- Otomatik karakter tespit sistemi
- Backward compatibility
- Kolay kullanım fonksiyonları
"""

import asyncio
from typing import Dict, Any, Optional, List
import structlog

# Universal character system imports
from handlers.universal_character_system import (
    character_manager,
    handle_character_dm,
    handle_character_group_message,
    get_character_stats,
    is_character_registered
)
from handlers.character_definitions import (
    register_all_characters,
    get_character_by_username,
    get_character_by_type
)

# Utils
from utils.log_utils import log_event
try:
    from core.analytics_logger import log_analytics
except ImportError:
    def log_analytics(source: str, event: str, data: dict = None):
        log_event(source, f"{event}: {data}")

logger = structlog.get_logger("universal_integration")

# ==================== AUTO INITIALIZATION ====================

def initialize_universal_characters():
    """Universal karakter sistemini başlat"""
    try:
        # Tüm karakterleri kaydet
        register_all_characters()
        
        logger.info("✅ Universal Character System başlatıldı")
        return True
        
    except Exception as e:
        logger.error(f"❌ Universal Character System başlatma hatası: {e}")
        return False

# ==================== CHARACTER DETECTION ====================

def detect_character_from_profile(bot_profile: Dict[str, Any]) -> Optional[str]:
    """Bot profilinden karakter tipini tespit et"""
    
    if not bot_profile:
        return None
    
    # Username'den tespit et
    username = bot_profile.get("username", "")
    character_id = get_character_by_username(username)
    if character_id:
        return character_id
    
    # Display name'den tespit et
    display_name = bot_profile.get("display_name", "")
    if "lara" in display_name.lower():
        return "lara"
    elif "geisha" in display_name.lower():
        return "geisha"
    elif "gavat" in display_name.lower() or "baba" in display_name.lower():
        return "babagavat"
    elif "maya" in display_name.lower():
        return "maya"
    elif "noir" in display_name.lower():
        return "noir"
    
    # Type'dan tespit et
    bot_type = bot_profile.get("type", "")
    if bot_type == "lara_bot":
        return "lara"
    elif bot_type == "geisha_bot":
        return "geisha" 
    elif bot_type == "babagavat_bot":
        return "babagavat"
    
    # Personality'den tespit et
    personality = bot_profile.get("personality", [])
    if any("flörtöz" in trait.lower() for trait in personality):
        return "lara"
    elif any("seductive" in trait.lower() or "çekici" in trait.lower() for trait in personality):
        return "geisha"
    elif any("leader" in trait.lower() or "lider" in trait.lower() for trait in personality):
        return "babagavat"
    
    return None

def is_universal_character(bot_username: str, bot_profile: Optional[Dict] = None) -> bool:
    """Bir bot'un universal karakter olup olmadığını kontrol et"""
    
    # Username kontrolü
    character_id = get_character_by_username(bot_username)
    if character_id:
        return is_character_registered(character_id)
    
    # Profile kontrolü
    if bot_profile:
        character_id = detect_character_from_profile(bot_profile)
        if character_id:
            return is_character_registered(character_id)
    
    return False

# ==================== DM INTEGRATION ====================

async def integrate_universal_dm_handler(
    client,
    sender, 
    message_text: str,
    bot_username: str,
    bot_profile: Optional[Dict] = None
) -> bool:
    """
    DM handler'a universal karakter entegrasyonu
    
    Args:
        client: Telegram client
        sender: Mesaj gönderen kullanıcı
        message_text: Mesaj içeriği
        bot_username: Bot kullanıcı adı
        bot_profile: Bot profil bilgileri
    
    Returns:
        Universal karakter tarafından işlendi mi
    """
    try:
        # Karakter tespit et
        character_id = get_character_by_username(bot_username)
        if not character_id:
            character_id = detect_character_from_profile(bot_profile)
        
        if not character_id or not is_character_registered(character_id):
            return False
        
        logger.info(f"🎭 Universal DM entegrasyonu: {character_id} -> {sender.first_name}")
        
        # Universal handler'ı çağır
        success = await handle_character_dm(character_id, client, sender, message_text)
        
        if success:
            log_analytics("universal_integration", "dm_handled", {
                "character_id": character_id,
                "bot_username": bot_username,
                "user_id": sender.id,
                "user_name": sender.first_name or sender.username,
                "integration_type": "dm"
            })
            
            logger.info(f"✅ Universal DM başarıyla işlendi: {character_id}")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Universal DM entegrasyon hatası: {e}")
        return False

# ==================== GROUP INTEGRATION ====================

async def integrate_universal_group_handler(
    client,
    event,
    bot_username: str,
    bot_profile: Optional[Dict] = None
) -> bool:
    """
    Grup handler'a universal karakter entegrasyonu
    
    Args:
        client: Telegram client
        event: Telegram event
        bot_username: Bot kullanıcı adı
        bot_profile: Bot profil bilgileri
    
    Returns:
        Universal karakter tarafından işlendi mi
    """
    try:
        # Karakter tespit et
        character_id = get_character_by_username(bot_username)
        if not character_id:
            character_id = detect_character_from_profile(bot_profile)
        
        if not character_id or not is_character_registered(character_id):
            return False
        
        # Mention/reply kontrolü
        if not (event.is_reply or f"@{bot_username}" in event.raw_text.lower()):
            return False
        
        sender = event.sender or await event.get_sender()
        if not sender:
            return False
        
        logger.info(f"🎭 Universal grup entegrasyonu: {character_id} -> {sender.first_name}")
        
        # Universal handler'ı çağır
        success = await handle_character_group_message(character_id, client, event, bot_username)
        
        if success:
            log_analytics("universal_integration", "group_handled", {
                "character_id": character_id,
                "bot_username": bot_username,
                "chat_id": event.chat_id,
                "user_id": sender.id,
                "user_name": sender.first_name or sender.username,
                "integration_type": "group"
            })
            
            logger.info(f"✅ Universal grup mesajı işlendi: {character_id}")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Universal grup entegrasyon hatası: {e}")
        return False

# ==================== PROFILE MANAGEMENT ====================

def create_universal_character_profile(
    character_id: str,
    bot_username: str, 
    user_id: int,
    existing_profile: Optional[Dict] = None
) -> Optional[Dict[str, Any]]:
    """Universal karakter profili oluştur"""
    
    try:
        if not is_character_registered(character_id):
            logger.error(f"Karakter kayıtlı değil: {character_id}")
            return None
        
        character = character_manager.get_character(character_id)
        if not character:
            return None
        
        # Base profile oluştur
        profile = {
            "username": bot_username,
            "telegram_handle": f"@{bot_username}",
            "display_name": character.display_name,
            "type": f"{character_id}_bot",
            "user_id": user_id,
            "created_at": "2025-01-30",
            
            # Karakter özellikleri
            "character_id": character_id,
            "character_name": character.name,
            "character_type": character.character_type.value,
            "personality": character.personality,
            "languages": character.languages,
            "nationality": character.nationality,
            "age": character.age,
            
            # Bot ayarları
            "reply_mode": "gpt_enhanced",
            "gpt_enhanced": True,
            "gpt_mode": f"{character_id}_personality",
            "auto_menu_enabled": True,
            "auto_menu_threshold": 2,
            
            # Universal config
            "universal_character": True,
            "character_config": {
                "min_response_delay": character.min_response_delay,
                "max_response_delay": character.max_response_delay,
                "emoji_usage": character.emoji_usage,
                "special_words": character.special_words,
                "sales_focus": character.sales_focus
            },
            
            # Hizmet ayarları
            "vip_services": character.vip_services,
            "payment_info": character.payment_info
        }
        
        # Mevcut profil varsa bazı bilgileri koru
        if existing_profile:
            for key in ["created_at", "customer_info", "owner_id"]:
                if key in existing_profile:
                    profile[key] = existing_profile[key]
            
            # Original type'ı kaydet
            profile["original_type"] = existing_profile.get("type", "unknown")
        
        return profile
        
    except Exception as e:
        logger.error(f"Universal profil oluşturma hatası: {e}")
        return None

def update_existing_bot_to_universal(
    bot_profile: Dict[str, Any],
    character_id: str = None
) -> Optional[Dict[str, Any]]:
    """Mevcut bot'u universal karakter'e çevir"""
    
    try:
        # Karakter ID tespit et
        if not character_id:
            character_id = detect_character_from_profile(bot_profile)
        
        if not character_id or not is_character_registered(character_id):
            logger.warning(f"Karakter tespit edilemedi veya kayıtlı değil: {character_id}")
            return None
        
        # Universal profil oluştur
        universal_profile = create_universal_character_profile(
            character_id,
            bot_profile.get("username", "unknown"),
            bot_profile.get("user_id", 0),
            bot_profile
        )
        
        if universal_profile:
            logger.info(f"✅ Bot universal karakter'e çevrildi: {character_id}")
        
        return universal_profile
        
    except Exception as e:
        logger.error(f"Universal dönüşüm hatası: {e}")
        return None

# ==================== ANALYTICS & MONITORING ====================

def get_universal_integration_stats() -> Dict[str, Any]:
    """Universal entegrasyon istatistiklerini getir"""
    
    try:
        # Tüm karakterlerin stats'larını topla
        all_stats = {}
        total_conversations = 0
        total_active = 0
        total_high_interest = 0
        total_payment_inquiries = 0
        
        for character_id in character_manager.characters.keys():
            char_stats = get_character_stats(character_id)
            all_stats[character_id] = char_stats
            
            total_conversations += char_stats.get("total_conversations", 0)
            total_active += char_stats.get("active_conversations", 0)
            total_high_interest += char_stats.get("high_interest_users", 0)
            total_payment_inquiries += char_stats.get("payment_inquiries", 0)
        
        return {
            "integration_version": "1.0.0",
            "total_registered_characters": len(character_manager.characters),
            "character_stats": all_stats,
            "summary": {
                "total_conversations": total_conversations,
                "total_active_conversations": total_active,
                "total_high_interest_users": total_high_interest,
                "total_payment_inquiries": total_payment_inquiries
            }
        }
        
    except Exception as e:
        logger.error(f"Stats toplama hatası: {e}")
        return {"error": str(e)}

# ==================== BACKWARD COMPATIBILITY ====================

# Lara bot için backward compatibility
async def handle_lara_dm_compatibility(client, sender, message_text: str) -> bool:
    """Lara bot için eski API uyumluluğu"""
    return await handle_character_dm("lara", client, sender, message_text)

async def handle_lara_group_message_compatibility(client, event, username: str) -> bool:
    """Lara bot grup mesajları için eski API uyumluluğu"""
    return await handle_character_group_message("lara", client, event, username)

def get_lara_stats_compatibility() -> Dict[str, Any]:
    """Lara istatistikleri için eski API uyumluluğu"""
    return get_character_stats("lara")

# Geisha bot için backward compatibility
async def handle_geisha_dm_compatibility(client, sender, message_text: str) -> bool:
    """Geisha bot için eski API uyumluluğu"""
    return await handle_character_dm("geisha", client, sender, message_text)

async def handle_geisha_group_message_compatibility(client, event, username: str) -> bool:
    """Geisha bot grup mesajları için eski API uyumluluğu"""
    return await handle_character_group_message("geisha", client, event, username)

# BabaGavat bot için backward compatibility
async def handle_babagavat_dm_compatibility(client, sender, message_text: str) -> bool:
    """BabaGavat bot için eski API uyumluluğu"""
    return await handle_character_dm("babagavat", client, sender, message_text)

async def handle_babagavat_group_message_compatibility(client, event, username: str) -> bool:
    """BabaGavat bot grup mesajları için eski API uyumluluğu"""
    return await handle_character_group_message("babagavat", client, event, username)

# ==================== CONVENIENCE FUNCTIONS ====================

def get_available_characters() -> List[str]:
    """Mevcut karakterlerin listesini al"""
    return list(character_manager.characters.keys())

def get_character_info(character_id: str) -> Optional[Dict[str, Any]]:
    """Karakter bilgilerini al"""
    character = character_manager.get_character(character_id)
    if not character:
        return None
    
    return {
        "character_id": character_id,
        "name": character.name,
        "display_name": character.display_name,
        "age": character.age,
        "nationality": character.nationality,
        "character_type": character.character_type.value,
        "personality": character.personality,
        "languages": character.languages,
        "vip_services_count": len(character.vip_services),
        "has_payment_info": bool(character.payment_info)
    }

def list_all_characters() -> Dict[str, Dict[str, Any]]:
    """Tüm karakterlerin bilgilerini listele"""
    return {
        char_id: get_character_info(char_id) 
        for char_id in get_available_characters()
    }

# ==================== AUTO INITIALIZATION ====================

# Sistem başlatılınca karakterleri otomatik kaydet
try:
    if not character_manager.characters:
        initialize_universal_characters()
        logger.info("🎭 Universal Character System otomatik başlatıldı")
except Exception as e:
    logger.warning(f"⚠️ Universal Character System otomatik başlatma hatası: {e}")

# ==================== EXPORTS ====================

__all__ = [
    # Main integration functions
    "integrate_universal_dm_handler",
    "integrate_universal_group_handler",
    
    # Character detection
    "detect_character_from_profile",
    "is_universal_character",
    
    # Profile management
    "create_universal_character_profile",
    "update_existing_bot_to_universal",
    
    # Stats and monitoring
    "get_universal_integration_stats",
    
    # Backward compatibility
    "handle_lara_dm_compatibility",
    "handle_lara_group_message_compatibility",
    "get_lara_stats_compatibility",
    "handle_geisha_dm_compatibility",
    "handle_geisha_group_message_compatibility",
    "handle_babagavat_dm_compatibility",
    "handle_babagavat_group_message_compatibility",
    
    # Convenience functions
    "get_available_characters",
    "get_character_info",
    "list_all_characters",
    "initialize_universal_characters"
] 