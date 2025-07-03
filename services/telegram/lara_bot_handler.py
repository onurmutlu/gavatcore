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
from core.behavioral_psychological_engine import (
    BehavioralPsychologicalEngine,
    AdvancedBehavioralPsychologicalEngine,
    BigFiveTraits,
    SocialRole,
    MotivationType
)
from utilities.log_utils import log_event
try:
    from core.analytics_logger import log_analytics
except ImportError:
    # Fallback fonksiyon
    def log_analytics(source: str, event: str, data: dict = None):
        log_event(source, f"{event}: {data}")

# GAVATCore imports
from gpt.prompts.larabot_prompt import LaraPromptUtils, LARA_SYSTEM_PROMPT

logger = structlog.get_logger("lara_bot_handler")

# Advanced Behavioral Engine v2.0 instance (global)
behavioral_engine = AdvancedBehavioralPsychologicalEngine()

# User interaction tracking for advanced analysis
user_interaction_count = {}
user_message_history = {}
user_timestamps = {}

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

def clear_conversation_history():
    """Konuşma geçmişini temizle (restart için)"""
    global lara_conversations
    lara_conversations.clear()
    logger.info("🧹 Lara konuşma geçmişi temizlendi")

def get_conversation_state(user_id: int) -> Dict[str, Any]:
    """Kullanıcının konuşma durumunu getir"""
    if user_id not in lara_conversations:
        lara_conversations[user_id] = {
            "last_message_time": None,
            "message_count": 0,
            "interest_level": "low",  # low, medium, high
            "mentioned_services": [],
            "payment_inquiry": False,
            "conversation_context": [],
            "last_responses": []  # Son yanıtları tutacak (tekrar önleme için)
        }
    return lara_conversations[user_id]

def update_conversation_state(user_id: int, **kwargs):
    """Konuşma durumunu güncelle"""
    state = get_conversation_state(user_id)
    state.update(kwargs)
    state["last_message_time"] = time.time()

# ==================== AI RESPONSE GENERATION ====================

