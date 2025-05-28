#!/usr/bin/env python3
"""
GavatCore V2 - CRM Management Script
Veritabanı, AI analizi ve broadcast yönetimi için komut satırı aracı
"""

import asyncio
import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any
sys.path.append('.')

async def init_database():
    """Veritabanını başlat"""
    print("🗄️ Veritabanı başlatılıyor...")
    
    try:
        from core.database_manager import database_manager
        await database_manager.initialize()
        print("✅ Veritabanı başarıyla başlatıldı")
        return True
    except Exception as e:
        print(f"❌ Veritabanı başlatma hatası: {e}")
        return False

async def add_broadcast_targets(targets_file: str = None):
    """Broadcast hedeflerini ekle"""
    print("📢 Broadcast hedefleri ekleniyor...")
    
    try:
        from core.database_manager import database_manager, BroadcastTarget
        
        # Örnek hedefler (gerçek kullanımda dosyadan okunacak)
        sample_targets = [
            {
                "target_id": "-1002607016335",  # Gerçek test grubu
                "target_type": "group",
                "bot_username": "gavatcore_bot",
                "is_accessible": True,
                "notes": "Ana test grubu"
            },
            {
                "target_id": "test_group_2",
                "target_type": "group", 
                "bot_username": "gavatcore_bot",
                "is_accessible": True,
                "notes": "İkinci test grubu"
            }
        ]
        
        if targets_file and os.path.exists(targets_file):
            with open(targets_file, 'r', encoding='utf-8') as f:
                targets_data = json.load(f)
        else:
            targets_data = sample_targets
            print("⚠️ Hedef dosyası bulunamadı, örnek hedefler kullanılıyor")
        
        added_count = 0
        for target_data in targets_data:
            target = BroadcastTarget(
                target_id=target_data["target_id"],
                target_type=target_data["target_type"],
                bot_username=target_data["bot_username"],
                is_accessible=target_data.get("is_accessible", True),
                notes=target_data.get("notes", "")
            )
            
            success = await database_manager.add_broadcast_target(target)
            if success:
                added_count += 1
                print(f"✅ Hedef eklendi: {target.target_type}:{target.target_id}")
        
        print(f"📊 Toplam {added_count} hedef eklendi")
        return True
        
    except Exception as e:
        print(f"❌ Broadcast hedef ekleme hatası: {e}")
        return False

async def generate_sample_users(count: int = 50):
    """Örnek kullanıcı verileri oluştur"""
    print(f"👥 {count} örnek kullanıcı oluşturuluyor...")
    
    try:
        from core.database_manager import database_manager, UserInteractionType
        import random
        
        characters = ["geisha", "babagavat", "ai_assistant"]
        interaction_types = list(UserInteractionType)
        
        for i in range(count):
            user_id = f"sample_user_{i+1}"
            username = f"user_{i+1}"
            
            # Rastgele kullanıcı verileri
            message_count = random.randint(1, 100)
            voice_minutes = random.randint(0, 120)
            quests_completed = random.randint(0, 20)
            events_joined = random.randint(0, 10)
            favorite_character = random.choice(characters)
            
            # Kullanıcı analytics güncelle
            await database_manager.update_user_analytics(
                user_id=user_id,
                username=username,
                interaction_data={
                    "message_count": message_count,
                    "voice_minutes": voice_minutes,
                    "quest_completed": quests_completed > 0,
                    "event_joined": events_joined > 0,
                    "favorite_character": favorite_character
                }
            )
            
            # Rastgele etkileşimler ekle
            interaction_count = random.randint(5, 25)
            for j in range(interaction_count):
                await database_manager.log_user_interaction(
                    user_id=user_id,
                    interaction_type=random.choice(interaction_types),
                    character_id=random.choice(characters),
                    duration_seconds=random.randint(30, 300),
                    metadata={"session": f"session_{j}", "sample": True}
                )
            
            if (i + 1) % 10 == 0:
                print(f"✅ {i + 1} kullanıcı oluşturuldu...")
        
        print(f"🎉 {count} örnek kullanıcı başarıyla oluşturuldu")
        return True
        
    except Exception as e:
        print(f"❌ Örnek kullanıcı oluşturma hatası: {e}")
        return False

