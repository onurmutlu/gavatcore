# core/crm_analytics.py
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import asdict
import openai
from core.crm_database import crm_db, UserProfile, GroupProfile
from utils.log_utils import log_event
from core.analytics_logger import log_analytics

class CRMAnalytics:
    """GPT destekli CRM analiz sistemi"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()
    
    # ===== USER ANALYSIS =====
    
    async def analyze_user_behavior(self, user_profile: UserProfile) -> Dict:
        """Kullanıcı davranış analizi"""
        try:
            # GPT'ye gönderilecek kullanıcı verilerini hazırla
            user_data = {
                "user_id": user_profile.user_id,
                "username": user_profile.username,
                "total_interactions": user_profile.total_interactions,
                "response_rate": user_profile.response_rate,
                "engagement_score": user_profile.engagement_score,
                "active_hours": user_profile.active_hours,
                "preferred_bots": user_profile.preferred_bots,
                "interests": user_profile.interests,
                "conversion_potential": user_profile.conversion_potential,
                "group_activity_score": user_profile.group_activity_score
            }
            
            prompt = f"""
            Aşağıdaki kullanıcı verilerini analiz et ve detaylı bir profil çıkar:
            
            {json.dumps(user_data, indent=2, ensure_ascii=False)}
            
            Lütfen şu konularda analiz yap:
            1. Kullanıcının engagement seviyesi ve davranış kalıpları
            2. VIP'e dönüşme potansiyeli ve öneriler
            3. En aktif olduğu saatler ve optimal iletişim zamanları
            4. İlgi alanları ve içerik tercihleri
            5. Hangi bot'larla daha iyi etkileşim kurduğu
            6. Grup aktivite seviyesi ve sosyal davranışları
            7. Pazarlama stratejisi önerileri
            
            JSON formatında yanıt ver:
            {{
                "engagement_level": "low/medium/high/very_high",
                "conversion_probability": 0.0-1.0,
                "optimal_contact_hours": [saat listesi],
                "content_preferences": ["tercih1", "tercih2"],
                "recommended_approach": "yaklaşım stratejisi",
                "risk_factors": ["risk1", "risk2"],
                "opportunities": ["fırsat1", "fırsat2"],
                "next_actions": ["aksiyon1", "aksiyon2"]
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # Analiz sonuçlarını kullanıcı profiline uygula
            await self._apply_user_analysis(user_profile, analysis)
            
            log_event("crm_analytics", f"✅ Kullanıcı analizi tamamlandı: {user_profile.username}")
            return analysis
            
        except Exception as e:
            log_event("crm_analytics", f"❌ Kullanıcı analiz hatası {user_profile.user_id}: {e}")
            return {}
    
    async def _apply_user_analysis(self, user_profile: UserProfile, analysis: Dict):
        """Analiz sonuçlarını kullanıcı profiline uygula"""
        try:
            # Engagement score güncelle
            engagement_levels = {"low": 25, "medium": 50, "high": 75, "very_high": 95}
            if analysis.get("engagement_level") in engagement_levels:
                user_profile.engagement_score = engagement_levels[analysis["engagement_level"]]
            
            # Conversion potential güncelle
            if "conversion_probability" in analysis:
                user_profile.conversion_potential = float(analysis["conversion_probability"])
            
            # İçerik tercihlerini güncelle
            if "content_preferences" in analysis:
                user_profile.interests = analysis["content_preferences"]
            
            # Profili kaydet
            await crm_db.update_user_profile(user_profile)
            
        except Exception as e:
            log_event("crm_analytics", f"❌ Kullanıcı analiz uygulama hatası: {e}")
    
    # ===== GROUP ANALYSIS =====
    
    async def analyze_group_performance(self, group_profile: GroupProfile) -> Dict:
        """Grup performans analizi"""
        try:
            # GPT'ye gönderilecek grup verilerini hazırla
            group_data = {
                "group_id": group_profile.group_id,
                "title": group_profile.title,
                "member_count": group_profile.member_count,
                "total_messages_sent": group_profile.total_messages_sent,
                "total_responses_received": group_profile.total_responses_received,
                "response_rate": group_profile.response_rate,
                "activity_level": group_profile.activity_level,
                "member_engagement": group_profile.member_engagement,
                "spam_tolerance": group_profile.spam_tolerance,
                "bot_performance": group_profile.bot_performance,
                "campaign_fatigue_score": group_profile.campaign_fatigue_score,
                "target_priority": group_profile.target_priority
            }
            
            prompt = f"""
            Aşağıdaki grup verilerini analiz et ve detaylı bir performans raporu çıkar:
            
            {json.dumps(group_data, indent=2, ensure_ascii=False)}
            
            Lütfen şu konularda analiz yap:
            1. Grubun genel aktivite seviyesi ve engagement kalitesi
            2. Bot performansları ve hangi bot'un daha etkili olduğu
            3. Spam toleransı ve optimal mesaj sıklığı
            4. Kampanya yorgunluğu ve dinlenme ihtiyacı
            5. Hedefleme önceliği ve potansiyel değeri
            6. Risk faktörleri ve fırsatlar
            7. Gelişim önerileri ve strateji tavsiyeleri
            
            JSON formatında yanıt ver:
            {{
                "performance_score": 0.0-100.0,
                "activity_classification": "dead/low/medium/high/very_high",
                "best_performing_bot": "bot_username",
                "optimal_message_frequency": "günde kaç mesaj",
                "spam_risk_level": "low/medium/high",
                "campaign_readiness": "ready/needs_rest/oversaturated",
                "target_value": "low/medium/high/premium",
                "recommended_strategy": "strateji açıklaması",
                "improvement_areas": ["alan1", "alan2"],
                "next_campaign_timing": "ne zaman kampanya yapılmalı"
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # Analiz sonuçlarını grup profiline uygula
            await self._apply_group_analysis(group_profile, analysis)
            
            log_event("crm_analytics", f"✅ Grup analizi tamamlandı: {group_profile.title}")
            return analysis
            
        except Exception as e:
            log_event("crm_analytics", f"❌ Grup analiz hatası {group_profile.group_id}: {e}")
            return {}
    
    async def _apply_group_analysis(self, group_profile: GroupProfile, analysis: Dict):
        """Analiz sonuçlarını grup profiline uygula"""
        try:
            # Activity level güncelle
            if "activity_classification" in analysis:
                group_profile.activity_level = analysis["activity_classification"]
            
            # Member engagement güncelle
            if "performance_score" in analysis:
                group_profile.member_engagement = float(analysis["performance_score"]) / 100.0
            
            # Target priority güncelle
            target_values = {"low": 1, "medium": 3, "high": 4, "premium": 5}
            if analysis.get("target_value") in target_values:
                group_profile.target_priority = target_values[analysis["target_value"]]
            
            # Spam tolerance güncelle
            spam_levels = {"low": 0.3, "medium": 0.6, "high": 0.9}
            if analysis.get("spam_risk_level") in spam_levels:
                group_profile.spam_tolerance = spam_levels[analysis["spam_risk_level"]]
            
            # Profili kaydet
            await crm_db.update_group_profile(group_profile)
            
        except Exception as e:
            log_event("crm_analytics", f"❌ Grup analiz uygulama hatası: {e}")
    
    # ===== CAMPAIGN OPTIMIZATION =====
    
    async def optimize_campaign_targeting(self, bot_username: str) -> Dict:
        """Kampanya hedeflemesi optimizasyonu"""
        try:
            # Tüm grupları analiz et
            all_groups = await self._get_all_groups()
            group_scores = []
            
            for group_profile in all_groups:
                # Grup için hedefleme skoru hesapla
                score = await self._calculate_targeting_score(group_profile, bot_username)
                group_scores.append({
                    "group_id": group_profile.group_id,
                    "title": group_profile.title,
                    "score": score,
                    "profile": group_profile
                })
            
            # Skorlara göre sırala
            group_scores.sort(key=lambda x: x["score"], reverse=True)
            
            # En iyi 10 grubu seç
            top_groups = group_scores[:10]
            
            # GPT ile kampanya stratejisi oluştur
            campaign_data = {
                "bot_username": bot_username,
                "top_groups": [
                    {
                        "group_id": g["group_id"],
                        "title": g["title"],
                        "score": g["score"],
                        "response_rate": g["profile"].response_rate,
                        "activity_level": g["profile"].activity_level,
                        "member_count": g["profile"].member_count
                    }
                    for g in top_groups
                ]
            }
            
            prompt = f"""
            Aşağıdaki veriler için optimal kampanya stratejisi oluştur:
            
            {json.dumps(campaign_data, indent=2, ensure_ascii=False)}
            
            Lütfen şu konularda strateji öner:
            1. Hangi gruplara öncelik verilmeli
            2. Mesaj zamanlaması ve sıklığı
            3. İçerik stratejisi ve mesaj tonu
            4. Risk yönetimi ve spam önleme
            5. Performans takibi ve optimizasyon
            
            JSON formatında yanıt ver:
            {{
                "priority_groups": [{{group_id, reason}}],
                "message_schedule": {{
                    "frequency": "günlük/haftalık",
                    "optimal_hours": [saat listesi],
                    "rest_days": [gün listesi]
                }},
                "content_strategy": {{
                    "tone": "ton açıklaması",
                    "themes": ["tema1", "tema2"],
                    "personalization": "kişiselleştirme önerileri"
                }},
                "risk_management": {{
                    "spam_prevention": "önlem açıklaması",
                    "monitoring": "takip stratejisi"
                }},
                "success_metrics": ["metrik1", "metrik2"]
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            
            strategy = json.loads(response.choices[0].message.content)
            strategy["top_groups"] = top_groups
            
            log_event("crm_analytics", f"✅ Kampanya optimizasyonu tamamlandı: {bot_username}")
            return strategy
            
        except Exception as e:
            log_event("crm_analytics", f"❌ Kampanya optimizasyon hatası {bot_username}: {e}")
            return {}
    
    async def _calculate_targeting_score(self, group_profile: GroupProfile, bot_username: str) -> float:
        """Grup için hedefleme skoru hesapla"""
        try:
            score = 0.0
            
            # Response rate (0-30 puan)
            score += group_profile.response_rate * 30
            
            # Activity level (0-25 puan)
            activity_scores = {"dead": 0, "low": 5, "medium": 15, "high": 20, "very_high": 25}
            score += activity_scores.get(group_profile.activity_level, 10)
            
            # Member count (0-20 puan)
            if group_profile.member_count > 1000:
                score += 20
            elif group_profile.member_count > 500:
                score += 15
            elif group_profile.member_count > 100:
                score += 10
            else:
                score += 5
            
            # Bot performance (0-15 puan)
            if bot_username in group_profile.bot_performance:
                bot_perf = group_profile.bot_performance[bot_username]
                if bot_perf["messages_sent"] > 0:
                    bot_response_rate = bot_perf["responses_received"] / bot_perf["messages_sent"]
                    score += bot_response_rate * 15
            
            # Spam tolerance (0-10 puan)
            score += group_profile.spam_tolerance * 10
            
            # Campaign fatigue penalty (-20 to 0 puan)
            score -= group_profile.campaign_fatigue_score * 20
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            log_event("crm_analytics", f"❌ Hedefleme skoru hesaplama hatası: {e}")
            return 0.0
    
    async def _get_all_groups(self) -> List[GroupProfile]:
        """Tüm grup profillerini getir"""
        try:
            # Redis'ten tüm grup anahtarlarını al
            keys = await crm_db.redis.keys("crm:group:*")
            groups = []
            
            for key in keys:
                group_id = int(key.decode().split(":")[-1])
                group_profile = await crm_db.get_group_profile(group_id)
                if group_profile:
                    groups.append(group_profile)
            
            return groups
            
        except Exception as e:
            log_event("crm_analytics", f"❌ Grup listesi alma hatası: {e}")
            return []
    
    # ===== REPORTING =====
    
    async def generate_performance_report(self, bot_username: str, days: int = 7) -> Dict:
        """Performans raporu oluştur"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Mesaj ve yanıt istatistiklerini topla
            stats = await self._collect_performance_stats(bot_username, start_date, end_date)
            
            # GPT ile rapor oluştur
            prompt = f"""
            Aşağıdaki {days} günlük performans verilerini analiz et ve detaylı rapor oluştur:
            
            {json.dumps(stats, indent=2, ensure_ascii=False)}
            
            Raporda şunları içer:
            1. Genel performans özeti
            2. En başarılı gruplar ve stratejiler
            3. İyileştirme alanları
            4. Gelecek dönem önerileri
            5. Risk analizi
            
            Türkçe, profesyonel ve aksiyon odaklı bir rapor hazırla.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            report = {
                "bot_username": bot_username,
                "period": f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
                "stats": stats,
                "analysis": response.choices[0].message.content,
                "generated_at": datetime.now().isoformat()
            }
            
            log_event("crm_analytics", f"✅ Performans raporu oluşturuldu: {bot_username}")
            return report
            
        except Exception as e:
            log_event("crm_analytics", f"❌ Performans raporu hatası {bot_username}: {e}")
            return {}
    
    async def _collect_performance_stats(self, bot_username: str, start_date: datetime, end_date: datetime) -> Dict:
        """Performans istatistiklerini topla"""
        try:
            # Bu fonksiyon Redis'ten mesaj verilerini toplayacak
            # Şimdilik basit bir implementasyon
            stats = {
                "total_messages_sent": 0,
                "total_responses_received": 0,
                "unique_groups_reached": 0,
                "unique_users_engaged": 0,
                "average_response_rate": 0.0,
                "top_performing_groups": [],
                "engagement_trends": []
            }
            
            # Gerçek implementasyon Redis query'leri ile yapılacak
            return stats
            
        except Exception as e:
            log_event("crm_analytics", f"❌ İstatistik toplama hatası: {e}")
            return {}

# Global instance
crm_analytics = CRMAnalytics() 