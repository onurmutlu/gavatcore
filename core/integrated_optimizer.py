from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
# core/integrated_optimizer.py - Entegre Optimizasyon Sistemi

import asyncio
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
import weakref
import gc
import psutil

# Core imports
from core.performance_optimizer import (
    performance_optimizer, PerformanceOptimizer, 
    start_performance_monitoring, stop_performance_monitoring,
    get_performance_stats, optimize_system
)
from core.smart_cache_manager import (
    CacheManagerFactory, SmartCacheManager, CachePolicy, CacheStrategy,
    get_profile_cache, get_gpt_cache, get_log_cache, get_session_cache,
    get_all_cache_stats
)
from core.db_pool_manager import (
    pool_manager, DatabasePoolManager, DatabaseType, PoolConfig,
    create_db_pool, get_db_connection, get_pool_stats, health_check_pools
)

# Database imports
from core.db.connection import get_db_session
from utilities.redis_client import redis_client
from utilities.log_utils import log_event

# Performance monitoring
import structlog
logger = structlog.get_logger("gavatcore.integrated_optimizer")

@dataclass
class OptimizationConfig:
    """Optimizasyon konfigürasyonu"""
    # Performance monitoring
    enable_performance_monitoring: bool = True
    performance_monitoring_interval: int = 30
    memory_threshold_mb: int = 500
    cpu_threshold_percent: float = 80.0
    
    # Cache optimization
    enable_smart_caching: bool = True
    cache_cleanup_interval: int = 300
    cache_compression_threshold: int = 1024
    cache_auto_refresh: bool = True
    
    # Database optimization
    enable_db_pooling: bool = True
    db_health_check_interval: int = 60
    connection_lifetime_hours: int = 2
    idle_timeout_minutes: int = 5
    
    # System optimization
    auto_gc_interval: int = 600  # 10 dakika
    log_flush_interval: int = 30
    metrics_retention_hours: int = 24
    
    # Advanced features
    enable_predictive_caching: bool = True
    enable_adaptive_pooling: bool = True
    enable_load_balancing: bool = True
    enable_auto_scaling: bool = True

