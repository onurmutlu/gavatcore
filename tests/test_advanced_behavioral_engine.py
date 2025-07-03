#!/usr/bin/env python3
"""
ADVANCED BEHAVIORAL ENGINE v2.0 TEST SUITE
==========================================

Gelişmiş davranışsal analiz motoru için kapsamlı test sistemi.

Test Edilenler:
- Big Five Personality Traits (OCEAN)
- Mesaj zamanlama kalıpları  
- Sentiment trend analizi
- Grup sosyal dinamikleri
- Motivasyon faktörleri
- Predictive analytics
- Kapsamlı raporlama

@version: 2.0.0
@created: 2025-01-30
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import structlog

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.behavioral_psychological_engine import (
    BehavioralPsychologicalEngine,
    AdvancedBehavioralPsychologicalEngine,
    BigFiveTraits,
    PersonalityType,
    SocialRole,
    MotivationType
)

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("behavioral_test_v2")

class AdvancedBehavioralEngineTestSuite:
    """Gelişmiş behavioral engine test suite"""
    
    def __init__(self):
        self.engine = AdvancedBehavioralPsychologicalEngine()
        self.test_results = {}
        
    def create_test_users(self) -> Dict[str, Dict]:
        """Gelişmiş test kullanıcıları oluştur"""
        
        # Realistic message timestamps for timing analysis
        now = datetime.now()
        
        return {
            "high_achiever_ali": {
                "user_id": 1001,
                "messages": [
                    "Bugün yeni bir proje başlattım, çok heyecanlıyım!",
                    "Hedeflerimi belirledim ve plan yapıyorum",
                    "Başarı için çok çalışmak gerekiyor",
                    "Yarışmaya katılıp kazanmak istiyorum",
                    "Her gün kendimi geliştirmeye odaklanıyorum",
                    "Liderlik becerilerimi artırmak için kurs alıyorum",
                    "Ekip arkadaşlarımla birlikte büyük işler yapacağız",
                    "Yeni teknolojileri öğrenmeyi seviyorum",
                    "Girişimcilik hayalim var",
                    "Performansımı sürekli analiz ediyorum"
                ],
                "timestamps": [
                    now - timedelta(days=i, hours=9) for i in range(10)  # Morning person
                ],
                "group_messages": [
                    {"user_id": 1001, "text": "Bu projeyi organize edelim arkadaşlar"},
                    {"user_id": 1002, "text": "Güzel fikir"},
                    {"user_id": 1001, "text": "Plan yapalım, kim hangi görevi alacak?"},
                    {"user_id": 1003, "text": "Ben tasarım kısmını alabilirim"},
                    {"user_id": 1001, "text": "Mükemmel! Bir program hazırlayıp paylaşırım"},
                    {"user_id": 1002, "text": "Ali her zaman iyi organize eder"},
                    {"user_id": 1001, "text": "Beraber başaracağız bu işi!"}
                ]
            },
            
            "social_butterfly_selin": {
                "user_id": 1002, 
                "messages": [
                    "Arkadaşlarımla çok güzel vakit geçirdim!",
                    "Yeni insanlarla tanışmayı çok seviyorum",
                    "Bugün çok eğlenceli bir etkinlik vardı",
                    "Sosyal medyada yeni arkadaşlar edindim",
                    "Grup aktivitelerine katılmak harika",
                    "Herkesle iyi geçinmeye çalışıyorum",
                    "Beraber yapılan işler daha keyifli oluyor",
                    "Paylaşımcı olmayı seviyorum",
                    "Toplumsal sorumluluk projelerine katılıyorum",
                    "İnsanların mutluluğu beni mutlu ediyor"
                ],
                "timestamps": [
                    now - timedelta(days=i, hours=14) for i in range(10)  # Afternoon person
                ],
                "group_messages": [
                    {"user_id": 1002, "text": "Herkese merhaba! Bugün nasılsınız?"},
                    {"user_id": 1001, "text": "İyiyiz Selin, sen nasılsın?"},
                    {"user_id": 1002, "text": "Süper! Yeni bir cafe keşfettim, beraber gidelim"},
                    {"user_id": 1003, "text": "Harika fikir!"},
                    {"user_id": 1002, "text": "Grupça çıkmak çok eğlenceli oluyor"},
                    {"user_id": 1001, "text": "Sen hep böyle sosyal etkinlikler organizasyonu"},
                    {"user_id": 1002, "text": "Beraber olmak güzel! 😊"}
                ]
            },
            
            "creative_artist_mehmet": {
                "user_id": 1003,
                "messages": [
                    "Yeni bir sanat eseri üzerinde çalışıyorum",
                    "Yaratıcılık benim tutkum",
                    "Farklı tarzlar denemeyi seviyorum", 
                    "İlham veren şeyler arıyorum sürekli",
                    "Sanatla hayatı güzelleştirmek istiyorum",
                    "Özgün işler çıkarmaya odaklanıyorum",
                    "Renk kombinasyonları ile deneyler yapıyorum",
                    "Müzik dinlerken daha yaratıcı oluyorum",
                    "Doğadan çok ilham alıyorum",
                    "Her gün yeni bir şey öğrenmeye çalışıyorum"
                ],
                "timestamps": [
                    now - timedelta(days=i, hours=22) for i in range(10)  # Night owl
                ],
                "group_messages": [
                    {"user_id": 1003, "text": "Bu proje için yaratıcı bir tasarım yapabilirim"},
                    {"user_id": 1001, "text": "Harika! Senin tasarım becerin çok iyi"},
                    {"user_id": 1003, "text": "Farklı bakış açıları deneyelim"},
                    {"user_id": 1002, "text": "Mehmet'in fikirleri hep ilginç oluyor"},
                    {"user_id": 1003, "text": "Rengarenk bir şey yapalım!"},
                    {"user_id": 1001, "text": "Özgünlük senin alanın"}
                ]
            },
            
            "analytical_engineer_ayse": {
                "user_id": 1004,
                "messages": [
                    "Veriyi analiz etmeyi çok seviyorum",
                    "Her şeyin mantıklı bir açıklaması vardır", 
                    "Sistematik yaklaşım önemli",
                    "Detayları gözden kaçırmam",
                    "Problem çözme becerimi geliştiriyorum",
                    "Teknoloji ile hayatı kolaylaştırmak istiyorum",
                    "Algoritmaları incelemeyi seviyorum",
                    "Verimlilik benim önceliğim",
                    "Süreçleri optimize etmeye odaklanıyorum",
                    "Kanıta dayalı kararlar almayı tercih ederim"
                ],
                "timestamps": [
                    now - timedelta(days=i, hours=10) for i in range(10)  # Consistent schedule
                ],
                "group_messages": [
                    {"user_id": 1004, "text": "Bu planı daha sistematik hale getirebiliriz"},
                    {"user_id": 1001, "text": "Nasıl bir sistem öneriyorsun Ayşe?"},
                    {"user_id": 1004, "text": "Adım adım ilerleyelim, önce analiz yapalım"},
                    {"user_id": 1002, "text": "Ayşe hep düzenli yaklaşıyor"},
                    {"user_id": 1004, "text": "Etkili sonuç için detaylı planlama şart"},
                    {"user_id": 1003, "text": "Sen hep böyle mantıklı çözümler buluyorsun"}
                ]
            },
            
            "emotional_volatile_emre": {
                "user_id": 1005,
                "messages": [
                    "Bugün çok mutluyum, harika bir gün!",
                    "Üzgün hissediyorum, her şey ters gidiyor",
                    "Sinirli oldum, bu durumu kabul edemiyorum",
                    "Çok heyecanlıyım, yeni fırsatlar var!",
                    "Endişeliyim, her şey değişiyor çok hızlı",
                    "Müthiş bir enerji hissediyorum şu an",
                    "Biraz stresli oldum bugün, iş yoğunluğu var",
                    "Sakin ve huzurluyum, meditasyon yaptım",
                    "Kaygılı hissediyorum, belirsizlik var",
                    "Neşeliyim, arkadaşlarımla güzel zaman geçirdim"
                ],
                "timestamps": [
                    now - timedelta(days=i, hours=(8 + i*2) % 24) for i in range(10)  # Irregular schedule
                ],
                "group_messages": [
                    {"user_id": 1005, "text": "Bu konu beni çok heyecanlandırıyor!"},
                    {"user_id": 1001, "text": "Güzel Emre, enerjin çok iyi"},
                    {"user_id": 1005, "text": "Bazen endişe ediyorum ama, her şey yolunda gider mi?"},
                    {"user_id": 1002, "text": "Merak etme, beraber hallederiz"},
                    {"user_id": 1005, "text": "Haklısınız, takım halinde güçlüyüz"},
                    {"user_id": 1004, "text": "Duygusal zeka da önemli, Emre bu konuda başarılı"}
                ]
            }
        }
    
    async def test_big_five_analysis(self) -> Dict[str, Any]:
        """Big Five personality traits testleri"""
        
        logger.info("🧠 Big Five Personality Traits testleri başlatılıyor...")
        results = {}
        
        test_users = self.create_test_users()
        
        for user_name, user_data in test_users.items():
            try:
                user_id = user_data["user_id"]
                messages = user_data["messages"]
                
                # Big Five analizi
                big_five = await self.engine.analyze_big_five_traits(messages, user_id)
                
                results[user_name] = {
                    "user_id": user_id,
                    "big_five_scores": big_five.to_dict(),
                    "dominant_traits": [
                        trait for trait, score in big_five.to_dict().items() if score > 0.6
                    ],
                    "analysis_success": True
                }
                
                logger.info(f"✅ {user_name} Big Five analizi tamamlandı")
                
            except Exception as e:
                logger.error(f"❌ {user_name} Big Five analiz hatası: {e}")
                results[user_name] = {"analysis_success": False, "error": str(e)}
        
        return results
    
    async def test_comprehensive_analysis(self) -> Dict[str, Any]:
        """Kapsamlı analiz testleri"""
        
        logger.info("🔬 Comprehensive Analysis testleri başlatılıyor...")
        results = {}
        
        test_users = self.create_test_users()
        
        for user_name, user_data in test_users.items():
            try:
                user_id = user_data["user_id"]
                messages = user_data["messages"]
                timestamps = user_data["timestamps"]
                group_messages = user_data.get("group_messages", [])
                
                # Kapsamlı analiz
                advanced_profile = await self.engine.comprehensive_user_analysis(
                    user_id=user_id,
                    messages=messages,
                    message_timestamps=timestamps,
                    group_messages=group_messages
                )
                
                results[user_name] = {
                    "user_id": user_id,
                    "profile_created": advanced_profile is not None,
                    "big_five_analyzed": hasattr(advanced_profile, 'big_five'),
                    "timing_analyzed": hasattr(advanced_profile, 'timing_pattern'),
                    "sentiment_analyzed": hasattr(advanced_profile, 'sentiment_trend'),
                    "social_analyzed": hasattr(advanced_profile, 'social_dynamics'),
                    "motivation_analyzed": hasattr(advanced_profile, 'motivation_profile'),
                    "predictive_analyzed": hasattr(advanced_profile, 'predictive_insights'),
                    "analysis_success": True
                }
                
                logger.info(f"✅ {user_name} Comprehensive Analysis tamamlandı")
                
            except Exception as e:
                logger.error(f"❌ {user_name} Comprehensive Analysis hatası: {e}")
                results[user_name] = {"analysis_success": False, "error": str(e)}
        
        return results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Tüm testleri çalıştır"""
        
        logger.info("🚀 Advanced Behavioral Engine v2.0 Test Suite başlatılıyor...")
        
        all_results = {
            "test_suite_version": "2.0.0",
            "start_time": datetime.now().isoformat(),
            "engine_info": {
                "gpt_available": self.engine.gpt_available,
                "total_profiles": len(self.engine.user_profiles)
            }
        }
        
        # Test sırası
        tests = [
            ("big_five_analysis", self.test_big_five_analysis),
            ("comprehensive_analysis", self.test_comprehensive_analysis)
        ]
        
        for test_name, test_func in tests:
            try:
                logger.info(f"🔄 {test_name} testi başlatılıyor...")
                test_results = await test_func()
                all_results[test_name] = test_results
                
                # Success count
                successful_tests = sum(1 for result in test_results.values() 
                                     if isinstance(result, dict) and result.get("analysis_success", False))
                total_tests = len(test_results)
                
                logger.info(f"✅ {test_name} tamamlandı: {successful_tests}/{total_tests} başarılı")
                
            except Exception as e:
                logger.error(f"❌ {test_name} kritik hatası: {e}")
                all_results[test_name] = {"critical_error": str(e)}
        
        # Final stats
        all_results["end_time"] = datetime.now().isoformat()
        all_results["engine_final_stats"] = self.engine.get_advanced_engine_stats()
        
        logger.info("🎉 Tüm testler tamamlandı!")
        
        return all_results

