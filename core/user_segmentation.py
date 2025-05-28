# core/user_segmentation.py
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import openai

from core.crm_database import crm_db, UserProfile
from utils.log_utils import log_event
from core.analytics_logger import log_analytics

class UserSegment(Enum):
    """Kullanıcı segmentleri"""
    HOT_LEAD = "hot_lead"  # Yüksek dönüşüm potansiyeli
    WARM_LEAD = "warm_lead"  # Orta dönüşüm potansiyeli
    COLD_LEAD = "cold_lead"  # Düşük dönüşüm potansiyeli
    ACTIVE_CUSTOMER = "active_customer"  # Aktif VIP müşteri
    CHURNED = "churned"  # Kaybedilmiş müşteri
    ENGAGED = "engaged"  # Yüksek etkileşimli
    PASSIVE = "passive"  # Pasif takipçi
    NEW_USER = "new_user"  # Yeni kullanıcı
    BOT_LOVER = "bot_lover"  # Bot sevenler
    NIGHT_OWL = "night_owl"  # Gece kuşları
    PREMIUM_POTENTIAL = "premium_potential"  # Premium potansiyeli yüksek
    HIGH_VALUE = "high_value"  # Yüksek değerli kullanıcı

@dataclass
class SegmentProfile:
    """Segment profili"""
    segment: UserSegment
    confidence: float  # 0-1 arası güven skoru
    characteristics: List[str]
    recommended_actions: List[str]
    optimal_contact_times: List[int]
    message_frequency: str  # hourly, daily, weekly
    content_preferences: List[str]
    conversion_probability: float

