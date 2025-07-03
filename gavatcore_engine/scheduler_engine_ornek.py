#!/usr/bin/env python3
"""
Scheduler Engine Kullanım Örnekleri
====================================

Scheduler Engine'in pratik kullanım senaryolarını gösterir.
"""

import asyncio
from datetime import datetime, timedelta
from gavatcore_engine.scheduler_engine import (
    scheduler_engine, ScheduledTask, TaskType, GroupConfig
)


async def ornek_1_basit_zamanlama():
    """Örnek 1: Basit mesaj zamanlama."""
    print("📅 Örnek 1: 10 saniye sonra mesaj gönder")
    
    task = ScheduledTask(
        id="basit_mesaj",
        task_type=TaskType.SCHEDULED_MESSAGE,
        scheduled_at=datetime.utcnow() + timedelta(seconds=10),
        bot_id="yayincilara",
        task_data={
            "content": "Merhaba! Bu 10 saniye önce zamanlanmış bir mesaj.",
            "target_chat_id": -1001234567890,
            "message_type": "group_message",
            "priority": "normal"
        }
    )
    
    task_id = await scheduler_engine.add_task(task)
    print(f"✅ Task oluşturuldu: {task_id}")
    return task_id


async def ornek_2_tekrarlayan_mesaj():
    """Örnek 2: Tekrarlayan mesaj."""
    print("🔄 Örnek 2: Her 30 saniyede tekrarlayan mesaj")
    
    task = ScheduledTask(
        id="tekrarlayan_mesaj",
        task_type=TaskType.RECURRING_MESSAGE,
        scheduled_at=datetime.utcnow() + timedelta(seconds=5),
        bot_id="xxxgeisha",
        recurring=True,
        recurring_interval=30,  # 30 saniyede bir
        max_executions=5,       # Toplam 5 kez
        task_data={
            "content": "Bu tekrarlayan mesajın {execution_count}. gönderimi! 🔄",
            "target_chat_id": -1001234567890,
            "message_type": "group_message",
            "priority": "low"
        }
    )
    
    task_id = await scheduler_engine.add_task(task)
    print(f"✅ Tekrarlayan task oluşturuldu: {task_id}")
    return task_id


async def ornek_3_cron_zamanlama():
    """Örnek 3: Cron expression ile zamanlama."""
    print("⏰ Örnek 3: Cron expression - her saat başı")
    
    task = ScheduledTask(
        id="cron_mesaj",
        task_type=TaskType.SCHEDULED_MESSAGE,
        scheduled_at=datetime.utcnow(),
        bot_id="yayincilara",
        recurring=True,
        cron_expression="0 * * * *",  # Her saat başı
        max_executions=24,            # 24 saat = 1 gün
        task_data={
            "content": f"🕐 Saat başı hatırlatma! Şu an saat {datetime.now().hour}:00",
            "target_chat_id": -1001234567890,
            "message_type": "group_message",
            "priority": "high"
        }
    )
    
    task_id = await scheduler_engine.add_task(task)
    print(f"✅ Cron task oluşturuldu: {task_id}")
    return task_id


async def ornek_4_grup_konfigurasyonu():
    """Örnek 4: Grup özel konfigürasyonu."""
    print("⚙️ Örnek 4: Grup bazlı spam protection ayarları")
    
    # VIP grup - daha hızlı mesajlaşma
    vip_config = GroupConfig(
        group_id=-1001111111111,
        interval_min=60,    # 1 dakika
        interval_max=120,   # 2 dakika
        cooldown_min=30,
        cooldown_max=60,
        max_messages_per_hour=30,
        spam_protection_enabled=True,
        random_delay_enabled=True,
        priority_multiplier=0.8,  # %20 daha hızlı
        active=True
    )
    
    # Normal grup - standart ayarlar
    normal_config = GroupConfig(
        group_id=-1001222222222,
        interval_min=300,   # 5 dakika
        interval_max=600,   # 10 dakika
        cooldown_min=120,
        cooldown_max=300,
        max_messages_per_hour=12,
        spam_protection_enabled=True,
        random_delay_enabled=True,
        priority_multiplier=1.0,
        active=True
    )
    
    await scheduler_engine.update_group_config(-1001111111111, vip_config)
    await scheduler_engine.update_group_config(-1001222222222, normal_config)
    
    print("✅ Grup konfigürasyonları kaydedildi")
    
    # Test mesajları
    for group_id, group_name in [(-1001111111111, "VIP"), (-1001222222222, "Normal")]:
        task = ScheduledTask(
            id=f"group_test_{group_id}",
            task_type=TaskType.SCHEDULED_MESSAGE,
            scheduled_at=datetime.utcnow() + timedelta(seconds=5),
            group_id=group_id,
            bot_id="yayincilara",
            task_data={
                "content": f"Bu {group_name} grup için özel ayarlarla gönderilen mesaj!",
                "target_chat_id": group_id,
                "message_type": "group_message",
                "priority": "normal"
            }
        )
        
        await scheduler_engine.add_task(task)
        print(f"✅ {group_name} grup mesajı zamanlandı")


