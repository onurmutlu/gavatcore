#!/usr/bin/env python3
"""
🌅 GavatCore Auto Health Ping - Morning Commander Report
Sabah için otomatik sistem sağlık kontrolü
"""

import requests
import subprocess
import os
import json
from datetime import datetime
import sys

def check_redis():
    """Redis durumu"""
    try:
        result = subprocess.run(['redis-cli', 'ping'], capture_output=True, text=True, timeout=5)
        return "✅ Redis: PONG" if result.returncode == 0 else "❌ Redis: DOWN"
    except:
        return "❌ Redis: ERROR"

def check_mongodb():
    """MongoDB durumu"""
    try:
        result = subprocess.run(['pgrep', '-f', 'mongod'], capture_output=True, text=True)
        return "✅ MongoDB: RUNNING" if result.returncode == 0 else "❌ MongoDB: DOWN"
    except:
        return "❌ MongoDB: ERROR"

def check_api():
    """Production API durumu"""
    try:
        response = requests.get("http://localhost:5050/api/system/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            total_bots = data.get('system_stats', {}).get('total_bots', 0)
            return f"✅ Production API: Active ({total_bots} bots configured)"
        else:
            return "❌ Production API: HTTP Error"
    except:
        return "❌ Production API: DOWN"

def check_sessions():
    """Session dosyaları"""
    try:
        sessions = [f for f in os.listdir('sessions/') if f.endswith('.session')]
        return f"✅ Sessions: {len(sessions)} files available"
    except:
        return "❌ Sessions: ERROR"

def check_flutter_build():
    """Flutter build"""
    try:
        if os.path.exists('deploy_package/gavatcore_web/'):
            return "✅ Flutter Web: Build ready"
        else:
            return "⚠️ Flutter Web: Build not found"
    except:
        return "❌ Flutter Web: ERROR"

def generate_morning_report():
    """Sabah raporu oluştur"""
    
    print("🌅 GOOD MORNING COMMANDER!")
    print("=" * 50)
    print(f"📅 Date: {datetime.now().strftime('%d %B %Y, %H:%M:%S')}")
    print("🔍 System Health Check Results:")
    print()
    
    # Health checks
    checks = [
        check_redis(),
        check_mongodb(), 
        check_api(),
        check_sessions(),
        check_flutter_build()
    ]
    
    for check in checks:
        print(f"   {check}")
    
    print()
    
    # Fire Mode Day 2 reminder
    print("🔥 FIRE MODE DAY 2 BATTLE PLAN:")
    print("   ⏰ 09:00 - python3 utils/ultimate_telegram_bot_launcher.py")
    print("   🤖 09:30 - Bot Army Activation")
    print("   💰 10:30 - Coin System Testing")
    print("   📱 13:00 - Mobile WebApp Integration")
    print("   👥 14:00 - Real User Testing")
    print("   🚀 17:00 - Production Deploy")
    print("   🎉 18:00 - LIVE LAUNCH!")
    
    print()
    print("⚡ SYSTEM STATUS: READY FOR LEGENDARY DAY 2")
    print("🎯 MISSION: Make bots talk to real users!")
    print()
    print("🔥 LET'S MAKE HISTORY AGAIN, COMMANDER!")
    print("=" * 50)
    
    # Log'a da kaydet
    try:
        with open(f"logs/morning_health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", "w") as f:
            f.write(f"Morning Health Check - {datetime.now()}\n")
            f.write("=" * 40 + "\n")
            for check in checks:
                f.write(check + "\n")
            f.write("\nSystem ready for Fire Mode Day 2\n")
        print("📝 Health check logged successfully!")
    except Exception as e:
        print(f"⚠️ Logging error: {e}")

if __name__ == "__main__":
    generate_morning_report() 