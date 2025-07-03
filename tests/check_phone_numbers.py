#!/usr/bin/env python3
"""
🔍 Telefon Numarası - Hesap Kontrolü 🔍
"""

import asyncio
from telethon import TelegramClient
from config import API_ID, API_HASH

async def check_phone_accounts():
    """Session numaralarının hangi hesaplara ait olduğunu kontrol eder"""
    
    numbers = [
        ('905382617727', '+905382617727'),
        ('905486306226', '+905486306226'), 
        ('905513272355', '+905513272355')
    ]
    
    print("🔍 Session-Hesap Eşleşmesi Kontrolü:\n")
    
    for session_num, phone in numbers:
        try:
            client = TelegramClient(f'sessions/_{session_num}', API_ID, API_HASH)
            await client.start()
            me = await client.get_me()
            print(f"📱 {phone} -> @{me.username} (ID: {me.id}) [{me.first_name}]")
            await client.disconnect()
        except Exception as e:
            print(f"❌ {phone} -> ERROR: {e}")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    asyncio.run(check_phone_accounts()) 