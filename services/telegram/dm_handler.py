# handlers/dm_handler.py
import random
import datetime
import asyncio
import time
import hashlib
from telethon import Button
from core.license_checker import LicenseChecker
from core.profile_loader import load_profile
from gpt.flirt_agent import generate_reply
from gpt.system_prompt_manager import get_menu_prompt
from utilities.log_utils import log_event
from utilities.template_utils import get_profile_reply_message
from utilities.payment_utils import generate_payment_message, load_banks
from core.analytics_logger import log_analytics
from utilities.smart_reply import smart_reply

# Redis state management import et
from utilities.redis_client import set_state, get_state, delete_state, set_cooldown, check_cooldown

# manualplus pending dictionary'sini group_handler'dan import et
from handlers.group_handler import manualplus_pending

# Merkezi davet yöneticisini import et
from core.invite_manager import invite_manager

# ===== DM COOLDOWN SİSTEMİ - AGRESİF MESAJLAŞMAYI ÖNLEMEK =====
dm_cooldowns = {}  # {f"{bot_username}:{user_id}": last_message_time}
dm_message_counts = {}  # {f"{bot_username}:{user_id}": [timestamps]}

# Cooldown ayarları
DM_COOLDOWN_SECONDS = 300  # 5 dakika minimum bekleme
DM_MAX_MESSAGES_PER_HOUR = 3  # Saatte maksimum 3 mesaj
DM_TRACKING_WINDOW = 3600  # 1 saat pencere

# ===== YENİ: SATIŞ KAPATMA SİSTEMİ =====
# VIP ilgi gösterenleri takip et
vip_interested_users = {}  # {f"{bot_username}:{user_id}": {"timestamp": time, "stage": "interested/pricing/payment"}}

# Satış kapatma anahtar kelimeleri
VIP_INTEREST_KEYWORDS = [
    "vip", "özel", "premium", "grup", "kanal", "exclusive", "katıl", "üye", "membership",
    "ilginç", "merak", "nasıl", "ne kadar", "fiyat", "ücret", "para", "ödeme",
    "istiyorum", "olur", "tamam", "evet", "kabul", "ok", "peki", "iyi"
]

PAYMENT_KEYWORDS = [
    "iban", "papara", "ödeme", "banka", "para", "gönder", "transfer", "havale",
    "nasıl", "nereye", "hangi", "hesap", "kart", "ödeyeceğim", "göndereceğim"
]

def check_vip_interest(message_text: str) -> bool:
    """Kullanıcının VIP'e ilgi gösterip göstermediğini kontrol eder"""
    lowered = message_text.lower()
    return any(keyword in lowered for keyword in VIP_INTEREST_KEYWORDS)

def check_payment_intent(message_text: str) -> bool:
    """Kullanıcının ödeme niyeti gösterip göstermediğini kontrol eder"""
    lowered = message_text.lower()
    return any(keyword in lowered for keyword in PAYMENT_KEYWORDS)

def update_vip_interest(bot_username: str, user_id: int, stage: str = "interested"):
    """VIP ilgi durumunu günceller"""
    key = f"{bot_username}:{user_id}"
    vip_interested_users[key] = {
        "timestamp": time.time(),
        "stage": stage
    }

def get_vip_interest_stage(bot_username: str, user_id: int) -> str:
    """Kullanıcının VIP ilgi aşamasını döner"""
    key = f"{bot_username}:{user_id}"
    if key in vip_interested_users:
        # 1 saatten eski ilgiyi sıfırla
        if time.time() - vip_interested_users[key]["timestamp"] > 3600:
            vip_interested_users.pop(key, None)
            return "none"
        return vip_interested_users[key]["stage"]
    return "none"

