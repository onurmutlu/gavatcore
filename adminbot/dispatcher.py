# ===============================================================
#   adminbot/dispatcher.py  ✦  GAVATCORE ADMIN BOT DISPATCHER
# ---------------------------------------------------------------
#   Yazar:    ChatGPT-4o (revize: Onur, 2025-05-24)
#   Amaç:     Tüm admin bot komutlarının, onboarding akışının,
#             callback/inline işlemlerinin ve user/session
#             command'larının asenkron yönetimi. Botun giriş
#             noktasıdır.
#   Açıklama: 
#      - Admin ve kullanıcı komutlarını yakalar, doğru handler'a yönlendirir.
#      - Onboarding ve session işlemlerini destekler.
#      - Hataları ve edge-case'leri minimuma indirir.
#      - Hem terminal hem log dosyası için önemli olayları basar.
#   Revizyon: Maksimal, bulletproof — exception handling, input
#             validation, missing env guard, log integration.
#   Son güncelleme: 2025-05-24
# ===============================================================

import os
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events
from adminbot.commands import handle_admin_command
from core.onboarding_flow import (
    start_onboarding,
    handle_onboarding_callback,
    handle_onboarding_text
)
from handlers.dm_handler import handle_inline_bank_choice
from handlers.user_commands import handle_user_command
from handlers.session_handler import handle_session_command
from handlers.inline_handler import inline_handler
from handlers.customer_onboarding import customer_onboarding, CUSTOMER_ONBOARDING_STATE

# -------- CUSTOMER ONBOARDING TEXT HANDLER --------
async def handle_customer_onboarding_text(event, customer_state):
    """Müşteri onboarding text mesajlarını işler"""
    user_id = event.sender_id
    step = customer_state.get("step")
    text = event.raw_text.strip()
    
    try:
        if step == "waiting_phone_input":
            await customer_onboarding.process_phone_number(event, text)
        elif step == "waiting_telegram_code":
            await customer_onboarding.process_telegram_code(event, text)
        elif step == "waiting_2fa_password":
            await customer_onboarding.process_2fa_password(event, text)
        else:
            await event.respond("❓ Beklenmeyen mesaj. Lütfen butonları kullanın.")
    except Exception as e:
        logger.error(f"Customer onboarding text handler hatası: {e}")
        await event.respond("❌ İşlem sırasında hata oluştu. Lütfen tekrar deneyin.")

# -------- LOGGING & ENV GUARD --------
logger = logging.getLogger("gavatcore.adminbot.dispatcher")

def get_env_var(name, required=True, default=None):
    val = os.getenv(name, default)
    if required and not val:
        logger.critical(f"❌ ENV ERROR: {name} bulunamadı! Admin bot başlatılamaz.")
        raise SystemExit(f"Çıkılıyor: {name} ayarı eksik!")
    return val

# Global admin_bot değişkeni
admin_bot = None