class UserSegmentationEngine:
    """Kullanıcı segmentasyon motoru"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()
        self.segment_cache = {}  # {user_id: SegmentProfile}
        self.segment_rules = self._define_segment_rules()
    
    def _define_segment_rules(self) -> Dict:
        """Segment kurallarını tanımla"""
        return {
            UserSegment.HOT_LEAD: {
                "min_engagement": 70,
                "min_conversion_potential": 0.7,
                "min_interactions": 5,
                "recent_activity_days": 3,
                "vip_interest": True
            },
            UserSegment.WARM_LEAD: {
                "min_engagement": 50,
                "min_conversion_potential": 0.4,
                "min_interactions": 3,
                "recent_activity_days": 7
            },
            UserSegment.COLD_LEAD: {
                "max_engagement": 30,
                "max_conversion_potential": 0.3,
                "recent_activity_days": 30
            },
            UserSegment.ENGAGED: {
                "min_engagement": 80,
                "min_interactions": 10,
                "recent_activity_days": 3
            },
            UserSegment.BOT_LOVER: {
                "min_bot_preferences": 3,
                "min_engagement": 60
            },
            UserSegment.NIGHT_OWL: {
                "night_hours": [22, 23, 0, 1, 2, 3],
                "min_night_activity": 0.6
            },
            UserSegment.NEW_USER: {
                "max_days_since_join": 7,
                "max_interactions": 5
            },
            UserSegment.PREMIUM_POTENTIAL: {
                "is_premium": True,
                "min_engagement": 60,
                "min_conversion_potential": 0.5
            }
        }
    
    async def segment_user(self, user_profile: UserProfile) -> List[SegmentProfile]:
        """Kullanıcıyı segmentlere ayır"""
        try:
            segments = []
            
            # Kural tabanlı segmentasyon
            rule_segments = await self._apply_rule_based_segmentation(user_profile)
            
            # GPT tabanlı gelişmiş analiz
            gpt_segments = await self._apply_gpt_segmentation(user_profile)
            
            # Segmentleri birleştir ve önceliklendir
            all_segments = rule_segments + gpt_segments
            
            # Duplicate'leri kaldır ve confidence'a göre sırala
            unique_segments = {}
            for seg in all_segments:
                if seg.segment not in unique_segments or seg.confidence > unique_segments[seg.segment].confidence:
                    unique_segments[seg.segment] = seg
            
            segments = sorted(unique_segments.values(), key=lambda x: x.confidence, reverse=True)
            
            # Cache'e kaydet
            self.segment_cache[user_profile.user_id] = segments[0] if segments else None
            
            # Analytics log
            log_analytics("segmentation", "user_segmented", {
                "user_id": user_profile.user_id,
                "segments": [s.segment.value for s in segments[:3]],
                "primary_segment": segments[0].segment.value if segments else None
            })
            
            return segments
            
        except Exception as e:
            log_event("segmentation", f"❌ Segmentasyon hatası {user_profile.user_id}: {e}")
            return []
    
    async def _apply_rule_based_segmentation(self, user_profile: UserProfile) -> List[SegmentProfile]:
        """Kural tabanlı segmentasyon"""
        segments = []
        now = datetime.now()
        
        # HOT LEAD kontrolü
        if (user_profile.engagement_score >= 70 and 
            user_profile.conversion_potential >= 0.7 and
            user_profile.total_interactions >= 5 and
            (now - user_profile.last_seen).days <= 3):
            
            segments.append(SegmentProfile(
                segment=UserSegment.HOT_LEAD,
                confidence=0.9,
                characteristics=["Yüksek etkileşim", "VIP ilgisi", "Aktif kullanıcı"],
                recommended_actions=["Özel VIP teklifi", "Kişisel mesaj", "Hızlı takip"],
                optimal_contact_times=user_profile.active_hours[:3] if user_profile.active_hours else [20, 21, 22],
                message_frequency="daily",
                content_preferences=["VIP avantajları", "Özel içerik", "Promosyonlar"],
                conversion_probability=user_profile.conversion_potential
            ))
        
        # WARM LEAD kontrolü
        elif (user_profile.engagement_score >= 50 and 
              user_profile.conversion_potential >= 0.4 and
              user_profile.total_interactions >= 3 and
              (now - user_profile.last_seen).days <= 7):
            
            segments.append(SegmentProfile(
                segment=UserSegment.WARM_LEAD,
                confidence=0.8,
                characteristics=["Orta etkileşim", "Potansiyel ilgi"],
                recommended_actions=["Engagement artırma", "Değer sunumu"],
                optimal_contact_times=user_profile.active_hours[:2] if user_profile.active_hours else [19, 20],
                message_frequency="every_2_days",
                content_preferences=["İlgi çekici içerik", "Sosyal proof"],
                conversion_probability=user_profile.conversion_potential
            ))
        
        # ENGAGED kontrolü
        if (user_profile.engagement_score >= 80 and 
            user_profile.total_interactions >= 10 and
            (now - user_profile.last_seen).days <= 3):
            
            segments.append(SegmentProfile(
                segment=UserSegment.ENGAGED,
                confidence=0.95,
                characteristics=["Çok yüksek etkileşim", "Sadık takipçi"],
                recommended_actions=["Özel ilgi", "VIP dönüşüm"],
                optimal_contact_times=user_profile.active_hours[:4] if user_profile.active_hours else [19, 20, 21, 22],
                message_frequency="daily",
                content_preferences=["Premium içerik", "Özel teklifler"],
                conversion_probability=0.8
            ))
        
        # BOT LOVER kontrolü
        if len(user_profile.preferred_bots) >= 3 and user_profile.engagement_score >= 60:
            segments.append(SegmentProfile(
                segment=UserSegment.BOT_LOVER,
                confidence=0.85,
                characteristics=["Çoklu bot takibi", "Bot içeriği sever"],
                recommended_actions=["Cross-promotion", "Bot önerileri"],
                optimal_contact_times=user_profile.active_hours[:3] if user_profile.active_hours else [20, 21, 22],
                message_frequency="daily",
                content_preferences=["Yeni bot tanıtımları", "Özel bot içerikleri"],
                conversion_probability=0.7
            ))
        
        # NIGHT OWL kontrolü
        night_hours = [22, 23, 0, 1, 2, 3]
        if user_profile.active_hours:
            night_activity = sum(1 for h in user_profile.active_hours if h in night_hours) / len(user_profile.active_hours)
            if night_activity >= 0.6:
                segments.append(SegmentProfile(
                    segment=UserSegment.NIGHT_OWL,
                    confidence=0.9,
                    characteristics=["Gece aktif", "Geç saatleri tercih eder"],
                    recommended_actions=["Gece özel içerikleri", "Canlı yayın bildirimleri"],
                    optimal_contact_times=[h for h in user_profile.active_hours if h in night_hours],
                    message_frequency="nightly",
                    content_preferences=["Gece özel", "Canlı içerik"],
                    conversion_probability=0.6
                ))
        
        # NEW USER kontrolü
        if (now - user_profile.first_seen).days <= 7 and user_profile.total_interactions <= 5:
            segments.append(SegmentProfile(
                segment=UserSegment.NEW_USER,
                confidence=1.0,
                characteristics=["Yeni katılım", "Keşif aşamasında"],
                recommended_actions=["Hoşgeldin mesajı", "Değer sunumu", "Soft yaklaşım"],
                optimal_contact_times=[19, 20, 21],
                message_frequency="every_2_days",
                content_preferences=["Tanıtım içeriği", "Popüler içerikler"],
                conversion_probability=0.4
            ))
        
        # PREMIUM POTENTIAL kontrolü
        if user_profile.is_premium and user_profile.engagement_score >= 60:
            segments.append(SegmentProfile(
                segment=UserSegment.PREMIUM_POTENTIAL,
                confidence=0.85,
                characteristics=["Premium kullanıcı", "Ödeme gücü var"],
                recommended_actions=["Premium VIP paketler", "Özel teklifler"],
                optimal_contact_times=user_profile.active_hours[:3] if user_profile.active_hours else [19, 20, 21],
                message_frequency="every_3_days",
                content_preferences=["Lüks içerik", "Özel avantajlar"],
                conversion_probability=0.75
            ))
        
        return segments
    
    async def _apply_gpt_segmentation(self, user_profile: UserProfile) -> List[SegmentProfile]:
        """GPT tabanlı gelişmiş segmentasyon"""
        try:
            # Kullanıcı verilerini hazırla
            user_data = {
                "user_id": user_profile.user_id,
                "username": user_profile.username,
                "total_interactions": user_profile.total_interactions,
                "engagement_score": user_profile.engagement_score,
                "conversion_potential": user_profile.conversion_potential,
                "active_hours": user_profile.active_hours,
                "preferred_bots": user_profile.preferred_bots,
                "is_premium": user_profile.is_premium,
                "days_since_join": (datetime.now() - user_profile.first_seen).days,
                "days_since_last_seen": (datetime.now() - user_profile.last_seen).days,
                "response_rate": user_profile.response_rate,
                "group_activity": len(user_profile.group_memberships)
            }
            
            prompt = f"""
            Aşağıdaki kullanıcı verilerini analiz et ve en uygun segmentleri belirle:
            
            {json.dumps(user_data, indent=2, ensure_ascii=False)}
            
            Mevcut segmentler:
            - HOT_LEAD: Yüksek dönüşüm potansiyeli
            - WARM_LEAD: Orta dönüşüm potansiyeli
            - COLD_LEAD: Düşük dönüşüm potansiyeli
            - ENGAGED: Yüksek etkileşimli
            - PASSIVE: Pasif takipçi
            - BOT_LOVER: Bot sevenler
            - NIGHT_OWL: Gece kuşları
            - PREMIUM_POTENTIAL: Premium potansiyeli
            - HIGH_VALUE: Yüksek değerli
            
            Bu kullanıcı için EN UYGUN 2 segmenti belirle ve her biri için:
            1. Neden bu segmente uygun olduğunu açıkla
            2. Bu segment için optimal iletişim stratejisi öner
            3. Mesaj sıklığı ve zamanlaması öner
            4. İçerik tercihlerini belirle
            
            JSON formatında yanıt ver:
            {{
                "segments": [
                    {{
                        "segment": "SEGMENT_ADI",
                        "confidence": 0.0-1.0,
                        "reasoning": "Neden bu segment",
                        "characteristics": ["özellik1", "özellik2"],
                        "recommended_actions": ["aksiyon1", "aksiyon2"],
                        "optimal_hours": [saat listesi],
                        "message_frequency": "hourly/daily/weekly",
                        "content_preferences": ["içerik1", "içerik2"],
                        "conversion_probability": 0.0-1.0
                    }}
                ]
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # GPT sonuçlarını SegmentProfile objesine dönüştür
            segments = []
            for seg_data in result.get("segments", []):
                try:
                    segment_enum = UserSegment[seg_data["segment"]]
                    segments.append(SegmentProfile(
                        segment=segment_enum,
                        confidence=float(seg_data["confidence"]),
                        characteristics=seg_data["characteristics"],
                        recommended_actions=seg_data["recommended_actions"],
                        optimal_contact_times=seg_data["optimal_hours"],
                        message_frequency=seg_data["message_frequency"],
                        content_preferences=seg_data["content_preferences"],
                        conversion_probability=float(seg_data["conversion_probability"])
                    ))
                except:
                    continue
            
            return segments
            
        except Exception as e:
            log_event("segmentation", f"❌ GPT segmentasyon hatası: {e}")
            return []
    
    async def get_segment_users(self, segment: UserSegment, limit: int = 100) -> List[UserProfile]:
        """Belirli bir segmentteki kullanıcıları getir"""
        try:
            segment_users = []
            
            # Redis'ten tüm kullanıcı anahtarlarını al
            keys = await crm_db.redis.keys("crm:user:*")
            
            for key in keys[:limit * 2]:  # Daha fazla kontrol et, limit kadar döndür
                user_id = int(key.decode().split(":")[-1])
                user_profile = await crm_db.get_user_profile(user_id)
                
                if not user_profile:
                    continue
                
                # Kullanıcıyı segmentlere ayır
                user_segments = await self.segment_user(user_profile)
                
                # İstenen segment varsa ekle
                if any(s.segment == segment for s in user_segments):
                    segment_users.append(user_profile)
                    if len(segment_users) >= limit:
                        break
            
            return segment_users
            
        except Exception as e:
            log_event("segmentation", f"❌ Segment kullanıcıları alma hatası: {e}")
            return []
    
    async def get_user_primary_segment(self, user_id: int) -> Optional[SegmentProfile]:
        """Kullanıcının birincil segmentini getir"""
        try:
            # Cache'den kontrol et
            if user_id in self.segment_cache:
                return self.segment_cache[user_id]
            
            # Kullanıcı profilini al
            user_profile = await crm_db.get_user_profile(user_id)
            if not user_profile:
                return None
            
            # Segmentlere ayır
            segments = await self.segment_user(user_profile)
            
            return segments[0] if segments else None
            
        except Exception as e:
            log_event("segmentation", f"❌ Birincil segment alma hatası: {e}")
            return None
    
    async def analyze_segment_performance(self) -> Dict:
        """Segment performanslarını analiz et"""
        try:
            segment_stats = {}
            
            # Her segment için istatistikler
            for segment in UserSegment:
                segment_users = await self.get_segment_users(segment, limit=50)
                
                if not segment_users:
                    continue
                
                # Ortalama metrikleri hesapla
                avg_engagement = sum(u.engagement_score for u in segment_users) / len(segment_users)
                avg_conversion = sum(u.conversion_potential for u in segment_users) / len(segment_users)
                avg_interactions = sum(u.total_interactions for u in segment_users) / len(segment_users)
                
                # Response rate hesapla
                total_response_rate = sum(u.response_rate for u in segment_users) / len(segment_users)
                
                segment_stats[segment.value] = {
                    "user_count": len(segment_users),
                    "avg_engagement": avg_engagement,
                    "avg_conversion_potential": avg_conversion,
                    "avg_interactions": avg_interactions,
                    "avg_response_rate": total_response_rate,
                    "performance_score": (avg_engagement + avg_conversion * 100 + total_response_rate * 100) / 3
                }
            
            # En iyi performans gösteren segmentleri sırala
            sorted_segments = sorted(
                segment_stats.items(),
                key=lambda x: x[1]["performance_score"],
                reverse=True
            )
            
            return {
                "segment_stats": segment_stats,
                "top_performing_segments": [s[0] for s in sorted_segments[:3]],
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            log_event("segmentation", f"❌ Segment performans analizi hatası: {e}")
            return {}

# Global instance
user_segmentation = UserSegmentationEngine() 