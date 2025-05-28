#!/usr/bin/env python3

import json
import os
from pathlib import Path

def check_spam_status():
    """Tüm botların spam durumunu kontrol et"""
    
    personas_dir = Path("data/personas")
    
    print("🔍 SPAM LOOP DURUM RAPORU")
    print("=" * 50)
    
    for persona_file in personas_dir.glob("*.json"):
        if persona_file.name == ".gitkeep":
            continue
            
        try:
            with open(persona_file, "r", encoding="utf-8") as f:
                profile = json.load(f)
            
            username = profile.get("username", persona_file.stem)
            autospam = profile.get("autospam", False)
            bot_type = profile.get("type", "unknown")
            phone = profile.get("phone", "")
            
            # Session dosyası var mı kontrol et (hem username hem telefon formatında)
            session_exists = False
            session_file_used = ""
            
            # Önce username formatını kontrol et
            username_session = f"sessions/{username}.session"
            if os.path.exists(username_session):
                session_exists = True
                session_file_used = username_session
            
            # Telefon numarası formatını kontrol et
            if phone and not session_exists:
                phone_session = f"sessions/{phone.replace('+', '_')}.session"
                if os.path.exists(phone_session):
                    session_exists = True
                    session_file_used = phone_session
            
            status_icon = "✅" if autospam else "❌"
            session_icon = "📁" if session_exists else "❌"
            
            print(f"{status_icon} {username}")
            print(f"   📋 Type: {bot_type}")
            print(f"   📱 Phone: {phone}")
            print(f"   🔄 AutoSpam: {autospam}")
            print(f"   {session_icon} Session: {session_exists}")
            if session_exists:
                print(f"   📄 Session File: {session_file_used}")
            
            if autospam and session_exists:
                print(f"   🚀 SPAM AKTIF")
            elif autospam and not session_exists:
                print(f"   ⚠️  SPAM AKTIF AMA SESSION YOK")
            elif not autospam and session_exists:
                print(f"   💤 SPAM KAPALI")
            else:
                print(f"   ❌ SPAM KAPALI VE SESSION YOK")
            
            print()
            
        except Exception as e:
            print(f"❌ {persona_file.name}: Hata - {e}")
            print()

if __name__ == "__main__":
    check_spam_status() 