def setup_admin_bot():
    """AdminBot'u başlatır ve event handler'ları ekler"""
    global admin_bot
    
    # .env'i yükle
    load_dotenv()
    
    try:
        API_ID = int(get_env_var("TELEGRAM_API_ID"))
        API_HASH = get_env_var("TELEGRAM_API_HASH")
        ADMIN_BOT_TOKEN = get_env_var("ADMIN_BOT_TOKEN")
    except Exception as e:
        logger.critical(f"AdminBot başlatılamadı: {e}")
        raise

    # -------- TELEGRAM CLIENT INIT --------
    try:
        # Farklı session dosyası adı kullan
        session_name = 'adminbot_main'
        admin_bot = TelegramClient(session_name, API_ID, API_HASH)
        logger.info(f"AdminBot TelegramClient oluşturuldu: {session_name}.session")
    except Exception as e:
        logger.critical(f"Admin bot oluşturulurken hata: {e}")
        raise

    # -------- ADMIN COMMAND HANDLER --------
    @admin_bot.on(events.NewMessage(pattern=r"^/"))
    async def admin_command_handler(event):
        try:
            if event.is_private:
                await handle_admin_command(admin_bot, event)
        except Exception as e:
            logger.error(f"Admin komutunda hata: {e}")
            await event.respond("⚠️ Admin komutu çalıştırılırken hata oluştu.")

    # -------- USER/SERVICE COMMAND HANDLER --------
    @admin_bot.on(events.NewMessage(incoming=True))
    async def universal_private_handler(event):
        try:
            if event.is_private:
                # State kontrolü - VIP mesajı veya Papara bilgisi bekleniyor mu?
                from utils.state_utils import get_state, clear_state
                from core.profile_loader import update_profile
                from utils.log_utils import log_event
                
                sender = await event.get_sender()
                user_id = sender.id
                
                # VIP mesajı bekleniyor mu?
                awaiting_vip = await get_state(user_id, "awaiting_vip_message")
                if awaiting_vip:
                    try:
                        username = awaiting_vip
                        vip_message = event.raw_text.strip()
                        update_profile(username, {"vip_message": vip_message})
                        await event.respond(f"✅ **{username}** için VIP mesajı güncellendi:\n\n{vip_message}")
                        await clear_state(user_id, "awaiting_vip_message")
                        log_event(user_id, f"VIP mesaj güncellendi: {username}")
                        return
                    except Exception as e:
                        await event.respond(f"❌ VIP mesajı kaydedilemedi: {e}")
                        await clear_state(user_id, "awaiting_vip_message")
                        return
                
                # Papara bilgisi bekleniyor mu?
                awaiting_papara = await get_state(user_id, "awaiting_papara_info")
                if awaiting_papara:
                    try:
                        username = awaiting_papara
                        papara_text = event.raw_text.strip()
                        
                        # Format: IBAN | Ad Soyad | Papara ID
                        if "|" in papara_text:
                            parts = [x.strip() for x in papara_text.split("|")]
                            if len(parts) >= 3:
                                iban, name, papara_id = parts[0], parts[1], parts[2]
                                update_profile(username, {
                                    "papara_iban": iban,
                                    "papara_name": name,
                                    "papara_note": papara_id
                                })
                                await event.respond(f"✅ **{username}** Papara bilgisi güncellendi:\n\n💳 {iban}\n👤 {name}\n📝 ID: {papara_id}")
                                await clear_state(user_id, "awaiting_papara_info")
                                log_event(user_id, f"Papara bilgisi güncellendi: {username}")
                                return
                        
                        await event.respond("❌ Format hatası. Şöyle yaz:\n`IBAN | Ad Soyad | Papara ID`")
                        return
                        
                    except Exception as e:
                        await event.respond(f"❌ Papara bilgisi kaydedilemedi: {e}")
                        await clear_state(user_id, "awaiting_papara_info")
                        return
                
                # Müşteri onboarding state kontrolü
                customer_state = CUSTOMER_ONBOARDING_STATE.get(user_id)
                if customer_state:
                    await handle_customer_onboarding_text(event, customer_state)
                    return
                
                # Normal komut işleme
                text = event.raw_text.strip().lower()
                if text.startswith("/"):
                    await handle_user_command(event)
                    await handle_session_command(event)
                    return
                await handle_onboarding_text(event)
        except Exception as e:
            logger.error(f"User/session komutunda hata: {e}")
            await event.respond("⚠️ Komut işlenirken hata oluştu.")

    # -------- INLINE CALLBACK HANDLER --------
    @admin_bot.on(events.CallbackQuery)
    async def callback_query_handler(event):
        try:
            await inline_handler(event)
        except Exception as e:
            logger.error(f"CallbackQuery handler'da hata: {e}")
            await event.answer("⚠️ Inline callback işlenirken hata oluştu.", alert=True)

    # -------- ONBOARDING ENTRY --------
    @admin_bot.on(events.NewMessage(pattern=r"^/basla$"))
    async def onboarding_entry(event):
        try:
            if event.is_private:
                await start_onboarding(admin_bot, event)
        except Exception as e:
            logger.error(f"Onboarding başlatılırken hata: {e}")
            await event.respond("⚠️ Onboarding başlatılamadı.")

# -------- BOT STARTER --------
def start_dispatcher():
    try:
        # AdminBot'u kur
        setup_admin_bot()
        
        print("🤖 AdminBot aktif! Tüm komutlar ve onboarding başlatıldı.")
        logger.info("AdminBot dispatcher başlatıldı.")
        admin_bot.run_until_disconnected()
    except Exception as e:
        logger.critical(f"Admin bot başlatılamadı: {e}")
        raise