async def handle_vip_sales_funnel(client, user_id, message_text, bot_profile, client_username):
    """VIP satış funnel'ını yönetir - ilgiden ödemeye kadar"""
    current_stage = get_vip_interest_stage(client_username, user_id)
    
    # VIP ilgisi tespit edildi
    if check_vip_interest(message_text) and current_stage == "none":
        update_vip_interest(client_username, user_id, "interested")
        
        # VIP tanıtım mesajı + fiyat bilgisi
        vip_intro_messages = [
            f"🔥 VIP grubumda çok daha özel içerikler var canım! Sadece seçkin üyelerim için 💎\n\n"
            f"VIP üyelik: **{bot_profile.get('vip_price', '300')}₺**\n"
            f"📱 Özel show'lar, arşiv erişimi, birebir sohbet hakkı...\n\n"
            f"💳 Hemen katılmak istersen IBAN bilgimi verebilirim 😘",
            
            f"💋 VIP kanalımda seni çok daha cesur halimle tanışacaksın 🔥\n\n"
            f"Üyelik ücreti: **{bot_profile.get('vip_price', '300')}₺**\n"
            f"🎭 Özel videolar, canlı show'lar, premium içerikler...\n\n"
            f"💰 Ödeme yapmak istersen hangi bankayı kullanıyorsun? 😉",
            
            f"✨ VIP grubum sadece özel müşterilerim için canım 💎\n\n"
            f"Fiyat: **{bot_profile.get('vip_price', '300')}₺** (tek seferlik)\n"
            f"🔥 Sınırsız erişim, özel muamele, premium deneyim...\n\n"
            f"💳 İstersen şimdi ödeme bilgilerimi paylaşabilirim 💕"
        ]
        
        response = random.choice(vip_intro_messages)
        await client.send_message(user_id, response, parse_mode="markdown")
        
        # DM cooldown'ı güncelle
        await update_dm_cooldown(client_username, user_id)
        
        log_event(client_username, f"💎 VIP satış funnel başlatıldı: {user_id}")
        log_analytics(client_username, "vip_sales_funnel_started", {
            "user_id": user_id,
            "stage": "interested",
            "message": message_text
        })
        return True
    
    # Ödeme niyeti tespit edildi
    elif check_payment_intent(message_text) or current_stage == "interested":
        # Daha önce ödeme mesajı gönderildi mi kontrol et
        payment_sent_key = f"payment_sent:{client_username}:{user_id}"
        from utilities.redis_client import get_state, set_state
        
        payment_already_sent = await get_state(payment_sent_key, "sent", default="false")
        
        if payment_already_sent == "true":
            # Zaten ödeme bilgileri gönderilmiş, tekrar gönderme
            log_event(client_username, f"💰 VIP ödeme bilgileri zaten gönderilmiş: {user_id}")
            return True
        
        update_vip_interest(client_username, user_id, "payment")
        
        # Direkt IBAN/Papara yönlendirme
        papara_bankas = bot_profile.get("papara_accounts") or DEFAULT_PAPARA_BANKAS
        
        payment_messages = [
            f"💳 Harika! VIP üyeliğin için ödeme bilgileri:\n\n"
            f"**Tutar: {bot_profile.get('vip_price', '300')}₺**\n\n"
            f"Hangi bankayı kullanıyorsun canım? 👇",
            
            f"🔥 Mükemmel seçim! VIP grubuma hoş geldin 💎\n\n"
            f"**Ödeme: {bot_profile.get('vip_price', '300')}₺**\n\n"
            f"Banka seçimi yap, IBAN'ımı göndereyim 💕",
            
            f"💋 VIP deneyimin başlıyor! Çok heyecanlıyım 🔥\n\n"
            f"**Üyelik ücreti: {bot_profile.get('vip_price', '300')}₺**\n\n"
            f"Hangi banka ile ödeme yapacaksın? 👇"
        ]
        
        response = random.choice(payment_messages)
        
        # Banka seçim butonları
        buttons = [Button.inline(bank, data=f"bank_{bank}") for bank in papara_bankas.keys()]
        await client.send_message(user_id, response, buttons=buttons, parse_mode="markdown")
        
        # DM cooldown'ı güncelle
        await update_dm_cooldown(client_username, user_id)
        
        # Ödeme mesajı gönderildi olarak işaretle (24 saat TTL)
        await set_state(payment_sent_key, "sent", "true", expire_seconds=86400)
        
        log_event(client_username, f"💰 VIP ödeme aşamasına geçildi: {user_id}")
        log_analytics(client_username, "vip_payment_stage", {
            "user_id": user_id,
            "stage": "payment",
            "vip_price": bot_profile.get('vip_price', '300')
        })
        return True
    
    return False

def check_dm_cooldown(bot_username: str, user_id: int) -> tuple[bool, str]:
    """
    DM cooldown kontrolü - agresif mesajlaşmayı önler
    Returns: (can_send: bool, reason: str)
    """
    current_time = time.time()
    cooldown_key = f"{bot_username}:{user_id}"
    
    # Son mesaj zamanını kontrol et
    if cooldown_key in dm_cooldowns:
        time_since_last = current_time - dm_cooldowns[cooldown_key]
        if time_since_last < DM_COOLDOWN_SECONDS:
            remaining = DM_COOLDOWN_SECONDS - time_since_last
            return False, f"DM cooldown: {remaining/60:.1f} dakika kaldı"
    
    # Saatlik mesaj sayısını kontrol et
    if cooldown_key not in dm_message_counts:
        dm_message_counts[cooldown_key] = []
    
    # Eski mesajları temizle (1 saatten eski)
    dm_message_counts[cooldown_key] = [
        timestamp for timestamp in dm_message_counts[cooldown_key]
        if current_time - timestamp < DM_TRACKING_WINDOW
    ]
    
    # Saatlik limit kontrolü
    if len(dm_message_counts[cooldown_key]) >= DM_MAX_MESSAGES_PER_HOUR:
        return False, f"Saatlik limit aşıldı: {DM_MAX_MESSAGES_PER_HOUR} mesaj/saat"
    
    return True, "OK"

async def update_dm_cooldown(bot_username: str, user_id: int):
    """DM cooldown'ı güncelle ve merkezi kayıt yap"""
    current_time = time.time()
    cooldown_key = f"{bot_username}:{user_id}"
    
    # Son mesaj zamanını kaydet
    dm_cooldowns[cooldown_key] = current_time
    
    # Mesaj sayısını artır
    if cooldown_key not in dm_message_counts:
        dm_message_counts[cooldown_key] = []
    dm_message_counts[cooldown_key].append(current_time)
    
    # Merkezi DM kaydı
    await invite_manager.record_dm_sent(bot_username, user_id)

def cleanup_dm_cooldowns():
    """Eski DM cooldown'ları temizle"""
    current_time = time.time()
    
    # 24 saatten eski cooldown'ları temizle
    old_keys = []
    for key, timestamp in dm_cooldowns.items():
        if current_time - timestamp > 86400:  # 24 saat
            old_keys.append(key)
    
    for key in old_keys:
        dm_cooldowns.pop(key, None)
        dm_message_counts.pop(key, None)

DEFAULT_FLIRT_TEMPLATES = [
    "Selam! 💖 Bugün sohbet etmek ister misin?",
    "Günün nasıl geçti? Seni biraz motive edebilirim 😉",
    "Hazırsan eğlenceli bir sohbete başlayalım 😈",
    "VIP grubumda daha fazlası seni bekliyor 🫦 Katılmak ister misin?"
]
DEFAULT_SERVICES_MENU = """
💼 *Hizmet Menüsü* 💼

- Sesli Sohbet: 200₺
- Görüntülü Görüşme: 300₺
- VIP Grup Üyeliği: 150₺
- Kişiye Özel Arşiv: 100₺

💳 IBAN/Papara için bilgi almak istersen yazabilirsin.
"""
DEFAULT_PAPARA_BANKAS = {
    "Ziraat": "TR12 0001 0012 3456 7890 1234 56",
    "Vakif": "TR34 0001 0012 3456 7890 9876 54",
    "Isbank": "TR56 0001 0012 3456 7890 1928 34"
}

