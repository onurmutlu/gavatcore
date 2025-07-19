from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🚀 GAVATCore 2.0 - AI Trigger Engine
=====================================

Token bazlı manipülasyon sistemi için tetikleyici motor.
Kullanıcı davranışlarına göre Zehra'nın ruh halini ve yanıt stratejisini belirler.

Features:
- Token harcama takibi
- Kullanıcı davranış analizi  
- Ruh hali geçişleri
- Manipülasyon taktik seçimi
- Zamanlama optimizasyonu
"""

import asyncio
import json
import time
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog

logger = structlog.get_logger("gavatcore.ai_reactor.trigger_engine")

class MoodState(Enum):
    """Zehra'nın ruh halleri"""
    HAPPY = "happy"        # 🔥 Token harcandı, ilgili
    TESTING = "testing"    # 🖤 Kullanıcıyı test ediyor
    NEUTRAL = "neutral"    # 🤍 Normal, bekleme modu
    ANGRY = "angry"        # 😡 Token yok, kızgın
    COLD = "cold"          # 🧊 Tamamen soğuk, manipülatif

class TriggerType(Enum):
    """Tetikleyici türleri"""
    TOKEN_PURCHASE = "token_purchase"
    TOKEN_DEPLETION = "token_depletion"
    MESSAGE_FREQUENCY = "message_frequency"
    TIME_BASED = "time_based"
    BEHAVIORAL = "behavioral"
    KEYWORD = "keyword"

@dataclass
class UserTokenProfile:
    """Kullanıcı token profili"""
    user_id: str
    current_tokens: int = 0
    total_spent: int = 0
    last_purchase: Optional[datetime] = None
    spending_pattern: str = "unknown"  # whale, regular, cheapskate, freeloader
    manipulation_resistance: float = 0.5  # 0-1 arası
    response_history: List[str] = field(default_factory=list)
    mood_triggers: List[str] = field(default_factory=list)
    last_interaction: Optional[datetime] = None

@dataclass
class TriggerEvent:
    """Tetikleyici olay"""
    trigger_type: TriggerType
    user_id: str
    data: Dict[str, Any]
    timestamp: datetime
    priority: int = 1  # 1-5 arası
    metadata: Dict[str, Any] = field(default_factory=dict)

