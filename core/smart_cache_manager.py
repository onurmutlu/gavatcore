#!/usr/bin/env python3
# core/smart_cache_manager.py - Akıllı Cache Yönetim Sistemi

import asyncio
import time
import json
import pickle
import zlib
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple, Union, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import weakref
import threading

# Database imports
from utilities.redis_client import redis_client
from utilities.log_utils import log_event

# Performance monitoring
import structlog
logger = structlog.get_logger("gavatcore.cache")

T = TypeVar('T')

class CacheStrategy(Enum):
    """Cache stratejileri"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Adaptive strategy
    WRITE_THROUGH = "write_through"  # Write-through cache
    WRITE_BACK = "write_back"  # Write-back cache

class CacheLevel(Enum):
    """Cache seviyeleri"""
    L1_MEMORY = "l1_memory"  # In-memory cache
    L2_REDIS = "l2_redis"    # Redis cache
    L3_DATABASE = "l3_database"  # Database cache

@dataclass
class CachePolicy:
    """Cache politikası"""
    strategy: CacheStrategy = CacheStrategy.ADAPTIVE
    ttl: int = 300  # 5 dakika
    max_size: int = 1000
    compression: bool = True
    persistence: bool = True
    auto_refresh: bool = False
    refresh_threshold: float = 0.8  # %80 TTL'de refresh
    priority_levels: int = 3
    
@dataclass
class CacheEntry(Generic[T]):
    """Cache entry"""
    key: str
    value: T
    timestamp: float
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    priority: int = 1
    size: int = 0
    compressed: bool = False
    dirty: bool = False  # Write-back için
    
    @property
    def age(self) -> float:
        return time.time() - self.timestamp
    
    @property
    def idle_time(self) -> float:
        return time.time() - self.last_access
    
    def access(self) -> None:
        """Entry'ye erişim kaydı"""
        self.access_count += 1
        self.last_access = time.time()

