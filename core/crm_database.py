# core/crm_database.py
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from dataclasses import dataclass, asdict
from utils.redis_client import redis_client
from utils.log_utils import log_event
from core.analytics_logger import log_analytics

@dataclass
class UserProfile:
    """Kullanıcı profil modeli"""
    user_id: int
    username: str
    first_name: str
    last_name: str
    phone: Optional[str]
    is_bot: bool
    is_premium: bool
    language_code: str
    
    # CRM verileri
    first_seen: datetime
    last_seen: datetime
    total_interactions: int
    response_rate: float  # Mesajlara yanıt verme oranı
    engagement_score: float  # 0-100 arası engagement skoru
    interests: List[str]  # İlgi alanları
    preferred_bots: List[str]  # Hangi botlarla daha çok etkileşim kuruyor
    
    # Davranış analizi
    active_hours: List[int]  # Aktif olduğu saatler (0-23)
    message_frequency: str  # low, medium, high
    conversion_potential: float  # VIP'e dönüşme potansiyeli
    last_vip_interest: Optional[datetime]
    
    # Grup aktivitesi
    group_memberships: List[int]  # Üye olduğu grup ID'leri
    group_activity_score: Dict[int, float]  # Grup bazında aktivite skoru

@dataclass
class GroupProfile:
    """Grup profil modeli"""
    group_id: int
    title: str
    username: Optional[str]
    type: str  # group, supergroup, channel
    member_count: int
    
    # CRM verileri
    first_discovered: datetime
    last_activity: datetime
    total_messages_sent: int
    total_responses_received: int
    response_rate: float
    
    # Grup analizi
    activity_level: str  # dead, low, medium, high, very_high
    peak_hours: List[int]  # En aktif saatler
    member_engagement: float  # Üye etkileşim oranı
    spam_tolerance: float  # Spam toleransı (0-1)
    
    # Bot performansı
    bot_performance: Dict[str, Dict]  # Bot bazında performans metrikleri
    last_successful_campaign: Optional[datetime]
    campaign_fatigue_score: float  # Kampanya yorgunluğu
    
    # Hedefleme verileri
    target_priority: int  # 1-5 arası öncelik
    optimal_message_times: List[int]  # Optimal mesaj saatleri
    content_preferences: List[str]  # İçerik tercihleri

