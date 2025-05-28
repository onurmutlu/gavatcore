# core/onboarding_flow.py

import asyncio
from telethon import events, Button
from core.profile_loader import (
    load_profile,
    save_profile,
    update_profile,
    DEFAULT_USER_PROFILE
)
from core.analytics_logger import log_analytics
from config import GAVATCORE_ADMIN_ID

ONBOARDING_STATE = {}

def get_username_safe(sender) -> str:
    return sender.username or f"user_{sender.id}"

def create_user_profile(username: str):
    profile = {
        "username": username,
        "display_name": username,
        "type": "user",
        **DEFAULT_USER_PROFILE
    }
    save_profile(username, profile)
    log_analytics(username, "onboarding_profile_created")

async def start_onboarding(client, event):
    try:
        # Önce cache'den dene
        sender = event.sender
        if sender is None:
            try:
                sender = await event.get_sender()
            except Exception as e:
                print(f"❌ Onboarding start API hatası: {e}")
                return
        if sender is None:
            return
        username = get_username_safe(sender)
    except Exception as e:
        print(f"❌ Onboarding start sender hatası: {e}")
        return
    create_user_profile(username)
    ONBOARDING_STATE[username] = {"step": 0, "data": {}}
    log_analytics(username, "onboarding_start", {"via": "telegram"})

    # ROL SEÇİMİ (İçerik Üretici/Ajans veya Son Kullanıcı)
    await event.respond(
        "👋 Hoş geldin!\nLütfen kendini tanımla:",
        buttons=[
            [Button.inline("İçerik Üretici / Ajansım", data="onb_role_producer")],
            [Button.inline("Son Kullanıcı / Müşteriyim", data="onb_role_client")]
        ]
    )

async def handle_onboarding_callback(event):
    try:
        # Önce cache'den dene
        sender = event.sender
        if sender is None:
            try:
                sender = await event.get_sender()
            except Exception as e:
                print(f"❌ Onboarding callback API hatası: {e}")
                return
        if sender is None:
            return
        username = get_username_safe(sender)
    except Exception as e:
        print(f"❌ Onboarding callback sender hatası: {e}")
        return
    data = event.data.decode("utf-8")
    state = ONBOARDING_STATE.get(username, {"step": 0, "data": {}})

    # ROL SEÇİMİ: ŞOVCU/PRODUCER
    if data == "onb_role_producer":
        state["step"] = 1
        state["data"]["type"] = "producer"
        update_profile(username, {"type": "producer"})
        log_analytics(username, "onboarding_role_set", {"role": "producer"})
        await event.respond(
            "Tebrikler, İçerik Üretici/Ajans olarak kaydedildin!\n"
            "Özel mesaj şablonların hazır mı?",
            buttons=[
                [Button.inline("Kendi Şablonlarımı Gireceğim", data="onb_flirt_custom")],
                [Button.inline("Sistemin Hazır Şablonlarını Kullan", data="onb_flirt_default")]
            ]
        )

    # ROL SEÇİMİ: SON KULLANICI
    elif data == "onb_role_client":
        state["step"] = 100
        state["data"]["type"] = "client"
        update_profile(username, {"type": "client"})
        log_analytics(username, "onboarding_role_set", {"role": "client"})
        await event.respond(
            "Şu anda sistemi aktif olarak kullanan bir içerik üreticisi/ajans değilsin.\n"
            "Destek, öneri veya şikayet için aşağıdaki komutları kullanabilirsin:\n\n"
            "• <b>/yardim</b> – Destek talebi aç\n"
            "• <b>/raporla</b> – Kullanıcı/ajans/bot şikayet et\n"
            "• <b>/oner</b> – Öneri/görüş ilet\n\n"
            "Her komut admin ekibimize DM olarak iletilir. Teşekkürler!"
        )
        # Onboarding sonu: step ilerlemiyor

    # ÜRETİCİ onboarding adımları:
    elif data == "onb_flirt_custom":
        state["step"] = 2
        log_analytics(username, "onboarding_flirt_mode", {"mode": "custom"})
        await event.respond("✍️ Her satıra bir mesaj gelecek şekilde mesaj şablonlarını gir. (Örn: Hoşgeldin, nasılsın?)")

    elif data == "onb_flirt_default":
        update_profile(username, {"use_default_templates": True})
        log_analytics(username, "onboarding_flirt_mode", {"mode": "default"})
        state["step"] = 3
        await event.respond("📋 Şimdi hizmet menünü yaz. (Örn: VIP Sohbet: 200₺)")

    elif data == "onb_skip_all_payments":
        update_profile(username, state["data"])
        log_analytics(username, "onboarding_complete", {"skipped": True})
        await event.respond("✅ Onboarding tamamlandı! Şimdi DM'leri otomatik cevaplamaya hazırsın 😘")
        ONBOARDING_STATE.pop(username, None)

    ONBOARDING_STATE[username] = state

