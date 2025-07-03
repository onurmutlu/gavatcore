#!/usr/bin/env python3
"""
🔧 GAVATCore Configuration Module 🔧

Production-ready configuration management with comprehensive validation,
environment variable loading, and enterprise-grade error handling.

Features:
- Type-safe configuration with full type hints
- Comprehensive validation with descriptive error messages  
- Environment variable loading with fallbacks
- Security-focused sensitive data handling
- Dataclass-based configuration structures
- Extensive logging and debugging support

Example usage:
    from config import CONFIG, validate_config, ConfigValidationError
    
    # Validate current configuration
    if validate_config():
        print("✅ Configuration is valid!")
        
    # Get configuration summary (sensitive data masked)
    summary = get_config_summary()
    print(f"API configured: {summary['api_configured']}")
"""

import os
import logging
from typing import Optional, List, Dict, Any, Union, TypedDict, Literal
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

# Load .env file first
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
    print("🔑 .env dosyası başarıyla yüklendi!")
except ImportError:
    print("⚠️ python-dotenv bulunamadı, environment variables kullanılacak")

# Configure basic logging for config validation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gavatcore.config")

# ==================== TYPE DEFINITIONS ====================

class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing" 
    STAGING = "staging"
    PRODUCTION = "production"

class LogFormat(str, Enum):
    """Log format types."""
    JSON = "json"
    CONSOLE = "console"
    STRUCTURED = "structured"

class LogLevel(str, Enum):
    """Log level types."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class TelegramConfig:
    """Telegram API configuration with validation."""
    api_id: int
    api_hash: str
    session_name: str = "gavatcore_session"
    bot_username: str = "gavatcore_bot"
    bot_token: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate Telegram configuration after initialization."""
        if self.api_id <= 0:
            raise ConfigValidationError("API_ID must be a positive integer")
        if len(str(self.api_id)) < 4:
            raise ConfigValidationError("API_ID appears too short for a valid Telegram API ID")
        if not self.api_hash or len(self.api_hash) < 8:
            raise ConfigValidationError("API_HASH must be at least 8 characters long")
        if not self.session_name:
            raise ConfigValidationError("SESSION_NAME cannot be empty")

@dataclass
class DatabaseConfig:
    """Database configuration with connection details."""
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "gavatcore"
    redis_url: str = "redis://localhost:6379"
    redis_ttl: int = 3600  # Session TTL in seconds
    postgresql_url: str = "postgresql://localhost:5432/gavatcore"
    
    def __post_init__(self) -> None:
        """Validate database configuration."""
        if self.redis_ttl <= 0:
            raise ConfigValidationError("Redis TTL must be positive")

@dataclass 
class OpenAIConfig:
    """OpenAI API configuration with model settings."""
    api_key: str = ""
    model: str = "gpt-4"
    turbo_model: str = "gpt-3.5-turbo"
    vision_model: str = "gpt-4-vision-preview"
    max_tokens: int = 150
    temperature: float = 0.7
    
    def __post_init__(self) -> None:
        """Validate OpenAI configuration."""
        if self.max_tokens <= 0:
            raise ConfigValidationError("OpenAI max_tokens must be positive")
        if not (0.0 <= self.temperature <= 2.0):
            raise ConfigValidationError("OpenAI temperature must be between 0.0 and 2.0")

