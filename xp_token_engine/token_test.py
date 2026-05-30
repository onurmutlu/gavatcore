#!/usr/bin/env python3
"""
🧪 GavatCoin Token Test CLI v1.0 🧪

XP kazanma → token biriktirme → içerik alma test sistemi
OnlyVips v6.0 Token Economy Test Suite
"""

import asyncio
import json
import logging
from typing import Dict, Any
from .token_manager import get_token_manager
from .spend_handlers import SpendHandlers, spend_token_for_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TokenTestCLI:
    """Interactive CLI for testing token system"""
    
    def __init__(self):
        self.user_id: str = ""
        self.running = True
    
    async def start(self):
        """Start the interactive CLI"""
        print("🪙 " + "="*50)
        print("🚀 GavatCoin Token Test CLI v1.0")
        print("💰 OnlyVips v6.0 Token Economy Tester")
        print("🪙 " + "="*50)
        print()
        
        # Get user ID
        self.user_id = input("👤 Enter your user ID: ").strip()
        if not self.user_id:
            print("❌ User ID is required!")
            return
        
        print(f"✅ Welcome, {self.user_id}!")
        print()
        
        # Initialize token manager
        async with get_token_manager() as tm:
            self.token_manager = tm
            
            # Give initial 50 XP → convert to 50 tokens
            print("🎁 Giving you 50 XP as welcome bonus...")
            new_balance = await tm.xp_to_token(self.user_id, 50)
            print(f"💰 Converted 50 XP → 50 tokens! Current balance: {new_balance}")
            print()
            
            # Start main loop
            await self.main_loop()
    
    async def main_loop(self):
        """Main interactive loop"""
        while self.running:
            await self.show_menu()
            choice = input("👉 Enter your choice: ").strip()
            
            if choice == "1":
                await self.buy_content()
            elif choice == "2":
                await self.upgrade_to_vip()
            elif choice == "3":
                await self.boost_quest()
            elif choice == "4":
                await self.unlock_nft()
            elif choice == "5":
                await self.priority_dm()
            elif choice == "6":
                await self.show_balance()
            elif choice == "7":
                await self.show_logs()
            elif choice == "8":
                await self.add_xp()
            elif choice == "9":
                await self.show_stats()
            elif choice == "0":
                self.running = False
                print("👋 Thanks for testing GavatCoin! Goodbye!")
            else:
                print("❌ Invalid choice! Please try again.")
            
            if self.running:
                input("\n⏸️  Press Enter to continue...")
                print()
    
    async def show_menu(self):
        """Display main menu"""
        balance = await self.token_manager.get_balance(self.user_id)
        affordable = await SpendHandlers.get_affordable_services(self.user_id)
        
        print("💰 " + "="*50)
        print(f"💳 Current Balance: {balance} tokens")
        print("💰 " + "="*50)
        print()
        print("🛒 SPENDING OPTIONS:")
        print(f"  1. 🎬 Buy Content (10 tokens) {'✅' if affordable['content']['affordable'] else '❌'}")
        print(f"  2. 👑 Upgrade to VIP (25 tokens) {'✅' if affordable['vip']['affordable'] else '❌'}")
        print(f"  3. ⚡ Boost Quest (5 tokens) {'✅' if affordable['boost']['affordable'] else '❌'}")
        print(f"  4. 🎨 Unlock NFT Badge (50 tokens) {'✅' if affordable['nft']['affordable'] else '❌'}")
        print(f"  5. 📨 Priority DM Access (15 tokens) {'✅' if affordable['priority_dm']['affordable'] else '❌'}")
        print()
        print("📊 INFO OPTIONS:")
        print("  6. 💳 Show Balance")
        print("  7. 📜 Show Transaction Logs")
        print("  8. 🎁 Add XP (Convert to Tokens)")
        print("  9. 📈 Show System Stats")
        print()
        print("  0. 🚪 Exit")
        print()
    
    async def buy_content(self):
        """Buy premium content"""
        print("🎬 " + "="*30)
        print("🎬 BUY PREMIUM CONTENT")
        print("🎬 " + "="*30)
        
        content_id = input("📋 Enter content ID (or press Enter for default): ").strip()
        if not content_id:
            content_id = "premium_video_001"
        
        success, message = await spend_token_for_service(
            self.user_id, 
            "content", 
            content_id=content_id
        )
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
        
        await self.show_updated_balance()
    
    async def upgrade_to_vip(self):
        """Upgrade to VIP status"""
        print("👑 " + "="*30)
        print("👑 UPGRADE TO VIP")
        print("👑 " + "="*30)
        
        success, message = await spend_token_for_service(self.user_id, "vip")
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
        
        await self.show_updated_balance()
    
    async def boost_quest(self):
        """Boost daily quest"""
        print("⚡ " + "="*30)
        print("⚡ BOOST DAILY QUEST")
        print("⚡ " + "="*30)
        
        success, message = await spend_token_for_service(self.user_id, "boost")
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
        
        await self.show_updated_balance()
    
    async def unlock_nft(self):
        """Unlock NFT badge"""
        print("🎨 " + "="*30)
        print("🎨 UNLOCK NFT BADGE")
        print("🎨 " + "="*30)
        
        success, message = await spend_token_for_service(self.user_id, "nft")
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
        
        await self.show_updated_balance()
    
    async def priority_dm(self):
        """Activate priority DM"""
        print("📨 " + "="*30)
        print("📨 PRIORITY DM ACCESS")
        print("📨 " + "="*30)
        
        success, message = await spend_token_for_service(self.user_id, "priority_dm")
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
        
        await self.show_updated_balance()
    
    async def show_balance(self):
        """Show current balance"""
        balance = await self.token_manager.get_balance(self.user_id)
        print(f"💳 Current balance: {balance} tokens")
    
    async def show_logs(self):
        """Show transaction logs"""
        print("📜 " + "="*30)
        print("📜 TRANSACTION LOGS")
        print("📜 " + "="*30)
        
        logs = await self.token_manager.get_logs(self.user_id, limit=10)
        
        if not logs:
            print("📭 No transactions found")
            return
        
        for log in logs:
            print(json.dumps(log, indent=2))
            print("-" * 30)
    
    async def add_xp(self):
        """Add XP and convert to tokens"""
        print("🎁 " + "="*30)
        print("🎁 ADD XP → CONVERT TO TOKENS")
        print("🎁 " + "="*30)
        
        try:
            xp_str = input("💎 Enter XP amount: ").strip()
            xp = int(xp_str)
            
            if xp <= 0:
                print("❌ XP amount must be positive!")
                return
            
            new_balance = await self.token_manager.xp_to_token(self.user_id, xp)
            print(f"✅ Converted {xp} XP → {xp} tokens!")
            print(f"💰 New balance: {new_balance} tokens")
            
        except ValueError:
            print("❌ Please enter a valid number!")
    
    async def show_stats(self):
        """Show system stats"""
        print("📈 " + "="*30)
        print("📈 SYSTEM STATISTICS")
        print("📈 " + "="*30)
        
        stats = await self.token_manager.get_all_users_stats()
        print(json.dumps(stats, indent=2))
    
    async def show_updated_balance(self):
        """Show updated balance after transaction"""
        balance = await self.token_manager.get_balance(self.user_id)
        print(f"💰 Updated balance: {balance} tokens")

# Main execution
async def main():
    """Main function"""
    cli = TokenTestCLI()
    await cli.start()

def run_test():
    """Run the test CLI"""
    try:
        # Install aiosqlite if not available
        import aiosqlite  # noqa
    except ImportError:
        print("❌ aiosqlite not found. Installing...")
        import subprocess
        subprocess.run(["pip", "install", "aiosqlite"])
        import aiosqlite  # noqa
    
    # Run the async main function
    asyncio.run(main())

if __name__ == "__main__":
    run_test() 