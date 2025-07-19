from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
BEHAVIORAL CACHE MANAGER - Redis Tabanlı Cache Sistemi
=======================================================

Advanced Behavioral Engine için Redis tabanlı caching layer.
Vektör analizi, predictive insights ve Big Five sonuçlarını cache'ler.

Özellikler:
- Redis cluster desteği
- TTL (Time To Live) yönetimi
- Intelligent cache invalidation
- Performance metrics tracking
- Memory optimization

@version: 1.0.0
@created: 2025-01-30
"""

import asyncio
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
import structlog

# Redis imports
try:
    import redis
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    structlog.get_logger().warning("⚠️ Redis not available, using memory cache fallback")

# Cache data structures
from dataclasses import dataclass, field
import pickle

logger = structlog.get_logger("behavioral_cache")

@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    memory_usage: float = 0.0
    avg_response_time: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

@dataclass 
class CacheConfig:
    """Cache configuration"""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 1
    redis_password: Optional[str] = None
    
    # TTL settings (seconds)
    big_five_ttl: int = 7200  # 2 hours
    predictive_ttl: int = 3600  # 1 hour
    sentiment_ttl: int = 1800  # 30 minutes
    timing_ttl: int = 86400  # 24 hours
    
    # Cache keys
    key_prefix: str = "behavioral:"
    compression: bool = True
    max_memory_mb: int = 512

class BehavioralCacheManager:
    """
    🚀 Advanced Behavioral Cache Manager
    
    Redis tabanlı yüksek performanslı caching sistemi.
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.metrics = CacheMetrics()
        self.redis_client: Optional[aioredis.Redis] = None
        self.fallback_cache: Dict[str, Dict] = {}  # Memory fallback
        self.is_redis_available = REDIS_AVAILABLE
        
        logger.info("🗄️ Behavioral Cache Manager başlatılıyor...")
    
    async def initialize(self) -> bool:
        """Cache sistemini başlat"""
        
        if not self.is_redis_available:
            logger.warning("⚠️ Redis kullanılamıyor, memory cache kullanılacak")
            return True
        
        try:
            # Redis connection
            self.redis_client = aioredis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password,
                decode_responses=False,  # Binary data için
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Connection test
            await self.redis_client.ping()
            
            # Memory limit set
            try:
                await self.redis_client.config_set(
                    "maxmemory", 
                    f"{self.config.max_memory_mb}mb"
                )
                await self.redis_client.config_set(
                    "maxmemory-policy", 
                    "allkeys-lru"
                )
            except Exception as e:
                logger.warning(f"⚠️ Redis memory config ayarlanamadı: {e}")
            
            logger.info("✅ Redis cache bağlantısı başarılı")
            return True
            
        except Exception as e:
            logger.error(f"❌ Redis bağlantı hatası: {e}")
            logger.info("🔄 Memory cache fallback aktif")
            self.redis_client = None
            return True
    
    def _generate_cache_key(self, 
                           analysis_type: str, 
                           user_id: int, 
                           data_hash: Optional[str] = None) -> str:
        """Cache key oluştur"""
        base_key = f"{self.config.key_prefix}{analysis_type}:{user_id}"
        if data_hash:
            base_key += f":{data_hash}"
        return base_key
    
    def _hash_data(self, data: Any) -> str:
        """Data için hash oluştur"""
        try:
            if isinstance(data, (list, dict)):
                serialized = json.dumps(data, sort_keys=True)
            else:
                serialized = str(data)
            return hashlib.md5(serialized.encode()).hexdigest()[:16]
        except Exception:
            return hashlib.md5(str(data).encode()).hexdigest()[:16]
    
    async def _serialize_data(self, data: Any) -> bytes:
        """Data serialization"""
        try:
            if self.config.compression:
                import zlib
                serialized = pickle.dumps(data)
                return zlib.compress(serialized)
            else:
                return pickle.dumps(data)
        except Exception as e:
            logger.error(f"❌ Serialization hatası: {e}")
            return pickle.dumps({"error": str(e)})
    
    async def _deserialize_data(self, data: bytes) -> Any:
        """Data deserialization"""
        try:
            if self.config.compression:
                import zlib
                decompressed = zlib.decompress(data)
                return pickle.loads(decompressed)
            else:
                return pickle.loads(data)
        except Exception as e:
            logger.error(f"❌ Deserialization hatası: {e}")
            return None
    
    async def set_big_five_cache(self, 
                                user_id: int, 
                                messages: List[str], 
                                big_five_result: Dict) -> bool:
        """Big Five analysis sonucunu cache'le"""
        
        start_time = time.time()
        
        try:
            # Data hash for cache invalidation
            data_hash = self._hash_data(messages)
            cache_key = self._generate_cache_key("big_five", user_id, data_hash)
            
            # Cache data
            cache_data = {
                "result": big_five_result,
                "timestamp": datetime.now().isoformat(),
                "message_count": len(messages),
                "data_hash": data_hash
            }
            
            serialized_data = await self._serialize_data(cache_data)
            
            if self.redis_client:
                await self.redis_client.setex(
                    cache_key, 
                    self.config.big_five_ttl, 
                    serialized_data
                )
            else:
                # Memory fallback
                self.fallback_cache[cache_key] = {
                    "data": cache_data,
                    "expires": time.time() + self.config.big_five_ttl
                }
            
            # Metrics
            self.metrics.sets += 1
            response_time = time.time() - start_time
            self._update_avg_response_time(response_time)
            
            logger.debug(f"✅ Big Five cache set: {user_id} ({response_time:.3f}s)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Big Five cache set hatası: {e}")
            return False
    
    async def get_big_five_cache(self, 
                                user_id: int, 
                                messages: List[str]) -> Optional[Dict]:
        """Big Five cache'den al"""
        
        start_time = time.time()
        
        try:
            data_hash = self._hash_data(messages)
            cache_key = self._generate_cache_key("big_five", user_id, data_hash)
            
            cached_data = None
            
            if self.redis_client:
                cached_bytes = await self.redis_client.get(cache_key)
                if cached_bytes:
                    cached_data = await self._deserialize_data(cached_bytes)
            else:
                # Memory fallback
                fallback_item = self.fallback_cache.get(cache_key)
                if fallback_item and fallback_item["expires"] > time.time():
                    cached_data = fallback_item["data"]
                elif fallback_item:
                    # Expired, remove
                    del self.fallback_cache[cache_key]
            
            # Metrics
            response_time = time.time() - start_time
            self._update_avg_response_time(response_time)
            
            if cached_data:
                self.metrics.hits += 1
                logger.debug(f"🎯 Big Five cache hit: {user_id} ({response_time:.3f}s)")
                return cached_data["result"]
            else:
                self.metrics.misses += 1
                logger.debug(f"❌ Big Five cache miss: {user_id}")
                return None
            
        except Exception as e:
            logger.error(f"❌ Big Five cache get hatası: {e}")
            self.metrics.misses += 1
            return None
    
    async def set_predictive_cache(self, 
                                  user_id: int, 
                                  profile_data: Dict, 
                                  predictive_result: Dict) -> bool:
        """Predictive insights cache'le"""
        
        try:
            profile_hash = self._hash_data(profile_data)
            cache_key = self._generate_cache_key("predictive", user_id, profile_hash)
            
            cache_data = {
                "result": predictive_result,
                "timestamp": datetime.now().isoformat(),
                "profile_hash": profile_hash
            }
            
            serialized_data = await self._serialize_data(cache_data)
            
            if self.redis_client:
                await self.redis_client.setex(
                    cache_key,
                    self.config.predictive_ttl,
                    serialized_data
                )
            else:
                self.fallback_cache[cache_key] = {
                    "data": cache_data,
                    "expires": time.time() + self.config.predictive_ttl
                }
            
            self.metrics.sets += 1
            logger.debug(f"✅ Predictive cache set: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Predictive cache set hatası: {e}")
            return False
    
    async def get_predictive_cache(self, 
                                  user_id: int, 
                                  profile_data: Dict) -> Optional[Dict]:
        """Predictive cache'den al"""
        
        try:
            profile_hash = self._hash_data(profile_data)
            cache_key = self._generate_cache_key("predictive", user_id, profile_hash)
            
            cached_data = None
            
            if self.redis_client:
                cached_bytes = await self.redis_client.get(cache_key)
                if cached_bytes:
                    cached_data = await self._deserialize_data(cached_bytes)
            else:
                fallback_item = self.fallback_cache.get(cache_key)
                if fallback_item and fallback_item["expires"] > time.time():
                    cached_data = fallback_item["data"]
                elif fallback_item:
                    del self.fallback_cache[cache_key]
            
            if cached_data:
                self.metrics.hits += 1
                logger.debug(f"🎯 Predictive cache hit: {user_id}")
                return cached_data["result"]
            else:
                self.metrics.misses += 1
                return None
                
        except Exception as e:
            logger.error(f"❌ Predictive cache get hatası: {e}")
            self.metrics.misses += 1
            return None
    
    async def invalidate_user_cache(self, user_id: int) -> bool:
        """Kullanıcının tüm cache'ini invalidate et"""
        
        try:
            pattern = f"{self.config.key_prefix}*:{user_id}:*"
            
            if self.redis_client:
                # Redis'de pattern matching ile sil
                keys = await self.redis_client.keys(pattern)
                if keys:
                    deleted = await self.redis_client.delete(*keys)
                    self.metrics.deletes += deleted
                    logger.info(f"🗑️ User cache invalidated: {user_id} ({deleted} keys)")
            else:
                # Memory fallback
                keys_to_delete = [k for k in self.fallback_cache.keys() 
                                if k.startswith(f"{self.config.key_prefix}") and f":{user_id}:" in k]
                for key in keys_to_delete:
                    del self.fallback_cache[key]
                self.metrics.deletes += len(keys_to_delete)
                logger.info(f"🗑️ User memory cache invalidated: {user_id} ({len(keys_to_delete)} keys)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache invalidation hatası: {e}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Cache istatistikleri"""
        
        try:
            redis_info = {}
            
            if self.redis_client:
                info = await self.redis_client.info("memory")
                redis_info = {
                    "used_memory": info.get("used_memory", 0),
                    "used_memory_human": info.get("used_memory_human", "0B"),
                    "memory_fragmentation_ratio": info.get("memory_fragmentation_ratio", 0),
                    "connected_clients": info.get("connected_clients", 0)
                }
                
                # Key count
                key_count = await self.redis_client.dbsize()
                redis_info["total_keys"] = key_count
            
            return {
                "cache_type": "redis" if self.redis_client else "memory",
                "metrics": {
                    "hits": self.metrics.hits,
                    "misses": self.metrics.misses,
                    "hit_rate": self.metrics.hit_rate,
                    "sets": self.metrics.sets,
                    "deletes": self.metrics.deletes,
                    "avg_response_time": self.metrics.avg_response_time
                },
                "redis_info": redis_info,
                "memory_cache_size": len(self.fallback_cache),
                "last_updated": self.metrics.last_updated.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Cache stats hatası: {e}")
            return {"error": str(e)}
    
    def _update_avg_response_time(self, response_time: float):
        """Average response time güncelle"""
        total_ops = self.metrics.hits + self.metrics.misses + self.metrics.sets
        if total_ops == 1:
            self.metrics.avg_response_time = response_time
        else:
            # Moving average
            self.metrics.avg_response_time = (
                (self.metrics.avg_response_time * (total_ops - 1) + response_time) / total_ops
            )
    
    async def cleanup_expired(self) -> int:
        """Expired entries temizle (memory cache için)"""
        
        if self.redis_client:
            return 0  # Redis kendi expired key'leri temizler
        
        try:
            current_time = time.time()
            expired_keys = [
                key for key, item in self.fallback_cache.items()
                if item["expires"] < current_time
            ]
            
            for key in expired_keys:
                del self.fallback_cache[key]
            
            logger.debug(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")
            return len(expired_keys)
            
        except Exception as e:
            logger.error(f"❌ Cache cleanup hatası: {e}")
            return 0
    
    async def close(self):
        """Cache bağlantısını kapat"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("📦 Redis cache bağlantısı kapatıldı")

# Global cache manager instance
behavioral_cache_manager = BehavioralCacheManager()

# Convenience functions
async def get_cache_manager() -> BehavioralCacheManager:
    """Global cache manager'ı al"""
    if not behavioral_cache_manager.redis_client and behavioral_cache_manager.is_redis_available:
        await behavioral_cache_manager.initialize()
    return behavioral_cache_manager

__all__ = [
    "BehavioralCacheManager",
    "CacheMetrics", 
    "CacheConfig",
    "behavioral_cache_manager",
    "get_cache_manager"
] 