class SmartCacheManager:
    """Akıllı cache yönetim sistemi"""
    
    def __init__(self, name: str, policy: CachePolicy):
        self.name = name
        self.policy = policy
        
        # Multi-level cache
        self.l1_cache: Dict[str, CacheEntry] = {}  # Memory cache
        self.l2_keys: set = set()  # Redis'te olan key'ler
        
        # Cache statistics
        self.stats = {
            "hits": {"l1": 0, "l2": 0, "l3": 0},
            "misses": 0,
            "evictions": 0,
            "compressions": 0,
            "refreshes": 0,
            "writes": 0,
            "errors": 0
        }
        
        # Locks
        self._lock = asyncio.Lock()
        self._refresh_lock = asyncio.Lock()
        
        # Background tasks
        self._maintenance_task = None
        self._write_back_task = None
        
        # Priority queues
        self.priority_queues = [deque() for _ in range(policy.priority_levels)]
        
        # Adaptive learning
        self.access_patterns = defaultdict(list)
        self.prediction_model = {}
        
    async def start(self) -> None:
        """Cache manager'ı başlat"""
        if self._maintenance_task is None:
            self._maintenance_task = asyncio.create_task(self._maintenance_loop())
            
        if self.policy.strategy == CacheStrategy.WRITE_BACK and self._write_back_task is None:
            self._write_back_task = asyncio.create_task(self._write_back_loop())
            
        logger.info(f"Smart cache manager başlatıldı: {self.name}")
    
    async def stop(self) -> None:
        """Cache manager'ı durdur"""
        if self._maintenance_task:
            self._maintenance_task.cancel()
            
        if self._write_back_task:
            self._write_back_task.cancel()
            
        # Dirty entries'leri flush et
        await self._flush_dirty_entries()
        
        logger.info(f"Smart cache manager durduruldu: {self.name}")
    
    async def get(self, key: str, default: T = None) -> Optional[T]:
        """Cache'den değer al"""
        async with self._lock:
            # L1 Cache (Memory)
            if key in self.l1_cache:
                entry = self.l1_cache[key]
                
                # TTL kontrolü
                if entry.age < self.policy.ttl:
                    entry.access()
                    self.stats["hits"]["l1"] += 1
                    
                    # Auto refresh kontrolü
                    if (self.policy.auto_refresh and 
                        entry.age > self.policy.ttl * self.policy.refresh_threshold):
                        asyncio.create_task(self._auto_refresh(key))
                    
                    # Access pattern learning
                    self._learn_access_pattern(key)
                    
                    return entry.value
                else:
                    # Expired
                    await self._evict_entry(key)
            
            # L2 Cache (Redis)
            if key in self.l2_keys and redis_client:
                try:
                    redis_key = self._redis_key(key)
                    cached_data = await redis_client.get(redis_key)
                    
                    if cached_data:
                        value = await self._deserialize(cached_data)
                        
                        # L1'e promote et
                        await self._set_l1(key, value, priority=2)
                        
                        self.stats["hits"]["l2"] += 1
                        self._learn_access_pattern(key)
                        
                        return value
                    else:
                        self.l2_keys.discard(key)
                        
                except Exception as e:
                    logger.error(f"L2 cache error: {e}")
                    self.stats["errors"] += 1
            
            # Cache miss
            self.stats["misses"] += 1
            return default
    
    async def set(self, key: str, value: T, priority: int = 1, ttl: Optional[int] = None) -> None:
        """Cache'e değer kaydet"""
        async with self._lock:
            effective_ttl = ttl or self.policy.ttl
            
            # L1 Cache'e kaydet
            await self._set_l1(key, value, priority, effective_ttl)
            
            # L2 Cache'e kaydet (persistence enabled ise)
            if self.policy.persistence and redis_client:
                try:
                    await self._set_l2(key, value, effective_ttl)
                except Exception as e:
                    logger.error(f"L2 cache set error: {e}")
                    self.stats["errors"] += 1
            
            self.stats["writes"] += 1
    
    async def _set_l1(self, key: str, value: T, priority: int = 1, ttl: int = None) -> None:
        """L1 cache'e kaydet"""
        # Boyut kontrolü
        if len(self.l1_cache) >= self.policy.max_size:
            await self._evict_by_strategy()
        
        # Entry oluştur
        entry = CacheEntry(
            key=key,
            value=value,
            timestamp=time.time(),
            priority=min(priority, self.policy.priority_levels - 1),
            size=self._estimate_size(value)
        )
        
        # Compression
        if self.policy.compression and entry.size > 1024:  # 1KB üzeri compress
            try:
                compressed_value = await self._compress(value)
                if len(compressed_value) < entry.size * 0.8:  # %20 tasarruf varsa
                    entry.value = compressed_value
                    entry.compressed = True
                    entry.size = len(compressed_value)
                    self.stats["compressions"] += 1
            except Exception as e:
                logger.warning(f"Compression failed: {e}")
        
        self.l1_cache[key] = entry
        
        # Priority queue'ya ekle
        self.priority_queues[entry.priority].append(key)
    
    async def _set_l2(self, key: str, value: T, ttl: int) -> None:
        """L2 cache'e kaydet"""
        redis_key = self._redis_key(key)
        serialized_value = await self._serialize(value)
        
        await redis_client.set(redis_key, serialized_value, ex=ttl)
        self.l2_keys.add(key)
    
    async def delete(self, key: str) -> bool:
        """Cache'den sil"""
        async with self._lock:
            deleted = False
            
            # L1'den sil
            if key in self.l1_cache:
                await self._evict_entry(key)
                deleted = True
            
            # L2'den sil
            if key in self.l2_keys and redis_client:
                try:
                    redis_key = self._redis_key(key)
                    await redis_client.delete(redis_key)
                    self.l2_keys.discard(key)
                    deleted = True
                except Exception as e:
                    logger.error(f"L2 cache delete error: {e}")
            
            return deleted
    
    async def clear(self) -> None:
        """Cache'i temizle"""
        async with self._lock:
            # L1 temizle
            self.l1_cache.clear()
            for queue in self.priority_queues:
                queue.clear()
            
            # L2 temizle
            if redis_client:
                try:
                    redis_keys = [self._redis_key(key) for key in self.l2_keys]
                    if redis_keys:
                        await redis_client.delete(*redis_keys)
                    self.l2_keys.clear()
                except Exception as e:
                    logger.error(f"L2 cache clear error: {e}")
    
    async def _evict_by_strategy(self) -> None:
        """Strateji'ye göre eviction"""
        if self.policy.strategy == CacheStrategy.LRU:
            await self._evict_lru()
        elif self.policy.strategy == CacheStrategy.LFU:
            await self._evict_lfu()
        elif self.policy.strategy == CacheStrategy.ADAPTIVE:
            await self._evict_adaptive()
        else:
            await self._evict_priority()
    
    async def _evict_lru(self) -> None:
        """LRU eviction"""
        if not self.l1_cache:
            return
            
        oldest_key = min(self.l1_cache.keys(), 
                        key=lambda k: self.l1_cache[k].last_access)
        await self._evict_entry(oldest_key)
    
    async def _evict_lfu(self) -> None:
        """LFU eviction"""
        if not self.l1_cache:
            return
            
        least_used_key = min(self.l1_cache.keys(),
                           key=lambda k: self.l1_cache[k].access_count)
        await self._evict_entry(least_used_key)
    
    async def _evict_adaptive(self) -> None:
        """Adaptive eviction"""
        if not self.l1_cache:
            return
        
        # Scoring function: access_count / age
        def score(key: str) -> float:
            entry = self.l1_cache[key]
            return entry.access_count / max(entry.age, 1)
        
        lowest_score_key = min(self.l1_cache.keys(), key=score)
        await self._evict_entry(lowest_score_key)
    
    async def _evict_priority(self) -> None:
        """Priority-based eviction"""
        # En düşük priority'den başla
        for priority in range(self.policy.priority_levels):
            queue = self.priority_queues[priority]
            while queue:
                key = queue.popleft()
                if key in self.l1_cache:
                    await self._evict_entry(key)
                    return
    
    async def _evict_entry(self, key: str) -> None:
        """Entry'yi evict et"""
        if key in self.l1_cache:
            entry = self.l1_cache[key]
            
            # Write-back strategy için dirty check
            if entry.dirty and self.policy.strategy == CacheStrategy.WRITE_BACK:
                await self._write_back_entry(key, entry)
            
            del self.l1_cache[key]
            self.stats["evictions"] += 1
            
            # Priority queue'dan da çıkar
            for queue in self.priority_queues:
                if key in queue:
                    queue.remove(key)
                    break
    
    async def _auto_refresh(self, key: str) -> None:
        """Auto refresh"""
        async with self._refresh_lock:
            if key in self.l1_cache:
                # Refresh logic burada implement edilecek
                # Örneğin: database'den fresh data çek
                self.stats["refreshes"] += 1
                logger.debug(f"Auto refreshed: {key}")
    
    def _learn_access_pattern(self, key: str) -> None:
        """Access pattern learning"""
        now = time.time()
        self.access_patterns[key].append(now)
        
        # Son 100 access'i tut
        if len(self.access_patterns[key]) > 100:
            self.access_patterns[key] = self.access_patterns[key][-100:]
        
        # Pattern prediction
        if len(self.access_patterns[key]) >= 10:
            intervals = []
            accesses = self.access_patterns[key]
            for i in range(1, len(accesses)):
                intervals.append(accesses[i] - accesses[i-1])
            
            avg_interval = sum(intervals) / len(intervals)
            self.prediction_model[key] = {
                "avg_interval": avg_interval,
                "next_predicted": now + avg_interval
            }
    
    async def _maintenance_loop(self) -> None:
        """Maintenance loop"""
        while True:
            try:
                await asyncio.sleep(60)  # 1 dakika interval
                
                # TTL cleanup
                await self._cleanup_expired()
                
                # Memory pressure check
                await self._check_memory_pressure()
                
                # Statistics update
                await self._update_statistics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Maintenance loop error: {e}")
                await asyncio.sleep(60)
    
    async def _write_back_loop(self) -> None:
        """Write-back loop"""
        while True:
            try:
                await asyncio.sleep(30)  # 30 saniye interval
                await self._flush_dirty_entries()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Write-back loop error: {e}")
                await asyncio.sleep(30)
    
    async def _cleanup_expired(self) -> None:
        """Expired entries'leri temizle"""
        async with self._lock:
            expired_keys = []
            now = time.time()
            
            for key, entry in self.l1_cache.items():
                if entry.age > self.policy.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                await self._evict_entry(key)
    
    async def _check_memory_pressure(self) -> None:
        """Memory pressure kontrolü"""
        import psutil
        
        try:
            memory_percent = psutil.virtual_memory().percent
            
            if memory_percent > 80:  # %80 üzeri memory kullanımı
                # Agresif eviction
                target_size = int(len(self.l1_cache) * 0.7)  # %30 azalt
                
                while len(self.l1_cache) > target_size:
                    await self._evict_by_strategy()
                
                logger.warning(f"Memory pressure cleanup: {self.name}")
                
        except Exception as e:
            logger.error(f"Memory pressure check error: {e}")
    
    async def _flush_dirty_entries(self) -> None:
        """Dirty entries'leri flush et"""
        if self.policy.strategy != CacheStrategy.WRITE_BACK:
            return
        
        async with self._lock:
            dirty_entries = [(k, v) for k, v in self.l1_cache.items() if v.dirty]
            
            for key, entry in dirty_entries:
                await self._write_back_entry(key, entry)
    
    async def _write_back_entry(self, key: str, entry: CacheEntry) -> None:
        """Entry'yi write-back et"""
        try:
            # Write-back logic burada implement edilecek
            # Örneğin: database'e kaydet
            entry.dirty = False
            logger.debug(f"Write-back completed: {key}")
            
        except Exception as e:
            logger.error(f"Write-back error for {key}: {e}")
    
    async def _serialize(self, value: Any) -> bytes:
        """Serialize value"""
        if self.policy.compression:
            return zlib.compress(pickle.dumps(value))
        else:
            return pickle.dumps(value)
    
    async def _deserialize(self, data: bytes) -> Any:
        """Deserialize value"""
        if self.policy.compression:
            return pickle.loads(zlib.decompress(data))
        else:
            return pickle.loads(data)
    
    async def _compress(self, value: Any) -> bytes:
        """Compress value"""
        return zlib.compress(pickle.dumps(value))
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate object size"""
        import sys
        return sys.getsizeof(value)
    
    def _redis_key(self, key: str) -> str:
        """Redis key oluştur"""
        return f"smartcache:{self.name}:{key}"
    
    async def _update_statistics(self) -> None:
        """İstatistikleri güncelle"""
        # Cache efficiency metrics
        total_requests = sum(self.stats["hits"].values()) + self.stats["misses"]
        if total_requests > 0:
            hit_ratio = sum(self.stats["hits"].values()) / total_requests
            
            # Redis'e stats kaydet
            if redis_client:
                try:
                    stats_key = f"cache_stats:{self.name}"
                    stats_data = {
                        "hit_ratio": hit_ratio,
                        "total_requests": total_requests,
                        "l1_size": len(self.l1_cache),
                        "l2_size": len(self.l2_keys),
                        "timestamp": time.time()
                    }
                    await redis_client.hset(stats_key, mapping=stats_data)
                except Exception as e:
                    logger.error(f"Stats update error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Cache istatistikleri"""
        total_requests = sum(self.stats["hits"].values()) + self.stats["misses"]
        hit_ratio = sum(self.stats["hits"].values()) / max(total_requests, 1)
        
        l1_memory_usage = sum(entry.size for entry in self.l1_cache.values())
        
        return {
            "name": self.name,
            "policy": {
                "strategy": self.policy.strategy.value,
                "ttl": self.policy.ttl,
                "max_size": self.policy.max_size
            },
            "levels": {
                "l1_size": len(self.l1_cache),
                "l2_size": len(self.l2_keys),
                "l1_memory_mb": l1_memory_usage / 1024 / 1024
            },
            "performance": {
                "hit_ratio": hit_ratio,
                "l1_hit_ratio": self.stats["hits"]["l1"] / max(total_requests, 1),
                "l2_hit_ratio": self.stats["hits"]["l2"] / max(total_requests, 1),
                "total_requests": total_requests
            },
            "operations": dict(self.stats),
            "predictions": len(self.prediction_model)
        }

