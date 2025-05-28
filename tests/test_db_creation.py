#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from core.db.connection import init_database
from core.db.models import EventLog, SaleLog, MessageRecord, UserSession

async def test_db_creation():
    print("🔧 Database tablo oluşturma testi...")
    
    success = await init_database()
    if success:
        print("✅ Database başlatıldı")
    else:
        print("❌ Database başlatma hatası")

if __name__ == "__main__":
    asyncio.run(test_db_creation()) 