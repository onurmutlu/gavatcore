#!/usr/bin/env python3
"""
GavatCore V2 - Advanced AI Test Suite
Gelişmiş AI özelliklerini test eden kapsamlı test sistemi
"""

import asyncio
import json
import time
from datetime import datetime
import structlog

# Config ve AI sistemleri
from config import validate_config, OPENAI_API_KEY
from core.advanced_ai_manager import initialize_advanced_ai_manager, AITaskType, AIPriority
from core.ai_crm_analyzer import AICRMAnalyzer
from core.database_manager import database_manager

logger = structlog.get_logger("gavatcore.test_advanced_ai")

class AdvancedAITestSuite:
    """Gelişmiş AI Test Paketi"""
    
    def __init__(self):
        self.ai_manager = None
        self.crm_analyzer = None
        self.test_results = {}
        
    async def initialize(self):
        """Test sistemini başlat"""
        try:
            logger.info("🚀 Advanced AI Test Suite başlatılıyor...")
            
            # Config doğrula
            validate_config()
            
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY gerekli!")
            
            # AI Manager'ı başlat
            self.ai_manager = await initialize_advanced_ai_manager()
            
            # CRM Analyzer'ı başlat
            self.crm_analyzer = AICRMAnalyzer(OPENAI_API_KEY)
            
            # Database'i başlat
            await database_manager.initialize()
            
            logger.info("✅ Test sistemi başarıyla başlatıldı")
            
        except Exception as e:
            logger.error(f"❌ Test sistemi başlatma hatası: {e}")
            raise
    
    async def run_all_tests(self):
        """Tüm testleri çalıştır"""
        try:
            logger.info("🧪 Tüm AI testleri başlatılıyor...")
            
            # Test kategorileri
            test_categories = [
                ("AI Manager Tests", self.test_ai_manager),
                ("Sentiment Analysis Tests", self.test_sentiment_analysis),
                ("Personality Analysis Tests", self.test_personality_analysis),
                ("Predictive Analytics Tests", self.test_predictive_analytics),
                ("Content Optimization Tests", self.test_content_optimization),
                ("CRM Analysis Tests", self.test_crm_analysis),
                ("Real-time Processing Tests", self.test_real_time_processing),
                ("System Performance Tests", self.test_system_performance)
            ]
            
            for category_name, test_func in test_categories:
                logger.info(f"📋 {category_name} başlatılıyor...")
                start_time = time.time()
                
                try:
                    result = await test_func()
                    duration = time.time() - start_time
                    
                    self.test_results[category_name] = {
                        "status": "success",
                        "duration": duration,
                        "result": result
                    }
                    
                    logger.info(f"✅ {category_name} tamamlandı ({duration:.2f}s)")
                    
                except Exception as e:
                    duration = time.time() - start_time
                    
                    self.test_results[category_name] = {
                        "status": "error",
                        "duration": duration,
                        "error": str(e)
                    }
                    
                    logger.error(f"❌ {category_name} hatası ({duration:.2f}s): {e}")
            
            # Sonuçları raporla
            await self.generate_test_report()
            
        except Exception as e:
            logger.error(f"❌ Test suite hatası: {e}")
    
    async def test_ai_manager(self):
        """AI Manager temel testleri"""
        results = {}
        
        # 1. System Analytics Test
        analytics = await self.ai_manager.get_system_analytics()
        results["system_analytics"] = analytics
        
        # 2. Task Submission Test
        task_id = await self.ai_manager.submit_ai_task(
            task_type=AITaskType.CONTENT_GENERATION,
            user_id="test_user_001",
            prompt="Merhaba dünya için kısa bir mesaj oluştur",
            priority=AIPriority.HIGH
        )
        
        results["task_submission"] = {"task_id": task_id, "success": bool(task_id)}
        
        # 3. Task Result Test
        if task_id:
            task_result = await self.ai_manager.get_task_result(task_id, wait_timeout=15.0)
            results["task_result"] = task_result
        
        return results
    
    async def test_sentiment_analysis(self):
        """Duygu analizi testleri"""
        results = {}
        
        test_texts = [
            "Bugün çok mutluyum! Harika bir gün geçiriyorum.",
            "Üzgünüm, işler pek iyi gitmiyor.",
            "Bu konuda kararsızım, ne yapacağımı bilmiyorum.",
            "Çok sinirliyim! Bu kabul edilemez!",
            "Merhaba, nasılsın? İyi misin?"
        ]
        
        for i, text in enumerate(test_texts):
            sentiment_result = await self.ai_manager.analyze_real_time_sentiment(
                user_id=f"test_user_{i:03d}",
                text=text,
                context={"test_case": f"sentiment_test_{i}"}
            )
            
            results[f"test_case_{i}"] = {
                "input_text": text,
                "sentiment_result": sentiment_result
            }
        
        return results
    
    async def test_personality_analysis(self):
        """Kişilik analizi testleri"""
        results = {}
        
        # Test kullanıcı verileri
        test_user_data = {
            "user_id": "test_personality_001",
            "interactions": [
                {"type": "message", "content": "Merhaba, yeni özellikler hakkında bilgi alabilir miyim?", "timestamp": "2024-01-01T10:00:00"},
                {"type": "voice", "duration": 45, "content": "Sesli mesaj testi", "timestamp": "2024-01-01T11:00:00"},
                {"type": "quest_completion", "quest_id": "daily_challenge", "score": 85, "timestamp": "2024-01-01T12:00:00"}
            ],
            "preferences": {
                "communication_style": "formal",
                "activity_level": "high",
                "social_engagement": "medium"
            },
            "behavioral_patterns": {
                "active_hours": ["09:00-12:00", "14:00-17:00"],
                "response_time": "fast",
                "engagement_quality": "high"
            }
        }
        
        personality_result = await self.ai_manager.analyze_personality(
            user_id="test_personality_001",
            user_data=test_user_data
        )
        
        results["personality_analysis"] = personality_result
        
        return results
    
    async def test_predictive_analytics(self):
        """Tahmin analizi testleri"""
        results = {}
        
        # Test kullanıcı geçmişi
        test_user_history = {
            "user_id": "test_predictive_001",
            "activity_history": [
                {"date": "2024-01-01", "sessions": 3, "duration": 120, "engagement_score": 85},
                {"date": "2024-01-02", "sessions": 2, "duration": 90, "engagement_score": 75},
                {"date": "2024-01-03", "sessions": 4, "duration": 150, "engagement_score": 90},
                {"date": "2024-01-04", "sessions": 1, "duration": 30, "engagement_score": 60},
                {"date": "2024-01-05", "sessions": 0, "duration": 0, "engagement_score": 0}
            ],
            "feature_usage": {
                "voice_chat": 15,
                "text_chat": 45,
                "quests": 8,
                "social_events": 3
            },
            "character_interactions": {
                "geisha": 25,
                "babagavat": 18,
                "ai_assistant": 12
            }
        }
        
        prediction_result = await self.ai_manager.predict_user_behavior(
            user_id="test_predictive_001",
            user_history=test_user_history
        )
        
        results["behavior_prediction"] = prediction_result
        
        return results
    
    async def test_content_optimization(self):
        """İçerik optimizasyon testleri"""
        results = {}
        
        # Test kullanıcı profili
        test_user_profile = {
            "user_id": "test_content_001",
            "demographics": {
                "age_group": "25-35",
                "interests": ["technology", "gaming", "ai"],
                "activity_level": "high"
            },
            "engagement_patterns": {
                "preferred_content_length": "medium",
                "best_engagement_times": ["10:00-12:00", "20:00-22:00"],
                "response_rate": 0.85,
                "completion_rate": 0.75
            }
        }
        
        test_content_history = {
            "recent_content": [
                {"type": "quest", "engagement": 90, "completion": True, "feedback": "positive"},
                {"type": "voice_message", "engagement": 85, "completion": True, "feedback": "positive"},
                {"type": "text_message", "engagement": 70, "completion": True, "feedback": "neutral"},
                {"type": "social_event", "engagement": 95, "completion": True, "feedback": "very_positive"}
            ],
            "preferences": {
                "content_types": ["interactive", "voice", "gamified"],
                "topics": ["ai_features", "community_events", "personal_growth"]
            }
        }
        
        optimization_result = await self.ai_manager.optimize_content_strategy(
            user_id="test_content_001",
            user_profile=test_user_profile,
            content_history=test_content_history
        )
        
        results["content_optimization"] = optimization_result
        
        return results
    
    async def test_crm_analysis(self):
        """CRM analizi testleri"""
        results = {}
        
        # 1. User Segmentation Test
        segmentation_result = await self.crm_analyzer.analyze_user_segmentation(limit=50)
        results["user_segmentation"] = segmentation_result
        
        # 2. Broadcast Optimization Test
        broadcast_result = await self.crm_analyzer.analyze_broadcast_optimization()
        results["broadcast_optimization"] = broadcast_result
        
        return results
    
    async def test_real_time_processing(self):
        """Gerçek zamanlı işleme testleri"""
        results = {}
        
        # Paralel görev gönderimi
        tasks = []
        for i in range(5):
            task_id = await self.ai_manager.submit_ai_task(
                task_type=AITaskType.SENTIMENT_ANALYSIS,
                user_id=f"realtime_user_{i:03d}",
                prompt=f"Test mesajı {i}: Bu bir gerçek zamanlı test mesajıdır.",
                priority=AIPriority.REAL_TIME
            )
            tasks.append(task_id)
        
        # Sonuçları bekle
        task_results = []
        for task_id in tasks:
            if task_id:
                result = await self.ai_manager.get_task_result(task_id, wait_timeout=10.0)
                task_results.append({"task_id": task_id, "result": result})
        
        results["parallel_processing"] = task_results
        
        return results
    
    async def test_system_performance(self):
        """Sistem performans testleri"""
        results = {}
        
        # 1. System Analytics
        analytics = await self.ai_manager.get_system_analytics()
        results["system_analytics"] = analytics
        
        # 2. Database Performance
        db_start = time.time()
        users = await database_manager.get_users_for_ai_analysis(100)
        db_duration = time.time() - db_start
        
        results["database_performance"] = {
            "query_duration": db_duration,
            "user_count": len(users) if users else 0
        }
        
        # 3. Memory Usage (basit)
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        results["memory_usage"] = {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024
        }
        
        return results
    
    async def generate_test_report(self):
        """Test raporu oluştur"""
        try:
            report = {
                "test_summary": {
                    "total_tests": len(self.test_results),
                    "successful_tests": len([r for r in self.test_results.values() if r["status"] == "success"]),
                    "failed_tests": len([r for r in self.test_results.values() if r["status"] == "error"]),
                    "total_duration": sum(r["duration"] for r in self.test_results.values()),
                    "timestamp": datetime.now().isoformat()
                },
                "test_results": self.test_results,
                "system_info": {
                    "openai_api_available": bool(OPENAI_API_KEY),
                    "ai_features_enabled": await self.ai_manager.get_system_analytics() if self.ai_manager else {}
                }
            }
            
            # Raporu dosyaya kaydet
            report_filename = f"advanced_ai_test_report_{int(time.time())}.json"
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            # Özet yazdır
            print("\n" + "="*80)
            print("🧪 ADVANCED AI TEST SUITE RAPORU")
            print("="*80)
            print(f"📊 Toplam Test: {report['test_summary']['total_tests']}")
            print(f"✅ Başarılı: {report['test_summary']['successful_tests']}")
            print(f"❌ Başarısız: {report['test_summary']['failed_tests']}")
            print(f"⏱️ Toplam Süre: {report['test_summary']['total_duration']:.2f} saniye")
            print(f"📄 Rapor: {report_filename}")
            print("="*80)
            
            # Detaylı sonuçlar
            for test_name, result in self.test_results.items():
                status_icon = "✅" if result["status"] == "success" else "❌"
                print(f"{status_icon} {test_name}: {result['duration']:.2f}s")
                
                if result["status"] == "error":
                    print(f"   Hata: {result['error']}")
            
            print("\n🎉 Test suite tamamlandı!")
            
        except Exception as e:
            logger.error(f"❌ Test raporu oluşturma hatası: {e}")

async def main():
    """Ana test fonksiyonu"""
    try:
        # Test suite'i başlat
        test_suite = AdvancedAITestSuite()
        await test_suite.initialize()
        
        # Tüm testleri çalıştır
        await test_suite.run_all_tests()
        
    except Exception as e:
        logger.error(f"❌ Test suite ana hatası: {e}")
        print(f"\n❌ Test suite hatası: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 