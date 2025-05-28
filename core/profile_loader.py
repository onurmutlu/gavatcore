# core/profile_loader.py

import os
import json
import threading
import asyncio
from typing import Optional, Dict, List

# MongoDB profile store'u import et
from core.profile_store import (
    get_profile_by_username as mongo_get_profile,
    create_or_update_profile as mongo_save_profile,
    update_profile_field as mongo_update_profile
)

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
    "reply_messages": [],
    "phone": "",  # Telefon numarası alanı
}

_profile_lock = threading.RLock()

def get_profile_path(username: str) -> str:
    """Kullanıcı adından dosya yolu üretir."""
    return os.path.join(PERSONA_DIR, f"{username}.json")

async def create_profile_async(username: str, profile_data: dict = {}) -> None:
    """
    Async profil oluşturma - MongoDB'ye yazar
    """
    try:
        # Önce mevcut profili kontrol et
        existing = await mongo_get_profile(username)
        if existing:
            return  # Zaten var
        
        full_profile = {
            "username": username,
            "display_name": username,
            "type": "user",
            **DEFAULT_USER_PROFILE,
            **profile_data
        }
        
        await mongo_save_profile(username, full_profile)
    except Exception as e:
        print(f"MongoDB profil oluşturma hatası, file-based fallback: {e}")
        create_profile_file(username, profile_data)

def create_profile(username: str, profile_data: dict = {}) -> None:
    """
    Sync wrapper - async create_profile_async'i çağırır
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Event loop çalışıyorsa task olarak ekle
            asyncio.create_task(create_profile_async(username, profile_data))
        else:
            asyncio.run(create_profile_async(username, profile_data))
    except Exception as e:
        print(f"Async profil oluşturma hatası, file-based fallback: {e}")
        create_profile_file(username, profile_data)

def create_profile_file(username: str, profile_data: dict = {}) -> None:
    """
    File-based profil oluşturma (fallback)
    """
    path = get_profile_path(username)
    os.makedirs(PERSONA_DIR, exist_ok=True)
    if not os.path.exists(path):
        full_profile = {
            "username": username,
            "display_name": username,
            "type": "user",
            **DEFAULT_USER_PROFILE,
            **profile_data
        }
        save_profile_file(username, full_profile)

async def load_profile_async(username: str) -> dict:
    """
    Async profil yükleme - MongoDB'den getirir
    """
    try:
        profile = await mongo_get_profile(username)
        if not profile:
            raise FileNotFoundError(f"Profil bulunamadı: {username}")
        
        # Eksik alanları tamamla
        for key, value in DEFAULT_USER_PROFILE.items():
            if key not in profile:
                profile[key] = value
        
        # Template'ten reply mesajı çek
        if not profile.get("reply_messages") and "_template" in profile:
            tpl = profile["_template"]
            if isinstance(tpl, dict) and tpl.get("reply_messages"):
                profile["reply_messages"] = tpl["reply_messages"]
        
        # Migration'lar
        if "phone" not in profile:
            profile["phone"] = ""
        if "username" not in profile:
            profile["username"] = username
        if "display_name" not in profile:
            profile["display_name"] = username
        
        return profile
    except Exception as e:
        print(f"MongoDB profil yükleme hatası, file-based fallback: {e}")
        return load_profile_file(username)

def load_profile(username: str) -> dict:
    """
    Sync wrapper - async load_profile_async'i çağırır
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Event loop çalışıyorsa sync fallback kullan
            return load_profile_file(username)
        else:
            return asyncio.run(load_profile_async(username))
    except Exception as e:
        print(f"Async profil yükleme hatası, file-based fallback: {e}")
        return load_profile_file(username)

def load_profile_file(username: str) -> dict:
    """
    File-based profil yükleme (fallback)
    """
    path = get_profile_path(username)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Profil bulunamadı: {username}")

    with _profile_lock:
        with open(path, "r", encoding="utf-8") as f:
            profile = json.load(f)

        # Eksik alanları tamamla (her migration'da garanti)
        for key, value in DEFAULT_USER_PROFILE.items():
            if key not in profile:
                profile[key] = value

        # Template'ten reply mesajı çek
        if not profile.get("reply_messages") and "_template" in profile:
            tpl = profile["_template"]
            if isinstance(tpl, dict) and tpl.get("reply_messages"):
                profile["reply_messages"] = tpl["reply_messages"]

        # Telefon migration
        if "phone" not in profile:
            profile["phone"] = ""

        # username ve display_name fallback
        if "username" not in profile:
            profile["username"] = username
        if "display_name" not in profile:
            profile["display_name"] = username

    return profile

