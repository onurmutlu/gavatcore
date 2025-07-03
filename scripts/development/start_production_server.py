#!/usr/bin/env python3
"""
BabaGAVAT Coin System Production Server
Onur Metodu ile canlı ortam başlatıcısı
"""

import uvicorn
import asyncio
import sys
from datetime import datetime

# Core imports
from core.coin_service import babagavat_coin_service
from core.erko_analyzer import babagavat_erko_analyzer
from core.database_manager import database_manager
from apis.coin_endpoints import app

async def initialize_babagavat_production():
    """BabaGAVAT Production ortamını başlat"""
    try:
        print("""
🔥🔥🔥 BABAGAVAT COIN SYSTEM - PRODUCTION SERVER 🔥🔥🔥

💪 ONUR METODU CANLI ORTAM BAŞLATILIYOR!

🎯 Production Features:
✅ Coin Balance Management
✅ ErkoAnalyzer Segmentation  
✅ Risk Assessment System
✅ FastAPI Endpoints
✅ Real-time Monitoring
✅ Background Analytics
✅ Admin Panel Ready

🚀 BabaGAVAT'ın sokak zekası ile güçlendirilmiş sistem!

⚡ Production ortamı hazırlanıyor...
        """)
        
        # Database'i başlat
        print("📊 Database başlatılıyor...")
        await database_manager.initialize()
        
        # Coin service'i başlat  
        print("💰 Coin Service başlatılıyor...")
        await babagavat_coin_service.initialize()
        
        # ErkoAnalyzer'ı başlat
        print("🔍 ErkoAnalyzer başlatılıyor...")
        await babagavat_erko_analyzer.initialize()
        
        # Health check
        print("🔧 Sistem sağlık kontrolü...")
        test_balance = await babagavat_coin_service.get_balance(999999)
        print(f"   ✅ Coin Service test: {test_balance} coin")
        
        segment_stats = await babagavat_erko_analyzer.get_segment_statistics()
        print(f"   ✅ ErkoAnalyzer test: {len(segment_stats.get('segments', {}))} segment")
        
        print("""
✅ BabaGAVAT PRODUCTION HAZIR!

🌐 API Server: http://localhost:8000
📊 System Status: OPERATIONAL
💪 BabaGAVAT Approval: CONFIRMED
🎯 Onur Metodu: ACTIVE

🚀 API sunucusu başlatılıyor...
        """)
        
        return True
        
    except Exception as e:
        print(f"❌ Production initialization hatası: {e}")
        return False

def start_server():
    """API server'ı başlat"""
    try:
        print("""
🌐 BabaGAVAT COIN API SERVERİ BAŞLATILIYOR...

📡 API Endpoints:
   GET  /coins/balance/{user_id}
   POST /coins/add
   POST /coins/spend
   POST /coins/referral-bonus
   POST /coins/message-to-performer
   GET  /coins/leaderboard
   GET  /coins/system-status
   GET  /docs (Swagger Documentation)

🔒 Security: HTTPBearer Authentication
🎯 Onur Metodu: AKTİF
💪 BabaGAVAT: CANLI

⚡ Server başlatılıyor...
        """)
        
        # Uvicorn ile API server'ı başlat
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True,
            reload=False
        )
        
    except Exception as e:
        print(f"❌ API server başlatma hatası: {e}")
        return 1
    
    return 0

async def main():
    """Ana başlatma fonksiyonu"""
    try:
        # Production ortamını başlat
        success = await initialize_babagavat_production()
        
        if not success:
            print("❌ Production initialization başarısız!")
            return 1
        
        print("🎯 Production başarıyla başlatıldı! API server başlatılıyor...")
        
        # API server'ı başlat (blocking)
        return start_server()
        
    except Exception as e:
        print(f"❌ Ana başlatma hatası: {e}")
        return 1

if __name__ == "__main__":
    try:
        # Async initialization sonra sync server
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n🛑 BabaGAVAT Production Server kapatılıyor...")
        print("💪 Sokak zekası ile güçlendirilmiş sistem başarıyla çalıştı!")
        
    except Exception as e:
        print(f"❌ Server hatası: {e}")
        sys.exit(1) 