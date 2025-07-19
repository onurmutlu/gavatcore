from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
BabaGAVAT ErkoAnalyzer - Onur Metodu ile Erkek Kullanıcı Analizi
Redis Cache + MongoDB + SQLite Hybrid Architecture 
BabaGAVAT'ın sokak zekası ile database lock sorunları çözüldü
"""

import asyncio
import sqlite3
import aiosqlite
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
import structlog
from dataclasses import dataclass, asdict
import json
import random

# Redis ve MongoDB managers
from .redis_manager import babagavat_redis_manager
from .mongodb_manager import babagavat_mongo_manager
from .database_manager import database_manager

logger = structlog.get_logger("babagavat.erko_analyzer")

class ErkoSegment(Enum):
    """Erkek kullanıcı segmentleri - BabaGAVAT'ın sokak sınıflandırması"""
    HOT = "hot"           # Aktif, çok harcayan, etkileşimli
    COLD = "cold"         # Pasif, az harcayan, düşük etkileşim
    GHOST = "ghost"       # Görünmez, hiç etkileşim yok
    FAKE = "fake"         # Sahte, şüpheli davranış
    VIP = "vip"          # Premium, yüksek değerli müşteri
    WHALE = "whale"       # Çok yüksek harcama yapan
    NEWBIE = "newbie"     # Yeni kullanıcı
    REGULAR = "regular"   # Normal kullanıcı

class ErkoRiskLevel(Enum):
    """Risk seviyeleri - BabaGAVAT'ın güvenlik değerlendirmesi"""
    LOW = "low"           # Düşük risk
    MEDIUM = "medium"     # Orta risk
    HIGH = "high"         # Yüksek risk
    CRITICAL = "critical" # Kritik risk

@dataclass
class ErkoProfile:
    """Erkek kullanıcı profili - BabaGAVAT'ın dosyası"""
    user_id: int
    username: str
    segment: ErkoSegment
    risk_level: ErkoRiskLevel
    coin_balance: int
    total_spent: int
    total_earned: int
    message_count: int
    performer_interactions: int
    last_activity: datetime
    registration_date: datetime
    babagavat_score: float  # 0.0 - 1.0
    street_smart_rating: float  # 0.0 - 1.0
    spending_pattern: Dict[str, Any]
    interaction_quality: float
    red_flags: List[str]
    green_flags: List[str]
    babagavat_notes: str
    last_analyzed: datetime = None

