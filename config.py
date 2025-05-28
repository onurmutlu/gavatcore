#!/usr/bin/env python3
# config.py

"""
Gavatcore için merkezi yapılandırma dosyası.
Tüm sistem ayarları ve .env okuma işlemleri.
"""

import os
import dotenv

# .env dosyasını yükle
dotenv.load_dotenv()

# === Database Ayarları ===
# PostgreSQL (Logs, Events, Sales)
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql+asyncpg://localhost/gavatcore")  # Production default
POSTGRES_ECHO = os.getenv("POSTGRES_ECHO", "False").lower() in ("true", "1")

# MongoDB (User Profiles, GPT Configs)
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/gavatcore")  # Production default
MONGODB_DB = os.getenv("MONGODB_DB", "gavatcore")

# Redis (State, Cooldowns, Temporary Data)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_DECODE_RESPONSES = True

# === Telegram Ayarları ===
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN", "")
GAVATCORE_SYSTEM_PHONE = os.getenv("GAVATCORE_SYSTEM_PHONE", "")
GAVATCORE_ADMIN_ID = int(os.getenv("GAVATCORE_ADMIN_ID", "0"))

# === Bot Tanımları ===
# Admin Bot (Token ile çalışan)
ADMIN_BOT_USERNAME = os.getenv("ADMIN_BOT_USERNAME", "@GavatBaba_BOT")
ADMIN_BOT_HANDLE = ADMIN_BOT_USERNAME.replace("@", "").lower()

# User Bot Profilleri (Session ile çalışan)
BOT_BABAGAVAT = os.getenv("BOT_BABAGAVAT", "babagavat")  # Session adı
BOT_YAYINCILARA = os.getenv("BOT_YAYINCILARA", "yayincilara")  # Session adı
BOT_GEISHANIZ = os.getenv("BOT_GEISHANIZ", "geishaniz")  # Session adı (cezalı)

TELEGRAM_ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", os.getenv("GAVATCORE_ADMIN_ID", "0")))

# Opsiyonel: Admin email ve SMTP ayarları (kullanan eski modüller için)
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# === ADVANCED GPT/OpenAI Ayarları - FULL POWER! 🚀 ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Ana GPT Modelleri
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")  # En güçlü model
OPENAI_TURBO_MODEL = os.getenv("OPENAI_TURBO_MODEL", "gpt-4-turbo-preview")
OPENAI_VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4-vision-preview")

# Model Parametreleri
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "4096"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

# Özelleşmiş AI Modelleri
CRM_AI_MODEL = os.getenv("CRM_AI_MODEL", "gpt-4o")
CRM_AI_TEMPERATURE = float(os.getenv("CRM_AI_TEMPERATURE", "0.3"))
CRM_AI_MAX_TOKENS = int(os.getenv("CRM_AI_MAX_TOKENS", "2048"))

CHARACTER_AI_MODEL = os.getenv("CHARACTER_AI_MODEL", "gpt-4o")
CHARACTER_AI_TEMPERATURE = float(os.getenv("CHARACTER_AI_TEMPERATURE", "0.8"))
CHARACTER_AI_MAX_TOKENS = int(os.getenv("CHARACTER_AI_MAX_TOKENS", "1024"))

SOCIAL_AI_MODEL = os.getenv("SOCIAL_AI_MODEL", "gpt-4o")
SOCIAL_AI_TEMPERATURE = float(os.getenv("SOCIAL_AI_TEMPERATURE", "0.6"))

# Voice AI Konfigürasyonu
OPENAI_TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1-hd")
OPENAI_TTS_VOICE = os.getenv("OPENAI_TTS_VOICE", "nova")
OPENAI_STT_MODEL = os.getenv("OPENAI_STT_MODEL", "whisper-1")

# Gelişmiş AI Özellikleri
ENABLE_VOICE_AI = os.getenv("ENABLE_VOICE_AI", "true").lower() in ("true", "1")
ENABLE_CRM_AI = os.getenv("ENABLE_CRM_AI", "true").lower() in ("true", "1")
ENABLE_SOCIAL_AI = os.getenv("ENABLE_SOCIAL_AI", "true").lower() in ("true", "1")
ENABLE_ADVANCED_ANALYTICS = os.getenv("ENABLE_ADVANCED_ANALYTICS", "true").lower() in ("true", "1")
ENABLE_REAL_TIME_ANALYSIS = os.getenv("ENABLE_REAL_TIME_ANALYSIS", "true").lower() in ("true", "1")
ENABLE_PREDICTIVE_ANALYTICS = os.getenv("ENABLE_PREDICTIVE_ANALYTICS", "true").lower() in ("true", "1")
ENABLE_SENTIMENT_ANALYSIS = os.getenv("ENABLE_SENTIMENT_ANALYSIS", "true").lower() in ("true", "1")
ENABLE_PERSONALITY_ANALYSIS = os.getenv("ENABLE_PERSONALITY_ANALYSIS", "true").lower() in ("true", "1")

# Performance Ayarları
AI_CONCURRENT_REQUESTS = int(os.getenv("AI_CONCURRENT_REQUESTS", "10"))
AI_RATE_LIMIT_PER_MINUTE = int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "100"))
AI_CACHE_ENABLED = os.getenv("AI_CACHE_ENABLED", "true").lower() in ("true", "1")

# === Lisans & Demo Ayarları ===
DEMO_DURATION_MINUTES = int(os.getenv("DEMO_DURATION_MINUTES", "180"))
DEFAULT_LICENSE_DAYS = int(os.getenv("DEFAULT_LICENSE_DAYS", "30"))