active_bank_requests = {}

def _load_bot_profile(client_username, bot_user_id):
    """Bot profilini yükler"""
    try:
        profile = load_profile(client_username)
        if profile:
            return profile
    except:
        pass
    
    # Fallback: default bot profili
    return {
        "type": "bot",
        "reply_mode": "manualplus",
        "manualplus_timeout_sec": 90,
        "services_menu": DEFAULT_SERVICES_MENU,
        "papara_accounts": DEFAULT_PAPARA_BANKAS,
        "auto_menu_enabled": True,
        "auto_menu_threshold": 3
    }

def _load_profile_any(username, user_id, client_username):
    """Kullanıcı profilini yükler"""
    try:
        return load_profile(username) or load_profile(str(user_id))
    except:
        return {"type": "client"}

async def get_conversation_state(dm_key: str) -> dict:
    """Redis'ten conversation state getir"""
    try:
        state = await get_state(dm_key, "conversation_state")
        if state is None:
            # Default state oluştur
            current_time = time.time()
            state = {
                "last_bot_message": 0,
                "user_responded": False,
                "conversation_active": True,
                "last_user_message": current_time,
                "phase": "initial_contact",
                "manual_intervention_time": 0,
                "followup_count": 0,
                "last_manual_check": 0,
                "auto_message_count": 0,
                "menu_sent": False,
                "manual_mode_active": False,  # Manuel mod aktif mi
                "last_manual_message": 0,     # Son manuel mesaj zamanı
                "auto_messages_paused": False  # Otomatik mesajlar duraklatıldı mı
            }
            await set_state(dm_key, "conversation_state", state, expire_seconds=86400)  # 24 saat TTL
        return state
    except Exception as e:
        print(f"Redis conversation state hatası: {e}")
        # Fallback: in-memory state
        return {
            "last_bot_message": 0,
            "user_responded": False,
            "conversation_active": True,
            "last_user_message": time.time(),
            "phase": "initial_contact",
            "manual_intervention_time": 0,
            "followup_count": 0,
            "last_manual_check": 0,
            "auto_message_count": 0,
            "menu_sent": False,
            "manual_mode_active": False,
            "last_manual_message": 0,
            "auto_messages_paused": False
        }

async def update_conversation_state(dm_key, user_responded=False, bot_sent_message=False, manual_intervention=False, menu_sent=False):
    """DM conversation state'ini günceller - Redis ile - manuel müdahale sonrası otomatik mesajları durdurur"""
    current_time = time.time()
    
    # Mevcut state'i getir
    state = await get_conversation_state(dm_key)
    
    if user_responded:
        state["user_responded"] = True
        state["last_user_message"] = current_time
        state["conversation_active"] = True
        
        # Manuel müdahale sonrası kullanıcı cevap verdi - doğal konuşma devam ediyor
        if state["manual_mode_active"]:
            state["phase"] = "manual_conversation"
            state["last_manual_check"] = current_time
            # Otomatik mesajları tekrar aktifleştir ama daha az agresif
            state["auto_messages_paused"] = False
        
        # Kullanıcı cevap verdi, pending timeout'u iptal et
        if dm_key in manualplus_pending:
            manualplus_pending[dm_key] = False
    
    if bot_sent_message:
        state["last_bot_message"] = current_time
        state["user_responded"] = False
        state["conversation_active"] = True
        
        # Manuel mod aktifken otomatik mesaj sayacını artırma
        if not state["manual_mode_active"]:
            state["auto_message_count"] = state.get("auto_message_count", 0) + 1
    
    if manual_intervention:
        state["phase"] = "manual_engaged"
        state["manual_intervention_time"] = current_time
        state["last_manual_message"] = current_time
        state["manual_mode_active"] = True
        state["auto_messages_paused"] = True  # Otomatik mesajları duraklat
        state["followup_count"] = 0  # Reset followup counter
        state["auto_message_count"] = 0  # Reset auto message counter
        
        # Pending timeout'ları iptal et
        if dm_key in manualplus_pending:
            manualplus_pending[dm_key] = False
    
    if menu_sent:
        state["menu_sent"] = True
    
    # State'i Redis'e kaydet
    try:
        await set_state(dm_key, "conversation_state", state, expire_seconds=86400)  # 24 saat TTL
    except Exception as e:
        print(f"Redis state kaydetme hatası: {e}")
    
    return state

async def should_send_auto_menu(dm_key, bot_profile=None):
    """Otomatik menü gönderilmeli mi kontrol et - manuel mod kontrolü ile - Redis'ten state alır"""
    try:
        state = await get_conversation_state(dm_key)
        
        # Manuel mod aktifken otomatik menü gönderme
        if state.get("manual_mode_active", False) or state.get("auto_messages_paused", False):
            return False
        
        # Bot profilinden ayarları al
        if bot_profile:
            auto_menu_enabled = bot_profile.get("auto_menu_enabled", True)
            auto_menu_threshold = bot_profile.get("auto_menu_threshold", 3)
        else:
            auto_menu_enabled = True
            auto_menu_threshold = 3
        
        # Otomatik menü devre dışı mı
        if not auto_menu_enabled:
            return False
        
        # Menü zaten gönderildi mi
        if state.get("menu_sent", False):
            return False
        
        # Manuel müdahale varsa menü gönderme
        if state.get("phase") in ["manual_engaged", "manual_conversation"]:
            return False
        
        # Otomatik mesaj sayısı threshold'u geçti mi
        auto_count = state.get("auto_message_count", 0)
        return auto_count >= auto_menu_threshold
    except Exception as e:
        print(f"Auto menu kontrol hatası: {e}")
        return False

