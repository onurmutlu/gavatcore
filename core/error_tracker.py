#!/usr/bin/env python3
# core/error_tracker.py
"""
Hata izleme ve raporlama modülü.
Tüm sistem hatalarını loglar, kritik olanları e-posta ve Telegram ile bildirir.

YENİ EKLEMELER (v2.0):
- Admin bildirim rate-limit/flood koruması (1dk içinde max 10 aynı hata)
- Uzun Telegram mesajlarını otomatik parçalama (4096 karakter limiti)
- E-posta ve log güvenliği iyileştirmeleri (uzun içerik kısaltma)
- Geliştirilmiş capture_exception decorator (daha detaylı context)
- Daha modüler test/örnek kod yapısı
"""

import os
import logging
import smtplib
import traceback
import json
import requests
import hashlib
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, Union, List, Set
from logging.handlers import RotatingFileHandler
from collections import defaultdict

# Yapılandırma dosyası/env'den ayarları oku
from config import (
    ERROR_LOG_PATH,
    ADMIN_EMAIL,
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    TELEGRAM_WEBHOOK_URL,
    TELEGRAM_ADMIN_ID,
    ERROR_LOG_MAX_SIZE,
    ERROR_LOG_BACKUP_COUNT
)

# Sabitler
MAX_TRACEBACK_LENGTH = 4000  # Maksimum traceback uzunluğu
MAX_CONTEXT_LENGTH = 4000    # Maksimum context uzunluğu
TELEGRAM_MSG_LIMIT = 4096    # Telegram mesaj karakter limiti
RATE_LIMIT_WINDOW = 60      # Rate limit penceresi (saniye)
RATE_LIMIT_MAX = 10         # Rate limit penceresi içindeki maksimum bildirim

# Rate limiting için in-memory cache
_error_cache: Dict[str, List[float]] = defaultdict(list)
_error_notification_counts: Dict[str, int] = defaultdict(int)

# Logging yapılandırması
logger = logging.getLogger("gavatcore.error_tracker")
logger.setLevel(logging.ERROR)

# Hata log dosyası yapılandırması - döngüsel (rotating) log dosyası
os.makedirs(os.path.dirname(ERROR_LOG_PATH), exist_ok=True)
file_handler = RotatingFileHandler(
    ERROR_LOG_PATH,
    maxBytes=ERROR_LOG_MAX_SIZE,
    backupCount=ERROR_LOG_BACKUP_COUNT
)
file_handler.setLevel(logging.ERROR)

# Log formatı
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def _generate_error_hash(module_name: str, error_msg: str, context: Optional[Dict] = None) -> str:
    """
    Hata için benzersiz bir hash oluşturur.
    
    Args:
        module_name: Modül adı
        error_msg: Hata mesajı
        context: Hata bağlamı
        
    Returns:
        Hata hash'i
    """
    hash_content = f"{module_name}:{error_msg}"
    if context:
        # Context'i sıralı bir şekilde hash'e ekle
        sorted_context = json.dumps(context, sort_keys=True)
        hash_content += f":{sorted_context}"
    return hashlib.md5(hash_content.encode()).hexdigest()


def _should_send_notification(error_hash: str) -> bool:
    """
    Rate limiting kontrolü yapar.
    
    Args:
        error_hash: Hata hash'i
        
    Returns:
        Bildirim gönderilmeli mi
    """
    current_time = time.time()
    timestamps = _error_cache[error_hash]
    
    # Zaman penceresinden eski kayıtları temizle
    while timestamps and current_time - timestamps[0] > RATE_LIMIT_WINDOW:
        timestamps.pop(0)
    
    # Yeni timestamp'i ekle
    timestamps.append(current_time)
    
    # İlk hata veya 10'un katlarında bildirim gönder
    count = len(timestamps)
    if count == 1 or count % RATE_LIMIT_MAX == 0:
        _error_notification_counts[error_hash] += 1
        return True
    
    return False


