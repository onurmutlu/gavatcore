# utils/dm_code_callbacks.py

import asyncio
from telethon import events

CODE_STATE = {}

async def code_cb_dm(event, prompt_text="🔑 Telegram onay kodunu gir:"):
    """
    Kullanıcıdan DM ile onay kodunu asenkron olarak alır.
    - Sadece ilgili kullanıcıdan gelen ilk mesajı yakalar.
    - Event handler'ı başarılı/başarısız durumda temizler.
    - Zombi handler bırakmaz.
    """
    user_id = event.sender_id
    await event.respond(prompt_text)
    loop = asyncio.get_event_loop()
    fut = loop.create_future()

    async def handler(msg_event):
        if msg_event.sender_id == user_id and not msg_event.is_out:
            if not fut.done():
                fut.set_result(msg_event.raw_text.strip())
            # Handler'ı temizle (sadece bu kullanıcı için)
            await event.client.remove_event_handler(handler, events.NewMessage)
            return True

    event.client.add_event_handler(handler, events.NewMessage)
    try:
        result = await fut
    finally:
        # Her halükarda handler cleanup (timeout vs. olursa da)
        await event.client.remove_event_handler(handler, events.NewMessage)
    return result

async def password_cb_dm(event, prompt_text="🔒 2FA şifreni gir:"):
    """
    Kullanıcıdan DM ile 2FA şifresini alır (aynı mantık).
    """
    return await code_cb_dm(event, prompt_text)
