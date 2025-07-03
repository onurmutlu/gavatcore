#!/usr/bin/env python3
# migrate_sessions_to_db.py - Session Migration Script

import asyncio
import os
import sqlite3
import base64
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Local imports
from core.db_session import DatabaseSession
from utilities.redis_client import init_redis, close_redis
from utilities.log_utils import log_event

class SessionMigrator:
    """Session dosyalarını veritabanına migrate eder"""
    
    def __init__(self):
        self.sessions_dir = Path("sessions")
        self.backup_dir = Path(f"backups/sessions_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.stats = {
            "total_sessions": 0,
            "migrated_sessions": 0,
            "failed_sessions": 0,
            "errors": []
        }
    
    async def init_storage(self):
        """Storage sistemlerini başlat"""
        print("🔌 Storage sistemleri başlatılıyor...")
        
        # Redis başlat
        await init_redis()
        print("✅ Redis bağlantısı hazır")
        
        # PostgreSQL ve MongoDB da başlatılabilir
        # await init_database()
        # await init_profile_store()
    
    def create_backup(self):
        """Session dosyalarının backup'ını oluştur"""
        print("💾 Session backup'ı oluşturuluyor...")
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Tüm session dosyalarını backup'la
            session_files = list(self.sessions_dir.glob("*.session*"))
            
            for session_file in session_files:
                backup_file = self.backup_dir / session_file.name
                import shutil
                shutil.copy2(session_file, backup_file)
            
            print(f"✅ {len(session_files)} session dosyası backup'landı: {self.backup_dir}")
            
        except Exception as e:
            print(f"❌ Backup oluşturma hatası: {e}")
            raise
    
    def get_session_files(self) -> list:
        """Session dosyalarını listele"""
        session_files = []
        
        for session_file in self.sessions_dir.glob("*.session"):
            # Journal dosyalarını atla
            if session_file.name.endswith("-journal"):
                continue
            
            session_name = session_file.stem
            session_files.append({
                "name": session_name,
                "path": session_file,
                "size": session_file.stat().st_size,
                "modified": datetime.fromtimestamp(session_file.stat().st_mtime)
            })
        
        return session_files
    
    def read_sqlite_session(self, session_path: Path) -> Optional[Dict[str, Any]]:
        """SQLite session dosyasını oku"""
        try:
            conn = sqlite3.connect(str(session_path))
            cursor = conn.cursor()
            
            session_data = {}
            
            # Version tablosunu oku
            try:
                cursor.execute("SELECT version FROM version")
                session_data["version"] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                session_data["version"] = 1
            
            # Sessions tablosunu oku
            try:
                cursor.execute("""
                    SELECT dc_id, server_address, port, auth_key, takeout_id 
                    FROM sessions
                """)
                row = cursor.fetchone()
                if row:
                    session_data.update({
                        "dc_id": row[0],
                        "server_address": row[1],
                        "port": row[2],
                        "auth_key": base64.b64encode(row[3]).decode() if row[3] else None,
                        "takeout_id": row[4]
                    })
            except sqlite3.OperationalError as e:
                print(f"⚠️ Sessions tablosu okunamadı: {e}")
            
            # Entities tablosunu oku
            try:
                cursor.execute("""
                    SELECT id, hash, username, phone, name, date 
                    FROM entities
                """)
                entities = []
                for row in cursor.fetchall():
                    entities.append({
                        "id": row[0],
                        "hash": row[1],
                        "username": row[2],
                        "phone": row[3],
                        "name": row[4],
                        "date": row[5]
                    })
                session_data["entities"] = entities
            except sqlite3.OperationalError:
                session_data["entities"] = []
            
            # Sent files tablosunu oku
            try:
                cursor.execute("""
                    SELECT md5_digest, file_size, type, id, hash 
                    FROM sent_files
                """)
                files = []
                for row in cursor.fetchall():
                    files.append({
                        "md5_digest": base64.b64encode(row[0]).decode() if row[0] else None,
                        "file_size": row[1],
                        "type": row[2],
                        "id": row[3],
                        "hash": row[4]
                    })
                session_data["files"] = files
            except sqlite3.OperationalError:
                session_data["files"] = []
            
            conn.close()
            return session_data
            
        except Exception as e:
            print(f"❌ SQLite session okuma hatası {session_path}: {e}")
            return None
    
    async def migrate_session_to_redis(self, session_name: str, session_data: Dict[str, Any]) -> bool:
        """Session verilerini Redis'e migrate et"""
        try:
            # DatabaseSession oluştur
            db_session = DatabaseSession(session_name, "redis")
            
            # DC bilgilerini kaydet
            if all(k in session_data for k in ["dc_id", "server_address", "port"]):
                db_session.set_dc(
                    session_data["dc_id"],
                    session_data["server_address"],
                    session_data["port"]
                )
            
            # Auth key'i kaydet
            if session_data.get("auth_key"):
                from utilities.redis_client import redis_client
                if redis_client:
                    await redis_client.set(
                        f"session:{session_name}:auth_key",
                        session_data["auth_key"],
                        ex=86400 * 30  # 30 gün TTL
                    )
            
            # Entities'leri kaydet
            if session_data.get("entities"):
                from utilities.redis_client import redis_client
                if redis_client:
                    entities_json = json.dumps(session_data["entities"])
                    await redis_client.set(
                        f"session:{session_name}:entities",
                        entities_json,
                        ex=86400 * 7  # 7 gün TTL
                    )
            
            # Files'ları kaydet
            if session_data.get("files"):
                from utilities.redis_client import redis_client
                if redis_client:
                    files_json = json.dumps(session_data["files"])
                    await redis_client.set(
                        f"session:{session_name}:files",
                        files_json,
                        ex=86400 * 1  # 1 gün TTL
                    )
            
            # Metadata kaydet
            metadata = {
                "migrated_at": datetime.now().isoformat(),
                "version": session_data.get("version", 1),
                "entities_count": len(session_data.get("entities", [])),
                "files_count": len(session_data.get("files", []))
            }
            
            from utilities.redis_client import redis_client
            if redis_client:
                await redis_client.hset(
                    f"session:{session_name}:metadata",
                    mapping=metadata
                )
            
            log_event(session_name, f"✅ Session Redis'e migrate edildi")
            return True
            
        except Exception as e:
            log_event(session_name, f"❌ Redis migration hatası: {e}")
            self.stats["errors"].append(f"{session_name}: {e}")
            return False
    
    async def migrate_all_sessions(self):
        """Tüm session'ları migrate et"""
        print("🔄 Session migration başlıyor...")
        
        session_files = self.get_session_files()
        self.stats["total_sessions"] = len(session_files)
        
        print(f"📁 {len(session_files)} session dosyası bulundu")
        
        for session_info in session_files:
            session_name = session_info["name"]
            session_path = session_info["path"]
            
            print(f"\n🔄 {session_name} migrate ediliyor...")
            
            # SQLite session'ı oku
            session_data = self.read_sqlite_session(session_path)
            
            if not session_data:
                print(f"❌ {session_name} okunamadı")
                self.stats["failed_sessions"] += 1
                continue
            
            # Redis'e migrate et
            success = await self.migrate_session_to_redis(session_name, session_data)
            
            if success:
                print(f"✅ {session_name} başarıyla migrate edildi")
                self.stats["migrated_sessions"] += 1
            else:
                print(f"❌ {session_name} migration başarısız")
                self.stats["failed_sessions"] += 1
    
    async def verify_migration(self):
        """Migration'ı doğrula"""
        print("\n🔍 Migration doğrulaması yapılıyor...")
        
        try:
            from utilities.redis_client import redis_client
            if redis_client:
                # Redis'teki session key'lerini say
                session_keys = await redis_client.keys("session:*")
                unique_sessions = set()
                
                for key in session_keys:
                    # session:username:type formatından username'i çıkar
                    parts = key.split(":")
                    if len(parts) >= 2:
                        unique_sessions.add(parts[1])
                
                print(f"📊 Redis'te {len(unique_sessions)} unique session bulundu")
                print(f"📊 Toplam {len(session_keys)} session key'i var")
                
                # Örnek session verilerini göster
                for session_name in list(unique_sessions)[:3]:
                    metadata = await redis_client.hgetall(f"session:{session_name}:metadata")
                    if metadata:
                        print(f"   📋 {session_name}: {metadata}")
        
        except Exception as e:
            print(f"⚠️ Verification hatası: {e}")
    
    def print_summary(self):
        """Migration özetini yazdır"""
        print("\n" + "="*60)
        print("📊 SESSION MIGRATION ÖZET")
        print("="*60)
        print(f"📁 Toplam session: {self.stats['total_sessions']}")
        print(f"✅ Başarılı migration: {self.stats['migrated_sessions']}")
        print(f"❌ Başarısız migration: {self.stats['failed_sessions']}")
        print(f"📈 Başarı oranı: {(self.stats['migrated_sessions']/max(self.stats['total_sessions'],1)*100):.1f}%")
        
        if self.stats["errors"]:
            print(f"\n❌ Hatalar ({len(self.stats['errors'])}):")
            for error in self.stats["errors"][:5]:  # İlk 5 hatayı göster
                print(f"   • {error}")
        
        print(f"\n💾 Backup konumu: {self.backup_dir}")
        print("="*60)
    
    async def run_migration(self):
        """Ana migration işlemini çalıştır"""
        print("🚀 GAVATCORE Session Migration başlıyor...")
        print(f"⏰ Başlangıç zamanı: {datetime.now()}")
        
        try:
            # 1. Backup oluştur
            self.create_backup()
            
            # 2. Storage sistemlerini başlat
            await self.init_storage()
            
            # 3. Migration'ı çalıştır
            await self.migrate_all_sessions()
            
            # 4. Doğrulama
            await self.verify_migration()
            
            # 5. Özet
            self.print_summary()
            
            print(f"\n🎉 Session migration tamamlandı! ⏰ {datetime.now()}")
            
        except Exception as e:
            print(f"\n💥 Migration hatası: {e}")
            self.stats["errors"].append(f"General: {e}")
            self.print_summary()
            raise
        
        finally:
            # Cleanup
            await close_redis()

# CLI interface
async def main():
    """Ana fonksiyon"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        print("🧪 DRY RUN MODE - Sadece analiz yapılacak")
        # Dry run implementation
        migrator = SessionMigrator()
        session_files = migrator.get_session_files()
        
        print(f"📁 {len(session_files)} session dosyası bulundu:")
        for session_info in session_files:
            print(f"   📄 {session_info['name']} ({session_info['size']} bytes)")
        
        return
    
    # Gerçek migration
    migrator = SessionMigrator()
    await migrator.run_migration()

if __name__ == "__main__":
    asyncio.run(main()) 