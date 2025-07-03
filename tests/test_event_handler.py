#!/usr/bin/env python3
# test_event_handler.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import asyncio
from telethon import TelegramClient, events
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

async def test_event_handler():
    """Geisha bot'unun event handler'ını test et"""
    
    # Geisha bot session'ını kullan
    client = TelegramClient('sessions/bot_geishaniz', TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    try:
        await client.start()
        me = await client.get_me()
        print(f"✅ Bot başlatıldı: {me.username} (ID: {me.id})")
        
        # Event handler ekle
        @client.on(events.NewMessage(incoming=True))
        async def message_handler(event):
            print(f"📨 MESAJ YAKALANDI: {event.raw_text}")
            print(f"🔍 Event türü: private={event.is_private}, group={event.is_group}, channel={event.is_channel}")
            if event.is_private:
                print(f"🔒 PRIVATE MESSAGE: {event.raw_text}")
                sender = await event.get_sender()
                print(f"👤 Gönderen: {sender.username or sender.first_name} (ID: {sender.id})")
            elif event.is_group:
                print(f"👥 GROUP MESSAGE: {event.raw_text}")
            else:
                print(f"❓ UNKNOWN MESSAGE TYPE: {event.raw_text}")
        
        print("🎧 Event handler aktif. 10 saniye bekliyor...")
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"💥 Test hatası: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_event_handler()) 