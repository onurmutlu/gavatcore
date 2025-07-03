# handlers/inline_handler.py

from telethon import events
from handlers.dm_handler import handle_inline_bank_choice
from core.onboarding_flow import handle_onboarding_callback
from utils.state_utils import set_state, get_state, clear_state
from utils.log_utils import log_event
from core.analytics_logger import log_analytics
from handlers.customer_onboarding import customer_onboarding
# İleride role-based handlerlar eklerseniz (ör: admin_panel_handler, user_ticket_handler) burada import edersin

async def inline_handler(event):
    data = event.data.decode("utf-8")
    sender = await event.get_sender()
    user_id = sender.id

    # 💳 Banka seçimi inline button
    if data.startswith("bank_"):
        bank = data.split("bank_")[1]
        await set_state(user_id, "selected_bank", bank)
        await handle_inline_bank_choice(event)
        log_event(user_id, f"Inline Banka Seçimi: {bank}")
        log_analytics(user_id, "inline_bank_selected", {"bank": bank})

    # 🚀 Onboarding flow inline button
    elif data.startswith("onb_"):
        await handle_onboarding_callback(event)
        log_event(user_id, f"Inline Onboarding Step: {data}")
        log_analytics(user_id, "inline_onboarding_step", {"data": data})
    
    # 💰 Müşteri onboarding paket seçimi
    elif data.startswith("pkg_"):
        package_type = data.split("pkg_")[1]
        await customer_onboarding.handle_package_selection(event, package_type)
        log_analytics(user_id, "customer_package_selected", {"package": package_type})
    
    # ✅ Paket onayı
    elif data.startswith("confirm_"):
        package_type = data.split("confirm_")[1]
        await customer_onboarding.confirm_package_and_start_setup(event, package_type)
        log_analytics(user_id, "customer_package_confirmed", {"package": package_type})
    
    # 💳 Ödeme tamamlandı
    elif data.startswith("payment_done_"):
        package_type = data.split("payment_done_")[1]
        await customer_onboarding.handle_payment_confirmation(event, package_type)
        log_analytics(user_id, "customer_payment_claimed", {"package": package_type})
    
    # 📱 Telefon numarası girişi
    elif data == "enter_phone":
        await customer_onboarding.handle_phone_input(event)
        log_analytics(user_id, "customer_phone_input_started")
    
    # 🔙 Paketlere geri dön
    elif data == "back_to_packages":
        await customer_onboarding.start_customer_onboarding(event)
        log_analytics(user_id, "customer_back_to_packages")
    
    # 💳 Ödeme bilgileri
    elif data == "payment_info":
        await event.answer("💳 Ödeme bilgileri yukarıda gösterildi.", alert=True)
    
    # ❓ Güvenlik bilgisi
    elif data == "security_info":
        await event.answer("🔒 Bilgileriniz güvenli şekilde saklanır ve sadece bot kurulumu için kullanılır.", alert=True)

    # 🛡️ Admin paneli inline komutları (örnek)
    elif data.startswith("admin_"):
        # from handlers.admin_panel import handle_admin_inline
        # await handle_admin_inline(event)
        log_event(user_id, f"Inline Admin Command: {data}")
        log_analytics(user_id, "inline_admin_command", {"data": data})
        # await event.respond("🛡️ Admin panelinde bir özellik seçtiniz. (Demo)")

    # 🤖 GPT Modu Ayarlama
    elif data.startswith("gpt_mode_"):
        from telethon import Button
        from core.profile_loader import load_profile
        
        username = data.split("gpt_mode_")[1]
        try:
            profile = load_profile(username)
            current_mode = profile.get("gpt_enhanced", False)
            
            buttons = [
                [Button.inline("❌ GPT OFF", f"gpt_set_off_{username}")],
                [Button.inline("🤖 HYBRID", f"gpt_set_hybrid_{username}")],
                [Button.inline("🧠 GPT_ONLY", f"gpt_set_only_{username}")],
                [Button.inline("🔙 Geri", f"panel_back_{username}")]
            ]
            
            status = "✅ Aktif" if current_mode else "❌ Kapalı"
            await event.edit(f"🤖 **GPT Modu Ayarları**\n\nMevcut durum: {status}\n\nYeni modu seç:", buttons=buttons, parse_mode="markdown")
            log_event(user_id, f"GPT mode panel açıldı: {username}")
            
        except Exception as e:
            await event.edit(f"❌ Hata: {e}")

    elif data.startswith("gpt_set_"):
        from core.profile_loader import update_profile
        
        parts = data.split("_")
        mode = parts[2]  # off, hybrid, only
        username = "_".join(parts[3:])
        
        try:
            if mode == "off":
                update_profile(username, {"gpt_enhanced": False, "gpt_mode": "off"})
                status_msg = "❌ GPT kapatıldı"
            elif mode == "hybrid":
                update_profile(username, {"gpt_enhanced": True, "gpt_mode": "hybrid"})
                status_msg = "🤖 HYBRID modu aktif"
            elif mode == "only":
                update_profile(username, {"gpt_enhanced": True, "gpt_mode": "gpt_only"})
                status_msg = "🧠 GPT_ONLY modu aktif"
            
            await event.edit(f"✅ **{username}** için {status_msg}")
            log_event(user_id, f"GPT mode değiştirildi: {username} -> {mode}")
            log_analytics(user_id, "gpt_mode_changed", {"username": username, "mode": mode})
            
        except Exception as e:
            await event.edit(f"❌ Ayar kaydedilemedi: {e}")

    # 🕒 Spam Sıklığı Ayarlama
    elif data.startswith("spam_speed_"):
        from telethon import Button
        from core.profile_loader import load_profile
        
        username = data.split("spam_speed_")[1]
        try:
            profile = load_profile(username)
            current_speed = profile.get("spam_speed", "medium")
            
            buttons = [
                [Button.inline("🐢 Yavaş", f"speed_set_slow_{username}")],
                [Button.inline("⚖️ Orta", f"speed_set_medium_{username}")],
                [Button.inline("🚀 Hızlı", f"speed_set_fast_{username}")],
                [Button.inline("🔙 Geri", f"panel_back_{username}")]
            ]
            
            await event.edit(f"🕒 **Spam Sıklığı Ayarları**\n\nMevcut: {current_speed.title()}\n\nYeni hızı seç:", buttons=buttons, parse_mode="markdown")
            log_event(user_id, f"Spam speed panel açıldı: {username}")
            
        except Exception as e:
            await event.edit(f"❌ Hata: {e}")

    elif data.startswith("speed_set_"):
        from core.profile_loader import update_profile
        
        parts = data.split("_")
        speed = parts[2]  # slow, medium, fast
        username = "_".join(parts[3:])
        
        try:
            update_profile(username, {"spam_speed": speed})
            
            speed_emoji = {"slow": "🐢", "medium": "⚖️", "fast": "🚀"}
            await event.edit(f"✅ **{username}** spam hızı {speed_emoji.get(speed, '')} {speed.title()} olarak ayarlandı")
            log_event(user_id, f"Spam speed değiştirildi: {username} -> {speed}")
            log_analytics(user_id, "spam_speed_changed", {"username": username, "speed": speed})
            
        except Exception as e:
            await event.edit(f"❌ Ayar kaydedilemedi: {e}")

    # 💎 VIP Mesajı Düzenleme
    elif data.startswith("vip_edit_"):
        username = data.split("vip_edit_")[1]
        await set_state(user_id, "awaiting_vip_message", username)
        await event.edit("💎 **VIP Mesajı Düzenleme**\n\nYeni VIP mesajını yaz, ben güncelleyeyim.\n\n⚠️ Sonraki mesajın VIP mesajı olarak kaydedilecek.")
        log_event(user_id, f"VIP mesaj düzenleme başlatıldı: {username}")

    # 💳 Papara Bilgisi Güncelleme
    elif data.startswith("update_papara_"):
        username = data.split("update_papara_")[1]
        await set_state(user_id, "awaiting_papara_info", username)
        await event.edit("💳 **Papara Bilgisi Güncelleme**\n\nYeni papara bilgisini şu formatta yaz:\n\n`IBAN | Ad Soyad | Papara ID`\n\n⚠️ Sonraki mesajın papara bilgisi olarak kaydedilecek.")
        log_event(user_id, f"Papara bilgi güncelleme başlatıldı: {username}")

    # 📊 Durum Görüntüleme
    elif data.startswith("status_"):
        from core.profile_loader import load_profile
        
        username = data.split("status_")[1]
        try:
            profile = load_profile(username)
            
            gpt_mode = profile.get("gpt_enhanced", False)
            spam_speed = profile.get("spam_speed", "medium")
            reply_mode = profile.get("reply_mode", "manual")
            autospam = profile.get("autospam", False)
            
            status_text = f"""📊 **{username} Durum Raporu**

🤖 GPT Enhanced: {'✅ Aktif' if gpt_mode else '❌ Kapalı'}
🕒 Spam Hızı: {spam_speed.title()}
🧠 Yanıt Modu: {reply_mode}
🔄 Auto Spam: {'✅ Aktif' if autospam else '❌ Kapalı'}

VIP Mesajı: {len(profile.get('vip_message', '')) > 0}
Papara: {len(profile.get('papara_iban', '')) > 0}
Flört Şablonları: {len(profile.get('flirt_templates', []))}"""
            
            await event.edit(status_text, parse_mode="markdown")
            log_analytics(user_id, "user_status_viewed", {"username": username})
            
        except Exception as e:
            await event.edit(f"❌ Durum alınamadı: {e}")

    # 🔙 Panel Geri Dönüş
    elif data.startswith("panel_back_"):
        from telethon import Button
        from core.profile_loader import load_profile
        
        username = data.split("panel_back_")[1]
        try:
            profile = load_profile(username)
            current_gpt_mode = profile.get("gpt_enhanced", False)
            current_spam_speed = profile.get("spam_speed", "medium")
            
            buttons = [
                [Button.inline("🤖 GPT Modu", f"gpt_mode_{username}")],
                [Button.inline("🕒 Spam Sıklığı", f"spam_speed_{username}")],
                [Button.inline("💎 VIP Mesajı", f"vip_edit_{username}")],
                [Button.inline("💳 Papara Bilgisi", f"update_papara_{username}")],
                [Button.inline("📊 Durum", f"status_{username}")]
            ]
            
            status_text = f"""🛠️ **{username} Kontrol Paneli**

🤖 GPT Modu: {'✅ Aktif' if current_gpt_mode else '❌ Kapalı'}
🕒 Spam Hızı: {current_spam_speed.title()}

Ayarlamak istediğin özelliği seç:"""
            
            await event.edit(status_text, buttons=buttons, parse_mode="markdown")
            
        except Exception as e:
            await event.edit(f"❌ Panel yüklenemedi: {e}")

    # 👤 Kullanıcıya özel inline komutlar (örnek)
    elif data.startswith("user_"):
        # from handlers.user_commands import handle_user_inline
        # await handle_user_inline(event)
        log_event(user_id, f"Inline User Command: {data}")
        log_analytics(user_id, "inline_user_command", {"data": data})
        # await event.respond("👤 Kullanıcı paneli fonksiyonu (Demo)")

    # 🏭 İçerik üretici (şovcu) paneli inline komutları (örnek)
    elif data.startswith("producer_"):
        # from handlers.producer_panel import handle_producer_inline
        # await handle_producer_inline(event)
        log_event(user_id, f"Inline Producer Command: {data}")
        log_analytics(user_id, "inline_producer_command", {"data": data})
        # await event.respond("🏭 Üretici paneli fonksiyonu (Demo)")

    # 🧠 Buraya istediğin kadar yeni inline prefix & handler ekleyebilirsin

    else:
        await clear_state(user_id)
        log_event(user_id, f"Unknown Inline Callback: {data}")
        log_analytics(user_id, "inline_unknown", {"data": data})
        # await event.respond("Tanımsız inline callback geldi (loglandı).")

