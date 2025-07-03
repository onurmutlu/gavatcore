#!/usr/bin/env python3
"""
LARA BOT HANDLER - Flörtöz Şovcu AI Sistemi
==========================================

Lara karakteri için özelleştirilmiş mesaj işleme ve yanıtlama sistemi.
GAVATCore alt yapısını kullanarak Lara promptu ile AI yanıtlar üretir.

Özellikler:
- Flörtöz ama profesyonel karakter
- Satış odaklı konuşma yönlendirme
- Rusça kelime entegrasyonu
- VIP hizmet tanıtımı
- Emoji kullanımı ve duygusal yanıtlar
"""

import asyncio
import random
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import structlog

# Core imports
from core.advanced_ai_manager import advanced_ai_manager, AITaskType, AIPriority
from core.user_analyzer import babagavat_user_analyzer
from utils.log_utils import log_event
try:
    from core.analytics_logger import log_analytics
except ImportError:
    # Fallback fonksiyon
    def log_analytics(source: str, event: str, data: dict = None):
        log_event(source, f"{event}: {data}")

# GAVATCore imports
from gpt.prompts.larabot_prompt import LaraPromptUtils, LARA_SYSTEM_PROMPT

logger = structlog.get_logger("lara_bot_handler")

# ==================== LARA BOT CONFIGURATION ====================

class LaraConfig:
    """Lara bot konfigürasyonu"""
    
    # Karakter ayarları
    MIN_RESPONSE_DELAY = 2.0    # Minimum yanıt gecikmesi (saniye)
    MAX_RESPONSE_DELAY = 5.0    # Maksimum yanıt gecikmesi (saniye)
    
    # Rusça kelimeler havuzu
    RUSSIAN_WORDS = [
        "davay", "moya lyubov", "krasotka", "malchik", 
        "dorogoy", "miliy", "sladkiy", "umnitsa"
    ]
    
    # Emoji havuzu
    LARA_EMOJIS = ["🔥", "💋", "😘", "🌹", "✨", "💄", "🎭", "💎", "🍷", "🌙"]
    
    # VIP hizmet fiyatları
    VIP_SERVICES = {
        "özel_mesaj": {"price": "50₺", "description": "Kişisel sohbet ve özel fotoğraflar"},
        "vip_grup": {"price": "100₺", "description": "VIP grup üyeliği, günlük özel içerik"},
        "özel_video": {"price": "200₺", "description": "Talep üzerine kişiselleştirilmiş video"},
        "canlı_yayın": {"price": "150₺", "description": "Telegram'da özel yayın"}
    }
    
    # Ödeme bilgileri
    PAPARA_INFO = {
        "papara_no": "1234567890",
        "iban": "TR12 3456 7890 1234 5678 9012 34",
        "hesap_sahibi": "Lara K."
    }

# ==================== CONVERSATION STATE MANAGEMENT ====================

# Kullanıcı konuşma durumları
lara_conversations: Dict[int, Dict[str, Any]] = {}

def get_conversation_state(user_id: int) -> Dict[str, Any]:
    """Kullanıcının konuşma durumunu getir"""
    if user_id not in lara_conversations:
        lara_conversations[user_id] = {
            "last_message_time": None,
            "message_count": 0,
            "interest_level": "low",  # low, medium, high
            "mentioned_services": [],
            "payment_inquiry": False,
            "conversation_context": []
        }
    return lara_conversations[user_id]

def update_conversation_state(user_id: int, **kwargs):
    """Konuşma durumunu güncelle"""
    state = get_conversation_state(user_id)
    state.update(kwargs)
    state["last_message_time"] = time.time()

# ==================== AI RESPONSE GENERATION ====================