@dataclass
class SecurityConfig:
    """Security configuration with user and group access control."""
    authorized_users: List[int] = field(default_factory=list)
    allowed_groups: List[int] = field(default_factory=list)
    admin_users: List[int] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Validate security configuration."""
        if not self.authorized_users:
            logger.warning("No authorized users configured - admin commands will be disabled")
        
        # Validate user IDs are in valid Telegram range
        for user_id in self.authorized_users + self.admin_users:
            if not (1 <= user_id <= 2**63 - 1):
                raise ConfigValidationError(f"Invalid user ID: {user_id}")

@dataclass
class PerformanceConfig:
    """Performance and rate limiting configuration."""
    max_concurrent_operations: int = 10
    message_rate_limit: int = 30  # messages per minute
    contact_retry_attempts: int = 3
    contact_retry_delay: float = 2.0
    cleanup_interval_hours: int = 6
    cleanup_max_age_hours: int = 24
    cleanup_batch_size: int = 100
    
    def __post_init__(self) -> None:
        """Validate performance configuration."""
        if self.max_concurrent_operations <= 0:
            raise ConfigValidationError("max_concurrent_operations must be positive")
        if self.message_rate_limit <= 0:
            raise ConfigValidationError("message_rate_limit must be positive")
        if self.contact_retry_attempts < 0:
            raise ConfigValidationError("contact_retry_attempts cannot be negative")

@dataclass
class FeatureFlags:
    """Feature flags for enabling/disabling functionality."""
    contact_management: bool = True
    auto_cleanup: bool = True  
    gpt_responses: bool = False
    analytics: bool = True
    admin_commands: bool = True
    voice_ai: bool = False
    social_gaming: bool = True

class ConfigSummary(TypedDict, total=False):
    """Type definition for configuration summary."""
    environment: str
    debug_mode: bool
    api_configured: bool
    databases: Dict[str, bool]
    ai_services: Dict[str, Any]
    features: Dict[str, bool]
    authorized_users_count: int
    allowed_groups_count: int
    session_name: str
    bot_username: str

# ==================== CONFIGURATION EXCEPTIONS ====================

class ConfigValidationError(Exception):
    """
    Configuration validation error with detailed context.
    
    Attributes:
        field: The configuration field that failed validation
        value: The invalid value
        reason: Human-readable reason for the failure
    """
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        super().__init__(message)
        self.field = field
        self.value = value
        self.reason = message

# ==================== ENVIRONMENT DETECTION ====================

DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
ENVIRONMENT: Environment = Environment(os.getenv("ENVIRONMENT", "production"))

print(f"🔧 Config loading... Environment: {ENVIRONMENT.value} | Debug: {DEBUG_MODE}")

# ==================== PARSING FUNCTIONS ====================

def parse_user_ids(user_ids_str: Optional[str]) -> List[int]:
    """
    Parse comma-separated user IDs string into validated list of integers.
    
    Args:
        user_ids_str: Comma-separated user IDs string (e.g., "123456789,987654321")
        
    Returns:
        List of validated user IDs
        
    Raises:
        ConfigValidationError: If parsing fails or validation errors occur
        
    Example:
        >>> parse_user_ids("123456789,987654321")
        [123456789, 987654321]
        >>> parse_user_ids("")  # Returns empty list
        []
    """
    if user_ids_str is None:
        raise ConfigValidationError(
            "User IDs string cannot be None", 
            field="user_ids_str", 
            value=user_ids_str
        )
        
    if not user_ids_str or not user_ids_str.strip():
        return []  # Return empty list for empty string
    
    user_ids: List[int] = []
    for user_id_str in user_ids_str.split(','):
        user_id_str = user_id_str.strip()
        if not user_id_str:  # Skip empty strings
            continue
            
        try:
            user_id = int(user_id_str)
        except ValueError:
            raise ConfigValidationError(
                f"Invalid user ID format: '{user_id_str}' - must be a valid integer", 
                field="user_id", 
                value=user_id_str
            )
        
        if user_id <= 0:
            raise ConfigValidationError(
                f"User ID must be positive: {user_id}", 
                field="user_id", 
                value=user_id
            )
        
        if len(str(user_id)) < 6:
            raise ConfigValidationError(
                f"User ID too short: {user_id} - Telegram user IDs are typically 8-10 digits", 
                field="user_id", 
                value=user_id
            )
        
        if user_id > 9999999999999999999:  # Telegram's max range
            raise ConfigValidationError(
                f"User ID too large: {user_id} - exceeds Telegram's maximum user ID range", 
                field="user_id", 
                value=user_id
            )
        
        if user_id not in user_ids:  # Deduplicate
            user_ids.append(user_id)
    
    return user_ids

def parse_group_ids(group_ids_str: Optional[str]) -> List[int]:
    """
    Parse comma-separated group IDs string into validated list of integers.
    
    Args:
        group_ids_str: Comma-separated group IDs string (e.g., "-1001234567890,-1009876543210")
        
    Returns:
        List of validated group IDs (all negative for supergroups)
        
    Raises:
        ConfigValidationError: If parsing fails or validation errors occur
        
    Example:
        >>> parse_group_ids("-1001234567890,-1009876543210")
        [-1001234567890, -1009876543210]
        >>> parse_group_ids("")  # Returns empty list
        []
    """
    if not group_ids_str or not group_ids_str.strip():
        return []  # Return empty list for empty string
    
    group_ids: List[int] = []
    for group_id_str in group_ids_str.split(','):
        group_id_str = group_id_str.strip()
        if not group_id_str:  # Skip empty strings
            continue
            
        try:
            group_id = int(group_id_str)
        except ValueError:
            raise ConfigValidationError(
                f"Invalid group ID format: '{group_id_str}' - must be a valid integer", 
                field="group_id", 
                value=group_id_str
            )
        
        if group_id >= 0:
            raise ConfigValidationError(
                f"Group ID must be negative: {group_id} - Telegram supergroup IDs start with -100", 
                field="group_id", 
                value=group_id
            )
        
        if group_id not in group_ids:  # Deduplicate
            group_ids.append(group_id)
    
    return group_ids

# ==================== CONFIGURATION INITIALIZATION ====================

def get_api_id() -> int:
    """Get Telegram API ID with comprehensive validation."""
    api_id_str = os.getenv("API_ID") or os.getenv("TELEGRAM_API_ID", "0")
    try:
        api_id = int(api_id_str)
        if api_id <= 0:
            raise ConfigValidationError("API_ID must be positive integer")
        return api_id
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid API_ID: {api_id_str}")
        raise ConfigValidationError(f"Invalid API_ID: {api_id_str} - {e}")

def get_api_hash() -> str:
    """Get Telegram API Hash with validation."""
    api_hash = os.getenv("API_HASH") or os.getenv("TELEGRAM_API_HASH", "")
    if not api_hash or len(api_hash) < 10:
        logger.warning("API_HASH appears invalid or missing")
        raise ConfigValidationError("API_HASH is required and must be at least 10 characters")
    return api_hash

# Initialize configuration components
try:
    telegram_config = TelegramConfig(
        api_id=get_api_id(),
        api_hash=get_api_hash(),
        session_name=os.getenv("SESSION_NAME", "gavatcore_session"),
        bot_username=os.getenv("BOT_USERNAME", "gavatcore_bot"),
        bot_token=os.getenv("BOT_TOKEN") or os.getenv("ADMIN_BOT_TOKEN")
    )
    
    database_config = DatabaseConfig(
        mongodb_uri=os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        mongodb_database=os.getenv("MONGO_DATABASE", "gavatcore"),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        redis_ttl=int(os.getenv("REDIS_TTL", "3600")),
        postgresql_url=os.getenv("DATABASE_URL", "postgresql://localhost:5432/gavatcore")
    )
    
    openai_config = OpenAIConfig(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        turbo_model=os.getenv("OPENAI_TURBO_MODEL", "gpt-3.5-turbo"),
        vision_model=os.getenv("OPENAI_VISION_MODEL", "gpt-4-vision-preview"),
        max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "150")),
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    )
    
    # Parse authorized users from multiple sources
    authorized_users_list: List[int] = []
    
    # Method 1: AUTHORIZED_USERS (comma separated)
    if os.getenv("AUTHORIZED_USERS"):
        authorized_users_list.extend(parse_user_ids(os.getenv("AUTHORIZED_USERS")))
    
    # Method 2: GAVATCORE_ADMIN_ID (single user)
    if os.getenv("GAVATCORE_ADMIN_ID"):
        try:
            admin_id = int(os.getenv("GAVATCORE_ADMIN_ID", "0"))
            if admin_id > 0:
                authorized_users_list.append(admin_id)
        except (ValueError, TypeError):
            logger.warning(f"Invalid GAVATCORE_ADMIN_ID: {os.getenv('GAVATCORE_ADMIN_ID')}")
    
    # Method 3: ADMIN_USER_ID (fallback)
    if os.getenv("ADMIN_USER_ID"):
        try:
            admin_id = int(os.getenv("ADMIN_USER_ID", "0"))
            if admin_id > 0:
                authorized_users_list.append(admin_id)
        except (ValueError, TypeError):
            logger.warning(f"Invalid ADMIN_USER_ID: {os.getenv('ADMIN_USER_ID')}")
    
    security_config = SecurityConfig(
        authorized_users=list(set(authorized_users_list)),  # Remove duplicates
        allowed_groups=parse_group_ids(os.getenv("ALLOWED_GROUPS", "")),
        admin_users=authorized_users_list.copy()
    )
    
    performance_config = PerformanceConfig(
        max_concurrent_operations=int(os.getenv("MAX_CONCURRENT_OPERATIONS", "10")),
        message_rate_limit=int(os.getenv("MESSAGE_RATE_LIMIT", "30")),
        contact_retry_attempts=int(os.getenv("CONTACT_RETRY_ATTEMPTS", "3")),
        contact_retry_delay=float(os.getenv("CONTACT_RETRY_DELAY", "2.0")),
        cleanup_interval_hours=int(os.getenv("CLEANUP_INTERVAL_HOURS", "6")),
        cleanup_max_age_hours=int(os.getenv("CLEANUP_MAX_AGE_HOURS", "24")),
        cleanup_batch_size=int(os.getenv("CLEANUP_BATCH_SIZE", "100"))
    )
    
    feature_flags = FeatureFlags(
        contact_management=os.getenv("FEATURE_CONTACT_MANAGEMENT", "true").lower() == "true",
        auto_cleanup=os.getenv("FEATURE_AUTO_CLEANUP", "true").lower() == "true",
        gpt_responses=os.getenv("FEATURE_GPT_RESPONSES", "false").lower() == "true",
        analytics=os.getenv("FEATURE_ANALYTICS", "true").lower() == "true",
        admin_commands=os.getenv("FEATURE_ADMIN_COMMANDS", "true").lower() == "true",
        voice_ai=os.getenv("FEATURE_VOICE_AI", "false").lower() == "true",
        social_gaming=os.getenv("FEATURE_SOCIAL_GAMING", "true").lower() == "true"
    )

except Exception as e:
    logger.error(f"Configuration initialization failed: {e}")
    raise ConfigValidationError(f"Failed to initialize configuration: {e}")

# Legacy aliases for backward compatibility
API_ID: int = telegram_config.api_id
API_HASH: str = telegram_config.api_hash
SESSION_NAME: str = telegram_config.session_name
BOT_USERNAME: str = telegram_config.bot_username
BOT_TOKEN: Optional[str] = telegram_config.bot_token
ADMIN_BOT_TOKEN: Optional[str] = os.getenv("ADMIN_BOT_TOKEN")  # Admin bot token
TELEGRAM_API_ID: int = telegram_config.api_id
TELEGRAM_API_HASH: str = telegram_config.api_hash

MONGO_URI: str = database_config.mongodb_uri
MONGO_DATABASE: str = database_config.mongodb_database
REDIS_URL: str = database_config.redis_url
REDIS_TTL: int = database_config.redis_ttl
DATABASE_URL: str = database_config.postgresql_url

OPENAI_API_KEY: str = openai_config.api_key
OPENAI_MODEL: str = openai_config.model
OPENAI_TURBO_MODEL: str = openai_config.turbo_model
OPENAI_VISION_MODEL: str = openai_config.vision_model
OPENAI_MAX_TOKENS: int = openai_config.max_tokens

AUTHORIZED_USERS: List[int] = security_config.authorized_users
ALLOWED_GROUPS: List[int] = security_config.allowed_groups

MAX_CONCURRENT_OPERATIONS: int = performance_config.max_concurrent_operations
MESSAGE_RATE_LIMIT: int = performance_config.message_rate_limit

FEATURES: Dict[str, bool] = {
    "contact_management": feature_flags.contact_management,
    "auto_cleanup": feature_flags.auto_cleanup,
    "gpt_responses": feature_flags.gpt_responses,
    "analytics": feature_flags.analytics,
    "admin_commands": feature_flags.admin_commands,
    "voice_ai": feature_flags.voice_ai,
    "social_gaming": feature_flags.social_gaming
}

# System configuration
LOG_LEVEL: LogLevel = LogLevel(os.getenv("LOG_LEVEL", "INFO" if not DEBUG_MODE else "DEBUG"))
LOG_FORMAT: LogFormat = LogFormat(os.getenv("LOG_FORMAT", "json" if ENVIRONMENT == Environment.PRODUCTION else "console"))

# ==================== AI CONFIGURATION (ADVANCED) ====================

# AI Model Configuration
CRM_AI_MODEL: str = os.getenv("CRM_AI_MODEL", "gpt-4")
CHARACTER_AI_MODEL: str = os.getenv("CHARACTER_AI_MODEL", "gpt-4")
SOCIAL_AI_MODEL: str = os.getenv("SOCIAL_AI_MODEL", "gpt-3.5-turbo")

# AI Temperature Settings
CRM_AI_TEMPERATURE: float = float(os.getenv("CRM_AI_TEMPERATURE", "0.3"))
CHARACTER_AI_TEMPERATURE: float = float(os.getenv("CHARACTER_AI_TEMPERATURE", "0.7"))
SOCIAL_AI_TEMPERATURE: float = float(os.getenv("SOCIAL_AI_TEMPERATURE", "0.8"))

# AI Token Limits
CRM_AI_MAX_TOKENS: int = int(os.getenv("CRM_AI_MAX_TOKENS", "2000"))
CHARACTER_AI_MAX_TOKENS: int = int(os.getenv("CHARACTER_AI_MAX_TOKENS", "500"))
SOCIAL_AI_MAX_TOKENS: int = int(os.getenv("SOCIAL_AI_MAX_TOKENS", "300"))

# AI Feature Flags
ENABLE_VOICE_AI: bool = os.getenv("ENABLE_VOICE_AI", "false").lower() == "true"
ENABLE_CRM_AI: bool = os.getenv("ENABLE_CRM_AI", "true").lower() == "true"
ENABLE_SOCIAL_AI: bool = os.getenv("ENABLE_SOCIAL_AI", "true").lower() == "true"
ENABLE_ADVANCED_ANALYTICS: bool = os.getenv("ENABLE_ADVANCED_ANALYTICS", "true").lower() == "true"
ENABLE_REAL_TIME_ANALYSIS: bool = os.getenv("ENABLE_REAL_TIME_ANALYSIS", "true").lower() == "true"
ENABLE_PREDICTIVE_ANALYTICS: bool = os.getenv("ENABLE_PREDICTIVE_ANALYTICS", "true").lower() == "true"
ENABLE_SENTIMENT_ANALYSIS: bool = os.getenv("ENABLE_SENTIMENT_ANALYSIS", "true").lower() == "true"
ENABLE_PERSONALITY_ANALYSIS: bool = os.getenv("ENABLE_PERSONALITY_ANALYSIS", "true").lower() == "true"

# AI Performance Settings
AI_CONCURRENT_REQUESTS: int = int(os.getenv("AI_CONCURRENT_REQUESTS", "5"))
AI_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "60"))

# ==================== AI UTILITY FUNCTIONS ====================

def get_ai_model_for_task(task_type: str) -> str:
    """
    Get the appropriate AI model for a specific task type.
    
    Args:
        task_type: Type of task (e.g., 'crm_analysis', 'character_interaction')
        
    Returns:
        str: AI model name for the task
    """
    task_models = {
        "crm_analysis": CRM_AI_MODEL,
        "character_interaction": CHARACTER_AI_MODEL,
        "social_gaming": SOCIAL_AI_MODEL,
        "customer_support": CRM_AI_MODEL,
        "content_generation": CHARACTER_AI_MODEL,
        "sentiment_analysis": SOCIAL_AI_MODEL,
        "data_analysis": CRM_AI_MODEL
    }
    
    return task_models.get(task_type, CRM_AI_MODEL)  # Default to CRM model

def get_ai_temperature_for_task(task_type: str) -> float:
    """
    Get the appropriate AI temperature for a specific task type.
    
    Args:
        task_type: Type of task
        
    Returns:
        float: Temperature value for the task
    """
    task_temperatures = {
        "crm_analysis": CRM_AI_TEMPERATURE,
        "character_interaction": CHARACTER_AI_TEMPERATURE,
        "social_gaming": SOCIAL_AI_TEMPERATURE,
        "predictive_analytics": 0.2,
        "creative_writing": 0.9,
        "technical_support": 0.1,
        "sentiment_analysis": 0.3
    }
    
    return task_temperatures.get(task_type, 0.7)  # Default temperature

def get_ai_max_tokens_for_task(task_type: str) -> int:
    """
    Get the appropriate max tokens for a specific task type.
    
    Args:
        task_type: Type of task
        
    Returns:
        int: Max tokens for the task
    """
    task_max_tokens = {
        "crm_analysis": CRM_AI_MAX_TOKENS,
        "character_interaction": CHARACTER_AI_MAX_TOKENS,
        "social_gaming": SOCIAL_AI_MAX_TOKENS,
        "sentiment_analysis": 100,
        "quick_response": 50,
        "detailed_analysis": 4000,
        "summary_generation": 300
    }
    
    return task_max_tokens.get(task_type, 1000)  # Default max tokens

# ==================== CONFIGURATION FUNCTIONS ====================

def load_env_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables with comprehensive validation.
    
    Returns:
        Dictionary containing validated configuration values
        
    Raises:
        ConfigValidationError: If required environment variables are missing or invalid
        
    Example:
        >>> config = load_env_config()
        >>> print(f"API ID: {config['API_ID']}")
    """
    # Check for required environment variables
    api_id_str = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    authorized_users_str = os.getenv("AUTHORIZED_USERS")
    
    # Check if any required env vars are missing completely
    if api_id_str is None or api_hash is None or authorized_users_str is None:
        raise ConfigValidationError(
            "Missing required environment variables: TELEGRAM_API_ID, TELEGRAM_API_HASH, AUTHORIZED_USERS",
            field="environment_variables"
        )
    
    # Validate API ID
    try:
        api_id = int(api_id_str)
    except (ValueError, TypeError):
        raise ConfigValidationError(
            "Invalid API_ID: must be a valid integer",
            field="TELEGRAM_API_ID",
            value=api_id_str
        )
    
    # Validate API Hash - check for empty string specifically
    if not api_hash or not api_hash.strip():
        raise ConfigValidationError(
            "API_HASH cannot be empty",
            field="TELEGRAM_API_HASH",
            value=api_hash
        )
    
    # Parse authorized users
    try:
        authorized_users = parse_user_ids(authorized_users_str)
    except ConfigValidationError as e:
        raise ConfigValidationError(
            f"Invalid AUTHORIZED_USERS: {e}",
            field="AUTHORIZED_USERS",
            value=authorized_users_str
        )
    
    # Parse debug mode
    debug_mode_str = os.getenv("DEBUG_MODE", "false").lower()
    debug_mode = debug_mode_str in ["true", "1", "yes", "on"]
    
    return {
        "API_ID": api_id,
        "API_HASH": api_hash,
        "AUTHORIZED_USERS": authorized_users,
        "DEBUG_MODE": debug_mode
    }

