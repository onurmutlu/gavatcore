#!/usr/bin/env python3
"""
🚀 GavatCore V2 - FINAL POWER TEST
Sistemin tam gücünü gösteren ultimate test!
"""

import asyncio
import json
import time
from datetime import datetime
from config import validate_config
from core.advanced_ai_manager import AdvancedAIManager, AITaskType, AIPriority

async def ultimate_power_test():
    """🔥 ULTIMATE POWER TEST - Sistemin tam gücü!"""
    print("🚀" + "="*60)
    print("🔥 GAVATCORE V2 - ULTIMATE POWER TEST")
    print("💰 YAŞASIN SPONSORLAR! FULL GPT-4 POWER!")
    print("="*60)
    
    # Config doğrula
    print("\n📋 Config Validation:")
    validate_config()
    
    # AI Manager başlat
    print("\n🤖 AI Manager başlatılıyor...")
    ai_manager = AdvancedAIManager()
    
    # Test senaryoları
    test_scenarios = [
        {
            "name": "💭 Sentiment Analysis",
            "task_type": AITaskType.SENTIMENT_ANALYSIS,
            "prompt": "Bugün çok mutluyum! GavatCore sistemi mükemmel çalışıyor!",
            "priority": AIPriority.REAL_TIME
        },
        {
            "name": "🧠 Personality Analysis", 
            "task_type": AITaskType.PERSONALITY_ANALYSIS,
            "prompt": "Kullanıcı profili: Aktif, sosyal, teknoloji meraklısı, lider karakterli",
            "priority": AIPriority.HIGH
        },
        {
            "name": "📝 Content Generation",
            "task_type": AITaskType.CONTENT_GENERATION, 
            "prompt": "GavatCore V2 için motivasyonel bir mesaj oluştur",
            "priority": AIPriority.NORMAL
        }
    ]
    
    print(f"\n🎯 {len(test_scenarios)} test senaryosu başlatılıyor...")
    
    # Paralel test'ler başlat
    task_ids = []
    start_time = time.time()
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n🚀 Test {i+1}: {scenario['name']}")
        
        task_id = await ai_manager.submit_ai_task(
            task_type=scenario['task_type'],
            user_id=f"power_test_user_{i}",
            prompt=scenario['prompt'],
            priority=scenario['priority']
        )
        
        task_ids.append((task_id, scenario['name']))
        print(f"   📤 Task ID: {task_id}")
    
    # Sonuçları bekle ve topla
    print(f"\n⏳ Sonuçlar bekleniyor...")
    results = {}
    
    for task_id, name in task_ids:
        print(f"\n🔍 {name} sonucu alınıyor...")
        result = await ai_manager.get_task_result(task_id, wait_timeout=20.0)
        results[name] = result
        
        if "error" not in result:
            print(f"   ✅ Başarılı!")
            # İlk 100 karakteri göster
            if isinstance(result, dict):
                preview = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
                print(f"   📊 Önizleme: {preview}")
        else:
            print(f"   ❌ Hata: {result.get('error', 'Bilinmeyen hata')}")
    
    total_time = time.time() - start_time
    
    # System Analytics
    print(f"\n📈 SYSTEM ANALYTICS:")
    analytics = await ai_manager.get_system_analytics()
    
    print(f"   🎯 Queue Status:")
    print(f"      Pending: {analytics['queue_status']['pending_tasks']}")
    print(f"      Active: {analytics['queue_status']['active_tasks']}")  
    print(f"      Completed: {analytics['queue_status']['completed_tasks']}")
    
    print(f"   ⚡ Rate Limiting:")
    print(f"      Utilization: {analytics['rate_limiting']['utilization']}")
    print(f"      Requests: {analytics['rate_limiting']['requests_this_minute']}/{analytics['rate_limiting']['limit']}")
    
    print(f"   🚀 AI Features:")
    features = analytics['ai_features']
    for feature, status in features.items():
        status_icon = "✅" if status else "❌"
        print(f"      {feature}: {status_icon}")
    
    # Final Rapor
    print(f"\n🏆 FINAL RAPOR:")
    print(f"   ⏱️  Toplam Süre: {total_time:.2f}s")
    print(f"   🎯 Test Sayısı: {len(test_scenarios)}")
    
    successful_tests = len([r for r in results.values() if "error" not in r])
    print(f"   ✅ Başarılı: {successful_tests}/{len(test_scenarios)}")
    
    if successful_tests == len(test_scenarios):
        print(f"\n🎉 MÜKEMMEL! TÜM TESTLER BAŞARILI!")
        print(f"🚀 GAVATCORE V2 - FULL POWER CONFIRMED!")
        print(f"💰 YAŞASIN SPONSORLAR!")
    else:
        print(f"\n⚠️  Bazı testler başarısız oldu, ama sistem çalışıyor!")
    
    # Detaylı sonuçları kaydet
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_time": total_time,
        "test_count": len(test_scenarios),
        "successful_tests": successful_tests,
        "results": results,
        "analytics": analytics
    }
    
    report_file = f"ultimate_power_test_report_{int(time.time())}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📄 Detaylı rapor kaydedildi: {report_file}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(ultimate_power_test()) 