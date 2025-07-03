#!/usr/bin/env python3
# handlers/customer_onboarding.py - Müşteri Self-Service Onboarding Sistemi

import asyncio
import os
import json
import time
from datetime import datetime, timedelta
from telethon import Button, events
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PasswordHashInvalidError
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, GAVATCORE_ADMIN_ID
from core.session_manager import open_session, get_session_path
from core.profile_loader import save_profile, load_profile, update_profile
from core.profile_generator import generate_bot_persona, generate_showcu_persona
from utils.log_utils import log_event
from core.analytics_logger import log_analytics
from utils.redis_client import set_state, get_state, delete_state

# Onboarding state management
CUSTOMER_ONBOARDING_STATE = {}

# Paket fiyatları ve özellikler
PACKAGES = {
    "basic": {
        "name": "Temel Paket",
        "price": 500,
        "features": [
            "1 Bot Hesabı",
            "Manuel Yanıtlama (Kendi yazarsın)",
            "Temel DM Daveti (%30 şans)",
            "Basit Grup Daveti",
            "Temel Menü Sistemi",
            "7 Gün WhatsApp Destek"
        ],
        "duration_days": 30,
        "bot_limits": 1,
        "gpt_enabled": False,
        "reply_mode": "manual",
        "dm_invite_chance": 0.3,
        "group_invite_type": "basic",
        "support_level": "basic"
    },
    "premium": {
        "name": "Premium Paket", 
        "price": 1000,
        "features": [
            "1 Bot Hesabı",
            "GPT-4 AI Yanıtlama (Hybrid)",
            "Akıllı DM Daveti (%50 şans)",
            "Agresif Grup Daveti",
            "VIP Satış Funnel'ı",
            "Gelişmiş Menü Sistemi",
            "Analytics Dashboard",
            "15 Gün Telegram + WhatsApp Destek"
        ],
        "duration_days": 30,
        "bot_limits": 1,
        "gpt_enabled": True,
        "reply_mode": "hybrid",
        "dm_invite_chance": 0.5,
        "group_invite_type": "aggressive",
        "support_level": "premium"
    },
    "enterprise": {
        "name": "Kurumsal Paket",
        "price": 2000,
        "features": [
            "1 Bot Hesabı",
            "Özel GPT-4 Eğitimi (Full AI)",
            "Çok Agresif DM Daveti (%70 şans)", 
            "Çok Agresif Grup Stratejileri",
            "Özel VIP Funnel Tasarımı",
            "Gelişmiş Analytics + Raporlama",
            "Özel Spam Koruması",
            "Multi-Platform Destek",
            "7/24 Öncelikli Destek"
        ],
        "duration_days": 30,
        "bot_limits": 1,
        "gpt_enabled": True,
        "reply_mode": "gpt_enhanced",
        "dm_invite_chance": 0.7,
        "group_invite_type": "very_aggressive",
        "support_level": "enterprise"
    }
}

