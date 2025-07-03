#!/usr/bin/env python3
"""
🧪 GavatCoin System Quick Test 🧪

Token ekonomisini hızlı test etmek için basit script
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_gavatcoin_system():
    """Quick test of GavatCoin token system"""
    
    print("🪙 " + "="*50)
    print("🚀 GavatCoin Token System Test")
    print("💰 OnlyVips v6.0 Token Economy")
    print("🪙 " + "="*50)
    print()
    
    try:
        # Import token system
        from xp_token_engine import get_token_manager, spend_token_for_service, SpendHandlers
        
        print("✅ Token system imported successfully!")
        
        # Test user
        test_user = "test_baron_123"
        
        async with get_token_manager() as tm:
            print(f"✅ Token manager initialized for user: {test_user}")
            
            # 1. Give initial XP
            print("\n💎 Step 1: Converting 100 XP to tokens...")
            balance = await tm.xp_to_token(test_user, 100)
            print(f"💰 New balance: {balance} tokens")
            
            # 2. Show current balance
            current_balance = await tm.get_balance(test_user)
            print(f"💳 Current balance: {current_balance} tokens")
            
            # 3. Show service costs
            costs = await SpendHandlers.get_service_costs()
            print(f"\n💸 Service costs: {costs}")
            
            # 4. Check what user can afford
            affordable = await SpendHandlers.get_affordable_services(test_user)
            print(f"\n🛒 Affordable services:")
            for service, info in affordable.items():
                status = "✅" if info['affordable'] else "❌"
                print(f"  {status} {service}: {info['cost']} tokens")
            
            # 5. Try buying content
            print(f"\n🎬 Trying to buy premium content...")
            success, message = await spend_token_for_service(test_user, "content", content_id="test_video_001")
            print(f"Result: {message}")
            
            # 6. Try boosting quest
            print(f"\n⚡ Trying to boost daily quest...")
            success, message = await spend_token_for_service(test_user, "boost")
            print(f"Result: {message}")
            
            # 7. Show updated balance
            final_balance = await tm.get_balance(test_user)
            print(f"\n💰 Final balance: {final_balance} tokens")
            
            # 8. Show transaction logs
            print(f"\n📜 Transaction history:")
            logs = await tm.get_logs(test_user, limit=5)
            for log in logs:
                print(f"  {log['type']}: {log['amount']} tokens - {log['reason']}")
            
            # 9. Show system stats
            print(f"\n📈 System statistics:")
            stats = await tm.get_all_users_stats()
            print(f"  Total users: {stats['total_users']}")
            print(f"  Total tokens: {stats['total_tokens']}")
            print(f"  Total transactions: {stats['total_transactions']}")
            
            print("\n🎉 GavatCoin system test completed successfully!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gavatcoin_system()) 