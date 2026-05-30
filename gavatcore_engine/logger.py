from infrastructure.config.logger import get_logger

"""
Structured Logging Configuration
===============================

JSON-based structured logging with structlog.
"""

import structlog
import logging
import sys
from typing import Any, Dict
from .config import get_settings


def setup_logging() -> None:
    """Configure structured logging for the application."""
    settings = get_settings()
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.log_format == "json" 
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """Get logger instance for this class."""
        return get_logger(self.__class__.__name__)
    
    def log_event(self, event: str, **kwargs: Any) -> None:
        """Log an event with additional context."""
        self.logger.info(event, **kwargs)
    
    def log_error(self, error: str, exc_info: bool = True, **kwargs: Any) -> None:
        """Log an error with exception info."""
        self.logger.error(error, exc_info=exc_info, **kwargs)
    
    def log_warning(self, warning: str, **kwargs: Any) -> None:
        """Log a warning message."""
        self.logger.warning(warning, **kwargs)
    
    def log_debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message."""
        self.logger.debug(message, **kwargs) 