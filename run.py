import asyncio
import os
from dotenv import load_dotenv
from core.controller import launch_all_sessions
from adminbot.dispatcher import start_dispatcher
from telethon import TelegramClient

def check_env_vars():
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    admin_token = os.getenv("ADMIN_BOT_TOKEN")
    if not api_id or not api_hash or not admin_token:
        print("❌ .env dosyasında eksik bilgi var! Lütfen TELEGRAM_API_ID, TELEGRAM_API_HASH ve ADMIN_BOT_TOKEN tanımlı mı kontrol et.")
        return False
    return True

async def print_admin_id():
    api_id = int(os.getenv("TELEGRAM_API_ID"))
    api_hash = os.getenv("TELEGRAM_API_HASH")
    client = TelegramClient("temp_admin_id_check", api_id, api_hash)
    await client.start()
    me = await client.get_me()
    print(f"🆔 [Admin User ID'n]: {me.id} — bunu .env dosyasındaki `GAVATCORE_ADMIN_ID` alanına yapıştır kanka.")
    await client.disconnect()

async def start_everything():
    print("🚀 GAVATCORE başlatılıyor...")

    # 🔎 Admin ID yaz
    await print_admin_id()

    # 🧠 Admin botu thread'de başlat
    admin_task = asyncio.create_task(asyncio.to_thread(start_dispatcher))

    # 💼 GavatBot şovcular
    gavat_task = asyncio.create_task(launch_all_sessions())

    await asyncio.gather(admin_task, gavat_task)

if __name__ == "__main__":
    load_dotenv()
    if check_env_vars():
        try:
            asyncio.run(start_everything())
        except Exception as e:
            print(f"💥 Başlatma hatası: {e}")
