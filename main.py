from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🔥 GAVATCORE TELETHON USERBOT SYSTEM 🔥
Production-grade multi-session userbot manager
Author: GavatCore Team
Version: 3.0
"""

import asyncio
import sys
import os
import signal
import logging
from typing import Dict, List, Optional
from datetime import datetime
import structlog

# GavatCore imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from userbot_session import UserbotSession
from utils.config_manager import ConfigManager
from utils.health_monitor import HealthMonitor

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
    context_class=dict,
    logger_factory=structlog.WriteLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("gavatcore.main")

class GavatCoreUserbotManager:
    """
    🎯 GAVATCORE USERBOT MANAGER
    
    Manages multiple Telegram userbot sessions with different roles:
    - @gawatbaba: System admin, commands, coin control
    - @yayincilara: GPT persona, user interactions
    - @xxxgeisha: Dominant AI, group replies, DM responses
    """
    
    def __init__(self):
        self.config = ConfigManager()
        self.sessions: Dict[str, UserbotSession] = {}
        self.health_monitor = HealthMonitor()
        self.running = False
        
        # Bot configurations
        self.bot_configs = {
            "gawatbaba": {
                "username": "gawatbaba",
                "phone": "+447832134241",
                "role": "admin",
                "handlers": ["admin_handler", "coin_handler"],
                "gpt_enabled": False,
                "reply_mode": "manual",
                "auto_reply": False,
                "scheduler_enabled": False,
                "description": "🔥 System Admin - Commands & Control"
            },
            "yayincilara": {
                "username": "yayincilara", 
                "phone": self.config.get("YAYINCILARA_PHONE", "+90XXXXXXXXXX"),
                "role": "gpt_persona",
                "handlers": ["gpt_handler", "common_handler"],
                "gpt_enabled": True,
                "reply_mode": "hybrid", 
                "auto_reply": True,
                "scheduler_enabled": True,
                "scheduler_interval": 300,  # 5 minutes
                "description": "🎮 GPT Persona - Yarı-Rus Gaming Girl"
            },
            "xxxgeisha": {
                "username": "xxxgeisha",
                "phone": self.config.get("XXXGEISHA_PHONE", "+90YYYYYYYYY"), 
                "role": "dominant_ai",
                "handlers": ["gpt_handler", "seduction_handler"],
                "gpt_enabled": True,
                "reply_mode": "manualplus",
                "auto_reply": True,
                "scheduler_enabled": True,
                "scheduler_interval": 420,  # 7 minutes
                "description": "🌸 Dominant AI - Sexy & Sophisticated"
            }
        }
        
    async def initialize_sessions(self):
        """Initialize all userbot sessions"""
        logger.info("🚀 Initializing GavatCore userbot sessions...")
        
        for bot_name, config in self.bot_configs.items():
            try:
                logger.info(f"📱 Setting up {bot_name} session...", 
                          username=config['username'], role=config['role'])
                
                session = UserbotSession(
                    bot_name=bot_name,
                    config=config,
                    health_monitor=self.health_monitor
                )
                
                await session.initialize()
                self.sessions[bot_name] = session
                
                logger.info(f"✅ {bot_name} session initialized successfully",
                          bot=bot_name, phone=config['phone'])
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize {bot_name}: {str(e)}",
                           bot=bot_name, error=str(e))
                continue
        
        if not self.sessions:
            raise RuntimeError("❌ No userbot sessions could be initialized!")
            
        logger.info(f"🎉 {len(self.sessions)} userbot sessions ready!", 
                   active_bots=list(self.sessions.keys()))
    
    async def start_all_sessions(self):
        """Start all userbot sessions concurrently"""
        logger.info("🔥 Starting all userbot sessions...")
        
        # Create startup tasks
        startup_tasks = []
        for bot_name, session in self.sessions.items():
            task = asyncio.create_task(
                session.start(),
                name=f"start_{bot_name}"
            )
            startup_tasks.append(task)
        
        # Wait for all sessions to start
        results = await asyncio.gather(*startup_tasks, return_exceptions=True)
        
        # Check results
        successful_starts = 0
        for i, (bot_name, result) in enumerate(zip(self.sessions.keys(), results)):
            if isinstance(result, Exception):
                logger.error(f"❌ {bot_name} startup failed: {result}",
                           bot=bot_name, error=str(result))
            else:
                successful_starts += 1
                logger.info(f"✅ {bot_name} started successfully", bot=bot_name)
        
        logger.info(f"📊 Startup complete: {successful_starts}/{len(self.sessions)} sessions active")
        return successful_starts > 0
    
    async def stop_all_sessions(self):
        """Gracefully stop all sessions"""
        logger.info("🛑 Stopping all userbot sessions...")
        
        stop_tasks = []
        for bot_name, session in self.sessions.items():
            task = asyncio.create_task(
                session.stop(),
                name=f"stop_{bot_name}"
            )
            stop_tasks.append(task)
        
        # Wait for all to stop
        await asyncio.gather(*stop_tasks, return_exceptions=True)
        
        self.sessions.clear()
        logger.info("✅ All sessions stopped successfully")
    
    async def health_check_loop(self):
        """Continuous health monitoring"""
        while self.running:
            try:
                await self.health_monitor.check_all_sessions(self.sessions)
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def run(self):
        """Main execution loop"""
        self.running = True
        
        try:
            # Initialize sessions
            await self.initialize_sessions()
            
            # Start all sessions
            if not await self.start_all_sessions():
                raise RuntimeError("Failed to start any userbot sessions!")
            
            # Start health monitoring
            health_task = asyncio.create_task(self.health_check_loop())
            
            logger.info("🎯 GavatCore Userbot System is running!")
            logger.info("🔥 Available bots:")
            for bot_name, config in self.bot_configs.items():
                if bot_name in self.sessions:
                    logger.info(f"   {config['description']}", bot=bot_name)
            
            logger.info("Press Ctrl+C to stop...")
            
            # Keep running until interrupted
            try:
                while self.running:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                logger.info("🛑 Shutdown signal received")
            
        except KeyboardInterrupt:
            logger.info("🛑 Keyboard interrupt received")
        except Exception as e:
            logger.error(f"💥 Fatal error: {e}")
        finally:
            self.running = False
            
            # Cancel health task
            if 'health_task' in locals():
                health_task.cancel()
                try:
                    await health_task
                except asyncio.CancelledError:
                    pass
            
            # Stop all sessions
            await self.stop_all_sessions()
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        def signal_handler(signum, frame):
            logger.info(f"🔔 Received signal {signum}")
            self.running = False
            
            # Get current event loop
            try:
                loop = asyncio.get_running_loop()
                # Schedule graceful shutdown
                for task in asyncio.all_tasks(loop):
                    task.cancel()
            except RuntimeError:
                pass
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Application entry point"""
    print("""
🔥═══════════════════════════════════════════════════════════════🔥
        🚀 GAVATCORE TELETHON USERBOT SYSTEM v3.0 🚀
🔥═══════════════════════════════════════════════════════════════🔥
        🔥 GawatBaba - System Admin & Control
        🎮 Yayıncı Lara - GPT Gaming Persona  
        🌸 XXXGeisha - Dominant AI Seductress
🔥═══════════════════════════════════════════════════════════════🔥
    """)
    
    manager = GavatCoreUserbotManager()
    manager.setup_signal_handlers()
    
    try:
        await manager.run()
    except KeyboardInterrupt:
        logger.info("👋 GavatCore shutting down...")
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Set proper event loop policy for Windows
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Run the application
    asyncio.run(main()) 