async def should_send_followup(dm_key, followup_delay=3600):  # 1 saat
    """Takip mesajı gönderilmeli mi kontrol et - manuel mod kontrolü ile - Redis'ten state alır"""
    try:
        state = await get_conversation_state(dm_key)
        current_time = time.time()
        phase = state.get("phase", "initial_contact")
        
        # Manuel mod aktifken takip mesajı gönderme
        if state.get("manual_mode_active", False) or state.get("auto_messages_paused", False):
            return False
        
        # Manuel müdahale sonrası çok daha uzun bekle
        if phase == "manual_engaged":
            time_since_manual = current_time - state.get("manual_intervention_time", 0)
            if time_since_manual < 14400:  # 4 saat bekle
                return False
            
            # Son kullanıcı mesajından beri geçen süre
            time_since_user = current_time - state.get("last_user_message", 0)
            return time_since_user > 21600  # 6 saat sessizlik sonrası
        
        elif phase == "manual_conversation":
            # Manuel konuşma sonrası çok nazik takip
            time_since_user = current_time - state.get("last_user_message", 0)
            return time_since_user > 43200  # 12 saat sessizlik sonrası
        
        elif phase == "active_conversation":
            # Aktif konuşma sonrası daha nazik takip
            time_since_user = current_time - state.get("last_user_message", 0)
            return time_since_user > 21600  # 6 saat sessizlik sonrası
        
        # Normal takip mantığı
        time_since_bot_message = current_time - state["last_bot_message"]
        
        # Kullanıcı cevap vermedi ve yeterli süre geçti
        return (not state["user_responded"] and 
                time_since_bot_message > followup_delay and
                state["conversation_active"])
    except Exception as e:
        print(f"Followup kontrol hatası: {e}")
        return False

async def schedule_followup_message(client, user_id, dm_key, bot_profile, client_username):
    """Takip mesajı zamanlayıcısı - manuel mod kontrolü ile"""
    state = await get_conversation_state(dm_key)
    phase = state.get("phase", "initial_contact")
    
    # Manuel mod aktifken takip mesajı gönderme
    if state.get("manual_mode_active", False) or state.get("auto_messages_paused", False):
        log_event(client_username, f"📵 Takip mesajı iptal edildi - manuel mod aktif")
        return
    
    # Çok daha konservatif takip stratejileri - spam önleme
    if phase == "manual_engaged":
        followup_delays = [86400, 172800, 604800]  # 24 saat, 48 saat, 1 hafta
        followup_messages = [
            "Merhaba! Nasıl gidiyor? 🤗",
            "Selam, bugün nasıl geçti? 💕",
            "Hey! Seni merak ettim, her şey yolunda mı? 🤗"
        ]
    elif phase == "manual_conversation":
        followup_delays = [172800, 604800, 1209600]  # 48 saat, 1 hafta, 2 hafta
        followup_messages = [
            "Selam! Bugün nasıl geçti? 😊",
            "Merhaba canım, uzun zamandır konuşmuyoruz 💕",
            "Hey! Seni özledim, nasılsın? 🤗"
        ]
    elif phase == "active_conversation":
        followup_delays = [86400, 259200, 604800]  # 24 saat, 3 gün, 1 hafta
        followup_messages = [
            "Selam! Bugün nasıl geçti? 😊",
            "Merhaba canım, uzun zamandır konuşmuyoruz 💕",
            "Hey! Seni özledim, nasılsın? 🤗"
        ]
    else:
        # Normal takip (ilk temas) - reduced frequency
        followup_delays = [86400, 259200, 604800]  # 24 saat, 3 gün, 1 hafta
        followup_messages = [
            "Merhaba! Mesajımı gördün mü? 😊",
            "Selam canım, nasılsın? Sohbet etmek ister misin? 💕",
            "Hey! Uzun zamandır konuşmuyoruz, her şey yolunda mı? 🤗"
        ]
    
    for i, delay in enumerate(followup_delays):
        await asyncio.sleep(delay)
        
        # Her delay'de conversation state kontrol et
        current_state = await get_conversation_state(dm_key)
        
        # Manuel mod kontrolü
        if current_state.get("manual_mode_active", False) or current_state.get("auto_messages_paused", False):
            log_event(client_username, f"📵 Takip mesajı #{i+1} iptal edildi - manuel mod aktif")
            break
        
        if await should_send_followup(dm_key, 0):  # 0 delay = hemen kontrol et
            # Takip mesajı için de cooldown kontrolü
            can_send_followup, followup_reason = check_dm_cooldown(client_username, user_id)
            if not can_send_followup:
                log_event(client_username, f"🚫 Takip mesajı #{i+1} cooldown: {followup_reason}")
                break
            
            # Merkezi DM kontrolü de yap
            can_send_dm, dm_reason = await invite_manager.can_send_dm(client_username, user_id)
            if not can_send_dm:
                log_event(client_username, f"🚫 Takip mesajı #{i+1} merkezi engel: {dm_reason}")
                break
            
            try:
                # Phase'e uygun takip mesajı gönder
                if i < len(followup_messages):
                    followup_msg = followup_messages[i]
                else:
                    # Son mesaj için akıllı yanıt kullan
                    followup_msg = await smart_reply.get_smart_reply("takip mesajı", bot_profile, client_username)
                
                await client.send_message(user_id, followup_msg)
                
                # DM cooldown'ı güncelle
                await update_dm_cooldown(client_username, user_id)
                
                # Bot mesaj gönderdi, state güncelle
                await update_conversation_state(dm_key, bot_sent_message=True)
                
                # Followup count artır
                current_state["followup_count"] = current_state.get("followup_count", 0) + 1
                
                log_event(client_username, f"📬 {phase} takip mesajı #{i+1} gönderildi: {followup_msg}")
                log_analytics(client_username, "dm_followup_sent", {
                    "user_id": user_id,
                    "followup_number": i+1,
                    "message": followup_msg,
                    "phase": phase,
                    "total_followups": current_state["followup_count"]
                })
                
            except Exception as e:
                log_event(client_username, f"❌ Takip mesajı #{i+1} hatası: {e}")
                break

