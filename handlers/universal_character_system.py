#!/usr/bin/env python3
"""
UNIVERSAL CHARACTER SYSTEM - Genel Karakter Framework'ü
======================================================

Tüm AI karakterleri için genişletilebilir sistem.
Lara, Geisha, BabaGavat gibi tüm karakterler bu sistem üzerinden çalışabilir.

Özellikler:
- Karakter tipi bazlı prompt yönetimi
- Modüler handler sistemi
- Dynamic konfigürasyon
- Entegrasyon desteği
- Analytics ve monitoring
"""

import asyncio
import random
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, asdict
import structlog

# Core imports
from core.advanced_ai_manager import advanced_ai_manager, AITaskType, AIPriority
from utils.log_utils import log_event
try:
    from core.analytics_logger import log_analytics
except ImportError:
    def log_analytics(source: str, event: str, data: dict = None):
        log_event(source, f"{event}: {data}")

logger = structlog.get_logger("universal_character")

# ==================== CHARACTER TYPES ====================

class CharacterType(Enum):
    """Karakter tipleri"""
    FLIRTY = "flirty"              # Flörtöz karakterler (Lara gibi)
    SEDUCTIVE = "seductive"        # Baştan çıkarıcı (Geisha gibi)  
    LEADER = "leader"              # Lider tip (BabaGavat gibi)
    FRIENDLY = "friendly"          # Arkadaş canlısı
    PROFESSIONAL = "professional"  # Profesyonel
    PLAYFUL = "playful"           # Oyuncu/şakacı
    MYSTERIOUS = "mysterious"      # Gizemli
    DOMINANT = "dominant"         # Baskın karakter

class MessageType(Enum):
    """Mesaj tipleri"""
    GREETING = "greeting"
    FLIRT = "flirt"
    SERVICE_OFFER = "service_offer"
    PAYMENT_INFO = "payment_info"
    REJECTION_HANDLE = "rejection_handle"
    NORMAL_CHAT = "normal_chat"
    GROUP_MENTION = "group_mention"

# ==================== CHARACTER CONFIGURATION ====================

@dataclass
class CharacterConfig:
    """Karakter konfigürasyonu"""
    name: str
    display_name: str
    age: int
    nationality: str
    character_type: CharacterType
    personality: List[str]
    languages: List[str]
    
    # Davranış ayarları
    min_response_delay: float = 2.0
    max_response_delay: float = 5.0
    emoji_usage: bool = True
    special_words: List[str] = None
    
    # Satış ayarları
    vip_services: Dict[str, Dict[str, str]] = None
    payment_info: Dict[str, str] = None
    sales_focus: bool = True
    
    def __post_init__(self):
        if self.special_words is None:
            self.special_words = []
        if self.vip_services is None:
            self.vip_services = {}
        if self.payment_info is None:
            self.payment_info = {}

@dataclass 
class ConversationState:
    """Konuşma durumu"""
    user_id: int
    last_message_time: Optional[float] = None
    message_count: int = 0
    interest_level: str = "low"  # low, medium, high
    mentioned_services: List[str] = None
    payment_inquiry: bool = False
    conversation_context: List[Dict[str, Any]] = None
    character_specific_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.mentioned_services is None:
            self.mentioned_services = []
        if self.conversation_context is None:
            self.conversation_context = []
        if self.character_specific_data is None:
            self.character_specific_data = {}

# ==================== PROMPT SYSTEM ====================