async def generate_lara_response(
    message: str, 
    user_name: str,
    conversation_state: Dict[str, Any],
    user_id: int
) -> str:
    """
    Lara karakteri için AI yanıt üret
    
    Args:
        message: Kullanıcı mesajı
        user_name: Kullanıcı adı
        conversation_state: Konuşma durumu
        user_id: Kullanıcı ID'si
    
    Returns:
        Lara karakterinde yanıt
    """
    try:
        # Lara promptunu kullanıcı adı ile kişiselleştir
        system_prompt = LaraPromptUtils.insertUserName(user_name)
        
        # Konuşma geçmişini hazırla
        context_messages = conversation_state.get("conversation_context", [])
        
        # Son 10 mesajı dahil et (memory management)
        if len(context_messages) > 10:
            context_messages = context_messages[-10:]
        
        # Konuşma geçmişini prompt'a ekle
        context_text = ""
        if context_messages:
            context_text = "\n\nKonuşma geçmişi:\n"
            for msg in context_messages[-5:]:  # Son 5 mesaj
                context_text += f"- {msg['role']}: {msg['content'][:100]}...\n"
        
        full_prompt = system_prompt + context_text
        
        # OpenAI'dan yanıt al
        if advanced_ai_manager:
            # Advanced AI manager ile task submit et
            task_id = await advanced_ai_manager.submit_ai_task(
                task_type=AITaskType.CHARACTER_INTERACTION,
                user_id=str(user_id),
                prompt=full_prompt,
                context={"user_message": message, "character": "Lara"},
                character_id="lara",
                priority=AIPriority.HIGH
            )
            
            # Sonucu al
            ai_result = await advanced_ai_manager.get_task_result(task_id, wait_timeout=10.0)
            
            if ai_result and not ai_result.get("error"):
                # JSON formatındaki yanıttan metni çıkar
                if isinstance(ai_result, dict):
                    response = (
                        ai_result.get("response") or 
                        ai_result.get("message") or 
                        ai_result.get("content") or
                        str(ai_result)
                    )
                else:
                    response = str(ai_result)
            else:
                response = None
        else:
            response = None
        
        if not response:
            # Fallback yanıtları
            return get_fallback_response(conversation_state)
        
        # Yanıtı temizle ve Lara tarzı eklemeler yap
        enhanced_response = enhance_lara_response(response, conversation_state)
        
        # Konuşma geçmişini güncelle
        context_messages.append({"role": "user", "content": message})
        context_messages.append({"role": "assistant", "content": enhanced_response})
        
        conversation_state["conversation_context"] = context_messages
        
        return enhanced_response
        
    except Exception as e:
        logger.error(f"Lara response generation error: {e}")
        return get_fallback_response(conversation_state)

def enhance_lara_response(response: str, conversation_state: Dict[str, Any]) -> str:
    """Lara yanıtını geliştir - emoji, Rusça kelimeler, satış taktikleri ekle"""
    
    # Emoji ekleme kontrolü
    if not any(emoji in response for emoji in LaraConfig.LARA_EMOJIS):
        response += f" {random.choice(LaraConfig.LARA_EMOJIS)}"
    
    # Rusça kelime ekleme (bazen)
    if random.random() < 0.3:  # %30 şans
        russian_word = random.choice(LaraConfig.RUSSIAN_WORDS)
        response += f" {russian_word} 😘"
    
    # VIP hizmet tanıtımı ekleme (düşük mesaj sayısında)
    message_count = conversation_state.get("message_count", 0)
    if message_count >= 3 and message_count <= 6 and random.random() < 0.4:
        if "VIP" not in response and "özel" not in response:
            service_hint = random.choice([
                "\n\nBu arada, özel içeriklerim var... İlgin var mı? 🔥",
                "\n\nVIP grubuma katılmak ister misin? Özel şeyler paylaşıyorum 💋",
                "\n\nSeninle özel konuşmak isterim... 😘"
            ])
            response += service_hint
    
    return response

def get_fallback_response(conversation_state: Dict[str, Any]) -> str:
    """AI yanıt alamadığında kullanılacak yedek yanıtlar"""
    
    message_count = conversation_state.get("message_count", 0)
    
    if message_count == 0:
        # İlk mesaj
        return random.choice([
            "Merhaba tatlım! 😘 Ben Lara, seni burada gördüğüme çok sevindim! Sen nasılsın?",
            "Selam krasotka! 🔥 Ben Lara, seninle tanışmak güzel! Ne yapmak istersin?",
            "Hey malchik! 💋 Ben Lara, çok güzel bir karşılaşma! Bana kendini anlat?"
        ])
    
    elif message_count < 3:
        # Erken konuşma
        return random.choice([
            "Çok tatlısın! 😘 Benimle daha fazla konuşmak ister misin?",
            "Sen gerçekten özelsin davay! 🔥 Seni daha iyi tanımak istiyorum.",
            "Moya lyubov, seninle sohbet etmek çok güzel! 💋"
        ])
    
    else:
        # İleri konuşma - satış odaklı
        return random.choice([
            "Sana özel bir teklifim var... VIP grubuma katılmak ister misin? 🔥",
            "Krasotka, seninle özel konuşmak istiyorum. 50₺'a özel mesajlaşabiliriz 💋",
            "Dorogoy, sana özel videolar hazırlayabilirim... İlgin var mı? 😘"
        ])