# ===== CLEANUP TASK =====
async def dm_cooldown_cleanup_task():
    """Background task - DM cooldown temizliği"""
    while True:
        try:
            await asyncio.sleep(3600)  # 1 saat interval
            cleanup_dm_cooldowns()
            log_event("dm_handler", f"🧹 DM cooldown temizliği: {len(dm_cooldowns)} kullanıcı")
        except Exception as e:
            log_event("dm_handler", f"❌ DM cooldown temizlik hatası: {e}")
        else:
            # Kullanıcı cevap verdi veya conversation inactive, takip mesajlarını durdur
            log_event(client_username, f"✅ {phase} takip mesajı #{i+1} iptal edildi - kullanıcı aktif")
            break

async def send_auto_menu(client, user_id, dm_key, bot_profile, client_username):
    """Otomatik menü gönderme fonksiyonu"""
    try:
        # Show menü sistemini kullan
        from utilities.menu_manager import show_menu_manager
        
        # Önce show menüsünü dene
        show_menu = show_menu_manager.get_show_menu(client_username, compact=True)  # Otomatik için kısa versiyon
        
        # Menü öncesi geçiş mesajı
        transition_messages = [
            "Bu arada, sana özel hizmetlerimizi göstermek istiyorum 😊",
            "Daha fazla eğlence için menümüze göz atabilirsin 💕",
            "Sana özel tekliflerim var, bakmak ister misin? 😉",
            "Show menümü görmek ister misin? 🎭",
            "Özel hizmetlerimden haberdar olmak istersen... 🔥"
        ]
        
        import random
        transition_msg = random.choice(transition_messages)
        
        # Geçiş mesajı gönder
        await client.send_message(user_id, transition_msg)
        await asyncio.sleep(2)  # 2 saniye bekle
        
        # Menü mesajı gönder
        if show_menu:
            await client.send_message(user_id, "🎭 Show menüsü:", parse_mode="markdown")
            await client.send_message(user_id, show_menu, parse_mode="markdown")
            log_event(client_username, f"🎭 Otomatik show menüsü gönderildi: {len(show_menu)} karakter")
        else:
            # Fallback: eski sistem
            services_menu = bot_profile.get("services_menu") or DEFAULT_SERVICES_MENU
            await client.send_message(user_id, "📝 Hizmet menüsü aşağıda:", parse_mode="markdown")
            await client.send_message(user_id, services_menu, parse_mode="markdown")
            log_event(client_username, f"📝 Fallback menü gönderildi: {len(services_menu)} karakter")
        
        # State güncelle - menü gönderildi
        await update_conversation_state(dm_key, menu_sent=True, bot_sent_message=True)
        
        log_event(client_username, f"🍽️ Otomatik menü gönderildi: {user_id}")
        log_analytics(client_username, "dm_auto_menu_sent", {
            "user_id": user_id,
            "auto_message_count": await get_conversation_state(dm_key).get("auto_message_count", 0),
            "transition_message": transition_msg,
            "menu_type": "show" if show_menu else "fallback"
        })
        
    except Exception as e:
        log_event(client_username, f"❌ Otomatik menü gönderme hatası: {e}")

