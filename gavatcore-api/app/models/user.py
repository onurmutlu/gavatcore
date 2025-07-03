#!/usr/bin/env python3
"""
👤 USER MODEL
Database model for users
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(BigInteger, unique=True, index=True, nullable=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    
    # Authentication
    password_hash = Column(String(255), nullable=True)  # Optional for Telegram auth
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Telegram specific
    telegram_username = Column(String(50), nullable=True)
    telegram_first_name = Column(String(50), nullable=True)
    telegram_last_name = Column(String(50), nullable=True)
    telegram_language_code = Column(String(10), default="tr")
    
    # Registration source
    registration_source = Column(String(20), default="web")  # web, telegram, api
    referral_code = Column(String(20), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # JSON fields for additional data
    preferences = Column(Text, nullable=True)  # JSON string
    user_metadata = Column(Text, nullable=True)     # JSON string
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    bot_instances = relationship("BotInstance", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"
    
    @property
    def full_name(self):
        """Get full name"""
        if self.first_name and self.last_name:  # type: ignore
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:  # type: ignore
            return self.first_name
        elif self.telegram_first_name and self.telegram_last_name:  # type: ignore
            return f"{self.telegram_first_name} {self.telegram_last_name}"
        elif self.telegram_first_name:  # type: ignore
            return self.telegram_first_name
        else:
            return self.username
    
    def get_active_subscription(self):
        """Get current active subscription"""
        for sub in self.subscriptions:
            if sub.is_active:
                return sub
        return None 