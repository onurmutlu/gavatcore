#!/usr/bin/env python3
"""
BabaGAVAT Quick API Test
Hızlı API endpoint testi
"""

import asyncio
import requests
import json
from datetime import datetime

async def quick_api_test():
    """Hızlı API test"""
    try:
        print("""
🔥 BabaGAVAT QUICK API TEST

🎯 Test edilen endpoints:
- System Status
- Balance Query
- Leaderboard

🚀 Test başlatılıyor...
        """)
        
        # Test verileri
        base_url = "http://localhost:8000"
        headers = {"Authorization": "Bearer test_token_123456789"}
        
        # Önce uvicorn'u doğrudan başlat
        print("🌐 API Server başlatılıyor...")
        
        # Test 1: System Status
        try:
            response = requests.get(f"{base_url}/coins/system-status", headers=headers, timeout=5)
            print(f"✅ System Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   📊 System: {data.get('system_name', 'Unknown')}")
        except Exception as e:
            print(f"❌ System Status hatası: {e}")
        
        # Test 2: Balance Query
        try:
            response = requests.get(f"{base_url}/coins/balance/999999", headers=headers, timeout=5)
            print(f"✅ Balance Query: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   💰 Balance: {data.get('balance', 0)} coin")
        except Exception as e:
            print(f"❌ Balance Query hatası: {e}")
        
        # Test 3: Leaderboard
        try:
            response = requests.get(f"{base_url}/coins/leaderboard", headers=headers, timeout=5)
            print(f"✅ Leaderboard: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   🏆 Top Users: {len(data.get('leaderboard', []))}")
        except Exception as e:
            print(f"❌ Leaderboard hatası: {e}")
        
        print("✅ API test tamamlandı!")
        
    except Exception as e:
        print(f"❌ Quick API test hatası: {e}")

def start_simple_server():
    """Basit server başlat"""
    try:
        import uvicorn
        from api.coin_endpoints import app
        
        print("🌐 Basit API server başlatılıyor...")
        
        # Background'da server başlat
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
        
    except Exception as e:
        print(f"❌ Server başlatma hatası: {e}")

if __name__ == "__main__":
    try:
        # Async test
        asyncio.run(quick_api_test())
        
    except Exception as e:
        print(f"❌ Test hatası: {e}") 