#!/usr/bin/env python3
"""
Simple test bot to check Telethon compatibility
"""

import asyncio
import logging
from telethon import TelegramClient
from config import API_ID, API_HASH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_connection():
    """Test single bot connection"""
    
    # Test with one bot
    client = TelegramClient('sessions/test_bot', API_ID, API_HASH)
    
    try:
        logger.info("🔗 Testing connection...")
        await client.start(phone='+905382617727')  # Lara
        
        me = await client.get_me()
        logger.info(f"✅ Connected! @{me.username} (ID: {me.id})")
        
        await client.disconnect()
        logger.info("✅ Test successful!")
        
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        if client.is_connected():
            await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_connection()) 