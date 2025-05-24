# // adminbot/dispatcher.py

import os
from telethon import TelegramClient, events
from adminbot.commands import handle_admin_command
from core.onboarding_flow import (
    start_onboarding,
    handle_onboarding_callback,
    handle_onboarding_text
)
from handlers.dm_handler import handle_inline_bank_choice
from handlers.user_commands import handle_user_command
from handlers.session_handler import handle_session_command
from handlers.inline_handler import inline_handler  # ✅ Yeni handler dahil edildi

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN")

admin_bot = TelegramClient('adminbot', API_ID, API_HASH).start(bot_token=ADMIN_BOT_TOKEN)

# ✅ Admin komutları
@admin_bot.on(events.NewMessage(pattern=r"^/"))
async def admin_command_handler(event):
    if event.is_private:
        await handle_admin_command(admin_bot, event)

# ✅ Şovcu onboarding başlatıcı
@admin_bot.on(events.NewMessage(pattern=r"^/basla$"))
async def onboarding_entry(event):
    if event.is_private:
        await start_onboarding(admin_bot, event)

# ✅ Inline button handler (onboarding + banka seçimleri + gelecekteki butonlar)
@admin_bot.on(events.CallbackQuery)
async def callback_query_handler(event):
    await inline_handler(event)

# ✅ Kullanıcıdan gelen metin inputları
@admin_bot.on(events.NewMessage(incoming=True))
async def universal_private_handler(event):
    if event.is_private:
        text = event.raw_text.strip().lower()
        if text.startswith("/"):
            await handle_user_command(event)
            await handle_session_command(event)
        else:
            await handle_onboarding_text(event)  # onboarding devamı

def start_dispatcher():
    print("🤖 AdminBot aktif! Tüm komutlar ve onboarding başlatıldı.")
    admin_bot.run_until_disconnected()
