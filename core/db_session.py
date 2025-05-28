#!/usr/bin/env python3
# core/db_session.py - Database-based Telegram Session

import json
import asyncio
from typing import Optional, Dict, Any
from telethon.sessions import Session
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from telethon.tl.types import InputPeerUser, InputPeerChat, InputPeerChannel
from utils.log_utils import log_event

class DatabaseSession(Session):
    """
    Veritabanı tabanlı Telegram session sınıfı
    PostgreSQL, MongoDB veya Redis'te session verilerini saklar
    """
    
    def __init__(self, session_id: str, storage_type: str = "redis"):
        """
        Args:
            session_id: Unique session identifier (username)
            storage_type: "redis", "postgres", "mongodb"
        """
        super().__init__()
        self.session_id = session_id
        self.storage_type = storage_type
        self._auth_key = None
        self._dc_id = None
        self._server_address = None
        self._port = None
        self._takeout_id = None
        
        # Cache for entities and files
        self._entities = {}
        self._files = {}
        
        # Session başlangıcında verileri yükle
        asyncio.create_task(self._load_session_data())
    
    async def _load_session_data(self):
        """Session verilerini yükle"""
        try:
            await self._load_dc_info()
            await self._load_auth_key()
        except Exception as e:
            log_event(self.session_id, f"❌ Session data yükleme hatası: {e}")
        
    async def _get_storage_client(self):
        """Storage client'ını al"""
        if self.storage_type == "redis":
            from utils.redis_client import redis_client
            # Redis client'ı başlat
            if redis_client is None:
                from utils.redis_client import init_redis
                await init_redis()
                from utils.redis_client import redis_client
            return redis_client
        elif self.storage_type == "postgres":
            from core.db.connection import get_async_session
            return get_async_session()
        elif self.storage_type == "mongodb":
            from core.profile_store import mongo_db
            return mongo_db
        else:
            raise ValueError(f"Desteklenmeyen storage type: {self.storage_type}")
    
    def _session_key(self, key: str) -> str:
        """Session key oluştur"""
        return f"session:{self.session_id}:{key}"
    
    # === Core Session Methods ===
    
    def set_dc(self, dc_id: int, server_address: str, port: int):
        """Data center bilgilerini ayarla"""
        self._dc_id = dc_id
        self._server_address = server_address
        self._port = port
        asyncio.create_task(self._save_dc_info())
    
    async def _save_dc_info(self):
        """DC bilgilerini veritabanına kaydet"""
        try:
            if self.storage_type == "redis":
                client = await self._get_storage_client()
                if client:
                    dc_data = {
                        "dc_id": self._dc_id,
                        "server_address": self._server_address,
                        "port": self._port
                    }
                    await client.hset(
                        self._session_key("dc_info"),
                        mapping=dc_data
                    )
                    log_event(self.session_id, f"💾 DC bilgileri Redis'e kaydedildi: DC{self._dc_id}")
            
            elif self.storage_type == "postgres":
                # PostgreSQL implementation
                async with await self._get_storage_client() as session:
                    from core.db.models import UserSession
                    from sqlalchemy import select, update
                    
                    stmt = select(UserSession).where(UserSession.user_id == self.session_id)
                    result = await session.execute(stmt)
                    user_session = result.scalar_one_or_none()
                    
                    dc_data = {
                        "dc_id": self._dc_id,
                        "server_address": self._server_address,
                        "port": self._port
                    }
                    
                    if user_session:
                        # Update existing
                        stmt = update(UserSession).where(
                            UserSession.user_id == self.session_id
                        ).values(extra_data=dc_data)
                        await session.execute(stmt)
                    else:
                        # Create new
                        new_session = UserSession(
                            user_id=self.session_id,
                            username=self.session_id,
                            bot_type="telegram_client",
                            extra_data=dc_data
                        )
                        session.add(new_session)
                    
                    await session.commit()
                    log_event(self.session_id, f"💾 DC bilgileri PostgreSQL'e kaydedildi: DC{self._dc_id}")
            
            elif self.storage_type == "mongodb":
                # MongoDB implementation
                client = await self._get_storage_client()
                if client:
                    dc_data = {
                        "session_id": self.session_id,
                        "dc_id": self._dc_id,
                        "server_address": self._server_address,
                        "port": self._port,
                        "updated_at": datetime.utcnow()
                    }
                    
                    await client.sessions.update_one(
                        {"session_id": self.session_id},
                        {"$set": dc_data},
                        upsert=True
                    )
                    log_event(self.session_id, f"💾 DC bilgileri MongoDB'ye kaydedildi: DC{self._dc_id}")
        
        except Exception as e:
            log_event(self.session_id, f"❌ DC bilgileri kaydetme hatası: {e}")
    
    @property
    def dc_id(self) -> Optional[int]:
        """Data center ID'sini döndür"""
        if self._dc_id is None:
            # Sync olarak DC bilgilerini yükle
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self._load_dc_info())
                else:
                    loop.run_until_complete(self._load_dc_info())
            except Exception as e:
                log_event(self.session_id, f"❌ DC bilgileri sync yükleme hatası: {e}")
        return self._dc_id
    
    @property
    def server_address(self) -> Optional[str]:
        """Server adresini döndür"""
        return self._server_address
    
    @property
    def port(self) -> Optional[int]:
        """Port'u döndür"""
        return self._port
    
    async def _load_dc_info(self):
        """DC bilgilerini veritabanından yükle"""
        try:
            if self.storage_type == "redis":
                client = await self._get_storage_client()
                if client:
                    dc_data = await client.hgetall(self._session_key("dc_info"))
                    if dc_data:
                        self._dc_id = int(dc_data.get("dc_id", 0))
                        self._server_address = dc_data.get("server_address")
                        self._port = int(dc_data.get("port", 0))
            
            # PostgreSQL ve MongoDB implementasyonları...
            
        except Exception as e:
            log_event(self.session_id, f"❌ DC bilgileri yükleme hatası: {e}")
    
    # === Auth Key Methods ===
    
    @property
    def auth_key(self):
        """Auth key'i döndür"""
        if self._auth_key is None:
            # Sync olarak auth key'i yükle
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Event loop çalışıyorsa task oluştur
                    asyncio.create_task(self._load_auth_key())
                else:
                    # Event loop çalışmıyorsa sync çalıştır
                    loop.run_until_complete(self._load_auth_key())
            except Exception as e:
                log_event(self.session_id, f"❌ Auth key sync yükleme hatası: {e}")
        return self._auth_key
    
    @auth_key.setter
    def auth_key(self, value):
        """Auth key'i ayarla ve kaydet"""
        self._auth_key = value
        if value:
            asyncio.create_task(self._save_auth_key())
    
    async def _save_auth_key(self):
        """Auth key'i veritabanına kaydet"""
        try:
            if self.storage_type == "redis" and self._auth_key:
                client = await self._get_storage_client()
                if client:
                    # Auth key'i base64 encode ederek kaydet
                    import base64
                    auth_key_b64 = base64.b64encode(self._auth_key.key).decode()
                    await client.set(
                        self._session_key("auth_key"),
                        auth_key_b64,
                        ex=86400 * 30  # 30 gün TTL
                    )
                    log_event(self.session_id, "🔐 Auth key Redis'e kaydedildi")
        
        except Exception as e:
            log_event(self.session_id, f"❌ Auth key kaydetme hatası: {e}")
    
    async def _load_auth_key(self):
        """Auth key'i veritabanından yükle"""
        try:
            if self.storage_type == "redis":
                client = await self._get_storage_client()
                if client:
                    auth_key_b64 = await client.get(self._session_key("auth_key"))
                    if auth_key_b64:
                        import base64
                        from telethon.crypto import AuthKey
                        auth_key_bytes = base64.b64decode(auth_key_b64)
                        self._auth_key = AuthKey(auth_key_bytes)
                        log_event(self.session_id, "🔐 Auth key Redis'ten yüklendi")
        
        except Exception as e:
            log_event(self.session_id, f"❌ Auth key yükleme hatası: {e}")
    
    # === Entity Cache Methods ===
    
    def get_entity_rows_by_phone(self, phone: str):
        """Telefon numarasına göre entity getir"""
        return self._entities.get(f"phone:{phone}")
    
    def get_entity_rows_by_username(self, username: str):
        """Username'e göre entity getir"""
        return self._entities.get(f"username:{username}")
    
    def get_entity_rows_by_name(self, name: str):
        """İsme göre entity getir"""
        return self._entities.get(f"name:{name}")
    
    def get_entity_rows_by_id(self, entity_id: int, exact: bool = True):
        """ID'ye göre entity getir"""
        return self._entities.get(f"id:{entity_id}")
    
    def get_file(self, md5_digest: bytes, file_size: int, cls):
        """Dosya cache'inden getir"""
        key = f"{md5_digest.hex()}:{file_size}"
        return self._files.get(key)
    
    def cache_file(self, md5_digest: bytes, file_size: int, instance):
        """Dosyayı cache'e kaydet"""
        key = f"{md5_digest.hex()}:{file_size}"
        self._files[key] = instance
        # Async olarak veritabanına kaydet
        asyncio.create_task(self._save_file_cache(key, instance))
    
    async def _save_file_cache(self, key: str, instance):
        """Dosya cache'ini veritabanına kaydet"""
        try:
            if self.storage_type == "redis":
                client = await self._get_storage_client()
                if client:
                    # Instance'ı serialize et
                    import pickle
                    import base64
                    serialized = base64.b64encode(pickle.dumps(instance)).decode()
                    await client.set(
                        self._session_key(f"file:{key}"),
                        serialized,
                        ex=3600  # 1 saat TTL
                    )
        
        except Exception as e:
            log_event(self.session_id, f"❌ File cache kaydetme hatası: {e}")
    
    # === Cleanup Methods ===
    
    def delete(self):
        """Session'ı sil"""
        asyncio.create_task(self._delete_session())
    
    async def _delete_session(self):
        """Session verilerini veritabanından sil"""
        try:
            if self.storage_type == "redis":
                client = await self._get_storage_client()
                if client:
                    # Tüm session key'lerini sil
                    keys = await client.keys(self._session_key("*"))
                    if keys:
                        await client.delete(*keys)
                    log_event(self.session_id, "🗑️ Session Redis'ten silindi")
        
        except Exception as e:
            log_event(self.session_id, f"❌ Session silme hatası: {e}")
    
    def save(self):
        """Session'ı kaydet (compatibility için)"""
        pass  # Async operations zaten otomatik kaydediyor
    
    def close(self):
        """Session'ı kapat"""
        pass  # Cleanup gerekirse buraya eklenebilir
    
    # === Abstract Methods Implementation ===
    
    def get_input_entity(self, key):
        """Input entity al"""
        return self._entities.get(key)
    
    def get_update_state(self, entity_id):
        """Update state al"""
        return None  # Basit implementasyon
    
    def get_update_states(self):
        """Tüm update state'leri al"""
        return []  # Basit implementasyon
    
    def process_entities(self, tlo):
        """Entity'leri işle"""
        # Basit implementasyon - entity'leri cache'e ekle
        if hasattr(tlo, 'users'):
            for user in tlo.users:
                self._entities[user.id] = user
        if hasattr(tlo, 'chats'):
            for chat in tlo.chats:
                self._entities[chat.id] = chat
    
    def set_update_state(self, entity_id, state):
        """Update state ayarla"""
        pass  # Basit implementasyon
    
    @property
    def takeout_id(self):
        """Takeout ID döndür"""
        return self._takeout_id
    
    @takeout_id.setter
    def takeout_id(self, value):
        """Takeout ID ayarla"""
        self._takeout_id = value

# Factory function
def create_database_session(session_id: str, storage_type: str = "redis") -> DatabaseSession:
    """Database session oluştur"""
    return DatabaseSession(session_id, storage_type) 