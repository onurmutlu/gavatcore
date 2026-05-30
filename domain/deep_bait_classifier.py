from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🎣 GAVATCore 2.1 - Deep Bait Classifier

**Layer:** Domain Layer — Core business logic for bait vs genuine analysis.
=======================================

Kullanıcı etkileşimlerini "bait" vs "gerçek" olarak sınıflandıran yapay zeka modülü.
Yüzeysel ilgi çekme taktikleri ile samimi etkileşimi ayırt eder.

Features:
- Real-time bait detection
- Authenticity scoring
- Pattern recognition
- Response depth analysis
- Engagement quality assessment
"""

import asyncio
import json
import re
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog

logger = structlog.get_logger("gavatcore.deep_bait_classifier")

class InteractionType(Enum):
    """Etkileşim türleri"""
    GENUINE_INTEREST = "genuine_interest"        # Gerçek ilgi
    SURFACE_BAIT = "surface_bait"               # Yüzeysel bait
    ATTENTION_SEEKING = "attention_seeking"      # Dikkat çekme
    EMOTIONAL_MANIPULATION = "emotional_manipulation" # Duygusal manipülasyon
    TRANSACTION_FOCUSED = "transaction_focused"  # İşlem odaklı
    EXPLORATION_PHASE = "exploration_phase"      # Keşif aşaması

class AuthenticityLevel(Enum):
    """Gerçeklik seviyeleri"""
    AUTHENTIC = "authentic"          # 0.8-1.0
    MOSTLY_GENUINE = "mostly_genuine" # 0.6-0.8
    MIXED = "mixed"                  # 0.4-0.6
    MOSTLY_BAIT = "mostly_bait"      # 0.2-0.4
    PURE_BAIT = "pure_bait"          # 0.0-0.2

@dataclass
class BaitIndicators:
    """Bait göstergeleri"""
    quick_responses: int = 0          # Çok hızlı yanıtlar
    generic_compliments: int = 0      # Genel komplimante
    attention_hooks: int = 0          # Dikkat çekici hook'lar
    transaction_hints: int = 0        # İşlem ipuçları
    emotional_triggers: int = 0       # Duygusal tetikleyiciler
    repetitive_patterns: int = 0      # Tekrarlayan pattern'ler

@dataclass
class AuthenticityMetrics:
    """Gerçeklik metrikleri"""
    response_thoughtfulness: float = 0.0  # Yanıt düşünceliği
    personal_disclosure: float = 0.0      # Kişisel paylaşım
    conversation_depth: float = 0.0       # Konuşma derinliği
    emotional_consistency: float = 0.0    # Duygusal tutarlılık
    engagement_quality: float = 0.0       # Etkileşim kalitesi
    spontaneity_score: float = 0.0        # Spontanlık

@dataclass
class BaitClassification:
    """Bait sınıflandırma sonucu"""
    user_id: str
    character_id: str
    timestamp: datetime
    interaction_type: InteractionType
    authenticity_level: AuthenticityLevel
    authenticity_score: float             # 0-1 arası
    bait_indicators: BaitIndicators
    authenticity_metrics: AuthenticityMetrics
    confidence_score: float               # Sınıflandırma güveni
    evidence: List[str]                   # Kanıtlar
    red_flags: List[str]                  # Kırmızı bayraklar
    recommendations: List[str]            # Öneriler

class DeepBaitClassifier:
    """
    🎣 Derin Bait Sınıflandırıcı
    
    Her etkileşimi analiz ederek gerçek ilgi vs manipülatif bait'i ayırt eder.
    Machine learning pattern'leri kullanarak authenticity score üretir.
    """
    
    def __init__(self):
        self.classification_history: Dict[str, List[BaitClassification]] = {}
        self.bait_patterns = self._load_bait_patterns()
        self.authentic_patterns = self._load_authentic_patterns()
        self.learned_patterns: Dict[str, float] = {}  # Öğrenilen pattern'ler
        
        # Analytics
        self.daily_stats = {
            "total_classified": 0,
            "genuine_interactions": 0,
            "bait_detected": 0,
            "average_authenticity": 0.0,
            "false_positive_rate": 0.0
        }
        
        logger.info("🎣 Deep Bait Classifier initialized")
    
    def _load_bait_patterns(self) -> Dict[str, List[str]]:
        """Bait pattern'lerini yükle"""
        return {
            "generic_compliments": [
                r"çok güzelsin",
                r"harikasın",
                r"mükemmelsin", 
                r"en güzeli sensin",
                r"bayıldım sana",
                r"çok seksi",
                r"süpersin"
            ],
            "attention_hooks": [
                r"özel bir şey söyleyeceğim",
                r"sana sır vereceğim",
                r"sadece sana özel",
                r"kimseye söyleme",
                r"çok özel birşey",
                r"sadece ikimiz",
                r"gizli"
            ],
            "transaction_hints": [
                r"hediye göndereceğim",
                r"para gönderirim",
                r"size yardım edebilirim",
                r"alışveriş yapabilirim",
                r"ödül vereceğim",
                r"karşılık veririm"
            ],
            "emotional_triggers": [
                r"çok yalnızım",
                r"sadece sen anlarsın",
                r"kimse beni anlamıyor",
                r"sen farklısın",
                r"ilk defa böyle hissediyorum",
                r"kalbimi çaldın"
            ],
            "quick_response_indicators": [
                r"hemen cevap ver",
                r"şimdi söyle",
                r"acele et",
                r"beklemek istemiyorum",
                r"çabuk",
                r"derhal"
            ]
        }
    
    def _load_authentic_patterns(self) -> Dict[str, List[str]]:
        """Gerçek etkileşim pattern'lerini yükle"""
        return {
            "thoughtful_responses": [
                r"düşünmek istiyorum",
                r"bu konuda",
                r"bence",
                r"sanırım",
                r"hissediyorum ki",
                r"deneyimim",
                r"görüşüm"
            ],
            "personal_sharing": [
                r"benim",
                r"ailem",
                r"çocukluğum",
                r"geçmişim",
                r"hikayem",
                r"deneyimim",
                r"yaşadım"
            ],
            "genuine_questions": [
                r"sence",
                r"ne düşünüyorsun",
                r"nasıl hissedersin",
                r"anlat bana",
                r"merak ediyorum",
                r"öğrenmek istiyorum"
            ],
            "emotional_depth": [
                r"derinden",
                r"samimiyetle", 
                r"içtenlikle",
                r"gerçekten",
                r"kalbimden",
                r"dürüstçe",
                r"açıkça"
            ],
            "future_oriented": [
                r"gelecekte",
                r"planlarım",
                r"hayalim",
                r"istiyorum ki",
                r"olmasını umuyorum",
                r"birlikte",
                r"devam"
            ]
        }
    
    async def classify_interaction(
        self,
        user_id: str,
        character_id: str,
        messages: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> BaitClassification:
        """
        Etkileşimi sınıflandır
        
        Args:
            user_id: Kullanıcı ID
            character_id: Karakter ID
            messages: Mesaj listesi
            context: Ek bağlam
            
        Returns:
            BaitClassification objesi
        """
        try:
            # Bait göstergelerini tespit et
            bait_indicators = await self._detect_bait_indicators(messages)
            
            # Gerçeklik metriklerini hesapla
            authenticity_metrics = await self._calculate_authenticity_metrics(messages)
            
            # Authenticity score hesapla
            authenticity_score = await self._calculate_authenticity_score(
                bait_indicators, authenticity_metrics
            )
            
            # Etkileşim türünü belirle
            interaction_type = await self._determine_interaction_type(
                bait_indicators, authenticity_metrics, messages
            )
            
            # Gerçeklik seviyesi
            authenticity_level = self._determine_authenticity_level(authenticity_score)
            
            # Güven skoru
            confidence_score = await self._calculate_confidence_score(
                bait_indicators, authenticity_metrics
            )
            
            # Kanıtları topla
            evidence = await self._collect_evidence(messages, bait_indicators, authenticity_metrics)
            
            # Kırmızı bayrakları tespit et
            red_flags = await self._detect_red_flags(messages, bait_indicators)
            
            # Öneriler oluştur
            recommendations = await self._generate_recommendations(
                interaction_type, authenticity_score, red_flags
            )
            
            # Sınıflandırma objesi
            classification = BaitClassification(
                user_id=user_id,
                character_id=character_id,
                timestamp=datetime.now(),
                interaction_type=interaction_type,
                authenticity_level=authenticity_level,
                authenticity_score=authenticity_score,
                bait_indicators=bait_indicators,
                authenticity_metrics=authenticity_metrics,
                confidence_score=confidence_score,
                evidence=evidence,
                red_flags=red_flags,
                recommendations=recommendations
            )
            
            # Geçmişe ekle
            if user_id not in self.classification_history:
                self.classification_history[user_id] = []
            self.classification_history[user_id].append(classification)
            
            # Öğrenme - pattern'leri güncelle
            await self._update_learned_patterns(classification, messages)
            
            # İstatistikleri güncelle
            await self._update_stats(classification)
            
            logger.info(f"🎣 Interaction classified",
                       user=user_id,
                       type=interaction_type.value,
                       authenticity=authenticity_score,
                       confidence=confidence_score)
            
            return classification
            
        except Exception as e:
            logger.error(f"❌ Error classifying interaction: {e}")
            return self._create_fallback_classification(user_id, character_id)
    
    async def _detect_bait_indicators(self, messages: List[Dict[str, Any]]) -> BaitIndicators:
        """Bait göstergelerini tespit et"""
        indicators = BaitIndicators()
        
        all_content = " ".join(msg.get("content", "") for msg in messages).lower()
        
        # Generic compliments
        for pattern in self.bait_patterns["generic_compliments"]:
            indicators.generic_compliments += len(re.findall(pattern, all_content))
        
        # Attention hooks
        for pattern in self.bait_patterns["attention_hooks"]:
            indicators.attention_hooks += len(re.findall(pattern, all_content))
        
        # Transaction hints
        for pattern in self.bait_patterns["transaction_hints"]:
            indicators.transaction_hints += len(re.findall(pattern, all_content))
        
        # Emotional triggers
        for pattern in self.bait_patterns["emotional_triggers"]:
            indicators.emotional_triggers += len(re.findall(pattern, all_content))
        
        # Quick response indicators
        for pattern in self.bait_patterns["quick_response_indicators"]:
            indicators.quick_responses += len(re.findall(pattern, all_content))
        
        # Repetitive patterns - tekrarlayan ifadeler
        words = all_content.split()
        word_counts = {}
        for word in words:
            if len(word) > 3:  # Kısa kelimeler hariç
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # 3'ten fazla tekrar eden kelimeler
        indicators.repetitive_patterns = sum(1 for count in word_counts.values() if count > 3)
        
        return indicators
    
    async def _calculate_authenticity_metrics(self, messages: List[Dict[str, Any]]) -> AuthenticityMetrics:
        """Gerçeklik metriklerini hesapla"""
        metrics = AuthenticityMetrics()
        
        if not messages:
            return metrics
        
        all_content = " ".join(msg.get("content", "") for msg in messages).lower()
        
        # Response thoughtfulness - düşünceli yanıtlar
        thoughtful_score = 0.0
        for pattern in self.authentic_patterns["thoughtful_responses"]:
            thoughtful_score += len(re.findall(pattern, all_content))
        metrics.response_thoughtfulness = min(1.0, thoughtful_score / 5)
        
        # Personal disclosure - kişisel paylaşım
        personal_score = 0.0
        for pattern in self.authentic_patterns["personal_sharing"]:
            personal_score += len(re.findall(pattern, all_content))
        metrics.personal_disclosure = min(1.0, personal_score / 3)
        
        # Conversation depth - konuşma derinliği
        depth_score = 0.0
        depth_score += len(re.findall(r'\?', all_content)) * 0.2  # Sorular
        depth_score += len(re.findall(r'çünkü|nedeni|sebep', all_content)) * 0.3  # Açıklamalar
        depth_score += len(re.findall(r'hissediyorum|düşünüyorum|inanıyorum', all_content)) * 0.4
        metrics.conversation_depth = min(1.0, depth_score / 3)
        
        # Emotional consistency - önceki modülden
        metrics.emotional_consistency = 0.7  # Placeholder
        
        # Engagement quality
        engagement_score = 0.0
        for pattern in self.authentic_patterns["genuine_questions"]:
            engagement_score += len(re.findall(pattern, all_content))
        metrics.engagement_quality = min(1.0, engagement_score / 4)
        
        # Spontaneity - doğallık
        spontaneity = 1.0
        # Çok mükemmel grammar = düşük spontanlık
        if not re.search(r'[.]{2,}|[!]{2,}|[?]{2,}', all_content):
            spontaneity -= 0.2
        # Hata/typo varlığı = yüksek spontanlık  
        if re.search(r'\b\w*[0-9]\w*\b', all_content):  # Typo pattern
            spontaneity += 0.1
        metrics.spontaneity_score = max(0.0, min(1.0, spontaneity))
        
        return metrics
    
    async def _calculate_authenticity_score(
        self, 
        bait_indicators: BaitIndicators, 
        authenticity_metrics: AuthenticityMetrics
    ) -> float:
        """Gerçeklik skoru hesapla"""
        
        # Pozitif faktörler (authenticity artırır)
        positive_score = (
            authenticity_metrics.response_thoughtfulness * 0.20 +
            authenticity_metrics.personal_disclosure * 0.18 +
            authenticity_metrics.conversation_depth * 0.22 +
            authenticity_metrics.emotional_consistency * 0.15 +
            authenticity_metrics.engagement_quality * 0.15 +
            authenticity_metrics.spontaneity_score * 0.10
        )
        
        # Negatif faktörler (bait göstergeleri)
        bait_penalty = (
            min(bait_indicators.generic_compliments / 5, 1.0) * 0.25 +
            min(bait_indicators.attention_hooks / 3, 1.0) * 0.30 +
            min(bait_indicators.transaction_hints / 2, 1.0) * 0.35 +
            min(bait_indicators.emotional_triggers / 4, 1.0) * 0.20 +
            min(bait_indicators.quick_responses / 3, 1.0) * 0.15 +
            min(bait_indicators.repetitive_patterns / 5, 1.0) * 0.10
        ) / 6  # Ortalama penalty
        
        # Final score
        authenticity_score = max(0.0, positive_score - bait_penalty)
        
        return round(authenticity_score, 3)
    
    async def _determine_interaction_type(
        self,
        bait_indicators: BaitIndicators,
        authenticity_metrics: AuthenticityMetrics,
        messages: List[Dict[str, Any]]
    ) -> InteractionType:
        """Etkileşim türünü belirle"""
        
        # Transaction hints yüksekse
        if bait_indicators.transaction_hints > 2:
            return InteractionType.TRANSACTION_FOCUSED
        
        # Emotional triggers + generic compliments yüksekse
        if (bait_indicators.emotional_triggers > 3 and 
            bait_indicators.generic_compliments > 3):
            return InteractionType.EMOTIONAL_MANIPULATION
        
        # Attention hooks yüksekse
        if bait_indicators.attention_hooks > 2:
            return InteractionType.ATTENTION_SEEKING
        
        # Genel bait göstergeleri yüksekse
        total_bait = (bait_indicators.generic_compliments + 
                     bait_indicators.attention_hooks + 
                     bait_indicators.quick_responses)
        if total_bait > 5:
            return InteractionType.SURFACE_BAIT
        
        # Authenticity yüksekse
        if (authenticity_metrics.personal_disclosure > 0.5 and 
            authenticity_metrics.conversation_depth > 0.4):
            return InteractionType.GENUINE_INTEREST
        
        # Default
        return InteractionType.EXPLORATION_PHASE
    
    def _determine_authenticity_level(self, score: float) -> AuthenticityLevel:
        """Gerçeklik seviyesi belirle"""
        if score >= 0.8:
            return AuthenticityLevel.AUTHENTIC
        elif score >= 0.6:
            return AuthenticityLevel.MOSTLY_GENUINE
        elif score >= 0.4:
            return AuthenticityLevel.MIXED
        elif score >= 0.2:
            return AuthenticityLevel.MOSTLY_BAIT
        else:
            return AuthenticityLevel.PURE_BAIT
    
    async def _calculate_confidence_score(
        self,
        bait_indicators: BaitIndicators,
        authenticity_metrics: AuthenticityMetrics
    ) -> float:
        """Sınıflandırma güven skoru"""
        
        # Güçlü göstergeler = yüksek güven
        strong_indicators = 0
        
        # Bait göstergeleri
        if bait_indicators.transaction_hints > 1:
            strong_indicators += 1
        if bait_indicators.attention_hooks > 2:
            strong_indicators += 1
        if bait_indicators.emotional_triggers > 3:
            strong_indicators += 1
            
        # Authenticity göstergeleri
        if authenticity_metrics.personal_disclosure > 0.6:
            strong_indicators += 1
        if authenticity_metrics.conversation_depth > 0.5:
            strong_indicators += 1
        
        confidence = min(1.0, strong_indicators / 5 + 0.3)  # Min %30 güven
        return round(confidence, 3)
    
    async def _collect_evidence(
        self,
        messages: List[Dict[str, Any]],
        bait_indicators: BaitIndicators,
        authenticity_metrics: AuthenticityMetrics
    ) -> List[str]:
        """Kanıtları topla"""
        evidence = []
        
        if bait_indicators.generic_compliments > 2:
            evidence.append(f"Generic compliments detected: {bait_indicators.generic_compliments}")
        
        if bait_indicators.transaction_hints > 0:
            evidence.append(f"Transaction hints found: {bait_indicators.transaction_hints}")
        
        if authenticity_metrics.personal_disclosure > 0.5:
            evidence.append(f"High personal disclosure: {authenticity_metrics.personal_disclosure:.2f}")
        
        if authenticity_metrics.conversation_depth > 0.4:
            evidence.append(f"Good conversation depth: {authenticity_metrics.conversation_depth:.2f}")
        
        if bait_indicators.repetitive_patterns > 3:
            evidence.append(f"Repetitive patterns: {bait_indicators.repetitive_patterns}")
        
        return evidence
    
    async def _detect_red_flags(
        self,
        messages: List[Dict[str, Any]],
        bait_indicators: BaitIndicators
    ) -> List[str]:
        """Kırmızı bayrakları tespit et"""
        red_flags = []
        
        if bait_indicators.transaction_hints > 1:
            red_flags.append("Multiple transaction hints - possible scam")
        
        if bait_indicators.emotional_triggers > 4:
            red_flags.append("Excessive emotional manipulation")
        
        if bait_indicators.attention_hooks > 3:
            red_flags.append("Too many attention-seeking behaviors")
        
        if bait_indicators.quick_responses > 2:
            red_flags.append("Pressure for immediate responses")
        
        # Suspicious patterns
        all_content = " ".join(msg.get("content", "") for msg in messages).lower()
        
        if re.search(r'şifre|kredi\s*kartı|banka\s*hesap', all_content):
            red_flags.append("Requesting sensitive information")
        
        if re.search(r'acil\s*para|maddi\s*sıkıntı|borç', all_content):
            red_flags.append("Financial emergency claims")
        
        return red_flags
    
    async def _generate_recommendations(
        self,
        interaction_type: InteractionType,
        authenticity_score: float,
        red_flags: List[str]
    ) -> List[str]:
        """Öneriler oluştur"""
        recommendations = []
        
        if interaction_type == InteractionType.TRANSACTION_FOCUSED:
            recommendations.append("Be cautious - interaction seems transaction-focused")
        
        if interaction_type == InteractionType.EMOTIONAL_MANIPULATION:
            recommendations.append("Warning: Emotional manipulation detected")
        
        if authenticity_score > 0.7:
            recommendations.append("High authenticity - genuine interaction likely")
        elif authenticity_score < 0.3:
            recommendations.append("Low authenticity - possible bait interaction")
        
        if red_flags:
            recommendations.append("Multiple red flags detected - exercise extreme caution")
        
        if interaction_type == InteractionType.GENUINE_INTEREST:
            recommendations.append("Positive interaction - continue building connection")
        
        return recommendations
    
    async def _update_learned_patterns(
        self,
        classification: BaitClassification,
        messages: List[Dict[str, Any]]
    ) -> None:
        """Öğrenilen pattern'leri güncelle"""
        
        # Bu AI sisteminin kendini geliştirmesi için
        # Pattern'leri kaydet ve gelecekte kullan
        
        message_content = " ".join(msg.get("content", "") for msg in messages).lower()
        
        # Yeni pattern'leri tespit et
        words = message_content.split()
        
        for word in words:
            if len(word) > 4:  # Anlamlı kelimeler
                pattern_key = f"{classification.interaction_type.value}_{word}"
                current_score = self.learned_patterns.get(pattern_key, 0.0)
                
                # Authenticity score'a göre güncelle
                if classification.authenticity_score > 0.7:
                    self.learned_patterns[pattern_key] = current_score + 0.1
                elif classification.authenticity_score < 0.3:
                    self.learned_patterns[pattern_key] = current_score - 0.1
    
    def _create_fallback_classification(self, user_id: str, character_id: str) -> BaitClassification:
        """Hata durumunda fallback sınıflandırma"""
        return BaitClassification(
            user_id=user_id,
            character_id=character_id,
            timestamp=datetime.now(),
            interaction_type=InteractionType.EXPLORATION_PHASE,
            authenticity_level=AuthenticityLevel.MIXED,
            authenticity_score=0.5,
            bait_indicators=BaitIndicators(),
            authenticity_metrics=AuthenticityMetrics(),
            confidence_score=0.3,
            evidence=["Analysis failed"],
            red_flags=["Classification error"],
            recommendations=["Retry analysis"]
        )
    
    async def _update_stats(self, classification: BaitClassification) -> None:
        """İstatistikleri güncelle"""
        self.daily_stats["total_classified"] += 1
        
        if classification.interaction_type == InteractionType.GENUINE_INTEREST:
            self.daily_stats["genuine_interactions"] += 1
        
        if classification.authenticity_score < 0.4:
            self.daily_stats["bait_detected"] += 1
        
        # Ortalama authenticity güncelle
        prev_avg = self.daily_stats["average_authenticity"]
        total = self.daily_stats["total_classified"]
        new_avg = (prev_avg * (total - 1) + classification.authenticity_score) / total
        self.daily_stats["average_authenticity"] = round(new_avg, 3)
    
    async def get_user_interaction_profile(self, user_id: str) -> Dict[str, Any]:
        """Kullanıcının etkileşim profili"""
        if user_id not in self.classification_history:
            return {"error": "No classification history found"}
        
        classifications = self.classification_history[user_id]
        
        avg_authenticity = sum(c.authenticity_score for c in classifications) / len(classifications)
        
        # En sık görülen etkileşim türü
        interaction_types = [c.interaction_type.value for c in classifications]
        most_common_type = max(set(interaction_types), key=interaction_types.count)
        
        # Trend analizi
        recent_scores = [c.authenticity_score for c in classifications[-5:]]
        if len(recent_scores) > 1:
            trend = "improving" if recent_scores[-1] > recent_scores[0] else "declining"
        else:
            trend = "insufficient_data"
        
        # Kırmızı bayrak sayısı
        total_red_flags = sum(len(c.red_flags) for c in classifications)
        
        return {
            "user_id": user_id,
            "total_interactions": len(classifications),
            "average_authenticity": round(avg_authenticity, 3),
            "most_common_interaction_type": most_common_type,
            "authenticity_trend": trend,
            "total_red_flags": total_red_flags,
            "latest_classification": {
                "type": classifications[-1].interaction_type.value,
                "authenticity": classifications[-1].authenticity_score,
                "red_flags": classifications[-1].red_flags
            }
        }
    
    def get_system_bait_stats(self) -> Dict[str, Any]:
        """Sistem geneli bait istatistikleri"""
        return {
            "daily_stats": self.daily_stats,
            "total_users_classified": len(self.classification_history),
            "bait_detection_rate": (
                self.daily_stats["bait_detected"] / 
                max(self.daily_stats["total_classified"], 1)
            ),
            "genuine_interaction_rate": (
                self.daily_stats["genuine_interactions"] / 
                max(self.daily_stats["total_classified"], 1)
            ),
            "learned_patterns_count": len(self.learned_patterns)
        } 
