"""
🧠 Behavioral Tracker - Kullanıcı davranış analizi ve manipülasyon stratejileri
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
import logging
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)

@dataclass
class UserBehavior:
    """Kullanıcı davranış modeli"""
    user_id: str
    total_messages: int = 0
    avg_response_time: float = 0.0  # saniye
    sentiment_scores: Dict[str, int] = field(default_factory=dict)
    interaction_times: List[str] = field(default_factory=list)  # HH:MM formatında
    vip_interest_signals: int = 0
    payment_inquiries: int = 0
    rejection_count: int = 0
    compliment_count: int = 0
    trust_level: float = 0.5  # 0-1 arası
    manipulation_resistance: float = 0.5  # 0-1 arası
    last_analysis_date: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return asdict(self)

class BehavioralTracker:
    """Kullanıcı davranış takip ve analiz sistemi"""
    
    def __init__(self, storage_dir: str = "data/behavioral"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        # Aktif kullanıcı davranışları
        self.active_behaviors: Dict[str, UserBehavior] = {}
        
        # Geçici veri (response time hesaplama için)
        self.pending_responses: Dict[str, datetime] = {}
        
        logger.info("🧠 Behavioral Tracker başlatıldı")
    
    def track_message(
        self,
        user_id: str,
        message: str,
        sentiment: str = "neutral",
        is_bot_message: bool = False
    ) -> None:
        """
        Mesajı ve davranışı takip et
        
        Args:
            user_id: Kullanıcı ID
            message: Mesaj içeriği
            sentiment: Duygu durumu
            is_bot_message: Bot mesajı mı
        """
        behavior = self._get_or_create_behavior(user_id)
        
        if not is_bot_message:
            # Kullanıcı mesajı
            behavior.total_messages += 1
            
            # Sentiment takibi
            if sentiment not in behavior.sentiment_scores:
                behavior.sentiment_scores[sentiment] = 0
            behavior.sentiment_scores[sentiment] += 1
            
            # Saat takibi
            current_time = datetime.now().strftime("%H:%M")
            behavior.interaction_times.append(current_time)
            
            # VIP ilgi sinyalleri
            vip_keywords = ["vip", "özel", "video", "fiyat", "ödeme", "papara"]
            if any(keyword in message.lower() for keyword in vip_keywords):
                behavior.vip_interest_signals += 1
            
            # Ödeme sorguları
            payment_keywords = ["fiyat", "kaç", "ödeme", "papara", "iban"]
            if any(keyword in message.lower() for keyword in payment_keywords):
                behavior.payment_inquiries += 1
            
            # Red sinyalleri
            rejection_keywords = ["istemiyorum", "hayır", "olmaz", "gerek yok"]
            if any(keyword in message.lower() for keyword in rejection_keywords):
                behavior.rejection_count += 1
            
            # İltifat/pozitif
            compliment_keywords = ["güzel", "harika", "mükemmel", "seviyorum"]
            if any(keyword in message.lower() for keyword in compliment_keywords):
                behavior.compliment_count += 1
            
            # Response time hesaplama
            if user_id in self.pending_responses:
                response_time = (datetime.now() - self.pending_responses[user_id]).total_seconds()
                
                # Ortalama güncelle
                if behavior.avg_response_time == 0:
                    behavior.avg_response_time = response_time
                else:
                    # Moving average
                    behavior.avg_response_time = (behavior.avg_response_time * 0.8) + (response_time * 0.2)
                
                del self.pending_responses[user_id]
        
        else:
            # Bot mesajı gönderildi, response bekleniyor
            self.pending_responses[user_id] = datetime.now()
        
        # Trust level güncelle
        behavior.trust_level = self._calculate_trust_level(behavior)
        
        # Manipulation resistance güncelle
        behavior.manipulation_resistance = self._calculate_manipulation_resistance(behavior)
        
        # Periyodik kaydet
        if behavior.total_messages % 10 == 0:
            self._save_behavior(user_id)
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Kullanıcı davranış profilini getir
        
        Returns:
            Detaylı davranış profili ve öneriler
        """
        behavior = self._get_or_create_behavior(user_id)
        
        # Temel profil
        profile = {
            "user_id": user_id,
            "engagement_level": self._calculate_engagement_level(behavior),
            "primary_sentiment": self._get_primary_sentiment(behavior),
            "optimal_contact_time": self._calculate_optimal_time(behavior),
            "vip_conversion_probability": self._calculate_vip_probability(behavior),
            "recommended_strategy": self._recommend_strategy(behavior),
            "risk_indicators": self._identify_risks(behavior),
            "behavioral_insights": self._generate_insights(behavior)
        }
        
        return profile
    
    def _get_or_create_behavior(self, user_id: str) -> UserBehavior:
        """Kullanıcı davranışını getir veya oluştur"""
        if user_id not in self.active_behaviors:
            # Diskten yükle
            behavior_file = os.path.join(self.storage_dir, f"{user_id}.json")
            
            if os.path.exists(behavior_file):
                try:
                    with open(behavior_file, 'r') as f:
                        data = json.load(f)
                        self.active_behaviors[user_id] = UserBehavior(**data)
                except Exception as e:
                    logger.error(f"❌ Davranış yükleme hatası: {e}")
                    self.active_behaviors[user_id] = UserBehavior(user_id=user_id)
            else:
                self.active_behaviors[user_id] = UserBehavior(user_id=user_id)
        
        return self.active_behaviors[user_id]
    
    def _save_behavior(self, user_id: str) -> None:
        """Davranışı diske kaydet"""
        if user_id not in self.active_behaviors:
            return
        
        behavior = self.active_behaviors[user_id]
        behavior.last_analysis_date = datetime.now().isoformat()
        
        behavior_file = os.path.join(self.storage_dir, f"{user_id}.json")
        
        try:
            with open(behavior_file, 'w') as f:
                json.dump(behavior.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"❌ Davranış kaydetme hatası: {e}")
    
    def _calculate_trust_level(self, behavior: UserBehavior) -> float:
        """Güven seviyesini hesapla"""
        factors = []
        
        # Mesaj sayısı faktörü
        msg_factor = min(behavior.total_messages / 100, 1.0) * 0.3
        factors.append(msg_factor)
        
        # Response time faktörü (hızlı yanıt = yüksek güven)
        if behavior.avg_response_time > 0:
            rt_factor = max(0, 1 - (behavior.avg_response_time / 300)) * 0.2  # 5 dk üzeri düşük
            factors.append(rt_factor)
        
        # Pozitif sentiment faktörü
        positive_sentiments = behavior.sentiment_scores.get("happy", 0) + \
                            behavior.sentiment_scores.get("flirty", 0) + \
                            behavior.compliment_count
        
        total_sentiments = sum(behavior.sentiment_scores.values())
        if total_sentiments > 0:
            sentiment_factor = (positive_sentiments / total_sentiments) * 0.3
            factors.append(sentiment_factor)
        
        # VIP ilgi faktörü
        vip_factor = min(behavior.vip_interest_signals / 10, 1.0) * 0.2
        factors.append(vip_factor)
        
        return max(0.1, min(1.0, sum(factors)))
    
    def _calculate_manipulation_resistance(self, behavior: UserBehavior) -> float:
        """Manipülasyon direncini hesapla"""
        # Red sayısı yüksekse direnç yüksek
        rejection_factor = min(behavior.rejection_count / 5, 1.0) * 0.4
        
        # Yavaş yanıt = düşünüyor = dirençli
        slow_response_factor = 0
        if behavior.avg_response_time > 60:  # 1 dk üzeri
            slow_response_factor = min((behavior.avg_response_time - 60) / 240, 1.0) * 0.3
        
        # Nötr/negatif sentiment çoksa dirençli
        negative_sentiments = behavior.sentiment_scores.get("angry", 0) + \
                            behavior.sentiment_scores.get("sad", 0) + \
                            behavior.sentiment_scores.get("neutral", 0)
        
        total_sentiments = sum(behavior.sentiment_scores.values())
        sentiment_resistance = 0
        if total_sentiments > 0:
            sentiment_resistance = (negative_sentiments / total_sentiments) * 0.3
        
        return max(0.0, min(1.0, rejection_factor + slow_response_factor + sentiment_resistance))
    
    def _calculate_engagement_level(self, behavior: UserBehavior) -> str:
        """Etkileşim seviyesini belirle"""
        if behavior.total_messages < 5:
            return "new"
        elif behavior.total_messages < 20:
            return "warming_up"
        elif behavior.total_messages < 50:
            return "engaged"
        elif behavior.total_messages < 100:
            return "highly_engaged"
        else:
            return "loyal"
    
    def _get_primary_sentiment(self, behavior: UserBehavior) -> str:
        """Baskın duygu durumunu belirle"""
        if not behavior.sentiment_scores:
            return "neutral"
        
        return max(behavior.sentiment_scores.items(), key=lambda x: x[1])[0]
    
    def _calculate_optimal_time(self, behavior: UserBehavior) -> str:
        """Optimal iletişim zamanını hesapla"""
        if not behavior.interaction_times:
            return "20:00-23:00"  # Default akşam
        
        # Saat dağılımını çıkar
        hours = [int(time.split(":")[0]) for time in behavior.interaction_times[-50:]]  # Son 50
        
        if not hours:
            return "20:00-23:00"
        
        # En yoğun saat aralığını bul
        hour_counts = defaultdict(int)
        for hour in hours:
            hour_counts[hour] += 1
        
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
        
        # 3 saatlik aralık döndür
        start = max(0, peak_hour - 1)
        end = min(23, peak_hour + 1)
        
        return f"{start:02d}:00-{end:02d}:00"
    
    def _calculate_vip_probability(self, behavior: UserBehavior) -> float:
        """VIP'e dönüşüm olasılığını hesapla"""
        factors = []
        
        # Trust level
        factors.append(behavior.trust_level * 0.3)
        
        # VIP ilgi sinyalleri
        vip_signal_factor = min(behavior.vip_interest_signals / 5, 1.0) * 0.4
        factors.append(vip_signal_factor)
        
        # Payment sorguları
        payment_factor = min(behavior.payment_inquiries / 3, 1.0) * 0.2
        factors.append(payment_factor)
        
        # Engagement level
        engagement_bonus = {
            "new": 0.0,
            "warming_up": 0.05,
            "engaged": 0.1,
            "highly_engaged": 0.15,
            "loyal": 0.2
        }
        engagement = self._calculate_engagement_level(behavior)
        factors.append(engagement_bonus.get(engagement, 0))
        
        # Resistance penalty
        factors.append(-behavior.manipulation_resistance * 0.1)
        
        return max(0.0, min(1.0, sum(factors)))
    
    def _recommend_strategy(self, behavior: UserBehavior) -> Dict[str, Any]:
        """Önerilen strateji"""
        vip_prob = self._calculate_vip_probability(behavior)
        resistance = behavior.manipulation_resistance
        trust = behavior.trust_level
        
        if vip_prob > 0.7:
            return {
                "approach": "direct_sales",
                "tone": "confident",
                "tactics": ["scarcity", "exclusivity", "social_proof"],
                "message": "Direkt VIP satışına geç, hazır"
            }
        elif vip_prob > 0.4 and resistance < 0.5:
            return {
                "approach": "gradual_escalation",
                "tone": "seductive",
                "tactics": ["tease", "mystery", "desire_building"],
                "message": "Yavaş yavaş VIP'e yönlendir"
            }
        elif trust < 0.3:
            return {
                "approach": "trust_building",
                "tone": "friendly",
                "tactics": ["empathy", "validation", "connection"],
                "message": "Önce güven inşa et"
            }
        elif resistance > 0.7:
            return {
                "approach": "soft_engagement",
                "tone": "casual",
                "tactics": ["humor", "light_flirt", "no_pressure"],
                "message": "Baskı yapma, eğlenceli tut"
            }
        else:
            return {
                "approach": "balanced",
                "tone": "flirty",
                "tactics": ["charm", "intrigue", "value_display"],
                "message": "Dengeli yaklaşım, fırsatları kolla"
            }
    
    def _identify_risks(self, behavior: UserBehavior) -> List[str]:
        """Risk göstergelerini belirle"""
        risks = []
        
        if behavior.rejection_count > 5:
            risks.append("high_rejection_rate")
        
        if behavior.manipulation_resistance > 0.8:
            risks.append("manipulation_resistant")
        
        if behavior.trust_level < 0.2:
            risks.append("low_trust")
        
        if behavior.avg_response_time > 300:  # 5 dk
            risks.append("slow_responder")
        
        if behavior.total_messages > 100 and behavior.payment_inquiries == 0:
            risks.append("no_payment_interest")
        
        return risks
    
    def _generate_insights(self, behavior: UserBehavior) -> List[str]:
        """Davranışsal içgörüler üret"""
        insights = []
        
        # Response pattern
        if behavior.avg_response_time < 30:
            insights.append("Çok hızlı yanıt veriyor - yüksek ilgi")
        elif behavior.avg_response_time > 180:
            insights.append("Yavaş yanıtlıyor - düşük öncelik veya meşgul")
        
        # Sentiment pattern
        primary = self._get_primary_sentiment(behavior)
        if primary == "flirty":
            insights.append("Flört sinyalleri güçlü - romantik yaklaşım işe yarar")
        elif primary == "neutral":
            insights.append("Duygusal olarak mesafeli - ısınma zamanı")
        
        # Time pattern
        if behavior.interaction_times:
            hours = [int(t.split(":")[0]) for t in behavior.interaction_times[-20:]]
            if all(h >= 22 or h <= 2 for h in hours):
                insights.append("Gece kuşu - geç saatlerde aktif")
            elif all(6 <= h <= 9 for h in hours):
                insights.append("Sabahçı - erken saatlerde yazıyor")
        
        # VIP signals
        if behavior.vip_interest_signals > 3:
            insights.append("VIP'e ilgi var - satış fırsatı")
        
        return insights
    
    def get_strategy_for_message(
        self,
        user_id: str,
        message: str,
        current_strategy: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Mesaja ve profile göre strateji öner
        
        Returns:
            (önerilen_ton, taktik_parametreleri)
        """
        profile = self.get_user_profile(user_id)
        behavior = self._get_or_create_behavior(user_id)
        
        # Mesaj analizi
        message_lower = message.lower()
        
        # VIP sorgusu
        if any(word in message_lower for word in ["vip", "özel", "fiyat"]):
            if profile["vip_conversion_probability"] > 0.6:
                return "seductive", {
                    "urgency": "high",
                    "exclusivity": True,
                    "price_anchor": "high"
                }
            else:
                return "mysterious", {
                    "tease_level": "high",
                    "reveal": "partial"
                }
        
        # Red/olumsuz
        if any(word in message_lower for word in ["hayır", "istemiyorum", "olmaz"]):
            return "soft", {
                "back_off": True,
                "change_topic": True,
                "humor": True
            }
        
        # İltifat/pozitif
        if any(word in message_lower for word in ["güzel", "harika", "seviyorum"]):
            return "flirty", {
                "reciprocate": True,
                "escalate": behavior.trust_level > 0.6,
                "compliment_back": True
            }
        
        # Default - profile bazlı
        recommended = profile["recommended_strategy"]
        return recommended["tone"], {
            "tactics": recommended["tactics"],
            "intensity": "medium"
        }

# Singleton instance
behavioral_tracker = BehavioralTracker() 