#!/usr/bin/env python3
"""
💳 PAYMENT MODEL
Database model for payments and transactions
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base


class Payment(Base):
    """Payment model"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    
    # Payment identification
    payment_intent_id = Column(String(100), unique=True, nullable=False)  # External payment ID
    external_payment_id = Column(String(100), nullable=True)  # Stripe/TON transaction ID
    
    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="TRY")
    payment_method = Column(String(20), nullable=False)  # stripe, stars, ton
    
    # Plan information
    plan_name = Column(String(20), nullable=False)
    plan_duration_days = Column(Integer, default=30)
    
    # Status
    status = Column(String(20), default="pending")  # pending, completed, failed, refunded
    is_successful = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Payment method specific data
    stripe_data = Column(Text, nullable=True)          # JSON for Stripe data
    stars_data = Column(Text, nullable=True)           # JSON for Telegram Stars data  
    ton_data = Column(Text, nullable=True)             # JSON for TON data
    
    # Error handling
    failure_reason = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Refund information
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    refund_amount = Column(Numeric(10, 2), nullable=True)
    refund_reason = Column(Text, nullable=True)
    
    # Webhook tracking
    webhook_received = Column(Boolean, default=False)
    webhook_data = Column(Text, nullable=True)         # JSON webhook payload
    
    # Relationships
    user = relationship("User", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payments")

    def __repr__(self):
        return f"<Payment {self.payment_intent_id} - {self.amount} {self.currency}>"
    
    def mark_as_completed(self):
        """Mark payment as completed"""
        self.status = "completed"
        self.is_successful = True
        self.completed_at = datetime.utcnow()
    
    def mark_as_failed(self, reason: str):
        """Mark payment as failed"""
        self.status = "failed"
        self.is_successful = False
        self.failed_at = datetime.utcnow()
        self.failure_reason = reason
        self.retry_count += 1
    
    def mark_as_refunded(self, amount: float, reason: str):
        """Mark payment as refunded"""
        self.status = "refunded"
        self.refunded_at = datetime.utcnow()
        self.refund_amount = amount
        self.refund_reason = reason
    
    def process_webhook(self, webhook_data: dict):
        """Process webhook data"""
        import json
        self.webhook_received = True
        self.webhook_data = json.dumps(webhook_data)
        
        # Process based on payment method
        if self.payment_method == "stripe":  # type: ignore
            self._process_stripe_webhook(webhook_data)
        elif self.payment_method == "stars":  # type: ignore
            self._process_stars_webhook(webhook_data)
        elif self.payment_method == "ton":  # type: ignore
            self._process_ton_webhook(webhook_data)
    
    def _process_stripe_webhook(self, data: dict):
        """Process Stripe webhook"""
        event_type = data.get("type")
        
        if event_type == "payment_intent.succeeded":
            self.mark_as_completed()
        elif event_type == "payment_intent.payment_failed":
            self.mark_as_failed("Stripe payment failed")
    
    def _process_stars_webhook(self, data: dict):
        """Process Telegram Stars webhook"""
        # Implementation for Stars webhook processing
        status = data.get("status")
        if status == "paid":
            self.mark_as_completed()
        elif status == "failed":
            self.mark_as_failed("Stars payment failed")
    
    def _process_ton_webhook(self, data: dict):
        """Process TON webhook"""
        # Implementation for TON webhook processing
        if data.get("confirmed"):
            self.mark_as_completed()
        else:
            self.mark_as_failed("TON payment not confirmed")
    
    @property
    def is_pending(self):
        """Check if payment is pending"""
        return self.status == "pending"
    
    @property
    def is_completed(self):
        """Check if payment is completed"""
        return self.status == "completed" and self.is_successful 