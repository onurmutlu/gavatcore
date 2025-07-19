from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
📊 Cache Performance Monitor
===========================

Redis cache kullanımını JSON log olarak kaydeden ve günlük hit/miss
oranlarını analiz eden sistem monitoring.

✨ Özellikler:
- Real-time cache metrics tracking
- JSON structured logging
- Performance trend analysis
- Cache efficiency optimization suggestions
- Alert system for poor performance
- Dashboard-ready metrics export

@version: 1.0.0
@created: 2025-01-30
"""

import asyncio
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import threading
from pathlib import Path

import structlog

# Configure structured logging
logger = structlog.get_logger("cache_monitor")

@dataclass
class CacheMetric:
    """Cache metric data point."""
    timestamp: datetime
    operation: str  # hit, miss, set, delete, expire
    cache_key: str
    response_time_ms: float
    cache_size_kb: Optional[float] = None
    ttl_seconds: Optional[int] = None
    user_id: Optional[str] = None
    endpoint: Optional[str] = None

@dataclass
class CachePerformanceReport:
    """Cache performance raporu."""
    time_period: str
    total_operations: int
    cache_hits: int
    cache_misses: int
    hit_rate_percentage: float
    avg_response_time_ms: float
    peak_response_time_ms: float
    operations_per_second: float
    cache_size_trends: List[Tuple[datetime, float]]
    top_accessed_keys: List[Tuple[str, int]]
    performance_grade: str  # A, B, C, D, F
    recommendations: List[str]

@dataclass
class CacheAlert:
    """Cache alert."""
    timestamp: datetime
    severity: str  # info, warning, critical
    message: str
    metric_type: str
    current_value: float
    threshold_value: float
    action_required: str

class CachePerformanceMonitor:
    """
    📊 Cache performance monitoring sistemi.
    
    Real-time cache metrics tracking ve analiz.
    """
    
    def __init__(self, log_file: str = "logs/cache_performance.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Metrics storage
        self.metrics: deque = deque(maxlen=10000)  # Son 10k metric
        self.hourly_stats: Dict[str, Dict] = defaultdict(dict)
        self.daily_stats: Dict[str, Dict] = defaultdict(dict)
        
        # Performance thresholds
        self.thresholds = {
            'hit_rate_warning': 70.0,    # %70'in altında warning
            'hit_rate_critical': 50.0,   # %50'nin altında critical
            'response_time_warning': 100.0,  # 100ms'nin üstünde warning
            'response_time_critical': 500.0,  # 500ms'nin üstünde critical
            'ops_per_sec_min': 10.0     # Saniyede minimum 10 operation
        }
        
        # Alert system
        self.alerts: deque = deque(maxlen=1000)
        self.last_alert_time: Dict[str, datetime] = {}
        self.alert_cooldown_minutes = 5
        
        # Background monitoring
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        logger.info("📊 Cache Performance Monitor initialized",
                   log_file=str(self.log_file))
    
    def record_cache_operation(self,
                             operation: str,
                             cache_key: str,
                             response_time_ms: float,
                             cache_size_kb: Optional[float] = None,
                             ttl_seconds: Optional[int] = None,
                             user_id: Optional[str] = None,
                             endpoint: Optional[str] = None) -> None:
        """
        Cache operation'ı kaydet.
        
        Args:
            operation: hit, miss, set, delete, expire
            cache_key: Cache anahtarı
            response_time_ms: Response time in milliseconds
            cache_size_kb: Cache boyutu (KB)
            ttl_seconds: TTL değeri
            user_id: Kullanıcı ID (optional)
            endpoint: API endpoint (optional)
        """
        try:
            metric = CacheMetric(
                timestamp=datetime.now(),
                operation=operation,
                cache_key=cache_key,
                response_time_ms=response_time_ms,
                cache_size_kb=cache_size_kb,
                ttl_seconds=ttl_seconds,
                user_id=user_id,
                endpoint=endpoint
            )
            
            # Memory storage
            self.metrics.append(metric)
            
            # JSON log'a yaz
            self._write_metric_to_log(metric)
            
            # Real-time analysis
            self._update_real_time_stats(metric)
            
            # Alert checking
            self._check_performance_alerts(metric)
            
            logger.debug("📝 Cache metric recorded",
                        operation=operation,
                        key=cache_key,
                        response_time=response_time_ms)
            
        except Exception as e:
            logger.error("❌ Failed to record cache metric",
                        error=str(e),
                        operation=operation,
                        cache_key=cache_key)
    
    def _write_metric_to_log(self, metric: CacheMetric) -> None:
        """Metric'i JSON log dosyasına yaz."""
        try:
            log_entry = {
                'timestamp': metric.timestamp.isoformat(),
                'operation': metric.operation,
                'cache_key': metric.cache_key,
                'response_time_ms': metric.response_time_ms,
                'cache_size_kb': metric.cache_size_kb,
                'ttl_seconds': metric.ttl_seconds,
                'user_id': metric.user_id,
                'endpoint': metric.endpoint
            }
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.error("❌ Failed to write metric to log",
                        error=str(e),
                        log_file=str(self.log_file))
    
    def _update_real_time_stats(self, metric: CacheMetric) -> None:
        """Real-time istatistikleri güncelle."""
        try:
            now = datetime.now()
            hour_key = now.strftime('%Y-%m-%d %H:00')
            day_key = now.strftime('%Y-%m-%d')
            
            # Hourly stats
            if hour_key not in self.hourly_stats:
                self.hourly_stats[hour_key] = {
                    'total_operations': 0,
                    'hits': 0,
                    'misses': 0,
                    'response_times': [],
                    'operations_by_type': defaultdict(int),
                    'top_keys': defaultdict(int)
                }
            
            hour_stats = self.hourly_stats[hour_key]
            hour_stats['total_operations'] += 1
            hour_stats['response_times'].append(metric.response_time_ms)
            hour_stats['operations_by_type'][metric.operation] += 1
            hour_stats['top_keys'][metric.cache_key] += 1
            
            if metric.operation == 'hit':
                hour_stats['hits'] += 1
            elif metric.operation == 'miss':
                hour_stats['misses'] += 1
            
            # Daily stats (similar structure)
            if day_key not in self.daily_stats:
                self.daily_stats[day_key] = {
                    'total_operations': 0,
                    'hits': 0,
                    'misses': 0,
                    'response_times': [],
                    'operations_by_type': defaultdict(int),
                    'top_keys': defaultdict(int)
                }
            
            day_stats = self.daily_stats[day_key]
            day_stats['total_operations'] += 1
            day_stats['response_times'].append(metric.response_time_ms)
            day_stats['operations_by_type'][metric.operation] += 1
            day_stats['top_keys'][metric.cache_key] += 1
            
            if metric.operation == 'hit':
                day_stats['hits'] += 1
            elif metric.operation == 'miss':
                day_stats['misses'] += 1
                
        except Exception as e:
            logger.error("❌ Failed to update real-time stats",
                        error=str(e))
    
    def _check_performance_alerts(self, metric: CacheMetric) -> None:
        """Performance alert'lerini kontrol et."""
        try:
            now = datetime.now()
            
            # Response time alerts
            if metric.response_time_ms > self.thresholds['response_time_critical']:
                self._create_alert(
                    'critical',
                    f"Critical response time: {metric.response_time_ms:.1f}ms",
                    'response_time',
                    metric.response_time_ms,
                    self.thresholds['response_time_critical'],
                    f"Investigate cache key: {metric.cache_key}"
                )
            elif metric.response_time_ms > self.thresholds['response_time_warning']:
                self._create_alert(
                    'warning',
                    f"High response time: {metric.response_time_ms:.1f}ms",
                    'response_time',
                    metric.response_time_ms,
                    self.thresholds['response_time_warning'],
                    "Monitor cache performance"
                )
            
            # Check hit rate alerts (every 100 operations)
            if len(self.metrics) % 100 == 0 and len(self.metrics) > 0:
                recent_metrics = list(self.metrics)[-100:]
                hits = sum(1 for m in recent_metrics if m.operation == 'hit')
                total_cache_ops = sum(1 for m in recent_metrics if m.operation in ['hit', 'miss'])
                
                if total_cache_ops > 0:
                    hit_rate = (hits / total_cache_ops) * 100
                    
                    if hit_rate < self.thresholds['hit_rate_critical']:
                        self._create_alert(
                            'critical',
                            f"Critical hit rate: {hit_rate:.1f}%",
                            'hit_rate',
                            hit_rate,
                            self.thresholds['hit_rate_critical'],
                            "Review cache strategy and TTL values"
                        )
                    elif hit_rate < self.thresholds['hit_rate_warning']:
                        self._create_alert(
                            'warning',
                            f"Low hit rate: {hit_rate:.1f}%",
                            'hit_rate',
                            hit_rate,
                            self.thresholds['hit_rate_warning'],
                            "Consider increasing cache TTL"
                        )
                        
        except Exception as e:
            logger.error("❌ Failed to check performance alerts",
                        error=str(e))
    
    def _create_alert(self,
                     severity: str,
                     message: str,
                     metric_type: str,
                     current_value: float,
                     threshold_value: float,
                     action_required: str) -> None:
        """Performance alert oluştur."""
        try:
            # Alert cooldown check
            alert_key = f"{severity}_{metric_type}"
            now = datetime.now()
            
            if alert_key in self.last_alert_time:
                time_since_last = (now - self.last_alert_time[alert_key]).total_seconds() / 60
                if time_since_last < self.alert_cooldown_minutes:
                    return  # Skip duplicate alert
            
            alert = CacheAlert(
                timestamp=now,
                severity=severity,
                message=message,
                metric_type=metric_type,
                current_value=current_value,
                threshold_value=threshold_value,
                action_required=action_required
            )
            
            self.alerts.append(alert)
            self.last_alert_time[alert_key] = now
            
            # Log alert
            logger.warning("⚠️ Cache performance alert",
                          severity=severity,
                          message=message,
                          current_value=current_value,
                          threshold=threshold_value)
            
            # Write alert to separate log file
            alert_log_file = self.log_file.parent / "cache_alerts.json"
            with open(alert_log_file, 'a', encoding='utf-8') as f:
                alert_data = asdict(alert)
                alert_data['timestamp'] = alert.timestamp.isoformat()
                f.write(json.dumps(alert_data) + '\n')
                
        except Exception as e:
            logger.error("❌ Failed to create alert",
                        error=str(e))
    
    def generate_performance_report(self, 
                                   time_period: str = "last_hour") -> CachePerformanceReport:
        """
        Performance raporu oluştur.
        
        Args:
            time_period: "last_hour", "last_day", "last_week"
            
        Returns:
            CachePerformanceReport
        """
        try:
            now = datetime.now()
            
            # Time period filtering
            if time_period == "last_hour":
                cutoff_time = now - timedelta(hours=1)
            elif time_period == "last_day":
                cutoff_time = now - timedelta(days=1)
            elif time_period == "last_week":
                cutoff_time = now - timedelta(weeks=1)
            else:
                cutoff_time = now - timedelta(hours=1)
            
            # Filter metrics
            relevant_metrics = [
                m for m in self.metrics 
                if m.timestamp >= cutoff_time
            ]
            
            if not relevant_metrics:
                return self._create_empty_report(time_period)
            
            # Calculate statistics
            total_operations = len(relevant_metrics)
            cache_hits = sum(1 for m in relevant_metrics if m.operation == 'hit')
            cache_misses = sum(1 for m in relevant_metrics if m.operation == 'miss')
            
            total_cache_ops = cache_hits + cache_misses
            hit_rate = (cache_hits / max(total_cache_ops, 1)) * 100
            
            response_times = [m.response_time_ms for m in relevant_metrics]
            avg_response_time = statistics.mean(response_times)
            peak_response_time = max(response_times)
            
            # Operations per second
            time_span_seconds = (now - cutoff_time).total_seconds()
            ops_per_second = total_operations / max(time_span_seconds, 1)
            
            # Cache size trends
            cache_size_trends = []
            for m in relevant_metrics:
                if m.cache_size_kb is not None:
                    cache_size_trends.append((m.timestamp, m.cache_size_kb))
            
            # Top accessed keys
            key_counts = defaultdict(int)
            for m in relevant_metrics:
                key_counts[m.cache_key] += 1
            
            top_keys = sorted(key_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Performance grade
            performance_grade = self._calculate_performance_grade(
                hit_rate, avg_response_time, ops_per_second
            )
            
            # Recommendations
            recommendations = self._generate_recommendations(
                hit_rate, avg_response_time, ops_per_second, top_keys
            )
            
            report = CachePerformanceReport(
                time_period=time_period,
                total_operations=total_operations,
                cache_hits=cache_hits,
                cache_misses=cache_misses,
                hit_rate_percentage=hit_rate,
                avg_response_time_ms=avg_response_time,
                peak_response_time_ms=peak_response_time,
                operations_per_second=ops_per_second,
                cache_size_trends=cache_size_trends,
                top_accessed_keys=top_keys,
                performance_grade=performance_grade,
                recommendations=recommendations
            )
            
            logger.info("📊 Performance report generated",
                       time_period=time_period,
                       hit_rate=f"{hit_rate:.1f}%",
                       grade=performance_grade)
            
            return report
            
        except Exception as e:
            logger.error("❌ Failed to generate performance report",
                        error=str(e),
                        time_period=time_period)
            return self._create_empty_report(time_period)
    
    def _create_empty_report(self, time_period: str) -> CachePerformanceReport:
        """Boş performance raporu oluştur."""
        return CachePerformanceReport(
            time_period=time_period,
            total_operations=0,
            cache_hits=0,
            cache_misses=0,
            hit_rate_percentage=0.0,
            avg_response_time_ms=0.0,
            peak_response_time_ms=0.0,
            operations_per_second=0.0,
            cache_size_trends=[],
            top_accessed_keys=[],
            performance_grade="N/A",
            recommendations=["No data available for analysis"]
        )
    
    def _calculate_performance_grade(self, 
                                   hit_rate: float,
                                   avg_response_time: float,
                                   ops_per_second: float) -> str:
        """Performance grade hesapla."""
        score = 0
        
        # Hit rate scoring (40 points)
        if hit_rate >= 90:
            score += 40
        elif hit_rate >= 80:
            score += 35
        elif hit_rate >= 70:
            score += 30
        elif hit_rate >= 60:
            score += 20
        elif hit_rate >= 50:
            score += 10
        
        # Response time scoring (35 points)
        if avg_response_time <= 10:
            score += 35
        elif avg_response_time <= 50:
            score += 30
        elif avg_response_time <= 100:
            score += 25
        elif avg_response_time <= 200:
            score += 15
        elif avg_response_time <= 500:
            score += 5
        
        # Operations per second scoring (25 points)
        if ops_per_second >= 100:
            score += 25
        elif ops_per_second >= 50:
            score += 20
        elif ops_per_second >= 20:
            score += 15
        elif ops_per_second >= 10:
            score += 10
        elif ops_per_second >= 1:
            score += 5
        
        # Grade assignment
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_recommendations(self,
                                hit_rate: float,
                                avg_response_time: float,
                                ops_per_second: float,
                                top_keys: List[Tuple[str, int]]) -> List[str]:
        """Performance önerileri oluştur."""
        recommendations = []
        
        # Hit rate recommendations
        if hit_rate < 70:
            recommendations.append("Increase cache TTL values to improve hit rate")
            recommendations.append("Review cache invalidation strategy")
        
        if hit_rate < 50:
            recommendations.append("Consider pre-warming cache for popular keys")
        
        # Response time recommendations
        if avg_response_time > 100:
            recommendations.append("Optimize cache lookup operations")
            recommendations.append("Consider cache data compression")
        
        if avg_response_time > 500:
            recommendations.append("Critical: Investigate cache backend performance")
        
        # Operations per second recommendations
        if ops_per_second < 10:
            recommendations.append("Cache utilization is low - review implementation")
        
        # Top keys analysis
        if top_keys:
            top_key_access = top_keys[0][1]
            total_accesses = sum(count for _, count in top_keys)
            if top_key_access / total_accesses > 0.5:
                recommendations.append("High concentration on single key - consider data distribution")
        
        # Default recommendations
        if not recommendations:
            recommendations.append("Cache performance is good - maintain current strategy")
        
        return recommendations[:5]  # Top 5 recommendations
    
    def export_dashboard_metrics(self) -> Dict[str, Any]:
        """Dashboard için metrics export et."""
        try:
            # Generate recent reports
            hourly_report = self.generate_performance_report("last_hour")
            daily_report = self.generate_performance_report("last_day")
            
            # Recent alerts
            recent_alerts = [
                {
                    'timestamp': alert.timestamp.isoformat(),
                    'severity': alert.severity,
                    'message': alert.message,
                    'metric_type': alert.metric_type,
                    'current_value': alert.current_value,
                    'action_required': alert.action_required
                }
                for alert in list(self.alerts)[-10:]  # Last 10 alerts
            ]
            
            return {
                'timestamp': datetime.now().isoformat(),
                'hourly_performance': asdict(hourly_report),
                'daily_performance': asdict(daily_report),
                'recent_alerts': recent_alerts,
                'system_health': {
                    'monitoring_active': self.monitoring_active,
                    'total_metrics_recorded': len(self.metrics),
                    'alert_count_24h': len([a for a in self.alerts 
                                          if (datetime.now() - a.timestamp).days < 1])
                },
                'thresholds': self.thresholds
            }
            
        except Exception as e:
            logger.error("❌ Failed to export dashboard metrics",
                        error=str(e))
            return {'error': str(e)}
    
    def start_background_monitoring(self) -> None:
        """Background monitoring başlat."""
        if self.monitoring_active:
            logger.warning("⚠️ Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._background_monitor, daemon=True)
        self.monitor_thread.start()
        
        logger.info("✅ Background cache monitoring started")
    
    def stop_background_monitoring(self) -> None:
        """Background monitoring durdur."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("🛑 Background cache monitoring stopped")
    
    def _background_monitor(self) -> None:
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                # Cleanup old metrics (keep last 24 hours)
                cutoff_time = datetime.now() - timedelta(hours=24)
                metrics_to_keep = [m for m in self.metrics if m.timestamp >= cutoff_time]
                self.metrics.clear()
                self.metrics.extend(metrics_to_keep)
                
                # Cleanup old hourly stats (keep last week)
                week_ago = datetime.now() - timedelta(weeks=1)
                keys_to_remove = [
                    k for k in self.hourly_stats.keys()
                    if datetime.strptime(k, '%Y-%m-%d %H:00') < week_ago
                ]
                for key in keys_to_remove:
                    del self.hourly_stats[key]
                
                # Sleep for 5 minutes
                time.sleep(300)
                
            except Exception as e:
                logger.error("❌ Background monitor error",
                           error=str(e))
                time.sleep(60)  # Wait 1 minute on error

# Global monitor instance
cache_monitor = CachePerformanceMonitor()

def record_cache_hit(cache_key: str, response_time_ms: float, **kwargs) -> None:
    """Cache hit kaydet."""
    cache_monitor.record_cache_operation(
        'hit', cache_key, response_time_ms, **kwargs
    )

def record_cache_miss(cache_key: str, response_time_ms: float, **kwargs) -> None:
    """Cache miss kaydet."""
    cache_monitor.record_cache_operation(
        'miss', cache_key, response_time_ms, **kwargs
    )

def record_cache_set(cache_key: str, response_time_ms: float, **kwargs) -> None:
    """Cache set kaydet."""
    cache_monitor.record_cache_operation(
        'set', cache_key, response_time_ms, **kwargs
    )

if __name__ == "__main__":
    # Test the monitor
    print("📊 Testing Cache Performance Monitor...")
    print("=" * 50)
    
    # Start background monitoring
    cache_monitor.start_background_monitoring()
    
    # Simulate some cache operations
    import random
    
    print("🔄 Simulating cache operations...")
    
    for i in range(50):
        # Simulate cache operations
        if random.random() < 0.7:  # 70% hit rate
            record_cache_hit(
                f"user_profile_{random.randint(1, 10)}",
                random.uniform(5, 50)
            )
        else:
            record_cache_miss(
                f"user_profile_{random.randint(1, 10)}",
                random.uniform(20, 200)
            )
        
        # Some cache sets
        if random.random() < 0.1:
            record_cache_set(
                f"user_profile_{random.randint(1, 10)}",
                random.uniform(10, 100),
                ttl_seconds=3600
            )
    
    print("✅ Generated 50 cache operations")
    
    # Generate performance report
    report = cache_monitor.generate_performance_report("last_hour")
    print(f"\n📊 Performance Report:")
    print(f"   Hit Rate: {report.hit_rate_percentage:.1f}%")
    print(f"   Avg Response Time: {report.avg_response_time_ms:.1f}ms")
    print(f"   Operations/sec: {report.operations_per_second:.1f}")
    print(f"   Performance Grade: {report.performance_grade}")
    print(f"   Recommendations: {len(report.recommendations)}")
    
    # Export dashboard metrics
    dashboard_data = cache_monitor.export_dashboard_metrics()
    print(f"\n📈 Dashboard export: {len(dashboard_data)} sections")
    
    # Stop monitoring
    cache_monitor.stop_background_monitoring()
    print("\n✅ Cache Performance Monitor test completed!") 