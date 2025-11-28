#!/usr/bin/env python3
"""
Input Validation and Sanitization Middleware
Secure input handling across all APIs and bot handlers
"""

import html
import json
import re
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

import structlog
from pydantic import BaseModel, ValidationError, validator

logger = structlog.get_logger("gavatcore.input_validator")


class InputValidationError(Exception):
    """Input validation error"""

    pass


class TelegramInputValidator:
    """Validator for Telegram-specific inputs"""

    # Regex patterns for validation
    USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{5,32}$")
    USER_ID_PATTERN = re.compile(r"^\d{1,12}$")
    PHONE_PATTERN = re.compile(r"^\+?[1-9]\d{1,14}$")

    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"on\w+\s*=", re.IGNORECASE),
        re.compile(r"eval\s*\(", re.IGNORECASE),
        re.compile(r"exec\s*\(", re.IGNORECASE),
        re.compile(r"__import__", re.IGNORECASE),
        re.compile(r"subprocess", re.IGNORECASE),
        re.compile(r"os\.system", re.IGNORECASE),
    ]

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """Sanitize text input to prevent XSS and injection"""
        if not isinstance(text, str):
            return str(text)

        # HTML escape
        text = html.escape(text)

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern.search(text):
                logger.warning(f"Dangerous pattern detected in input: {text[:100]}")
                raise InputValidationError("Input contains potentially dangerous content")

        # Limit length
        if len(text) > 4096:
            text = text[:4096]
            logger.warning("Input truncated due to length limit")

        return text.strip()

    @classmethod
    def validate_user_id(cls, user_id: Union[str, int]) -> int:
        """Validate Telegram user ID"""
        user_id_str = str(user_id)

        if not cls.USER_ID_PATTERN.match(user_id_str):
            raise InputValidationError(f"Invalid user ID format: {user_id}")

        user_id_int = int(user_id_str)
        if user_id_int <= 0:
            raise InputValidationError("User ID must be positive")

        return user_id_int

    @classmethod
    def validate_username(cls, username: str) -> str:
        """Validate Telegram username"""
        if not isinstance(username, str):
            raise InputValidationError("Username must be string")

        username = username.lstrip("@").lower()

        if not cls.USERNAME_PATTERN.match(username):
            raise InputValidationError(f"Invalid username format: {username}")

        return username

    @classmethod
    def validate_phone(cls, phone: str) -> str:
        """Validate phone number"""
        if not isinstance(phone, str):
            raise InputValidationError("Phone must be string")

        # Remove spaces and dashes
        phone = re.sub(r"[\s\-]", "", phone)

        if not cls.PHONE_PATTERN.match(phone):
            raise InputValidationError(f"Invalid phone format: {phone}")

        return phone


