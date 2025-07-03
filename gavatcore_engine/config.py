"""
Configuration Management
========================

Centralized configuration management with environment variables.
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    app_name: str = Field(default="GavatCore Engine", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Telegram API settings
    telegram_api_id: int = Field(..., env="TELEGRAM_API_ID")
    telegram_api_hash: str = Field(..., env="TELEGRAM_API_HASH")
    
    # Redis settings
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # Message processing settings
    max_message_retries: int = Field(default=3, env="MAX_MESSAGE_RETRIES")
    message_retry_delay: int = Field(default=60, env="MESSAGE_RETRY_DELAY")  # seconds
    worker_sleep_interval: float = Field(default=1.0, env="WORKER_SLEEP_INTERVAL")
    
    # Rate limiting
    rate_limit_messages_per_minute: int = Field(default=20, env="RATE_LIMIT_MESSAGES_PER_MINUTE")
    rate_limit_burst_size: int = Field(default=5, env="RATE_LIMIT_BURST_SIZE")
    
    # Admin settings
    admin_user_ids: List[int] = Field(default_factory=list, env="ADMIN_USER_IDS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # AI settings
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ai_model: str = Field(default="gpt-3.5-turbo", env="AI_MODEL")
    ai_max_tokens: int = Field(default=150, env="AI_MAX_TOKENS")
    ai_temperature: float = Field(default=0.7, env="AI_TEMPERATURE")
    
    # Legacy GavatCore settings (from existing config.py)
    # These will be loaded from the existing config if available
    babagavat_phone: Optional[str] = Field(default=None, env="BABAGAVAT_PHONE")
    babagavat_session: Optional[str] = Field(default=None, env="BABAGAVAT_SESSION")
    xxxgeisha_phone: Optional[str] = Field(default=None, env="XXXGEISHA_PHONE") 
    xxxgeisha_session: Optional[str] = Field(default=None, env="XXXGEISHA_SESSION")
    yayincilara_phone: Optional[str] = Field(default=None, env="YAYINCILARA_PHONE")
    yayincilara_session: Optional[str] = Field(default=None, env="YAYINCILARA_SESSION")
    
    # Database settings (for existing GavatCore DB)
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    postgres_host: Optional[str] = Field(default=None, env="POSTGRES_HOST")
    postgres_port: Optional[int] = Field(default=5432, env="POSTGRES_PORT")
    postgres_user: Optional[str] = Field(default=None, env="POSTGRES_USER")
    postgres_password: Optional[str] = Field(default=None, env="POSTGRES_PASSWORD")
    postgres_db: Optional[str] = Field(default=None, env="POSTGRES_DB")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Try to load from existing GavatCore config if available
        self._load_legacy_config()
        
        # Parse admin user IDs if provided as string
        if isinstance(self.admin_user_ids, str):
            try:
                self.admin_user_ids = [int(x.strip()) for x in self.admin_user_ids.split(",") if x.strip()]
            except ValueError:
                self.admin_user_ids = []
    
    def _load_legacy_config(self):
        """Try to load configuration from existing GavatCore config.py"""
        try:
            import sys
            from pathlib import Path
            
            # Add project root to path
            project_root = Path(__file__).parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            # Try to import existing config
            try:
                import config as legacy_config
                
                # Load Telegram API credentials
                if hasattr(legacy_config, 'TELEGRAM_API_ID') and not self.telegram_api_id:
                    self.telegram_api_id = legacy_config.TELEGRAM_API_ID
                if hasattr(legacy_config, 'TELEGRAM_API_HASH') and not self.telegram_api_hash:
                    self.telegram_api_hash = legacy_config.TELEGRAM_API_HASH
                
                # Load bot phone numbers
                if hasattr(legacy_config, 'BABAGAVAT_PHONE') and not self.babagavat_phone:
                    self.babagavat_phone = legacy_config.BABAGAVAT_PHONE
                if hasattr(legacy_config, 'XXXGEISHA_PHONE') and not self.xxxgeisha_phone:
                    self.xxxgeisha_phone = legacy_config.XXXGEISHA_PHONE
                if hasattr(legacy_config, 'YAYINCILARA_PHONE') and not self.yayincilara_phone:
                    self.yayincilara_phone = legacy_config.YAYINCILARA_PHONE
                
                # Load session strings if available
                if hasattr(legacy_config, 'BABAGAVAT_SESSION') and not self.babagavat_session:
                    self.babagavat_session = legacy_config.BABAGAVAT_SESSION
                if hasattr(legacy_config, 'XXXGEISHA_SESSION') and not self.xxxgeisha_session:
                    self.xxxgeisha_session = legacy_config.XXXGEISHA_SESSION
                if hasattr(legacy_config, 'YAYINCILARA_SESSION') and not self.yayincilara_session:
                    self.yayincilara_session = legacy_config.YAYINCILARA_SESSION
                
                # Load database settings
                if hasattr(legacy_config, 'DATABASE_URL') and not self.database_url:
                    self.database_url = legacy_config.DATABASE_URL
                
                # Load OpenAI API key
                if hasattr(legacy_config, 'OPENAI_API_KEY') and not self.openai_api_key:
                    self.openai_api_key = legacy_config.OPENAI_API_KEY
                
            except ImportError:
                # Legacy config not available, that's fine
                pass
                
        except Exception:
            # Any error in loading legacy config should not break the app
            pass
    
    @property
    def redis_connection_url(self) -> str:
        """Get Redis connection URL."""
        if self.redis_url:
            return self.redis_url
        
        auth_part = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth_part}{self.redis_host}:{self.redis_port}/{self.redis_db}"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings 