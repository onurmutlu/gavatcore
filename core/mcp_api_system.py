from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
GavatCore V2 - MCP Tabanlı Modüler API Sistemi
AI Voice, Social Gaming, Quest System için merkezi API
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import structlog
from pathlib import Path

logger = structlog.get_logger("gavatcore.mcp_api")

class CharacterType(Enum):
    """Karakter tipleri"""
    SEDUCTIVE = "seductive"  # Geisha gibi
    LEADER = "leader"        # BabaGavat gibi
    PLAYFUL = "playful"      # Lara gibi
    MENTOR = "mentor"        # Öğretmen tipi
    COMPANION = "companion"  # Arkadaş tipi

class QuestType(Enum):
    """Görev tipleri"""
    DAILY = "daily"
    WEEKLY = "weekly"
    SOCIAL = "social"
    VOICE = "voice"
    ROLEPLAY = "roleplay"
    COMMUNITY = "community"

class RewardType(Enum):
    """Ödül tipleri"""
    XP = "xp"
    TOKEN = "token"
    BADGE = "badge"
    NFT = "nft"
    VIP_ACCESS = "vip_access"

@dataclass
class Character:
    """AI Karakter modeli"""
    id: str
    name: str
    display_name: str
    character_type: CharacterType
    voice_id: Optional[str] = None
    personality_prompt: str = ""
    voice_style: str = "neutral"
    level: int = 1
    xp: int = 0
    special_abilities: List[str] = None
    memory_context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.special_abilities is None:
            self.special_abilities = []
        if self.memory_context is None:
            self.memory_context = {}

@dataclass
class Quest:
    """Görev modeli"""
    id: str
    title: str
    description: str
    quest_type: QuestType
    character_id: Optional[str] = None
    requirements: Dict[str, Any] = None
    rewards: List[Dict[str, Any]] = None
    duration_hours: int = 24
    max_participants: int = 1
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.requirements is None:
            self.requirements = {}
        if self.rewards is None:
            self.rewards = []
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class UserProgress:
    """Kullanıcı ilerleme modeli"""
    user_id: str
    username: str
    level: int = 1
    total_xp: int = 0
    tokens: int = 0
    badges: List[str] = None
    completed_quests: List[str] = None
    active_quests: List[str] = None
    character_relationships: Dict[str, int] = None  # character_id -> relationship_level
    last_activity: datetime = None
    
    def __post_init__(self):
        if self.badges is None:
            self.badges = []
        if self.completed_quests is None:
            self.completed_quests = []
        if self.active_quests is None:
            self.active_quests = []
        if self.character_relationships is None:
            self.character_relationships = {}
        if self.last_activity is None:
            self.last_activity = datetime.now()

