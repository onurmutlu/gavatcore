import asyncio
from telethon import events, Button
from core.profile_loader import (
    load_profile,
    save_profile,
    update_profile,
    DEFAULT_USER_PROFILE
)
from core.analytics_logger import log_analytics

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
    sender = await event.get_sender()
    username = get_username_safe(sender)

    create_user_profile(username)
    ONBOARDING_STATE[username] = {"step": 0, "data": {}}

    log_analytics(username, "onboarding_start", {"via": "telegram"})

    await event.respond(
        "👋 Hoş geldin canım! Seni tanıyalım... Özel mesaj şablonların hazır mı?",
        buttons=[
            [Button.inline("Kendi Şablonlarımı Gireceğim", data="onb_flirt_custom")],
            [Button.inline("Sistemin Hazır Şablonlarını Kullan", data="onb_flirt_default")]
        ]
    )

async def handle_onboarding_callback(event):
    sender = await event.get_sender()
    username = get_username_safe(sender)
    data = event.data.decode("utf-8")

    state = ONBOARDING_STATE.get(username, {"step": 0, "data": {}})

    if data == "onb_flirt_custom":
        state["step"] = 1
        log_analytics(username, "onboarding_flirt_mode", {"mode": "custom"})
        await event.respond("✍️ Her satıra bir mesaj gelecek şekilde flört şablonlarını gir.")

    elif data == "onb_flirt_default":
        update_profile(username, {"use_default_templates": True})
        log_analytics(username, "onboarding_flirt_mode", {"mode": "default"})
        state["step"] = 2
        await event.respond("📋 Şimdi hizmet menünü yaz tatlım. Örneğin:\n- Sesli Fantazi: 200₺\n- VIP Grup: 150₺")

    elif data == "onb_skip_all_payments":
        update_profile(username, state["data"])
        log_analytics(username, "onboarding_complete", {"skipped": True})
        await event.respond("✅ Onboarding tamamlandı! Şimdi DM'leri otomatik cevaplamaya hazırsın 😘")
        ONBOARDING_STATE.pop(username, None)

    ONBOARDING_STATE[username] = state

async def handle_onboarding_text(event):
    sender = await event.get_sender()
    username = get_username_safe(sender)
    message = event.raw_text.strip()

    if username not in ONBOARDING_STATE:
        return

    state = ONBOARDING_STATE[username]
    step = state["step"]
    data = state["data"]

    if step == 1:
        flirt_templates = [m.strip() for m in message.splitlines() if m.strip()]
        update_profile(username, {"flirt_templates": flirt_templates})
        log_analytics(username, "onboarding_flirt_templates", {"count": len(flirt_templates)})
        state["step"] = 2
        await event.respond("📋 Şimdi hizmet menünü yaz tatlım. Örneğin:\n- Sesli Fantazi: 200₺\n- VIP Grup: 150₺")

    elif step == 2:
        update_profile(username, {"services_menu": message})
        log_analytics(username, "onboarding_services_menu", {"preview": message[:100]})
        state["step"] = 3
        await event.respond("💳 Papara açıklama (kullanıcı ID) bilgisini gir.\nGeçmek için `geç` yazabilirsin.")

    elif step == 3:
        if message.lower() != "geç":
            data["papara_note"] = message
            log_analytics(username, "onboarding_papara_note", {"note": message})
        state["step"] = 4
        await event.respond("🏦 IBAN ve isim: `TRxx... | Ad Soyad` şeklinde gir.\nGeçmek için `geç` yazabilirsin.")

    elif step == 4:
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
            except:
                await event.respond("⚠️ Format: `TRxx1234 | Ayşe Yıldız` olmalı. Lütfen tekrar gir.")
                return

        update_profile(username, data)
        log_analytics(username, "onboarding_complete", {"has_papara": "papara_note" in data, "has_iban": "personal_iban" in data})
        await event.respond("✅ Onboarding tamamlandı! Şimdi DM'leri otomatik cevaplamaya hazırsın 😘")
        ONBOARDING_STATE.pop(username, None)

    ONBOARDING_STATE[username] = state
