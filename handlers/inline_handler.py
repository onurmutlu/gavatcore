# handlers/inline_handler.py

from telethon import events
from handlers.dm_handler import handle_inline_bank_choice
from core.onboarding_flow import handle_onboarding_callback
from utils.state_utils import set_state, get_state, clear_state

# Bu handler sadece CallbackQuery (inline button) olaylarını yönetmek için çağrılır
# dispatcher içinden import edilerek kullanılmalı

async def inline_handler(event):
    data = event.data.decode("utf-8")
    sender = await event.get_sender()
    user_id = sender.id

    # 💳 Banka seçimi butonuna tıklandı
    if data.startswith("bank_"):
        bank = data.split("bank_")[1]
        await set_state(user_id, "selected_bank", bank)
        await handle_inline_bank_choice(event)

    # 🚀 Onboarding süreci butonları
    elif data.startswith("onb_"):
        await handle_onboarding_callback(event)

    # 🧠 Genişletilebilir diğer inline butonlar için:
    # elif data.startswith("xyz_"):
    #     ...

    else:
        await clear_state(user_id)
