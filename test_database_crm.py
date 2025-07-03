#!/usr/bin/env python3
"""
GavatCore V2 - Database & AI CRM Test
Veritabanı ve AI CRM sistemlerini test eder
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
sys.path.append('.')

async def test_database_system():
    """Database sistemini test et"""
    print("🗄️ Database Manager testi başlatılıyor...")
    
    try:
        from core.database_manager import database_manager, BroadcastTarget, UserInteractionType
        
        # Database'i başlat
        await database_manager.initialize()
        print("✅ Database başlatıldı")
        
        # Test broadcast target'ı ekle
        test_target = BroadcastTarget(
            target_id="test_group_123",
            target_type="group",
            bot_username="test_bot",
            is_accessible=True,
            notes="Test grubu"
        )
        
        success = await database_manager.add_broadcast_target(test_target)
        print(f"✅ Broadcast target eklendi: {success}")
        
        # Broadcast target'ları al
        targets = await database_manager.get_broadcast_targets()
        print(f"✅ Broadcast targets alındı: {len(targets)} adet")
        
        # Test kullanıcı analytics
        await database_manager.update_user_analytics(
            user_id="test_user_123",
            username="test_user",
            interaction_data={
                "message_count": 5,
                "voice_minutes": 10,
                "quest_completed": True,
                "favorite_character": "geisha"
            }
        )
        print("✅ User analytics güncellendi")
        
        # User interaction kaydet
        await database_manager.log_user_interaction(
            user_id="test_user_123",
            interaction_type=UserInteractionType.MESSAGE,
            character_id="geisha",
            duration_seconds=120,
            metadata={"test": True}
        )
        print("✅ User interaction kaydedildi")
        
        # Grup analytics güncelle
        await database_manager.update_group_analytics(
            group_id="test_group_123",
            group_name="Test Grubu",
            member_count=50,
            bot_accessible=True
        )
        print("✅ Group analytics güncellendi")
        
        # CRM segment oluştur
        segment_success = await database_manager.create_crm_segment(
            segment_name="test_segment",
            criteria={"engagement_level": "high", "min_activity_score": 50},
            description="Test segmenti"
        )
        print(f"✅ CRM segment oluşturuldu: {segment_success}")
        
        # AI analizi için kullanıcı verilerini al
        users_for_ai = await database_manager.get_users_for_ai_analysis(10)
        print(f"✅ AI analizi için kullanıcı verileri alındı: {len(users_for_ai)} kullanıcı")
        
        # Broadcast stats al
        broadcast_stats = await database_manager.get_broadcast_stats(7)
        print(f"✅ Broadcast stats alındı: {broadcast_stats}")
        
        # User engagement report al
        engagement_report = await database_manager.get_user_engagement_report()
        print(f"✅ User engagement report alındı: {engagement_report}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test hatası: {e}")
        return False

async def test_ai_crm_system():
    """AI CRM sistemini test et"""
    print("\n🤖 AI CRM Analyzer testi başlatılıyor...")
    
    try:
        from core.ai_crm_analyzer import initialize_ai_crm_analyzer
        
        # AI CRM Analyzer'ı başlat (OpenAI key olmadan mock mode)
        ai_crm = await initialize_ai_crm_analyzer()
        print("✅ AI CRM Analyzer başlatıldı (mock mode)")
        
        # User segmentation analizi
        print("📊 User segmentation analizi...")
        segmentation_result = await ai_crm.analyze_user_segmentation(10)
        print(f"✅ User segmentation tamamlandı: {segmentation_result.get('segment', 'N/A')}")
        
        # Broadcast optimization analizi
        print("📢 Broadcast optimization analizi...")
        broadcast_opt = await ai_crm.analyze_broadcast_optimization()
        print(f"✅ Broadcast optimization tamamlandı: {len(broadcast_opt.get('optimal_times', []))} optimal zaman")
        
        # Churn prediction analizi
        print("⚠️ Churn prediction analizi...")
        churn_prediction = await ai_crm.predict_churn_risk()
        print(f"✅ Churn prediction tamamlandı: {churn_prediction.get('risk_level', 'N/A')} risk")
        
        # Engagement optimization analizi
        print("🎯 Engagement optimization analizi...")
        engagement_opt = await ai_crm.optimize_engagement()
        print(f"✅ Engagement optimization tamamlandı: {len(engagement_opt.get('engagement_strategies', []))} strateji")
        
        # Tam CRM analizi
        print("🔍 Tam CRM analizi...")
        full_analysis = await ai_crm.run_full_crm_analysis()
        print(f"✅ Tam CRM analizi tamamlandı: {full_analysis.get('summary', {}).get('total_analyses', 0)} analiz")
        
        return True
        
    except Exception as e:
        print(f"❌ AI CRM test hatası: {e}")
        return False

async def test_telegram_broadcaster():
    """Telegram Broadcaster sistemini test et"""
    print("\n📢 Telegram Broadcaster testi başlatılıyor...")
    
    try:
        from core.telegram_broadcaster import telegram_broadcaster
        
        # Mock client'lar ile başlat
        mock_clients = {
            "test_bot": None  # Gerçek client olmadan test
        }
        
        # Broadcaster'ı başlat (client'lar olmadan sadece queue test)
        print("✅ Telegram Broadcaster mock test")
        
        # Test broadcast'leri
        test_data = {
            "weekly_top_3": [
                {"username": "test_user1", "total_xp": 150},
                {"username": "test_user2", "total_xp": 120},
                {"username": "test_user3", "total_xp": 100}
            ]
        }
        
        # Leaderboard broadcast test
        broadcast_id = await telegram_broadcaster.broadcast_leaderboard_update(test_data)
        print(f"✅ Leaderboard broadcast test: {broadcast_id}")
        
        # Quest completed broadcast test
        quest_data = {
            "user_id": "test_user_123",
            "quest_title": "Test Quest",
            "xp_earned": 50
        }
        quest_broadcast_id = await telegram_broadcaster.broadcast_quest_completed(quest_data)
        print(f"✅ Quest broadcast test: {quest_broadcast_id}")
        
        # Level up broadcast test
        level_data = {
            "user_id": "test_user_123",
            "new_level": 5
        }
        level_broadcast_id = await telegram_broadcaster.broadcast_level_up(level_data)
        print(f"✅ Level up broadcast test: {level_broadcast_id}")
        
        # Social event broadcast test
        event_data = {
            "title": "Test Etkinliği",
            "event_type": "voice_party",
            "host_character": "geisha"
        }
        event_broadcast_id = await telegram_broadcaster.broadcast_social_event(event_data)
        print(f"✅ Social event broadcast test: {event_broadcast_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Telegram Broadcaster test hatası: {e}")
        return False

async def test_integration():
    """Entegrasyon testi"""
    print("\n🔗 Entegrasyon testi başlatılıyor...")
    
    try:
        from core.database_manager import database_manager, UserInteractionType
        from core.ai_crm_analyzer import initialize_ai_crm_analyzer
        from core.telegram_broadcaster import telegram_broadcaster
        
        # Gerçek bir kullanıcı senaryosu simüle et
        user_id = "integration_test_user"
        
        # 1. Kullanıcı aktivitesi kaydet
        await database_manager.update_user_analytics(
            user_id=user_id,
            username="integration_user",
            interaction_data={
                "message_count": 10,
                "voice_minutes": 25,
                "quest_completed": True,
                "event_joined": True,
                "favorite_character": "geisha"
            }
        )
        
        # 2. Detaylı etkileşimler kaydet
        for i in range(5):
            await database_manager.log_user_interaction(
                user_id=user_id,
                interaction_type=UserInteractionType.MESSAGE,
                character_id="geisha",
                duration_seconds=60 + i * 10,
                metadata={"session": f"test_session_{i}"}
            )
        
        # 3. AI analizi yap
        ai_crm = await initialize_ai_crm_analyzer()
        analysis = await ai_crm.analyze_user_segmentation(1)
        
        # 4. Analiz sonucuna göre broadcast gönder
        if analysis and not analysis.get("error"):
            broadcast_data = {
                "user_id": user_id,
                "analysis_result": analysis.get("segment", "unknown"),
                "engagement_score": analysis.get("engagement_score", 0)
            }
            
            # Custom broadcast gönder
            custom_message = f"🎯 Kullanıcı {user_id} analiz edildi!\n"
            custom_message += f"📊 Segment: {analysis.get('segment', 'N/A')}\n"
            custom_message += f"⭐ Engagement Score: {analysis.get('engagement_score', 0)}\n"
            custom_message += f"💡 Öneriler: {', '.join(analysis.get('recommendations', [])[:2])}"
            
            broadcast_id = await telegram_broadcaster.broadcast_custom_message(
                message=custom_message,
                target_types=["group"],
                priority="normal"
            )
            
            print(f"✅ Entegrasyon testi tamamlandı - Broadcast ID: {broadcast_id}")
        
        # 5. Sistem metrikleri al
        broadcast_stats = await database_manager.get_broadcast_stats(1)
        engagement_report = await database_manager.get_user_engagement_report()
        
        print(f"📊 Sistem Metrikleri:")
        print(f"   - Broadcast Stats: {broadcast_stats}")
        print(f"   - Engagement Report: {engagement_report}")
        
        return True
        
    except Exception as e:
        print(f"❌ Entegrasyon test hatası: {e}")
        return False

async def main():
    """Ana test fonksiyonu"""
    print("🧪 GavatCore V2 Database & AI CRM Test Başlatılıyor...\n")
    
    results = {}
    
    # Database test
    results["database"] = await test_database_system()
    
    # AI CRM test
    results["ai_crm"] = await test_ai_crm_system()
    
    # Telegram Broadcaster test
    results["telegram_broadcaster"] = await test_telegram_broadcaster()
    
    # Entegrasyon test
    results["integration"] = await test_integration()
    
    # Sonuçları özetle
    print("\n" + "="*50)
    print("🎯 TEST SONUÇLARI:")
    print("="*50)
    
    for test_name, success in results.items():
        status = "✅ BAŞARILI" if success else "❌ BAŞARISIZ"
        print(f"{test_name.upper()}: {status}")
    
    total_tests = len(results)
    successful_tests = sum(results.values())
    
    print(f"\n📊 ÖZET: {successful_tests}/{total_tests} test başarılı")
    
    if successful_tests == total_tests:
        print("🎉 Tüm testler başarıyla geçti!")
        print("\n🚀 GavatCore V2 Database & AI CRM sistemi hazır!")
        print("\n💡 Özellikler:")
        print("   ✅ Veritabanı temelli broadcast yönetimi")
        print("   ✅ AI-powered kullanıcı analizi")
        print("   ✅ CRM segmentasyonu")
        print("   ✅ Churn prediction")
        print("   ✅ Engagement optimization")
        print("   ✅ Telegram broadcast entegrasyonu")
        print("   ✅ Real-time analytics")
    else:
        print("⚠️ Bazı testler başarısız oldu. Lütfen hataları kontrol edin.")

if __name__ == "__main__":
    asyncio.run(main()) 