# ==================== SERVICE PRESENTATION ====================

def get_service_menu() -> str:
    """VIP hizmet menüsünü getir"""
    menu = "💎 **LARA'NIN ÖZEL HİZMETLERİ** 💎\n\n"
    
    for service_key, service_info in LaraConfig.VIP_SERVICES.items():
        menu += f"🔥 **{service_key.replace('_', ' ').title()}** - {service_info['price']}\n"
        menu += f"   {service_info['description']}\n\n"
    
    menu += "💳 **Ödeme:** Papara / IBAN\n"
    menu += "📞 **İletişim:** Mesajla seçimini belirt!\n\n"
    menu += "Hangi hizmeti seçmek istersin moya lyubov? 😘"
    
    return menu

def get_payment_info() -> str:
    """Ödeme bilgilerini getir"""
    info = "💳 **ÖDEME BİLGİLERİ** 💳\n\n"
    info += f"📱 **Papara No:** {LaraConfig.PAPARA_INFO['papara_no']}\n"
    info += f"🏦 **IBAN:** {LaraConfig.PAPARA_INFO['iban']}\n"
    info += f"👤 **Hesap Sahibi:** {LaraConfig.PAPARA_INFO['hesap_sahibi']}\n\n"
    info += "💋 **Önemli:** Ödeme açıklamasına Telegram kullanıcı adını yazınız!\n"
    info += "⚡ Ödeme onaylandıktan sonra hemen hizmetiniz aktif olacak!\n\n"
    info += "Davay dorogoy, seni bekliyorum! 🔥"
    
    return info

# ==================== MESSAGE ANALYSIS ====================

def analyze_user_message(message: str) -> Dict[str, bool]:
    """Kullanıcı mesajını analiz et"""
    message_lower = message.lower()
    
    analysis = {
        "is_greeting": any(word in message_lower for word in ["merhaba", "selam", "hey", "hi"]),
        "is_flirty": any(word in message_lower for word in ["güzel", "tatlı", "seviyorum", "aşk"]),
        "asks_service": any(word in message_lower for word in ["hizmet", "vip", "özel", "video", "grup"]),
        "asks_price": any(word in message_lower for word in ["fiyat", "kaç", "para", "ücret", "ödeme"]),
        "asks_payment": any(word in message_lower for word in ["papara", "iban", "ödeme", "nasıl"]),
        "is_rejection": any(word in message_lower for word in ["istemiyorum", "hayır", "olmaz", "gerek"]),
        "is_rude": any(word in message_lower for word in ["aptal", "salak", "kötü", "rezil"])
    }
    
    return analysis

# ==================== MAIN HANDLER FUNCTIONS ====================

