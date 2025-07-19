from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🧬 GAVATCore 2.1 - Emotion Quality Analyzer
==========================================

Gerçek duygusal yakınlık vs manipülatif bait'i ayırt eden yapay zeka modülü.
Her konuşmayı analiz eder ve EQS (Emotional Quality Score) üretir.

Features:
- Metin tonu ve derinlik analizi
- Karşılık oranı hesaplama
- İlgi süresi tracking
- Gerçek vs sahte yakınlık tespiti
- Tatmin potansiyeli ölçümü
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

logger = structlog.get_logger("gavatcore.emotion_quality_analyzer")

class EmotionalState(Enum):
    """Duygusal durum kategorileri"""
    GENUINE_INTIMACY = "genuine_intimacy"        # Gerçek yakınlık
    SURFACE_FLIRT = "surface_flirt"              # Yüzeysel flört
    MANIPULATIVE_BAIT = "manipulative_bait"      # Manipülatif bait
    EMOTIONAL_VOID = "emotional_void"            # Duygusal boşluk
    SEXUAL_TENSION = "sexual_tension"            # Cinsel gerilim
    SATISFACTION_BUILDING = "satisfaction_building" # Tatmin inşası

class IntimacyLevel(Enum):
    """Yakınlık seviyeleri"""
    STRANGER = "stranger"              # 0.0-0.2
    ACQUAINTANCE = "acquaintance"      # 0.2-0.4
    FRIEND = "friend"                  # 0.4-0.6
    INTIMATE = "intimate"              # 0.6-0.8
    DEEPLY_CONNECTED = "deeply_connected" # 0.8-1.0

@dataclass
class EmotionalMetrics:
    """Duygusal metrikler"""
    text_depth: float = 0.0           # Metin derinliği (0-1)
    response_quality: float = 0.0     # Yanıt kalitesi (0-1)
    emotional_consistency: float = 0.0 # Duygusal tutarlılık (0-1)
    intimacy_progression: float = 0.0  # Yakınlık ilerlemesi (0-1)
    satisfaction_potential: float = 0.0 # Tatmin potansiyeli (0-1)
    manipulation_score: float = 0.0   # Manipülasyon skoru (0-1, yüksek=kötü)

@dataclass
class ConversationAnalysis:
    """Konuşma analizi sonucu"""
    user_id: str
    character_id: str
    timestamp: datetime
    eqs_score: float                  # Emotional Quality Score (0-1)
    intimacy_level: IntimacyLevel
    emotional_state: EmotionalState
    metrics: EmotionalMetrics
    conversation_length: int
    response_times: List[float]
    key_emotions: List[str]
    satisfaction_indicators: List[str]
    warning_flags: List[str]
    recommendations: List[str]

