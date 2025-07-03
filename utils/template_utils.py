import json
import random
from pathlib import Path

REPLY_MESSAGES_FILE = Path("data/reply_messages.json")
GROUP_SPAM_MESSAGES_FILE = Path("data/group_spam_messages.json")

def load_default_reply_messages():
    """
    Genel sistem fallback reply mesajlarını döner (data/reply_messages.json).
    """
    if not REPLY_MESSAGES_FILE.exists():
        return []
    try:
        with open(REPLY_MESSAGES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("_template", {}).get("reply_messages", [])
    except Exception as e:
        print(f"[ERROR] Reply mesajları yüklenemedi: {e}")
        return []

def get_profile_reply_message(profile: dict) -> str:
    """
    Şovcu profiline özel yanıt mesajı döner. Tanımlı değilse sistem geneline fallback yapar.
    """
    messages = (
        profile.get("reply_messages") or
        profile.get("_template", {}).get("reply_messages")
    )
    if messages:
        return random.choice(messages)

    fallback = load_default_reply_messages()
    return random.choice(fallback) if fallback else "💬 Cevabın içime dokundu... Konuşalım mı?"

def load_group_spam_messages():
    """
    Grup spam mesajlarını yükler (data/group_spam_messages.json).
    """
    if not GROUP_SPAM_MESSAGES_FILE.exists():
        return []
    try:
        with open(GROUP_SPAM_MESSAGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Grup spam mesajları yüklenemedi: {e}")
        return []

def get_profile_spam_message(profile: dict) -> str:
    """
    Şovcuya özel spam mesajı döner. Tanımlı değilse sistem genelinden seçer.
    """
    messages = (
        profile.get("group_spam_templates") or
        profile.get("_template", {}).get("group_spam_templates")
    )
    if messages:
        return random.choice(messages)

    fallback = load_group_spam_messages()
    return random.choice(fallback) if fallback else "💖 Selam! Sohbete var mısın canım?"