def _truncate_text(text: str, max_length: int) -> str:
    """
    Metni belirli bir uzunlukta kısaltır.
    
    Args:
        text: Kısaltılacak metin
        max_length: Maksimum uzunluk
        
    Returns:
        Kısaltılmış metin
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "... (kısaltıldı)"


def _split_telegram_message(message: str) -> List[str]:
    """
    Uzun Telegram mesajını parçalara böler.
    
    Args:
        message: Orijinal mesaj
        
    Returns:
        Mesaj parçaları listesi
    """
    if len(message) <= TELEGRAM_MSG_LIMIT:
        return [message]
    
    parts = []
    current_part = ""
    lines = message.split('\n')
    
    for line in lines:
        if len(current_part) + len(line) + 1 <= TELEGRAM_MSG_LIMIT:
            current_part += line + '\n'
        else:
            if current_part:
                parts.append(current_part.rstrip())
            current_part = line + '\n'
    
    if current_part:
        parts.append(current_part.rstrip())
    
    # Parça numaralarını ekle
    return [f"[{i+1}/{len(parts)}]\n{part}" for i, part in enumerate(parts)]


def log_error(
    module_name: str, 
    error_msg: str, 
    critical: bool = False, 
    exception: Optional[Exception] = None,
    context: Dict[str, Any] = None
) -> None:
    """
    Hata bilgisini loglar ve kritik durumlarda bildirim gönderir.
    
    Args:
        module_name: Hatanın oluştuğu modül adı
        error_msg: Hata mesajı
        critical: Kritik hata mı (admin bildirimi gönderilecek)
        exception: İlgili Exception nesnesi (isteğe bağlı)
        context: Hata bağlamı hakkında ek bilgiler (isteğe bağlı)
    """
    # Temel hata bilgisi
    error_data = {
        "timestamp": datetime.now().isoformat(),
        "module": module_name,
        "message": error_msg,
        "critical": critical,
        "context": context or {}
    }
    
    # Exception varsa detayları ekle
    if exception:
        error_data["exception_type"] = type(exception).__name__
        traceback_text = traceback.format_exc()
        error_data["traceback"] = _truncate_text(traceback_text, MAX_TRACEBACK_LENGTH)
    
    # Context'i kısalt
    if context:
        context_str = json.dumps(context)
        if len(context_str) > MAX_CONTEXT_LENGTH:
            error_data["context"] = json.loads(_truncate_text(context_str, MAX_CONTEXT_LENGTH))
    
    # Log mesajı oluştur
    log_parts = [
        f"[{module_name}]",
        error_msg
    ]
    if context:
        log_parts.append(f"Context: {json.dumps(error_data['context'])}")
    if exception:
        log_parts.append(f"Exception: {error_data['exception_type']}")
    
    log_message = " | ".join(log_parts)
    logger.error(log_message, exc_info=exception is not None)
    
    # Kritik hatalar için bildirim gönder
    if critical:
        error_hash = _generate_error_hash(module_name, error_msg, context)
        if _should_send_notification(error_hash):
            try:
                # E-mail ile bildirim
                send_email_notification(error_data)
                # Telegram ile bildirim
                send_telegram_notification(error_data)
            except Exception as notification_error:
                logger.error(
                    f"Bildirim gönderilirken hata: {notification_error}",
                    exc_info=True
                )


def send_email_notification(error_data: Dict[str, Any]) -> None:
    """
    Kritik hatalar için e-posta bildirimi gönderir.
    
    Args:
        error_data: Hata verileri sözlüğü
    """
    # E-posta ayarları yoksa atla
    if not all([ADMIN_EMAIL, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD]):
        logger.warning("E-posta bildirimi için SMTP ayarları eksik")
        return
    
    try:
        # E-posta içeriği
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = f"[GAVATCORE] KRİTİK HATA: {error_data['module']}"
        
        # HTML içerik
        html = f"""
        <html>
        <body>
            <h2>🚨 KRİTİK HATA BİLDİRİMİ</h2>
            <p><b>Zaman:</b> {error_data['timestamp']}</p>
            <p><b>Modül:</b> {error_data['module']}</p>
            <p><b>Hata:</b> {error_data['message']}</p>
            
            {f"<p><b>Exception:</b> {error_data.get('exception_type', '')}</p>" if 'exception_type' in error_data else ""}
            
            {f"<h3>Bağlam:</h3><pre>{json.dumps(error_data['context'], indent=2)}</pre>" if error_data['context'] else ""}
            
            {f"<h3>Traceback:</h3><pre>{error_data.get('traceback', '')}</pre>" if 'traceback' in error_data else ""}
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        # E-posta gönderimi
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Kritik hata bildirimi e-posta ile gönderildi: {ADMIN_EMAIL}")
    except smtplib.SMTPConnectError as e:
        logger.error(f"SMTP sunucusuna bağlanırken hata: {e}")
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP kimlik doğrulama hatası: {e}")
    except smtplib.SMTPException as e:
        logger.error(f"SMTP hatası: {e}")
    except Exception as e:
        logger.error(f"E-posta gönderilirken beklenmeyen hata: {e}")


