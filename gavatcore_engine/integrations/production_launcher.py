#!/usr/bin/env python3
"""
GavatCore Engine Production Launcher
====================================

Complete integrated system launcher with all modules working together.
"""

import asyncio
import json
import os
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gavatcore_engine.config import get_settings
from gavatcore_engine.logger import get_logger
from gavatcore_engine.redis_state import redis_state
from gavatcore_engine.message_pool import message_pool
from gavatcore_engine.telegram_client import telegram_client_pool, ClientConfig
from gavatcore_engine.scheduler_engine import scheduler_engine, ScheduledTask, TaskType
from gavatcore_engine.ai_blending import ai_blending
from gavatcore_engine.admin_commands import admin_commands

logger = get_logger(__name__)


class GavatCoreProductionLauncher:
    """Production launcher for complete GavatCore system."""
    
    def __init__(self):
        self.settings = get_settings()
        self.running = False
        self.background_tasks = set()
        
    async def initialize_system(self) -> bool:
        """Initialize all system components."""
        logger.info("🚀 Initializing GavatCore Engine Production System...")
        
        try:
            # 1. Initialize Redis
            logger.info("📡 Connecting to Redis...")
            await redis_state.connect()
            logger.info("✅ Redis connected successfully")
            
            # 2. Initialize Message Pool
            logger.info("📬 Initializing message pool...")
            await message_pool.initialize()
            logger.info("✅ Message pool initialized")
            
            # 3. Initialize Scheduler Engine
            logger.info("⏰ Initializing scheduler engine...")
            await scheduler_engine.initialize()
            logger.info("✅ Scheduler engine initialized")
            
            # 4. Initialize AI Blending
            logger.info("🧠 Initializing AI blending...")
            await ai_blending.initialize()
            logger.info("✅ AI blending initialized")
            
            # 5. Initialize Admin Commands
            logger.info("👑 Initializing admin commands...")
            await admin_commands.initialize()
            logger.info("✅ Admin commands initialized")
            
            # 6. Load and configure Telegram bots
            logger.info("🤖 Loading Telegram bots...")
            await self.load_telegram_bots()
            
            # 7. Start background workers
            logger.info("⚙️ Starting background workers...")
            await self.start_background_workers()
            
            logger.info("🎉 GavatCore Engine Production System initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ System initialization failed: {e}")
            return False
    
    async def load_telegram_bots(self):
        """Load Telegram bots from existing configuration."""
        bots_loaded = 0
        
        try:
            # Try to load from existing config.py
            try:
                import config
                api_id = config.TELEGRAM_API_ID
                api_hash = config.TELEGRAM_API_HASH
                logger.info("📋 Loaded API credentials from config.py")
            except ImportError:
                logger.error("❌ config.py not found - using environment variables")
                api_id = os.getenv("TELEGRAM_API_ID")
                api_hash = os.getenv("TELEGRAM_API_HASH")
                
                if not api_id or not api_hash:
                    raise ValueError("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set")
            
            # Load active bot profiles
            bot_configs = []
            
            # According to memory: system works with yayincilara + xxxgeisha
            # BabaGavat is banned
            
            # 1. Yayıncılar Bot
            if hasattr(config, 'YAYINCILARA_PHONE'):
                bot_configs.append({
                    "session_name": "yayincilara",
                    "phone": config.YAYINCILARA_PHONE,
                    "device_model": "GavatCore Yayıncılar Bot",
                    "description": "Ana yayıncı bot sistemi"
                })
            
            # 2. XXXGeisha Bot
            if hasattr(config, 'XXXGEISHA_PHONE'):
                bot_configs.append({
                    "session_name": "xxxgeisha", 
                    "phone": config.XXXGEISHA_PHONE,
                    "device_model": "GavatCore XXXGeisha Bot",
                    "description": "Geisha karakter botu"
                })
            
            # 3. Load from profiles directory
            profiles_dir = Path("data/profiles")
            if profiles_dir.exists():
                for profile_file in profiles_dir.glob("*.json"):
                    # Skip banned profiles
                    if profile_file.name.endswith(".banned"):
                        logger.info(f"⚠️ Skipping banned profile: {profile_file.name}")
                        continue
                    
                    try:
                        with open(profile_file, 'r', encoding='utf-8') as f:
                            profile_data = json.load(f)
                        
                        if profile_data.get('active', True) and 'phone' in profile_data:
                            bot_configs.append({
                                "session_name": profile_file.stem,
                                "phone": profile_data['phone'],
                                "device_model": f"GavatCore {profile_data.get('name', profile_file.stem).title()} Bot",
                                "description": profile_data.get('description', 'Profile bot')
                            })
                            
                    except Exception as e:
                        logger.error(f"❌ Error loading profile {profile_file}: {e}")
            
            # Initialize bots
            for bot_config in bot_configs:
                logger.info(f"🤖 Initializing {bot_config['session_name']} - {bot_config['description']}")
                
                client_config = ClientConfig(
                    session_name=bot_config["session_name"],
                    api_id=int(api_id),
                    api_hash=api_hash,
                    phone=bot_config["phone"],
                    device_model=bot_config["device_model"],
                    connection_retries=3,
                    retry_delay=5,
                    auto_reconnect=True
                )
                
                success = await telegram_client_pool.add_client(client_config)
                
                if success:
                    bots_loaded += 1
                    logger.info(f"✅ {bot_config['session_name']} loaded successfully")
                    
                    # Store bot info in Redis
                    await redis_state.hset(
                        f"bot_info:{bot_config['session_name']}",
                        "config",
                        json.dumps({
                            "session_name": bot_config["session_name"],
                            "device_model": bot_config["device_model"],
                            "description": bot_config["description"],
                            "loaded_at": datetime.utcnow().isoformat()
                        })
                    )
                else:
                    logger.error(f"❌ Failed to load {bot_config['session_name']}")
            
            logger.info(f"🎯 Total bots loaded: {bots_loaded}/{len(bot_configs)}")
            
            # Store pool info
            pool_stats = await telegram_client_pool.get_pool_stats()
            await redis_state.hset(
                "system_info",
                "telegram_pool",
                json.dumps(pool_stats, default=str)
            )
            
        except Exception as e:
            logger.error(f"❌ Error loading Telegram bots: {e}")
            raise
    
    async def start_background_workers(self):
        """Start all background worker tasks."""
        
        # 1. Message Processing Worker
        task1 = asyncio.create_task(self.message_processing_worker())
        self.background_tasks.add(task1)
        logger.info("✅ Message processing worker started")
        
        # 2. Scheduler Worker
        task2 = asyncio.create_task(self.scheduler_worker())
        self.background_tasks.add(task2)
        logger.info("✅ Scheduler worker started")
        
        # 3. Health Monitoring Worker
        task3 = asyncio.create_task(self.health_monitoring_worker())
        self.background_tasks.add(task3)
        logger.info("✅ Health monitoring worker started")
        
        # 4. Statistics Worker
        task4 = asyncio.create_task(self.statistics_worker())
        self.background_tasks.add(task4)
        logger.info("✅ Statistics worker started")
        
        # 5. AI Conversation Worker
        task5 = asyncio.create_task(self.ai_conversation_worker())
        self.background_tasks.add(task5)
        logger.info("✅ AI conversation worker started")
        
        logger.info(f"🎯 Total background workers: {len(self.background_tasks)}")
    
    async def message_processing_worker(self):
        """Process messages from the message pool."""
        logger.info("📬 Message processing worker active")
        
        while self.running:
            try:
                # Get next priority message
                message = await message_pool.get_next_message()
                
                if message:
                    logger.info(f"📤 Processing message {message.id} to {message.target_entity}")
                    
                    # Get appropriate client
                    client = await telegram_client_pool.get_client(message.session_name)
                    
                    if client:
                        # AI enhance message if enabled
                        if message.ai_enhanced:
                            enhanced_content = await ai_blending.generate_response(
                                message.content,
                                message.session_name,
                                message.target_entity
                            )
                            if enhanced_content:
                                message.content = enhanced_content
                        
                        # Send message
                        result = await client.send_message(
                            entity=message.target_entity,
                            message=message.content,
                            parse_mode=message.parse_mode,
                            silent=message.silent
                        )
                        
                        if result.success:
                            await message_pool.update_message_status(message.id, "sent")
                            await redis_state.increment_counter("messages_sent_total")
                            logger.info(f"✅ Message {message.id} sent successfully")
                        else:
                            await message_pool.update_message_status(message.id, "failed")
                            await redis_state.increment_counter("messages_failed_total")
                            logger.error(f"❌ Message {message.id} failed: {result.error}")
                    else:
                        logger.error(f"❌ No available client for message {message.id}")
                        await message_pool.update_message_status(message.id, "failed")
                else:
                    # No messages, short sleep
                    await asyncio.sleep(0.1)
                    
            except asyncio.CancelledError:
                logger.info("📬 Message processing worker cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Message processing worker error: {e}")
                await asyncio.sleep(1)
    
    async def scheduler_worker(self):
        """Process scheduled tasks."""
        logger.info("⏰ Scheduler worker active")
        
        while self.running:
            try:
                await scheduler_engine.process_pending_tasks()
                await asyncio.sleep(1)  # Check every second
                
            except asyncio.CancelledError:
                logger.info("⏰ Scheduler worker cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Scheduler worker error: {e}")
                await asyncio.sleep(5)
    
    async def health_monitoring_worker(self):
        """Monitor system health."""
        logger.info("🏥 Health monitoring worker active")
        
        while self.running:
            try:
                # Check Redis connection
                try:
                    await redis_state.ping()
                    await redis_state.set("health_check:redis", "ok")
                except Exception as e:
                    logger.error(f"❌ Redis health check failed: {e}")
                    await redis_state.set("health_check:redis", "failed")
                
                # Check Telegram clients
                pool_stats = await telegram_client_pool.get_pool_stats()
                
                if pool_stats['connected_clients'] == 0 and pool_stats['total_clients'] > 0:
                    logger.error("⚠️ No Telegram clients connected!")
                    await redis_state.set("health_check:telegram", "no_clients")
                else:
                    await redis_state.set("health_check:telegram", "ok")
                
                # Store health summary
                health_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "telegram_clients": f"{pool_stats['connected_clients']}/{pool_stats['total_clients']}",
                    "message_pool": "active",
                    "scheduler": "active",
                    "ai_blending": "active"
                }
                
                await redis_state.hset("system_health", "summary", json.dumps(health_data))
                
                # Sleep for 5 minutes
                await asyncio.sleep(300)
                
            except asyncio.CancelledError:
                logger.info("🏥 Health monitoring worker cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Health monitoring worker error: {e}")
                await asyncio.sleep(300)
    
    async def statistics_worker(self):
        """Update system statistics."""
        logger.info("📊 Statistics worker active")
        
        while self.running:
            try:
                # Collect statistics
                pool_stats = await telegram_client_pool.get_pool_stats()
                message_stats = await message_pool.get_statistics()
                scheduler_stats = await scheduler_engine.get_statistics()
                
                # Get counter values
                messages_sent = await redis_state.get("counter:messages_sent_total") or 0
                messages_failed = await redis_state.get("counter:messages_failed_total") or 0
                
                system_stats = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "counters": {
                        "messages_sent": int(messages_sent),
                        "messages_failed": int(messages_failed)
                    },
                    "telegram_pool": pool_stats,
                    "message_pool": message_stats,
                    "scheduler": scheduler_stats
                }
                
                # Store statistics
                await redis_state.hset("system_stats", "latest", json.dumps(system_stats, default=str))
                
                # Store hourly snapshot
                hour_key = datetime.utcnow().strftime("%Y-%m-%d_%H")
                await redis_state.hset("system_stats", f"hourly:{hour_key}", json.dumps(system_stats, default=str))
                
                logger.info(f"📊 Statistics updated - Sent: {messages_sent}, Failed: {messages_failed}")
                
                # Sleep for 1 minute
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                logger.info("📊 Statistics worker cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Statistics worker error: {e}")
                await asyncio.sleep(60)
    
    async def ai_conversation_worker(self):
        """Handle AI conversation generation."""
        logger.info("🧠 AI conversation worker active")
        
        while self.running:
            try:
                # Check for pending AI tasks
                await ai_blending.process_pending_conversations()
                
                # Sleep briefly
                await asyncio.sleep(2)
                
            except asyncio.CancelledError:
                logger.info("🧠 AI conversation worker cancelled")
                break
            except Exception as e:
                logger.error(f"❌ AI conversation worker error: {e}")
                await asyncio.sleep(5)
    
    async def run(self):
        """Run the production system."""
        self.running = True
        
        # Initialize system
        success = await self.initialize_system()
        
        if not success:
            logger.error("❌ System initialization failed - exiting")
            return False
        
        # Store system startup info
        startup_info = {
            "started_at": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "environment": "production",
            "components": ["redis", "message_pool", "scheduler", "telegram_clients", "ai_blending", "admin_commands"]
        }
        
        await redis_state.hset("system_info", "startup", json.dumps(startup_info))
        
        logger.info("🎉 GavatCore Engine Production System is now running!")
        
        try:
            # Keep running until interrupted
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown signal received")
        except Exception as e:
            logger.error(f"❌ System error: {e}")
        finally:
            await self.shutdown()
        
        return True
    
    async def shutdown(self):
        """Graceful shutdown of all components."""
        logger.info("🛑 Starting graceful shutdown...")
        
        self.running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Shutdown components
        try:
            await scheduler_engine.shutdown()
            logger.info("✅ Scheduler engine shut down")
        except Exception as e:
            logger.error(f"❌ Scheduler shutdown error: {e}")
        
        try:
            await telegram_client_pool.shutdown()
            logger.info("✅ Telegram client pool shut down")
        except Exception as e:
            logger.error(f"❌ Telegram pool shutdown error: {e}")
        
        try:
            await message_pool.shutdown()
            logger.info("✅ Message pool shut down")
        except Exception as e:
            logger.error(f"❌ Message pool shutdown error: {e}")
        
        try:
            await redis_state.disconnect()
            logger.info("✅ Redis disconnected")
        except Exception as e:
            logger.error(f"❌ Redis disconnect error: {e}")
        
        logger.info("🏁 GavatCore Engine shutdown complete")


async def main():
    """Main entry point."""
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        if launcher.running:
            launcher.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run launcher
    launcher = GavatCoreProductionLauncher()
    
    try:
        success = await launcher.run()
        
        if success:
            logger.info("✅ GavatCore Engine completed successfully")
            sys.exit(0)
        else:
            logger.error("❌ GavatCore Engine failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc() 