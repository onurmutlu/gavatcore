#!/usr/bin/env python3
# core/db/crud.py - Async CRUD Operations

import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from core.db.connection import get_db_session
from core.db.models import EventLog, SaleLog, MessageRecord, UserSession

# ==================== EVENT LOGS ====================

async def log_event(user_identifier: str, event_type: str, message: str = "", 
                   context: Dict[str, Any] = None, level: str = "INFO", 
                   username: str = None) -> bool:
    """Async event log kaydet"""
    try:
        async for session in get_db_session():
            event = EventLog(
                user_id=str(user_identifier),
                username=username,
                event_type=event_type,
                message=message,
                context=context or {},
                level=level
            )
            session.add(event)
            await session.commit()
            return True
    except Exception as e:
        print(f"❌ Event log hatası: {e}")
        return False

async def get_events(user_identifier: str = None, event_type: str = None, 
                    level: str = None, limit: int = 100, 
                    hours_back: int = 24) -> List[EventLog]:
    """Event logları getir"""
    try:
        async for session in get_db_session():
            query = select(EventLog).order_by(desc(EventLog.timestamp))
            
            # Filtreler
            conditions = []
            if user_identifier:
                conditions.append(EventLog.user_id == str(user_identifier))
            if event_type:
                conditions.append(EventLog.event_type == event_type)
            if level:
                conditions.append(EventLog.level == level)
            if hours_back:
                since = datetime.utcnow() - timedelta(hours=hours_back)
                conditions.append(EventLog.timestamp >= since)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            query = query.limit(limit)
            result = await session.execute(query)
            return result.scalars().all()
    except Exception as e:
        print(f"❌ Event getirme hatası: {e}")
        return []

async def search_events(keyword: str, user_identifier: str = None, 
                       limit: int = 50, level: str = None,
                       after_date: datetime = None) -> List[EventLog]:
    """Event loglarında arama yap"""
    try:
        async for session in get_db_session():
            conditions = []
            
            # Keyword search
            if keyword:
                conditions.append(
                    or_(
                        EventLog.message.ilike(f"%{keyword}%"),
                        EventLog.event_type.ilike(f"%{keyword}%")
                    )
                )
            
            # User filter
            if user_identifier:
                conditions.append(EventLog.user_id == str(user_identifier))
            
            # Level filter
            if level:
                conditions.append(EventLog.level == level)
            
            # Date filter
            if after_date:
                conditions.append(EventLog.timestamp >= after_date)
            
            query = select(EventLog).order_by(desc(EventLog.timestamp))
            
            if conditions:
                query = query.where(and_(*conditions))
            
            query = query.limit(limit)
            result = await session.execute(query)
            return result.scalars().all()
    except Exception as e:
        print(f"❌ Event arama hatası: {e}")
        return []

# ==================== SALE LOGS ====================

async def log_sale(user_id: str, product_type: str, amount: float,
                  customer_id: str = None, bot_username: str = None,
                  product_name: str = None, currency: str = "TRY",
                  payment_method: str = None, payment_reference: str = None,
                  extra_data: Dict[str, Any] = None) -> bool:
    """Async satış log kaydet"""
    try:
        async for session in get_db_session():
            sale = SaleLog(
                user_id=str(user_id),
                customer_id=str(customer_id) if customer_id else None,
                bot_username=bot_username,
                product_type=product_type,
                product_name=product_name,
                amount=amount,
                currency=currency,
                payment_method=payment_method,
                payment_reference=payment_reference,
                extra_data=extra_data or {}
            )
            session.add(sale)
            await session.commit()
            return True
    except Exception as e:
        print(f"❌ Sale log hatası: {e}")
        return False

async def get_sales(user_id: str = None, days_back: int = 30,
                   payment_status: str = None) -> List[SaleLog]:
    """Satış logları getir"""
    try:
        async for session in get_db_session():
            query = select(SaleLog).order_by(desc(SaleLog.created_at))
            
            conditions = []
            if user_id:
                conditions.append(SaleLog.user_id == str(user_id))
            if payment_status:
                conditions.append(SaleLog.payment_status == payment_status)
            if days_back:
                since = datetime.utcnow() - timedelta(days=days_back)
                conditions.append(SaleLog.created_at >= since)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            result = await session.execute(query)
            return result.scalars().all()
    except Exception as e:
        print(f"❌ Sales getirme hatası: {e}")
        return []

