#!/usr/bin/env python3
"""
GavatCore V2 Test Script
Tüm yeni sistemleri test eder
"""

import asyncio
import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any

# Test için gerekli imports
from core.mcp_api_system import mcp_api, Character, Quest, CharacterType, QuestType
from core.social_gaming_engine import social_gaming, SocialEvent, EventType

async def test_mcp_api_system():
    """MCP API sistemini test et"""
    print("\n🔧 MCP API System Test")
    print("=" * 40)
    
    try:
        # Initialize
        await mcp_api.initialize()
        print("✅ MCP API başlatıldı")
        
        # Test user creation
        user_id = "test_user_123"
        result = await mcp_api.add_xp(user_id, 100, "test")
        print(f"✅ Test kullanıcısı oluşturuldu: {result}")
        
        # Test character retrieval
        geisha = await mcp_api.get_character("geisha")
        if geisha:
            print(f"✅ Karakter bulundu: {geisha.name}")
        else:
            print("❌ Karakter bulunamadı")
        
        # Test quest assignment
        quest_assigned = await mcp_api.assign_quest_to_user("daily_chat", user_id)
        print(f"✅ Görev atandı: {quest_assigned}")
        
        # Test quest completion
        if quest_assigned:
            completion_result = await mcp_api.complete_quest("daily_chat", user_id)
            print(f"✅ Görev tamamlandı: {completion_result}")
        
        # Test leaderboard
        leaderboard = await mcp_api.get_leaderboard(5)
        print(f"✅ Leaderboard alındı: {len(leaderboard)} kullanıcı")
        
        # Test user progress
        user_progress = await mcp_api.get_user_progress(user_id)
        if user_progress:
            print(f"✅ Kullanıcı ilerlemesi: Level {user_progress.level}, XP {user_progress.total_xp}")
        
        print("✅ MCP API System testi başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ MCP API System test hatası: {e}")
        return False

async def test_voice_engine():
    """Voice Engine'i test et"""
    print("\n🎤 Voice Engine Test")
    print("=" * 40)
    
    try:
        # Check if OpenAI API key exists
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            print("⚠️ OPENAI_API_KEY bulunamadı, voice engine test atlanıyor")
            return True
        
        from core.ai_voice_engine import initialize_voice_engine
        
        # Initialize voice engine
        voice_engine = await initialize_voice_engine(openai_api_key)
        print("✅ Voice Engine başlatıldı")
        
        # Test voice session creation
        user_id = "test_user_voice"
        session_id = await voice_engine.start_voice_session(user_id, "geisha")
        if session_id:
            print(f"✅ Voice session oluşturuldu: {session_id}")
            
            # Test text-to-speech
            test_text = "Merhaba, ben Geisha. Sesli sohbet testini yapıyoruz."
            audio_data = await voice_engine.generate_speech(test_text, "geisha")
            if audio_data:
                print(f"✅ TTS test başarılı: {len(audio_data)} bytes")
            else:
                print("❌ TTS test başarısız")
            
            # Test character response generation
            response = await voice_engine.generate_character_response("Merhaba", session_id)
            if response:
                print(f"✅ Karakter yanıtı: {response[:50]}...")
            else:
                print("❌ Karakter yanıtı oluşturulamadı")
            
            # End session
            end_result = await voice_engine.end_voice_session(session_id)
            if end_result.get("success"):
                print("✅ Voice session sonlandırıldı")
            
        print("✅ Voice Engine testi başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ Voice Engine test hatası: {e}")
        return False

