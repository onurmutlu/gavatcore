#!/usr/bin/env python3
"""
Baron Bot Handler — GavatCore sistem hesabı mesaj işleme motoru.
"""

from __future__ import annotations

import json
import os
import random
from datetime import datetime
from typing import Any, Dict, Optional

import structlog
from telethon import TelegramClient
from telethon.tl.types import User

from character_engine import (
    CharacterConfig,
    CharacterManager,
    FallbackReplyManager,
    GPTReplyGenerator,
    MemoryContextTracker,
)
from utilities.humanizer import Humanizer

logger = structlog.get_logger("baron_bot_handler")

PERSONA_FILE = "data/personas/baron.json"
BOT_NAME = "baron"

_stats: Dict[str, Any] = {
    "dm_handled": 0,
    "group_handled": 0,
    "gpt_replies": 0,
    "template_replies": 0,
    "errors": 0,
    "started_at": datetime.now().isoformat(),
}

character_manager = CharacterManager()
memory_tracker = MemoryContextTracker()
gpt_generator = GPTReplyGenerator()
fallback_manager = FallbackReplyManager()
humanizer = Humanizer(
    character_config={
        "typing_speed": 22,
        "emoji_usage_rate": 0.05,
        "mistake_chance": 0.02,
        "response_delay_range": [1.0, 3.0],
        "silence_chance": 0.05,
    }
)

_ai_blending = None
_conversations: Dict[str, list] = {}


def _track_message(user_id: str, role: str, content: str) -> None:
    if user_id not in _conversations:
        _conversations[user_id] = []
    _conversations[user_id].append({"role": role, "content": content})
    if len(_conversations[user_id]) > 20:
        _conversations[user_id] = _conversations[user_id][-20:]
    memory_tracker.add_memory(
        user_id,
        {"role": role, "content": content, "timestamp": datetime.now().isoformat()},
    )


def _get_context_messages(user_id: str) -> list:
    return list(_conversations.get(user_id, []))


def _load_persona() -> Dict[str, Any]:
    if os.path.exists(PERSONA_FILE):
        with open(PERSONA_FILE, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return {}


def _get_character() -> CharacterConfig:
    if "baron" in character_manager.characters:
        return character_manager.characters["baron"]
    persona = _load_persona()
    persona_block = persona.get("persona", {})
    return CharacterConfig(
        name=persona.get("display_name", "Baron"),
        username=persona.get("username", "baron"),
        system_prompt=persona_block.get(
            "gpt_prompt",
            "Sen Baron'sun. Özgüvenli, net ve lider bir üslupla konuşursun.",
        ),
        reply_mode=persona.get("reply_mode", "hybrid"),
        tone="professional",
        template_replies=[
            "Mesajını aldım. Kısa sürede döneceğim.",
            "Net konuşalım — ne istiyorsun?",
            "Buradayım. Devam et.",
        ],
        gpt_settings={"model": "gpt-4o", "temperature": 0.7, "max_tokens": 200},
    )


async def _maybe_init_ai_blending() -> None:
    global _ai_blending
    if _ai_blending is not None:
        return
    try:
        from gavatcore_engine.ai_blending import AIBlendingSystem

        system = AIBlendingSystem()
        if await system.initialize():
            _ai_blending = system
            logger.info("AI blending aktif")
    except Exception as exc:
        logger.warning("AI blending devre dışı", error=str(exc))


async def _generate_reply(user_id: str, message_text: str, use_blending: bool = True) -> str:
    character = _get_character()
    _track_message(user_id, "user", message_text)
    context = _get_context_messages(user_id)
    reply: Optional[str] = None

    if character.reply_mode in ("gpt", "hybrid") and gpt_generator.client:
        reply = await gpt_generator.generate_reply(
            user_message=message_text,
            character_config=character.to_dict(),
            context_messages=context,
            user_id=user_id,
        )
        if reply:
            _stats["gpt_replies"] += 1

    if not reply and character.template_replies:
        reply = random.choice(character.template_replies)
        _stats["template_replies"] += 1

    if not reply:
        reply = await fallback_manager.get_fallback_reply(
            user_id=user_id,
            character_config=character.to_dict(),
            fallback_type="no_reply",
        )
        if not reply:
            reply = "Mesajını aldım, kısa sürede döneceğim."

    if use_blending and os.getenv("BARON_AI_BLEND", "true").lower() == "true":
        await _maybe_init_ai_blending()
        if _ai_blending and _ai_blending.openai_client:
            try:
                from gavatcore_engine.ai_blending import EnhancementType

                blended = await _ai_blending.generate_response(
                    text=reply,
                    bot_name="baron",
                    target_entity=user_id,
                    enhancement_type=EnhancementType.PROFESSIONAL,
                )
                if blended:
                    reply = blended
            except Exception as exc:
                logger.warning("AI blend atlandı", error=str(exc))

    _track_message(user_id, "assistant", reply)
    return reply


async def handle_baron_dm(
    client: TelegramClient,
    sender: User,
    message_text: str,
) -> bool:
    try:
        if getattr(sender, "bot", False):
            return False

        user_id = str(sender.id)
        user_name = sender.first_name or "kullanıcı"
        logger.info("Baron DM", user=user_name, preview=message_text[:80])

        if not humanizer.should_respond():
            logger.info("Baron sessiz mod", user=user_name)
            return True

        reply = await _generate_reply(user_id, message_text)
        await humanizer.send_typing_then_message(client, sender.id, reply)
        _stats["dm_handled"] += 1
        return True
    except Exception as exc:
        _stats["errors"] += 1
        logger.error("Baron DM hatası", error=str(exc))
        return False


async def handle_baron_group_message(
    client: TelegramClient,
    event,
    username: str,
) -> bool:
    try:
        sender = await event.get_sender()
        if not sender or getattr(sender, "bot", False):
            return False

        raw = event.raw_text or ""
        if not (event.is_reply or f"@{username.lower()}" in raw.lower()):
            return False

        clean = raw.replace(f"@{username}", "").strip()
        user_id = str(sender.id)
        character = _get_character()

        if character.reply_mode in ("gpt", "hybrid") and gpt_generator.client:
            reply = await gpt_generator.generate_reply(
                user_message=clean or "mention",
                character_config={
                    **character.to_dict(),
                    "system_prompt": (
                        f"{character.system_prompt} "
                        "Grup mesajına çok kısa (1-2 cümle) yanıt ver."
                    ),
                },
                user_id=user_id,
            )
        else:
            reply = random.choice(
                character.template_replies
                or ["Buradayım. DM'den devam edelim."]
            )

        await humanizer.send_typing_then_message(
            client, event.chat_id, reply, reply_to=event.id
        )
        _stats["group_handled"] += 1
        return True
    except Exception as exc:
        _stats["errors"] += 1
        logger.error("Baron grup hatası", error=str(exc))
        return False


def get_baron_stats() -> Dict[str, Any]:
    character = _get_character()
    return {
        **_stats,
        "character": character.name,
        "reply_mode": character.reply_mode,
        "gpt_available": gpt_generator.client is not None,
        "active_conversations": len(_conversations),
    }


async def test_baron_gpt(message: str) -> Dict[str, Any]:
    reply = await _generate_reply("test_user", message, use_blending=True)
    return {
        "input": message,
        "output": reply,
        "reply_mode": _get_character().reply_mode,
        "gpt_available": gpt_generator.client is not None,
    }
