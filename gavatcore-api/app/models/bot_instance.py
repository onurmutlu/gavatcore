#!/usr/bin/env python3
"""
🤖 BOT INSTANCE MODEL
Database model for user bot instances
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional
from app.database.connection import Base


class BotInstance(Base):
    """Bot instance model"""
    __tablename__ = "bot_instances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Bot identification
    bot_name = Column(String(50), nullable=False)  # User-defined name
    bot_username = Column(String(50), nullable=True)  # Telegram username
    telegram_user_id = Column(BigInteger, nullable=True)  # Bot's Telegram user ID
    
    # Bot configuration
    bot_type = Column(String(20), default="persona")  # persona, business, custom
    personality = Column(String(50), nullable=True)   # gawatbaba, yayincilara, xxxgeisha
    reply_mode = Column(String(20), default="manual") # manual, gpt, hybrid, manualplus
    
    # Phone and session
    phone_number = Column(String(20), nullable=True)
    session_file_path = Column(String(255), nullable=True)
    session_status = Column(String(20), default="pending")  # pending, active, inactive, error
    
    # Status
    is_active = Column(Boolean, default=False)
    is_online = Column(Boolean, default=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    
    # Configuration JSON
    config = Column(Text, nullable=True)              # JSON configuration
    triggers = Column(Text, nullable=True)            # JSON trigger words
    responses = Column(Text, nullable=True)           # JSON custom responses
    
    # Usage statistics
    messages_sent = Column(Integer, default=0)
    messages_received = Column(Integer, default=0)
    coins_used = Column(Integer, default=0)
    
    # Scheduling
    scheduler_enabled = Column(Boolean, default=False)
    scheduler_interval = Column(Integer, default=300)  # seconds
    last_scheduled_message = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    stopped_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error tracking
    last_error = Column(Text, nullable=True)
    error_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="bot_instances")

    def __repr__(self):
        return f"<BotInstance {self.bot_name} ({self.personality})>"
    
    @property
    def uptime_seconds(self):
        """Get uptime in seconds"""
        if self.started_at:  # type: ignore
            end_time = self.stopped_at or datetime.utcnow()
            return (end_time - self.started_at).total_seconds()
        return 0
    
    @property
    def is_running(self):
        """Check if bot is currently running"""
        return self.is_active and self.session_status == "active"
    
    def start_bot(self):
        """Start the bot instance"""
        self.is_active = True
        self.started_at = datetime.utcnow()
        self.stopped_at = None
        self.session_status = "active"
    
    def stop_bot(self, reason: Optional[str] = None):
        """Stop the bot instance"""
        self.is_active = False
        self.is_online = False
        self.stopped_at = datetime.utcnow()
        self.session_status = "inactive"
        if reason:
            self.last_error = reason
    
    def log_error(self, error_message: str):
        """Log an error"""
        self.last_error = error_message
        self.error_count += 1
        self.session_status = "error"
    
    def increment_usage(self, messages_sent: int = 0, messages_received: int = 0, coins_used: int = 0):
        """Increment usage statistics"""
        self.messages_sent += messages_sent
        self.messages_received += messages_received  
        self.coins_used += coins_used
        self.last_seen_at = datetime.utcnow()
    
    def get_config_dict(self):
        """Get configuration as dictionary"""
        if self.config:  # type: ignore
            import json
            try:
                return json.loads(self.config)  # type: ignore
            except:
                return {}
        return {}
    
    def update_config(self, config_dict: dict):
        """Update configuration"""
        import json
        self.config = json.dumps(config_dict) 