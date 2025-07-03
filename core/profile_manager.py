#!/usr/bin/env python3
# core/profile_manager.py - Profil Yönetim Sistemi

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import aiofiles
import structlog
from core.db.connection import get_db_session
from sqlalchemy import text
from sqlalchemy.sql import select
from core.db.models import Profile
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("gavatcore.profile_manager")

class ProfileManager:
    """Profil yöneticisi"""
    
    def __init__(self):
        self._profile_cache = {}
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Gerekli dizinleri oluştur"""
        os.makedirs("data/personas", exist_ok=True)
        
    async def get_profile(self, username: str) -> Optional[Dict]:
        """Profil bilgisini al"""
        try:
            # Önce cache'den kontrol et
            if username in self._profile_cache:
                return self._profile_cache[username]
            
            # JSON dosyasından oku
            json_path = f"data/personas/{username}.json"
            if os.path.exists(json_path):
                try:
                    async with aiofiles.open(json_path, 'r', encoding='utf-8') as f:
                        content = await f.read()
                        profile = json.loads(content)
                        self._profile_cache[username] = profile
                        return profile
                except Exception as e:
                    logger.error(f"JSON profil okuma hatası ({username}): {str(e)}")
            
            # DB'den oku
            try:
                from core.db.connection import get_session
                session = await get_session()
                async with session as db:
                    result = await db.execute(
                        select(Profile).where(Profile.username == username)
                    )
                    db_profile = result.scalar_one_or_none()
                    
                    if db_profile:
                        profile_data = db_profile.profile_data
                        self._profile_cache[username] = profile_data
                        return profile_data
                    
            except Exception as e:
                logger.error(f"DB profil okuma hatası ({username}): {str(e)}")
                    
            return None
            
        except Exception as e:
            logger.error(f"Profil okuma genel hatası ({username}): {str(e)}")
            return None
    
    async def save_profile(self, username: str, profile: Dict[str, Any]) -> bool:
        """Profil bilgisini kaydet"""
        try:
            # Timestamp ekle
            profile["updated_at"] = datetime.now().isoformat()
            if "created_at" not in profile or profile["created_at"] is None:
                profile["created_at"] = profile["updated_at"]
            
            # Dosyaya kaydet
            profile_path = os.path.join("data/personas", f"{username}.json")
            async with aiofiles.open(profile_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(profile, indent=2, ensure_ascii=False))
            
            # Cache'i güncelle
            self._profile_cache[username] = profile
            
            # Veritabanına kaydet
            try:
                async with get_db_session() as session:
                    # Mevcut profil var mı kontrol et
                    result = await session.execute(
                        text("SELECT id FROM profiles WHERE username = :username"),
                        {"username": username}
                    )
                    existing = result.first()
                    
                    if existing:
                        # Güncelle
                        await session.execute(
                            text("""
                                UPDATE profiles 
                                SET profile_type = :profile_type,
                                    is_spam_active = :is_spam_active,
                                    is_dm_active = :is_dm_active,
                                    is_group_active = :is_group_active,
                                    engaging_messages = :engaging_messages,
                                    response_style = :response_style,
                                    tone = :tone,
                                    topics = :topics,
                                    updated_at = :updated_at
                                WHERE username = :username
                            """),
                            {
                                "username": username,
                                "profile_type": profile.get("profile_type", "spambot"),
                                "is_spam_active": profile.get("is_spam_active", False),
                                "is_dm_active": profile.get("is_dm_active", False),
                                "is_group_active": profile.get("is_group_active", False),
                                "engaging_messages": json.dumps(profile.get("engaging_messages", [])),
                                "response_style": profile.get("response_style", "friendly"),
                                "tone": profile.get("tone", "warm"),
                                "topics": json.dumps(profile.get("topics", [])),
                                "updated_at": profile["updated_at"]
                            }
                        )
                    else:
                        # Yeni ekle
                        await session.execute(
                            text("""
                                INSERT INTO profiles 
                                (username, profile_type, is_spam_active, is_dm_active, 
                                 is_group_active, engaging_messages, response_style, 
                                 tone, topics, created_at, updated_at)
                                VALUES 
                                (:username, :profile_type, :is_spam_active, :is_dm_active,
                                 :is_group_active, :engaging_messages, :response_style,
                                 :tone, :topics, :created_at, :updated_at)
                            """),
                            {
                                "username": username,
                                "profile_type": profile.get("profile_type", "spambot"),
                                "is_spam_active": profile.get("is_spam_active", False),
                                "is_dm_active": profile.get("is_dm_active", False),
                                "is_group_active": profile.get("is_group_active", False),
                                "engaging_messages": json.dumps(profile.get("engaging_messages", [])),
                                "response_style": profile.get("response_style", "friendly"),
                                "tone": profile.get("tone", "warm"),
                                "topics": json.dumps(profile.get("topics", [])),
                                "created_at": profile["created_at"],
                                "updated_at": profile["updated_at"]
                            }
                        )
                    
                    await session.commit()
                    
            except Exception as e:
                logger.error(f"DB profil kaydetme hatası ({username}): {e}")
            
            logger.info(f"✅ Profil kaydedildi: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Profil kaydetme hatası ({username}): {e}")
            return False
    
    async def get_all_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Tüm profilleri al"""
        profiles = {}
        
        # Dosyalardan oku
        try:
            for filename in os.listdir("data/personas"):
                if filename.endswith(".json"):
                    username = filename[:-5]  # .json'u çıkar
                    profile = await self.get_profile(username)
                    if profile:
                        profiles[username] = profile
        except Exception as e:
            logger.error(f"Profil listesi alma hatası: {e}")
        
        return profiles
    
    async def delete_profile(self, username: str) -> bool:
        """Profili sil"""
        try:
            # Dosyayı sil
            profile_path = os.path.join("data/personas", f"{username}.json")
            if os.path.exists(profile_path):
                os.remove(profile_path)
            
            # Cache'den sil
            if username in self._profile_cache:
                del self._profile_cache[username]
            
            # Veritabanından sil
            try:
                async with get_db_session() as session:
                    await session.execute(
                        text("DELETE FROM profiles WHERE username = :username"),
                        {"username": username}
                    )
                    await session.commit()
            except Exception as e:
                logger.error(f"DB profil silme hatası ({username}): {e}")
            
            logger.info(f"✅ Profil silindi: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Profil silme hatası ({username}): {e}")
            return False
    
    async def update_profile_activity(self, username: str, activity_type: str, is_active: bool) -> bool:
        """Profil aktivitesini güncelle"""
        profile = await self.get_profile(username)
        
        if not profile:
            logger.warning(f"Profil bulunamadı: {username}")
            return False
        
        # Aktiviteyi güncelle
        if activity_type == "spam":
            profile["is_spam_active"] = is_active
        elif activity_type == "dm":
            profile["is_dm_active"] = is_active
        elif activity_type == "group":
            profile["is_group_active"] = is_active
        else:
            logger.warning(f"Geçersiz aktivite tipi: {activity_type}")
            return False
        
        # Kaydet
        return await self.save_profile(username, profile)
    
    def clear_cache(self):
        """Cache'i temizle"""
        self._profile_cache.clear()
        logger.info("Profile cache temizlendi")

# Global instance
profile_manager = ProfileManager() 