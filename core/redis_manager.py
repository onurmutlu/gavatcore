#!/usr/bin/env python3
"""
BabaGAVAT Redis Manager
Onur Metodu ile Redis Cache ve Session Management
BabaGAVAT'ın sokak zekası ile Redis kullanımı
"""

import redis.asyncio as redis
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger("babagavat.redis")

class BabaGAVATRedisManager:
    """BabaGAVAT Redis Manager - Sokak tecrübesi ile Cache yönetimi"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.is_initialized = False
        
    async def initialize(self) -> None:
        """Redis bağlantısını başlat"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                health_check_interval=30,
                socket_keepalive=True,
                socket_keepalive_options={}
            )
            
            # Bağlantı testi
            await self.redis_client.ping()
            self.is_initialized = True
            
            logger.info("🔥 BabaGAVAT Redis Manager başlatıldı - Sokak cache sistemi aktif!")
            
        except Exception as e:
            logger.error(f"❌ Redis bağlantı hatası: {e}")
            # Fallback: Redis yoksa memory cache kullan
            self.redis_client = None
            self.is_initialized = False
    
    async def close(self) -> None:
        """Redis bağlantısını kapat"""
        if self.redis_client:
            await self.redis_client.close()
    
    # COIN BALANCE CACHE METHODS
    async def get_coin_balance(self, user_id: int) -> Optional[float]:
        """Kullanıcı coin bakiyesini Redis'ten al"""
        try:
            if not self.redis_client:
                return None
                
            key = f"babagavat:coin:balance:{user_id}"
            balance = await self.redis_client.get(key)
            
            if balance is not None:
                logger.info(f"💰 BabaGAVAT Redis cache hit: user_id={user_id}, balance={balance}")
                return float(balance)
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Redis coin balance get hatası: {e}")
            return None
    
    async def set_coin_balance(self, user_id: int, balance: float, expire_seconds: int = 300) -> bool:
        """Kullanıcı coin bakiyesini Redis'e kaydet"""
        try:
            if not self.redis_client:
                return False
                
            key = f"babagavat:coin:balance:{user_id}"
            await self.redis_client.setex(key, expire_seconds, str(balance))
            
            logger.info(f"💰 BabaGAVAT Redis cache set: user_id={user_id}, balance={balance}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Redis coin balance set hatası: {e}")
            return False
    
    async def invalidate_coin_balance(self, user_id: int) -> bool:
        """Kullanıcı coin balance cache'ini temizle"""
        try:
            if not self.redis_client:
                return False
                
            key = f"babagavat:coin:balance:{user_id}"
            await self.redis_client.delete(key)
            
            logger.info(f"🗑️ BabaGAVAT Redis cache invalidated: user_id={user_id}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Redis cache invalidate hatası: {e}")
            return False
    
    # DAILY LIMITS CACHE METHODS
    async def get_daily_limits(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Günlük limitler cache'den al"""
        try:
            if not self.redis_client:
                return None
                
            key = f"babagavat:daily:limits:{user_id}"
            data = await self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Redis daily limits get hatası: {e}")
            return None
    
    async def set_daily_limits(self, user_id: int, limits_data: Dict[str, Any]) -> bool:
        """Günlük limitler cache'e kaydet"""
        try:
            if not self.redis_client:
                return False
                
            key = f"babagavat:daily:limits:{user_id}"
            
            # Günün sonuna kadar expire et
            now = datetime.now()
            midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            expire_seconds = int((midnight - now).total_seconds())
            
            await self.redis_client.setex(key, expire_seconds, json.dumps(limits_data))
            
            logger.info(f"📅 BabaGAVAT günlük limit cache set: user_id={user_id}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Redis daily limits set hatası: {e}")
            return False
    
    # ERKO ANALYZER CACHE METHODS
    async def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """ErkoAnalyzer kullanıcı profili cache'den al"""
        try:
            if not self.redis_client:
                return None
                
            key = f"babagavat:erko:profile:{user_id}"
            data = await self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Redis user profile get hatası: {e}")
            return None
    
    async def set_user_profile(self, user_id: int, profile_data: Dict[str, Any], expire_seconds: int = 1800) -> bool:
        """ErkoAnalyzer kullanıcı profili cache'e kaydet"""
        try:
            if not self.redis_client:
                return False
                
            key = f"babagavat:erko:profile:{user_id}"
            await self.redis_client.setex(key, expire_seconds, json.dumps(profile_data))
            
            logger.info(f"🔍 BabaGAVAT ErkoAnalyzer profile cache set: user_id={user_id}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Redis user profile set hatası: {e}")
            return False
    
    # LEADERBOARD CACHE METHODS
    async def get_leaderboard(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Leaderboard cache'den al"""
        try:
            if not self.redis_client:
                return None
                
            key = f"babagavat:leaderboard:top{limit}"
            data = await self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Redis leaderboard get hatası: {e}")
            return None
    
    async def set_leaderboard(self, leaderboard_data: List[Dict[str, Any]], limit: int = 10, expire_seconds: int = 180) -> bool:
        """Leaderboard cache'e kaydet"""
        try:
            if not self.redis_client:
                return False
                
            key = f"babagavat:leaderboard:top{limit}"
            await self.redis_client.setex(key, expire_seconds, json.dumps(leaderboard_data))
            
            logger.info(f"🏆 BabaGAVAT Leaderboard cache set: {len(leaderboard_data)} entries")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Redis leaderboard set hatası: {e}")
            return False
    
    # SESSION MANAGEMENT METHODS
    async def create_session(self, user_id: int, session_data: Dict[str, Any], expire_seconds: int = 3600) -> str:
        """Kullanıcı session oluştur"""
        try:
            if not self.redis_client:
                return f"fallback_session_{user_id}"
                
            session_id = f"babagavat_session_{user_id}_{datetime.now().timestamp()}"
            key = f"babagavat:session:{session_id}"
            
            session_data.update({
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "session_id": session_id
            })
            
            await self.redis_client.setex(key, expire_seconds, json.dumps(session_data))
            
            logger.info(f"🔐 BabaGAVAT session created: {session_id}")
            return session_id
            
        except Exception as e:
            logger.warning(f"⚠️ Redis session create hatası: {e}")
            return f"fallback_session_{user_id}"
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Session bilgilerini al"""
        try:
            if not self.redis_client:
                return None
                
            key = f"babagavat:session:{session_id}"
            data = await self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Redis session get hatası: {e}")
            return None
    
    async def invalidate_session(self, session_id: str) -> bool:
        """Session'ı geçersiz kıl"""
        try:
            if not self.redis_client:
                return False
                
            key = f"babagavat:session:{session_id}"
            await self.redis_client.delete(key)
            
            logger.info(f"🗑️ BabaGAVAT session invalidated: {session_id}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Redis session invalidate hatası: {e}")
            return False
    
    # ANALYTICS CACHE METHODS
    async def increment_counter(self, counter_name: str, amount: int = 1) -> int:
        """Analytics counter artır"""
        try:
            if not self.redis_client:
                return 0
                
            key = f"babagavat:analytics:{counter_name}"
            count = await self.redis_client.incrby(key, amount)
            
            # Counter'ın expire time'ını ayarla (günlük reset için)
            await self.redis_client.expire(key, 86400)  # 24 saat
            
            return count
            
        except Exception as e:
            logger.warning(f"⚠️ Redis counter increment hatası: {e}")
            return 0
    
    async def get_counter(self, counter_name: str) -> int:
        """Analytics counter değerini al"""
        try:
            if not self.redis_client:
                return 0
                
            key = f"babagavat:analytics:{counter_name}"
            count = await self.redis_client.get(key)
            
            return int(count) if count else 0
            
        except Exception as e:
            logger.warning(f"⚠️ Redis counter get hatası: {e}")
            return 0
    
    # BATCH OPERATIONS
    async def batch_invalidate(self, pattern: str) -> int:
        """Pattern'e uyan tüm cache'leri temizle"""
        try:
            if not self.redis_client:
                return 0
                
            keys = await self.redis_client.keys(f"babagavat:{pattern}:*")
            if keys:
                count = await self.redis_client.delete(*keys)
                logger.info(f"🗑️ BabaGAVAT batch invalidate: {count} keys deleted")
                return count
            
            return 0
            
        except Exception as e:
            logger.warning(f"⚠️ Redis batch invalidate hatası: {e}")
            return 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Cache istatistiklerini al"""
        try:
            if not self.redis_client:
                return {"status": "not_connected"}
                
            info = await self.redis_client.info()
            
            # BabaGAVAT cache keys sayısı
            babagavat_keys = await self.redis_client.keys("babagavat:*")
            
            return {
                "status": "connected",
                "redis_version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "babagavat_keys_count": len(babagavat_keys),
                "babagavat_cache_active": True
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Redis stats get hatası: {e}")
            return {"status": "error", "error": str(e)}

# Global Redis Manager instance
babagavat_redis_manager = BabaGAVATRedisManager() 