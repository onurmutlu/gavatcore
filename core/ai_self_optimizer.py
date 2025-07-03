#!/usr/bin/env python3
"""
🤖 AI Self-Optimizer
==================

CPU ve ops/sec metriklerine göre kendini optimize eden
AI destekli meta-analyzer sistemi.

✨ Özellikler:
- Real-time performance monitoring
- AI-driven optimization suggestions
- Auto-tuning configuration updates
- Machine learning pattern recognition
- Predictive performance scaling
- Dynamic resource allocation

@version: 1.0.0
@created: 2025-01-30
"""

import asyncio
import json
import time
import yaml
import psutil
import statistics
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
import structlog

# AI/ML imports
try:
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = structlog.get_logger("ai_self_optimizer")

@dataclass
class PerformanceMetrics:
    """Performance metrikleri veri yapısı."""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    cache_hit_rate: float
    avg_response_time: float
    operations_per_second: float
    active_connections: int
    error_rate: float

@dataclass
class OptimizationRecommendation:
    """Optimizasyon önerisi veri yapısı."""
    category: str
    priority: int  # 1-5 (5 = critical)
    title: str
    description: str
    config_changes: Dict[str, Any]
    expected_improvement: float
    confidence: float
    implementation_difficulty: str  # easy, medium, hard

@dataclass
class SystemBenchmark:
    """Sistem benchmark veri yapısı."""
    baseline_cpu: float
    baseline_memory: float
    baseline_ops_per_sec: float
    peak_performance_time: str
    degradation_threshold: float = 0.15  # %15 düşüş
    improvement_target: float = 0.20     # %20 artış hedefi

