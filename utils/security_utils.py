#!/usr/bin/env python3
# utils/security_utils.py
"""
Güvenlik yardımcı modülü.
Kullanıcı yetkilendirme, rate-limiting ve güvenlik kontrolleri.
"""

import os
import time
import json
import logging
import hashlib
import ipaddress
import threading
from typing import Dict, List, Set, Tuple, Optional, Union, Any, Callable
from datetime import datetime, timedelta
from functools import wraps

# Yapılandırma dosyası/env'den ayarları oku
from config import (
    AUTHORIZED_USERS_FILE,
    RATE_LIMIT_CONFIG,
    ACCESS_LOG_FILE,
    ADMIN_USER_IDS,
    SECURITY_LOG_PATH
)

# Yerel dosyalardan yardımcı modülleri içe aktar
from utils.file_utils import load_json, save_json

# Logging yapılandırması
logger = logging.getLogger("gavatcore.security")
logger.setLevel(logging.INFO)

# Dosya handler
if SECURITY_LOG_PATH:
    os.makedirs(os.path.dirname(SECURITY_LOG_PATH), exist_ok=True)
    file_handler = logging.FileHandler(SECURITY_LOG_PATH)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


# ====== Sınıflar ve Yardımcı Fonksiyonlar ====== #

class RateLimiter:
    """Rate limit kontrolü için sınıf."""
    
    def __init__(self):
        """Rate limiter başlatma."""
        # {(user_id, action): [(timestamp1), (timestamp2), ...]}
        self._requests = {}
        self._lock = threading.RLock()
        
        # Varsayılan rate limit ayarları
        self._default_limits = RATE_LIMIT_CONFIG.get("default", {
            "window_seconds": 60,
            "max_requests": 30
        })
        
        # Özel action limit ayarları
        self._action_limits = RATE_LIMIT_CONFIG.get("actions", {})
    
    def check(self, user_id: Union[int, str], action: str) -> Tuple[bool, int, int]:
        """
        Belirtilen kullanıcı ve işlem için rate limit kontrolü yapar.
        
        Args:
            user_id: Kullanıcı ID
            action: İşlem adı
            
        Returns:
            (Limit aşılmadı mı, Kalan istek sayısı, Yenileme için saniye)
        """
        with self._lock:
            now = time.time()
            key = (str(user_id), action)
            
            # İşlem için limit ayarlarını al
            limits = self._action_limits.get(action, self._default_limits)
            window = limits.get("window_seconds", 60)
            max_requests = limits.get("max_requests", 30)
            
            # Zaman penceresi dışındaki istekleri temizle
            if key in self._requests:
                self._requests[key] = [ts for ts in self._requests[key] if now - ts < window]
            else:
                self._requests[key] = []
            
            # İstek sayısını kontrol et
            current_requests = len(self._requests[key])
            
            if current_requests >= max_requests:
                # Limit aşıldı
                oldest_request = min(self._requests[key]) if self._requests[key] else now
                reset_time = int(oldest_request + window - now)
                return False, 0, reset_time
            
            # Yeni isteği kaydet
            self._requests[key].append(now)
            
            # Kalan istek sayısı ve sıfırlama zamanı
            remaining = max_requests - len(self._requests[key])
            reset_time = int(window - (now - min(self._requests[key]) if self._requests[key] else 0))
            
            return True, remaining, reset_time
    
    def record_request(self, user_id: Union[int, str], action: str) -> None:
        """
        İstek kaydı ekler (check() yapmadan).
        
        Args:
            user_id: Kullanıcı ID
            action: İşlem adı
        """
        with self._lock:
            key = (str(user_id), action)
            if key not in self._requests:
                self._requests[key] = []
            self._requests[key].append(time.time())


# Küresel rate limiter nesnesi
rate_limiter = RateLimiter()


