# handlers/onboarding_session.py

import asyncio
import os
from telethon import events
from core.session_manager import open_session, get_session_path
from core.profile_loader import update_profile
from dotenv import load_dotenv

# .env'den çek
load_dotenv()
ADMIN_ID = int(os.getenv("GAVATCORE_ADMIN_ID", "0"))
SYSTEM_PHONE = os.getenv("GAVATCORE_SYSTEM_PHONE", "")

SESSION_ONBOARD_STATE = {}

async def session_onboarding_handler(event):
    sender = await event.get_sender()
    user_id = sender.id
    username = sender.username or f"user_{user_id}"

    # Yalnızca admin BAŞKASININ oturumunu açabilir, kullanıcı kendi için açar
    await event.respond(
        "📞 Telefon numarasını başında + ile yaz (örn: +905xxxxxxxxx):\n"
        "(Yalnızca kendi hesabınızı veya adminseniz sistem hesabını açabilirsiniz)"
    )
    SESSION_ONBOARD_STATE[user_id] = {
        "step": 1,
        "initiator_id": user_id,
        "initiator_username": username,
    }

@events.register(events.NewMessage(incoming=True, pattern=None))
async def onboarding_text_handler(event):
    user_id = event.sender_id
    state = SESSION_ONBOARD_STATE.get(user_id)
    if not state:
        return

    step = state.get("step", 0)
    initiator_id = state.get("initiator_id")

    if step == 1:
        # Telefon numarasını al
        phone = event.raw_text.strip()
        is_admin = (user_id == ADMIN_ID)
        # Sadece admin sistem hesabını açabilir, diğer herkes sadece kendi telefonunu girebilir
        if not is_admin and phone != SYSTEM_PHONE and user_id != ADMIN_ID:
            # Eğer kendi telefonunu yazmıyorsa izin verme
            await event.respond("⛔️ Yalnızca kendi hesabınız için oturum açabilirsiniz.")
            SESSION_ONBOARD_STATE.pop(user_id, None)
            return
        state["phone"] = phone
        state["step"] = 2
        await event.respond("✅ Kod gönderildi. Lütfen Telegram’dan gelen onay kodunu gir:")
        SESSION_ONBOARD_STATE[user_id] = state
        asyncio.create_task(start_session_flow(event, user_id, phone))

async def code_cb_dm(event, user_id, prompt_text="🔑 Onay kodunu gir:"):
    fut = asyncio.get_event_loop().create_future()
    def on_message(msg_event):
        if msg_event.sender_id == user_id and not msg_event.is_out:
            fut.set_result(msg_event.raw_text.strip())
            return True
    event.client.add_event_handler(on_message, events.NewMessage)
    code = await fut
    event.client.remove_event_handler(on_message, events.NewMessage)
    return code

async def password_cb_dm(event, user_id, prompt_text="🔒 2FA şifreni gir:"):
    await event.respond(prompt_text)
    return await code_cb_dm(event, user_id, prompt_text)

async def start_session_flow(event, user_id, phone):
    from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

    async def code_cb():
        await event.respond("🔑 Kod bekleniyor...")
        return await code_cb_dm(event, user_id)

    async def password_cb():
        await event.respond("🔒 2FA şifren bekleniyor...")
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
        # Profiline telefon numarasını veya session dosya yolunu yazabilirsin
        update_profile(me.username or phone, {"phone": phone})
        await client.disconnect()
    except Exception as e:
        await event.respond(f"❌ Oturum açılamadı: {e}")
    finally:
        SESSION_ONBOARD_STATE.pop(user_id, None)
