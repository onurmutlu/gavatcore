#!/usr/bin/env python3
"""
🧪 XP Bot Integration Test 🧪

Production bot XP/Token entegrasyonunu test eder
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_xp_bot_integration():
    """XP/Token bot integration test"""
    
    print("🎮 " + "="*50)
    print("🚀 XP Bot Integration Test")
    print("💰 OnlyVips v6.0 Token Economy + Bot Integration")
    print("🎮 " + "="*50)
    print()
    
    try:
        # Import XP bot integration
        from xp_token_engine.bot_integration import award_user_xp, handle_user_stats, handle_user_spend
        from xp_token_engine import get_token_manager
        
        print("✅ XP Bot Integration imported successfully!")
        
        # Test user (Telegram user ID simulation)
        test_user_id = 123456789
        
        print(f"✅ Test user ID: {test_user_id}")
        print()
        
        # Test 1: /start command XP
        print("🚀 Test 1: /start command XP...")
        success, tokens, message = await award_user_xp(test_user_id, "start_command")
        print(f"Result: {success}")
        print(f"Tokens: {tokens}")
        print(f"Message: {message}")
        print()
        
        # Test 2: First DM XP
        print("💌 Test 2: First DM XP...")
        success, tokens, message = await award_user_xp(test_user_id, "first_dm")
        print(f"Result: {success}")
        print(f"Tokens: {tokens}")
        print(f"Message: {message}")
        print()
        
        # Test 3: DM Reply XP
        print("💬 Test 3: DM Reply XP...")
        success, tokens, message = await award_user_xp(test_user_id, "dm_reply")
        print(f"Result: {success}")
        print(f"Tokens: {tokens}")
        print(f"Message: {message}")
        print()
        
        # Test 4: Group mention XP
        print("📢 Test 4: Group mention XP...")
        success, tokens, message = await award_user_xp(test_user_id, "group_mention")
        print(f"Result: {success}")
        print(f"Tokens: {tokens}")
        print(f"Message: {message}")
        print()
        
        # Test 5: Daily bonus check
        print("🎁 Test 5: Daily bonus...")
        success, tokens, message = await award_user_xp(test_user_id, "daily_bonus")
        print(f"Result: {success}")
        print(f"Tokens: {tokens}")
        print(f"Message: {message}")
        print()
        
        # Test 6: /stats command
        print("📊 Test 6: /stats command...")
        stats_response = await handle_user_stats(test_user_id)
        print("Stats Response:")
        print(stats_response)
        print()
        
        # Test 7: Current balance check
        print("💳 Test 7: Balance check...")
        async with get_token_manager() as tm:
            balance = await tm.get_balance(str(test_user_id))
            print(f"Current balance: {balance} tokens")
        print()
        
        # Test 8: Token spending attempt
        print("🛒 Test 8: Token spending (content)...")
        spend_response = await handle_user_spend(test_user_id, "content", "test_video_premium")
        print("Spend Response:")
        print(spend_response)
        print()
        
        # Test 9: VIP upgrade attempt
        print("👑 Test 9: VIP upgrade attempt...")
        spend_response = await handle_user_spend(test_user_id, "vip")
        print("VIP Upgrade Response:")
        print(spend_response)
        print()
        
        # Test 10: Final stats
        print("📈 Test 10: Final stats...")
        final_stats = await handle_user_stats(test_user_id)
        print("Final Stats:")
        print(final_stats)
        print()
        
        # Test 11: Cooldown test
        print("⏰ Test 11: Cooldown test (should fail)...")
        success, tokens, message = await award_user_xp(test_user_id, "dm_reply")
        print(f"Cooldown Result: {success}")
        print(f"Message: {message}")
        print()
        
        # Test 12: Different user test
        test_user_2 = 987654321
        print(f"👤 Test 12: Different user ({test_user_2})...")
        success, tokens, message = await award_user_xp(test_user_2, "start_command")
        print(f"New user XP: {success} -> {tokens} tokens")
        print()
        
        # Test 13: System stats
        print("📊 Test 13: System-wide statistics...")
        async with get_token_manager() as tm:
            system_stats = await tm.get_all_users_stats()
            print("System Stats:")
            print(f"  Total users: {system_stats['total_users']}")
            print(f"  Total tokens: {system_stats['total_tokens']}")
            print(f"  Total transactions: {system_stats['total_transactions']}")
            if system_stats['top_users']:
                print("  Top users:")
                for user in system_stats['top_users']:
                    print(f"    {user['user_id']}: {user['balance']} tokens")
        print()
        
        print("🎉 XP Bot Integration test completed successfully!")
        
        # Usage examples
        print("\n📖 " + "="*50)
        print("📖 PRODUCTION USAGE EXAMPLES")
        print("📖 " + "="*50)
        print()
        print("1. In bot message handler:")
        print("   success, tokens, msg = await award_user_xp(sender.id, 'dm_reply')")
        print()
        print("2. For /stats command:")
        print("   response = await handle_user_stats(sender.id)")
        print("   await event.reply(response)")
        print()
        print("3. For token spending:")
        print("   response = await handle_user_spend(sender.id, 'content', 'video123')")
        print("   await event.reply(response)")
        print()
        print("4. Available actions:")
        print("   - start_command, first_dm, dm_reply")
        print("   - group_mention, group_reply")
        print("   - daily_bonus, invite_friend")
        print("   - premium_interaction, vip_activity")
        print()
        print("5. Available services for spending:")
        print("   - content (10 tokens), vip (25 tokens)")
        print("   - boost (5 tokens), nft (50 tokens)")
        print("   - priority_dm (15 tokens)")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_xp_bot_integration()) 