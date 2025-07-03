#!/usr/bin/env python3
import asyncio
import os
import sys
import random
from datetime import datetime
from telethon import TelegramClient, events

# Config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

async def main():
    sessions = ["sessions/babagavat_conversation.session", "sessions/yayincilara_conversation.session", "sessions/xxxgeisha_conversation.session"]
    print("🚀 Mini Bot Launcher başlıyor...")
    print("🔥 3 BOT FULL YAYIN MODU!")
    
    clients = []
    for i, session in enumerate(sessions):
        name = session.split('/')[1].split('_')[0]
        print(f"▶️ {name} botu başlatılıyor...")
        
        client = TelegramClient(session, TELEGRAM_API_ID, TELEGRAM_API_HASH)
        await client.start()
        me = await client.get_me()
        print(f"✅ {name} ({me.first_name}) aktif!")
        
        # Mesaj handler'ı
        @client.on(events.NewMessage())
        async def handler(event):
            if event.is_private:
                sender = await event.get_sender()
                if sender and not sender.bot:
                    username = sender.first_name
                    print(f"💬 {name}: {username} mesaj gönderdi")
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    await event.respond(f"Merhaba {username}! Ben {name}, nasıl yardımcı olabilirim?")
        
        clients.append(client)
        
    print("\n🎉 Tüm botlar aktif! Ctrl+C ile durdur.\n")
    
    # Botları beklet
    await asyncio.gather(*[client.run_until_disconnected() for client in clients])

if __name__ == "__main__":
    asyncio.run(main()) 