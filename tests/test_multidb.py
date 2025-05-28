#!/usr/bin/env python3
# test_multidb.py - Multi-database sistem testi

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from core.db.connection import init_database, close_database
from core.profile_store import init_profile_store, close_profile_store
from utils.redis_client import init_redis, close_redis

async def test_databases():
    print('🗄️ Database sistemleri test ediliyor...')
    
    try:
        # PostgreSQL/SQLite test
        await init_database()
        print('✅ PostgreSQL/SQLite bağlantısı başarılı')
        
        # MongoDB test
        await init_profile_store()
        print('✅ MongoDB/File-based profil sistemi başarılı')
        
        # Redis test
        await init_redis()
        print('✅ Redis bağlantısı başarılı')
        
        print('🎉 Tüm database sistemleri çalışıyor!')
        
        # Cleanup
        await close_database()
        await close_profile_store()
        await close_redis()
        print('✅ Tüm bağlantılar kapatıldı')
        
        return True
        
    except Exception as e:
        print(f'❌ Database test hatası: {e}')
        return False

if __name__ == "__main__":
    success = asyncio.run(test_databases())
    if success:
        print("\n🚀 Multi-database sistemi hazır!")
    else:
        print("\n💥 Multi-database sistemi başlatılamadı!") 