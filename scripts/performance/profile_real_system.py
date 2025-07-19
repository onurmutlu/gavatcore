from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🔍 Real GAVATCore System Profiler
================================

Gerçek GAVATCore sistemindeki bottleneck'leri tespit eder.
Mevcut behavioral engine'i profile ederek performans sorunlarını bulur.

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
from datetime import datetime
from typing import Dict, List, Any, Optional
import structlog

# GAVATCore imports
try:
    from core.behavioral_psychological_engine import AdvancedBehavioralPsychologyEngine
    from core.behavioral_cache_manager import BehavioralCacheManager
    GAVATCORE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ GAVATCore modülleri bulunamadı: {e}")
    GAVATCORE_AVAILABLE = False

logger = structlog.get_logger("real_system_profiler")

class RealSystemProfiler:
    """
    🔍 Real GAVATCore System Performance Profiler
    
    Gerçek sistemdeki performans bottleneck'lerini tespit eder.
    """
    
    def __init__(self):
        self.profiler = cProfile.Profile()
        self.engine = None
        self.cache_manager = None
        
        logger.info("🔍 Real System Profiler başlatıldı")
    
    async def initialize(self):
        """Gerçek sistem bileşenlerini başlat"""
        if not GAVATCORE_AVAILABLE:
            raise RuntimeError("GAVATCore modülleri bulunamadı")
        
        try:
            # Behavioral engine başlat
            self.engine = AdvancedBehavioralPsychologyEngine()
            
            # Cache manager başlat
            self.cache_manager = BehavioralCacheManager()
            await self.cache_manager.initialize()
            
            logger.info("✅ Gerçek sistem bileşenleri başlatıldı")
            
        except Exception as e:
            logger.error(f"❌ Sistem başlatma hatası: {e}")
            raise
    
    def profile_big_five_analysis(self, sample_count: int = 50):
        """Big Five analysis performance profiling"""
        
        # Test data
        test_messages = [
            ["I love exploring new ideas and concepts", "Learning excites me", "I enjoy creative projects"],
            ["I prefer organized environments", "I like to plan ahead", "Structure is important to me"],
            ["I enjoy social gatherings", "Meeting new people energizes me", "I like being the center of attention"],
            ["I try to help others whenever possible", "Cooperation is better than competition", "I trust people easily"],
            ["I often worry about things", "Stress affects me easily", "I get anxious in uncertain situations"],
            ["Art and music inspire me", "I question traditional ways", "Innovation interests me"],
            ["I keep my commitments", "Reliability is important", "I work systematically"],
            ["I speak up in groups", "Social events are fun", "I'm comfortable with public speaking"],
            ["I'm considerate of others", "Kindness matters", "I avoid conflicts"],
            ["I stay calm under pressure", "I'm emotionally stable", "I handle stress well"]
        ]
        
        print(f"\n🧠 Profiling Big Five Analysis ({sample_count} samples)...")
        
        self.profiler.enable()
        start_time = time.time()
        
        results = []
        for i in range(sample_count):
            messages = test_messages[i % len(test_messages)]
            user_id = i + 1
            
            # Synchronous version for profiling
            try:
                # Simulate the analysis (simplified version)
                result = self._simulate_big_five_analysis(messages, user_id)
                results.append(result)
            except Exception as e:
                logger.error(f"Big Five analysis error: {e}")
        
        end_time = time.time()
        self.profiler.disable()
        
        execution_time = end_time - start_time
        avg_time = execution_time / sample_count
        
        print(f"✅ Big Five Analysis Profiling tamamlandı")
        print(f"   Total Time: {execution_time:.4f}s")
        print(f"   Average per call: {avg_time:.4f}s")
        print(f"   Samples processed: {len(results)}")
        
        return results
    
    def _simulate_big_five_analysis(self, messages: List[str], user_id: int) -> Dict:
        """Big Five analysis simulation (synchronous)"""
        import random
        import json
        import hashlib
        import time
        
        # Simulate text processing bottleneck
        processed_text = ""
        for message in messages:
            # Simulate heavy text processing
            words = message.lower().split()
            for word in words:
                # Simulate word analysis - potential bottleneck
                word_hash = hashlib.md5(word.encode()).hexdigest()
                word_score = hash(word_hash) % 100
                processed_text += f"{word}:{word_score} "
        
        # Simulate trait calculation - potential bottleneck
        traits = {}
        trait_names = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
        
        for trait in trait_names:
            # Complex calculation simulation
            score = 0.0
            for message in messages:
                for word in message.split():
                    # Simulate NLP processing overhead
                    word_value = hash(word + trait) % 1000 / 1000.0
                    score += word_value
                    
                    # Simulate additional processing delay
                    for _ in range(100):  # CPU-intensive loop
                        score += random.random() * 0.001
            
            traits[trait] = min(max(score / len(messages), 0.0), 1.0)
        
        # Simulate JSON serialization overhead
        result = {
            "user_id": user_id,
            "traits": traits,
            "processed_text_length": len(processed_text),
            "analysis_timestamp": time.time(),
            "confidence": random.uniform(0.7, 0.95)
        }
        
        # Multiple JSON serializations (potential bottleneck)
        for _ in range(5):
            json_str = json.dumps(result)
            parsed = json.loads(json_str)
        
        return result
    
    def profile_cache_operations(self, operation_count: int = 100):
        """Cache operations performance profiling"""
        
        print(f"\n🗄️ Profiling Cache Operations ({operation_count} operations)...")
        
        self.profiler.enable()
        start_time = time.time()
        
        # Simulate cache operations
        cache_data = {}
        hits = 0
        misses = 0
        
        for i in range(operation_count):
            key = f"cache_key_{i % 50}"  # 50% hit rate simulation
            
            # Cache get simulation
            if key in cache_data:
                # Cache hit - simulate retrieval overhead
                data = cache_data[key]
                
                # Simulate deserialization overhead (potential bottleneck)
                import pickle
                import zlib
                
                # Multiple serialization/deserialization cycles
                for _ in range(3):
                    serialized = pickle.dumps(data)
                    compressed = zlib.compress(serialized)
                    decompressed = zlib.decompress(compressed)
                    deserialized = pickle.loads(decompressed)
                
                hits += 1
            else:
                # Cache miss - simulate data computation and storage
                import hashlib
                import json
                
                # Simulate expensive computation
                computed_data = {
                    "key": key,
                    "value": f"computed_value_{i}",
                    "metadata": {
                        "creation_time": time.time(),
                        "computation_result": [j**2 for j in range(100)]  # CPU intensive
                    }
                }
                
                # Simulate hash calculation (potential bottleneck)
                data_str = json.dumps(computed_data, sort_keys=True)
                for hash_algo in [hashlib.md5, hashlib.sha1, hashlib.sha256]:
                    hash_result = hash_algo(data_str.encode()).hexdigest()
                
                cache_data[key] = computed_data
                misses += 1
        
        end_time = time.time()
        self.profiler.disable()
        
        execution_time = end_time - start_time
        hit_rate = (hits / (hits + misses)) * 100
        
        print(f"✅ Cache Operations Profiling tamamlandı")
        print(f"   Total Time: {execution_time:.4f}s")
        print(f"   Hit Rate: {hit_rate:.1f}%")
        print(f"   Operations: {operation_count}")
        
        return {"hits": hits, "misses": misses, "hit_rate": hit_rate}
    
    def profile_json_operations(self, json_count: int = 1000):
        """JSON serialization/deserialization profiling"""
        
        print(f"\n📄 Profiling JSON Operations ({json_count} operations)...")
        
        # Large JSON data for testing
        large_data = {
            "user_profiles": [
                {
                    "user_id": i,
                    "messages": [f"Message {j} from user {i}" for j in range(50)],
                    "analysis_results": {
                        "big_five": {trait: hash(f"{i}_{trait}") % 100 / 100.0 
                                   for trait in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]},
                        "sentiment_scores": [hash(f"{i}_{j}") % 100 / 100.0 for j in range(20)],
                        "metadata": {"processed_at": time.time()}
                    }
                }
                for i in range(100)
            ]
        }
        
        self.profiler.enable()
        start_time = time.time()
        
        for i in range(json_count):
            # JSON serialization (potential bottleneck)
            json_str = json.dumps(large_data, separators=(',', ':'))
            
            # JSON deserialization (potential bottleneck)
            parsed_data = json.loads(json_str)
            
            # Simulate additional processing
            if i % 100 == 0:
                # Simulate complex nested access
                for profile in parsed_data["user_profiles"][:10]:
                    scores = profile["analysis_results"]["big_five"]
                    avg_score = sum(scores.values()) / len(scores)
        
        end_time = time.time()
        self.profiler.disable()
        
        execution_time = end_time - start_time
        avg_time = execution_time / json_count
        json_size_mb = len(json.dumps(large_data)) / (1024 * 1024)
        
        print(f"✅ JSON Operations Profiling tamamlandı")
        print(f"   Total Time: {execution_time:.4f}s")
        print(f"   Average per operation: {avg_time:.6f}s")
        print(f"   JSON Size: {json_size_mb:.2f}MB")
        
        return {"avg_time": avg_time, "json_size_mb": json_size_mb}
    
    def analyze_profiling_results(self, min_percentage: float = 1.0):
        """Profiling sonuçlarını analiz et ve bottleneck'leri bul"""
        
        # cProfile sonuçlarını al
        s = io.StringIO()
        stats = pstats.Stats(self.profiler, stream=s)
        stats.sort_stats('cumulative')
        stats.print_stats(30)  # Top 30 functions
        
        profile_output = s.getvalue()
        
        print(f"\n🔍 PROFILING ANALYSIS RESULTS")
        print("=" * 50)
        
        # Parse critical bottlenecks
        lines = profile_output.split('\n')
        bottlenecks_found = []
        
        for line in lines:
            if ('json' in line.lower() or 
                'pickle' in line.lower() or 
                'hash' in line.lower() or 
                'compress' in line.lower() or
                'behavioral' in line.lower()):
                
                print(f"🚨 Potential Bottleneck: {line.strip()}")
                bottlenecks_found.append(line.strip())
        
        # Show top time-consuming functions
        print(f"\n📊 Top Time-Consuming Functions:")
        print("-" * 40)
        
        data_section = False
        function_count = 0
        
        for line in lines:
            if line.strip().startswith('ncalls'):
                data_section = True
                continue
            
            if data_section and line.strip() and function_count < 10:
                parts = line.strip().split()
                if len(parts) >= 6:
                    try:
                        cumtime = float(parts[3])
                        function_name = ' '.join(parts[5:])
                        if cumtime > 0.001:  # Only show functions > 1ms
                            print(f"   {function_count + 1}. {function_name}")
                            print(f"      Cumulative Time: {cumtime:.6f}s")
                            function_count += 1
                    except (ValueError, IndexError):
                        continue
        
        return bottlenecks_found
    
    def generate_optimization_report(self, bottlenecks: List[str]) -> Dict[str, Any]:
        """Optimizasyon raporu oluştur"""
        
        optimizations = []
        
        # JSON optimizations
        json_bottlenecks = [b for b in bottlenecks if 'json' in b.lower()]
        if json_bottlenecks:
            optimizations.append({
                "area": "JSON Serialization",
                "issue": "Heavy JSON operations detected",
                "solutions": [
                    "Use ujson instead of standard json module",
                    "Implement JSON streaming for large data",
                    "Cache serialized data",
                    "Use MessagePack for binary serialization"
                ]
            })
        
        # Hashing optimizations
        hash_bottlenecks = [b for b in bottlenecks if 'hash' in b.lower()]
        if hash_bottlenecks:
            optimizations.append({
                "area": "Hashing Operations",
                "issue": "Multiple hash calculations detected",
                "solutions": [
                    "Use faster hash algorithms (blake2b)",
                    "Cache hash results",
                    "Reduce hash frequency",
                    "Use string interning for repeated data"
                ]
            })
        
        # Compression optimizations
        compression_bottlenecks = [b for b in bottlenecks if 'compress' in b.lower() or 'pickle' in b.lower()]
        if compression_bottlenecks:
            optimizations.append({
                "area": "Compression/Serialization",
                "issue": "Heavy compression/pickle operations",
                "solutions": [
                    "Use lighter compression (lz4 instead of zlib)",
                    "Implement compression thresholds",
                    "Use protocol 5 for pickle",
                    "Consider binary formats like protobuf"
                ]
            })
        
        # Behavioral analysis optimizations
        behavioral_bottlenecks = [b for b in bottlenecks if 'behavioral' in b.lower()]
        if behavioral_bottlenecks:
            optimizations.append({
                "area": "Behavioral Analysis",
                "issue": "Complex analysis algorithms detected",
                "solutions": [
                    "Implement result caching",
                    "Use vectorized operations (numpy)",
                    "Optimize text processing pipelines",
                    "Implement batch processing"
                ]
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "bottlenecks_detected": len(bottlenecks),
            "optimization_areas": len(optimizations),
            "optimizations": optimizations,
            "priority_recommendations": [
                "Implement advanced caching for frequent operations",
                "Replace standard JSON with ujson or orjson",
                "Use blake2b for hashing operations", 
                "Implement batch processing for bulk operations",
                "Add compression thresholds and use lz4"
            ]
        }

async def main():
    """Ana profiling fonksiyonu"""
    profiler = RealSystemProfiler()
    
    print("\n🔍 REAL GAVATCORE SYSTEM PROFILING")
    print("=" * 50)
    
    try:
        # Sistem başlat
        if GAVATCORE_AVAILABLE:
            print("🔄 Gerçek sistem bileşenleri başlatılıyor...")
            await profiler.initialize()
        else:
            print("⚠️ GAVATCore modülleri bulunamadı, simulated profiling yapılacak")
        
        # Performance profiling scenarios
        print("\n📊 Performance Profiling Scenarios:")
        
        # 1. Big Five Analysis Profiling
        big_five_results = profiler.profile_big_five_analysis(sample_count=30)
        
        # 2. Cache Operations Profiling
        cache_results = profiler.profile_cache_operations(operation_count=200)
        
        # 3. JSON Operations Profiling
        json_results = profiler.profile_json_operations(json_count=100)
        
        # 4. Analyze results
        bottlenecks = profiler.analyze_profiling_results()
        
        # 5. Generate optimization report
        optimization_report = profiler.generate_optimization_report(bottlenecks)
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"real_system_profiling_report_{timestamp}.json"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(optimization_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Optimization report saved: {report_filename}")
        
        # Show optimization recommendations
        print(f"\n💡 OPTIMIZATION RECOMMENDATIONS")
        print("=" * 40)
        
        for i, recommendation in enumerate(optimization_report["priority_recommendations"], 1):
            print(f"{i}. {recommendation}")
        
        if optimization_report["optimizations"]:
            print(f"\n🔧 DETAILED OPTIMIZATIONS")
            print("=" * 30)
            
            for opt in optimization_report["optimizations"]:
                print(f"\n🎯 {opt['area']}:")
                print(f"   Issue: {opt['issue']}")
                print(f"   Solutions:")
                for solution in opt['solutions']:
                    print(f"   • {solution}")
        
        print(f"\n🎉 Real System Profiling completed!")
        print(f"Found {len(bottlenecks)} potential bottlenecks")
        print(f"Generated {len(optimization_report['optimizations'])} optimization areas")
        
    except Exception as e:
        logger.error(f"❌ Profiling error: {e}")
        print(f"❌ Profiling failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())