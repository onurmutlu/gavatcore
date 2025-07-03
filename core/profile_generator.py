# core/profile_generator.py

import datetime

DEFAULT_USER_TEMPLATE = {
    "engaging_messages": [],
    "reply_messages": [
        "😌 Ne tatlı yazmışsın, bi daha yazsana?",
        "🙈 Ayyy utandım, ama sevdim…",
        "🥰 Böyle mesajlara bayılıyorum!",
        "😉 Devam et, tam hoşlandığım tarz",
        "💬 Sen yaz, ben dinliyorum…"
    ]
}

DEFAULT_BOT_TEMPLATE = {
    "engaging_messages": [],
    "reply_messages": [
        "🤖 Merhaba! Ben buradayım 😎",
        "💡 Ne demek istedin tatlım?",
        "🧠 Sana nasıl yardımcı olabilirim?",
        "🫦 Sohbete devam edelim mi?",
        "😇 Botum ama kalbim seninle…"
    ]
}

DEFAULT_USER_PROFILE = {
    "type": "user",
    "reply_mode": "manualplus",
    "manualplus_timeout_sec": 180,
    "flirt_templates": [],
    "services_menu": "",
    "papara_accounts": {},
    "papara_note": "",
    "personal_iban": {
        "iban": "",
        "name": ""
    },
    "use_default_templates": True,
    "_template": DEFAULT_USER_TEMPLATE
}

DEFAULT_BOT_PROFILE = {
    "type": "bot",
    "owner_id": "system",
    "reply_mode": "gpt",
    "manualplus_timeout_sec": 90,
    "persona": {
        "age": "25-35",
        "style": "Yapay zekalı sohbet asistanı",
        "role": "Otomatik yanıtlayıcı",
        "gpt_prompt": "Sen bir AI sohbet botusun. Kullanıcılara sıcak, flörtöz ama stil sahibi yanıtlar veriyorsun. Her yanıtında en az 1 emoji olmalı."
    },
    "_template": DEFAULT_BOT_TEMPLATE
}

def generate_showcu_persona(username: str) -> dict:
    """
    Yeni bir şovcu için default profil döner.
    """
    return {
        "username": username,
        "display_name": username,
        "created_at": datetime.datetime.utcnow().isoformat(),
        **DEFAULT_USER_PROFILE
    }

def generate_bot_persona(username: str) -> dict:
    """
    Yeni bir sistem botu için default profil döner.
    """
    return {
        "username": username,
        "display_name": username,
        "created_at": datetime.datetime.utcnow().isoformat(),
        **DEFAULT_BOT_PROFILE
    }
