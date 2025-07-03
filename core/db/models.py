#!/usr/bin/env python3
# core/db/models.py - SQLAlchemy Models

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON
from sqlalchemy.sql import func
from core.db.connection import Base

class EventLog(Base):
    """Event log tablosu - tüm sistem olayları"""
    __tablename__ = "event_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True, nullable=False)
    username = Column(String(100), index=True)
    event_type = Column(String(50), index=True, nullable=False)  # dm_received, spam_sent, gpt_reply, etc.
    message = Column(Text)
    context = Column(JSON)  # Ek bilgiler (grup_id, mesaj_id, etc.)
    level = Column(String(20), default="INFO")  # INFO, WARNING, ERROR
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<EventLog(user_id={self.user_id}, type={self.event_type}, timestamp={self.timestamp})>"

class SaleLog(Base):
    """Satış log tablosu - VIP, show, ödeme takibi"""
    __tablename__ = "sale_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True, nullable=False)
    customer_id = Column(String(100), index=True)
    bot_username = Column(String(100), index=True)
    product_type = Column(String(50), nullable=False)  # vip_membership, private_show, custom_content
    product_name = Column(String(200))
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="TRY")
    payment_method = Column(String(50))  # papara, iban, crypto
    payment_status = Column(String(20), default="pending")  # pending, completed, failed, refunded
    payment_reference = Column(String(200))  # Papara ID, IBAN referansı
    notes = Column(Text)
    extra_data = Column(JSON)  # Ek bilgiler
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SaleLog(user_id={self.user_id}, product={self.product_type}, amount={self.amount})>"

class MessageRecord(Base):
    """Mesaj kayıt tablosu - spam, DM, grup mesajları"""
    __tablename__ = "message_records"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_username = Column(String(100), index=True, nullable=False)
    message_type = Column(String(20), index=True, nullable=False)  # spam, dm, group_reply, mention
    target_type = Column(String(20), index=True)  # group, user
    target_id = Column(String(100), index=True)  # grup_id veya user_id
    target_name = Column(String(200))
    message_content = Column(Text)
    message_id = Column(String(100))  # Telegram message ID
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    response_time_ms = Column(Integer)
    extra_data = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<MessageRecord(bot={self.bot_username}, type={self.message_type}, target={self.target_id})>"

class UserSession(Base):
    """Kullanıcı session tablosu - aktif oturumlar"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True, nullable=False, unique=True)
    username = Column(String(100), index=True)
    session_token = Column(String(200), unique=True)
    bot_type = Column(String(50))  # producer, admin, client
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    extra_data = Column(JSON)
    
    def __repr__(self):
        return f"<UserSession(user_id={self.user_id}, active={self.is_active})>"

class Profile(Base):
    """Bot profil modeli"""
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    profile_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Profile {self.username}>" 