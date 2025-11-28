#!/usr/bin/env python3
"""
GavatCore - Unified Entry Point
Main application launcher with all services
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import List, Optional

import structlog

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.base.bot_handler import BaseBotHandler
from core.config import ConfigValidationError, get_config
from core.database.connection_manager import get_connection_manager
from services.telegram.bot_manager.bot_system import YagmurBotAutomation

logger = structlog.get_logger("gavatcore.main")


class GavatCoreApplication:
    """Main GavatCore application"""

    def __init__(self):
        self.config = None
        self.db_manager = None
        self.bot_handlers: List[BaseBotHandler] = []
        self.api_tasks: List[asyncio.Task] = []
        self.running = False

    async def initialize(self) -> None:
        """Initialize the application"""
        logger.info("Initializing GavatCore...")

        try:
            # Load configuration
            self.config = get_config()
            logger.info(f"Configuration loaded for environment: {self.config.environment}")

            # Initialize database connections
            self.db_manager = await get_connection_manager()
            logger.info("Database connections initialized")

            # Health check
            health = await self.db_manager.health_check()
            logger.info(f"Database health check: {health}")

        except ConfigValidationError as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            sys.exit(1)

    async def start_bots(self, bot_names: Optional[List[str]] = None) -> None:
        """Start specified bots or all configured bots"""
        logger.info("Starting Telegram bots...")

        # For now, start the main bot system
        # In the future, this would dynamically load bot handlers
        if not bot_names or "yagmur" in bot_names:
            try:
                yagmur_bot = YagmurBotAutomation()
                await yagmur_bot.start()
                logger.info("Yagmur bot started successfully")
            except Exception as e:
                logger.error(f"Failed to start Yagmur bot: {e}")

    async def start_apis(self) -> None:
        """Start API services"""
        logger.info("Starting API services...")

        # Start production bot API on port 5050
        try:
            import uvicorn

            from apis.production_bot_api import app as bot_api

            # Run API in background task
            api_task = asyncio.create_task(self._run_api(bot_api, "production_bot_api", 5050))
            self.api_tasks.append(api_task)

        except Exception as e:
            logger.error(f"Failed to start production bot API: {e}")

        # Start token API on port 5051
        try:
            from apis.xp_token_api_sync import app as token_api

            token_task = asyncio.create_task(self._run_api(token_api, "xp_token_api", 5051))
            self.api_tasks.append(token_task)

        except Exception as e:
            logger.error(f"Failed to start token API: {e}")

    async def _run_api(self, app, name: str, port: int) -> None:
        """Run API service"""
        try:
            import uvicorn

            config = uvicorn.Config(
                app, host="0.0.0.0", port=port, log_level="info", reload=self.config.debug
            )
            server = uvicorn.Server(config)
            logger.info(f"Starting {name} on port {port}")
            await server.serve()
        except Exception as e:
            logger.error(f"Failed to run {name}: {e}")

    async def start(self, components: Optional[List[str]] = None) -> None:
        """Start the application with specified components"""
        await self.initialize()

        components = components or ["bots", "apis"]
        self.running = True

        logger.info(f"Starting GavatCore components: {components}")

        tasks = []

        if "bots" in components:
            tasks.append(self.start_bots())

        if "apis" in components:
            tasks.append(self.start_apis())

        try:
            # Run all components concurrently
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            await self.stop()
        except Exception as e:
            logger.error(f"Application error: {e}")
            await self.stop()
            raise

    async def stop(self) -> None:
        """Stop the application gracefully"""
        if not self.running:
            return

        logger.info("Stopping GavatCore...")
        self.running = False

        # Stop API tasks
        for task in self.api_tasks:
            if not task.done():
                task.cancel()

        if self.api_tasks:
            await asyncio.gather(*self.api_tasks, return_exceptions=True)

        # Stop bot handlers
        for handler in self.bot_handlers:
            await handler.stop()

        # Close database connections
        if self.db_manager:
            await self.db_manager.close()

        logger.info("GavatCore stopped successfully")

    async def health_check(self) -> dict:
        """Perform system health check"""
        health = {
            "status": "healthy" if self.running else "stopped",
            "timestamp": asyncio.get_event_loop().time(),
            "components": {},
        }

        if self.db_manager:
            health["components"]["database"] = await self.db_manager.health_check()

        health["components"]["bots"] = {
            handler.bot_name: await handler.health_check() for handler in self.bot_handlers
        }

        return health


async def main() -> None:
    """Main entry point"""
    parser = argparse.ArgumentParser(description="GavatCore - AI Telegram Bot Platform")
    parser.add_argument(
        "--components",
        nargs="+",
        choices=["bots", "apis", "all"],
        default=["all"],
        help="Components to start",
    )
    parser.add_argument(
        "--bots", nargs="+", help="Specific bots to start (e.g., yagmur, lara, babagavat)"
    )
    parser.add_argument("--health-check", action="store_true", help="Perform health check and exit")

    args = parser.parse_args()

    app = GavatCoreApplication()

    if args.health_check:
        await app.initialize()
        health = await app.health_check()
        print(f"Health status: {health}")
        return

    components = args.components
    if "all" in components:
        components = ["bots", "apis"]

    try:
        await app.start(components)
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
