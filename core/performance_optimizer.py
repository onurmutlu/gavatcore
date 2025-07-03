#!/usr/bin/env python3
# core/performance_optimizer.py - GAVATCORE Performans Optimizasyon Sistemi

import asyncio
import time
import json
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from contextlib import asynccontextmanager
import weakref
import gc
import psutil
import logging

# Database imports
from core.db.connection import get_db_session
from core.profile_store import get_profile_by_username, create_or_update_profile
from utils.redis_client import redis_client, set_state, get_state
from utils.log_utils import log_event

# Performance monitoring
import structlog
logger = structlog.get_logger("gavatcore.performance")

@dataclass
class PerformanceMetrics:
    """Performans metrikleri"""
    operation_name: str
    start_time: float
    end_time: float
    duration: float
    memory_before: float
    memory_after: float
    cache_hit: bool = False
    error: Optional[str] = None
    
    @property
    def memory_delta(self) -> float:
        return self.memory_after - self.memory_before

@dataclass
class CacheConfig:
    """Cache konfigürasyonu"""
    ttl: int = 300  # 5 dakika
    max_size: int = 1000
    cleanup_threshold: float = 0.8  # %80 dolduğunda temizle
    compression: bool = True
    persistence: bool = False

class AdvancedCache:
    """Gelişmiş cache sistemi"""
    
    def __init__(self, name: str, config: CacheConfig):
        self.name = name
        self.config = config
        self._cache: Dict[str, Tuple[Any, float, int]] = {}  # key: (value, timestamp, access_count)
        self._access_order = deque()  # LRU için
        self._lock = asyncio.Lock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "memory_usage": 0
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """Cache'den değer al"""
        async with self._lock:
            if key in self._cache:
                value, timestamp, access_count = self._cache[key]
                
                # TTL kontrolü
                if time.time() - timestamp < self.config.ttl:
                    # Access count ve order güncelle
                    self._cache[key] = (value, timestamp, access_count + 1)
                    self._access_order.append(key)
                    self._stats["hits"] += 1
                    return value
                else:
                    # Expired
                    del self._cache[key]
            
            self._stats["misses"] += 1
            return None
    
    async def set(self, key: str, value: Any) -> None:
        """Cache'e değer kaydet"""
        async with self._lock:
            current_time = time.time()
            
            # Boyut kontrolü ve temizlik
            if len(self._cache) >= self.config.max_size * self.config.cleanup_threshold:
                await self._cleanup()
            
            self._cache[key] = (value, current_time, 1)
            self._access_order.append(key)
            
            # Redis'e persist et
            if self.config.persistence and redis_client:
                try:
                    cache_key = f"cache:{self.name}:{key}"
                    if self.config.compression:
                        import pickle
                        import zlib
                        compressed_value = zlib.compress(pickle.dumps(value))
                        await redis_client.set(cache_key, compressed_value, ex=self.config.ttl)
                    else:
                        await redis_client.set(cache_key, json.dumps(value), ex=self.config.ttl)
                except Exception as e:
                    logger.warning(f"Cache persistence hatası: {e}")
    
    async def _cleanup(self) -> None:
        """LRU temizlik"""
        target_size = int(self.config.max_size * 0.7)  # %70'e düşür
        
        # Access count ve timestamp'e göre sırala
        sorted_items = sorted(
            self._cache.items(),
            key=lambda x: (x[1][2], x[1][1])  # access_count, timestamp
        )
        
        # En az kullanılanları sil
        for key, _ in sorted_items[:len(self._cache) - target_size]:
            del self._cache[key]
            self._stats["evictions"] += 1
        
        # Access order'ı temizle
        self._access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Cache istatistikleri"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_ratio = self._stats["hits"] / max(total_requests, 1)
        
        return {
            "name": self.name,
            "size": len(self._cache),
            "max_size": self.config.max_size,
            "hit_ratio": hit_ratio,
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "evictions": self._stats["evictions"],
            "memory_usage": self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> int:
        """Tahmini memory kullanımı (bytes)"""
        import sys
        total_size = 0
        for key, (value, _, _) in self._cache.items():
            total_size += sys.getsizeof(key) + sys.getsizeof(value)
        return total_size

class DatabaseOptimizer:
    """Veritabanı optimizasyon sistemi"""
    
    def __init__(self):
        self.connection_pool_stats = defaultdict(int)
        self.query_cache = AdvancedCache("db_queries", CacheConfig(ttl=60, max_size=500))
        self.prepared_statements = {}
        self._query_metrics = deque(maxlen=1000)
    
    @asynccontextmanager
    async def optimized_db_session(self):
        """Optimize edilmiş database session"""
        start_time = time.time()
        memory_before = psutil.Process().memory_info().rss / 1024 / 1024
        
        try:
            async with get_db_session() as session:
                self.connection_pool_stats["active"] += 1
                yield session
                await session.commit()
        except Exception as e:
            await session.rollback()
            raise
        finally:
            self.connection_pool_stats["active"] -= 1
            self.connection_pool_stats["total"] += 1
            
            # Metrics kaydet
            end_time = time.time()
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024
            
            metric = PerformanceMetrics(
                operation_name="db_session",
                start_time=start_time,
                end_time=end_time,
                duration=end_time - start_time,
                memory_before=memory_before,
                memory_after=memory_after
            )
            self._query_metrics.append(metric)
    
    async def cached_query(self, query_func: Callable, cache_key: str, *args, **kwargs) -> Any:
        """Cache'li query execution"""
        # Cache'den kontrol et
        cached_result = await self.query_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Query çalıştır
        start_time = time.time()
        try:
            result = await query_func(*args, **kwargs)
            await self.query_cache.set(cache_key, result)
            
            # Metrics
            duration = time.time() - start_time
            logger.info(f"Query executed: {cache_key} ({duration:.3f}s)")
            
            return result
        except Exception as e:
            logger.error(f"Query error: {cache_key} - {e}")
            raise
    
    def get_db_stats(self) -> Dict[str, Any]:
        """Database istatistikleri"""
        recent_queries = list(self._query_metrics)[-100:]  # Son 100 query
        avg_duration = sum(m.duration for m in recent_queries) / max(len(recent_queries), 1)
        
        return {
            "connection_pool": dict(self.connection_pool_stats),
            "query_cache": self.query_cache.get_stats(),
            "recent_avg_duration": avg_duration,
            "total_queries": len(self._query_metrics)
        }

class GPTOptimizer:
    """GPT/OpenAI optimizasyon sistemi"""
    
    def __init__(self):
        self.response_cache = AdvancedCache("gpt_responses", CacheConfig(ttl=1800, max_size=2000))  # 30 dakika
        self.rate_limiter = AsyncRateLimiter(max_calls=20, time_window=60)  # 20 call/dakika
        self.token_usage_tracker = defaultdict(int)
        self.cost_tracker = defaultdict(float)
        self._request_metrics = deque(maxlen=500)
    
    async def optimized_gpt_call(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        """Optimize edilmiş GPT çağrısı"""
        # Cache key oluştur
        cache_key = self._generate_cache_key(prompt, system_prompt, kwargs)
        
        # Cache'den kontrol et
        cached_response = await self.response_cache.get(cache_key)
        if cached_response:
            logger.info(f"GPT cache hit: {cache_key[:20]}...")
            return cached_response
        
        # Rate limiting
        await self.rate_limiter.acquire()
        
        # GPT çağrısı
        start_time = time.time()
        memory_before = psutil.Process().memory_info().rss / 1024 / 1024
        
        try:
            from gpt.openai_utils import call_openai_chat
            response = call_openai_chat(prompt, system_prompt)
            
            # Cache'e kaydet
            await self.response_cache.set(cache_key, response)
            
            # Token usage tracking
            estimated_tokens = len(prompt.split()) + len(response.split())
            self.token_usage_tracker[datetime.now().strftime("%Y-%m-%d")] += estimated_tokens
            
            # Cost estimation (gpt-3.5-turbo: $0.002/1K tokens)
            cost = (estimated_tokens / 1000) * 0.002
            self.cost_tracker[datetime.now().strftime("%Y-%m-%d")] += cost
            
            # Metrics
            end_time = time.time()
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024
            
            metric = PerformanceMetrics(
                operation_name="gpt_call",
                start_time=start_time,
                end_time=end_time,
                duration=end_time - start_time,
                memory_before=memory_before,
                memory_after=memory_after,
                cache_hit=False
            )
            self._request_metrics.append(metric)
            
            logger.info(f"GPT call completed: {len(response)} chars, {estimated_tokens} tokens, ${cost:.4f}")
            return response
            
        except Exception as e:
            logger.error(f"GPT call error: {e}")
            # Fallback response
            return "🤖 Şu an yanıt üretemiyorum, biraz sonra tekrar dene!"
    
    def _generate_cache_key(self, prompt: str, system_prompt: str, kwargs: Dict) -> str:
        """Cache key oluştur"""
        content = f"{prompt}|{system_prompt}|{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_gpt_stats(self) -> Dict[str, Any]:
        """GPT istatistikleri"""
        today = datetime.now().strftime("%Y-%m-%d")
        recent_requests = list(self._request_metrics)[-50:]
        avg_duration = sum(m.duration for m in recent_requests) / max(len(recent_requests), 1)
        
        return {
            "response_cache": self.response_cache.get_stats(),
            "rate_limiter": self.rate_limiter.get_stats(),
            "token_usage_today": self.token_usage_tracker[today],
            "cost_today": self.cost_tracker[today],
            "avg_response_time": avg_duration,
            "total_requests": len(self._request_metrics)
        }

class AsyncRateLimiter:
    """Async rate limiter"""
    
    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Rate limit acquire"""
        async with self._lock:
            now = time.time()
            
            # Eski çağrıları temizle
            while self.calls and now - self.calls[0] > self.time_window:
                self.calls.popleft()
            
            # Limit kontrolü
            if len(self.calls) >= self.max_calls:
                sleep_time = self.time_window - (now - self.calls[0])
                if sleep_time > 0:
                    logger.info(f"Rate limit: {sleep_time:.2f}s bekleniyor...")
                    await asyncio.sleep(sleep_time)
                    return await self.acquire()
            
            self.calls.append(now)
    
    def get_stats(self) -> Dict[str, Any]:
        """Rate limiter istatistikleri"""
        now = time.time()
        recent_calls = [call for call in self.calls if now - call <= self.time_window]
        
        return {
            "max_calls": self.max_calls,
            "time_window": self.time_window,
            "current_calls": len(recent_calls),
            "remaining_calls": max(0, self.max_calls - len(recent_calls))
        }

class LogOptimizer:
    """Log optimizasyon sistemi"""
    
    def __init__(self):
        self.log_buffer = defaultdict(list)
        self.buffer_size = 100
        self.flush_interval = 30  # saniye
        self.log_cache = AdvancedCache("logs", CacheConfig(ttl=120, max_size=1000))
        self._last_flush = time.time()
        self._log_metrics = defaultdict(int)
    
    async def optimized_log(self, user_id: str, event_type: str, message: str, level: str = "INFO") -> None:
        """Optimize edilmiş loglama"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "event_type": event_type,
            "message": message,
            "level": level
        }
        
        # Buffer'a ekle
        self.log_buffer[user_id].append(log_entry)
        self._log_metrics[level] += 1
        
        # Buffer flush kontrolü
        if (len(self.log_buffer[user_id]) >= self.buffer_size or 
            time.time() - self._last_flush > self.flush_interval):
            await self._flush_logs(user_id)
    
    async def _flush_logs(self, user_id: Optional[str] = None) -> None:
        """Log buffer'ını flush et"""
        try:
            if user_id:
                users_to_flush = [user_id]
            else:
                users_to_flush = list(self.log_buffer.keys())
            
            for uid in users_to_flush:
                if uid in self.log_buffer and self.log_buffer[uid]:
                    logs = self.log_buffer[uid].copy()
                    self.log_buffer[uid].clear()
                    
                    # Batch insert to database
                    await self._batch_insert_logs(logs)
            
            self._last_flush = time.time()
            
        except Exception as e:
            logger.error(f"Log flush error: {e}")
    
    async def _batch_insert_logs(self, logs: List[Dict]) -> None:
        """Batch log insertion"""
        try:
            from core.db.crud import log_event
            
            # Batch olarak database'e kaydet
            tasks = []
            for log_entry in logs:
                task = log_event(
                    user_identifier=log_entry["user_id"],
                    event_type=log_entry["event_type"],
                    message=log_entry["message"],
                    level=log_entry["level"]
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Batch log insert error: {e}")
    
    async def get_cached_logs(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Cache'li log getirme"""
        cache_key = f"logs:{user_id}:{limit}"
        
        cached_logs = await self.log_cache.get(cache_key)
        if cached_logs:
            return cached_logs
        
        # Database'den getir
        try:
            from core.db.crud import get_events
            events = await get_events(user_identifier=user_id, limit=limit)
            
            # Format ve cache'e kaydet
            formatted_logs = [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "message": event.message,
                    "level": event.level
                }
                for event in events
            ]
            
            await self.log_cache.set(cache_key, formatted_logs)
            return formatted_logs
            
        except Exception as e:
            logger.error(f"Log retrieval error: {e}")
            return []
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Log istatistikleri"""
        total_buffered = sum(len(logs) for logs in self.log_buffer.values())
        
        return {
            "buffer_size": total_buffered,
            "users_in_buffer": len(self.log_buffer),
            "log_cache": self.log_cache.get_stats(),
            "metrics_by_level": dict(self._log_metrics),
            "last_flush": self._last_flush
        }

class ConfigOptimizer:
    """Konfigürasyon optimizasyon sistemi"""
    
    def __init__(self):
        self.config_cache = AdvancedCache("configs", CacheConfig(ttl=600, max_size=200))  # 10 dakika
        self.profile_cache = AdvancedCache("profiles", CacheConfig(ttl=300, max_size=500))  # 5 dakika
        self._config_versions = {}
        self._hot_configs = set()  # Sık kullanılan config'ler
    
    async def get_optimized_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """Optimize edilmiş profil getirme"""
        cache_key = f"profile:{username}"
        
        # Cache'den kontrol et
        cached_profile = await self.profile_cache.get(cache_key)
        if cached_profile:
            self._hot_configs.add(username)
            return cached_profile
        
        # Database'den getir
        try:
            profile = await get_profile_by_username(username)
            if profile:
                await self.profile_cache.set(cache_key, profile)
                return profile
        except Exception as e:
            logger.error(f"Profile retrieval error for {username}: {e}")
        
        return None
    
    async def update_optimized_profile(self, username: str, profile_data: Dict[str, Any]) -> bool:
        """Optimize edilmiş profil güncelleme"""
        try:
            # Database'e kaydet
            success = await create_or_update_profile(username, profile_data)
            
            if success:
                # Cache'i güncelle
                cache_key = f"profile:{username}"
                await self.profile_cache.set(cache_key, profile_data)
                
                # Version tracking
                self._config_versions[username] = time.time()
                
                return True
        except Exception as e:
            logger.error(f"Profile update error for {username}: {e}")
        
        return False
    
    async def get_hot_configs(self) -> List[str]:
        """Sık kullanılan config'leri getir"""
        return list(self._hot_configs)
    
    async def preload_hot_configs(self) -> None:
        """Sık kullanılan config'leri önceden yükle"""
        for username in self._hot_configs:
            await self.get_optimized_profile(username)
    
    def get_config_stats(self) -> Dict[str, Any]:
        """Config istatistikleri"""
        return {
            "profile_cache": self.profile_cache.get_stats(),
            "config_cache": self.config_cache.get_stats(),
            "hot_configs": len(self._hot_configs),
            "config_versions": len(self._config_versions)
        }

class PerformanceOptimizer:
    """Ana performans optimizasyon sistemi"""
    
    def __init__(self):
        self.db_optimizer = DatabaseOptimizer()
        self.gpt_optimizer = GPTOptimizer()
        self.log_optimizer = LogOptimizer()
        self.config_optimizer = ConfigOptimizer()
        
        # Global metrics
        self._system_metrics = deque(maxlen=1000)
        self._optimization_tasks = []
        self._monitoring_active = False
    
    async def start_monitoring(self) -> None:
        """Performans monitoring'i başlat"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        
        # Background tasks
        self._optimization_tasks = [
            asyncio.create_task(self._memory_monitor()),
            asyncio.create_task(self._cache_maintenance()),
            asyncio.create_task(self._log_flusher()),
            asyncio.create_task(self._config_preloader())
        ]
        
        logger.info("🚀 Performance monitoring başlatıldı")
    
    async def stop_monitoring(self) -> None:
        """Performans monitoring'i durdur"""
        self._monitoring_active = False
        
        for task in self._optimization_tasks:
            task.cancel()
        
        await asyncio.gather(*self._optimization_tasks, return_exceptions=True)
        logger.info("🛑 Performance monitoring durduruldu")
    
    async def _memory_monitor(self) -> None:
        """Memory monitoring"""
        while self._monitoring_active:
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                cpu_percent = process.cpu_percent()
                
                metric = {
                    "timestamp": time.time(),
                    "memory_rss": memory_info.rss / 1024 / 1024,  # MB
                    "memory_vms": memory_info.vms / 1024 / 1024,  # MB
                    "cpu_percent": cpu_percent,
                    "threads": process.num_threads()
                }
                
                self._system_metrics.append(metric)
                
                # Memory threshold kontrolü
                if memory_info.rss > 500 * 1024 * 1024:  # 500MB
                    logger.warning(f"High memory usage: {memory_info.rss / 1024 / 1024:.1f}MB")
                    gc.collect()  # Garbage collection
                
                await asyncio.sleep(30)  # 30 saniye interval
                
            except Exception as e:
                logger.error(f"Memory monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _cache_maintenance(self) -> None:
        """Cache maintenance"""
        while self._monitoring_active:
            try:
                # Cache cleanup
                caches = [
                    self.db_optimizer.query_cache,
                    self.gpt_optimizer.response_cache,
                    self.log_optimizer.log_cache,
                    self.config_optimizer.profile_cache,
                    self.config_optimizer.config_cache
                ]
                
                for cache in caches:
                    await cache._cleanup()
                
                await asyncio.sleep(300)  # 5 dakika interval
                
            except Exception as e:
                logger.error(f"Cache maintenance error: {e}")
                await asyncio.sleep(600)
    
    async def _log_flusher(self) -> None:
        """Log flusher"""
        while self._monitoring_active:
            try:
                await self.log_optimizer._flush_logs()
                await asyncio.sleep(30)  # 30 saniye interval
                
            except Exception as e:
                logger.error(f"Log flusher error: {e}")
                await asyncio.sleep(60)
    
    async def _config_preloader(self) -> None:
        """Config preloader"""
        while self._monitoring_active:
            try:
                await self.config_optimizer.preload_hot_configs()
                await asyncio.sleep(600)  # 10 dakika interval
                
            except Exception as e:
                logger.error(f"Config preloader error: {e}")
                await asyncio.sleep(1200)
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Kapsamlı sistem istatistikleri"""
        recent_metrics = list(self._system_metrics)[-10:]  # Son 10 metric
        
        if recent_metrics:
            avg_memory = sum(m["memory_rss"] for m in recent_metrics) / len(recent_metrics)
            avg_cpu = sum(m["cpu_percent"] for m in recent_metrics) / len(recent_metrics)
        else:
            avg_memory = avg_cpu = 0
        
        return {
            "system": {
                "avg_memory_mb": avg_memory,
                "avg_cpu_percent": avg_cpu,
                "monitoring_active": self._monitoring_active,
                "total_metrics": len(self._system_metrics)
            },
            "database": self.db_optimizer.get_db_stats(),
            "gpt": self.gpt_optimizer.get_gpt_stats(),
            "logging": self.log_optimizer.get_log_stats(),
            "config": self.config_optimizer.get_config_stats()
        }
    
    async def optimize_system(self) -> Dict[str, Any]:
        """Sistem optimizasyonu çalıştır"""
        start_time = time.time()
        optimizations = []
        
        try:
            # Memory optimization
            gc.collect()
            optimizations.append("memory_gc")
            
            # Cache optimization
            await self._cache_maintenance()
            optimizations.append("cache_cleanup")
            
            # Log optimization
            await self.log_optimizer._flush_logs()
            optimizations.append("log_flush")
            
            # Config optimization
            await self.config_optimizer.preload_hot_configs()
            optimizations.append("config_preload")
            
            duration = time.time() - start_time
            
            return {
                "success": True,
                "duration": duration,
                "optimizations": optimizations,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time,
                "optimizations": optimizations
            }

# Global optimizer instance
performance_optimizer = PerformanceOptimizer()

# Convenience functions
async def start_performance_monitoring():
    """Performans monitoring'i başlat"""
    await performance_optimizer.start_monitoring()

async def stop_performance_monitoring():
    """Performans monitoring'i durdur"""
    await performance_optimizer.stop_monitoring()

async def get_performance_stats():
    """Performans istatistiklerini getir"""
    return performance_optimizer.get_comprehensive_stats()

async def optimize_system():
    """Sistem optimizasyonu çalıştır"""
    return await performance_optimizer.optimize_system()

# Decorators
def performance_monitor(operation_name: str):
    """Performans monitoring decorator"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            memory_before = psutil.Process().memory_info().rss / 1024 / 1024
            
            try:
                result = await func(*args, **kwargs)
                error = None
            except Exception as e:
                error = str(e)
                raise
            finally:
                end_time = time.time()
                memory_after = psutil.Process().memory_info().rss / 1024 / 1024
                
                metric = PerformanceMetrics(
                    operation_name=operation_name,
                    start_time=start_time,
                    end_time=end_time,
                    duration=end_time - start_time,
                    memory_before=memory_before,
                    memory_after=memory_after,
                    error=error
                )
                
                logger.info(f"Performance: {operation_name} - {metric.duration:.3f}s, {metric.memory_delta:.1f}MB")
            
            return result
        return wrapper
    return decorator 