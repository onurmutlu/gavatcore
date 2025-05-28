#!/usr/bin/env python3
"""
GavatCore V2 - Telegram Broadcast Sistemi
Veritabanı temelli, AI-powered broadcast yönetimi
"""

import asyncio
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
import structlog
from telethon import TelegramClient
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, ChatWriteForbiddenError
from .database_manager import database_manager, BroadcastTarget, BroadcastStatus, UserInteractionType

logger = structlog.get_logger("gavatcore.telegram_broadcaster")

class TelegramBroadcaster:
    """Veritabanı Temelli Telegram Broadcast Sistemi"""
    
    def __init__(self):
        self.clients: Dict[str, TelegramClient] = {}
        self.is_initialized = False
        self.broadcast_queue: List[Dict[str, Any]] = []
        self.processing_queue = False
        
        # Broadcast rate limiting
        self.rate_limits = {
            "group": {"messages_per_minute": 20, "delay_between": 3},
            "user": {"messages_per_minute": 30, "delay_between": 2}
        }
        
        logger.info("📢 Telegram Broadcaster başlatıldı")
    
    async def initialize(self, clients: Dict[str, TelegramClient]) -> None:
        """Broadcaster'ı başlat"""
        try:
            self.clients = clients
            
            # Database'i başlat
            await database_manager.initialize()
            
            # Mevcut grupları ve kullanıcıları tara
            await self._discover_targets()
            
            # Queue processor'ı başlat
            asyncio.create_task(self._process_broadcast_queue())
            
            self.is_initialized = True
            logger.info("✅ Telegram Broadcaster hazır")
            
        except Exception as e:
            logger.error(f"❌ Telegram Broadcaster başlatma hatası: {e}")
            raise
    
    async def _discover_targets(self) -> None:
        """Mevcut grupları ve kullanıcıları keşfet"""
        try:
            for bot_username, client in self.clients.items():
                try:
                    # Grupları tara
                    async for dialog in client.iter_dialogs():
                        if dialog.is_group or dialog.is_channel:
                            # Grup bilgilerini kaydet
                            await database_manager.update_group_analytics(
                                group_id=str(dialog.id),
                                group_name=dialog.title,
                                member_count=getattr(dialog.entity, 'participants_count', 0),
                                bot_accessible=True
                            )
                            
                            # Broadcast target olarak ekle
                            target = BroadcastTarget(
                                target_id=str(dialog.id),
                                target_type="group",
                                bot_username=bot_username,
                                is_accessible=True,
                                notes=f"Auto-discovered: {dialog.title}"
                            )
                            await database_manager.add_broadcast_target(target)
                    
                    logger.info(f"✅ {bot_username} için hedefler keşfedildi")
                    
                except Exception as e:
                    logger.warning(f"⚠️ {bot_username} hedef keşfi hatası: {e}")
            
        except Exception as e:
            logger.error(f"❌ Target discovery hatası: {e}")
    
    # ==================== BROADCAST METHODS ====================
    
    async def broadcast_leaderboard_update(self, data: Dict[str, Any]) -> str:
        """Leaderboard güncellemesi broadcast'i"""
        try:
            broadcast_id = str(uuid.uuid4())
            
            # Mesaj içeriğini oluştur
            message = self._format_leaderboard_message(data)
            
            # Broadcast'i kuyruğa ekle
            await self._queue_broadcast(
                broadcast_id=broadcast_id,
                message_type="leaderboard_update",
                message_content=message,
                target_types=["group"],  # Sadece gruplara
                priority="normal"
            )
            
            logger.info(f"📊 Leaderboard broadcast kuyruğa eklendi: {broadcast_id}")
            return broadcast_id
            
        except Exception as e:
            logger.error(f"❌ Leaderboard broadcast hatası: {e}")
            return ""
    
    async def broadcast_quest_completed(self, data: Dict[str, Any]) -> str:
        """Quest tamamlama broadcast'i"""
        try:
            broadcast_id = str(uuid.uuid4())
            
            # Mesaj içeriğini oluştur
            message = self._format_quest_message(data)
            
            # Kullanıcının tercihine göre hedef belirle
            user_id = data.get("user_id")
            target_types = await self._get_user_preferred_channels(user_id)
            
            await self._queue_broadcast(
                broadcast_id=broadcast_id,
                message_type="quest_completed",
                message_content=message,
                target_types=target_types,
                target_user_id=user_id,
                priority="high"
            )
            
            logger.info(f"🎯 Quest broadcast kuyruğa eklendi: {broadcast_id}")
            return broadcast_id
            
        except Exception as e:
            logger.error(f"❌ Quest broadcast hatası: {e}")
            return ""
    
    async def broadcast_level_up(self, data: Dict[str, Any]) -> str:
        """Level up broadcast'i"""
        try:
            broadcast_id = str(uuid.uuid4())
            
            message = self._format_level_up_message(data)
            
            # Level up önemli bir event, hem grup hem DM
            await self._queue_broadcast(
                broadcast_id=broadcast_id,
                message_type="level_up",
                message_content=message,
                target_types=["group", "user"],
                target_user_id=data.get("user_id"),
                priority="high"
            )
            
            logger.info(f"⬆️ Level up broadcast kuyruğa eklendi: {broadcast_id}")
            return broadcast_id
            
        except Exception as e:
            logger.error(f"❌ Level up broadcast hatası: {e}")
            return ""
    
    async def broadcast_social_event(self, data: Dict[str, Any]) -> str:
        """Sosyal etkinlik broadcast'i"""
        try:
            broadcast_id = str(uuid.uuid4())
            
            message = self._format_social_event_message(data)
            
            # Sosyal etkinlikler gruplara daha uygun
            await self._queue_broadcast(
                broadcast_id=broadcast_id,
                message_type="social_event",
                message_content=message,
                target_types=["group"],
                priority="normal"
            )
            
            logger.info(f"🎉 Social event broadcast kuyruğa eklendi: {broadcast_id}")
            return broadcast_id
            
        except Exception as e:
            logger.error(f"❌ Social event broadcast hatası: {e}")
            return ""
    
    async def broadcast_custom_message(self, message: str, target_types: List[str] = None,
                                     target_segments: List[str] = None, priority: str = "normal") -> str:
        """Özel mesaj broadcast'i"""
        try:
            broadcast_id = str(uuid.uuid4())
            
            await self._queue_broadcast(
                broadcast_id=broadcast_id,
                message_type="custom",
                message_content=message,
                target_types=target_types or ["group"],
                target_segments=target_segments,
                priority=priority
            )
            
            logger.info(f"📝 Custom broadcast kuyruğa eklendi: {broadcast_id}")
            return broadcast_id
            
        except Exception as e:
            logger.error(f"❌ Custom broadcast hatası: {e}")
            return ""
    
    # ==================== QUEUE MANAGEMENT ====================
    
    async def _queue_broadcast(self, broadcast_id: str, message_type: str, message_content: str,
                             target_types: List[str], target_user_id: str = None,
                             target_segments: List[str] = None, priority: str = "normal") -> None:
        """Broadcast'i kuyruğa ekle"""
        try:
            broadcast_item = {
                "broadcast_id": broadcast_id,
                "message_type": message_type,
                "message_content": message_content,
                "target_types": target_types,
                "target_user_id": target_user_id,
                "target_segments": target_segments or [],
                "priority": priority,
                "created_at": datetime.now(),
                "retry_count": 0
            }
            
            # Priority'ye göre sırala
            if priority == "high":
                self.broadcast_queue.insert(0, broadcast_item)
            else:
                self.broadcast_queue.append(broadcast_item)
            
        except Exception as e:
            logger.error(f"❌ Broadcast queue hatası: {e}")
    
    async def _process_broadcast_queue(self) -> None:
        """Broadcast kuyruğunu işle"""
        while True:
            try:
                if not self.processing_queue and self.broadcast_queue:
                    self.processing_queue = True
                    
                    # Kuyruktaki ilk item'ı al
                    broadcast_item = self.broadcast_queue.pop(0)
                    
                    # Broadcast'i gönder
                    await self._send_broadcast(broadcast_item)
                    
                    self.processing_queue = False
                
                # Kısa bekleme
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Broadcast queue processing hatası: {e}")
                self.processing_queue = False
                await asyncio.sleep(5)
    
    async def _send_broadcast(self, broadcast_item: Dict[str, Any]) -> None:
        """Broadcast'i gönder"""
        try:
            broadcast_id = broadcast_item["broadcast_id"]
            message_content = broadcast_item["message_content"]
            target_types = broadcast_item["target_types"]
            
            # Hedefleri al
            targets = []
            for target_type in target_types:
                type_targets = await database_manager.get_broadcast_targets(
                    target_type=target_type,
                    accessible_only=True
                )
                targets.extend(type_targets)
            
            # Segment filtreleme
            if broadcast_item.get("target_segments"):
                targets = await self._filter_targets_by_segments(targets, broadcast_item["target_segments"])
            
            # Her hedefe gönder
            for target in targets:
                try:
                    await self._send_to_target(broadcast_id, target, message_content, broadcast_item["message_type"])
                    
                    # Rate limiting
                    delay = self.rate_limits[target.target_type]["delay_between"]
                    await asyncio.sleep(delay)
                    
                except Exception as e:
                    logger.error(f"❌ Target'a gönderim hatası ({target.target_id}): {e}")
                    
                    # Hata durumunu kaydet
                    await database_manager.log_broadcast_attempt(
                        broadcast_id=broadcast_id,
                        target_id=target.target_id,
                        target_type=target.target_type,
                        bot_username=target.bot_username,
                        message_type=broadcast_item["message_type"],
                        message_content=message_content,
                        status=BroadcastStatus.FAILED,
                        error_message=str(e)
                    )
            
            logger.info(f"✅ Broadcast tamamlandı: {broadcast_id} ({len(targets)} hedef)")
            
        except Exception as e:
            logger.error(f"❌ Broadcast gönderim hatası: {e}")
            
            # Retry logic
            if broadcast_item["retry_count"] < 3:
                broadcast_item["retry_count"] += 1
                self.broadcast_queue.append(broadcast_item)
                logger.warning(f"🔄 Broadcast tekrar denenecek: {broadcast_item['broadcast_id']}")
    
    async def _send_to_target(self, broadcast_id: str, target: BroadcastTarget,
                            message: str, message_type: str) -> None:
        """Belirli bir hedefe mesaj gönder"""
        try:
            client = self.clients.get(target.bot_username)
            if not client:
                raise Exception(f"Bot client bulunamadı: {target.bot_username}")
            
            # Mesajı gönder
            if target.target_type == "group":
                await client.send_message(int(target.target_id), message)
            elif target.target_type == "user":
                await client.send_message(int(target.target_id), message)
            
            # Başarılı gönderimi kaydet
            await database_manager.log_broadcast_attempt(
                broadcast_id=broadcast_id,
                target_id=target.target_id,
                target_type=target.target_type,
                bot_username=target.bot_username,
                message_type=message_type,
                message_content=message,
                status=BroadcastStatus.SENT
            )
            
            # User interaction kaydet (eğer kullanıcıya gönderildiyse)
            if target.target_type == "user":
                await database_manager.log_user_interaction(
                    user_id=target.target_id,
                    interaction_type=UserInteractionType.DM_ACTIVITY,
                    metadata={"broadcast_type": message_type, "broadcast_id": broadcast_id}
                )
            
        except (FloodWaitError, ChatWriteForbiddenError, UserPrivacyRestrictedError) as e:
            # Bu hedefi geçici olarak devre dışı bırak
            target.is_accessible = False
            target.failure_count += 1
            await database_manager.add_broadcast_target(target)
            raise e
        
        except Exception as e:
            raise e
    
    # ==================== HELPER METHODS ====================
    
    async def _get_user_preferred_channels(self, user_id: str) -> List[str]:
        """Kullanıcının tercih ettiği iletişim kanallarını al"""
        try:
            # Default: sadece grup
            return ["group"]
            
        except Exception as e:
            logger.warning(f"⚠️ User preference alma hatası: {e}")
            return ["group"]
    
    async def _filter_targets_by_segments(self, targets: List[BroadcastTarget],
                                        segments: List[str]) -> List[BroadcastTarget]:
        """Hedefleri CRM segmentlerine göre filtrele"""
        try:
            # Bu özellik geliştirilecek - şimdilik tüm hedefleri döndür
            return targets
            
        except Exception as e:
            logger.error(f"❌ Segment filtreleme hatası: {e}")
            return targets
    
    # ==================== MESSAGE FORMATTERS ====================
    
    def _format_leaderboard_message(self, data: Dict[str, Any]) -> str:
        """Leaderboard mesajını formatla"""
        try:
            weekly_top = data.get("weekly_top_3", [])
            
            message = "🏆 **LEADERBOARD GÜNCELLENDİ!** 🏆\n\n"
            
            if weekly_top:
                message += "📅 **Haftalık Top 3:**\n"
                for i, user in enumerate(weekly_top[:3], 1):
                    message += f"{i}. {user.get('username', 'Anonim')} - {user.get('total_xp', 0)} XP\n"
            
            message += "\n🎯 Sen de sıralamaya katıl! Quest'leri tamamla ve XP kazan!"
            
            return message
            
        except Exception as e:
            logger.error(f"❌ Leaderboard mesaj formatı hatası: {e}")
            return "🏆 Leaderboard güncellendi! Detaylar için bota yazın."
    
    def _format_quest_message(self, data: Dict[str, Any]) -> str:
        """Quest mesajını formatla"""
        try:
            quest_title = data.get("quest_title", "Bilinmeyen Quest")
            user_id = data.get("user_id", "")
            xp_earned = data.get("xp_earned", 0)
            
            message = f"🎯 **QUEST TAMAMLANDI!** 🎯\n\n"
            message += f"👤 Kullanıcı: {user_id}\n"
            message += f"📋 Quest: {quest_title}\n"
            message += f"⭐ Kazanılan XP: {xp_earned}\n\n"
            message += "🎉 Tebrikler! Yeni quest'ler için bota yazın!"
            
            return message
            
        except Exception as e:
            logger.error(f"❌ Quest mesaj formatı hatası: {e}")
            return "🎯 Bir quest tamamlandı! Detaylar için bota yazın."
    
    def _format_level_up_message(self, data: Dict[str, Any]) -> str:
        """Level up mesajını formatla"""
        try:
            user_id = data.get("user_id", "")
            new_level = data.get("new_level", 1)
            
            message = f"🚀 **LEVEL UP!** 🚀\n\n"
            message += f"👤 {user_id}\n"
            message += f"🆙 Yeni Level: {new_level}\n\n"
            message += "🎊 Harika! Yeni özellikler açıldı!"
            
            return message
            
        except Exception as e:
            logger.error(f"❌ Level up mesaj formatı hatası: {e}")
            return "🚀 Birisi level atladı! Tebrikler!"
    
    def _format_social_event_message(self, data: Dict[str, Any]) -> str:
        """Sosyal etkinlik mesajını formatla"""
        try:
            event_title = data.get("title", "Yeni Etkinlik")
            event_type = data.get("event_type", "event")
            host_character = data.get("host_character", "GavatCore")
            
            message = f"🎉 **YENİ ETKİNLİK!** 🎉\n\n"
            message += f"📅 {event_title}\n"
            message += f"🎭 Host: {host_character}\n"
            message += f"🎪 Tür: {event_type}\n\n"
            message += "🎯 Katılmak için bota yazın!"
            
            return message
            
        except Exception as e:
            logger.error(f"❌ Social event mesaj formatı hatası: {e}")
            return "🎉 Yeni bir etkinlik başladı! Katılmak için bota yazın."
    
    # ==================== ANALYTICS & REPORTING ====================
    
    async def get_broadcast_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Broadcast analitiklerini al"""
        try:
            stats = await database_manager.get_broadcast_stats(days)
            
            # Ek metrikler ekle
            targets = await database_manager.get_broadcast_targets()
            
            analytics = {
                **stats,
                "total_targets": len(targets),
                "active_targets": len([t for t in targets if t.is_accessible]),
                "failed_targets": len([t for t in targets if not t.is_accessible]),
                "queue_size": len(self.broadcast_queue)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Broadcast analytics hatası: {e}")
            return {}
    
    async def optimize_broadcast_schedule(self) -> Dict[str, Any]:
        """Broadcast zamanlamasını optimize et"""
        try:
            # AI CRM analyzer ile optimizasyon önerileri al
            from .ai_crm_analyzer import ai_crm_analyzer
            
            if ai_crm_analyzer:
                optimization = await ai_crm_analyzer.analyze_broadcast_optimization()
                return optimization
            
            return {"error": "AI CRM Analyzer mevcut değil"}
            
        except Exception as e:
            logger.error(f"❌ Broadcast optimization hatası: {e}")
            return {"error": str(e)}

# Global instance
telegram_broadcaster = TelegramBroadcaster() 