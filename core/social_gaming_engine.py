from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
GavatCore V2 - Social Gaming Engine
Gerçek zamanlı topluluk etkileşimi, grup görevleri ve sosyal oyunlar
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import structlog
from pathlib import Path

from .mcp_api_system import mcp_api, Quest, QuestType, RewardType

logger = structlog.get_logger("gavatcore.social_gaming")

class EventType(Enum):
    """Etkinlik tipleri"""
    VOICE_PARTY = "voice_party"
    GROUP_CHALLENGE = "group_challenge"
    ROLEPLAY_EVENT = "roleplay_event"
    COMMUNITY_QUEST = "community_quest"
    LIVE_SHOW = "live_show"

class RoomType(Enum):
    """Oda tipleri"""
    VOICE_CHAT = "voice_chat"
    TEXT_CHAT = "text_chat"
    GAME_ROOM = "game_room"
    PRIVATE_ROOM = "private_room"

@dataclass
class SocialEvent:
    """Sosyal etkinlik modeli"""
    event_id: str
    title: str
    description: str
    event_type: EventType
    host_character_id: str
    max_participants: int = 10
    current_participants: List[str] = None
    start_time: datetime = None
    duration_minutes: int = 60
    rewards: List[Dict[str, Any]] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.current_participants is None:
            self.current_participants = []
        if self.rewards is None:
            self.rewards = []
        if self.start_time is None:
            self.start_time = datetime.now()

@dataclass
class SocialRoom:
    """Sosyal oda modeli"""
    room_id: str
    name: str
    room_type: RoomType
    host_user_id: str
    participants: List[str] = None
    max_capacity: int = 20
    is_private: bool = False
    password: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.participants is None:
            self.participants = []
        if self.created_at is None:
            self.created_at = datetime.now()

