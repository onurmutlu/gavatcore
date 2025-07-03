#!/usr/bin/env python3
# cleanup_sessions.py - Journal dosyalarını sürekli temizle

import os
import time
import glob
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("session_cleanup")

def cleanup_journal_files():
    """Journal dosyalarını temizle"""
    journal_patterns = [
        "sessions/*.session-journal",
        "sessions/*.session-wal", 
        "sessions/*.session-shm"
    ]
    
    cleaned_count = 0
    for pattern in journal_patterns:
        files = glob.glob(pattern)
        for file_path in files:
            try:
                # Dosya 5 saniyeden eski mi kontrol et
                if os.path.exists(file_path):
                    file_age = time.time() - os.path.getmtime(file_path)
                    if file_age > 5:  # 5 saniye
                        os.remove(file_path)
                        logger.info(f"Journal dosyası temizlendi: {file_path}")
                        cleaned_count += 1
            except Exception as e:
                logger.warning(f"Journal dosyası temizlenemedi {file_path}: {e}")
    
    return cleaned_count

def main():
    logger.info("🧹 Session journal cleanup başlatıldı")
    
    while True:
        try:
            cleaned = cleanup_journal_files()
            if cleaned > 0:
                logger.info(f"✅ {cleaned} journal dosyası temizlendi")
            
            # 2 saniye bekle
            time.sleep(2)
            
        except KeyboardInterrupt:
            logger.info("🛑 Session cleanup durduruldu")
            break
        except Exception as e:
            logger.error(f"Cleanup hatası: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main() 