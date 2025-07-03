#!/usr/bin/env python3
"""
Log Utilities - Loglama yardımcı fonksiyonları
"""

import os
from datetime import datetime
import portalocker  # pip install portalocker
import re
import structlog
import asyncio

LOGS_DIR = "logs"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB

logger = structlog.get_logger("gavatcore.log_utils")

def log_event(user_id_or_username: str, text: str, level: str = "INFO"):
    """
    Kullanıcının log dosyasına zaman damgalı bir olay ekler.
    """
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Sessions klasörü için özel path oluştur
    if user_id_or_username.endswith('.session'):
        sessions_log_dir = os.path.join(LOGS_DIR, "sessions")
        os.makedirs(sessions_log_dir, exist_ok=True)
        # Eğer zaten sessions/ ile başlıyorsa, sadece dosya adını al
        if user_id_or_username.startswith('sessions/'):
            session_filename = os.path.basename(user_id_or_username)
        else:
            session_filename = user_id_or_username
        filename = f"{session_filename}.log"
        path = os.path.join(sessions_log_dir, filename)
    else:
        filename = f"{str(user_id_or_username).replace('@', '')}.log"
        path = os.path.join(LOGS_DIR, filename)
    
    timestamp = datetime.now().isoformat(timespec="seconds")
    log_line = f"[{timestamp}] [{level.upper()}] {text}\n"

    # Dosya büyüdüyse rotate et (eskiyi sil veya taşı)
    if os.path.exists(path) and os.path.getsize(path) > MAX_LOG_SIZE:
        rotated = path + f".{int(datetime.now().timestamp())}.bak"
        os.rename(path, rotated)

    # Multi-process lock ile güvenli yaz
    try:
        with portalocker.Lock(path, timeout=3):
            with open(path, "a", encoding="utf-8") as f:
                f.write(log_line)
    except Exception as e:
        # Log yazma hatası durumunda sessizce devam et
        print(f"Log yazma hatası: {e}")
        pass

def get_logs(user_id_or_username: str, limit: int = 20) -> str:
    """
    Son X log satırını döner. Log yoksa uyarı verir.
    """
    filename = f"{str(user_id_or_username).replace('@', '')}.log"
    path = os.path.join(LOGS_DIR, filename)

    if not os.path.exists(path):
        return "📭 Log bulunamadı."

    with portalocker.Lock(path, timeout=3):
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    if not lines:
        return "📭 Log dosyası boş."

    return "".join(lines[-limit:])

# 🔎 Gelişmiş arama & filtre
def search_logs(user_id_or_username: str, keyword: str = "", level: str = "", after: str = "") -> str:
    """
    Log dosyasında anahtar kelime, seviye ve tarih filtresiyle arama yapar.
    after: "2024-06-03" gibi tarih ile, o günden sonrakileri gösterir.
    """
    filename = f"{str(user_id_or_username).replace('@', '')}.log"
    path = os.path.join(LOGS_DIR, filename)

    if not os.path.exists(path):
        return "📭 Log bulunamadı."

    results = []
    after_dt = None
    if after:
        try:
            after_dt = datetime.fromisoformat(after)
        except:
            pass  # Hatalı format, yok say

    try:
        with portalocker.Lock(path, timeout=3):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if level and f"[{level.upper()}]" not in line:
                        continue
                    if keyword and keyword.lower() not in line.lower():
                        continue
                    if after_dt:
                        try:
                            ts = line.split("]")[0].strip("[")
                            log_dt = datetime.fromisoformat(ts)
                            if log_dt < after_dt:
                                continue
                        except:
                            continue
                    results.append(line)

        if not results:
            return "❌ Eşleşen log satırı bulunamadı."
        return "".join(results[-20:])  # Son 20 sonucu dön
    except Exception as e:
        return f"❌ Log arama hatası: {e}"

def get_log_stats(user_id_or_username: str) -> dict:
    """Log dosyası istatistiklerini döndürür"""
    filename = f"{str(user_id_or_username).replace('@', '')}.log"
    path = os.path.join(LOGS_DIR, filename)
    
    if not os.path.exists(path):
        return {"exists": False}
    
    try:
        with portalocker.Lock(path, timeout=3):
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        total_lines = len(lines)
        file_size = os.path.getsize(path)
        
        # Seviye sayıları
        info_count = sum(1 for line in lines if "[INFO]" in line)
        error_count = sum(1 for line in lines if "[ERROR]" in line)
        warning_count = sum(1 for line in lines if "[WARNING]" in line)
        
        # İlk ve son log tarihi
        first_log = lines[0].split("]")[0].strip("[") if lines else None
        last_log = lines[-1].split("]")[0].strip("[") if lines else None
        
        return {
            "exists": True,
            "total_lines": total_lines,
            "file_size": file_size,
            "info_count": info_count,
            "error_count": error_count,
            "warning_count": warning_count,
            "first_log": first_log,
            "last_log": last_log
        }
    except Exception as e:
        return {"exists": True, "error": str(e)}

async def log_event_async(event_type: str, data: dict = None):
    """
    Asenkron olarak log kaydı tutar
    
    Args:
        event_type (str): Olay tipi
        data (dict, optional): Ek veriler
    """
    try:
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data or {}
        }
        
        # Log kaydını asenkron olarak yaz
        await asyncio.to_thread(
            logger.info,
            "event_log",
            **log_data
        )
        
    except Exception as e:
        logger.error(f"Log kaydı hatası: {e}")

# Kullanım örneği:
# log_event("gavatbaba", "Oturum başlatıldı.", level="INFO")
# print(get_logs("gavatbaba"))
# print("".join(search_logs("gavatbaba", keyword="Oturum", level="INFO")))