async def handle_lara_dm(client, sender, message_text: str) -> bool:
    """
    Lara bot için DM mesajlarını işle
    
    Args:
        client: Telegram client
        sender: Mesaj gönderen kullanıcı
        message_text: Mesaj içeriği
    
    Returns:
        Yanıt verildi mi
    """
    try:
        user_id = sender.id
        user_name = sender.first_name or sender.username or f"user_{user_id}"
        
        # Konuşma durumunu getir/güncelle
        conversation_state = get_conversation_state(user_id)
        conversation_state["message_count"] += 1
        
        # Mesajı analiz et
        message_analysis = analyze_user_message(message_text)
        
        # Yanıt gecikmesi (doğal görünmek için)
        delay = random.uniform(LaraConfig.MIN_RESPONSE_DELAY, LaraConfig.MAX_RESPONSE_DELAY)
        await asyncio.sleep(delay)
        
        # Özel durum kontrolü
        if message_analysis["is_rude"]:
            response = "Dorogoy, böyle konuşmaya gerek yok... Ben sadece güzel sohbet istiyorum 🌹"
        elif message_analysis["asks_service"]:
            response = get_service_menu()
            conversation_state["interest_level"] = "high"
        elif message_analysis["asks_payment"]:
            response = get_payment_info()
            conversation_state["payment_inquiry"] = True
        else:
            # Normal AI yanıt üret
            response = await generate_lara_response(
                message_text, user_name, conversation_state, user_id
            )
        
        # Yanıtı gönder
        await client.send_message(user_id, response)
        
        # Durum güncellemesi
        update_conversation_state(
            user_id,
            message_count=conversation_state["message_count"],
            interest_level=conversation_state.get("interest_level", "medium")
        )
        
        # Analytics log
        log_analytics("lara_bot", "dm_response_sent", {
            "user_id": user_id,
            "user_name": user_name,
            "message_length": len(message_text),
            "response_length": len(response),
            "message_analysis": message_analysis,
            "conversation_count": conversation_state["message_count"]
        })
        
        logger.info(f"🌹 Lara DM yanıtı gönderildi: {user_name} -> {response[:50]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"Lara DM handler error: {e}")
        return False

async def handle_lara_group_message(client, event, username: str) -> bool:
    """
    Lara bot için grup mesajlarını işle (mention/reply durumunda)
    
    Args:
        client: Telegram client
        event: Telegram event
        username: Bot kullanıcı adı
    
    Returns:
        Yanıt verildi mi
    """
    try:
        # Sadece mention veya reply durumunda yanıt ver
        if not (event.is_reply or f"@{username}" in event.raw_text.lower()):
            return False
        
        sender = event.sender
        if not sender:
            return False
        
        user_name = sender.first_name or sender.username or f"user_{sender.id}"
        
        # Grup yanıtları daha kısa ve flörtöz olsun
        group_responses = [
            f"Merhaba {user_name}! 😘 DM'den konuşalım mı tatlım?",
            f"Hey krasotka! 💋 Bana özel mesaj at, seni bekliyorum!",
            f"Davay {user_name}! 🔥 DM'de daha güzel sohbet ederiz!",
            f"Selam dorogoy! 💎 Özelde konuşmak ister misin?"
        ]
        
        response = random.choice(group_responses)
        
        # Yanıt gecikmesi
        await asyncio.sleep(random.uniform(1.0, 3.0))
        
        await event.reply(response)
        
        # Analytics
        log_analytics("lara_bot", "group_mention_response", {
            "chat_id": event.chat_id,
            "user_id": sender.id,
            "user_name": user_name,
            "message": event.raw_text[:100]
        })
        
        logger.info(f"🌹 Lara grup yanıtı: {user_name} -> {response}")
        
        return True
        
    except Exception as e:
        logger.error(f"Lara group handler error: {e}")
        return False

# ==================== CONVERSATION ANALYTICS ====================

def get_lara_stats() -> Dict[str, Any]:
    """Lara bot istatistiklerini getir"""
    stats = {
        "total_conversations": len(lara_conversations),
        "active_conversations": 0,
        "high_interest_users": 0,
        "payment_inquiries": 0,
        "average_message_count": 0
    }
    
    if lara_conversations:
        total_messages = 0
        current_time = time.time()
        
        for user_id, state in lara_conversations.items():
            total_messages += state.get("message_count", 0)
            
            # Son 24 saatte aktif olan
            last_message = state.get("last_message_time")
            if last_message and (current_time - last_message) < 86400:  # 24 saat
                stats["active_conversations"] += 1
            
            # Yüksek ilgi
            if state.get("interest_level") == "high":
                stats["high_interest_users"] += 1
            
            # Ödeme sorgusu
            if state.get("payment_inquiry"):
                stats["payment_inquiries"] += 1
        
        stats["average_message_count"] = total_messages / len(lara_conversations)
    
    return stats

# ==================== EXPORT FUNCTIONS ====================

__all__ = [
    "handle_lara_dm",
    "handle_lara_group_message", 
    "get_lara_stats",
    "LaraConfig"
] 