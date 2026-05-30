#!/usr/bin/env python3
"""
⚠️ GAVATCORE SaaS EXCEPTIONS
Custom exception classes for API
"""

from typing import Optional, Dict, Any


class APIException(Exception):
    """Base API exception"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        code: str = "API_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(APIException):
    """Authentication failed"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=401,
            code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(APIException):
    """Authorization failed"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            status_code=403,
            code="AUTHORIZATION_ERROR"
        )


class ValidationError(APIException):
    """Validation failed"""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=422,
            code="VALIDATION_ERROR",
            details=details
        )


class PaymentError(APIException):
    """Payment processing error"""
    
    def __init__(self, message: str = "Payment processing failed"):
        super().__init__(
            message=message,
            status_code=402,
            code="PAYMENT_ERROR"
        )


class SubscriptionError(APIException):
    """Subscription related error"""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=400,
            code="SUBSCRIPTION_ERROR"
        )


class BotInstanceError(APIException):
    """Bot instance creation/management error"""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=500,
            code="BOT_INSTANCE_ERROR"
        ) 