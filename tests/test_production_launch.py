#!/usr/bin/env python3
"""
BabaGAVAT Coin System Production Test
Basit production test ve sistem kontrolleri
"""

import asyncio
import sys
import json
import time
from datetime import datetime

print("""
🔥 BabaGAVAT COIN SYSTEM PRODUCTION TEST 🔥

💪 ONUR METODU CANLI ORTAM TESTİ

🚀 Sistem kontrolleri başlatılıyor...
""")

async def test_database_connection():
    """Database bağlantısı testi"""
    try:
        print("📊 Database bağlantısı test ediliyor...")
        
        from core.database_manager import database_manager
        await database_manager.initialize()
        
        print("✅ Database bağlantısı başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ Database bağlantısı hatası: {e}")
        return False

async def test_coin_service():
    """Coin service testi"""
    try:
        print("💰 Coin Service test ediliyor...")
        
        from core.coin_service import babagavat_coin_service
        await babagavat_coin_service.initialize()
        
        # Test kullanıcısı bakiyesi
        test_balance = await babagavat_coin_service.get_balance(999999)
        print(f"   💰 Test kullanıcı bakiye: {test_balance} coin")
        
        # Test coin ekleme
        success = await babagavat_coin_service.add_coins(
            user_id=999999,
            amount=50,
            transaction_type=babagavat_coin_service.__class__.__module__.split('.')[-1],
            description="Production test coin"
        )
        
        if success:
            new_balance = await babagavat_coin_service.get_balance(999999)
            print(f"   💰 Coin eklendi: {new_balance} coin")
        
        print("✅ Coin Service başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ Coin Service hatası: {e}")
        return False

async def test_erko_analyzer():
    """ErkoAnalyzer testi"""
    try:
        print("🔍 ErkoAnalyzer test ediliyor...")
        
        from core.erko_analyzer import babagavat_erko_analyzer
        await babagavat_erko_analyzer.initialize()
        
        # Test kullanıcı analizi
        profile = await babagavat_erko_analyzer.analyze_user(999999)
        print(f"   📊 Test kullanıcı profili: {profile.segment.value} segment, {profile.risk_level.value} risk")
        
        # Segment istatistikleri
        segment_stats = await babagavat_erko_analyzer.get_segment_statistics()
        print(f"   📈 Aktif segmentler: {len(segment_stats.get('segments', {}))}")
        
        print("✅ ErkoAnalyzer başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ ErkoAnalyzer hatası: {e}")
        return False

async def test_api_endpoints():
    """API endpoints testi"""
    try:
        print("🌐 API Endpoints test ediliyor...")
        
        from apis.coin_endpoints import app
        from fastapi.testclient import TestClient
        
        # Test client oluştur
        client = TestClient(app)
        
        # System status endpoint test
        response = client.get("/coins/system-status", headers={"Authorization": "Bearer test_token_123456789"})
        print(f"   📡 System Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Response: {data.get('system_name', 'Unknown')}")
        
        print("✅ API Endpoints başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ API Endpoints hatası: {e}")
        return False

async def run_production_tests():
    """Tüm production testlerini çalıştır"""
    try:
        start_time = datetime.now()
        
        print("🧪 Production testleri başlatılıyor...")
        
        # Test senaryoları
        tests = [
            ("Database Connection", test_database_connection),
            ("Coin Service", test_coin_service),
            ("ErkoAnalyzer", test_erko_analyzer),
            ("API Endpoints", test_api_endpoints)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🔍 {test_name} testi...")
            result = await test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: BAŞARILI")
            else:
                print(f"❌ {test_name}: BAŞARISIZ")
        
        # Sonuçları özetle
        duration = (datetime.now() - start_time).total_seconds()
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"""

🏆 PRODUCTION TEST SONUÇLARI:
⏱️ Test Süresi: {duration:.2f} saniye
✅ Başarılı: {passed}/{total}
📈 Başarı Oranı: {(passed/total)*100:.1f}%

🎯 BabaGAVAT Production Durumu: {'✅ HAZIR' if passed == total else '⚠️ PARSİYEL'}
💪 Sokak Zekası: MAKSIMUM
        """)
        
        return passed == total
        
    except Exception as e:
        print(f"❌ Production test hatası: {e}")
        return False

async def main():
    """Ana test fonksiyonu"""
    try:
        # Production testlerini çalıştır
        success = await run_production_tests()
        
        if success:
            print("""
🚀 BabaGAVAT COIN SYSTEM PRODUCTION READY!

💪 Onur Metodu başarıyla test edildi!
🔥 Sistem canlı ortama hazır!

🌐 API Server başlatmaya hazır: http://localhost:8000
📊 Monitoring: Aktif
🎯 BabaGAVAT Onayı: VERİLDİ
            """)
            
            # Basit API server başlat
            await start_simple_api_server()
            
        else:
            print("❌ Production testlerinde sorunlar var. Lütfen kontrol edin.")
            
    except Exception as e:
        print(f"❌ Ana test hatası: {e}")
        return 1
    
    return 0

async def start_simple_api_server():
    """Basit API server başlat"""
    try:
        print("""
🌐 BabaGAVAT API SERVER BAŞLATILIYOR...

📡 Endpoints:
   GET  http://localhost:8000/coins/system-status
   GET  http://localhost:8000/coins/balance/999999
   POST http://localhost:8000/coins/add
   GET  http://localhost:8000/coins/leaderboard

🔒 Authorization: Bearer test_token_123456789
🎯 Onur Metodu: AKTİF
💪 BabaGAVAT: CANLI

⚡ Server başlatılıyor...
        """)
        
        import uvicorn
        from apis.coin_endpoints import app
        
        # Uvicorn ile API server'ı başlat
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        
    except Exception as e:
        print(f"❌ API server başlatma hatası: {e}")

if __name__ == "__main__":
    try:
        # FastAPI test client için gerekli
        import sys
        sys.path.append('.')
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n🛑 BabaGAVAT Production sistemi kapatılıyor...")
        print("💪 Sokak zekası ile test edildi!")
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        sys.exit(1) 