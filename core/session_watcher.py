# core/session_watcher.py

import os
import asyncio
import logging
from telethon import TelegramClient
from aiogram import Bot
from config import (
    TELEGRAM_API_ID,
    TELEGRAM_API_HASH,
    ADMIN_BOT_TOKEN,
    GAVATCORE_ADMIN_ID,
)

SESSIONS_DIR = "sessions"
CHECK_INTERVAL = 300  # saniye

bot = Bot(token=ADMIN_BOT_TOKEN, parse_mode="HTML")
logging.basicConfig(level=logging.INFO)

async def send_bot_dm(user_id: int, msg: str):
    try:
        await bot.send_message(user_id, msg)
    except Exception as e:
        logging.error(f"[DM] Gönderilemedi (user: {user_id}): {e}")

async def watch_sessions():
    while True:
        session_files = [
            f for f in os.listdir(SESSIONS_DIR)
            if f.endswith('.session')
        ]
        for session_file in session_files:
            username = session_file.replace(".session", "")
            session_path = os.path.join(SESSIONS_DIR, session_file)
            try:
                async with TelegramClient(session_path, TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
                    if not await client.is_user_authorized():
                        await notify_session_down(username)
            except Exception as e:
                await notify_session_down(username, error=str(e))
        await asyncio.sleep(CHECK_INTERVAL)

async def notify_session_down(username, error=None):
    # Admin'e DM
    msg_admin = (
        f"⚠️ <b>Dikkat:</b> <code>{username}</code> oturumu düştü veya bağlantı sorunu var."
    )
    if error:
        msg_admin += f"\n<b>Detay:</b> <code>{error}</code>"
    await send_bot_dm(int(GAVATCORE_ADMIN_ID), msg_admin)
    logging.error(f"[WATCHER] {username} session düştü: {error}")

    # Şovcuya da DM (eğer user_id biliniyorsa)
    showcu_id = get_performer_user_id(username)
    if showcu_id:
        msg_showcu = (
            "⚠️ Oturumunuz sistemde kapalı görünüyor. Lütfen tekrar giriş yapın veya destek ekibiyle iletişime geçin."
        )
        await send_bot_dm(int(showcu_id), msg_showcu)

def get_performer_user_id(username: str):
    """
    Önce yeni personas’dan, yoksa user_profiles.json’dan arar.
    """
    # Yeni sistem: data/personas/{username}.json
    persona_path = os.path.join("data/personas", f"{username}.json")
    if os.path.exists(persona_path):
        import json
        try:
            with open(persona_path, "r", encoding="utf-8") as f:
                p = json.load(f)
                # id varsa, yoksa username’i döndür
                return p.get("telegram_user_id") or p.get("user_id")
        except Exception:
            pass

    # Eski sistem: data/user_profiles.json
    try:
        from utilities.file_utils import load_json
        profiles = load_json("data/user_profiles.json", default={})
        for user_id, profile in profiles.items():
            if profile.get("username") == username:
                return user_id
    except Exception:
        pass
    return None

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.create_task(watch_sessions())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Session watcher durduruldu.")
