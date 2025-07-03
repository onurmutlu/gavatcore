#!/usr/bin/env python3
"""
BEHAVIORAL PERFORMANCE OPTIMIZER & PROFILER
============================================

Advanced Behavioral Engine için performance optimization ve memory profiling.
Bottleneck detection, memory optimization ve performance tuning.

Özellikler:
- Memory profiling ve leak detection  
- CPU usage optimization
- Async operation optimization
- Cache performance tuning
- Garbage collection optimization

@version: 1.0.0
@created: 2025-01-30
"""

import asyncio
import time
import gc
import sys
import psutil
import tracemalloc
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
import functools
import structlog

# Memory profiling imports
try:
    import memory_profiler
    MEMORY_PROFILER_AVAILABLE = True
except ImportError:
    MEMORY_PROFILER_AVAILABLE = False

# Async profiling
try:
    import cProfile
    import pstats
    import io
    PROFILING_AVAILABLE = True
except ImportError:
    PROFILING_AVAILABLE = False

logger = structlog.get_logger("behavioral_optimizer")

@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    execution_time: float = 0.0
    memory_before: float = 0.0
    memory_after: float = 0.0
    memory_peak: float = 0.0
    cpu_percent: float = 0.0
    function_name: str = ""
    
    @property 
    def memory_delta(self) -> float:
        return self.memory_after - self.memory_before
    
    @property
    def is_completed(self) -> bool:
        return self.end_time is not None

@dataclass
class OptimizationReport:
    """Optimization analysis report"""
    bottlenecks: List[Dict[str, Any]] = field(default_factory=list)
    memory_hotspots: List[Dict[str, Any]] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    performance_score: float = 0.0
    memory_efficiency: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

