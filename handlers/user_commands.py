# // handlers/user_commands.py
import os
from datetime import datetime
from telethon import events
from core.profile_loader import update_profile, load_profile
from utils.log_utils import log_event
from utils.payment_utils import generate_payment_message, load_banks
from core.license_checker import LicenseChecker
from core.analytics_logger import log_analytics
from handlers.customer_onboarding import customer_onboarding

SESSION_DIR = "sessions"

async def handle_user_command(event):
    if not event.is_private:
        return

    sender = await event.get_sender()
    user_id = sender.id
    username = sender.username or f"user_{user_id}"
    message = event.raw_text.strip()
    lowered = message.lower()
    try:
        profile = load_profile(username)
    except:
        profile = {}
    license_checker = LicenseChecker()

    log_analytics(username, "user_command_received", {"command": lowered})

    # 📋 /menü [metin]
    if lowered.startswith("/menü") or lowered.startswith("/menu"):
        content = message.split(" ", 1)[-1].strip()
        if not content or content.startswith("/menü") or content.startswith("/menu"):
            await event.respond("⚠️ Menü içeriği boş olamaz.")
            return
        update_profile(username, {"services_menu": content})
        await event.respond("✅ Hizmet menüsü güncellendi.")
        log_event(username, "📝 Hizmet menüsü güncellendi.")
        log_analytics(username, "menu_updated", {"text": content})

    # 🎭 /show_menu [metin] - Yeni show menü sistemi
    elif lowered.startswith("/show_menu") or lowered.startswith("/show_menü"):
        content = message.split(" ", 1)[-1].strip()
        if not content or content.startswith("/show_menu") or content.startswith("/show_menü"):
            # Mevcut show menüsünü göster
            from utils.menu_manager import show_menu_manager
            current_menu = show_menu_manager.get_show_menu(username, compact=False)
            if current_menu:
                await event.respond(f"📋 Mevcut show menün:\n\n{current_menu}")
            else:
                await event.respond("❌ Henüz show menün yok. Kullanım:\n/show_menu [menü metni]")
            return
        
        # Show menüsünü güncelle
        from utils.menu_manager import show_menu_manager
        success = show_menu_manager.update_show_menu(username, content)
        if success:
            await event.respond("✅ Show menüsü güncellendi!")
            log_event(username, "🎭 Show menüsü güncellendi.")
            log_analytics(username, "show_menu_updated", {"text": content})
        else:
            await event.respond("❌ Show menüsü güncellenirken hata oluştu.")

    # 🎭 /show_compact - Kısa show menüsünü göster
    elif lowered.startswith("/show_compact"):
        from utils.menu_manager import show_menu_manager
        compact_menu = show_menu_manager.get_show_menu(username, compact=True)
        if compact_menu:
            await event.respond(f"📋 Kısa show menün:\n\n{compact_menu}")
        else:
            await event.respond("❌ Kısa show menün bulunamadı.")
        log_analytics(username, "show_compact_viewed")

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
            await event.respond(f"✅ IBAN bilgisi kaydedildi:\n🏦 {bank}\n💳 {iban}\n👤 {name}")
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
    elif lowered.startswith("/iban "):
        try:
            _, bank_name = message.split(" ", 1)
            banks_data = load_banks()
            msg = generate_payment_message(bank_name.strip(), profile, banks_data)
            await event.respond(msg, parse_mode="markdown")
            log_analytics(username, "payment_info_requested", {"bank": bank_name.strip()})
        except:
            await event.respond("⚠️ Kullanım: `/iban Garanti`\nBanka adı girilmedi veya tanımlı değil.")

    # 💌 /flört satır satır (multi-line) veya tek satır
    elif lowered.startswith("/flört"):
        content = message[len("/flört"):].strip()
        if not content:
            await event.respond("⚠️ En az 1 mesaj şablonu girmelisin. Her satıra 1 mesaj!")
            return
        templates = [x.strip() for x in content.splitlines() if x.strip()]
        update_profile(username, {"flirt_templates": templates})
        await event.respond(f"✅ {len(templates)} flört mesajı kaydedildi.")
        log_event(username, "💌 Flört şablonları güncellendi.")
        log_analytics(username, "flirt_templates_updated", {"count": len(templates)})

    # 🧠 /mod [manual/gpt/hybrid/manualplus]
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
        flirt_count = len(profile.get("flirt_templates", []))
        menu_preview = profile.get("services_menu", "")[:60] + ("..." if len(profile.get("services_menu", "")) > 60 else "")
        text = f"""🧾 *Profil Bilgilerin*:

👤 Yanıt Modu: `{profile.get("reply_mode", "-")}`
💌 Flört Şablonu Sayısı: {flirt_count}
📋 Hizmet Menüsü: `{menu_preview}`
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

    # 🚀 /onboarding_yenile
    elif lowered.startswith("/onboarding_yenile"):
        # Onboarding baştan başlat (geliştiriciye referans)
        update_profile(username, {"onboarding_step": 0})
        await event.respond("🚀 Onboarding sıfırlandı! Yeniden başlayabilirsin.")
        log_event(username, "onboarding_reset")
        log_analytics(username, "onboarding_reset")
    
    # 💰 /musteri_panel - Müşteri self-service paneli
    elif lowered.startswith("/musteri_panel") or lowered.startswith("/customer"):
        await customer_onboarding.start_customer_onboarding(event)
        log_analytics(username, "customer_panel_accessed")
    
    # 📊 /dashboard - Müşteri dashboard'u
    elif lowered.startswith("/dashboard"):
        try:
            profile = load_profile(username)
            if profile.get("type") == "customer_bot":
                await customer_onboarding.show_customer_dashboard(event, profile)
            else:
                await event.respond("❌ Bu komut sadece müşteri hesapları için kullanılabilir.")
        except:
            await event.respond("❌ Profil bulunamadı. Önce /musteri_panel ile kayıt olun.")
        log_analytics(username, "dashboard_accessed")
    
    # 🤖 /bot_durum - Bot durumu kontrolü
    elif lowered.startswith("/bot_durum"):
        try:
            profile = load_profile(username)
            if profile.get("type") == "customer_bot":
                customer_info = profile.get("customer_info", {})
                bot_status = "🟢 Aktif" if profile.get("customer_status") == "active" else "🔴 Pasif"
                
                await event.respond(
                    f"🤖 **Bot Durum Raporu**\n\n"
                    f"**Bot:** @{profile.get('username', 'Bilinmiyor')}\n"
                    f"**Durum:** {bot_status}\n"
                    f"**Paket:** {customer_info.get('package_name', 'Bilinmiyor')}\n"
                    f"**Bitiş:** {customer_info.get('expires_at', 'Bilinmiyor')[:10]}\n\n"
                    f"**Ayarlar:**\n"
                    f"• DM Yanıtlama: {'✅' if profile.get('bot_config', {}).get('dm_invite_enabled') else '❌'}\n"
                    f"• Grup Daveti: {'✅' if profile.get('bot_config', {}).get('group_invite_aggressive') else '❌'}\n"
                    f"• Yanıt Modu: {profile.get('reply_mode', 'manual')}"
                )
            else:
                await event.respond("❌ Bu komut sadece müşteri hesapları için kullanılabilir.")
        except:
            await event.respond("❌ Bot durumu alınamadı.")
        log_analytics(username, "bot_status_checked")
    
    # 📞 /destek - Teknik destek
    elif lowered.startswith("/destek"):
        await event.respond(
            "📞 **Teknik Destek**\n\n"
            "Destek için aşağıdaki kanalları kullanabilirsiniz:\n\n"
            "• **Telegram:** @gavatbaba\n"
            "• **WhatsApp:** +90 XXX XXX XX XX\n"
            "• **E-mail:** destek@gavatcore.com\n\n"
            "Sorunuzda bot username'inizi belirtmeyi unutmayın!"
        )
        log_analytics(username, "support_requested")

    # 👁‍🗨 /state
    elif lowered.startswith("/state"):
        # Geliştiricinin debug için state dump’ı
        await event.respond(f"```{profile}```", parse_mode="markdown")
        log_event(username, "profile_state_dumped")

    # 🆘 /yardım
    elif lowered.startswith("/yardım") or lowered.startswith("/help"):
        await event.respond("""ℹ️ *Komutlar Listesi:*

📋 /menü [metin] — Hizmet menüsünü günceller  
🎭 /show_menu [metin] — Show menüsünü günceller  
🎭 /show_compact — Kısa show menüsünü göster  
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
🚀 /onboarding_yenile — Onboarding sıfırla (deneme)
👁‍🗨 /state — Profil state'i dump (debug)

Hepsi sadece özel mesajda çalışır 💌
""", parse_mode="markdown")
        log_analytics(username, "help_command_shown")

    # 🚫 Bilinmeyen komut
    else:
        await event.respond("❓ Komut anlaşılamadı. /yardım ile tüm komutları görebilirsin.")
        log_analytics(username, "unknown_command", {"command": lowered})
