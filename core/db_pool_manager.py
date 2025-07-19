from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
# core/db_pool_manager.py - Gelişmiş Database Connection Pool Yönetimi

import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple, Union, Callable, AsyncContextManager
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import threading
import weakref
import logging

# Database imports
import asyncpg
import aiosqlite
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool, NullPool, StaticPool
import redis.asyncio as redis

# Performance monitoring
import structlog
logger = structlog.get_logger("gavatcore.db_pool")

class DatabaseType(Enum):
    """Veritabanı türleri"""
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    REDIS = "redis"

class PoolStrategy(Enum):
    """Pool stratejileri"""
    STATIC = "static"  # Sabit boyut
    DYNAMIC = "dynamic"  # Dinamik boyut
    ADAPTIVE = "adaptive"  # Adaptif boyut
    LOAD_BALANCED = "load_balanced"  # Load balanced

@dataclass
class PoolConfig:
    """Pool konfigürasyonu"""
    min_size: int = 5
    max_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600  # 1 saat
    pool_pre_ping: bool = True
    retry_attempts: int = 3
    retry_delay: float = 1.0
    health_check_interval: int = 60
    connection_lifetime: int = 7200  # 2 saat
    idle_timeout: int = 300  # 5 dakika
    
@dataclass
class ConnectionMetrics:
    """Connection metrikleri"""
    created_at: float
    last_used: float
    usage_count: int = 0
    error_count: int = 0
    total_time: float = 0.0
    is_healthy: bool = True
    
    @property
    def age(self) -> float:
        return time.time() - self.created_at
    
    @property
    def idle_time(self) -> float:
        return time.time() - self.last_used
    
    @property
    def avg_response_time(self) -> float:
        return self.total_time / max(self.usage_count, 1)

