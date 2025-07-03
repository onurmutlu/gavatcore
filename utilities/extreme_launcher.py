#!/usr/bin/env python3
"""
🔥 EXTREME MODE LAUNCHER 🔥

GAVATCore Extreme Mode için gelişmiş launcher.
Tüm bağımlılıkları kontrol eder ve sistemi başlatır.
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

# PostgreSQL
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=postgres
PG_DATABASE=extreme_mode

# MongoDB
MONGO_URI=mongodb://localhost:27017

# Redis
REDIS_URI=redis://localhost:6379

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

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import asyncpg
        import motor
        import redis.asyncio
        import openai
        import telethon
        import structlog
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nInstall with: pip install -r requirements_extreme.txt")
        return False

def main():
    """Main launcher"""
    print("""
💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀
💀                                                               💀
💀         🔥 EXTREME MODE LAUNCHER 🔥                          💀
💀                                                               💀
💀          💣 DATABASE LOCKED TARIH OLUYOR! 💣                  💀
💀                                                               💀
💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀
    """)
    
    # Create .env file if not exists
    create_env_file()
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check environment variables
    print("\n🔍 Checking environment variables...")
    required_env = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 'OPENAI_API_KEY']
    missing = [env for env in required_env if not os.getenv(env) or os.getenv(env) == f"your_{env.lower()}_here"]
    
    if missing:
        print(f"❌ Missing or template environment variables: {', '.join(missing)}")
        print("\nPlease edit your .env file with actual values")
        return
    
    print("✅ All environment variables set")
    
    # Launch extreme mode
    print("\n🚀 Launching EXTREME MODE...")
    print("💀 DATABASE LOCKED PROBLEM IS HISTORY! 💀\n")
    
    try:
        # Import and run
        from extreme_mode_final import main as extreme_main
        asyncio.run(extreme_main())
    except KeyboardInterrupt:
        print("\n\n💀 EXTREME MODE TERMINATED BY USER")
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 