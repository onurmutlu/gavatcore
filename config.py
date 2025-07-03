#!/usr/bin/env python3
# config.py
"""
Gavatcore için merkezi yapılandırma dosyası.
Tüm sistem ayarları, sabitler ve yapılandırma değişkenleri.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import dotenv

# .env dosyasını yükle
dotenv.load_dotenv()

# Ana dizinler
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")

# Log dizinleri
ERROR_LOG_DIR = os.path.join(LOGS_DIR, "errors")
METRICS_DIR = os.path.join(LOGS_DIR, "metrics")
SECURITY_LOG_DIR = os.path.join(LOGS_DIR, "security")

# Veri dizinleri
PERSONAS_DIR = os.path.join(DATA_DIR, "personas")
TEMPLATES_DIR = os.path.join(DATA_DIR, "templates")

# Uygulamaya özel dizinleri ve dosyaları oluştur
for dir_path in [LOGS_DIR, DATA_DIR, SESSIONS_DIR, ERROR_LOG_DIR, 
                METRICS_DIR, SECURITY_LOG_DIR, PERSONAS_DIR, TEMPLATES_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# ===== Hata Takibi Ayarları ===== #
ERROR_LOG_PATH = os.path.join(ERROR_LOG_DIR, "errors.log")
ERROR_LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
ERROR_LOG_BACKUP_COUNT = 5

# Email bildirimleri
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Telegram bildirimleri
TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL", "")
TELEGRAM_ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID", "")

# ===== Dosya İşlemleri Ayarları ===== #
DEFAULT_ENCODING = "utf-8"
FILE_BACKUP_DIR = os.path.join(BASE_DIR, "backups")
MAX_BACKUP_COUNT = 10

# ===== Güvenlik Ayarları ===== #
AUTHORIZED_USERS_FILE = os.path.join(DATA_DIR, "authorized_users.json")
SECURITY_LOG_PATH = os.path.join(SECURITY_LOG_DIR, "security.log")
ACCESS_LOG_FILE = os.path.join(SECURITY_LOG_DIR, "access.log")

# Admin kullanıcılar (ID'ler)
ADMIN_USER_IDS = json.loads(os.getenv("ADMIN_USER_IDS", "[]"))

# Rate limit ayarları
RATE_LIMIT_CONFIG = {
    "default": {
        "window_seconds": 60,
        "max_requests": 30
    },
    "actions": {
        "send_message": {
            "window_seconds": 60,
            "max_requests": 15
        },
        "register": {
            "window_seconds": 3600,  # 1 saat
            "max_requests": 3
        },
        "api_call": {
            "window_seconds": 60,
            "max_requests": 100
        }
    }
}

# JWT ayarları
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-change-this")
JWT_EXPIRATION = 24 * 60 * 60  # 24 saat (saniye)

# ===== Metrik Ayarları ===== #
METRICS_FORMAT = os.getenv("METRICS_FORMAT", "jsonl")  # "jsonl" veya "csv"
METRICS_FLUSH_INTERVAL = int(os.getenv("METRICS_FLUSH_INTERVAL", "60"))  # saniye
METRICS_RETENTION_DAYS = int(os.getenv("METRICS_RETENTION_DAYS", "30"))

# Dashboard entegrasyonu
DASHBOARD_API_URL = os.getenv("DASHBOARD_API_URL", "")
DASHBOARD_API_KEY = os.getenv("DASHBOARD_API_KEY", "")

# ===== GPT / AI Ayarları ===== #
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_GPT_MODEL = os.getenv("DEFAULT_GPT_MODEL", "gpt-4-turbo-preview")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# ===== Telegram Bot Ayarları ===== #
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Otomatik mesajlaşma ayarları
AUTO_REPLY_DELAY_MIN = int(os.getenv("AUTO_REPLY_DELAY_MIN", "30"))  # saniye
AUTO_REPLY_DELAY_MAX = int(os.getenv("AUTO_REPLY_DELAY_MAX", "120"))  # saniye

# ===== Uygulama Ayarları ===== #
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "yes")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Dil ayarları
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "tr")

# İşlev modları
AVAILABLE_REPLY_MODES = ["manual", "gpt", "hybrid", "manualplus"]
DEFAULT_REPLY_MODE = os.getenv("DEFAULT_REPLY_MODE", "manual")

# Hizmet menüsü varsayılan metni
DEFAULT_SERVICES_MENU = """
🔥 PREMİUM HİZMETLER 🔥

