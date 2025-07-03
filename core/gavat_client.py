# core/gavat_client.py

import os
import asyncio
import time
import logging
from telethon import TelegramClient, events
from telethon.sessions import SQLiteSession
from pathlib import Path
import sqlite3
from core.db_session import create_database_session

logger = logging.getLogger("gavatcore.gavat_client")

class SafeSQLiteSession(SQLiteSession):
    """WAL mode'u devre dışı bırakılmış güvenli SQLite session"""
    
    def __init__(self, session_id=None):
        super().__init__(session_id)
        self._wal_disabled = False
    
    def _execute(self, *args, **kwargs):
        """Override _execute to disable WAL mode and handle disk I/O errors"""
        try:
            # İlk bağlantıda WAL mode'u devre dışı bırak
            if not self._wal_disabled:
                try:
                    # WAL mode'u DELETE mode'a çevir
                    super()._execute("PRAGMA journal_mode=DELETE")
                    # Synchronous mode'u NORMAL yap
                    super()._execute("PRAGMA synchronous=NORMAL")
                    # Temp store'u memory'de tut
                    super()._execute("PRAGMA temp_store=MEMORY")
                    # Busy timeout ayarla
                    super()._execute("PRAGMA busy_timeout=30000")
                    # Cache size'ı artır
                    super()._execute("PRAGMA cache_size=10000")
                    self._wal_disabled = True
                    logger.debug("SQLite WAL mode devre dışı bırakıldı")
                except Exception as e:
                    logger.warning(f"SQLite PRAGMA ayarları uygulanamadı: {e}")
                    self._wal_disabled = True
            
            return super()._execute(*args, **kwargs)
            
        except sqlite3.OperationalError as e:
            if "disk I/O error" in str(e):
                logger.error(f"Disk I/O hatası yakalandı: {e}")
                # Session'ı yeniden başlatmaya çalış
                try:
                    if hasattr(self, '_conn') and self._conn:
                        self._conn.close()
                        self._conn = None
                    # Yeniden bağlan
                    return super()._execute(*args, **kwargs)
                except Exception as e2:
                    logger.error(f"Session yeniden başlatılamadı: {e2}")
                    raise e
            else:
                raise e
        except Exception as e:
            logger.error(f"SQLite execute hatası: {e}")
            raise e

class GavatClient:
    def __init__(self, session_identifier: str):
        # Session identifier artık username olacak (path değil)
        self.session_identifier = session_identifier
        self.username = session_identifier
        self.client = None
        self._setup_client()

    def _setup_client(self):
        """Client'ı database session ile kurar."""
        try:
            # API bilgilerini config'den al
            from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
            
            # Database session kullan (Redis)
            db_session = create_database_session(self.session_identifier, "redis")
            
            self.client = TelegramClient(
                db_session,
                TELEGRAM_API_ID,
                TELEGRAM_API_HASH,
                connection_retries=3,
                retry_delay=10,
                timeout=30,
                request_retries=2,
                flood_sleep_threshold=60*60,  # 1 saat flood wait
                auto_reconnect=True,
                sequential_updates=True  # Update'leri sıralı işle
            )
            
            logger.info(f"Client oluşturuldu: {self.session_identifier}")
            
        except Exception as e:
            logger.error(f"Client setup hatası: {e}")
            raise

    async def start(self):
        """Client'ı başlatır."""
        try:
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                logger.error(f"Client yetkilendirilmemiş: {self.session_identifier}")
                return False
            
            # Username'i al
            me = await self.client.get_me()
            self.username = me.username or f"user_{me.id}"
            
            logger.info(f"[{self.username}] başarıyla başlatıldı - User: {me.first_name}")
            return True
            
        except Exception as e:
            logger.error(f"Client başlatma hatası: {e}")
            return False

    async def run(self):
        """Client'ı çalıştırır."""
        try:
            if not await self.start():
                return
            
            logger.info(f"[{self.username}] çalışıyor...")
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"Client çalışma hatası: {e}")
        finally:
            if self.client and self.client.is_connected():
                await self.client.disconnect()

    async def disconnect(self):
        """Client'ı güvenli şekilde kapatır."""
        try:
            if self.client and self.client.is_connected():
                await self.client.disconnect()
                logger.info(f"[{self.username}] bağlantı kapatıldı")
        except Exception as e:
            logger.warning(f"Disconnect hatası: {e}")

# Utility fonksiyonlar
def is_session_available(username):
    """Session dosyasının mevcut olup olmadığını kontrol eder."""
    session_path = f"sessions/{username}.session"
    return os.path.exists(session_path)
