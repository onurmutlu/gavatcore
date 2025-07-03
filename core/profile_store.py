#!/usr/bin/env python3
# core/profile_store.py - MongoDB Async Profile Store

import os
import asyncio
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

# Global MongoDB client ve database
# Type: Optional[AsyncIOMotorClient]
mongo_client = None
# Type: Optional[AsyncIOMotorDatabase] 
mongo_db = None

async def init_profile_store():
    """MongoDB bağlantısını başlat"""
    global mongo_client, mongo_db
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB", "gavatcore")
        
        # File-based fallback için kontrol
        if mongodb_uri.startswith("file://"):
            print("⚠️ File-based profil storage kullanılıyor (development mode)")
            # Dizini oluştur
            profile_dir = mongodb_uri.replace("file://", "")
            os.makedirs(profile_dir, exist_ok=True)
            print("✅ File-based profil storage başarılı")
            return True
        
        mongo_client = AsyncIOMotorClient(mongodb_uri)
        mongo_db = mongo_client[db_name]
        
        # Bağlantıyı test et
        await mongo_client.admin.command('ping')
        
        # Index'leri oluştur
        await create_indexes()
        
        print("✅ MongoDB bağlantısı başarılı")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB bağlantı hatası: {e}")
        print("⚠️ File-based fallback kullanılıyor...")
        # File-based fallback
        profile_dir = "./data/profiles"
        os.makedirs(profile_dir, exist_ok=True)
        print("✅ File-based profil storage başarılı")
        return True

async def create_indexes():
    """MongoDB index'lerini oluştur"""
    try:
        if mongo_db is None:
            return
            
        profiles_collection = mongo_db.profiles
        
        # Username index (unique)
        await profiles_collection.create_index("username", unique=True)
        
        # User ID index
        await profiles_collection.create_index("user_id")
        
        # Type index (bot, user, admin)
        await profiles_collection.create_index("type")
        
        # Created at index
        await profiles_collection.create_index("created_at")
        
        # Compound index for active bots
        await profiles_collection.create_index([
            ("type", 1),
            ("autospam", 1),
            ("is_active", 1)
        ])
        
        print("✅ MongoDB index'leri oluşturuldu")
        
    except Exception as e:
        print(f"❌ MongoDB index hatası: {e}")

async def close_profile_store():
    """MongoDB bağlantısını kapat"""
    global mongo_client
    if mongo_client is not None:
        mongo_client.close()
        print("✅ MongoDB bağlantısı kapatıldı")

# ==================== PROFILE OPERATIONS ====================

async def get_profile_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Username ile profil getir"""
    try:
        if mongo_db is None:
            await init_profile_store()
        
        # File-based fallback
        if mongo_db is None:
            return await _get_profile_from_file(username)
        
        collection = mongo_db.profiles
        profile = await collection.find_one({"username": username})
        
        if profile:
            # MongoDB ObjectId'yi string'e çevir
            profile["_id"] = str(profile["_id"])
        
        return profile
        
    except Exception as e:
        print(f"❌ Profil getirme hatası ({username}): {e}")
        # File-based fallback
        return await _get_profile_from_file(username)

async def get_profile_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    """User ID ile profil getir"""
    try:
        if mongo_db is None:
            await init_profile_store()
        
        if mongo_db is None:
            return None
            
        collection = mongo_db.profiles
        profile = await collection.find_one({"user_id": str(user_id)})
        
        if profile:
            profile["_id"] = str(profile["_id"])
        
        return profile
        
    except Exception as e:
        print(f"❌ Profil getirme hatası (user_id: {user_id}): {e}")
        return None

async def create_or_update_profile(username: str, data: Dict[str, Any]) -> bool:
    """Profil oluştur veya güncelle"""
    try:
        if mongo_db is None:
            await init_profile_store()
        
        # File-based fallback
        if mongo_db is None:
            return await _save_profile_to_file(username, data)
        
        collection = mongo_db.profiles
        
        # Timestamp ekle
        data["updated_at"] = datetime.utcnow()
        
        # Eğer yeni profil ise created_at ekle
        existing = await collection.find_one({"username": username})
        if not existing:
            data["created_at"] = datetime.utcnow()
            data["username"] = username
        
        # Upsert (update or insert)
        result = await collection.replace_one(
            {"username": username},
            data,
            upsert=True
        )
        
        return result.acknowledged
        
    except Exception as e:
        print(f"❌ Profil kaydetme hatası ({username}): {e}")
        # File-based fallback
        return await _save_profile_to_file(username, data)

async def update_profile_field(username: str, field: str, value: Any) -> bool:
    """Profilde tek alan güncelle"""
    try:
        if mongo_db is None:
            await init_profile_store()
        
        collection = mongo_db.profiles
        
        result = await collection.update_one(
            {"username": username},
            {
                "$set": {
                    field: value,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
        
    except Exception as e:
        print(f"❌ Profil alan güncelleme hatası ({username}.{field}): {e}")
        return False

async def update_profile_fields(username: str, fields: Dict[str, Any]) -> bool:
    """Profilde birden fazla alan güncelle"""
    try:
        if mongo_db is None:
            await init_profile_store()
        
        collection = mongo_db.profiles
        
        # Updated timestamp ekle
        fields["updated_at"] = datetime.utcnow()
        
        result = await collection.update_one(
            {"username": username},
            {"$set": fields}
        )
        
        return result.modified_count > 0
        
    except Exception as e:
        print(f"❌ Profil alanları güncelleme hatası ({username}): {e}")
        return False

async def delete_profile(username: str) -> bool:
    """Profil sil"""
    try:
        if mongo_db is None:
            await init_profile_store()
        
        collection = mongo_db.profiles
        result = await collection.delete_one({"username": username})
        
        return result.deleted_count > 0
        
    except Exception as e:
        print(f"❌ Profil silme hatası ({username}): {e}")
        return False

# ==================== BULK OPERATIONS ====================

async def get_all_profiles(profile_type: str = None, 
                          is_active: bool = None) -> List[Dict[str, Any]]:
    """Tüm profilleri getir"""
    try:
        if mongo_db is None:
            await init_profile_store()
        
        collection = mongo_db.profiles
        
        # Filter oluştur
        filter_query = {}
        if profile_type:
            filter_query["type"] = profile_type
        if is_active is not None:
            filter_query["is_active"] = is_active
        
        cursor = collection.find(filter_query)
        profiles = []
        
        async for profile in cursor:
            profile["_id"] = str(profile["_id"])
            profiles.append(profile)
        
        return profiles
        
    except Exception as e:
        print(f"❌ Tüm profiller getirme hatası: {e}")
        return []

async def get_bot_profiles(autospam_only: bool = False) -> List[Dict[str, Any]]:
    """Bot profillerini getir"""
    try:
        filter_query = {"type": "bot"}
        
        if autospam_only:
            filter_query["autospam"] = True
        
        return await get_all_profiles()
        
    except Exception as e:
        print(f"❌ Bot profilleri getirme hatası: {e}")
        return []

async def search_profiles(keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Profillerde arama yap"""
    try:
        if mongo_db is None:
            await init_profile_store()
        
        collection = mongo_db.profiles
        
        # Text search
        cursor = collection.find({
            "$or": [
                {"username": {"$regex": keyword, "$options": "i"}},
                {"display_name": {"$regex": keyword, "$options": "i"}},
                {"telegram_handle": {"$regex": keyword, "$options": "i"}}
            ]
        }).limit(limit)
        
        profiles = []
        async for profile in cursor:
            profile["_id"] = str(profile["_id"])
            profiles.append(profile)
        
        return profiles
        
    except Exception as e:
        print(f"❌ Profil arama hatası: {e}")
        return []