class CacheManagerFactory:
    """Cache manager factory"""
    
    _instances: Dict[str, SmartCacheManager] = {}
    
    @classmethod
    async def get_cache_manager(cls, name: str, policy: Optional[CachePolicy] = None) -> SmartCacheManager:
        """Cache manager instance al"""
        if name not in cls._instances:
            if policy is None:
                policy = CachePolicy()
            
            manager = SmartCacheManager(name, policy)
            await manager.start()
            cls._instances[name] = manager
        
        return cls._instances[name]
    
    @classmethod
    async def shutdown_all(cls) -> None:
        """Tüm cache manager'ları kapat"""
        for manager in cls._instances.values():
            await manager.stop()
        cls._instances.clear()

# Predefined cache managers
async def get_profile_cache() -> SmartCacheManager:
    """Profil cache manager"""
    policy = CachePolicy(
        strategy=CacheStrategy.ADAPTIVE,
        ttl=600,  # 10 dakika
        max_size=500,
        compression=True,
        persistence=True,
        auto_refresh=True
    )
    return await CacheManagerFactory.get_cache_manager("profiles", policy)

async def get_gpt_cache() -> SmartCacheManager:
    """GPT response cache manager"""
    policy = CachePolicy(
        strategy=CacheStrategy.LRU,
        ttl=1800,  # 30 dakika
        max_size=2000,
        compression=True,
        persistence=True,
        auto_refresh=False
    )
    return await CacheManagerFactory.get_cache_manager("gpt_responses", policy)