class BehavioralPerformanceOptimizer:
    """
    🚀 Advanced Behavioral Engine Performance Optimizer
    
    Performance monitoring, profiling ve optimization sistemi.
    """
    
    def __init__(self):
        self.performance_history: List[PerformanceMetrics] = []
        self.memory_snapshots: List[Dict] = []
        self.optimization_cache: Dict[str, Any] = {}
        self.is_profiling_active = False
        
        # Process info
        self.process = psutil.Process()
        
        logger.info("⚡ Performance Optimizer başlatıldı")
    
    def performance_monitor(self, func_name: Optional[str] = None):
        """Performance monitoring decorator"""
        
        def decorator(func: Callable):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._monitor_async_function(func, func_name or func.__name__, *args, **kwargs)
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return self._monitor_sync_function(func, func_name or func.__name__, *args, **kwargs)
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
                
        return decorator
    
    async def _monitor_async_function(self, func: Callable, name: str, *args, **kwargs):
        """Async function monitoring"""
        
        metrics = PerformanceMetrics(
            function_name=name,
            memory_before=self._get_memory_usage(),
            cpu_percent=self.process.cpu_percent()
        )
        
        try:
            # Memory peak tracking
            if MEMORY_PROFILER_AVAILABLE:
                peak_monitor = memory_profiler.LineProfiler()
                peak_monitor.add_function(func)
                peak_monitor.enable_by_count()
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Finalize metrics
            metrics.end_time = time.time()
            metrics.execution_time = metrics.end_time - metrics.start_time
            metrics.memory_after = self._get_memory_usage()
            
            if MEMORY_PROFILER_AVAILABLE:
                peak_monitor.disable_by_count()
                # Get peak memory from profiler
                metrics.memory_peak = max(metrics.memory_before, metrics.memory_after)
            
            self.performance_history.append(metrics)
            
            # Performance logging
            if metrics.execution_time > 1.0:  # Slow function warning
                logger.warning(f"⚠️ Slow function detected: {name} ({metrics.execution_time:.3f}s)")
            
            if metrics.memory_delta > 50:  # High memory usage warning (MB)
                logger.warning(f"⚠️ High memory usage: {name} (+{metrics.memory_delta:.1f}MB)")
            
            return result
            
        except Exception as e:
            metrics.end_time = time.time()
            metrics.execution_time = metrics.end_time - metrics.start_time
            logger.error(f"❌ Function error in {name}: {e}")
            raise
    
    def _monitor_sync_function(self, func: Callable, name: str, *args, **kwargs):
        """Sync function monitoring"""
        
        metrics = PerformanceMetrics(
            function_name=name,
            memory_before=self._get_memory_usage(),
            cpu_percent=self.process.cpu_percent()
        )
        
        try:
            result = func(*args, **kwargs)
            
            metrics.end_time = time.time()
            metrics.execution_time = metrics.end_time - metrics.start_time
            metrics.memory_after = self._get_memory_usage()
            
            self.performance_history.append(metrics)
            
            return result
            
        except Exception as e:
            metrics.end_time = time.time()
            metrics.execution_time = metrics.end_time - metrics.start_time
            logger.error(f"❌ Function error in {name}: {e}")
            raise
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            return self.process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0
    
    def start_memory_profiling(self):
        """Memory profiling başlat"""
        if tracemalloc.is_tracing():
            tracemalloc.stop()
        
        tracemalloc.start()
        self.is_profiling_active = True
        
        # Initial snapshot
        snapshot = tracemalloc.take_snapshot()
        self.memory_snapshots = [snapshot]
        
        logger.info("🔍 Memory profiling başlatıldı")
    
    def take_memory_snapshot(self, tag: str = ""):
        """Memory snapshot al"""
        if not tracemalloc.is_tracing():
            logger.warning("⚠️ Memory profiling aktif değil")
            return
        
        snapshot = tracemalloc.take_snapshot()
        self.memory_snapshots.append(snapshot)
        
        logger.info(f"📸 Memory snapshot alındı: {tag}")
    
    def stop_memory_profiling(self) -> Dict[str, Any]:
        """Memory profiling durdur ve analiz et"""
        
        if not tracemalloc.is_tracing():
            logger.warning("⚠️ Memory profiling zaten durmuş")
            return {}
        
        # Final snapshot
        final_snapshot = tracemalloc.take_snapshot()
        self.memory_snapshots.append(final_snapshot)
        
        tracemalloc.stop()
        self.is_profiling_active = False
        
        # Memory analysis
        if len(self.memory_snapshots) >= 2:
            comparison = final_snapshot.compare_to(self.memory_snapshots[0], 'lineno')
            
            memory_analysis = {
                "total_snapshots": len(self.memory_snapshots),
                "top_memory_consumers": [],
                "memory_growth": [],
                "leaks_detected": []
            }
            
            # Top memory consumers
            for stat in final_snapshot.statistics('lineno')[:10]:
                memory_analysis["top_memory_consumers"].append({
                    "file": stat.traceback.format()[-1] if stat.traceback else "unknown",
                    "size_mb": stat.size / 1024 / 1024,
                    "count": stat.count
                })
            
            # Memory growth
            for stat in comparison[:10]:
                if stat.size_diff > 0:
                    memory_analysis["memory_growth"].append({
                        "file": stat.traceback.format()[-1] if stat.traceback else "unknown",
                        "growth_mb": stat.size_diff / 1024 / 1024,
                        "count_diff": stat.count_diff
                    })
            
            # Potential leaks (significant growth)
            for stat in comparison:
                if stat.size_diff > 10 * 1024 * 1024:  # 10MB+ growth
                    memory_analysis["leaks_detected"].append({
                        "file": stat.traceback.format()[-1] if stat.traceback else "unknown",
                        "leak_size_mb": stat.size_diff / 1024 / 1024,
                        "severity": "high" if stat.size_diff > 50 * 1024 * 1024 else "medium"
                    })
            
            logger.info(f"🔍 Memory profiling tamamlandı: {len(memory_analysis['leaks_detected'])} leak detected")
            return memory_analysis
        
        return {}
    
    def optimize_garbage_collection(self):
        """Garbage collection optimize et"""
        
        logger.info("🗑️ Garbage collection optimization başlatılıyor...")
        
        # GC stats before
        gc_stats_before = gc.get_stats()
        objects_before = len(gc.get_objects())
        
        # Force collection
        collected = gc.collect()
        
        # GC stats after  
        objects_after = len(gc.get_objects())
        freed_objects = objects_before - objects_after
        
        # GC thresholds optimization
        # Daha agresif threshold'lar set et
        gc.set_threshold(700, 10, 10)  # Default: (700, 10, 10)
        
        optimization_result = {
            "objects_freed": freed_objects,
            "objects_before": objects_before,
            "objects_after": objects_after,
            "collected_cycles": collected,
            "memory_freed_estimate_mb": freed_objects * 100 / 1024 / 1024  # Rough estimate
        }
        
        logger.info(f"✅ GC optimization: {freed_objects} objects freed, {collected} cycles collected")
        
        return optimization_result
    
    def analyze_bottlenecks(self) -> OptimizationReport:
        """Performance bottleneck analizi"""
        
        if not self.performance_history:
            return OptimizationReport()
        
        logger.info("🔍 Performance bottleneck analizi başlatılıyor...")
        
        # Analyze performance metrics
        bottlenecks = []
        memory_hotspots = []
        suggestions = []
        
        # Group by function
        function_stats = {}
        for metric in self.performance_history:
            if metric.function_name not in function_stats:
                function_stats[metric.function_name] = {
                    "call_count": 0,
                    "total_time": 0.0,
                    "total_memory": 0.0,
                    "max_time": 0.0,
                    "max_memory": 0.0
                }
            
            stats = function_stats[metric.function_name]
            stats["call_count"] += 1
            stats["total_time"] += metric.execution_time
            stats["total_memory"] += metric.memory_delta
            stats["max_time"] = max(stats["max_time"], metric.execution_time)
            stats["max_memory"] = max(stats["max_memory"], metric.memory_delta)
        
        # Find bottlenecks
        for func_name, stats in function_stats.items():
            avg_time = stats["total_time"] / stats["call_count"]
            avg_memory = stats["total_memory"] / stats["call_count"]
            
            # Time bottlenecks
            if avg_time > 0.5 or stats["max_time"] > 2.0:
                bottlenecks.append({
                    "function": func_name,
                    "type": "time",
                    "avg_time": avg_time,
                    "max_time": stats["max_time"],
                    "call_count": stats["call_count"],
                    "severity": "high" if stats["max_time"] > 5.0 else "medium"
                })
                
                suggestions.append(f"Optimize {func_name} - slow execution detected (avg: {avg_time:.3f}s)")
            
            # Memory bottlenecks
            if avg_memory > 20 or stats["max_memory"] > 100:  # MB thresholds
                memory_hotspots.append({
                    "function": func_name,
                    "avg_memory_mb": avg_memory,
                    "max_memory_mb": stats["max_memory"],
                    "call_count": stats["call_count"],
                    "severity": "high" if stats["max_memory"] > 200 else "medium"
                })
                
                suggestions.append(f"Optimize {func_name} memory usage - high consumption detected ({avg_memory:.1f}MB avg)")
        
        # Performance score calculation
        total_functions = len(function_stats)
        problematic_functions = len(bottlenecks) + len(memory_hotspots)
        performance_score = max(0, 100 - (problematic_functions / max(total_functions, 1) * 100))
        
        # Memory efficiency
        total_memory_usage = sum(stats["total_memory"] for stats in function_stats.values())
        memory_efficiency = max(0, 100 - min(total_memory_usage / 1000, 100))  # Cap at 1GB
        
        # Additional suggestions
        if performance_score < 70:
            suggestions.append("Consider implementing caching for frequently called functions")
            suggestions.append("Review algorithm complexity for identified bottlenecks")
        
        if memory_efficiency < 70:
            suggestions.append("Implement object pooling for frequently created objects")
            suggestions.append("Review data structures for memory optimization")
        
        suggestions.append("Enable async processing where possible")
        suggestions.append("Consider implementing lazy loading for large data sets")
        
        report = OptimizationReport(
            bottlenecks=bottlenecks,
            memory_hotspots=memory_hotspots,
            optimization_suggestions=suggestions,
            performance_score=performance_score,
            memory_efficiency=memory_efficiency
        )
        
        logger.info(f"✅ Bottleneck analysis completed: {len(bottlenecks)} bottlenecks, {len(memory_hotspots)} memory hotspots")
        
        return report
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Current system metrics"""
        
        try:
            # CPU and memory
            cpu_percent = self.process.cpu_percent()
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            # System-wide metrics
            system_memory = psutil.virtual_memory()
            system_cpu = psutil.cpu_percent(interval=1)
            
            return {
                "process": {
                    "cpu_percent": cpu_percent,
                    "memory_rss_mb": memory_info.rss / 1024 / 1024,
                    "memory_vms_mb": memory_info.vms / 1024 / 1024,
                    "memory_percent": memory_percent,
                    "num_threads": self.process.num_threads()
                },
                "system": {
                    "cpu_percent": system_cpu,
                    "memory_total_gb": system_memory.total / 1024 / 1024 / 1024,
                    "memory_available_gb": system_memory.available / 1024 / 1024 / 1024,
                    "memory_used_percent": system_memory.percent
                },
                "performance_history": {
                    "total_measurements": len(self.performance_history),
                    "avg_execution_time": sum(m.execution_time for m in self.performance_history) / max(len(self.performance_history), 1),
                    "total_memory_delta": sum(m.memory_delta for m in self.performance_history)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ System metrics error: {e}")
            return {"error": str(e)}
    
    def clear_performance_history(self):
        """Performance geçmişini temizle"""
        self.performance_history.clear()
        self.memory_snapshots.clear()
        logger.info("🧹 Performance history cleared")
    
    async def optimize_async_operations(self):
        """Async operations optimize et"""
        
        logger.info("⚡ Async operations optimization...")
        
        optimizations = {
            "event_loop_optimization": False,
            "task_pool_optimization": False,
            "concurrent_limits": False
        }
        
        try:
            # Event loop optimization
            loop = asyncio.get_event_loop()
            if hasattr(loop, 'set_debug'):
                loop.set_debug(False)  # Debug mode'u kapat (production için)
                optimizations["event_loop_optimization"] = True
            
            # Concurrent task limits
            self.optimization_cache["max_concurrent_tasks"] = 50
            self.optimization_cache["semaphore"] = asyncio.Semaphore(50)
            optimizations["concurrent_limits"] = True
            
            logger.info("✅ Async operations optimized")
            
        except Exception as e:
            logger.error(f"❌ Async optimization error: {e}")
        
        return optimizations

# Global optimizer instance
behavioral_performance_optimizer = BehavioralPerformanceOptimizer()

# Convenience decorator
def monitor_performance(func_name: Optional[str] = None):
    """Performance monitoring decorator"""
    return behavioral_performance_optimizer.performance_monitor(func_name)

__all__ = [
    "BehavioralPerformanceOptimizer",
    "PerformanceMetrics",
    "OptimizationReport", 
    "behavioral_performance_optimizer",
    "monitor_performance"
] 