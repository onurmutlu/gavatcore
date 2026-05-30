from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🤖 BOT LAUNCHER SERVICE
Automatic userbot instance creation and management
"""

import os
import json
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings, get_subscription_limits
from app.core.exceptions import BotInstanceError, ValidationError
from app.models.user import User
from app.models.subscription import Subscription
from app.models.bot_instance import BotInstance
import structlog

logger = structlog.get_logger("gavatcore.bot_launcher")


class BotLauncherService:
    """Service for launching and managing bot instances"""
    
    def __init__(self):
        self.session_storage_path = Path(settings.SESSION_STORAGE_PATH)
        self.session_storage_path.mkdir(exist_ok=True)
        
        # Bot personality configurations
        self.personalities = {
            "gawatbaba": {
                "display_name": "GawatBaba",
                "reply_mode": "manual",
                "description": "Sistem yöneticisi, coin kontrol",
                "default_triggers": ["merhaba", "selam", "coin"],
                "persona_file": "gawatbaba.json"
            },
            "yayincilara": {
                "display_name": "Yayıncı Lara", 
                "reply_mode": "hybrid",
                "description": "Gaming persona, Türkçe-Rusça mix",
                "default_triggers": ["oyun", "stream", "канал"],
                "persona_file": "yayincilara.json"
            },
            "xxxgeisha": {
                "display_name": "XXX Geisha",
                "reply_mode": "manualplus", 
                "description": "Seductive AI, sophisticated responses",
                "default_triggers": ["tatlım", "canım", "darling"],
                "persona_file": "xxxgeisha.json"
            }
        }
    
    async def create_bot_instance(
        self,
        user: User,
        subscription: Subscription,
        personality: str = "yayincilara",
        phone_number: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> BotInstance:
        """Create a new bot instance for user"""
        
        try:
            # Validate personality
            if personality not in self.personalities:
                raise ValidationError(f"Invalid personality: {personality}")
            
            # Check subscription limits
            current_bots = await self._get_user_active_bots(user.id, db)  # type: ignore
            if len(current_bots) >= subscription.max_bots:  # type: ignore
                raise BotInstanceError(
                    f"Maximum bot limit reached ({subscription.max_bots})"  # type: ignore
                )
            
            # Generate unique bot name
            bot_name = f"{personality}_{user.id}_{int(datetime.utcnow().timestamp())}"  # type: ignore
            
            # Create session file path
            session_file = self.session_storage_path / f"{bot_name}.session"
            
            # Create bot instance record
            bot_instance = BotInstance(
                user_id=user.id,  # type: ignore
                bot_name=bot_name,
                bot_username=f"@{bot_name}",
                personality=personality,
                reply_mode=self.personalities[personality]["reply_mode"],
                phone_number=phone_number,
                session_file_path=str(session_file),
                session_status="creating",
                config=json.dumps({
                    "personality": self.personalities[personality],
                    "max_coins": subscription.max_coins,  # type: ignore
                    "features": subscription.get_features_list(),
                    "auto_reply": True,
                    "scheduler_enabled": "scheduler" in subscription.get_features_list(),
                    "created_at": datetime.utcnow().isoformat()
                }),
                triggers=json.dumps(self.personalities[personality]["default_triggers"])
            )
            
            if db:
                db.add(bot_instance)
                await db.commit()
                await db.refresh(bot_instance)
            
            logger.info(f"Bot instance created: {bot_name} for user {user.username}")
            
            # Start bot instance in background
            if db:
                asyncio.create_task(self._start_bot_process(bot_instance, db))
            
            return bot_instance
            
        except Exception as e:
            logger.error(f"Failed to create bot instance: {e}")
            raise BotInstanceError(f"Bot creation failed: {e}")
    
    async def _start_bot_process(self, bot_instance: BotInstance, db: Optional[AsyncSession]):
        """Start the actual bot process"""
        try:
            logger.info(f"Starting bot process: {bot_instance.bot_name}")
            
            # Create bot configuration file
            config_file = await self._create_bot_config(bot_instance)
            
            # Launch bot using existing userbot_session.py
            launch_command = [
                "python3",
                "../userbot_session.py",  # Use existing userbot system
                "--config", str(config_file),
                "--personality", bot_instance.personality,  # type: ignore
                "--mode", bot_instance.reply_mode,  # type: ignore
                "--session", bot_instance.session_file_path,  # type: ignore
            ]
            
            # Start bot process
            process = await asyncio.create_subprocess_exec(
                *launch_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=settings.SESSION_STORAGE_PATH
            )
            
            # Update bot status
            if db:
                bot_instance.session_status = "active"  # type: ignore
                bot_instance.start_bot()
                await db.commit()
            
            logger.info(f"Bot process started successfully: {bot_instance.bot_name}")
            
            # Monitor process (optional - could be separate service)
            await self._monitor_bot_process(bot_instance, process, db)
            
        except Exception as e:
            logger.error(f"Failed to start bot process: {e}")
            if db:
                bot_instance.log_error(str(e))  # type: ignore
                await db.commit()
    
    async def _create_bot_config(self, bot_instance: BotInstance) -> Path:
        """Create configuration file for bot instance"""
        config_data = {
            "bot_name": bot_instance.bot_name,
            "personality": bot_instance.personality,
            "reply_mode": bot_instance.reply_mode,
            "session_file": bot_instance.session_file_path,
            "user_id": bot_instance.user_id,
            "triggers": json.loads(bot_instance.triggers or "[]"),  # type: ignore
            "config": json.loads(bot_instance.config or "{}"),  # type: ignore
            
            # API settings
            "api_base_url": "http://localhost:8000",
            "openai_api_key": settings.OPENAI_API_KEY,
            "openai_model": settings.OPENAI_MODEL,
            
            # Telegram settings
            "telegram_api_id": settings.TELEGRAM_API_ID,
            "telegram_api_hash": settings.TELEGRAM_API_HASH,
            
            # Logging
            "log_level": "INFO",
            "log_file": f"logs/{bot_instance.bot_name}.log"
        }
        
        config_file = self.session_storage_path / f"{bot_instance.bot_name}_config.json"
        config_file.write_text(json.dumps(config_data, indent=2))
        
        return config_file
    
    async def _monitor_bot_process(
        self, 
        bot_instance: BotInstance, 
        process: asyncio.subprocess.Process,
        db: Optional[AsyncSession]
    ):
        """Monitor bot process health"""
        try:
            # Wait for process to complete or handle errors
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Bot process completed successfully: {bot_instance.bot_name}")
            else:
                logger.error(f"Bot process failed: {bot_instance.bot_name}, stderr: {stderr.decode()}")
                if db:
                    bot_instance.log_error(f"Process failed: {stderr.decode()}")  # type: ignore
                    await db.commit()
                    
        except Exception as e:
            logger.error(f"Error monitoring bot process: {e}")
    
    async def stop_bot_instance(self, bot_instance: BotInstance, db: AsyncSession):
        """Stop a running bot instance"""
        try:
            # Update database
            bot_instance.stop_bot("User requested stop")  # type: ignore
            await db.commit()
            
            # TODO: Implement process termination
            # This would require tracking process IDs
            
            logger.info(f"Bot instance stopped: {bot_instance.bot_name}")
            
        except Exception as e:
            logger.error(f"Failed to stop bot instance: {e}")
            raise BotInstanceError(f"Failed to stop bot: {e}")
    
    async def restart_bot_instance(self, bot_instance: BotInstance, db: AsyncSession):
        """Restart a bot instance"""
        try:
            # Stop first
            await self.stop_bot_instance(bot_instance, db)
            
            # Wait a bit
            await asyncio.sleep(2)
            
            # Start again
            await self._start_bot_process(bot_instance, db)
            
            logger.info(f"Bot instance restarted: {bot_instance.bot_name}")
            
        except Exception as e:
            logger.error(f"Failed to restart bot instance: {e}")
            raise BotInstanceError(f"Failed to restart bot: {e}")
    
    async def get_bot_status(self, bot_instance: BotInstance) -> Dict[str, Any]:
        """Get comprehensive bot status"""
        return {
            "bot_name": bot_instance.bot_name,
            "personality": bot_instance.personality,
            "status": bot_instance.session_status,
            "is_active": bot_instance.is_active,  # type: ignore
            "is_online": bot_instance.is_online,  # type: ignore
            "uptime_seconds": bot_instance.uptime_seconds,
            "messages_sent": bot_instance.messages_sent,  # type: ignore
            "messages_received": bot_instance.messages_received,  # type: ignore
            "coins_used": bot_instance.coins_used,  # type: ignore
            "last_seen": bot_instance.last_seen_at.isoformat() if bot_instance.last_seen_at else None,  # type: ignore
            "error_count": bot_instance.error_count,  # type: ignore
            "last_error": bot_instance.last_error,  # type: ignore
        }
    
    async def _get_user_active_bots(self, user_id: int, db: Optional[AsyncSession]) -> List[BotInstance]:
        """Get user's active bot instances"""
        if not db:
            return []
            
        stmt = select(BotInstance).where(
            BotInstance.user_id == user_id,
            BotInstance.is_active == True  # type: ignore
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def create_default_bot_for_subscription(
        self,
        user: User,
        subscription: Subscription,
        db: AsyncSession
    ) -> BotInstance:
        """Create default bot when subscription is activated"""
        
        # Determine default personality based on plan
        personality_map = {
            "trial": "yayincilara",
            "starter": "yayincilara", 
            "pro": "xxxgeisha",
            "deluxe": "gawatbaba"
        }
        
        default_personality = personality_map.get(
            subscription.plan_name,  # type: ignore
            "yayincilara"
        )
        
        logger.info(f"Creating default bot for user {user.username} with plan {subscription.plan_name}")  # type: ignore
        
        return await self.create_bot_instance(
            user=user,
            subscription=subscription,
            personality=default_personality,
            db=db
        ) 