async def save_profile_async(username: str, profile_data: dict) -> None:
    """
    Async profil kaydetme - MongoDB'ye yazar
    """
    try:
        await mongo_save_profile(username, profile_data)
    except Exception as e:
        print(f"MongoDB profil kaydetme hatası, file-based fallback: {e}")
        save_profile_file(username, profile_data)

def save_profile(username: str, profile_data: dict) -> None:
    """
    Sync wrapper - async save_profile_async'i çağırır
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Event loop çalışıyorsa task olarak ekle
            asyncio.create_task(save_profile_async(username, profile_data))
        else:
            asyncio.run(save_profile_async(username, profile_data))
    except Exception as e:
        print(f"Async profil kaydetme hatası, file-based fallback: {e}")
        save_profile_file(username, profile_data)

def save_profile_file(username: str, profile_data: dict) -> None:
    """
    File-based profil kaydetme (fallback)
    """
    path = get_profile_path(username)
    os.makedirs(PERSONA_DIR, exist_ok=True)
    with _profile_lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)

async def update_profile_async(username: str, updates: dict) -> None:
    """
    Async profil güncelleme - MongoDB'de günceller
    """
    try:
        # MongoDB'de field-level update
        for field, value in updates.items():
            await mongo_update_profile(username, field, value)
    except Exception as e:
        print(f"MongoDB profil güncelleme hatası, file-based fallback: {e}")
        update_profile_file(username, updates)

def update_profile(username: str, updates: dict) -> None:
    """
    Sync wrapper - async update_profile_async'i çağırır
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Event loop çalışıyorsa task olarak ekle
            asyncio.create_task(update_profile_async(username, updates))
        else:
            asyncio.run(update_profile_async(username, updates))
    except Exception as e:
        print(f"Async profil güncelleme hatası, file-based fallback: {e}")
        update_profile_file(username, updates)

def update_profile_file(username: str, updates: dict) -> None:
    """
    File-based profil güncelleme (fallback)
    """
    with _profile_lock:
        profile = load_profile_file(username)
        profile.update(updates)
        save_profile_file(username, profile)

def get_all_profiles() -> dict:
    """
    Sistemdeki tüm profilleri getirir (file-based fallback)
    """
    os.makedirs(PERSONA_DIR, exist_ok=True)
    profiles = {}
    with _profile_lock:
        for file in os.listdir(PERSONA_DIR):
            if file.endswith(".json"):
                with open(os.path.join(PERSONA_DIR, file), "r", encoding="utf-8") as f:
                    profile = json.load(f)
                    # Eksik alanları tamamla (migration)
                    for key, value in DEFAULT_USER_PROFILE.items():
                        if key not in profile:
                            profile[key] = value
                    # Template'ten reply mesajı çek
                    if not profile.get("reply_messages") and "_template" in profile:
                        tpl = profile["_template"]
                        if isinstance(tpl, dict) and tpl.get("reply_messages"):
                            profile["reply_messages"] = tpl["reply_messages"]
                    # Telefon migration
                    if "phone" not in profile:
                        profile["phone"] = ""
                    # username ve display_name fallback
                    if "username" not in profile:
                        profile["username"] = file.replace(".json", "")
                    if "display_name" not in profile:
                        profile["display_name"] = profile["username"]
                    username = file.replace(".json", "")
                    profiles[username] = profile
    return profiles

def load_profile_by_user_id(user_id: int) -> Optional[dict]:
    """User ID'ye göre profil yükle"""
    profiles = get_all_profiles()
    
    for username, profile in profiles.items():
        if profile.get("user_id") == user_id:
            return profile
    
    return None

def save_profile_by_user_id(user_id: int, profile_data: dict) -> bool:
    """User ID'ye göre profili kaydet"""
    profiles = get_all_profiles()
    
    for username, profile in profiles.items():
        if profile.get("user_id") == user_id:
            # Username'i güncelle
            profile_data["username"] = username
            # Direkt file-based kaydet
            save_profile_file(username, profile_data)
            return True
    
    return False
