#!/usr/bin/env python3
"""
💳 STRIPE PAYMENT SERVICE
Stripe checkout sessions and webhook handling
"""

import stripe
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings, get_subscription_limits, get_pricing
from app.core.exceptions import PaymentError, ValidationError
from app.models.user import User
from app.models.payment import Payment
from app.models.subscription import Subscription
import structlog

logger = structlog.get_logger("gavatcore.stripe")

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Stripe payment processing service"""
    
    def __init__(self):
        self.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        self.pricing = get_pricing()
    
    async def create_checkout_session(
        self,
        user: User,
        plan_name: str,
        success_url: str,
        cancel_url: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Create Stripe checkout session"""
        
        # Validate plan
        if plan_name not in self.pricing:
            raise ValidationError(f"Invalid plan: {plan_name}")
        
        plan_data = self.pricing[plan_name]
        
        # Skip payment for trial plan
        if plan_name == "trial":
            return await self._create_trial_subscription(user, db)
        
        try:
            # Create payment record
            payment = Payment(
                user_id=user.id,  # type: ignore
                payment_intent_id=f"pending_{user.id}_{int(datetime.utcnow().timestamp())}",  # type: ignore
                amount=plan_data["price"],
                currency=plan_data["currency"],
                payment_method="stripe",
                plan_name=plan_name,
                plan_duration_days=30,
                status="pending"
            )
            
            db.add(payment)
            await db.commit()
            await db.refresh(payment)
            
            # Create Stripe checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': plan_data["currency"].lower(),
                        'product_data': {
                            'name': f'GavatCore {plan_data["name"]} Plan',
                            'description': f'30 günlük {plan_data["name"]} aboneliği',
                        },
                        'unit_amount': int(plan_data["price"] * 100),  # Stripe expects cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=str(user.id),  # type: ignore
                metadata={
                    'user_id': str(user.id),  # type: ignore
                    'plan_name': plan_name,
                    'payment_id': str(payment.id)  # type: ignore
                }
            )
            
            # Update payment with Stripe session ID
            payment.external_payment_id = session.id  # type: ignore
            payment.stripe_data = json.dumps({  # type: ignore
                'session_id': session.id,
                'session_url': session.url
            })
            await db.commit()
            
            logger.info(f"Stripe checkout session created: {session.id} for user {user.username}")
            
            return {
                'session_id': session.id,
                'session_url': session.url,
                'payment_id': payment.id,  # type: ignore
                'amount': plan_data["price"],
                'currency': plan_data["currency"],
                'plan_name': plan_name
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            raise PaymentError(f"Payment processing failed: {e}")
        except Exception as e:
            logger.error(f"Checkout session creation failed: {e}")
            raise PaymentError("Failed to create payment session")
    
    async def _create_trial_subscription(self, user: User, db: AsyncSession) -> Dict[str, Any]:
        """Create trial subscription without payment"""
        try:
            # Check if user already had a trial
            stmt = select(Subscription).where(
                Subscription.user_id == user.id,  # type: ignore
                Subscription.is_trial == True  # type: ignore
            )
            result = await db.execute(stmt)
            existing_trial = result.scalar_one_or_none()
            
            if existing_trial:
                raise ValidationError("User already used trial period")
            
            # Create trial subscription
            limits = get_subscription_limits("trial")
            subscription = Subscription(
                user_id=user.id,  # type: ignore
                plan_name="trial",
                plan_price=0,
                plan_currency="TRY",
                started_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=limits["duration_days"]),
                is_active=True,
                is_trial=True,
                payment_method="trial",
                max_bots=limits["max_bots"],
                max_coins=limits["coins"],
                features=json.dumps(limits["features"])
            )
            
            db.add(subscription)
            await db.commit()
            await db.refresh(subscription)
            
            logger.info(f"Trial subscription created for user {user.username}")
            
            return {
                'trial': True,
                'subscription_id': subscription.id,  # type: ignore
                'expires_at': subscription.expires_at.isoformat(),
                'plan_name': 'trial'
            }
            
        except Exception as e:
            logger.error(f"Trial subscription creation failed: {e}")
            raise PaymentError("Failed to create trial subscription")
    
    async def handle_webhook(
        self,
        payload: bytes,
        signature: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Handle Stripe webhook"""
        
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            logger.info(f"Stripe webhook received: {event['type']}")
            
            # Handle different event types
            if event['type'] == 'checkout.session.completed':
                return await self._handle_checkout_completed(event['data']['object'], db)
            elif event['type'] == 'payment_intent.succeeded':
                return await self._handle_payment_succeeded(event['data']['object'], db)
            elif event['type'] == 'payment_intent.payment_failed':
                return await self._handle_payment_failed(event['data']['object'], db)
            else:
                logger.info(f"Unhandled webhook event: {event['type']}")
                return {'status': 'ignored', 'event_type': event['type']}
            
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            raise PaymentError("Invalid webhook signature")
        except Exception as e:
            logger.error(f"Webhook handling failed: {e}")
            raise PaymentError("Webhook processing failed")
    
    async def _handle_checkout_completed(
        self,
        session_data: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Handle successful checkout session"""
        
        try:
            user_id = int(session_data['metadata']['user_id'])
            plan_name = session_data['metadata']['plan_name']
            payment_id = int(session_data['metadata']['payment_id'])
            
            # Get payment record
            stmt = select(Payment).where(Payment.id == payment_id)
            result = await db.execute(stmt)
            payment = result.scalar_one_or_none()
            
            if not payment:
                raise PaymentError(f"Payment not found: {payment_id}")
            
            # Mark payment as completed
            payment.mark_as_completed()
            payment.external_payment_id = session_data['payment_intent']  # type: ignore
            payment.stripe_data = json.dumps(session_data)  # type: ignore
            
            # Create subscription
            await self._create_subscription(user_id, plan_name, payment, db)
            
            await db.commit()
            
            logger.info(f"Payment completed: {payment_id} for user {user_id}")
            
            return {
                'status': 'completed',
                'payment_id': payment_id,
                'user_id': user_id,
                'plan_name': plan_name
            }
            
        except Exception as e:
            logger.error(f"Checkout completion handling failed: {e}")
            raise PaymentError("Failed to process completed payment")
    
    async def _handle_payment_succeeded(
        self,
        payment_intent: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Handle successful payment intent"""
        logger.info(f"Payment intent succeeded: {payment_intent['id']}")
        return {'status': 'success', 'payment_intent_id': payment_intent['id']}
    
    async def _handle_payment_failed(
        self,
        payment_intent: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Handle failed payment intent"""
        logger.error(f"Payment intent failed: {payment_intent['id']}")
        return {'status': 'failed', 'payment_intent_id': payment_intent['id']}
    
    async def _create_subscription(
        self,
        user_id: int,
        plan_name: str,
        payment: Payment,
        db: AsyncSession
    ) -> Subscription:
        """Create subscription after successful payment"""
        
        limits = get_subscription_limits(plan_name)
        
        # Deactivate existing subscriptions
        stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.is_active == True  # type: ignore
        )
        result = await db.execute(stmt)
        existing_subs = result.scalars().all()
        
        for sub in existing_subs:
            sub.is_active = False  # type: ignore
            sub.cancelled_at = datetime.utcnow()  # type: ignore
            sub.cancellation_reason = f"Upgraded to {plan_name}"  # type: ignore
        
        # Create new subscription
        subscription = Subscription(
            user_id=user_id,
            plan_name=plan_name,
            plan_price=payment.amount,
            plan_currency=payment.currency,
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=limits["duration_days"]),
            is_active=True,
            is_trial=False,
            payment_method="stripe",
            external_subscription_id=payment.external_payment_id,
            max_bots=limits["max_bots"],
            max_coins=limits["coins"],
            features=json.dumps(limits["features"])
        )
        
        # Link payment to subscription
        payment.subscription_id = subscription.id  # type: ignore
        
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)
        
        logger.info(f"Subscription created: {plan_name} for user {user_id}")
        
        return subscription 