async def start_dispatcher_async():
    """Async version for single process operation"""
    global admin_bot
    
    # .env'i yükle
    load_dotenv()
    
    try:
        API_ID = int(get_env_var("TELEGRAM_API_ID"))
        API_HASH = get_env_var("TELEGRAM_API_HASH")
        ADMIN_BOT_TOKEN = get_env_var("ADMIN_BOT_TOKEN")
    except Exception as e:
        logger.critical(f"AdminBot başlatılamadı: {e}")
        raise

    # -------- TELEGRAM CLIENT INIT --------
    try:
        # Farklı session dosyası adı kullan
        session_name = 'adminbot_main'
        admin_bot = TelegramClient(session_name, API_ID, API_HASH)
        await admin_bot.start(bot_token=ADMIN_BOT_TOKEN)
        logger.info(f"AdminBot TelegramClient başlatıldı: {session_name}.session")
    except Exception as e:
        logger.critical(f"Admin bot başlatılırken hata: {e}")
        raise

    # Event handler'ları ekle (setup_admin_bot'taki aynı handler'lar)
    @admin_bot.on(events.NewMessage(pattern=r"^/"))
    async def admin_command_handler(event):
        try:
            if event.is_private:
                await handle_admin_command(admin_bot, event)
        except Exception as e:
            logger.error(f"Admin komutunda hata: {e}")
            await event.respond("⚠️ Admin komutu çalıştırılırken hata oluştu.")

    @admin_bot.on(events.NewMessage(incoming=True))
    async def universal_private_handler(event):
        try:
            if event.is_private:
                # State kontrolü - VIP mesajı veya Papara bilgisi bekleniyor mu?
                from utils.state_utils import get_state, clear_state
                from core.profile_loader import update_profile
                from utils.log_utils import log_event
                
                sender = await event.get_sender()
                user_id = sender.id
                
                # VIP mesajı bekleniyor mu?
                awaiting_vip = await get_state(user_id, "awaiting_vip_message")
                if awaiting_vip:
                    try:
                        username = awaiting_vip
                        vip_message = event.raw_text.strip()
                        update_profile(username, {"vip_message": vip_message})
                        await event.respond(f"✅ **{username}** için VIP mesajı güncellendi:\n\n{vip_message}")
                        await clear_state(user_id, "awaiting_vip_message")
                        log_event(user_id, f"VIP mesaj güncellendi: {username}")
                        return
                    except Exception as e:
                        await event.respond(f"❌ VIP mesajı kaydedilemedi: {e}")
                        await clear_state(user_id, "awaiting_vip_message")
                        return
                
                # Papara bilgisi bekleniyor mu?
                awaiting_papara = await get_state(user_id, "awaiting_papara_info")
                if awaiting_papara:
                    try:
                        username = awaiting_papara
                        papara_text = event.raw_text.strip()
                        
                        # Format: IBAN | Ad Soyad | Papara ID
                        if "|" in papara_text:
                            parts = [x.strip() for x in papara_text.split("|")]
                            if len(parts) >= 3:
                                iban, name, papara_id = parts[0], parts[1], parts[2]
                                update_profile(username, {
                                    "papara_iban": iban,
                                    "papara_name": name,
                                    "papara_note": papara_id
                                })
                                await event.respond(f"✅ **{username}** Papara bilgisi güncellendi:\n\n💳 {iban}\n👤 {name}\n📝 ID: {papara_id}")
                                await clear_state(user_id, "awaiting_papara_info")
                                log_event(user_id, f"Papara bilgisi güncellendi: {username}")
                                return
                        
                        await event.respond("❌ Format hatası. Şöyle yaz:\n`IBAN | Ad Soyad | Papara ID`")
                        return
                        
                    except Exception as e:
                        await event.respond(f"❌ Papara bilgisi kaydedilemedi: {e}")
                        await clear_state(user_id, "awaiting_papara_info")
                        return
                
                # Müşteri onboarding state kontrolü
                customer_state = CUSTOMER_ONBOARDING_STATE.get(user_id)
                if customer_state:
                    await handle_customer_onboarding_text(event, customer_state)
                    return
                
                # Normal komut işleme
                text = event.raw_text.strip().lower()
                if text.startswith("/"):
                    await handle_user_command(event)
                    await handle_session_command(event)
                    return
                await handle_onboarding_text(event)
        except Exception as e:
            logger.error(f"User/session komutunda hata: {e}")
            await event.respond("⚠️ Komut işlenirken hata oluştu.")

    @admin_bot.on(events.CallbackQuery)
    async def callback_query_handler(event):
        try:
            await inline_handler(event)
        except Exception as e:
            logger.error(f"CallbackQuery handler'da hata: {e}")
            await event.answer("⚠️ Inline callback işlenirken hata oluştu.", alert=True)

    @admin_bot.on(events.NewMessage(pattern=r"^/basla$"))
    async def onboarding_entry(event):
        try:
            if event.is_private:
                await start_onboarding(admin_bot, event)
        except Exception as e:
            logger.error(f"Onboarding başlatılırken hata: {e}")
            await event.respond("⚠️ Onboarding başlatılamadı.")
    
    print("🤖 AdminBot aktif! Tüm komutlar ve onboarding başlatıldı.")
    logger.info("AdminBot dispatcher başlatıldı.")
    
    try:
        await admin_bot.run_until_disconnected()
    except Exception as e:
        logger.critical(f"Admin bot çalışırken hata: {e}")
        raise

