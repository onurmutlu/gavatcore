#!/usr/bin/env python3
"""Baron — GavatCore sistem hesabı (+905325566496)."""

import argparse
import asyncio
import json
import os
import sys

from telethon import TelegramClient, events

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

PERSONA_FILE = "data/personas/baron.json"
DEFAULT_PHONE = "+905325566496"


def _resolve_onay_kodu(cli_value: str | None = None) -> str | None:
    """SMS onay kodu: CLI > TELEGRAM_ONAY_KODU > ONAY_KODU > TELEGRAM_LOGIN_CODE."""
    if cli_value:
        return cli_value.strip()
    for key in ("TELEGRAM_ONAY_KODU", "ONAY_KODU", "TELEGRAM_LOGIN_CODE"):
        value = os.getenv(key)
        if value and value.strip():
            return value.strip()
    return None


def _resolve_onay_sifresi(cli_value: str | None = None) -> str | None:
    """2FA onay şifresi: CLI > TELEGRAM_ONAY_SIFRESI > ONAY_SIFRESI > TELEGRAM_2FA_PASSWORD."""
    if cli_value:
        return cli_value.strip()
    for key in ("TELEGRAM_ONAY_SIFRESI", "ONAY_SIFRESI", "TELEGRAM_2FA_PASSWORD"):
        value = os.getenv(key)
        if value and value.strip():
            return value.strip()
    return None


class BaronSimpleLauncher:
    def __init__(
        self,
        onay_kodu: str | None = None,
        onay_sifresi: str | None = None,
    ):
        self.client = None
        self.display_name = "Baron"
        self.phone = DEFAULT_PHONE
        self.onay_kodu = onay_kodu
        self.onay_sifresi = onay_sifresi

    def load_persona(self) -> None:
        if os.path.exists(PERSONA_FILE):
            with open(PERSONA_FILE, "r", encoding="utf-8") as f:
                persona = json.load(f)
            self.phone = persona.get("phone", DEFAULT_PHONE)
            self.display_name = persona.get("display_name", "Baron")

    def _code_callback(self):
        kod = _resolve_onay_kodu(self.onay_kodu)
        if kod:
            print("🔑 Onay kodu ortam/argümandan alındı.")
            return kod
        return input("🔑 Telegram onay kodunu girin: ").strip()

    def _password_callback(self):
        sifre = _resolve_onay_sifresi(self.onay_sifresi)
        if sifre:
            print("🔒 Onay şifresi ortam/argümandan alındı.")
            return sifre
        import getpass

        return getpass.getpass("🔒 Telegram onay şifresini girin (2FA): ")

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

        await self.client.connect()
        if not await self.client.is_user_authorized():
            print("⚠️ Session geçersiz veya süresi dolmuş — onay kodu/şifre gerekli.")
            onay_sifresi = _resolve_onay_sifresi(self.onay_sifresi)
            await self.client.start(
                phone=self.phone,
                code_callback=self._code_callback,
                password=onay_sifresi if onay_sifresi else self._password_callback,
            )
        else:
            print("✅ Mevcut session ile giriş yapıldı (onay kodu gerekmedi).")
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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Baron Telegram launcher")
    parser.add_argument(
        "--onay-kodu",
        dest="onay_kodu",
        metavar="KOD",
        help="Telegram SMS onay kodu (veya TELEGRAM_ONAY_KODU env)",
    )
    parser.add_argument(
        "--onay-sifre",
        dest="onay_sifresi",
        metavar="SIFRE",
        help="Telegram 2FA onay şifresi (veya TELEGRAM_ONAY_SIFRESI env)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(
        BaronSimpleLauncher(
            onay_kodu=args.onay_kodu,
            onay_sifresi=args.onay_sifresi,
        ).start()
    )
