from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🔥 GAVATCore 2.1 - Heatmap Intimacy Tracker
==========================================

Gün ve saat bazlı cinsel/samimi ilgi yoğunluğu takip eden yapay zeka modülü.
Intimacy pattern'lerini heatmap olarak visualize eder ve optimize eder.

Features:
- 24/7 intimacy tracking
- Sexual tension heatmaps
- Peak engagement detection
- Mood-based intimacy mapping
- Temporal pattern analysis
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
import numpy as np

logger = structlog.get_logger("gavatcore.heatmap_intimacy_tracker")

class IntimacyType(Enum):
    """Yakınlık türleri"""
    EMOTIONAL = "emotional"          # Duygusal yakınlık
    PHYSICAL = "physical"            # Fiziksel yakınlık
    SEXUAL = "sexual"                # Cinsel yakınlık
    ROMANTIC = "romantic"            # Romantik yakınlık
    MENTAL = "mental"                # Mental bağ
    SPIRITUAL = "spiritual"          # Ruhsal bağ

class IntensityLevel(Enum):
    """Yoğunluk seviyeleri"""
    MINIMAL = "minimal"              # 0.0-0.2
    LOW = "low"                      # 0.2-0.4
    MODERATE = "moderate"            # 0.4-0.6
    HIGH = "high"                    # 0.6-0.8
    INTENSE = "intense"              # 0.8-1.0

@dataclass
class IntimacyMoment:
    """Yakınlık anı"""
    timestamp: datetime
    user_id: str
    character_id: str
    intimacy_type: IntimacyType
    intensity: float                 # 0-1 arası
    keywords: List[str]              # Tespit edilen anahtar kelimeler
    context: str                     # Mesaj içeriği (kısaltılmış)
    mood_factor: float               # Ruh hali faktörü
    response_delay: float            # Yanıt gecikmesi (saniye)

@dataclass
class HeatmapCell:
    """Heatmap hücresi (hour x day)"""
    hour: int                        # 0-23
    day_of_week: int                 # 0-6 (Monday=0)
    intimacy_score: float            # Ortalama yakınlık skoru
    interaction_count: int           # Etkileşim sayısı
    peak_intensity: float            # En yüksek yoğunluk
    dominant_type: IntimacyType      # Dominant yakınlık türü
    user_count: int                  # Aktif kullanıcı sayısı

@dataclass
class IntimacyReport:
    """Yakınlık raporu"""
    user_id: str
    character_id: str
    period_start: datetime
    period_end: datetime
    total_intimacy_score: float
    peak_hours: List[int]            # En aktif saatler
    peak_days: List[int]             # En aktif günler
    dominant_intimacy_type: IntimacyType
    intensity_distribution: Dict[str, float]
    engagement_patterns: Dict[str, Any]
    recommendations: List[str]