class MCPAPISystem:
    """MCP Tabanlı Modüler API Sistemi"""
    
    def __init__(self, data_dir: str = "data/mcp_system"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Core data storage
        self.users: Dict[str, UserProgress] = {}
        self.characters: Dict[str, Character] = {}
        self.quests: Dict[str, Quest] = {}
        self.active_user_quests: Dict[str, List[str]] = {}  # user_id -> quest_ids
        
        # System stats
        self.system_stats = {
            "total_users": 0,
            "total_xp_distributed": 0,
            "total_tokens_distributed": 0,
            "completed_quests": 0,
            "active_quests": 0
        }
        
        # Event handlers
        self.event_handlers: Dict[str, List] = {}
        
        logger.info("🎮 MCP API Sistemi başlatıldı")
    
    async def initialize(self) -> None:
        """Sistemi başlat"""
        try:
            await self._load_data()
            await self._setup_default_characters()
            await self._setup_default_quests()
            await self._update_leaderboard()
            
            logger.info("✅ MCP API Sistemi hazır")
            
        except Exception as e:
            logger.error(f"❌ MCP API başlatma hatası: {e}")
            raise
    
    # ==================== CHARACTER MANAGEMENT ====================
    
    async def register_character(self, character: Character) -> bool:
        """Yeni karakter kaydet"""
        try:
            self.characters[character.id] = character
            await self._save_characters()
            
            await self.emit("character_registered", {
                "character_id": character.id,
                "character_name": character.name,
                "character_type": character.character_type.value
            })
            
            logger.info(f"✅ Karakter kaydedildi: {character.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Karakter kaydetme hatası: {e}")
            return False
    
    async def get_character(self, character_id: str) -> Optional[Character]:
        """Karakter bilgilerini al"""
        return self.characters.get(character_id)
    
    async def update_character_memory(self, character_id: str, user_id: str, memory_data: Dict[str, Any]) -> bool:
        """Karakter hafızasını güncelle"""
        try:
            character = self.characters.get(character_id)
            if not character:
                return False
            
            if user_id not in character.memory_context:
                character.memory_context[user_id] = {}
            
            character.memory_context[user_id].update(memory_data)
            character.memory_context[user_id]["last_interaction"] = datetime.now().isoformat()
            
            await self._save_characters()
            return True
            
        except Exception as e:
            logger.error(f"❌ Karakter hafıza güncelleme hatası: {e}")
            return False
    
    # ==================== QUEST SYSTEM ====================
    
    async def create_quest(self, quest: Quest) -> bool:
        """Yeni görev oluştur"""
        try:
            self.quests[quest.id] = quest
            await self._save_quests()
            
            self.system_stats["active_quests"] += 1
            
            await self.emit("quest_created", {
                "quest_id": quest.id,
                "quest_title": quest.title,
                "quest_type": quest.quest_type.value,
                "character_id": quest.character_id
            })
            
            logger.info(f"✅ Görev oluşturuldu: {quest.title}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Görev oluşturma hatası: {e}")
            return False
    
    async def assign_quest_to_user(self, quest_id: str, user_id: str) -> bool:
        """Kullanıcıya görev ata"""
        try:
            quest = self.quests.get(quest_id)
            if not quest or not quest.is_active:
                return False
            
            user = await self._get_or_create_user(user_id)
            
            if quest_id in user.active_quests:
                return False  # Zaten aktif
            
            if quest_id in user.completed_quests:
                return False  # Zaten tamamlanmış
            
            user.active_quests.append(quest_id)
            await self._save_user_progress()
            
            await self.emit("quest_assigned", {
                "quest_id": quest_id,
                "user_id": user_id,
                "quest_title": quest.title
            })
            
            logger.info(f"✅ Görev atandı: {quest.title} -> {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Görev atama hatası: {e}")
            return False
    
    async def complete_quest(self, quest_id: str, user_id: str) -> Dict[str, Any]:
        """Görevi tamamla ve ödülleri ver"""
        try:
            quest = self.quests.get(quest_id)
            user = self.users.get(user_id)
            
            if not quest or not user or quest_id not in user.active_quests:
                return {"success": False, "error": "Invalid quest or user"}
            
            # Görevi tamamlanmış olarak işaretle
            user.active_quests.remove(quest_id)
            user.completed_quests.append(quest_id)
            
            # Ödülleri ver
            rewards_given = []
            for reward in quest.rewards:
                reward_result = await self._give_reward(user, reward)
                if reward_result:
                    rewards_given.append(reward)
            
            user.last_activity = datetime.now()
            await self._save_user_progress()
            
            self.system_stats["completed_quests"] += 1
            
            await self.emit("quest_completed", {
                "quest_id": quest_id,
                "user_id": user_id,
                "rewards": rewards_given,
                "new_level": user.level,
                "total_xp": user.total_xp
            })
            
            # Leaderboard güncelle
            await self._update_leaderboard()
            
            logger.info(f"✅ Görev tamamlandı: {quest.title} -> {user_id}")
            
            return {
                "success": True,
                "rewards": rewards_given,
                "new_level": user.level,
                "total_xp": user.total_xp,
                "tokens": user.tokens
            }
            
        except Exception as e:
            logger.error(f"❌ Görev tamamlama hatası: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== USER PROGRESS ====================
    
    async def get_user_progress(self, user_id: str) -> Optional[UserProgress]:
        """Kullanıcı ilerlemesini al"""
        return self.users.get(user_id)
    
    async def add_xp(self, user_id: str, xp_amount: int, source: str = "general") -> Dict[str, Any]:
        """Kullanıcıya XP ekle"""
        try:
            user = await self._get_or_create_user(user_id)
            old_level = user.level
            
            user.total_xp += xp_amount
            user.last_activity = datetime.now()
            
            # Level hesapla (her 1000 XP = 1 level)
            new_level = (user.total_xp // 1000) + 1
            level_up = new_level > old_level
            
            if level_up:
                user.level = new_level
                await self.emit("level_up", {
                    "user_id": user_id,
                    "old_level": old_level,
                    "new_level": new_level,
                    "total_xp": user.total_xp
                })
            
            self.system_stats["total_xp_distributed"] += xp_amount
            await self._save_user_progress()
            
            return {
                "success": True,
                "xp_added": xp_amount,
                "total_xp": user.total_xp,
                "level": user.level,
                "level_up": level_up,
                "source": source
            }
            
        except Exception as e:
            logger.error(f"❌ XP ekleme hatası: {e}")
            return {"success": False, "error": str(e)}
    
    async def add_tokens(self, user_id: str, token_amount: int, source: str = "general") -> bool:
        """Kullanıcıya token ekle"""
        try:
            user = await self._get_or_create_user(user_id)
            user.tokens += token_amount
            user.last_activity = datetime.now()
            
            self.system_stats["total_tokens_distributed"] += token_amount
            await self._save_user_progress()
            
            await self.emit("tokens_added", {
                "user_id": user_id,
                "tokens_added": token_amount,
                "total_tokens": user.tokens,
                "source": source
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Token ekleme hatası: {e}")
            return False
    
    async def add_badge(self, user_id: str, badge_id: str, badge_name: str) -> bool:
        """Kullanıcıya rozet ver"""
        try:
            user = await self._get_or_create_user(user_id)
            
            if badge_id not in user.badges:
                user.badges.append(badge_id)
                user.last_activity = datetime.now()
                await self._save_user_progress()
                
                await self.emit("badge_earned", {
                    "user_id": user_id,
                    "badge_id": badge_id,
                    "badge_name": badge_name,
                    "total_badges": len(user.badges)
                })
                
                return True
            
            return False  # Zaten var
            
        except Exception as e:
            logger.error(f"❌ Rozet verme hatası: {e}")
            return False
    
    # ==================== SOCIAL FEATURES ====================
    
    async def update_character_relationship(self, user_id: str, character_id: str, relationship_change: int) -> bool:
        """Karakter ilişkisini güncelle"""
        try:
            user = await self._get_or_create_user(user_id)
            
            if character_id not in user.character_relationships:
                user.character_relationships[character_id] = 0
            
            user.character_relationships[character_id] += relationship_change
            
            # 0-100 arası sınırla
            user.character_relationships[character_id] = max(0, min(100, user.character_relationships[character_id]))
            
            user.last_activity = datetime.now()
            await self._save_user_progress()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ İlişki güncelleme hatası: {e}")
            return False
    
    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Liderlik tablosunu al"""
        return self.leaderboard[:limit]
    
    async def get_active_quests_for_user(self, user_id: str) -> List[Quest]:
        """Kullanıcının aktif görevlerini al"""
        user = self.users.get(user_id)
        if not user:
            return []
        
        active_quests = []
        for quest_id in user.active_quests:
            quest = self.quests.get(quest_id)
            if quest and quest.is_active:
                active_quests.append(quest)
        
        return active_quests
    
    # ==================== VOICE INTERACTION ====================
    
    async def log_voice_interaction(self, user_id: str, character_id: str, duration_seconds: int, interaction_type: str = "voice_chat") -> bool:
        """Sesli etkileşimi kaydet"""
        try:
            # XP ver (her dakika için 10 XP)
            xp_earned = max(1, duration_seconds // 6)  # Her 6 saniye = 1 XP
            await self.add_xp(user_id, xp_earned, f"voice_interaction_{character_id}")
            
            # İlişki puanı artır
            relationship_boost = max(1, duration_seconds // 30)  # Her 30 saniye = 1 puan
            await self.update_character_relationship(user_id, character_id, relationship_boost)
            
            self.system_stats["voice_interactions"] += 1
            
            await self.emit("voice_interaction", {
                "user_id": user_id,
                "character_id": character_id,
                "duration_seconds": duration_seconds,
                "xp_earned": xp_earned,
                "interaction_type": interaction_type
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Sesli etkileşim kaydetme hatası: {e}")
            return False
    
    # ==================== EVENT SYSTEM ====================
    
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
    
    # ==================== PRIVATE METHODS ====================
    
    async def _get_or_create_user(self, user_id: str, username: str = None) -> UserProgress:
        """Kullanıcıyı al veya oluştur"""
        if user_id not in self.users:
            self.users[user_id] = UserProgress(
                user_id=user_id,
                username=username or f"user_{user_id}"
            )
            self.system_stats["total_users"] += 1
            await self._save_user_progress()
        
        return self.users[user_id]
    
    async def _give_reward(self, user: UserProgress, reward: Dict[str, Any]) -> bool:
        """Ödül ver"""
        try:
            reward_type = RewardType(reward.get("type"))
            amount = reward.get("amount", 1)
            
            if reward_type == RewardType.XP:
                await self.add_xp(user.user_id, amount, "quest_reward")
            elif reward_type == RewardType.TOKEN:
                await self.add_tokens(user.user_id, amount, "quest_reward")
            elif reward_type == RewardType.BADGE:
                await self.add_badge(user.user_id, reward.get("badge_id"), reward.get("badge_name"))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ödül verme hatası: {e}")
            return False
    
    async def _update_leaderboard(self) -> None:
        """Liderlik tablosunu güncelle"""
        try:
            # XP'ye göre sırala
            sorted_users = sorted(
                self.users.values(),
                key=lambda u: u.total_xp,
                reverse=True
            )
            
            self.leaderboard = []
            for i, user in enumerate(sorted_users[:50]):  # Top 50
                self.leaderboard.append({
                    "rank": i + 1,
                    "user_id": user.user_id,
                    "username": user.username,
                    "level": user.level,
                    "total_xp": user.total_xp,
                    "tokens": user.tokens,
                    "badges_count": len(user.badges),
                    "completed_quests": len(user.completed_quests)
                })
            
        except Exception as e:
            logger.error(f"❌ Leaderboard güncelleme hatası: {e}")
    
    async def _setup_default_characters(self) -> None:
        """Varsayılan karakterleri kur"""
        if not self.characters:
            # Geisha karakteri
            geisha = Character(
                id="geisha",
                name="Geisha",
                display_name="💋 Geisha",
                character_type=CharacterType.SEDUCTIVE,
                voice_id="geisha_voice",
                personality_prompt="Geisha, 23-25 yaşlarında, kıvırcık kızıl saçlı, erotik hikayeler anlatmayı seven, duygusal ama dominant, karşısındakini hem şefkatle hem tensel çağrışımlarla yönlendiren, karizmatik bir kadın karakter.",
                voice_style="seductive",
                special_abilities=["flirt_master", "story_teller", "emotional_support"]
            )
            
            # BabaGavat karakteri
            babagavat = Character(
                id="babagavat",
                name="BabaGavat",
                display_name="👑 Gavat Baba",
                character_type=CharacterType.LEADER,
                voice_id="babagavat_voice",
                personality_prompt="Gavat Baba, 35 yaşında, deneyimli bir pezevenk. Ortama hakim, karizmatik, zeki espriler yapan, güven veren ve işleri tatlı dille çözen bir lider figürüdür.",
                voice_style="authoritative",
                special_abilities=["leadership", "organization", "social_networking"]
            )
            
            await self.register_character(geisha)
            await self.register_character(babagavat)
    
    async def _setup_default_quests(self) -> None:
        """Varsayılan görevleri kur"""
        if not self.quests:
            # Günlük görevler
            daily_chat = Quest(
                id="daily_chat",
                title="Günlük Sohbet",
                description="Herhangi bir karakterle 5 dakika sohbet et",
                quest_type=QuestType.DAILY,
                requirements={"chat_duration_minutes": 5},
                rewards=[
                    {"type": "xp", "amount": 50},
                    {"type": "token", "amount": 10}
                ]
            )
            
            voice_interaction = Quest(
                id="voice_interaction",
                title="Sesli Tanışma",
                description="Bir karakterle sesli sohbet yap",
                quest_type=QuestType.VOICE,
                requirements={"voice_duration_seconds": 60},
                rewards=[
                    {"type": "xp", "amount": 100},
                    {"type": "token", "amount": 25},
                    {"type": "badge", "badge_id": "voice_pioneer", "badge_name": "Ses Öncüsü"}
                ]
            )
            
            await self.create_quest(daily_chat)
            await self.create_quest(voice_interaction)
    
    async def _load_data(self) -> None:
        """Verileri yükle"""
        try:
            # Characters
            characters_file = self.data_dir / "characters.json"
            if characters_file.exists():
                with open(characters_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for char_data in data:
                        char = Character(**char_data)
                        char.character_type = CharacterType(char.character_type)
                        self.characters[char.id] = char
            
            # Quests
            quests_file = self.data_dir / "quests.json"
            if quests_file.exists():
                with open(quests_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for quest_data in data:
                        quest_data['created_at'] = datetime.fromisoformat(quest_data['created_at'])
                        quest = Quest(**quest_data)
                        quest.quest_type = QuestType(quest.quest_type)
                        self.quests[quest.id] = quest
            
            # User Progress
            users_file = self.data_dir / "user_progress.json"
            if users_file.exists():
                with open(users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_data in data:
                        user_data['last_activity'] = datetime.fromisoformat(user_data['last_activity'])
                        user = UserProgress(**user_data)
                        self.users[user.user_id] = user
            
        except Exception as e:
            logger.error(f"❌ Veri yükleme hatası: {e}")
    
    async def _save_characters(self) -> None:
        """Karakterleri kaydet"""
        try:
            characters_file = self.data_dir / "characters.json"
            data = []
            for char in self.characters.values():
                char_dict = asdict(char)
                char_dict['character_type'] = char.character_type.value
                data.append(char_dict)
            
            with open(characters_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Karakter kaydetme hatası: {e}")
    
    async def _save_quests(self) -> None:
        """Görevleri kaydet"""
        try:
            quests_file = self.data_dir / "quests.json"
            data = []
            for quest in self.quests.values():
                quest_dict = asdict(quest)
                quest_dict['quest_type'] = quest.quest_type.value
                quest_dict['created_at'] = quest.created_at.isoformat()
                data.append(quest_dict)
            
            with open(quests_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Görev kaydetme hatası: {e}")
    
    async def _save_user_progress(self) -> None:
        """Kullanıcı ilerlemesini kaydet"""
        try:
            users_file = self.data_dir / "user_progress.json"
            data = []
            for user in self.users.values():
                user_dict = asdict(user)
                user_dict['last_activity'] = user.last_activity.isoformat()
                data.append(user_dict)
            
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Kullanıcı verisi kaydetme hatası: {e}")

# Global instance
mcp_api = MCPAPISystem() 