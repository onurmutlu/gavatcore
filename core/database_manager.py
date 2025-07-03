#!/usr/bin/env python3
"""
GavatCore V2 - Database Manager
Veritabanı temelli broadcast, kullanıcı analizi ve CRM data mining sistemi
"""

import asyncio
import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import structlog
from pathlib import Path
import aiosqlite

logger = structlog.get_logger("gavatcore.database")

class BroadcastStatus(Enum):
    """Broadcast durumları"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SCHEDULED = "scheduled"

class UserInteractionType(Enum):
    """Kullanıcı etkileşim tipleri"""
    MESSAGE = "message"
    VOICE_CHAT = "voice_chat"
    QUEST_COMPLETE = "quest_complete"
    EVENT_JOIN = "event_join"
    GROUP_ACTIVITY = "group_activity"
    DM_ACTIVITY = "dm_activity"

@dataclass
class BroadcastTarget:
    """Broadcast hedefi"""
    target_id: str  # grup_id veya user_id
    target_type: str  # "group" veya "user"
    bot_username: str  # hangi bot gönderecek
    is_accessible: bool = True
    last_success: Optional[datetime] = None
    failure_count: int = 0
    notes: str = ""

@dataclass
class UserAnalytics:
    """Kullanıcı analitik verisi"""
    user_id: str
    username: str
    first_seen: datetime
    last_activity: datetime
    total_messages: int = 0
    voice_minutes: int = 0
    quests_completed: int = 0
    events_joined: int = 0
    favorite_character: Optional[str] = None
    activity_score: float = 0.0
    engagement_level: str = "low"  # low, medium, high, vip
    preferred_time_slots: List[str] = None
    group_memberships: List[str] = None
    dm_responsive: bool = True

class DatabaseManager:
    """Veritabanı Yöneticisi"""
    
    def __init__(self, db_path: str = "gavatcore_v2.db"):
        self.db_path = db_path
        self.connection_pool = {}
        logger.info(f"🗄️ Database Manager başlatılıyor: {db_path}")
    
    async def initialize(self) -> None:
        """Veritabanını başlat ve tabloları oluştur"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await self._create_tables(db)
                await self._create_indexes(db)
                await db.commit()
            
            logger.info("✅ Database Manager hazır")
            
        except Exception as e:
            logger.error(f"❌ Database başlatma hatası: {e}")
            raise
    
    def _get_connection(self):
        """Database bağlantısı al"""
        return aiosqlite.connect(self.db_path)
    
    async def _create_tables(self, db: aiosqlite.Connection) -> None:
        """Tabloları oluştur"""
        
        # Broadcast Targets tablosu
        await db.execute("""
            CREATE TABLE IF NOT EXISTS broadcast_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id TEXT NOT NULL,
                target_type TEXT NOT NULL,
                bot_username TEXT NOT NULL,
                is_accessible BOOLEAN DEFAULT TRUE,
                last_success TIMESTAMP,
                failure_count INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(target_id, target_type, bot_username)
            )
        """)
        
        # Broadcast History tablosu
        await db.execute("""
            CREATE TABLE IF NOT EXISTS broadcast_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                broadcast_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                target_type TEXT NOT NULL,
                bot_username TEXT NOT NULL,
                message_type TEXT NOT NULL,
                message_content TEXT NOT NULL,
                status TEXT NOT NULL,
                sent_at TIMESTAMP,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User Analytics tablosu
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                username TEXT,
                first_seen TIMESTAMP NOT NULL,
                last_activity TIMESTAMP NOT NULL,
                total_messages INTEGER DEFAULT 0,
                voice_minutes INTEGER DEFAULT 0,
                quests_completed INTEGER DEFAULT 0,
                events_joined INTEGER DEFAULT 0,
                favorite_character TEXT,
                activity_score REAL DEFAULT 0.0,
                engagement_level TEXT DEFAULT 'low',
                preferred_time_slots TEXT, -- JSON array
                group_memberships TEXT, -- JSON array
                dm_responsive BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User Interactions tablosu (detaylı etkileşim geçmişi)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                character_id TEXT,
                group_id TEXT,
                duration_seconds INTEGER,
                metadata TEXT, -- JSON data
                sentiment_score REAL,
                engagement_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Group Analytics tablosu
        await db.execute("""
            CREATE TABLE IF NOT EXISTS group_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT UNIQUE NOT NULL,
                group_name TEXT,
                member_count INTEGER DEFAULT 0,
                active_members INTEGER DEFAULT 0,
                message_count INTEGER DEFAULT 0,
                bot_accessible BOOLEAN DEFAULT TRUE,
                admin_permissions TEXT, -- JSON array
                activity_level TEXT DEFAULT 'low',
                peak_hours TEXT, -- JSON array
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # AI Analysis Results tablosu
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ai_analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                analysis_data TEXT NOT NULL, -- JSON
                insights TEXT NOT NULL, -- JSON
                recommendations TEXT NOT NULL, -- JSON
                confidence_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # CRM Segments tablosu
        await db.execute("""
            CREATE TABLE IF NOT EXISTS crm_segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                segment_name TEXT UNIQUE NOT NULL,
                criteria TEXT NOT NULL, -- JSON
                user_count INTEGER DEFAULT 0,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    async def _create_indexes(self, db: aiosqlite.Connection) -> None:
        """İndeksleri oluştur"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_broadcast_targets_type ON broadcast_targets(target_type)",
            "CREATE INDEX IF NOT EXISTS idx_broadcast_history_status ON broadcast_history(status)",
            "CREATE INDEX IF NOT EXISTS idx_user_analytics_activity ON user_analytics(last_activity)",
            "CREATE INDEX IF NOT EXISTS idx_user_analytics_engagement ON user_analytics(engagement_level)",
            "CREATE INDEX IF NOT EXISTS idx_user_interactions_type ON user_interactions(interaction_type)",
            "CREATE INDEX IF NOT EXISTS idx_user_interactions_user ON user_interactions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_group_analytics_activity ON group_analytics(activity_level)",
            "CREATE INDEX IF NOT EXISTS idx_ai_analysis_type ON ai_analysis_results(analysis_type)"
        ]
        
        for index_sql in indexes:
            await db.execute(index_sql)
    
    # ==================== BROADCAST MANAGEMENT ====================
    
    async def add_broadcast_target(self, target: BroadcastTarget) -> bool:
        """Broadcast hedefi ekle"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO broadcast_targets 
                    (target_id, target_type, bot_username, is_accessible, last_success, failure_count, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    target.target_id, target.target_type, target.bot_username,
                    target.is_accessible, target.last_success, target.failure_count, target.notes
                ))
                await db.commit()
            
            logger.info(f"✅ Broadcast hedefi eklendi: {target.target_type}:{target.target_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Broadcast hedefi ekleme hatası: {e}")
            return False
    
    async def get_broadcast_targets(self, target_type: Optional[str] = None, accessible_only: bool = True) -> List[BroadcastTarget]:
        """Broadcast hedeflerini al"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                query = "SELECT * FROM broadcast_targets WHERE 1=1"
                params = []
                
                if target_type:
                    query += " AND target_type = ?"
                    params.append(target_type)
                
                if accessible_only:
                    query += " AND is_accessible = TRUE"
                
                query += " ORDER BY failure_count ASC, last_success DESC"
                
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    
                    targets = []
                    for row in rows:
                        target = BroadcastTarget(
                            target_id=row[1],
                            target_type=row[2],
                            bot_username=row[3],
                            is_accessible=bool(row[4]),
                            last_success=datetime.fromisoformat(row[5]) if row[5] else None,
                            failure_count=row[6],
                            notes=row[7]
                        )
                        targets.append(target)
                    
                    return targets
            
        except Exception as e:
            logger.error(f"❌ Broadcast hedefleri alma hatası: {e}")
            return []
    
    async def log_broadcast_attempt(self, broadcast_id: str, target_id: str, target_type: str, 
                                  bot_username: str, message_type: str, message_content: str,
                                  status: BroadcastStatus, error_message: str = None) -> None:
        """Broadcast denemesini kaydet"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO broadcast_history 
                    (broadcast_id, target_id, target_type, bot_username, message_type, 
                     message_content, status, sent_at, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    broadcast_id, target_id, target_type, bot_username, message_type,
                    message_content, status.value, 
                    datetime.now() if status == BroadcastStatus.SENT else None,
                    error_message
                ))
                
                # Target'ın durumunu güncelle
                if status == BroadcastStatus.SENT:
                    await db.execute("""
                        UPDATE broadcast_targets 
                        SET last_success = ?, failure_count = 0, updated_at = ?
                        WHERE target_id = ? AND target_type = ? AND bot_username = ?
                    """, (datetime.now(), datetime.now(), target_id, target_type, bot_username))
                elif status == BroadcastStatus.FAILED:
                    await db.execute("""
                        UPDATE broadcast_targets 
                        SET failure_count = failure_count + 1, updated_at = ?
                        WHERE target_id = ? AND target_type = ? AND bot_username = ?
                    """, (datetime.now(), target_id, target_type, bot_username))
                
                await db.commit()
            
        except Exception as e:
            logger.error(f"❌ Broadcast log hatası: {e}")
    
    # ==================== USER ANALYTICS ====================
    
    async def update_user_analytics(self, user_id: str, username: str = None, 
                                  interaction_data: Dict[str, Any] = None) -> None:
        """Kullanıcı analitiğini güncelle"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Mevcut kullanıcıyı kontrol et
                async with db.execute("SELECT * FROM user_analytics WHERE user_id = ?", (user_id,)) as cursor:
                    existing = await cursor.fetchone()
                
                now = datetime.now()
                
                if existing:
                    # Güncelle
                    updates = ["last_activity = ?", "updated_at = ?"]
                    params = [now, now]
                    
                    if username:
                        updates.append("username = ?")
                        params.append(username)
                    
                    if interaction_data:
                        if interaction_data.get("message_count"):
                            updates.append("total_messages = total_messages + ?")
                            params.append(interaction_data["message_count"])
                        
                        if interaction_data.get("voice_minutes"):
                            updates.append("voice_minutes = voice_minutes + ?")
                            params.append(interaction_data["voice_minutes"])
                        
                        if interaction_data.get("quest_completed"):
                            updates.append("quests_completed = quests_completed + 1")
                        
                        if interaction_data.get("event_joined"):
                            updates.append("events_joined = events_joined + 1")
                        
                        if interaction_data.get("favorite_character"):
                            updates.append("favorite_character = ?")
                            params.append(interaction_data["favorite_character"])
                    
                    params.append(user_id)
                    
                    await db.execute(f"""
                        UPDATE user_analytics 
                        SET {', '.join(updates)}
                        WHERE user_id = ?
                    """, params)
                else:
                    # Yeni kullanıcı oluştur
                    await db.execute("""
                        INSERT INTO user_analytics 
                        (user_id, username, first_seen, last_activity, total_messages, voice_minutes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        user_id, username or f"user_{user_id}", now, now,
                        interaction_data.get("message_count", 0) if interaction_data else 0,
                        interaction_data.get("voice_minutes", 0) if interaction_data else 0
                    ))
                
                await db.commit()
                
                # Activity score hesapla
                await self._calculate_user_activity_score(db, user_id)
            
        except Exception as e:
            logger.error(f"❌ User analytics güncelleme hatası: {e}")
    
    async def log_user_interaction(self, user_id: str, interaction_type: UserInteractionType,
                                 character_id: str = None, group_id: str = None,
                                 duration_seconds: int = None, metadata: Dict[str, Any] = None) -> None:
        """Kullanıcı etkileşimini kaydet"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO user_interactions 
                    (user_id, interaction_type, character_id, group_id, duration_seconds, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_id, interaction_type.value, character_id, group_id,
                    duration_seconds, json.dumps(metadata) if metadata else None
                ))
                await db.commit()
            
        except Exception as e:
            logger.error(f"❌ User interaction log hatası: {e}")
    
    async def _calculate_user_activity_score(self, db: aiosqlite.Connection, user_id: str) -> None:
        """Kullanıcı aktivite skorunu hesapla"""
        try:
            # Son 30 günlük aktiviteyi al
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            async with db.execute("""
                SELECT COUNT(*) as interaction_count,
                       SUM(duration_seconds) as total_duration
                FROM user_interactions 
                WHERE user_id = ? AND created_at > ?
            """, (user_id, thirty_days_ago)) as cursor:
                result = await cursor.fetchone()
                
                interaction_count = result[0] or 0
                total_duration = result[1] or 0
                
                # Basit scoring algoritması
                activity_score = min(100.0, (interaction_count * 2) + (total_duration / 60))
                
                # Engagement level belirle
                if activity_score >= 80:
                    engagement_level = "vip"
                elif activity_score >= 50:
                    engagement_level = "high"
                elif activity_score >= 20:
                    engagement_level = "medium"
                else:
                    engagement_level = "low"
                
                await db.execute("""
                    UPDATE user_analytics 
                    SET activity_score = ?, engagement_level = ?, updated_at = ?
                    WHERE user_id = ?
                """, (activity_score, engagement_level, datetime.now(), user_id))
            
        except Exception as e:
            logger.error(f"❌ Activity score hesaplama hatası: {e}")
    
    # ==================== GROUP ANALYTICS ====================
    
    async def update_group_analytics(self, group_id: str, group_name: str = None,
                                   member_count: int = None, bot_accessible: bool = None) -> None:
        """Grup analitiğini güncelle"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Mevcut grubu kontrol et
                async with db.execute("SELECT * FROM group_analytics WHERE group_id = ?", (group_id,)) as cursor:
                    existing = await cursor.fetchone()
                
                now = datetime.now()
                
                if existing:
                    # Güncelle
                    updates = ["updated_at = ?"]
                    params = [now]
                    
                    if group_name:
                        updates.append("group_name = ?")
                        params.append(group_name)
                    
                    if member_count is not None:
                        updates.append("member_count = ?")
                        params.append(member_count)
                    
                    if bot_accessible is not None:
                        updates.append("bot_accessible = ?")
                        params.append(bot_accessible)
                    
                    params.append(group_id)
                    
                    await db.execute(f"""
                        UPDATE group_analytics 
                        SET {', '.join(updates)}
                        WHERE group_id = ?
                    """, params)
                else:
                    # Yeni grup oluştur
                    await db.execute("""
                        INSERT INTO group_analytics 
                        (group_id, group_name, member_count, bot_accessible)
                        VALUES (?, ?, ?, ?)
                    """, (group_id, group_name, member_count or 0, bot_accessible if bot_accessible is not None else True))
                
                await db.commit()
            
        except Exception as e:
            logger.error(f"❌ Group analytics güncelleme hatası: {e}")
    
    # ==================== AI ANALYSIS & CRM ====================
    
    async def get_users_for_ai_analysis(self, limit: int = 100) -> List[Dict[str, Any]]:
        """AI analizi için kullanıcı verilerini al"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT ua.*, 
                           COUNT(ui.id) as recent_interactions,
                           AVG(ui.duration_seconds) as avg_interaction_duration
                    FROM user_analytics ua
                    LEFT JOIN user_interactions ui ON ua.user_id = ui.user_id 
                        AND ui.created_at > datetime('now', '-30 days')
                    GROUP BY ua.user_id
                    ORDER BY ua.activity_score DESC
                    LIMIT ?
                """, (limit,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    users = []
                    for row in rows:
                        user_data = {
                            "user_id": row[1],
                            "username": row[2],
                            "first_seen": row[3],
                            "last_activity": row[4],
                            "total_messages": row[5],
                            "voice_minutes": row[6],
                            "quests_completed": row[7],
                            "events_joined": row[8],
                            "favorite_character": row[9],
                            "activity_score": row[10],
                            "engagement_level": row[11],
                            "recent_interactions": row[14] or 0,
                            "avg_interaction_duration": row[15] or 0
                        }
                        users.append(user_data)
                    
                    return users
            
        except Exception as e:
            logger.error(f"❌ AI analizi için veri alma hatası: {e}")
            return []
    
    async def save_ai_analysis_result(self, analysis_type: str, target_id: str,
                                    analysis_data: Dict[str, Any], insights: Dict[str, Any],
                                    recommendations: Dict[str, Any], confidence_score: float = 0.0) -> None:
        """AI analiz sonucunu kaydet"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO ai_analysis_results 
                    (analysis_type, target_id, analysis_data, insights, recommendations, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    analysis_type, target_id,
                    json.dumps(analysis_data), json.dumps(insights),
                    json.dumps(recommendations), confidence_score
                ))
                await db.commit()
            
        except Exception as e:
            logger.error(f"❌ AI analiz sonucu kaydetme hatası: {e}")
    
    async def create_crm_segment(self, segment_name: str, criteria: Dict[str, Any],
                               description: str = "") -> bool:
        """CRM segmenti oluştur"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Kriterlere göre kullanıcı sayısını hesapla
                user_count = await self._count_users_by_criteria(db, criteria)
                
                await db.execute("""
                    INSERT OR REPLACE INTO crm_segments 
                    (segment_name, criteria, user_count, description)
                    VALUES (?, ?, ?, ?)
                """, (segment_name, json.dumps(criteria), user_count, description))
                await db.commit()
                
                logger.info(f"✅ CRM segmenti oluşturuldu: {segment_name} ({user_count} kullanıcı)")
                return True
            
        except Exception as e:
            logger.error(f"❌ CRM segmenti oluşturma hatası: {e}")
            return False
    
    async def _count_users_by_criteria(self, db: aiosqlite.Connection, criteria: Dict[str, Any]) -> int:
        """Kriterlere göre kullanıcı sayısını hesapla"""
        try:
            query = "SELECT COUNT(*) FROM user_analytics WHERE 1=1"
            params = []
            
            if criteria.get("engagement_level"):
                query += " AND engagement_level = ?"
                params.append(criteria["engagement_level"])
            
            if criteria.get("min_activity_score"):
                query += " AND activity_score >= ?"
                params.append(criteria["min_activity_score"])
            
            if criteria.get("min_messages"):
                query += " AND total_messages >= ?"
                params.append(criteria["min_messages"])
            
            if criteria.get("favorite_character"):
                query += " AND favorite_character = ?"
                params.append(criteria["favorite_character"])
            
            async with db.execute(query, params) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0
            
        except Exception as e:
            logger.error(f"❌ Kullanıcı sayısı hesaplama hatası: {e}")
            return 0
    
    # ==================== REPORTING ====================
    
    async def get_broadcast_stats(self, days: int = 7) -> Dict[str, Any]:
        """Broadcast istatistiklerini al"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                since_date = datetime.now() - timedelta(days=days)
                
                async with db.execute("""
                    SELECT status, COUNT(*) as count
                    FROM broadcast_history 
                    WHERE created_at > ?
                    GROUP BY status
                """, (since_date,)) as cursor:
                    status_counts = {row[0]: row[1] for row in await cursor.fetchall()}
                
                async with db.execute("""
                    SELECT target_type, COUNT(*) as count
                    FROM broadcast_history 
                    WHERE created_at > ?
                    GROUP BY target_type
                """, (since_date,)) as cursor:
                    type_counts = {row[0]: row[1] for row in await cursor.fetchall()}
                
                return {
                    "period_days": days,
                    "status_breakdown": status_counts,
                    "type_breakdown": type_counts,
                    "total_broadcasts": sum(status_counts.values()),
                    "success_rate": status_counts.get("sent", 0) / max(1, sum(status_counts.values())) * 100
                }
            
        except Exception as e:
            logger.error(f"❌ Broadcast stats hatası: {e}")
            return {}
    
    async def get_user_engagement_report(self) -> Dict[str, Any]:
        """Kullanıcı engagement raporu"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT engagement_level, COUNT(*) as count, AVG(activity_score) as avg_score
                    FROM user_analytics
                    GROUP BY engagement_level
                """) as cursor:
                    engagement_data = {row[0]: {"count": row[1], "avg_score": row[2]} 
                                     for row in await cursor.fetchall()}
                
                async with db.execute("""
                    SELECT COUNT(*) as total_users,
                           AVG(activity_score) as avg_activity_score,
                           SUM(total_messages) as total_messages,
                           SUM(voice_minutes) as total_voice_minutes
                    FROM user_analytics
                """) as cursor:
                    overall_stats = await cursor.fetchone()
                
                return {
                    "engagement_breakdown": engagement_data,
                    "total_users": overall_stats[0],
                    "avg_activity_score": overall_stats[1],
                    "total_messages": overall_stats[2],
                    "total_voice_minutes": overall_stats[3]
                }
            
        except Exception as e:
            logger.error(f"❌ User engagement report hatası: {e}")
            return {}

# Global instance
database_manager = DatabaseManager() 