async def handle_onboarding_text(event):
    try:
        # Önce cache'den dene
        sender = event.sender
        if sender is None:
            try:
                sender = await event.get_sender()
            except Exception as e:
                print(f"❌ Onboarding text API hatası: {e}")
                return
        if sender is None:
            return
        username = get_username_safe(sender)
    except Exception as e:
        print(f"❌ Onboarding text sender hatası: {e}")
        return
    message = event.raw_text.strip()

    if username not in ONBOARDING_STATE:
        return

    state = ONBOARDING_STATE[username]
    step = state["step"]
    data = state["data"]

    # ÜRETİCİ/AJANS onboarding
    if data.get("type") == "producer":
        if step == 2:
            flirt_templates = [m.strip() for m in message.splitlines() if m.strip()]
            update_profile(username, {"flirt_templates": flirt_templates})
            log_analytics(username, "onboarding_flirt_templates", {"count": len(flirt_templates)})
            state["step"] = 3
            await event.respond("📋 Şimdi hizmet menünü yaz. (Örn: VIP Sohbet: 200₺)")

        elif step == 3:
            update_profile(username, {"services_menu": message})
            log_analytics(username, "onboarding_services_menu", {"preview": message[:100]})
            state["step"] = 4
            await event.respond("💳 Papara açıklama (kullanıcı ID) bilgisini gir.\nGeçmek için <code>geç</code> yazabilirsin.")

        elif step == 4:
            if message.lower() != "geç":
                data["papara_note"] = message
                log_analytics(username, "onboarding_papara_note", {"note": message})
            state["step"] = 5
            await event.respond("🏦 IBAN ve isim: <code>TRxx... | Ad Soyad</code> şeklinde gir.\nGeçmek için <code>geç</code> yazabilirsin.")

        elif step == 5:
            if message.lower() != "geç":
                try:
                    iban, name = message.split("|", 1)
                    data["personal_iban"] = {
                        "iban": iban.strip(),
                        "name": name.strip()
                    }
                    log_analytics(username, "onboarding_iban_set", {
                        "iban": iban.strip(),
                        "name": name.strip()
                    })
                except Exception:
                    await event.respond("⚠️ Format: <code>TRxx1234 | Ayşe Yıldız</code> olmalı. Lütfen tekrar gir.")
                    return

            update_profile(username, data)
            log_analytics(username, "onboarding_complete", {
                "has_papara": "papara_note" in data,
                "has_iban": "personal_iban" in data
            })
            # Session açma önerisi ve kısa açıklama!
            await event.respond(
                "✅ Onboarding tamamlandı!\n"
                "Şimdi sistemde DM’leri otomatik cevaplayabilir, gruplara katılabilirsin.\n\n"
                "Eğer kendi hesabını bot gibi kullanacaksan, DM'den <b>/oturumac</b> komutunu kullanıp Telegram kodu ve 2FA şifrenle oturumunu başlatabilirsin."
            )
            ONBOARDING_STATE.pop(username, None)

        ONBOARDING_STATE[username] = state

    # SON KULLANICI onboarding'i — komut ile yönetilecek (yardım/talep/rapor)
    elif data.get("type") == "client":
        # /yardim, /raporla, /oner gibi mesajlar için DM_handler veya user_commands'de ayrıca routing olacak
        await event.respond(
            "Şu anda içerik üretici/ajans modunda değilsin. Destek veya şikayet için komutları kullanabilirsin."
        )
        ONBOARDING_STATE.pop(username, None)
