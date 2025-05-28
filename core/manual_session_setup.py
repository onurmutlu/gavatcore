#!/usr/bin/env python3
# core/manual_session_setup.py
import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError
import getpass

SESSIONS_DIR = "sessions"
PERSONAS_DIR = "data/personas"

# Test ve örnek dosyaları için filtre listesi
EXCLUDED_PATTERNS = [
    "test_",           # test_ ile başlayan dosyalar
    "example",         # example içeren dosyalar
    "demo",           # demo içeren dosyalar
    ".banned",        # yasaklı hesaplar
    ".disabled",      # devre dışı hesaplar
    ".sample"         # örnek dosyalar
]

class PersonaType:
    BOT = "bot"
    USER = "user"
    CUSTOMER = "customer"

class SessionManager:
    def __init__(self):
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        if not self.api_id or not self.api_hash:
            raise ValueError("❌ API ID veya HASH eksik. Lütfen .env dosyanızı kontrol edin.")
        self.api_id = int(self.api_id)
        os.makedirs(SESSIONS_DIR, exist_ok=True)

    async def create_session(self, phone: str, persona_data: Optional[Dict] = None) -> Optional[str]:
        """Belirtilen telefon numarası için session oluşturur"""
        session_name = None
        session_path = None
        client = None
        
        try:
            # Session adını belirle - her zaman telefon numarası formatında
            session_name = phone.replace("+", "_")
            print(f"📱 Session oluşturuluyor: {session_name} (telefon numarası formatı)")
            
            session_path = os.path.join(SESSIONS_DIR, f"{session_name}.session")
            
            # Eğer session dosyası varsa kontrol et
            if os.path.exists(session_path):
                # Mevcut session'ı test et
                client = TelegramClient(session_path, self.api_id, self.api_hash)
                await client.connect()
                
                if await client.is_user_authorized():
                    print(f"✅ Mevcut session aktif: {session_name}")
                    me = await client.get_me()
                    print(f"👤 Mevcut hesap: {me.first_name} (@{me.username or me.id})")
                    
                    if input("⚠️ Session aktif. Yeniden oluşturulsun mu? (E/h): ").lower().startswith('h'):
                        print("✋ Session oluşturma işlemi iptal edildi")
                        return session_path
                
                await client.disconnect()
                client = None
                
                # Session'ı yeniden oluştur
                os.remove(session_path)
                print(f"🔄 Session yeniden oluşturuluyor: {session_name}")
            
            # Yeni session oluştur
            client = TelegramClient(session_path, self.api_id, self.api_hash)
            await client.connect()
            
            if not await client.is_user_authorized():
                await client.send_code_request(phone)
                code = input(f"🔐 {phone} için Telegram'dan gelen kodu girin: ").strip()
                try:
                    await client.sign_in(phone, code)
                except SessionPasswordNeededError:
                    pw = getpass.getpass("🔒 2FA şifrenizi girin (ekranda görünmez): ").strip()
                    await client.sign_in(password=pw)
                except PhoneNumberInvalidError:
                    print(f"❌ Geçersiz telefon numarası: {phone}")
                    if os.path.exists(session_path):
                        os.remove(session_path)
                    return None
            
            me = await client.get_me()
            print(f"✅ Giriş başarılı: {me.first_name} (@{me.username or me.id})")
            print(f"📁 Session dosyası: {session_path}")
            
            if persona_data:
                # Telegram'dan alınan bilgileri persona'ya ekle
                persona_data.update({
                    "user_id": me.id,
                    "telegram_username": me.username,
                    "telegram_first_name": me.first_name,
                    "telegram_last_name": me.last_name
                })
                self._update_persona_file(phone, persona_data)
            
            return session_path
            
        except Exception as e:
            print(f"❌ Oturum açma başarısız: {e}")
            if session_path and os.path.exists(session_path):
                os.remove(session_path)
            return None
            
        finally:
            if client:
                await client.disconnect()

    def _update_persona_file(self, phone: str, data: Dict):
        """Persona dosyasını user_id ile günceller"""
        for file in Path(PERSONAS_DIR).glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    persona = json.load(f)
                if persona.get("phone") == phone:
                    persona.update(data)
                    with open(file, "w", encoding="utf-8") as f:
                        json.dump(persona, f, indent=2, ensure_ascii=False)
                    print(f"✅ Persona dosyası güncellendi: {file}")
                    break
            except Exception as e:
                print(f"❌ Persona dosyası güncellenirken hata: {e}")

    def _is_excluded_file(self, filename: str) -> bool:
        """Dosyanın test veya örnek dosya olup olmadığını kontrol eder"""
        filename = filename.lower()
        return any(pattern.lower() in filename for pattern in EXCLUDED_PATTERNS)

    def load_personas(self) -> Dict[str, List[Dict]]:
        """Persona dosyalarını yükler ve tipine göre gruplar"""
        personas = {
            PersonaType.BOT: [],
            PersonaType.USER: [],
            PersonaType.CUSTOMER: []
        }
        
        for file in Path(PERSONAS_DIR).glob("*.json"):
            # Test ve örnek dosyalarını atla
            if self._is_excluded_file(file.name):
                continue
                
            try:
                with open(file, "r", encoding="utf-8") as f:
                    persona = json.load(f)
                    # Aktif persona kontrolü
                    if not persona.get("active", True):  # active alanı yoksa True kabul et
                        continue
                        
                    p_type = persona.get("type", "user")
                    if p_type == "customer_bot":
                        personas[PersonaType.CUSTOMER].append(persona)
                    else:
                        personas[p_type].append(persona)
            except Exception as e:
                print(f"❌ Persona dosyası okunamadı {file}: {e}")
        
        return personas