class EmotionQualityAnalyzer:
    """
    🧬 Duygusal Kalite Analiz Motoru
    
    Her konuşmayı analiz ederek gerçek duygusal bağ vs manipülatif bait'i ayırt eder.
    EQS (Emotional Quality Score) üretir ve tatmin potansiyelini ölçer.
    """
    
    def __init__(self):
        self.conversation_history: Dict[str, List[ConversationAnalysis]] = {}
        self.emotional_patterns = self._load_emotional_patterns()
        self.intimacy_keywords = self._load_intimacy_keywords()
        self.manipulation_indicators = self._load_manipulation_indicators()
        
        # Analytics
        self.daily_stats = {
            "total_analyzed": 0,
            "genuine_intimacy_count": 0,
            "manipulation_detected": 0,
            "average_eqs": 0.0,
            "satisfaction_rate": 0.0
        }
        
        logger.info("🧬 Emotion Quality Analyzer initialized")
    
    def _load_emotional_patterns(self) -> Dict[str, Any]:
        """Duygusal pattern'leri yükle"""
        return {
            "genuine_intimacy_indicators": [
                r"özledim",
                r"düşünüyorum seni",
                r"hissediyorum",
                r"samimi",
                r"yakın\w*",
                r"özel\w*",
                r"anlıyorum seni",
                r"paylaş\w*",
                r"dinli\w*",
                r"rahatla\w*"
            ],
            "surface_flirt_indicators": [
                r"güzelsin",
                r"seksisin",
                r"çekicisin",
                r"ateşli\w*",
                r"harika\w*",
                r"mükemmel\w*",
                r"beğendim",
                r"hoşuma gitti"
            ],
            "sexual_tension_indicators": [
                r"dokunmak",
                r"öpmek",
                r"sarılmak",
                r"yaklaş\w*",
                r"hisset\w*",
                r"arzuluyorum",
                r"istiyorum seni",
                r"tutkuyla",
                r"ateşle\w*",
                r"coşkuyla"
            ],
            "manipulation_patterns": [
                r"para\w*",
                r"token\w*",
                r"ödeme\w*",
                r"hediye\w*",
                r"almak zorunda",
                r"şartım\w*",
                r"kuralım\w*",
                r"olmazsa\w*"
            ]
        }
    
    def _load_intimacy_keywords(self) -> Dict[str, List[str]]:
        """Yakınlık anahtar kelimelerini yükle"""
        return {
            "emotional_depth": [
                "ruh", "kalp", "hissetmek", "duygu", "iç", "derinde",
                "samimi", "içten", "gerçek", "doğal", "saf"
            ],
            "physical_intimacy": [
                "dokunmak", "sarılmak", "öpmek", "yakın", "temas",
                "deri", "nefes", "sıcaklık", "titremek", "heyecan"
            ],
            "mental_connection": [
                "anlıyorum", "biliyorum", "düşünce", "fikir", "hayal",
                "rüya", "zihin", "akıl", "mantık", "sezgi"
            ],
            "future_orientation": [
                "gelecek", "plan", "birlikte", "devam", "sürekli",
                "uzun", "kalıcı", "daim", "sonsuza", "ebedi"
            ]
        }
    
    def _load_manipulation_indicators(self) -> List[str]:
        """Manipülasyon göstergelerini yükle"""
        return [
            "token", "para", "ödeme", "hediye", "satın",
            "almak zorunda", "şart", "kural", "mecbur",
            "olmazsa", "eğer", "ama önce", "karşılığında",
            "bedava", "ücretsiz", "parasız", "beleş"
        ]
    
    async def analyze_conversation(
        self,
        user_id: str,
        character_id: str,
        messages: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> ConversationAnalysis:
        """
        Konuşmayı analiz et ve EQS skoru üret
        
        Args:
            user_id: Kullanıcı ID
            character_id: Karakter ID  
            messages: Mesaj listesi
            context: Ek bağlam bilgileri
            
        Returns:
            ConversationAnalysis objesi
        """
        try:
            # Metrikler hesapla
            metrics = await self._calculate_emotional_metrics(messages, context or {})
            
            # EQS skoru hesapla
            eqs_score = await self._calculate_eqs_score(metrics, messages)
            
            # Yakınlık seviyesi belirle
            intimacy_level = self._determine_intimacy_level(eqs_score, metrics)
            
            # Duygusal durum tespit et
            emotional_state = await self._detect_emotional_state(messages, metrics)
            
            # Yanıt süreleri analiz et
            response_times = self._analyze_response_times(messages)
            
            # Anahtar duygular çıkar
            key_emotions = await self._extract_key_emotions(messages)
            
            # Tatmin göstergeleri tespit et
            satisfaction_indicators = await self._detect_satisfaction_indicators(messages)
            
            # Uyarı bayrakları kontrol et
            warning_flags = await self._check_warning_flags(messages, metrics)
            
            # Öneriler oluştur
            recommendations = await self._generate_recommendations(eqs_score, metrics, warning_flags)
            
            # Analiz objesi oluştur
            analysis = ConversationAnalysis(
                user_id=user_id,
                character_id=character_id,
                timestamp=datetime.now(),
                eqs_score=eqs_score,
                intimacy_level=intimacy_level,
                emotional_state=emotional_state,
                metrics=metrics,
                conversation_length=len(messages),
                response_times=response_times,
                key_emotions=key_emotions,
                satisfaction_indicators=satisfaction_indicators,
                warning_flags=warning_flags,
                recommendations=recommendations
            )
            
            # Geçmişe ekle
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            self.conversation_history[user_id].append(analysis)
            
            # İstatistikleri güncelle
            await self._update_stats(analysis)
            
            logger.info(f"🧬 Conversation analyzed",
                       user=user_id,
                       character=character_id,
                       eqs=eqs_score,
                       intimacy=intimacy_level.value,
                       state=emotional_state.value)
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing conversation: {e}")
            # Fallback analysis
            return self._create_fallback_analysis(user_id, character_id, len(messages))
    
    async def _calculate_emotional_metrics(
        self, 
        messages: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> EmotionalMetrics:
        """Duygusal metrikleri hesapla"""
        
        if not messages:
            return EmotionalMetrics()
        
        # Metin derinliği analizi
        text_depth = await self._analyze_text_depth(messages)
        
        # Yanıt kalitesi
        response_quality = await self._analyze_response_quality(messages)
        
        # Duygusal tutarlılık
        emotional_consistency = await self._analyze_emotional_consistency(messages)
        
        # Yakınlık ilerlemesi
        intimacy_progression = await self._analyze_intimacy_progression(messages)
        
        # Tatmin potansiyeli
        satisfaction_potential = await self._analyze_satisfaction_potential(messages)
        
        # Manipülasyon skoru
        manipulation_score = await self._analyze_manipulation_score(messages)
        
        return EmotionalMetrics(
            text_depth=text_depth,
            response_quality=response_quality,
            emotional_consistency=emotional_consistency,
            intimacy_progression=intimacy_progression,
            satisfaction_potential=satisfaction_potential,
            manipulation_score=manipulation_score
        )
    
    async def _analyze_text_depth(self, messages: List[Dict[str, Any]]) -> float:
        """Metin derinliği analizi"""
        if not messages:
            return 0.0
        
        depth_score = 0.0
        total_messages = 0
        
        for msg in messages:
            content = msg.get("content", "")
            if not content:
                continue
                
            total_messages += 1
            msg_score = 0.0
            
            # Uzunluk skoru (uzun mesajlar daha derin)
            length_score = min(len(content) / 200, 1.0)
            msg_score += length_score * 0.3
            
            # Duygusal kelimeler
            emotional_words = 0
            for pattern_list in self.emotional_patterns.values():
                for pattern in pattern_list:
                    emotional_words += len(re.findall(pattern, content.lower()))
            
            emotion_score = min(emotional_words / 5, 1.0)
            msg_score += emotion_score * 0.4
            
            # Soru ve etkileşim belirteci
            questions = len(re.findall(r'\?', content))
            interaction_score = min(questions / 3, 1.0)
            msg_score += interaction_score * 0.3
            
            depth_score += msg_score
        
        return depth_score / max(total_messages, 1)
    
    async def _analyze_response_quality(self, messages: List[Dict[str, Any]]) -> float:
        """Yanıt kalitesi analizi"""
        if len(messages) < 2:
            return 0.0
        
        quality_score = 0.0
        response_count = 0
        
        for i in range(1, len(messages)):
            current_msg = messages[i].get("content", "")
            previous_msg = messages[i-1].get("content", "")
            
            if not current_msg or not previous_msg:
                continue
            
            response_count += 1
            msg_quality = 0.0
            
            # Yanıt uygunluğu (önceki mesajla ilişki)
            common_words = set(current_msg.lower().split()) & set(previous_msg.lower().split())
            relevance_score = min(len(common_words) / 5, 1.0)
            msg_quality += relevance_score * 0.4
            
            # Özgünlük (tekrar eden cevaplar değil)
            uniqueness_score = 1.0  # Basit implementation
            msg_quality += uniqueness_score * 0.3
            
            # Duygusal tepki
            emotional_response = 0
            for emotion_list in self.intimacy_keywords.values():
                for emotion in emotion_list:
                    if emotion in current_msg.lower():
                        emotional_response += 1
            
            emotion_score = min(emotional_response / 3, 1.0)
            msg_quality += emotion_score * 0.3
            
            quality_score += msg_quality
        
        return quality_score / max(response_count, 1)
    
    async def _analyze_emotional_consistency(self, messages: List[Dict[str, Any]]) -> float:
        """Duygusal tutarlılık analizi"""
        if len(messages) < 3:
            return 0.5  # Yeterli veri yok
        
        emotional_tones = []
        
        for msg in messages:
            content = msg.get("content", "").lower()
            tone_score = 0.0
            
            # Pozitif duygular
            positive_patterns = [r"seviyorum", r"mutluyum", r"güzel", r"harika", r"mükemmel"]
            for pattern in positive_patterns:
                if re.search(pattern, content):
                    tone_score += 1
            
            # Negatif duygular
            negative_patterns = [r"üzgün", r"kızgın", r"sinirli", r"kötü", r"berbat"]
            for pattern in negative_patterns:
                if re.search(pattern, content):
                    tone_score -= 1
            
            emotional_tones.append(tone_score)
        
        # Tutarlılık hesapla (ani değişimler tutarsızlık)
        if len(emotional_tones) < 2:
            return 0.5
        
        changes = []
        for i in range(1, len(emotional_tones)):
            change = abs(emotional_tones[i] - emotional_tones[i-1])
            changes.append(change)
        
        avg_change = sum(changes) / len(changes)
        consistency = max(0.0, 1.0 - (avg_change / 3.0))  # 3+ değişim tutarsızlık
        
        return consistency
    
    async def _analyze_intimacy_progression(self, messages: List[Dict[str, Any]]) -> float:
        """Yakınlık ilerlemesi analizi"""
        if len(messages) < 3:
            return 0.0
        
        intimacy_scores = []
        
        for msg in messages:
            content = msg.get("content", "").lower()
            intimacy = 0.0
            
            # Yakınlık kelimelerini say
            for category, keywords in self.intimacy_keywords.items():
                for keyword in keywords:
                    if keyword in content:
                        intimacy += 1
            
            intimacy_scores.append(intimacy)
        
        # İlerleme hesapla
        if len(intimacy_scores) < 2:
            return 0.0
        
        progression = 0.0
        for i in range(1, len(intimacy_scores)):
            if intimacy_scores[i] > intimacy_scores[i-1]:
                progression += 1
            elif intimacy_scores[i] < intimacy_scores[i-1]:
                progression -= 0.5
        
        return max(0.0, min(1.0, progression / len(intimacy_scores)))
    
    async def _analyze_satisfaction_potential(self, messages: List[Dict[str, Any]]) -> float:
        """Tatmin potansiyeli analizi"""
        satisfaction_indicators = [
            r"tatmin", r"doyum", r"mutlu", r"rahat", r"huzur",
            r"zevk", r"keyif", r"memnun", r"başarı", r"tamamla"
        ]
        
        building_indicators = [
            r"geli\w*", r"artıyor", r"yükseliyor", r"daha\s*çok",
            r"devam", r"sürekli", r"uzun", r"derinleş"
        ]
        
        satisfaction_score = 0.0
        total_content = ""
        
        for msg in messages:
            content = msg.get("content", "").lower()
            total_content += " " + content
        
        # Tatmin belirteçleri
        for indicator in satisfaction_indicators:
            satisfaction_score += len(re.findall(indicator, total_content)) * 0.2
        
        # İnşa belirteçleri
        for indicator in building_indicators:
            satisfaction_score += len(re.findall(indicator, total_content)) * 0.15
        
        return min(1.0, satisfaction_score)
    
    async def _analyze_manipulation_score(self, messages: List[Dict[str, Any]]) -> float:
        """Manipülasyon skoru analizi (yüksek = kötü)"""
        manipulation_score = 0.0
        total_content = ""
        
        for msg in messages:
            content = msg.get("content", "").lower()
            total_content += " " + content
        
        # Manipülasyon belirteçleri
        for indicator in self.manipulation_indicators:
            manipulation_score += len(re.findall(indicator, total_content)) * 0.2
        
        # Pattern'lerdeki manipülasyon belirteçleri
        for pattern in self.emotional_patterns["manipulation_patterns"]:
            manipulation_score += len(re.findall(pattern, total_content)) * 0.3
        
        return min(1.0, manipulation_score)
    
    async def _calculate_eqs_score(
        self, 
        metrics: EmotionalMetrics, 
        messages: List[Dict[str, Any]]
    ) -> float:
        """EQS (Emotional Quality Score) hesapla"""
        
        # Ağırlıklı ortalama
        eqs = (
            metrics.text_depth * 0.20 +           # %20 metin derinliği
            metrics.response_quality * 0.25 +     # %25 yanıt kalitesi
            metrics.emotional_consistency * 0.15 + # %15 tutarlılık
            metrics.intimacy_progression * 0.20 +  # %20 yakınlık ilerlemesi
            metrics.satisfaction_potential * 0.20  # %20 tatmin potansiyeli
        )
        
        # Manipülasyon cezası
        manipulation_penalty = metrics.manipulation_score * 0.3
        eqs = max(0.0, eqs - manipulation_penalty)
        
        # Konuşma uzunluğu bonusu
        length_bonus = min(len(messages) / 50, 0.1)  # Max %10 bonus
        eqs = min(1.0, eqs + length_bonus)
        
        return round(eqs, 3)
    
    def _determine_intimacy_level(self, eqs_score: float, metrics: EmotionalMetrics) -> IntimacyLevel:
        """Yakınlık seviyesi belirle"""
        if eqs_score >= 0.8:
            return IntimacyLevel.DEEPLY_CONNECTED
        elif eqs_score >= 0.6:
            return IntimacyLevel.INTIMATE
        elif eqs_score >= 0.4:
            return IntimacyLevel.FRIEND
        elif eqs_score >= 0.2:
            return IntimacyLevel.ACQUAINTANCE
        else:
            return IntimacyLevel.STRANGER
    
    async def _detect_emotional_state(
        self, 
        messages: List[Dict[str, Any]], 
        metrics: EmotionalMetrics
    ) -> EmotionalState:
        """Duygusal durum tespit et"""
        
        # Manipülasyon yüksekse
        if metrics.manipulation_score > 0.6:
            return EmotionalState.MANIPULATIVE_BAIT
        
        # Tatmin potansiyeli yüksekse
        if metrics.satisfaction_potential > 0.7:
            return EmotionalState.SATISFACTION_BUILDING
        
        # Cinsel tension kontrol et
        sexual_content = ""
        for msg in messages:
            sexual_content += msg.get("content", "").lower()
        
        sexual_indicators = 0
        for pattern in self.emotional_patterns["sexual_tension_indicators"]:
            sexual_indicators += len(re.findall(pattern, sexual_content))
        
        if sexual_indicators > 3:
            return EmotionalState.SEXUAL_TENSION
        
        # EQS'e göre karar ver
        if metrics.text_depth > 0.6 and metrics.intimacy_progression > 0.5:
            return EmotionalState.GENUINE_INTIMACY
        elif metrics.response_quality > 0.4:
            return EmotionalState.SURFACE_FLIRT
        else:
            return EmotionalState.EMOTIONAL_VOID
    
    def _analyze_response_times(self, messages: List[Dict[str, Any]]) -> List[float]:
        """Yanıt sürelerini analiz et"""
        response_times = []
        
        for i in range(1, len(messages)):
            current_time = messages[i].get("timestamp")
            previous_time = messages[i-1].get("timestamp")
            
            if current_time and previous_time:
                try:
                    if isinstance(current_time, str):
                        current_time = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
                    if isinstance(previous_time, str):
                        previous_time = datetime.fromisoformat(previous_time.replace('Z', '+00:00'))
                    
                    diff = (current_time - previous_time).total_seconds()
                    response_times.append(diff)
                except:
                    continue
        
        return response_times
    
    async def _extract_key_emotions(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Anahtar duyguları çıkar"""
        emotions = []
        emotion_patterns = {
            "love": [r"sevgi", r"aşk", r"seviyorum"],
            "desire": [r"arzu", r"istek", r"istiyorum"],
            "happiness": [r"mutlu", r"sevin", r"neşe"],
            "sadness": [r"üzgün", r"kederli", r"hüzün"],
            "excitement": [r"heyecan", r"coşku", r"ateş"],
            "intimacy": [r"yakın", r"samimi", r"özel"]
        }
        
        all_content = " ".join(msg.get("content", "") for msg in messages).lower()
        
        for emotion, patterns in emotion_patterns.items():
            for pattern in patterns:
                if re.search(pattern, all_content):
                    emotions.append(emotion)
                    break
        
        return emotions
    
    async def _detect_satisfaction_indicators(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Tatmin göstergelerini tespit et"""
        indicators = []
        satisfaction_patterns = {
            "physical_satisfaction": [r"tatmin", r"doyum", r"rahatla"],
            "emotional_fulfillment": [r"tamamlan", r"bütünleş", r"huzur"],
            "anticipation_building": [r"bekli", r"merak", r"heyecan"],
            "progression_signs": [r"ilerliy", r"gelişiy", r"büyüyor"]
        }
        
        all_content = " ".join(msg.get("content", "") for msg in messages).lower()
        
        for indicator_type, patterns in satisfaction_patterns.items():
            for pattern in patterns:
                if re.search(pattern, all_content):
                    indicators.append(indicator_type)
                    break
        
        return indicators
    
    async def _check_warning_flags(
        self, 
        messages: List[Dict[str, Any]], 
        metrics: EmotionalMetrics
    ) -> List[str]:
        """Uyarı bayraklarını kontrol et"""
        warnings = []
        
        # Yüksek manipülasyon
        if metrics.manipulation_score > 0.7:
            warnings.append("High manipulation detected")
        
        # Düşük EQS
        if metrics.text_depth < 0.3 and metrics.response_quality < 0.3:
            warnings.append("Low emotional engagement")
        
        # Tutarsız duygusal ton
        if metrics.emotional_consistency < 0.3:
            warnings.append("Inconsistent emotional tone")
        
        # Yakınlık ilerlemesi yok
        if metrics.intimacy_progression < 0.1 and len(messages) > 10:
            warnings.append("No intimacy progression")
        
        # Tatmin potansiyeli düşük
        if metrics.satisfaction_potential < 0.2:
            warnings.append("Low satisfaction potential")
        
        return warnings
    
    async def _generate_recommendations(
        self, 
        eqs_score: float, 
        metrics: EmotionalMetrics, 
        warnings: List[str]
    ) -> List[str]:
        """Öneriler oluştur"""
        recommendations = []
        
        if eqs_score < 0.4:
            recommendations.append("Increase emotional depth and authenticity")
        
        if metrics.manipulation_score > 0.5:
            recommendations.append("Reduce manipulative tactics, focus on genuine connection")
        
        if metrics.intimacy_progression < 0.3:
            recommendations.append("Build intimacy gradually through personal sharing")
        
        if metrics.satisfaction_potential < 0.4:
            recommendations.append("Create more anticipation and satisfaction building")
        
        if not warnings:
            recommendations.append("Conversation quality is good, maintain current approach")
        
        return recommendations
    
    def _create_fallback_analysis(self, user_id: str, character_id: str, msg_count: int) -> ConversationAnalysis:
        """Hata durumunda fallback analiz"""
        return ConversationAnalysis(
            user_id=user_id,
            character_id=character_id,
            timestamp=datetime.now(),
            eqs_score=0.3,  # Orta seviye
            intimacy_level=IntimacyLevel.ACQUAINTANCE,
            emotional_state=EmotionalState.SURFACE_FLIRT,
            metrics=EmotionalMetrics(),
            conversation_length=msg_count,
            response_times=[],
            key_emotions=["neutral"],
            satisfaction_indicators=[],
            warning_flags=["Analysis failed"],
            recommendations=["Retry analysis with better data"]
        )
    
    async def _update_stats(self, analysis: ConversationAnalysis) -> None:
        """İstatistikleri güncelle"""
        self.daily_stats["total_analyzed"] += 1
        
        if analysis.emotional_state == EmotionalState.GENUINE_INTIMACY:
            self.daily_stats["genuine_intimacy_count"] += 1
        
        if analysis.metrics.manipulation_score > 0.6:
            self.daily_stats["manipulation_detected"] += 1
        
        # Ortalama EQS güncelle
        prev_avg = self.daily_stats["average_eqs"]
        total = self.daily_stats["total_analyzed"]
        new_avg = (prev_avg * (total - 1) + analysis.eqs_score) / total
        self.daily_stats["average_eqs"] = round(new_avg, 3)
        
        # Tatmin oranı
        if analysis.satisfaction_indicators:
            satisfaction_count = self.daily_stats.get("satisfaction_conversations", 0) + 1
            self.daily_stats["satisfaction_rate"] = satisfaction_count / total
            self.daily_stats["satisfaction_conversations"] = satisfaction_count
    
    async def get_user_emotional_profile(self, user_id: str) -> Dict[str, Any]:
        """Kullanıcının duygusal profili"""
        if user_id not in self.conversation_history:
            return {"error": "No conversation history found"}
        
        analyses = self.conversation_history[user_id]
        
        avg_eqs = sum(a.eqs_score for a in analyses) / len(analyses)
        
        # En sık görülen duygusal durum
        states = [a.emotional_state.value for a in analyses]
        most_common_state = max(set(states), key=states.count)
        
        # Yakınlık trendi
        eqs_scores = [a.eqs_score for a in analyses]
        if len(eqs_scores) > 1:
            trend = "improving" if eqs_scores[-1] > eqs_scores[0] else "declining"
        else:
            trend = "insufficient_data"
        
        return {
            "user_id": user_id,
            "total_conversations": len(analyses),
            "average_eqs": round(avg_eqs, 3),
            "most_common_emotional_state": most_common_state,
            "eqs_trend": trend,
            "latest_intimacy_level": analyses[-1].intimacy_level.value,
            "warning_flags": analyses[-1].warning_flags,
            "recommendations": analyses[-1].recommendations
        }
    
    def get_system_emotional_stats(self) -> Dict[str, Any]:
        """Sistem geneli duygusal istatistikler"""
        return {
            "daily_stats": self.daily_stats,
            "total_users_analyzed": len(self.conversation_history),
            "average_system_eqs": self.daily_stats["average_eqs"],
            "manipulation_detection_rate": (
                self.daily_stats["manipulation_detected"] / 
                max(self.daily_stats["total_analyzed"], 1)
            ),
            "genuine_intimacy_rate": (
                self.daily_stats["genuine_intimacy_count"] / 
                max(self.daily_stats["total_analyzed"], 1)
            )
        } 