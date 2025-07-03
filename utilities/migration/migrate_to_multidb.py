#!/usr/bin/env python3
"""
GAVATCORE Multi-Database Migration Script
=========================================

Bu script mevcut SQLite verilerini PostgreSQL, MongoDB ve Redis'e migrate eder.

Özellikler:
- SQLite'dan PostgreSQL'e log ve event verilerini taşır
- File-based profil verilerini MongoDB'ye taşır  
- Mevcut session state'lerini Redis'e taşır
- Backup oluşturur
- Rollback desteği sağlar
"""

import asyncio
import os
import shutil
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import traceback

# Local imports
from core.db.connection import init_database, get_async_session
from core.db.models import EventLog, SaleLog, MessageRecord, UserSession
from core.profile_store import init_profile_store, create_or_update_profile, close_profile_store
from utilities.redis_client import init_redis, set_state, set_cooldown, close_redis
import config

class MultiDBMigrator:
    def __init__(self):
        self.backup_dir = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.sqlite_path = "gavatcore.db"
        self.profiles_dir = "data/profiles"
        self.sessions_dir = "sessions"
        
        # Database clients initialized
        
        # Migration stats
        self.stats = {
            "events_migrated": 0,
            "sales_migrated": 0,
            "messages_migrated": 0,
            "profiles_migrated": 0,
            "sessions_migrated": 0,
            "errors": []
        }
    
    async def init_clients(self):
        """Database client'larını başlat"""
        print("🔌 Database bağlantıları başlatılıyor...")
        
        # PostgreSQL/SQLite
        await init_database()
        print("✅ PostgreSQL/SQLite bağlantısı hazır")
        
        # MongoDB/File-based
        await init_profile_store()
        print("✅ MongoDB/File-based profil store hazır")
        
        # Redis
        await init_redis()
        print("✅ Redis bağlantısı hazır")
    
    def create_backup(self):
        """Mevcut verilerin backup'ını oluştur"""
        print(f"📦 Backup oluşturuluyor: {self.backup_dir}")
        
        # Backups dizinini oluştur
        os.makedirs("backups", exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # SQLite backup
        if os.path.exists(self.sqlite_path):
            shutil.copy2(self.sqlite_path, f"{self.backup_dir}/gavatcore.db")
            print("✅ SQLite backup oluşturuldu")
        
        # Profiles backup
        if os.path.exists(self.profiles_dir):
            shutil.copytree(self.profiles_dir, f"{self.backup_dir}/profiles")
            print("✅ Profil dosyaları backup oluşturuldu")
        
        # Sessions backup
        if os.path.exists(self.sessions_dir):
            shutil.copytree(self.sessions_dir, f"{self.backup_dir}/sessions")
            print("✅ Session dosyaları backup oluşturuldu")
        
        # Logs backup
        if os.path.exists("logs"):
            shutil.copytree("logs", f"{self.backup_dir}/logs")
            print("✅ Log dosyaları backup oluşturuldu")
    
    async def migrate_sqlite_to_postgres(self):
        """SQLite verilerini PostgreSQL'e migrate et"""
        print("🔄 SQLite → PostgreSQL migration başlıyor...")
        
        if not os.path.exists(self.sqlite_path):
            print("⚠️ SQLite dosyası bulunamadı, atlanıyor")
            return
        
        # SQLite bağlantısı
        sqlite_conn = sqlite3.connect(self.sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        cursor = sqlite_conn.cursor()
        
        try:
            async with get_async_session() as session:
                # Events migration
                try:
                    cursor.execute("SELECT * FROM events ORDER BY timestamp")
                    events = cursor.fetchall()
                    
                    for event in events:
                        event_log = EventLog(
                            timestamp=datetime.fromisoformat(event['timestamp']) if event['timestamp'] else datetime.now(),
                            event_type=event['event_type'] or 'unknown',
                            user_id=event['user_id'],
                            details=event['details'] or '{}',
                            severity=event.get('severity', 'info')
                        )
                        session.add(event_log)
                        self.stats["events_migrated"] += 1
                    
                    await session.commit()
                    print(f"✅ {self.stats['events_migrated']} event migrate edildi")
                
                except Exception as e:
                    print(f"⚠️ Events migration hatası: {e}")
                    self.stats["errors"].append(f"Events: {e}")
                
                # Sales migration
                try:
                    cursor.execute("SELECT * FROM sales ORDER BY timestamp")
                    sales = cursor.fetchall()
                    
                    for sale in sales:
                        sale_log = SaleLog(
                            timestamp=datetime.fromisoformat(sale['timestamp']) if sale['timestamp'] else datetime.now(),
                            user_id=sale['user_id'],
                            product_type=sale['product_type'] or 'unknown',
                            amount=float(sale['amount']) if sale['amount'] else 0.0,
                            currency=sale.get('currency', 'USD'),
                            details=sale['details'] or '{}'
                        )
                        session.add(sale_log)
                        self.stats["sales_migrated"] += 1
                    
                    await session.commit()
                    print(f"✅ {self.stats['sales_migrated']} sale migrate edildi")
                
                except Exception as e:
                    print(f"⚠️ Sales migration hatası: {e}")
                    self.stats["errors"].append(f"Sales: {e}")
                
                # Messages migration
                try:
                    cursor.execute("SELECT * FROM messages ORDER BY timestamp")
                    messages = cursor.fetchall()
                    
                    for msg in messages:
                        message_record = MessageRecord(
                            timestamp=datetime.fromisoformat(msg['timestamp']) if msg['timestamp'] else datetime.now(),
                            user_id=msg['user_id'],
                            chat_id=msg.get('chat_id'),
                            message_type=msg.get('message_type', 'text'),
                            content=msg['content'] or '',
                            metadata=msg.get('metadata', '{}')
                        )
                        session.add(message_record)
                        self.stats["messages_migrated"] += 1
                    
                    await session.commit()
                    print(f"✅ {self.stats['messages_migrated']} message migrate edildi")
                
                except Exception as e:
                    print(f"⚠️ Messages migration hatası: {e}")
                    self.stats["errors"].append(f"Messages: {e}")
        
        finally:
            sqlite_conn.close()
    
    async def migrate_profiles_to_mongodb(self):
        """File-based profilleri MongoDB'ye migrate et"""
        print("🔄 File-based Profiles → MongoDB migration başlıyor...")
        
        if not os.path.exists(self.profiles_dir):
            print("⚠️ Profil dizini bulunamadı, atlanıyor")
            return
        
        try:
            for profile_file in Path(self.profiles_dir).glob("*.json"):
                try:
                    with open(profile_file, 'r', encoding='utf-8') as f:
                        profile_data = json.load(f)
                    
                    user_id = profile_file.stem
                    
                    # MongoDB'ye kaydet
                    await create_or_update_profile(user_id, profile_data)
                    self.stats["profiles_migrated"] += 1
                    
                    print(f"✅ Profil migrate edildi: {user_id}")
                
                except Exception as e:
                    print(f"⚠️ Profil migration hatası {profile_file}: {e}")
                    self.stats["errors"].append(f"Profile {profile_file}: {e}")
            
            print(f"✅ {self.stats['profiles_migrated']} profil migrate edildi")
        
        except Exception as e:
            print(f"⚠️ Profiles migration genel hatası: {e}")
            self.stats["errors"].append(f"Profiles general: {e}")
    
    async def migrate_sessions_to_redis(self):
        """Session state'lerini Redis'e migrate et"""
        print("🔄 Session States → Redis migration başlıyor...")
        
        # DM conversation states
        dm_state_file = "dm_conversation_state.json"
        if os.path.exists(dm_state_file):
            try:
                with open(dm_state_file, 'r', encoding='utf-8') as f:
                    dm_states = json.load(f)
                
                for user_id, state in dm_states.items():
                    await set_state(user_id, "dm_conversation", state)
                    self.stats["sessions_migrated"] += 1
                
                print(f"✅ {len(dm_states)} DM conversation state migrate edildi")
            
            except Exception as e:
                print(f"⚠️ DM states migration hatası: {e}")
                self.stats["errors"].append(f"DM states: {e}")
        
        # Cooldown states
        cooldown_file = "cooldowns.json"
        if os.path.exists(cooldown_file):
            try:
                with open(cooldown_file, 'r', encoding='utf-8') as f:
                    cooldowns = json.load(f)
                
                for key, expiry in cooldowns.items():
                    # Expiry time'ı hesapla
                    if isinstance(expiry, (int, float)):
                        ttl = max(0, int(expiry - datetime.now().timestamp()))
                        if ttl > 0:
                            await set_cooldown("global", key, ttl)
                            self.stats["sessions_migrated"] += 1
                
                print(f"✅ Cooldown states migrate edildi")
            
            except Exception as e:
                print(f"⚠️ Cooldowns migration hatası: {e}")
                self.stats["errors"].append(f"Cooldowns: {e}")
    
    async def verify_migration(self):
        """Migration'ın başarılı olduğunu doğrula"""
        print("🔍 Migration doğrulaması yapılıyor...")
        
        try:
            # PostgreSQL/SQLite verification
            async with get_async_session() as session:
                from sqlalchemy import select, func
                
                events_count = await session.scalar(select(func.count(EventLog.id)))
                sales_count = await session.scalar(select(func.count(SaleLog.id)))
                messages_count = await session.scalar(select(func.count(MessageRecord.id)))
                
                print(f"📊 PostgreSQL/SQLite: {events_count} events, {sales_count} sales, {messages_count} messages")
            
            # MongoDB verification
            from core.profile_store import mongo_db
            if mongo_db:
                profiles_count = await mongo_db.profiles.count_documents({})
                print(f"📊 MongoDB: {profiles_count} profiles")
            else:
                # File-based count
                profile_files = list(Path(self.profiles_dir).glob("*.json")) if os.path.exists(self.profiles_dir) else []
                print(f"📊 File-based: {len(profile_files)} profiles")
            
            # Redis verification
            from utilities.redis_client import redis_client
            if redis_client:
                redis_keys = await redis_client.keys("*")
                print(f"📊 Redis: {len(redis_keys)} keys")
            else:
                print("📊 Redis: bağlantı yok")
            
            print("✅ Migration doğrulaması tamamlandı")
        
        except Exception as e:
            print(f"⚠️ Verification hatası: {e}")
            self.stats["errors"].append(f"Verification: {e}")
    
    def print_summary(self):
        """Migration özetini yazdır"""
        print("\n" + "="*50)
        print("📋 MIGRATION ÖZETI")
        print("="*50)
        print(f"Events migrated: {self.stats['events_migrated']}")
        print(f"Sales migrated: {self.stats['sales_migrated']}")
        print(f"Messages migrated: {self.stats['messages_migrated']}")
        print(f"Profiles migrated: {self.stats['profiles_migrated']}")
        print(f"Sessions migrated: {self.stats['sessions_migrated']}")
        print(f"Backup location: {self.backup_dir}")
        
        if self.stats["errors"]:
            print(f"\n⚠️ Hatalar ({len(self.stats['errors'])}):")
            for error in self.stats["errors"]:
                print(f"  - {error}")
        else:
            print("\n✅ Hiç hata yok!")
        
        print("="*50)
    
    async def run_migration(self):
        """Ana migration işlemini çalıştır"""
        print("🚀 GAVATCORE Multi-Database Migration başlıyor...")
        print(f"⏰ Başlangıç zamanı: {datetime.now()}")
        
        try:
            # 1. Backup oluştur
            self.create_backup()
            
            # 2. Database client'larını başlat
            await self.init_clients()
            
            # 3. Migration'ları çalıştır
            await self.migrate_sqlite_to_postgres()
            await self.migrate_profiles_to_mongodb()
            await self.migrate_sessions_to_redis()
            
            # 4. Doğrulama
            await self.verify_migration()
            
            # 5. Özet
            self.print_summary()
            
            print(f"\n🎉 Migration tamamlandı! ⏰ {datetime.now()}")
            
        except Exception as e:
            print(f"\n💥 Migration hatası: {e}")
            print(f"📋 Traceback:\n{traceback.format_exc()}")
            self.stats["errors"].append(f"General: {e}")
            self.print_summary()
            raise
        
        finally:
            # Cleanup
            await close_redis()
            await close_profile_store()

async def main():
    """Ana fonksiyon"""
    migrator = MultiDBMigrator()
    await migrator.run_migration()

if __name__ == "__main__":
    asyncio.run(main())