class BabaGAVATErkoAnalyzer:
    """BabaGAVAT ErkoAnalyzer - Sokak tecrübesi ile erkek kullanıcı analizi"""
    
    def __init__(self):
        self.is_initialized = False
        self.redis_enabled = False
        self.mongodb_enabled = False
        
    async def initialize(self) -> None:
        """BabaGAVAT ErkoAnalyzer'ı başlat"""
        try:
            # Redis Manager'ı başlat
            await babagavat_redis_manager.initialize()
            self.redis_enabled = babagavat_redis_manager.is_initialized
            
            # MongoDB Manager'ı başlat
            await babagavat_mongo_manager.initialize()
            self.mongodb_enabled = babagavat_mongo_manager.is_initialized
            
            # SQLite Database Manager'ı başlat (fallback)
            await database_manager.initialize()
            
            # Database tabloları oluştur
            await self._create_erko_analyzer_tables()
            
            self.is_initialized = True
            
            logger.info("💪 BabaGAVAT ErkoAnalyzer başlatıldı - Erkek kullanıcı sokak analizi aktif!")
            logger.info(f"🔥 Redis: {'✅ AKTİF' if self.redis_enabled else '❌ PASİF'}")
            logger.info(f"🔥 MongoDB: {'✅ AKTİF' if self.mongodb_enabled else '❌ PASİF'}")
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT ErkoAnalyzer başlatma hatası: {e}")
            raise
    
    async def _create_erko_analyzer_tables(self) -> None:
        """ErkoAnalyzer tabloları oluştur (SQLite fallback için)"""
        try:
            async with database_manager._get_connection() as db:
                # BabaGAVAT ErkoAnalyzer Profiles Table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_erko_profiles (
                        user_id INTEGER PRIMARY KEY,
                        segment TEXT NOT NULL,
                        risk_level TEXT NOT NULL,
                        babagavat_score REAL DEFAULT 0.0,
                        sokak_zekasi_level INTEGER DEFAULT 1,
                        last_message_count INTEGER DEFAULT 0,
                        last_spending_amount REAL DEFAULT 0.0,
                        activity_frequency TEXT DEFAULT 'low',
                        behavior_pattern TEXT DEFAULT 'normal',
                        risk_indicators TEXT DEFAULT '[]',
                        last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Eksik column'u ekle (eğer yoksa)
                try:
                    await db.execute("ALTER TABLE babagavat_erko_profiles ADD COLUMN sokak_zekasi_level INTEGER DEFAULT 1")
                except Exception:
                    # Column zaten var, devam et
                    pass
                
                # BabaGAVAT ErkoAnalyzer Activity Log Table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_erko_activity_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        activity_type TEXT NOT NULL,
                        activity_data TEXT NOT NULL,
                        risk_score REAL DEFAULT 0.0,
                        babagavat_flag BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # BabaGAVAT ErkoAnalyzer Segmentation History Table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_erko_segmentation_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        old_segment TEXT,
                        new_segment TEXT NOT NULL,
                        old_risk_level TEXT,
                        new_risk_level TEXT NOT NULL,
                        reason TEXT,
                        babagavat_approved BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # BabaGAVAT ErkoAnalyzer Alerts Table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_erko_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        alert_type TEXT NOT NULL,
                        alert_level TEXT NOT NULL,
                        alert_message TEXT NOT NULL,
                        alert_data TEXT DEFAULT '{}',
                        is_resolved BOOLEAN DEFAULT FALSE,
                        resolved_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Indexes oluştur
                await db.execute("CREATE INDEX IF NOT EXISTS idx_erko_profiles_segment ON babagavat_erko_profiles(segment)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_erko_profiles_risk ON babagavat_erko_profiles(risk_level)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_erko_activity_user ON babagavat_erko_activity_log(user_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_erko_activity_type ON babagavat_erko_activity_log(activity_type)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_erko_segmentation_user ON babagavat_erko_segmentation_history(user_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_erko_alerts_user ON babagavat_erko_alerts(user_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_erko_alerts_resolved ON babagavat_erko_alerts(is_resolved)")
                
                await db.commit()
                
            logger.info("✅ BabaGAVAT ErkoAnalyzer tabloları oluşturuldu - Erkek kullanıcı dosyaları hazır! 📋")
            
        except Exception as e:
            logger.error(f"❌ ErkoAnalyzer tabloları oluşturma hatası: {e}")
            raise
    
    async def analyze_user(self, user_id: int, force_refresh: bool = False) -> ErkoProfile:
        """Kullanıcı analizi - Redis → MongoDB → SQLite cascade"""
        try:
            # Redis cache'ten dene (force refresh değilse)
            if not force_refresh and self.redis_enabled:
                cached_profile = await babagavat_redis_manager.get_user_profile(user_id)
                if cached_profile:
                    # Dict'i ErkoProfile'a çevir - mevcut yapıya uygun
                    profile = ErkoProfile(
                        user_id=cached_profile["user_id"],
                        username=cached_profile.get("username", f"user_{user_id}"),
                        segment=ErkoSegment(cached_profile["segment"]),
                        risk_level=ErkoRiskLevel(cached_profile["risk_level"]),
                        coin_balance=cached_profile.get("coin_balance", 0),
                        total_spent=cached_profile.get("total_spent", 0),
                        total_earned=cached_profile.get("total_earned", 0),
                        message_count=cached_profile.get("message_count", 0),
                        performer_interactions=cached_profile.get("performer_interactions", 0),
                        last_activity=datetime.fromisoformat(cached_profile.get("last_activity", datetime.now().isoformat())),
                        registration_date=datetime.fromisoformat(cached_profile.get("registration_date", datetime.now().isoformat())),
                        babagavat_score=cached_profile.get("babagavat_score", 0.0),
                        street_smart_rating=cached_profile.get("street_smart_rating", 0.0),
                        spending_pattern=cached_profile.get("spending_pattern", {}),
                        interaction_quality=cached_profile.get("interaction_quality", 0.0),
                        red_flags=cached_profile.get("red_flags", []),
                        green_flags=cached_profile.get("green_flags", []),
                        babagavat_notes=cached_profile.get("babagavat_notes", ""),
                        last_analyzed=datetime.fromisoformat(cached_profile.get("last_analyzed", datetime.now().isoformat()))
                    )
                    logger.info(f"🔍 BabaGAVAT Redis cache hit: user_id={user_id}, segment={profile.segment.value}")
                    return profile
            
            # MongoDB'den dene
            if self.mongodb_enabled:
                mongo_profile = await babagavat_mongo_manager.get_user_profile(user_id)
                if mongo_profile:
                    profile = ErkoProfile(
                        user_id=mongo_profile["user_id"],
                        username=mongo_profile.get("username", f"user_{user_id}"),
                        segment=ErkoSegment(mongo_profile["segment"]),
                        risk_level=ErkoRiskLevel(mongo_profile["risk_level"]),
                        coin_balance=mongo_profile.get("coin_balance", 0),
                        total_spent=mongo_profile.get("total_spent", 0),
                        total_earned=mongo_profile.get("total_earned", 0),
                        message_count=mongo_profile.get("message_count", 0),
                        performer_interactions=mongo_profile.get("performer_interactions", 0),
                        last_activity=mongo_profile.get("last_activity", datetime.now()),
                        registration_date=mongo_profile.get("registration_date", datetime.now()),
                        babagavat_score=mongo_profile.get("babagavat_score", 0.0),
                        street_smart_rating=mongo_profile.get("street_smart_rating", 0.0),
                        spending_pattern=mongo_profile.get("spending_pattern", {}),
                        interaction_quality=mongo_profile.get("interaction_quality", 0.0),
                        red_flags=mongo_profile.get("red_flags", []),
                        green_flags=mongo_profile.get("green_flags", []),
                        babagavat_notes=mongo_profile.get("babagavat_notes", ""),
                        last_analyzed=datetime.fromisoformat(mongo_profile.get("last_analyzed", datetime.now().isoformat()))
                    )
                    
                    # Redis'e cache'le
                    if self.redis_enabled:
                        profile_dict = asdict(profile)
                        # datetime objelerini string'e çevir
                        profile_dict["last_activity"] = profile.last_activity.isoformat()
                        profile_dict["registration_date"] = profile.registration_date.isoformat()
                        await babagavat_redis_manager.set_user_profile(user_id, profile_dict)
                    
                    return profile
            
            # SQLite fallback ve yeni analiz
            profile = await self._perform_user_analysis(user_id)
            
            # Profili kaydet
            await self._save_user_profile(profile)
            
            return profile
            
        except Exception as e:
            logger.warning(f"⚠️ Kullanıcı analizi hatası: {e}")
            # Fallback profile
            return ErkoProfile(
                user_id=user_id,
                username=f"user_{user_id}",
                segment=ErkoSegment.NEWBIE,
                risk_level=ErkoRiskLevel.MEDIUM,
                coin_balance=0,
                total_spent=0,
                total_earned=0,
                message_count=0,
                performer_interactions=0,
                last_activity=datetime.now(),
                registration_date=datetime.now(),
                babagavat_score=0.0,
                street_smart_rating=0.0,
                spending_pattern={},
                interaction_quality=0.0,
                red_flags=[],
                green_flags=[],
                babagavat_notes="Yeni kullanıcı - BabaGAVAT analizi beklemede",
                last_analyzed=datetime.now()
            )
    
    async def _perform_user_analysis(self, user_id: int) -> ErkoProfile:
        """Gerçek kullanıcı analizi yap"""
        try:
            # Kullanıcı verilerini topla
            user_data = await self._collect_user_data(user_id)
            
            # Segment analizi
            segment = await self._analyze_user_segment(user_data)
            
            # Risk analizi  
            risk_level = await self._analyze_risk_level(user_data)
            
            # BabaGAVAT skoru hesapla
            babagavat_score = await self._calculate_babagavat_score(user_data)
            
            # Sokak zekası rating
            street_smart_rating = await self._calculate_street_smart_rating(user_data)
            
            # Harcama pattern analizi
            spending_pattern = await self._analyze_spending_pattern(user_data)
            
            # Risk göstergeleri
            red_flags, green_flags = await self._identify_risk_flags(user_data)
            
            # BabaGAVAT notları
            babagavat_notes = await self._generate_babagavat_notes(segment, risk_level, user_data)
            
            profile = ErkoProfile(
                user_id=user_id,
                username=user_data.get("username", f"user_{user_id}"),
                segment=segment,
                risk_level=risk_level,
                coin_balance=user_data.get("coin_balance", 0),
                total_spent=user_data.get("total_spent", 0),
                total_earned=user_data.get("total_earned", 0),
                message_count=user_data.get("message_count", 0),
                performer_interactions=user_data.get("performer_interactions", 0),
                last_activity=user_data.get("last_activity", datetime.now()),
                registration_date=user_data.get("registration_date", datetime.now()),
                babagavat_score=babagavat_score,
                street_smart_rating=street_smart_rating,
                spending_pattern=spending_pattern,
                interaction_quality=user_data.get("interaction_quality", 0.0),
                red_flags=red_flags,
                green_flags=green_flags,
                babagavat_notes=babagavat_notes,
                last_analyzed=datetime.now()
            )
            
            logger.info(f"🔍 BabaGAVAT ErkoAnalyzer: user_id={user_id}, segment={segment.value}, risk={risk_level.value}")
            
            return profile
            
        except Exception as e:
            logger.warning(f"⚠️ Kullanıcı analizi gerçekleştirme hatası: {e}")
            raise
    
    async def _save_user_profile(self, profile: ErkoProfile) -> None:
        """Kullanıcı profilini kaydet - MongoDB → Redis → SQLite"""
        try:
            # MongoDB'ye kaydet
            if self.mongodb_enabled:
                profile_data = asdict(profile)
                # datetime objelerini string'e çevir
                profile_data["last_activity"] = profile.last_activity.isoformat()
                profile_data["registration_date"] = profile.registration_date.isoformat() 
                profile_data["last_analyzed"] = profile.last_analyzed.isoformat()
                # Enum'ları string'e çevir
                profile_data["segment"] = profile.segment.value
                profile_data["risk_level"] = profile.risk_level.value
                await babagavat_mongo_manager.set_user_profile(profile.user_id, profile_data)
            
            # Redis'e cache'le
            if self.redis_enabled:
                profile_data = asdict(profile)
                profile_data["last_activity"] = profile.last_activity.isoformat()
                profile_data["registration_date"] = profile.registration_date.isoformat()
                profile_data["last_analyzed"] = profile.last_analyzed.isoformat()
                profile_data["segment"] = profile.segment.value
                profile_data["risk_level"] = profile.risk_level.value
                await babagavat_redis_manager.set_user_profile(profile.user_id, profile_data)
            
            # SQLite'ye kaydet (non-blocking attempt)
            try:
                async with database_manager._get_connection() as db:
                    await db.execute("""
                        INSERT OR REPLACE INTO babagavat_erko_profiles 
                        (user_id, segment, risk_level, babagavat_score, sokak_zekasi_level,
                         last_message_count, last_spending_amount, activity_frequency, 
                         behavior_pattern, risk_indicators, last_analyzed, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        profile.user_id, profile.segment.value, profile.risk_level.value,
                        profile.babagavat_score, 1,  # Default sokak_zekasi_level
                        profile.message_count, float(profile.total_spent),
                        "medium", "normal",  # Default activity_frequency, behavior_pattern
                        json.dumps(profile.red_flags), profile.last_analyzed,
                        datetime.now()
                    ))
                    
                    await db.commit()
            except Exception as sqlite_error:
                # SQLite lock hatası durumunda sadece log at, devam et
                logger.warning(f"⚠️ BabaGAVAT ErkoAnalyzer SQLite kayıt hatası: {sqlite_error}")
                
        except Exception as e:
            logger.warning(f"⚠️ Kullanıcı profili kaydetme hatası: {e}")
    
    async def _collect_user_data(self, user_id: int) -> Dict[str, Any]:
        """Kullanıcı verilerini topla - multiple source"""
        try:
            user_data = {
                "user_id": user_id,
                "message_count": 0,
                "spending_amount": 0.0,
                "activity_frequency": "low",
                "behavior_pattern": "normal",
                "registration_date": datetime.now() - timedelta(days=30),
                "last_activity": datetime.now() - timedelta(days=1),
                "total_sessions": 0,
                "avg_session_duration": 0.0
            }
            
            # MongoDB'den veri topla
            if self.mongodb_enabled:
                # Transaction verilerini al
                transactions = await babagavat_mongo_manager.get_coin_transactions(user_id, limit=100)
                if transactions:
                    spending_transactions = [t for t in transactions if t.get("amount", 0) < 0]
                    user_data["spending_amount"] = sum(abs(t.get("amount", 0)) for t in spending_transactions)
                    user_data["message_count"] = len([t for t in transactions if "message" in t.get("transaction_type", "")])
                
                # Activity verilerini al
                # Bu gerçek production'da activity log collection'dan alınacak
                user_data["total_sessions"] = random.randint(1, 50)
                user_data["avg_session_duration"] = random.uniform(5.0, 120.0)
            
            # SQLite'den backup veri al
            try:
                async with database_manager._get_connection() as db:
                    # Transaction sayısını al
                    cursor = await db.execute("""
                        SELECT COUNT(*), SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END)
                        FROM babagavat_coin_transactions 
                        WHERE user_id = ?
                    """, (user_id,))
                    
                    result = await cursor.fetchone()
                    if result:
                        user_data["message_count"] = result[0] or 0
                        user_data["spending_amount"] = result[1] or 0.0
                        
            except Exception as sqlite_error:
                logger.warning(f"⚠️ SQLite veri toplama hatası: {sqlite_error}")
            
            # Activity frequency hesapla
            if user_data["message_count"] > 50:
                user_data["activity_frequency"] = "high"
            elif user_data["message_count"] > 10:
                user_data["activity_frequency"] = "medium"
            else:
                user_data["activity_frequency"] = "low"
            
            return user_data
            
        except Exception as e:
            logger.warning(f"⚠️ Kullanıcı veri toplama hatası: {e}")
            return {"user_id": user_id, "message_count": 0, "spending_amount": 0.0}
    
    async def get_segment_statistics(self) -> Dict[str, Any]:
        """Segment istatistiklerini al - Redis cache first"""
        try:
            # Redis cache'ten dene
            if self.redis_enabled:
                stats_key = "segment_statistics"
                cached_stats = await babagavat_redis_manager.redis_client.get(f"babagavat:analytics:{stats_key}")
                if cached_stats:
                    return json.loads(cached_stats)
            
            # MongoDB'den istatistik al
            if self.mongodb_enabled:
                stats = await babagavat_mongo_manager.get_analytics_data(days=7)
                if stats:
                    # Redis'e cache'le
                    if self.redis_enabled:
                        await babagavat_redis_manager.redis_client.setex(
                            f"babagavat:analytics:segment_statistics",
                            300,  # 5 dakika cache
                            json.dumps(stats)
                        )
                    return stats
            
            # SQLite fallback
            async with database_manager._get_connection() as db:
                cursor = await db.execute("""
                    SELECT segment, COUNT(*) as count
                    FROM babagavat_erko_profiles 
                    GROUP BY segment
                """)
                
                rows = await cursor.fetchall()
                
                segments = {}
                total_users = 0
                for row in rows:
                    segments[row[0]] = row[1]
                    total_users += row[1]
                
                stats = {
                    "segments": segments,
                    "total_users": total_users,
                    "analysis_date": datetime.now().isoformat()
                }
                
                # Cache'le
                if self.redis_enabled:
                    await babagavat_redis_manager.redis_client.setex(
                        f"babagavat:analytics:segment_statistics",
                        300,
                        json.dumps(stats)
                    )
                
                return stats
                
        except Exception as e:
            logger.warning(f"⚠️ Segment istatistikleri hatası: {e}")
            return {"segments": {}, "total_users": 0}
    
    async def get_high_risk_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Yüksek riskli kullanıcıları al"""
        try:
            # MongoDB'den al
            if self.mongodb_enabled:
                # Gerçek production'da bu aggregation pipeline olacak
                high_risk_users = []
                # Placeholder implementation
                return high_risk_users
            
            # SQLite fallback
            async with database_manager._get_connection() as db:
                cursor = await db.execute("""
                    SELECT user_id, segment, risk_level, babagavat_score, risk_indicators
                    FROM babagavat_erko_profiles 
                    WHERE risk_level IN ('high', 'critical')
                    ORDER BY babagavat_score DESC
                    LIMIT ?
                """, (limit,))
                
                rows = await cursor.fetchall()
                
                high_risk_users = []
                for row in rows:
                    user = {
                        "user_id": row[0],
                        "username": f"user_{row[0]}",  # Gerçek username gerekli
                        "segment": row[1],
                        "risk_level": row[2],
                        "babagavat_score": row[3],
                        "risk_indicators": json.loads(row[4] or "[]")
                    }
                    high_risk_users.append(user)
                
                return high_risk_users
                
        except Exception as e:
            logger.warning(f"⚠️ Yüksek riskli kullanıcılar sorgu hatası: {e}")
            return []
    
    async def _analyze_user_segment(self, user_data: Dict[str, Any]) -> ErkoSegment:
        """Kullanıcı segmentini analiz et"""
        message_count = user_data.get("message_count", 0)
        spending_amount = user_data.get("spending_amount", 0.0)
        activity_frequency = user_data.get("activity_frequency", "low")
        
        # BabaGAVAT'ın sokak segmentasyon kuralları
        if spending_amount > 1000 and message_count > 100:
            return ErkoSegment.WHALE
        elif spending_amount > 500:
            return ErkoSegment.VIP
        elif message_count > 50 and activity_frequency == "high":
            return ErkoSegment.HOT
        elif message_count < 5 and spending_amount < 10:
            return ErkoSegment.COLD
        elif message_count == 0 and spending_amount == 0:
            return ErkoSegment.GHOST
        elif activity_frequency == "low" and spending_amount < 50:
            return ErkoSegment.REGULAR
        else:
            return ErkoSegment.NEWBIE
    
    async def _analyze_risk_level(self, user_data: Dict[str, Any]) -> ErkoRiskLevel:
        """Risk seviyesini analiz et"""
        spending_amount = user_data.get("spending_amount", 0.0)
        message_count = user_data.get("message_count", 0)
        
        # Risk kriterleri
        if spending_amount > 2000:
            return ErkoRiskLevel.CRITICAL
        elif spending_amount > 1000 or message_count > 100:
            return ErkoRiskLevel.HIGH
        elif spending_amount > 100 or message_count > 20:
            return ErkoRiskLevel.MEDIUM
        else:
            return ErkoRiskLevel.LOW
    
    async def _calculate_babagavat_score(self, user_data: Dict[str, Any]) -> float:
        """BabaGAVAT skoru hesapla"""
        message_count = user_data.get("message_count", 0)
        spending_amount = user_data.get("spending_amount", 0.0)
        activity_frequency = user_data.get("activity_frequency", "low")
        
        # Sokak zekası algoritması
        score = 0.0
        score += min(message_count * 0.1, 10.0)  # Mesaj aktivitesi
        score += min(spending_amount * 0.01, 20.0)  # Harcama tutarı
        
        if activity_frequency == "high":
            score += 5.0
        elif activity_frequency == "medium":
            score += 2.0
        
        return min(score, 100.0)
    
    async def _calculate_sokak_zekasi_level(self, user_data: Dict[str, Any]) -> int:
        """Sokak zekası seviyesi hesapla"""
        babagavat_score = await self._calculate_babagavat_score(user_data)
        
        if babagavat_score >= 80:
            return 5  # Usta seviye
        elif babagavat_score >= 60:
            return 4  # İleri seviye
        elif babagavat_score >= 40:
            return 3  # Orta seviye
        elif babagavat_score >= 20:
            return 2  # Başlangıç seviye
        else:
            return 1  # Çaylak seviye
    
    async def _calculate_street_smart_rating(self, user_data: Dict[str, Any]) -> float:
        """Sokak zekası rating hesapla (0.0 - 1.0)"""
        try:
            spending_amount = user_data.get("spending_amount", 0.0)
            message_count = user_data.get("message_count", 0)
            activity_frequency = user_data.get("activity_frequency", "low")
            
            # Sokak zekası algoritması
            rating = 0.0
            
            # Harcama pattern'ına göre puan
            if 50 <= spending_amount <= 500:  # Mantıklı harcama
                rating += 0.3
            elif spending_amount > 1000:  # Aşırı harcama (risk)
                rating += 0.1
            elif spending_amount < 10:  # Çok az harcama
                rating += 0.15
            
            # Message frequency'ye göre puan
            if 10 <= message_count <= 50:  # Dengeli mesajlaşma
                rating += 0.3
            elif message_count > 100:  # Aşırı mesaj (spam risk)
                rating += 0.1
            elif message_count < 5:  # Çok az etkileşim
                rating += 0.15
            
            # Activity pattern'ına göre puan
            if activity_frequency == "medium":
                rating += 0.2
            elif activity_frequency == "high":
                rating += 0.15
            else:
                rating += 0.1
            
            # BabaGAVAT bonus (deneyim)
            rating += 0.2
            
            return min(rating, 1.0)
            
        except Exception as e:
            logger.warning(f"⚠️ Sokak zekası rating hesaplama hatası: {e}")
            return 0.5  # Default rating
    
    async def _analyze_spending_pattern(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Harcama pattern analizi"""
        try:
            spending_amount = user_data.get("spending_amount", 0.0)
            message_count = user_data.get("message_count", 0)
            
            pattern = {
                "total_spending": spending_amount,
                "avg_per_message": spending_amount / max(message_count, 1),
                "spending_tier": "bronze",
                "pattern_type": "normal",
                "risk_indicators": []
            }
            
            # Spending tier hesapla
            if spending_amount >= 1000:
                pattern["spending_tier"] = "whale"
            elif spending_amount >= 500:
                pattern["spending_tier"] = "gold"
            elif spending_amount >= 100:
                pattern["spending_tier"] = "silver"
            else:
                pattern["spending_tier"] = "bronze"
            
            # Pattern type belirle
            if spending_amount > 2000:
                pattern["pattern_type"] = "excessive"
                pattern["risk_indicators"].append("high_spending")
            elif spending_amount == 0 and message_count > 10:
                pattern["pattern_type"] = "freeloader"
                pattern["risk_indicators"].append("no_spending")
            elif spending_amount / max(message_count, 1) > 50:
                pattern["pattern_type"] = "big_spender"
            else:
                pattern["pattern_type"] = "normal"
            
            return pattern
            
        except Exception as e:
            logger.warning(f"⚠️ Harcama pattern analizi hatası: {e}")
            return {"total_spending": 0, "pattern_type": "unknown"}
    
    async def _identify_risk_flags(self, user_data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Risk flag'lerini tespit et (red_flags, green_flags)"""
        try:
            red_flags = []
            green_flags = []
            
            spending_amount = user_data.get("spending_amount", 0.0)
            message_count = user_data.get("message_count", 0)
            activity_frequency = user_data.get("activity_frequency", "low")
            
            # Red flags (risk göstergeleri)
            if spending_amount > 2000:
                red_flags.append("excessive_spending")
            if message_count > 100:
                red_flags.append("spam_behavior")
            if spending_amount == 0 and message_count > 20:
                red_flags.append("freeloader_behavior")
            if activity_frequency == "high" and spending_amount < 50:
                red_flags.append("suspicious_activity")
            
            # Green flags (olumlu göstergeler)
            if 100 <= spending_amount <= 1000:
                green_flags.append("healthy_spending")
            if 5 <= message_count <= 50:
                green_flags.append("balanced_interaction")
            if activity_frequency == "medium":
                green_flags.append("consistent_activity")
            if spending_amount > 0 and message_count > 0:
                green_flags.append("engaged_user")
            
            return red_flags, green_flags
            
        except Exception as e:
            logger.warning(f"⚠️ Risk flag analizi hatası: {e}")
            return [], []
    
    async def _generate_babagavat_notes(self, segment: ErkoSegment, risk_level: ErkoRiskLevel, user_data: Dict[str, Any]) -> str:
        """BabaGAVAT notları oluştur"""
        try:
            spending_amount = user_data.get("spending_amount", 0.0)
            message_count = user_data.get("message_count", 0)
            
            # Segment'e göre temel not
            segment_notes = {
                ErkoSegment.WHALE: "🐋 Bu adam gerçek bir balina! Para konusunda sıkıntısı yok.",
                ErkoSegment.VIP: "⭐ VIP müşteri - özel ilgi gösterilmeli.",
                ErkoSegment.HOT: "🔥 Aktif kullanıcı - iyi potansiyel var.",
                ErkoSegment.COLD: "❄️ Soğuk müşteri - canlandırmaya ihtiyacı var.",
                ErkoSegment.GHOST: "👻 Hayalet kullanıcı - hiç etkileşim yok.",
                ErkoSegment.FAKE: "🚫 Şüpheli hesap - yakın takip gerekli.",
                ErkoSegment.NEWBIE: "🆕 Yeni kullanıcı - yönlendirme yapılmalı.",
                ErkoSegment.REGULAR: "👤 Normal kullanıcı - standart yaklaşım."
            }
            
            base_note = segment_notes.get(segment, "Kullanıcı analizi tamamlandı.")
            
            # Risk level'a göre ek notlar
            risk_notes = {
                ErkoRiskLevel.CRITICAL: " ⚠️ KRİTİK RİSK - ACİL MÜDAHALE GEREKLİ!",
                ErkoRiskLevel.HIGH: " 🚨 Yüksek risk - dikkatli takip edilmeli.",
                ErkoRiskLevel.MEDIUM: " ⚡ Orta risk - normal prosedürler uygulanabilir.",
                ErkoRiskLevel.LOW: " ✅ Düşük risk - güvenli kullanıcı."
            }
            
            risk_note = risk_notes.get(risk_level, "")
            
            # Harcama detayları
            spending_note = ""
            if spending_amount > 1000:
                spending_note = f" 💰 Toplam harcama: {spending_amount:.0f} coin - büyük müşteri!"
            elif spending_amount > 100:
                spending_note = f" 💵 Toplam harcama: {spending_amount:.0f} coin - iyi müşteri."
            elif spending_amount == 0:
                spending_note = " 🆓 Hiç harcama yapmamış - teşvik gerekli."
            
            # Mesaj detayları
            message_note = ""
            if message_count > 50:
                message_note = f" 📨 {message_count} mesaj - çok aktif!"
            elif message_count > 10:
                message_note = f" 💬 {message_count} mesaj - orta aktivite."
            elif message_count == 0:
                message_note = " 🤐 Hiç mesaj yok - sessiz kullanıcı."
            
            # Final not
            final_note = base_note + risk_note + spending_note + message_note
            
            return final_note
            
        except Exception as e:
            logger.warning(f"⚠️ BabaGAVAT notları oluşturma hatası: {e}")
            return "BabaGAVAT analizi tamamlandı."
    
    async def _identify_risk_indicators(self, user_data: Dict[str, Any]) -> List[str]:
        """Risk göstergelerini tespit et (legacy method)"""
        indicators = []
        
        spending_amount = user_data.get("spending_amount", 0.0)
        message_count = user_data.get("message_count", 0)
        
        if spending_amount > 1500:
            indicators.append("high_spending")
        if message_count > 100:
            indicators.append("excessive_messaging")
        if spending_amount == 0 and message_count == 0:
            indicators.append("inactive_user")
        
        return indicators

# Global BabaGAVAT ErkoAnalyzer instance
babagavat_erko_analyzer = BabaGAVATErkoAnalyzer() 