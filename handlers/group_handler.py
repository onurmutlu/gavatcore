# handlers/group_handler.py
import asyncio
import time
from telethon import events
from core.license_checker import LicenseChecker
from core.profile_loader import load_profile
from gpt.flirt_agent import generate_reply
from utils.template_utils import get_profile_reply_message
from utils.log_utils import log_event
from core.analytics_logger import log_analytics
from utils.smart_reply import smart_reply
from core.crm_database import crm_db

MANUALPLUS_TIMEOUT = 180  # saniye

# Dinamik spam scheduler entegrasyonu
try:
    from utils.dynamic_spam_scheduler import dynamic_scheduler
    DYNAMIC_SPAM_ENABLED = True
except ImportError:
    DYNAMIC_SPAM_ENABLED = False

# Global manualplus pending dictionary - hem DM hem grup için
manualplus_pending = {}

# Grup trafik takibi için
group_message_counts = {}  # {group_id: [timestamp1, timestamp2, ...]}
TRAFFIC_WINDOW = 300  # 5 dakika pencere

# ===== YENİ: COOLDOWN VE DUPLICATE PREVENTION SİSTEMİ =====
# Reply cooldown sistemi - agresif davranışı önlemek için
reply_cooldowns = {}  # {f"{bot_username}:{group_id}:{user_id}": last_reply_time}
group_reply_cooldowns = {}  # {f"{bot_username}:{group_id}": last_reply_time}
processed_messages = set()  # İşlenmiş mesaj ID'leri - duplicate prevention

# Cooldown süreleri (saniye)
USER_REPLY_COOLDOWN = 60  # Aynı kullanıcıya 1 dakika cooldown
GROUP_REPLY_COOLDOWN = 30  # Aynı grupta 30 saniye cooldown
CONVERSATION_COOLDOWN = 120  # Conversation response için 2 dakika cooldown

def _load_bot_profile(client_username, bot_user_id):
    """Bot profilini session dosya adından yükler."""
    try:
        # Session dosya adından bot profilini bul
        import os
        session_files = [f for f in os.listdir("sessions") if f.endswith(".session")]
        for session_file in session_files:
            session_name = session_file.replace(".session", "")
            try:
                profile = load_profile(session_name)
                if profile.get("user_id") == bot_user_id or profile.get("username") == client_username:
                    return profile
            except:
                continue
    except:
        pass
    return {}

def safe_load_profile(username, user_id):
    # Önce user_id, sonra username ile dene (int ve string olarak)
    try:
        return load_profile(str(user_id))
    except:
        try:
            return load_profile(username)
        except:
            return {}

