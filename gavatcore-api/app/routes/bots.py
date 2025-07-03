#!/usr/bin/env python3
"""
🤖 GAVATCORE SaaS BOT ROUTES
Bot instance management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
import structlog

from app.core.dependencies import get_db, get_current_user
from app.services.bot_launcher_service import BotLauncherService
from app.models.user import User
from app.models.bot_instance import BotInstance
from app.models.subscription import Subscription
from app.core.exceptions import BotInstanceError, ValidationError

logger = structlog.get_logger("gavatcore.bots")

router = APIRouter()

# Initialize bot launcher service
bot_launcher = BotLauncherService()


# Request/Response Models
class CreateBotRequest(BaseModel):
    personality: str
    phone_number: Optional[str] = None
    custom_name: Optional[str] = None


class BotInstanceResponse(BaseModel):
    id: int
    bot_name: str
    personality: str
    reply_mode: str
    session_status: str
    is_active: bool
    is_online: bool
    messages_sent: int
    messages_received: int
    coins_used: int
    created_at: str
    uptime_seconds: float
    
    class Config:
        from_attributes = True


class BotStatusResponse(BaseModel):
    bot_name: str
    personality: str
    status: str
    is_active: bool
    is_online: bool
    uptime_seconds: float
    messages_sent: int
    messages_received: int
    coins_used: int
    last_seen: Optional[str]
    error_count: int
    last_error: Optional[str]


@router.get("/", response_model=List[BotInstanceResponse])
async def get_user_bots(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's bot instances"""
    try:
        stmt = select(BotInstance).where(BotInstance.user_id == current_user.id)  # type: ignore
        result = await db.execute(stmt)
        bots = result.scalars().all()
        
        return [
            BotInstanceResponse(
                id=bot.id,  # type: ignore
                bot_name=bot.bot_name,  # type: ignore
                personality=bot.personality or "unknown",  # type: ignore
                reply_mode=bot.reply_mode or "manual",  # type: ignore
                session_status=bot.session_status or "pending",  # type: ignore
                is_active=bool(bot.is_active),  # type: ignore
                is_online=bool(bot.is_online),  # type: ignore
                messages_sent=bot.messages_sent or 0,  # type: ignore
                messages_received=bot.messages_received or 0,  # type: ignore
                coins_used=bot.coins_used or 0,  # type: ignore
                created_at=bot.created_at.isoformat() if bot.created_at else "",  # type: ignore
                uptime_seconds=bot.uptime_seconds,
            )
            for bot in bots
        ]
        
    except Exception as e:
        logger.error(f"Failed to get user bots: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve bots"
        )


@router.post("/create", response_model=BotInstanceResponse)
async def create_bot_instance(
    request: CreateBotRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new bot instance"""
    try:
        # Get user's active subscription
        stmt = select(Subscription).where(
            Subscription.user_id == current_user.id,  # type: ignore
            Subscription.is_active == True  # type: ignore
        )
        result = await db.execute(stmt)
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No active subscription found"
            )
        
        # Create bot instance
        bot_instance = await bot_launcher.create_bot_instance(
            user=current_user,
            subscription=subscription,
            personality=request.personality,
            phone_number=request.phone_number,
            db=db
        )
        
        return BotInstanceResponse(
            id=bot_instance.id,  # type: ignore
            bot_name=bot_instance.bot_name,  # type: ignore
            personality=bot_instance.personality or "",  # type: ignore
            reply_mode=bot_instance.reply_mode or "manual",  # type: ignore
            session_status=bot_instance.session_status or "creating",  # type: ignore
            is_active=bool(bot_instance.is_active),  # type: ignore
            is_online=bool(bot_instance.is_online),  # type: ignore
            messages_sent=bot_instance.messages_sent or 0,  # type: ignore
            messages_received=bot_instance.messages_received or 0,  # type: ignore
            coins_used=bot_instance.coins_used or 0,  # type: ignore
            created_at=bot_instance.created_at.isoformat() if bot_instance.created_at else "",  # type: ignore
            uptime_seconds=bot_instance.uptime_seconds,
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except BotInstanceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Failed to create bot instance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bot creation failed"
        )


@router.get("/{bot_id}", response_model=BotStatusResponse)
async def get_bot_details(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get bot instance details"""
    try:
        # Get bot instance
        stmt = select(BotInstance).where(
            BotInstance.id == bot_id,
            BotInstance.user_id == current_user.id  # type: ignore
        )
        result = await db.execute(stmt)
        bot_instance = result.scalar_one_or_none()
        
        if not bot_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bot instance not found"
            )
        
        # Get detailed status
        status_data = await bot_launcher.get_bot_status(bot_instance)
        
        return BotStatusResponse(**status_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get bot details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve bot details"
        )


