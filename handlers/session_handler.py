# // handlers/session_handler.py

import os
from telethon import events
from core.session_manager import is_session_active  # refresh_session_for_user opsiyonel
from utils.log_utils import log_event

# Sadece özel mesajlarda geçerli olan komutlar

async def handle_session_command(event):
    if not event.is_private:
        return

    sender = await event.get_sender()
    user_id = sender.id
    username = sender.username or f"user_{user_id}"
    message = event.raw_text.strip().lower()

    # ✅ Oturum dosyası durumu kontrol
    if message == "/session_durum":
        session_file = f"sessions/{username}.session"
        if os.path.exists(session_file):
            await event.respond("✅ Oturum dosyası mevcut. Bağlantı aktif olabilir.")
        else:
            await event.respond("❌ Oturum dosyası bulunamadı. Yeniden giriş yapılması gerekebilir.")
        log_event(username, "📡 /session_durum komutu çalıştırıldı.")

    # 🔄 Oturum yenileme (şimdilik manuel işlem önerilir)
    elif message == "/session_yenile":
        await event.respond(
            "♻️ Oturum yenileme işlemi başlatılmalı. Bu işlem şu an manuel yapılmalıdır.\n"
            "Lütfen yeniden giriş için @GavatBaba ile iletişime geçin."
        )
        log_event(username, "♻️ /session_yenile komutu çalıştırıldı.")
