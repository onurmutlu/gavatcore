import asyncio
import random
import json
from pathlib import Path
from core.profile_loader import load_all_profiles
from utils.log_utils import log_event
from telethon.errors import ChatWriteForbiddenError

DEFAULT_INTERVAL_SECONDS = (60, 420)  # 1–7 dakika
BANNED_GROUP_IDS = set()
DEFAULT_MESSAGES_FILE = Path("data/group_spam_messages.json")

def load_default_spam_messages() -> list:
    if DEFAULT_MESSAGES_FILE.exists():
        try:
            with open(DEFAULT_MESSAGES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("_template", {}).get("engaging_messages", [])
        except Exception as e:
            print(f"⚠️ group_spam_messages.json okunamadı: {e}")
    return [
        "💖 Selam yakışıklı! VIP grubum doluyor 😘",
        "🎀 Bugün benimle daha yakın olmak ister misin? DM 💌",
        "😈 Şımarmaya hazır mısın? VIP'e bekliyorum..."
    ]

async def spam_loop(client):
    username = client.username or client.session.filename
    profile = load_all_profiles().get(username)

    if not profile or not profile.get("autospam"):
        return

    while True:
        await asyncio.sleep(random.uniform(*DEFAULT_INTERVAL_SECONDS))

        profile = load_all_profiles().get(username)
        if not profile or not profile.get("autospam"):
            log_event(username, "🛑 Otomatik spam kapatıldı, döngü durduruldu.")
            break

        # 📥 Mesaj havuzu: Önce şovcuya özel varsa onu, yoksa default
        messages = profile.get("group_spam_templates")
        if not messages or not isinstance(messages, list) or len(messages) < 1:
            messages = load_default_spam_messages()

        message = random.choice(messages)

        try:
            dialogs = await client.get_dialogs()
            sent_count = 0

            for dialog in dialogs:
                if not dialog.is_group or dialog.id in BANNED_GROUP_IDS:
                    continue

                try:
                    await client.send_message(dialog.id, message)
                    log_event(username, f"📤 [{dialog.name}] mesaj gönderildi: {message}")
                    sent_count += 1
                    await asyncio.sleep(random.uniform(1, 4))

                except ChatWriteForbiddenError:
                    BANNED_GROUP_IDS.add(dialog.id)
                    log_event(username, f"🚫 Yazma engeli alındı: {dialog.name}")
                except Exception as e:
                    log_event(username, f"⚠️ Mesaj gönderim hatası [{dialog.name}]: {e}")

            log_event(username, f"✅ {sent_count} gruba spam mesajı gönderildi.")

        except Exception as e:
            log_event(username, f"💥 Spam döngüsü genel hatası: {e}")
