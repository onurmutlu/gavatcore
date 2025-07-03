# 🛠️ Telegram Handler’ları – Referans Standart ve İpuçları

> **Bu dokümandaki handler örnekleri ve notlar, GavatCore projesinin Telegram grup ve DM işleyicileri için ana referanstır.
> Her yeni handler bu standardı yakalamalıdır!**

```python
"""
🪪 Onboarding Session Handler — GavatCore

Kullanıcı ve adminin Telegram DM üzerinden kolayca kendi hesabı veya sistem hesabı için
Telethon session açmasını sağlar. Güvenlik, state ve hata kontrolü içerir.

- Kullanıcı kendi hesabını açabilir
- Admin, sistem telefonunu açabilir (örn. @gavatbaba, admin bot hesabı vs.)
- Oturum açma sırasında kod/2FA istenir, asenkron DM ile toplanır
- Başarılı girişte profil güncellenir ve loglanır
- Her durumda state temizlenir, boşa düşmez

Geliştirici Notu:  
State veya güvenlik ek kontrolü eklemen gerekiyorsa, SESSION_ONBOARD_STATE ile rahatça genişlet.
"""
# handlers/session_handler.py
import asyncio
import os
from telethon import events
from core.session_manager import open_session, get_session_path
from core.profile_loader import update_profile
from core.analytics_logger import log_analytics
from utils.log_utils import log_event
from dotenv import load_dotenv

load_dotenv()
ADMIN_ID = int(os.getenv("GAVATCORE_ADMIN_ID", "0"))
SYSTEM_PHONE = os.getenv("GAVATCORE_SYSTEM_PHONE", "")

SESSION_ONBOARD_STATE = {}

async def session_onboarding_handler(event):
    sender = await event.get_sender()
    user_id = sender.id
    username = sender.username or f"user_{user_id}"

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
            is_admin = (user_id == ADMIN_ID)
            # Sadece admin sistem hesabını açabilir, diğer herkes sadece kendi hesabını açar
            if not is_admin and phone != SYSTEM_PHONE and user_id != ADMIN_ID:
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
    fut = asyncio.get_event_loop().create_future()
    def on_message(msg_event):
        if msg_event.sender_id == user_id and not msg_event.is_out:
            fut.set_result(msg_event.raw_text.strip())
            return True
    event.client.add_event_handler(on_message, events.NewMessage)
    await event.respond(prompt_text)
    code = await fut
    event.client.remove_event_handler(on_message, events.NewMessage)
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
```

----------------------------------------------

## 🚦 Inline Handler Referans Implementasyon

Aşağıdaki inline_handler.py dosyası, GavatCore’da tüm CallbackQuery/inline button işlemlerinin merkezidir.  
Her yeni fonksiyon burada bir elif ile genişletilir.  
Log ve analytics dahil, future-proof yapıda.  
Tüm projelerde **referans** olarak kullanılır.

