# handlers/session_handler.py

import asyncio
import os
from telethon import events
from dotenv import load_dotenv
from core.session_manager import open_session
from core.profile_loader import update_profile
from core.analytics_logger import log_analytics
from utilities.log_utils import log_event

load_dotenv()
ADMIN_ID = int(os.getenv("GAVATCORE_ADMIN_ID", "0"))
SYSTEM_PHONE = os.getenv("GAVATCORE_SYSTEM_PHONE", "")

SESSION_ONBOARD_STATE = {}

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

async def handle_session_command(event):
    """
    Komut bazlı session yönetimi (örn: /session_ac +905xxxxxxxxx, /session_kapat +905xxxxxxxxx).
    """
    text = event.raw_text.strip().lower()
    sender = await event.get_sender()
    user_id = sender.id

    if text.startswith("/session_ac"):
        parts = text.split()
        if len(parts) < 2:
            await event.respond("Kullanım: /session_ac +905xxxxxxxxx")
            return
        phone = parts[1]
        # Admin değilse sadece kendi numarası
        if not is_admin(user_id) and phone != SYSTEM_PHONE:
            await event.respond("⛔️ Sadece kendi hesabınız için oturum açabilirsiniz.")
            return
        await start_session_onboarding(event, user_id, phone)
    elif text.startswith("/session_kapat"):
        parts = text.split()
        if len(parts) < 2:
            await event.respond("Kullanım: /session_kapat +905xxxxxxxxx")
            return
        phone = parts[1]
        await terminate_session(event, phone)
    else:
        await event.respond("Bilinmeyen session komutu.")

async def start_session_onboarding(event, user_id, phone=None):
    """
    Session onboarding başlatır.
    """
    username = (await event.get_sender()).username or f"user_{user_id}"
    if not phone:
        await event.respond(
            "📞 Telefon numarasını başında + ile yaz (örn: +905xxxxxxxxx):\n"
            "Yalnızca kendi hesabınızı ya da adminseniz sistem hesabını açabilirsiniz."
        )
        SESSION_ONBOARD_STATE[user_id] = {
            "step": 1,
            "initiator_id": user_id,
            "initiator_username": username,
        }
        log_event(user_id, "session_onboard_started")
        log_analytics(user_id, "session_onboard_started", {"username": username})
        return
    else:
        # Admin kontrolü burada da olsun
        if not is_admin(user_id) and phone != SYSTEM_PHONE:
            await event.respond("⛔️ Sadece kendi hesabınız için oturum açabilirsiniz.")
            return
        await event.respond("✅ Kod gönderildi. Lütfen Telegram’dan gelen onay kodunu girin:")
        asyncio.create_task(start_session_flow(event, user_id, phone))

@events.register(events.NewMessage(incoming=True, pattern=None))
async def onboarding_text_handler(event):
    user_id = event.sender_id
    state = SESSION_ONBOARD_STATE.get(user_id)
    if not state:
        return

    step = state.get("step", 0)
    initiator_id = state.get("initiator_id")
    try:
        if step == 1:
            phone = event.raw_text.strip()
            # Admin değilse sadece kendi numarası
            if not is_admin(user_id) and phone != SYSTEM_PHONE:
                await event.respond("⛔️ Yalnızca kendi hesabınız için oturum açabilirsiniz.")
                log_event(user_id, f"session_onboard_failed_wrong_phone {phone}")
                SESSION_ONBOARD_STATE.pop(user_id, None)
                return
            state["phone"] = phone
            state["step"] = 2
            await event.respond("✅ Kod gönderildi. Lütfen Telegram’dan gelen onay kodunu girin:")
            SESSION_ONBOARD_STATE[user_id] = state
            asyncio.create_task(start_session_flow(event, user_id, phone))
    except Exception as e:
        await event.respond(f"❌ Oturum açma sırasında hata oluştu: {e}")
        log_event(user_id, f"session_onboard_exception: {str(e)}")
        SESSION_ONBOARD_STATE.pop(user_id, None)

async def code_cb_dm(event, user_id, prompt_text="🔑 Onay kodunu gir:"):
    """
    Kullanıcıdan DM'den kod alır (callback).
    """
    fut = asyncio.get_event_loop().create_future()

    async def handler(msg_event):
        if msg_event.sender_id == user_id and not msg_event.is_out:
            fut.set_result(msg_event.raw_text.strip())
            event.client.remove_event_handler(handler, events.NewMessage)
            return True

    event.client.add_event_handler(handler, events.NewMessage)
    await event.respond(prompt_text)
    code = await fut
    return code

async def password_cb_dm(event, user_id, prompt_text="🔒 2FA şifreni gir:"):
    return await code_cb_dm(event, user_id, prompt_text)

async def start_session_flow(event, user_id, phone):
    from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
    async def code_cb():
        return await code_cb_dm(event, user_id)
    async def password_cb():
        return await password_cb_dm(event, user_id)
    try:
        client, me = await open_session(
            phone,
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH,
            code_cb=code_cb,
            password_cb=password_cb
        )
        await event.respond(f"✅ Başarıyla giriş yapıldı: {me.first_name} ({me.username})")
        update_profile(me.username or phone, {"phone": phone})
        await client.disconnect()
        log_event(user_id, f"session_onboard_success: {me.username or phone}")
        log_analytics(user_id, "session_onboard_success", {"phone": phone, "telegram": me.username})
    except Exception as e:
        await event.respond(f"❌ Oturum açılamadı: {e}")
        log_event(user_id, f"session_onboard_fail: {str(e)}")
        log_analytics(user_id, "session_onboard_fail", {"error": str(e)})
    finally:
        SESSION_ONBOARD_STATE.pop(user_id, None)

async def terminate_session(event, phone):
    from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
    from core.session_manager import close_session
    try:
        await close_session(phone, TELEGRAM_API_ID, TELEGRAM_API_HASH)
        await event.respond(f"✅ {phone} için oturum kapatıldı ve session dosyası silindi.")
        log_event(event.sender_id, f"session_terminated: {phone}")
        log_analytics(event.sender_id, "session_terminated", {"phone": phone})
    except Exception as e:
        await event.respond(f"❌ Oturum kapatılamadı: {e}")
        log_event(event.sender_id, f"session_terminate_fail: {str(e)}")
        log_analytics(event.sender_id, "session_terminate_fail", {"phone": phone, "error": str(e)})