class AITriggerEngine:
    """
    🚀 AI Tetikleyici Motor
    
    Zehra'nın token bazlı manipülasyon sisteminin beyin merkezi.
    Kullanıcı davranışlarını analiz eder ve optimal yanıt stratejisi belirler.
    """
    
    def __init__(self):
        self.user_profiles: Dict[str, UserTokenProfile] = {}
        self.active_triggers: Dict[str, List[TriggerEvent]] = {}
        self.mood_history: Dict[str, List[Tuple[MoodState, datetime]]] = {}
        self.manipulation_tactics = self._load_manipulation_tactics()
        
        # Trigger pattern'leri
        self.trigger_patterns = {
            "token_keywords": [
                r"token",
                r"para",
                r"ödeme",
                r"satın\s*al",
                r"bedava",
                r"ücretsiz",
                r"parasız"
            ],
            "emotional_keywords": [
                r"seviyorum",
                r"özledim",
                r"aşk",
                r"bırak",
                r"git",
                r"sıkıldım"
            ],
            "manipulation_triggers": [
                r"başka\s*(kız|kadın)",
                r"ex.*",
                r"eski.*sevgili",
                r"aldatmak",
                r"yalan"
            ]
        }
        
        logger.info("🚀 AI Trigger Engine initialized")
    
    def _load_manipulation_tactics(self) -> Dict[str, List[str]]:
        """Manipülasyon taktiklerini yükle"""
        return {
            "scarcity": [
                "Token'lar tükeniyor, son şansın...",
                "Sadece 24 saat geçerli bu fiyat",
                "Diğerleri aldı, sen kaçırma"
            ],
            "social_proof": [
                "Başka erkekler 1000 token aldı",
                "En çok harcayan sen olabilirsin",
                "VIP listesinde ilk 10'a girebilirsin"
            ],
            "loss_aversion": [
                "Token biterse bu fırsatı kaçırırsın",
                "Bir daha bu fiyatı bulamazsın",
                "Pişman olacaksın token almayınca"
            ],
            "emotional": [
                "Üzülüyorum token alamadığına",
                "Sevgi göstermen güzel olurdu",
                "Değer verdiğini hissettir bana"
            ]
        }
    
    async def process_message(self, user_id: str, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kullanıcı mesajını analiz eder ve tetikleyicileri belirler
        
        Args:
            user_id: Kullanıcı ID
            message: Mesaj içeriği
            context: Ek bağlam bilgileri
            
        Returns:
            Trigger analizi ve yanıt stratejisi
        """
        try:
            # Kullanıcı profilini al veya oluştur
            profile = self._get_or_create_profile(user_id)
            
            # Mesajı analiz et
            analysis = await self._analyze_message(message, profile)
            
            # Tetikleyicileri belirle
            triggers = await self._detect_triggers(user_id, message, analysis, context)
            
            # Ruh hali güncellemesi
            new_mood = await self._update_mood(user_id, triggers, profile)
            
            # Yanıt stratejisi oluştur
            response_strategy = await self._generate_response_strategy(
                user_id, new_mood, triggers, analysis
            )
            
            # Profili güncelle
            await self._update_profile(user_id, message, analysis, new_mood)
            
            return {
                "mood": new_mood.value,
                "triggers": [t.trigger_type.value for t in triggers],
                "strategy": response_strategy,
                "analysis": analysis,
                "metadata": {
                    "tokens": profile.current_tokens,
                    "spending_pattern": profile.spending_pattern,
                    "manipulation_resistance": profile.manipulation_resistance
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            return {
                "mood": MoodState.NEUTRAL.value,
                "triggers": [],
                "strategy": {"tactic": "safe_response"},
                "error": str(e)
            }
    
    def _get_or_create_profile(self, user_id: str) -> UserTokenProfile:
        """Kullanıcı profilini al veya oluştur"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserTokenProfile(user_id=user_id)
        return self.user_profiles[user_id]
    
    async def _analyze_message(self, message: str, profile: UserTokenProfile) -> Dict[str, Any]:
        """Mesajı analiz et"""
        analysis = {
            "contains_token_keywords": False,
            "emotional_tone": "neutral",
            "urgency_level": 0,
            "manipulation_attempt": False,
            "token_request": False,
            "complaint_detected": False,
            "length": len(message),
            "emoji_count": len(re.findall(r'[😀-🿿]', message))
        }
        
        message_lower = message.lower()
        
        # Token anahtar kelime kontrolü
        for pattern in self.trigger_patterns["token_keywords"]:
            if re.search(pattern, message_lower):
                analysis["contains_token_keywords"] = True
                break
        
        # Duygusal ton analizi
        emotional_patterns = {
            "angry": [r"sinir", r"kızgın", r"öfke", r"bıktım"],
            "sad": [r"üzgün", r"ağla", r"kırıl", r"mutsuz"],
            "happy": [r"mutlu", r"sevin", r"güzel", r"harika"],
            "manipulative": [r"başka", r"ex", r"eski", r"aldatmak"]
        }
        
        for tone, patterns in emotional_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    analysis["emotional_tone"] = tone
                    break
        
        # Aciliyet seviyesi
        urgency_markers = ["hemen", "şimdi", "acil", "çabuk"]
        analysis["urgency_level"] = sum(1 for marker in urgency_markers if marker in message_lower)
        
        # Token talebi
        token_request_patterns = [r"token.*ver", r"bedava.*token", r"ücretsiz"]
        for pattern in token_request_patterns:
            if re.search(pattern, message_lower):
                analysis["token_request"] = True
                break
        
        return analysis
    
    async def _detect_triggers(
        self, 
        user_id: str, 
        message: str, 
        analysis: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> List[TriggerEvent]:
        """Tetikleyicileri tespit et"""
        triggers = []
        now = datetime.now()
        profile = self.user_profiles[user_id]
        
        # Token tükenmesi tetikleyicisi
        if profile.current_tokens <= 5:
            triggers.append(TriggerEvent(
                trigger_type=TriggerType.TOKEN_DEPLETION,
                user_id=user_id,
                data={"remaining_tokens": profile.current_tokens},
                timestamp=now,
                priority=5
            ))
        
        # Davranışsal tetikleyici
        if analysis["token_request"]:
            triggers.append(TriggerEvent(
                trigger_type=TriggerType.BEHAVIORAL,
                user_id=user_id,
                data={"behavior": "requesting_free_tokens"},
                timestamp=now,
                priority=4
            ))
        
        # Anahtar kelime tetikleyicisi
        if analysis["contains_token_keywords"]:
            triggers.append(TriggerEvent(
                trigger_type=TriggerType.KEYWORD,
                user_id=user_id,
                data={"keywords": "token_related"},
                timestamp=now,
                priority=3
            ))
        
        # Zaman bazlı tetikleyici
        if profile.last_interaction:
            time_diff = now - profile.last_interaction
            if time_diff > timedelta(hours=24):
                triggers.append(TriggerEvent(
                    trigger_type=TriggerType.TIME_BASED,
                    user_id=user_id,
                    data={"hours_since_last": time_diff.total_seconds() / 3600},
                    timestamp=now,
                    priority=2
                ))
        
        return triggers
    
    async def _update_mood(
        self, 
        user_id: str, 
        triggers: List[TriggerEvent], 
        profile: UserTokenProfile
    ) -> MoodState:
        """Ruh halini güncelle"""
        current_mood = MoodState.NEUTRAL
        
        # Trigger önceliklerine göre ruh hali belirle
        if any(t.trigger_type == TriggerType.TOKEN_PURCHASE for t in triggers):
            current_mood = MoodState.HAPPY
        elif any(t.trigger_type == TriggerType.TOKEN_DEPLETION for t in triggers):
            if profile.total_spent > 500:
                current_mood = MoodState.TESTING  # Eski müşteri, test et
            else:
                current_mood = MoodState.COLD     # Yeni/ucuz müşteri, soğuk ol
        elif any(t.trigger_type == TriggerType.BEHAVIORAL and 
                t.data.get("behavior") == "requesting_free_tokens" for t in triggers):
            current_mood = MoodState.ANGRY
        else:
            current_mood = MoodState.TESTING
        
        # Mood history'e ekle
        if user_id not in self.mood_history:
            self.mood_history[user_id] = []
        
        self.mood_history[user_id].append((current_mood, datetime.now()))
        
        # Son 10 mood'u sakla
        if len(self.mood_history[user_id]) > 10:
            self.mood_history[user_id] = self.mood_history[user_id][-10:]
        
        return current_mood
    
    async def _generate_response_strategy(
        self,
        user_id: str,
        mood: MoodState,
        triggers: List[TriggerEvent],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Yanıt stratejisi oluştur"""
        profile = self.user_profiles[user_id]
        
        strategy = {
            "tactic": "neutral",
            "manipulation_type": None,
            "delay_response": False,
            "delay_seconds": 0,
            "use_emoji": True,
            "message_tone": "neutral"
        }
        
        if mood == MoodState.HAPPY:
            strategy.update({
                "tactic": "reward",
                "message_tone": "warm",
                "use_emoji": True,
                "delay_seconds": 2
            })
        
        elif mood == MoodState.TESTING:
            strategy.update({
                "tactic": "manipulation",
                "manipulation_type": "social_proof",
                "message_tone": "challenging",
                "delay_seconds": 10
            })
        
        elif mood == MoodState.ANGRY:
            strategy.update({
                "tactic": "punishment",
                "message_tone": "cold",
                "delay_response": True,
                "delay_seconds": 60,
                "use_emoji": False
            })
        
        elif mood == MoodState.COLD:
            strategy.update({
                "tactic": "scarcity",
                "manipulation_type": "loss_aversion",
                "message_tone": "distant",
                "delay_seconds": 30
            })
        
        # Trigger'lara göre ince ayar
        high_priority_triggers = [t for t in triggers if t.priority >= 4]
        if high_priority_triggers:
            strategy["priority_trigger"] = high_priority_triggers[0].trigger_type.value
        
        return strategy
    
    async def _update_profile(
        self,
        user_id: str,
        message: str,
        analysis: Dict[str, Any],
        mood: MoodState
    ) -> None:
        """Kullanıcı profilini güncelle"""
        profile = self.user_profiles[user_id]
        
        # Son etkileşim zamanını güncelle
        profile.last_interaction = datetime.now()
        
        # Yanıt geçmişine ekle
        profile.response_history.append(f"{mood.value}:{len(message)}")
        if len(profile.response_history) > 20:
            profile.response_history = profile.response_history[-20:]
        
        # Manipülasyon direnci güncelle
        if analysis["token_request"]:
            profile.manipulation_resistance += 0.1
        elif analysis["emotional_tone"] == "angry":
            profile.manipulation_resistance += 0.05
        
        # Harcama pattern analizi
        if profile.total_spent == 0:
            profile.spending_pattern = "freeloader"
        elif profile.total_spent < 100:
            profile.spending_pattern = "cheapskate"
        elif profile.total_spent < 500:
            profile.spending_pattern = "regular"
        else:
            profile.spending_pattern = "whale"
    
    async def update_token_balance(self, user_id: str, tokens: int, transaction_type: str) -> None:
        """Token bakiyesini güncelle"""
        profile = self._get_or_create_profile(user_id)
        
        if transaction_type == "purchase":
            profile.current_tokens += tokens
            profile.total_spent += tokens
            profile.last_purchase = datetime.now()
            
            # Token satın alma tetikleyicisi oluştur
            trigger = TriggerEvent(
                trigger_type=TriggerType.TOKEN_PURCHASE,
                user_id=user_id,
                data={"tokens_purchased": tokens},
                timestamp=datetime.now(),
                priority=5
            )
            
            if user_id not in self.active_triggers:
                self.active_triggers[user_id] = []
            self.active_triggers[user_id].append(trigger)
            
            logger.info(f"💰 Token purchase registered: {user_id} bought {tokens} tokens")
        
        elif transaction_type == "spend":
            profile.current_tokens = max(0, profile.current_tokens - tokens)
            logger.info(f"💸 Token spent: {user_id} spent {tokens} tokens")
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Kullanıcı istatistiklerini al"""
        if user_id not in self.user_profiles:
            return {"error": "User not found"}
        
        profile = self.user_profiles[user_id]
        mood_history = self.mood_history.get(user_id, [])
        
        return {
            "current_tokens": profile.current_tokens,
            "total_spent": profile.total_spent,
            "spending_pattern": profile.spending_pattern,
            "manipulation_resistance": profile.manipulation_resistance,
            "last_interaction": profile.last_interaction.isoformat() if profile.last_interaction else None,
            "mood_history": [(mood.value, ts.isoformat()) for mood, ts in mood_history[-5:]],
            "response_count": len(profile.response_history)
        } 