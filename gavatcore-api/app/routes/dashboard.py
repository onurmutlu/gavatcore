from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
📊 GAVATCORE SaaS DASHBOARD ROUTES
Comprehensive management dashboard endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import os
import structlog
from pathlib import Path

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.bot_instance import BotInstance
from app.models.subscription import Subscription
from app.models.payment import Payment

logger = structlog.get_logger("gavatcore.dashboard")

router = APIRouter()

# Response Models
class PerformerStatsResponse(BaseModel):
    performer_name: str
    status: str
    total_messages: int
    messages_today: int
    response_time_avg: float
    online_time_hours: float
    earnings_today: float
    earnings_month: float
    engagement_rate: float
    last_active: str

class SystemOverviewResponse(BaseModel):
    total_users: int
    active_bots: int
    total_bots: int
    total_messages_today: int
    total_revenue_today: float
    total_revenue_month: float
    active_subscriptions: int
    system_uptime: float
    server_status: str

class AnalyticsResponse(BaseModel):
    date: str
    total_messages: int
    unique_users: int
    revenue: float
    new_subscriptions: int
    bot_uptime: float

class LicenseStatusResponse(BaseModel):
    user_id: int
    username: str
    plan_name: str
    status: str
    expires_at: str
    days_remaining: int
    auto_renewal: bool
    last_payment: Optional[str]
    next_payment: Optional[str]

class PaymentSummaryResponse(BaseModel):
    total_revenue: float
    monthly_revenue: float
    weekly_revenue: float
    daily_revenue: float
    total_transactions: int
    successful_payments: int
    failed_payments: int
    refunds: int


@router.get("/overview", response_model=SystemOverviewResponse)
async def get_system_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive system overview"""
    try:
        # Total users
        total_users_stmt = select(func.count(User.id))
        total_users_result = await db.execute(total_users_stmt)
        total_users = total_users_result.scalar() or 0

        # Bot statistics
        active_bots_stmt = select(func.count(BotInstance.id)).where(BotInstance.is_active == True)
        active_bots_result = await db.execute(active_bots_stmt)
        active_bots = active_bots_result.scalar() or 0

        total_bots_stmt = select(func.count(BotInstance.id))
        total_bots_result = await db.execute(total_bots_stmt)
        total_bots = total_bots_result.scalar() or 0

        # Active subscriptions
        active_subs_stmt = select(func.count(Subscription.id)).where(
            and_(
                Subscription.status == "active",
                Subscription.expires_at > datetime.now()
            )
        )
        active_subs_result = await db.execute(active_subs_stmt)
        active_subscriptions = active_subs_result.scalar() or 0

        # Revenue calculations
        today = datetime.now().date()
        month_start = datetime.now().replace(day=1).date()

        daily_revenue_stmt = select(func.sum(Payment.amount)).where(
            and_(
                Payment.status == "completed",
                func.date(Payment.created_at) == today
            )
        )
        daily_revenue_result = await db.execute(daily_revenue_stmt)
        daily_revenue = float(daily_revenue_result.scalar() or 0.0)

        monthly_revenue_stmt = select(func.sum(Payment.amount)).where(
            and_(
                Payment.status == "completed",
                func.date(Payment.created_at) >= month_start
            )
        )
        monthly_revenue_result = await db.execute(monthly_revenue_stmt)
        monthly_revenue = float(monthly_revenue_result.scalar() or 0.0)

        # Get analytics data for today's messages
        analytics_data = await get_analytics_data(str(today))
        total_messages_today = analytics_data.get("total_messages", 0)

        return SystemOverviewResponse(
            total_users=total_users,
            active_bots=active_bots,
            total_bots=total_bots,
            total_messages_today=total_messages_today,
            total_revenue_today=daily_revenue,
            total_revenue_month=monthly_revenue,
            active_subscriptions=active_subscriptions,
            system_uptime=99.9,  # Mock data
            server_status="healthy"
        )

    except Exception as e:
        logger.error(f"Failed to get system overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system overview"
        )


@router.get("/performers", response_model=List[PerformerStatsResponse])
async def get_performer_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed performer statistics"""
    try:
        # Get performer data from personas and profiles
        performers = []
        
        # Get data from analytics for recent activity
        today = datetime.now().date()
        analytics_data = await get_analytics_data(str(today))
        
        # Mock performer data based on our 3-bot system
        performers_data = [
            {
                "performer_name": "Yayıncı Lara",
                "username": "yayincilara",
                "phone": "+905382617727",
                "status": "active"
            },
            {
                "performer_name": "XXX Geisha",
                "username": "xxxgeisha", 
                "phone": "+905486306226",
                "status": "active"
            },
            {
                "performer_name": "Gavat Baba",
                "username": "babagavat",
                "phone": "+905513272355",
                "status": "banned"
            }
        ]

        for performer in performers_data:
            # Get analytics for this performer
            performer_analytics = await get_performer_analytics(performer["username"])
            
            performers.append(PerformerStatsResponse(
                performer_name=performer["performer_name"],
                status=performer["status"],
                total_messages=performer_analytics.get("total_messages", 0),
                messages_today=performer_analytics.get("messages_today", 0),
                response_time_avg=performer_analytics.get("response_time", 2.1),
                online_time_hours=performer_analytics.get("online_hours", 8.5),
                earnings_today=performer_analytics.get("earnings_today", 0.0),
                earnings_month=performer_analytics.get("earnings_month", 0.0),
                engagement_rate=performer_analytics.get("engagement_rate", 85.2),
                last_active=performer_analytics.get("last_active", datetime.now().isoformat())
            ))

        return performers

    except Exception as e:
        logger.error(f"Failed to get performer stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve performer statistics"
        )