async def update_sale_status(sale_id: int, status: str, 
                           notes: str = None) -> bool:
    """Satış durumunu güncelle"""
    try:
        async for session in get_db_session():
            query = select(SaleLog).where(SaleLog.id == sale_id)
            result = await session.execute(query)
            sale = result.scalar_one_or_none()
            
            if sale:
                sale.payment_status = status
                if notes:
                    sale.notes = notes
                sale.updated_at = datetime.utcnow()
                await session.commit()
                return True
            return False
    except Exception as e:
        print(f"❌ Sale güncelleme hatası: {e}")
        return False

# ==================== MESSAGE RECORDS ====================

async def log_message(bot_username: str, message_type: str, target_type: str,
                     target_id: str, message_content: str = None,
                     success: bool = True, error_message: str = None,
                     response_time_ms: int = None, target_name: str = None,
                     extra_data: Dict[str, Any] = None) -> bool:
    """Async mesaj log kaydet"""
    try:
        async for session in get_db_session():
            record = MessageRecord(
                bot_username=bot_username,
                message_type=message_type,
                target_type=target_type,
                target_id=str(target_id),
                target_name=target_name,
                message_content=message_content,
                success=success,
                error_message=error_message,
                response_time_ms=response_time_ms,
                extra_data=extra_data or {}
            )
            session.add(record)
            await session.commit()
            return True
    except Exception as e:
        print(f"❌ Message log hatası: {e}")
        return False

async def get_message_stats(bot_username: str = None, 
                           hours_back: int = 24) -> Dict[str, Any]:
    """Mesaj istatistikleri getir"""
    try:
        async for session in get_db_session():
            query = select(MessageRecord)
            
            if hours_back:
                since = datetime.utcnow() - timedelta(hours=hours_back)
                query = query.where(MessageRecord.timestamp >= since)
            
            if bot_username:
                query = query.where(MessageRecord.bot_username == bot_username)
            
            result = await session.execute(query)
            messages = result.scalars().all()
            
            stats = {
                "total_messages": len(messages),
                "successful": len([m for m in messages if m.success]),
                "failed": len([m for m in messages if not m.success]),
                "by_type": {},
                "by_target_type": {}
            }
            
            for msg in messages:
                # Tip bazında
                if msg.message_type not in stats["by_type"]:
                    stats["by_type"][msg.message_type] = 0
                stats["by_type"][msg.message_type] += 1
                
                # Hedef tip bazında
                if msg.target_type not in stats["by_target_type"]:
                    stats["by_target_type"][msg.target_type] = 0
                stats["by_target_type"][msg.target_type] += 1
            
            return stats
    except Exception as e:
        print(f"❌ Message stats hatası: {e}")
        return {}

# ==================== USER SESSIONS ====================

async def create_or_update_session(user_id: str, username: str = None,
                                  bot_type: str = None, 
                                  extra_data: Dict[str, Any] = None) -> bool:
    """Kullanıcı session oluştur veya güncelle"""
    try:
        async for session in get_db_session():
            # Mevcut session'ı bul
            query = select(UserSession).where(UserSession.user_id == str(user_id))
            result = await session.execute(query)
            user_session = result.scalar_one_or_none()
            
            if user_session:
                # Güncelle
                user_session.username = username or user_session.username
                user_session.bot_type = bot_type or user_session.bot_type
                user_session.is_active = True
                user_session.last_activity = datetime.utcnow()
                if extra_data:
                    user_session.extra_data = {**(user_session.extra_data or {}), **extra_data}
            else:
                # Yeni oluştur
                user_session = UserSession(
                    user_id=str(user_id),
                    username=username,
                    bot_type=bot_type,
                    extra_data=extra_data or {}
                )
                session.add(user_session)
            
            await session.commit()
            return True
    except Exception as e:
        print(f"❌ Session güncelleme hatası: {e}")
        return False

async def get_active_sessions(bot_type: str = None) -> List[UserSession]:
    """Aktif session'ları getir"""
    try:
        async for session in get_db_session():
            query = select(UserSession).where(UserSession.is_active == True)
            
            if bot_type:
                query = query.where(UserSession.bot_type == bot_type)
            
            result = await session.execute(query)
            return result.scalars().all()
    except Exception as e:
        print(f"❌ Active sessions hatası: {e}")
        return [] 