# === Dizinler ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.getenv("DATA_DIR", os.path.join(BASE_DIR, "data"))
SESSIONS_DIR = os.getenv("SESSIONS_DIR", os.path.join(BASE_DIR, "sessions"))
LOGS_DIR = os.getenv("LOGS_DIR", os.path.join(BASE_DIR, "logs"))
ERROR_LOG_PATH = os.path.join(LOGS_DIR, "errors.log")
METRICS_DIR = os.path.join(LOGS_DIR, "metrics")
PERSONAS_DIR = os.path.join(DATA_DIR, "personas")
TEMPLATES_DIR = os.path.join(DATA_DIR, "templates")

# === Diğer Opsiyonel/Gelişmiş Ayarlar ===
USE_DEFAULT_FLIRT_TEMPLATES = os.getenv("USE_DEFAULT_FLIRT_TEMPLATES", "True").lower() in ("true", "1")
LOG_ALL_MESSAGES = os.getenv("LOG_ALL_MESSAGES", "True").lower() in ("true", "1")
ENABLE_GROUP_HANDLERS = os.getenv("ENABLE_GROUP_HANDLERS", "True").lower() in ("true", "1")

# AI Logging
ENABLE_AI_LOGGING = os.getenv("ENABLE_AI_LOGGING", "true").lower() in ("true", "1")
ENABLE_PERFORMANCE_LOGGING = os.getenv("ENABLE_PERFORMANCE_LOGGING", "true").lower() in ("true", "1")

# === Geriye dönük uyumluluk için ===
DEFAULT_GPT_MODEL = OPENAI_MODEL

TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL", "")

ERROR_LOG_MAX_SIZE = 10 * 1024 * 1024
ERROR_LOG_BACKUP_COUNT = 5

# === AI Model Seçici Fonksiyonları ===
def get_ai_model_for_task(task_type: str) -> str:
    """Görev tipine göre en uygun AI modelini döndür"""
    model_map = {
        "crm_analysis": CRM_AI_MODEL,
        "character_interaction": CHARACTER_AI_MODEL,
        "social_gaming": SOCIAL_AI_MODEL,
        "voice_processing": OPENAI_MODEL,
        "vision_analysis": OPENAI_VISION_MODEL,
        "heavy_analysis": OPENAI_TURBO_MODEL,
        "default": OPENAI_MODEL
    }
    return model_map.get(task_type, OPENAI_MODEL)

def get_ai_temperature_for_task(task_type: str) -> float:
    """Görev tipine göre en uygun temperature değerini döndür"""
    temp_map = {
        "crm_analysis": CRM_AI_TEMPERATURE,
        "character_interaction": CHARACTER_AI_TEMPERATURE,
        "social_gaming": SOCIAL_AI_TEMPERATURE,
        "analytical": 0.2,
        "creative": 0.9,
        "default": OPENAI_TEMPERATURE
    }
    return temp_map.get(task_type, OPENAI_TEMPERATURE)

def get_ai_max_tokens_for_task(task_type: str) -> int:
    """Görev tipine göre en uygun max_tokens değerini döndür"""
    token_map = {
        "crm_analysis": CRM_AI_MAX_TOKENS,
        "character_interaction": CHARACTER_AI_MAX_TOKENS,
        "short_response": 512,
        "medium_response": 1024,
        "long_analysis": 4096,
        "default": OPENAI_MAX_TOKENS
    }
    return token_map.get(task_type, OPENAI_MAX_TOKENS)

# === Fonksiyon: Gelişmiş doğrulama ===
def validate_config():
    missing = []
    warnings = []
    
    # Kritik ayarlar
    if not TELEGRAM_API_ID: missing.append("TELEGRAM_API_ID")
    if not TELEGRAM_API_HASH: missing.append("TELEGRAM_API_HASH")
    if not ADMIN_BOT_TOKEN: missing.append("ADMIN_BOT_TOKEN")
    if not OPENAI_API_KEY: missing.append("OPENAI_API_KEY (GPT modları için gerekli!)")
    
    # AI özellik uyarıları
    if OPENAI_API_KEY and not ENABLE_VOICE_AI:
        warnings.append("OPENAI_API_KEY var ama ENABLE_VOICE_AI=false")
    if OPENAI_API_KEY and not ENABLE_CRM_AI:
        warnings.append("OPENAI_API_KEY var ama ENABLE_CRM_AI=false")
    
    if missing:
        print(f"❌ Kritik eksik ayarlar: {', '.join(missing)}")
    if warnings:
        print(f"⚠️ Uyarılar: {', '.join(warnings)}")
    
    # AI özellik durumu
    if OPENAI_API_KEY:
        print("🚀 AI Özellikleri:")
        print(f"   🎤 Voice AI: {'✅' if ENABLE_VOICE_AI else '❌'}")
        print(f"   📊 CRM AI: {'✅' if ENABLE_CRM_AI else '❌'}")
        print(f"   🎮 Social AI: {'✅' if ENABLE_SOCIAL_AI else '❌'}")
        print(f"   📈 Advanced Analytics: {'✅' if ENABLE_ADVANCED_ANALYTICS else '❌'}")
        print(f"   🔮 Predictive Analytics: {'✅' if ENABLE_PREDICTIVE_ANALYTICS else '❌'}")
        print(f"   💭 Sentiment Analysis: {'✅' if ENABLE_SENTIMENT_ANALYSIS else '❌'}")
        print(f"   🧠 Personality Analysis: {'✅' if ENABLE_PERSONALITY_ANALYSIS else '❌'}")
        print(f"   📱 Ana Model: {OPENAI_MODEL}")
        print(f"   🚀 Turbo Model: {OPENAI_TURBO_MODEL}")
        print(f"   👁️ Vision Model: {OPENAI_VISION_MODEL}")

if __name__ == "__main__":
    validate_config()
    print("🎉 Config başarıyla yüklendi!")