def send_telegram_notification(error_data: Dict[str, Any]) -> None:
    """
    Kritik hatalar için Telegram bildirimi gönderir.
    
    Args:
        error_data: Hata verileri sözlüğü
    """
    # Telegram webhook ayarları yoksa atla
    if not TELEGRAM_WEBHOOK_URL or not TELEGRAM_ADMIN_ID:
        logger.warning("Telegram bildirimi için webhook ayarları eksik")
        return
    
    try:
        # Telegram mesaj içeriği
        base_message = f"""
🚨 *KRİTİK HATA*
⏰ Zaman: `{error_data['timestamp']}`
📂 Modül: `{error_data['module']}`
❌ Hata: `{error_data['message']}`
        """
        
        # Exception varsa ekle
        if 'exception_type' in error_data:
            base_message += f"\n⚠️ Exception: `{error_data['exception_type']}`"
        
        # Bağlam varsa ekle
        if error_data['context']:
            context_str = json.dumps(error_data['context'], ensure_ascii=False)
            base_message += f"\n📌 Bağlam: `{context_str}`"
        
        # Traceback varsa ekle
        if 'traceback' in error_data:
            base_message += f"\n🔍 Traceback:\n```\n{error_data['traceback']}\n```"
        
        # Mesajı parçalara böl
        message_parts = _split_telegram_message(base_message)
        
        # Her parçayı gönder
        for part in message_parts:
            payload = {
                "chat_id": TELEGRAM_ADMIN_ID,
                "text": part,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(TELEGRAM_WEBHOOK_URL, json=payload, timeout=5)
            response.raise_for_status()
            
            # Çok hızlı gönderim yapma
            if len(message_parts) > 1:
                time.sleep(0.5)
        
        logger.info(f"Kritik hata bildirimi Telegram ile gönderildi: {TELEGRAM_ADMIN_ID}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Telegram API hatası: {e}")
    except Exception as e:
        logger.error(f"Telegram bildirimi gönderilirken hata: {e}")


def capture_exception(
    module_name: str, 
    critical: bool = False, 
    context: Dict[str, Any] = None
) -> callable:
    """
    Fonksiyonları saran bir decorator.
    Oluşan istisnaları yakalar ve error_tracker ile loglar.
    
    Args:
        module_name: Modül adı
        critical: Kritik hata olarak işaretlensin mi
        context: Ek bağlam bilgisi
        
    Returns:
        Decorator fonksiyonu
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_context = context.copy() if context else {}
                
                # Fonksiyon bilgilerini ekle
                error_context.update({
                    "function": func.__name__,
                    "module": func.__module__,
                    "qualname": func.__qualname__
                })
                
                # args ve kwargs'yi güvenli şekilde context'e ekle
                try:
                    if args:
                        error_context['args'] = str(args)
                    if kwargs:
                        error_context['kwargs'] = str(kwargs)
                except:
                    error_context['args_parse_error'] = True
                
                log_error(
                    module_name=module_name,
                    error_msg=f"Fonksiyon çağrısında hata: {func.__qualname__}() - {str(e)}",
                    critical=critical,
                    exception=e,
                    context=error_context
                )
                raise  # Orijinal hatayı tekrar fırlat
        return wrapper
    return decorator


# Test ve örnek kullanım
if __name__ == "__main__":
    def test_error_tracking():
        """Hata izleme özelliklerini test eder."""
        
        # 1. Basit hata loglama
        log_error("test_module", "Test hata mesajı")
        
        # 2. Rate-limit/flood koruması testi
        for i in range(15):
            log_error(
                module_name="payment_system",
                error_msg="Ödeme işlemi başarısız",
                critical=True,
                context={"user_id": 12345, "amount": 100, "attempt": i}
            )
            time.sleep(0.1)  # Gerçekçi simülasyon için
        
        # 3. Uzun içerik ve parçalama testi
        long_traceback = "x" * 5000
        log_error(
            module_name="data_processor",
            error_msg="Veri işleme hatası",
            critical=True,
            context={"data": "x" * 5000},
            exception=Exception(long_traceback)
        )
        
        # 4. Decorator kullanımı
        @capture_exception("user_module", critical=True, context={"service": "auth"})
        def risky_function(user_id: int, action: str) -> None:
            if user_id < 0:
                raise ValueError(f"Geçersiz kullanıcı ID: {user_id}")
            print(f"İşlem başarılı: {action}")
        
        # Decorator test
        try:
            risky_function(-1, "login")
        except ValueError:
            print("Hata yakalandı ve loglandı")
    
    # Testleri çalıştır
    test_error_tracking() 