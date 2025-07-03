#!/usr/bin/env python3
"""
Scheduler Engine Test Script
===========================

Bu script scheduler_engine.py modülünün tüm özelliklerini test eder.
"""

import asyncio
import json
from datetime import datetime, timedelta
from gavatcore_engine.scheduler_engine import (
    scheduler_engine, ScheduledTask, TaskType, GroupConfig
)
from gavatcore_engine.redis_state import redis_state


async def test_scheduler_engine():
    """Scheduler engine'in tüm özelliklerini test et."""
    
    print("🚀 Scheduler Engine Test Başlıyor...")
    print("="*60)
    
    # Redis'e bağlan
    await redis_state.connect()
    
    # Scheduler'ı başlat
    await scheduler_engine.initialize()
    
    # Test 1: Group Config
    print("\n1️⃣ Group Config Testi...")
    group_config = GroupConfig(
        group_id=-1001234567890,
        interval_min=30,  # 30 saniye
        interval_max=60,  # 1 dakika
        cooldown_min=10,
        cooldown_max=30,
        max_messages_per_hour=20,
        spam_protection_enabled=True,
        random_delay_enabled=True,
    )
    
    await scheduler_engine.update_group_config(-1001234567890, group_config)
    retrieved_config = await scheduler_engine.get_group_config(-1001234567890)
    print(f"   ✅ Group config kaydedildi: {retrieved_config.group_id}")
    
    # Test 2: Basit Zamanlanmış Mesaj
    print("\n2️⃣ Zamanlanmış Mesaj Testi...")
    scheduled_task = ScheduledTask(
        id="test_message_1",
        task_type=TaskType.SCHEDULED_MESSAGE,
        scheduled_at=datetime.utcnow() + timedelta(seconds=5),  # 5 saniye sonra
        group_id=-1001234567890,
        bot_id="yayincilara",
        task_data={
            "content": "Bu bir test mesajıdır! 🚀",
            "target_chat_id": -1001234567890,
            "message_type": "group_message",
            "priority": "normal"
        }
    )
    
    task_id = await scheduler_engine.add_task(scheduled_task)
    print(f"   ✅ Zamanlanmış mesaj eklendi: {task_id}")
    
    # Test 3: Recurring (Tekrarlayan) Mesaj
    print("\n3️⃣ Tekrarlayan Mesaj Testi...")
    recurring_task = ScheduledTask(
        id="test_recurring_1",
        task_type=TaskType.RECURRING_MESSAGE,
        scheduled_at=datetime.utcnow() + timedelta(seconds=10),
        group_id=-1001234567890,
        bot_id="xxxgeisha",
        recurring=True,
        recurring_interval=30,  # Her 30 saniyede
        max_executions=3,  # Sadece 3 kez
        task_data={
            "content": "Tekrarlayan mesaj #{execution_count} 🔄",
            "target_chat_id": -1001234567890,
            "message_type": "group_message",
            "priority": "high"
        }
    )
    
    recurring_id = await scheduler_engine.add_task(recurring_task)
    print(f"   ✅ Tekrarlayan mesaj eklendi: {recurring_id}")
    
    # Test 4: Cron Expression ile Zamanlanmış
    print("\n4️⃣ Cron Expression Testi...")
    cron_task = ScheduledTask(
        id="test_cron_1",
        task_type=TaskType.SCHEDULED_MESSAGE,
        scheduled_at=datetime.utcnow(),
        group_id=-1001234567890,
        bot_id="yayincilara",
        recurring=True,
        cron_expression="*/30 * * * * *",  # Her 30 saniyede (saniye cron)
        max_executions=2,
        task_data={
            "content": "Cron tabanlı mesaj ⏰",
            "target_chat_id": -1001234567890,
            "message_type": "group_message",
            "priority": "low"
        }
    )
    
    cron_id = await scheduler_engine.add_task(cron_task)
    print(f"   ✅ Cron mesaj eklendi: {cron_id}")
    
    # Test 5: Task Listeleme ve Stats
    print("\n5️⃣ Task Listeleme Testi...")
    all_tasks = await scheduler_engine.get_all_tasks()
    print(f"   📊 Toplam task sayısı: {len(all_tasks)}")
    
    for task in all_tasks:
        print(f"   📋 {task['id']}: {task['task_type']} - {task['status']}")
    
    stats = await scheduler_engine.get_stats()
    print(f"   📈 Scheduler stats: {stats}")
    
    # Test 6: Spam Protection
    print("\n6️⃣ Spam Protection Testi...")
    config = await scheduler_engine.get_group_config(-1001234567890)
    delay = await scheduler_engine.spam_protection.calculate_delay(
        -1001234567890, 
        "yayincilara", 
        config
    )
    print(f"   ⏰ Hesaplanan delay: {delay:.2f} saniye")
    
    # Test 7: Task Operasyonları
    print("\n7️⃣ Task Operasyonları Testi...")
    
    # Pause task
    await scheduler_engine.pause_task(task_id)
    print(f"   ⏸️ Task paused: {task_id}")
    
    # Resume task
    await scheduler_engine.resume_task(task_id)
    print(f"   ▶️ Task resumed: {task_id}")
    
    # Scheduler'ı başlat ve biraz bekle
    print("\n8️⃣ Scheduler Execution Testi...")
    print("   🔄 Scheduler başlatılıyor, 60 saniye test edilecek...")
    
    await scheduler_engine.start()
    
    # 60 saniye bekle
    for i in range(12):  # 12 * 5 = 60 saniye
        await asyncio.sleep(5)
        stats = await scheduler_engine.get_stats()
        print(f"   ⏳ {(i+1)*5}s - Aktif tasks: {stats['status_counts']}")
    
    # Test 8: Manual Task Execution Simulation
    print("\n9️⃣ Manual Execution Simulation...")
    
    # Create a task that should execute immediately
    immediate_task = ScheduledTask(
        id="test_immediate",
        task_type=TaskType.SCHEDULED_MESSAGE,
        scheduled_at=datetime.utcnow() - timedelta(seconds=1),  # Past time
        group_id=-1001234567890,
        bot_id="yayincilara",
        task_data={
            "content": "Immediate execution test! ⚡",
            "target_chat_id": -1001234567890,
            "message_type": "group_message",
            "priority": "urgent"
        }
    )
    
    immediate_id = await scheduler_engine.add_task(immediate_task)
    print(f"   ⚡ Immediate task eklendi: {immediate_id}")
    
    # Wait a bit for execution
    await asyncio.sleep(3)
    
    # Test 9: Error Handling
    print("\n🔟 Error Handling Testi...")
    
    # Create a task with invalid data
    error_task = ScheduledTask(
        id="test_error",
        task_type=TaskType.SCHEDULED_MESSAGE,
        scheduled_at=datetime.utcnow() + timedelta(seconds=2),
        group_id=-1001234567890,
        bot_id="invalid_bot",
        task_data={
            "content": "",  # Empty content should cause error
            "target_chat_id": None,  # Invalid target
            "message_type": "invalid_type",
            "priority": "invalid_priority"
        }
    )
    
    error_id = await scheduler_engine.add_task(error_task)
    print(f"   ❌ Error task eklendi: {error_id}")
    
    # Wait for error handling
    await asyncio.sleep(5)
    
    # Final stats
    print("\n📊 Final Test Sonuçları...")
    final_stats = await scheduler_engine.get_stats()
    print(f"   📈 Final stats: {json.dumps(final_stats, indent=2)}")
    
    all_tasks_final = await scheduler_engine.get_all_tasks()
    print(f"   📋 Final task count: {len(all_tasks_final)}")
    
    for task in all_tasks_final:
        print(f"   📄 {task['id'][:12]}... | {task['task_type']} | {task['status']} | Executions: {task['execution_count']}")
    
    # Cleanup
    print("\n🧹 Cleanup...")
    await scheduler_engine.stop()
    await redis_state.disconnect()
    
    print("\n✅ Scheduler Engine Test Tamamlandı!")
    print("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(test_scheduler_engine())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc() 