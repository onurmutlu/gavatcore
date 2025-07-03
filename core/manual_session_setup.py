"""
Bu dosya sadece sistemdeki AI botlar (Geisha, Lara, GavatBaba) için
manuel oturum kurulumunda kullanılır. Kullanıcılar bu dosyayı asla görmez.
"""
# core/manual_session_setup.py
import os
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

SESSIONS_DIR = "sessions"

async def create_session_flow():
    api_id = int(os.getenv("TELEGRAM_API_ID"))
    api_hash = os.getenv("TELEGRAM_API_HASH")

    print("📲 Yeni şovcu girişi başlatılıyor...")
    phone = input("📞 Telefon numaranızı girin (örn: +905xxxxxxxxx): ").strip()

    session_name = phone.replace("+", "_")
    session_path = os.path.join(SESSIONS_DIR, f"{session_name}")
    
    client = TelegramClient(session_path, api_id, api_hash)

    await client.connect()
    if not await client.is_user_authorized():
        try:
            await client.send_code_request(phone)
            code = input("🔐 Telegram'dan gelen kodu girin: ").strip()
            try:
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                pw = input("🔒 2FA şifrenizi girin: ").strip()
                await client.sign_in(password=pw)
        except Exception as e:
            print(f"❌ Giriş başarısız: {e}")
            return None

    me = await client.get_me()
    print(f"✅ Giriş başarılı: {me.first_name} ({me.username})")
    await client.disconnect()
    return session_path

if __name__ == "__main__":
    asyncio.run(create_session_flow())