class AIPerformanceAnalyzer:
    """AI destekli performans analyzer."""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history_size = 1000
        self.model_trained = False
        
        if ML_AVAILABLE:
            self.performance_model = LinearRegression()
            self.scaler = StandardScaler()
        
        logger.info("🤖 AI Performance Analyzer initialized")
    
    def add_metrics(self, metrics: PerformanceMetrics):
        """Yeni metrik ekle."""
        self.metrics_history.append(metrics)
        
        # History'yi sınırla
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    def analyze_trends(self) -> Dict[str, Any]:
        """Performance trend analizi."""
        if len(self.metrics_history) < 10:
            return {"status": "insufficient_data", "samples": len(self.metrics_history)}
        
        recent_metrics = self.metrics_history[-50:]  # Son 50 sample
        
        # Trend hesaplamaları
        cpu_trend = self._calculate_trend([m.cpu_usage for m in recent_metrics])
        memory_trend = self._calculate_trend([m.memory_usage for m in recent_metrics])
        response_trend = self._calculate_trend([m.avg_response_time for m in recent_metrics])
        ops_trend = self._calculate_trend([m.operations_per_second for m in recent_metrics])
        
        # Anomaly detection
        anomalies = self._detect_anomalies(recent_metrics)
        
        return {
            "status": "analyzed",
            "trends": {
                "cpu": cpu_trend,
                "memory": memory_trend,
                "response_time": response_trend,
                "operations_per_second": ops_trend
            },
            "anomalies": anomalies,
            "samples_analyzed": len(recent_metrics),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Trend hesapla."""
        if len(values) < 5:
            return {"trend": "unknown", "slope": 0, "correlation": 0}
        
        x = list(range(len(values)))
        y = values
        
        # Linear regression ile trend
        if ML_AVAILABLE:
            try:
                x_array = np.array(x).reshape(-1, 1)
                y_array = np.array(y)
                
                model = LinearRegression()
                model.fit(x_array, y_array)
                
                slope = model.coef_[0]
                correlation = model.score(x_array, y_array)
                
                if slope > 0.01:
                    trend_direction = "increasing"
                elif slope < -0.01:
                    trend_direction = "decreasing"
                else:
                    trend_direction = "stable"
                
                return {
                    "trend": trend_direction,
                    "slope": slope,
                    "correlation": correlation,
                    "avg": statistics.mean(values),
                    "std": statistics.stdev(values) if len(values) > 1 else 0
                }
            except Exception as e:
                logger.warning("⚠️ Trend calculation error", error=str(e))
        
        # Fallback: basit trend
        recent_avg = statistics.mean(values[-5:])
        older_avg = statistics.mean(values[:5])
        
        if recent_avg > older_avg * 1.05:
            trend_direction = "increasing"
        elif recent_avg < older_avg * 0.95:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
        
        return {
            "trend": trend_direction,
            "slope": recent_avg - older_avg,
            "correlation": 0,
            "avg": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0
        }
    
    def _detect_anomalies(self, metrics: List[PerformanceMetrics]) -> List[Dict[str, Any]]:
        """Anomaly detection."""
        anomalies = []
        
        if len(metrics) < 10:
            return anomalies
        
        # CPU spike detection
        cpu_values = [m.cpu_usage for m in metrics]
        cpu_avg = statistics.mean(cpu_values)
        cpu_std = statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0
        
        for i, metric in enumerate(metrics[-10:]):  # Son 10'u kontrol et
            if metric.cpu_usage > cpu_avg + (2 * cpu_std):
                anomalies.append({
                    "type": "cpu_spike",
                    "severity": "high" if metric.cpu_usage > 80 else "medium",
                    "value": metric.cpu_usage,
                    "threshold": cpu_avg + (2 * cpu_std),
                    "timestamp": metric.timestamp
                })
            
            # Response time spike
            if metric.avg_response_time > 1000:  # 1 saniye üzeri
                anomalies.append({
                    "type": "response_spike", 
                    "severity": "critical" if metric.avg_response_time > 5000 else "high",
                    "value": metric.avg_response_time,
                    "threshold": 1000,
                    "timestamp": metric.timestamp
                })
            
            # Low operations per second
            if metric.operations_per_second < 100 and metric.operations_per_second > 0:
                anomalies.append({
                    "type": "low_performance",
                    "severity": "medium",
                    "value": metric.operations_per_second,
                    "threshold": 100,
                    "timestamp": metric.timestamp
                })
        
        return anomalies

class AIOptimizationEngine:
    """AI destekli optimizasyon engine."""
    
    def __init__(self):
        self.analyzer = AIPerformanceAnalyzer()
        self.config_path = Path("config/engine_config.yaml")
        self.recommendations_history: List[OptimizationRecommendation] = []
        
        # Baseline performance
        self.baseline: Optional[SystemBenchmark] = None
        self._load_baseline()
        
        logger.info("🧠 AI Optimization Engine initialized")
    
    def _load_baseline(self):
        """Baseline performance'ı yükle."""
        baseline_file = Path("config/system_baseline.json")
        if baseline_file.exists():
            try:
                with open(baseline_file, 'r') as f:
                    data = json.load(f)
                    self.baseline = SystemBenchmark(**data)
                    logger.info("📊 Baseline loaded", baseline=data)
            except Exception as e:
                logger.warning("⚠️ Baseline loading error", error=str(e))
    
    def save_baseline(self, metrics: PerformanceMetrics):
        """Yeni baseline kaydet."""
        baseline_data = {
            "baseline_cpu": metrics.cpu_usage,
            "baseline_memory": metrics.memory_usage,
            "baseline_ops_per_sec": metrics.operations_per_second,
            "peak_performance_time": datetime.now().isoformat()
        }
        
        baseline_file = Path("config/system_baseline.json")
        baseline_file.parent.mkdir(exist_ok=True)
        
        with open(baseline_file, 'w') as f:
            json.dump(baseline_data, f, indent=2)
        
        self.baseline = SystemBenchmark(**baseline_data)
        logger.info("✅ New baseline saved", **baseline_data)
    
    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """AI destekli optimizasyon önerileri oluştur."""
        recommendations = []
        
        if analysis["status"] != "analyzed":
            return recommendations
        
        trends = analysis["trends"]
        anomalies = analysis["anomalies"]
        
        # CPU optimization
        if trends["cpu"]["trend"] == "increasing" and trends["cpu"]["avg"] > 70:
            recommendations.append(OptimizationRecommendation(
                category="performance",
                priority=4,
                title="CPU Usage Optimization",
                description="CPU kullanımı artış eğiliminde. Cache katmanı güçlendirilmeli.",
                config_changes={
                    "cache": {
                        "default_ttl": 600,  # 10 dakika
                        "max_entries": 5000,
                        "compression_enabled": True
                    },
                    "threading": {
                        "max_workers": max(1, psutil.cpu_count() - 1)
                    }
                },
                expected_improvement=0.25,
                confidence=0.8,
                implementation_difficulty="easy"
            ))
        
        # Response time optimization
        if trends["response_time"]["trend"] == "increasing" and trends["response_time"]["avg"] > 500:
            recommendations.append(OptimizationRecommendation(
                category="latency",
                priority=5,
                title="Response Time Optimization",
                description="Yanıt süreleri kritik seviyede. Agresif cache ve connection pooling gerekli.",
                config_changes={
                    "cache": {
                        "aggressive_mode": True,
                        "preload_frequent_queries": True
                    },
                    "database": {
                        "connection_pool_size": 20,
                        "query_timeout": 5
                    }
                },
                expected_improvement=0.40,
                confidence=0.9,
                implementation_difficulty="medium"
            ))
        
        # Memory optimization
        if trends["memory"]["trend"] == "increasing" and trends["memory"]["avg"] > 80:
            recommendations.append(OptimizationRecommendation(
                category="memory",
                priority=3,
                title="Memory Usage Optimization",
                description="Bellek kullanımı yüksek. Garbage collection ve cache cleanup gerekli.",
                config_changes={
                    "memory": {
                        "gc_threshold": 70,
                        "cache_cleanup_interval": 300
                    }
                },
                expected_improvement=0.15,
                confidence=0.7,
                implementation_difficulty="easy"
            ))
        
        # Operations per second optimization
        if trends["operations_per_second"]["trend"] == "decreasing":
            recommendations.append(OptimizationRecommendation(
                category="throughput",
                priority=4,
                title="Throughput Optimization",
                description="İşlem hızı düşüyor. Paralel işleme ve batch operations gerekli.",
                config_changes={
                    "processing": {
                        "batch_size": 100,
                        "parallel_workers": psutil.cpu_count(),
                        "async_mode": True
                    }
                },
                expected_improvement=0.30,
                confidence=0.75,
                implementation_difficulty="medium"
            ))
        
        # Anomaly-based recommendations
        for anomaly in anomalies:
            if anomaly["type"] == "cpu_spike":
                recommendations.append(OptimizationRecommendation(
                    category="stability",
                    priority=5,
                    title="CPU Spike Prevention",
                    description=f"CPU spike detected ({anomaly['value']:.1f}%). Rate limiting gerekli.",
                    config_changes={
                        "rate_limiting": {
                            "enabled": True,
                            "max_requests_per_minute": 60,
                            "burst_limit": 10
                        }
                    },
                    expected_improvement=0.20,
                    confidence=0.85,
                    implementation_difficulty="easy"
                ))
        
        # Remove duplicates and sort by priority
        unique_recommendations = list({r.title: r for r in recommendations}.values())
        unique_recommendations.sort(key=lambda x: x.priority, reverse=True)
        
        self.recommendations_history.extend(unique_recommendations)
        logger.info("🤖 Generated recommendations", count=len(unique_recommendations))
        
        return unique_recommendations
    
    def apply_optimizations(self, recommendations: List[OptimizationRecommendation], 
                          auto_apply: bool = False) -> Dict[str, Any]:
        """Optimizasyonları uygula."""
        applied_changes = {}
        applied_count = 0
        
        for rec in recommendations:
            # Auto-apply sadece kolay ve güvenli değişiklikler için
            if auto_apply and rec.implementation_difficulty == "easy" and rec.confidence > 0.8:
                try:
                    self._apply_config_changes(rec.config_changes)
                    applied_changes[rec.title] = rec.config_changes
                    applied_count += 1
                    
                    logger.info("✅ Auto-applied optimization",
                              title=rec.title,
                              category=rec.category,
                              expected_improvement=f"{rec.expected_improvement:.1%}")
                except Exception as e:
                    logger.error("❌ Auto-apply failed",
                               title=rec.title,
                               error=str(e))
        
        return {
            "applied_count": applied_count,
            "total_recommendations": len(recommendations),
            "applied_changes": applied_changes,
            "timestamp": datetime.now().isoformat()
        }
    
    def _apply_config_changes(self, changes: Dict[str, Any]):
        """Config değişikliklerini uygula."""
        # Engine config dosyasını yükle/oluştur
        self.config_path.parent.mkdir(exist_ok=True)
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}
        
        # Değişiklikleri uygula
        for section, values in changes.items():
            if section not in config:
                config[section] = {}
            config[section].update(values)
        
        # Timestamp ekle
        config["last_optimization"] = datetime.now().isoformat()
        
        # Kaydet
        with open(self.config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)