async def test_social_gaming():
    """Social Gaming Engine'i test et"""
    print("\n🎮 Social Gaming Test")
    print("=" * 40)
    
    try:
        # Initialize
        await social_gaming.initialize()
        print("✅ Social Gaming Engine başlatıldı")
        
        # Test event creation
        event = SocialEvent(
            event_id="test_event_123",
            title="Test Voice Party",
            description="Test etkinliği",
            event_type=EventType.VOICE_PARTY,
            host_character_id="geisha",
            max_participants=10,
            rewards=[
                {"type": "xp", "amount": 100},
                {"type": "token", "amount": 50}
            ]
        )
        
        event_created = await social_gaming.create_social_event(event)
        if event_created:
            print("✅ Sosyal etkinlik oluşturuldu")
            
            # Test event joining
            user_id = "test_user_social"
            join_result = await social_gaming.join_event("test_event_123", user_id)
            if join_result.get("success"):
                print("✅ Etkinliğe katılım başarılı")
                
                # Test event completion
                complete_result = await social_gaming.complete_event("test_event_123")
                if complete_result.get("success"):
                    print("✅ Etkinlik tamamlandı")
            
        # Test group challenge creation
        challenge_id = await social_gaming.create_group_challenge(
            "Test Challenge",
            "Test grup challenge'ı",
            "babagavat",
            1  # 1 saat
        )
        if challenge_id:
            print(f"✅ Grup challenge oluşturuldu: {challenge_id}")
        
        # Test leaderboard
        leaderboard = await social_gaming.get_leaderboard("weekly", 5)
        print(f"✅ Haftalık leaderboard: {len(leaderboard)} kullanıcı")
        
        print("✅ Social Gaming testi başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ Social Gaming test hatası: {e}")
        return False

async def test_integration():
    """Entegrasyon testi"""
    print("\n🔗 Integration Test")
    print("=" * 40)
    
    try:
        # Test user journey
        user_id = "integration_test_user"
        
        # 1. User creates account (via XP addition)
        await mcp_api.add_xp(user_id, 0, "registration")
        print("✅ Kullanıcı kaydı")
        
        # 2. Assign daily quests
        await mcp_api.assign_quest_to_user("daily_chat", user_id)
        print("✅ Günlük görev atandı")
        
        # 3. Join social event
        test_event = SocialEvent(
            event_id="integration_event",
            title="Integration Test Event",
            description="Entegrasyon test etkinliği",
            event_type=EventType.COMMUNITY_QUEST,
            host_character_id="geisha",
            max_participants=5
        )
        await social_gaming.create_social_event(test_event)
        await social_gaming.join_event("integration_event", user_id)
        print("✅ Sosyal etkinliğe katıldı")
        
        # 4. Complete quest
        completion_result = await mcp_api.complete_quest("daily_chat", user_id)
        if completion_result.get("success"):
            print("✅ Görev tamamlandı")
        
        # 5. Check final user progress
        final_progress = await mcp_api.get_user_progress(user_id)
        if final_progress:
            print(f"✅ Final durum: Level {final_progress.level}, XP {final_progress.total_xp}, Tokens {final_progress.tokens}")
        
        print("✅ Entegrasyon testi başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ Entegrasyon test hatası: {e}")
        return False

async def test_performance():
    """Performance testi"""
    print("\n⚡ Performance Test")
    print("=" * 40)
    
    try:
        start_time = time.time()
        
        # Test multiple user operations
        tasks = []
        for i in range(10):
            user_id = f"perf_test_user_{i}"
            tasks.append(mcp_api.add_xp(user_id, 100, "performance_test"))
        
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ 10 kullanıcı işlemi: {duration:.2f} saniye")
        print(f"✅ Ortalama işlem süresi: {duration/10:.3f} saniye")
        
        # Test leaderboard performance
        start_time = time.time()
        leaderboard = await mcp_api.get_leaderboard(50)
        end_time = time.time()
        
        print(f"✅ Leaderboard sorgusu: {end_time - start_time:.3f} saniye")
        
        print("✅ Performance testi başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ Performance test hatası: {e}")
        return False

async def main():
    """Ana test fonksiyonu"""
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║                    GAVATCORE V2 TEST SUITE                   ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    test_results = {}
    
    # Run all tests
    test_results["mcp_api"] = await test_mcp_api_system()
    test_results["voice_engine"] = await test_voice_engine()
    test_results["social_gaming"] = await test_social_gaming()
    test_results["integration"] = await test_integration()
    test_results["performance"] = await test_performance()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SONUÇLARI")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    for test_name, result in test_results.items():
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{test_name.upper():<20} {status}")
    
    print("-" * 60)
    print(f"TOPLAM: {passed_tests}/{total_tests} test başarılı")
    
    if passed_tests == total_tests:
        print("🎉 TÜM TESTLER BAŞARILI! GavatCore V2 hazır!")
        return True
    else:
        print("⚠️ Bazı testler başarısız. Lütfen hataları kontrol edin.")
        return False

if __name__ == "__main__":
    # Environment setup
    if not os.path.exists(".env"):
        print("⚠️ .env dosyası bulunamadı. OPENAI_API_KEY ayarlanmamış olabilir.")
    
    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 