class SmartConnectionPool:
    """Akıllı connection pool"""
    
    def __init__(self, name: str, db_type: DatabaseType, config: PoolConfig, connection_string: str):
        self.name = name
        self.db_type = db_type
        self.config = config
        self.connection_string = connection_string
        
        # Pool state
        self._pool = None
        self._connections: Dict[str, Any] = {}
        self._metrics: Dict[str, ConnectionMetrics] = {}
        self._available_connections = asyncio.Queue()
        self._active_connections = set()
        
        # Statistics
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "idle_connections": 0,
            "failed_connections": 0,
            "total_queries": 0,
            "failed_queries": 0,
            "avg_response_time": 0.0,
            "pool_hits": 0,
            "pool_misses": 0
        }
        
        # Locks
        self._lock = asyncio.Lock()
        self._health_check_lock = asyncio.Lock()
        
        # Background tasks
        self._health_check_task = None
        self._cleanup_task = None
        self._monitoring_task = None
        
        # Load balancing
        self._connection_weights = defaultdict(float)
        self._last_used_index = 0
        
    async def initialize(self) -> None:
        """Pool'u başlat"""
        try:
            if self.db_type == DatabaseType.POSTGRESQL:
                await self._init_postgresql()
            elif self.db_type == DatabaseType.SQLITE:
                await self._init_sqlite()
            elif self.db_type == DatabaseType.MONGODB:
                await self._init_mongodb()
            elif self.db_type == DatabaseType.REDIS:
                await self._init_redis()
            
            # Background tasks başlat
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info(f"Connection pool başlatıldı: {self.name} ({self.db_type.value})")
            
        except Exception as e:
            logger.error(f"Pool initialization error: {e}")
            raise
    
    async def _init_postgresql(self) -> None:
        """PostgreSQL pool başlat"""
        self._pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=self.config.min_size,
            max_size=self.config.max_size,
            command_timeout=self.config.pool_timeout,
            server_settings={
                'application_name': f'gavatcore_{self.name}',
                'jit': 'off'  # Performance için
            }
        )
        
        # Initial connections oluştur
        for _ in range(self.config.min_size):
            await self._create_connection()
    
    async def _init_sqlite(self) -> None:
        """SQLite pool başlat"""
        # SQLite için custom pool implementation
        for _ in range(self.config.min_size):
            await self._create_sqlite_connection()
    
    async def _init_mongodb(self) -> None:
        """MongoDB pool başlat"""
        self._pool = AsyncIOMotorClient(
            self.connection_string,
            maxPoolSize=self.config.max_size,
            minPoolSize=self.config.min_size,
            maxIdleTimeMS=self.config.idle_timeout * 1000,
            serverSelectionTimeoutMS=self.config.pool_timeout * 1000
        )
    
    async def _init_redis(self) -> None:
        """Redis pool başlat"""
        self._pool = redis.ConnectionPool.from_url(
            self.connection_string,
            max_connections=self.config.max_size,
            retry_on_timeout=True,
            health_check_interval=self.config.health_check_interval
        )
    
    async def _create_connection(self) -> str:
        """Yeni connection oluştur"""
        connection_id = f"{self.name}_{len(self._connections)}_{time.time()}"
        
        try:
            if self.db_type == DatabaseType.POSTGRESQL:
                conn = await self._pool.acquire()
            elif self.db_type == DatabaseType.SQLITE:
                conn = await self._create_sqlite_connection()
            elif self.db_type == DatabaseType.MONGODB:
                conn = self._pool
            elif self.db_type == DatabaseType.REDIS:
                conn = redis.Redis(connection_pool=self._pool)
            
            self._connections[connection_id] = conn
            self._metrics[connection_id] = ConnectionMetrics(
                created_at=time.time(),
                last_used=time.time()
            )
            
            await self._available_connections.put(connection_id)
            self.stats["total_connections"] += 1
            
            return connection_id
            
        except Exception as e:
            logger.error(f"Connection creation error: {e}")
            self.stats["failed_connections"] += 1
            raise
    
    async def _create_sqlite_connection(self) -> aiosqlite.Connection:
        """SQLite connection oluştur"""
        return await aiosqlite.connect(
            self.connection_string,
            timeout=self.config.pool_timeout,
            isolation_level=None  # Autocommit mode
        )
    
    async def acquire_connection(self) -> AsyncContextManager:
        """Connection al"""
        return SmartConnectionContext(self)
    
    async def _acquire_connection_internal(self) -> Tuple[str, Any]:
        """Internal connection acquire"""
        async with self._lock:
            # Available connection var mı?
            try:
                connection_id = await asyncio.wait_for(
                    self._available_connections.get(),
                    timeout=self.config.pool_timeout
                )
                
                # Connection health check
                if not await self._check_connection_health(connection_id):
                    await self._recreate_connection(connection_id)
                
                # Metrics güncelle
                metrics = self._metrics[connection_id]
                metrics.last_used = time.time()
                metrics.usage_count += 1
                
                self._active_connections.add(connection_id)
                self.stats["active_connections"] += 1
                self.stats["pool_hits"] += 1
                
                return connection_id, self._connections[connection_id]
                
            except asyncio.TimeoutError:
                # Pool timeout - yeni connection oluştur
                if len(self._connections) < self.config.max_size + self.config.max_overflow:
                    connection_id = await self._create_connection()
                    connection_id = await self._available_connections.get()
                    
                    self._active_connections.add(connection_id)
                    self.stats["active_connections"] += 1
                    self.stats["pool_misses"] += 1
                    
                    return connection_id, self._connections[connection_id]
                else:
                    raise Exception("Pool exhausted")
    
    async def _release_connection_internal(self, connection_id: str, error: Optional[Exception] = None) -> None:
        """Internal connection release"""
        async with self._lock:
            if connection_id in self._active_connections:
                self._active_connections.remove(connection_id)
                self.stats["active_connections"] -= 1
                
                # Error handling
                if error:
                    self._metrics[connection_id].error_count += 1
                    self.stats["failed_queries"] += 1
                    
                    # Connection'ı yeniden oluştur
                    if self._metrics[connection_id].error_count > 3:
                        await self._recreate_connection(connection_id)
                        return
                
                # Connection'ı available pool'a geri koy
                await self._available_connections.put(connection_id)
    
    async def _check_connection_health(self, connection_id: str) -> bool:
        """Connection health check"""
        try:
            conn = self._connections[connection_id]
            metrics = self._metrics[connection_id]
            
            # Age check
            if metrics.age > self.config.connection_lifetime:
                return False
            
            # Idle timeout check
            if metrics.idle_time > self.config.idle_timeout:
                return False
            
            # Database specific health check
            if self.db_type == DatabaseType.POSTGRESQL:
                await conn.execute("SELECT 1")
            elif self.db_type == DatabaseType.SQLITE:
                await conn.execute("SELECT 1")
            elif self.db_type == DatabaseType.MONGODB:
                await conn.admin.command('ping')
            elif self.db_type == DatabaseType.REDIS:
                await conn.ping()
            
            metrics.is_healthy = True
            return True
            
        except Exception as e:
            logger.warning(f"Health check failed for {connection_id}: {e}")
            self._metrics[connection_id].is_healthy = False
            return False
    
    async def _recreate_connection(self, connection_id: str) -> None:
        """Connection'ı yeniden oluştur"""
        try:
            # Eski connection'ı kapat
            await self._close_connection(connection_id)
            
            # Yeni connection oluştur
            new_connection_id = await self._create_connection()
            
            logger.info(f"Connection recreated: {connection_id} -> {new_connection_id}")
            
        except Exception as e:
            logger.error(f"Connection recreation error: {e}")
    
    async def _close_connection(self, connection_id: str) -> None:
        """Connection'ı kapat"""
        if connection_id in self._connections:
            try:
                conn = self._connections[connection_id]
                
                if self.db_type == DatabaseType.POSTGRESQL:
                    await self._pool.release(conn)
                elif self.db_type == DatabaseType.SQLITE:
                    await conn.close()
                elif self.db_type == DatabaseType.REDIS:
                    await conn.close()
                
                del self._connections[connection_id]
                del self._metrics[connection_id]
                
            except Exception as e:
                logger.error(f"Connection close error: {e}")
    
    async def _health_check_loop(self) -> None:
        """Health check loop"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                
                async with self._health_check_lock:
                    unhealthy_connections = []
                    
                    for connection_id in list(self._connections.keys()):
                        if not await self._check_connection_health(connection_id):
                            unhealthy_connections.append(connection_id)
                    
                    # Unhealthy connections'ları yeniden oluştur
                    for connection_id in unhealthy_connections:
                        await self._recreate_connection(connection_id)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Cleanup loop"""
        while True:
            try:
                await asyncio.sleep(300)  # 5 dakika interval
                
                # Idle connections'ları temizle
                await self._cleanup_idle_connections()
                
                # Metrics temizle
                await self._cleanup_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    async def _cleanup_idle_connections(self) -> None:
        """Idle connections'ları temizle"""
        async with self._lock:
            idle_connections = []
            min_connections = self.config.min_size
            
            for connection_id, metrics in self._metrics.items():
                if (metrics.idle_time > self.config.idle_timeout and 
                    len(self._connections) > min_connections):
                    idle_connections.append(connection_id)
            
            for connection_id in idle_connections:
                await self._close_connection(connection_id)
                logger.debug(f"Cleaned up idle connection: {connection_id}")
    
    async def _cleanup_metrics(self) -> None:
        """Metrics temizle"""
        # Eski metrics'leri temizle
        cutoff_time = time.time() - 3600  # 1 saat öncesi
        
        for connection_id in list(self._metrics.keys()):
            if connection_id not in self._connections:
                del self._metrics[connection_id]
    
    async def _monitoring_loop(self) -> None:
        """Monitoring loop"""
        while True:
            try:
                await asyncio.sleep(60)  # 1 dakika interval
                
                # Statistics güncelle
                await self._update_statistics()
                
                # Performance metrics hesapla
                await self._calculate_performance_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
    
    async def _update_statistics(self) -> None:
        """Statistics güncelle"""
        self.stats["idle_connections"] = len(self._connections) - len(self._active_connections)
        
        # Average response time hesapla
        if self._metrics:
            total_time = sum(m.total_time for m in self._metrics.values())
            total_usage = sum(m.usage_count for m in self._metrics.values())
            self.stats["avg_response_time"] = total_time / max(total_usage, 1)
    
    async def _calculate_performance_metrics(self) -> None:
        """Performance metrics hesapla"""
        # Connection weights güncelle (load balancing için)
        for connection_id, metrics in self._metrics.items():
            if metrics.usage_count > 0:
                weight = 1.0 / (metrics.avg_response_time + metrics.error_count * 0.1)
                self._connection_weights[connection_id] = weight
    
    async def close(self) -> None:
        """Pool'u kapat"""
        # Background tasks'ları durdur
        if self._health_check_task:
            self._health_check_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        if self._monitoring_task:
            self._monitoring_task.cancel()
        
        # Tüm connections'ları kapat
        for connection_id in list(self._connections.keys()):
            await self._close_connection(connection_id)
        
        # Pool'u kapat
        if self._pool:
            if self.db_type == DatabaseType.POSTGRESQL:
                await self._pool.close()
            elif self.db_type == DatabaseType.MONGODB:
                self._pool.close()
        
        logger.info(f"Connection pool kapatıldı: {self.name}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Pool istatistikleri"""
        healthy_connections = sum(1 for m in self._metrics.values() if m.is_healthy)
        
        return {
            "name": self.name,
            "db_type": self.db_type.value,
            "config": {
                "min_size": self.config.min_size,
                "max_size": self.config.max_size,
                "max_overflow": self.config.max_overflow
            },
            "connections": {
                "total": len(self._connections),
                "active": len(self._active_connections),
                "idle": len(self._connections) - len(self._active_connections),
                "healthy": healthy_connections,
                "unhealthy": len(self._connections) - healthy_connections
            },
            "performance": dict(self.stats),
            "metrics": {
                "avg_connection_age": sum(m.age for m in self._metrics.values()) / max(len(self._metrics), 1),
                "avg_usage_count": sum(m.usage_count for m in self._metrics.values()) / max(len(self._metrics), 1),
                "total_errors": sum(m.error_count for m in self._metrics.values())
            }
        }

class SmartConnectionContext:
    """Smart connection context manager"""
    
    def __init__(self, pool: SmartConnectionPool):
        self.pool = pool
        self.connection_id = None
        self.connection = None
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        self.connection_id, self.connection = await self.pool._acquire_connection_internal()
        return self.connection
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Execution time kaydet
        if self.start_time and self.connection_id:
            execution_time = time.time() - self.start_time
            metrics = self.pool._metrics[self.connection_id]
            metrics.total_time += execution_time
            
            # Query stats güncelle
            self.pool.stats["total_queries"] += 1
        
        # Connection'ı release et
        await self.pool._release_connection_internal(self.connection_id, exc_val)

class DatabasePoolManager:
    """Database pool manager"""
    
    def __init__(self):
        self.pools: Dict[str, SmartConnectionPool] = {}
        self._default_configs = {
            DatabaseType.POSTGRESQL: PoolConfig(min_size=5, max_size=20),
            DatabaseType.SQLITE: PoolConfig(
                min_size=5,
                max_size=20,
                max_overflow=30,
                pool_timeout=60,
                pool_recycle=1800,
                idle_timeout=600,
                retry_attempts=5,
                retry_delay=2.0
            ),
            DatabaseType.MONGODB: PoolConfig(min_size=3, max_size=15),
            DatabaseType.REDIS: PoolConfig(min_size=5, max_size=25)
        }
    
    async def create_pool(self, name: str, db_type: DatabaseType, connection_string: str, 
                         config: Optional[PoolConfig] = None) -> SmartConnectionPool:
        """Pool oluştur"""
        if name in self.pools:
            raise ValueError(f"Pool already exists: {name}")
        
        if config is None:
            config = self._default_configs[db_type]
        
        pool = SmartConnectionPool(name, db_type, config, connection_string)
        await pool.initialize()
        
        self.pools[name] = pool
        logger.info(f"Pool oluşturuldu: {name}")
        
        return pool
    
    async def get_pool(self, name: str) -> SmartConnectionPool:
        """Pool al"""
        if name not in self.pools:
            raise ValueError(f"Pool not found: {name}")
        return self.pools[name]
    
    async def get_connection(self, pool_name: str) -> AsyncContextManager:
        """Connection al"""
        pool = await self.get_pool(pool_name)
        return await pool.acquire_connection()
    
    async def close_pool(self, name: str) -> None:
        """Pool kapat"""
        if name in self.pools:
            await self.pools[name].close()
            del self.pools[name]
            logger.info(f"Pool kapatıldı: {name}")
    
    async def close_all_pools(self) -> None:
        """Tüm pool'ları kapat"""
        for name in list(self.pools.keys()):
            await self.close_pool(name)
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Tüm pool istatistikleri"""
        return {name: pool.get_stats() for name, pool in self.pools.items()}
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Tüm pool'ların health check'i"""
        results = {}
        for name, pool in self.pools.items():
            try:
                # Test connection
                async with await pool.acquire_connection() as conn:
                    if pool.db_type == DatabaseType.POSTGRESQL:
                        await conn.execute("SELECT 1")
                    elif pool.db_type == DatabaseType.SQLITE:
                        await conn.execute("SELECT 1")
                    elif pool.db_type == DatabaseType.MONGODB:
                        await conn.admin.command('ping')
                    elif pool.db_type == DatabaseType.REDIS:
                        await conn.ping()
                results[name] = True
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                results[name] = False
        
        return results

# Global pool manager instance
pool_manager = DatabasePoolManager()

# Convenience functions
async def create_db_pool(name: str, db_type: DatabaseType, connection_string: str, 
                        config: Optional[PoolConfig] = None) -> SmartConnectionPool:
    """Database pool oluştur"""
    return await pool_manager.create_pool(name, db_type, connection_string, config)

async def get_db_connection(pool_name: str) -> AsyncContextManager:
    """Database connection al"""
    return await pool_manager.get_connection(pool_name)

async def get_pool_stats() -> Dict[str, Any]:
    """Pool istatistikleri al"""
    return pool_manager.get_all_stats()

async def health_check_pools() -> Dict[str, bool]:
    """Pool health check"""
    return await pool_manager.health_check_all()

# Decorators
def with_db_connection(pool_name: str):
    """Database connection decorator"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            async with await get_db_connection(pool_name) as conn:
                return await func(conn, *args, **kwargs)
        return wrapper
    return decorator 