async def get_log_cache() -> SmartCacheManager:
    """Log cache manager"""
    policy = CachePolicy(
        strategy=CacheStrategy.TTL,
        ttl=300,  # 5 dakika
        max_size=1000,
        compression=False,
        persistence=False,
        auto_refresh=False
    )
    return await CacheManagerFactory.get_cache_manager("logs", policy)

async def get_session_cache() -> SmartCacheManager:
    """Session cache manager"""
    policy = CachePolicy(
        strategy=CacheStrategy.WRITE_BACK,
        ttl=3600,  # 1 saat
        max_size=200,
        compression=True,
        persistence=True,
        auto_refresh=True
    )
    return await CacheManagerFactory.get_cache_manager("sessions", policy)

# Convenience functions
async def cached_get(cache_name: str, key: str, default=None):
    """Cache'den değer al"""
    manager = await CacheManagerFactory.get_cache_manager(cache_name)
    return await manager.get(key, default)

async def cached_set(cache_name: str, key: str, value, priority: int = 1, ttl: Optional[int] = None):
    """Cache'e değer kaydet"""
    manager = await CacheManagerFactory.get_cache_manager(cache_name)
    await manager.set(key, value, priority, ttl)

async def get_all_cache_stats() -> Dict[str, Any]:
    """Tüm cache istatistikleri"""
    stats = {}
    for name, manager in CacheManagerFactory._instances.items():
        stats[name] = manager.get_stats()
    return stats 