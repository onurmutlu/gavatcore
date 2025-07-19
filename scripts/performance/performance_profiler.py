from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🔍 GAVATCore Performance Profiler & Bottleneck Analyzer
=====================================================

Detaylı cProfile analizi ve performans optimizasyonu.
Sistem bottleneck'lerini tespit eder ve optimize edilmiş çözümler sunar.

@version: 1.0.0
@created: 2025-01-30
"""

import cProfile
import pstats
import io
import time
import asyncio
import json
import sys
import tracemalloc
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import structlog

# Performance monitoring imports
try:
    import psutil
    import memory_profiler
    PROFILING_AVAILABLE = True
except ImportError:
    PROFILING_AVAILABLE = False

logger = structlog.get_logger("performance_profiler")

@dataclass
class BottleneckReport:
    """Bottleneck analysis report"""
    function_name: str
    total_time: float
    cumulative_time: float
    call_count: int
    per_call_time: float
    percentage_of_total: float
    memory_usage_mb: float = 0.0
    optimization_priority: str = "medium"
    
    @property
    def is_critical(self) -> bool:
        return (self.percentage_of_total > 10.0 or 
                self.per_call_time > 0.1 or 
                self.memory_usage_mb > 50.0)

@dataclass
class ProfilingSession:
    """Profiling session results"""
    session_name: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    bottlenecks: List[BottleneckReport] = field(default_factory=list)
    total_execution_time: float = 0.0
    memory_usage_peak: float = 0.0
    optimization_recommendations: List[str] = field(default_factory=list)

class GAVATCorePerformanceProfiler:
    """
    🔍 Comprehensive Performance Profiler
    
    Detaylı cProfile analizi ile bottleneck tespiti ve optimizasyon önerileri.
    """
    
    def __init__(self):
        self.profiling_sessions: List[ProfilingSession] = []
        self.profiler = cProfile.Profile()
        self.memory_tracer_active = False
        
        logger.info("🔍 GAVATCore Performance Profiler başlatıldı")
    
    def start_memory_tracking(self):
        """Memory tracking başlat"""
        if not self.memory_tracer_active:
            tracemalloc.start()
            self.memory_tracer_active = True
            logger.info("📊 Memory tracking başlatıldı")
    
    def stop_memory_tracking(self) -> Dict[str, float]:
        """Memory tracking durdur ve sonuçları döndür"""
        if self.memory_tracer_active:
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            self.memory_tracer_active = False
            
            return {
                "current_memory_mb": current / (1024 * 1024),
                "peak_memory_mb": peak / (1024 * 1024)
            }
        return {"current_memory_mb": 0.0, "peak_memory_mb": 0.0}
    
    def profile_function(self, func: Callable, *args, **kwargs) -> Any:
        """Bir fonksiyonu profile et"""
        self.start_memory_tracking()
        
        # cProfile ile profiling
        self.profiler.enable()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Profiling sırasında hata: {e}")
            result = None
        finally:
            end_time = time.time()
            self.profiler.disable()
        
        # Memory tracking sonuçları
        memory_stats = self.stop_memory_tracking()
        
        # Profiling sonuçlarını analiz et
        execution_time = end_time - start_time
        logger.info(f"Fonksiyon profiling tamamlandı: {execution_time:.4f}s")
        
        return result
    
    async def profile_async_function(self, func: Callable, *args, **kwargs) -> Any:
        """Async bir fonksiyonu profile et"""
        self.start_memory_tracking()
        
        # cProfile async desteği için wrapper
        def async_wrapper():
            return asyncio.run(func(*args, **kwargs))
        
        self.profiler.enable()
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Async profiling sırasında hata: {e}")
            result = None
        finally:
            end_time = time.time()
            self.profiler.disable()
        
        memory_stats = self.stop_memory_tracking()
        execution_time = end_time - start_time
        
        logger.info(f"Async fonksiyon profiling tamamlandı: {execution_time:.4f}s")
        return result
    
    def analyze_bottlenecks(self, min_percentage: float = 1.0) -> List[BottleneckReport]:
        """cProfile sonuçlarından bottleneck'leri analiz et"""
        
        # cProfile sonuçlarını string buffer'a al
        s = io.StringIO()
        stats = pstats.Stats(self.profiler, stream=s)
        stats.sort_stats('cumulative')
        stats.print_stats()
        
        # Sonuçları parse et
        profile_output = s.getvalue()
        bottlenecks = []
        
        # Profile output'unu satır satır analiz et
        lines = profile_output.split('\n')
        data_started = False
        total_time = 0.0
        
        for line in lines:
            if 'function calls' in line and 'CPU seconds' in line:
                # Total time bilgisini çıkar
                try:
                    total_time = float(line.split('CPU seconds')[0].split()[-1])
                except:
                    total_time = 1.0
                continue
            
            if line.strip().startswith('ncalls'):
                data_started = True
                continue
                
            if data_started and line.strip():
                try:
                    # Parse function data
                    parts = line.strip().split()
                    if len(parts) >= 6:
                        ncalls = parts[0]
                        tottime = float(parts[1])
                        percall_tottime = float(parts[2]) if parts[2] != '0.000' else 0.0
                        cumtime = float(parts[3])
                        percall_cumtime = float(parts[4]) if parts[4] != '0.000' else 0.0
                        filename_function = ' '.join(parts[5:])
                        
                        # Call count parse et
                        call_count = int(ncalls.split('/')[0])
                        
                        # Percentage hesapla
                        percentage = (cumtime / total_time * 100) if total_time > 0 else 0
                        
                        if percentage >= min_percentage:
                            # Optimization priority belirleme
                            if percentage > 20:
                                priority = "critical"
                            elif percentage > 10:
                                priority = "high"
                            elif percentage > 5:
                                priority = "medium"
                            else:
                                priority = "low"
                            
                            bottleneck = BottleneckReport(
                                function_name=filename_function,
                                total_time=tottime,
                                cumulative_time=cumtime,
                                call_count=call_count,
                                per_call_time=percall_cumtime,
                                percentage_of_total=percentage,
                                optimization_priority=priority
                            )
                            
                            bottlenecks.append(bottleneck)
                            
                except (ValueError, IndexError) as e:
                    continue
        
        # Bottleneck'leri percentage'a göre sırala
        bottlenecks.sort(key=lambda x: x.percentage_of_total, reverse=True)
        
        logger.info(f"🔍 {len(bottlenecks)} bottleneck tespit edildi")
        return bottlenecks
    
    def generate_optimization_recommendations(self, bottlenecks: List[BottleneckReport]) -> List[str]:
        """Bottleneck'lere dayalı optimizasyon önerileri oluştur"""
        recommendations = []
        
        critical_bottlenecks = [b for b in bottlenecks if b.is_critical]
        
        if critical_bottlenecks:
            recommendations.append("🚨 Kritik performans sorunları tespit edildi:")
            
            for bottleneck in critical_bottlenecks[:5]:  # Top 5
                if "behavioral" in bottleneck.function_name.lower():
                    recommendations.append(
                        f"• Behavioral analysis optimize et: {bottleneck.function_name} "
                        f"({bottleneck.percentage_of_total:.1f}% CPU)"
                    )
                elif "cache" in bottleneck.function_name.lower():
                    recommendations.append(
                        f"• Cache operations optimize et: {bottleneck.function_name} "
                        f"({bottleneck.percentage_of_total:.1f}% CPU)"
                    )
                elif "database" in bottleneck.function_name.lower() or "sql" in bottleneck.function_name.lower():
                    recommendations.append(
                        f"• Database queries optimize et: {bottleneck.function_name} "
                        f"({bottleneck.percentage_of_total:.1f}% CPU)"
                    )
                elif "json" in bottleneck.function_name.lower() or "pickle" in bottleneck.function_name.lower():
                    recommendations.append(
                        f"• Serialization optimize et: {bottleneck.function_name} "
                        f"({bottleneck.percentage_of_total:.1f}% CPU)"
                    )
                else:
                    recommendations.append(
                        f"• Optimize: {bottleneck.function_name} "
                        f"({bottleneck.percentage_of_total:.1f}% CPU)"
                    )
        
        # Genel optimizasyon önerileri
        high_call_count_funcs = [b for b in bottlenecks if b.call_count > 1000]
        if high_call_count_funcs:
            recommendations.append("🔄 Yüksek call count optimizasyonları:")
            recommendations.append("• Function call overhead'ı azalt")
            recommendations.append("• Caching/memoization kullan")
            recommendations.append("• Batch processing implementasyonu")
        
        slow_per_call_funcs = [b for b in bottlenecks if b.per_call_time > 0.01]
        if slow_per_call_funcs:
            recommendations.append("⏱️ Yavaş fonksiyon optimizasyonları:")
            recommendations.append("• Algoritma complexity azalt")
            recommendations.append("• I/O operations optimize et")
            recommendations.append("• Parallel processing kullan")
        
        return recommendations
    
    def save_profiling_report(self, session: ProfilingSession, filename: Optional[str] = None) -> str:
        """Profiling raporunu kaydet"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"profiling_report_{timestamp}.json"
        
        report_data = {
            "session_name": session.session_name,
            "timestamp": session.start_time.isoformat(),
            "execution_time_seconds": session.total_execution_time,
            "memory_peak_mb": session.memory_usage_peak,
            "bottlenecks_count": len(session.bottlenecks),
            "critical_bottlenecks": len([b for b in session.bottlenecks if b.is_critical]),
            "bottlenecks": [
                {
                    "function": b.function_name,
                    "total_time": b.total_time,
                    "cumulative_time": b.cumulative_time,
                    "call_count": b.call_count,
                    "per_call_time": b.per_call_time,
                    "cpu_percentage": b.percentage_of_total,
                    "priority": b.optimization_priority
                }
                for b in session.bottlenecks[:20]  # Top 20
            ],
            "optimization_recommendations": session.optimization_recommendations
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Profiling raporu kaydedildi: {filename}")
        return filename

# Test scenarios için performance test fonksiyonları
def simulate_behavioral_analysis():
    """Behavioral analysis simulation for profiling"""
    import random
    import json
    
    # Simulate heavy computation
    users_data = []
    for i in range(100):
        user_data = {
            "user_id": i,
            "messages": [f"Message {j} from user {i}" for j in range(10)],
            "personality_traits": {
                "openness": random.random(),
                "conscientiousness": random.random(),
                "extraversion": random.random(),
                "agreeableness": random.random(),
                "neuroticism": random.random()
            }
        }
        
        # Simulate complex calculations
        for trait, value in user_data["personality_traits"].items():
            # Complex mathematical operations
            result = 0
            for _ in range(1000):
                result += value * random.random() ** 2
        
        # JSON serialization/deserialization
        json_str = json.dumps(user_data)
        parsed_data = json.loads(json_str)
        
        users_data.append(parsed_data)
    
    return users_data

def simulate_cache_operations():
    """Cache operations simulation for profiling"""
    cache_data = {}
    
    # Simulate cache set operations
    for i in range(500):
        key = f"cache_key_{i}"
        value = {
            "data": f"cached_value_{i}",
            "timestamp": time.time(),
            "metadata": {"priority": i % 10}
        }
        
        # Simulate hash calculation
        import hashlib
        key_hash = hashlib.md5(key.encode()).hexdigest()
        
        # Simulate compression
        import json
        json_str = json.dumps(value)
        
        cache_data[key_hash] = json_str
    
    # Simulate cache get operations
    hits = 0
    for i in range(200):
        key = f"cache_key_{i % 100}"
        key_hash = hashlib.md5(key.encode()).hexdigest()
        
        if key_hash in cache_data:
            data = json.loads(cache_data[key_hash])
            hits += 1
    
    return hits

def simulate_database_operations():
    """Database operations simulation for profiling"""
    import sqlite3
    import tempfile
    import os
    
    # Temporary database
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    
    try:
        conn = sqlite3.connect(temp_db.name)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                data TEXT
            )
        ''')
        
        # Insert operations
        for i in range(1000):
            cursor.execute(
                "INSERT INTO users (name, data) VALUES (?, ?)",
                (f"User_{i}", f"Data_{i}" * 100)
            )
        
        conn.commit()
        
        # Select operations
        for i in range(100):
            cursor.execute("SELECT * FROM users WHERE id = ?", (i,))
            result = cursor.fetchone()
        
        # Complex query
        cursor.execute("""
            SELECT name, COUNT(*) as count 
            FROM users 
            WHERE name LIKE 'User_%' 
            GROUP BY name 
            ORDER BY count DESC 
            LIMIT 10
        """)
        results = cursor.fetchall()
        
        conn.close()
        return len(results)
        
    finally:
        os.unlink(temp_db.name)

async def main():
    """Ana profiling test fonksiyonu"""
    profiler = GAVATCorePerformanceProfiler()
    
    print("\n🔍 GAVATCore Performance Profiling Başlatılıyor...")
    print("=" * 60)
    
    # Test scenarios
    test_scenarios = [
        ("Behavioral Analysis", simulate_behavioral_analysis),
        ("Cache Operations", simulate_cache_operations),
        ("Database Operations", simulate_database_operations)
    ]
    
    for scenario_name, test_func in test_scenarios:
        print(f"\n📊 Profiling: {scenario_name}")
        print("-" * 40)
        
        session = ProfilingSession(session_name=scenario_name)
        
        # Profiling yap
        start_time = time.time()
        result = profiler.profile_function(test_func)
        end_time = time.time()
        
        session.total_execution_time = end_time - start_time
        session.end_time = datetime.now()
        
        # Bottleneck analizi
        bottlenecks = profiler.analyze_bottlenecks(min_percentage=0.5)
        session.bottlenecks = bottlenecks
        
        # Optimization recommendations
        recommendations = profiler.generate_optimization_recommendations(bottlenecks)
        session.optimization_recommendations = recommendations
        
        # Sonuçları göster
        print(f"✅ Execution Time: {session.total_execution_time:.4f}s")
        print(f"🔍 Bottlenecks Found: {len(bottlenecks)}")
        
        if bottlenecks:
            print(f"\n🚨 Top 5 Bottlenecks:")
            for i, bottleneck in enumerate(bottlenecks[:5], 1):
                print(f"   {i}. {bottleneck.function_name}")
                print(f"      CPU: {bottleneck.percentage_of_total:.2f}% | "
                      f"Calls: {bottleneck.call_count} | "
                      f"Per Call: {bottleneck.per_call_time:.6f}s")
        
        if recommendations:
            print(f"\n💡 Optimization Recommendations:")
            for rec in recommendations[:3]:
                print(f"   • {rec}")
        
        # Raporu kaydet
        report_file = profiler.save_profiling_report(session)
        profiler.profiling_sessions.append(session)
        
        # Profiler'ı reset et
        profiler.profiler = cProfile.Profile()
    
    # Overall summary
    total_bottlenecks = sum(len(s.bottlenecks) for s in profiler.profiling_sessions)
    critical_bottlenecks = sum(
        len([b for b in s.bottlenecks if b.is_critical]) 
        for s in profiler.profiling_sessions
    )
    
    print(f"\n🎯 PROFILING SUMMARY")
    print("=" * 30)
    print(f"Total Scenarios: {len(profiler.profiling_sessions)}")
    print(f"Total Bottlenecks: {total_bottlenecks}")
    print(f"Critical Issues: {critical_bottlenecks}")
    
    if critical_bottlenecks > 0:
        print(f"\n⚠️ {critical_bottlenecks} kritik performans sorunu tespit edildi!")
        print("Optimizasyon önerileri için raporları inceleyin.")
    else:
        print(f"\n✅ Kritik performans sorunu tespit edilmedi.")
    
    print(f"\n📄 Detaylı raporlar kaydedildi.")

if __name__ == "__main__":
    asyncio.run(main())