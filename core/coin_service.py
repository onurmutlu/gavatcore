from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
BabaGAVAT Coin Service - Sokak Zekası ile Güçlendirilmiş Coin Sistemi
FlirtMarket / GavatCore için Onur Metodu entegrasyonu
BabaGAVAT'ın sokak tecrübesi ile coin ekonomisi yönetimi
Redis Cache + MongoDB + PostgreSQL Hybrid Architecture
BabaGAVAT'ın sokak zekası ile database lock sorunları çözüldü
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import structlog
from .database_manager import database_manager

# Redis, MongoDB ve PostgreSQL managers
from .redis_manager import babagavat_redis_manager
from .mongodb_manager import babagavat_mongo_manager
from .postgresql_manager import babagavat_postgresql_manager

logger = structlog.get_logger("babagavat.coin_service")

class CoinTransactionType(Enum):
    """Coin işlem tipleri - BabaGAVAT'ın sokak ekonomisi"""
    EARN_REFERRAL = "earn_referral"           # Referans daveti
    EARN_TASK = "earn_task"                   # Görev tamamlama
    EARN_MESSAGE = "earn_message"             # Mesaj yazma
    EARN_ADMIN = "earn_admin"                 # Admin ödülü
    EARN_BONUS = "earn_bonus"                 # Bonus ödül
    SPEND_MESSAGE = "spend_message"           # Şovcuya mesaj
    SPEND_VIP_CONTENT = "spend_vip_content"   # VIP içerik
    SPEND_VIP_GROUP = "spend_vip_group"       # VIP grup üyelik
    SPEND_SPECIAL_SHOW = "spend_special_show" # Özel şov talebi
    SPEND_ADMIN = "spend_admin"               # Admin harcama

class UserType(Enum):
    """Kullanıcı tipleri - BabaGAVAT'ın sınıflandırması"""
    MALE = "male"           # Erkek kullanıcı
    PERFORMER = "performer" # Şovcu
    ADMIN = "admin"         # Admin
    VIP = "vip"            # VIP kullanıcı

@dataclass
class CoinTransaction:
    """Coin işlemi - BabaGAVAT'ın kayıt sistemi"""
    user_id: int
    amount: int
    transaction_type: CoinTransactionType
    description: str
    related_user_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = None

