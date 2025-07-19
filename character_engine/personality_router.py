from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🎯 Personality Router - Kişilik bazlı yanıt yönlendirme sistemi
"""

import random
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum
import structlog

logger = structlog.get_logger("gavatcore.personality_router")

class ReplyType(Enum):
    """Yanıt tipleri"""
    ROMANTIC = "romantic"
    AGGRESSIVE = "aggressive"
    WISE = "wise"
    MANIPULATIVE = "manipulative"
    TEASING = "teasing"
    COMFORTING = "comforting"
    MYSTERIOUS = "mysterious"
    SEDUCTIVE = "seductive"
    SPIRITUAL = "spiritual"
    CASUAL = "casual"

class PersonalityRouter:
    """Kişilik bazlı yanıt yönlendirici"""
    
    def __init__(self):
        self.routes = {}
        logger.info("🎯 PersonalityRouter başlatıldı")
        
        # Kişilik-yanıt tipi eşleşmeleri
        self.personality_mappings = {
            "flirty": [ReplyType.ROMANTIC, ReplyType.SEDUCTIVE, ReplyType.TEASING],
            "soft": [ReplyType.COMFORTING, ReplyType.WISE, ReplyType.ROMANTIC],
            "dark": [ReplyType.MYSTERIOUS, ReplyType.MANIPULATIVE, ReplyType.AGGRESSIVE],
            "mystic": [ReplyType.SPIRITUAL, ReplyType.WISE, ReplyType.MYSTERIOUS],
            "aggressive": [ReplyType.AGGRESSIVE, ReplyType.MANIPULATIVE, ReplyType.TEASING]
        }
        
        # Yanıt tipi stratejileri
        self.reply_strategies = {
            ReplyType.ROMANTIC: self._romantic_strategy,
            ReplyType.AGGRESSIVE: self._aggressive_strategy,
            ReplyType.WISE: self._wise_strategy,
            ReplyType.MANIPULATIVE: self._manipulative_strategy,
            ReplyType.TEASING: self._teasing_strategy,
            ReplyType.COMFORTING: self._comforting_strategy,
            ReplyType.MYSTERIOUS: self._mysterious_strategy,
            ReplyType.SEDUCTIVE: self._seductive_strategy,
            ReplyType.SPIRITUAL: self._spiritual_strategy,
            ReplyType.CASUAL: self._casual_strategy
        }
    
    def add_route(self, personality_type: str, handler):
        """Kişilik tipi için yönlendirme ekle"""
        self.routes[personality_type] = handler
        logger.info(f"✅ Yönlendirme eklendi: {personality_type}")

    def get_handler(self, personality_type: str):
        """Kişilik tipi için yönlendirme al"""
        return self.routes.get(personality_type)
    
    def route_reply(
        self,
        user_message: str,
        character_config: Dict[str, Any],
        user_context: Dict[str, Any],
        message_analysis: Optional[Dict[str, Any]] = None
    ) -> Tuple[ReplyType, Dict[str, Any]]:
        """
        Mesaja ve bağlama göre yanıt tipini belirle
        
        Args:
            user_message: Kullanıcı mesajı
            character_config: Karakter konfigürasyonu
            user_context: Kullanıcı bağlam bilgileri (trust_index, geçmiş vb.)
            message_analysis: Mesaj analiz sonuçları
        
        Returns:
            (ReplyType, strateji_parametreleri)
        """
        tone = character_config.get("tone", "flirty")
        trust_index = user_context.get("trust_index", 0.5)
        message_count = user_context.get("message_count", 0)
        
        # Mesaj analizini kullan
        if message_analysis:
            emotion = message_analysis.get("emotion", "neutral")
            intent = message_analysis.get("intent", "chat")
            urgency = message_analysis.get("urgency", "medium")
        else:
            emotion = "neutral"
            intent = "chat"
            urgency = "medium"
        
        # Özel durumlar
        if emotion == "desperate" and trust_index > 0.7:
            return ReplyType.MANIPULATIVE, {"intensity": "high"}
        
        if emotion == "sad":
            return ReplyType.COMFORTING, {"warmth": "high"}
        
        if intent == "flirt" and tone == "flirty":
            return ReplyType.SEDUCTIVE, {"level": "medium"}
        
        if message_count < 5:
            # İlk mesajlarda gizemli ol
            return ReplyType.MYSTERIOUS, {"reveal": "low"}
        
        # Kişiliğe göre rastgele seç
        possible_types = self.personality_mappings.get(tone, [ReplyType.CASUAL])
        
        # Trust index'e göre ağırlık ver
        if trust_index > 0.8:
            # Yüksek güven - daha agresif/manipülatif olabilir
            weights = [1.5 if rt in [ReplyType.MANIPULATIVE, ReplyType.SEDUCTIVE] else 1.0 
                      for rt in possible_types]
        else:
            # Düşük güven - daha soft yaklaş
            weights = [1.5 if rt in [ReplyType.COMFORTING, ReplyType.ROMANTIC] else 1.0 
                      for rt in possible_types]
        
        # Ağırlıklı rastgele seçim
        reply_type = random.choices(possible_types, weights=weights)[0]
        
        # Strateji parametrelerini belirle
        strategy_params = self._get_strategy_params(reply_type, user_context)
        
        logger.info(f"🎯 Yanıt tipi belirlendi: {reply_type.value} - Parametreler: {strategy_params}")
        
        return reply_type, strategy_params
    
    def _get_strategy_params(self, reply_type: ReplyType, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Strateji parametrelerini belirle"""
        trust_index = user_context.get("trust_index", 0.5)
        
        base_params = {
            "trust_index": trust_index,
            "timestamp": datetime.now().isoformat()
        }
        
        # Tip bazlı özel parametreler
        if reply_type == ReplyType.ROMANTIC:
            base_params.update({
                "intensity": "high" if trust_index > 0.7 else "medium",
                "emoji_count": 2 if trust_index > 0.6 else 1
            })
        
        elif reply_type == ReplyType.MANIPULATIVE:
            base_params.update({
                "technique": random.choice(["guilt", "desire", "fear", "validation"]),
                "intensity": "medium" if trust_index < 0.8 else "high"
            })
        
        elif reply_type == ReplyType.SEDUCTIVE:
            base_params.update({
                "level": "subtle" if trust_index < 0.6 else "direct",
                "mystery": "high" if trust_index < 0.7 else "low"
            })
        
        return base_params
    
    def apply_strategy(
        self,
        reply: str,
        reply_type: ReplyType,
        strategy_params: Dict[str, Any]
    ) -> str:
        """
        Belirlenen stratejiyi yanıta uygula
        
        Args:
            reply: Ham yanıt metni
            reply_type: Yanıt tipi
            strategy_params: Strateji parametreleri
        
        Returns:
            Strateji uygulanmış yanıt
        """
        if reply_type in self.reply_strategies:
            return self.reply_strategies[reply_type](reply, strategy_params)
        
        return reply
    
    # Strateji fonksiyonları
    def _romantic_strategy(self, reply: str, params: Dict[str, Any]) -> str:
        """Romantik strateji uygula"""
        intensity = params.get("intensity", "medium")
        emoji_count = params.get("emoji_count", 1)
        
        romantic_emojis = ["❤️", "💕", "😍", "🥰", "💖", "💗"]
        
        if intensity == "high":
            reply = f"Aşkım, {reply}"
        elif intensity == "medium":
            reply = f"Canım, {reply}"
        
        # Emoji ekle
        for _ in range(emoji_count):
            reply += f" {random.choice(romantic_emojis)}"
        
        return reply
    
    def _aggressive_strategy(self, reply: str, params: Dict[str, Any]) -> str:
        """Agresif strateji uygula"""
        # Emir kipi kullan
        reply = reply.replace("yapabilir misin", "yap")
        reply = reply.replace("olur mu", "olacak")
        
        # Güçlü ifadeler ekle
        if not reply.endswith("!"):
            reply += "!"
        
        return reply
    
    def _wise_strategy(self, reply: str, params: Dict[str, Any]) -> str:
        """Bilge strateji uygula"""
        wisdom_intros = [
            "Hayat tecrübelerim bana öğretti ki",
            "Bilirsin",
            "Aslında",
            "Derin bir gerçek var ki"
        ]
        
        if len(reply) > 20 and random.random() > 0.5:
            reply = f"{random.choice(wisdom_intros)}, {reply.lower()}"
        
        return reply
    
    def _manipulative_strategy(self, reply: str, params: Dict[str, Any]) -> str:
        """Manipülatif strateji uygula"""
        technique = params.get("technique", "validation")
        
        if technique == "guilt":
            reply += " Ama sen bilirsin tabii..."
        elif technique == "desire":
            reply += " Sana özel bir şeyler hazırlıyorum 😉"
        elif technique == "fear":
            reply += " Umarım başka biriyle konuşmuyorsundur?"
        elif technique == "validation":
            reply = f"Sen gerçekten özelsin. {reply}"
        
        return reply
    
    def _teasing_strategy(self, reply: str, params: Dict[str, Any]) -> str:
        """Takılma stratejisi uygula"""
        teasing_endings = [
            " 😝",
            " hahaha",
            " 😂",
            " şaka şaka",
            " (dalga geçiyorum)"
        ]
        
        reply += random.choice(teasing_endings)
        return reply
    
    def _comforting_strategy(self, reply: str, params: Dict[str, Any]) -> str:
        """Teselli stratejisi uygula"""
        warmth = params.get("warmth", "medium")
        
        if warmth == "high":
            reply = f"Canım benim, {reply} Her şey düzelecek 🤗"
        else:
            reply += " 💝"
        
        return reply
    
    def _mysterious_strategy(self, reply: str, params: Dict[str, Any]) -> str:
        """Gizemli strateji uygula"""
        reveal = params.get("reveal", "medium")
        
        if reveal == "low":
            # Cümleyi yarıda kes
            if len(reply) > 30:
                reply = reply[:25] + "..."
        
        mystery_endings = [" 🌙", " ✨", " 🔮", "... kim bilir?"]
        reply += random.choice(mystery_endings)
        
        return reply
    
    def _seductive_strategy(self, reply: str, params: Dict[str, Any]) -> str:
        """Baştan çıkarıcı strateji uygula"""
        level = params.get("level", "subtle")
        
        if level == "subtle":
            seductive_hints = [
                " Senin için bazı sürprizlerim var",
                " Bu gece rüyalarında görüşürüz",
                " Sana anlatamayacağım şeyler var"
            ]
            reply += random.choice(seductive_hints) + " 😏"
        else:
            reply = f"Mmm... {reply} 💋"
        
        return reply
    
    def _spiritual_strategy(self, reply: str, params: Dict[str, Any]) -> str:
        """Ruhsal strateji uygula"""
        spiritual_symbols = ["🙏", "☯️", "🕉️", "⚛️", "🔮"]
        
        # Ruhsal kavramlar ekle
        spiritual_concepts = [
            " Evren seni duyuyor.",
            " Enerjin çok güçlü.",
            " Karmik bağımız var.",
            " Ruhun bana sesleniyor."
        ]
        
        if random.random() > 0.5:
            reply += random.choice(spiritual_concepts)
        
        reply += f" {random.choice(spiritual_symbols)}"
        return reply
    
    def _casual_strategy(self, reply: str, params: Dict[str, Any]) -> str:
        """Gündelik strateji uygula"""
        # Sadece basit emoji ekle
        casual_emojis = ["😊", "👍", "✌️", "🙂", "😄"]
        
        if not any(emoji in reply for emoji in casual_emojis):
            reply += f" {random.choice(casual_emojis)}"
        
        return reply

# Global instance
personality_router = PersonalityRouter() 