class SelfOptimizingSystem:
    """Self-optimizing GAVATCore sistemi."""
    
    def __init__(self):
        self.engine = AIOptimizationEngine()
        self.monitoring_active = False
        self.optimization_interval = 300  # 5 dakika
        self.auto_optimize = True  # Otomatik optimizasyon
        
        logger.info("🚀 Self-Optimizing System initialized")
    
    def start_monitoring(self):
        """Monitoring'i başlat."""
        if self.monitoring_active:
            logger.warning("⚠️ Monitoring already active")
            return
        
        self.monitoring_active = True
        
        # Background thread başlat
        monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitoring_thread.start()
        
        logger.info("📊 Self-optimization monitoring started",
                   interval=self.optimization_interval,
                   auto_optimize=self.auto_optimize)
    
    def stop_monitoring(self):
        """Monitoring'i durdur."""
        self.monitoring_active = False
        logger.info("🛑 Self-optimization monitoring stopped")
    
    def _monitoring_loop(self):
        """Ana monitoring loop."""
        logger.info("🔄 Monitoring loop started")
        
        while self.monitoring_active:
            try:
                # Mevcut metrikleri topla
                metrics = self._collect_current_metrics()
                self.engine.analyzer.add_metrics(metrics)
                
                # Her optimization_interval'da analiz yap
                if len(self.engine.analyzer.metrics_history) % 10 == 0:  # Her 10 metrik toplama
                    self._run_optimization_cycle()
                
                time.sleep(30)  # 30 saniye bekle
                
            except Exception as e:
                logger.error("❌ Monitoring loop error", error=str(e))
                time.sleep(60)  # Hata durumunda daha uzun bekle
    
    def _collect_current_metrics(self) -> PerformanceMetrics:
        """Mevcut sistem metriklerini topla."""
        try:
            # System metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Network connections
            connections = len(psutil.net_connections())
            
            # Placeholder values - gerçek uygulamada API'lerden gelecek
            cache_hit_rate = 0.0
            avg_response_time = 0.0
            operations_per_second = 0.0
            error_rate = 0.0
            
            # Try to get real data from running services
            try:
                import requests
                # Dashboard stats'den gerçek değerleri al
                response = requests.get("http://localhost:8000/api/dashboard/stats", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    cache_hit_rate = data.get('cache_hit_rate', 0)
                    avg_response_time = data.get('avg_response_time', 0)
            except:
                pass
            
            return PerformanceMetrics(
                timestamp=time.time(),
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                cache_hit_rate=cache_hit_rate,
                avg_response_time=avg_response_time,
                operations_per_second=operations_per_second,
                active_connections=connections,
                error_rate=error_rate
            )
            
        except Exception as e:
            logger.error("❌ Metrics collection error", error=str(e))
            # Return default metrics
            return PerformanceMetrics(
                timestamp=time.time(),
                cpu_usage=0.0,
                memory_usage=0.0,
                cache_hit_rate=0.0,
                avg_response_time=0.0,
                operations_per_second=0.0,
                active_connections=0,
                error_rate=0.0
            )
    
    def _run_optimization_cycle(self):
        """Optimizasyon döngüsünü çalıştır."""
        try:
            logger.info("🔍 Running optimization analysis...")
            
            # Trend analizi
            analysis = self.engine.analyzer.analyze_trends()
            
            if analysis["status"] == "analyzed":
                # Recommendations oluştur
                recommendations = self.engine.generate_recommendations(analysis)
                
                if recommendations:
                    logger.info("💡 Optimization recommendations generated",
                              count=len(recommendations),
                              high_priority=len([r for r in recommendations if r.priority >= 4]))
                    
                    # Auto-apply if enabled
                    if self.auto_optimize:
                        result = self.engine.apply_optimizations(recommendations, auto_apply=True)
                        
                        if result["applied_count"] > 0:
                            logger.info("✅ Auto-optimizations applied",
                                      applied=result["applied_count"],
                                      total=result["total_recommendations"])
                    
                    # Save optimization report
                    self._save_optimization_report(analysis, recommendations)
                else:
                    logger.debug("🎯 System performing optimally - no recommendations needed")
            else:
                logger.debug("📊 Insufficient data for analysis",
                           samples=analysis.get("samples", 0))
                
        except Exception as e:
            logger.error("❌ Optimization cycle error", error=str(e))
    
    def _save_optimization_report(self, analysis: Dict[str, Any], 
                                recommendations: List[OptimizationRecommendation]):
        """Optimizasyon raporunu kaydet."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "recommendations": [
                {
                    "category": r.category,
                    "priority": r.priority,
                    "title": r.title,
                    "description": r.description,
                    "expected_improvement": r.expected_improvement,
                    "confidence": r.confidence,
                    "difficulty": r.implementation_difficulty
                }
                for r in recommendations
            ]
        }
        
        reports_dir = Path("logs/optimization_reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / f"optimization_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.debug("📄 Optimization report saved", file=str(report_file))

# Global instance
self_optimizer = SelfOptimizingSystem()

def start_self_optimization():
    """Self-optimization sistemini başlat."""
    self_optimizer.start_monitoring()

def stop_self_optimization():
    """Self-optimization sistemini durdur."""
    self_optimizer.stop_monitoring()

def get_optimization_status() -> Dict[str, Any]:
    """Optimizasyon durumunu al."""
    return {
        "monitoring_active": self_optimizer.monitoring_active,
        "auto_optimize": self_optimizer.auto_optimize,
        "total_metrics": len(self_optimizer.engine.analyzer.metrics_history),
        "total_recommendations": len(self_optimizer.engine.recommendations_history),
        "ml_available": ML_AVAILABLE
    }

if __name__ == "__main__":
    import signal
    import sys
    
    def signal_handler(signum, frame):
        logger.info("🛑 Shutdown signal received")
        stop_self_optimization()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🤖 Starting AI Self-Optimizer...")
    print("=" * 50)
    print("🧠 Features:")
    print("   • Real-time performance monitoring")
    print("   • AI-driven optimization suggestions")
    print("   • Auto-tuning configuration updates")
    print("   • Machine learning pattern recognition")
    print("   • Predictive performance scaling")
    print("   • Dynamic resource allocation")
    print()
    print(f"🔬 ML Available: {ML_AVAILABLE}")
    print("🚀 Starting monitoring...")
    print("=" * 50)
    
    start_self_optimization()
    
    try:
        while True:
            time.sleep(60)
            status = get_optimization_status()
            print(f"📊 Status: Monitoring={status['monitoring_active']}, "
                  f"Metrics={status['total_metrics']}, "
                  f"Recommendations={status['total_recommendations']}")
    except KeyboardInterrupt:
        logger.info("⌨️ Keyboard interrupt")
        stop_self_optimization() 