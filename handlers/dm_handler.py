from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
📱 DM Handler - Özel mesaj yönetimi
"""
from telethon import events
from core.controller import Controller

import structlog
import time
from utilities.redis_client import set_state, get_state, delete_state
from handlers.gpt_messaging_handler import gpt_messaging_handler
from handlers.safe_spam_handler import safe_spam_handler

logger = structlog.get_logger("gavatcore.dm_handler")

# Cooldown ayarları
DM_COOLDOWN_SECONDS = 300  # 5 dakika
DM_MAX_MESSAGES_PER_HOUR = 3
DM_TRACKING_WINDOW = 3600  # 1 saat

# Cooldown takibi
dm_cooldowns = {}  # {user_id: last_message_time}
dm_message_counts = {}  # {user_id: [timestamps]}

dm_conversation_state = {}

VIP_INTEREST_KEYWORDS = [
    "vip", "özel", "premium", "grup", "kanal", "exclusive",
    "katıl", "üye", "membership", "ilginç", "merak"
]

PAYMENT_KEYWORDS = [
    "ödeme", "payment", "fiyat", "price", "ücret", "fee",
    "satın al", "buy", "purchase", "kredi kartı", "credit card",
    "havale", "eft", "transfer", "banka", "bank"
]

dm_cooldown_cleanup_task = None  # Testler için placeholder

vip_interested_users = set()

class DMHandler:
    def __init__(self, controller: Controller):
        self.controller = controller
        
    async def handle_dm(self, event: events.NewMessage.Event):
        """Özel mesajları işle"""
        try:
            # Mesaj içeriğini al
            message = event.message.text
            
            # Komut kontrolü
            if message.startswith('/'):
                await self.handle_command(event)
                return
                
            # Normal mesaj işleme
            await self.process_message(event)
            
        except Exception as e:
            print(f"DM Handler Error: {e}")
            
    async def handle_command(self, event: events.NewMessage.Event):
        """Komutları işle"""
        try:
            # Komut işleme mantığı
            pass
        except Exception as e:
            print(f"Command Handler Error: {e}")
            
    async def process_message(self, event: events.NewMessage.Event):
        """Normal mesajları işle"""
        try:
            # Mesaj işleme mantığı
            pass
        except Exception as e:
            print(f"Message Processing Error: {e}")

    async def handle_message(self, user_id: int, message: str) -> str:
        """Kullanıcı mesajını işler ve yanıt döndürür."""
        try:
            # Spam kontrolü
            if not await safe_spam_handler(message, user_id):
                return "Spam tespit edildi. Lütfen uygun mesajlar gönderin."
            
            # Cooldown kontrolü
            can_send, reason = await check_dm_cooldown(user_id)
            if not can_send:
                return reason
            
            # VIP ilgi kontrolü
            await update_vip_interest(user_id, message)
            
            # Konuşma durumunu güncelle
            await update_conversation_state(user_id, message)
            
            # Otomatik menü kontrolü
            if await should_send_auto_menu(user_id, message):
                return "Menü seçenekleri:\n1. Yardım\n2. Bilgi\n3. Destek"
            
            # GPT yanıtı oluştur
            return await gpt_messaging_handler(message)
            
        except Exception as e:
            logger.error(f"Mesaj işleme hatası: {e}")
            return "Bir hata oluştu. Lütfen daha sonra tekrar deneyin."

    async def handle_inline_bank_choice(self, choice: str) -> str:
        """Inline banka seçimini işler."""
        try:
            if choice == "1":
                return "Banka 1 seçildi."
            elif choice == "2":
                return "Banka 2 seçildi."
            else:
                return "Geçersiz seçim."
        except Exception as e:
            logger.error(f"Banka seçimi hatası: {e}")
            return "Bir hata oluştu."

    async def _load_bot_profile(self) -> dict:
        """Bot profilini yükler."""
        try:
            # Örnek profil
            return {
                "name": "GavatBot",
                "version": "1.0",
                "status": "active"
            }
        except Exception as e:
            logger.error(f"Profil yükleme hatası: {e}")
            return {}

    async def _load_profile_any(self) -> dict:
        """Herhangi bir profil yüklemeyi dener."""
        try:
            profile = await self._load_bot_profile()
            if profile:
                return profile
            return {
                "name": "DefaultBot",
                "version": "1.0",
                "status": "active"
            }
        except Exception as e:
            logger.error(f"Profil yükleme hatası: {e}")
            return {}

async def update_conversation_state(user_id: int, message: str = None, is_bot: bool = False) -> dict:
    """
    Konuşma durumunu günceller
    
    Args:
        user_id (int): Kullanıcı ID'si
        message (str, optional): Mesaj içeriği
        is_bot (bool): Bot mesajı mı?
        
    Returns:
        dict: Güncel konuşma durumu
    """
    try:
        # Redis'ten mevcut durumu al
        state_key = f"conv:{user_id}"
        current_state = await get_state(state_key) or {}
        
        # Yeni durum
        new_state = {
            "last_message": message,
            "last_message_time": time.time(),
            "is_bot": is_bot,
            "message_count": current_state.get("message_count", 0) + 1
        }
        
        # Redis'e kaydet
        await set_state(state_key, new_state)
        
        return new_state
        
    except Exception as e:
        logger.error(f"Konuşma durumu güncelleme hatası: {e}")
        return {}

async def check_dm_cooldown(user_id: int) -> tuple[bool, str]:
    """
    DM cooldown kontrolü yapar
    
    Args:
        user_id (int): Kullanıcı ID'si
        
    Returns:
        tuple[bool, str]: (Mesaj gönderilebilir mi?, Sebep)
    """
    try:
        current_time = time.time()
        
        # Son mesaj zamanını kontrol et
        last_message_time = dm_cooldowns.get(user_id, 0)
        if current_time - last_message_time < DM_COOLDOWN_SECONDS:
            remaining = int(DM_COOLDOWN_SECONDS - (current_time - last_message_time))
            return False, f"Lütfen {remaining} saniye bekleyin"
            
        # Saatlik mesaj limitini kontrol et
        user_messages = dm_message_counts.get(user_id, [])
        # Son 1 saatteki mesajları filtrele
        recent_messages = [t for t in user_messages if current_time - t < DM_TRACKING_WINDOW]
        
        if len(recent_messages) >= DM_MAX_MESSAGES_PER_HOUR:
            return False, "Saatlik mesaj limitine ulaştınız"
            
        return True, ""
        
    except Exception as e:
        logger.error(f"Cooldown kontrolü hatası: {e}")
        return False, "Sistem hatası"

async def check_vip_interest(message: str) -> bool:
    """
    VIP ilgi kelimelerini kontrol eder
    
    Args:
        message (str): Kontrol edilecek mesaj
        
    Returns:
        bool: VIP ilgi varsa True
    """
    try:
        # Mesajı küçük harfe çevir
        message_lower = message.lower()
        
        # VIP kelimelerini kontrol et
        for keyword in VIP_INTEREST_KEYWORDS:
            if keyword in message_lower:
                return True
                
        return False
        
    except Exception as e:
        logger.error(f"VIP ilgi kontrolü hatası: {e}")
        return False

async def should_send_auto_menu(user_id: int, message: str) -> bool:
    """
    Otomatik menü gönderilip gönderilmeyeceğini kontrol eder
    
    Args:
        user_id (int): Kullanıcı ID'si
        message (str): Mesaj içeriği
        
    Returns:
        bool: Menü gönderilmeli mi?
    """
    try:
        # Son konuşma durumunu al
        state = await get_state(f"conv:{user_id}") or {}
        
        # İlk mesaj ise menü gönder
        if not state.get("message_count"):
            return True
            
        # Menü kelimeleri
        menu_keywords = ["menü", "menu", "komutlar", "yardım", "help"]
        
        # Mesajı küçük harfe çevir
        message_lower = message.lower()
        
        # Menü kelimelerini kontrol et
        for keyword in menu_keywords:
            if keyword in message_lower:
                return True
                
        return False
        
    except Exception as e:
        logger.error(f"Menü kontrolü hatası: {e}")
        return False

async def update_dm_cooldown(user_id: int):
    """
    DM cooldown'ı günceller
    
    Args:
        user_id (int): Kullanıcı ID'si
    """
    try:
        current_time = time.time()
        
        # Son mesaj zamanını güncelle
        dm_cooldowns[user_id] = current_time
        
        # Mesaj sayısını güncelle
        if user_id not in dm_message_counts:
            dm_message_counts[user_id] = []
        dm_message_counts[user_id].append(current_time)
        
        # Eski mesajları temizle
        dm_message_counts[user_id] = [
            t for t in dm_message_counts[user_id]
            if current_time - t < DM_TRACKING_WINDOW
        ]
        
    except Exception as e:
        logger.error(f"Cooldown güncelleme hatası: {e}")

async def check_payment_intent(message: str) -> bool:
    """
    Ödeme niyeti olup olmadığını kontrol eder
    
    Args:
        message (str): Kontrol edilecek mesaj
        
    Returns:
        bool: Ödeme niyeti varsa True
    """
    try:
        # Ödeme kelimeleri
        payment_keywords = [
            "ödeme", "payment", "fiyat", "price", "ücret", "fee",
            "satın al", "buy", "purchase", "kredi kartı", "credit card",
            "havale", "eft", "transfer", "banka", "bank"
        ]
        
        # Mesajı küçük harfe çevir
        message_lower = message.lower()
        
        # Ödeme kelimelerini kontrol et
        for keyword in payment_keywords:
            if keyword in message_lower:
                return True
                
        return False
        
    except Exception as e:
        logger.error(f"Ödeme niyeti kontrolü hatası: {e}")
        return False

async def cleanup_dm_cooldowns():
    """DM cooldownlarını periyodik olarak temizler."""
    import asyncio
    while True:
        current_time = time.time()
        to_delete = [user_id for user_id, t in dm_cooldowns.items() if current_time - t > DM_TRACKING_WINDOW]
        for user_id in to_delete:
            del dm_cooldowns[user_id]
            if user_id in dm_message_counts:
                del dm_message_counts[user_id]
        await asyncio.sleep(600)  # 10 dakikada bir temizle

async def update_vip_interest(user_id: int, message: str) -> bool:
    """Kullanıcının VIP ilgisini günceller."""
    try:
        if await check_vip_interest(message):
            state = await get_state(f"conv:{user_id}") or {}
            state["vip_interested"] = True
            await set_state(f"conv:{user_id}", state)
            return True
        return False
    except Exception as e:
        logger.error(f"VIP ilgi güncelleme hatası: {e}")
        return False

async def should_send_followup(user_id: int, message: str) -> bool:
    """Kullanıcıya takip mesajı gönderilmeli mi kontrol eder."""
    try:
        state = await get_state(f"conv:{user_id}") or {}
        # Eğer VIP ilgisi varsa ve henüz takip mesajı gönderilmediyse
        if state.get("vip_interested") and not state.get("followup_sent"):
            return True
        return False
    except Exception as e:
        logger.error(f"Takip mesajı kontrol hatası: {e}")
        return False

async def get_vip_interest_stage(user_id: int) -> str:
    """Kullanıcının VIP ilgi aşamasını döndürür."""
    try:
        state = await get_state(f"conv:{user_id}") or {}
        if state.get("vip_interested"):
            return "interested"
        return "not_interested"
    except Exception as e:
        logger.error(f"VIP ilgi aşaması kontrolü hatası: {e}")
        return "unknown"

async def get_conversation_state(user_id: int) -> dict:
    """Kullanıcının konuşma durumunu döndürür."""
    try:
        state_key = f"conv:{user_id}"
        return await get_state(state_key) or {}
    except Exception as e:
        logger.error(f"Konuşma durumu alma hatası: {e}")
        return {}

import asyncio

async def schedule_followup_message(user_id: int, message: str, delay: int = 60):
    """Takip mesajını belirli bir gecikmeyle planlar."""
    await asyncio.sleep(delay)
    # Burada gerçek takip mesajı gönderme mantığı olmalı
    logger.info(f"Takip mesajı gönderildi: {user_id} - {message}")

async def send_auto_menu(user_id: int) -> str:
    """Otomatik menü mesajını gönderir."""
    try:
        menu_message = "Menü seçenekleri:\n1. Yardım\n2. Bilgi\n3. Destek"
        # Burada gerçek mesaj gönderme mantığı olmalı
        logger.info(f"Otomatik menü gönderildi: {user_id}")
        return menu_message
    except Exception as e:
        logger.error(f"Otomatik menü gönderme hatası: {e}")
        return "Menü gönderilemedi."

# Global instance
dm_handler = DMHandler(Controller())

# Modül seviyesinde dışa aktarım
def handle_message(user_id: int, message: str) -> str:
    """Kullanıcı mesajını işler ve yanıt döndürür."""
    return dm_handler.handle_message(user_id, message)

async def handle_vip_sales_funnel(user_id: int, message: str) -> str:
    """VIP satış hunisi akışını yönetir."""
    try:
        # VIP ilgi kontrolü
        await update_vip_interest(user_id, message)
        # VIP aşamasını al
        stage = await get_vip_interest_stage(user_id)
        if stage == "interested":
            return "VIP teklifimizle ilgilendiğiniz için teşekkürler! Size özel fırsatlarımızı ileteceğiz."
        return "VIP teklifimizle ilgileniyorsanız lütfen 'VIP' yazın."
    except Exception as e:
        logger.error(f"VIP satış hunisi hatası: {e}")
        return "Bir hata oluştu."

def handle_inline_bank_choice(choice: str) -> str:
    """Inline banka seçimini işler."""
    return dm_handler.handle_inline_bank_choice(choice)

async def _load_profile_any() -> dict:
    """Herhangi bir profil yüklemeyi dener."""
    return await dm_handler._load_profile_any()

async def _load_bot_profile() -> dict:
    return await dm_handler._load_bot_profile()

def start_dm_cooldown_cleanup_task():
    import asyncio
    global dm_cooldown_cleanup_task
    dm_cooldown_cleanup_task = asyncio.create_task(cleanup_dm_cooldowns())

def setup_dm_handlers(client):
    """DM handler'ları Telegram client'a kaydeder."""
    # Burada gerçek event handler kaydı yapılmalı
    # Örnek: client.add_event_handler(...)
    logger.info("DM handler'lar kaydedildi.") 