async def interactive_setup():
    manager = SessionManager()
    personas = manager.load_personas()
    
    while True:
        print("\n🤖 Session Kurulum Menüsü")
        print("=" * 50)
        print("1) Tüm aktif persona'lar için otomatik session kur")
        print("2) Sadece botlar için session kur")
        print("3) Sadece kullanıcılar için session kur")
        print("4) Sadece müşteri botları için session kur")
        print("5) Tek bir persona için session kur")
        print("6) Yeni telefon numarası ile session kur")
        print("0) Çıkış")
        
        choice = input("\n👉 Seçiminiz: ").strip()
        
        if choice == "0":
            break
            
        elif choice == "1":
            all_personas = []
            for p_list in personas.values():
                all_personas.extend(p_list)
            if not all_personas:
                print("❌ Aktif persona bulunamadı!")
                continue
                
            print(f"\n📱 Toplam {len(all_personas)} aktif persona bulundu:")
            for persona in all_personas:
                print(f"- {persona['username']} ({persona['type']})")
            
            if input("\n⚠️ Tüm persona'lar için session kurulacak. Devam? (E/h): ").lower() != 'h':
                for persona in all_personas:
                    if phone := persona.get("phone"):
                        print(f"\n📱 {persona['username']} için session kuruluyor...")
                        await manager.create_session(phone, persona)
        
        elif choice in ["2", "3", "4"]:
            p_type = {
                "2": PersonaType.BOT,
                "3": PersonaType.USER,
                "4": PersonaType.CUSTOMER
            }[choice]
            
            type_personas = personas[p_type]
            if not type_personas:
                print(f"❌ Aktif {p_type} persona bulunamadı!")
                continue
                
            print(f"\n📱 {len(type_personas)} adet {p_type} bulundu:")
            for persona in type_personas:
                print(f"- {persona['username']}")
                
            if input("\n⚠️ Tüm persona'lar için session kurulacak. Devam? (E/h): ").lower() != 'h':
                for persona in type_personas:
                    if phone := persona.get("phone"):
                        print(f"\n📱 {persona['username']} için session kuruluyor...")
                        await manager.create_session(phone, persona)
        
        elif choice == "5":
            print("\n📱 Mevcut Persona'lar:")
            all_personas = []
            for p_list in personas.values():
                all_personas.extend(p_list)
                
            if not all_personas:
                print("❌ Aktif persona bulunamadı!")
                continue
            
            for i, persona in enumerate(all_personas, 1):
                print(f"{i}) {persona['username']} ({persona['type']})")
            
            try:
                idx = int(input("\n👉 Persona numarası seçin: ").strip()) - 1
                persona = all_personas[idx]
                if phone := persona.get("phone"):
                    await manager.create_session(phone, persona)
                else:
                    print("❌ Bu persona için telefon numarası tanımlanmamış!")
            except (ValueError, IndexError):
                print("❌ Geçersiz seçim!")
        
        elif choice == "6":
            phone = input("📞 Telefon numarasını girin (+90xxxxxxxxxx): ").strip()
            await manager.create_session(phone)
        
        else:
            print("❌ Geçersiz seçim!")

if __name__ == "__main__":
    try:
        asyncio.run(interactive_setup())
    except KeyboardInterrupt:
        print("\n\n👋 Session kurulum işlemi sonlandırıldı.")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