@router.get("/analytics", response_model=List[AnalyticsResponse])
async def get_analytics(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics data for specified days"""
    try:
        analytics = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).date()
            date_str = str(date)
            
            # Get daily analytics
            daily_data = await get_analytics_data(date_str)
            
            # Get revenue for this date
            revenue_stmt = select(func.sum(Payment.amount)).where(
                and_(
                    Payment.status == "completed",
                    func.date(Payment.created_at) == date
                )
            )
            revenue_result = await db.execute(revenue_stmt)
            daily_revenue = float(revenue_result.scalar() or 0.0)

            # Get new subscriptions for this date
            new_subs_stmt = select(func.count(Subscription.id)).where(
                func.date(Subscription.created_at) == date
            )
            new_subs_result = await db.execute(new_subs_stmt)
            new_subscriptions = new_subs_result.scalar() or 0

            analytics.append(AnalyticsResponse(
                date=date_str,
                total_messages=daily_data.get("total_messages", 0),
                unique_users=daily_data.get("unique_users", 0),
                revenue=daily_revenue,
                new_subscriptions=new_subscriptions,
                bot_uptime=daily_data.get("bot_uptime", 99.0)
            ))

        return sorted(analytics, key=lambda x: x.date)

    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )


@router.get("/licenses", response_model=List[LicenseStatusResponse])
async def get_license_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive license status for all users"""
    try:
        # Get all active subscriptions with user info
        stmt = select(Subscription, User).join(User).where(
            Subscription.status == "active"
        )
        result = await db.execute(stmt)
        subscriptions = result.all()

        licenses = []
        for subscription, user in subscriptions:
            # Calculate days remaining
            days_remaining = (subscription.expires_at - datetime.now()).days if subscription.expires_at else 0
            
            # Get last payment
            last_payment_stmt = select(Payment).where(
                and_(
                    Payment.user_id == user.id,
                    Payment.status == "completed"
                )
            ).order_by(Payment.created_at.desc()).limit(1)
            last_payment_result = await db.execute(last_payment_stmt)
            last_payment = last_payment_result.scalar_one_or_none()

            licenses.append(LicenseStatusResponse(
                user_id=user.id,
                username=user.username,
                plan_name=subscription.plan_name,
                status=subscription.status,
                expires_at=subscription.expires_at.isoformat() if subscription.expires_at else "",
                days_remaining=max(0, days_remaining),
                auto_renewal=subscription.auto_renewal or False,
                last_payment=last_payment.created_at.isoformat() if last_payment else None,
                next_payment=subscription.expires_at.isoformat() if subscription.expires_at else None
            ))

        return licenses

    except Exception as e:
        logger.error(f"Failed to get license status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve license status"
        )


@router.get("/payments/summary", response_model=PaymentSummaryResponse)
async def get_payment_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payment summary and statistics"""
    try:
        # Total revenue
        total_revenue_stmt = select(func.sum(Payment.amount)).where(
            Payment.status == "completed"
        )
        total_revenue_result = await db.execute(total_revenue_stmt)
        total_revenue = float(total_revenue_result.scalar() or 0.0)

        # Monthly revenue
        month_start = datetime.now().replace(day=1).date()
        monthly_revenue_stmt = select(func.sum(Payment.amount)).where(
            and_(
                Payment.status == "completed",
                func.date(Payment.created_at) >= month_start
            )
        )
        monthly_revenue_result = await db.execute(monthly_revenue_stmt)
        monthly_revenue = float(monthly_revenue_result.scalar() or 0.0)

        # Weekly revenue
        week_start = datetime.now().date() - timedelta(days=7)
        weekly_revenue_stmt = select(func.sum(Payment.amount)).where(
            and_(
                Payment.status == "completed",
                func.date(Payment.created_at) >= week_start
            )
        )
        weekly_revenue_result = await db.execute(weekly_revenue_stmt)
        weekly_revenue = float(weekly_revenue_result.scalar() or 0.0)

        # Daily revenue
        today = datetime.now().date()
        daily_revenue_stmt = select(func.sum(Payment.amount)).where(
            and_(
                Payment.status == "completed",
                func.date(Payment.created_at) == today
            )
        )
        daily_revenue_result = await db.execute(daily_revenue_stmt)
        daily_revenue = float(daily_revenue_result.scalar() or 0.0)

        # Payment statistics
        total_payments_stmt = select(func.count(Payment.id))
        total_payments_result = await db.execute(total_payments_stmt)
        total_transactions = total_payments_result.scalar() or 0

        successful_payments_stmt = select(func.count(Payment.id)).where(
            Payment.status == "completed"
        )
        successful_payments_result = await db.execute(successful_payments_stmt)
        successful_payments = successful_payments_result.scalar() or 0

        failed_payments_stmt = select(func.count(Payment.id)).where(
            Payment.status == "failed"
        )
        failed_payments_result = await db.execute(failed_payments_stmt)
        failed_payments = failed_payments_result.scalar() or 0

        refunds_stmt = select(func.count(Payment.id)).where(
            Payment.status == "refunded"
        )
        refunds_result = await db.execute(refunds_stmt)
        refunds = refunds_result.scalar() or 0

        return PaymentSummaryResponse(
            total_revenue=total_revenue,
            monthly_revenue=monthly_revenue,
            weekly_revenue=weekly_revenue,
            daily_revenue=daily_revenue,
            total_transactions=total_transactions,
            successful_payments=successful_payments,
            failed_payments=failed_payments,
            refunds=refunds
        )

    except Exception as e:
        logger.error(f"Failed to get payment summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment summary"
        )


# Helper functions
async def get_analytics_data(date_str: str) -> Dict[str, Any]:
    """Get analytics data from JSON files"""
    try:
        analytics_file = Path(f"data/analytics/{date_str}.json")
        if analytics_file.exists():
            with open(analytics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Process the data
            total_messages = len([item for item in data if 'message_received' in item.get('action', '')])
            unique_users = len(set(item.get('user', '') for item in data))
            
            return {
                "total_messages": total_messages,
                "unique_users": unique_users,
                "bot_uptime": 98.5  # Mock data
            }
    except Exception as e:
        logger.error(f"Failed to read analytics data for {date_str}: {e}")
    
    return {"total_messages": 0, "unique_users": 0, "bot_uptime": 0.0}


async def get_performer_analytics(username: str) -> Dict[str, Any]:
    """Get analytics for specific performer"""
    try:
        # Get today's analytics
        today = datetime.now().date()
        analytics_file = Path(f"data/analytics/{today}.json")
        
        if analytics_file.exists():
            with open(analytics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Filter data for this performer
            performer_data = [item for item in data if item.get('user') == username]
            
            messages_today = len([item for item in performer_data if 'message_received' in item.get('action', '')])
            replies_sent = len([item for item in performer_data if 'reply_sent' in item.get('action', '')])
            
            # Calculate engagement rate
            engagement_rate = (replies_sent / messages_today * 100) if messages_today > 0 else 0
            
            return {
                "total_messages": messages_today * 30,  # Mock monthly data
                "messages_today": messages_today,
                "response_time": 2.1,  # Mock data
                "online_hours": 8.5,  # Mock data
                "earnings_today": messages_today * 0.50,  # Mock earnings
                "earnings_month": messages_today * 30 * 0.50,  # Mock monthly earnings
                "engagement_rate": engagement_rate,
                "last_active": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Failed to get performer analytics for {username}: {e}")
    
    return {
        "total_messages": 0,
        "messages_today": 0,
        "response_time": 0.0,
        "online_hours": 0.0,
        "earnings_today": 0.0,
        "earnings_month": 0.0,
        "engagement_rate": 0.0,
        "last_active": datetime.now().isoformat()
    }


@router.get("/realtime/stats")
async def get_realtime_stats(
    current_user: User = Depends(get_current_user)
):
    """Get real-time system statistics"""
    try:
        # Mock real-time data - in production this would connect to Redis/WebSocket
        return {
            "active_users": 45,
            "messages_per_minute": 12,
            "cpu_usage": 35.2,
            "memory_usage": 68.1,
            "disk_usage": 42.3,
            "network_io": {"in": 1.2, "out": 0.8},
            "active_sessions": 23,
            "error_rate": 0.02,
            "response_time": 1.8,
            "uptime": "15d 4h 32m"
        }
    except Exception as e:
        logger.error(f"Failed to get real-time stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve real-time statistics"
        ) 