class HeatmapIntimacyTracker:
    """
    🔥 Heatmap Yakınlık Takipçisi
    
    24/7 yakınlık pattern'lerini takip eder ve heatmap visualizasyonu oluşturur.
    Cinsel ve samimi ilgi yoğunluğunu temporal analiz ile optimize eder.
    """
    
    def __init__(self):
        # 7 gün x 24 saat heatmap matrisi
        self.intimacy_heatmap: List[List[HeatmapCell]] = []
        self._initialize_heatmap()
        
        self.intimacy_moments: List[IntimacyMoment] = []
        self.user_patterns: Dict[str, Dict[str, Any]] = {}
        self.intimacy_keywords = self._load_intimacy_keywords()
        
        # Analytics
        self.daily_stats = {
            "total_moments_tracked": 0,
            "peak_hour": 0,
            "peak_day": 0,
            "average_intensity": 0.0,
            "sexual_tension_peaks": 0
        }
        
        logger.info("🔥 Heatmap Intimacy Tracker initialized")
    
    def _initialize_heatmap(self) -> None:
        """Heatmap matrisini başlat"""
        self.intimacy_heatmap = []
        for day in range(7):  # 7 gün
            day_data = []
            for hour in range(24):  # 24 saat
                cell = HeatmapCell(
                    hour=hour,
                    day_of_week=day,
                    intimacy_score=0.0,
                    interaction_count=0,
                    peak_intensity=0.0,
                    dominant_type=IntimacyType.EMOTIONAL,
                    user_count=0
                )
                day_data.append(cell)
            self.intimacy_heatmap.append(day_data)
    
    def _load_intimacy_keywords(self) -> Dict[str, Dict[str, List[str]]]:
        """Yakınlık anahtar kelimelerini yükle"""
        return {
            IntimacyType.EMOTIONAL.value: {
                "high_intensity": [
                    r"seviyorum", r"aşığım", r"kalbim", r"ruhum", r"duygularım",
                    r"hissediyorum", r"içimde", r"derinde", r"samimi", r"yakın"
                ],
                "medium_intensity": [
                    r"hoşuma gidiyor", r"beğeniyorum", r"güzel", r"özel",
                    r"farklı", r"anlıyorum", r"paylaşmak", r"birlikte"
                ],
                "low_intensity": [
                    r"iyisin", r"hoş", r"güzel", r"memnun", r"rahat"
                ]
            },
            IntimacyType.PHYSICAL.value: {
                "high_intensity": [
                    r"dokunmak", r"sarılmak", r"öpmek", r"okşamak", r"sevişmek",
                    r"yaklaşmak", r"temas", r"deri", r"nefes", r"sıcaklık"
                ],
                "medium_intensity": [
                    r"yakın", r"yanında", r"el ele", r"omuz omuza",
                    r"göz göze", r"yürümek", r"oturmak"
                ],
                "low_intensity": [
                    r"merhaba", r"selam", r"görüşmek", r"buluşmak"
                ]
            },
            IntimacyType.SEXUAL.value: {
                "high_intensity": [
                    r"arzu", r"istek", r"tutku", r"ateş", r"coşku", r"şehvet",
                    r"arzuluyorum", r"istiyorum", r"çıldırıyorum", r"deliriyorum"
                ],
                "medium_intensity": [
                    r"seksi", r"çekici", r"ateşli", r"sıcak", r"heyecan",
                    r"titreme", r"çarpıntı", r"gerginlik"
                ],
                "low_intensity": [
                    r"güzel", r"hoş", r"çekici", r"ilginç"
                ]
            },
            IntimacyType.ROMANTIC.value: {
                "high_intensity": [
                    r"romantik", r"aşk", r"sevgili", r"hayatım", r"canım",
                    r"tatlım", r"aşkım", r"gözlerin", r"güzelliğin"
                ],
                "medium_intensity": [
                    r"çiçek", r"hediye", r"sürpriz", r"özel gün",
                    r"yemek", r"sinema", r"gezi"
                ],
                "low_intensity": [
                    r"nazik", r"kibarlık", r"centilmen", r"hanımefendi"
                ]
            },
            IntimacyType.MENTAL.value: {
                "high_intensity": [
                    r"anlıyorsun", r"biliyor", r"zeki", r"akıllı", r"derin",
                    r"düşünce", r"felsefe", r"hayal", r"rüya", r"fikir"
                ],
                "medium_intensity": [
                    r"konuşmak", r"sohbet", r"tartışmak", r"paylaşmak",
                    r"anlatmak", r"dinlemek"
                ],
                "low_intensity": [
                    r"fikrin", r"düşüncen", r"görüşün", r"yorumun"
                ]
            },
            IntimacyType.SPIRITUAL.value: {
                "high_intensity": [
                    r"ruh", r"manevi", r"ruhsal", r"tinsel", r"kutsal",
                    r"ilahi", r"ebedi", r"sonsuz", r"derin bağ"
                ],
                "medium_intensity": [
                    r"huzur", r"barış", r"sakinlik", r"dinginlik",
                    r"meditasyon", r"yoga", r"nefes"
                ],
                "low_intensity": [
                    r"inanç", r"din", r"maneviyat", r"felsefe"
                ]
            }
        }
    
    async def track_intimacy_moment(
        self,
        user_id: str,
        character_id: str,
        message_content: str,
        timestamp: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[IntimacyMoment]:
        """
        Yakınlık anını takip et
        
        Args:
            user_id: Kullanıcı ID
            character_id: Karakter ID
            message_content: Mesaj içeriği
            timestamp: Zaman damgası
            context: Ek bağlam bilgileri
            
        Returns:
            IntimacyMoment objesi veya None
        """
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            # Yakınlık analizi
            intimacy_analysis = await self._analyze_intimacy_content(message_content)
            
            if intimacy_analysis["intensity"] < 0.1:  # Minimum eşik
                return None
            
            # Ruh hali faktörü (context'ten)
            mood_factor = context.get("mood_factor", 1.0) if context else 1.0
            
            # Yanıt gecikmesi
            response_delay = context.get("response_delay", 0.0) if context else 0.0
            
            # IntimacyMoment oluştur
            moment = IntimacyMoment(
                timestamp=timestamp,
                user_id=user_id,
                character_id=character_id,
                intimacy_type=intimacy_analysis["type"],
                intensity=intimacy_analysis["intensity"] * mood_factor,
                keywords=intimacy_analysis["keywords"],
                context=message_content[:100] + "..." if len(message_content) > 100 else message_content,
                mood_factor=mood_factor,
                response_delay=response_delay
            )
            
            # Moment'i kaydet
            self.intimacy_moments.append(moment)
            
            # Heatmap'i güncelle
            await self._update_heatmap(moment)
            
            # Kullanıcı pattern'ini güncelle
            await self._update_user_patterns(moment)
            
            # İstatistikleri güncelle
            await self._update_stats(moment)
            
            logger.info(f"🔥 Intimacy moment tracked",
                       user=user_id,
                       character=character_id,
                       type=moment.intimacy_type.value,
                       intensity=moment.intensity,
                       hour=timestamp.hour)
            
            return moment
            
        except Exception as e:
            logger.error(f"❌ Error tracking intimacy moment: {e}")
            return None
    
    async def _analyze_intimacy_content(self, content: str) -> Dict[str, Any]:
        """Mesaj içeriğinin yakınlık analizi"""
        content_lower = content.lower()
        
        best_type = IntimacyType.EMOTIONAL
        max_intensity = 0.0
        found_keywords = []
        
        # Her yakınlık türü için analiz
        for intimacy_type, intensity_levels in self.intimacy_keywords.items():
            type_intensity = 0.0
            type_keywords = []
            
            # Yoğunluk seviyelerine göre puanlama
            for level, keywords in intensity_levels.items():
                level_score = {"high_intensity": 1.0, "medium_intensity": 0.6, "low_intensity": 0.3}[level]
                
                for keyword_pattern in keywords:
                    matches = re.findall(keyword_pattern, content_lower)
                    if matches:
                        type_intensity += len(matches) * level_score * 0.2
                        type_keywords.extend(matches)
            
            # En yüksek yoğunluk
            if type_intensity > max_intensity:
                max_intensity = type_intensity
                best_type = IntimacyType(intimacy_type)
                found_keywords = type_keywords
        
        # Intensity'yi normalize et (max 1.0)
        normalized_intensity = min(1.0, max_intensity)
        
        return {
            "type": best_type,
            "intensity": normalized_intensity,
            "keywords": found_keywords[:5]  # İlk 5 anahtar kelime
        }
    
    async def _update_heatmap(self, moment: IntimacyMoment) -> None:
        """Heatmap'i güncelle"""
        hour = moment.timestamp.hour
        day_of_week = moment.timestamp.weekday()
        
        cell = self.intimacy_heatmap[day_of_week][hour]
        
        # Mevcut değerleri güncelle
        old_count = cell.interaction_count
        new_count = old_count + 1
        
        # Ağırlıklı ortalama ile intimacy score güncelle
        old_score = cell.intimacy_score
        new_score = (old_score * old_count + moment.intensity) / new_count
        
        cell.intimacy_score = new_score
        cell.interaction_count = new_count
        
        # Peak intensity güncelle
        if moment.intensity > cell.peak_intensity:
            cell.peak_intensity = moment.intensity
            cell.dominant_type = moment.intimacy_type
        
        # Kullanıcı sayısını yaklaşık olarak güncelle
        cell.user_count = max(cell.user_count, len(set(m.user_id for m in self.intimacy_moments 
                                                       if m.timestamp.hour == hour and 
                                                       m.timestamp.weekday() == day_of_week)))
    
    async def _update_user_patterns(self, moment: IntimacyMoment) -> None:
        """Kullanıcı pattern'lerini güncelle"""
        user_id = moment.user_id
        
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = {
                "total_moments": 0,
                "average_intensity": 0.0,
                "peak_hours": {},
                "preferred_intimacy_types": {},
                "intensity_trend": [],
                "last_update": moment.timestamp
            }
        
        pattern = self.user_patterns[user_id]
        
        # Total moments güncelle
        old_total = pattern["total_moments"]
        new_total = old_total + 1
        pattern["total_moments"] = new_total
        
        # Average intensity güncelle
        old_avg = pattern["average_intensity"]
        new_avg = (old_avg * old_total + moment.intensity) / new_total
        pattern["average_intensity"] = new_avg
        
        # Peak hours güncelle
        hour = moment.timestamp.hour
        pattern["peak_hours"][hour] = pattern["peak_hours"].get(hour, 0) + 1
        
        # Preferred intimacy types güncelle
        intimacy_type = moment.intimacy_type.value
        pattern["preferred_intimacy_types"][intimacy_type] = \
            pattern["preferred_intimacy_types"].get(intimacy_type, 0) + moment.intensity
        
        # Intensity trend güncelle (son 20 moment)
        pattern["intensity_trend"].append(moment.intensity)
        if len(pattern["intensity_trend"]) > 20:
            pattern["intensity_trend"] = pattern["intensity_trend"][-20:]
        
        pattern["last_update"] = moment.timestamp
    
    async def _update_stats(self, moment: IntimacyMoment) -> None:
        """İstatistikleri güncelle"""
        self.daily_stats["total_moments_tracked"] += 1
        
        # Peak hour güncelle
        hour_counts = {}
        for m in self.intimacy_moments:
            hour = m.timestamp.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        if hour_counts:
            self.daily_stats["peak_hour"] = max(hour_counts, key=hour_counts.get)
        
        # Peak day güncelle  
        day_counts = {}
        for m in self.intimacy_moments:
            day = m.timestamp.weekday()
            day_counts[day] = day_counts.get(day, 0) + 1
        
        if day_counts:
            self.daily_stats["peak_day"] = max(day_counts, key=day_counts.get)
        
        # Average intensity güncelle
        total_intensity = sum(m.intensity for m in self.intimacy_moments)
        self.daily_stats["average_intensity"] = total_intensity / len(self.intimacy_moments)
        
        # Sexual tension peaks
        if moment.intimacy_type == IntimacyType.SEXUAL and moment.intensity > 0.8:
            self.daily_stats["sexual_tension_peaks"] += 1
    
    def get_heatmap_matrix(self, normalize: bool = True) -> List[List[float]]:
        """
        Heatmap matrisini al
        
        Args:
            normalize: Değerleri 0-1 arasında normalize et
            
        Returns:
            7x24 matrix (günler x saatler)
        """
        matrix = []
        
        for day_row in self.intimacy_heatmap:
            hour_values = []
            for cell in day_row:
                value = cell.intimacy_score
                hour_values.append(value)
            matrix.append(hour_values)
        
        if normalize:
            # Tüm değerlerin max'ını bul
            all_values = [val for row in matrix for val in row]
            max_val = max(all_values) if all_values else 1.0
            
            if max_val > 0:
                matrix = [[val / max_val for val in row] for row in matrix]
        
        return matrix
    
    def get_heatmap_visualization_data(self) -> Dict[str, Any]:
        """Heatmap visualizasyon verisi"""
        matrix = self.get_heatmap_matrix(normalize=True)
        
        # Peak points
        peaks = []
        for day in range(7):
            for hour in range(24):
                cell = self.intimacy_heatmap[day][hour]
                if cell.intimacy_score > 0.7:  # Yüksek aktivite
                    peaks.append({
                        "day": day,
                        "hour": hour,
                        "score": cell.intimacy_score,
                        "count": cell.interaction_count,
                        "dominant_type": cell.dominant_type.value
                    })
        
        # Day labels
        day_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", 
                     "Friday", "Saturday", "Sunday"]
        
        # Hour labels
        hour_labels = [f"{h:02d}:00" for h in range(24)]
        
        return {
            "matrix": matrix,
            "day_labels": day_labels,
            "hour_labels": hour_labels,
            "peaks": peaks,
            "total_interactions": sum(cell.interaction_count 
                                    for row in self.intimacy_heatmap 
                                    for cell in row),
            "peak_hour": self.daily_stats["peak_hour"],
            "peak_day": self.daily_stats["peak_day"]
        }
    
    async def generate_intimacy_report(
        self,
        user_id: str,
        character_id: str,
        days_back: int = 7
    ) -> IntimacyReport:
        """
        Kullanıcı için yakınlık raporu oluştur
        
        Args:
            user_id: Kullanıcı ID
            character_id: Karakter ID
            days_back: Kaç gün geriye bakılacak
            
        Returns:
            IntimacyReport objesi
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        # Kullanıcının moment'lerini filtrele
        user_moments = [
            m for m in self.intimacy_moments
            if m.user_id == user_id and 
               m.character_id == character_id and
               start_time <= m.timestamp <= end_time
        ]
        
        if not user_moments:
            return IntimacyReport(
                user_id=user_id,
                character_id=character_id,
                period_start=start_time,
                period_end=end_time,
                total_intimacy_score=0.0,
                peak_hours=[],
                peak_days=[],
                dominant_intimacy_type=IntimacyType.EMOTIONAL,
                intensity_distribution={},
                engagement_patterns={},
                recommendations=["No intimacy data found for this period"]
            )
        
        # Total intimacy score
        total_score = sum(m.intensity for m in user_moments)
        
        # Peak hours
        hour_scores = {}
        for moment in user_moments:
            hour = moment.timestamp.hour
            hour_scores[hour] = hour_scores.get(hour, 0) + moment.intensity
        
        peak_hours = sorted(hour_scores.keys(), key=lambda h: hour_scores[h], reverse=True)[:3]
        
        # Peak days
        day_scores = {}
        for moment in user_moments:
            day = moment.timestamp.weekday()
            day_scores[day] = day_scores.get(day, 0) + moment.intensity
        
        peak_days = sorted(day_scores.keys(), key=lambda d: day_scores[d], reverse=True)[:3]
        
        # Dominant intimacy type
        type_scores = {}
        for moment in user_moments:
            intimacy_type = moment.intimacy_type
            type_scores[intimacy_type] = type_scores.get(intimacy_type, 0) + moment.intensity
        
        dominant_type = max(type_scores.keys(), key=lambda t: type_scores[t]) if type_scores else IntimacyType.EMOTIONAL
        
        # Intensity distribution
        intensity_ranges = {
            "minimal": len([m for m in user_moments if 0.0 <= m.intensity < 0.2]),
            "low": len([m for m in user_moments if 0.2 <= m.intensity < 0.4]),
            "moderate": len([m for m in user_moments if 0.4 <= m.intensity < 0.6]),
            "high": len([m for m in user_moments if 0.6 <= m.intensity < 0.8]),
            "intense": len([m for m in user_moments if 0.8 <= m.intensity <= 1.0])
        }
        
        total_moments = len(user_moments)
        intensity_distribution = {
            k: (v / total_moments) if total_moments > 0 else 0.0 
            for k, v in intensity_ranges.items()
        }
        
        # Engagement patterns
        engagement_patterns = {
            "total_moments": total_moments,
            "average_intensity": total_score / total_moments if total_moments > 0 else 0.0,
            "peak_intensity": max(m.intensity for m in user_moments) if user_moments else 0.0,
            "consistency": self._calculate_consistency(user_moments),
            "trend": self._calculate_trend(user_moments)
        }
        
        # Recommendations
        recommendations = await self._generate_intimacy_recommendations(
            user_moments, engagement_patterns, intensity_distribution
        )
        
        return IntimacyReport(
            user_id=user_id,
            character_id=character_id,
            period_start=start_time,
            period_end=end_time,
            total_intimacy_score=total_score,
            peak_hours=peak_hours,
            peak_days=peak_days,
            dominant_intimacy_type=dominant_type,
            intensity_distribution=intensity_distribution,
            engagement_patterns=engagement_patterns,
            recommendations=recommendations
        )
    
    def _calculate_consistency(self, moments: List[IntimacyMoment]) -> float:
        """Yakınlık tutarlılığını hesapla"""
        if len(moments) < 2:
            return 0.0
        
        intensities = [m.intensity for m in moments]
        mean_intensity = sum(intensities) / len(intensities)
        
        # Standart sapma hesapla
        variance = sum((x - mean_intensity) ** 2 for x in intensities) / len(intensities)
        std_dev = variance ** 0.5
        
        # Tutarlılık = 1 - normalized_std_dev
        consistency = max(0.0, 1.0 - (std_dev / max(mean_intensity, 0.1)))
        
        return round(consistency, 3)
    
    def _calculate_trend(self, moments: List[IntimacyMoment]) -> str:
        """Yakınlık trendini hesapla"""
        if len(moments) < 3:
            return "insufficient_data"
        
        # Son 5 moment ile önceki 5 moment'i karşılaştır
        recent_moments = sorted(moments, key=lambda m: m.timestamp)
        
        if len(recent_moments) >= 6:
            recent_avg = sum(m.intensity for m in recent_moments[-3:]) / 3
            earlier_avg = sum(m.intensity for m in recent_moments[:3]) / 3
            
            if recent_avg > earlier_avg * 1.2:
                return "increasing"
            elif recent_avg < earlier_avg * 0.8:
                return "decreasing"
            else:
                return "stable"
        
        return "stable"
    
    async def _generate_intimacy_recommendations(
        self,
        moments: List[IntimacyMoment],
        engagement_patterns: Dict[str, Any],
        intensity_distribution: Dict[str, float]
    ) -> List[str]:
        """Yakınlık önerileri oluştur"""
        recommendations = []
        
        avg_intensity = engagement_patterns["average_intensity"]
        consistency = engagement_patterns["consistency"]
        trend = engagement_patterns["trend"]
        
        # Intensity bazlı öneriler
        if avg_intensity < 0.3:
            recommendations.append("Low intimacy detected - increase emotional depth")
        elif avg_intensity > 0.8:
            recommendations.append("High intimacy maintained - excellent engagement")
        
        # Consistency bazlı öneriler
        if consistency < 0.4:
            recommendations.append("Inconsistent intimacy patterns - stabilize approach")
        elif consistency > 0.8:
            recommendations.append("Very consistent intimacy - maintain current strategy")
        
        # Trend bazlı öneriler
        if trend == "decreasing":
            recommendations.append("Intimacy declining - revitalize approach")
        elif trend == "increasing":
            recommendations.append("Intimacy growing - continue current tactics")
        
        # Distribution bazlı öneriler
        if intensity_distribution["intense"] > 0.3:
            recommendations.append("High intensity moments frequent - manage sustainability")
        
        if intensity_distribution["minimal"] > 0.5:
            recommendations.append("Too many low-intensity moments - increase engagement")
        
        return recommendations
    
    def get_peak_engagement_times(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """En yüksek etkileşim zamanlarını al"""
        peak_times = []
        
        for day in range(7):
            for hour in range(24):
                cell = self.intimacy_heatmap[day][hour]
                if cell.interaction_count > 0:
                    peak_times.append({
                        "day": day,
                        "hour": hour,
                        "day_name": ["Monday", "Tuesday", "Wednesday", "Thursday", 
                                   "Friday", "Saturday", "Sunday"][day],
                        "time": f"{hour:02d}:00",
                        "intimacy_score": cell.intimacy_score,
                        "interaction_count": cell.interaction_count,
                        "peak_intensity": cell.peak_intensity,
                        "dominant_type": cell.dominant_type.value,
                        "user_count": cell.user_count
                    })
        
        # Intimacy score'a göre sırala
        peak_times.sort(key=lambda x: x["intimacy_score"], reverse=True)
        
        return peak_times[:top_n]
    
    def get_system_intimacy_stats(self) -> Dict[str, Any]:
        """Sistem geneli yakınlık istatistikleri"""
        total_users = len(set(m.user_id for m in self.intimacy_moments))
        
        # Intimacy type dağılımı
        type_distribution = {}
        for moment in self.intimacy_moments:
            intimacy_type = moment.intimacy_type.value
            type_distribution[intimacy_type] = type_distribution.get(intimacy_type, 0) + 1
        
        return {
            "daily_stats": self.daily_stats,
            "total_users_tracked": total_users,
            "total_moments": len(self.intimacy_moments),
            "peak_engagement_times": self.get_peak_engagement_times(3),
            "intimacy_type_distribution": type_distribution,
            "heatmap_summary": {
                "peak_hour": self.daily_stats["peak_hour"],
                "peak_day": self.daily_stats["peak_day"],
                "average_intensity": self.daily_stats["average_intensity"]
            }
        } 