from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
BabaGAVAT MongoDB Manager
Onur Metodu ile MongoDB Async Database Operations
BabaGAVAT'ın sokak zekası ile NoSQL kullanımı
"""

import motor.motor_asyncio
import pymongo
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import structlog
import asyncio

logger = structlog.get_logger("babagavat.mongodb")

class BabaGAVATMongoManager:
    """BabaGAVAT MongoDB Manager - Sokak tecrübesi ile NoSQL yönetimi"""
    
    def __init__(self, mongo_url: str = "mongodb://localhost:27017", db_name: str = "babagavat_db"):
        self.mongo_url = mongo_url
        self.db_name = db_name
        self.client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None
        self.is_initialized = False
        
    async def initialize(self) -> None:
        """MongoDB bağlantısını başlat"""
        try:
            # Motor client oluştur
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                self.mongo_url,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=10
            )
            
            # Database seç
            self.db = self.client[self.db_name]
            
            # Bağlantı testi
            await self.client.admin.command('ping')
            self.is_initialized = True
            
            # Collections ve indexes oluştur
            await self._create_collections_and_indexes()
            
            logger.info("🔥 BabaGAVAT MongoDB Manager başlatıldı - Sokak NoSQL sistemi aktif!")
            
        except Exception as e:
            logger.error(f"❌ MongoDB bağlantı hatası: {e}")
            # Fallback: MongoDB yoksa SQLite devam etsin
            self.client = None
            self.db = None
            self.is_initialized = False
    
    async def close(self) -> None:
        """MongoDB bağlantısını kapat"""
        if self.client:
            self.client.close()
    
    async def _create_collections_and_indexes(self) -> None:
        """Collections ve indexes oluştur"""
        try:
            # Coin Balances Collection
            coin_balances = self.db.coin_balances
            await coin_balances.create_index("user_id", unique=True)
            await coin_balances.create_index("created_at")
            
            # Coin Transactions Collection
            coin_transactions = self.db.coin_transactions
            await coin_transactions.create_index("user_id")
            await coin_transactions.create_index("transaction_type")
            await coin_transactions.create_index("created_at")
            await coin_transactions.create_index([("user_id", 1), ("created_at", -1)])
            
            # Daily Limits Collection
            daily_limits = self.db.daily_limits
            await daily_limits.create_index([("user_id", 1), ("limit_date", 1)], unique=True)
            await daily_limits.create_index("limit_date")
            
            # ErkoAnalyzer Profiles Collection
            erko_profiles = self.db.erko_profiles
            await erko_profiles.create_index("user_id", unique=True)
            await erko_profiles.create_index("segment")
            await erko_profiles.create_index("risk_level")
            await erko_profiles.create_index("last_analyzed")
            
            # ErkoAnalyzer Activity Log Collection
            erko_activity = self.db.erko_activity
            await erko_activity.create_index("user_id")
            await erko_activity.create_index("activity_type")
            await erko_activity.create_index("created_at")
            await erko_activity.create_index([("user_id", 1), ("created_at", -1)])
            
            # Leaderboard Collection
            leaderboard = self.db.leaderboard
            await leaderboard.create_index("user_id", unique=True)
            await leaderboard.create_index([("balance", -1)])
            await leaderboard.create_index("tier")
            
            logger.info("✅ BabaGAVAT MongoDB collections ve indexes oluşturuldu")
            
        except Exception as e:
            logger.warning(f"⚠️ MongoDB collections/indexes oluşturma hatası: {e}")
    
    # COIN BALANCE OPERATIONS
    async def get_coin_balance(self, user_id: int) -> float:
        """Kullanıcı coin bakiyesini MongoDB'den al"""
        try:
            if self.db is None:
                return 0.0
                
            result = await self.db.coin_balances.find_one({"user_id": user_id})
            
            if result:
                logger.info(f"💰 BabaGAVAT MongoDB balance get: user_id={user_id}, balance={result['balance']}")
                return float(result["balance"])
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"⚠️ MongoDB balance get hatası: {e}")
            return 0.0
    
    async def set_coin_balance(self, user_id: int, balance: float, tier: str = "bronze") -> bool:
        """Kullanıcı coin bakiyesini MongoDB'ye kaydet"""
        try:
            if self.db is None:
                return False
                
            # Upsert operation
            await self.db.coin_balances.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "balance": float(balance),
                        "tier": tier,
                        "updated_at": datetime.now()
                    },
                    "$setOnInsert": {
                        "user_id": user_id,
                        "created_at": datetime.now()
                    }
                },
                upsert=True
            )
            
            # Leaderboard güncelle
            await self.db.leaderboard.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "balance": float(balance),
                        "tier": tier,
                        "updated_at": datetime.now()
                    },
                    "$setOnInsert": {
                        "user_id": user_id,
                        "created_at": datetime.now()
                    }
                },
                upsert=True
            )
            
            logger.info(f"💰 BabaGAVAT MongoDB balance set: user_id={user_id}, balance={balance}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ MongoDB balance set hatası: {e}")
            return False
    
    async def add_coin_transaction(self, user_id: int, amount: float, transaction_type: str, description: str = "") -> bool:
        """Coin transaction kaydet"""
        try:
            if self.db is None:
                return False
                
            transaction = {
                "user_id": user_id,
                "amount": float(amount),
                "transaction_type": transaction_type,
                "description": description,
                "created_at": datetime.now(),
                "babagavat_approved": True
            }
            
            await self.db.coin_transactions.insert_one(transaction)
            
            logger.info(f"💸 BabaGAVAT MongoDB transaction added: user_id={user_id}, amount={amount}, type={transaction_type}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ MongoDB transaction add hatası: {e}")
            return False
    
    async def get_coin_transactions(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Kullanıcı coin transaction geçmişini al"""
        try:
            if self.db is None:
                return []
                
            cursor = self.db.coin_transactions.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(limit)
            
            transactions = []
            async for transaction in cursor:
                # MongoDB ObjectId'yi string'e çevir
                transaction["_id"] = str(transaction["_id"])
                transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            logger.warning(f"⚠️ MongoDB transactions get hatası: {e}")
            return []
    
    # DAILY LIMITS OPERATIONS
    async def get_daily_limits(self, user_id: int, limit_date: str = None) -> Optional[Dict[str, Any]]:
        """Günlük limitler MongoDB'den al"""
        try:
            if self.db is None:
                return None
                
            if not limit_date:
                limit_date = datetime.now().strftime("%Y-%m-%d")
                
            result = await self.db.daily_limits.find_one({
                "user_id": user_id,
                "limit_date": limit_date
            })
            
            if result:
                result["_id"] = str(result["_id"])
                return result
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ MongoDB daily limits get hatası: {e}")
            return None
    
    async def set_daily_limits(self, user_id: int, earn_amount: float, spend_amount: float, limit_date: str = None) -> bool:
        """Günlük limitler MongoDB'ye kaydet"""
        try:
            if self.db is None:
                return False
                
            if not limit_date:
                limit_date = datetime.now().strftime("%Y-%m-%d")
                
            await self.db.daily_limits.update_one(
                {"user_id": user_id, "limit_date": limit_date},
                {
                    "$set": {
                        "daily_earn_amount": float(earn_amount),
                        "daily_spend_amount": float(spend_amount),
                        "updated_at": datetime.now()
                    },
                    "$setOnInsert": {
                        "user_id": user_id,
                        "limit_date": limit_date,
                        "created_at": datetime.now()
                    }
                },
                upsert=True
            )
            
            logger.info(f"📅 BabaGAVAT MongoDB daily limits set: user_id={user_id}, earn={earn_amount}, spend={spend_amount}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ MongoDB daily limits set hatası: {e}")
            return False
    
    # ERKO ANALYZER OPERATIONS
    async def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """ErkoAnalyzer kullanıcı profili MongoDB'den al"""
        try:
            if self.db is None:
                return None
                
            result = await self.db.erko_profiles.find_one({"user_id": user_id})
            
            if result:
                result["_id"] = str(result["_id"])
                return result
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ MongoDB user profile get hatası: {e}")
            return None
    
    async def set_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """ErkoAnalyzer kullanıcı profili MongoDB'ye kaydet"""
        try:
            if self.db is None:
                return False
                
            profile_data.update({
                "user_id": user_id,
                "last_analyzed": datetime.now(),
                "updated_at": datetime.now()
            })
            
            await self.db.erko_profiles.update_one(
                {"user_id": user_id},
                {
                    "$set": profile_data,
                    "$setOnInsert": {
                        "created_at": datetime.now()
                    }
                },
                upsert=True
            )
            
            logger.info(f"🔍 BabaGAVAT MongoDB user profile set: user_id={user_id}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ MongoDB user profile set hatası: {e}")
            return False
    
    async def add_user_activity(self, user_id: int, activity_type: str, activity_data: Dict[str, Any]) -> bool:
        """Kullanıcı aktivitesi kaydet"""
        try:
            if self.db is None:
                return False
                
            activity = {
                "user_id": user_id,
                "activity_type": activity_type,
                "activity_data": activity_data,
                "created_at": datetime.now(),
                "babagavat_tracking": True
            }
            
            await self.db.erko_activity.insert_one(activity)
            
            logger.info(f"📊 BabaGAVAT MongoDB user activity added: user_id={user_id}, type={activity_type}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ MongoDB user activity add hatası: {e}")
            return False
    
    # LEADERBOARD OPERATIONS
    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Leaderboard MongoDB'den al"""
        try:
            if self.db is None:
                return []
                
            cursor = self.db.leaderboard.find().sort("balance", -1).limit(limit)
            
            leaderboard = []
            async for entry in cursor:
                entry["_id"] = str(entry["_id"])
                leaderboard.append(entry)
            
            return leaderboard
            
        except Exception as e:
            logger.warning(f"⚠️ MongoDB leaderboard get hatası: {e}")
            return []
    
    # ANALYTICS OPERATIONS
    async def get_analytics_data(self, days: int = 7) -> Dict[str, Any]:
        """Analytics verilerini al"""
        try:
            if self.db is None:
                return {}
                
            # Son N günün verilerini al
            start_date = datetime.now() - timedelta(days=days)
            
            # Toplam kullanıcı sayısı
            total_users = await self.db.coin_balances.count_documents({})
            
            # Aktif kullanıcılar (son 7 günde transaction yapan)
            active_users = await self.db.coin_transactions.distinct(
                "user_id",
                {"created_at": {"$gte": start_date}}
            )
            
            # Toplam transaction sayısı
            total_transactions = await self.db.coin_transactions.count_documents(
                {"created_at": {"$gte": start_date}}
            )
            
            # Toplam coin hacmi
            pipeline = [
                {"$match": {"created_at": {"$gte": start_date}}},
                {"$group": {
                    "_id": None,
                    "total_volume": {"$sum": "$amount"}
                }}
            ]
            
            volume_result = await self.db.coin_transactions.aggregate(pipeline).to_list(1)
            total_volume = volume_result[0]["total_volume"] if volume_result else 0
            
            # Segment dağılımı
            segment_pipeline = [
                {"$group": {
                    "_id": "$segment",
                    "count": {"$sum": 1}
                }}
            ]
            
            segment_data = await self.db.erko_profiles.aggregate(segment_pipeline).to_list(None)
            segments = {item["_id"]: item["count"] for item in segment_data}
            
            return {
                "total_users": total_users,
                "active_users_count": len(active_users),
                "total_transactions": total_transactions,
                "total_coin_volume": total_volume,
                "segment_distribution": segments,
                "analysis_period_days": days,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"⚠️ MongoDB analytics get hatası: {e}")
            return {}
    
    async def get_db_stats(self) -> Dict[str, Any]:
        """Database istatistiklerini al"""
        try:
            if self.db is None:
                return {"status": "not_connected"}
                
            # Database stats
            stats = await self.db.command("dbStats")
            
            # Collection counts
            collections_stats = {}
            for collection_name in ["coin_balances", "coin_transactions", "daily_limits", "erko_profiles", "erko_activity", "leaderboard"]:
                count = await self.db[collection_name].count_documents({})
                collections_stats[collection_name] = count
            
            return {
                "status": "connected",
                "database_name": self.db_name,
                "collections": collections_stats,
                "storage_size": stats.get("storageSize", 0),
                "data_size": stats.get("dataSize", 0),
                "index_size": stats.get("indexSize", 0),
                "objects": stats.get("objects", 0),
                "babagavat_nosql_active": True
            }
            
        except Exception as e:
            logger.warning(f"⚠️ MongoDB stats get hatası: {e}")
            return {"status": "error", "error": str(e)}

# Global MongoDB Manager instance
babagavat_mongo_manager = BabaGAVATMongoManager() 