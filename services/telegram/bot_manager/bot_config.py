"""
🤖 GAVATCore Bot Configuration
==============================

Merkezi bot yönetimi için konfigürasyon dosyası.
Tüm bot tanımlamaları ve ayarları burada.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class BotConfig:
    """Bot konfigürasyon sınıfı"""
    name: str
    display_name: str
    phone: str
    session_path: str
    persona_file: str
    personality: str
    features: List[str]
    enabled: bool = True

# Ana bot konfigürasyonları
BOT_CONFIGS = {
    "lara": BotConfig(
        name="lara",
        display_name="Lara - Flörtöz Yayıncı",
        phone="+905382617727",
        session_path="sessions/_905382617727.session",
        persona_file="data/personas/yayincilara.json",
        personality="Enerjik, eğlenceli, flörtöz yayıncı kız",
        features=["gpt4", "auto_reply", "group_chat", "dm_support"]
    ),
    
    "babagavat": BotConfig(
        name="babagavat",
        display_name="BabaGavat - Pavyon Lideri",
        phone="+905513272355",
        session_path="sessions/_905513272355.session",
        persona_file="data/personas/babagavat.json",
        personality="Sokak zekası yüksek, güvenilir abi",
        features=["gpt4", "auto_reply", "group_chat", "dm_support", "spam_protection"]
    ),
    
    "geisha": BotConfig(
        name="geisha",
        display_name="Geisha - Vamp Moderatör",
        phone="+905486306226",
        session_path="sessions/_905486306226.session",
        persona_file="data/personas/xxxgeisha.json",
        personality="Zarif, gizemli, çekici moderatör",
        features=["gpt4", "auto_reply", "group_chat", "dm_support", "moderation"]
    )
}

# Grup konfigürasyonları
TARGET_GROUPS = [
    {
        "name": "OnlyVips",
        "keywords": ["onlyvips", "only vips", "vip", "gavat", "arayış"],
        "auto_join": True,
        "active_bots": ["lara", "babagavat", "geisha"],
        "features": ["auto_reply", "contact_management", "spam_protection"]
    }
]

# API ve servis konfigürasyonları
SERVICE_CONFIG = {
    "monitoring_api": {
        "enabled": True,
        "host": "0.0.0.0",
        "port": 5005,
        "endpoints": [
            "/api/bots/status",
            "/api/bots/{bot_name}/info",
            "/api/bots/{bot_name}/messages",
            "/api/system/health"
        ]
    },
    
    "admin_panel": {
        "enabled": True,
        "type": "flutter_web",
        "port": 9095,
        "auto_open": False
    }
}

# Spam koruması ayarları
SPAM_PROTECTION = {
    "enabled": True,
    "flood_wait_threshold": 60,  # saniye
    "max_messages_per_minute": 5,
    "auto_switch_to_dm": True,
    "contact_add_on_dm_request": True,
    "ban_check_interval": 3600  # 1 saat
}

# GPT-4 ayarları
GPT_CONFIG = {
    "model": "gpt-4",
    "temperature": 0.8,
    "max_tokens": 150,
    "context_messages": 10,
    "personality_weight": 0.7
}

# Veritabanı ayarları
DATABASE_CONFIG = {
    "contacts_db": "data/databases/spam_aware_contacts.db",
    "messages_db": "data/databases/bot_messages.db",
    "analytics_db": "data/databases/bot_analytics.db"
}

# Loglama ayarları
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "json",
    "file_prefix": "gavatcore_bot",
    "rotation": "daily",
    "retention_days": 7
}

def get_bot_config(bot_name: str) -> BotConfig:
    """Bot konfigürasyonunu getir"""
    return BOT_CONFIGS.get(bot_name)

def get_active_bots() -> List[str]:
    """Aktif bot listesini getir"""
    return [name for name, config in BOT_CONFIGS.items() if config.enabled]

def get_group_config(group_name: str) -> Dict[str, Any]:
    """Grup konfigürasyonunu getir"""
    for group in TARGET_GROUPS:
        if any(keyword in group_name.lower() for keyword in group["keywords"]):
            return group
    return None 