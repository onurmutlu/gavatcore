# core/profile_loader.py

import os
import json

PERSONA_DIR = "data/personas"

DEFAULT_USER_PROFILE = {
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
    "engaging_messages": [],
    "reply_messages": []
}

def get_profile_path(username: str):
    return os.path.join(PERSONA_DIR, f"{username}.json")

def create_profile(username: str, profile_data: dict = {}):
    path = get_profile_path(username)
    if not os.path.exists(path):
        full_profile = {
            "username": username,
            "display_name": username,
            "type": "user",
            **DEFAULT_USER_PROFILE,
            **profile_data
        }
        save_profile(username, full_profile)

def load_profile(username: str):
    path = get_profile_path(username)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Profil bulunamadı: {username}")

    with open(path, "r", encoding="utf-8") as f:
        profile = json.load(f)

    # ⛑ Geriye dönük uyumluluk: Eksik alanları default ile tamamla
    for key, value in DEFAULT_USER_PROFILE.items():
        profile.setdefault(key, value)

    # 🔁 Eğer `_template.reply_messages` varsa ve `reply_messages` boşsa kullan
    if not profile.get("reply_messages") and "_template" in profile:
        tpl = profile["_template"]
        if isinstance(tpl, dict) and tpl.get("reply_messages"):
            profile["reply_messages"] = tpl["reply_messages"]

    return profile

def save_profile(username: str, profile_data: dict):
    path = get_profile_path(username)
    os.makedirs(PERSONA_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2, ensure_ascii=False)

def update_profile(username: str, updates: dict):
    profile = load_profile(username)
    profile.update(updates)
    save_profile(username, profile)

def get_all_profiles():
    os.makedirs(PERSONA_DIR, exist_ok=True)
    profiles = []
    for file in os.listdir(PERSONA_DIR):
        if file.endswith(".json"):
            with open(os.path.join(PERSONA_DIR, file), "r", encoding="utf-8") as f:
                profile = json.load(f)

                # Eksik alanları tamamla
                for key, value in DEFAULT_USER_PROFILE.items():
                    profile.setdefault(key, value)

                if not profile.get("reply_messages") and "_template" in profile:
                    tpl = profile["_template"]
                    if isinstance(tpl, dict) and tpl.get("reply_messages"):
                        profile["reply_messages"] = tpl["reply_messages"]

                profiles.append(profile)

    return profiles
