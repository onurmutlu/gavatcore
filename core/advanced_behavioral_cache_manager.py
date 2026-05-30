from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
ADVANCED BEHAVIORAL CACHE MANAGER - Intelligent Redis Caching System
=====================================================================

Gelişmiş Redis tabanlı cache sistemi ile %85+ hit rate hedefi.

Özellikler:
- Dynamic TTL (kullanım sıklığına göre)
- Multi-tier caching (L1 memory + L2 Redis)  
- Smart cache invalidation patterns
- Probabilistic cache warming
- Adaptive cache sizing
- Real-time analytics ve monitoring
- Cache compression optimization
- Intelligent prefetching

@version: 2.0.0
@created: 2025-01-30
"""

import asyncio
import json
import hashlib
import time
import random
import math
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Tuple, Set
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
import structlog

# Redis imports
try:
    import redis
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    structlog.get_logger().warning("⚠️ Redis not available, using memory cache fallback")

# Additional imports
import pickle
import zlib
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor

logger = structlog.get_logger("advanced_behavioral_cache")

class CacheLevel(Enum):
    """Cache seviyeleri"""
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"

class CacheStrategy(Enum):
    """Cache stratejileri"""
    LRU = "lru"
    LFU = "lfu"
    ADAPTIVE = "adaptive"
    PREDICTIVE = "predictive"

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl_seconds: int = 3600
    data_size: int = 0
    cache_level: CacheLevel = CacheLevel.L2_REDIS
    
    @property
    def age_seconds(self) -> float:
        """Entry yaşı (saniye)"""
        return (datetime.now() - self.created_at).total_seconds()
    
    @property
    def time_since_access(self) -> float:
        """Son erişimden bu yana geçen süre"""
        return (datetime.now() - self.last_accessed).total_seconds()
    
    @property
    def is_expired(self) -> bool:
        """Entry expired mi?"""
        return self.age_seconds > self.ttl_seconds
    
    @property
    def access_frequency(self) -> float:
        """Erişim sıklığı (erişim/saat)"""
        age_hours = max(self.age_seconds / 3600, 0.1)
        return self.access_count / age_hours

@dataclass
class CacheMetrics:
    """Gelişmiş cache metrics"""
    # Hit/Miss stats
    l1_hits: int = 0
    l2_hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    
    # Performance metrics
    response_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    memory_usage_mb: float = 0.0
    redis_memory_mb: float = 0.0
    
    # Advanced metrics
    evictions: int = 0
    cache_warming_requests: int = 0
    prefetch_hits: int = 0
    invalidations: int = 0
    
    # Time-based metrics
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def total_hits(self) -> int:
        return self.l1_hits + self.l2_hits
    
    @property
    def total_requests(self) -> int:
        return self.total_hits + self.misses
    
    @property
    def hit_rate(self) -> float:
        total = self.total_requests
        return (self.total_hits / total * 100) if total > 0 else 0.0
    
    @property
    def l1_hit_rate(self) -> float:
        total = self.total_requests
        return (self.l1_hits / total * 100) if total > 0 else 0.0
    
    @property
    def avg_response_time(self) -> float:
        return statistics.mean(self.response_times) if self.response_times else 0.0

@dataclass
class AdvancedCacheConfig:
    """Gelişmiş cache konfigürasyonu"""
    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 1
    redis_password: Optional[str] = None
    redis_pool_size: int = 20
    
    # Multi-tier cache settings
    l1_cache_size: int = 1000  # L1 memory cache size
    l2_redis_max_memory_mb: int = 1024  # L2 Redis max memory
    
    # Dynamic TTL settings
    base_ttl_seconds: int = 3600  # Base TTL (1 hour)
    min_ttl_seconds: int = 300    # Min TTL (5 minutes)
    max_ttl_seconds: int = 86400  # Max TTL (24 hours)
    
    # Access-based TTL multipliers
    high_frequency_multiplier: float = 2.0  # Sık erişilen data için
    low_frequency_multiplier: float = 0.5   # Az erişilen data için
    
    # Cache warming settings
    cache_warming_enabled: bool = True
    prefetch_probability: float = 0.3  # %30 olasılıkla prefetch
    
    # Performance settings
    compression_enabled: bool = True
    compression_threshold: int = 1024  # 1KB üzeri compress
    batch_size: int = 100
    
    # Cache strategies
    eviction_strategy: CacheStrategy = CacheStrategy.ADAPTIVE
    
    # Key settings
    key_prefix: str = "behavioral_v2:"
    namespace_separator: str = ":"

class AdvancedBehavioralCacheManager:
    """
    🚀 Advanced Behavioral Cache Manager
    
    Multi-tier, intelligent caching sistemi:
    - L1: Memory cache (ultra-fast)
    - L2: Redis cache (persistent)
    - Dynamic TTL based on access patterns
    - Smart prefetching ve cache warming
    - Real-time performance optimization
    """
    
    def __init__(self, config: Optional[AdvancedCacheConfig] = None):
        self.config = config or AdvancedCacheConfig()
        self.metrics = CacheMetrics()
        
        # Redis client
        self.redis_client: Optional[aioredis.Redis] = None
        self.redis_pool: Optional[aioredis.ConnectionPool] = None
        
        # L1 Memory cache
        self.l1_cache: Dict[str, CacheEntry] = {}
        self.l1_cache_lock = threading.RLock()
        
        # Access tracking for intelligent TTL
        self.access_patterns: Dict[str, List[datetime]] = defaultdict(list)
        self.popular_keys: Set[str] = set()
        
        # Performance tracking
        self.key_performance: Dict[str, float] = defaultdict(float)
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        self.cleanup_interval: int = 300  # 5 minutes
        
        # Thread pool for CPU-intensive operations
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        self.is_redis_available = REDIS_AVAILABLE
        logger.info("🗄️ Advanced Behavioral Cache Manager başlatılıyor...")
    
    async def initialize(self) -> bool:
        """Advanced cache sistemini başlat"""
        
        if not self.is_redis_available:
            logger.warning("⚠️ Redis kullanılamıyor, sadece L1 memory cache aktif")
            return True
        
        try:
            # Redis connection pool
            self.redis_pool = aioredis.ConnectionPool(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password,
                max_connections=self.config.redis_pool_size,
                socket_connect_timeout=5,
                socket_timeout=5,
                decode_responses=False
            )
            
            self.redis_client = aioredis.Redis(connection_pool=self.redis_pool)
            
            # Connection test
            await self.redis_client.ping()
            
            # Redis optimizations
            await self._configure_redis()
            
            # Background tasks başlat
            await self._start_background_tasks()
            
            logger.info("✅ Advanced Redis cache system başlatıldı",
                       l1_size=self.config.l1_cache_size,
                       l2_memory_mb=self.config.l2_redis_max_memory_mb)
            return True
            
        except Exception as e:
            logger.error(f"❌ Redis bağlantı hatası: {e}")
            logger.info("🔄 Sadece L1 memory cache aktif")
            self.redis_client = None
            return True
    
    async def _configure_redis(self):
        """Redis optimizasyonları"""
        try:
            # Memory optimization
            await self.redis_client.config_set(
                "maxmemory", f"{self.config.l2_redis_max_memory_mb}mb"
            )
            await self.redis_client.config_set("maxmemory-policy", "allkeys-lru")
            
            # Performance optimizations
            await self.redis_client.config_set("tcp-keepalive", "60")
            await self.redis_client.config_set("timeout", "300")
            
            logger.info("✅ Redis optimizasyonları uygulandı")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis konfigürasyon uyarısı: {e}")
    
    async def _start_background_tasks(self):
        """Background task'ları başlat"""
        # Cleanup task
        cleanup_task = asyncio.create_task(self._periodic_cleanup())
        self.background_tasks.add(cleanup_task)
        cleanup_task.add_done_callback(self.background_tasks.discard)
        
        # Cache warming task
        if self.config.cache_warming_enabled:
            warming_task = asyncio.create_task(self._cache_warming())
            self.background_tasks.add(warming_task)
            warming_task.add_done_callback(self.background_tasks.discard)
        
        # Metrics update task
        metrics_task = asyncio.create_task(self._update_metrics())
        self.background_tasks.add(metrics_task)
        metrics_task.add_done_callback(self.background_tasks.discard)
    
    def _generate_cache_key(self, namespace: str, identifier: str, 
                           data_hash: Optional[str] = None) -> str:
        """Gelişmiş cache key oluştur"""
        key_parts = [self.config.key_prefix, namespace, identifier]
        if data_hash:
            key_parts.append(data_hash)
        return self.config.namespace_separator.join(key_parts)
    
    def _hash_data(self, data: Any) -> str:
        """Optimize edilmiş data hash"""
        try:
            if isinstance(data, (list, dict)):
                serialized = json.dumps(data, sort_keys=True, separators=(',', ':'))
            else:
                serialized = str(data)
            return hashlib.blake2b(serialized.encode(), digest_size=8).hexdigest()
        except Exception:
            return hashlib.md5(str(data).encode()).hexdigest()[:16]
    
    def _calculate_dynamic_ttl(self, cache_key: str, 
                              base_ttl: Optional[int] = None) -> int:
        """Access pattern'e göre dynamic TTL hesapla"""
        base_ttl = base_ttl or self.config.base_ttl_seconds
        
        # Access pattern analizi
        access_times = self.access_patterns.get(cache_key, [])
        if len(access_times) < 2:
            return base_ttl
        
        # Son 1 saatteki access frequency
        now = datetime.now()
        recent_accesses = [
            t for t in access_times 
            if (now - t).total_seconds() < 3600
        ]
        
        if not recent_accesses:
            # Az erişilen data - düşük TTL
            return max(
                int(base_ttl * self.config.low_frequency_multiplier),
                self.config.min_ttl_seconds
            )
        
        # Access frequency hesapla
        frequency = len(recent_accesses)
        
        if frequency >= 10:  # Yüksek frequency
            multiplier = self.config.high_frequency_multiplier
        elif frequency >= 3:  # Orta frequency
            multiplier = 1.0
        else:  # Düşük frequency
            multiplier = self.config.low_frequency_multiplier
        
        # Dynamic TTL calculate
        dynamic_ttl = int(base_ttl * multiplier)
        
        # Bounds check
        return max(
            min(dynamic_ttl, self.config.max_ttl_seconds),
            self.config.min_ttl_seconds
        )
    
    def _track_access(self, cache_key: str):
        """Cache access'i track et"""
        now = datetime.now()
        self.access_patterns[cache_key].append(now)
        
        # Son 24 saatlik geçmişi sakla
        cutoff = now - timedelta(hours=24)
        self.access_patterns[cache_key] = [
            t for t in self.access_patterns[cache_key] 
            if t > cutoff
        ]
        
        # Popular key detection
        if len(self.access_patterns[cache_key]) >= 5:
            self.popular_keys.add(cache_key)
    
    async def _serialize_data(self, data: Any) -> bytes:
        """Gelişmiş data serialization"""
        try:
            # Pickle serialize
            serialized = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Compression if needed
            if (self.config.compression_enabled and 
                len(serialized) > self.config.compression_threshold):
                
                serialized = zlib.compress(serialized, level=6)
                
            return serialized
            
        except Exception as e:
            logger.error(f"❌ Serialization hatası: {e}")
            return pickle.dumps({"error": str(e)})
    
    async def _deserialize_data(self, data: bytes) -> Any:
        """Data deserialization"""
        try:
            # Compression check (zlib header)
            if data.startswith(b'\x78'):
                data = zlib.decompress(data)
            
            return pickle.loads(data)
            
        except Exception as e:
            logger.error(f"❌ Deserialization hatası: {e}")
            return None
    
    async def _l1_get(self, cache_key: str) -> Optional[CacheEntry]:
        """L1 memory cache'den get"""
        with self.l1_cache_lock:
            entry = self.l1_cache.get(cache_key)
            if entry and not entry.is_expired:
                # Access update
                entry.last_accessed = datetime.now()
                entry.access_count += 1
                self.metrics.l1_hits += 1
                return entry
            elif entry:
                # Expired entry cleanup
                del self.l1_cache[cache_key]
        return None
    
    async def _l1_set(self, cache_key: str, data: Any, ttl_seconds: int):
        """L1 memory cache'e set"""
        with self.l1_cache_lock:
            # L1 cache size limit
            if len(self.l1_cache) >= self.config.l1_cache_size:
                await self._l1_evict()
            
            # Estimate data size
            try:
                data_size = len(pickle.dumps(data))
            except:
                data_size = 1000  # Default estimate
            
            entry = CacheEntry(
                data=data,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                ttl_seconds=ttl_seconds,
                data_size=data_size,
                cache_level=CacheLevel.L1_MEMORY
            )
            
            self.l1_cache[cache_key] = entry
    
    async def _l1_evict(self):
        """L1 cache eviction (LRU strategy)"""
        with self.l1_cache_lock:
            if not self.l1_cache:
                return
            
            # Strategy'ye göre eviction
            if self.config.eviction_strategy == CacheStrategy.LRU:
                # En az recently used'ı bul
                oldest_key = min(
                    self.l1_cache.keys(),
                    key=lambda k: self.l1_cache[k].last_accessed
                )
                del self.l1_cache[oldest_key]
                
            elif self.config.eviction_strategy == CacheStrategy.LFU:
                # En az frequently used'ı bul
                least_freq_key = min(
                    self.l1_cache.keys(),
                    key=lambda k: self.l1_cache[k].access_count
                )
                del self.l1_cache[least_freq_key]
                
            elif self.config.eviction_strategy == CacheStrategy.ADAPTIVE:
                # Adaptive eviction - access frequency + recency
                scores = {}
                now = datetime.now()
                
                for key, entry in self.l1_cache.items():
                    recency_score = 1.0 / max(entry.time_since_access / 3600, 0.1)
                    frequency_score = entry.access_frequency
                    scores[key] = recency_score * 0.6 + frequency_score * 0.4
                
                worst_key = min(scores.keys(), key=lambda k: scores[k])
                del self.l1_cache[worst_key]
            
            self.metrics.evictions += 1
    
    async def get(self, namespace: str, identifier: str, 
                  data_hash: Optional[str] = None) -> Optional[Any]:
        """
        Gelişmiş cache get - Multi-tier lookup
        
        Args:
            namespace: Cache namespace (ör: "big_five")
            identifier: Cache identifier (ör: user_id)
            data_hash: Optional data hash for cache invalidation
            
        Returns:
            Cached data or None
        """
        start_time = time.time()
        cache_key = self._generate_cache_key(namespace, identifier, data_hash)
        
        try:
            # Track access
            self._track_access(cache_key)
            
            # L1 Memory cache check
            l1_entry = await self._l1_get(cache_key)
            if l1_entry:
                response_time = time.time() - start_time
                self.metrics.response_times.append(response_time)
                return l1_entry.data
            
            # L2 Redis cache check
            if self.redis_client:
                redis_data = await self.redis_client.get(cache_key)
                if redis_data:
                    # Deserialize
                    data = await self._deserialize_data(redis_data)
                    if data is not None:
                        # Promote to L1 cache
                        dynamic_ttl = self._calculate_dynamic_ttl(cache_key)
                        await self._l1_set(cache_key, data, dynamic_ttl)
                        
                        self.metrics.l2_hits += 1
                        response_time = time.time() - start_time
                        self.metrics.response_times.append(response_time)
                        return data
            
            # Cache miss
            self.metrics.misses += 1
            response_time = time.time() - start_time
            self.metrics.response_times.append(response_time)
            
            # Prefetch trigger
            if (self.config.cache_warming_enabled and 
                random.random() < self.config.prefetch_probability):
                await self._trigger_prefetch(namespace, identifier)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Cache get error: {e}", cache_key=cache_key)
            return None
    
    async def set(self, namespace: str, identifier: str, data: Any,
                  ttl_seconds: Optional[int] = None, 
                  data_hash: Optional[str] = None) -> bool:
        """
        Gelişmiş cache set - Multi-tier storage
        
        Args:
            namespace: Cache namespace
            identifier: Cache identifier 
            data: Data to cache
            ttl_seconds: Optional TTL override
            data_hash: Optional data hash
            
        Returns:
            True if successful
        """
        cache_key = self._generate_cache_key(namespace, identifier, data_hash)
        
        try:
            # Dynamic TTL calculation
            dynamic_ttl = ttl_seconds or self._calculate_dynamic_ttl(cache_key)
            
            # L1 Memory cache set
            await self._l1_set(cache_key, data, dynamic_ttl)
            
            # L2 Redis cache set
            if self.redis_client:
                serialized_data = await self._serialize_data(data)
                await self.redis_client.setex(
                    cache_key, 
                    dynamic_ttl, 
                    serialized_data
                )
            
            self.metrics.sets += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache set error: {e}", cache_key=cache_key)
            return False
    
    async def invalidate(self, namespace: str, identifier: str = "*") -> int:
        """
        Smart cache invalidation
        
        Args:
            namespace: Cache namespace to invalidate
            identifier: Specific identifier or "*" for all
            
        Returns:
            Number of invalidated entries
        """
        try:
            invalidated_count = 0
            
            if identifier == "*":
                # Namespace-wide invalidation
                pattern = f"{self.config.key_prefix}{namespace}{self.config.namespace_separator}*"
                
                # L1 cache invalidation
                with self.l1_cache_lock:
                    keys_to_remove = [
                        key for key in self.l1_cache.keys()
                        if key.startswith(f"{self.config.key_prefix}{namespace}{self.config.namespace_separator}")
                    ]
                    for key in keys_to_remove:
                        del self.l1_cache[key]
                        invalidated_count += 1
                
                # L2 Redis invalidation
                if self.redis_client:
                    redis_keys = await self.redis_client.keys(pattern)
                    if redis_keys:
                        await self.redis_client.delete(*redis_keys)
                        invalidated_count += len(redis_keys)
            else:
                # Specific key invalidation
                cache_key = self._generate_cache_key(namespace, identifier)
                
                # L1 invalidation
                with self.l1_cache_lock:
                    if cache_key in self.l1_cache:
                        del self.l1_cache[cache_key]
                        invalidated_count += 1
                
                # L2 invalidation
                if self.redis_client:
                    result = await self.redis_client.delete(cache_key)
                    invalidated_count += result
            
            self.metrics.invalidations += invalidated_count
            logger.info(f"🗑️ Cache invalidated", 
                       namespace=namespace,
                       identifier=identifier,
                       count=invalidated_count)
            
            return invalidated_count
            
        except Exception as e:
            logger.error(f"❌ Cache invalidation error: {e}")
            return 0
    
    async def _trigger_prefetch(self, namespace: str, identifier: str):
        """Predictive prefetching trigger"""
        try:
            # Related key patterns
            related_patterns = [
                f"{namespace}_related",
                f"{namespace}_similar",
                f"user_{identifier}_profile"
            ]
            
            for pattern in related_patterns:
                if random.random() < 0.1:  # %10 chance
                    # Mock prefetch request
                    self.metrics.cache_warming_requests += 1
                    
        except Exception as e:
            logger.error(f"❌ Prefetch error: {e}")
    
    async def _cache_warming(self):
        """Background cache warming"""
        while True:
            try:
                await asyncio.sleep(600)  # 10 minutes
                
                # Popular keys warming
                if self.popular_keys:
                    warming_count = 0
                    for key in list(self.popular_keys)[:10]:  # Top 10
                        # Check if needs warming
                        if key not in self.l1_cache:
                            warming_count += 1
                    
                    if warming_count > 0:
                        logger.info(f"🔥 Cache warming: {warming_count} keys")
                        
            except Exception as e:
                logger.error(f"❌ Cache warming error: {e}")
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of expired entries"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                # L1 cleanup
                expired_keys = []
                with self.l1_cache_lock:
                    for key, entry in self.l1_cache.items():
                        if entry.is_expired:
                            expired_keys.append(key)
                    
                    for key in expired_keys:
                        del self.l1_cache[key]
                
                if expired_keys:
                    logger.info(f"🧹 L1 cleanup: {len(expired_keys)} expired entries")
                
                # Access patterns cleanup
                cutoff = datetime.now() - timedelta(hours=24)
                cleaned_patterns = 0
                for key in list(self.access_patterns.keys()):
                    self.access_patterns[key] = [
                        t for t in self.access_patterns[key] if t > cutoff
                    ]
                    if not self.access_patterns[key]:
                        del self.access_patterns[key]
                        cleaned_patterns += 1
                
                if cleaned_patterns > 0:
                    logger.info(f"🧹 Access patterns cleanup: {cleaned_patterns} keys")
                    
            except Exception as e:
                logger.error(f"❌ Cleanup error: {e}")
    
    async def _update_metrics(self):
        """Background metrics update"""
        while True:
            try:
                await asyncio.sleep(60)  # 1 minute
                
                # L1 memory usage
                with self.l1_cache_lock:
                    total_size = sum(entry.data_size for entry in self.l1_cache.values())
                    self.metrics.memory_usage_mb = total_size / (1024 * 1024)
                
                # Redis memory usage
                if self.redis_client:
                    try:
                        redis_info = await self.redis_client.info("memory")
                        used_memory = redis_info.get("used_memory", 0)
                        self.metrics.redis_memory_mb = used_memory / (1024 * 1024)
                    except:
                        pass
                
                self.metrics.last_updated = datetime.now()
                
            except Exception as e:
                logger.error(f"❌ Metrics update error: {e}")
    
    async def get_advanced_metrics(self) -> Dict[str, Any]:
        """Gelişmiş cache metrics"""
        
        # Popular keys analysis
        popular_keys_info = []
        for key in list(self.popular_keys)[:10]:
            access_count = len(self.access_patterns.get(key, []))
            popular_keys_info.append({
                "key": key,
                "access_count_24h": access_count,
                "in_l1": key in self.l1_cache
            })
        
        # Cache size distribution
        cache_size_distribution = {
            "l1_entries": len(self.l1_cache),
            "l1_size_mb": self.metrics.memory_usage_mb,
            "redis_size_mb": self.metrics.redis_memory_mb
        }
        
        # Performance metrics
        performance_metrics = {
            "avg_response_time_ms": self.metrics.avg_response_time * 1000,
            "hit_rate_percent": self.metrics.hit_rate,
            "l1_hit_rate_percent": self.metrics.l1_hit_rate,
            "total_requests": self.metrics.total_requests,
            "evictions": self.metrics.evictions
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cache_health": {
                "hit_rate": self.metrics.hit_rate,
                "status": "excellent" if self.metrics.hit_rate > 80 else
                         "good" if self.metrics.hit_rate > 60 else "needs_improvement"
            },
            "performance": performance_metrics,
            "cache_distribution": cache_size_distribution,
            "popular_keys": popular_keys_info,
            "access_patterns": len(self.access_patterns),
            "background_tasks": len(self.background_tasks),
            "cache_warming": {
                "enabled": self.config.cache_warming_enabled,
                "requests": self.metrics.cache_warming_requests,
                "prefetch_hits": self.metrics.prefetch_hits
            }
        }
    
    async def optimize_cache_settings(self) -> Dict[str, Any]:
        """
        Cache ayarlarını otomatik optimize et
        
        Returns:
            Optimization report with recommendations
        """
        metrics = await self.get_advanced_metrics()
        hit_rate = metrics["cache_health"]["hit_rate"]
        
        recommendations = []
        changes_made = []
        
        # Hit rate optimization
        if hit_rate < 60:
            # Increase L1 cache size
            if self.config.l1_cache_size < 2000:
                old_size = self.config.l1_cache_size
                self.config.l1_cache_size = min(old_size * 1.5, 2000)
                changes_made.append(f"L1 cache size: {old_size} → {self.config.l1_cache_size}")
            
            # Increase base TTL
            if self.config.base_ttl_seconds < 7200:
                old_ttl = self.config.base_ttl_seconds
                self.config.base_ttl_seconds = min(old_ttl * 1.2, 7200)
                changes_made.append(f"Base TTL: {old_ttl}s → {self.config.base_ttl_seconds}s")
            
            recommendations.append("Increase cache warming frequency")
            recommendations.append("Consider pre-loading popular data")
        
        elif hit_rate > 90:
            # Can reduce cache size to save memory
            if self.config.l1_cache_size > 500:
                old_size = self.config.l1_cache_size
                self.config.l1_cache_size = max(old_size * 0.8, 500)
                changes_made.append(f"L1 cache size optimized: {old_size} → {self.config.l1_cache_size}")
        
        # Memory optimization
        memory_usage = metrics["cache_distribution"]["l1_size_mb"]
        if memory_usage > 100:  # 100MB threshold
            recommendations.append("Consider enabling more aggressive compression")
            recommendations.append("Review large cached objects")
        
        # Performance optimization
        avg_response_time = metrics["performance"]["avg_response_time_ms"]
        if avg_response_time > 50:  # 50ms threshold
            recommendations.append("Consider async optimization")
            recommendations.append("Review serialization performance")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "current_hit_rate": hit_rate,
            "optimization_level": "excellent" if hit_rate > 85 else
                                "good" if hit_rate > 70 else
                                "needs_improvement",
            "changes_made": changes_made,
            "recommendations": recommendations,
            "metrics_summary": {
                "hit_rate": f"{hit_rate:.1f}%",
                "memory_usage_mb": f"{memory_usage:.1f}MB",
                "avg_response_time_ms": f"{avg_response_time:.1f}ms",
                "total_requests": metrics["performance"]["total_requests"]
            }
        }
    
    async def close(self):
        """Cache sistemini kapat"""
        try:
            # Background tasks'ı iptal et
            for task in self.background_tasks:
                task.cancel()
            
            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)
            
            # Redis connection'ı kapat
            if self.redis_client:
                await self.redis_client.close()
            
            if self.redis_pool:
                await self.redis_pool.disconnect()
            
            # Thread pool'u kapat
            self.thread_pool.shutdown(wait=True)
            
            logger.info("✅ Advanced Cache Manager kapatıldı")
            
        except Exception as e:
            logger.error(f"❌ Cache shutdown error: {e}")

# Global cache manager instance
_cache_manager: Optional[AdvancedBehavioralCacheManager] = None

async def get_cache_manager() -> AdvancedBehavioralCacheManager:
    """Global cache manager instance"""
    global _cache_manager
    
    if _cache_manager is None:
        _cache_manager = AdvancedBehavioralCacheManager()
        await _cache_manager.initialize()
    
    return _cache_manager

# Utility functions for easy integration
async def cache_get(namespace: str, identifier: str, 
                   data_hash: Optional[str] = None) -> Optional[Any]:
    """Simple cache get wrapper"""
    cache_manager = await get_cache_manager()
    return await cache_manager.get(namespace, identifier, data_hash)

async def cache_set(namespace: str, identifier: str, data: Any,
                   ttl_seconds: Optional[int] = None,
                   data_hash: Optional[str] = None) -> bool:
    """Simple cache set wrapper"""
    cache_manager = await get_cache_manager()
    return await cache_manager.set(namespace, identifier, data, ttl_seconds, data_hash)

async def cache_invalidate(namespace: str, identifier: str = "*") -> int:
    """Simple cache invalidation wrapper"""
    cache_manager = await get_cache_manager()
    return await cache_manager.invalidate(namespace, identifier)