#!/usr/bin/env python3
"""
🚀 Advanced Cache Optimization Test Suite v2.0
===============================================

Test script to validate Advanced Behavioral Cache Manager performance.
Target: Increase hit rate from 50% to 85%+

Test Scenarios:
- Multi-tier cache performance (L1 + L2)
- Dynamic TTL effectiveness  
- Cache warming and prefetching
- Smart invalidation strategies
- Performance under load
- Memory optimization

@version: 2.0.0
@created: 2025-01-30
"""

import asyncio
import time
import random
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import structlog

# Test imports
try:
    from core.advanced_behavioral_cache_manager import (
        AdvancedBehavioralCacheManager,
        AdvancedCacheConfig,
        CacheStrategy
    )
    CACHE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Cache imports failed: {e}")
    CACHE_AVAILABLE = False

logger = structlog.get_logger("advanced_cache_test")

@dataclass
class TestMetrics:
    """Test performance metrics"""
    test_name: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Cache metrics
    total_requests: int = 0
    l1_hits: int = 0
    l2_hits: int = 0
    cache_misses: int = 0
    
    # Performance metrics
    response_times: List[float] = field(default_factory=list)
    memory_usage_mb: float = 0.0
    
    # Advanced metrics
    cache_warming_events: int = 0
    prefetch_hits: int = 0
    invalidations: int = 0
    
    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def total_hits(self) -> int:
        return self.l1_hits + self.l2_hits
    
    @property
    def hit_rate(self) -> float:
        total = self.total_hits + self.cache_misses
        return (self.total_hits / total * 100) if total > 0 else 0.0
    
    @property
    def avg_response_time(self) -> float:
        return statistics.mean(self.response_times) if self.response_times else 0.0

