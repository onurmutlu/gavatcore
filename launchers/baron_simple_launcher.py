#!/usr/bin/env python3
"""Baron — GavatCore sistem hesabı (+905325566496)."""

import asyncio
import json
import os
import sys

from telethon import TelegramClient, events

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

PERSONA_FILE = "data/personas/baron.json"
DEFAULT_PHONE = "+905325566496"


class BaronSimpleLauncher:
    def __init__(self):
        self.client = None
        self.display_name = "Baron"
        self.phone = DEFAULT_PHONE

    def load_persona(self) -> None:
        if os.path.exists(PERSONA_FILE):
            with open(PERSONA_FILE, "r", encoding="utf-8") as f:
                persona = json.load(f)
            self.phone = persona.get("phone", DEFAULT_PHONE)
            self.display_name = persona.get("display_name", "Baron")

    async def start(self):
        self.load_persona()
        print(f"👑 {self.display_name} başlatılıyor...")

        clean_phone = self.phone.replace("+", "")
        session_path = f"sessions/_{clean_phone}"

        print(f"📱 Telefon: {self.phone}")
        print(f"💾 Session: {session_path}")

        self.client = TelegramClient(
            session_path,
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH,
            device_model=f"{self.display_name} Bot",
            system_version="GAVATCore v2.1",
        )

        login_code = os.getenv("TELEGRAM_LOGIN_CODE")
        twofa = os.getenv("TELEGRAM_2FA_PASSWORD")

        await self.client.start(
            phone=self.phone,
            code_callback=lambda: login_code or input("Please enter the code you received: "),
            password=twofa if twofa else lambda: __import__("getpass").getpass(
                "Please enter your password: "
            ),
        )
        me = await self.client.get_me()
        print(f"✅ {self.display_name} aktif: @{me.username or '—'} (ID: {me.id})")
        print(f"   Ad: {me.first_name} {me.last_name or ''}".strip())

        @self.client.on(events.NewMessage(incoming=True))
        async def handler(event):
            if event.is_private:
                sender = await event.get_sender()
                if sender and not getattr(sender, "bot", False):
                    name = getattr(sender, "first_name", "?")
                    print(f"💬 {self.display_name} DM: {name} -> {event.raw_text[:50]}...")

        print(f"🔥 {self.display_name} hazır — mesajları dinliyor!")
        await self.client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(BaronSimpleLauncher().start())
