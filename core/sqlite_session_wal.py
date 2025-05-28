"""
WAL mode destekli SQLite Session sınıfı
"""

from telethon.sessions import SQLiteSession
import sqlite3

class WALSQLiteSession(SQLiteSession):
    """SQLite session with WAL mode enabled"""
    
    def _execute(self, *args, **kwargs):
        """Override _execute to ensure WAL mode is set"""
        # İlk bağlantıda WAL mode'u ayarla
        if not hasattr(self, '_wal_set'):
            try:
                # Önce parent'ın _execute metodunu çağır
                result = super()._execute("PRAGMA journal_mode=WAL")
                super()._execute("PRAGMA synchronous=NORMAL")
                super()._execute("PRAGMA temp_store=MEMORY")
                super()._execute("PRAGMA busy_timeout=30000")  # 30 saniye timeout
                self._wal_set = True
            except Exception:
                # Eğer hata olursa session muhtemelen zaten oluşturulmuş
                self._wal_set = True
                
        # Normal _execute işlemini devam ettir
        return super()._execute(*args, **kwargs) 