"""Typed, owner-scoped settings for the web panel.

Process control is intentionally unavailable until the existing launcher can
track and terminate processes. No sample metrics or success fallbacks are used.
"""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user, get_db
from app.models.bot_instance import BotInstance
from app.models.user import User

router = APIRouter()


class BotSettings(BaseModel):
    reply_mode: Literal["manual", "manualplus", "hybrid", "gpt"]
    scheduler_enabled: bool
    scheduler_interval: int = Field(ge=30, le=86400)

    class Config:
        extra = "forbid"
        from_attributes = True


@router.get("/capabilities")
async def capabilities():
    return {
        "local_preview": settings.PANEL_LOCAL_PREVIEW,
        "process_control": False,
        "process_control_reason": "Süreç yöneticisi henüz bağlı değil. Başlatma ve durdurma kullanılamıyor.",
    }


async def owned_bot(bot_id: int, user: User, db: AsyncSession) -> BotInstance:
    bot = await db.scalar(select(BotInstance).where(
        BotInstance.id == bot_id, BotInstance.user_id == user.id
    ))
    if bot is None:
        raise HTTPException(status_code=404, detail="Bot bulunamadı")
    return bot


@router.get("/bots/{bot_id}/settings", response_model=BotSettings)
async def get_settings(bot_id: int, user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    return await owned_bot(bot_id, user, db)


@router.put("/bots/{bot_id}/settings", response_model=BotSettings)
async def save_settings(bot_id: int, body: BotSettings,
                        user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    bot = await owned_bot(bot_id, user, db)
    for key, value in body.model_dump().items():
        setattr(bot, key, value)
    config = bot.get_config_dict()
    config.update(body.model_dump())
    bot.update_config(config)
    await db.commit()
    await db.refresh(bot)
    return bot