class CustomerOnboardingHandler:
    def __init__(self):
        self.pending_sessions = {}  # {user_id: {"phone": "+90xxx", "step": "code/password", "client": client}}
        
    async def start_customer_onboarding(self, event):
        """Müşteri onboarding sürecini başlatır"""
        sender = await event.get_sender()
        user_id = sender.id
        username = sender.username or f"user_{user_id}"
        
        # Mevcut müşteri kontrolü
        try:
            profile = load_profile(username)
            if profile.get("customer_status") == "active":
                await self.show_customer_dashboard(event, profile)
                return
        except:
            pass
        
        # Hoş geldin mesajı ve paket seçimi
        await event.respond(
            "🎉 **GAVATCORE Müşteri Paneline Hoş Geldiniz!**\n\n"
            "Telegram bot sistemimizle işinizi büyütün:\n"
            "• Otomatik müşteri yanıtlama\n"
            "• Akıllı grup daveti sistemi\n"
            "• VIP satış funnel'ları\n"
            "• Gelişmiş analitikler\n\n"
            "Hangi paketi tercih edersiniz?",
            buttons=[
                [Button.inline("💎 Temel - 500₺", data="pkg_basic")],
                [Button.inline("🔥 Premium - 1000₺", data="pkg_premium")],
                [Button.inline("👑 Kurumsal - 2000₺", data="pkg_enterprise")],
                [Button.inline("ℹ️ Paket Karşılaştırması", data="pkg_compare")]
            ],
            parse_mode="markdown"
        )
        
        # State kaydet
        CUSTOMER_ONBOARDING_STATE[user_id] = {
            "step": "package_selection",
            "username": username,
            "started_at": time.time()
        }
        
        log_analytics(username, "customer_onboarding_started", {"user_id": user_id})
    
    async def handle_package_selection(self, event, package_type):
        """Paket seçimi işlemi"""
        user_id = event.sender_id
        state = CUSTOMER_ONBOARDING_STATE.get(user_id, {})
        username = state.get("username", f"user_{user_id}")
        
        if package_type == "compare":
            await self.show_package_comparison(event)
            return
        
        package = PACKAGES.get(package_type)
        if not package:
            await event.respond("❌ Geçersiz paket seçimi!")
            return
        
        # Paket detayları göster
        features_text = "\n".join([f"✅ {feature}" for feature in package["features"]])
        
        await event.respond(
            f"📦 **{package['name']}** - {package['price']}₺\n\n"
            f"**Özellikler:**\n{features_text}\n\n"
            f"**Süre:** {package['duration_days']} gün\n\n"
            "Bu paketi seçmek istediğinizden emin misiniz?",
            buttons=[
                [Button.inline("✅ Evet, Devam Et", data=f"confirm_{package_type}")],
                [Button.inline("🔙 Geri Dön", data="back_to_packages")],
                [Button.inline("💳 Ödeme Bilgileri", data="payment_info")]
            ],
            parse_mode="markdown"
        )
        
        # State güncelle
        state.update({
            "step": "package_confirmation",
            "selected_package": package_type,
            "package_details": package
        })
        CUSTOMER_ONBOARDING_STATE[user_id] = state
    
    async def confirm_package_and_start_setup(self, event, package_type):
        """Paket onayı ve kurulum başlatma"""
        user_id = event.sender_id
        state = CUSTOMER_ONBOARDING_STATE.get(user_id, {})
        username = state.get("username", f"user_{user_id}")
        package = PACKAGES.get(package_type)
        
        # Ödeme bilgileri göster
        await event.respond(
            f"💳 **Ödeme Bilgileri**\n\n"
            f"**Paket:** {package['name']}\n"
            f"**Tutar:** {package['price']}₺\n\n"
            f"**Papara:** 1060936740\n"
            f"**IBAN:** TR83 0082 9000 0949 1060 9367 40\n"
            f"**Ad:** ONUR MUTLU\n\n"
            f"**Açıklama:** {username}_{package_type}\n\n"
            "Ödeme yaptıktan sonra 'Ödeme Yaptım' butonuna basın.",
            buttons=[
                [Button.inline("✅ Ödeme Yaptım", data=f"payment_done_{package_type}")],
                [Button.inline("🔙 Geri Dön", data="back_to_packages")]
            ],
            parse_mode="markdown"
        )
        
        # State güncelle
        state.update({
            "step": "payment_waiting",
            "payment_requested_at": time.time()
        })
        CUSTOMER_ONBOARDING_STATE[user_id] = state
        
        # Admin'e bildirim gönder
        admin_message = (
            f"💰 **Yeni Ödeme Bekleniyor**\n\n"
            f"👤 Müşteri: @{username} ({user_id})\n"
            f"📦 Paket: {package['name']}\n"
            f"💵 Tutar: {package['price']}₺\n"
            f"🕐 Zaman: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        try:
            from adminbot.dispatcher import admin_bot
            await admin_bot.send_message(GAVATCORE_ADMIN_ID, admin_message, parse_mode="markdown")
        except:
            pass
    
    async def handle_payment_confirmation(self, event, package_type):
        """Ödeme onayı ve bot kurulum süreci"""
        user_id = event.sender_id
        state = CUSTOMER_ONBOARDING_STATE.get(user_id, {})
        username = state.get("username", f"user_{user_id}")
        package = PACKAGES.get(package_type)
        
        await event.respond(
            "⏳ **Ödemeniz Kontrol Ediliyor...**\n\n"
            "Ödemeniz admin tarafından onaylandıktan sonra bot kurulum sürecine başlayacağız.\n"
            "Bu işlem genellikle 5-10 dakika sürer.\n\n"
            "Şimdi bot hesabınızı kurmaya başlayalım!"
        )
        
        # Bot kurulum sürecini başlat
        await self.start_bot_setup_process(event, package_type)
    
    async def start_bot_setup_process(self, event, package_type):
        """Bot kurulum sürecini başlatır"""
        user_id = event.sender_id
        state = CUSTOMER_ONBOARDING_STATE.get(user_id, {})
        username = state.get("username", f"user_{user_id}")
        package = PACKAGES.get(package_type)
        
        await event.respond(
            "🤖 **Bot Kurulum Süreci**\n\n"
            "Bot hesabınızı kurmak için Telegram hesap bilgilerinize ihtiyacımız var.\n\n"
            "**Adım 1:** Telefon numaranızı girin\n"
            "**Adım 2:** Telegram kodunu girin\n"
            "**Adım 3:** 2FA şifrenizi girin (varsa)\n\n"
            "Telefon numaranızı +90 ile başlayarak girin:",
            buttons=[
                [Button.inline("📱 Telefon Numarası Gir", data="enter_phone")],
                [Button.inline("❓ Güvenlik Hakkında", data="security_info")]
            ]
        )
        
        # State güncelle
        state.update({
            "step": "bot_setup_phone",
            "setup_started_at": time.time()
        })
        CUSTOMER_ONBOARDING_STATE[user_id] = state
    
    async def handle_phone_input(self, event):
        """Telefon numarası girişi"""
        user_id = event.sender_id
        state = CUSTOMER_ONBOARDING_STATE.get(user_id, {})
        
        await event.respond(
            "📱 **Telefon Numarası Girişi**\n\n"
            "Lütfen telefon numaranızı +90 ile başlayarak girin:\n"
            "Örnek: +905551234567\n\n"
            "⚠️ Bu numara bot hesabınız olacak, doğru girdiğinizden emin olun!"
        )
        
        # State güncelle
        state.update({
            "step": "waiting_phone_input"
        })
        CUSTOMER_ONBOARDING_STATE[user_id] = state
    
    async def process_phone_number(self, event, phone):
        """Telefon numarası işleme"""
        user_id = event.sender_id
        state = CUSTOMER_ONBOARDING_STATE.get(user_id, {})
        username = state.get("username", f"user_{user_id}")
        
        # Telefon numarası validasyonu
        if not phone.startswith("+90") or len(phone) != 13:
            await event.respond(
                "❌ **Geçersiz telefon numarası!**\n\n"
                "Lütfen +90 ile başlayan 13 haneli numaranızı girin.\n"
                "Örnek: +905551234567"
            )
            return
        
        try:
            # Session oluşturmaya başla
            await event.respond(
                f"📞 **Kod Gönderiliyor...**\n\n"
                f"Telefon: {phone}\n"
                f"Telegram'a kod gönderiliyor, lütfen bekleyin..."
            )
            
            # Session path oluştur
            session_path = f"sessions/{username}.session"
            
            # Telethon client oluştur
            from telethon import TelegramClient
            client = TelegramClient(session_path, TELEGRAM_API_ID, TELEGRAM_API_HASH)
            
            await client.connect()
            
            # Kod gönder
            await client.send_code_request(phone)
            
            await event.respond(
                "✅ **Kod Gönderildi!**\n\n"
                f"📱 {phone} numarasına Telegram kodu gönderildi.\n"
                "Lütfen aldığınız 5 haneli kodu girin:"
            )
            
            # Pending session kaydet
            self.pending_sessions[user_id] = {
                "phone": phone,
                "client": client,
                "step": "waiting_code"
            }
            
            # State güncelle
            state.update({
                "step": "waiting_telegram_code",
                "phone": phone
            })
            CUSTOMER_ONBOARDING_STATE[user_id] = state
            
        except Exception as e:
            await event.respond(f"❌ Kod gönderim hatası: {str(e)}")
            log_event(username, f"❌ Kod gönderim hatası: {e}")
    
    async def process_telegram_code(self, event, code):
        """Telegram kodu işleme"""
        user_id = event.sender_id
        state = CUSTOMER_ONBOARDING_STATE.get(user_id, {})
        username = state.get("username", f"user_{user_id}")
        
        pending = self.pending_sessions.get(user_id)
        if not pending:
            await event.respond("❌ Session bulunamadı. Lütfen tekrar başlayın.")
            return
        
        try:
            client = pending["client"]
            phone = pending["phone"]
            
            await event.respond("🔐 **Kod Doğrulanıyor...**")
            
            # Kod ile giriş yap
            await client.sign_in(phone, code)
            
            # Başarılı giriş
            me = await client.get_me()
            await client.disconnect()
            
            await event.respond(
                f"✅ **Bot Hesabı Başarıyla Kuruldu!**\n\n"
                f"🤖 Bot: {me.first_name} (@{me.username or 'username_yok'})\n"
                f"📱 Telefon: {phone}\n\n"
                "Bot hesabınız aktif edildi ve sisteme eklendi!"
            )
            
            # Profil oluştur
            await self.create_customer_profile(user_id, username, state, me, phone)
            
            # Cleanup
            self.pending_sessions.pop(user_id, None)
            
        except SessionPasswordNeededError:
            # 2FA gerekli
            await event.respond(
                "🔒 **2FA Şifresi Gerekli**\n\n"
                "Hesabınızda iki faktörlü doğrulama aktif.\n"
                "Lütfen 2FA şifrenizi girin:"
            )
            
            # State güncelle
            pending["step"] = "waiting_2fa"
            state["step"] = "waiting_2fa_password"
            CUSTOMER_ONBOARDING_STATE[user_id] = state
            
        except PhoneCodeInvalidError:
            await event.respond(
                "❌ **Geçersiz Kod!**\n\n"
                "Girdiğiniz kod hatalı. Lütfen tekrar deneyin:"
            )
            
        except Exception as e:
            await event.respond(f"❌ Giriş hatası: {str(e)}")
            log_event(username, f"❌ Telegram giriş hatası: {e}")
    
    async def process_2fa_password(self, event, password):
        """2FA şifresi işleme"""
        user_id = event.sender_id
        state = CUSTOMER_ONBOARDING_STATE.get(user_id, {})
        username = state.get("username", f"user_{user_id}")
        
        pending = self.pending_sessions.get(user_id)
        if not pending:
            await event.respond("❌ Session bulunamadı. Lütfen tekrar başlayın.")
            return
        
        try:
            client = pending["client"]
            phone = pending["phone"]
            
            await event.respond("🔐 **2FA Doğrulanıyor...**")
            
            # 2FA ile giriş
            await client.sign_in(password=password)
            
            # Başarılı giriş
            me = await client.get_me()
            await client.disconnect()
            
            await event.respond(
                f"✅ **Bot Hesabı Başarıyla Kuruldu!**\n\n"
                f"🤖 Bot: {me.first_name} (@{me.username or 'username_yok'})\n"
                f"📱 Telefon: {phone}\n\n"
                "Bot hesabınız aktif edildi ve sisteme eklendi!"
            )
            
            # Profil oluştur
            await self.create_customer_profile(user_id, username, state, me, phone)
            
            # Cleanup
            self.pending_sessions.pop(user_id, None)
            
        except PasswordHashInvalidError:
            await event.respond(
                "❌ **Geçersiz 2FA Şifresi!**\n\n"
                "Girdiğiniz şifre hatalı. Lütfen tekrar deneyin:"
            )
            
        except Exception as e:
            await event.respond(f"❌ 2FA hatası: {str(e)}")
            log_event(username, f"❌ 2FA hatası: {e}")
    
    async def create_customer_profile(self, user_id, username, state, telegram_user, phone):
        """Müşteri profili oluştur"""
        package_type = state.get("selected_package")
        package = PACKAGES.get(package_type)
        
        # Bot profili oluştur
        bot_username = telegram_user.username or f"bot_{user_id}"
        
        # Persona dosyası oluştur - Paket özelliklerine göre
        persona_data = {
            "username": bot_username,
            "telegram_handle": f"@{bot_username}",
            "display_name": telegram_user.first_name,
            "type": "customer_bot",
            "owner_id": str(user_id),
            "phone": phone,
            "user_id": telegram_user.id,
            "created_at": datetime.now().isoformat(),
            "customer_status": "active",
            "customer_info": {
                "customer_username": username,
                "customer_user_id": user_id,
                "package_type": package_type,
                "package_name": package["name"],
                "package_price": package["price"],
                "bot_limits": package["bot_limits"],
                "support_level": package["support_level"],
                "activated_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=package["duration_days"])).isoformat()
            },
            # Paket bazlı özellikler
            "reply_mode": package["reply_mode"],
            "gpt_enhanced": package["gpt_enabled"],
            "gpt_mode": "gpt_only" if package["reply_mode"] == "gpt_enhanced" else "hybrid" if package["gpt_enabled"] else "off",
            "auto_menu_enabled": True,
            "auto_menu_threshold": 3,
            "vip_price": "250" if package_type == "basic" else "300" if package_type == "premium" else "500",
            "autospam": False,  # Başlangıçta kapalı, müşteri açacak
            "bot_config": {
                "dm_invite_enabled": True,
                "dm_invite_chance": package["dm_invite_chance"],
                "spam_protection_enabled": True,
                "spam_protection_type": "basic" if package_type == "basic" else "advanced",
                "max_messages_per_minute": 2 if package_type == "basic" else 4 if package_type == "premium" else 6,
                "reply_mode": package["reply_mode"],
                "auto_menu_enabled": True,
                "auto_menu_threshold": 3,
                "vip_price": "250" if package_type == "basic" else "300" if package_type == "premium" else "500",
                "group_invite_aggressive": package["group_invite_type"] in ["aggressive", "very_aggressive"],
                "group_invite_frequency": package["group_invite_type"],
                "analytics_enabled": package_type in ["premium", "enterprise"],
                "custom_funnel_enabled": package_type == "enterprise"
            }
        }
        
        # Persona dosyasını kaydet
        save_profile(bot_username, persona_data)
        
        # Müşteri dashboard'unu göster
        await self.show_customer_dashboard_after_setup(user_id, username, package, bot_username)
        
        # Cleanup
        CUSTOMER_ONBOARDING_STATE.pop(user_id, None)
        
        log_analytics(username, "customer_onboarding_completed", {
            "package": package_type,
            "bot_username": bot_username,
            "phone": phone
        })
    
    async def show_customer_dashboard_after_setup(self, user_id, username, package, bot_username):
        """Kurulum sonrası müşteri dashboard'u"""
        try:
            from adminbot.dispatcher import admin_bot
            
            dashboard_text = (
                f"🎉 **Kurulum Tamamlandı!**\n\n"
                f"**Paketiniz:** {package['name']}\n"
                f"**Bot Username:** @{bot_username}\n"
                f"**Süre:** {package['duration_days']} gün\n\n"
                f"**Aktif Özellikler:**\n"
            )
            
            for feature in package["features"]:
                dashboard_text += f"✅ {feature}\n"
            
            dashboard_text += (
                f"\n**Yönetim Komutları:**\n"
                f"• /dashboard - Kontrol paneli\n"
                f"• /bot_durum - Bot durumu\n"
                f"• /istatistik - Performans raporu\n"
                f"• /destek - Teknik destek\n\n"
                f"Bot hesabınız şimdi aktif ve çalışıyor! 🚀"
            )
            
            await admin_bot.send_message(
                user_id,
                dashboard_text,
                buttons=[
                    [Button.inline("📊 Dashboard", data="customer_dashboard")],
                    [Button.inline("🤖 Bot Durumu", data="bot_status")],
                    [Button.inline("📞 Destek", data="customer_support")]
                ],
                parse_mode="markdown"
            )
            
        except Exception as e:
            log_event(username, f"❌ Dashboard gösterim hatası: {e}")
    
    async def show_package_comparison(self, event):
        """Paket karşılaştırması göster"""
        comparison_text = "📊 **Paket Karşılaştırması**\n\n"
        
        for pkg_key, pkg_data in PACKAGES.items():
            comparison_text += f"**{pkg_data['name']} - {pkg_data['price']}₺**\n"
            for feature in pkg_data['features']:
                comparison_text += f"  ✅ {feature}\n"
            comparison_text += f"  📅 Süre: {pkg_data['duration_days']} gün\n\n"
        
        await event.respond(
            comparison_text,
            buttons=[
                [Button.inline("💎 Temel Seç", data="pkg_basic")],
                [Button.inline("🔥 Premium Seç", data="pkg_premium")],
                [Button.inline("👑 Kurumsal Seç", data="pkg_enterprise")]
            ],
            parse_mode="markdown"
        )
    
    async def show_customer_dashboard(self, event, profile):
        """Mevcut müşteri dashboard'u"""
        customer_info = profile.get("customer_info", {})
        
        dashboard_text = (
            f"👤 **Müşteri Dashboard**\n\n"
            f"**Paket:** {customer_info.get('package_name', 'Bilinmiyor')}\n"
            f"**Bot:** @{profile.get('username', 'Bilinmiyor')}\n"
            f"**Durum:** {'🟢 Aktif' if profile.get('customer_status') == 'active' else '🔴 Pasif'}\n"
            f"**Bitiş:** {customer_info.get('expires_at', 'Bilinmiyor')[:10]}\n\n"
        )
        
        await event.respond(
            dashboard_text,
            buttons=[
                [Button.inline("📊 İstatistikler", data="customer_stats")],
                [Button.inline("🤖 Bot Ayarları", data="bot_settings")],
                [Button.inline("💰 Paket Yenile", data="renew_package")],
                [Button.inline("📞 Destek", data="customer_support")]
            ],
            parse_mode="markdown"
        )

# Global instance
customer_onboarding = CustomerOnboardingHandler() 