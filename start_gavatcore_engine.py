#!/usr/bin/env python3
"""
GavatCore Engine Starter
========================

Complete integrated system starter script.
Starts all components together with proper initialization.
"""

import asyncio
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

def print_banner():
    """Print startup banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ██████╗  █████╗ ██╗   ██╗ █████╗ ████████╗ ██████╗ ██████╗ ║
║  ██╔════╝ ██╔══██╗██║   ██║██╔══██╗╚══██╔══╝██╔════╝██╔═══██╗║
║  ██║  ███╗███████║██║   ██║███████║   ██║   ██║     ██║   ██║║
║  ██║   ██║██╔══██║╚██╗ ██╔╝██╔══██║   ██║   ██║     ██║   ██║║
║  ╚██████╔╝██║  ██║ ╚████╔╝ ██║  ██║   ██║   ╚██████╗╚██████╔╝║
║   ╚═════╝ ╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═════╝ ║
║                                                              ║
║                    ENGINE v1.0.0 - PRODUCTION               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print("🚀 GavatCore Auto-Messaging Engine")
    print("⚡ Integrated System with Telegram + Scheduler + AI")
    print("🔗 Redis State Management + Message Pool + Admin Commands")
    print("="*70)


def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "fastapi", "uvicorn", "telethon", "redis", "aioredis",
        "structlog", "croniter", "pydantic", "asyncpg"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package} - MISSING")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Run: pip install -r gavatcore_engine/requirements.txt")
        return False
    
    print("✅ All dependencies OK")
    return True


def check_redis_connection():
    """Check Redis connection."""
    print("📡 Checking Redis connection...")
    
    try:
        import redis
        
        # Try default connection
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        print("✅ Redis connection OK")
        return True
        
    except redis.ConnectionError:
        print("❌ Redis connection failed")
        print("💡 Make sure Redis server is running:")
        print("   - macOS: brew services start redis")
        print("   - Ubuntu: sudo systemctl start redis")
        print("   - Docker: docker run -d -p 6379:6379 redis:alpine")
        return False
    except Exception as e:
        print(f"❌ Redis check error: {e}")
        return False


def check_config_files():
    """Check if required config files exist."""
    print("📋 Checking configuration files...")
    
    config_files = {
        "config.py": "Main configuration file",
        "gavatcore_engine/": "Engine directory",
        "data/profiles/": "Bot profiles directory",
        "sessions/": "Telegram sessions directory"
    }
    
    all_ok = True
    
    for file_path, description in config_files.items():
        path = Path(file_path)
        
        if path.exists():
            print(f"   ✅ {file_path} - {description}")
        else:
            print(f"   ⚠️ {file_path} - {description} (will be created)")
            
            # Create directories if needed
            if file_path.endswith("/"):
                path.mkdir(parents=True, exist_ok=True)
                print(f"      📁 Created directory: {file_path}")
    
    # Check for API credentials
    try:
        import config
        if hasattr(config, 'TELEGRAM_API_ID') and hasattr(config, 'TELEGRAM_API_HASH'):
            print("   ✅ Telegram API credentials found")
        else:
            print("   ⚠️ Telegram API credentials missing in config.py")
            all_ok = False
    except ImportError:
        print("   ⚠️ config.py not found - some features may not work")
    
    return all_ok


def setup_environment():
    """Setup required environment."""
    print("⚙️ Setting up environment...")
    
    # Create required directories
    directories = [
        "sessions",
        "data/profiles", 
        "data/analytics",
        "data/conversations",
        "logs",
        "reports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   📁 {directory}/")
    
    # Set Python path
    current_dir = Path.cwd()
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    print("✅ Environment setup complete")


async def start_integrated_system():
    """Start the complete integrated system."""
    print("🚀 Starting GavatCore Engine Integrated System...")
    
    try:
        # Import and run the production launcher
        from gavatcore_engine.integrations.production_launcher import GavatCoreProductionLauncher
        
        launcher = GavatCoreProductionLauncher()
        
        # Setup signal handlers
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, shutting down...")
            launcher.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Run the system
        success = await launcher.run()
        
        if success:
            print("✅ GavatCore Engine completed successfully")
            return True
        else:
            print("❌ GavatCore Engine failed to start")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all modules are properly installed")
        return False
    except Exception as e:
        print(f"❌ System error: {e}")
        import traceback
        traceback.print_exc()
        return False


def start_fastapi_server():
    """Start FastAPI server as alternative."""
    print("🌐 Starting FastAPI server...")
    
    try:
        import uvicorn
        
        # Run FastAPI server
        uvicorn.run(
            "gavatcore_engine.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI server error: {e}")
        return False


def show_startup_menu():
    """Show startup options menu."""
    print("\n🎯 Startup Options:")
    print("1. 🚀 Start Complete Integrated System (Recommended)")
    print("2. 🌐 Start FastAPI Server Only")
    print("3. 🧪 Test System Components")
    print("4. 📊 Show System Status")
    print("5. 🛑 Exit")
    
    choice = input("\nSelect option (1-5): ").strip()
    return choice


async def test_system_components():
    """Test system components."""
    print("🧪 Testing System Components...")
    
    try:
        # Test Redis
        print("\n📡 Testing Redis...")
        from gavatcore_engine.redis_state import redis_state
        await redis_state.connect()
        await redis_state.set("test_key", "test_value")
        value = await redis_state.get("test_key")
        if value == "test_value":
            print("   ✅ Redis test passed")
        else:
            print("   ❌ Redis test failed")
        await redis_state.delete("test_key")
        
        # Test Message Pool
        print("\n📬 Testing Message Pool...")
        from gavatcore_engine.message_pool import message_pool, Message, MessageType
        await message_pool.initialize()
        
        test_message = Message(
            target_entity="test",
            content="Test message",
            message_type=MessageType.TEXT
        )
        
        message_id = await message_pool.add_message(test_message)
        if message_id:
            print("   ✅ Message Pool test passed")
        else:
            print("   ❌ Message Pool test failed")
        
        # Test Scheduler
        print("\n⏰ Testing Scheduler...")
        from gavatcore_engine.scheduler_engine import scheduler_engine
        await scheduler_engine.initialize()
        stats = await scheduler_engine.get_statistics()
        if isinstance(stats, dict):
            print("   ✅ Scheduler test passed")
        else:
            print("   ❌ Scheduler test failed")
        
        # Test AI Blending
        print("\n🧠 Testing AI Blending...")
        from gavatcore_engine.ai_blending import ai_blending
        await ai_blending.initialize()
        response = await ai_blending.generate_response("test", "test_bot", "test_entity")
        print("   ✅ AI Blending test passed")
        
        print("\n✅ All component tests completed")
        
    except Exception as e:
        print(f"❌ Component test error: {e}")
        import traceback
        traceback.print_exc()


async def show_system_status():
    """Show current system status."""
    print("📊 System Status Check...")
    
    try:
        from gavatcore_engine.redis_state import redis_state
        
        # Check Redis
        try:
            await redis_state.connect()
            
            # Get system stats
            stats_data = await redis_state.hget("system_stats", "latest")
            if stats_data:
                if isinstance(stats_data, bytes):
                    stats_data = stats_data.decode()
                stats = json.loads(stats_data)
                
                print(f"\n📊 Latest Statistics:")
                print(f"   Timestamp: {stats.get('timestamp', 'N/A')}")
                
                if 'counters' in stats:
                    counters = stats['counters']
                    print(f"   Messages Sent: {counters.get('messages_sent', 0)}")
                    print(f"   Messages Failed: {counters.get('messages_failed', 0)}")
                
                if 'telegram_pool' in stats:
                    pool = stats['telegram_pool']
                    print(f"   Telegram Clients: {pool.get('connected_clients', 0)}/{pool.get('total_clients', 0)}")
            else:
                print("   ⚠️ No system statistics available")
            
            # Check health
            health_data = await redis_state.hget("system_health", "summary")
            if health_data:
                if isinstance(health_data, bytes):
                    health_data = health_data.decode()
                health = json.loads(health_data)
                
                print(f"\n🏥 Health Status:")
                print(f"   Timestamp: {health.get('timestamp', 'N/A')}")
                print(f"   Telegram: {health.get('telegram_clients', 'N/A')}")
                print(f"   Message Pool: {health.get('message_pool', 'N/A')}")
                print(f"   Scheduler: {health.get('scheduler', 'N/A')}")
            else:
                print("   ⚠️ No health data available")
            
        except Exception as e:
            print(f"❌ Status check error: {e}")
            
    except Exception as e:
        print(f"❌ Redis connection error: {e}")


async def main():
    """Main function."""
    
    # Print banner
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed")
        sys.exit(1)
    
    # Check Redis
    if not check_redis_connection():
        print("\n❌ Redis check failed")
        sys.exit(1)
    
    # Check config
    check_config_files()
    
    # Setup environment
    setup_environment()
    
    print("\n✅ Pre-flight checks completed")
    
    # Main loop
    while True:
        choice = show_startup_menu()
        
        if choice == "1":
            # Start integrated system
            success = await start_integrated_system()
            if not success:
                print("❌ System failed to start")
            break
            
        elif choice == "2":
            # Start FastAPI only
            print("\n🌐 Starting FastAPI server...")
            print("📡 API will be available at: http://localhost:8000")
            print("📖 API docs: http://localhost:8000/docs")
            start_fastapi_server()
            break
            
        elif choice == "3":
            # Test components
            await test_system_components()
            input("\nPress Enter to continue...")
            
        elif choice == "4":
            # Show status
            await show_system_status()
            input("\nPress Enter to continue...")
            
        elif choice == "5":
            # Exit
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice, please try again")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc() 