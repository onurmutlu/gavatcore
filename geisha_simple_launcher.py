#!/usr/bin/env python3
import asyncio
import json
import os
from telethon import TelegramClient, events
from telethon.tl.types import User
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
from datetime import datetime

class GeishaSimpleLauncher:
    def __init__(self):
        self.client = None
        
    async def start(self):
        print("💋 Geisha Bot başlatılıyor...")
        
        # Persona dosyasından telefon al
        with open('data/personas/xxxgeisha.json', 'r', encoding='utf-8') as f:
            persona = json.load(f)
        
        phone = persona.get('phone', '+905486306226')
        clean_phone = phone.replace('+', '')
        session_path = f'sessions/_{clean_phone}'
        
        print(f"📱 Telefon: {phone}")
        print(f"💾 Session: {session_path}")
        
        self.client = TelegramClient(
            session_path, TELEGRAM_API_ID, TELEGRAM_API_HASH,
            device_model="Geisha Bot", system_version="GAVATCore v2.0"
        )
        
        await self.client.start()
        me = await self.client.get_me()
        print(f"✅ Geisha aktif: @{me.username} (ID: {me.id})")
        
        @self.client.on(events.NewMessage(incoming=True))
        async def handler(event):
            if event.is_private:
                sender = await event.get_sender()
                if sender and not getattr(sender, 'bot', False):
                    print(f"💬 Geisha DM: {sender.first_name} -> {event.raw_text[:30]}...")
        
        print("🔥 Geisha hazır - mesajları dinliyor!")
        await self.client.run_until_disconnected()

if __name__ == "__main__":
    launcher = GeishaSimpleLauncher()
    asyncio.run(launcher.start())
