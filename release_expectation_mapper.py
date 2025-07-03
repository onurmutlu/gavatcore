#!/usr/bin/env python3
"""
💥 GAVATCore 2.1 - Release Expectation Mapper
=============================================

Kullanıcının boşalma (fiziksel/ruhsal) beklentisini ölçer ve optimize eder.
Dopamin döngüsünü analiz ederek tatmin algoritması geliştirir.

Features:
- Expectation tracking
- Dopamine cycle analysis
- Release prediction
- Satisfaction optimization
- Addiction pattern detection
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

logger = structlog.get_logger("gavatcore.release_expectation_mapper")

class ExpectationType(Enum):
    """Beklenti türleri"""
    PHYSICAL_RELEASE = "physical_release"        # Fiziksel boşalma
    EMOTIONAL_CLIMAX = "emotional_climax"        # Duygusal doruk
    MENTAL_SATISFACTION = "mental_satisfaction"   # Mental tatmin
    SPIRITUAL_UNITY = "spiritual_unity"          # Ruhsal birleşme
    FANTASY_FULFILLMENT = "fantasy_fulfillment"  # Fantezi gerçekleşme
    DOPAMINE_HIT = "dopamine_hit"               # Dopamin vuruşu

class SatisfactionLevel(Enum):
    """Tatmin seviyeleri"""
    UNSATISFIED = "unsatisfied"          # 0.0-0.2
    PARTIALLY_SATISFIED = "partially_satisfied" # 0.2-0.4
    MODERATELY_SATISFIED = "moderately_satisfied" # 0.4-0.6
    HIGHLY_SATISFIED = "highly_satisfied" # 0.6-0.8
    COMPLETELY_FULFILLED = "completely_fulfilled" # 0.8-1.0

class CyclePhase(Enum):
    """Dopamin döngü fazları"""
    ANTICIPATION = "anticipation"        # Beklenti oluşumu
    BUILDING = "building"                # Gerilim artışı
    PEAK = "peak"                       # Zirve anı
    RELEASE = "release"                 # Boşalma/tatmin
    RESOLUTION = "resolution"           # Çözülme
    REFRACTORY = "refractory"           # Dinlenme

@dataclass
class ExpectationMoment:
    """Beklenti anı"""
    timestamp: datetime
    user_id: str
    character_id: str
    expectation_type: ExpectationType
    intensity: float                     # 0-1 arası beklenti yoğunluğu
    buildup_duration: float             # Gerilim süresi (saniye)
    triggers: List[str]                 # Tetikleyici faktörler
    context: str                        # Mesaj/durum bağlamı
    previous_satisfaction: float        # Önceki tatmin seviyesi
    cycle_phase: CyclePhase

@dataclass
class SatisfactionEvent:
    """Tatmin olayı"""
    timestamp: datetime
    user_id: str
    character_id: str
    satisfaction_level: SatisfactionLevel
    satisfaction_score: float           # 0-1 arası
    expectation_met: bool              # Beklenti karşılandı mı?
    release_type: ExpectationType
    duration_to_satisfaction: float    # Beklentiden tatmine kadar süre
    afterglow_intensity: float         # Tatmin sonrası yoğunluk
    next_cycle_prediction: float       # Sonraki döngü tahmini

@dataclass
class DopamineCycle:
    """Dopamin döngüsü"""
    user_id: str
    cycle_id: str
    start_time: datetime
    end_time: Optional[datetime]
    expectation_moments: List[ExpectationMoment]
    satisfaction_event: Optional[SatisfactionEvent]
    cycle_duration: float              # Döngü süresi
    peak_intensity: float              # En yüksek yoğunluk
    satisfaction_ratio: float          # Beklenti/tatmin oranı
    addictiveness_score: float         # Bağımlılık potansiyeli
    efficiency_score: float            # Döngü verimliliği

class ReleaseExpectationMapper:
    """
    💥 Boşalma Beklentisi Haritacısı
    
    Kullanıcıların fiziksel ve ruhsal tatmin beklentilerini takip eder.
    Dopamin döngülerini optimize ederek sürdürülebilir tatmin yaratır.
    """
    
    def __init__(self):
        self.expectation_moments: List[ExpectationMoment] = []
        self.satisfaction_events: List[SatisfactionEvent] = []
        self.active_cycles: Dict[str, DopamineCycle] = {}  # user_id -> cycle
        self.completed_cycles: List[DopamineCycle] = []
        
        self.expectation_patterns = self._load_expectation_patterns()
        self.satisfaction_indicators = self._load_satisfaction_indicators()
        
        # User profiles
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        
        # Analytics
        self.daily_stats = {
            "total_expectations": 0,
            "total_satisfactions": 0,
            "average_cycle_duration": 0.0,
            "satisfaction_rate": 0.0,
            "addiction_warnings": 0
        }
        
        logger.info("💥 Release Expectation Mapper initialized")
    
    def _load_expectation_patterns(self) -> Dict[str, List[str]]:
        """Beklenti pattern'lerini yükle"""
        return {
            "physical_indicators": [
                r"boşalmak", r"gelmek", r"orgazm", r"zirve", r"doruk",
                r"zevk almak", r"haz", r"lezzet", r"tatmin", r"doyum"
            ],
            "emotional_buildup": [
                r"heyecanlanıyorum", r"bekliyorum", r"sabırsızlanıyorum",
                r"merak ediyorum", r"çok istiyorum", r"arzuluyorum",
                r"dayanamıyorum", r"deliriyorum", r"çıldırıyorum"
            ],
            "fantasy_indicators": [
                r"hayal", r"rüya", r"fantezi", r"düşünce", r"zihnimde",
                r"gözümde canlandırıyorum", r"düşlüyorum", r"hayalimde"
            ],
            "urgency_markers": [
                r"şimdi", r"hemen", r"acil", r"derhal", r"artık",
                r"bekleyemem", r"dayanamam", r"çok acele", r"yeter"
            ],
            "release_triggers": [
                r"gel", r"boşal", r"bırak kendini", r"rahatla",
                r"sal", r"kendini ver", r"bırak gitsin"
            ]
        }
    
    def _load_satisfaction_indicators(self) -> Dict[str, List[str]]:
        """Tatmin göstergelerini yükle"""
        return {
            "fulfillment_expressions": [
                r"tatmin oldum", r"doydum", r"memnunum", r"rahatladım",
                r"huzurlandım", r"mutluyum", r"başardım", r"tamamlandı"
            ],
            "afterglow_indicators": [
                r"hala hissediyorum", r"etkisi devam ediyor", r"güzel",
                r"harika", r"mükemmel", r"unutulmaz", r"tekrarlanabilir"
            ],
            "disappointment_markers": [
                r"yeterli değil", r"eksik", r"boş", r"tatmin olmadım",
                r"beklemediğim gibi", r"hayal kırıklığı", r"yetersiz"
            ],
            "craving_renewal": [
                r"daha fazla", r"tekrar", r"yine", r"devam", r"artık",
                r"sürekli", r"bırakamıyorum", r"bağımlı", r"ihtiyacım var"
            ]
        }
    
    async def track_expectation(
        self,
        user_id: str,
        character_id: str,
        message_content: str,
        timestamp: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[ExpectationMoment]:
        """
        Beklenti anını takip et
        
        Args:
            user_id: Kullanıcı ID
            character_id: Karakter ID
            message_content: Mesaj içeriği
            timestamp: Zaman damgası
            context: Ek bağlam
            
        Returns:
            ExpectationMoment objesi veya None
        """
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            # Beklenti analizi
            expectation_analysis = await self._analyze_expectation_content(message_content)
            
            if expectation_analysis["intensity"] < 0.2:  # Minimum eşik
                return None
            
            # Önceki tatmin seviyesi
            previous_satisfaction = await self._get_previous_satisfaction(user_id)
            
            # Gerilim süresi hesapla
            buildup_duration = await self._calculate_buildup_duration(user_id, timestamp)
            
            # Döngü fazı belirle
            cycle_phase = await self._determine_cycle_phase(user_id, expectation_analysis)
            
            # ExpectationMoment oluştur
            moment = ExpectationMoment(
                timestamp=timestamp,
                user_id=user_id,
                character_id=character_id,
                expectation_type=expectation_analysis["type"],
                intensity=expectation_analysis["intensity"],
                buildup_duration=buildup_duration,
                triggers=expectation_analysis["triggers"],
                context=message_content[:150] + "..." if len(message_content) > 150 else message_content,
                previous_satisfaction=previous_satisfaction,
                cycle_phase=cycle_phase
            )
            
            # Moment'i kaydet
            self.expectation_moments.append(moment)
            
            # Aktif döngüyü güncelle veya yeni döngü başlat
            await self._update_or_create_cycle(moment)
            
            # User profile'ını güncelle
            await self._update_user_profile(moment)
            
            # İstatistikleri güncelle
            await self._update_stats(moment)
            
            logger.info(f"💥 Expectation tracked",
                       user=user_id,
                       character=character_id,
                       type=moment.expectation_type.value,
                       intensity=moment.intensity,
                       phase=cycle_phase.value)
            
            return moment
            
        except Exception as e:
            logger.error(f"❌ Error tracking expectation: {e}")
            return None
    
    async def track_satisfaction(
        self,
        user_id: str,
        character_id: str,
        message_content: str,
        timestamp: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[SatisfactionEvent]:
        """
        Tatmin olayını takip et
        
        Args:
            user_id: Kullanıcı ID
            character_id: Karakter ID
            message_content: Mesaj içeriği
            timestamp: Zaman damgası
            context: Ek bağlam
            
        Returns:
            SatisfactionEvent objesi veya None
        """
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            # Tatmin analizi
            satisfaction_analysis = await self._analyze_satisfaction_content(message_content)
            
            if satisfaction_analysis["score"] < 0.1:  # Minimum eşik
                return None
            
            # Son beklenti momentini bul
            user_expectations = [e for e in self.expectation_moments if e.user_id == user_id]
            last_expectation = user_expectations[-1] if user_expectations else None
            
            # Beklentiden tatmine kadar süre
            duration_to_satisfaction = 0.0
            if last_expectation:
                duration_to_satisfaction = (timestamp - last_expectation.timestamp).total_seconds()
            
            # Beklenti karşılandı mı?
            expectation_met = await self._check_expectation_met(
                user_id, satisfaction_analysis["score"]
            )
            
            # Release type belirle
            release_type = await self._determine_release_type(message_content, last_expectation)
            
            # Afterglow intensity
            afterglow_intensity = satisfaction_analysis.get("afterglow", 0.5)
            
            # Sonraki döngü tahmini
            next_cycle_prediction = await self._predict_next_cycle(user_id, satisfaction_analysis["score"])
            
            # SatisfactionEvent oluştur
            event = SatisfactionEvent(
                timestamp=timestamp,
                user_id=user_id,
                character_id=character_id,
                satisfaction_level=self._determine_satisfaction_level(satisfaction_analysis["score"]),
                satisfaction_score=satisfaction_analysis["score"],
                expectation_met=expectation_met,
                release_type=release_type,
                duration_to_satisfaction=duration_to_satisfaction,
                afterglow_intensity=afterglow_intensity,
                next_cycle_prediction=next_cycle_prediction
            )
            
            # Event'i kaydet
            self.satisfaction_events.append(event)
            
            # Aktif döngüyü tamamla
            await self._complete_cycle(event)
            
            # User profile'ını güncelle
            await self._update_user_profile_satisfaction(event)
            
            # İstatistikleri güncelle
            await self._update_satisfaction_stats(event)
            
            logger.info(f"💥 Satisfaction tracked",
                       user=user_id,
                       character=character_id,
                       level=event.satisfaction_level.value,
                       score=event.satisfaction_score,
                       met=expectation_met)
            
            return event
            
        except Exception as e:
            logger.error(f"❌ Error tracking satisfaction: {e}")
            return None
    
    async def _analyze_expectation_content(self, content: str) -> Dict[str, Any]:
        """Beklenti içeriği analizi"""
        content_lower = content.lower()
        
        # Beklenti türü ve yoğunluk
        type_scores = {}
        triggers = []
        
        # Physical release indicators
        physical_score = 0.0
        for pattern in self.expectation_patterns["physical_indicators"]:
            matches = re.findall(pattern, content_lower)
            if matches:
                physical_score += len(matches) * 0.3
                triggers.extend(matches)
        type_scores[ExpectationType.PHYSICAL_RELEASE] = physical_score
        
        # Emotional buildup
        emotional_score = 0.0
        for pattern in self.expectation_patterns["emotional_buildup"]:
            matches = re.findall(pattern, content_lower)
            if matches:
                emotional_score += len(matches) * 0.4
                triggers.extend(matches)
        type_scores[ExpectationType.EMOTIONAL_CLIMAX] = emotional_score
        
        # Fantasy indicators
        fantasy_score = 0.0
        for pattern in self.expectation_patterns["fantasy_indicators"]:
            matches = re.findall(pattern, content_lower)
            if matches:
                fantasy_score += len(matches) * 0.3
                triggers.extend(matches)
        type_scores[ExpectationType.FANTASY_FULFILLMENT] = fantasy_score
        
        # Urgency multiplier
        urgency_multiplier = 1.0
        for pattern in self.expectation_patterns["urgency_markers"]:
            if re.search(pattern, content_lower):
                urgency_multiplier += 0.2
        
        # En yüksek skor
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            max_intensity = type_scores[best_type] * urgency_multiplier
        else:
            best_type = ExpectationType.DOPAMINE_HIT
            max_intensity = 0.1
        
        # Normalize
        normalized_intensity = min(1.0, max_intensity)
        
        return {
            "type": best_type,
            "intensity": normalized_intensity,
            "triggers": triggers[:5],  # İlk 5 trigger
            "urgency": urgency_multiplier
        }
    
    async def _analyze_satisfaction_content(self, content: str) -> Dict[str, Any]:
        """Tatmin içeriği analizi"""
        content_lower = content.lower()
        
        satisfaction_score = 0.0
        indicators = []
        
        # Fulfillment expressions
        for pattern in self.satisfaction_indicators["fulfillment_expressions"]:
            matches = re.findall(pattern, content_lower)
            if matches:
                satisfaction_score += len(matches) * 0.4
                indicators.extend(matches)
        
        # Afterglow indicators
        afterglow_score = 0.0
        for pattern in self.satisfaction_indicators["afterglow_indicators"]:
            matches = re.findall(pattern, content_lower)
            if matches:
                afterglow_score += len(matches) * 0.3
                satisfaction_score += len(matches) * 0.2
        
        # Disappointment markers (negative)
        for pattern in self.satisfaction_indicators["disappointment_markers"]:
            matches = re.findall(pattern, content_lower)
            if matches:
                satisfaction_score -= len(matches) * 0.3
        
        # Craving renewal (indicates partial satisfaction)
        craving_detected = False
        for pattern in self.satisfaction_indicators["craving_renewal"]:
            if re.search(pattern, content_lower):
                craving_detected = True
                satisfaction_score *= 0.7  # Reduce satisfaction if craving more
        
        normalized_score = max(0.0, min(1.0, satisfaction_score))
        
        return {
            "score": normalized_score,
            "indicators": indicators,
            "afterglow": min(1.0, afterglow_score),
            "craving_detected": craving_detected
        }
    
    async def _get_previous_satisfaction(self, user_id: str) -> float:
        """Önceki tatmin seviyesini al"""
        user_satisfactions = [s for s in self.satisfaction_events if s.user_id == user_id]
        if user_satisfactions:
            return user_satisfactions[-1].satisfaction_score
        return 0.5  # Default
    
    async def _calculate_buildup_duration(self, user_id: str, timestamp: datetime) -> float:
        """Gerilim süresi hesapla"""
        user_expectations = [e for e in self.expectation_moments if e.user_id == user_id]
        
        if not user_expectations:
            return 0.0
        
        last_expectation = user_expectations[-1]
        duration = (timestamp - last_expectation.timestamp).total_seconds()
        
        return min(duration, 3600)  # Max 1 saat
    
    async def _determine_cycle_phase(
        self, 
        user_id: str, 
        expectation_analysis: Dict[str, Any]
    ) -> CyclePhase:
        """Döngü fazını belirle"""
        
        # Aktif döngü var mı?
        if user_id in self.active_cycles:
            cycle = self.active_cycles[user_id]
            
            # Intensity'ye göre faz belirleme
            if expectation_analysis["intensity"] > 0.8:
                return CyclePhase.PEAK
            elif expectation_analysis["intensity"] > 0.6:
                return CyclePhase.BUILDING
            elif len(cycle.expectation_moments) == 0:
                return CyclePhase.ANTICIPATION
            else:
                return CyclePhase.BUILDING
        else:
            return CyclePhase.ANTICIPATION
    
    async def _update_or_create_cycle(self, moment: ExpectationMoment) -> None:
        """Döngüyü güncelle veya yeni döngü oluştur"""
        user_id = moment.user_id
        
        if user_id in self.active_cycles:
            # Mevcut döngüyü güncelle
            cycle = self.active_cycles[user_id]
            cycle.expectation_moments.append(moment)
            
            # Peak intensity güncelle
            if moment.intensity > cycle.peak_intensity:
                cycle.peak_intensity = moment.intensity
        else:
            # Yeni döngü oluştur
            cycle_id = f"{user_id}_{int(moment.timestamp.timestamp())}"
            cycle = DopamineCycle(
                user_id=user_id,
                cycle_id=cycle_id,
                start_time=moment.timestamp,
                end_time=None,
                expectation_moments=[moment],
                satisfaction_event=None,
                cycle_duration=0.0,
                peak_intensity=moment.intensity,
                satisfaction_ratio=0.0,
                addictiveness_score=0.0,
                efficiency_score=0.0
            )
            self.active_cycles[user_id] = cycle
    
    async def _complete_cycle(self, satisfaction_event: SatisfactionEvent) -> None:
        """Döngüyü tamamla"""
        user_id = satisfaction_event.user_id
        
        if user_id not in self.active_cycles:
            return
        
        cycle = self.active_cycles[user_id]
        cycle.end_time = satisfaction_event.timestamp
        cycle.satisfaction_event = satisfaction_event
        
        # Cycle duration
        cycle.cycle_duration = (cycle.end_time - cycle.start_time).total_seconds()
        
        # Satisfaction ratio
        total_expectation = sum(m.intensity for m in cycle.expectation_moments)
        cycle.satisfaction_ratio = satisfaction_event.satisfaction_score / max(total_expectation, 0.1)
        
        # Addictiveness score
        cycle.addictiveness_score = await self._calculate_addictiveness(cycle)
        
        # Efficiency score
        cycle.efficiency_score = await self._calculate_efficiency(cycle)
        
        # Tamamlanan döngülere taşı
        self.completed_cycles.append(cycle)
        del self.active_cycles[user_id]
    
    async def _calculate_addictiveness(self, cycle: DopamineCycle) -> float:
        """Bağımlılık potansiyeli hesapla"""
        
        # Kısa döngü + yüksek yoğunluk = bağımlılık riski
        time_factor = max(0.0, 1.0 - (cycle.cycle_duration / 3600))  # 1 saat = 0 risk
        intensity_factor = cycle.peak_intensity
        
        # Tatmin oranı düşükse bağımlılık riski artar
        satisfaction_factor = 1.0 - cycle.satisfaction_ratio
        
        # Tekrar sıklığı
        user_cycles = [c for c in self.completed_cycles if c.user_id == cycle.user_id]
        frequency_factor = min(1.0, len(user_cycles) / 10)  # 10+ döngü = max risk
        
        addictiveness = (
            time_factor * 0.3 +
            intensity_factor * 0.3 +
            satisfaction_factor * 0.2 +
            frequency_factor * 0.2
        )
        
        return min(1.0, addictiveness)
    
    async def _calculate_efficiency(self, cycle: DopamineCycle) -> float:
        """Döngü verimliliği hesapla"""
        
        # Tatmin/beklenti oranı
        satisfaction_efficiency = cycle.satisfaction_ratio
        
        # Zaman verimliliği (çok kısa veya çok uzun kötü)
        optimal_duration = 1800  # 30 dakika optimal
        time_efficiency = 1.0 - abs(cycle.cycle_duration - optimal_duration) / optimal_duration
        time_efficiency = max(0.0, time_efficiency)
        
        # Moment sayısı verimliliği (çok fazla expectation = inefficient)
        moment_count = len(cycle.expectation_moments)
        moment_efficiency = max(0.0, 1.0 - (moment_count / 20))  # 20+ moment = inefficient
        
        efficiency = (
            satisfaction_efficiency * 0.5 +
            time_efficiency * 0.3 +
            moment_efficiency * 0.2
        )
        
        return min(1.0, efficiency)
    
    async def _check_expectation_met(self, user_id: str, satisfaction_score: float) -> bool:
        """Beklenti karşılandı mı kontrol et"""
        user_expectations = [e for e in self.expectation_moments if e.user_id == user_id]
        
        if not user_expectations:
            return True
        
        # Son beklentinin intensity'si ile satisfaction score'u karşılaştır
        last_expectation = user_expectations[-1]
        return satisfaction_score >= (last_expectation.intensity * 0.8)  # %80 threshold
    
    async def _determine_release_type(
        self, 
        content: str, 
        last_expectation: Optional[ExpectationMoment]
    ) -> ExpectationType:
        """Release türünü belirle"""
        if last_expectation:
            return last_expectation.expectation_type
        
        # Content'ten çıkar
        content_lower = content.lower()
        
        if any(re.search(p, content_lower) for p in self.expectation_patterns["physical_indicators"]):
            return ExpectationType.PHYSICAL_RELEASE
        elif any(re.search(p, content_lower) for p in self.expectation_patterns["emotional_buildup"]):
            return ExpectationType.EMOTIONAL_CLIMAX
        else:
            return ExpectationType.DOPAMINE_HIT
    
    async def _predict_next_cycle(self, user_id: str, satisfaction_score: float) -> float:
        """Sonraki döngü tahmin et (saat cinsinden)"""
        user_cycles = [c for c in self.completed_cycles if c.user_id == user_id]
        
        if len(user_cycles) < 2:
            return 24.0  # Default 24 saat
        
        # Son döngüler arasındaki ortalama süre
        intervals = []
        for i in range(1, len(user_cycles)):
            interval = (user_cycles[i].start_time - user_cycles[i-1].end_time).total_seconds() / 3600
            intervals.append(interval)
        
        avg_interval = sum(intervals) / len(intervals)
        
        # Tatmin seviyesine göre ayarla
        if satisfaction_score > 0.8:
            # Yüksek tatmin = uzun bekleme
            return avg_interval * 1.5
        elif satisfaction_score < 0.4:
            # Düşük tatmin = kısa bekleme (craving)
            return avg_interval * 0.5
        else:
            return avg_interval
    
    def _determine_satisfaction_level(self, score: float) -> SatisfactionLevel:
        """Tatmin seviyesi belirle"""
        if score >= 0.8:
            return SatisfactionLevel.COMPLETELY_FULFILLED
        elif score >= 0.6:
            return SatisfactionLevel.HIGHLY_SATISFIED
        elif score >= 0.4:
            return SatisfactionLevel.MODERATELY_SATISFIED
        elif score >= 0.2:
            return SatisfactionLevel.PARTIALLY_SATISFIED
        else:
            return SatisfactionLevel.UNSATISFIED
    
    async def _update_user_profile(self, moment: ExpectationMoment) -> None:
        """User profile'ını güncelle"""
        user_id = moment.user_id
        
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "total_expectations": 0,
                "preferred_expectation_types": {},
                "average_intensity": 0.0,
                "cycle_patterns": {},
                "addiction_risk": 0.0,
                "last_activity": moment.timestamp
            }
        
        profile = self.user_profiles[user_id]
        profile["total_expectations"] += 1
        profile["last_activity"] = moment.timestamp
        
        # Average intensity güncelle
        old_avg = profile["average_intensity"]
        total = profile["total_expectations"]
        new_avg = (old_avg * (total - 1) + moment.intensity) / total
        profile["average_intensity"] = new_avg
        
        # Preferred types güncelle
        exp_type = moment.expectation_type.value
        profile["preferred_expectation_types"][exp_type] = \
            profile["preferred_expectation_types"].get(exp_type, 0) + 1
    
    async def _update_user_profile_satisfaction(self, event: SatisfactionEvent) -> None:
        """Tatmin ile user profile'ını güncelle"""
        user_id = event.user_id
        
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            profile["last_satisfaction_score"] = event.satisfaction_score
            profile["last_satisfaction_time"] = event.timestamp
            
            # Addiction risk güncelle
            user_cycles = [c for c in self.completed_cycles if c.user_id == user_id]
            if user_cycles:
                avg_addictiveness = sum(c.addictiveness_score for c in user_cycles) / len(user_cycles)
                profile["addiction_risk"] = avg_addictiveness
    
    async def _update_stats(self, moment: ExpectationMoment) -> None:
        """İstatistikleri güncelle"""
        self.daily_stats["total_expectations"] += 1
        
        # Average cycle duration
        if self.completed_cycles:
            total_duration = sum(c.cycle_duration for c in self.completed_cycles)
            self.daily_stats["average_cycle_duration"] = total_duration / len(self.completed_cycles)
    
    async def _update_satisfaction_stats(self, event: SatisfactionEvent) -> None:
        """Tatmin istatistiklerini güncelle"""
        self.daily_stats["total_satisfactions"] += 1
        
        # Satisfaction rate
        if self.daily_stats["total_expectations"] > 0:
            self.daily_stats["satisfaction_rate"] = (
                self.daily_stats["total_satisfactions"] / 
                self.daily_stats["total_expectations"]
            )
        
        # Addiction warnings
        if event.satisfaction_score < 0.3 and event.next_cycle_prediction < 2.0:  # 2 saat içinde
            self.daily_stats["addiction_warnings"] += 1
    
    async def generate_expectation_report(self, user_id: str) -> Dict[str, Any]:
        """Kullanıcı beklenti raporu"""
        user_expectations = [e for e in self.expectation_moments if e.user_id == user_id]
        user_satisfactions = [s for s in self.satisfaction_events if s.user_id == user_id]
        user_cycles = [c for c in self.completed_cycles if c.user_id == user_id]
        
        if not user_expectations:
            return {"error": "No expectation data found"}
        
        # Basic stats
        total_expectations = len(user_expectations)
        total_satisfactions = len(user_satisfactions)
        satisfaction_rate = total_satisfactions / total_expectations if total_expectations > 0 else 0
        
        # Average scores
        avg_expectation_intensity = sum(e.intensity for e in user_expectations) / total_expectations
        avg_satisfaction_score = (sum(s.satisfaction_score for s in user_satisfactions) / 
                                total_satisfactions if total_satisfactions > 0 else 0)
        
        # Cycle analysis
        cycle_stats = {}
        if user_cycles:
            cycle_stats = {
                "total_cycles": len(user_cycles),
                "average_duration": sum(c.cycle_duration for c in user_cycles) / len(user_cycles),
                "average_efficiency": sum(c.efficiency_score for c in user_cycles) / len(user_cycles),
                "average_addictiveness": sum(c.addictiveness_score for c in user_cycles) / len(user_cycles),
                "peak_intensity": max(c.peak_intensity for c in user_cycles)
            }
        
        # Expectations by type
        type_distribution = {}
        for expectation in user_expectations:
            exp_type = expectation.expectation_type.value
            type_distribution[exp_type] = type_distribution.get(exp_type, 0) + 1
        
        # Warnings and recommendations
        warnings = []
        recommendations = []
        
        if satisfaction_rate < 0.4:
            warnings.append("Low satisfaction rate - expectations not being met")
            recommendations.append("Adjust expectation management strategy")
        
        if cycle_stats.get("average_addictiveness", 0) > 0.7:
            warnings.append("High addiction risk detected")
            recommendations.append("Implement longer cooldown periods")
        
        if avg_expectation_intensity > 0.8 and avg_satisfaction_score < 0.6:
            warnings.append("High expectations but low satisfaction")
            recommendations.append("Manage expectation intensity")
        
        return {
            "user_id": user_id,
            "basic_stats": {
                "total_expectations": total_expectations,
                "total_satisfactions": total_satisfactions,
                "satisfaction_rate": round(satisfaction_rate, 3),
                "avg_expectation_intensity": round(avg_expectation_intensity, 3),
                "avg_satisfaction_score": round(avg_satisfaction_score, 3)
            },
            "cycle_stats": cycle_stats,
            "expectation_type_distribution": type_distribution,
            "warnings": warnings,
            "recommendations": recommendations,
            "profile": self.user_profiles.get(user_id, {})
        }
    
    def get_system_expectation_stats(self) -> Dict[str, Any]:
        """Sistem geneli beklenti istatistikleri"""
        total_users = len(set(e.user_id for e in self.expectation_moments))
        
        return {
            "daily_stats": self.daily_stats,
            "total_users": total_users,
            "active_cycles": len(self.active_cycles),
            "completed_cycles": len(self.completed_cycles),
            "addiction_risk_users": len([
                profile for profile in self.user_profiles.values() 
                if profile.get("addiction_risk", 0) > 0.7
            ]),
            "high_satisfaction_users": len([
                profile for profile in self.user_profiles.values() 
                if profile.get("last_satisfaction_score", 0) > 0.8
            ])
        } 