```python
# handlers/inline_handler.py
"""
🔗 Inline Handler — Telegram CallbackQuery/Inline Button Yönetimi

Bu dosya, GavatCore ekosisteminde tüm inline button (CallbackQuery) olaylarını
tek noktadan yönetmek için kullanılır.

• Yeni butonlar kolayca eklenir (bank_ / onb_ / xyz_ ...)
• Her tıklama loglanır ve analytics'e aktarılır.
• Butonun anlamı yoksa state temizlenir, boşa düşmez.
• Sadece dispatcher ya da controller’dan import edilip kullanılmalı.

Geliştirici Notu:
Tüm genişletmeler için altına yeni elif’ler ekle, 
yeni modülleri async handler’la bağla — *tek nokta kontrol!*
"""

from telethon import events
from handlers.dm_handler import handle_inline_bank_choice
from core.onboarding_flow import handle_onboarding_callback
from utils.state_utils import set_state, get_state, clear_state
from utils.log_utils import log_event
from core.analytics_logger import log_analytics
# İleride role-based handlerlar eklerseniz (ör: admin_panel_handler, user_ticket_handler) burada import edersin

async def inline_handler(event):
    data = event.data.decode("utf-8")
    sender = await event.get_sender()
    user_id = sender.id

    # 💳 Banka seçimi inline button
    if data.startswith("bank_"):
        bank = data.split("bank_")[1]
        await set_state(user_id, "selected_bank", bank)
        await handle_inline_bank_choice(event)
        log_event(user_id, f"Inline Banka Seçimi: {bank}")
        log_analytics(user_id, "inline_bank_selected", {"bank": bank})

    # 🚀 Onboarding flow inline button
    elif data.startswith("onb_"):
        await handle_onboarding_callback(event)
        log_event(user_id, f"Inline Onboarding Step: {data}")
        log_analytics(user_id, "inline_onboarding_step", {"data": data})

    # 🛡️ Admin paneli inline komutları (örnek)
    elif data.startswith("admin_"):
        # from handlers.admin_panel import handle_admin_inline
        # await handle_admin_inline(event)
        log_event(user_id, f"Inline Admin Command: {data}")
        log_analytics(user_id, "inline_admin_command", {"data": data})
        # await event.respond("🛡️ Admin panelinde bir özellik seçtiniz. (Demo)")

    # 👤 Kullanıcıya özel inline komutlar (örnek)
    elif data.startswith("user_"):
        # from handlers.user_commands import handle_user_inline
        # await handle_user_inline(event)
        log_event(user_id, f"Inline User Command: {data}")
        log_analytics(user_id, "inline_user_command", {"data": data})
        # await event.respond("👤 Kullanıcı paneli fonksiyonu (Demo)")

    # 🏭 İçerik üretici (şovcu) paneli inline komutları (örnek)
    elif data.startswith("producer_"):
        # from handlers.producer_panel import handle_producer_inline
        # await handle_producer_inline(event)
        log_event(user_id, f"Inline Producer Command: {data}")
        log_analytics(user_id, "inline_producer_command", {"data": data})
        # await event.respond("🏭 Üretici paneli fonksiyonu (Demo)")

    # 🧠 Buraya istediğin kadar yeni inline prefix & handler ekleyebilirsin

    else:
        await clear_state(user_id)
        log_event(user_id, f"Unknown Inline Callback: {data}")
        log_analytics(user_id, "inline_unknown", {"data": data})
        # await event.respond("Tanımsız inline callback geldi (loglandı).")
```
---
> Kanka, **bundan iyisi el yapımı!**  
> Ekle, genişlet, yeri geldi mi ctrl+c/ctrl+v yardır,  
> Sistemde inline işlerini bundan sonra hep bu bloktan başlatırsın.  
> Sende iş, bende referans!
---

## 📦 Dosya: `handlers/group_handler.py`

### 🎯 Grup Mesajı Handler’ı – Production-Grade Referans