def calculate_dynamic_timeout(group_id, base_timeout=180):
    """
    Grup trafiğine göre dinamik timeout hesaplar.
    Yoğun gruplarda daha kısa timeout.
    """
    current_time = time.time()
    
    # Grup mesaj sayısını güncelle
    if group_id not in group_message_counts:
        group_message_counts[group_id] = []
    
    # Eski mesajları temizle (5 dakikadan eski)
    group_message_counts[group_id] = [
        timestamp for timestamp in group_message_counts[group_id]
        if current_time - timestamp < TRAFFIC_WINDOW
    ]
    
    # Yeni mesajı ekle
    group_message_counts[group_id].append(current_time)
    
    msg_count = len(group_message_counts[group_id])
    
    # Dinamik timeout hesapla
    if msg_count > 50:  # Çok yoğun grup
        return max(30, base_timeout // 4), msg_count
    elif msg_count > 20:  # Yoğun grup
        return max(60, base_timeout // 2), msg_count
    elif msg_count > 10:  # Orta yoğun grup
        return max(90, base_timeout * 3 // 4), msg_count
    else:  # Sakin grup
        return base_timeout, msg_count

def _check_reply_cooldown(bot_username: str, group_id: int, user_id: int) -> tuple[bool, str]:
    """
    Reply cooldown kontrolü yapar
    Returns: (can_reply: bool, reason: str)
    """
    current_time = time.time()
    
    # Kullanıcı bazlı cooldown kontrolü
    user_key = f"{bot_username}:{group_id}:{user_id}"
    if user_key in reply_cooldowns:
        time_since_last = current_time - reply_cooldowns[user_key]
        if time_since_last < USER_REPLY_COOLDOWN:
            remaining = USER_REPLY_COOLDOWN - time_since_last
            return False, f"Kullanıcı cooldown: {remaining:.0f}s kaldı"
    
    # Grup bazlı cooldown kontrolü
    group_key = f"{bot_username}:{group_id}"
    if group_key in group_reply_cooldowns:
        time_since_last = current_time - group_reply_cooldowns[group_key]
        if time_since_last < GROUP_REPLY_COOLDOWN:
            remaining = GROUP_REPLY_COOLDOWN - time_since_last
            return False, f"Grup cooldown: {remaining:.0f}s kaldı"
    
    return True, "OK"

def _update_reply_cooldown(bot_username: str, group_id: int, user_id: int):
    """Reply cooldown'ları günceller"""
    current_time = time.time()
    user_key = f"{bot_username}:{group_id}:{user_id}"
    group_key = f"{bot_username}:{group_id}"
    
    reply_cooldowns[user_key] = current_time
    group_reply_cooldowns[group_key] = current_time

def _is_conversation_response_smart(client, event, bot_user_id, username) -> bool:
    """
    Daha akıllı conversation response detection
    Sadece gerçekten bot ile konuşma devam ediyorsa True döner
    """
    try:
        # Conversation cooldown kontrolü
        conv_key = f"{username}:{event.chat_id}:conversation"
        current_time = time.time()
        
        if conv_key in reply_cooldowns:
            time_since_last = current_time - reply_cooldowns[conv_key]
            if time_since_last < CONVERSATION_COOLDOWN:
                return False
        
        # Son 5 mesajı kontrol et (daha dar aralık)
        recent_messages = []
        bot_message_found = False
        user_message_count = 0
        
        async def check_recent_messages():
            nonlocal bot_message_found, user_message_count
            async for message in client.iter_messages(event.chat_id, limit=5):
                if message.id >= event.id:  # Kendi mesajımızdan sonraki mesajları atla
                    continue
                
                recent_messages.append(message)
                
                # Bot'un mesajını bul
                if message.sender_id == bot_user_id:
                    bot_message_found = True
                    break
                elif message.sender_id == event.sender_id:
                    user_message_count += 1
        
        # Async function'ı çalıştır
        try:
            import asyncio
            # Event loop kontrolü
            try:
                loop = asyncio.get_running_loop()
                # Zaten çalışan loop varsa, task olarak çalıştır
                task = asyncio.create_task(check_recent_messages())
                # Task'i beklemek için geçici çözüm - bu fonksiyon sync olduğu için
                # conversation detection'ı basitleştir
                return False  # Geçici olarak False döndür
            except RuntimeError:
                # Çalışan loop yok, normal şekilde çalıştır
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(check_recent_messages())
        except Exception as e:
            log_event(username, f"❌ Event loop hatası: {e}")
            return False
        
        # Conversation response kriterleri:
        # 1. Bot'un son 5 mesaj içinde mesajı var
        # 2. Kullanıcının bot'tan sonra 2'den fazla mesajı yok (spam değil)
        # 3. Mesaj bot'a yönelik görünüyor (kısa, soru, vs.)
        if bot_message_found and user_message_count <= 2:
            # Mesaj içeriği analizi
            text = event.raw_text.lower().strip()
            
            # Conversation indicators
            conversation_indicators = [
                len(text) < 50,  # Kısa mesaj
                any(word in text for word in ['ne', 'nasıl', 'neden', 'kim', 'nerede', 'ne zaman']),  # Soru kelimeleri
                any(word in text for word in ['evet', 'hayır', 'tamam', 'ok', 'peki', 'iyi']),  # Onay kelimeleri
                any(word in text for word in ['merhaba', 'selam', 'hey', 'hi']),  # Selamlama
                text.endswith('?'),  # Soru işareti
                len(text.split()) <= 5  # 5 kelimeden az
            ]
            
            # En az 2 kriter karşılanmalı
            if sum(conversation_indicators) >= 2:
                # Conversation cooldown'ı güncelle
                reply_cooldowns[conv_key] = current_time
                return True
        
        return False
        
    except Exception as e:
        log_event(username, f"❌ Smart conversation detection hatası: {e}")
        return False

async def handle_group_message(event, client):
    if not event.is_group:
        return

    # Gelişmiş duplicate message prevention
    message_key = f"{event.chat_id}:{event.id}:{event.sender_id}:{hash(event.raw_text)}"
    if message_key in processed_messages:
        log_event("duplicate_filter", f"🔄 Çift mesaj engellendi: {event.chat_id}:{event.id}")
        return
    processed_messages.add(message_key)
    
    # Processed messages cache'ini temizle (memory leak prevention)
    if len(processed_messages) > 500:  # Daha küçük cache
        # En eski %50'sini temizle
        old_messages = list(processed_messages)[:250]
        for old_msg in old_messages:
            processed_messages.discard(old_msg)

    try:
        # Önce cache'den dene, yoksa API'den çek
        sender = event.sender
        if sender is None:
            try:
                sender = await event.get_sender()
            except Exception as e:
                log_event("unknown_bot", f"❌ Sender API'den alınamadı: {e}")
                return
        if sender is None:
            return
        user_id = sender.id
        
        # Bot kontrolü - Eğer gönderen bir bot ise mesajı işleme
        if hasattr(sender, 'bot') and sender.bot:
            log_event("bot_filter", f"🤖 Grup bot mesajı engellendi: {sender.username or sender.first_name} ({user_id}) - '{event.raw_text}'")
            return
        
        # Telegram'ın resmi bot'larını da engelle (user_id'ye göre)
        telegram_official_bots = [
            178220800,  # @SpamBot
            93372553,   # @BotFather  
            136817688,  # @StickerBot
            429000,     # @Telegram
            777000,     # Telegram Service Messages
            1087968824  # @GroupAnonymousBot
        ]
        
        if user_id in telegram_official_bots:
            log_event("bot_filter", f"🚫 Grup Telegram resmi bot'u engellendi: {sender.username or sender.first_name} ({user_id}) - '{event.raw_text}'")
            return
            
    except Exception as e:
        log_event("unknown_bot", f"❌ Sender alınamadı: {e}")
        return
    
    # Bot username'ini al
    try:
        me = await client.get_me()
        username = me.username or f"bot_{me.id}"
        bot_user_id = me.id
    except:
        username = "unknown_bot"
        bot_user_id = 0

    # Cooldown kontrolü - erken exit
    can_reply, cooldown_reason = _check_reply_cooldown(username, event.chat_id, user_id)
    if not can_reply:
        log_event(username, f"🕒 Reply cooldown aktif: {cooldown_reason}")
        return

    # Geliştirilmiş reply/mention/conversation kontrolü
    is_reply_to_bot = False
    is_mentioned = False
    is_conversation_response = False
    
    # Reply kontrolü - sadece bot'a reply ise
    if event.is_reply:
        try:
            replied_msg = await event.get_reply_message()
            if replied_msg and replied_msg.sender_id == bot_user_id:
                is_reply_to_bot = True
                log_event(username, f"✅ Bot'a reply tespit edildi: {event.raw_text}")
        except Exception as e:
            log_event(username, f"❌ Reply mesajı alınamadı: {e}")
    
    # Mention kontrolü - bot username'i geçiyor mu
    if f"@{username}".lower() in event.raw_text.lower():
        is_mentioned = True
        log_event(username, f"✅ Bot mention tespit edildi: {event.raw_text}")
    
    # Akıllı conversation response kontrolü - GEÇİCİ OLARAK DEVRE DIŞI (flood wait sorunu)
    is_conversation_response = False
    # if not (is_reply_to_bot or is_mentioned):
    #     is_conversation_response = _is_conversation_response_smart(client, event, bot_user_id, username)
    #     if is_conversation_response:
    #         log_event(username, f"💬 Akıllı conversation response tespit edildi: {event.raw_text}")
    
    # Bot'a reply, mention veya conversation response varsa devam et
    if not (is_reply_to_bot or is_mentioned or is_conversation_response):
        return

    # CRM: Kullanıcı ve grup profillerini güncelle
    await _update_crm_profiles(event, username, user_id, bot_user_id)

    # Bot profilini yükle
    bot_profile = _load_bot_profile(username, bot_user_id)

    license_checker = LicenseChecker()
    # Bot profilinden created_at bilgisini al
    try:
        created_at_str = bot_profile.get("created_at")
        if created_at_str:
            from datetime import datetime
            session_created_at = datetime.fromisoformat(created_at_str)
        else:
            from datetime import datetime
            session_created_at = datetime.now()
    except Exception:
        from datetime import datetime
        session_created_at = datetime.now()

    if not license_checker.is_license_valid(user_id, session_created_at, bot_profile):
        log_analytics(username, "group_blocked_demo_timeout", {
            "user_id": user_id,
            "group_id": event.chat_id
        })
        return

    # Bot profilinden ayarları al (kullanıcı profili değil!)
    reply_mode = bot_profile.get("reply_mode") or "manualplus"  # ultimate safe
    manualplus_timeout = int(bot_profile.get("manualplus_timeout_sec", MANUALPLUS_TIMEOUT))

    log_event(username, f"📥 Grup mesajı alındı: {event.raw_text} | Yanıt modu: {reply_mode}")
    log_analytics(username, "group_message_received", {
        "from_user_id": user_id,
        "group_id": event.chat_id,
        "text": event.raw_text,
        "reply_mode": reply_mode,
        "bot_profile": username
    })

    # Cooldown'ı güncelle (yanıt vereceğimiz için)
    _update_reply_cooldown(username, event.chat_id, user_id)
    
    # Dinamik spam scheduler için grup aktivitesini güncelle
    if DYNAMIC_SPAM_ENABLED:
        dynamic_scheduler.update_group_activity(event.chat_id, 1)

    # ======== REPLY MODES ========
    if reply_mode == "gpt":
        try:
            response = await generate_reply(agent_name=username, user_message=event.raw_text)
            await event.reply(response)
            log_event(username, f"🤖 GPT yanıtı gönderildi: {response}")
            log_analytics(username, "group_gpt_reply_sent", {
                "response": response,
                "group_id": event.chat_id
            })
        except Exception as e:
            error_str = str(e).lower()
            if "chatwriteforbidden" in error_str or "forbidden" in error_str:
                log_event(username, f"⚠️ GPT yanıtı - Gruba yazma izni yok: {event.chat_id}")
            else:
                log_event(username, f"❌ GPT hatası: {str(e)}")
                log_analytics(username, "group_gpt_reply_failed", {
                    "error": str(e),
                    "group_id": event.chat_id
                })

    elif reply_mode == "manual":
        log_event(username, "✋ manual mod: kullanıcı yanıtlaması bekleniyor.")
        log_analytics(username, "group_manual_no_reply", {
            "group_id": event.chat_id
        })

    elif reply_mode == "hybrid":
        try:
            # Yeni hybrid mode: GPT ağırlıklı doğal yanıt
            response = await smart_reply.get_hybrid_reply(event.raw_text, bot_profile, username)
            await event.reply(response)
            log_event(username, f"🎭 HYBRID grup yanıtı: {response}")
            log_analytics(username, "group_hybrid_reply_sent", {
                "response": response,
                "group_id": event.chat_id
            })
        except Exception as e:
            error_str = str(e).lower()
            if "chatwriteforbidden" in error_str or "forbidden" in error_str:
                log_event(username, f"⚠️ Hybrid öneri - Gruba yazma izni yok: {event.chat_id}")
            else:
                log_event(username, f"❌ Hybrid GPT hatası: {str(e)}")
                log_analytics(username, "group_hybrid_suggestion_failed", {
                    "error": str(e),
                    "group_id": event.chat_id
                })

    elif reply_mode == "manualplus":
        # Dinamik timeout hesapla
        dynamic_timeout, msg_count = calculate_dynamic_timeout(event.chat_id, manualplus_timeout)
        
        # HER grubun kendi unique key'i olsun - improved uniqueness
        key = f"group:{username}:{event.chat_id}:{event.id}:{user_id}"
        manualplus_pending[key] = True
        
        log_event(username, f"📊 Grup trafik analizi: {msg_count} mesaj/5dk → timeout: {dynamic_timeout}s")

        async def check_manualplus_timeout():
            await asyncio.sleep(dynamic_timeout)
            if manualplus_pending.get(key):
                try:
                    # Grup yazma izni kontrolü
                    try:
                        chat = await client.get_entity(event.chat_id)
                        me = await client.get_me()
                        
                        # Admin kontrolü veya yazma izni kontrolü
                        if hasattr(chat, 'admin_rights') and chat.admin_rights:
                            can_write = True
                        else:
                            # Basit mesaj gönderme testi (sessiz)
                            can_write = True  # Varsayılan olarak izin var kabul et
                    except:
                        can_write = False
                    
                    if not can_write:
                        log_event(username, f"⚠️ Gruba yazma izni yok: {event.chat_id}")
                        manualplus_pending.pop(key, None)
                        return
                    
                    # Hybrid mode varsa onu kullan, yoksa normal smart reply
                    if bot_profile.get("reply_mode") == "hybrid":
                        smart_response = await smart_reply.get_hybrid_reply(event.raw_text, bot_profile, username)
                    else:
                        smart_response = await smart_reply.get_smart_reply(event.raw_text, bot_profile, username)
                    await event.reply(smart_response)
                    log_event(username, f"⏱️ manualplus: süre doldu, akıllı yanıt verildi → {smart_response}")
                    log_analytics(username, "group_manualplus_smart_fallback_sent", {
                        "smart_response": smart_response,
                        "group_id": event.chat_id
                    })
                except Exception as e:
                    error_str = str(e).lower()
                    if "chatwriteforbidden" in error_str or "forbidden" in error_str:
                        log_event(username, f"⚠️ Gruba yazma izni yok: {event.chat_id} - {e}")
                    else:
                        log_event(username, f"❌ manualplus akıllı fallback hatası: {str(e)}")
                        # Sadece yazma izni yoksa sessiz geç, diğer hatalar için log
                        log_analytics(username, "group_manualplus_smart_fallback_failed", {
                            "error": str(e),
                            "group_id": event.chat_id
                        })
            manualplus_pending.pop(key, None)

        asyncio.create_task(check_manualplus_timeout())
        log_event(username, f"🕒 manualplus mod: {dynamic_timeout}s kullanıcı yanıtı bekleniyor...")
        log_analytics(username, "group_manualplus_waiting", {
            "group_id": event.chat_id,
            "dynamic_timeout": dynamic_timeout,
            "traffic_count": msg_count
        })

# ===== YENİ: COOLDOWN TEMİZLEME FONKSİYONU =====
async def _update_crm_profiles(event, bot_username, user_id, bot_user_id):
    """CRM profillerini güncelle"""
    try:
        # Kullanıcı profilini al veya oluştur
        user_profile = await crm_db.get_user_profile(user_id)
        if not user_profile:
            sender = event.sender
            user_profile = await crm_db.create_user_profile(
                user_id=user_id,
                username=sender.username or f"user_{user_id}",
                first_name=sender.first_name or "Unknown",
                last_name=sender.last_name or "",
                is_bot=getattr(sender, 'bot', False),
                is_premium=getattr(sender, 'premium', False)
            )
        
        # Grup profilini al veya oluştur
        group_profile = await crm_db.get_group_profile(event.chat_id)
        if not group_profile:
            try:
                chat = await event.get_chat()
                group_profile = await crm_db.create_group_profile(
                    group_id=event.chat_id,
                    title=chat.title or f"Group_{event.chat_id}",
                    username=getattr(chat, 'username', None),
                    group_type="supergroup" if hasattr(chat, 'megagroup') and chat.megagroup else "group",
                    member_count=getattr(chat, 'participants_count', 0)
                )
            except:
                # Fallback grup profili
                group_profile = await crm_db.create_group_profile(
                    group_id=event.chat_id,
                    title=f"Group_{event.chat_id}",
                    username=None,
                    group_type="group",
                    member_count=0
                )
        
        # Kullanıcı yanıtını kaydet
        await crm_db.record_user_response(
            bot_username, event.chat_id, user_id, event.raw_text, True
        )
        
    except Exception as e:
        log_event("crm_integration", f"❌ CRM profil güncelleme hatası: {e}")

def cleanup_old_cooldowns():
    """Eski cooldown'ları temizler - memory leak prevention"""
    current_time = time.time()
    
    # 1 saatten eski cooldown'ları temizle
    old_keys = []
    for key, timestamp in reply_cooldowns.items():
        if current_time - timestamp > 3600:  # 1 saat
            old_keys.append(key)
    
    for key in old_keys:
        reply_cooldowns.pop(key, None)
    
    # Grup cooldown'ları için de aynı işlem
    old_keys = []
    for key, timestamp in group_reply_cooldowns.items():
        if current_time - timestamp > 3600:  # 1 saat
            old_keys.append(key)
    
    for key in old_keys:
        group_reply_cooldowns.pop(key, None)

# Periyodik temizlik için background task
async def cooldown_cleanup_task():
    """Background task - cooldown temizliği"""
    while True:
        try:
            await asyncio.sleep(1800)  # 30 dakika interval
            cleanup_old_cooldowns()
            log_event("group_handler", f"🧹 Cooldown temizliği: {len(reply_cooldowns)} user, {len(group_reply_cooldowns)} grup")
        except Exception as e:
            log_event("group_handler", f"❌ Cooldown temizlik hatası: {e}")

# Cleanup task'ı sistem başlatıldığında controller tarafından başlatılacak

async def setup_group_handlers(client, username):
    """Group handler'ları setup et"""
    from telethon import events
    
    try:
        # Group mesaj handler'ı
        @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_group))
        async def group_message_handler(event):
            try:
                await handle_group_message(event, client)
            except Exception as e:
                log_event(username, f"❌ Group handler hatası: {e}")
        
        # Inline button handler'ı
        @client.on(events.CallbackQuery(pattern=b"cmd_"))
        async def command_button_handler(event):
            try:
                await handle_inline_command_choice(event)
            except Exception as e:
                log_event(username, f"❌ Command button handler hatası: {e}")
        
        # Cooldown temizleme task'ını başlat
        asyncio.create_task(cooldown_cleanup_task())
        
        log_event(username, "✅ Group handler'lar kuruldu")
        
    except Exception as e:
        log_event(username, f"❌ Group handler kurulum hatası: {e}")
