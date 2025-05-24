# handlers/group_handler.py

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
