#!/usr/bin/env python3
"""
Base Bot Handler Class
Common functionality for all Telegram bot handlers
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import structlog
from telethon import TelegramClient, events
from telethon.events import ChatAction, NewMessage

from character_engine.character_manager import character_manager
from core.config import get_config
from core.database.connection_manager import get_connection_manager
from core.security.input_validator import TelegramInputValidator, validate_telegram_input

logger = structlog.get_logger("gavatcore.base_handler")


@dataclass
class BotMetrics:
    """Bot performance metrics"""

    messages_processed: int = 0
    errors_count: int = 0
    start_time: datetime = None
    last_activity: datetime = None


class BaseBotHandler(ABC):
    """Base class for all bot handlers"""

    def __init__(self, bot_name: str, character_username: Optional[str] = None):
        self.bot_name = bot_name
        self.character_username = character_username
        self.client: Optional[TelegramClient] = None
        self.config = get_config()
        self.metrics = BotMetrics(start_time=datetime.now())
        self.is_running = False
        self._tasks: List[asyncio.Task] = []

        # Load character configuration if specified
        self.character_config = None
        if character_username:
            self.character_config = character_manager.load_character(character_username)
            if not self.character_config:
                logger.warning(f"Character config not found: {character_username}")

    async def initialize(self) -> None:
        """Initialize bot handler"""
        logger.info(f"Initializing bot handler: {self.bot_name}")

        # Initialize database connections
        await get_connection_manager()

        # Initialize Telegram client
        self.client = TelegramClient(
            f"{self.config.sessions_dir}/{self.bot_name}",
            self.config.telegram.api_id,
            self.config.telegram.api_hash,
            device_model=self.config.telegram.device_model,
            system_version=self.config.telegram.system_version,
            app_version=self.config.telegram.app_version,
            use_ipv6=self.config.telegram.use_ipv6,
        )

        # Register event handlers
        await self._register_handlers()

        logger.info(f"Bot handler initialized: {self.bot_name}")

    async def _register_handlers(self) -> None:
        """Register Telegram event handlers"""
        if not self.client:
            raise RuntimeError("Client not initialized")

        # Register message handler with validation
        @validate_telegram_input
        async def message_handler(event):
            await self._handle_message(event)

        self.client.add_event_handler(message_handler, NewMessage)

        # Register additional handlers
        await self._register_custom_handlers()

    @abstractmethod
    async def _register_custom_handlers(self) -> None:
        """Register bot-specific event handlers"""
        pass

    @abstractmethod
    async def _handle_message(self, event) -> None:
        """Handle incoming messages"""
        pass

    async def start(self) -> None:
        """Start the bot"""
        if not self.client:
            await self.initialize()

        logger.info(f"Starting bot: {self.bot_name}")

        await self.client.start()
        self.is_running = True
        self.metrics.start_time = datetime.now()

        logger.info(f"Bot started successfully: {self.bot_name}")

    async def stop(self) -> None:
        """Stop the bot gracefully"""
        logger.info(f"Stopping bot: {self.bot_name}")

        self.is_running = False

        # Cancel all running tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        # Disconnect client
        if self.client and self.client.is_connected():
            await self.client.disconnect()

        logger.info(f"Bot stopped: {self.bot_name}")

    async def send_message(self, chat_id: int, message: str, **kwargs) -> None:
        """Send message with rate limiting and validation"""
        if not self.client:
            raise RuntimeError("Client not initialized")

        # Validate and sanitize message
        message = TelegramInputValidator.sanitize_text(message)

        try:
            await self.client.send_message(chat_id, message, **kwargs)
            self.metrics.messages_processed += 1
            self.metrics.last_activity = datetime.now()

        except Exception as e:
            self.metrics.errors_count += 1
            logger.error(f"Failed to send message: {e}")
            raise

    async def _update_metrics(self, event) -> None:
        """Update bot metrics"""
        self.metrics.messages_processed += 1
        self.metrics.last_activity = datetime.now()

    def get_metrics(self) -> Dict[str, Any]:
        """Get bot performance metrics"""
        uptime = None
        if self.metrics.start_time:
            uptime = (datetime.now() - self.metrics.start_time).total_seconds()

        return {
            "bot_name": self.bot_name,
            "is_running": self.is_running,
            "messages_processed": self.metrics.messages_processed,
            "errors_count": self.metrics.errors_count,
            "uptime_seconds": uptime,
            "last_activity": self.metrics.last_activity.isoformat()
            if self.metrics.last_activity
            else None,
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        health = {
            "bot_name": self.bot_name,
            "status": "healthy" if self.is_running else "stopped",
            "client_connected": self.client.is_connected() if self.client else False,
            "character_loaded": self.character_config is not None,
            "metrics": self.get_metrics(),
        }

        # Check database connections
        try:
            db_manager = await get_connection_manager()
            health["database"] = await db_manager.health_check()
        except Exception as e:
            health["database"] = {"error": str(e)}

        return health

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(bot_name={self.bot_name}, running={self.is_running})>"


class CharacterBotHandler(BaseBotHandler):
    """Base class for character-based bots"""

    def __init__(self, bot_name: str, character_username: str):
        super().__init__(bot_name, character_username)

        if not self.character_config:
            raise ValueError(f"Character configuration required for {character_username}")

    async def get_ai_response(self, message: str, context: Dict[str, Any] = None) -> str:
        """Get AI response based on character configuration"""
        if not self.character_config:
            return "Character not configured"

        # This would integrate with your GPT system
        # For now, return a placeholder
        return f"[{self.character_config.name}] Response to: {message[:50]}..."

    async def _handle_message(self, event) -> None:
        """Handle message with character-based response"""
        await self._update_metrics(event)

        try:
            message_text = event.message.text
            if not message_text:
                return

            # Get character response
            response = await self.get_ai_response(message_text)

            # Send response
            await self.send_message(event.chat_id, response)

        except Exception as e:
            logger.error(f"Error handling message in {self.bot_name}: {e}")
            self.metrics.errors_count += 1