async def ornek_5_toplu_mesaj_planlama():
    """Örnek 5: Toplu mesaj planlama."""
    print("📢 Örnek 5: Birden fazla gruba toplu mesaj")
    
    groups = [
        -1001234567890,
        -1001111111111,
        -1001222222222,
    ]
    
    base_time = datetime.utcnow() + timedelta(minutes=1)
    
    for i, group_id in enumerate(groups):
        # Her grup için 30 saniye arayla zamanla
        send_time = base_time + timedelta(seconds=i * 30)
        
        task = ScheduledTask(
            id=f"toplu_mesaj_{group_id}",
            task_type=TaskType.GROUP_BROADCAST,
            scheduled_at=send_time,
            group_id=group_id,
            bot_id="xxxgeisha",
            task_data={
                "content": f"📢 Toplu duyuru! Bu mesaj {len(groups)} gruba gönderildi.",
                "target_chat_id": group_id,
                "message_type": "group_message",
                "priority": "high"
            }
        )
        
        await scheduler_engine.add_task(task)
        print(f"✅ Grup {group_id} için {send_time.strftime('%H:%M:%S')}'de zamanlandı")


async def ornek_6_dinamik_spam_protection():
    """Örnek 6: Dinamik spam protection test."""
    print("🛡️ Örnek 6: Spam protection simulation")
    
    group_id = -1001234567890
    config = await scheduler_engine.get_group_config(group_id)
    
    # Birden fazla mesaj ekle - spam protection devreye girmeli
    for i in range(5):
        task = ScheduledTask(
            id=f"spam_test_{i}",
            task_type=TaskType.SCHEDULED_MESSAGE,
            scheduled_at=datetime.utcnow() + timedelta(seconds=i * 2),
            group_id=group_id,
            bot_id="yayincilara",
            task_data={
                "content": f"Spam test mesajı #{i+1}",
                "target_chat_id": group_id,
                "message_type": "group_message",
                "priority": "normal"
            }
        )
        
        await scheduler_engine.add_task(task)
    
    print("✅ 5 spam test mesajı eklendi - spam protection test edilecek")
    
    # Delay hesapla
    for i in range(3):
        delay = await scheduler_engine.spam_protection.calculate_delay(
            group_id, "yayincilara", config
        )
        print(f"   🕒 Hesaplanan delay #{i+1}: {delay:.2f} saniye")
        
        # Mesaj sayacını artır (simulate message send)
        await scheduler_engine.spam_protection.increment_message_count(group_id, "yayincilara")


async def ornek_7_task_yonetimi():
    """Örnek 7: Task yönetimi operasyonları."""
    print("🎛️ Örnek 7: Task yönetimi - pause, resume, cancel")
    
    # Test task oluştur
    task = ScheduledTask(
        id="yonetim_test",
        task_type=TaskType.SCHEDULED_MESSAGE,
        scheduled_at=datetime.utcnow() + timedelta(minutes=5),
        bot_id="yayincilara",
        task_data={
            "content": "Bu mesaj yönetim testi için oluşturuldu",
            "target_chat_id": -1001234567890,
            "message_type": "group_message",
            "priority": "normal"
        }
    )
    
    task_id = await scheduler_engine.add_task(task)
    print(f"✅ Test task oluşturuldu: {task_id}")
    
    # Task'ı pause et
    await scheduler_engine.pause_task(task_id)
    print(f"⏸️ Task paused: {task_id}")
    
    # 5 saniye bekle
    await asyncio.sleep(5)
    
    # Task'ı resume et
    await scheduler_engine.resume_task(task_id)
    print(f"▶️ Task resumed: {task_id}")
    
    # 3 saniye bekle
    await asyncio.sleep(3)
    
    # Task'ı cancel et
    await scheduler_engine.cancel_task(task_id)
    print(f"❌ Task cancelled: {task_id}")


async def main():
    """Ana demo fonksiyonu."""
    print("🚀 Scheduler Engine Kullanım Örnekleri")
    print("="*60)
    
    # Scheduler'ı başlat
    await scheduler_engine.initialize()
    
    # Örnekleri çalıştır
    await ornek_1_basit_zamanlama()
    print()
    
    await ornek_2_tekrarlayan_mesaj()
    print()
    
    await ornek_3_cron_zamanlama()
    print()
    
    await ornek_4_grup_konfigurasyonu()
    print()
    
    await ornek_5_toplu_mesaj_planlama()
    print()
    
    await ornek_6_dinamik_spam_protection()
    print()
    
    await ornek_7_task_yonetimi()
    print()
    
    # Scheduler'ı başlat
    print("🔄 Scheduler başlatılıyor...")
    await scheduler_engine.start()
    
    # Stats göster
    print("\n📊 Başlangıç Stats:")
    stats = await scheduler_engine.get_stats()
    print(f"   📋 Toplam task: {stats['total_tasks']}")
    print(f"   📈 Status dağılımı: {stats['status_counts']}")
    
    # Task listesi
    tasks = await scheduler_engine.get_all_tasks()
    print(f"\n📝 Aktif Task Listesi ({len(tasks)} adet):")
    for task in tasks[:10]:  # İlk 10'unu göster
        print(f"   📄 {task['id'][:20]}... | {task['task_type']} | {task['status']}")
    
    print(f"\n⏱️ 30 saniye boyunca scheduler çalışacak...")
    
    # 30 saniye bekle ve stats göster
    for i in range(6):  # 6 * 5 = 30 saniye
        await asyncio.sleep(5)
        stats = await scheduler_engine.get_stats()
        print(f"   📊 {(i+1)*5}s: {stats['status_counts']}")
    
    # Final stats
    print("\n📊 Final Stats:")
    final_stats = await scheduler_engine.get_stats()
    print(f"   📈 Final stats: {final_stats}")
    
    # Cleanup
    print("\n🧹 Scheduler durduruluyor...")
    await scheduler_engine.stop()
    
    print("\n✅ Demo tamamlandı!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc() 