#!/usr/bin/env python3
"""
BEHAVIORAL ENGINE PERFORMANCE OPTIMIZATION TEST
===============================================

Advanced Behavioral Engine v2.1 için performance ve optimization testi.
Cache hit rates, response times, memory usage ve optimization metrics.

Test Scenarios:
- Cache performance testing
- Memory usage optimization
- Response time benchmarking
- Concurrent operation testing
- Bottleneck detection

@version: 1.0.0
@created: 2025-01-30
"""

import asyncio
import time
import statistics
import concurrent.futures
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import structlog
import json

# Test framework
import pytest

# Core modules
try:
    from core.behavioral_psychological_engine import AdvancedBehavioralPsychologicalEngine
    from core.behavioral_cache_manager import BehavioralCacheManager, CacheConfig
    from core.behavioral_performance_optimizer import (
        BehavioralPerformanceOptimizer, 
        behavioral_performance_optimizer
    )
    ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Core modules not available: {e}")
    ENGINE_AVAILABLE = False

logger = structlog.get_logger("performance_test")

class BehavioralPerformanceTester:
    """
    🚀 Behavioral Engine Performance Tester
    
    Comprehensive performance testing ve optimization validation.
    """
    
    def __init__(self):
        self.engine = None
        self.cache_manager = None
        self.optimizer = behavioral_performance_optimizer
        self.test_results = {}
        self.start_time = None
        
        logger.info("🧪 Performance Tester initialized")
    
    async def setup(self):
        """Test environment setup"""
        
        if not ENGINE_AVAILABLE:
            raise RuntimeError("Required modules not available")
        
        self.start_time = datetime.now()
        
        # Initialize engine
        self.engine = AdvancedBehavioralPsychologicalEngine()
        await self.engine._initialize_cache()
        
        # Initialize cache manager
        self.cache_manager = self.engine.cache_manager
        
        # Clear any existing data
        if self.cache_manager:
            try:
                await self.cache_manager.cleanup_expired()
            except Exception:
                pass
        
        # Clear performance history
        self.optimizer.clear_performance_history()
        
        logger.info("✅ Test environment setup completed")
    
    def generate_test_messages(self, count: int, user_pattern: str = "social") -> List[str]:
        """Test mesajları oluştur"""
        
        patterns = {
            "social": [
                "Merhaba arkadaşlar! Bugün harika bir gün",
                "Yeni projemde çok heyecanlıyım, birlikte çalışalım",
                "Bu grup çok eğlenceli, herkes çok nazik",
                "Yardıma ihtiyacım var, birlikte halledebiliriz",
                "Sosyal aktiviteler organize etmeyi seviyorum"
            ],
            "analytical": [
                "Bu veriye göre analiz yapmamız gerekiyor",
                "Sistematik bir plan geliştirmeliyiz",
                "Detaylı araştırma yapmamın gereğini düşünüyorum",
                "Objektif kriterlere göre karar vermeliyiz",
                "Verimlilik ölçütlerini optimize etmeli"
            ],
            "creative": [
                "Çok yaratıcı bir fikrim var!",
                "Sanat projesi üzerinde çalışıyorum",
                "İnovasyona açığım, yeni şeyler deneyelim",
                "Farklı perspektiflerden bakmalıyız",
                "İlham verici şeyler paylaşmayı seviyorum"
            ]
        }
        
        base_messages = patterns.get(user_pattern, patterns["social"])
        
        # Extend with variations
        messages = []
        for i in range(count):
            base_msg = base_messages[i % len(base_messages)]
            variation = f"{base_msg} - Test message {i+1}"
            messages.append(variation)
        
        return messages
    
    async def test_cache_performance(self) -> Dict[str, Any]:
        """Cache performance testi"""
        
        logger.info("🗄️ Cache performance testing başlatılıyor...")
        
        test_results = {
            "cache_hit_rate": 0.0,
            "cache_response_time": 0.0,
            "cache_memory_usage": 0.0,
            "cache_operations": 0,
            "errors": []
        }
        
        try:
            # Test users
            test_users = [1001, 1002, 1003, 1004, 1005]
            cache_operations = 0
            response_times = []
            
            # Initial cache population
            for user_id in test_users:
                messages = self.generate_test_messages(20, "social")
                
                start_time = time.time()
                await self.engine.analyze_big_five_traits(messages, user_id)
                response_time = time.time() - start_time
                
                response_times.append(response_time)
                cache_operations += 1
            
            # Cache hit testing
            cache_hits = 0
            for user_id in test_users:
                messages = self.generate_test_messages(20, "social")  # Same messages
                
                start_time = time.time()
                result = await self.engine.analyze_big_five_traits(messages, user_id)
                response_time = time.time() - start_time
                
                response_times.append(response_time)
                cache_operations += 1
                
                # Cache hit olup olmadığını kontrol et
                if response_time < 0.1:  # Very fast = likely cache hit
                    cache_hits += 1
            
            # Cache stats
            if self.cache_manager:
                cache_stats = await self.cache_manager.get_cache_stats()
                test_results["cache_hit_rate"] = cache_stats.get("metrics", {}).get("hit_rate", 0.0)
            else:
                test_results["cache_hit_rate"] = (cache_hits / len(test_users)) * 100
            
            test_results["cache_response_time"] = statistics.mean(response_times)
            test_results["cache_operations"] = cache_operations
            
            logger.info(f"✅ Cache test completed: {test_results['cache_hit_rate']:.1f}% hit rate")
            
        except Exception as e:
            error_msg = f"Cache test error: {e}"
            test_results["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
        
        return test_results
    
    async def test_memory_optimization(self) -> Dict[str, Any]:
        """Memory optimization testi"""
        
        logger.info("🧠 Memory optimization testing başlatılıyor...")
        
        test_results = {
            "memory_before_mb": 0.0,
            "memory_after_mb": 0.0,
            "memory_peak_mb": 0.0,
            "gc_effectiveness": 0.0,
            "memory_leaks_detected": 0,
            "errors": []
        }
        
        try:
            # Start memory profiling
            self.optimizer.start_memory_profiling()
            
            # Initial memory
            initial_memory = self.optimizer._get_memory_usage()
            test_results["memory_before_mb"] = initial_memory
            
            # Memory intensive operations
            users_count = 50
            for i in range(users_count):
                user_id = 2000 + i
                messages = self.generate_test_messages(30, ["social", "analytical", "creative"][i % 3])
                
                # Big Five analysis
                await self.engine.analyze_big_five_traits(messages, user_id)
                
                # Comprehensive analysis
                await self.engine.comprehensive_user_analysis(user_id, messages)
                
                # Memory snapshot every 10 operations
                if i % 10 == 0:
                    self.optimizer.take_memory_snapshot(f"operation_{i}")
            
            # Peak memory
            peak_memory = self.optimizer._get_memory_usage()
            test_results["memory_peak_mb"] = peak_memory
            
            # Garbage collection optimization
            gc_result = self.optimizer.optimize_garbage_collection()
            test_results["gc_effectiveness"] = gc_result["objects_freed"]
            
            # Final memory
            final_memory = self.optimizer._get_memory_usage()
            test_results["memory_after_mb"] = final_memory
            
            # Memory analysis
            memory_analysis = self.optimizer.stop_memory_profiling()
            if memory_analysis:
                test_results["memory_leaks_detected"] = len(memory_analysis.get("leaks_detected", []))
            
            logger.info(f"✅ Memory test completed: {final_memory:.1f}MB final, {gc_result['objects_freed']} objects freed")
            
        except Exception as e:
            error_msg = f"Memory test error: {e}"
            test_results["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
        
        return test_results
    
    async def test_concurrent_operations(self) -> Dict[str, Any]:
        """Concurrent operations testi"""
        
        logger.info("⚡ Concurrent operations testing başlatılıyor...")
        
        test_results = {
            "concurrent_users": 0,
            "avg_response_time": 0.0,
            "throughput_per_second": 0.0,
            "success_rate": 0.0,
            "concurrent_errors": 0,
            "errors": []
        }
        
        try:
            concurrent_users = 20
            operations_per_user = 5
            
            async def user_simulation(user_id: int) -> Dict[str, Any]:
                """Single user simulation"""
                user_results = {
                    "user_id": user_id,
                    "operations": 0,
                    "total_time": 0.0,
                    "errors": 0
                }
                
                try:
                    for i in range(operations_per_user):
                        messages = self.generate_test_messages(15, ["social", "analytical", "creative"][i % 3])
                        
                        start_time = time.time()
                        result = await self.engine.analyze_big_five_traits(messages, user_id)
                        operation_time = time.time() - start_time
                        
                        user_results["operations"] += 1
                        user_results["total_time"] += operation_time
                        
                        # Small delay to simulate real usage
                        await asyncio.sleep(0.1)
                        
                except Exception as e:
                    user_results["errors"] += 1
                    logger.warning(f"⚠️ User {user_id} operation error: {e}")
                
                return user_results
            
            # Run concurrent simulations
            start_time = time.time()
            
            tasks = [user_simulation(3000 + i) for i in range(concurrent_users)]
            user_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            total_time = time.time() - start_time
            
            # Analyze results
            successful_results = [r for r in user_results if isinstance(r, dict) and r["errors"] == 0]
            total_operations = sum(r["operations"] for r in successful_results)
            total_errors = sum(r["errors"] for r in user_results if isinstance(r, dict))
            
            if total_operations > 0:
                avg_response_time = sum(r["total_time"] for r in successful_results) / total_operations
                throughput = total_operations / total_time
                success_rate = (len(successful_results) / concurrent_users) * 100
            else:
                avg_response_time = 0.0
                throughput = 0.0
                success_rate = 0.0
            
            test_results.update({
                "concurrent_users": concurrent_users,
                "avg_response_time": avg_response_time,
                "throughput_per_second": throughput,
                "success_rate": success_rate,
                "concurrent_errors": total_errors
            })
            
            logger.info(f"✅ Concurrent test completed: {throughput:.2f} ops/sec, {success_rate:.1f}% success")
            
        except Exception as e:
            error_msg = f"Concurrent test error: {e}"
            test_results["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
        
        return test_results
    
    async def test_bottleneck_detection(self) -> Dict[str, Any]:
        """Bottleneck detection testi"""
        
        logger.info("🔍 Bottleneck detection testing başlatılıyor...")
        
        test_results = {
            "bottlenecks_found": 0,
            "memory_hotspots": 0,
            "performance_score": 0.0,
            "optimization_suggestions": [],
            "errors": []
        }
        
        try:
            # Performance intensive operations to create bottlenecks
            for i in range(20):
                user_id = 4000 + i
                messages = self.generate_test_messages(50, "analytical")  # Longer messages
                
                # Multiple analyses
                await self.engine.analyze_big_five_traits(messages, user_id)
                await self.engine.comprehensive_user_analysis(user_id, messages)
                
                # Generate report
                if user_id in self.engine.user_profiles:
                    self.engine.generate_comprehensive_report(user_id)
            
            # Analyze bottlenecks
            optimization_report = self.optimizer.analyze_bottlenecks()
            
            test_results.update({
                "bottlenecks_found": len(optimization_report.bottlenecks),
                "memory_hotspots": len(optimization_report.memory_hotspots),
                "performance_score": optimization_report.performance_score,
                "optimization_suggestions": optimization_report.optimization_suggestions
            })
            
            logger.info(f"✅ Bottleneck test completed: {len(optimization_report.bottlenecks)} bottlenecks, score: {optimization_report.performance_score:.1f}")
            
        except Exception as e:
            error_msg = f"Bottleneck test error: {e}"
            test_results["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
        
        return test_results
    
    async def test_api_performance(self) -> Dict[str, Any]:
        """API endpoint performance testi"""
        
        logger.info("🌐 API performance testing başlatılıyor...")
        
        test_results = {
            "dashboard_response_time": 0.0,
            "user_analytics_response_time": 0.0,
            "performance_metrics_response_time": 0.0,
            "api_errors": 0,
            "errors": []
        }
        
        try:
            # Dashboard analytics
            start_time = time.time()
            dashboard_metrics = await self.engine.get_optimization_metrics()
            test_results["dashboard_response_time"] = time.time() - start_time
            
            # User analytics (test bir kullanıcı için)
            if self.engine.user_profiles:
                test_user_id = list(self.engine.user_profiles.keys())[0]
                
                start_time = time.time()
                user_report = self.engine.generate_comprehensive_report(test_user_id)
                test_results["user_analytics_response_time"] = time.time() - start_time
            
            # Performance metrics
            start_time = time.time()
            system_metrics = self.optimizer.get_system_metrics()
            test_results["performance_metrics_response_time"] = time.time() - start_time
            
            logger.info("✅ API performance test completed")
            
        except Exception as e:
            error_msg = f"API test error: {e}"
            test_results["errors"].append(error_msg)
            test_results["api_errors"] += 1
            logger.error(f"❌ {error_msg}")
        
        return test_results
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Comprehensive performance test suite"""
        
        logger.info("🚀 Comprehensive performance test suite başlatılıyor...")
        
        comprehensive_results = {
            "test_start_time": self.start_time.isoformat() if self.start_time else datetime.now().isoformat(),
            "test_duration_seconds": 0.0,
            "overall_score": 0.0,
            "test_results": {},
            "recommendations": [],
            "summary": {}
        }
        
        try:
            test_start = time.time()
            
            # Test sequence
            test_suite = [
                ("cache_performance", self.test_cache_performance),
                ("memory_optimization", self.test_memory_optimization),
                ("concurrent_operations", self.test_concurrent_operations),
                ("bottleneck_detection", self.test_bottleneck_detection),
                ("api_performance", self.test_api_performance)
            ]
            
            for test_name, test_func in test_suite:
                logger.info(f"🧪 Running {test_name}...")
                
                test_start_time = time.time()
                test_result = await test_func()
                test_duration = time.time() - test_start_time
                
                test_result["test_duration"] = test_duration
                comprehensive_results["test_results"][test_name] = test_result
                
                logger.info(f"✅ {test_name} completed in {test_duration:.2f}s")
            
            # Calculate overall performance score
            scores = []
            
            # Cache performance score
            cache_result = comprehensive_results["test_results"]["cache_performance"]
            cache_score = min(100, cache_result.get("cache_hit_rate", 0) + (1.0 / max(cache_result.get("cache_response_time", 1), 0.01)) * 10)
            scores.append(cache_score)
            
            # Memory optimization score
            memory_result = comprehensive_results["test_results"]["memory_optimization"]
            gc_effectiveness = memory_result.get("gc_effectiveness", 0)
            memory_score = min(100, (gc_effectiveness / 1000) * 100 + 50)  # Base score 50
            scores.append(memory_score)
            
            # Concurrent operations score
            concurrent_result = comprehensive_results["test_results"]["concurrent_operations"]
            concurrent_score = min(100, concurrent_result.get("success_rate", 0) + concurrent_result.get("throughput_per_second", 0) * 5)
            scores.append(concurrent_score)
            
            # Bottleneck detection score
            bottleneck_result = comprehensive_results["test_results"]["bottleneck_detection"]
            bottleneck_score = bottleneck_result.get("performance_score", 0)
            scores.append(bottleneck_score)
            
            # API performance score
            api_result = comprehensive_results["test_results"]["api_performance"]
            api_response_times = [
                api_result.get("dashboard_response_time", 1),
                api_result.get("user_analytics_response_time", 1),
                api_result.get("performance_metrics_response_time", 1)
            ]
            avg_api_time = statistics.mean(api_response_times)
            api_score = max(0, 100 - (avg_api_time * 50))  # Slower = lower score
            scores.append(api_score)
            
            overall_score = statistics.mean(scores)
            comprehensive_results["overall_score"] = overall_score
            
            # Generate recommendations
            recommendations = []
            
            if cache_result.get("cache_hit_rate", 0) < 70:
                recommendations.append("Cache hit rate düşük - cache TTL ayarlarını optimize edin")
            
            if memory_result.get("memory_leaks_detected", 0) > 0:
                recommendations.append("Memory leak tespit edildi - object lifecycle'ı gözden geçirin")
            
            if concurrent_result.get("success_rate", 0) < 95:
                recommendations.append("Concurrent operation başarısı düşük - async optimization gerekli")
            
            if bottleneck_score < 80:
                recommendations.append("Performance bottleneck'leri tespit edildi - code profiling yapın")
            
            if avg_api_time > 2.0:
                recommendations.append("API response time yüksek - query optimization gerekli")
            
            if overall_score < 70:
                recommendations.append("Genel performance düşük - sistem architecture gözden geçirin")
            
            comprehensive_results["recommendations"] = recommendations
            
            # Summary
            comprehensive_results["summary"] = {
                "total_tests": len(test_suite),
                "overall_performance": "Excellent" if overall_score >= 90 else "Good" if overall_score >= 70 else "Fair" if overall_score >= 50 else "Poor",
                "cache_efficiency": cache_result.get("cache_hit_rate", 0),
                "memory_health": "Healthy" if memory_result.get("memory_leaks_detected", 0) == 0 else "Issues detected",
                "concurrency_support": "Strong" if concurrent_result.get("success_rate", 0) >= 95 else "Moderate",
                "api_responsiveness": "Fast" if avg_api_time < 1.0 else "Moderate" if avg_api_time < 2.0 else "Slow"
            }
            
            # Test duration
            total_duration = time.time() - test_start
            comprehensive_results["test_duration_seconds"] = total_duration
            
            logger.info(f"🎉 Comprehensive test completed! Overall score: {overall_score:.1f}/100 ({total_duration:.1f}s)")
            
        except Exception as e:
            logger.error(f"❌ Comprehensive test error: {e}")
            comprehensive_results["error"] = str(e)
        
        return comprehensive_results
    
    def print_test_report(self, results: Dict[str, Any]):
        """Test sonuçlarını formatlanmış şekilde yazdır"""
        
        print("\n" + "🚀" + "="*70 + "🚀")
        print("   BEHAVIORAL ENGINE PERFORMANCE OPTIMIZATION REPORT")
        print("🚀" + "="*70 + "🚀")
        print()
        
        # Overview
        print("📊 OVERVIEW:")
        print(f"   Overall Score: {results.get('overall_score', 0):.1f}/100")
        print(f"   Test Duration: {results.get('test_duration_seconds', 0):.1f} seconds")
        print(f"   Performance Level: {results.get('summary', {}).get('overall_performance', 'Unknown')}")
        print()
        
        # Detailed Results
        print("📈 DETAILED RESULTS:")
        for test_name, test_result in results.get("test_results", {}).items():
            print(f"\n   🧪 {test_name.upper().replace('_', ' ')}:")
            
            if test_name == "cache_performance":
                print(f"      Cache Hit Rate: {test_result.get('cache_hit_rate', 0):.1f}%")
                print(f"      Avg Response Time: {test_result.get('cache_response_time', 0):.3f}s")
                print(f"      Cache Operations: {test_result.get('cache_operations', 0)}")
                
            elif test_name == "memory_optimization":
                print(f"      Memory Before: {test_result.get('memory_before_mb', 0):.1f}MB")
                print(f"      Memory Peak: {test_result.get('memory_peak_mb', 0):.1f}MB")
                print(f"      Memory After: {test_result.get('memory_after_mb', 0):.1f}MB")
                print(f"      GC Objects Freed: {test_result.get('gc_effectiveness', 0)}")
                print(f"      Memory Leaks: {test_result.get('memory_leaks_detected', 0)}")
                
            elif test_name == "concurrent_operations":
                print(f"      Concurrent Users: {test_result.get('concurrent_users', 0)}")
                print(f"      Success Rate: {test_result.get('success_rate', 0):.1f}%")
                print(f"      Throughput: {test_result.get('throughput_per_second', 0):.2f} ops/sec")
                print(f"      Avg Response Time: {test_result.get('avg_response_time', 0):.3f}s")
                
            elif test_name == "bottleneck_detection":
                print(f"      Bottlenecks Found: {test_result.get('bottlenecks_found', 0)}")
                print(f"      Memory Hotspots: {test_result.get('memory_hotspots', 0)}")
                print(f"      Performance Score: {test_result.get('performance_score', 0):.1f}/100")
                
            elif test_name == "api_performance":
                print(f"      Dashboard Response: {test_result.get('dashboard_response_time', 0):.3f}s")
                print(f"      User Analytics Response: {test_result.get('user_analytics_response_time', 0):.3f}s")
                print(f"      Metrics Response: {test_result.get('performance_metrics_response_time', 0):.3f}s")
            
            if test_result.get("errors"):
                print(f"      ⚠️ Errors: {len(test_result['errors'])}")
        
        # Recommendations
        recommendations = results.get("recommendations", [])
        if recommendations:
            print("\n💡 OPTIMIZATION RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        else:
            print("\n✅ NO OPTIMIZATION RECOMMENDATIONS - SYSTEM PERFORMING WELL!")
        
        # Summary
        summary = results.get("summary", {})
        print("\n📋 SUMMARY:")
        print(f"   Cache Efficiency: {summary.get('cache_efficiency', 0):.1f}%")
        print(f"   Memory Health: {summary.get('memory_health', 'Unknown')}")
        print(f"   Concurrency Support: {summary.get('concurrency_support', 'Unknown')}")
        print(f"   API Responsiveness: {summary.get('api_responsiveness', 'Unknown')}")
        
        print("\n" + "🎉" + "="*70 + "🎉")

async def main():
    """Ana test fonksiyonu"""
    
    print("🚀 Behavioral Engine Performance Optimization Test Suite")
    print("=" * 60)
    
    try:
        # Test setup
        tester = BehavioralPerformanceTester()
        await tester.setup()
        
        # Run comprehensive tests
        results = await tester.run_comprehensive_test()
        
        # Print report
        tester.print_test_report(results)
        
        # Save results to file
        results_filename = f"performance_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed results saved to: {results_filename}")
        
        # Return status code based on performance
        overall_score = results.get("overall_score", 0)
        if overall_score >= 80:
            print("\n🎉 PERFORMANCE TEST: PASSED (Excellent)")
            return 0
        elif overall_score >= 60:
            print("\n⚠️ PERFORMANCE TEST: WARNING (Needs Optimization)")
            return 1
        else:
            print("\n❌ PERFORMANCE TEST: FAILED (Critical Issues)")
            return 2
            
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        logger.error(f"Test suite error: {e}")
        return 3

if __name__ == "__main__":
    import sys
    
    # Run test suite
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 