# ==================== STATISTICS ====================

async def get_profile_stats() -> Dict[str, Any]:
    """Profil istatistikleri getir"""
    try:
        if mongo_db is None:
            await init_profile_store()
        
        collection = mongo_db.profiles
        
        # Aggregation pipeline
        pipeline = [
            {
                "$group": {
                    "_id": "$type",
                    "count": {"$sum": 1},
                    "active_count": {
                        "$sum": {
                            "$cond": [{"$eq": ["$is_active", True]}, 1, 0]
                        }
                    },
                    "autospam_count": {
                        "$sum": {
                            "$cond": [{"$eq": ["$autospam", True]}, 1, 0]
                        }
                    }
                }
            }
        ]
        
        cursor = collection.aggregate(pipeline)
        stats = {"by_type": {}, "total": 0}
        
        async for result in cursor:
            profile_type = result["_id"] or "unknown"
            stats["by_type"][profile_type] = {
                "total": result["count"],
                "active": result["active_count"],
                "autospam": result["autospam_count"]
            }
            stats["total"] += result["count"]
        
        return stats
        
    except Exception as e:
        print(f"❌ Profil istatistik hatası: {e}")
        return {}

# ==================== MIGRATION HELPERS ====================

async def migrate_from_json_files(json_dir: str = "data/personas") -> int:
    """JSON dosyalarından MongoDB'ye migration"""
    try:
        import json
        import os
        from pathlib import Path
        
        migrated_count = 0
        json_path = Path(json_dir)
        
        if not json_path.exists():
            print(f"❌ JSON dizini bulunamadı: {json_dir}")
            return 0
        
        for json_file in json_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                
                username = json_file.stem  # Dosya adından username
                
                # MongoDB'ye kaydet
                success = await create_or_update_profile(username, profile_data)
                if success:
                    migrated_count += 1
                    print(f"✅ Migrated: {username}")
                else:
                    print(f"❌ Migration failed: {username}")
                    
            except Exception as e:
                print(f"❌ JSON okuma hatası ({json_file}): {e}")
        
        print(f"🎉 Migration tamamlandı: {migrated_count} profil")
        return migrated_count
        
    except Exception as e:
        print(f"❌ Migration hatası: {e}")
        return 0

# ==================== FILE-BASED FALLBACK ====================

async def _get_profile_from_file(username: str) -> Optional[Dict[str, Any]]:
    """File'dan profil getir"""
    try:
        import json
        from pathlib import Path
        
        profile_file = Path(f"./data/profiles/{username}.json")
        if profile_file.exists():
            with open(profile_file, 'r', encoding='utf-8') as f:
                profile = json.load(f)
                profile["_id"] = username  # Fake ID
                return profile
        return None
    except Exception as e:
        print(f"❌ File profil okuma hatası ({username}): {e}")
        return None

async def _save_profile_to_file(username: str, data: Dict[str, Any]) -> bool:
    """File'a profil kaydet"""
    try:
        import json
        from pathlib import Path
        
        profile_dir = Path("./data/profiles")
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        profile_file = profile_dir / f"{username}.json"
        data["updated_at"] = datetime.utcnow().isoformat()
        
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"❌ File profil kaydetme hatası ({username}): {e}")
        return False

def init_mongodb():
    """MongoDB bağlantısını başlatır."""
    try:
        # MongoDB bağlantı ayarları
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017/")
        db = client["gavatcore"]
        return db
    except Exception as e:
        print(f"MongoDB başlatma hatası: {e}")
        return None

def close_mongodb():
    """MongoDB bağlantısını kapatır."""
    try:
        # MongoDB bağlantısını kapat
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017/")
        client.close()
    except Exception as e:
        print(f"MongoDB kapatma hatası: {e}") 