async def run_ai_analysis(analysis_type: str = "full"):
    """AI analizi çalıştır"""
    print(f"🤖 AI analizi başlatılıyor: {analysis_type}")
    
    try:
        from core.ai_crm_analyzer import initialize_ai_crm_analyzer
        
        # AI CRM Analyzer'ı başlat
        ai_crm = await initialize_ai_crm_analyzer()
        
        if analysis_type == "segmentation":
            result = await ai_crm.analyze_user_segmentation()
            print("📊 User Segmentation Analizi:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif analysis_type == "broadcast":
            result = await ai_crm.analyze_broadcast_optimization()
            print("📢 Broadcast Optimization Analizi:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif analysis_type == "churn":
            result = await ai_crm.predict_churn_risk()
            print("⚠️ Churn Prediction Analizi:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif analysis_type == "engagement":
            result = await ai_crm.optimize_engagement()
            print("🎯 Engagement Optimization Analizi:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif analysis_type == "full":
            result = await ai_crm.run_full_crm_analysis()
            print("🔍 Tam CRM Analizi:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        else:
            print(f"❌ Bilinmeyen analiz tipi: {analysis_type}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ AI analizi hatası: {e}")
        return False

async def show_analytics():
    """Sistem analitiklerini göster"""
    print("📊 Sistem analitikleri alınıyor...")
    
    try:
        from core.database_manager import database_manager
        
        # Broadcast stats
        broadcast_stats = await database_manager.get_broadcast_stats(30)
        print("\n📢 Broadcast İstatistikleri (Son 30 gün):")
        print(json.dumps(broadcast_stats, indent=2, ensure_ascii=False))
        
        # User engagement report
        engagement_report = await database_manager.get_user_engagement_report()
        print("\n👥 Kullanıcı Engagement Raporu:")
        print(json.dumps(engagement_report, indent=2, ensure_ascii=False))
        
        # Broadcast targets
        targets = await database_manager.get_broadcast_targets()
        print(f"\n🎯 Broadcast Hedefleri: {len(targets)} adet")
        
        accessible_targets = [t for t in targets if t.is_accessible]
        failed_targets = [t for t in targets if not t.is_accessible]
        
        print(f"   ✅ Erişilebilir: {len(accessible_targets)}")
        print(f"   ❌ Erişilemeyen: {len(failed_targets)}")
        
        # Grup breakdown
        group_targets = [t for t in targets if t.target_type == "group"]
        user_targets = [t for t in targets if t.target_type == "user"]
        
        print(f"   📱 Gruplar: {len(group_targets)}")
        print(f"   👤 Kullanıcılar: {len(user_targets)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analitik alma hatası: {e}")
        return False

async def test_broadcast(message: str = None):
    """Test broadcast gönder"""
    print("📢 Test broadcast gönderiliyor...")
    
    try:
        from core.telegram_broadcaster import telegram_broadcaster
        
        if not message:
            message = f"🧪 Test mesajı - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            message += "Bu bir GavatCore V2 test mesajıdır.\n"
            message += "🎯 Veritabanı temelli broadcast sistemi çalışıyor!"
        
        broadcast_id = await telegram_broadcaster.broadcast_custom_message(
            message=message,
            target_types=["group"],
            priority="normal"
        )
        
        print(f"✅ Test broadcast kuyruğa eklendi: {broadcast_id}")
        print("⏳ Mesaj gönderilmesi için birkaç saniye bekleyin...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test broadcast hatası: {e}")
        return False

async def create_crm_segments():
    """CRM segmentleri oluştur"""
    print("🎯 CRM segmentleri oluşturuluyor...")
    
    try:
        from core.database_manager import database_manager
        
        segments = [
            {
                "name": "vip_users",
                "criteria": {"engagement_level": "vip", "min_activity_score": 80},
                "description": "VIP kullanıcılar - Yüksek aktivite ve engagement"
            },
            {
                "name": "high_engagement",
                "criteria": {"engagement_level": "high", "min_activity_score": 50},
                "description": "Yüksek engagement gösteren aktif kullanıcılar"
            },
            {
                "name": "voice_users",
                "criteria": {"min_voice_minutes": 10},
                "description": "Sesli özellikler kullanan kullanıcılar"
            },
            {
                "name": "quest_masters",
                "criteria": {"min_quests": 5},
                "description": "Çok quest tamamlayan kullanıcılar"
            },
            {
                "name": "churn_risk",
                "criteria": {"engagement_level": "low"},
                "description": "Kayıp riski taşıyan kullanıcılar"
            }
        ]
        
        created_count = 0
        for segment in segments:
            success = await database_manager.create_crm_segment(
                segment_name=segment["name"],
                criteria=segment["criteria"],
                description=segment["description"]
            )
            
            if success:
                created_count += 1
                print(f"✅ Segment oluşturuldu: {segment['name']}")
        
        print(f"🎉 {created_count} CRM segmenti oluşturuldu")
        return True
        
    except Exception as e:
        print(f"❌ CRM segment oluşturma hatası: {e}")
        return False

async def cleanup_database():
    """Veritabanını temizle"""
    print("🧹 Veritabanı temizleniyor...")
    
    try:
        from core.database_manager import database_manager
        import aiosqlite
        
        # Test verilerini temizle
        async with aiosqlite.connect(database_manager.db_path) as db:
            # Test kullanıcılarını sil
            await db.execute("DELETE FROM user_analytics WHERE user_id LIKE 'sample_user_%' OR user_id LIKE 'test_user_%'")
            await db.execute("DELETE FROM user_interactions WHERE user_id LIKE 'sample_user_%' OR user_id LIKE 'test_user_%'")
            
            # Test gruplarını sil
            await db.execute("DELETE FROM group_analytics WHERE group_id LIKE 'test_group_%'")
            await db.execute("DELETE FROM broadcast_targets WHERE target_id LIKE 'test_group_%' OR notes LIKE '%test%'")
            
            # Eski broadcast history'yi temizle (30 günden eski)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            await db.execute("DELETE FROM broadcast_history WHERE created_at < ?", (thirty_days_ago,))
            
            await db.commit()
        
        print("✅ Veritabanı temizlendi")
        return True
        
    except Exception as e:
        print(f"❌ Veritabanı temizleme hatası: {e}")
        return False

async def export_data(output_file: str = "gavatcore_export.json"):
    """Verileri export et"""
    print(f"📤 Veriler export ediliyor: {output_file}")
    
    try:
        from core.database_manager import database_manager
        
        # Tüm verileri al
        users = await database_manager.get_users_for_ai_analysis(1000)
        broadcast_stats = await database_manager.get_broadcast_stats(90)
        engagement_report = await database_manager.get_user_engagement_report()
        targets = await database_manager.get_broadcast_targets()
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "users": users,
            "broadcast_stats": broadcast_stats,
            "engagement_report": engagement_report,
            "broadcast_targets": [
                {
                    "target_id": t.target_id,
                    "target_type": t.target_type,
                    "bot_username": t.bot_username,
                    "is_accessible": t.is_accessible,
                    "failure_count": t.failure_count,
                    "notes": t.notes
                } for t in targets
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Veriler başarıyla export edildi: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Export hatası: {e}")
        return False

async def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="GavatCore V2 CRM Management")
    parser.add_argument("command", choices=[
        "init", "add-targets", "generate-users", "analyze", "analytics", 
        "test-broadcast", "create-segments", "cleanup", "export"
    ], help="Çalıştırılacak komut")
    
    parser.add_argument("--count", type=int, default=50, help="Oluşturulacak kullanıcı sayısı")
    parser.add_argument("--analysis-type", default="full", choices=["segmentation", "broadcast", "churn", "engagement", "full"], help="Analiz tipi")
    parser.add_argument("--message", help="Test broadcast mesajı")
    parser.add_argument("--targets-file", help="Broadcast hedefleri dosyası")
    parser.add_argument("--output", default="gavatcore_export.json", help="Export dosyası")
    
    args = parser.parse_args()
    
    print("🚀 GavatCore V2 CRM Management başlatılıyor...\n")
    
    # Database'i her zaman başlat
    if not await init_database():
        print("❌ Veritabanı başlatılamadı, çıkılıyor...")
        return
    
    success = False
    
    if args.command == "init":
        print("✅ Veritabanı başlatıldı")
        success = True
        
    elif args.command == "add-targets":
        success = await add_broadcast_targets(args.targets_file)
        
    elif args.command == "generate-users":
        success = await generate_sample_users(args.count)
        
    elif args.command == "analyze":
        success = await run_ai_analysis(args.analysis_type)
        
    elif args.command == "analytics":
        success = await show_analytics()
        
    elif args.command == "test-broadcast":
        success = await test_broadcast(args.message)
        
    elif args.command == "create-segments":
        success = await create_crm_segments()
        
    elif args.command == "cleanup":
        success = await cleanup_database()
        
    elif args.command == "export":
        success = await export_data(args.output)
    
    if success:
        print(f"\n✅ {args.command} komutu başarıyla tamamlandı!")
    else:
        print(f"\n❌ {args.command} komutu başarısız oldu!")

if __name__ == "__main__":
    asyncio.run(main()) 