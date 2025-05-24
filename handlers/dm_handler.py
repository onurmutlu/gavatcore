# handlers/dm_handler.py

import random
import datetime
from telethon import Button
from core.license_checker import LicenseChecker
from core.profile_loader import load_profile
from gpt.flirt_agent import generate_reply
from gpt.system_prompt_manager import get_menu_prompt
from utils.log_utils import log_event
from utils.template_utils import get_profile_reply_message
from utils.payment_utils import generate_payment_message, load_banks
from core.analytics_logger import log_analytics
from handlers.group_handler import manualplus_pending

DEFAULT_FLIRT_TEMPLATES = [
    "Selam tatlım 💖 Bugün seninle özel bir bağ kurabiliriz...",
    "Günün nasıl geçti? İstersen seni biraz şımartabilirim 😉",
    "Hazırım 😈 Ama önce küçük bir destek lazım 💸",
    "VIP grubumda çok daha fazlası var 🫦 Katılmak ister misin?"
]

DEFAULT_SERVICES_MENU = """
💋 *Hizmet Menüm* 💋

- Sesli Fantazi: 200₺
- Görüntülü Şov: 300₺
- VIP Grup Üyeliği: 150₺
- Ayak Arşivi: 100₺

💳 IBAN/Papara bilgisi için yaz ❤️
"""

DEFAULT_PAPARA_BANKAS = {
    "Ziraat": "TR12 0001 0012 3456 7890 1234 56",
    "Vakif": "TR34 0001 0012 3456 7890 9876 54",
    "Isbank": "TR56 0001 0012 3456 7890 1928 34"
}

active_bank_requests = {}

async def handle_message(client, sender, message_text, session_created_at):
    user_id = sender.id
    username = sender.username or sender.first_name or "kanka"

    checker = LicenseChecker()
    if not checker.is_license_valid(user_id, session_created_at):
        await client.send_message(user_id, "⏳ Canım, demo süren dolmuş gibi görünüyor 😢 Lisansla devam edebilmek için bize ulaş lütfen 💌")
        log_analytics(username, "dm_blocked_demo_timeout", {"message": message_text})
        return

    profile = load_profile(client.username)
    flirt_templates = profile.get("flirt_templates", DEFAULT_FLIRT_TEMPLATES)
    services_menu = profile.get("services_menu", DEFAULT_SERVICES_MENU)
    papara_bankas = profile.get("papara_accounts", DEFAULT_PAPARA_BANKAS)
    reply_mode = profile.get("reply_mode", "manual")

    lowered = message_text.lower()
    log_event(client.username, f"📥 DM alındı: {message_text} | Yanıt modu: {reply_mode}")
    log_analytics(client.username, "dm_received", {
        "from_user": username,
        "message": message_text,
        "mode": reply_mode
    })

    # manualplus zamanlayıcısını iptal et
    pending_keys = [k for k in manualplus_pending if k.startswith(f"{client.username}:")]
    for key in pending_keys:
        manualplus_pending[key] = False
        log_event(client.username, f"🛑 manualplus yanıtı zamanında geldi, GPT tetiklenmeyecek")

    # 💰 Menü ve VIP içerik yanıtı
    if any(keyword in lowered for keyword in ["fiyat", "menü", "ücret", "kaç para", "vip"]):
        await client.send_message(user_id, "📝 Elbette! Aşağıda tüm detayları bulabilirsin:", parse_mode="markdown")
        try:
            menu_prompt = get_menu_prompt(client.username)
            menu_reply = await generate_reply(agent_name=client.username, user_message=menu_prompt)
            await client.send_message(user_id, menu_reply)
            log_analytics(client.username, "dm_menu_prompt_reply", {"prompt": menu_prompt})
        except Exception as e:
            log_event(client.username, f"⚠️ Menü GPT üretim hatası: {str(e)}")

        await client.send_message(user_id, services_menu, parse_mode="markdown")
        return

    # 💳 IBAN/Papara bilgisi
    if any(keyword in lowered for keyword in ["iban", "papara", "ödeme"]):
        buttons = [Button.inline(bank, data=f"bank_{bank}") for bank in papara_bankas.keys()]
        active_bank_requests[user_id] = papara_bankas
        await client.send_message(user_id, "💳 Hangi bankayı kullanıyorsun tatlım? Aşağıdan seç 🙏", buttons=buttons)
        log_analytics(client.username, "dm_bank_selection_prompt")
        return

    if message_text.strip() in papara_bankas:
        iban = papara_bankas[message_text.strip()]
        await client.send_message(user_id, f"💳 IBAN: `{iban}`\n📌 Açıklama kısmına Telegram adını yaz 💕", parse_mode="markdown")
        log_analytics(client.username, "dm_direct_bank_selected", {"bank": message_text.strip()})
        return

    # 💬 Yanıt üretimi
    if reply_mode == "gpt":
        try:
            response = await generate_reply(agent_name=client.username, user_message=message_text)
            await client.send_message(user_id, response)
            log_event(client.username, f"🤖 GPT yanıtı gönderildi: {response}")
            log_analytics(client.username, "dm_gpt_reply_sent", {"response": response})
        except Exception as e:
            await client.send_message(user_id, "🤖 Cevap üretilemedi.")
            log_event(client.username, f"❌ GPT hatası: {str(e)}")
            log_analytics(client.username, "dm_gpt_reply_failed", {"error": str(e)})

    elif reply_mode == "manual":
        log_event(client.username, "✋ manual: yanıtı şovcu verecek")
        log_analytics(client.username, "dm_manual_no_reply")

    elif reply_mode == "manualplus":
        fallback_msg = get_profile_reply_message(profile)
        await client.send_message(user_id, fallback_msg)
        log_event(client.username, f"🕒 manualplus: fallback yanıtı verildi: {fallback_msg}")
        log_analytics(client.username, "dm_manualplus_fallback", {"fallback": fallback_msg})

    elif reply_mode == "hybrid":
        try:
            suggestion = await generate_reply(agent_name=client.username, user_message=message_text)
            await client.send_message(user_id, f"💬 GPT önerisi: {suggestion}")
            log_event(client.username, "💡 hybrid: öneri gösterildi")
            log_analytics(client.username, "dm_hybrid_suggestion", {"suggestion": suggestion})
        except Exception as e:
            log_event(client.username, f"⚠️ Hybrid mod hatası: {str(e)}")
            log_analytics(client.username, "dm_hybrid_suggestion_failed", {"error": str(e)})

# 💳 Inline bankadan seçim sonrası
async def handle_inline_bank_choice(event):
    sender = await event.get_sender()
    user_id = sender.id
    username = sender.username or str(user_id)
    data = event.data.decode("utf-8")

    if data.startswith("bank_"):
        bank_name = data.split("bank_")[1]
        try:
            profile = load_profile(username)
            banks_data = load_banks()
            message = generate_payment_message(bank_name, profile, banks_data)
            await event.respond(message, parse_mode="markdown")
            log_analytics(username, "inline_bank_choice_success", {"bank": bank_name})
        except Exception as e:
            await event.respond("❌ Ödeme bilgisi alınırken hata oluştu.")
            log_event(username, f"❌ Banka inline hatası: {str(e)}")
            log_analytics(username, "inline_bank_choice_error", {"error": str(e)})
