# core/profile_generator.py

import datetime
from core.profile_manager import profile_manager
from core.user_analyzer import babagavat_user_analyzer
from core.analytics_logger import log_analytics
from core.metrics_collector import MetricsCollector
import asyncio
from typing import Dict, Any

DEFAULT_USER_TEMPLATE = {
    "engaging_messages": [],
    "reply_messages": [
        "😌 Ne tatlı yazmışsın, bi daha yazsana?",
        "🙈 Ayyy utandım, ama sevdim…",
        "🥰 Böyle mesajlara bayılıyorum!",
        "😉 Devam et, tam hoşlandığım tarz",
        "💬 Sen yaz, ben dinliyorum…"
    ]
}

DEFAULT_BOT_TEMPLATE = {
    "engaging_messages": [],
    "reply_messages": [
        "🤖 Merhaba! Ben buradayım 😎",
        "💡 Ne demek istedin tatlım?",
        "🧠 Sana nasıl yardımcı olabilirim?",
        "🫦 Sohbete devam edelim mi?",
        "😇 Botum ama kalbim seninle…"
    ]
}

DEFAULT_USER_PROFILE = {
    "type": "user",
    "reply_mode": "manualplus",
    "manualplus_timeout_sec": 180,
    "flirt_templates": [],
    "services_menu": "",
    "papara_accounts": {},
    "papara_note": "",
    "personal_iban": {
        "iban": "",
        "name": ""
    },
    "use_default_templates": True,
    "_template": DEFAULT_USER_TEMPLATE,
    "phone": ""   # <-- ŞOVCU/PRODUCER için EKLENDİ!
}

DEFAULT_BOT_PROFILE = {
    "type": "bot",
    "owner_id": "system",
    "reply_mode": "gpt",
    "manualplus_timeout_sec": 90,
    "persona": {
        "age": "25-35",
        "style": "Yapay zekalı sohbet asistanı",
        "role": "Otomatik yanıtlayıcı",
        "gpt_prompt": "Sen bir AI sohbet botusun. Kullanıcılara sıcak, flörtöz ama stil sahibi yanıtlar veriyorsun. Her yanıtında en az 1 emoji olmalı."
    },
    "_template": DEFAULT_BOT_TEMPLATE
}

class ProfileGenerator:
    def __init__(self):
        self.metrics = MetricsCollector()
        
    async def generate_profile(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Kullanıcı analizi yap
            user_analytics = await babagavat_user_analyzer.analyze_user(user_data)
            
            # Profil verilerini oluştur
            profile_data = {
                "id": user_data.get("id"),
                "username": user_data.get("username"),
                "created_at": datetime.datetime.now().isoformat(),
                "analytics": user_analytics,
                "preferences": self._generate_preferences(user_data, user_analytics),
                "settings": self._generate_settings(user_data),
                "stats": self._generate_stats(user_data, user_analytics)
            }
            
            # Profili kaydet
            await profile_manager.create_profile(profile_data)
            
            # Metrikleri topla
            metrics = await self.metrics.collect_metrics()
            
            # Analitik logla
            await log_analytics(
                event_type="profile_generation",
                data={
                    "user_id": user_data.get("id"),
                    "analytics": user_analytics,
                    "metrics": metrics
                }
            )
            
            return profile_data
            
        except Exception as e:
            await log_analytics(
                event_type="profile_generation_error",
                data={"error": str(e)}
            )
            raise
            
    def _generate_preferences(self, user_data: Dict, analytics: Dict) -> Dict:
        return {
            "language": user_data.get("language", "tr"),
            "notifications": {
                "enabled": True,
                "channels": ["telegram", "email"],
                "frequency": "daily"
            },
            "privacy": {
                "profile_visibility": "public",
                "data_sharing": "limited"
            },
            "content_preferences": {
                "categories": analytics.get("preferred_categories", []),
                "format": "mixed"
            }
        }
        
    def _generate_settings(self, user_data: Dict) -> Dict:
        return {
            "theme": "light",
            "timezone": user_data.get("timezone", "Europe/Istanbul"),
            "currency": "TRY",
            "display_name": user_data.get("display_name", user_data.get("username")),
            "bio": user_data.get("bio", ""),
            "avatar": user_data.get("avatar_url", "")
        }
        
    def _generate_stats(self, user_data: Dict, analytics: Dict) -> Dict:
        return {
            "engagement_score": analytics.get("engagement_score", 0),
            "total_interactions": analytics.get("total_interactions", 0),
            "last_active": analytics.get("last_active", datetime.datetime.now().isoformat()),
            "preferred_time": analytics.get("preferred_time", "evening"),
            "content_consumption": analytics.get("content_consumption", {}),
            "interaction_history": analytics.get("interaction_history", [])
        }

# Singleton instance
profile_generator = ProfileGenerator()

def generate_showcu_persona(username: str, phone: str = "") -> dict:
    """
    Yeni bir içerik üretici/şovcu için default profil oluşturur.
    """
    return {
        "username": username,
        "display_name": username,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "phone": phone,  # <-- Öncelik burada
        **DEFAULT_USER_PROFILE,
    }

def generate_bot_persona(username: str) -> dict:
    """
    Yeni bir sistem botu için default profil döner.
    """
    return {
        "username": username,
        "display_name": username,
        "created_at": datetime.datetime.utcnow().isoformat(),
        **DEFAULT_BOT_PROFILE
    }
