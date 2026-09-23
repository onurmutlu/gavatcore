from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🤖 BOT LAUNCHER SERVICE
Automatic userbot instance creation and management
"""

import os
import json
import asyncio
import sys
from uuid import uuid4
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
from app.database.connection import async_session_factory
from app.services.process_supervisor import supervisor
import structlog

logger = structlog.get_logger("gavatcore.bot_launcher")


class BotLauncherService:
    """Service for launching and managing bot instances"""
    
    def __init__(self):
        self.session_storage_path = Path(settings.SESSION_STORAGE_PATH).resolve()
        self.session_storage_path.mkdir(parents=True, exist_ok=True)
        
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
            bot_name = f"{personality}_{user.id}_{uuid4().hex[:12]}"  # type: ignore
            
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
                await self._start_bot_process(bot_instance, db)
            
            return bot_instance
            
        except Exception as e:
            logger.error(f"Failed to create bot instance: {e}")
            raise BotInstanceError(f"Bot creation failed: {e}")
    
    async def _record_exit(self, bot_id: int, code: int):
        # A fresh session belongs to this monitor, never to an HTTP request.
        async with async_session_factory() as db:
            bot = await db.get(BotInstance, bot_id)
            if bot:
                bot.stop_bot()
                if code:
                    bot.log_error(f"Bot process exited with code {code}")
                await db.commit()

    async def shutdown(self):
        await supervisor.close(lambda bot_id: self._record_exit(bot_id, 0))

    async def _start_bot_process(self, bot_instance: BotInstance, db: Optional[AsyncSession]):
        """Return after readiness, not after the bot's lifetime."""
        if db is None or bot_instance.id is None:
            raise BotInstanceError("A persisted bot and database session are required")
        bot_id = bot_instance.id
        if bot_instance.is_active and bot_id not in supervisor.children:
            raise BotInstanceError("Active bot has no locally owned process; reconcile before starting")
        root = Path(__file__).resolve().parents[3]
        config_file = await self._create_bot_config(bot_instance)
        command = [sys.executable, str(root / "userbot_session.py"), "--config", str(config_file)]
        env = os.environ.copy()
        env.update({
            "TELEGRAM_API_ID": str(settings.TELEGRAM_API_ID),
            "TELEGRAM_API_HASH": settings.TELEGRAM_API_HASH,
            "OPENAI_API_KEY": settings.OPENAI_API_KEY,
            "OPENAI_MODEL": settings.OPENAI_MODEL,
        })

        async def started():
            bot_instance.start_bot()
            bot_instance.is_online = True
            await db.commit()

        try:
            await supervisor.start(
                bot_id, command, cwd=str(root), env=env,
                on_started=started,
                on_exit=lambda code: self._record_exit(bot_id, code),
            )
        except BaseException as exc:
            await db.rollback()
            bot = await db.get(BotInstance, bot_id)
            if bot:
                bot.stop_bot()
                bot.log_error("Bot startup failed; check authorization and runtime configuration")
                await db.commit()
            if isinstance(exc, asyncio.CancelledError):
                raise
            raise BotInstanceError("Bot failed to become ready") from exc

    async def _create_bot_config(self, bot_instance: BotInstance) -> Path:
        """Create configuration file for bot instance"""
        config_data = {
            "bot_name": bot_instance.bot_name,
            "personality": bot_instance.personality,
            "reply_mode": bot_instance.reply_mode,
            "session_file": str(Path(bot_instance.session_file_path).resolve()),
            "phone": bot_instance.phone_number,
            "non_interactive": True,
            "handlers": {
                "gawatbaba": ["admin_handler", "coin_handler"],
                "yayincilara": ["gpt_handler", "common_handler"],
                "xxxgeisha": ["gpt_handler"],
            }[bot_instance.personality],
            "user_id": bot_instance.user_id,
            "triggers": json.loads(bot_instance.triggers or "[]"),  # type: ignore
            "config": json.loads(bot_instance.config or "{}"),  # type: ignore
            
            # API settings
            "api_base_url": "http://localhost:8000",
            "openai_model": settings.OPENAI_MODEL,
            
            # Telegram settings
            
            # Logging
            "log_level": "INFO",
            "log_file": f"logs/{bot_instance.bot_name}.log"
        }
        
        config_file = self.session_storage_path / f"{bot_instance.bot_name}_config.json"
        fd = os.open(config_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        os.chmod(config_file, 0o600)
        with os.fdopen(fd, "w") as handle:
            json.dump(config_data, handle, indent=2)
        
        return config_file
    
    async def stop_bot_instance(self, bot_instance: BotInstance, db: AsyncSession):
        async def stopped():
            bot_instance.stop_bot("User requested stop")
            await db.commit()

        try:
            await supervisor.stop(
                bot_instance.id, on_stopped=stopped,
                require_owned=bool(bot_instance.is_active or bot_instance.is_online),
            )
        except Exception as exc:
            raise BotInstanceError(str(exc)) from exc

    async def restart_bot_instance(self, bot_instance: BotInstance, db: AsyncSession):
        await self.stop_bot_instance(bot_instance, db)
        await self._start_bot_process(bot_instance, db)

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