class BabaGAVATCoinService:
    """BabaGAVAT Coin Service - Sokak Zekası ile Coin Yönetimi"""
    
    def __init__(self):
        self.is_initialized = False
        self.redis_enabled = False
        self.mongodb_enabled = False
        self.postgresql_enabled = False
        
        # BabaGAVAT'ın coin fiyat listesi (sokak değerleri)
        self.coin_prices = {
            "message_to_performer": 5,      # Şovcuya mesaj: 5 coin
            "vip_content_view": 10,         # VIP içerik: 10 coin
            "vip_group_monthly": 100,       # VIP grup aylık: 100 coin
            "special_show_request": 50,     # Özel şov talebi: 50 coin
        }
        
        # BabaGAVAT'ın kazanç sistemi
        self.earning_rates = {
            "referral_bonus": 20,           # Referans bonusu: 20 coin
            "daily_task": 5,                # Günlük görev: 5 coin
            "message_reward": 1,            # Mesaj ödülü: 1 coin
            "group_join": 10,               # Grup katılım: 10 coin
            "content_share": 3,             # İçerik paylaşım: 3 coin
        }
        
        # BabaGAVAT'ın günlük limitler (sokak kuralları)
        self.daily_limits = {
            "max_earn_per_day": 100,        # Günlük max kazanç: 100 coin
            "max_spend_per_day": 500,       # Günlük max harcama: 500 coin
            "max_message_per_day": 20,      # Günlük max mesaj: 20 adet
        }
        
        logger.info("💪 BabaGAVAT Coin Service başlatıldı - Sokak ekonomisi aktif!")
    
    async def initialize(self) -> None:
        """BabaGAVAT Coin Service'i başlat"""
        try:
            # Redis Manager'ı başlat
            await babagavat_redis_manager.initialize()
            self.redis_enabled = babagavat_redis_manager.is_initialized
            
            # MongoDB Manager'ı başlat
            await babagavat_mongo_manager.initialize()
            self.mongodb_enabled = babagavat_mongo_manager.is_initialized
            
            # PostgreSQL Manager'ı başlat (production primary)
            await babagavat_postgresql_manager.initialize()
            self.postgresql_enabled = babagavat_postgresql_manager.is_initialized
            
            # SQLite Database Manager'ı başlat (fallback)
            await database_manager.initialize()
            
            # Database tabloları oluştur (SQLite fallback için)
            await self._create_coin_tables()
            
            self.is_initialized = True
            
            logger.info("💪 BabaGAVAT Coin Service başlatıldı - Sokak ekonomisi aktif!")
            logger.info(f"🔥 Redis: {'✅ AKTİF' if self.redis_enabled else '❌ PASİF'}")
            logger.info(f"🔥 MongoDB: {'✅ AKTİF' if self.mongodb_enabled else '❌ PASİF'}")
            logger.info(f"🔥 PostgreSQL: {'✅ AKTİF' if self.postgresql_enabled else '❌ PASİF'}")
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Coin Service başlatma hatası: {e}")
            raise
    
    async def _create_coin_tables(self) -> None:
        """BabaGAVAT coin tablolarını oluştur"""
        try:
            async with database_manager._get_connection() as db:
                # Coin Balances tablosu
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_coin_balances (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER UNIQUE NOT NULL,
                        balance INTEGER DEFAULT 0,
                        total_earned INTEGER DEFAULT 0,
                        total_spent INTEGER DEFAULT 0,
                        user_type TEXT DEFAULT 'male',
                        babagavat_tier TEXT DEFAULT 'bronze', -- bronze, silver, gold, platinum
                        daily_earn_count INTEGER DEFAULT 0,
                        daily_spend_count INTEGER DEFAULT 0,
                        last_daily_reset DATE DEFAULT CURRENT_DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Coin Transactions tablosu
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_coin_transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        amount INTEGER NOT NULL,
                        transaction_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        related_user_id INTEGER,
                        metadata TEXT, -- JSON
                        babagavat_approval BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Coin Prices tablosu (dinamik fiyatlar)
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_coin_prices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_type TEXT UNIQUE NOT NULL,
                        price INTEGER NOT NULL,
                        description TEXT,
                        is_active BOOLEAN DEFAULT TRUE,
                        babagavat_notes TEXT DEFAULT '',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Daily Limits tablosu
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_daily_limits (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        limit_date DATE NOT NULL,
                        earned_today INTEGER DEFAULT 0,
                        spent_today INTEGER DEFAULT 0,
                        messages_sent_today INTEGER DEFAULT 0,
                        babagavat_warnings INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, limit_date)
                    )
                """)
                
                # Coin Leaderboard tablosu
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_coin_leaderboard (
                        user_id INTEGER PRIMARY KEY,
                        balance REAL DEFAULT 0.0,
                        tier TEXT DEFAULT 'bronze',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Indexes oluştur
                await db.execute("CREATE INDEX IF NOT EXISTS idx_coin_transactions_user_id ON babagavat_coin_transactions(user_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_coin_transactions_type ON babagavat_coin_transactions(transaction_type)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_daily_limits_user_date ON babagavat_daily_limits(user_id, limit_date)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_leaderboard_balance ON babagavat_coin_leaderboard(balance DESC)")
                
                await db.commit()
                logger.info("✅ BabaGAVAT coin tabloları oluşturuldu - Sokak ekonomisi hazır! 💰")
                
        except Exception as e:
            logger.error(f"❌ BabaGAVAT coin tablo oluşturma hatası: {e}")
            raise
    
    async def get_balance(self, user_id: int) -> int:
        """Kullanıcının coin bakiyesini getir - Redis → PostgreSQL → MongoDB → SQLite cascade"""
        try:
            # 1. Önce Redis cache'ten dene
            if self.redis_enabled:
                cached_balance = await babagavat_redis_manager.get_coin_balance(user_id)
                if cached_balance is not None:
                    return cached_balance
            
            # 2. PostgreSQL'den dene (production primary)
            if self.postgresql_enabled:
                postgresql_balance = await babagavat_postgresql_manager.get_coin_balance(user_id)
                if postgresql_balance > 0:
                    # Redis'e cache'le
                    if self.redis_enabled:
                        await babagavat_redis_manager.set_coin_balance(user_id, postgresql_balance)
                    return postgresql_balance
            
            # 3. MongoDB'den dene
            if self.mongodb_enabled:
                mongo_balance = await babagavat_mongo_manager.get_coin_balance(user_id)
                if mongo_balance > 0:
                    # Redis'e cache'le
                    if self.redis_enabled:
                        await babagavat_redis_manager.set_coin_balance(user_id, mongo_balance)
                    return mongo_balance
            
            # 4. SQLite fallback
            async with database_manager._get_connection() as db:
                cursor = await db.execute(
                    "SELECT balance FROM babagavat_coin_balances WHERE user_id = ?",
                    (user_id,)
                )
                result = await cursor.fetchone()
                
                balance = result[0] if result else 0
                
                # Redis'e cache'le
                if balance > 0 and self.redis_enabled:
                    await babagavat_redis_manager.set_coin_balance(user_id, balance)
                
                logger.info(f"💰 BabaGAVAT bakiye sorgusu: user_id={user_id}, balance={balance}")
                return balance
                
        except Exception as e:
            logger.warning(f"⚠️ BabaGAVAT bakiye sorgu hatası: {e}")
            return 0
    
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Kullanıcının detaylı coin istatistikleri - BabaGAVAT analizi"""
        try:
            async with database_manager._get_connection() as db:
                cursor = await db.execute("""
                    SELECT balance, total_earned, total_spent, user_type, babagavat_tier,
                           daily_earn_count, daily_spend_count, last_daily_reset
                    FROM babagavat_coin_balances WHERE user_id = ?
                """, (user_id,))
                result = await cursor.fetchone()
                
                if not result:
                    return {
                        "balance": 0,
                        "total_earned": 0,
                        "total_spent": 0,
                        "user_type": "male",
                        "babagavat_tier": "bronze",
                        "daily_stats": {"earned": 0, "spent": 0},
                        "babagavat_status": "yeni_kullanici"
                    }
                
                balance, total_earned, total_spent, user_type, tier, daily_earn, daily_spend, last_reset = result
                
                # BabaGAVAT'ın kullanıcı değerlendirmesi
                babagavat_status = await self._get_babagavat_user_status(
                    balance, total_earned, total_spent, user_type
                )
                
                return {
                    "balance": balance,
                    "total_earned": total_earned,
                    "total_spent": total_spent,
                    "user_type": user_type,
                    "babagavat_tier": tier,
                    "daily_stats": {
                        "earned": daily_earn,
                        "spent": daily_spend,
                        "last_reset": last_reset
                    },
                    "babagavat_status": babagavat_status
                }
                
        except Exception as e:
            logger.error(f"❌ BabaGAVAT kullanıcı stats hatası: {e}")
            return {"error": str(e)}
    
    async def _get_babagavat_user_status(self, balance: int, total_earned: int, 
                                       total_spent: int, user_type: str) -> str:
        """BabaGAVAT'ın kullanıcı durumu değerlendirmesi"""
        try:
            # BabaGAVAT'ın sokak zekası ile kullanıcı analizi
            if total_spent > total_earned * 2:
                return "buyuk_musteri"  # Çok harcayan
            elif total_earned > 500 and total_spent < 100:
                return "coin_biriktiren"  # Biriktiren tip
            elif balance > 1000:
                return "zengin_kullanici"  # Zengin
            elif total_spent > 1000:
                return "sadik_musteri"  # Sadık müşteri
            elif user_type == "performer":
                return "sovcu_hesabi"  # Şovcu
            elif total_earned < 50 and total_spent < 10:
                return "yeni_kullanici"  # Yeni
            else:
                return "normal_kullanici"  # Normal
                
        except Exception as e:
            logger.warning(f"⚠️ BabaGAVAT user status değerlendirme hatası: {e}")
            return "bilinmeyen"
    
    async def add_coins(self, user_id: int, amount: int, transaction_type: CoinTransactionType,
                       description: str, related_user_id: Optional[int] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Kullanıcıya coin ekle - Redis → PostgreSQL → MongoDB → SQLite cascade"""
        try:
            if amount <= 0:
                logger.warning(f"⚠️ Geçersiz coin miktarı: {amount}")
                return False
            
            # FIX: Handle string transaction type input
            if isinstance(transaction_type, str):
                # Convert string to enum if needed
                try:
                    transaction_type = CoinTransactionType(transaction_type)
                except ValueError:
                    transaction_type = CoinTransactionType.EARN_ADMIN  # Default fallback
            
            # Günlük limitleri kontrol et
            limit_check = await self._check_daily_earn_limit(user_id, amount)
            if not limit_check:
                logger.warning(f"⚠️ BabaGAVAT günlük kazanç limiti aşıldı: user_id={user_id}")
                return False
            
            # Mevcut bakiyeyi al
            current_balance = await self.get_balance(user_id)
            new_balance = current_balance + amount
            
            # Tier hesapla
            tier = await self._get_babagavat_user_status(
                new_balance, 0, 0, "male"
            )
            
            # Transaction record et - PostgreSQL primary
            if self.postgresql_enabled:
                await babagavat_postgresql_manager.add_coin_transaction(
                    user_id, amount, transaction_type.value, description, related_user_id, metadata
                )
                await babagavat_postgresql_manager.set_coin_balance(user_id, new_balance, tier)
            
            # MongoDB sync
            if self.mongodb_enabled:
                await babagavat_mongo_manager.add_coin_transaction(user_id, amount, transaction_type.value, description)
                await babagavat_mongo_manager.set_coin_balance(user_id, new_balance, tier)
            
            # SQLite fallback (non-blocking)
            try:
                async with database_manager._get_connection() as db:
                    # Balance güncelle
                    await db.execute("""
                        INSERT OR REPLACE INTO babagavat_coin_balances 
                        (user_id, balance, total_earned, total_spent, babagavat_tier, updated_at) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (user_id, new_balance, amount, 0, tier, datetime.now()))
                    
                    # Transaction kaydet
                    await db.execute("""
                        INSERT INTO babagavat_coin_transactions 
                        (user_id, amount, transaction_type, description, related_user_id, metadata)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        user_id, amount, transaction_type.value, description,
                        related_user_id, json.dumps(metadata) if metadata else None
                    ))
                    
                    # Leaderboard güncelle
                    await db.execute("""
                        INSERT OR REPLACE INTO babagavat_coin_leaderboard 
                        (user_id, balance, tier, updated_at) 
                        VALUES (?, ?, ?, ?)
                    """, (user_id, new_balance, tier, datetime.now()))
                    
                    await db.commit()
            except Exception as sqlite_error:
                logger.warning(f"⚠️ SQLite sync hatası: {sqlite_error}")
            
            # Redis cache'i güncelle
            if self.redis_enabled:
                await babagavat_redis_manager.set_coin_balance(user_id, new_balance)
                await babagavat_redis_manager.invalidate_coin_balance(user_id)  # Force refresh
            
            # Günlük limitleri güncelle
            await self._update_daily_limits(user_id, "earn", amount)
            
            logger.info(f"💰 BabaGAVAT coin eklendi: user_id={user_id}, amount={amount}, type={transaction_type.value}")
            
            # BabaGAVAT'ın tier kontrolü
            await self._check_and_update_tier(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT coin ekleme hatası: {e}")
            return False
    
    async def spend_coins(self, user_id: int, amount: int, transaction_type: CoinTransactionType,
                         description: str, related_user_id: Optional[int] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Coin harca - Redis cache invalidation + MongoDB/SQLite update"""
        try:
            if amount <= 0:
                logger.warning(f"⚠️ Geçersiz coin miktarı: {amount}")
                return False
            
            # Mevcut bakiyeyi kontrol et
            current_balance = await self.get_balance(user_id)
            if current_balance < amount:
                logger.warning(f"⚠️ BabaGAVAT yetersiz bakiye: user_id={user_id}, balance={current_balance}, required={amount}")
                return False
            
            # Günlük limitleri kontrol et
            limit_check = await self._check_daily_spend_limit(user_id, amount)
            if not limit_check:
                logger.warning(f"⚠️ BabaGAVAT günlük harcama limiti aşıldı: user_id={user_id}")
                return False
            
            new_balance = current_balance - amount
            
            # Transaction record et
            if self.mongodb_enabled:
                await babagavat_mongo_manager.add_coin_transaction(user_id, -amount, transaction_type.value, description)
            
            # MongoDB'ye balance kaydet
            if self.mongodb_enabled:
                tier = await self._get_babagavat_user_status(
                    new_balance, 0, 0, "male"
                )
                await babagavat_mongo_manager.set_coin_balance(user_id, new_balance, tier)
            
            # SQLite'ye kaydet
            async with database_manager._get_connection() as db:
                # Balance güncelle
                await db.execute("""
                    INSERT OR REPLACE INTO babagavat_coin_balances 
                    (user_id, balance, total_spent, daily_spend_count, updated_at) 
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, new_balance, amount, 1, datetime.now()))
                
                # Transaction kaydet
                await db.execute("""
                    INSERT INTO babagavat_coin_transactions 
                    (user_id, amount, transaction_type, description, related_user_id, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_id, -amount, transaction_type.value, description,
                    related_user_id, json.dumps(metadata) if metadata else None
                ))
                
                # Leaderboard güncelle
                await db.execute("""
                    INSERT OR REPLACE INTO babagavat_coin_leaderboard 
                    (user_id, balance, tier, updated_at) 
                    VALUES (?, ?, ?, ?)
                """, (user_id, new_balance, tier, datetime.now()))
                
                await db.commit()
            
            # Redis cache'i invalidate et
            if self.redis_enabled:
                await babagavat_redis_manager.invalidate_coin_balance(user_id)
                await babagavat_redis_manager.set_coin_balance(user_id, new_balance)
            
            # Günlük limitleri güncelle
            await self._update_daily_limits(user_id, "spend", amount)
            
            logger.info(f"💸 BabaGAVAT coin harcandı: user_id={user_id}, amount={amount}, type={transaction_type.value}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT coin harcama hatası: {e}")
            return False
    
    async def _check_daily_earn_limit(self, user_id: int, amount: int) -> bool:
        """BabaGAVAT günlük kazanç limit kontrolü"""
        try:
            today = datetime.now().date()
            async with database_manager._get_connection() as db:
                cursor = await db.execute("""
                    SELECT earned_today FROM babagavat_daily_limits 
                    WHERE user_id = ? AND limit_date = ?
                """, (user_id, today))
                result = await cursor.fetchone()
                
                earned_today = result[0] if result else 0
                return (earned_today + amount) <= self.daily_limits["max_earn_per_day"]
                
        except Exception as e:
            logger.warning(f"⚠️ BabaGAVAT günlük kazanç limit kontrolü hatası: {e}")
            return True  # Hata durumunda izin ver
    
    async def _check_daily_spend_limit(self, user_id: int, amount: int) -> bool:
        """BabaGAVAT günlük harcama limit kontrolü"""
        try:
            today = datetime.now().date()
            async with database_manager._get_connection() as db:
                cursor = await db.execute("""
                    SELECT spent_today FROM babagavat_daily_limits 
                    WHERE user_id = ? AND limit_date = ?
                """, (user_id, today))
                result = await cursor.fetchone()
                
                spent_today = result[0] if result else 0
                return (spent_today + amount) <= self.daily_limits["max_spend_per_day"]
                
        except Exception as e:
            logger.warning(f"⚠️ BabaGAVAT günlük harcama limit kontrolü hatası: {e}")
            return True  # Hata durumunda izin ver
    
    async def _update_daily_limits(self, user_id: int, limit_type: str, amount: int) -> None:
        """BabaGAVAT günlük limit kayıtlarını güncelle"""
        try:
            today = datetime.now().date()
            async with database_manager._get_connection() as db:
                await db.execute("""
                    INSERT INTO babagavat_daily_limits (user_id, limit_date, earned_today, spent_today)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id, limit_date) DO UPDATE SET
                        earned_today = earned_today + ?,
                        spent_today = spent_today + ?
                """, (user_id, today, amount, 0, amount, 0))
                
        except Exception as e:
            logger.warning(f"⚠️ BabaGAVAT günlük limit güncelleme hatası: {e}")
    
    async def _check_and_update_tier(self, user_id: int) -> None:
        """BabaGAVAT tier kontrolü ve güncelleme"""
        try:
            stats = await self.get_user_stats(user_id)
            total_earned = stats.get("total_earned", 0)
            
            # BabaGAVAT'ın tier sistemi
            new_tier = "bronze"
            if total_earned >= 5000:
                new_tier = "platinum"
            elif total_earned >= 2000:
                new_tier = "gold"
            elif total_earned >= 500:
                new_tier = "silver"
            
            async with database_manager._get_connection() as db:
                await db.execute("""
                    UPDATE babagavat_coin_balances 
                    SET babagavat_tier = ? 
                    WHERE user_id = ?
                """, (new_tier, user_id))
                
                logger.info(f"🏆 BabaGAVAT tier güncellendi: user_id={user_id}, tier={new_tier}")
                
        except Exception as e:
            logger.warning(f"⚠️ BabaGAVAT tier güncelleme hatası: {e}")
    
    # ==================== BABAGAVAT ÖZEL METODLAR ====================
    
    async def babagavat_referral_bonus(self, referrer_id: int, referred_id: int) -> bool:
        """BabaGAVAT referans bonusu sistemi"""
        try:
            bonus_amount = self.earning_rates["referral_bonus"]
            
            success = await self.add_coins(
                user_id=referrer_id,
                amount=bonus_amount,
                transaction_type=CoinTransactionType.EARN_REFERRAL,
                description=f"BabaGAVAT referans bonusu - Davet edilen: {referred_id}",
                related_user_id=referred_id,
                metadata={"referral_bonus": True, "babagavat_approved": True}
            )
            
            if success:
                logger.info(f"💪 BabaGAVAT referans bonusu verildi: referrer={referrer_id}, referred={referred_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT referans bonusu hatası: {e}")
            return False
    
    async def babagavat_message_to_performer(self, user_id: int, performer_id: int, 
                                           message_content: str) -> bool:
        """BabaGAVAT şovcuya mesaj gönderme sistemi"""
        try:
            cost = self.coin_prices["message_to_performer"]
            
            success = await self.spend_coins(
                user_id=user_id,
                amount=cost,
                transaction_type=CoinTransactionType.SPEND_MESSAGE,
                description=f"BabaGAVAT şovcuya mesaj - Performer: {performer_id}",
                related_user_id=performer_id,
                metadata={
                    "message_preview": message_content[:50],
                    "babagavat_approved": True
                }
            )
            
            if success:
                logger.info(f"💌 BabaGAVAT şovcuya mesaj gönderildi: user={user_id}, performer={performer_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT şovcuya mesaj hatası: {e}")
            return False
    
    async def babagavat_daily_task_reward(self, user_id: int, task_type: str) -> bool:
        """BabaGAVAT günlük görev ödül sistemi"""
        try:
            reward_amount = self.earning_rates["daily_task"]
            
            success = await self.add_coins(
                user_id=user_id,
                amount=reward_amount,
                transaction_type=CoinTransactionType.EARN_TASK,
                description=f"BabaGAVAT günlük görev tamamlandı - {task_type}",
                metadata={"task_type": task_type, "babagavat_approved": True}
            )
            
            if success:
                logger.info(f"🎯 BabaGAVAT günlük görev ödülü: user={user_id}, task={task_type}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT günlük görev ödül hatası: {e}")
            return False
    
    async def babagavat_admin_add_coins(self, admin_id: int, target_user_id: int, 
                                      amount: int, reason: str) -> bool:
        """BabaGAVAT admin coin ekleme sistemi"""
        try:
            success = await self.add_coins(
                user_id=target_user_id,
                amount=amount,
                transaction_type=CoinTransactionType.EARN_ADMIN,
                description=f"BabaGAVAT Admin ödülü - {reason}",
                related_user_id=admin_id,
                metadata={"admin_action": True, "admin_id": admin_id, "reason": reason}
            )
            
            if success:
                logger.info(f"👑 BabaGAVAT admin coin ekledi: admin={admin_id}, user={target_user_id}, amount={amount}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT admin coin ekleme hatası: {e}")
            return False
    
    async def get_babagavat_transaction_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """BabaGAVAT işlem geçmişi"""
        try:
            async with database_manager._get_connection() as db:
                cursor = await db.execute("""
                    SELECT amount, transaction_type, description, related_user_id, 
                           metadata, created_at
                    FROM babagavat_coin_transactions 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (user_id, limit))
                
                transactions = []
                async for row in cursor:
                    amount, tx_type, description, related_user, metadata, created_at = row
                    
                    transactions.append({
                        "amount": amount,
                        "type": tx_type,
                        "description": description,
                        "related_user_id": related_user,
                        "metadata": json.loads(metadata) if metadata else {},
                        "created_at": created_at,
                        "babagavat_verified": True
                    })
                
                return transactions
                
        except Exception as e:
            logger.error(f"❌ BabaGAVAT işlem geçmişi hatası: {e}")
            return []
    
    async def get_babagavat_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """BabaGAVAT Leaderboard - Redis cache first"""
        try:
            # Redis cache'ten dene
            if self.redis_enabled:
                cached_leaderboard = await babagavat_redis_manager.get_leaderboard(limit)
                if cached_leaderboard:
                    return cached_leaderboard
            
            # MongoDB'den al
            if self.mongodb_enabled:
                mongo_leaderboard = await babagavat_mongo_manager.get_leaderboard(limit)
                if mongo_leaderboard:
                    # Redis'e cache'le
                    if self.redis_enabled:
                        await babagavat_redis_manager.set_leaderboard(mongo_leaderboard, limit)
                    return mongo_leaderboard
            
            # SQLite fallback
            async with database_manager._get_connection() as db:
                cursor = await db.execute("""
                    SELECT user_id, balance, tier 
                    FROM babagavat_coin_leaderboard 
                    ORDER BY balance DESC 
                    LIMIT ?
                """, (limit,))
                
                rows = await cursor.fetchall()
                
                leaderboard = []
                for row in rows:
                    entry = {
                        "user_id": row[0],
                        "balance": row[1],
                        "tier": row[2]
                    }
                    leaderboard.append(entry)
                
                # Cache'le
                if self.redis_enabled and leaderboard:
                    await babagavat_redis_manager.set_leaderboard(leaderboard, limit)
                
                return leaderboard
                
        except Exception as e:
            logger.warning(f"⚠️ Leaderboard sorgu hatası: {e}")
            return []

    async def _get_user_tier(self, balance: float) -> str:
        """Kullanıcı tier'ını hesapla"""
        if balance >= 10000:
            return "platinum"
        elif balance >= 5000:
            return "gold"
        elif balance >= 1000:
            return "silver"
        else:
            return "bronze"
    
    async def _update_user_tier(self, user_id: int, balance: float) -> None:
        """Kullanıcı tier'ını güncelle"""
        tier = await self._get_user_tier(balance)
        logger.info(f"🏆 BabaGAVAT tier güncellendi: user_id={user_id}, tier={tier}")

# Global instance
babagavat_coin_service = BabaGAVATCoinService() 