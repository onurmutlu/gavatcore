#!/usr/bin/env python3
"""
Hızlı AI Test - JSON parsing düzeltmelerini test et
"""

import asyncio
import json
from config import OPENAI_API_KEY
from core.advanced_ai_manager import AdvancedAIManager, AITaskType, AIPriority

async def quick_test():
    """Hızlı AI test"""
    print("🧪 Hızlı AI Test Başlatılıyor...")
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY bulunamadı!")
        return
    
    # AI Manager'ı başlat
    ai_manager = AdvancedAIManager()
    
    # Basit bir sentiment analizi test et
    print("📝 Sentiment analizi test ediliyor...")
    
    task_id = await ai_manager.submit_ai_task(
        task_type=AITaskType.SENTIMENT_ANALYSIS,
        user_id="test_user",
        prompt="Bugün çok mutluyum! Harika bir gün geçiriyorum.",
        priority=AIPriority.HIGH
    )
    
    print(f"🎯 Task ID: {task_id}")
    
    # Sonucu bekle
    result = await ai_manager.get_task_result(task_id, wait_timeout=15.0)
    
    print("📊 Sonuç:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # System analytics
    analytics = await ai_manager.get_system_analytics()
    print("\n📈 System Analytics:")
    print(f"   Pending: {analytics['queue_status']['pending_tasks']}")
    print(f"   Active: {analytics['queue_status']['active_tasks']}")
    print(f"   Completed: {analytics['queue_status']['completed_tasks']}")
    print(f"   Rate Limit: {analytics['rate_limiting']['utilization']}")

if __name__ == "__main__":
    asyncio.run(quick_test()) 