#!/usr/bin/env python3
"""
Telegram broadcast endpoints (one-shot group message)
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter
from pydantic import BaseModel

try:
    from telethon import TelegramClient, events
except Exception:  # pragma: no cover
    TelegramClient = None  # type: ignore


logger = structlog.get_logger("gavatcore.telegram_api")
router = APIRouter()


class BroadcastRequest(BaseModel):
    session_name: str  # e.g. "sessions/gawatbaba"
    group_ids: List[str]  # numeric chat ids as strings
    message: str
    api_id: Optional[int] = None
    api_hash: Optional[str] = None


@router.post("/broadcast")
async def broadcast_to_groups(payload: BroadcastRequest):
    if TelegramClient is None:
        return {"success": False, "message": "Telethon yüklü değil"}

    api_id_env = os.getenv("TELEGRAM_API_ID")
    api_hash_env = os.getenv("TELEGRAM_API_HASH")

    api_id = payload.api_id or (int(api_id_env) if api_id_env and api_id_env.isdigit() else None)
    api_hash = payload.api_hash or api_hash_env

    if not api_id or not api_hash:
        return {"success": False, "message": "TELEGRAM_API_ID/TELEGRAM_API_HASH eksik"}

    client = None
    try:
        os.makedirs(os.path.dirname(payload.session_name or "sessions"), exist_ok=True)
        client = TelegramClient(payload.session_name, api_id, api_hash)

        await client.connect()

        if not await client.is_user_authorized():
            return {"success": False, "message": "Session yetkili değil. Önce giriş yapın."}

        sent = 0
        errors: List[str] = []
        for gid in payload.group_ids:
            try:
                chat_id = int(gid)
                await client.send_message(chat_id, payload.message)
                sent += 1
            except Exception as e:  # pragma: no cover
                errors.append(f"{gid}: {e}")

        return {
            "success": True,
            "message": f"Mesaj gönderildi: {sent}/{len(payload.group_ids)}",
            "sent": sent,
            "total": len(payload.group_ids),
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
        return {"success": False, "message": str(e)}
    finally:
        if client is not None:
            await client.disconnect()


# ================== USERBOT AUTH (Telethon) ==================
_temp_sessions: Dict[str, Dict[str, Any]] = {}
_auto_bots: Dict[str, Dict[str, Any]] = {}


class SendCodeRequest(BaseModel):
    phone_number: str
    session_name: str  # e.g. "sessions/gawatbaba"
    api_id: Optional[int] = None
    api_hash: Optional[str] = None


@router.post("/auth/send-code")
async def telegram_send_code(req: SendCodeRequest):
    if TelegramClient is None:
        return {"success": False, "message": "Telethon yüklü değil"}

    api_id_env = os.getenv("TELEGRAM_API_ID")
    api_hash_env = os.getenv("TELEGRAM_API_HASH")
    api_id = req.api_id or (int(api_id_env) if api_id_env and api_id_env.isdigit() else None)
    api_hash = req.api_hash or api_hash_env
    if not api_id or not api_hash:
        return {"success": False, "message": "TELEGRAM_API_ID/TELEGRAM_API_HASH eksik"}

    client = None
    try:
        os.makedirs(os.path.dirname(req.session_name or "sessions"), exist_ok=True)
        client = TelegramClient(req.session_name, api_id, api_hash)
        await client.connect()

        sent = await client.send_code_request(req.phone_number)

        _temp_sessions[req.session_name] = {
            "client": client,
            "phone": req.phone_number,
            "phone_code_hash": getattr(sent, "phone_code_hash", None),
            "api_id": api_id,
            "api_hash": api_hash,
            "created_at": datetime.utcnow().isoformat(),
        }

        return {
            "success": True,
            "session_name": req.session_name,
            "phone_code_hash": getattr(sent, "phone_code_hash", None),
            "message": "Doğrulama kodu gönderildi",
        }
    except Exception as e:
        if client is not None:
            try:
                await client.disconnect()
            except Exception:
                pass
        logger.error(f"send-code error: {e}")
        return {"success": False, "message": str(e)}


class VerifyCodeRequest(BaseModel):
    session_name: str
    code: str


@router.post("/auth/verify-code")
async def telegram_verify_code(req: VerifyCodeRequest):
    if TelegramClient is None:
        return {"success": False, "message": "Telethon yüklü değil"}
    if req.session_name not in _temp_sessions:
        return {"success": False, "message": "Session bulunamadı. send-code ile başlayın"}

    data = _temp_sessions[req.session_name]
    client: TelegramClient = data["client"]
    phone: str = data["phone"]
    phone_code_hash: Optional[str] = data.get("phone_code_hash")

    from telethon.errors import SessionPasswordNeededError

    try:
        await client.sign_in(phone=phone, code=req.code, phone_code_hash=phone_code_hash)
        me = await client.get_me()
        await client.disconnect()
        # Temizle
        _temp_sessions.pop(req.session_name, None)

        return {
            "success": True,
            "user": {
                "id": getattr(me, "id", None),
                "username": getattr(me, "username", None),
                "phone": getattr(me, "phone", None),
                "name": f"{getattr(me, 'first_name', '')} {getattr(me, 'last_name', '')}".strip(),
            },
            "message": "Giriş başarılı",
        }
    except SessionPasswordNeededError:
        # 2FA gerekli, client açık kalsın
        return {"success": False, "needs_password": True, "message": "2FA gerekli"}
    except Exception as e:
        logger.error(f"verify-code error: {e}")
        try:
            await client.disconnect()
        except Exception:
            pass
        _temp_sessions.pop(req.session_name, None)
        return {"success": False, "message": str(e)}


class Verify2FARequest(BaseModel):
    session_name: str
    password: str


@router.post("/auth/verify-2fa")
async def telegram_verify_2fa(req: Verify2FARequest):
    if TelegramClient is None:
        return {"success": False, "message": "Telethon yüklü değil"}
    if req.session_name not in _temp_sessions:
        return {"success": False, "message": "Session bulunamadı. send-code ile başlayın"}

    data = _temp_sessions[req.session_name]
    client: TelegramClient = data["client"]
    try:
        await client.sign_in(password=req.password)
        me = await client.get_me()
        await client.disconnect()
        _temp_sessions.pop(req.session_name, None)
        return {
            "success": True,
            "user": {
                "id": getattr(me, "id", None),
                "username": getattr(me, "username", None),
                "phone": getattr(me, "phone", None),
            },
            "message": "2FA doğrulandı",
        }
    except Exception as e:
        logger.error(f"verify-2fa error: {e}")
        try:
            await client.disconnect()
        except Exception:
            pass
        _temp_sessions.pop(req.session_name, None)
        return {"success": False, "message": str(e)}


# ================== STATUS & CHAT/MESSAGE ENDPOINTS ==================
class StatusRequest(BaseModel):
    session_name: str
    api_id: Optional[int] = None
    api_hash: Optional[str] = None


@router.get("/status")
async def telegram_status(session_name: str, limit: int = 50):
    if TelegramClient is None:
        return {"success": False, "message": "Telethon yüklü değil"}
    client = None
    try:
        api_id_env = os.getenv("TELEGRAM_API_ID")
        api_hash_env = os.getenv("TELEGRAM_API_HASH")
        api_id = int(api_id_env) if api_id_env and api_id_env.isdigit() else None
        api_hash = api_hash_env
        client = TelegramClient(session_name, api_id, api_hash)
        await client.connect()
        authorized = await client.is_user_authorized()
        me = None
        dialogs_count = 0
        if authorized:
            me_obj = await client.get_me()
            me = {
                "id": getattr(me_obj, "id", None),
                "username": getattr(me_obj, "username", None),
                "phone": getattr(me_obj, "phone", None),
                "name": f"{getattr(me_obj, 'first_name', '')} {getattr(me_obj, 'last_name', '')}".strip(),
            }
            async for _ in client.iter_dialogs(limit=limit):
                dialogs_count += 1
        return {
            "success": True,
            "connected": True,
            "authorized": authorized,
            "me": me,
            "dialogs_count": dialogs_count,
        }
    except Exception as e:
        logger.error(f"status error: {e}")
        return {"success": False, "message": str(e)}
    finally:
        if client is not None:
            await client.disconnect()


@router.get("/chats")
async def telegram_chats(session_name: str, limit: int = 50, only_private: bool = False):
    if TelegramClient is None:
        return {"success": False, "message": "Telethon yüklü değil"}
    client = None
    try:
        api_id_env = os.getenv("TELEGRAM_API_ID")
        api_hash_env = os.getenv("TELEGRAM_API_HASH")
        api_id = int(api_id_env) if api_id_env and api_id_env.isdigit() else None
        api_hash = api_hash_env
        client = TelegramClient(session_name, api_id, api_hash)
        await client.connect()
        if not await client.is_user_authorized():
            return {"success": False, "message": "Session yetkili değil"}
        chats: List[Dict[str, Any]] = []
        async for dialog in client.iter_dialogs(limit=limit):
            is_group = bool(dialog.is_group)
            is_channel = bool(dialog.is_channel)
            is_private = not (is_group or is_channel)
            if only_private and not is_private:
                continue
            title = dialog.title
            if is_private:
                # Private chat title fallback
                try:
                    u = dialog.entity
                    first = getattr(u, "first_name", "") or ""
                    last = getattr(u, "last_name", "") or ""
                    uname = getattr(u, "username", "") or ""
                    title = (first + " " + last).strip() or (
                        ("@" + uname) if uname else str(dialog.id)
                    )
                except Exception:
                    pass
            chats.append(
                {
                    "id": dialog.id,
                    "title": title,
                    "is_channel": is_channel,
                    "is_group": is_group,
                    "is_private": is_private,
                }
            )
        return {"success": True, "chats": chats}
    except Exception as e:
        logger.error(f"chats error: {e}")
        return {"success": False, "message": str(e)}
    finally:
        if client is not None:
            await client.disconnect()


@router.get("/messages")
async def telegram_messages(session_name: str, chat_id: int, limit: int = 50):
    if TelegramClient is None:
        return {"success": False, "message": "Telethon yüklü değil"}
    client = None
    try:
        api_id_env = os.getenv("TELEGRAM_API_ID")
        api_hash_env = os.getenv("TELEGRAM_API_HASH")
        api_id = int(api_id_env) if api_id_env and api_id_env.isdigit() else None
        api_hash = api_hash_env
        client = TelegramClient(session_name, api_id, api_hash)
        await client.connect()
        if not await client.is_user_authorized():
            return {"success": False, "message": "Session yetkili değil"}
        msgs = []
        for m in await client.get_messages(chat_id, limit=limit):
            msgs.append(
                {
                    "id": getattr(m, "id", None),
                    "date": getattr(m, "date", None).isoformat()
                    if getattr(m, "date", None)
                    else None,
                    "text": getattr(m, "message", None),
                }
            )
        return {"success": True, "messages": msgs}
    except Exception as e:
        logger.error(f"messages error: {e}")
        return {"success": False, "message": str(e)}
    finally:
        if client is not None:
            await client.disconnect()


class SendMessageRequest(BaseModel):
    session_name: str
    chat_id: int
    message: str


@router.post("/send-message")
async def telegram_send_message(req: SendMessageRequest):
    if TelegramClient is None:
        return {"success": False, "message": "Telethon yüklü değil"}
    client = None
    try:
        api_id_env = os.getenv("TELEGRAM_API_ID")
        api_hash_env = os.getenv("TELEGRAM_API_HASH")
        api_id = int(api_id_env) if api_id_env and api_id_env.isdigit() else None
        api_hash = api_hash_env
        client = TelegramClient(req.session_name, api_id, api_hash)
        await client.connect()
        if not await client.is_user_authorized():
            return {"success": False, "message": "Session yetkili değil"}
        await client.send_message(int(req.chat_id), req.message)
        return {"success": True, "message": "Gönderildi"}
    except Exception as e:
        logger.error(f"send-message error: {e}")
        return {"success": False, "message": str(e)}
    finally:
        if client is not None:
            await client.disconnect()


# ================== AUTO MODE (BACKGROUND) ==================
class AutoStartRequest(BaseModel):
    session_name: str
    engage_probability_messages: float = 0.10  # 0-1 arası
    engage_probability_replies: float = 0.20  # 0-1 arası
    min_interval_seconds: int = 1800
    max_interval_seconds: int = 3600


@router.get("/auto/status")
async def auto_status(session_name: str):
    running = session_name in _auto_bots
    return {"success": True, "running": running}


@router.post("/auto/start")
async def auto_start(payload: AutoStartRequest):
    if TelegramClient is None:
        return {"success": False, "message": "Telethon yüklü değil"}
    if payload.session_name in _auto_bots:
        return {"success": True, "message": "Zaten çalışıyor"}

    import asyncio
    import json
    import os
    import random

    api_id_env = os.getenv("TELEGRAM_API_ID")
    api_hash_env = os.getenv("TELEGRAM_API_HASH")
    api_id = int(api_id_env) if api_id_env and api_id_env.isdigit() else None
    api_hash = api_hash_env
    if not api_id or not api_hash:
        return {"success": False, "message": "TELEGRAM_API_ID/TELEGRAM_API_HASH eksik"}

    # Persona'dan mesajları yükle (fallback boş listeler)
    engaging_messages: List[str] = []
    reply_messages: List[str] = []
    try:
        # Path: gavatcore-api/app/routes/telegram.py -> gavatcore/data/personas/yagmur.json
        # Go up 4 levels to project root, then into data/personas
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        persona_path = os.path.join(project_root, "data", "personas", "yagmur.json")
        with open(persona_path, "r", encoding="utf-8") as f:
            persona = json.load(f)
        engaging_messages = persona.get("engaging_messages", []) or []
        reply_messages = persona.get("reply_messages", []) or []
    except Exception:
        # Çalışmaya engel değil
        pass

    client = TelegramClient(payload.session_name, api_id, api_hash)

    async def runner():
        try:
            await client.connect()
            if not await client.is_user_authorized():
                await client.disconnect()
                raise RuntimeError("Session yetkili değil")

            @client.on(events.NewMessage(incoming=True))
            async def handler(event):
                try:
                    # Grup/kanal mesajlarına ara sıra yanıt
                    if (
                        getattr(event, "is_group", False) or getattr(event, "is_channel", False)
                    ) and random.random() < payload.engage_probability_replies:
                        if reply_messages:
                            await event.reply(random.choice(reply_messages))
                except Exception:
                    pass

            async def periodic():
                while True:
                    try:
                        async for dialog in client.iter_dialogs():
                            if (
                                dialog.is_group or dialog.is_channel
                            ) and random.random() < payload.engage_probability_messages:
                                if engaging_messages:
                                    try:
                                        await client.send_message(
                                            dialog, random.choice(engaging_messages)
                                        )
                                    except Exception:
                                        pass
                        await asyncio.sleep(
                            random.randint(
                                payload.min_interval_seconds, payload.max_interval_seconds
                            )
                        )
                    except Exception:
                        await asyncio.sleep(600)

            periodic_task = asyncio.create_task(periodic())
            # Store the periodic task so it can be cancelled on stop
            if payload.session_name in _auto_bots:
                _auto_bots[payload.session_name]["periodic_task"] = periodic_task
            logger.info("Yağmur otomatik mod aktif", session=payload.session_name)
            await client.run_until_disconnected()
        except Exception as e:
            logger.error(f"auto runner error: {e}")
        finally:
            # Cancel periodic task on cleanup
            if payload.session_name in _auto_bots:
                periodic_task = _auto_bots[payload.session_name].get("periodic_task")
                if periodic_task and not periodic_task.done():
                    periodic_task.cancel()
            try:
                await client.disconnect()
            except Exception:
                pass
            _auto_bots.pop(payload.session_name, None)

    task = asyncio.create_task(runner())
    _auto_bots[payload.session_name] = {"task": task, "client": client, "periodic_task": None}
    return {"success": True, "message": "Otomatik mod başlatıldı"}


@router.post("/auto/stop")
async def auto_stop(session_name: str):
    data = _auto_bots.get(session_name)
    if not data:
        return {"success": True, "message": "Zaten durdu"}

    # Cancel periodic task first to stop the infinite loop
    periodic_task = data.get("periodic_task")
    if periodic_task and not periodic_task.done():
        try:
            periodic_task.cancel()
        except Exception:
            pass

    # Disconnect client
    client: TelegramClient = data.get("client")
    try:
        await client.disconnect()
    except Exception:
        pass

    # Cancel runner task
    task = data.get("task")
    if task and not task.done():
        try:
            task.cancel()
        except Exception:
            pass

    _auto_bots.pop(session_name, None)
    return {"success": True, "message": "Otomatik mod durduruldu"}
