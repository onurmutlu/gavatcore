#!/usr/bin/env python3
"""
📦 SUBSCRIPTION MODEL
Database model for user subscriptions
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from typing import Optional
from app.database.connection import Base


class Subscription(Base):
    """Subscription model"""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Plan details
    plan_name = Column(String(20), nullable=False)  # trial, starter, pro, deluxe
    plan_price = Column(Numeric(10, 2), nullable=False)
    plan_currency = Column(String(3), default="TRY")
    
    # Subscription period
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_trial = Column(Boolean, default=False)
    auto_renew = Column(Boolean, default=True)
    
    # Payment info
    payment_method = Column(String(20), nullable=False)  # stripe, stars, ton
    external_subscription_id = Column(String(100), nullable=True)  # Stripe subscription ID
    
    # Usage limits
    max_bots = Column(Integer, default=1)
    max_coins = Column(Integer, default=500)
    features = Column(Text, nullable=True)  # JSON string
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Subscription {self.plan_name} for User {self.user_id}>"
    
    @property
    def is_expired(self) -> bool:
        """Check if subscription is expired"""
        return datetime.utcnow() > self.expires_at  # type: ignore
    
    @property
    def days_remaining(self):
        """Get days remaining in subscription"""
        if self.is_expired:  # type: ignore
            return 0
        delta = self.expires_at - datetime.utcnow()
        return delta.days
    
    @property
    def usage_percentage(self):
        """Get usage percentage of subscription period"""
        total_days = (self.expires_at - self.started_at).days
        elapsed_days = (datetime.utcnow() - self.started_at).days
        if total_days <= 0:
            return 100
        return min(100, (elapsed_days / total_days) * 100)
    
    def extend_subscription(self, days: int):
        """Extend subscription by given days"""
        if self.is_expired:  # type: ignore
            self.expires_at = datetime.utcnow() + timedelta(days=days)
        else:
            self.expires_at = self.expires_at + timedelta(days=days)
    
    def cancel_subscription(self, reason: Optional[str] = None):
        """Cancel subscription"""
        self.is_active = False
        self.auto_renew = False
        self.cancelled_at = datetime.utcnow()
        self.cancellation_reason = reason
    
    def get_features_list(self):
        """Get features as list"""
        if self.features:  # type: ignore
            import json
            try:
                return json.loads(self.features)  # type: ignore
            except:
                return []
        return [] 