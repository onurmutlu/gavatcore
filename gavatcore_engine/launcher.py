from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
GavatCore Engine Launcher
========================

Production launcher for GavatCore Auto-Messaging Engine.
"""

import asyncio
import signal
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gavatcore_engine.main import app
from gavatcore_engine.config import get_settings
from gavatcore_engine.logger import setup_logging, get_logger


class GavatCoreLauncher:
    """GavatCore Engine launcher with graceful shutdown."""
    
    def __init__(self):
        self.settings = get_settings()
        setup_logging()
        self.logger = get_logger("launcher")
        self.server = None
        self.shutdown_event = asyncio.Event()
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_event.set()
    
    async def start_server(self):
        """Start the FastAPI server."""
        import uvicorn
        
        config = uvicorn.Config(
            app,
            host=self.settings.host,
            port=self.settings.port,
            workers=1,  # Use 1 worker for async app
            log_level=self.settings.log_level.lower(),
            reload=self.settings.debug,
            access_log=True,
        )
        
        self.server = uvicorn.Server(config)
        
        self.logger.info(
            f"Starting GavatCore Engine on {self.settings.host}:{self.settings.port}"
        )
        
        # Start server in background
        server_task = asyncio.create_task(self.server.serve())
        
        # Wait for shutdown signal
        await self.shutdown_event.wait()
        
        # Graceful shutdown
        self.logger.info("Shutting down server...")
        self.server.should_exit = True
        
        # Wait for server to finish
        await server_task
        
        self.logger.info("Server shutdown complete")
    
    def run(self):
        """Run the launcher."""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Run the async server
            asyncio.run(self.start_server())
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Launcher error: {e}")
            sys.exit(1)
        
        self.logger.info("GavatCore Engine launcher finished")


def main():
    """Main entry point."""
    launcher = GavatCoreLauncher()
    launcher.run()


if __name__ == "__main__":
    main() 