def validate_config(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Validate configuration dictionary or current global config with detailed error reporting.
    
    Args:
        config: Optional configuration dictionary to validate. 
               If None, validates current global configuration.
               
    Returns:
        True if configuration is valid
        
    Raises:
        ConfigValidationError: If configuration is invalid with detailed error context
        
    Example:
        >>> if validate_config():
        ...     print("Configuration is valid!")
    """
    if config is None:
        # Validate current global configuration
        errors: List[str] = []
        warnings: List[str] = []
        
        # Required fields validation
        if not API_ID or API_ID <= 0:
            errors.append("API_ID is required and must be positive")
        
        if not API_HASH:
            errors.append("API_HASH is required")
        
        if not AUTHORIZED_USERS:
            errors.append("No authorized users configured")
        
        # Warn about missing optional components
        if not OPENAI_API_KEY:
            warnings.append("OpenAI API key not configured - GPT features will be disabled")
        
        if not MONGO_URI or MONGO_URI == "mongodb://localhost:27017":
            warnings.append("Using default MongoDB URI - ensure MongoDB is running locally")
        
        # Print warnings
        if warnings:
            logger.warning("Configuration warnings:")
            for warning in warnings:
                logger.warning(f"  ⚠️ {warning}")
        
        if errors:
            error_msg = f"Configuration validation failed: {'; '.join(errors)}"
            raise ConfigValidationError(error_msg, field="global_config")
        
        return True
    else:
        # Validate provided configuration dictionary
        required_fields = ["API_ID", "API_HASH", "AUTHORIZED_USERS"]
        
        for field in required_fields:
            if field not in config:
                raise ConfigValidationError(
                    f"Missing required configuration field: {field}",
                    field=field
                )
            
            if config[field] is None:
                raise ConfigValidationError(
                    f"Configuration field cannot be None: {field}",
                    field=field,
                    value=config[field]
                )
        
        # Validate API_ID
        if not isinstance(config["API_ID"], int) or config["API_ID"] <= 0:
            raise ConfigValidationError(
                "API_ID must be a positive integer",
                field="API_ID",
                value=config["API_ID"]
            )
        
        # Validate API_HASH
        if not isinstance(config["API_HASH"], str) or not config["API_HASH"].strip():
            raise ConfigValidationError(
                "API_HASH must be a non-empty string",
                field="API_HASH",
                value=config["API_HASH"]
            )
        
        # Validate AUTHORIZED_USERS
        if not isinstance(config["AUTHORIZED_USERS"], list) or len(config["AUTHORIZED_USERS"]) == 0:
            raise ConfigValidationError(
                "AUTHORIZED_USERS must be a non-empty list",
                field="AUTHORIZED_USERS",
                value=config["AUTHORIZED_USERS"]
            )
        
        return True

def get_config_summary(config: Optional[Dict[str, Any]] = None) -> ConfigSummary:
    """
    Get a comprehensive summary of current configuration for debugging and monitoring.
    
    Args:
        config: Optional configuration dictionary to summarize.
               If None, summarizes current global configuration.
               
    Returns:
        ConfigSummary with sensitive data properly masked
        
    Example:
        >>> summary = get_config_summary()
        >>> print(f"Environment: {summary['environment']}")
        >>> print(f"API configured: {summary['api_configured']}")
    """
    if config is None:
        # Use global configuration
        return ConfigSummary(
            environment=ENVIRONMENT.value,
            debug_mode=DEBUG_MODE,
            api_configured=bool(API_ID and API_HASH),
            databases={
                "mongodb": bool(MONGO_URI and MONGO_URI != "mongodb://localhost:27017"),
                "redis": bool(REDIS_URL and REDIS_URL != "redis://localhost:6379"),
                "postgresql": bool(DATABASE_URL and DATABASE_URL != "postgresql://localhost:5432/gavatcore"),
            },
            ai_services={
                "openai": bool(OPENAI_API_KEY),
                "models": {
                    "primary": OPENAI_MODEL,
                    "turbo": OPENAI_TURBO_MODEL,
                    "vision": OPENAI_VISION_MODEL,
                }
            },
            features=FEATURES,
            authorized_users_count=len(AUTHORIZED_USERS),
            allowed_groups_count=len(ALLOWED_GROUPS),
            session_name=SESSION_NAME,
            bot_username=BOT_USERNAME,
        )
    else:
        # Summarize provided configuration with sensitive data masking
        sensitive_keys = ["api_hash", "password", "secret", "token", "key"]
        
        def mask_sensitive_value(key: str, value: Any) -> Any:
            """Mask sensitive values in configuration for security."""
            if isinstance(key, str):
                key_lower = key.lower()
                if any(sensitive in key_lower for sensitive in sensitive_keys):
                    if isinstance(value, str) and len(value) > 4:
                        return value[:2] + "*" * (len(value) - 4) + value[-2:]
                    return "***masked***"
            return value
        
        summary = {}
        for key, value in config.items():
            if isinstance(value, dict):
                summary[key] = {k: mask_sensitive_value(k, v) for k, v in value.items()}
            else:
                summary[key] = mask_sensitive_value(key, value)
        
        # Add computed fields for better insights
        summary["api_configured"] = bool(config.get("API_ID") and config.get("API_HASH"))
        summary["authorized_users_count"] = len(config.get("AUTHORIZED_USERS", []))
        summary["debug_mode"] = config.get("DEBUG_MODE", False)
        
        return ConfigSummary(**summary)

def create_example_env() -> str:
    """
    Create an example environment configuration file content.
    
    Returns:
        str: Example .env file content
    """
    return f"""# 🔥 GAVATCore Production Configuration Template 🔥
# Copy this file to .env and fill in your actual values

# ==================== TELEGRAM API CONFIGURATION ====================
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here

# ==================== AUTHORIZATION ====================
AUTHORIZED_USERS=123456789,987654321
ADMIN_IDS=123456789

# ==================== BOT CONFIGURATION ====================
BOT_USERNAME=your_bot_username
DEBUG_MODE=false
PRODUCTION_MODE=true

# ==================== OPENAI CONFIGURATION ====================
OPENAI_API_KEY=sk-your-openai-api-key-here
CRM_AI_MODEL=gpt-4
CHARACTER_AI_MODEL=gpt-4
SOCIAL_AI_MODEL=gpt-3.5-turbo

# ==================== DATABASE CONFIGURATION ====================
DATABASE_URL=sqlite:///data/gavatcore.db
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://localhost:27017/gavatcore

# ==================== FEATURE FLAGS ====================
ENABLE_CRM_AI=true
ENABLE_SOCIAL_AI=true
ENABLE_ADVANCED_ANALYTICS=true
ENABLE_VOICE_AI=false

# ==================== PERFORMANCE SETTINGS ====================
MAX_CONCURRENT_OPERATIONS=10
MESSAGE_RATE_LIMIT=30
CONTACT_RETRY_ATTEMPTS=3

# ==================== SECURITY SETTINGS ====================
SESSION_TIMEOUT=3600
ENABLE_RATE_LIMITING=true
SECURE_MODE=true

# ==================== LOGGING ====================
LOG_LEVEL=INFO
ENABLE_DEBUG_LOGGING=false
LOG_FILE_PATH=logs/gavatcore.log
"""

# ==================== EXPORT CONFIGURATION ====================

__all__ = [
    # Configuration classes
    "TelegramConfig", "DatabaseConfig", "OpenAIConfig", "SecurityConfig", 
    "PerformanceConfig", "FeatureFlags", "ConfigSummary",
    
    # Enums
    "Environment", "LogFormat", "LogLevel",
    
    # Legacy compatibility
    "API_ID", "API_HASH", "SESSION_NAME", "BOT_USERNAME", "BOT_TOKEN",
    "ADMIN_BOT_TOKEN", "TELEGRAM_API_ID", "TELEGRAM_API_HASH",
    "MONGO_URI", "MONGO_DATABASE", "REDIS_URL", "REDIS_TTL", "DATABASE_URL",
    "OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_TURBO_MODEL", "OPENAI_VISION_MODEL", "OPENAI_MAX_TOKENS",
    "AUTHORIZED_USERS", "ALLOWED_GROUPS", "FEATURES",
    "DEBUG_MODE", "ENVIRONMENT", "LOG_LEVEL", "LOG_FORMAT",
    "MAX_CONCURRENT_OPERATIONS", "MESSAGE_RATE_LIMIT",
    
    # AI Configuration
    "CRM_AI_MODEL", "CHARACTER_AI_MODEL", "SOCIAL_AI_MODEL",
    "CRM_AI_TEMPERATURE", "CHARACTER_AI_TEMPERATURE", "SOCIAL_AI_TEMPERATURE",
    "CRM_AI_MAX_TOKENS", "CHARACTER_AI_MAX_TOKENS", "SOCIAL_AI_MAX_TOKENS",
    "ENABLE_VOICE_AI", "ENABLE_CRM_AI", "ENABLE_SOCIAL_AI", "ENABLE_ADVANCED_ANALYTICS",
    "ENABLE_REAL_TIME_ANALYSIS", "ENABLE_PREDICTIVE_ANALYTICS", "ENABLE_SENTIMENT_ANALYSIS",
    "ENABLE_PERSONALITY_ANALYSIS", "AI_CONCURRENT_REQUESTS", "AI_RATE_LIMIT_PER_MINUTE",
    
    # AI Utility Functions
    "get_ai_model_for_task", "get_ai_temperature_for_task", "get_ai_max_tokens_for_task",
    
    # Functions
    "validate_config", "get_config_summary", "load_env_config", "create_example_env",
    "parse_user_ids", "parse_group_ids",
    
    # Exceptions
    "ConfigValidationError",
    
    # Configuration instances
    "telegram_config", "database_config", "openai_config", "security_config",
    "performance_config", "feature_flags"
]

# ==================== AUTO-VALIDATION ====================

if __name__ == "__main__":
    print("🔧 Testing configuration...")
    try:
        if validate_config():
            print("🎉 Configuration is production ready!")
            print("\n📊 Configuration Summary:")
            import json
            summary = get_config_summary()
            print(json.dumps(dict(summary), indent=2))
        else:
            print("🔧 Example .env template:")
            print(create_example_env())
    except ConfigValidationError as e:
        print(f"🚨 Critical configuration error: {e}")
        if hasattr(e, 'field') and e.field:
            print(f"   Field: {e.field}")
        if hasattr(e, 'value') and e.value is not None:
            print(f"   Value: {e.value}")
else:
    # Validate when imported (only warnings in import mode)
    try:
        validate_config()
        print(f"✅ GAVATCore configuration loaded successfully!")
        print(f"   Environment: {ENVIRONMENT.value}")
        print(f"   Debug Mode: {DEBUG_MODE}")
        print(f"   Authorized Users: {len(AUTHORIZED_USERS)}")
        print(f"   Features Enabled: {sum(FEATURES.values())}/{len(FEATURES)}")
    except ConfigValidationError as e:
        logger.warning(f"Configuration validation warnings: {e}")
        print("⚠️ Configuration loaded with warnings - check logs for details")

# OpenAI TTS Model
OPENAI_TTS_MODEL = "tts-1"

# File Backup Directory
FILE_BACKUP_DIR = "backups"

# Error Log Path
ERROR_LOG_PATH = "logs/errors"

# MongoDB URI
MONGODB_URI = "mongodb://localhost:27017/gavatcore"

# Redis URI
REDIS_URI = "redis://localhost:6379/0"

# PostgreSQL URI
POSTGRESQL_URI = "postgresql://localhost:5432/gavatcore"

# Cache Settings
CACHE_ENABLED = True
CACHE_TTL = 3600  # 1 hour

# Analytics Settings
ANALYTICS_ENABLED = True
ANALYTICS_BATCH_SIZE = 100

# Performance Settings
PERFORMANCE_MONITORING = True
PERFORMANCE_LOG_INTERVAL = 300  # 5 minutes

# Security Settings
SECURITY_ENABLED = True
API_KEY_REQUIRED = True

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "json"

# Feature Flags
FEATURES = {
    "ai_content": True,
    "analytics": True,
    "caching": True,
    "performance": True,
    "security": True,
    "logging": True,
    "monitoring": True
}

# Eksik configler
MAX_BACKUP_COUNT = 10
ADMIN_EMAIL = "admin@example.com"
DEFAULT_ENCODING = "utf-8"
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USER = "noreply@example.com"
SMTP_PASSWORD = "password"

OPENAI_TTS_VOICE = "alloy"
OPENAI_STT_MODEL = "whisper-1"
CHARACTER_AI_MODEL = "gpt-4o"
CHARACTER_AI_TEMPERATURE = 0.7
CHARACTER_AI_MAX_TOKENS = 1024
ENABLE_VOICE_AI = True
ENABLE_SENTIMENT_ANALYSIS = True
ENABLE_PERSONALITY_ANALYSIS = True

METRICS_RETENTION_DAYS = 30