class IntegratedOptimizer:
    """Entegre optimizasyon sistemi"""
    
    def __init__(self, config: OptimizationConfig = None):
        self.config = config or OptimizationConfig()
        
        # Component references
        self.performance_optimizer = performance_optimizer
        self.cache_factory = CacheManagerFactory
        self.pool_manager = pool_manager
        
        # System state
        self._is_running = False
        self._optimization_tasks = []
        self._system_metrics = deque(maxlen=1000)
        self._optimization_history = deque(maxlen=100)
        
        # Advanced features
        self._predictive_cache_model = {}
        self._adaptive_pool_configs = {}
        self._load_balancer_weights = defaultdict(float)
        self._auto_scaling_decisions = deque(maxlen=50)
        
        # Locks
        self._optimization_lock = asyncio.Lock()
        self._metrics_lock = asyncio.Lock()
        
    async def start(self) -> None:
        """Entegre optimizasyon sistemini başlat"""
        if self._is_running:
            logger.warning("Integrated optimizer zaten çalışıyor")
            return
        
        try:
            logger.info("🚀 Entegre optimizasyon sistemi başlatılıyor...")
            
            # Performance monitoring başlat
            if self.config.enable_performance_monitoring:
                await start_performance_monitoring()
            
            # Cache managers başlat
            if self.config.enable_smart_caching:
                await self._initialize_cache_managers()
            
            # Database pools başlat
            if self.config.enable_db_pooling:
                await self._initialize_database_pools()
            
            # Background optimization tasks başlat
            self._optimization_tasks = [
                asyncio.create_task(self._system_monitor_loop()),
                asyncio.create_task(self._optimization_loop()),
                asyncio.create_task(self._predictive_cache_loop()),
                asyncio.create_task(self._adaptive_pool_loop()),
                asyncio.create_task(self._load_balancer_loop()),
                asyncio.create_task(self._auto_scaling_loop()),
                asyncio.create_task(self._metrics_cleanup_loop())
            ]
            
            self._is_running = True
            logger.info("✅ Entegre optimizasyon sistemi başarıyla başlatıldı")
            
        except Exception as e:
            logger.error(f"Integrated optimizer başlatma hatası: {e}")
            await self.stop()
            raise
    
    async def stop(self) -> None:
        """Entegre optimizasyon sistemini durdur"""
        if not self._is_running:
            return
        
        logger.info("🛑 Entegre optimizasyon sistemi durduruluyor...")
        
        self._is_running = False
        
        # Background tasks'ları durdur
        for task in self._optimization_tasks:
            task.cancel()
        
        await asyncio.gather(*self._optimization_tasks, return_exceptions=True)
        
        # Components'ları durdur
        if self.config.enable_performance_monitoring:
            await stop_performance_monitoring()
        
        if self.config.enable_smart_caching:
            await self.cache_factory.shutdown_all()
        
        if self.config.enable_db_pooling:
            await self.pool_manager.close_all_pools()
        
        logger.info("✅ Entegre optimizasyon sistemi durduruldu")
    
    async def _initialize_cache_managers(self) -> None:
        """Cache manager'ları başlat"""
        try:
            # Predefined cache managers'ları başlat
            await get_profile_cache()
            await get_gpt_cache()
            await get_log_cache()
            await get_session_cache()
            
            logger.info("Cache managers başlatıldı")
            
        except Exception as e:
            logger.error(f"Cache manager initialization error: {e}")
            raise
    
    async def _initialize_database_pools(self) -> None:
        """Database pool'ları başlat"""
        try:
            # PostgreSQL pool
            if os.getenv("DATABASE_URL"):
                await create_db_pool(
                    "main_postgresql",
                    DatabaseType.POSTGRESQL,
                    os.getenv("DATABASE_URL"),
                    PoolConfig(
                        min_size=5,
                        max_size=20,
                        connection_lifetime=self.config.connection_lifetime_hours * 3600,
                        idle_timeout=self.config.idle_timeout_minutes * 60
                    )
                )
            
            # SQLite pool
            await create_db_pool(
                "main_sqlite",
                DatabaseType.SQLITE,
                "gavatcore.db",
                PoolConfig(min_size=1, max_size=5)
            )
            
            # Redis pool
            if redis_client:
                await create_db_pool(
                    "main_redis",
                    DatabaseType.REDIS,
                    os.getenv("REDIS_URL", "redis://localhost:6379"),
                    PoolConfig(min_size=5, max_size=25)
                )
            
            # MongoDB pool
            if os.getenv("MONGODB_URL"):
                await create_db_pool(
                    "main_mongodb",
                    DatabaseType.MONGODB,
                    os.getenv("MONGODB_URL"),
                    PoolConfig(min_size=3, max_size=15)
                )
            
            logger.info("Database pools başlatıldı")
            
        except Exception as e:
            logger.error(f"Database pool initialization error: {e}")
            raise
    
    async def _system_monitor_loop(self) -> None:
        """Sistem monitoring loop"""
        while self._is_running:
            try:
                await asyncio.sleep(self.config.performance_monitoring_interval)
                
                # System metrics topla
                process = psutil.Process()
                memory_info = process.memory_info()
                cpu_percent = process.cpu_percent()
                
                metric = {
                    "timestamp": time.time(),
                    "memory_rss_mb": memory_info.rss / 1024 / 1024,
                    "memory_vms_mb": memory_info.vms / 1024 / 1024,
                    "cpu_percent": cpu_percent,
                    "threads": process.num_threads(),
                    "open_files": len(process.open_files()),
                    "connections": len(process.connections())
                }
                
                async with self._metrics_lock:
                    self._system_metrics.append(metric)
                
                # Threshold kontrolü
                if memory_info.rss / 1024 / 1024 > self.config.memory_threshold_mb:
                    await self._handle_memory_pressure()
                
                if cpu_percent > self.config.cpu_threshold_percent:
                    await self._handle_cpu_pressure()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"System monitor loop error: {e}")
                await asyncio.sleep(60)
    
    async def _optimization_loop(self) -> None:
        """Ana optimizasyon loop"""
        while self._is_running:
            try:
                await asyncio.sleep(600)  # 10 dakika interval
                
                async with self._optimization_lock:
                    optimization_result = await self._run_comprehensive_optimization()
                    
                    self._optimization_history.append({
                        "timestamp": time.time(),
                        "result": optimization_result,
                        "system_state": await self._get_system_state()
                    })
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Optimization loop error: {e}")
                await asyncio.sleep(300)
    
    async def _predictive_cache_loop(self) -> None:
        """Predictive caching loop"""
        if not self.config.enable_predictive_caching:
            return
        
        while self._is_running:
            try:
                await asyncio.sleep(300)  # 5 dakika interval
                
                # Access pattern'leri analiz et
                await self._analyze_access_patterns()
                
                # Predictive caching uygula
                await self._apply_predictive_caching()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Predictive cache loop error: {e}")
                await asyncio.sleep(600)
    
    async def _adaptive_pool_loop(self) -> None:
        """Adaptive pooling loop"""
        if not self.config.enable_adaptive_pooling:
            return
        
        while self._is_running:
            try:
                await asyncio.sleep(180)  # 3 dakika interval
                
                # Pool performance'ını analiz et
                pool_stats = await get_pool_stats()
                
                # Adaptive pool sizing uygula
                await self._apply_adaptive_pooling(pool_stats)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Adaptive pool loop error: {e}")
                await asyncio.sleep(300)
    
    async def _load_balancer_loop(self) -> None:
        """Load balancer loop"""
        if not self.config.enable_load_balancing:
            return
        
        while self._is_running:
            try:
                await asyncio.sleep(120)  # 2 dakika interval
                
                # Load balancing weights güncelle
                await self._update_load_balancer_weights()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Load balancer loop error: {e}")
                await asyncio.sleep(240)
    
    async def _auto_scaling_loop(self) -> None:
        """Auto scaling loop"""
        if not self.config.enable_auto_scaling:
            return
        
        while self._is_running:
            try:
                await asyncio.sleep(240)  # 4 dakika interval
                
                # Auto scaling kararları al
                await self._make_auto_scaling_decisions()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto scaling loop error: {e}")
                await asyncio.sleep(480)
    
    async def _metrics_cleanup_loop(self) -> None:
        """Metrics cleanup loop"""
        while self._is_running:
            try:
                await asyncio.sleep(3600)  # 1 saat interval
                
                # Eski metrics'leri temizle
                await self._cleanup_old_metrics()
                
                # Garbage collection
                if self.config.auto_gc_interval:
                    gc.collect()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics cleanup loop error: {e}")
                await asyncio.sleep(1800)
    
    async def _handle_memory_pressure(self) -> None:
        """Memory pressure handling"""
        logger.warning("🔥 Memory pressure detected - optimizing...")
        
        try:
            # Cache'leri temizle
            for name, manager in self.cache_factory._instances.items():
                await manager._cache_maintenance()
            
            # Garbage collection
            gc.collect()
            
            # Pool'ları optimize et
            for pool in self.pool_manager.pools.values():
                await pool._cleanup_idle_connections()
            
            logger.info("Memory pressure optimization completed")
            
        except Exception as e:
            logger.error(f"Memory pressure handling error: {e}")
    
    async def _handle_cpu_pressure(self) -> None:
        """CPU pressure handling"""
        logger.warning("⚡ CPU pressure detected - optimizing...")
        
        try:
            # Rate limiting uygula
            # Background task'ları yavaşlat
            await asyncio.sleep(5)
            
            logger.info("CPU pressure optimization completed")
            
        except Exception as e:
            logger.error(f"CPU pressure handling error: {e}")
    
    async def _run_comprehensive_optimization(self) -> Dict[str, Any]:
        """Kapsamlı optimizasyon çalıştır"""
        start_time = time.time()
        optimizations = []
        
        try:
            # Performance optimization
            perf_result = await optimize_system()
            optimizations.append(("performance", perf_result))
            
            # Cache optimization
            cache_result = await self._optimize_caches()
            optimizations.append(("cache", cache_result))
            
            # Database optimization
            db_result = await self._optimize_databases()
            optimizations.append(("database", db_result))
            
            # System optimization
            system_result = await self._optimize_system_resources()
            optimizations.append(("system", system_result))
            
            duration = time.time() - start_time
            
            result = {
                "success": True,
                "duration": duration,
                "optimizations": optimizations,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Comprehensive optimization completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time,
                "optimizations": optimizations
            }
    
    async def _optimize_caches(self) -> Dict[str, Any]:
        """Cache optimizasyonu"""
        try:
            results = {}
            
            for name, manager in self.cache_factory._instances.items():
                # Cache cleanup
                await manager._cache_maintenance()
                
                # Stats topla
                stats = manager.get_stats()
                results[name] = {
                    "hit_ratio": stats["performance"]["hit_ratio"],
                    "size": stats["levels"]["l1_size"],
                    "memory_mb": stats["levels"]["l1_memory_mb"]
                }
            
            return {"success": True, "cache_stats": results}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _optimize_databases(self) -> Dict[str, Any]:
        """Database optimizasyonu"""
        try:
            results = {}
            
            # Health check
            health_results = await health_check_pools()
            
            # Pool stats
            pool_stats = await get_pool_stats()
            
            for name, pool in self.pool_manager.pools.items():
                # Idle connections temizle
                await pool._cleanup_idle_connections()
                
                results[name] = {
                    "healthy": health_results.get(name, False),
                    "connections": pool_stats[name]["connections"],
                    "performance": pool_stats[name]["performance"]
                }
            
            return {"success": True, "pool_stats": results}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _optimize_system_resources(self) -> Dict[str, Any]:
        """Sistem kaynak optimizasyonu"""
        try:
            # Garbage collection
            collected = gc.collect()
            
            # Memory info
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "success": True,
                "gc_collected": collected,
                "memory_mb": memory_info.rss / 1024 / 1024,
                "threads": process.num_threads()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _analyze_access_patterns(self) -> None:
        """Access pattern analizi"""
        try:
            # Cache access patterns'ları analiz et
            for name, manager in self.cache_factory._instances.items():
                if hasattr(manager, 'access_patterns'):
                    patterns = manager.access_patterns
                    
                    # Pattern prediction model güncelle
                    for key, accesses in patterns.items():
                        if len(accesses) >= 5:
                            intervals = []
                            for i in range(1, len(accesses)):
                                intervals.append(accesses[i] - accesses[i-1])
                            
                            avg_interval = sum(intervals) / len(intervals)
                            self._predictive_cache_model[f"{name}:{key}"] = {
                                "avg_interval": avg_interval,
                                "next_predicted": time.time() + avg_interval,
                                "confidence": min(len(accesses) / 10, 1.0)
                            }
            
        except Exception as e:
            logger.error(f"Access pattern analysis error: {e}")
    
    async def _apply_predictive_caching(self) -> None:
        """Predictive caching uygula"""
        try:
            current_time = time.time()
            
            for cache_key, prediction in self._predictive_cache_model.items():
                if (prediction["next_predicted"] <= current_time and 
                    prediction["confidence"] > 0.7):
                    
                    # Cache'i preload et
                    cache_name, key = cache_key.split(":", 1)
                    
                    if cache_name in self.cache_factory._instances:
                        manager = self.cache_factory._instances[cache_name]
                        
                        # Auto refresh trigger
                        if hasattr(manager, '_auto_refresh'):
                            await manager._auto_refresh(key)
            
        except Exception as e:
            logger.error(f"Predictive caching error: {e}")
    
    async def _apply_adaptive_pooling(self, pool_stats: Dict[str, Any]) -> None:
        """Adaptive pooling uygula"""
        try:
            for name, stats in pool_stats.items():
                pool = self.pool_manager.pools.get(name)
                if not pool:
                    continue
                
                connections = stats["connections"]
                performance = stats["performance"]
                
                # Pool size optimization
                utilization = connections["active"] / max(connections["total"], 1)
                
                if utilization > 0.8:  # High utilization
                    # Pool size artır
                    new_max_size = min(pool.config.max_size + 5, 50)
                    pool.config.max_size = new_max_size
                    logger.info(f"Pool {name} max_size increased to {new_max_size}")
                
                elif utilization < 0.3:  # Low utilization
                    # Pool size azalt
                    new_max_size = max(pool.config.max_size - 2, pool.config.min_size + 2)
                    pool.config.max_size = new_max_size
                    logger.info(f"Pool {name} max_size decreased to {new_max_size}")
            
        except Exception as e:
            logger.error(f"Adaptive pooling error: {e}")
    
    async def _update_load_balancer_weights(self) -> None:
        """Load balancer weights güncelle"""
        try:
            # Pool performance'a göre weight'leri güncelle
            pool_stats = await get_pool_stats()
            
            for name, stats in pool_stats.items():
                performance = stats["performance"]
                
                # Weight hesapla (düşük response time = yüksek weight)
                avg_response_time = performance.get("avg_response_time", 1.0)
                weight = 1.0 / max(avg_response_time, 0.001)
                
                self._load_balancer_weights[name] = weight
            
        except Exception as e:
            logger.error(f"Load balancer update error: {e}")
    
    async def _make_auto_scaling_decisions(self) -> None:
        """Auto scaling kararları al"""
        try:
            # System metrics'e göre scaling kararları
            recent_metrics = list(self._system_metrics)[-10:]  # Son 10 metric
            
            if recent_metrics:
                avg_cpu = sum(m["cpu_percent"] for m in recent_metrics) / len(recent_metrics)
                avg_memory = sum(m["memory_rss_mb"] for m in recent_metrics) / len(recent_metrics)
                
                decision = {
                    "timestamp": time.time(),
                    "avg_cpu": avg_cpu,
                    "avg_memory": avg_memory,
                    "action": "none"
                }
                
                if avg_cpu > 70 or avg_memory > 400:
                    decision["action"] = "scale_up"
                    # Scale up logic
                    await self._scale_up_resources()
                
                elif avg_cpu < 30 and avg_memory < 200:
                    decision["action"] = "scale_down"
                    # Scale down logic
                    await self._scale_down_resources()
                
                self._auto_scaling_decisions.append(decision)
            
        except Exception as e:
            logger.error(f"Auto scaling decision error: {e}")
    
    async def _scale_up_resources(self) -> None:
        """Resource'ları scale up et"""
        try:
            # Cache sizes artır
            for manager in self.cache_factory._instances.values():
                if manager.policy.max_size < 2000:
                    manager.policy.max_size = int(manager.policy.max_size * 1.2)
            
            # Pool sizes artır
            for pool in self.pool_manager.pools.values():
                if pool.config.max_size < 30:
                    pool.config.max_size = min(pool.config.max_size + 3, 30)
            
            logger.info("Resources scaled up")
            
        except Exception as e:
            logger.error(f"Scale up error: {e}")
    
    async def _scale_down_resources(self) -> None:
        """Resource'ları scale down et"""
        try:
            # Cache sizes azalt
            for manager in self.cache_factory._instances.values():
                if manager.policy.max_size > 500:
                    manager.policy.max_size = int(manager.policy.max_size * 0.9)
            
            # Pool sizes azalt
            for pool in self.pool_manager.pools.values():
                if pool.config.max_size > pool.config.min_size + 5:
                    pool.config.max_size = max(pool.config.max_size - 2, pool.config.min_size + 2)
            
            logger.info("Resources scaled down")
            
        except Exception as e:
            logger.error(f"Scale down error: {e}")
    
    async def _cleanup_old_metrics(self) -> None:
        """Eski metrics'leri temizle"""
        try:
            cutoff_time = time.time() - (self.config.metrics_retention_hours * 3600)
            
            # System metrics temizle
            async with self._metrics_lock:
                self._system_metrics = deque(
                    [m for m in self._system_metrics if m["timestamp"] > cutoff_time],
                    maxlen=1000
                )
            
            # Optimization history temizle
            self._optimization_history = deque(
                [h for h in self._optimization_history if h["timestamp"] > cutoff_time],
                maxlen=100
            )
            
        except Exception as e:
            logger.error(f"Metrics cleanup error: {e}")
    
    async def _get_system_state(self) -> Dict[str, Any]:
        """Sistem durumunu al"""
        try:
            return {
                "performance": await get_performance_stats(),
                "cache": await get_all_cache_stats(),
                "database": await get_pool_stats(),
                "system": {
                    "running": self._is_running,
                    "optimization_tasks": len(self._optimization_tasks),
                    "metrics_count": len(self._system_metrics)
                }
            }
        except Exception as e:
            logger.error(f"System state error: {e}")
            return {"error": str(e)}
    
    async def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Kapsamlı sistem istatistikleri"""
        try:
            recent_metrics = list(self._system_metrics)[-10:]
            recent_optimizations = list(self._optimization_history)[-5:]
            
            if recent_metrics:
                avg_memory = sum(m["memory_rss_mb"] for m in recent_metrics) / len(recent_metrics)
                avg_cpu = sum(m["cpu_percent"] for m in recent_metrics) / len(recent_metrics)
            else:
                avg_memory = avg_cpu = 0
            
            return {
                "integrated_optimizer": {
                    "running": self._is_running,
                    "config": asdict(self.config),
                    "avg_memory_mb": avg_memory,
                    "avg_cpu_percent": avg_cpu,
                    "optimization_count": len(self._optimization_history),
                    "predictive_models": len(self._predictive_cache_model),
                    "load_balancer_weights": dict(self._load_balancer_weights)
                },
                "system_state": await self._get_system_state(),
                "recent_optimizations": recent_optimizations[-3:],
                "auto_scaling_decisions": list(self._auto_scaling_decisions)[-5:]
            }
            
        except Exception as e:
            logger.error(f"Comprehensive stats error: {e}")
            return {"error": str(e)}
    
    async def force_optimization(self) -> Dict[str, Any]:
        """Manuel optimizasyon çalıştır"""
        logger.info("🔧 Manuel optimizasyon başlatılıyor...")
        
        async with self._optimization_lock:
            result = await self._run_comprehensive_optimization()
            
            self._optimization_history.append({
                "timestamp": time.time(),
                "result": result,
                "system_state": await self._get_system_state(),
                "manual": True
            })
            
            return result

# Global integrated optimizer instance
integrated_optimizer = IntegratedOptimizer()

# Convenience functions
async def start_integrated_optimization(config: OptimizationConfig = None):
    """Entegre optimizasyonu başlat"""
    if config:
        integrated_optimizer.config = config
    await integrated_optimizer.start()

async def stop_integrated_optimization():
    """Entegre optimizasyonu durdur"""
    await integrated_optimizer.stop()

async def get_integrated_stats():
    """Entegre istatistikleri al"""
    return await integrated_optimizer.get_comprehensive_stats()

async def force_system_optimization():
    """Manuel sistem optimizasyonu"""
    return await integrated_optimizer.force_optimization()

# Configuration presets
BAMGUM_CONFIG = OptimizationConfig(
    enable_performance_monitoring=True,
    performance_monitoring_interval=15,  # Daha sık monitoring
    memory_threshold_mb=300,  # Düşük threshold
    cpu_threshold_percent=60.0,  # Düşük threshold
    enable_smart_caching=True,
    cache_cleanup_interval=120,  # Daha sık cleanup
    enable_predictive_caching=True,
    enable_adaptive_pooling=True,
    enable_auto_scaling=True,
    auto_gc_interval=300  # Daha sık GC
)

PRODUCTION_CONFIG = OptimizationConfig(
    enable_performance_monitoring=True,
    performance_monitoring_interval=60,
    memory_threshold_mb=800,
    cpu_threshold_percent=85.0,
    enable_smart_caching=True,
    cache_cleanup_interval=600,
    enable_predictive_caching=True,
    enable_adaptive_pooling=True,
    enable_auto_scaling=False,  # Production'da manuel control
    auto_gc_interval=1200
)

DEVELOPMENT_CONFIG = OptimizationConfig(
    enable_performance_monitoring=True,
    performance_monitoring_interval=30,
    memory_threshold_mb=200,
    cpu_threshold_percent=70.0,
    enable_smart_caching=False,  # Development'da basit cache
    enable_predictive_caching=False,
    enable_adaptive_pooling=False,
    enable_auto_scaling=False,
    auto_gc_interval=600
) 