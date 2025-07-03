# // handlers/user_commands.py

import os
from datetime import datetime
from telethon import events
from core.profile_loader import update_profile, load_profile
from utils.log_utils import log_event
from utils.payment_utils import generate_payment_message, load_banks
from core.license_checker import LicenseChecker
from core.analytics_logger import log_analytics

SESSION_DIR = "sessions"

async def handle_user_command(event):
    if not event.is_private:
        return

    sender = await event.get_sender()
    user_id = sender.id
    username = sender.username or f"user_{user_id}"
    message = event.raw_text.strip()
    lowered = message.lower()
    profile = load_profile(username)
    license_checker = LicenseChecker()

    log_analytics(username, "user_command_received", {"command": lowered})

    # 📋 /menü [metin]
    if lowered.startswith("/menü") or lowered.startswith("/menu"):
        content = message.split(" ", 1)[-1].strip()
        if not content:
            await event.respond("⚠️ Menü içeriği boş olamaz.")
            return
        update_profile(username, {"services_menu": content})
        await event.respond("✅ Hizmet menüsü güncellendi.")
        log_event(username, "📝 Hizmet menüsü güncellendi.")
        log_analytics(username, "menu_updated", {"text": content})

    # 🏦 /iban_kaydet TRxx... | Ad Soyad | Banka Adı
    elif lowered.startswith("/iban_kaydet"):
        try:
            _, data = message.split(" ", 1)
            iban, name, bank = [x.strip() for x in data.split("|")]
            update_profile(username, {
                "personal_iban": {
                    "iban": iban,
                    "name": name,
                    "bank_name": bank
                }
            })
            await event.respond(f"✅ IBAN bilgisi güncellendi:\n🏦 {bank}\n💳 {iban}\n👤 {name}")
            log_event(username, f"🏦 IBAN güncellendi: {bank} | {iban} | {name}")
            log_analytics(username, "iban_saved", {"bank": bank})
        except:
            await event.respond("⚠️ Format hatası. Şöyle yaz:\n/iban_kaydet TRxx... | Ad Soyad | Banka Adı")

    # 💸 /papara IBAN | Ad Soyad | Papara ID
    elif lowered.startswith("/papara"):
        try:
            _, data = message.split(" ", 1)
            iban, name, pid = [x.strip() for x in data.split("|")]
            update_profile(username, {
                "papara_iban": iban,
                "papara_name": name,
                "papara_note": pid
            })
            await event.respond(f"✅ Papara bilgisi güncellendi:\n💳 {iban}\n👤 {name}\n📝 ID: `{pid}`")
            log_event(username, f"💸 Papara güncellendi: {iban} | {name} | ID: {pid}")
            log_analytics(username, "papara_saved", {"name": name, "id": pid})
        except:
            await event.respond("⚠️ Format hatası. Şöyle yaz:\n/papara IBAN | Ad Soyad | Papara ID")

    # 📨 /iban Garanti (veya başka banka)
    elif lowered.startswith("/iban"):
        try:
            _, bank_name = message.split(" ", 1)
            banks_data = load_banks()
            msg = generate_payment_message(bank_name.strip(), profile, banks_data)
            await event.respond(msg, parse_mode="markdown")
            log_analytics(username, "payment_info_requested", {"bank": bank_name.strip()})
        except:
            await event.respond("⚠️ Kullanım: `/iban Garanti`\nBanka adı girilmedi veya tanımlı değil.")

    # 💌 /flört
    elif lowered.startswith("/flört"):
        templates = message[len("/flört"):].strip().splitlines()
        templates = [x.strip() for x in templates if x.strip()]
        if not templates:
            await event.respond("⚠️ En az 1 mesaj şablonu girmelisin.")
            return
        update_profile(username, {"flirt_templates": templates})
        await event.respond(f"✅ {len(templates)} flört mesajı kaydedildi.")
        log_event(username, "💌 Flört şablonları güncellendi.")
        log_analytics(username, "flirt_templates_updated", {"count": len(templates)})

    # 🧠 /mod
    elif lowered.startswith("/mod"):
        try:
            _, mode = message.split(" ", 1)
            mode = mode.strip()
            if mode not in ["manual", "gpt", "hybrid", "manualplus"]:
                raise ValueError()
            update_profile(username, {"reply_mode": mode})
            await event.respond(f"✅ Yanıt modu `{mode}` olarak ayarlandı.")
            log_event(username, f"🧠 Yanıt modu değişti: {mode}")
            log_analytics(username, "reply_mode_changed", {"mode": mode})
        except:
            await event.respond("⚠️ Geçerli modlar: manual, gpt, hybrid, manualplus")

    # 🧾 /bilgilerim
    elif lowered.startswith("/bilgilerim"):
        text = f"""🧾 *Profil Bilgilerin*:

👤 Yanıt Modu: `{profile.get("reply_mode")}`
💌 Flört Şablonu Sayısı: {len(profile.get("flirt_templates", []))}
📋 Hizmet Menüsü: `{profile.get("services_menu", "")[:50]}...`
🏦 IBAN: `{profile.get('personal_iban', {}).get('iban', 'Yok')}`
💳 Papara IBAN: `{profile.get('papara_iban', 'Yok')}`
📝 Papara ID: `{profile.get('papara_note', 'Yok')}`
"""
        await event.respond(text, parse_mode="markdown")
        log_analytics(username, "profile_viewed")

    # 📡 /session_durum
    elif lowered.startswith("/session_durum"):
        session_file = os.path.join(SESSION_DIR, f"{username}.session")
        if os.path.exists(session_file):
            await event.respond("✅ Oturum dosyası mevcut. Bağlantı aktif olabilir.")
        else:
            await event.respond("❌ Oturum dosyası bulunamadı.")
        log_analytics(username, "session_status_checked")

    # ♻️ /session_yenile
    elif lowered.startswith("/session_yenile"):
        await event.respond("⚠️ Oturum yenileme işlemi şu an manuel yapılmalı.\nYeni giriş için @GavatBaba ile iletişime geç.")
        log_analytics(username, "session_renew_requested")

    # ⏳ /lisans_süre
    elif lowered.startswith("/lisans_süre"):
        session_time = license_checker.get_session_creation_time(username)
        is_valid = license_checker.is_license_valid(user_id, session_time, profile)
        status = license_checker.get_license_status(user_id)
        elapsed = datetime.now() - session_time
        dk = int(elapsed.total_seconds() // 60)
        await event.respond(f"""
📜 *Lisans Bilgisi:*
🔑 Durum: `{status}`
⏱️ Geçen Süre: `{dk} dakika`
📅 Başlangıç: `{session_time.strftime('%Y-%m-%d %H:%M')}`
✅ Geçerli: {"Evet" if is_valid else "Hayır"}
""", parse_mode="markdown")
        log_analytics(username, "license_duration_checked", {"minutes": dk, "status": status})

    # ⛔ /dur
    elif lowered.startswith("/dur"):
        update_profile(username, {"autospam": False})
        await event.respond("⛔ Otomatik mesajlaşma durduruldu.")
        log_event(username, "✋ Otomatik spam durduruldu")
        log_analytics(username, "autospam_stopped")

    # ▶️ /devam
    elif lowered.startswith("/devam"):
        update_profile(username, {"autospam": True})
        await event.respond("✅ Otomatik mesajlaşma başlatıldı.")
        log_event(username, "▶️ Otomatik spam başlatıldı")
        log_analytics(username, "autospam_started")

    # 🆘 /yardım
    elif lowered.startswith("/yardım") or lowered.startswith("/help"):
        await event.respond("""ℹ️ *Komutlar Listesi:*

📋 /menü [metin] — Hizmet menüsünü günceller  
💌 /flört [...] — Her satır bir flört mesajı  
🏦 /iban [Banka Adı] — Ödeme bilgisini göster  
📝 /iban_kaydet TRxx | İsim | Banka — IBAN kaydet  
💳 /papara IBAN | Ad Soyad | ID — Papara bilgisi  
🧠 /mod [manual/gpt/hybrid/manualplus] — Yanıt modu  
🧾 /bilgilerim — Tüm bilgileri göster  
📡 /session_durum — Oturum dosyası kontrol  
♻️ /session_yenile — Oturum yenileme (manuel)  
⏳ /lisans_süre — Lisans durumu  
⛔ /dur — Otomatik mesaj durdur  
▶️ /devam — Otomatik mesaj başlat

Hepsi sadece özel mesajda çalışır 💌
""", parse_mode="markdown")
        log_analytics(username, "help_command_shown")