class AccessManager:
    """Kullanıcı erişim yönetimi için sınıf."""
    
    def __init__(self):
        """Erişim yöneticisini başlat."""
        self._authorized_users = set()
        self._admin_users = set(map(str, ADMIN_USER_IDS))
        self._blocked_users = set()
        self._suspicious_users = {}  # {user_id: [timestamp, reason]}
        self._lock = threading.RLock()
        
        # Verileri dosyadan yükle
        self._load_users()
    
    def _load_users(self) -> None:
        """Kullanıcı verilerini dosyadan yükle."""
        with self._lock:
            try:
                if os.path.exists(AUTHORIZED_USERS_FILE):
                    data = load_json(AUTHORIZED_USERS_FILE, default={})
                    
                    # Yetkilendirilmiş kullanıcılar
                    self._authorized_users = set(map(str, data.get("authorized", [])))
                    
                    # Admin kullanıcıları ekle
                    self._authorized_users.update(self._admin_users)
                    
                    # Engellenen kullanıcılar
                    self._blocked_users = set(map(str, data.get("blocked", [])))
                    
                    # Şüpheli kullanıcılar
                    self._suspicious_users = {
                        str(uid): data 
                        for uid, data in data.get("suspicious", {}).items()
                    }
                    
                    logger.debug(f"Kullanıcı verileri yüklendi: {len(self._authorized_users)} yetkili, "
                               f"{len(self._blocked_users)} engellenen")
            except Exception as e:
                logger.error(f"Kullanıcı verileri yüklenirken hata: {e}")
    
    def _save_users(self) -> None:
        """Kullanıcı verilerini dosyaya kaydet."""
        with self._lock:
            try:
                data = {
                    "authorized": list(self._authorized_users),
                    "blocked": list(self._blocked_users),
                    "suspicious": self._suspicious_users,
                    "updated_at": datetime.now().isoformat()
                }
                
                save_json(AUTHORIZED_USERS_FILE, data)
                logger.debug("Kullanıcı verileri kaydedildi")
            except Exception as e:
                logger.error(f"Kullanıcı verileri kaydedilirken hata: {e}")
    
    def is_authorized(self, user_id: Union[int, str]) -> bool:
        """
        Kullanıcının yetkili olup olmadığını kontrol eder.
        
        Args:
            user_id: Kullanıcı ID
            
        Returns:
            Yetkili ise True, değilse False
        """
        user_id = str(user_id)
        
        with self._lock:
            # Engellenmiş kullanıcı kontrolü
            if user_id in self._blocked_users:
                return False
            
            # Yetkili kullanıcı kontrolü
            return user_id in self._authorized_users
    
    def is_admin(self, user_id: Union[int, str]) -> bool:
        """
        Kullanıcının admin olup olmadığını kontrol eder.
        
        Args:
            user_id: Kullanıcı ID
            
        Returns:
            Admin ise True, değilse False
        """
        return str(user_id) in self._admin_users
    
    def authorize_user(self, user_id: Union[int, str]) -> None:
        """
        Kullanıcıya yetki verir.
        
        Args:
            user_id: Kullanıcı ID
        """
        user_id = str(user_id)
        
        with self._lock:
            # Engellenmiş kullanıcıyı engelliler listesinden çıkar
            if user_id in self._blocked_users:
                self._blocked_users.remove(user_id)
            
            # Yetkililer listesine ekle
            self._authorized_users.add(user_id)
            
            # Şüpheli listesinden çıkar
            if user_id in self._suspicious_users:
                del self._suspicious_users[user_id]
            
            # Değişiklikleri kaydet
            self._save_users()
            
            logger.info(f"Kullanıcı yetkilendirildi: {user_id}")
    
    def block_user(self, user_id: Union[int, str], reason: str = "Belirsiz") -> None:
        """
        Kullanıcıyı engeller.
        
        Args:
            user_id: Kullanıcı ID
            reason: Engelleme nedeni
        """
        user_id = str(user_id)
        
        with self._lock:
            # Yetkili listesinden çıkar
            if user_id in self._authorized_users:
                self._authorized_users.remove(user_id)
            
            # Engelli listesine ekle
            self._blocked_users.add(user_id)
            
            # Şüpheli listesinden çıkar
            if user_id in self._suspicious_users:
                del self._suspicious_users[user_id]
            
            # Değişiklikleri kaydet
            self._save_users()
            
            logger.warning(f"Kullanıcı engellendi: {user_id}, Neden: {reason}")
    
    def mark_suspicious(self, user_id: Union[int, str], reason: str) -> None:
        """
        Kullanıcıyı şüpheli olarak işaretle.
        
        Args:
            user_id: Kullanıcı ID
            reason: Şüpheli işaretleme nedeni
        """
        user_id = str(user_id)
        
        with self._lock:
            # Şüpheli listesine ekle
            self._suspicious_users[user_id] = [datetime.now().isoformat(), reason]
            
            # Değişiklikleri kaydet
            self._save_users()
            
            logger.warning(f"Kullanıcı şüpheli işaretlendi: {user_id}, Neden: {reason}")
    
    def log_access(self, user_id: Union[int, str], action: str, 
                   success: bool, details: Dict = None) -> None:
        """
        Erişim kaydı oluşturur.
        
        Args:
            user_id: Kullanıcı ID
            action: Yapılan işlem
            success: Başarılı mı
            details: Ek detaylar
        """
        user_id = str(user_id)
        
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "action": action,
                "success": success,
                "details": details or {}
            }
            
            # Dosyaya ekle (append)
            with open(ACCESS_LOG_FILE, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
            
            log_level = logging.INFO if success else logging.WARNING
            logger.log(log_level, f"Erişim: {user_id} - {action} - {'Başarılı' if success else 'Başarısız'}")
        except Exception as e:
            logger.error(f"Erişim kaydedilirken hata: {e}")


# Küresel erişim yöneticisi nesnesi
access_manager = AccessManager()


# ====== Ana Kullanım Fonksiyonları ====== #

def is_authorized_user(user_id: Union[int, str]) -> bool:
    """
    Kullanıcının yetkili olup olmadığını kontrol eder.
    
    Args:
        user_id: Kullanıcı ID
        
    Returns:
        Yetkili ise True, değilse False
    """
    return access_manager.is_authorized(user_id)


def is_admin_user(user_id: Union[int, str]) -> bool:
    """
    Kullanıcının admin olup olmadığını kontrol eder.
    
    Args:
        user_id: Kullanıcı ID
        
    Returns:
        Admin ise True, değilse False
    """
    return access_manager.is_admin(user_id)


def rate_limit_check(user_id: Union[int, str], action: str) -> Tuple[bool, int, int]:
    """
    Rate limit kontrolü yapar.
    
    Args:
        user_id: Kullanıcı ID
        action: İşlem adı
        
    Returns:
        (Limit aşılmadı mı, Kalan istek sayısı, Yenileme için saniye)
    """
    return rate_limiter.check(user_id, action)


def log_security_event(user_id: Union[int, str], action: str, success: bool, details: Dict = None) -> None:
    """
    Güvenlik olayını loglar.
    
    Args:
        user_id: Kullanıcı ID
        action: İşlem adı
        success: Başarılı mı
        details: Ek detaylar
    """
    access_manager.log_access(user_id, action, success, details)


def authorize_user(user_id: Union[int, str]) -> None:
    """
    Kullanıcıyı yetkilendirir.
    
    Args:
        user_id: Kullanıcı ID
    """
    access_manager.authorize_user(user_id)


def block_user(user_id: Union[int, str], reason: str = "Belirsiz") -> None:
    """
    Kullanıcıyı engeller.
    
    Args:
        user_id: Kullanıcı ID
        reason: Engelleme nedeni
    """
    access_manager.block_user(user_id, reason)


def mark_suspicious(user_id: Union[int, str], reason: str) -> None:
    """
    Kullanıcıyı şüpheli olarak işaretler.
    
    Args:
        user_id: Kullanıcı ID
        reason: Şüpheli işaretleme nedeni
    """
    access_manager.mark_suspicious(user_id, reason)


def validate_ip(ip_address: str) -> bool:
    """
    IP adresinin geçerli olup olmadığını kontrol eder.
    
    Args:
        ip_address: IP adresi
        
    Returns:
        Geçerli ise True, değilse False
    """
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False


def secure_hash(data: str) -> str:
    """
    Veriyi güvenli bir şekilde hashler.
    
    Args:
        data: Hashlenecek veri
        
    Returns:
        SHA-256 hash değeri
    """
    return hashlib.sha256(data.encode()).hexdigest()


# ====== Decorator'lar ====== #

def require_auth(func):
    """
    Fonksiyonu çağıran kullanıcının yetkili olmasını gerektiren decorator.
    
    Args:
        func: Decore edilecek fonksiyon
        
    Returns:
        Wrapper fonksiyon
    """
    @wraps(func)
    async def wrapper(client, event, *args, **kwargs):
        user_id = event.sender_id
        
        if not is_authorized_user(user_id):
            log_security_event(user_id, f"unauthorized_access:{func.__name__}", False)
            return
        
        log_security_event(user_id, f"access:{func.__name__}", True)
        return await func(client, event, *args, **kwargs)
    
    return wrapper


def require_admin(func):
    """
    Fonksiyonu çağıran kullanıcının admin olmasını gerektiren decorator.
    
    Args:
        func: Decore edilecek fonksiyon
        
    Returns:
        Wrapper fonksiyon
    """
    @wraps(func)
    async def wrapper(client, event, *args, **kwargs):
        user_id = event.sender_id
        
        if not is_admin_user(user_id):
            log_security_event(user_id, f"unauthorized_admin_access:{func.__name__}", False)
            return
        
        log_security_event(user_id, f"admin_access:{func.__name__}", True)
        return await func(client, event, *args, **kwargs)
    
    return wrapper


def rate_limited(action: str):
    """
    Fonksiyonu belirli bir işlem için rate-limit ile sınırlayan decorator.
    
    Args:
        action: İşlem adı
        
    Returns:
        Decorator fonksiyon
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(client, event, *args, **kwargs):
            user_id = event.sender_id
            
            # Rate limit kontrolü yap
            allowed, remaining, reset = rate_limit_check(user_id, action)
            
            if not allowed:
                # Limit aşıldı
                log_security_event(
                    user_id, 
                    f"rate_limit_exceeded:{action}", 
                    False,
                    {"reset_seconds": reset}
                )
                
                # Kullanıcıya bildirim gönder
                await event.respond(f"⚠️ İşlem sınırı aşıldı. {reset} saniye sonra tekrar deneyin.")
                return
            
            # İşlemi gerçekleştir
            return await func(client, event, *args, **kwargs)
        
        return wrapper
    
    return decorator


# ====== JWT/Token Yönetimi (Opsiyonel) ====== #

try:
    import jwt
    
    # JWT ayarları
    JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-change-this")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION = 24 * 60 * 60  # 24 saat (saniye cinsinden)
    
    def generate_token(user_id: Union[int, str], **claims) -> str:
        """
        Kullanıcı için JWT token oluşturur.
        
        Args:
            user_id: Kullanıcı ID
            claims: Ek token claim'leri
            
        Returns:
            JWT token string
        """
        payload = {
            "sub": str(user_id),
            "iat": int(time.time()),
            "exp": int(time.time() + JWT_EXPIRATION)
        }
        
        # Ek claim'leri ekle
        payload.update(claims)
        
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def verify_token(token: str) -> Tuple[bool, Dict]:
        """
        JWT token'ı doğrular.
        
        Args:
            token: JWT token string
            
        Returns:
            (Geçerli mi, Token içeriği)
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return True, payload
        except jwt.PyJWTError as e:
            logger.warning(f"Token doğrulama hatası: {e}")
            return False, {}

except ImportError:
    # PyJWT yüklü değilse
    logger.warning("PyJWT kütüphanesi bulunamadı. Token işlevleri devre dışı.")


# Kullanım örneği:
if __name__ == "__main__":
    # Yetkilendirme örneği
    user_id = "12345"
    
    if not is_authorized_user(user_id):
        print(f"Kullanıcı {user_id} yetkili değil, yetkilendiriliyor...")
        authorize_user(user_id)
    
    print(f"Kullanıcı {user_id} yetkili mi: {is_authorized_user(user_id)}")
    
    # Rate limit örneği
    for i in range(5):
        allowed, remaining, reset = rate_limit_check(user_id, "test_action")
        print(f"İstek {i+1}: İzin: {allowed}, Kalan: {remaining}, Sıfırlama: {reset}s") 