```python
import asyncio
from telethon import events
from core.license_checker import LicenseChecker
from core.profile_loader import load_profile
from gpt.flirt_agent import generate_reply
from utils.template_utils import get_profile_reply_message
from utils.log_utils import log_event
from core.analytics_logger import log_analytics

MANUALPLUS_TIMEOUT = 180  # saniye

# manualplus zaman aşımı için takip sözlüğü
manualplus_pending = {}

async def handle_group_message(event, client):
    if not event.is_group:
        return

    sender = await event.get_sender()
    user_id = sender.id
    username = client.username

    # Sadece reply veya @ ile mention olursa işlem yap
    if not (event.is_reply or f"@{username}" in event.raw_text.lower()):
        return

    license_checker = LicenseChecker()
    session_created_at = license_checker.get_session_creation_time(client.session.filename)
    if not license_checker.is_license_valid(user_id, session_created_at):
        log_analytics(username, "group_blocked_demo_timeout", {
            "user_id": user_id,
            "group_id": event.chat_id
        })
        return

    profile = load_profile(username)
    reply_mode = profile.get("reply_mode", "manual")

    log_event(username, f"📥 Grup mesajı alındı: {event.raw_text} | Yanıt modu: {reply_mode}")
    log_analytics(username, "group_message_received", {
        "from_user_id": user_id,
        "group_id": event.chat_id,
        "text": event.raw_text,
        "reply_mode": reply_mode
    })

    if reply_mode == "gpt":
        try:
            response = await generate_reply(agent_name=username, user_message=event.raw_text)
            await event.reply(response)
            log_event(username, f"🤖 GPT yanıtı gönderildi: {response}")
            log_analytics(username, "group_gpt_reply_sent", {
                "response": response,
                "group_id": event.chat_id
            })
        except Exception as e:
            await event.reply("🤖 Cevap üretilemedi.")
            log_event(username, f"❌ GPT hatası: {str(e)}")
            log_analytics(username, "group_gpt_reply_failed", {
                "error": str(e),
                "group_id": event.chat_id
            })

    elif reply_mode == "manual":
        log_event(username, "✋ manual mod: kullanıcı yanıtlaması bekleniyor.")
        log_analytics(username, "group_manual_no_reply", {
            "group_id": event.chat_id
        })

    elif reply_mode == "hybrid":
        try:
            suggestion = await generate_reply(agent_name=username, user_message=event.raw_text)
            await event.reply(f"📬 Yanıt önerisi (onaylanması gerek):\n\n{suggestion}")
            log_event(username, f"🧪 hybrid mod: öneri gönderildi → {suggestion}")
            log_analytics(username, "group_hybrid_suggestion_sent", {
                "suggestion": suggestion,
                "group_id": event.chat_id
            })
        except Exception as e:
            await event.reply("❌ GPT öneri üretilemedi.")
            log_event(username, f"❌ Hybrid GPT hatası: {str(e)}")
            log_analytics(username, "group_hybrid_suggestion_failed", {
                "error": str(e),
                "group_id": event.chat_id
            })

    elif reply_mode == "manualplus":
        key = f"{username}:{event.id}"
        manualplus_pending[key] = True

        async def check_manualplus_timeout():
            await asyncio.sleep(profile.get("manualplus_timeout_sec", MANUALPLUS_TIMEOUT))
            if manualplus_pending.get(key):
                try:
                    # 🎯 Önce hazır mesaj havuzundan fallback üret
                    fallback = get_profile_reply_message(profile)
                    await event.reply(fallback)
                    log_event(username, f"⏱️ manualplus: süre doldu, fallback yanıt verildi → {fallback}")
                    log_analytics(username, "group_manualplus_fallback_sent", {
                        "fallback": fallback,
                        "group_id": event.chat_id
                    })
                except Exception as e:
                    await event.reply("🤖 Otomatik yanıt üretilemedi.")
                    log_event(username, f"❌ manualplus fallback hatası: {str(e)}")
                    log_analytics(username, "group_manualplus_fallback_failed", {
                        "error": str(e),
                        "group_id": event.chat_id
                    })
            manualplus_pending.pop(key, None)

        asyncio.create_task(check_manualplus_timeout())
        log_event(username, "🕒 manualplus mod: kullanıcı yanıtı bekleniyor...")
        log_analytics(username, "group_manualplus_waiting", {
            "group_id": event.chat_id
        })
```

---

## ⭐️ Handler Standartları – Kural Listesi

* Her zaman **reply\_mode** üzerinden ayrım yap (gpt/manual/hybrid/manualplus).
* **Exception handling** (try/except) ekle, tüm hataları logla.
* Her önemli aksiyonda **log\_event** ve **log\_analytics** ile kayıt tut.
* manualplus için **timeout takibi** yap, fallback mesajı göster.
* Parametre ve değişken isimlerinde **tutarlılık** sağla.
* **Kodda emoji kullan**, okunurluğu ve “vibe”ı yükseltir.
* Kodun başında ne yaptığı, hangi use-case’leri kapsadığı net şekilde **yorumla**.

---

## 🔮 Kendi Handler’ını Yazarken

* Her yeni grup handler’ı bu örneğin üstünden **forklayabilirsin**.
* Gelişmiş handler’lar için ek parametreler veya yeni reply\_mode’lar (ör. “smart\_auto”, “campaign”) ekle.
* Handler’ı tek bir dosyada yaz, ama gerekirse fonksiyonları utils’e çıkar.
* Test ve debug sırasında ekstra log satırları ekle, production’da kısalt.

---

> ⚠️ **Not:**
> Bu handler, GavatCore sisteminin temel otomasyon altyapısı için “en güvenli” referans olarak alınmıştır.
> Copy-paste ile hemen işini görür, yeni projede hızlı başlarsın!

---

## 👷‍♂️ Katkı ve Refactor Kuralları

* Handler’ın iş mantığını değiştiriyorsan, önce burada güncelle ve tüm handler’lara yay.
* “Referans değişikliği” yaptığında, kısa changelog’u dosyanın altına yaz.
* Her zaman en güncel ve en sağlam mantık burada dursun.