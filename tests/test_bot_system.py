#!/usr/bin/env python3
"""
🔧 BOT SYSTEM TEST 🔧

Bot conversation sisteminin ne sorunu olduğunu test edelim
"""

import asyncio
from onlyvips_bot_conversation_system import OnlyVipsBotConversationSystem

async def test_bot_system():
    """🔧 Bot sistemini test et"""
    try:
        print("🔧 Bot Conversation System test ediliyor...")
        
        system = OnlyVipsBotConversationSystem()
        result = await system.initialize()
        
        print(f"✅ System initialized: {result}")
        
        if result:
            print(f"🤖 Active bots: {len(system.clients)}")
            print(f"📱 Group ID: {system.onlyvips_group_id}")
            
            for name, data in system.clients.items():
                print(f"   🤖 Bot {name}: @{data['me'].username}")
        
        await system.shutdown()
        return result
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_bot_system()) 