class CRMDatabase:
    """CRM veritabanı yönetim sistemi"""
    
    def __init__(self):
        self.redis = redis_client
        self.user_cache = {}
        self.group_cache = {}
        
    # ===== USER MANAGEMENT =====
    
    async def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Kullanıcı profilini getir"""
        try:
            # Önce cache'den kontrol et
            if user_id in self.user_cache:
                return self.user_cache[user_id]
            
            # Redis'ten al
            user_data = await self.redis.hgetall(f"crm:user:{user_id}")
            if not user_data:
                return None
            
            # JSON alanları parse et
            for field in ['interests', 'preferred_bots', 'active_hours', 'group_memberships']:
                if field in user_data:
                    user_data[field] = json.loads(user_data[field])
            
            for field in ['group_activity_score']:
                if field in user_data:
                    user_data[field] = {int(k): float(v) for k, v in json.loads(user_data[field]).items()}
            
            # Datetime alanları parse et
            for field in ['first_seen', 'last_seen', 'last_vip_interest']:
                if field in user_data and user_data[field]:
                    user_data[field] = datetime.fromisoformat(user_data[field])
            
            # Float alanları parse et
            for field in ['response_rate', 'engagement_score', 'conversion_potential']:
                if field in user_data:
                    user_data[field] = float(user_data[field])
            
            # Int alanları parse et
            for field in ['user_id', 'total_interactions']:
                if field in user_data:
                    user_data[field] = int(user_data[field])
            
            # Bool alanları parse et
            for field in ['is_bot', 'is_premium']:
                if field in user_data:
                    user_data[field] = user_data[field].lower() == 'true'
            
            profile = UserProfile(**user_data)
            self.user_cache[user_id] = profile
            return profile
            
        except Exception as e:
            log_event("crm_db", f"❌ Kullanıcı profil alma hatası {user_id}: {e}")
            return None
    
    async def update_user_profile(self, profile: UserProfile):
        """Kullanıcı profilini güncelle"""
        try:
            # Cache'i güncelle
            self.user_cache[profile.user_id] = profile
            
            # Redis'e kaydet
            user_data = asdict(profile)
            
            # JSON serialize et
            for field in ['interests', 'preferred_bots', 'active_hours', 'group_memberships']:
                user_data[field] = json.dumps(user_data[field])
            
            user_data['group_activity_score'] = json.dumps(user_data['group_activity_score'])
            
            # Datetime serialize et
            for field in ['first_seen', 'last_seen', 'last_vip_interest']:
                if user_data[field]:
                    user_data[field] = user_data[field].isoformat()
            
            await self.redis.hset(f"crm:user:{profile.user_id}", mapping=user_data)
            
            # TTL ayarla (1 yıl)
            await self.redis.expire(f"crm:user:{profile.user_id}", 31536000)
            
        except Exception as e:
            log_event("crm_db", f"❌ Kullanıcı profil güncelleme hatası {profile.user_id}: {e}")
    
    async def create_user_profile(self, user_id: int, username: str, first_name: str, 
                                last_name: str = "", phone: str = None, is_bot: bool = False,
                                is_premium: bool = False, language_code: str = "tr") -> UserProfile:
        """Yeni kullanıcı profili oluştur"""
        now = datetime.now()
        
        profile = UserProfile(
            user_id=user_id,
            username=username or f"user_{user_id}",
            first_name=first_name or "Unknown",
            last_name=last_name or "",
            phone=phone,
            is_bot=is_bot,
            is_premium=is_premium,
            language_code=language_code,
            
            first_seen=now,
            last_seen=now,
            total_interactions=0,
            response_rate=0.0,
            engagement_score=50.0,  # Başlangıç skoru
            interests=[],
            preferred_bots=[],
            
            active_hours=[],
            message_frequency="unknown",
            conversion_potential=0.5,  # Orta potansiyel
            last_vip_interest=None,
            
            group_memberships=[],
            group_activity_score={}
        )
        
        await self.update_user_profile(profile)
        log_event("crm_db", f"✅ Yeni kullanıcı profili oluşturuldu: {username} ({user_id})")
        return profile
    
    # ===== GROUP MANAGEMENT =====
    
    async def get_group_profile(self, group_id: int) -> Optional[GroupProfile]:
        """Grup profilini getir"""
        try:
            # Önce cache'den kontrol et
            if group_id in self.group_cache:
                return self.group_cache[group_id]
            
            # Redis'ten al
            group_data = await self.redis.hgetall(f"crm:group:{group_id}")
            if not group_data:
                return None
            
            # JSON alanları parse et
            for field in ['peak_hours', 'optimal_message_times', 'content_preferences']:
                if field in group_data:
                    group_data[field] = json.loads(group_data[field])
            
            for field in ['bot_performance']:
                if field in group_data:
                    group_data[field] = json.loads(group_data[field])
            
            # Datetime alanları parse et
            for field in ['first_discovered', 'last_activity', 'last_successful_campaign']:
                if field in group_data and group_data[field]:
                    group_data[field] = datetime.fromisoformat(group_data[field])
            
            # Float alanları parse et
            for field in ['response_rate', 'member_engagement', 'spam_tolerance', 'campaign_fatigue_score']:
                if field in group_data:
                    group_data[field] = float(group_data[field])
            
            # Int alanları parse et
            for field in ['group_id', 'member_count', 'total_messages_sent', 'total_responses_received', 'target_priority']:
                if field in group_data:
                    group_data[field] = int(group_data[field])
            
            profile = GroupProfile(**group_data)
            self.group_cache[group_id] = profile
            return profile
            
        except Exception as e:
            log_event("crm_db", f"❌ Grup profil alma hatası {group_id}: {e}")
            return None
    
    async def update_group_profile(self, profile: GroupProfile):
        """Grup profilini güncelle"""
        try:
            # Cache'i güncelle
            self.group_cache[profile.group_id] = profile
            
            # Redis'e kaydet
            group_data = asdict(profile)
            
            # JSON serialize et
            for field in ['peak_hours', 'optimal_message_times', 'content_preferences']:
                group_data[field] = json.dumps(group_data[field])
            
            group_data['bot_performance'] = json.dumps(group_data['bot_performance'])
            
            # Datetime serialize et
            for field in ['first_discovered', 'last_activity', 'last_successful_campaign']:
                if group_data[field]:
                    group_data[field] = group_data[field].isoformat()
            
            await self.redis.hset(f"crm:group:{profile.group_id}", mapping=group_data)
            
            # TTL ayarla (1 yıl)
            await self.redis.expire(f"crm:group:{profile.group_id}", 31536000)
            
        except Exception as e:
            log_event("crm_db", f"❌ Grup profil güncelleme hatası {profile.group_id}: {e}")
    
    async def create_group_profile(self, group_id: int, title: str, username: str = None,
                                 group_type: str = "group", member_count: int = 0) -> GroupProfile:
        """Yeni grup profili oluştur"""
        now = datetime.now()
        
        profile = GroupProfile(
            group_id=group_id,
            title=title,
            username=username,
            type=group_type,
            member_count=member_count,
            
            first_discovered=now,
            last_activity=now,
            total_messages_sent=0,
            total_responses_received=0,
            response_rate=0.0,
            
            activity_level="unknown",
            peak_hours=[],
            member_engagement=0.0,
            spam_tolerance=0.5,  # Orta tolerans
            
            bot_performance={},
            last_successful_campaign=None,
            campaign_fatigue_score=0.0,
            
            target_priority=3,  # Orta öncelik
            optimal_message_times=[],
            content_preferences=[]
        )
        
        await self.update_group_profile(profile)
        log_event("crm_db", f"✅ Yeni grup profili oluşturuldu: {title} ({group_id})")
        return profile
    
    # ===== INTERACTION TRACKING =====
    
    async def record_message_sent(self, bot_username: str, group_id: int, user_id: int, 
                                message_content: str, message_type: str = "spam"):
        """Gönderilen mesajı kaydet"""
        try:
            now = datetime.now()
            
            # Mesaj kaydı
            message_data = {
                "bot_username": bot_username,
                "group_id": group_id,
                "user_id": user_id,
                "content": message_content[:500],  # İlk 500 karakter
                "type": message_type,
                "timestamp": now.isoformat(),
                "response_received": False
            }
            
            message_key = f"crm:message:{bot_username}:{group_id}:{int(now.timestamp())}"
            await self.redis.hset(message_key, mapping=message_data)
            await self.redis.expire(message_key, 2592000)  # 30 gün TTL
            
            # Grup profilini güncelle
            group_profile = await self.get_group_profile(group_id)
            if group_profile:
                group_profile.total_messages_sent += 1
                group_profile.last_activity = now
                
                # Bot performansını güncelle
                if bot_username not in group_profile.bot_performance:
                    group_profile.bot_performance[bot_username] = {
                        "messages_sent": 0,
                        "responses_received": 0,
                        "last_message": None
                    }
                
                group_profile.bot_performance[bot_username]["messages_sent"] += 1
                group_profile.bot_performance[bot_username]["last_message"] = now.isoformat()
                
                await self.update_group_profile(group_profile)
            
            log_analytics(bot_username, "crm_message_sent", {
                "group_id": group_id,
                "user_id": user_id,
                "message_type": message_type
            })
            
        except Exception as e:
            log_event("crm_db", f"❌ Mesaj kaydetme hatası: {e}")
    
    async def record_user_response(self, bot_username: str, group_id: int, user_id: int,
                                 response_content: str, response_to_bot: bool = True):
        """Kullanıcı yanıtını kaydet"""
        try:
            now = datetime.now()
            
            # Kullanıcı profilini güncelle
            user_profile = await self.get_user_profile(user_id)
            if user_profile:
                user_profile.total_interactions += 1
                user_profile.last_seen = now
                
                # Aktif saat güncelle
                current_hour = now.hour
                if current_hour not in user_profile.active_hours:
                    user_profile.active_hours.append(current_hour)
                
                # Bot tercihi güncelle
                if bot_username not in user_profile.preferred_bots:
                    user_profile.preferred_bots.append(bot_username)
                
                # Grup aktivitesi güncelle
                if group_id not in user_profile.group_activity_score:
                    user_profile.group_activity_score[group_id] = 0.0
                user_profile.group_activity_score[group_id] += 1.0
                
                await self.update_user_profile(user_profile)
            
            # Grup profilini güncelle
            if response_to_bot:
                group_profile = await self.get_group_profile(group_id)
                if group_profile:
                    group_profile.total_responses_received += 1
                    group_profile.last_activity = now
                    
                    # Response rate hesapla
                    if group_profile.total_messages_sent > 0:
                        group_profile.response_rate = group_profile.total_responses_received / group_profile.total_messages_sent
                    
                    # Bot performansını güncelle
                    if bot_username in group_profile.bot_performance:
                        group_profile.bot_performance[bot_username]["responses_received"] += 1
                    
                    await self.update_group_profile(group_profile)
            
            log_analytics(bot_username, "crm_user_response", {
                "group_id": group_id,
                "user_id": user_id,
                "response_to_bot": response_to_bot
            })
            
        except Exception as e:
            log_event("crm_db", f"❌ Yanıt kaydetme hatası: {e}")

# Global instance
crm_db = CRMDatabase() 