#!/usr/bin/env python3
"""
Centralized Configuration Management System
Replaces scattered configuration across the codebase
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import structlog
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

logger = structlog.get_logger("gavatcore.config")


class ConfigValidationError(Exception):
    """Configuration validation error"""

    pass


@dataclass
class DatabaseConfig:
    """Database configuration"""

    postgresql_url: Optional[str] = None
    sqlite_path: str = "data/gavatcore.db"
    mongodb_url: Optional[str] = None
    redis_url: str = "redis://localhost:6379/0"
    connection_pool_size: int = 10
    max_overflow: int = 20


@dataclass
class TelegramConfig:
    """Telegram API configuration"""

    api_id: int
    api_hash: str
    session_name: str = "gavatcore"
    device_model: str = "GavatCore Bot"
    system_version: str = "1.0"
    app_version: str = "1.0"
    use_ipv6: bool = False

    def __post_init__(self):
        if self.api_id <= 0:
            raise ConfigValidationError("API_ID must be positive")
        if len(self.api_hash) < 8:
            raise ConfigValidationError("API_HASH must be at least 8 characters")


@dataclass
class SecurityConfig:
    """Security configuration"""

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    rate_limit_window: int = 60
    rate_limit_max_requests: int = 30
    admin_user_ids: List[int] = field(default_factory=list)
    authorized_users_file: str = "data/authorized_users.json"
    security_log_path: str = "logs/security.log"

    def __post_init__(self):
        if not self.jwt_secret:
            raise ConfigValidationError("JWT_SECRET must be set")
        if len(self.jwt_secret) < 32:
            raise ConfigValidationError("JWT_SECRET must be at least 32 characters")


@dataclass
class AIConfig:
    """AI and OpenAI configuration"""

    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.7
    default_reply_mode: str = "hybrid"

    def __post_init__(self):
        if self.openai_temperature < 0.0 or self.openai_temperature > 2.0:
            raise ConfigValidationError("Temperature must be between 0.0 and 2.0")


@dataclass
class PerformanceConfig:
    """Performance and optimization settings"""

    max_concurrent_operations: int = 10
    message_rate_limit: int = 30
    cache_ttl_seconds: int = 300
    connection_timeout: int = 30
    request_timeout: int = 60
    enable_performance_monitoring: bool = True

    def __post_init__(self):
        if self.max_concurrent_operations <= 0:
            raise ConfigValidationError("max_concurrent_operations must be positive")


class GavatCoreConfig(BaseSettings):
    """Main configuration class using Pydantic for validation"""

    # Environment
    environment: str = Field(default="development")
    debug: bool = Field(default=False)

    # Core configs - use Field with default_factory for Pydantic v2
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    telegram: TelegramConfig
    security: SecurityConfig
    ai: AIConfig = Field(default_factory=AIConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)

    # Paths
    data_dir: str = Field(default="data")
    logs_dir: str = Field(default="logs")
    sessions_dir: str = Field(default="sessions")
    character_config_dir: str = Field(default="character_engine/character_config")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "allow",
        "arbitrary_types_allowed": True,
    }

    @model_validator(mode="before")
    @classmethod
    def validate_nested_configs(cls, data: Any) -> Any:
        """Validate and convert nested configuration objects"""
        if isinstance(data, dict):
            # Convert telegram dict to TelegramConfig
            if "telegram" in data and isinstance(data["telegram"], dict):
                data["telegram"] = TelegramConfig(**data["telegram"])
            # Convert security dict to SecurityConfig
            if "security" in data and isinstance(data["security"], dict):
                data["security"] = SecurityConfig(**data["security"])
            # Convert ai dict to AIConfig
            if "ai" in data and isinstance(data["ai"], dict):
                data["ai"] = AIConfig(**data["ai"])
        return data

    @model_validator(mode="after")
    def create_directories(self) -> "GavatCoreConfig":
        """Create necessary directories after initialization"""
        for dir_path in [
            self.data_dir,
            self.logs_dir,
            self.sessions_dir,
            self.character_config_dir,
        ]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        return self


def load_config() -> GavatCoreConfig:
    """Load and validate configuration"""
    try:
        # Required environment variables
        telegram_config = TelegramConfig(
            api_id=int(os.getenv("TELEGRAM_API_ID", 0)),
            api_hash=os.getenv("TELEGRAM_API_HASH", ""),
            session_name=os.getenv("TELEGRAM_SESSION_NAME", "gavatcore"),
        )

        security_config = SecurityConfig(
            jwt_secret=os.getenv("JWT_SECRET", ""),
            admin_user_ids=[
                int(x) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip()
            ],
        )

        ai_config = AIConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        )

        config = GavatCoreConfig(telegram=telegram_config, security=security_config, ai=ai_config)

        logger.info("Configuration loaded successfully")
        return config

    except Exception as e:
        logger.error(f"Configuration loading failed: {e}")
        raise ConfigValidationError(f"Failed to load configuration: {e}")


# Global configuration instance
_config: Optional[GavatCoreConfig] = None


def get_config() -> GavatCoreConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


# Convenience functions for backward compatibility
def get_telegram_config() -> TelegramConfig:
    return get_config().telegram


def get_security_config() -> SecurityConfig:
    return get_config().security


def get_ai_config() -> AIConfig:
    return get_config().ai


def get_performance_config() -> PerformanceConfig:
    return get_config().performance
