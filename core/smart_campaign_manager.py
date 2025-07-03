# core/smart_campaign_manager.py
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from core.crm_database import crm_db, UserProfile, GroupProfile
from core.crm_analytics import crm_analytics
from gpt.flirt_agent import generate_reply
from utilities.log_utils import log_event
from core.analytics_logger import log_analytics

@dataclass
class CampaignMessage:
    """Kampanya mesaj modeli"""
    content: str
    target_group_id: int
    bot_username: str
    scheduled_time: datetime
    message_type: str  # engaging, reply, vip_offer
    personalization_data: Dict
    priority: int  # 1-5 arası

@dataclass
class CampaignPlan:
    """Kampanya planı modeli"""
    campaign_id: str
    bot_username: str
    target_groups: List[int]
    messages: List[CampaignMessage]
    start_time: datetime
    end_time: datetime
    strategy: Dict
    status: str  # planned, active, paused, completed

class SmartCampaignManager:
    """Akıllı kampanya yönetim sistemi"""
    
    def __init__(self):
        self.active_campaigns = {}
        self.message_queue = []
        self.running = False
    
    async def start_campaign_manager(self):
        """Kampanya yöneticisini başlat"""
        self.running = True
        log_event("campaign_manager", "🚀 Akıllı kampanya yöneticisi başlatıldı")
        
        # Background task'ları başlat
        asyncio.create_task(self._campaign_scheduler())
        asyncio.create_task(self._message_processor())
        asyncio.create_task(self._performance_monitor())
    
    async def stop_campaign_manager(self):
        """Kampanya yöneticisini durdur"""
        self.running = False
        log_event("campaign_manager", "⏹️ Akıllı kampanya yöneticisi durduruldu")
    
    # ===== CAMPAIGN CREATION =====
    
    async def create_smart_campaign(self, bot_username: str, campaign_type: str = "engagement") -> str:
        """Akıllı kampanya oluştur"""
        try:
            # Kampanya stratejisi al
            strategy = await crm_analytics.optimize_campaign_targeting(bot_username)
            if not strategy:
                log_event("campaign_manager", f"❌ Strateji oluşturulamadı: {bot_username}")
                return None
            
            # Kampanya ID oluştur
            campaign_id = f"{bot_username}_{campaign_type}_{int(datetime.now().timestamp())}"
            
            # Hedef grupları seç
            target_groups = [g["group_id"] for g in strategy.get("top_groups", [])[:5]]
            
            # Mesajları oluştur
            messages = await self._generate_campaign_messages(
                bot_username, target_groups, strategy, campaign_type
            )
            
            # Kampanya planı oluştur
            campaign_plan = CampaignPlan(
                campaign_id=campaign_id,
                bot_username=bot_username,
                target_groups=target_groups,
                messages=messages,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=24),
                strategy=strategy,
                status="planned"
            )
            
            # Kampanyayı kaydet
            self.active_campaigns[campaign_id] = campaign_plan
            
            log_event("campaign_manager", f"✅ Akıllı kampanya oluşturuldu: {campaign_id}")
            log_analytics(bot_username, "smart_campaign_created", {
                "campaign_id": campaign_id,
                "target_groups": len(target_groups),
                "total_messages": len(messages)
            })
            
            return campaign_id
            
        except Exception as e:
            log_event("campaign_manager", f"❌ Kampanya oluşturma hatası {bot_username}: {e}")
            return None
    
    async def _generate_campaign_messages(self, bot_username: str, target_groups: List[int], 
                                        strategy: Dict, campaign_type: str) -> List[CampaignMessage]:
        """Kampanya mesajlarını oluştur"""
        try:
            messages = []
            
            # Bot profilini al
            from core.profile_loader import load_profile
            bot_profile = load_profile(bot_username)
            
            # Her grup için mesajlar oluştur
            for group_id in target_groups:
                group_profile = await crm_db.get_group_profile(group_id)
                if not group_profile:
                    continue
                
                # Grup için optimal mesaj sayısını hesapla
                message_count = await self._calculate_optimal_message_count(group_profile, strategy)
                
                # Mesaj zamanlarını hesapla
                message_times = await self._calculate_message_schedule(group_profile, strategy, message_count)
                
                # Her mesaj için içerik oluştur
                for i, scheduled_time in enumerate(message_times):
                    # Mesaj tipini belirle
                    if i == 0:
                        message_type = "engaging"
                    elif i == len(message_times) - 1:
                        message_type = "vip_offer"
                    else:
                        message_type = "engaging"
                    
                    # Kişiselleştirilmiş mesaj oluştur
                    content = await self._generate_personalized_message(
                        bot_username, bot_profile, group_profile, message_type, strategy
                    )
                    
                    message = CampaignMessage(
                        content=content,
                        target_group_id=group_id,
                        bot_username=bot_username,
                        scheduled_time=scheduled_time,
                        message_type=message_type,
                        personalization_data={
                            "group_title": group_profile.title,
                            "activity_level": group_profile.activity_level,
                            "member_count": group_profile.member_count
                        },
                        priority=group_profile.target_priority
                    )
                    
                    messages.append(message)
            
            # Mesajları öncelik ve zamana göre sırala
            messages.sort(key=lambda x: (x.scheduled_time, -x.priority))
            
            return messages
            
        except Exception as e:
            log_event("campaign_manager", f"❌ Mesaj oluşturma hatası: {e}")
            return []
    
    async def _calculate_optimal_message_count(self, group_profile: GroupProfile, strategy: Dict) -> int:
        """Grup için optimal mesaj sayısını hesapla"""
        try:
            base_count = 2  # Minimum 2 mesaj
            
            # Activity level'a göre artır
            activity_multipliers = {
                "dead": 0.5,
                "low": 0.8,
                "medium": 1.0,
                "high": 1.5,
                "very_high": 2.0
            }
            
            multiplier = activity_multipliers.get(group_profile.activity_level, 1.0)
            
            # Spam tolerance'a göre ayarla
            if group_profile.spam_tolerance < 0.3:
                multiplier *= 0.7
            elif group_profile.spam_tolerance > 0.7:
                multiplier *= 1.3
            
            # Campaign fatigue'a göre azalt
            if group_profile.campaign_fatigue_score > 0.5:
                multiplier *= 0.6
            
            optimal_count = max(1, min(5, int(base_count * multiplier)))
            return optimal_count
            
        except Exception as e:
            log_event("campaign_manager", f"❌ Mesaj sayısı hesaplama hatası: {e}")
            return 2
    
    async def _calculate_message_schedule(self, group_profile: GroupProfile, strategy: Dict, 
                                        message_count: int) -> List[datetime]:
        """Mesaj zamanlamasını hesapla"""
        try:
            now = datetime.now()
            schedule = []
            
            # Optimal saatleri al
            optimal_hours = strategy.get("message_schedule", {}).get("optimal_hours", [14, 18, 21])
            
            # Grup peak hours'ları da dikkate al
            if group_profile.peak_hours:
                combined_hours = list(set(optimal_hours + group_profile.peak_hours))
            else:
                combined_hours = optimal_hours
            
            # Mesajları dağıt
            for i in range(message_count):
                # Saat seç
                hour = random.choice(combined_hours)
                
                # Gün hesapla (ilk mesaj bugün, diğerleri sonraki günlerde)
                days_offset = i // 3  # Her 3 mesajda bir gün ilerle
                
                # Dakika randomize et
                minute = random.randint(0, 59)
                
                scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                scheduled_time += timedelta(days=days_offset)
                
                # Geçmiş zaman kontrolü
                if scheduled_time <= now:
                    scheduled_time = now + timedelta(minutes=random.randint(5, 30))
                
                schedule.append(scheduled_time)
            
            return sorted(schedule)
            
        except Exception as e:
            log_event("campaign_manager", f"❌ Zamanlama hesaplama hatası: {e}")
            return [datetime.now() + timedelta(minutes=5)]
    
    async def _generate_personalized_message(self, bot_username: str, bot_profile: Dict, 
                                           group_profile: GroupProfile, message_type: str, 
                                           strategy: Dict) -> str:
        """Kişiselleştirilmiş mesaj oluştur"""
        try:
            # Mesaj tipine göre template seç
            if message_type == "vip_offer":
                base_messages = [
                    f"🔥 VIP grubumda özel içerikler var! {bot_profile.get('vip_price', '250')}₺ ile katıl 💎",
                    f"💋 Özel show'larım sadece VIP'lerde! {bot_profile.get('vip_price', '250')}₺ - DM at 🎭",
                    f"✨ VIP üyeliğin hazır! {bot_profile.get('vip_price', '250')}₺ ile premium deneyim 👑"
                ]
            else:
                # Engaging messages from bot profile
                base_messages = bot_profile.get("engaging_messages", [
                    "Selam güzeller! Bugün nasılsınız? 😊",
                    "Yeni bir gün, yeni fırsatlar! Kim hazır? 🌟",
                    "Burada güzel insanlar var! Tanışalım mı? 💕"
                ])
            
            # Grup özelliklerine göre kişiselleştir
            selected_message = random.choice(base_messages)
            
            # Grup aktivitesine göre ton ayarla
            if group_profile.activity_level == "very_high":
                # Daha enerjik ton
                if "!" not in selected_message:
                    selected_message += " 🔥"
            elif group_profile.activity_level in ["low", "dead"]:
                # Daha yumuşak ton
                selected_message = selected_message.replace("!", ".")
            
            # Grup büyüklüğüne göre ayarla
            if group_profile.member_count > 1000:
                # Büyük grup için daha genel mesaj
                pass
            elif group_profile.member_count < 50:
                # Küçük grup için daha samimi mesaj
                selected_message = selected_message.replace("güzeller", "canlarım")
            
            return selected_message
            
        except Exception as e:
            log_event("campaign_manager", f"❌ Mesaj kişiselleştirme hatası: {e}")
            return "Selam! Nasılsınız? 😊"
    
    # ===== CAMPAIGN EXECUTION =====
    
    async def _campaign_scheduler(self):
        """Kampanya zamanlayıcısı"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Aktif kampanyaları kontrol et
                for campaign_id, campaign in list(self.active_campaigns.items()):
                    if campaign.status == "planned" and campaign.start_time <= current_time:
                        # Kampanyayı aktifleştir
                        campaign.status = "active"
                        log_event("campaign_manager", f"🟢 Kampanya aktifleştirildi: {campaign_id}")
                        
                        # Mesajları kuyruğa ekle
                        for message in campaign.messages:
                            if message.scheduled_time <= current_time + timedelta(hours=1):
                                self.message_queue.append(message)
                    
                    elif campaign.status == "active" and campaign.end_time <= current_time:
                        # Kampanyayı tamamla
                        campaign.status = "completed"
                        log_event("campaign_manager", f"✅ Kampanya tamamlandı: {campaign_id}")
                
                await asyncio.sleep(60)  # Her dakika kontrol et
                
            except Exception as e:
                log_event("campaign_manager", f"❌ Kampanya zamanlayıcı hatası: {e}")
                await asyncio.sleep(60)
    
    async def _message_processor(self):
        """Mesaj işleyicisi"""
        while self.running:
            try:
                if not self.message_queue:
                    await asyncio.sleep(30)
                    continue
                
                current_time = datetime.now()
                
                # Zamanı gelen mesajları işle
                messages_to_send = []
                remaining_messages = []
                
                for message in self.message_queue:
                    if message.scheduled_time <= current_time:
                        messages_to_send.append(message)
                    else:
                        remaining_messages.append(message)
                
                self.message_queue = remaining_messages
                
                # Mesajları gönder
                for message in messages_to_send:
                    await self._send_campaign_message(message)
                    await asyncio.sleep(random.randint(5, 15))  # Mesajlar arası delay
                
                await asyncio.sleep(30)
                
            except Exception as e:
                log_event("campaign_manager", f"❌ Mesaj işleyici hatası: {e}")
                await asyncio.sleep(30)
    
    async def _send_campaign_message(self, message: CampaignMessage):
        """Kampanya mesajını gönder"""
        try:
            # Client'ı al
            from core.controller import get_client_by_username
            client = get_client_by_username(message.bot_username)
            
            if not client:
                log_event("campaign_manager", f"❌ Client bulunamadı: {message.bot_username}")
                return
            
            # Mesajı gönder
            await client.send_message(message.target_group_id, message.content)
            
            # CRM'e kaydet
            await crm_db.record_message_sent(
                message.bot_username,
                message.target_group_id,
                0,  # System user
                message.content,
                message.message_type
            )
            
            log_event("campaign_manager", f"📤 Kampanya mesajı gönderildi: {message.bot_username} -> {message.target_group_id}")
            log_analytics(message.bot_username, "campaign_message_sent", {
                "group_id": message.target_group_id,
                "message_type": message.message_type,
                "priority": message.priority
            })
            
        except Exception as e:
            log_event("campaign_manager", f"❌ Kampanya mesaj gönderme hatası: {e}")
    
    # ===== PERFORMANCE MONITORING =====
    
    async def _performance_monitor(self):
        """Performans izleyicisi"""
        while self.running:
            try:
                # Her 30 dakikada bir performans kontrolü
                await asyncio.sleep(1800)
                
                for campaign_id, campaign in self.active_campaigns.items():
                    if campaign.status == "active":
                        await self._analyze_campaign_performance(campaign)
                
            except Exception as e:
                log_event("campaign_manager", f"❌ Performans izleme hatası: {e}")
                await asyncio.sleep(1800)
    
    async def _analyze_campaign_performance(self, campaign: CampaignPlan):
        """Kampanya performansını analiz et"""
        try:
            # Gönderilen mesaj sayısı
            sent_messages = len([m for m in campaign.messages if m.scheduled_time <= datetime.now()])
            
            # Response rate hesapla (basit implementasyon)
            total_responses = 0
            for group_id in campaign.target_groups:
                group_profile = await crm_db.get_group_profile(group_id)
                if group_profile and campaign.bot_username in group_profile.bot_performance:
                    bot_perf = group_profile.bot_performance[campaign.bot_username]
                    total_responses += bot_perf.get("responses_received", 0)
            
            # Performans skoru hesapla
            if sent_messages > 0:
                response_rate = total_responses / sent_messages
                performance_score = min(100, response_rate * 100)
            else:
                performance_score = 0
            
            # Düşük performans uyarısı
            if performance_score < 10 and sent_messages > 3:
                log_event("campaign_manager", f"⚠️ Düşük performans: {campaign.campaign_id} - Skor: {performance_score:.1f}")
                
                # Kampanyayı duraklat
                campaign.status = "paused"
                log_event("campaign_manager", f"⏸️ Kampanya duraklatıldı: {campaign.campaign_id}")
            
            log_analytics(campaign.bot_username, "campaign_performance_check", {
                "campaign_id": campaign.campaign_id,
                "sent_messages": sent_messages,
                "total_responses": total_responses,
                "performance_score": performance_score
            })
            
        except Exception as e:
            log_event("campaign_manager", f"❌ Kampanya performans analizi hatası: {e}")
    
    # ===== PUBLIC METHODS =====
    
    async def get_campaign_status(self, campaign_id: str) -> Dict:
        """Kampanya durumunu getir"""
        try:
            if campaign_id not in self.active_campaigns:
                return {"error": "Kampanya bulunamadı"}
            
            campaign = self.active_campaigns[campaign_id]
            
            # İstatistikleri hesapla
            total_messages = len(campaign.messages)
            sent_messages = len([m for m in campaign.messages if m.scheduled_time <= datetime.now()])
            pending_messages = total_messages - sent_messages
            
            return {
                "campaign_id": campaign_id,
                "bot_username": campaign.bot_username,
                "status": campaign.status,
                "target_groups": len(campaign.target_groups),
                "total_messages": total_messages,
                "sent_messages": sent_messages,
                "pending_messages": pending_messages,
                "start_time": campaign.start_time.isoformat(),
                "end_time": campaign.end_time.isoformat()
            }
            
        except Exception as e:
            log_event("campaign_manager", f"❌ Kampanya durum alma hatası: {e}")
            return {"error": str(e)}
    
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Kampanyayı duraklat"""
        try:
            if campaign_id in self.active_campaigns:
                self.active_campaigns[campaign_id].status = "paused"
                log_event("campaign_manager", f"⏸️ Kampanya duraklatıldı: {campaign_id}")
                return True
            return False
        except Exception as e:
            log_event("campaign_manager", f"❌ Kampanya duraklatma hatası: {e}")
            return False
    
    async def resume_campaign(self, campaign_id: str) -> bool:
        """Kampanyayı devam ettir"""
        try:
            if campaign_id in self.active_campaigns:
                self.active_campaigns[campaign_id].status = "active"
                log_event("campaign_manager", f"▶️ Kampanya devam ettirildi: {campaign_id}")
                return True
            return False
        except Exception as e:
            log_event("campaign_manager", f"❌ Kampanya devam ettirme hatası: {e}")
            return False

# Global instance
smart_campaign_manager = SmartCampaignManager() 