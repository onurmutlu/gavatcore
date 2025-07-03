#!/usr/bin/env python3
"""
🔥 EXTREME MODE LITE LAUNCHER 🔥

GAVATCore Extreme Mode Lite - SQLite ile çalışan versiyon.
Docker gerektirmez, daha basit kurulum.
"""

import os
import sys
import time
import asyncio
import subprocess
from pathlib import Path

def create_env_file():
    """Create .env file with template values"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("📝 Creating .env file...")
        
        env_content = """# Telegram API
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
ADMIN_BOT_TOKEN=your_telegram_bot_token_here
GAVATCORE_SYSTEM_PHONE=your_phone_number_here

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# SQLite (Docker'a gerek yok!)
DATABASE_URL=sqlite+aiosqlite:///extreme_mode.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=extreme_mode.log

# Performance
MAX_CONCURRENT_BOTS=3
MESSAGE_BATCH_SIZE=50
AI_CACHE_TTL=3600
RATE_LIMIT_SECONDS=30
"""
        
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created successfully")
        print("⚠️  Please edit .env file with your actual values!")
        
        # Load the env file
        import dotenv
        dotenv.load_dotenv()
    else:
        print("✅ .env file found")
        # Load existing env file
        import dotenv
        dotenv.load_dotenv()

def install_dependencies():
    """Install missing dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Essential packages
    packages = [
        "python-dotenv",
        "Telethon",
        "openai",
        "aiosqlite",  # SQLite async driver
        "structlog",
        "cachetools",
        "backoff",
        "aiofiles"
    ]
    
    for package in packages:
        try:
            __import__(package.lower().replace("-", "_"))
            print(f"✅ {package} already installed")
        except ImportError:
            print(f"📥 Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
    
    print("\n✅ All dependencies installed!")

def main():
    """Main launcher"""
    print("""
💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀
💀                                                               💀
💀         🔥 EXTREME MODE LITE - NO DOCKER! 🔥                 💀
💀                                                               💀
💀          💣 SQLite ile DATABASE LOCKED YOK! 💣                💀
💀                                                               💀
💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀
    """)
    
    # Create .env file if not exists
    create_env_file()
    
    # Install dependencies
    install_dependencies()
    
    # Check environment variables
    print("\n🔍 Checking environment variables...")
    required_env = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 'OPENAI_API_KEY']
    missing = [env for env in required_env if not os.getenv(env) or os.getenv(env) == f"your_{env.lower()}_here"]
    
    if missing:
        print(f"❌ Missing or template environment variables: {', '.join(missing)}")
        print("\nPlease edit your .env file with actual values")
        return
    
    print("✅ All environment variables set")
    
    # Launch extreme mode lite
    print("\n🚀 Launching EXTREME MODE LITE...")
    print("💀 NO DOCKER, NO DATABASE LOCKS! 💀\n")
    
    try:
        # Import and run lite version
        from extreme_mode_lite import main as extreme_main
        asyncio.run(extreme_main())
    except KeyboardInterrupt:
        print("\n\n💀 EXTREME MODE TERMINATED BY USER")
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Creating extreme_mode_lite.py...")
        # Create lite version if not exists
        create_lite_version()
        print("\n✅ extreme_mode_lite.py created! Run again.")
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

def create_lite_version():
    """Create SQLite-based lite version"""
    lite_content = '''#!/usr/bin/env python3
"""
💀 EXTREME MODE LITE - SQLite Version 💀

No Docker needed! SQLite ile çalışan versiyon.
"""

import asyncio
import os
import sys
import time
import random
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Database
import aiosqlite

# AI
from openai import AsyncOpenAI

# Telegram
from telethon import TelegramClient, events

# Utils
import structlog
from cachetools import TTLCache

logger = structlog.get_logger(__name__)

# Bot Personalities
BOT_PERSONALITIES = {
    "babagavat": {
        "name": "BabaGAVAT",
        "session_file": "sessions/babagavat_conversation", 
        "style": "sokak lideri, para babası, dominant, alfa",
        "system_prompt": """Sen BabaGAVAT'sın. Sokak lideri, para babası, alfa erkeksin.
Kısa, etkili, sokak dili kullan. Para ve güç konularında dominant ol."""
    }
}

class ExtremeLiteBot:
    """Simplified bot with SQLite"""
    
    def __init__(self):
        self.db_path = "extreme_mode.db"
        self.ai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.cache = TTLCache(maxsize=100, ttl=3600)
        self.client = None
        
    async def initialize(self):
        """Initialize bot and database"""
        # Create database
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER,
                    user_id INTEGER,
                    message TEXT,
                    response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
        
        # Initialize Telegram
        from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
        
        session_file = BOT_PERSONALITIES["babagavat"]["session_file"]
        self.client = TelegramClient(session_file, TELEGRAM_API_ID, TELEGRAM_API_HASH)
        
        await self.client.start()
        me = await self.client.get_me()
        logger.info(f"Bot initialized: @{me.username}")
        
        # Setup handler
        @self.client.on(events.NewMessage)
        async def handler(event):
            try:
                # Skip own messages
                if event.sender_id == me.id:
                    return
                
                # Random reply chance
                if random.random() > 0.3:
                    return
                
                # Generate response
                response = await self.generate_response(event.message.message)
                if response:
                    await event.reply(response)
                    
                    # Log to database
                    await self.log_message(
                        event.chat_id,
                        event.sender_id,
                        event.message.message,
                        response
                    )
                    
            except Exception as e:
                logger.error(f"Handler error: {e}")
    
    async def generate_response(self, message: str) -> str:
        """Generate AI response"""
        try:
            # Check cache
            cache_key = hash(message.lower())
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Generate with OpenAI
            response = await self.ai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": BOT_PERSONALITIES["babagavat"]["system_prompt"]},
                    {"role": "user", "content": message}
                ],
                max_tokens=150,
                temperature=0.8
            )
            
            result = response.choices[0].message.content.strip()
            
            # Cache result
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return None
    
    async def log_message(self, group_id: int, user_id: int, message: str, response: str):
        """Log message to database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO messages (group_id, user_id, message, response) VALUES (?, ?, ?, ?)",
                    (group_id, user_id, message, response)
                )
                await db.commit()
        except Exception as e:
            logger.error(f"Database error: {e}")
    
    async def run(self):
        """Run the bot"""
        await self.initialize()
        print("🚀 Bot is running...")
        await self.client.run_until_disconnected()

async def main():
    """Main function"""
    bot = ExtremeLiteBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    with open("extreme_mode_lite.py", "w") as f:
        f.write(lite_content)

if __name__ == "__main__":
    main() 