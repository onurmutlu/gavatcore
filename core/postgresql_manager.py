from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
BabaGAVAT PostgreSQL Manager
Onur Metodu ile PostgreSQL Async Database Operations  
PostgreSQL + Redis + MongoDB Hybrid Architecture
BabaGAVAT'ın sokak zekası ile production database yönetimi
"""

import asyncio
import asyncpg
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, AsyncContextManager
import structlog
import json

logger = structlog.get_logger("babagavat.postgresql")

class BabaGAVATPostgreSQLManager:
    """BabaGAVAT PostgreSQL Manager - Sokak tecrübesi ile production database"""
    
    def __init__(self, postgres_url: str = None):
        self.postgres_url = postgres_url or os.getenv(
            "DATABASE_URL", 
            "postgresql://localhost:5432/babagavat_db"
        )
        self.pool: Optional[asyncpg.Pool] = None
        self.is_initialized = False
        
    async def initialize(self) -> None:
        """PostgreSQL pool'u başlat"""
        try:
            # AsyncPG pool oluştur
            self.pool = await asyncpg.create_pool(
                self.postgres_url,
                min_size=5,
                max_size=20,
                command_timeout=60,
                server_settings={
                    'application_name': 'babagavat_production',
                    'jit': 'off'  # Performance için
                }
            )
            
            # Connection test
            async with self.pool.acquire() as connection:
                result = await connection.fetchval("SELECT version()")
                logger.info(f"PostgreSQL connected: {result[:50]}...")
            
            # Database tabloları oluştur
            await self._create_tables()
            
            self.is_initialized = True
            logger.info("🔥 BabaGAVAT PostgreSQL Manager başlatıldı - Production DB aktif!")
            
        except Exception as e:
            logger.error(f"❌ PostgreSQL bağlantı hatası: {e}")
            self.pool = None
            self.is_initialized = False
    
    async def close(self) -> None:
        """PostgreSQL pool'u kapat"""
        if self.pool:
            await self.pool.close()
    
    async def _create_tables(self) -> None:
        """BabaGAVAT PostgreSQL tablolarını oluştur"""
        try:
            async with self.pool.acquire() as connection:
                # Coin Balances tablosu
                await connection.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_coin_balances (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT UNIQUE NOT NULL,
                        balance DECIMAL(15,2) DEFAULT 0.00,
                        total_earned DECIMAL(15,2) DEFAULT 0.00,
                        total_spent DECIMAL(15,2) DEFAULT 0.00,
                        user_type VARCHAR(20) DEFAULT 'male',
                        babagavat_tier VARCHAR(20) DEFAULT 'bronze',
                        daily_earn_count INTEGER DEFAULT 0,
                        daily_spend_count INTEGER DEFAULT 0,
                        last_daily_reset DATE DEFAULT CURRENT_DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Coin Transactions tablosu
                await connection.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_coin_transactions (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        amount DECIMAL(15,2) NOT NULL,
                        transaction_type VARCHAR(50) NOT NULL,
                        description TEXT NOT NULL,
                        related_user_id BIGINT,
                        metadata JSONB,
                        babagavat_approval BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Daily Limits tablosu
                await connection.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_daily_limits (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        limit_date DATE NOT NULL,
                        earned_today DECIMAL(15,2) DEFAULT 0.00,
                        spent_today DECIMAL(15,2) DEFAULT 0.00,
                        messages_sent_today INTEGER DEFAULT 0,
                        babagavat_warnings INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, limit_date)
                    )
                """)
                
                # ErkoAnalyzer Profiles tablosu
                await connection.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_erko_profiles (
                        user_id BIGINT PRIMARY KEY,
                        username VARCHAR(100),
                        segment VARCHAR(20) NOT NULL,
                        risk_level VARCHAR(20) NOT NULL,
                        babagavat_score DECIMAL(5,2) DEFAULT 0.00,
                        street_smart_rating DECIMAL(5,2) DEFAULT 0.00,
                        coin_balance DECIMAL(15,2) DEFAULT 0.00,
                        total_spent DECIMAL(15,2) DEFAULT 0.00,
                        total_earned DECIMAL(15,2) DEFAULT 0.00,
                        message_count INTEGER DEFAULT 0,
                        performer_interactions INTEGER DEFAULT 0,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        spending_pattern JSONB DEFAULT '{}',
                        interaction_quality DECIMAL(5,2) DEFAULT 0.00,
                        red_flags JSONB DEFAULT '[]',
                        green_flags JSONB DEFAULT '[]',
                        babagavat_notes TEXT DEFAULT '',
                        last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Leaderboard tablosu
                await connection.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_coin_leaderboard (
                        user_id BIGINT PRIMARY KEY,
                        balance DECIMAL(15,2) DEFAULT 0.00,
                        tier VARCHAR(20) DEFAULT 'bronze',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Indexes oluştur
                await connection.execute("CREATE INDEX IF NOT EXISTS idx_coin_transactions_user_id ON babagavat_coin_transactions(user_id)")
                await connection.execute("CREATE INDEX IF NOT EXISTS idx_coin_transactions_type ON babagavat_coin_transactions(transaction_type)")
                await connection.execute("CREATE INDEX IF NOT EXISTS idx_coin_transactions_created_at ON babagavat_coin_transactions(created_at)")
                await connection.execute("CREATE INDEX IF NOT EXISTS idx_daily_limits_user_date ON babagavat_daily_limits(user_id, limit_date)")
                await connection.execute("CREATE INDEX IF NOT EXISTS idx_erko_profiles_segment ON babagavat_erko_profiles(segment)")
                await connection.execute("CREATE INDEX IF NOT EXISTS idx_erko_profiles_risk ON babagavat_erko_profiles(risk_level)")
                await connection.execute("CREATE INDEX IF NOT EXISTS idx_leaderboard_balance ON babagavat_coin_leaderboard(balance DESC)")
                
                logger.info("✅ BabaGAVAT PostgreSQL tabloları oluşturuldu - Production DB hazır! 💾")
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL tablo oluşturma hatası: {e}")
            raise
    
    # COIN BALANCE OPERATIONS
    async def get_coin_balance(self, user_id: int) -> float:
        """Kullanıcı coin bakiyesini PostgreSQL'den al"""
        try:
            if not self.pool:
                return 0.0
                
            async with self.pool.acquire() as connection:
                result = await connection.fetchval(
                    "SELECT balance FROM babagavat_coin_balances WHERE user_id = $1",
                    user_id
                )
                
                balance = float(result) if result else 0.0
                logger.info(f"💰 BabaGAVAT PostgreSQL balance get: user_id={user_id}, balance={balance}")
                return balance
                
        except Exception as e:
            logger.warning(f"⚠️ PostgreSQL balance get hatası: {e}")
            return 0.0
    
    async def set_coin_balance(self, user_id: int, balance: float, tier: str = "bronze") -> bool:
        """Kullanıcı coin bakiyesini PostgreSQL'e kaydet"""
        try:
            if not self.pool:
                return False
                
            async with self.pool.acquire() as connection:
                # Upsert operation
                await connection.execute("""
                    INSERT INTO babagavat_coin_balances (user_id, balance, babagavat_tier, updated_at)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id) DO UPDATE SET
                        balance = EXCLUDED.balance,
                        babagavat_tier = EXCLUDED.babagavat_tier,
                        updated_at = EXCLUDED.updated_at
                """, user_id, balance, tier, datetime.now())
                
                # Leaderboard güncelle
                await connection.execute("""
                    INSERT INTO babagavat_coin_leaderboard (user_id, balance, tier, updated_at)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id) DO UPDATE SET
                        balance = EXCLUDED.balance,
                        tier = EXCLUDED.tier,
                        updated_at = EXCLUDED.updated_at
                """, user_id, balance, tier, datetime.now())
                
                logger.info(f"💰 BabaGAVAT PostgreSQL balance set: user_id={user_id}, balance={balance}")
                return True
                
        except Exception as e:
            logger.warning(f"⚠️ PostgreSQL balance set hatası: {e}")
            return False
    
    async def add_coin_transaction(self, user_id: int, amount: float, transaction_type: str, 
                                 description: str, related_user_id: Optional[int] = None,
                                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Coin transaction kaydet"""
        try:
            if not self.pool:
                return False
                
            async with self.pool.acquire() as connection:
                await connection.execute("""
                    INSERT INTO babagavat_coin_transactions 
                    (user_id, amount, transaction_type, description, related_user_id, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, user_id, amount, transaction_type, description, related_user_id, 
                    json.dumps(metadata) if metadata else None)
                
                logger.info(f"💸 BabaGAVAT PostgreSQL transaction added: user_id={user_id}, amount={amount}, type={transaction_type}")
                return True
                
        except Exception as e:
            logger.warning(f"⚠️ PostgreSQL transaction add hatası: {e}")
            return False
    
    async def get_coin_transactions(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Kullanıcı coin transaction geçmişini al"""
        try:
            if not self.pool:
                return []
                
            async with self.pool.acquire() as connection:
                rows = await connection.fetch("""
                    SELECT amount, transaction_type, description, related_user_id, 
                           metadata, created_at
                    FROM babagavat_coin_transactions 
                    WHERE user_id = $1 
                    ORDER BY created_at DESC 
                    LIMIT $2
                """, user_id, limit)
                
                transactions = []
                for row in rows:
                    transactions.append({
                        "amount": float(row["amount"]),
                        "transaction_type": row["transaction_type"],
                        "description": row["description"],
                        "related_user_id": row["related_user_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "created_at": row["created_at"].isoformat(),
                        "babagavat_verified": True
                    })
                
                return transactions
                
        except Exception as e:
            logger.warning(f"⚠️ PostgreSQL transactions get hatası: {e}")
            return []
    
    # ERKO ANALYZER OPERATIONS
    async def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """ErkoAnalyzer kullanıcı profili PostgreSQL'den al"""
        try:
            if not self.pool:
                return None
                
            async with self.pool.acquire() as connection:
                row = await connection.fetchrow("""
                    SELECT * FROM babagavat_erko_profiles WHERE user_id = $1
                """, user_id)
                
                if row:
                    profile = dict(row)
                    # JSON fields'ları parse et
                    profile["spending_pattern"] = json.loads(profile["spending_pattern"]) if profile["spending_pattern"] else {}
                    profile["red_flags"] = json.loads(profile["red_flags"]) if profile["red_flags"] else []
                    profile["green_flags"] = json.loads(profile["green_flags"]) if profile["green_flags"] else []
                    # Datetime'ları ISO format'a çevir
                    for field in ["last_activity", "registration_date", "last_analyzed", "created_at", "updated_at"]:
                        if profile[field]:
                            profile[field] = profile[field].isoformat()
                    
                    return profile
                
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ PostgreSQL user profile get hatası: {e}")
            return None
    
    async def set_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """ErkoAnalyzer kullanıcı profili PostgreSQL'e kaydet"""
        try:
            if not self.pool:
                return False
                
            async with self.pool.acquire() as connection:
                await connection.execute("""
                    INSERT INTO babagavat_erko_profiles 
                    (user_id, username, segment, risk_level, babagavat_score, street_smart_rating,
                     coin_balance, total_spent, total_earned, message_count, performer_interactions,
                     last_activity, registration_date, spending_pattern, interaction_quality,
                     red_flags, green_flags, babagavat_notes, last_analyzed, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
                    ON CONFLICT (user_id) DO UPDATE SET
                        username = EXCLUDED.username,
                        segment = EXCLUDED.segment,
                        risk_level = EXCLUDED.risk_level,
                        babagavat_score = EXCLUDED.babagavat_score,
                        street_smart_rating = EXCLUDED.street_smart_rating,
                        coin_balance = EXCLUDED.coin_balance,
                        total_spent = EXCLUDED.total_spent,
                        total_earned = EXCLUDED.total_earned,
                        message_count = EXCLUDED.message_count,
                        performer_interactions = EXCLUDED.performer_interactions,
                        last_activity = EXCLUDED.last_activity,
                        registration_date = EXCLUDED.registration_date,
                        spending_pattern = EXCLUDED.spending_pattern,
                        interaction_quality = EXCLUDED.interaction_quality,
                        red_flags = EXCLUDED.red_flags,
                        green_flags = EXCLUDED.green_flags,
                        babagavat_notes = EXCLUDED.babagavat_notes,
                        last_analyzed = EXCLUDED.last_analyzed,
                        updated_at = EXCLUDED.updated_at
                """, 
                user_id,
                profile_data.get("username", f"user_{user_id}"),
                profile_data.get("segment", "newbie"),
                profile_data.get("risk_level", "low"),
                profile_data.get("babagavat_score", 0.0),
                profile_data.get("street_smart_rating", 0.0),
                profile_data.get("coin_balance", 0.0),
                profile_data.get("total_spent", 0.0),
                profile_data.get("total_earned", 0.0),
                profile_data.get("message_count", 0),
                profile_data.get("performer_interactions", 0),
                datetime.fromisoformat(profile_data.get("last_activity", datetime.now().isoformat())),
                datetime.fromisoformat(profile_data.get("registration_date", datetime.now().isoformat())),
                json.dumps(profile_data.get("spending_pattern", {})),
                profile_data.get("interaction_quality", 0.0),
                json.dumps(profile_data.get("red_flags", [])),
                json.dumps(profile_data.get("green_flags", [])),
                profile_data.get("babagavat_notes", ""),
                datetime.fromisoformat(profile_data.get("last_analyzed", datetime.now().isoformat())),
                datetime.now()
                )
                
                logger.info(f"🔍 BabaGAVAT PostgreSQL user profile set: user_id={user_id}")
                return True
                
        except Exception as e:
            logger.warning(f"⚠️ PostgreSQL user profile set hatası: {e}")
            return False
    
    # LEADERBOARD OPERATIONS
    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Leaderboard PostgreSQL'den al"""
        try:
            if not self.pool:
                return []
                
            async with self.pool.acquire() as connection:
                rows = await connection.fetch("""
                    SELECT user_id, balance, tier 
                    FROM babagavat_coin_leaderboard 
                    ORDER BY balance DESC 
                    LIMIT $1
                """, limit)
                
                leaderboard = []
                for row in rows:
                    leaderboard.append({
                        "user_id": row["user_id"],
                        "balance": float(row["balance"]),
                        "tier": row["tier"]
                    })
                
                return leaderboard
                
        except Exception as e:
            logger.warning(f"⚠️ PostgreSQL leaderboard get hatası: {e}")
            return []
    
    # ANALYTICS OPERATIONS
    async def get_analytics_data(self, days: int = 7) -> Dict[str, Any]:
        """Analytics verilerini al"""
        try:
            if not self.pool:
                return {}
                
            start_date = datetime.now() - timedelta(days=days)
            
            async with self.pool.acquire() as connection:
                # Toplam kullanıcı sayısı
                total_users = await connection.fetchval(
                    "SELECT COUNT(*) FROM babagavat_coin_balances"
                )
                
                # Aktif kullanıcılar
                active_users = await connection.fetchval("""
                    SELECT COUNT(DISTINCT user_id) FROM babagavat_coin_transactions 
                    WHERE created_at >= $1
                """, start_date)
                
                # Toplam transaction sayısı
                total_transactions = await connection.fetchval("""
                    SELECT COUNT(*) FROM babagavat_coin_transactions 
                    WHERE created_at >= $1
                """, start_date)
                
                # Toplam coin hacmi
                total_volume = await connection.fetchval("""
                    SELECT COALESCE(SUM(ABS(amount)), 0) FROM babagavat_coin_transactions 
                    WHERE created_at >= $1
                """, start_date)
                
                # Segment dağılımı
                segment_rows = await connection.fetch("""
                    SELECT segment, COUNT(*) as count 
                    FROM babagavat_erko_profiles 
                    GROUP BY segment
                """)
                
                segments = {row["segment"]: row["count"] for row in segment_rows}
                
                return {
                    "total_users": total_users,
                    "active_users_count": active_users,
                    "total_transactions": total_transactions,
                    "total_coin_volume": float(total_volume) if total_volume else 0,
                    "segment_distribution": segments,
                    "analysis_period_days": days,
                    "generated_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.warning(f"⚠️ PostgreSQL analytics get hatası: {e}")
            return {}
    
    async def get_db_stats(self) -> Dict[str, Any]:
        """Database istatistiklerini al"""
        try:
            if not self.pool:
                return {"status": "not_connected"}
                
            async with self.pool.acquire() as connection:
                # Database boyutu
                db_size = await connection.fetchval("""
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """)
                
                # Tablo sayıları
                table_counts = {}
                for table in ["babagavat_coin_balances", "babagavat_coin_transactions", 
                             "babagavat_daily_limits", "babagavat_erko_profiles", "babagavat_coin_leaderboard"]:
                    count = await connection.fetchval(f"SELECT COUNT(*) FROM {table}")
                    table_counts[table] = count
                
                return {
                    "status": "connected",
                    "database_size": db_size,
                    "table_counts": table_counts,
                    "connection_pool_size": self.pool._queue.qsize() if self.pool else 0,
                    "babagavat_postgresql_active": True
                }
                
        except Exception as e:
            logger.warning(f"⚠️ PostgreSQL stats get hatası: {e}")
            return {"status": "error", "error": str(e)}

# Global PostgreSQL Manager instance
babagavat_postgresql_manager = BabaGAVATPostgreSQLManager() 