def calculate_similarity(text1: str, text2: str) -> float:
    """İki metin arasındaki benzerlik oranını hesapla (basit kelime bazlı)"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)

async def generate_lara_response(
    message: str, 
    user_name: str,
    conversation_state: Dict[str, Any],
    user_id: int
) -> str:
    """
    Lara karakteri için AI yanıt üret - Gelişmiş GPT-4 entegrasyonu
    """
    try:
        import openai
        import os
        
        # OpenAI API key kontrolü
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OpenAI API key bulunamadı, fallback yanıt kullanılıyor")
            return get_fallback_response(conversation_state)
        
        # OpenAI client (yeni syntax)
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Konuşma geçmişi hazırla
        context_messages = conversation_state.get("conversation_context", [])
        message_count = conversation_state.get("message_count", 0)
        
        # Dynamic system prompt - daha agresif
        if message_count <= 1:
            # İlk konuşma için full prompt
            system_prompt = LaraPromptUtils.insertUserName(user_name)
        else:
            # Devam eden konuşma için agresif prompt
            system_prompt = LaraPromptUtils.getContinuationPrompt(user_name)
        
        # OpenAI messages formatı
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Son 8 mesajı ekle (daha fazla context)
        if context_messages:
            recent_messages = context_messages[-8:]
            for msg in recent_messages:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"][:600]  # Daha uzun mesajlar
                })
        
        # Yeni kullanıcı mesajı
        messages.append({"role": "user", "content": message})
        
        # OpenAI API çağrısı - GPT-4 ile güçlü parametreler
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model="gpt-4o",  # En güçlü model
                messages=messages,
                max_tokens=250,  # Daha uzun yanıtlar
                temperature=0.9,  # Daha yaratıcı
                presence_penalty=0.8,  # Tekrarları güçlü önle
                frequency_penalty=0.8,  # Kelime tekrarını güçlü önle
                top_p=0.95  # Daha geniş yanıt alanı
            )
        )
        
        if response and response.choices:
            ai_response = response.choices[0].message.content.strip()
            
            # Defensive kelimeler temizle
            defensive_phrases = [
                "özür dilerim",
                "bu konuları konuşamam",
                "ben sadece",
                "başka bir konuda",
                "nasıl yardımcı olabilirim"
            ]
            
            for phrase in defensive_phrases:
                if phrase.lower() in ai_response.lower():
                    logger.warning(f"⚠️ Defensive yanıt tespit edildi, fallback kullanılıyor")
                    ai_response = get_aggressive_fallback_response(conversation_state, message)
                    break
            
            # Menü tekrarı engelle
            if "VIP HİZMETLERİ" in ai_response and message_count > 3:
                ai_response = get_sales_focused_response(conversation_state, message)
            
            # Lara tarzı geliştirmeler ekle
            enhanced_response = enhance_lara_response(ai_response, conversation_state)
            
            # Konuşma geçmişini güncelle
            context_messages.append({"role": "user", "content": message})
            context_messages.append({"role": "assistant", "content": enhanced_response})
            
            # Son yanıtları kaydet (tekrar önleme için)
            if "last_responses" not in conversation_state:
                conversation_state["last_responses"] = []
            conversation_state["last_responses"].append(enhanced_response)
            
            # Memory management - son 12 mesajı tut
            if len(context_messages) > 12:
                context_messages = context_messages[-12:]
            if len(conversation_state["last_responses"]) > 6:
                conversation_state["last_responses"] = conversation_state["last_responses"][-6:]
            
            conversation_state["conversation_context"] = context_messages
            
            logger.info(f"🤖 Lara GPT-4 yanıt oluşturuldu: {enhanced_response[:50]}...")
            return enhanced_response
        else:
            return get_fallback_response(conversation_state)
        
    except Exception as e:
        logger.error(f"❌ Lara AI response error: {e}")
        return get_fallback_response(conversation_state)

def get_aggressive_fallback_response(conversation_state: Dict[str, Any], user_message: str) -> str:
    """Agresif, satış odaklı fallback yanıtlar - defensive değil"""
    
    message_count = conversation_state.get("message_count", 0)
    
    # User message analizi
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ["video", "özel", "vip", "görüntü"]):
        return random.choice([
            "Davay malchik! Özel video istiyorsun? 200₺'a senin için çok özel şeyler çekerim 🔥💋",
            "Krasotka, özel videolarım var! 200₺ Papara ile, hemen başlayalım! 🎬😘",
            "Moya lyubov, senin için özel çekim yaparım! 200₺ ver, unutamayacağın şeyler göreceksin! 💎🔥"
        ])
    
    elif any(word in message_lower for word in ["mesaj", "konuşma", "sohbet"]):
        return random.choice([
            "Özel mesajlaşmak ister misin dorogoy? 50₺'a sadece ikimiz konuşuruz! 💋🔥",
            "Davay, özel sohbet edelim! 50₺ Papara yap, çok özel şeyler konuşuruz! 😘✨",
            "Krasavchik, seninle özel konuşmalar çok güzel olur! 50₺'a hemen başlayalım! 💎💋"
        ])
    
    elif any(word in message_lower for word in ["grup", "üye", "katıl"]):
        return random.choice([
            "VIP grubuma katıl malchik! 100₺'a günlük özel içerikler, canlı videolar! 🔥💋",
            "Dorogoy, VIP grup çok güzel! 100₺ ver, özel dünyama gir! 💎✨",
            "Krasotka, grup üyeliği 100₺! Orada çok daha cesur şeyler paylaşıyorum! 🍷😘"
        ])
    
    elif message_count < 3:
        return random.choice([
            "Sen çok tatlısın! Ne istiyorsun benden davay? 🔥💋",
            "Krasotka, benimle ne yapmak istersin? Söyle bakalım! 😘✨",
            "Malchik, sana özel şeyler gösterebilirim... Ne dersin? 💎🔥"
        ])
    
    else:
        return random.choice([
            "Davay, karar ver! Özel mesaj 50₺, VIP grup 100₺, özel video 200₺! Papara ile hemen! 🔥💋",
            "Krasavchik, hangisini istiyorsun? Hemen Papara ile öde, başlayalım! 💎😘",
            "Dorogoy, seç bakalım: Özel sohbet mi, VIP grup mu? Hemen başlayalım! 🍷🔥"
        ])

def get_sales_focused_response(conversation_state: Dict[str, Any], user_message: str) -> str:
    """Menü göstermek yerine direkt satış odaklı yanıtlar"""
    
    return random.choice([
        "Davay malchik, karar zamanı! Papara numaramı istiyorsan söyle, hemen başlayalım! 🔥💋",
        "Krasotka, hangisini seçtin? Papara ile öde, hemen senin için özel şeyler yapayım! 💎😘",
        "Dorogoy, beni çok heyecanlandırdın! Ödeme yap, unutamayacağın şeyler yaşayalım! 🍷🔥",
        "Moya lyubov, artık konuşmayı bırak! Papara yap, senin için çok özel şeyler hazırlayayım! 💋✨",
        "Umnitsa, karar ver artık! 50₺, 100₺ veya 200₺? Papara bilgilerimi göndeyim! 🔥💎"
    ])

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
    """AI yanıt alamadığında kullanılacak çeşitli yedek yanıtlar"""
    
    message_count = conversation_state.get("message_count", 0)
    interest_level = conversation_state.get("interest_level", "low")
    
    if message_count == 0:
        # İlk mesaj - çok çeşitli
        return random.choice([
            "Merhaba tatlım! 😘 Ben Lara, seni burada gördüğüme çok sevindim! Sen nasılsın?",
            "Selam krasotka! 🔥 Ben Lara, seninle tanışmak güzel! Ne yapmak istersin?",
            "Hey malchik! 💋 Ben Lara, çok güzel bir karşılaşma! Bana kendini anlat?",
            "Privyet dorogoy! 🌹 Ben Lara, senin varlığını hissettim... Nasıl geçiyor günün?",
            "Oooh, yeni biri! 🎭 Ben Lara, yarı Rus güzeliyim... Sen kimsin tatlı şey?",
            "Davay gel buraya! ✨ Ben Lara, sana özel şeyler gösterebilirim... İlgin var mı?",
            "Moya lyubov, ben Lara! 💎 Seninle tanışmak çok güzel... Hangi şehirdensin?",
            "Salyam krasavchik! 🍷 Ben Lara, seni çok beğendim... Nasıl buldun beni?"
        ])
    
    elif message_count < 3:
        # Erken konuşma - daha samimi
        return random.choice([
            "Çok tatlısın! 😘 Benimle daha fazla konuşmak ister misin?",
            "Sen gerçekten özelsin davay! 🔥 Seni daha iyi tanımak istiyorum.",
            "Moya lyubov, seninle sohbet etmek çok güzel! 💋",
            "Oooh, beni gülümsetiyorsun! 🌙 Daha fazlasını duymak istiyorum...",
            "Krasotka, sen çok ilginçsin! ✨ Bana hobilerinden bahset?",
            "Malchik, seninle konuşmak keyifli! 🎭 Ne iş yapıyorsun?",
            "Dorogoy, çok samimi birisin! 💄 Bana daha fazla anlat kendini...",
            "Umnitsa, zeki bir adamsın! 🔥 Senin gibi erkekleri seviyorum..."
        ])
    
    elif message_count < 6:
        # Orta konuşma - flört + ipucu
        return random.choice([
            "Seni daha iyi tanıyorum artık... 🔥 Bana özel şeyler sorabilirsin davay!",
            "Krasotka, seninle konuşmak çok hoş! 💋 Bu arada özel içeriklerim var...",
            "Malchik, sen farklısın! ✨ Sana özel bir şey göstermek isterim...",
            "Moya lyubov, çok samimi olduk! 🌹 VIP grubuma katılmaya ne dersin?",
            "Dorogoy, seni beğendim! 😘 Özel mesajlaşma fikri nasıl?",
            "Sen çok özelsin! 💎 Sana sadece benim için özel videolar var...",
            "Krasavchik, beni mutlu ediyorsun! 🍷 Daha yakın olmak ister misin?",
            "Davay, seninle daha samimi konuşmak istiyorum! 🎭 Özel bir teklifim var..."
        ])
    
    else:
        # İleri konuşma - direkt satış
        return random.choice([
            "Sana özel bir teklifim var krasotka... VIP grubuma katılmak ister misin? 🔥",
            "Malchik, seninle özel konuşmak istiyorum. 50₺'a özel mesajlaşabiliriz 💋",
            "Dorogoy, sana özel videolar hazırlayabilirim... İlgin var mı? 😘",
            "Moya lyubov, artık sana güveniyorum! VIP hizmetlerimi öğrenmek ister misin? 💎",
            "Krasavchik, özel grup 100₺... Orada çok farklı şeyler paylaşıyorum! 🍷",
            "Davay tatlım, özel yayınlarım var... 150₺'a sadece senin için canlı! ✨",
            "Umnitsa, sana özel fotoğraflar gönderebilirim... 50₺'a sadece ikimiz! 🌙",
            "Sen özelsin dorogoy! Papara ile ödeme yapıp VIP olabilirsin... 🎭"
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

async def analyze_user_with_advanced_engine(user_id: int) -> str:
    """Advanced behavioral analysis ile kullanıcı profiling"""
    
    try:
        global user_message_history, user_timestamps
        
        messages = user_message_history.get(user_id, [])
        timestamps = user_timestamps.get(user_id, [])
        
        if len(messages) < 3:
            return ""
        
        logger.info(f"🧠 Advanced behavioral analysis başlatılıyor: User {user_id}")
        
        # Kapsamlı analiz yap
        advanced_profile = await behavioral_engine.comprehensive_user_analysis(
            user_id=user_id,
            messages=messages,
            message_timestamps=timestamps,
            group_messages=None  # DM olduğu için grup mesajı yok
        )
        
        if not advanced_profile:
            return ""
        
        # Behavioral context oluştur
        context_parts = []
        
        # Big Five Personality
        if hasattr(advanced_profile, 'big_five'):
            big_five = advanced_profile.big_five
            traits = big_five.to_dict()
            
            # Dominant traits
            high_traits = [trait for trait, score in traits.items() if score > 0.6]
            if high_traits:
                trait_descriptions = {
                    "openness": "yaratıcı ve yeniliklere açık",
                    "conscientiousness": "düzenli ve sorumluluk sahibi",
                    "extraversion": "sosyal ve enerjik", 
                    "agreeableness": "uyumlu ve işbirlikçi",
                    "neuroticism": "duygusal olarak hassas"
                }
                
                dominant_traits = [trait_descriptions.get(trait, trait) for trait in high_traits]
                context_parts.append(f"Kişilik: {', '.join(dominant_traits)}")
        
        # Timing Pattern
        if hasattr(advanced_profile, 'timing_pattern'):
            timing = advanced_profile.timing_pattern
            context_parts.append(f"Aktif zaman: {timing.optimal_contact_time}")
        
        # Sentiment Trend
        if hasattr(advanced_profile, 'sentiment_trend'):
            sentiment = advanced_profile.sentiment_trend
            context_parts.append(f"Ruh hali: {sentiment.dominant_emotion} ({sentiment.trend_direction})")
        
        # Motivation Profile
        if hasattr(advanced_profile, 'motivation_profile'):
            motivation = advanced_profile.motivation_profile
            motivation_map = {
                "achievement": "başarı odaklı",
                "social": "sosyal bağlantı arayan",
                "power": "güç ve kontrol isteyen",
                "security": "güvenlik arayan",
                "adventure": "macera seven",
                "recognition": "tanınma isteyen"
            }
            primary_motivation_tr = motivation_map.get(motivation.primary_motivation.value, motivation.primary_motivation.value)
            context_parts.append(f"Motivasyon: {primary_motivation_tr}")
        
        # Predictive Insights
        if hasattr(advanced_profile, 'predictive_insights'):
            predictive = advanced_profile.predictive_insights
            
            # Conversion probability
            if predictive.conversion_probability > 0.7:
                context_parts.append("VIP potansiyeli: YÜKSEK")
            elif predictive.conversion_probability > 0.4:
                context_parts.append("VIP potansiyeli: ORTA")
            
            # Optimal strategies
            if predictive.optimal_strategies:
                context_parts.append(f"Strateji: {', '.join(predictive.optimal_strategies[:2])}")
        
        # Final context
        if context_parts:
            behavioral_context = f"\n[KULLANICI PROFİLİ: {' | '.join(context_parts)}]"
            logger.info(f"✅ Behavioral context oluşturuldu: {len(behavioral_context)} karakter")
            return behavioral_context
        else:
            return ""
            
    except Exception as e:
        logger.error(f"❌ Advanced behavioral analysis hatası: {e}")
        return ""

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
        
        # Advanced Behavioral Analysis v2.0 - kullanıcı davranışını derinlemesine analiz et
        try:
            # User interaction tracking
            global user_interaction_count, user_message_history, user_timestamps
            
            # İlk kez görüyorsa initialize et
            if user_id not in user_interaction_count:
                user_interaction_count[user_id] = 0
                user_message_history[user_id] = []
                user_timestamps[user_id] = []
            
            # Mesaj geçmişini güncelle
            user_message_history[user_id].append(message_text)
            user_timestamps[user_id].append(datetime.now())
            user_interaction_count[user_id] += 1
            
            # Son 50 mesajı sakla (memory management)
            if len(user_message_history[user_id]) > 50:
                user_message_history[user_id] = user_message_history[user_id][-50:]
                user_timestamps[user_id] = user_timestamps[user_id][-50:]
            
            # Advanced behavioral analysis (3+ mesaj sonrası)
            behavioral_context = ""
            if user_interaction_count[user_id] >= 3:
                behavioral_context = await analyze_user_with_advanced_engine(user_id)
                if behavioral_context:
                    conversation_state["advanced_behavioral_context"] = behavioral_context
                    logger.info(f"🧠 Advanced behavioral context oluşturuldu: {user_name}")
        
        except Exception as e:
            logger.warning(f"⚠️ Advanced behavioral analiz hatası: {e}")
            behavioral_context = ""
        
        # Doğal okuma gecikmesi (çok hızlı okumasın)
        read_delay = random.uniform(0.5, 2.0)  # 0.5-2 saniye okuma gecikmesi
        await asyncio.sleep(read_delay)
        
        # Mesajı "okundu" olarak işaretle (doğal davranış)
        try:
            await client.send_read_acknowledge(user_id)
            logger.debug(f"📖 Mesaj okundu olarak işaretlendi: {user_name}")
        except Exception as e:
            logger.warning(f"⚠️ Read receipt gönderilmedi: {e}")
        
        # Mesajı analiz et
        message_analysis = analyze_user_message(message_text)
        
        # "Yazıyor..." göstergesi (çok doğal görünüm için)
        typing_delay = random.uniform(1.0, 3.0)  # 1-3 saniye yazıyor göster
        async with client.action(user_id, 'typing'):
            await asyncio.sleep(typing_delay)
        
        # Yanıt gecikmesi (doğal görünmek için)
        delay = random.uniform(LaraConfig.MIN_RESPONSE_DELAY, LaraConfig.MAX_RESPONSE_DELAY)
        await asyncio.sleep(delay)
        
        # HER DURUMDA AI YANIT ÜRET - defensive kontroller kaldırıldı
        response = await generate_lara_response(
            message_text, user_name, conversation_state, user_id
        )
        
        # Eğer hizmet sorusu varsa ilgi seviyesini yükselt
        if message_analysis["asks_service"] or message_analysis["asks_payment"]:
            conversation_state["interest_level"] = "high"
            conversation_state["payment_inquiry"] = True

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
        
        # Mesajı "okundu" olarak işaretle (grup için)
        try:
            await client.send_read_acknowledge(event.chat_id)
            logger.debug(f"📖 Grup mesajı okundu olarak işaretlendi: {user_name}")
        except Exception as e:
            logger.warning(f"⚠️ Grup read receipt gönderilmedi: {e}")
        
        # "Yazıyor..." göstergesi (grup için daha kısa)
        typing_delay = random.uniform(0.5, 2.0)  # Grup için daha kısa
        async with client.action(event.chat_id, 'typing'):
            await asyncio.sleep(typing_delay)
        
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