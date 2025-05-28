#!/usr/bin/env python3
# core/package_manager.py - Paket Yönetim Sistemi

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import structlog
from core.db.connection import get_db_session
from sqlalchemy import text

logger = structlog.get_logger("gavatcore.package_manager")

# Paket tanımlamaları
PACKAGES = {
    "basic": {
        "name": "Basic",
        "daily_messages": 100,
        "groups": 50,
        "cooldown_minutes": 5,
        "dm_cooldown_minutes": 3,
        "max_warnings": 3,
        "features": ["spam", "dm_reply", "basic_support"]
    },
    "pro": {
        "name": "Pro",
        "daily_messages": 500,
        "groups": 150,
        "cooldown_minutes": 3,
        "dm_cooldown_minutes": 2,
        "max_warnings": 5,
        "features": ["spam", "dm_reply", "group_reply", "priority_support", "analytics"]
    },
    "enterprise": {
        "name": "Enterprise",
        "daily_messages": 2000,
        "groups": 500,
        "cooldown_minutes": 1,
        "dm_cooldown_minutes": 1,
        "max_warnings": 10,
        "features": ["spam", "dm_reply", "group_reply", "24_7_support", "analytics", "custom_messages", "api_access"]
    },
    "bamgum": {  # Özel paket - BAMGÜM! 🔥
        "name": "BAMGÜM",
        "daily_messages": 10000,  # Çok yüksek limit
        "groups": 1000,
        "cooldown_minutes": 0.5,  # 30 saniye
        "dm_cooldown_minutes": 0.5,
        "max_warnings": 20,
        "features": ["all", "unlimited", "bamgum_mode"]
    }
}

class PackageManager:
    """Paket yönetim sistemi"""
    
    def __init__(self):
        self.user_packages = {}  # Cache
        self.default_package = "basic"
    
    async def assign_package(self, user_id: int, package_name: str) -> bool:
        """Kullanıcıya paket ata"""
        if package_name not in PACKAGES:
            logger.error(f"Geçersiz paket: {package_name}")
            return False
        
        try:
            async with get_db_session() as session:
                # Mevcut paketi kontrol et
                result = await session.execute(
                    text("SELECT id FROM user_packages WHERE user_id = :user_id"),
                    {"user_id": user_id}
                )
                existing = result.first()
                
                if existing:
                    # Güncelle
                    await session.execute(
                        text("""
                            UPDATE user_packages 
                            SET package_name = :package_name,
                                updated_at = :updated_at
                            WHERE user_id = :user_id
                        """),
                        {
                            "user_id": user_id,
                            "package_name": package_name,
                            "updated_at": datetime.now()
                        }
                    )
                else:
                    # Yeni ekle
                    await session.execute(
                        text("""
                            INSERT INTO user_packages 
                            (user_id, package_name, created_at, updated_at)
                            VALUES 
                            (:user_id, :package_name, :created_at, :updated_at)
                        """),
                        {
                            "user_id": user_id,
                            "package_name": package_name,
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                    )
                
                await session.commit()
                
                # Cache'i güncelle
                self.user_packages[user_id] = package_name
                
                logger.info(f"✅ Paket atandı: User {user_id} -> {package_name}")
                return True
                
        except Exception as e:
            logger.error(f"Paket atama hatası: {e}")
            return False
    
    def get_user_package(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Kullanıcının paket bilgisini al"""
        # Cache'den kontrol et
        if user_id in self.user_packages:
            package_name = self.user_packages[user_id]
            package_info = PACKAGES.get(package_name, PACKAGES[self.default_package]).copy()
            package_info["package_name"] = package_name
            return package_info
        
        # Veritabanından kontrol et
        try:
            # Senkron context'de async işlem yapamayız, varsayılan paket dön
            # TODO: Async version eklenebilir
            return self.get_default_package()
        except Exception as e:
            logger.error(f"Paket bilgisi alma hatası: {e}")
            return self.get_default_package()
    
    def get_default_package(self) -> Dict[str, Any]:
        """Varsayılan paketi al"""
        package_info = PACKAGES[self.default_package].copy()
        package_info["package_name"] = self.default_package
        return package_info
    
    def get_limit(self, user_id: int, limit_type: str) -> Any:
        """Belirli bir limit değerini al"""
        package = self.get_user_package(user_id)
        return package.get(limit_type, 0)
    
    def has_feature(self, user_id: int, feature: str) -> bool:
        """Kullanıcının belirli bir özelliğe sahip olup olmadığını kontrol et"""
        package = self.get_user_package(user_id)
        features = package.get("features", [])
        
        # "all" veya "unlimited" varsa tüm özellikler var
        if "all" in features or "unlimited" in features:
            return True
        
        return feature in features
    
    def is_within_daily_limit(self, user_id: int, message_count: int) -> bool:
        """Günlük mesaj limitinde mi kontrol et"""
        daily_limit = self.get_limit(user_id, "daily_messages")
        return message_count < daily_limit
    
    def get_cooldown_seconds(self, user_id: int, cooldown_type: str = "spam") -> int:
        """Cooldown süresini saniye olarak al"""
        if cooldown_type == "dm":
            minutes = self.get_limit(user_id, "dm_cooldown_minutes")
        else:
            minutes = self.get_limit(user_id, "cooldown_minutes")
        
        return int(minutes * 60)
    
    def get_max_warnings(self, user_id: int) -> int:
        """Maksimum uyarı sayısını al"""
        return self.get_limit(user_id, "max_warnings")
    
    def get_all_packages(self) -> Dict[str, Dict[str, Any]]:
        """Tüm paket bilgilerini al"""
        return PACKAGES.copy()
    
    def upgrade_package(self, user_id: int) -> Optional[str]:
        """Paketi bir üst seviyeye yükselt"""
        current_package = self.get_user_package(user_id)
        current_name = current_package.get("package_name", self.default_package)
        
        upgrade_path = {
            "basic": "pro",
            "pro": "enterprise",
            "enterprise": "bamgum"
        }
        
        next_package = upgrade_path.get(current_name)
        if next_package:
            asyncio.create_task(self.assign_package(user_id, next_package))
            return next_package
        
        return None
    
    def check_bamgum_mode(self, user_id: int) -> bool:
        """BAMGÜM modunda mı kontrol et"""
        package = self.get_user_package(user_id)
        return package.get("package_name") == "bamgum"

# Global instance
package_manager = PackageManager()

# Asyncio import for upgrade_package
import asyncio 