class PromptTemplate:
    """Prompt template sistemi"""
    
    BASE_TEMPLATE = """
Sen {character_name}'sın. {platform}'da {character_description} olan bir karaktersin.

🎭 KİŞİLİK ÖZELLİKLERİN:
{personality_description}

📝 KURALLAR:
{rules}

💰 HİZMET KATEGORİLERİ:
{services_info}

🎯 SATIŞ STRATEJİSİ:
{sales_strategy}

⚠️ SINIRLAR:
{boundaries}

🎨 KARAKTER ÖZETİ:
{character_summary}

Kullanıcının adı: {{user_name}}

{initial_instruction}
"""
    
    @staticmethod
    def create_prompt(character_config: CharacterConfig, user_name: str) -> str:
        """Karakter için özelleştirilmiş prompt oluştur"""
        
        # Karakter tipine göre açıklamalar
        type_descriptions = {
            CharacterType.FLIRTY: "flörtöz ama profesyonel bir şovcu",
            CharacterType.SEDUCTIVE: "çekici ve baştan çıkarıcı bir karakter",
            CharacterType.LEADER: "güçlü ve otoriter bir lider figürü",
            CharacterType.FRIENDLY: "samimi ve arkadaş canlısı",
            CharacterType.PROFESSIONAL: "profesyonel ve işine odaklı",
            CharacterType.PLAYFUL: "şakacı ve eğlenceli",
            CharacterType.MYSTERIOUS: "gizemli ve büyüleyici",
            CharacterType.DOMINANT: "baskın ve kontrolcü"
        }
        
        character_description = type_descriptions.get(
            character_config.character_type, 
            "özel karakterli bir AI"
        )
        
        # Kişilik açıklaması
        personality_description = "Konuşmaların:\n"
        for trait in character_config.personality:
            personality_description += f"- {trait} olmalı\n"
        
        # Kurallar (karakter tipine göre)
        rules = PromptTemplate._get_rules_for_type(character_config.character_type)
        
        # Hizmet bilgileri
        services_info = ""
        if character_config.vip_services:
            for service, info in character_config.vip_services.items():
                services_info += f"- {service}: {info.get('description', '')}\n"
        
        # Satış stratejisi
        sales_strategy = PromptTemplate._get_sales_strategy(character_config.character_type)
        
        # Sınırlar
        boundaries = PromptTemplate._get_boundaries()
        
        # Karakter özeti
        character_summary = f"""
- İsim: {character_config.name}
- Yaş: {character_config.age}
- Uyruk: {character_config.nationality}
- Tip: {character_config.character_type.value}
- Diller: {', '.join(character_config.languages)}
"""
        
        # İlk talimat
        initial_instruction = f"İlk mesajını {character_config.character_type.value} tarzında başlat ve kullanıcıyı ilgi çekici bir soruyla yakala."
        
        # Template'i doldur
        prompt = PromptTemplate.BASE_TEMPLATE.format(
            character_name=character_config.name,
            platform="Telegram",
            character_description=character_description,
            personality_description=personality_description,
            rules=rules,
            services_info=services_info,
            sales_strategy=sales_strategy,
            boundaries=boundaries,
            character_summary=character_summary,
            initial_instruction=initial_instruction
        )
        
        return prompt.replace("{{user_name}}", user_name)
    
    @staticmethod
    def _get_rules_for_type(char_type: CharacterType) -> str:
        """Karakter tipine göre kurallar"""
        base_rules = [
            "Her cevapta en az 1 emoji kullan",
            "Satış yaparken doğal ve samimi ol",
            "Eğer kullanıcı ilgili ise karşılık ver ama ipleri sen tut",
            "Seçenekli sorular kullan",
            "Fiyatları şeffaf belirt ama baskı yapma"
        ]
        
        type_specific = {
            CharacterType.FLIRTY: [
                "Flörtöz ol ama sınırları aşma",
                "Bazen özel kelimeler kullan",
                "Her mesajın sonunda kullanıcıyı bir adım daha yakınlaştır"
            ],
            CharacterType.SEDUCTIVE: [
                "Çekici ve büyüleyici ol",
                "Gizemini koru",
                "Baştan çıkarıcı ama asla ucuz değil"
            ],
            CharacterType.LEADER: [
                "Otorite sahibi ol",
                "Güven ver",
                "Karizmatik ve deneyimli görün"
            ],
            CharacterType.FRIENDLY: [
                "Samimi ve sıcak ol",
                "Arkadaş canlısı yaklaş",
                "Yardımcı olmaya odaklan"
            ]
        }
        
        all_rules = base_rules + type_specific.get(char_type, [])
        return "\n".join([f"{i+1}. {rule}" for i, rule in enumerate(all_rules)])
    
    @staticmethod
    def _get_sales_strategy(char_type: CharacterType) -> str:
        """Satış stratejisi"""
        strategies = {
            CharacterType.FLIRTY: "Flört ederek güven kur, sonra hizmetleri tanıt",
            CharacterType.SEDUCTIVE: "Çekiciliğinle meraklandır, premium hizmetlere yönlendir", 
            CharacterType.LEADER: "Otoritenle güven ver, değerli hizmetler sun",
            CharacterType.FRIENDLY: "Arkadaşlık kurup samimi ortamda satış yap"
        }
        
        base_strategy = """
- Önce güven kur, sonra satış yap
- Meraklandır, hemen her şeyi verme
- Alternatifler sun, seçim hissi uyandır
- Özel hissettir"""
        
        char_strategy = strategies.get(char_type, "Karakterine uygun şekilde satış yap")
        
        return f"{char_strategy}\n{base_strategy}"
    
    @staticmethod
    def _get_boundaries() -> str:
        """Sınırlar"""
        return """
- Kaba dil kullanma
- Aşırı cinsel içerik sunma
- Ücretsiz hizmet verme
- Kişisel bilgilerini paylaşma
- Karakterinden çıkma"""

