#!/usr/bin/env python3
"""
💳 GAVATCORE SaaS PAYMENT ROUTES
Stripe, Telegram Stars, and TON payment endpoints
"""

from fastapi import APIRouter, Request, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import structlog
import stripe
import json
from datetime import datetime, timedelta

from app.core.dependencies import get_db, get_current_user
from app.services.stripe_service import StripeService
from app.services.bot_launcher_service import BotLauncherService
from app.models.user import User
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.core.exceptions import PaymentError, ValidationError
from app.core.config import get_pricing, settings

logger = structlog.get_logger("gavatcore.payment")

router = APIRouter()

# Initialize services
stripe_service = StripeService()
bot_launcher = BotLauncherService()


# Request/Response Models
class CheckoutRequest(BaseModel):
    plan_name: str
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseModel):
    session_id: str
    session_url: str
    payment_id: int
    amount: float
    currency: str
    plan_name: str


class TrialResponse(BaseModel):
    trial: bool
    subscription_id: int
    expires_at: str
    plan_name: str


class PlanResponse(BaseModel):
    plan_name: str
    display_name: str
    price: float
    currency: str
    duration_days: int
    max_bots: int
    max_coins: int
    features: List[str]


class SubscriptionStatusResponse(BaseModel):
    is_active: bool
    plan_name: str
    expires_at: str
    days_remaining: int
    usage_percentage: float
    max_bots: int
    max_coins: int
    features: List[str]


# Available plans configuration
PRICING_PLANS = {
    "trial": {
        "display_name": "Deneme",
        "price": 0.0,
        "currency": "TRY",
        "duration_days": 1,
        "max_bots": 1,
        "max_coins": 100,
        "features": ["Basic GPT", "Manual mode"]
    },
    "starter": {
        "display_name": "Başlangıç",
        "price": 499.0,
        "currency": "TRY", 
        "duration_days": 30,
        "max_bots": 1,
        "max_coins": 500,
        "features": ["Advanced GPT", "Hybrid mode", "Basic support"]
    },
    "pro": {
        "display_name": "Pro",
        "price": 799.0,
        "currency": "TRY",
        "duration_days": 30,
        "max_bots": 3,
        "max_coins": 2000,
        "features": ["Premium GPT", "All modes", "Scheduler", "Priority support"]
    },
    "deluxe": {
        "display_name": "Deluxe",
        "price": 1499.0,
        "currency": "TRY",
        "duration_days": 30,
        "max_bots": 5,
        "max_coins": 9999,
        "features": ["Unlimited coins", "Custom personas", "Analytics", "24/7 support"]
    }
}


@router.get("/plans", response_model=List[PlanResponse])
async def get_pricing_plans():
    """Get available pricing plans"""
    plans = []
    for plan_name, plan_data in PRICING_PLANS.items():
        plans.append(PlanResponse(
            plan_name=plan_name,
            display_name=plan_data["display_name"],
            price=plan_data["price"],
            currency=plan_data["currency"],
            duration_days=plan_data["duration_days"],
            max_bots=plan_data["max_bots"],
            max_coins=plan_data["max_coins"],
            features=plan_data["features"]
        ))
    return plans