async def main():
    """Ana test fonksiyonu"""
    
    print("\n" + "🧠" + "="*60 + "🧠")
    print("🚀 ADVANCED BEHAVIORAL ENGINE v2.0 TEST SUITE")
    print("💡 Comprehensive AI-Powered User Analysis Testing")
    print("🧠" + "="*60 + "🧠\n")
    
    # Test suite'i başlat
    test_suite = AdvancedBehavioralEngineTestSuite()
    
    try:
        # Tüm testleri çalıştır
        results = await test_suite.run_all_tests()
        
        # Sonuçları kaydet
        with open("advanced_behavioral_engine_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        # Özet rapor
        print("\n" + "📊" + "="*50 + "📊")
        print("🎯 TEST SONUÇLARI ÖZETİ")
        print("📊" + "="*50 + "📊")
        
        total_test_categories = len([k for k in results.keys() if not k.startswith(("test_suite", "start_time", "end_time", "engine"))])
        successful_categories = 0
        
        for test_name, test_data in results.items():
            if test_name.startswith(("test_suite", "start_time", "end_time", "engine")):
                continue
                
            if isinstance(test_data, dict) and "critical_error" not in test_data:
                successful_tests = sum(1 for result in test_data.values() 
                                     if isinstance(result, dict) and result.get("analysis_success", False))
                total_tests = len(test_data)
                success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
                
                print(f"✅ {test_name}: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
                if success_rate > 50:
                    successful_categories += 1
            else:
                print(f"❌ {test_name}: Kritik hata")
        
        overall_success_rate = (successful_categories / total_test_categories * 100) if total_test_categories > 0 else 0
        
        print(f"\n🎯 GENEL BAŞARI ORANI: {overall_success_rate:.1f}%")
        print(f"📈 Başarılı Kategoriler: {successful_categories}/{total_test_categories}")
        
        # Engine stats
        if "engine_final_stats" in results:
            stats = results["engine_final_stats"]
            print(f"\n🧠 ENGINE İSTATİSTİKLERİ:")
            print(f"   📊 Toplam Profil: {stats.get('total_profiles', 0)}")
            print(f"   🤖 GPT Mevcut: {stats.get('gpt_available', False)}")
            print(f"   📊 Advanced Analytics: {stats.get('advanced_analytics', False)}")
        
        print(f"\n💾 Detaylı sonuçlar: advanced_behavioral_engine_test_results.json")
        print("🎉 Test suite tamamlandı!")
        
    except Exception as e:
        logger.error(f"❌ Test suite kritik hatası: {e}")
        print(f"\n❌ Test suite kritik hatası: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 