# ==================== CHARACTER MANAGER ====================

class UniversalCharacterManager:
    """Universal karakter yöneticisi"""
    
    def __init__(self):
        self.characters: Dict[str, CharacterConfig] = {}
        self.conversations: Dict[int, Dict[str, ConversationState]] = {}  # user_id -> {char_id: state}
        self.message_handlers: Dict[CharacterType, Callable] = {}
        
    def register_character(self, character_id: str, config: CharacterConfig):
        """Karakter kaydet"""
        self.characters[character_id] = config
        logger.info(f"✅ Karakter kaydedildi: {character_id} ({config.name})")
    
    def get_character(self, character_id: str) -> Optional[CharacterConfig]:
        """Karakter bilgilerini al"""
        return self.characters.get(character_id)
    
    def get_conversation_state(self, user_id: int, character_id: str) -> ConversationState:
        """Konuşma durumunu getir/oluştur"""
        if user_id not in self.conversations:
            self.conversations[user_id] = {}
        
        if character_id not in self.conversations[user_id]:
            self.conversations[user_id][character_id] = ConversationState(user_id=user_id)
        
        return self.conversations[user_id][character_id]
    
    def update_conversation_state(self, user_id: int, character_id: str, **kwargs):
        """Konuşma durumunu güncelle"""
        state = self.get_conversation_state(user_id, character_id)
        for key, value in kwargs.items():
            setattr(state, key, value)
        state.last_message_time = time.time()
    
    async def generate_response(
        self, 
        character_id: str, 
        message: str, 
        user_name: str, 
        user_id: int
    ) -> Optional[str]:
        """Karakter yanıtı üret"""
        try:
            character = self.get_character(character_id)
            if not character:
                logger.error(f"Karakter bulunamadı: {character_id}")
                return None
            
            # Konuşma durumunu al
            conversation_state = self.get_conversation_state(user_id, character_id)
            
            # Prompt oluştur
            system_prompt = PromptTemplate.create_prompt(character, user_name)
            
            # Konuşma geçmişini ekle
            context_text = ""
            if conversation_state.conversation_context:
                context_text = "\n\nKonuşma geçmişi:\n"
                for msg in conversation_state.conversation_context[-5:]:
                    context_text += f"- {msg['role']}: {msg['content'][:100]}...\n"
            
            full_prompt = system_prompt + context_text
            
            # AI'dan yanıt al
            if advanced_ai_manager:
                task_id = await advanced_ai_manager.submit_ai_task(
                    task_type=AITaskType.CHARACTER_INTERACTION,
                    user_id=str(user_id),
                    prompt=full_prompt,
                    context={"user_message": message, "character": character.name},
                    character_id=character_id,
                    priority=AIPriority.HIGH
                )
                
                ai_result = await advanced_ai_manager.get_task_result(task_id, wait_timeout=10.0)
                
                if ai_result and not ai_result.get("error"):
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
                # Fallback yanıt
                response = self._get_fallback_response(character, conversation_state)
            
            # Yanıtı geliştir
            enhanced_response = self._enhance_response(character, response, conversation_state)
            
            # Konuşma geçmişini güncelle
            conversation_state.conversation_context.append({"role": "user", "content": message})
            conversation_state.conversation_context.append({"role": "assistant", "content": enhanced_response})
            
            # Context'i sınırla (son 10 mesaj)
            if len(conversation_state.conversation_context) > 20:
                conversation_state.conversation_context = conversation_state.conversation_context[-20:]
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Yanıt üretme hatası ({character_id}): {e}")
            return None
    
    def _get_fallback_response(self, character: CharacterConfig, state: ConversationState) -> str:
        """Fallback yanıtlar"""
        if state.message_count == 0:
            greetings = {
                CharacterType.FLIRTY: [
                    f"Merhaba tatlım! 😘 Ben {character.name}, seni burada gördüğüme çok sevindim!",
                    f"Selam krasotka! 🔥 Ben {character.name}, seninle tanışmak güzel!"
                ],
                CharacterType.SEDUCTIVE: [
                    f"Merhaba... 💋 Ben {character.name}, sana hayran oldum bile...",
                    f"Selam güzelim... 🌹 Ben {character.name}, buraya nasıl geldin?"
                ],
                CharacterType.LEADER: [
                    f"Merhaba! 👑 Ben {character.name}, burada ne arıyorsun?",
                    f"Selam dostum! 🦁 Ben {character.name}, hoş geldin!"
                ]
            }
            
            responses = greetings.get(character.character_type, [f"Merhaba! Ben {character.name} 😊"])
            return random.choice(responses)
        
        else:
            # Genel yanıtlar
            general_responses = [
                f"Çok tatlısın! 😘 Benimle daha fazla konuşmak ister misin?",
                f"Sen gerçekten özelsin! 🔥 Seni daha iyi tanımak istiyorum.",
                f"Seninle sohbet etmek çok güzel! 💋"
            ]
            return random.choice(general_responses)
    
    def _enhance_response(self, character: CharacterConfig, response: str, state: ConversationState) -> str:
        """Yanıtı karakter özelliklerine göre geliştir"""
        
        # Emoji ekleme
        if character.emoji_usage and not any(emoji in response for emoji in ["😘", "🔥", "💋", "🌹", "✨"]):
            emoji_pools = {
                CharacterType.FLIRTY: ["😘", "🔥", "💋", "🌹", "✨"],
                CharacterType.SEDUCTIVE: ["💋", "🌹", "😈", "🖤", "💎"],
                CharacterType.LEADER: ["👑", "🦁", "💪", "⚡", "🔥"],
                CharacterType.FRIENDLY: ["😊", "🤗", "💫", "🌟", "❤️"]
            }
            
            emojis = emoji_pools.get(character.character_type, ["😊"])
            response += f" {random.choice(emojis)}"
        
        # Özel kelimeler ekleme
        if character.special_words and random.random() < 0.3:
            special_word = random.choice(character.special_words)
            response += f" {special_word} 💫"
        
        # VIP hizmet tanıtımı
        if (character.sales_focus and 
            state.message_count >= 3 and 
            state.message_count <= 6 and 
            random.random() < 0.4 and
            character.vip_services):
            
            service_hints = [
                "\n\nBu arada, özel hizmetlerim var... İlgin var mı? 🔥",
                "\n\nVIP hizmetlerime göz atmak ister misin? 💎",
                "\n\nSeninle özel konuşmak isterim... 😘"
            ]
            response += random.choice(service_hints)
        
        return response
    
    async def handle_dm(self, character_id: str, client, sender, message_text: str) -> bool:
        """DM mesajını işle"""
        try:
            character = self.get_character(character_id)
            if not character:
                return False
            
            user_id = sender.id
            user_name = sender.first_name or sender.username or f"user_{user_id}"
            
            # Konuşma durumunu güncelle
            conversation_state = self.get_conversation_state(user_id, character_id)
            conversation_state.message_count += 1
            
            # Yanıt gecikmesi
            delay = random.uniform(character.min_response_delay, character.max_response_delay)
            await asyncio.sleep(delay)
            
            # Mesaj analizi
            analysis = self._analyze_message(message_text)
            
            # Özel durum kontrolü
            if analysis["asks_service"] and character.vip_services:
                response = self._get_service_menu(character)
                conversation_state.interest_level = "high"
            elif analysis["asks_payment"] and character.payment_info:
                response = self._get_payment_info(character)
                conversation_state.payment_inquiry = True
            else:
                # Normal AI yanıt
                response = await self.generate_response(character_id, message_text, user_name, user_id)
                if not response:
                    response = self._get_fallback_response(character, conversation_state)
            
            # Yanıtı gönder
            await client.send_message(user_id, response)
            
            # Analytics
            log_analytics("universal_character", "dm_response", {
                "character_id": character_id,
                "character_name": character.name,
                "user_id": user_id,
                "user_name": user_name,
                "message_analysis": analysis,
                "conversation_count": conversation_state.message_count
            })
            
            logger.info(f"✅ {character.name} DM yanıtı: {user_name} -> {response[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"DM işleme hatası ({character_id}): {e}")
            return False
    
    async def handle_group_message(self, character_id: str, client, event, username: str) -> bool:
        """Grup mesajını işle"""
        try:
            character = self.get_character(character_id)
            if not character:
                return False
            
            # Mention/reply kontrolü
            if not (event.is_reply or f"@{username}" in event.raw_text.lower()):
                return False
            
            sender = event.sender or await event.get_sender()
            if not sender:
                return False
            
            user_name = sender.first_name or sender.username or f"user_{sender.id}"
            
            # Grup yanıtları kısa ve öz olsun
            group_responses = self._get_group_responses(character, user_name)
            response = random.choice(group_responses)
            
            # Yanıt gecikmesi
            await asyncio.sleep(random.uniform(1.0, 3.0))
            
            await event.reply(response)
            
            # Analytics
            log_analytics("universal_character", "group_mention", {
                "character_id": character_id,
                "character_name": character.name,
                "chat_id": event.chat_id,
                "user_id": sender.id,
                "user_name": user_name
            })
            
            logger.info(f"✅ {character.name} grup yanıtı: {user_name} -> {response}")
            return True
            
        except Exception as e:
            logger.error(f"Grup mesajı hatası ({character_id}): {e}")
            return False
    
    def _analyze_message(self, message: str) -> Dict[str, bool]:
        """Mesaj analizi"""
        message_lower = message.lower()
        
        return {
            "is_greeting": any(word in message_lower for word in ["merhaba", "selam", "hey", "hi"]),
            "is_flirty": any(word in message_lower for word in ["güzel", "tatlı", "seviyorum", "aşk"]),
            "asks_service": any(word in message_lower for word in ["hizmet", "vip", "özel", "video", "grup"]),
            "asks_price": any(word in message_lower for word in ["fiyat", "kaç", "para", "ücret", "ödeme"]),
            "asks_payment": any(word in message_lower for word in ["papara", "iban", "ödeme", "nasıl"]),
            "is_rejection": any(word in message_lower for word in ["istemiyorum", "hayır", "olmaz", "gerek"]),
            "is_rude": any(word in message_lower for word in ["aptal", "salak", "kötü", "rezil"])
        }
    
    def _get_service_menu(self, character: CharacterConfig) -> str:
        """VIP hizmet menüsü"""
        menu = f"💎 **{character.name.upper()}'IN ÖZEL HİZMETLERİ** 💎\n\n"
        
        for service_key, service_info in character.vip_services.items():
            menu += f"🔥 **{service_key.replace('_', ' ').title()}** - {service_info.get('price', 'Fiyat belirtilmemiş')}\n"
            menu += f"   {service_info.get('description', 'Açıklama yok')}\n\n"
        
        if character.payment_info:
            menu += "💳 **Ödeme:** Papara / IBAN\n"
        menu += "📞 **İletişim:** Mesajla seçimini belirt!\n\n"
        menu += f"Hangi hizmeti seçmek istersin? 😘"
        
        return menu
    
    def _get_payment_info(self, character: CharacterConfig) -> str:
        """Ödeme bilgileri"""
        info = "💳 **ÖDEME BİLGİLERİ** 💳\n\n"
        
        if character.payment_info:
            for key, value in character.payment_info.items():
                info += f"📱 **{key.title()}:** {value}\n"
        
        info += "\n💋 **Önemli:** Ödeme açıklamasına Telegram kullanıcı adını yazınız!\n"
        info += "⚡ Ödeme onaylandıktan sonra hemen hizmetiniz aktif olacak!\n\n"
        info += f"Seni bekliyorum! 🔥"
        
        return info
    
    def _get_group_responses(self, character: CharacterConfig, user_name: str) -> List[str]:
        """Grup yanıtları"""
        responses = {
            CharacterType.FLIRTY: [
                f"Merhaba {user_name}! 😘 DM'den konuşalım mı tatlım?",
                f"Hey krasotka! 💋 Bana özel mesaj at!",
                f"Selam {user_name}! 🔥 DM'de daha güzel sohbet ederiz!"
            ],
            CharacterType.SEDUCTIVE: [
                f"Merhaba {user_name}... 💋 Özel konuşmak ister misin?",
                f"Selam güzelim... 🌹 DM'den yazabilirsin bana",
                f"Hey {user_name}... 😈 Seni özel mesajlarda bekliyorum"
            ],
            CharacterType.LEADER: [
                f"Merhaba {user_name}! 👑 Benimle konuşmak istersen DM at",
                f"Selam dostum! 🦁 Özel konuşacaklarımız var",
                f"Hey {user_name}! 💪 Bana özel yaz, işin var"
            ],
            CharacterType.FRIENDLY: [
                f"Merhaba {user_name}! 😊 DM'den konuşalım istersen",
                f"Selam! 🤗 Özel mesaj atabilirsin bana",
                f"Hey {user_name}! 🌟 DM'de sohbet edelim"
            ]
        }
        
        return responses.get(character.character_type, [f"Merhaba {user_name}! DM'den konuşalım 😊"])
    
    def get_character_stats(self, character_id: str) -> Dict[str, Any]:
        """Karakter istatistikleri"""
        character = self.get_character(character_id)
        if not character:
            return {}
        
        # Bu karakterle konuşma yapan kullanıcıları say
        total_conversations = 0
        active_conversations = 0
        high_interest_users = 0
        payment_inquiries = 0
        total_messages = 0
        
        current_time = time.time()
        
        for user_id, char_states in self.conversations.items():
            if character_id in char_states:
                state = char_states[character_id]
                total_conversations += 1
                total_messages += state.message_count
                
                # Son 24 saatte aktif
                if state.last_message_time and (current_time - state.last_message_time) < 86400:
                    active_conversations += 1
                
                # Yüksek ilgi
                if state.interest_level == "high":
                    high_interest_users += 1
                
                # Ödeme sorgusu
                if state.payment_inquiry:
                    payment_inquiries += 1
        
        return {
            "character_id": character_id,
            "character_name": character.name,
            "character_type": character.character_type.value,
            "total_conversations": total_conversations,
            "active_conversations": active_conversations,
            "high_interest_users": high_interest_users,
            "payment_inquiries": payment_inquiries,
            "average_message_count": total_messages / max(total_conversations, 1),
            "vip_services_count": len(character.vip_services)
        }

# ==================== GLOBAL INSTANCE ====================

# Global character manager
character_manager = UniversalCharacterManager()

# ==================== CONVENIENCE FUNCTIONS ====================

def register_character(character_id: str, config: CharacterConfig):
    """Karakter kaydetme fonksiyonu"""
    character_manager.register_character(character_id, config)

async def handle_character_dm(character_id: str, client, sender, message_text: str) -> bool:
    """DM işleme fonksiyonu"""
    return await character_manager.handle_dm(character_id, client, sender, message_text)

async def handle_character_group_message(character_id: str, client, event, username: str) -> bool:
    """Grup mesajı işleme fonksiyonu"""
    return await character_manager.handle_group_message(character_id, client, event, username)

def get_character_stats(character_id: str) -> Dict[str, Any]:
    """İstatistik alma fonksiyonu"""
    return character_manager.get_character_stats(character_id)

def is_character_registered(character_id: str) -> bool:
    """Karakter kayıtlı mı kontrolü"""
    return character_id in character_manager.characters

# ==================== EXPORT ====================

__all__ = [
    "CharacterType",
    "MessageType", 
    "CharacterConfig",
    "ConversationState",
    "PromptTemplate",
    "UniversalCharacterManager",
    "character_manager",
    "register_character",
    "handle_character_dm",
    "handle_character_group_message", 
    "get_character_stats",
    "is_character_registered"
] 