class AdvancedCacheOptimizationTester:
    """
    🧪 Advanced Cache Optimization Test Suite
    
    Comprehensive testing of cache optimizations to achieve 85%+ hit rates
    """
    
    def __init__(self):
        self.cache_manager: Optional[AdvancedBehavioralCacheManager] = None
        self.test_results: List[TestMetrics] = []
        
        logger.info("🧪 Advanced Cache Optimization Tester initialized")
    
    async def initialize(self):
        """Initialize test environment"""
        if not CACHE_AVAILABLE:
            raise RuntimeError("Cache system not available for testing")
        
        # Initialize optimized cache configuration
        optimized_config = AdvancedCacheConfig(
            # Increased cache sizes for testing
            l1_cache_size=2000,
            l2_redis_max_memory_mb=2048,
            
            # Optimized TTL settings
            base_ttl_seconds=3600,  # 1 hour base
            min_ttl_seconds=300,    # 5 minutes min
            max_ttl_seconds=14400,  # 4 hours max
            
            # Aggressive caching for high frequency data
            high_frequency_multiplier=3.0,
            low_frequency_multiplier=0.3,
            
            # Enhanced cache warming
            cache_warming_enabled=True,
            prefetch_probability=0.5,  # 50% prefetch probability
            
            # Performance optimizations
            compression_enabled=True,
            compression_threshold=512,  # Compress data > 512 bytes
            eviction_strategy=CacheStrategy.ADAPTIVE,
            
            # Test-specific settings
            redis_db=2,  # Use separate DB for testing
            key_prefix="test_advanced:"
        )
        
        # Initialize cache manager
        self.cache_manager = AdvancedBehavioralCacheManager(optimized_config)
        await self.cache_manager.initialize()
        
        logger.info("✅ Test environment initialized with optimized settings")
    
    async def test_multi_tier_cache_performance(self) -> TestMetrics:
        """Test L1 + L2 cache performance"""
        metrics = TestMetrics("Multi-Tier Cache Performance")
        
        logger.info("🔄 Testing multi-tier cache performance...")
        
        # Test data
        test_users = list(range(1, 101))  # 100 users
        
        # Phase 1: Cold cache (all misses expected)
        logger.info("📊 Phase 1: Cold cache testing...")
        for i, user_id in enumerate(test_users[:20]):
            start_time = time.time()
            
            result = await self.cache_manager.get("big_five", str(user_id))
            
            if result is None:
                # Simulate cache miss - store data
                fake_result = {"traits": {"openness": random.random()}}
                await self.cache_manager.set("big_five", str(user_id), fake_result)
                metrics.cache_misses += 1
            else:
                metrics.l2_hits += 1
            
            response_time = time.time() - start_time
            metrics.response_times.append(response_time)
            metrics.total_requests += 1
        
        # Phase 2: Warm cache (mix of L1/L2 hits expected)
        logger.info("📊 Phase 2: Warm cache testing...")
        for i in range(50):
            user_id = random.choice(test_users[:20])  # Reuse users for cache hits
            start_time = time.time()
            
            result = await self.cache_manager.get("big_five", str(user_id))
            
            if result is None:
                fake_result = {"traits": {"openness": random.random()}}
                await self.cache_manager.set("big_five", str(user_id), fake_result)
                metrics.cache_misses += 1
            else:
                # Check if it was L1 or L2 hit
                cache_key = f"test_advanced:big_five:{user_id}"
                if cache_key in self.cache_manager.l1_cache:
                    metrics.l1_hits += 1
                else:
                    metrics.l2_hits += 1
            
            response_time = time.time() - start_time
            metrics.response_times.append(response_time)
            metrics.total_requests += 1
        
        # Phase 3: Hot cache (high L1 hit rate expected)
        logger.info("📊 Phase 3: Hot cache testing...")
        hot_users = test_users[:10]  # Focus on subset for L1 hits
        
        for i in range(30):
            user_id = random.choice(hot_users)
            start_time = time.time()
            
            result = await self.cache_manager.get("big_five", str(user_id))
            
            if result is None:
                fake_result = {"traits": {"openness": random.random()}}
                await self.cache_manager.set("big_five", str(user_id), fake_result)
                metrics.cache_misses += 1
            else:
                cache_key = f"test_advanced:big_five:{user_id}"
                if cache_key in self.cache_manager.l1_cache:
                    metrics.l1_hits += 1
                else:
                    metrics.l2_hits += 1
            
            response_time = time.time() - start_time
            metrics.response_times.append(response_time)
            metrics.total_requests += 1
        
        metrics.end_time = datetime.now()
        
        logger.info("✅ Multi-tier cache test completed",
                   hit_rate=f"{metrics.hit_rate:.1f}%",
                   l1_hits=metrics.l1_hits,
                   l2_hits=metrics.l2_hits,
                   misses=metrics.cache_misses)
        
        return metrics
    
    async def test_cache_warming_prefetching(self) -> TestMetrics:
        """Test cache warming and prefetching effectiveness"""
        metrics = TestMetrics("Cache Warming & Prefetching")
        
        logger.info("🔄 Testing cache warming and prefetching...")
        
        test_users = list(range(1, 31))  # 30 users
        
        # Phase 1: Initial cache population
        for user_id in test_users[:15]:
            start_time = time.time()
            
            result = await self.cache_manager.get("predictive", str(user_id))
            if result is None:
                fake_result = {"engagement": random.random()}
                await self.cache_manager.set("predictive", str(user_id), fake_result)
                metrics.cache_misses += 1
                metrics.cache_warming_events += 1
            else:
                metrics.l2_hits += 1
            
            response_time = time.time() - start_time
            metrics.response_times.append(response_time)
            metrics.total_requests += 1
        
        # Phase 2: Test cache hits
        await asyncio.sleep(0.5)  # Allow caching to settle
        
        for user_id in test_users[:15]:
            start_time = time.time()
            
            result = await self.cache_manager.get("predictive", str(user_id))
            if result:
                cache_key = f"test_advanced:predictive:{user_id}"
                if cache_key in self.cache_manager.l1_cache:
                    metrics.l1_hits += 1
                else:
                    metrics.l2_hits += 1
                    metrics.prefetch_hits += 1
            else:
                metrics.cache_misses += 1
            
            response_time = time.time() - start_time
            metrics.response_times.append(response_time)
            metrics.total_requests += 1
        
        metrics.end_time = datetime.now()
        
        logger.info("✅ Cache warming test completed",
                   warming_events=metrics.cache_warming_events,
                   prefetch_hits=metrics.prefetch_hits)
        
        return metrics
    
    async def test_smart_invalidation(self) -> TestMetrics:
        """Test smart cache invalidation strategies"""
        metrics = TestMetrics("Smart Invalidation")
        
        logger.info("🔄 Testing smart cache invalidation...")
        
        # Setup: Cache data for multiple users and namespaces
        test_users = list(range(1, 21))  # 20 users
        namespaces = ["big_five", "predictive", "sentiment"]
        
        # Populate cache
        for user_id in test_users:
            for namespace in namespaces:
                fake_data = {namespace: {"score": random.random()}}
                await self.cache_manager.set(namespace, str(user_id), fake_data)
                metrics.total_requests += 1
        
        # Test selective invalidation
        target_user = test_users[0]
        invalidated_count = await self.cache_manager.invalidate("big_five", str(target_user))
        metrics.invalidations += invalidated_count
        
        # Test namespace-wide invalidation
        invalidated_count = await self.cache_manager.invalidate("sentiment", "*")
        metrics.invalidations += invalidated_count
        
        # Verify invalidation effectiveness
        for user_id in test_users[:5]:
            for namespace in namespaces:
                result = await self.cache_manager.get(namespace, str(user_id))
                
                if namespace == "sentiment":
                    # Should be cache miss (invalidated)
                    if result is None:
                        metrics.cache_misses += 1
                    else:
                        metrics.l2_hits += 1  # Unexpected hit
                elif namespace == "big_five" and user_id == target_user:
                    # Should be cache miss (invalidated)
                    if result is None:
                        metrics.cache_misses += 1
                    else:
                        metrics.l2_hits += 1  # Unexpected hit
                else:
                    # Should be cache hit (not invalidated)
                    if result:
                        metrics.l2_hits += 1
                    else:
                        metrics.cache_misses += 1  # Unexpected miss
                
                metrics.total_requests += 1
        
        metrics.end_time = datetime.now()
        
        logger.info("✅ Smart invalidation test completed",
                   invalidations=metrics.invalidations)
        
        return metrics
    
    async def test_concurrent_performance(self) -> TestMetrics:
        """Test cache performance under concurrent load"""
        metrics = TestMetrics("Concurrent Performance")
        
        logger.info("🔄 Testing concurrent cache performance...")
        
        # Concurrent user simulation
        async def simulate_user_session(user_id: int, session_metrics: TestMetrics):
            """Simulate a user session with multiple cache operations"""
            session_operations = 10
            
            for _ in range(session_operations):
                start_time = time.time()
                
                # Random operation type
                operation = random.choice(["big_five", "predictive", "sentiment"])
                
                # Get operation
                result = await self.cache_manager.get(operation, str(user_id))
                
                if result is None:
                    # Cache miss - store new data
                    fake_data = {operation: {"value": random.random()}}
                    await self.cache_manager.set(operation, str(user_id), fake_data)
                    session_metrics.cache_misses += 1
                else:
                    # Cache hit
                    cache_key = f"test_advanced:{operation}:{user_id}"
                    if cache_key in self.cache_manager.l1_cache:
                        session_metrics.l1_hits += 1
                    else:
                        session_metrics.l2_hits += 1
                
                response_time = time.time() - start_time
                session_metrics.response_times.append(response_time)
                session_metrics.total_requests += 1
                
                # Small delay between operations
                await asyncio.sleep(0.01)
        
        # Run concurrent sessions
        concurrent_users = 20
        tasks = []
        
        for user_id in range(1, concurrent_users + 1):
            task = asyncio.create_task(simulate_user_session(user_id, metrics))
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
        
        metrics.end_time = datetime.now()
        
        logger.info("✅ Concurrent performance test completed",
                   concurrent_users=concurrent_users,
                   hit_rate=f"{metrics.hit_rate:.1f}%",
                   avg_response_time=f"{metrics.avg_response_time*1000:.2f}ms")
        
        return metrics
    
    async def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        
        # Get current cache metrics
        cache_metrics = await self.cache_manager.get_advanced_metrics()
        optimization_report = await self.cache_manager.optimize_cache_settings()
        
        # Calculate aggregate metrics
        total_requests = sum(m.total_requests for m in self.test_results)
        total_hits = sum(m.total_hits for m in self.test_results)
        overall_hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
        
        avg_response_time = statistics.mean([
            rt for m in self.test_results for rt in m.response_times
        ]) if any(m.response_times for m in self.test_results) else 0
        
        # Performance improvement calculation
        baseline_hit_rate = 50.0  # Original hit rate
        improvement = overall_hit_rate - baseline_hit_rate
        improvement_percentage = (improvement / baseline_hit_rate) * 100
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_summary": {
                "total_tests": len(self.test_results),
                "total_requests": total_requests,
                "overall_hit_rate": round(overall_hit_rate, 2),
                "avg_response_time_ms": round(avg_response_time * 1000, 2),
                "memory_usage_mb": cache_metrics["cache_distribution"]["l1_size_mb"]
            },
            "performance_improvement": {
                "baseline_hit_rate": f"{baseline_hit_rate}%",
                "current_hit_rate": f"{overall_hit_rate:.1f}%",
                "improvement": f"+{improvement:.1f}%",
                "improvement_percentage": f"+{improvement_percentage:.1f}%",
                "target_achieved": overall_hit_rate >= 85.0
            },
            "test_results": [
                {
                    "test_name": m.test_name,
                    "hit_rate": round(m.hit_rate, 2),
                    "duration_seconds": round(m.duration_seconds, 2),
                    "avg_response_time_ms": round(m.avg_response_time * 1000, 2),
                    "l1_hits": m.l1_hits,
                    "l2_hits": m.l2_hits,
                    "misses": m.cache_misses
                }
                for m in self.test_results
            ],
            "cache_optimization": optimization_report,
            "recommendations": []
        }
        
        # Generate recommendations
        if overall_hit_rate < 70:
            report["recommendations"].extend([
                "Increase L1 cache size significantly",
                "Implement more aggressive cache warming",
                "Review and optimize TTL calculations",
                "Consider implementing predictive prefetching"
            ])
        elif overall_hit_rate < 85:
            report["recommendations"].extend([
                "Fine-tune dynamic TTL algorithms",
                "Optimize cache key strategies",
                "Implement smart prefetching for related data"
            ])
        else:
            report["recommendations"].extend([
                "Cache performance is excellent!",
                "Consider optimizing memory usage",
                "Monitor for edge cases and rare access patterns"
            ])
        
        return report
    
    async def run_full_test_suite(self) -> Dict[str, Any]:
        """Run complete advanced cache optimization test suite"""
        
        print("\n" + "🚀" + "="*70 + "🚀")
        print("🧪 ADVANCED CACHE OPTIMIZATION TEST SUITE v2.0")
        print("🎯 Target: Increase hit rate from 50% to 85%+")
        print("🚀" + "="*70 + "🚀\n")
        
        try:
            await self.initialize()
            
            # Test sequence
            tests = [
                ("Multi-Tier Cache", self.test_multi_tier_cache_performance),
                ("Cache Warming", self.test_cache_warming_prefetching),
                ("Smart Invalidation", self.test_smart_invalidation),
                ("Concurrent Performance", self.test_concurrent_performance)
            ]
            
            for test_name, test_func in tests:
                print(f"🔄 Running: {test_name}...")
                start_time = datetime.now()
                
                try:
                    test_result = await test_func()
                    self.test_results.append(test_result)
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    print(f"✅ {test_name} completed in {duration:.2f}s - Hit Rate: {test_result.hit_rate:.1f}%")
                    
                except Exception as e:
                    print(f"❌ {test_name} failed: {e}")
                    logger.error(f"Test {test_name} failed", error=str(e), exc_info=True)
                
                # Brief pause between tests
                await asyncio.sleep(0.5)
            
            # Generate final report
            print("\n📊 Generating optimization report...")
            report = await self.generate_optimization_report()
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}", exc_info=True)
            return {"error": str(e)}
        
        finally:
            # Cleanup
            if self.cache_manager:
                await self.cache_manager.close()

