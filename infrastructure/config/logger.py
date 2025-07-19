#!/usr/bin/env python3
"""
🚀 GAVATCORE LOGGER MODULE
Universal logging system for all bots
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional

# Ana logger configurasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_logger(name: str = "gavatcore") -> logging.Logger:
    """Universal logger instance"""
    return logging.getLogger(name)

def log_event(event: str, level: str = "info", details: Optional[str] = None):
    """Event logging with details"""
    logger = get_logger("events")
    
    message = f"🎯 {event}"
    if details:
        message += f" | {details}"
    
    if level.lower() == "error":
        logger.error(message)
    elif level.lower() == "warning":
        logger.warning(message)
    elif level.lower() == "debug":
        logger.debug(message)
    else:
        logger.info(message)

def log_analytics(action: str, user_id: str = None, data: dict = None):
    """Analytics logging"""
    logger = get_logger("analytics")
    
    analytics_data = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "user_id": user_id,
        "data": data or {}
    }
    
    logger.info(f"📊 Analytics: {analytics_data}")

def log_bot_activity(bot_name: str, activity: str, details: str = ""):
    """Bot activity logging"""
    logger = get_logger(f"bot.{bot_name}")
    logger.info(f"🤖 {activity} | {details}")

def log_error(error: Exception, context: str = ""):
    """Error logging with context"""
    logger = get_logger("errors")
    logger.error(f"❌ {context}: {str(error)}", exc_info=True)

def log_performance(operation: str, duration: float, details: str = ""):
    """Performance logging"""
    logger = get_logger("performance")
    logger.info(f"⚡ {operation}: {duration:.2f}s | {details}")

# Backward compatibility aliases
def setup_logging():
    """Setup logging (compatibility)"""
    pass

def get_performance_logger():
    """Get performance logger (compatibility)"""
    return get_logger("performance")

# Export main functions
__all__ = [
    'get_logger',
    'log_event', 
    'log_analytics',
    'log_bot_activity',
    'log_error',
    'log_performance',
    'setup_logging',
    'get_performance_logger'
] 