💎 ÖZEL GÖRÜŞME: 500₺ / 30dk
💋 CANLI KAMERA: 300₺ / 15dk
🔞 ÖZEL İÇERİK: 250₺ / 5 foto

💳 Ödeme sonrası hizmet başlar
❤️ İyi eğlenceler dilerim
"""

# ===== Redis Ayarları ===== #
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# ===== Yapılandırma Doğrulama ===== #

def validate_config() -> List[str]:
    """
    Yapılandırma ayarlarını doğrular ve sorunları bildirir.
    
    Returns:
        Yapılandırma sorunlarının listesi
    """
    issues = []
    
    # Kritik dizinleri kontrol et
    for dir_name, dir_path in [
        ("LOGS_DIR", LOGS_DIR),
        ("DATA_DIR", DATA_DIR),
        ("SESSIONS_DIR", SESSIONS_DIR)
    ]:
        if not os.path.exists(dir_path):
            issues.append(f"{dir_name} dizini oluşturulamadı: {dir_path}")
    
    # Kritik ayarları kontrol et
    if not TELEGRAM_API_ID or TELEGRAM_API_ID == 0:
        issues.append("TELEGRAM_API_ID ayarlanmamış")
    
    if not TELEGRAM_API_HASH:
        issues.append("TELEGRAM_API_HASH ayarlanmamış")
    
    # Rate limit ayarlarını kontrol et
    if not isinstance(RATE_LIMIT_CONFIG, dict):
        issues.append("RATE_LIMIT_CONFIG geçerli bir sözlük değil")
    
    # OpenAI API anahtarını kontrol et (GPT modu kullanılacaksa)
    if DEFAULT_REPLY_MODE in ("gpt", "hybrid") and not OPENAI_API_KEY:
        issues.append("GPT modu için OPENAI_API_KEY ayarlanmamış")
    
    return issues


# Yapılandırma sorunlarını logla
config_issues = validate_config()
if config_issues:
    print("⚠️ Yapılandırma sorunları tespit edildi:")
    for issue in config_issues:
        print(f"  - {issue}")
    
    if LOG_LEVEL == "DEBUG":
        print("\n⚙️ Mevcut yapılandırma değerleri:")
        for key, value in globals().items():
            if key.isupper() and not key.startswith("_"):
                # Hassas değerleri maskele
                if any(secret in key for secret in ["PASSWORD", "SECRET", "KEY", "TOKEN", "HASH"]):
                    if value:
                        print(f"  {key}: {'*' * 8}")
                    else:
                        print(f"  {key}: <not set>")
                else:
                    print(f"  {key}: {value}")


# Uygulama çalıştırma kontrolü için değişken
CONFIG_LOADED = True


# Yapılandırma bilgilerini döndür
def get_config() -> Dict[str, Any]:
    """
    Mevcut yapılandırma değerlerini döndürür.
    
    Returns:
        Yapılandırma değerlerinin sözlüğü
    """
    config_dict = {}
    
    for key, value in globals().items():
        if key.isupper() and not key.startswith("_"):
            # Hassas değerleri maskele
            if any(secret in key for secret in ["PASSWORD", "SECRET", "KEY", "TOKEN", "HASH"]):
                if value:
                    config_dict[key] = "********"
                else:
                    config_dict[key] = "<not set>"
            else:
                config_dict[key] = value
    
    return config_dict


# Test
if __name__ == "__main__":
    print("Gavatcore Yapılandırma Bilgileri:")
    config = get_config()
    
    for section in ["Dizinler", "Hata Takibi", "Güvenlik", "Metrikler", "GPT/AI", "Telegram"]:
        print(f"\n=== {section} ===")
        for key, value in config.items():
            if section.lower() in key.lower():
                print(f"{key}: {value}")
    
    if config_issues:
        print("\n⚠️ Yapılandırma Sorunları:")
        for issue in config_issues:
            print(f"- {issue}")
    else:
        print("\n✅ Yapılandırma doğrulaması başarılı!")
