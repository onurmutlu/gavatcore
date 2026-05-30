#!/usr/bin/env python3
"""
⚙️ GAVATCORE SaaS CONFIGURATION
Centralized configuration management
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://gavatcore:password@localhost/gavatcore_saas",
        env="DATABASE_URL"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    # JWT
    JWT_SECRET_KEY: str = Field(default="jwt-secret-key", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Stripe
    STRIPE_SECRET_KEY: str = Field(default="sk_test_...", env="STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: str = Field(default="pk_test_...", env="STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET: str = Field(default="whsec_...", env="STRIPE_WEBHOOK_SECRET")
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(default="", env="TELEGRAM_BOT_TOKEN")
    TELEGRAM_API_ID: str = Field(default="", env="TELEGRAM_API_ID")
    TELEGRAM_API_HASH: str = Field(default="", env="TELEGRAM_API_HASH")
    
    # TON Payments
    TON_WALLET_ADDRESS: str = Field(default="", env="TON_WALLET_ADDRESS")
    TON_API_KEY: str = Field(default="", env="TON_API_KEY")
    
    # OpenAI
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4o", env="OPENAI_MODEL")
    
    # Pricing (in Turkish Lira)
    PRICING_TRIAL_STARS: int = Field(default=100, env="PRICING_TRIAL_STARS")  # Telegram Stars
    PRICING_STARTER_TRY: int = Field(default=499, env="PRICING_STARTER_TRY")
    PRICING_PRO_TRY: int = Field(default=799, env="PRICING_PRO_TRY")  
    PRICING_DELUXE_TRY: int = Field(default=1499, env="PRICING_DELUXE_TRY")
    
    # Bot Instance Limits
    MAX_BOTS_STARTER: int = Field(default=1, env="MAX_BOTS_STARTER")
    MAX_BOTS_PRO: int = Field(default=3, env="MAX_BOTS_PRO")
    MAX_BOTS_DELUXE: int = Field(default=5, env="MAX_BOTS_DELUXE")
    
    # Coin Limits
    COINS_STARTER: int = Field(default=500, env="COINS_STARTER")
    COINS_PRO: int = Field(default=2000, env="COINS_PRO")
    COINS_DELUXE: int = Field(default=-1, env="COINS_DELUXE")  # -1 = unlimited
    
    # File Storage
    SESSION_STORAGE_PATH: str = Field(default="sessions/", env="SESSION_STORAGE_PATH")
    LOG_STORAGE_PATH: str = Field(default="./logs", env="LOG_STORAGE_PATH")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()


def get_subscription_limits(plan_name: str) -> dict:
    """Get subscription limits for a plan"""
    limits = {
        "trial": {
            "duration_days": 1,
            "max_bots": 1,
            "coins": 100,
            "features": ["basic_gpt", "manual_mode"]
        },
        "starter": {
            "duration_days": 30,
            "max_bots": 1,
            "coins": 500,
            "features": ["advanced_gpt", "hybrid_mode", "basic_support"]
        },
        "pro": {
            "duration_days": 30,
            "max_bots": 3,
            "coins": 2000,
            "features": ["premium_gpt", "all_modes", "scheduler", "priority_support"]
        },
        "deluxe": {
            "duration_days": 30,
            "max_bots": 5,
            "coins": 9999,
            "features": ["unlimited_coins", "custom_personas", "analytics", "24_7_support"]
        }
    }
    
    return limits.get(plan_name, limits["starter"])


def get_database_url() -> str:
    """Get database URL for different environments"""
    if settings.ENVIRONMENT == "production":
        return settings.DATABASE_URL
    elif settings.ENVIRONMENT == "testing":
        return settings.DATABASE_URL.replace("/gavatcore_saas", "/gavatcore_test")
    else:
        return settings.DATABASE_URL


def get_subscription_limits(plan: str) -> dict:
    """Get subscription limits for a plan"""
    limits = {
        "trial": {
            "max_bots": 1,
            "coins": 100,
            "duration_days": 1,
            "features": ["basic_bot"]
        },
        "starter": {
            "max_bots": settings.MAX_BOTS_STARTER,
            "coins": settings.COINS_STARTER,
            "duration_days": 30,
            "features": ["basic_bot", "gpt_replies"]
        },
        "pro": {
            "max_bots": settings.MAX_BOTS_PRO,
            "coins": settings.COINS_PRO,
            "duration_days": 30,
            "features": ["basic_bot", "gpt_replies", "scheduler", "hybrid_mode"]
        },
        "deluxe": {
            "max_bots": settings.MAX_BOTS_DELUXE,
            "coins": settings.COINS_DELUXE,
            "duration_days": 30,
            "features": ["all_features", "priority_support", "custom_gpt", "analytics"]
        }
    }
    
    return limits.get(plan, limits["starter"])


def get_pricing() -> dict:
    """Get pricing information"""
    return {
        "trial": {
            "price": 0,
            "currency": "TRY",
            "stars": settings.PRICING_TRIAL_STARS,
            "duration": "1 day"
        },
        "starter": {
            "price": settings.PRICING_STARTER_TRY,
            "currency": "TRY",
            "stars": settings.PRICING_STARTER_TRY * 10,  # 1 TRY = ~10 Stars
            "duration": "30 days"
        },
        "pro": {
            "price": settings.PRICING_PRO_TRY,
            "currency": "TRY", 
            "stars": settings.PRICING_PRO_TRY * 10,
            "duration": "30 days"
        },
        "deluxe": {
            "price": settings.PRICING_DELUXE_TRY,
            "currency": "TRY",
            "stars": settings.PRICING_DELUXE_TRY * 10,
            "duration": "30 days"
        }
    } 