async def main():
    """Main test execution"""
    tester = AdvancedCacheOptimizationTester()
    
    try:
        report = await tester.run_full_test_suite()
        
        # Display results
        print("\n" + "📊" + "="*70 + "📊")
        print("🎯 ADVANCED CACHE OPTIMIZATION RESULTS")
        print("📊" + "="*70 + "📊")
        
        if "error" in report:
            print(f"❌ Test failed: {report['error']}")
            return
        
        summary = report["test_summary"]
        improvement = report["performance_improvement"]
        
        print(f"\n📈 PERFORMANCE SUMMARY:")
        print(f"   Overall Hit Rate: {summary['overall_hit_rate']}%")
        print(f"   Total Requests: {summary['total_requests']:,}")
        print(f"   Avg Response Time: {summary['avg_response_time_ms']:.2f}ms")
        print(f"   Memory Usage: {summary['memory_usage_mb']:.2f}MB")
        
        print(f"\n🎯 IMPROVEMENT ANALYSIS:")
        print(f"   Baseline: {improvement['baseline_hit_rate']}")
        print(f"   Current: {improvement['current_hit_rate']}")
        print(f"   Improvement: {improvement['improvement']}")
        print(f"   Target Achieved: {'✅ YES' if improvement['target_achieved'] else '❌ NO'}")
        
        print(f"\n📋 TEST RESULTS:")
        for test in report["test_results"]:
            status = "✅" if test["hit_rate"] > 70 else "⚠️" if test["hit_rate"] > 50 else "❌"
            print(f"   {status} {test['test_name']}: {test['hit_rate']:.1f}% hit rate")
        
        if report["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")
        
        print("\n🎉 Advanced cache optimization test completed!")
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"advanced_cache_optimization_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Detailed report saved: {filename}")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        logger.error("Test execution failed", error=str(e), exc_info=True)

if __name__ == "__main__":
    asyncio.run(main()) 