class SocialGamingEngine:
    """Sosyal Oyun Motoru"""
    
    def __init__(self, data_dir: str = "data/social_gaming"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Core data
        self.active_events: Dict[str, SocialEvent] = {}
        self.active_rooms: Dict[str, SocialRoom] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> set of room_ids
        
        # Leaderboards
        self.weekly_leaderboard: List[Dict[str, Any]] = []
        self.monthly_leaderboard: List[Dict[str, Any]] = []
        
        # Event handlers
        self.event_handlers: Dict[str, List] = {}
        
        logger.info("🎮 Social Gaming Engine başlatıldı")
    
    async def initialize(self) -> None:
        """Sistemi başlat"""
        try:
            await self._load_data()
            await self._setup_default_events()
            await self._start_background_tasks()
            
            logger.info("✅ Social Gaming Engine hazır")
            
        except Exception as e:
            logger.error(f"❌ Social Gaming başlatma hatası: {e}")
            raise
    
    # ==================== EVENT MANAGEMENT ====================
    
    async def create_social_event(self, event: SocialEvent) -> bool:
        """Sosyal etkinlik oluştur"""
        try:
            self.active_events[event.event_id] = event
            await self._save_events()
            
            # Tüm kullanıcılara bildir
            await self._broadcast_event("event_created", {
                "event_id": event.event_id,
                "title": event.title,
                "event_type": event.event_type.value,
                "host_character": event.host_character_id,
                "start_time": event.start_time.isoformat(),
                "max_participants": event.max_participants
            })
            
            # Event handler'ları tetikle
            await self.emit("event_created", {
                "event_id": event.event_id,
                "title": event.title,
                "event_type": event.event_type.value,
                "host_character": event.host_character_id
            })
            
            logger.info(f"✅ Sosyal etkinlik oluşturuldu: {event.title}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Etkinlik oluşturma hatası: {e}")
            return False
    
    async def join_event(self, event_id: str, user_id: str) -> Dict[str, Any]:
        """Etkinliğe katıl"""
        try:
            event = self.active_events.get(event_id)
            if not event:
                return {"success": False, "error": "Etkinlik bulunamadı"}
            
            if not event.is_active:
                return {"success": False, "error": "Etkinlik aktif değil"}
            
            if user_id in event.current_participants:
                return {"success": False, "error": "Zaten katılmışsın"}
            
            if len(event.current_participants) >= event.max_participants:
                return {"success": False, "error": "Etkinlik dolu"}
            
            # Katılımcı ekle
            event.current_participants.append(user_id)
            await self._save_events()
            
            # XP ver
            await mcp_api.add_xp(user_id, 30, f"event_join_{event_id}")
            
            await self._broadcast_event("user_joined_event", {
                "event_id": event_id,
                "user_id": user_id,
                "participant_count": len(event.current_participants)
            })
            
            logger.info(f"✅ Kullanıcı etkinliğe katıldı: {user_id} -> {event.title}")
            
            return {
                "success": True,
                "event": asdict(event),
                "participant_count": len(event.current_participants)
            }
            
        except Exception as e:
            logger.error(f"❌ Etkinliğe katılma hatası: {e}")
            return {"success": False, "error": str(e)}
    
    async def complete_event(self, event_id: str) -> Dict[str, Any]:
        """Etkinliği tamamla ve ödülleri dağıt"""
        try:
            event = self.active_events.get(event_id)
            if not event:
                return {"success": False, "error": "Etkinlik bulunamadı"}
            
            # Ödülleri dağıt
            rewards_distributed = []
            for user_id in event.current_participants:
                for reward in event.rewards:
                    if reward.get("type") == "xp":
                        await mcp_api.add_xp(user_id, reward.get("amount", 50), f"event_complete_{event_id}")
                    elif reward.get("type") == "token":
                        await mcp_api.add_tokens(user_id, reward.get("amount", 20), f"event_complete_{event_id}")
                    elif reward.get("type") == "badge":
                        await mcp_api.add_badge(user_id, reward.get("badge_id"), reward.get("badge_name"))
                
                rewards_distributed.append({
                    "user_id": user_id,
                    "rewards": event.rewards
                })
            
            # Etkinliği kapat
            event.is_active = False
            await self._save_events()
            
            await self._broadcast_event("event_completed", {
                "event_id": event_id,
                "title": event.title,
                "participants": event.current_participants,
                "rewards_distributed": len(rewards_distributed)
            })
            
            logger.info(f"✅ Etkinlik tamamlandı: {event.title}")
            
            return {
                "success": True,
                "participants": len(event.current_participants),
                "rewards_distributed": rewards_distributed
            }
            
        except Exception as e:
            logger.error(f"❌ Etkinlik tamamlama hatası: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== ROOM MANAGEMENT ====================
    
    async def create_room(self, room: SocialRoom) -> str:
        """Sosyal oda oluştur"""
        try:
            self.active_rooms[room.room_id] = room
            await self._save_rooms()
            
            # Host'u odaya ekle
            if room.host_user_id not in self.user_connections:
                self.user_connections[room.host_user_id] = set()
            self.user_connections[room.host_user_id].add(room.room_id)
            
            await self._broadcast_event("room_created", {
                "room_id": room.room_id,
                "name": room.name,
                "room_type": room.room_type.value,
                "host": room.host_user_id,
                "max_capacity": room.max_capacity,
                "is_private": room.is_private
            })
            
            logger.info(f"✅ Oda oluşturuldu: {room.name}")
            return room.room_id
            
        except Exception as e:
            logger.error(f"❌ Oda oluşturma hatası: {e}")
            raise
    
    async def join_room(self, room_id: str, user_id: str, password: str = None) -> Dict[str, Any]:
        """Odaya katıl"""
        try:
            room = self.active_rooms.get(room_id)
            if not room:
                return {"success": False, "error": "Oda bulunamadı"}
            
            if user_id in room.participants:
                return {"success": False, "error": "Zaten odasın"}
            
            if len(room.participants) >= room.max_capacity:
                return {"success": False, "error": "Oda dolu"}
            
            if room.is_private and room.password != password:
                return {"success": False, "error": "Yanlış şifre"}
            
            # Kullanıcıyı odaya ekle
            room.participants.append(user_id)
            
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(room_id)
            
            await self._save_rooms()
            
            # XP ver
            await mcp_api.add_xp(user_id, 10, f"room_join_{room_id}")
            
            await self._broadcast_to_room(room_id, "user_joined_room", {
                "room_id": room_id,
                "user_id": user_id,
                "participant_count": len(room.participants)
            })
            
            logger.info(f"✅ Kullanıcı odaya katıldı: {user_id} -> {room.name}")
            
            return {
                "success": True,
                "room": asdict(room),
                "participant_count": len(room.participants)
            }
            
        except Exception as e:
            logger.error(f"❌ Odaya katılma hatası: {e}")
            return {"success": False, "error": str(e)}
    
    async def leave_room(self, room_id: str, user_id: str) -> bool:
        """Odadan ayrıl"""
        try:
            room = self.active_rooms.get(room_id)
            if not room or user_id not in room.participants:
                return False
            
            room.participants.remove(user_id)
            
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(room_id)
            
            # Oda boşsa sil
            if not room.participants:
                del self.active_rooms[room_id]
            
            await self._save_rooms()
            
            await self._broadcast_to_room(room_id, "user_left_room", {
                "room_id": room_id,
                "user_id": user_id,
                "participant_count": len(room.participants)
            })
            
            logger.info(f"✅ Kullanıcı odadan ayrıldı: {user_id} -> {room.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Odadan ayrılma hatası: {e}")
            return False
    
    # ==================== GROUP CHALLENGES ====================
    
    async def create_group_challenge(self, title: str, description: str, character_id: str, duration_hours: int = 24) -> str:
        """Grup challenge'ı oluştur"""
        try:
            challenge_id = f"challenge_{int(time.time())}"
            
            # Quest olarak oluştur
            quest = Quest(
                id=challenge_id,
                title=title,
                description=description,
                quest_type=QuestType.COMMUNITY,
                character_id=character_id,
                duration_hours=duration_hours,
                max_participants=50,  # Grup challenge
                requirements={"min_participants": 5},
                rewards=[
                    {"type": "xp", "amount": 100},
                    {"type": "token", "amount": 50},
                    {"type": "badge", "badge_id": f"challenge_{challenge_id}", "badge_name": f"Challenge Kahramanı"}
                ]
            )
            
            await mcp_api.create_quest(quest)
            
            # Sosyal etkinlik olarak da ekle
            event = SocialEvent(
                event_id=f"event_{challenge_id}",
                title=title,
                description=description,
                event_type=EventType.GROUP_CHALLENGE,
                host_character_id=character_id,
                max_participants=50,
                duration_minutes=duration_hours * 60,
                rewards=quest.rewards
            )
            
            await self.create_social_event(event)
            
            logger.info(f"✅ Grup challenge'ı oluşturuldu: {title}")
            return challenge_id
            
        except Exception as e:
            logger.error(f"❌ Grup challenge oluşturma hatası: {e}")
            raise
    
    # ==================== LEADERBOARDS ====================
    
    async def update_leaderboards(self) -> None:
        """Liderlik tablolarını güncelle"""
        try:
            # MCP API'den leaderboard al
            main_leaderboard = await mcp_api.get_leaderboard(50)
            
            # Haftalık ve aylık filtreleme (basit implementation)
            now = datetime.now()
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            
            # Bu implementation'da tüm kullanıcıları alıyoruz
            # Gerçek uygulamada tarih filtrelemesi yapılacak
            self.weekly_leaderboard = main_leaderboard[:20]
            self.monthly_leaderboard = main_leaderboard[:30]
            
            await self._broadcast_event("leaderboards_updated", {
                "weekly_top_3": self.weekly_leaderboard[:3],
                "monthly_top_3": self.monthly_leaderboard[:3]
            })
            
        except Exception as e:
            logger.error(f"❌ Leaderboard güncelleme hatası: {e}")
    
    async def get_leaderboard(self, board_type: str = "weekly", limit: int = 10) -> List[Dict[str, Any]]:
        """Liderlik tablosunu al"""
        if board_type == "weekly":
            return self.weekly_leaderboard[:limit]
        elif board_type == "monthly":
            return self.monthly_leaderboard[:limit]
        else:
            return await mcp_api.get_leaderboard(limit)
    
    # ==================== LIVE EVENTS ====================
    
    async def start_live_show(self, character_id: str, title: str, duration_minutes: int = 60) -> str:
        """Canlı show başlat"""
        try:
            show_id = f"live_{character_id}_{int(time.time())}"
            
            # Show room oluştur
            room = SocialRoom(
                room_id=f"room_{show_id}",
                name=f"🔴 {title}",
                room_type=RoomType.VOICE_CHAT,
                host_user_id=character_id,
                max_capacity=100
            )
            
            await self.create_room(room)
            
            # Show event oluştur
            event = SocialEvent(
                event_id=show_id,
                title=title,
                description=f"Canlı show: {title}",
                event_type=EventType.LIVE_SHOW,
                host_character_id=character_id,
                max_participants=100,
                duration_minutes=duration_minutes,
                rewards=[
                    {"type": "xp", "amount": 75},
                    {"type": "token", "amount": 30}
                ]
            )
            
            await self.create_social_event(event)
            
            logger.info(f"✅ Canlı show başlatıldı: {title}")
            return show_id
            
        except Exception as e:
            logger.error(f"❌ Canlı show başlatma hatası: {e}")
            raise
    
    # ==================== PRIVATE METHODS ====================
    
    async def _setup_default_events(self) -> None:
        """Varsayılan etkinlikleri kur"""
        try:
            # Günlük voice party
            daily_party = SocialEvent(
                event_id="daily_voice_party",
                title="Günlük Sesli Parti 🎉",
                description="Her gün saat 20:00'da sesli parti!",
                event_type=EventType.VOICE_PARTY,
                host_character_id="geisha",
                max_participants=20,
                duration_minutes=120,
                rewards=[
                    {"type": "xp", "amount": 100},
                    {"type": "token", "amount": 40}
                ]
            )
            
            await self.create_social_event(daily_party)
            
        except Exception as e:
            logger.error(f"❌ Varsayılan etkinlik kurma hatası: {e}")
    
    async def _start_background_tasks(self) -> None:
        """Arka plan görevlerini başlat"""
        try:
            # Leaderboard güncelleme görevi
            asyncio.create_task(self._leaderboard_update_loop())
            
            # Event cleanup görevi
            asyncio.create_task(self._event_cleanup_loop())
            
        except Exception as e:
            logger.error(f"❌ Arka plan görevleri başlatma hatası: {e}")
    
    async def _leaderboard_update_loop(self) -> None:
        """Leaderboard güncelleme döngüsü"""
        while True:
            try:
                await self.update_leaderboards()
                await asyncio.sleep(300)  # 5 dakikada bir güncelle
            except Exception as e:
                logger.error(f"❌ Leaderboard güncelleme döngüsü hatası: {e}")
                await asyncio.sleep(60)
    
    async def _event_cleanup_loop(self) -> None:
        """Süresi dolmuş etkinlikleri temizle"""
        while True:
            try:
                now = datetime.now()
                expired_events = []
                
                for event_id, event in self.active_events.items():
                    if event.is_active:
                        end_time = event.start_time + timedelta(minutes=event.duration_minutes)
                        if now > end_time:
                            expired_events.append(event_id)
                
                for event_id in expired_events:
                    await self.complete_event(event_id)
                
                await asyncio.sleep(60)  # 1 dakikada bir kontrol et
                
            except Exception as e:
                logger.error(f"❌ Event cleanup döngüsü hatası: {e}")
                await asyncio.sleep(60)
    
    async def _broadcast_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """Tüm kullanıcılara event yayınla"""
        # Bu method Telegram bot entegrasyonu ile geliştirilecek
        logger.info(f"📢 Broadcast: {event_name} - {data}")
        
        # Telegram broadcaster entegrasyonu
        try:
            from .telegram_broadcaster import telegram_broadcaster
            
            if event_name == "leaderboards_updated":
                await telegram_broadcaster.broadcast_leaderboard_update(data)
            elif event_name == "event_created":
                await telegram_broadcaster.broadcast_social_event(data)
                
        except Exception as e:
            logger.error(f"❌ Telegram broadcast hatası: {e}")
    
    async def _broadcast_to_room(self, room_id: str, event_name: str, data: Dict[str, Any]) -> None:
        """Odadaki kullanıcılara event yayınla"""
        room = self.active_rooms.get(room_id)
        if room:
            logger.info(f"📢 Room broadcast ({room.name}): {event_name} - {data}")
    
    async def _load_data(self) -> None:
        """Verileri yükle"""
        # Basit implementation - geliştirilecek
        pass
    
    async def _save_events(self) -> None:
        """Etkinlikleri kaydet"""
        # Basit implementation - geliştirilecek
        pass
    
    async def _save_rooms(self) -> None:
        """Odaları kaydet"""
        # Basit implementation - geliştirilecek
        pass

    def on(self, event_name: str, handler) -> None:
        """Event handler ekle"""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)
    
    async def emit(self, event_name: str, data: Dict[str, Any]) -> None:
        """Event tetikle"""
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                try:
                    await handler(data)
                except Exception as e:
                    logger.error(f"❌ Event handler hatası ({event_name}): {e}")

# Global instance
social_gaming = SocialGamingEngine() 