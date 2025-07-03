#!/usr/bin/env python3
"""
🔧 GAVATCORE CONFIG MANAGER
Centralized configuration management
"""

import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv

class ConfigManager:
    """Centralized configuration manager"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        self._config = {
            # Telegram API
            'TELEGRAM_API_ID': os.getenv('TELEGRAM_API_ID'),
            'TELEGRAM_API_HASH': os.getenv('TELEGRAM_API_HASH'),
            
            # Bot phones
            'GAWATBABA_PHONE': os.getenv('GAWATBABA_PHONE', '+447832134241'),
            'YAYINCILARA_PHONE': os.getenv('YAYINCILARA_PHONE', '+90XXXXXXXXXX'),
            'XXXGEISHA_PHONE': os.getenv('XXXGEISHA_PHONE', '+90YYYYYYYYY'),
            
            # OpenAI
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'OPENAI_MODEL': os.getenv('OPENAI_MODEL', 'gpt-4o'),
            
            # Redis
            'REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
            
            # Database
            'POSTGRES_URL': os.getenv('POSTGRES_URL', 'sqlite+aiosqlite:///./data/gavatcore.db'),
            
            # System
            'DEBUG_MODE': os.getenv('DEBUG_MODE', 'false').lower() == 'true',
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config[key] = value
    
    def validate_required(self) -> bool:
        """Validate required configuration"""
        required_keys = [
            'TELEGRAM_API_ID',
            'TELEGRAM_API_HASH',
        ]
        
        for key in required_keys:
            if not self.get(key):
                raise ValueError(f"Required config key missing: {key}")
        
        return True 