async def handle_message(client, sender, message_text, session_created_at):
    # Sender güvenlik kontrolü
    if sender is None:
        log_event("unknown_bot", "❌ DM sender None geldi")
        return
    
    user_id = sender.id
    username = sender.username or sender.first_name or f"user_{user_id}"

    # Bot kontrolü - Eğer gönderen bir bot ise mesajı işleme
    if hasattr(sender, 'bot') and sender.bot:
        log_event("bot_filter", f"🤖 Bot mesajı engellendi: {username} ({user_id}) - '{message_text}'")
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
        log_event("bot_filter", f"🚫 Telegram resmi bot'u engellendi: {username} ({user_id}) - '{message_text}'")
        return

    # Bot username'ini al
    try:
        me = await client.get_me()
        client_username = me.username or f"bot_{me.id}"
        bot_user_id = me.id
        log_event(client_username, f"🔍 DM HANDLER ÇAĞRILDI: '{message_text}' from {username}")
    except:
        client_username = "unknown_bot"
        bot_user_id = 0
        log_event("unknown_bot", "❌ Bot bilgisi alınamadı")
    
    # Merkezi DM kontrolü - invite_manager kullan
    can_send_dm, dm_reason = await invite_manager.can_send_dm(client_username, user_id)
    if not can_send_dm:
        log_event(client_username, f"🚫 DM engellendi: {dm_reason}")
        log_analytics(client_username, "dm_blocked_by_manager", {
            "user_id": user_id,
            "reason": dm_reason
        })
        return
    
    # Eski cooldown kontrolü - backward compatibility
    can_send, cooldown_reason = check_dm_cooldown(client_username, user_id)
    if not can_send:
        log_event(client_username, f"🚫 DM cooldown aktif: {cooldown_reason}")
        log_analytics(client_username, "dm_blocked_cooldown", {
            "user_id": user_id,
            "reason": cooldown_reason
        })
        return
    
    # Bot profilini yükle
    bot_profile = _load_bot_profile(client_username, bot_user_id)
    
    # Mesaj hash'i oluştur (duplicate kontrolü için)
    message_hash = hashlib.md5(message_text.encode()).hexdigest()[:8]
    
    # Duplicate mesaj kontrolü
    is_duplicate = await invite_manager.check_duplicate_message(client_username, user_id, message_hash)
    if is_duplicate:
        log_event(client_username, f"🔁 Duplicate mesaj tespit edildi, cevap verilmedi: {message_text[:50]}...")
        return
    
    # Spambot kontrolü - Telegram'ın resmi spam bot'una mesaj gönderme
    if username.lower() in ["spambot", "spam_bot"] or user_id == 178220800:  # @SpamBot'un user_id'si
        log_event(client_username, f"🚫 Spambot'a mesaj gönderilmedi: {message_text}")
        log_analytics(username, "dm_blocked_spambot", {"message": message_text})
        return
    
    # Lisans kontrolü - sistem botları için atla
    checker = LicenseChecker()
    if not checker.is_license_valid(user_id, session_created_at, bot_profile):
        # Kullanıcıya mesaj gönderme - sadece log'la ve hizmeti durdur
        log_event(client_username, f"⏳ Demo süresi doldu - hizmet durduruldu: {username}")
        log_analytics(username, "dm_blocked_demo_timeout", {"message": message_text})
        return

    # Bot profilinden ayarları al (kullanıcı profili değil!)
    # Enforce manualplus mode to reduce flooding and disable GPT
    reply_mode = "manualplus"
    manualplus_timeout = int(bot_profile.get("manualplus_timeout_sec", 3600))
    services_menu = bot_profile.get("services_menu") or DEFAULT_SERVICES_MENU
    papara_bankas = bot_profile.get("papara_accounts") or DEFAULT_PAPARA_BANKAS

    lowered = message_text.lower()
    log_event(client_username, f"📥 DM alındı: {message_text} | Yanıt modu: {reply_mode}")
    log_analytics(client_username, "dm_received", {
        "from_user": username,
        "message": message_text,
        "mode": reply_mode,
        "bot_profile": client_username
    })

    # manualplus zamanlayıcısı - DM için unique key
    dm_key = f"dm:{client_username}:{user_id}"
    
    # Conversation state güncelle - kullanıcı mesaj gönderdi (ama henüz manuel cevap değil)
    conv_state = await update_conversation_state(dm_key, user_responded=False)
    log_event(client_username, f"👤 Kullanıcı mesajı: conversation_active={conv_state['conversation_active']}")

    # ===== YENİ: VIP SATIŞ FUNNEL KONTROLÜ =====
    # VIP satış funnel'ını kontrol et - en öncelikli
    vip_handled = await handle_vip_sales_funnel(client, user_id, message_text, bot_profile, client_username)
    if vip_handled:
        # DM cooldown'ı güncelle
        await update_dm_cooldown(client_username, user_id)
        # Bot mesaj gönderdi, state güncelle
        await update_conversation_state(dm_key, bot_sent_message=True)
        return

    # ===== YENİ: @ARAYISVIPS GRUP DAVET SİSTEMİ =====
    # Konfigürasyondan DM davet ayarlarını kontrol et
    from utilities.bot_config_manager import bot_config_manager
    
    dm_invite_enabled, dm_invite_reason = bot_config_manager.is_dm_invite_enabled(client_username)
    if dm_invite_enabled:
        dm_invite_chance = bot_config_manager.get_dm_invite_chance_enhanced(client_username)
        
        # Agresif grup daveti kontrolü
        is_aggressive = bot_config_manager.is_group_invite_aggressive(client_username)
        if is_aggressive:
            dm_invite_chance = min(dm_invite_chance * 1.5, 0.8)  # Agresif modda %50 artır, max %80
        
        if random.random() < dm_invite_chance:
            try:
                from utilities.group_invite_strategy import group_invite_strategy
                
                # Hedef grubu al
                target_group = bot_config_manager.get_target_group(client_username)
                target_group_id = None
                
                # Grup ID'sini al
                try:
                    group_entity = await client.get_entity(target_group)
                    target_group_id = group_entity.id
                except Exception as e:
                    log_event(client_username, f"⚠️ Hedef grup ID alınamadı: {e}")
                
                # Grup daveti gönderilip gönderilemeyeceğini kontrol et
                can_invite = True
                invite_reason = ""
                
                if target_group_id:
                    can_invite, invite_reason = await invite_manager.can_send_group_invite(
                        client_username, user_id, target_group_id, client
                    )
                
                if can_invite:
                    # Grup daveti gönder
                    invite_success = await group_invite_strategy.invite_from_dm_conversation(
                        client, user_id, username, message_text, client_username
                    )
                    
                    if invite_success and target_group_id:
                        # Daveti kaydet
                        await invite_manager.record_group_invite(client_username, user_id, target_group_id)
                        log_event(client_username, f"📤 {target_group} grup daveti gönderildi: {username}")
                        
                        # DM kaydını güncelle
                        await invite_manager.record_dm_sent(client_username, user_id)
                        
                        # Davet gönderildiyse normal yanıtı atla (çift mesaj önleme)
                        await update_dm_cooldown(client_username, user_id)
                        await update_conversation_state(dm_key, bot_sent_message=True)
                        return
                else:
                    log_event(client_username, f"🚫 Grup daveti engellendi: {invite_reason}")
                    
            except Exception as e:
                log_event(client_username, f"⚠️ Grup davet hatası: {e}")
                # Hata olursa normal akışa devam et
    else:
        log_event(client_username, f"🚫 DM davet devre dışı: {dm_invite_reason}")

    # Menü veya VIP içerik talebi
    if any(keyword in lowered for keyword in ["fiyat", "menü", "ücret", "kaç para", "vip", "hizmet", "show", "şov"]):
        # Show menü sistemini kullan
        from utilities.menu_manager import show_menu_manager
        
        # Önce show menüsünü dene
        show_menu = show_menu_manager.get_show_menu(client_username, compact=False)
        if show_menu:
            await client.send_message(user_id, "🎭 Show menüsü aşağıda:", parse_mode="markdown")
            await client.send_message(user_id, show_menu, parse_mode="markdown")
            log_event(client_username, f"🎭 Show menüsü gönderildi: {len(show_menu)} karakter")
        else:
            # Fallback: eski sistem
            await client.send_message(user_id, "📝 Hizmet menüsü aşağıda:", parse_mode="markdown")
            try:
                menu_prompt = get_menu_prompt(client_username)
                menu_reply = await generate_reply(agent_name=client_username, user_message=menu_prompt)
                await client.send_message(user_id, menu_reply)
                log_analytics(client_username, "dm_menu_prompt_reply", {"prompt": menu_prompt})
            except Exception as e:
                log_event(client_username, f"⚠️ Menü GPT üretim hatası: {str(e)}")
            await client.send_message(user_id, services_menu, parse_mode="markdown")
        
        # Bot mesaj gönderdi, state güncelle
        await update_conversation_state(dm_key, bot_sent_message=True)
        return

    # IBAN/Papara
    if any(keyword in lowered for keyword in ["iban", "papara", "ödeme", "banka"]):
        buttons = [Button.inline(bank, data=f"bank_{bank}") for bank in papara_bankas.keys()]
        active_bank_requests[user_id] = papara_bankas
        await client.send_message(user_id, "💳 Hangi bankayı kullanıyorsunuz? Lütfen seçiniz:", buttons=buttons)
        
        # Bot mesaj gönderdi, state güncelle
        await update_conversation_state(dm_key, bot_sent_message=True)
        log_analytics(client_username, "dm_bank_selection_prompt")
        return

    if message_text.strip() in papara_bankas:
        iban = papara_bankas[message_text.strip()]
        await client.send_message(user_id, f"💳 IBAN: `{iban}`\n📌 Açıklama kısmına Telegram adınızı yazınız.", parse_mode="markdown")
        
        # Bot mesaj gönderdi, state güncelle
        await update_conversation_state(dm_key, bot_sent_message=True)
        log_analytics(client_username, "dm_direct_bank_selected", {"bank": message_text.strip()})
        return

    # --- YANIT MODLARI ---
    if reply_mode == "gpt":
        try:
            response = await generate_reply(agent_name=client_username, user_message=message_text)
            await client.send_message(user_id, response)
            
            # DM cooldown'ı güncelle
            await update_dm_cooldown(client_username, user_id)
            
            # Bot mesaj gönderdi, state güncelle
            await update_conversation_state(dm_key, bot_sent_message=True)
            
            # Otomatik menü kontrolü
            if await should_send_auto_menu(dm_key, bot_profile):
                await asyncio.sleep(3)  # 3 saniye bekle
                await send_auto_menu(client, user_id, dm_key, bot_profile, client_username)
            
            log_event(client_username, f"🤖 GPT yanıtı gönderildi: {response}")
            log_analytics(client_username, "dm_gpt_reply_sent", {"response": response})
        except Exception as e:
            await client.send_message(user_id, "🤖 Yanıt üretilemedi.")
            log_event(client_username, f"❌ GPT hatası: {str(e)}")
            log_analytics(client_username, "dm_gpt_reply_failed", {"error": str(e)})

    elif reply_mode == "manual":
        log_event(client_username, "✋ manual: yanıtı içerik üretici verecek")
        log_analytics(client_username, "dm_manual_no_reply")

    elif reply_mode == "manualplus":
        # Manuel yanıt bekleme sistemi - çift mesaj önleme ile
        if dm_key in manualplus_pending and manualplus_pending[dm_key]:
            log_event(client_username, "⚠️ Zaten bir manualplus timeout aktif, yeni timeout başlatılmıyor")
            return
        
        manualplus_pending[dm_key] = True

        async def check_dm_manualplus_timeout():
            await asyncio.sleep(manualplus_timeout)
            
            # Timeout sonrası conversation state kontrol et
            current_state = await get_conversation_state(dm_key)
            if current_state.get("user_responded", False):
                log_event(client_username, "✅ Kullanıcı manuel cevap verdi, otomatik yanıt iptal edildi")
                manualplus_pending.pop(dm_key, None)
                return
            
            if manualplus_pending.get(dm_key):
                try:
                    # Hybrid mode varsa onu kullan, yoksa normal smart reply
                    if bot_profile.get("reply_mode") == "hybrid":
                        smart_response = await smart_reply.get_hybrid_reply(message_text, bot_profile, client_username)
                    else:
                        smart_response = await smart_reply.get_smart_reply(message_text, bot_profile, client_username)
                    await client.send_message(user_id, smart_response)
                    
                    # DM cooldown'ı güncelle
                    await update_dm_cooldown(client_username, user_id)
                    
                    # Bot mesaj gönderdi, state güncelle
                    await update_conversation_state(dm_key, bot_sent_message=True)
                    
                    # Otomatik menü kontrolü
                    if await should_send_auto_menu(dm_key, bot_profile):
                        await asyncio.sleep(3)  # 3 saniye bekle
                        await send_auto_menu(client, user_id, dm_key, bot_profile, client_username)
                    
                    log_event(client_username, f"⏱️ DM manualplus: süre doldu, akıllı yanıt verildi → {smart_response}")
                    log_analytics(client_username, "dm_manualplus_smart_fallback_sent", {
                        "smart_response": smart_response,
                        "user_id": user_id
                    })
                    
                    # Takip mesajı için timer başlat
                    asyncio.create_task(schedule_followup_message(client, user_id, dm_key, bot_profile, client_username))
                    
                except Exception as e:
                    log_event(client_username, f"❌ DM manualplus akıllı fallback hatası: {str(e)}")
                    log_analytics(client_username, "dm_manualplus_smart_fallback_failed", {
                        "error": str(e),
                        "user_id": user_id
                    })
            manualplus_pending.pop(dm_key, None)

        asyncio.create_task(check_dm_manualplus_timeout())
        log_event(client_username, f"🕒 DM manualplus mod: {manualplus_timeout}s kullanıcı yanıtı bekleniyor...")
        log_analytics(client_username, "dm_manualplus_waiting", {
            "user_id": user_id,
            "timeout": manualplus_timeout
        })

    elif reply_mode == "hybrid":
        try:
            # Yeni Hybrid Mode: %30 GPT, %50 Bot Profili, %20 Genel Mesajlar
            response = await smart_reply.get_hybrid_reply(message_text, bot_profile, client_username)
            await client.send_message(user_id, response)
            
            # DM cooldown'ı güncelle
            await update_dm_cooldown(client_username, user_id)
            
            # Bot mesaj gönderdi, state güncelle
            await update_conversation_state(dm_key, bot_sent_message=True)
            
            # Otomatik menü kontrolü
            if await should_send_auto_menu(dm_key, bot_profile):
                await asyncio.sleep(3)  # 3 saniye bekle
                await send_auto_menu(client, user_id, dm_key, bot_profile, client_username)
            
            log_event(client_username, f"🎭 HYBRID yanıtı gönderildi: {response}")
            log_analytics(client_username, "dm_hybrid_reply_sent", {"response": response})
        except Exception as e:
            # Fallback: normal smart reply
            try:
                fallback_response = await smart_reply.get_smart_reply(message_text, bot_profile, client_username)
                await client.send_message(user_id, fallback_response)
                await update_conversation_state(dm_key, bot_sent_message=True)
                log_event(client_username, f"🔄 Hybrid fallback yanıtı: {fallback_response}")
                log_analytics(client_username, "dm_hybrid_fallback_sent", {"response": fallback_response})
            except Exception as fallback_error:
                await client.send_message(user_id, "🤖 Şu an yanıt veremiyorum, birazdan tekrar dene canım!")
                log_event(client_username, f"❌ Hybrid mod hatası: {str(e)}, Fallback hatası: {str(fallback_error)}")
                log_analytics(client_username, "dm_hybrid_failed", {"error": str(e), "fallback_error": str(fallback_error)})

    # User Type = Client ise: Feedback/Ticket sistemi (kullanıcı profili kontrol et)
    # NOT: Bu sadece reply_mode hiçbirine uymadığında çalışmalı
    else:
        user_profile = _load_profile_any(username, user_id, client_username)
        user_type = user_profile.get("type", "client")
        if user_type == "client":
            await client.send_message(
                user_id,
                "Görüşün, önerin veya şikayetin için teşekkürler! Destek ekibimize iletildi.",
            )
            log_analytics(client_username, "dm_client_feedback", {"feedback": message_text})

