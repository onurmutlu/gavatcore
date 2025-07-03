#!/usr/bin/env python3

import asyncio
from core.account_monitor import account_monitor
from core.gavat_client import GavatClient

async def test_spambot_debug():
    """SpamBot debug testi"""
    
    try:
        # Yayincilara client'ını başlat
        client = GavatClient("sessions/yayincilara.session")
        
        if not await client.start():
            print("❌ Client başlatılamadı")
            return
        
        print("✅ Client başlatıldı")
        
        # Manuel SpamBot kontrolü
        await account_monitor.manual_spambot_check(client.client, "yayincilara")
        
        print("🔍 SpamBot kontrolü tamamlandı, logları kontrol edin")
        
    except Exception as e:
        print(f"💥 Test hatası: {e}")

if __name__ == "__main__":
    asyncio.run(test_spambot_debug()) 