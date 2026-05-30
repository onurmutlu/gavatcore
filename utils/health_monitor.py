from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
📊 GAVATCORE HEALTH MONITOR
System health monitoring and diagnostics
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
import structlog

logger = structlog.get_logger("gavatcore.health")

class HealthMonitor:
    """System health monitoring"""
    
    def __init__(self):
        self.session_stats = {}
        self.last_check = None
    
    async def check_all_sessions(self, sessions: Dict[str, Any]) -> Dict[str, bool]:
        """Check health of all sessions"""
        results = {}
        
        for bot_name, session in sessions.items():
            try:
                is_healthy = await self.check_session_health(session)
                results[bot_name] = is_healthy
                
                if not is_healthy:
                    logger.warning(f"🔥 Health issue detected", bot=bot_name)
                    
            except Exception as e:
                logger.error(f"❌ Health check failed", bot=bot_name, error=str(e))
                results[bot_name] = False
        
        self.last_check = datetime.now()
        return results
    
    async def check_session_health(self, session: Any) -> bool:
        """Check individual session health"""
        try:
            # Basic connection check
            if hasattr(session, 'client') and session.client:
                if session.client.is_connected():
                    return True
            return False
        except Exception:
            return False 