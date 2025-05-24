import asyncio
import os
from telethon import TelegramClient, events
from core.gavat_client import GavatClient
from handlers.dm_handler import handle_message, handle_inline_bank_choice
from core.onboarding_flow import (
    start_onboarding,
    handle_onboarding_callback,
    handle_onboarding_text
)
from core.license_checker import LicenseChecker
from utils.scheduler_utils import spam_loop

SESSIONS_DIR = "sessions"

# ✅ Tüm session dosyalarını tara ve aktif hale getir
async def launch_all_sessions():
    session_files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".session")]
    clients = []

    for session_file in session_files:
        session_path = os.path.join(SESSIONS_DIR, session_file.replace(".session", ""))
        client = GavatClient(session_path)
        await client.client.connect()

        # 🧠 Event Handler: DM ve onboarding mesajları
        @client.client.on(events.NewMessage(incoming=True))
        async def unified_message_handler(event):
            if event.is_private:
                sender = await event.get_sender()
                user_id = sender.id
                session_created_at = LicenseChecker.get_session_creation_time(session_path)
                await handle_message(client.client, sender, event.raw_text, session_created_at)
                await handle_onboarding_text(event)

        # 💬 Event Handler: Inline button tıklamaları
        @client.client.on(events.CallbackQuery)
        async def unified_callback_handler(event):
            await handle_inline_bank_choice(event)
            await handle_onboarding_callback(event)

        # 🚀 Otomatik spam başlatılıyor (arka plan task olarak)
        asyncio.create_task(spam_loop(client.client))

        print(f"✅ {session_file} başlatıldı.")
        clients.append(client)

    # 🌐 Tüm client’ları çalışır halde tut
    await asyncio.gather(*(c.run() for c in clients))

if __name__ == "__main__":
    asyncio.run(launch_all_sessions())
