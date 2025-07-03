import asyncio
import os
from dotenv import load_dotenv
from core.controller import launch_all_sessions
from adminbot.dispatcher import start_dispatcher
from telethon import TelegramClient

# Database sistemlerini import et
from core.db.connection import init_database, close_database
from core.profile_store import init_profile_store, close_profile_store
from utils.redis_client import init_redis, close_redis

def check_env_vars():
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    admin_token = os.getenv("ADMIN_BOT_TOKEN")
    if not api_id or not api_hash or not admin_token:
        print("❌ .env dosyasında eksik bilgi var! Lütfen TELEGRAM_API_ID, TELEGRAM_API_HASH ve ADMIN_BOT_TOKEN tanımlı mı kontrol et.")
        return False
    return True

async def init_all_databases():
    """Tüm database sistemlerini başlat"""
    print("🗄️ Database sistemleri başlatılıyor...")
    
    try:
        # PostgreSQL/SQLite başlat
        await init_database()
        print("✅ PostgreSQL/SQLite bağlantısı kuruldu")
        
        # MongoDB başlat
        await init_profile_store()
        print("✅ MongoDB/File-based profil sistemi başlatıldı")
        
        # Redis başlat
        await init_redis()
        print("✅ Redis bağlantısı kuruldu")
        
        return True
    except Exception as e:
        print(f"❌ Database başlatma hatası: {e}")
        return False

async def close_all_databases():
    """Tüm database bağlantılarını kapat"""
    print("🔒 Database bağlantıları kapatılıyor...")
    
    try:
        await close_database()
        await close_profile_store()
        await close_redis()
        print("✅ Tüm database bağlantıları kapatıldı")
    except Exception as e:
        print(f"⚠️ Database kapatma hatası: {e}")

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

    # Database sistemlerini başlat
    if not await init_all_databases():
        print("💥 Database sistemleri başlatılamadı, çıkılıyor...")
        return

    try:
        # 🔎 Admin ID yazdırma atlandı - session sorunlarını önlemek için
        # await print_admin_id()

        # 🧠 Admin botu geçici olarak devre dışı - event loop sorunu
        # admin_task = asyncio.create_task(asyncio.to_thread(start_dispatcher))

        # 💼 GavatBot şovcular - controller ile spam loop'ları başlat
        gavat_task = asyncio.create_task(launch_all_sessions())

        await asyncio.gather(gavat_task)
    
    except Exception as e:
        print(f"💥 Çalışma hatası: {e}")
    finally:
        # Database bağlantılarını kapat
        await close_all_databases()

if __name__ == "__main__":
    load_dotenv()
    if check_env_vars():
        try:
            asyncio.run(start_everything())
        except Exception as e:
            print(f"💥 Başlatma hatası: {e}")
