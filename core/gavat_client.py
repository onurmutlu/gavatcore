# core/gavat_client.py
import os
import asyncio
import random
import json
import datetime
from telethon import TelegramClient, events, Button
from handlers.dm_handler import handle_message, handle_inline_bank_choice
from core.license_checker import LicenseChecker
from core.profile_loader import load_profile

class GavatClient:
    def __init__(self, session_path: str):
        self.session_path = session_path
        self.api_id = int(os.getenv("TELEGRAM_API_ID"))
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.client = TelegramClient(self.session_path, self.api_id, self.api_hash)
        self.license_checker = LicenseChecker()

    def get_random_engaging_message(self, username=None):
        """Kullanıcının profilinden ya da template’ten rastgele bir mesaj döndürür."""
        try:
            if username:
                profile = load_profile(username)
                if profile.get("engaging_messages"):
                    return random.choice(profile["engaging_messages"])
            # fallback template
            with open('data/group_spam_messages.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return random.choice(data["_template"]["engaging_messages"])
        except Exception as e:
            print(f"[⚠️] Mesajlar yüklenirken hata: {e}")
            return "Merhaba! Nasılsınız?"

    def get_session_created_at(self):
        """
        Gerçek session oluşturulma zamanını belirlemek için lisans dosyasına bakar.
        """
        session_file = os.path.basename(self.session_path)
        user_id = int(session_file.split('.')[0].replace("user_", ""))
        return self.license_checker.get_session_creation_time(user_id)

    async def run(self):
        await self.client.start()
        me = await self.client.get_me()
        username = me.username or f"user_{me.id}"
        print(f"\U0001F9E0 [{username}] olarak çalışıyor...")

        session_created_at = self.get_session_created_at()

        @self.client.on(events.NewMessage(incoming=True))
        async def handler(event):
            if event.is_private:
                sender = await event.get_sender()
                message_text = event.raw_text
                print(f"\U0001F4E9 DM geldi: {sender.username or sender.id} - {message_text}")
                await handle_message(self.client, sender, message_text, session_created_at)

        @self.client.on(events.CallbackQuery)
        async def inline_handler(event):
            await handle_inline_bank_choice(event)

        await self.client.run_until_disconnected()
