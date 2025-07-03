# core/dynamic_delivery_optimizer.py
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import openai

from core.crm_database import crm_db, UserProfile, GroupProfile
from core.user_segmentation import user_segmentation, UserSegment, SegmentProfile
from core.crm_analytics import crm_analytics
from utilities.log_utils import log_event
from core.analytics_logger import log_analytics

@dataclass
class DeliveryStrategy:
    """Gönderim stratejisi"""
    segment: UserSegment
    priority: int  # 1-10 arası öncelik
    message_types: List[str]  # engaging, vip_offer, reactivation, etc.
    frequency: str  # hourly, daily, weekly, monthly
    optimal_hours: List[int]
    max_messages_per_day: int
    cooldown_hours: int  # Mesajlar arası minimum bekleme
    content_templates: List[str]
    success_metrics: Dict[str, float]  # response_rate, conversion_rate, etc.

@dataclass
class OptimizedMessage:
    """Optimize edilmiş mesaj"""
    user_id: int
    group_id: int
    bot_username: str
    content: str
    scheduled_time: datetime
    segment: UserSegment
    priority: float
    expected_response_rate: float
    personalization_data: Dict

class DynamicDeliveryOptimizer:
    """Dinamik gönderim optimizasyon sistemi"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()
        self.delivery_strategies = self._init_delivery_strategies()
        self.message_queue = []
        self.performance_history = {}  # {segment: {date: metrics}}
        self.learning_data = {}  # Öğrenme verileri
        self.running = False
    
    def _init_delivery_strategies(self) -> Dict[UserSegment, DeliveryStrategy]:
        """Başlangıç gönderim stratejilerini tanımla"""
        return {
            UserSegment.HOT_LEAD: DeliveryStrategy(
                segment=UserSegment.HOT_LEAD,
                priority=10,
                message_types=["vip_offer", "personal", "engaging"],
                frequency="daily",
                optimal_hours=[20, 21, 22],
                max_messages_per_day=3,
                cooldown_hours=4,
                content_templates=["premium_offer", "exclusive_content", "limited_time"],
                success_metrics={"response_rate": 0.0, "conversion_rate": 0.0}
            ),
            UserSegment.WARM_LEAD: DeliveryStrategy(
                segment=UserSegment.WARM_LEAD,
                priority=7,
                message_types=["engaging", "value_prop", "social_proof"],
                frequency="every_2_days",
                optimal_hours=[19, 20, 21],
                max_messages_per_day=2,
                cooldown_hours=12,
                content_templates=["soft_sell", "testimonial", "benefit_focused"],
                success_metrics={"response_rate": 0.0, "conversion_rate": 0.0}
            ),
            UserSegment.ENGAGED: DeliveryStrategy(
                segment=UserSegment.ENGAGED,
                priority=8,
                message_types=["special_content", "vip_upgrade", "loyalty"],
                frequency="daily",
                optimal_hours=[19, 20, 21, 22],
                max_messages_per_day=2,
                cooldown_hours=6,
                content_templates=["reward", "exclusive", "appreciation"],
                success_metrics={"response_rate": 0.0, "conversion_rate": 0.0}
            ),
            UserSegment.NEW_USER: DeliveryStrategy(
                segment=UserSegment.NEW_USER,
                priority=6,
                message_types=["welcome", "introduction", "soft_engage"],
                frequency="every_2_days",
                optimal_hours=[19, 20, 21],
                max_messages_per_day=1,
                cooldown_hours=24,
                content_templates=["welcome_series", "value_intro", "community"],
                success_metrics={"response_rate": 0.0, "conversion_rate": 0.0}
            ),
            UserSegment.NIGHT_OWL: DeliveryStrategy(
                segment=UserSegment.NIGHT_OWL,
                priority=5,
                message_types=["night_special", "live_content", "exclusive_night"],
                frequency="nightly",
                optimal_hours=[22, 23, 0, 1],
                max_messages_per_day=2,
                cooldown_hours=8,
                content_templates=["night_exclusive", "late_night_chat", "after_hours"],
                success_metrics={"response_rate": 0.0, "conversion_rate": 0.0}
            )
        }
    
    async def start_optimizer(self):
        """Optimizer'ı başlat"""
        self.running = True
        log_event("delivery_optimizer", "🚀 Dinamik gönderim optimizer başlatıldı")
        
        # Background task'ları başlat
        asyncio.create_task(self._optimization_loop())
        asyncio.create_task(self._delivery_processor())
        asyncio.create_task(self._performance_analyzer())
        asyncio.create_task(self._strategy_learner())
    
    async def stop_optimizer(self):
        """Optimizer'ı durdur"""
        self.running = False
        log_event("delivery_optimizer", "⏹️ Dinamik gönderim optimizer durduruldu")
    
    async def _optimization_loop(self):
        """Ana optimizasyon döngüsü"""
        while self.running:
            try:
                # Aktif kullanıcıları segmentlere göre al
                optimized_messages = await self._create_optimized_messages()
                
                # Mesajları kuyruğa ekle
                self.message_queue.extend(optimized_messages)
                
                # Önceliğe göre sırala
                self.message_queue.sort(key=lambda x: x.priority, reverse=True)
                
                log_event("delivery_optimizer", 
                         f"📊 {len(optimized_messages)} optimize mesaj oluşturuldu")
                
                # 30 dakika bekle
                await asyncio.sleep(1800)
                
            except Exception as e:
                log_event("delivery_optimizer", f"❌ Optimizasyon döngüsü hatası: {e}")
                await asyncio.sleep(300)
    
    async def _create_optimized_messages(self) -> List[OptimizedMessage]:
        """Optimize edilmiş mesajlar oluştur"""
        optimized_messages = []
        
        try:
            # Paket kontrolü için package manager'ı import et
            from core.package_manager import package_manager, PackageType
            
            # Her segment için kullanıcıları al
            for segment, strategy in self.delivery_strategies.items():
                # Bu segmentteki kullanıcıları al
                segment_users = await user_segmentation.get_segment_users(segment, limit=20)
                
                if not segment_users:
                    continue
                
                # Her kullanıcı için optimize mesaj oluştur
                for user in segment_users:
                    # Kullanıcının paketini kontrol et
                    user_package = package_manager.get_user_package(user.user_id)
                    if user_package != PackageType.ENTERPRISE:
                        # Enterprise değilse dinamik gönderim yapma
                        continue
                    
                    # Kullanıcının son mesaj zamanını kontrol et
                    if not await self._can_send_to_user(user, strategy):
                        continue
                    
                    # En uygun grubu seç
                    best_group = await self._select_best_group_for_user(user)
                    if not best_group:
                        continue
                    
                    # Mesaj içeriğini oluştur
                    message = await self._create_personalized_message(
                        user, segment, strategy, best_group
                    )
                    
                    if message:
                        optimized_messages.append(message)
            
            return optimized_messages
            
        except Exception as e:
            log_event("delivery_optimizer", f"❌ Mesaj oluşturma hatası: {e}")
            return []
    
    async def _can_send_to_user(self, user: UserProfile, strategy: DeliveryStrategy) -> bool:
        """Kullanıcıya mesaj gönderilip gönderilemeyeceğini kontrol et"""
        try:
            # Son mesaj zamanını kontrol et
            last_message_key = f"last_message:{user.user_id}"
            last_message_time = await crm_db.redis.get(last_message_key)
            
            if last_message_time:
                last_time = datetime.fromisoformat(last_message_time.decode())
                hours_passed = (datetime.now() - last_time).total_seconds() / 3600
                
                if hours_passed < strategy.cooldown_hours:
                    return False
            
            # Günlük mesaj limitini kontrol et
            today_key = f"daily_messages:{user.user_id}:{datetime.now().date()}"
            today_count = await crm_db.redis.get(today_key)
            
            if today_count and int(today_count) >= strategy.max_messages_per_day:
                return False
            
            return True
            
        except Exception as e:
            log_event("delivery_optimizer", f"❌ Kullanıcı kontrol hatası: {e}")
            return False
    
    async def _select_best_group_for_user(self, user: UserProfile) -> Optional[int]:
        """Kullanıcı için en uygun grubu seç"""
        try:
            # Kullanıcının aktif olduğu grupları al
            if not user.group_memberships:
                return None
            
            # Her grup için skor hesapla
            group_scores = []
            
            for group_id in user.group_memberships[:10]:  # İlk 10 grup
                group_profile = await crm_db.get_group_profile(group_id)
                if not group_profile:
                    continue
                
                # Grup skoru hesapla
                score = 0.0
                
                # Aktivite seviyesi
                activity_scores = {
                    "very_high": 1.0, "high": 0.8, "medium": 0.6, 
                    "low": 0.4, "dead": 0.2, "unknown": 0.5
                }
                score += activity_scores.get(group_profile.activity_level, 0.5) * 30
                
                # Kullanıcının grup aktivitesi
                user_group_activity = user.group_activity_score.get(group_id, 0)
                score += min(user_group_activity / 10, 1.0) * 40
                
                # Grup spam toleransı
                score += group_profile.spam_tolerance * 30
                
                group_scores.append((group_id, score))
            
            # En yüksek skorlu grubu seç
            if group_scores:
                group_scores.sort(key=lambda x: x[1], reverse=True)
                return group_scores[0][0]
            
            return None
            
        except Exception as e:
            log_event("delivery_optimizer", f"❌ Grup seçim hatası: {e}")
            return None
    
    async def _create_personalized_message(self, user: UserProfile, segment: UserSegment,
                                         strategy: DeliveryStrategy, group_id: int) -> Optional[OptimizedMessage]:
        """Kişiselleştirilmiş mesaj oluştur"""
        try:
            # GPT ile mesaj oluştur
            prompt = f"""
            Aşağıdaki kullanıcı için kişiselleştirilmiş mesaj oluştur:
            
            Kullanıcı Segmenti: {segment.value}
            Kullanıcı Özellikleri:
            - İsim: {user.first_name}
            - Engagement skoru: {user.engagement_score}
            - Aktif saatler: {user.active_hours[:3] if user.active_hours else 'Belirsiz'}
            - İlgi alanları: {user.interests if user.interests else 'Belirsiz'}
            
            Mesaj Stratejisi:
            - Mesaj tipleri: {strategy.message_types}
            - İçerik şablonları: {strategy.content_templates}
            
            Bu bilgilere göre, samimi ve ilgi çekici bir mesaj oluştur.
            Mesaj maximum 100 karakter olmalı ve emoji içermeli.
            
            Sadece mesaj metnini döndür, başka bir şey ekleme.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=50
            )
            
            content = response.choices[0].message.content.strip()
            
            # Optimal zamanı hesapla
            now = datetime.now()
            if user.active_hours and strategy.optimal_hours:
                # Kullanıcının aktif saatleri ile strateji saatlerinin kesişimi
                best_hours = list(set(user.active_hours) & set(strategy.optimal_hours))
                if not best_hours:
                    best_hours = strategy.optimal_hours
            else:
                best_hours = strategy.optimal_hours
            
            # Bir sonraki uygun saati bul
            scheduled_hour = random.choice(best_hours)
            scheduled_time = now.replace(hour=scheduled_hour, minute=random.randint(0, 59))
            
            if scheduled_time <= now:
                scheduled_time += timedelta(days=1)
            
            # Bot seç (kullanıcının tercih ettiği botlardan)
            from core.profile_loader import get_all_profiles
            all_bots = list(get_all_profiles().keys())
            
            if user.preferred_bots:
                bot_username = random.choice(user.preferred_bots)
            else:
                bot_username = random.choice(all_bots) if all_bots else "default_bot"
            
            # Expected response rate hesapla
            base_rate = 0.1  # %10 baz oran
            segment_multipliers = {
                UserSegment.HOT_LEAD: 3.0,
                UserSegment.ENGAGED: 2.5,
                UserSegment.WARM_LEAD: 1.5,
                UserSegment.BOT_LOVER: 2.0,
                UserSegment.NEW_USER: 1.2
            }
            
            expected_response_rate = base_rate * segment_multipliers.get(segment, 1.0)
            expected_response_rate = min(expected_response_rate, 0.5)  # Max %50
            
            return OptimizedMessage(
                user_id=user.user_id,
                group_id=group_id,
                bot_username=bot_username,
                content=content,
                scheduled_time=scheduled_time,
                segment=segment,
                priority=strategy.priority * user.engagement_score / 100,
                expected_response_rate=expected_response_rate,
                personalization_data={
                    "user_name": user.first_name,
                    "segment": segment.value,
                    "interests": user.interests
                }
            )
            
        except Exception as e:
            log_event("delivery_optimizer", f"❌ Mesaj kişiselleştirme hatası: {e}")
            return None
    
    async def _delivery_processor(self):
        """Mesaj gönderim işleyicisi"""
        while self.running:
            try:
                if not self.message_queue:
                    await asyncio.sleep(60)
                    continue
                
                current_time = datetime.now()
                messages_to_send = []
                remaining_messages = []
                
                # Zamanı gelen mesajları ayır
                for message in self.message_queue:
                    if message.scheduled_time <= current_time:
                        messages_to_send.append(message)
                    else:
                        remaining_messages.append(message)
                
                self.message_queue = remaining_messages
                
                # Mesajları gönder
                for message in messages_to_send:
                    await self._send_optimized_message(message)
                    await asyncio.sleep(random.randint(5, 15))  # Anti-spam delay
                
                await asyncio.sleep(60)
                
            except Exception as e:
                log_event("delivery_optimizer", f"❌ Gönderim işleyici hatası: {e}")
                await asyncio.sleep(60)
    
    async def _send_optimized_message(self, message: OptimizedMessage):
        """Optimize edilmiş mesajı gönder"""
        try:
            # Client'ı al
            from core.controller import get_client_by_username
            client = get_client_by_username(message.bot_username)
            
            if not client:
                log_event("delivery_optimizer", f"❌ Client bulunamadı: {message.bot_username}")
                return
            
            # Mesajı gönder
            await client.send_message(message.group_id, message.content)
            
            # CRM'e kaydet
            await crm_db.record_message_sent(
                message.bot_username,
                message.group_id,
                message.user_id,
                message.content,
                "optimized"
            )
            
            # Son mesaj zamanını güncelle
            last_message_key = f"last_message:{message.user_id}"
            await crm_db.redis.set(last_message_key, datetime.now().isoformat())
            
            # Günlük mesaj sayısını artır
            today_key = f"daily_messages:{message.user_id}:{datetime.now().date()}"
            await crm_db.redis.incr(today_key)
            await crm_db.redis.expire(today_key, 86400)  # 1 gün TTL
            
            # Analytics
            log_analytics("delivery_optimizer", "optimized_message_sent", {
                "user_id": message.user_id,
                "group_id": message.group_id,
                "segment": message.segment.value,
                "bot": message.bot_username,
                "expected_response_rate": message.expected_response_rate
            })
            
            log_event("delivery_optimizer", 
                     f"📤 Optimize mesaj gönderildi: {message.segment.value} -> {message.group_id}")
            
        except Exception as e:
            log_event("delivery_optimizer", f"❌ Mesaj gönderme hatası: {e}")
    
    async def _performance_analyzer(self):
        """Performans analiz döngüsü"""
        while self.running:
            try:
                # Her saat performans analizi yap
                await asyncio.sleep(3600)
                
                # Her segment için performans metrikleri hesapla
                for segment in UserSegment:
                    await self._analyze_segment_performance(segment)
                
                # Genel performans raporu
                await self._generate_performance_report()
                
            except Exception as e:
                log_event("delivery_optimizer", f"❌ Performans analizi hatası: {e}")
                await asyncio.sleep(3600)
    
    async def _analyze_segment_performance(self, segment: UserSegment):
        """Segment performansını analiz et"""
        try:
            # Son 24 saatteki performans verilerini topla
            end_time = datetime.now()
            start_time = end_time - timedelta(days=1)
            
            # Redis'ten mesaj verilerini al (basitleştirilmiş)
            total_sent = 0
            total_responses = 0
            
            # Gerçek implementasyonda Redis'ten detaylı veri çekilecek
            # Şimdilik simüle edilmiş veriler
            segment_users = await user_segmentation.get_segment_users(segment, limit=50)
            
            for user in segment_users:
                # Kullanıcının response rate'ini kullan
                total_sent += 10  # Simüle edilmiş
                total_responses += int(10 * user.response_rate)
            
            # Metrikleri hesapla
            response_rate = total_responses / max(total_sent, 1)
            
            # Stratejiyi güncelle
            if segment in self.delivery_strategies:
                self.delivery_strategies[segment].success_metrics["response_rate"] = response_rate
            
            # Performans verisini kaydet
            if segment not in self.performance_history:
                self.performance_history[segment] = {}
            
            self.performance_history[segment][end_time.date().isoformat()] = {
                "sent": total_sent,
                "responses": total_responses,
                "response_rate": response_rate
            }
            
            log_event("delivery_optimizer", 
                     f"📊 {segment.value} performans: {response_rate:.2%} yanıt oranı")
            
        except Exception as e:
            log_event("delivery_optimizer", f"❌ Segment performans analizi hatası: {e}")
    
    async def _strategy_learner(self):
        """Strateji öğrenme döngüsü - GPT ile sürekli iyileştirme"""
        while self.running:
            try:
                # Her 6 saatte bir strateji öğrenmesi yap
                await asyncio.sleep(21600)
                
                # Performans verilerini topla
                learning_data = {
                    "segments": {},
                    "overall_metrics": {}
                }
                
                for segment, history in self.performance_history.items():
                    if history:
                        # Son 7 günün ortalamasını al
                        recent_data = list(history.values())[-7:]
                        avg_response_rate = sum(d["response_rate"] for d in recent_data) / len(recent_data)
                        
                        learning_data["segments"][segment.value] = {
                            "current_strategy": {
                                "frequency": self.delivery_strategies[segment].frequency,
                                "max_messages_per_day": self.delivery_strategies[segment].max_messages_per_day,
                                "optimal_hours": self.delivery_strategies[segment].optimal_hours
                            },
                            "performance": {
                                "avg_response_rate": avg_response_rate,
                                "trend": "improving" if len(recent_data) > 1 and recent_data[-1]["response_rate"] > recent_data[0]["response_rate"] else "declining"
                            }
                        }
                
                # GPT'ye strateji iyileştirmesi için sor
                prompt = f"""
                Aşağıdaki segment performans verilerini analiz et ve strateji iyileştirmeleri öner:
                
                {json.dumps(learning_data, indent=2, ensure_ascii=False)}
                
                Her segment için:
                1. Mevcut performansı değerlendir
                2. İyileştirme önerileri sun
                3. Yeni optimal parametreler belirle
                
                JSON formatında yanıt ver:
                {{
                    "segment_name": {{
                        "recommended_changes": {{
                            "frequency": "new_frequency",
                            "max_messages_per_day": number,
                            "optimal_hours": [hour_list],
                            "reasoning": "Neden bu değişiklikler"
                        }}
                    }}
                }}
                """
                
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                
                recommendations = json.loads(response.choices[0].message.content)
                
                # Önerileri uygula
                await self._apply_strategy_improvements(recommendations)
                
                log_event("delivery_optimizer", "🧠 Strateji öğrenmesi tamamlandı")
                
            except Exception as e:
                log_event("delivery_optimizer", f"❌ Strateji öğrenme hatası: {e}")
                await asyncio.sleep(21600)
    
    async def _apply_strategy_improvements(self, recommendations: Dict):
        """Strateji iyileştirmelerini uygula"""
        try:
            for segment_name, changes in recommendations.items():
                # Segment enum'ını bul
                try:
                    segment = UserSegment[segment_name.upper()]
                except:
                    continue
                
                if segment not in self.delivery_strategies:
                    continue
                
                strategy = self.delivery_strategies[segment]
                rec_changes = changes.get("recommended_changes", {})
                
                # Değişiklikleri uygula
                if "frequency" in rec_changes:
                    strategy.frequency = rec_changes["frequency"]
                
                if "max_messages_per_day" in rec_changes:
                    strategy.max_messages_per_day = int(rec_changes["max_messages_per_day"])
                
                if "optimal_hours" in rec_changes:
                    strategy.optimal_hours = rec_changes["optimal_hours"]
                
                log_event("delivery_optimizer", 
                         f"✅ {segment.value} stratejisi güncellendi: {rec_changes.get('reasoning', 'GPT önerisi')}")
                
        except Exception as e:
            log_event("delivery_optimizer", f"❌ Strateji uygulama hatası: {e}")
    
    async def _generate_performance_report(self):
        """Genel performans raporu oluştur"""
        try:
            report = {
                "date": datetime.now().isoformat(),
                "segments": {},
                "top_performing": None,
                "needs_improvement": None
            }
            
            segment_scores = []
            
            for segment, strategy in self.delivery_strategies.items():
                metrics = strategy.success_metrics
                report["segments"][segment.value] = {
                    "response_rate": metrics.get("response_rate", 0),
                    "priority": strategy.priority,
                    "frequency": strategy.frequency
                }
                
                segment_scores.append((segment.value, metrics.get("response_rate", 0)))
            
            # En iyi ve kötü performans gösterenleri belirle
            segment_scores.sort(key=lambda x: x[1], reverse=True)
            
            if segment_scores:
                report["top_performing"] = segment_scores[0][0]
                report["needs_improvement"] = segment_scores[-1][0]
            
            log_event("delivery_optimizer", f"📊 Performans raporu: {json.dumps(report, indent=2)}")
            
            # Analytics'e kaydet
            log_analytics("delivery_optimizer", "performance_report", report)
            
        except Exception as e:
            log_event("delivery_optimizer", f"❌ Rapor oluşturma hatası: {e}")

# Global instance
delivery_optimizer = DynamicDeliveryOptimizer() 