class APIInputValidator:
    """Validator for API inputs"""

    @staticmethod
    def validate_json_payload(
        payload: Dict[str, Any], max_size: int = 1024 * 1024
    ) -> Dict[str, Any]:
        """Validate JSON payload size and structure"""
        try:
            payload_str = json.dumps(payload)
            if len(payload_str) > max_size:
                raise InputValidationError(f"Payload too large: {len(payload_str)} bytes")

            # Recursive sanitization
            return APIInputValidator._sanitize_dict(payload)

        except (TypeError, ValueError) as e:
            raise InputValidationError(f"Invalid JSON payload: {e}")

    @staticmethod
    def _sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dictionary values"""
        sanitized = {}

        for key, value in data.items():
            # Sanitize key
            if not isinstance(key, str) or len(key) > 100:
                raise InputValidationError(f"Invalid key: {key}")

            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[key] = TelegramInputValidator.sanitize_text(value)
            elif isinstance(value, dict):
                sanitized[key] = APIInputValidator._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    TelegramInputValidator.sanitize_text(item) if isinstance(item, str) else item
                    for item in value[:100]  # Limit list size
                ]
            else:
                sanitized[key] = value

        return sanitized


class MessageValidator(BaseModel):
    """Pydantic model for message validation"""

    text: str
    user_id: int
    chat_id: Optional[int] = None
    reply_to_message_id: Optional[int] = None

    @validator("text")
    def validate_text(cls, v):
        return TelegramInputValidator.sanitize_text(v)

    @validator("user_id")
    def validate_user_id(cls, v):
        return TelegramInputValidator.validate_user_id(v)


def validate_telegram_input(func: Callable) -> Callable:
    """Decorator to validate Telegram event inputs.
    
    Works with Telethon event handlers that receive only `event` argument,
    not `client, event`. The decorator extracts client from event if needed.
    """

    @wraps(func)
    async def wrapper(event, *args, **kwargs):
        try:
            # Validate basic event properties
            if hasattr(event, "sender_id") and event.sender_id:
                TelegramInputValidator.validate_user_id(event.sender_id)

            # Validate message text if present
            if hasattr(event, "message") and event.message and hasattr(event.message, "text"):
                if event.message.text:
                    event.message.text = TelegramInputValidator.sanitize_text(event.message.text)

            return await func(event, *args, **kwargs)

        except InputValidationError as e:
            logger.warning(f"Input validation failed for {func.__name__}: {e}")
            if hasattr(event, "respond"):
                await event.respond("❌ Invalid input format")
            return
        except Exception as e:
            logger.error(f"Unexpected error in input validation: {e}")
            raise

    return wrapper


def validate_api_input(schema: BaseModel):
    """Decorator to validate API inputs using Pydantic schemas"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Find request data in args/kwargs
                request_data = None

                for arg in args:
                    if isinstance(arg, dict):
                        request_data = arg
                        break

                if request_data is None:
                    request_data = kwargs.get("data", kwargs.get("request", {}))

                # Validate using schema
                validated_data = schema(**request_data)

                # Replace original data with validated data
                if "data" in kwargs:
                    kwargs["data"] = validated_data.dict()
                elif "request" in kwargs:
                    kwargs["request"] = validated_data.dict()

                return await func(*args, **kwargs)

            except ValidationError as e:
                logger.warning(f"API validation failed for {func.__name__}: {e}")
                raise InputValidationError(f"Validation error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in API validation: {e}")
                raise

        return wrapper

    return decorator


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    if not isinstance(filename, str):
        raise InputValidationError("Filename must be string")

    # Remove path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', "", filename)
    filename = re.sub(r"\.\.", "", filename)  # Remove path traversal
    filename = filename.strip(". ")  # Remove leading/trailing dots and spaces

    if not filename or len(filename) > 255:
        raise InputValidationError("Invalid filename")

    return filename


def validate_sql_identifier(identifier: str) -> str:
    """Validate SQL identifiers (table names, column names)"""
    if not isinstance(identifier, str):
        raise InputValidationError("SQL identifier must be string")

    # Only allow alphanumeric and underscore
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier):
        raise InputValidationError(f"Invalid SQL identifier: {identifier}")

    if len(identifier) > 63:  # PostgreSQL limit
        raise InputValidationError("SQL identifier too long")

    return identifier.lower()


# Rate limiting decorator
def rate_limit_check(action: str, max_requests: int = 30, window_seconds: int = 60):
    """Rate limiting decorator for Telethon event handlers.
    
    Works with handlers that receive only `event` argument.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(event, *args, **kwargs):
            from utilities.security_utils import rate_limit_check as do_rate_limit_check

            user_id = event.sender_id if hasattr(event, "sender_id") else 0
            allowed, remaining, reset = do_rate_limit_check(user_id, action)

            if not allowed:
                logger.warning(f"Rate limit exceeded for user {user_id}, action {action}")
                if hasattr(event, "respond"):
                    await event.respond(f"⚠️ Rate limit exceeded. Try again in {reset} seconds.")
                return

            return await func(event, *args, **kwargs)

        return wrapper

    return decorator