@router.put("/{bot_id}/config")
async def update_bot_config(
    bot_id: int,
    config: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update bot configuration"""
    try:
        # Get bot instance
        stmt = select(BotInstance).where(
            BotInstance.id == bot_id,
            BotInstance.user_id == current_user.id  # type: ignore
        )
        result = await db.execute(stmt)
        bot_instance = result.scalar_one_or_none()
        
        if not bot_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bot instance not found"
            )
        
        # Update configuration
        bot_instance.update_config(config)
        await db.commit()
        
        logger.info(f"Bot config updated: {bot_instance.bot_name}")
        
        return {
            "success": True,
            "message": "Bot configuration updated",
            "bot_id": bot_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update bot config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update bot configuration"
        )


@router.post("/{bot_id}/start")
async def start_bot(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start bot instance"""
    try:
        # Get bot instance
        stmt = select(BotInstance).where(
            BotInstance.id == bot_id,
            BotInstance.user_id == current_user.id  # type: ignore
        )
        result = await db.execute(stmt)
        bot_instance = result.scalar_one_or_none()
        
        if not bot_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bot instance not found"
            )
        
        if bot_instance.is_active:  # type: ignore
            return {
                "success": True,
                "message": "Bot is already running",
                "bot_id": bot_id
            }
        
        # Start bot process
        await bot_launcher._start_bot_process(bot_instance, db)
        
        return {
            "success": True,
            "message": "Bot started successfully",
            "bot_id": bot_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start bot"
        )


@router.post("/{bot_id}/stop")
async def stop_bot(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stop bot instance"""
    try:
        # Get bot instance
        stmt = select(BotInstance).where(
            BotInstance.id == bot_id,
            BotInstance.user_id == current_user.id  # type: ignore
        )
        result = await db.execute(stmt)
        bot_instance = result.scalar_one_or_none()
        
        if not bot_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bot instance not found"
            )
        
        # Stop bot
        await bot_launcher.stop_bot_instance(bot_instance, db)
        
        return {
            "success": True,
            "message": "Bot stopped successfully",
            "bot_id": bot_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop bot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop bot"
        )


@router.post("/{bot_id}/restart")
async def restart_bot(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Restart bot instance"""
    try:
        # Get bot instance
        stmt = select(BotInstance).where(
            BotInstance.id == bot_id,
            BotInstance.user_id == current_user.id  # type: ignore
        )
        result = await db.execute(stmt)
        bot_instance = result.scalar_one_or_none()
        
        if not bot_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bot instance not found"
            )
        
        # Restart bot
        await bot_launcher.restart_bot_instance(bot_instance, db)
        
        return {
            "success": True,
            "message": "Bot restarted successfully",
            "bot_id": bot_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to restart bot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to restart bot"
        )


@router.delete("/{bot_id}")
async def delete_bot(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete bot instance"""
    try:
        # Get bot instance
        stmt = select(BotInstance).where(
            BotInstance.id == bot_id,
            BotInstance.user_id == current_user.id  # type: ignore
        )
        result = await db.execute(stmt)
        bot_instance = result.scalar_one_or_none()
        
        if not bot_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bot instance not found"
            )
        
        # Stop bot first if running
        if bot_instance.is_active:  # type: ignore
            await bot_launcher.stop_bot_instance(bot_instance, db)
        
        # Delete from database
        await db.delete(bot_instance)
        await db.commit()
        
        logger.info(f"Bot instance deleted: {bot_instance.bot_name}")
        
        return {
            "success": True,
            "message": "Bot deleted successfully",
            "bot_id": bot_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete bot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete bot"
        )


@router.get("/personalities/available")
async def get_available_personalities():
    """Get available bot personalities"""
    return {
        "success": True,
        "personalities": bot_launcher.personalities
    } 