@router.post("/stripe/create-checkout")
async def create_stripe_checkout(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create Stripe checkout session"""
    try:
        if request.plan_name not in PRICING_PLANS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan name"
            )
        
        plan_data = PRICING_PLANS[request.plan_name]
        
        # Create checkout session
        checkout_data = await stripe_service.create_checkout_session(
            user=current_user,
            plan_name=request.plan_name,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            db=db
        )
        
        logger.info(f"Stripe checkout created for user {current_user.username}, plan: {request.plan_name}")  # type: ignore
        
        return {
            "success": True,
            "checkout_url": checkout_data.get("session_url"),
            "session_id": checkout_data.get("session_id"),
            "amount": checkout_data.get("amount"),
            "currency": checkout_data.get("currency")
        }
        
    except Exception as e:
        logger.error(f"Failed to create Stripe checkout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events"""
    try:
        body = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            body, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        logger.info(f"Received Stripe webhook: {event['type']}")
        
        if event["type"] == "payment_intent.succeeded":
            await handle_payment_success(event["data"]["object"], db)
        elif event["type"] == "payment_intent.payment_failed":
            await handle_payment_failure(event["data"]["object"], db)
        
        return {"success": True}
        
    except ValueError as e:
        logger.error(f"Invalid Stripe webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.SignatureVerificationError as e:  # type: ignore
        logger.error(f"Invalid Stripe webhook signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Stripe webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


async def handle_payment_success(payment_intent: Dict[str, Any], db: AsyncSession):
    """Handle successful payment"""
    try:
        payment_intent_id = payment_intent["id"]
        
        # Find payment record
        stmt = select(Payment).where(Payment.payment_intent_id == payment_intent_id)
        result = await db.execute(stmt)
        payment = result.scalar_one_or_none()
        
        if not payment:
            logger.error(f"Payment not found for payment_intent: {payment_intent_id}")
            return
        
        # Mark payment as completed
        payment.mark_as_completed()
        payment.process_webhook({"type": "payment_intent.succeeded", "data": payment_intent})
        
        # Get user
        stmt = select(User).where(User.id == payment.user_id)  # type: ignore
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            logger.error(f"User not found for payment: {payment.id}")
            return
        
        # Create subscription
        plan_data = PRICING_PLANS[payment.plan_name]  # type: ignore
        
        subscription = Subscription(
            user_id=user.id,  # type: ignore
            plan_name=payment.plan_name,  # type: ignore
            plan_price=payment.amount,  # type: ignore
            plan_currency=payment.currency,  # type: ignore
            expires_at=payment.created_at + timedelta(days=payment.plan_duration_days),  # type: ignore
            is_trial=(payment.plan_name == "trial"),  # type: ignore
            payment_method="stripe",
            max_bots=plan_data["max_bots"],
            max_coins=plan_data["max_coins"],
            features=json.dumps(plan_data["features"])
        )
        
        db.add(subscription)
        payment.subscription = subscription
        
        await db.commit()
        await db.refresh(subscription)
        
        logger.info(f"Subscription created for user {user.username}: {payment.plan_name}")  # type: ignore
        
        # 🚀 AUTOMATIC BOT CREATION AND LAUNCH!
        try:
            default_bot = await bot_launcher.create_default_bot_for_subscription(
                user=user,
                subscription=subscription,
                db=db
            )
            
            logger.info(f"🤖 Auto-launched bot {default_bot.bot_name} for user {user.username}")  # type: ignore
            
        except Exception as bot_error:
            logger.error(f"Failed to auto-create bot for user {user.username}: {bot_error}")  # type: ignore
            # Don't fail the payment if bot creation fails
        
    except Exception as e:
        logger.error(f"Failed to handle payment success: {e}")


async def handle_payment_failure(payment_intent: Dict[str, Any], db: AsyncSession):
    """Handle failed payment"""
    try:
        payment_intent_id = payment_intent["id"]
        
        # Find payment record
        stmt = select(Payment).where(Payment.payment_intent_id == payment_intent_id)
        result = await db.execute(stmt)
        payment = result.scalar_one_or_none()
        
        if not payment:
            logger.error(f"Payment not found for payment_intent: {payment_intent_id}")
            return
        
        # Mark payment as failed
        failure_reason = payment_intent.get("last_payment_error", {}).get("message", "Payment failed")
        payment.mark_as_failed(failure_reason)
        payment.process_webhook({"type": "payment_intent.payment_failed", "data": payment_intent})
        
        await db.commit()
        
        logger.info(f"Payment failed for user {payment.user_id}: {failure_reason}")
        
    except Exception as e:
        logger.error(f"Failed to handle payment failure: {e}")


@router.get("/subscription/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's subscription status"""
    try:
        # Get active subscription
        stmt = select(Subscription).where(
            Subscription.user_id == current_user.id,  # type: ignore
            Subscription.is_active == True  # type: ignore
        )
        result = await db.execute(stmt)
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            return SubscriptionStatusResponse(
                is_active=False,
                plan_name="none",
                expires_at="",
                days_remaining=0,
                usage_percentage=0,
                max_bots=0,
                max_coins=0,
                features=[]
            )
        
        return SubscriptionStatusResponse(
            is_active=not subscription.is_expired,
            plan_name=subscription.plan_name,  # type: ignore
            expires_at=subscription.expires_at.isoformat(),  # type: ignore
            days_remaining=subscription.days_remaining,
            usage_percentage=subscription.usage_percentage,
            max_bots=subscription.max_bots,  # type: ignore
            max_coins=subscription.max_coins,  # type: ignore
            features=subscription.get_features_list()
        )
        
    except Exception as e:
        logger.error(f"Failed to get subscription status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription status"
        )


@router.get("/history")
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's payment history"""
    try:
        stmt = select(Payment).where(Payment.user_id == current_user.id).order_by(Payment.created_at.desc())  # type: ignore
        result = await db.execute(stmt)
        payments = result.scalars().all()
        
        return {
            "success": True,
            "payments": [
                {
                    "id": payment.id,  # type: ignore
                    "amount": float(payment.amount),  # type: ignore
                    "currency": payment.currency,  # type: ignore
                    "plan_name": payment.plan_name,  # type: ignore
                    "status": payment.status,  # type: ignore
                    "payment_method": payment.payment_method,  # type: ignore
                    "created_at": payment.created_at.isoformat() if payment.created_at else "",  # type: ignore
                    "completed_at": payment.completed_at.isoformat() if payment.completed_at else None,  # type: ignore
                }
                for payment in payments
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get payment history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment history"
        )


@router.post("/stars/invoice")
async def create_stars_invoice():
    """Create Telegram Stars invoice"""
    return {
        "success": True,
        "message": "Stars invoice - TODO: implement",
        "status": "coming_soon"
    }


@router.post("/ton/invoice") 
async def create_ton_invoice():
    """Create TON payment invoice"""
    return {
        "success": True,
        "message": "TON invoice - TODO: implement", 
        "status": "coming_soon"
    } 