# 💳 Inline bankadan seçim sonrası
async def handle_inline_bank_choice(event):
    try:
        # Önce cache'den dene
        sender = event.sender
        if sender is None:
            try:
                sender = await event.get_sender()
            except Exception as e:
                log_event("unknown_bot", f"❌ Inline bank choice API hatası: {e}")
                return
        if sender is None:
            log_event("unknown_bot", "❌ Inline bank choice sender None geldi")
            return
        user_id = sender.id
        username = sender.username or str(user_id)
    except Exception as e:
        log_event("unknown_bot", f"❌ Inline bank choice sender hatası: {e}")
        return
    data = event.data.decode("utf-8")

    if data.startswith("bank_"):
        bank_name = data.split("bank_")[1]
        try:
            profile = load_profile(username)
            banks_data = load_banks()
            message = generate_payment_message(bank_name, profile, banks_data)
            await event.respond(message, parse_mode="markdown")
            log_analytics(username, "inline_bank_choice_success", {"bank": bank_name})
        except Exception as e:
            await event.respond("❌ Ödeme bilgisi alınırken hata oluştu.")
            log_event(username, f"❌ Banka inline hatası: {str(e)}")
            log_analytics(username, "inline_bank_choice_error", {"error": str(e)})

async def setup_dm_handlers(client, username):
    """DM handler'ları setup et"""
    from telethon import events
    
    try:
        # DM mesaj handler'ı
        @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
        async def dm_message_handler(event):
            try:
                await handle_message(client, event.sender, event.text or "", None)
            except Exception as e:
                log_event(username, f"❌ DM handler hatası: {e}")
        
        # Inline button handler'ı
        @client.on(events.CallbackQuery(pattern=b"bank_"))
        async def bank_button_handler(event):
            try:
                await handle_inline_bank_choice(event)
            except Exception as e:
                log_event(username, f"❌ Bank button handler hatası: {e}")
        
        # DM cooldown temizleme task'ını başlat
        asyncio.create_task(dm_cooldown_cleanup_task())
        
        log_event(username, "✅ DM handler'lar kuruldu")
        
    except Exception as e:
        log_event(username, f"❌ DM handler kurulum hatası: {e}")
