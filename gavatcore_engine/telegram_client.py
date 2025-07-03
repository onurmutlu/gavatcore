"""
Telegram Client Management
=========================

Advanced Telegram client wrapper using Telethon with session management,
retry mechanisms, and centralized logging.
"""

import asyncio
import json
import os
import time
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from telethon import TelegramClient, events
from telethon.errors import (
    FloodWaitError,
    SessionPasswordNeededError,
    ApiIdInvalidError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    UserDeactivatedError,
    UserDeactivatedBanError,
    ChatWriteForbiddenError,
    MessageTooLongError,
    SlowModeWaitError,
    AuthKeyUnregisteredError,
    AuthKeyInvalidError,
    AuthKeyDuplicatedError,
    AuthRestartError,
    RPCError,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    FloodError,
    InternalServerError,
)
from telethon.tl.types import (
    User, Chat, Channel, Message, 
    MessageEntityMention, MessageEntityHashtag,
    PeerUser, PeerChat, PeerChannel,
    InputPeerUser, InputPeerChat, InputPeerChannel
)
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.sessions import StringSession, SQLiteSession

from .config import get_settings
from .logger import LoggerMixin
from .redis_state import redis_state


class ConnectionStatus(Enum):
    """Connection status enum."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"
    BANNED = "banned"
    UNAUTHORIZED = "unauthorized"


class MessageResult(Enum):
    """Message sending result enum."""
    SUCCESS = "success"
    FAILED = "failed"
    FLOOD_WAIT = "flood_wait"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    TOO_LONG = "too_long"
    RETRY = "retry"


@dataclass
class ClientConfig:
    """Telegram client configuration."""
    session_name: str
    api_id: int
    api_hash: str
    bot_token: Optional[str] = None
    phone: Optional[str] = None
    session_string: Optional[str] = None
    device_model: str = "GavatCore Bot"
    system_version: str = "1.0.0"
    app_version: str = "GavatCore Engine v1.0"
    lang_code: str = "tr"
    system_lang_code: str = "tr"
    connection_retries: int = 5
    retry_delay: int = 5
    timeout: int = 30
    request_retries: int = 3
    flood_sleep_threshold: int = 60
    auto_reconnect: bool = True
    sequential_updates: bool = True


@dataclass
class MessageSendResult:
    """Message sending result."""
    success: bool
    result: MessageResult
    message_id: Optional[int] = None
    error: Optional[str] = None
    retry_after: Optional[int] = None
    flood_wait_time: Optional[int] = None
    sent_message: Optional[Message] = None


@dataclass
class RetryConfig:
    """Retry configuration."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_flood: bool = True
    retry_on_server_error: bool = True
    retry_on_network_error: bool = True


class TelegramClientManager(LoggerMixin):
    """Advanced Telegram client manager with session management and retry logic."""
    
    def __init__(self, config: ClientConfig):
        self.config = config
        self.settings = get_settings()
        
        # Client state
        self.client: Optional[TelegramClient] = None
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.user_info: Optional[User] = None
        self.session_path: Optional[str] = None
        
        # Rate limiting and flood protection
        self.last_message_time: Dict[int, float] = {}
        self.flood_wait_until: Dict[int, datetime] = {}
        self.rate_limit_delay = 1.0  # Minimum delay between messages
        
        # Retry configuration
        self.retry_config = RetryConfig()
        
        # Event handlers
        self.message_handlers: List[Callable] = []
        self.disconnect_handlers: List[Callable] = []
        
        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_failed": 0,
            "flood_waits": 0,
            "reconnections": 0,
            "last_activity": None,
            "uptime_start": None,
        }
    
    async def initialize(self) -> bool:
        """Initialize the Telegram client."""
        try:
            self.log_event(
                "Initializing Telegram client",
                session_name=self.config.session_name,
                device_model=self.config.device_model,
            )
            
            # Create session
            session = self._create_session()
            
            # Create client
            self.client = TelegramClient(
                session,
                self.config.api_id,
                self.config.api_hash,
                device_model=self.config.device_model,
                system_version=self.config.system_version,
                app_version=self.config.app_version,
                lang_code=self.config.lang_code,
                system_lang_code=self.config.system_lang_code,
                connection_retries=self.config.connection_retries,
                retry_delay=self.config.retry_delay,
                timeout=self.config.timeout,
                request_retries=self.config.request_retries,
                flood_sleep_threshold=self.config.flood_sleep_threshold,
                auto_reconnect=self.config.auto_reconnect,
                sequential_updates=self.config.sequential_updates,
            )
            
            # Connect to Telegram
            success = await self._connect_with_retry()
            
            if success:
                # Setup event handlers
                await self._setup_event_handlers()
                
                # Store session info in Redis
                await self._store_session_info()
                
                self.stats["uptime_start"] = datetime.utcnow()
                
                self.log_event(
                    "Telegram client initialized successfully",
                    session_name=self.config.session_name,
                    username=self.user_info.username if self.user_info else None,
                    user_id=self.user_info.id if self.user_info else None,
                )
            
            return success
            
        except Exception as e:
            self.log_error(
                "Failed to initialize Telegram client",
                session_name=self.config.session_name,
                error=str(e),
            )
            self.connection_status = ConnectionStatus.FAILED
            return False
    
    async def disconnect(self) -> None:
        """Disconnect the Telegram client."""
        if self.client and self.connection_status == ConnectionStatus.CONNECTED:
            try:
                self.log_event("Disconnecting Telegram client")
                
                # Call disconnect handlers
                for handler in self.disconnect_handlers:
                    try:
                        await handler()
                    except Exception as e:
                        self.log_error("Disconnect handler error", error=str(e))
                
                # Disconnect client
                await self.client.disconnect()
                self.connection_status = ConnectionStatus.DISCONNECTED
                
                # Remove from Redis
                await self._remove_session_info()
                
                self.log_event("Telegram client disconnected")
                
            except Exception as e:
                self.log_error("Error during disconnect", error=str(e))
    
    async def send_message(
        self,
        entity: Union[str, int, User, Chat, Channel],
        message: str,
        parse_mode: Optional[str] = 'html',
        link_preview: bool = False,
        file: Optional[str] = None,
        force_document: bool = False,
        clear_draft: bool = False,
        buttons: Optional[Any] = None,
        silent: bool = False,
        schedule: Optional[datetime] = None,
    ) -> MessageSendResult:
        """Send a message with retry logic and flood protection."""
        
        if not self.client or self.connection_status != ConnectionStatus.CONNECTED:
            return MessageSendResult(
                success=False,
                result=MessageResult.FAILED,
                error="Client not connected"
            )
        
        # Check flood wait
        chat_id = await self._get_chat_id(entity)
        if chat_id in self.flood_wait_until:
            wait_until = self.flood_wait_until[chat_id]
            if datetime.utcnow() < wait_until:
                remaining = (wait_until - datetime.utcnow()).total_seconds()
                return MessageSendResult(
                    success=False,
                    result=MessageResult.FLOOD_WAIT,
                    flood_wait_time=int(remaining),
                    error=f"Flood wait: {remaining:.0f} seconds remaining"
                )
        
        # Apply rate limiting
        await self._apply_rate_limit(chat_id)
        
        # Attempt to send message with retry
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                self.log_event(
                    "Sending message",
                    entity=str(entity),
                    attempt=attempt + 1,
                    message_length=len(message),
                    parse_mode=parse_mode,
                )
                
                # Send message
                sent_message = await self.client.send_message(
                    entity=entity,
                    message=message,
                    parse_mode=parse_mode,
                    link_preview=link_preview,
                    file=file,
                    force_document=force_document,
                    clear_draft=clear_draft,
                    buttons=buttons,
                    silent=silent,
                    schedule=schedule,
                )
                
                # Success
                self.stats["messages_sent"] += 1
                self.stats["last_activity"] = datetime.utcnow()
                
                self.log_event(
                    "Message sent successfully",
                    entity=str(entity),
                    message_id=sent_message.id,
                    attempt=attempt + 1,
                )
                
                # Store success in Redis
                await redis_state.increment_bot_stat(
                    self.config.session_name, 
                    "messages_sent"
                )
                
                return MessageSendResult(
                    success=True,
                    result=MessageResult.SUCCESS,
                    message_id=sent_message.id,
                    sent_message=sent_message,
                )
                
            except FloodWaitError as e:
                self.stats["flood_waits"] += 1
                flood_wait_time = e.seconds
                
                self.log_event(
                    "Flood wait encountered",
                    entity=str(entity),
                    wait_time=flood_wait_time,
                    attempt=attempt + 1,
                )
                
                # Set flood wait
                self.flood_wait_until[chat_id] = datetime.utcnow() + timedelta(seconds=flood_wait_time)
                
                if self.retry_config.retry_on_flood and attempt < self.retry_config.max_retries:
                    await asyncio.sleep(min(flood_wait_time, 300))  # Max 5 minutes
                    continue
                else:
                    return MessageSendResult(
                        success=False,
                        result=MessageResult.FLOOD_WAIT,
                        flood_wait_time=flood_wait_time,
                        error=f"Flood wait: {flood_wait_time} seconds"
                    )
            
            except SlowModeWaitError as e:
                wait_time = e.seconds
                self.log_event(
                    "Slow mode wait",
                    entity=str(entity),
                    wait_time=wait_time,
                    attempt=attempt + 1,
                )
                
                if attempt < self.retry_config.max_retries:
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    return MessageSendResult(
                        success=False,
                        result=MessageResult.RETRY,
                        retry_after=wait_time,
                        error=f"Slow mode: {wait_time} seconds"
                    )
            
            except MessageTooLongError as e:
                self.log_error(
                    "Message too long",
                    entity=str(entity),
                    message_length=len(message),
                    max_length=4096,
                )
                
                return MessageSendResult(
                    success=False,
                    result=MessageResult.TOO_LONG,
                    error="Message too long"
                )
            
            except (ChatWriteForbiddenError, ForbiddenError) as e:
                self.log_error(
                    "Forbidden to send message",
                    entity=str(entity),
                    error=str(e),
                )
                
                return MessageSendResult(
                    success=False,
                    result=MessageResult.FORBIDDEN,
                    error="Forbidden to send message"
                )
            
            except (NotFoundError, ValueError) as e:
                self.log_error(
                    "Entity not found",
                    entity=str(entity),
                    error=str(e),
                )
                
                return MessageSendResult(
                    success=False,
                    result=MessageResult.NOT_FOUND,
                    error="Entity not found"
                )
            
            except (InternalServerError, RPCError) as e:
                self.log_error(
                    "Server error",
                    entity=str(entity),
                    error=str(e),
                    attempt=attempt + 1,
                )
                
                if (self.retry_config.retry_on_server_error and 
                    attempt < self.retry_config.max_retries):
                    delay = self._calculate_retry_delay(attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    return MessageSendResult(
                        success=False,
                        result=MessageResult.FAILED,
                        error=f"Server error: {str(e)}"
                    )
            
            except Exception as e:
                self.log_error(
                    "Unexpected error sending message",
                    entity=str(entity),
                    error=str(e),
                    attempt=attempt + 1,
                )
                
                if (self.retry_config.retry_on_network_error and 
                    attempt < self.retry_config.max_retries):
                    delay = self._calculate_retry_delay(attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    self.stats["messages_failed"] += 1
                    
                    await redis_state.increment_bot_stat(
                        self.config.session_name, 
                        "messages_failed"
                    )
                    
                    return MessageSendResult(
                        success=False,
                        result=MessageResult.FAILED,
                        error=str(e)
                    )
        
        # All retries exhausted
        self.stats["messages_failed"] += 1
        return MessageSendResult(
            success=False,
            result=MessageResult.FAILED,
            error="All retries exhausted"
        )
    
    async def get_me(self) -> Optional[User]:
        """Get current user info."""
        if not self.client:
            return None
        
        try:
            return await self.client.get_me()
        except Exception as e:
            self.log_error("Failed to get user info", error=str(e))
            return None
    
    async def get_entity(self, entity: Union[str, int]) -> Optional[Union[User, Chat, Channel]]:
        """Get entity information."""
        if not self.client:
            return None
        
        try:
            return await self.client.get_entity(entity)
        except Exception as e:
            self.log_error("Failed to get entity", entity=str(entity), error=str(e))
            return None
    
    async def get_messages(
        self,
        entity: Union[str, int, User, Chat, Channel],
        limit: int = 100,
        offset_date: Optional[datetime] = None,
        offset_id: int = 0,
        max_id: int = 0,
        min_id: int = 0,
        add_offset: int = 0,
        search: Optional[str] = None,
        filter_type: Optional[Any] = None,
        from_user: Optional[Union[str, int, User]] = None,
    ) -> List[Message]:
        """Get messages from entity."""
        if not self.client:
            return []
        
        try:
            messages = await self.client.get_messages(
                entity=entity,
                limit=limit,
                offset_date=offset_date,
                offset_id=offset_id,
                max_id=max_id,
                min_id=min_id,
                add_offset=add_offset,
                search=search,
                filter=filter_type,
                from_user=from_user,
            )
            
            return messages if isinstance(messages, list) else [messages]
            
        except Exception as e:
            self.log_error(
                "Failed to get messages",
                entity=str(entity),
                error=str(e),
            )
            return []
    
    async def is_connected(self) -> bool:
        """Check if client is connected."""
        if not self.client:
            return False
        
        try:
            return self.client.is_connected() and self.connection_status == ConnectionStatus.CONNECTED
        except:
            return False
    
    async def reconnect(self) -> bool:
        """Reconnect the client."""
        self.log_event("Attempting to reconnect")
        self.connection_status = ConnectionStatus.RECONNECTING
        self.stats["reconnections"] += 1
        
        try:
            if self.client:
                await self.client.disconnect()
            
            return await self._connect_with_retry()
            
        except Exception as e:
            self.log_error("Reconnection failed", error=str(e))
            self.connection_status = ConnectionStatus.FAILED
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        uptime = None
        if self.stats["uptime_start"]:
            uptime = (datetime.utcnow() - self.stats["uptime_start"]).total_seconds()
        
        return {
            "session_name": self.config.session_name,
            "connection_status": self.connection_status.value,
            "user_id": self.user_info.id if self.user_info else None,
            "username": self.user_info.username if self.user_info else None,
            "messages_sent": self.stats["messages_sent"],
            "messages_failed": self.stats["messages_failed"],
            "flood_waits": self.stats["flood_waits"],
            "reconnections": self.stats["reconnections"],
            "uptime_seconds": uptime,
            "last_activity": self.stats["last_activity"].isoformat() if self.stats["last_activity"] else None,
            "flood_wait_chats": len(self.flood_wait_until),
        }
    
    def add_message_handler(self, handler: Callable) -> None:
        """Add message event handler."""
        self.message_handlers.append(handler)
    
    def add_disconnect_handler(self, handler: Callable) -> None:
        """Add disconnect event handler."""
        self.disconnect_handlers.append(handler)
    
    def _create_session(self) -> Union[StringSession, SQLiteSession]:
        """Create session object."""
        if self.config.session_string:
            return StringSession(self.config.session_string)
        else:
            # Create sessions directory if it doesn't exist
            sessions_dir = Path("sessions")
            sessions_dir.mkdir(exist_ok=True)
            
            session_file = sessions_dir / f"{self.config.session_name}.session"
            self.session_path = str(session_file)
            
            return SQLiteSession(str(session_file))
    
    async def _connect_with_retry(self) -> bool:
        """Connect with retry logic."""
        for attempt in range(self.config.connection_retries):
            try:
                self.connection_status = ConnectionStatus.CONNECTING
                
                self.log_event(
                    "Connecting to Telegram",
                    attempt=attempt + 1,
                    max_attempts=self.config.connection_retries,
                )
                
                # Start client
                await self.client.start(
                    bot_token=self.config.bot_token,
                    phone=self.config.phone,
                )
                
                # Check authorization
                if not await self.client.is_user_authorized():
                    self.log_error("Client not authorized")
                    self.connection_status = ConnectionStatus.UNAUTHORIZED
                    return False
                
                # Get user info
                self.user_info = await self.client.get_me()
                self.connection_status = ConnectionStatus.CONNECTED
                
                self.log_event(
                    "Connected to Telegram successfully",
                    attempt=attempt + 1,
                    user_id=self.user_info.id,
                    username=self.user_info.username,
                )
                
                return True
                
            except (UserDeactivatedError, UserDeactivatedBanError) as e:
                self.log_error("User banned or deactivated", error=str(e))
                self.connection_status = ConnectionStatus.BANNED
                return False
            
            except (AuthKeyUnregisteredError, AuthKeyInvalidError, AuthKeyDuplicatedError) as e:
                self.log_error("Invalid auth key", error=str(e))
                self.connection_status = ConnectionStatus.UNAUTHORIZED
                return False
            
            except SessionPasswordNeededError:
                self.log_error("2FA required - cannot proceed")
                self.connection_status = ConnectionStatus.UNAUTHORIZED
                return False
            
            except Exception as e:
                self.log_error(
                    "Connection attempt failed",
                    attempt=attempt + 1,
                    error=str(e),
                )
                
                if attempt < self.config.connection_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    self.connection_status = ConnectionStatus.FAILED
                    return False
        
        return False
    
    async def _setup_event_handlers(self) -> None:
        """Setup Telegram event handlers."""
        
        @self.client.on(events.NewMessage(incoming=True))
        async def message_handler(event):
            """Handle incoming messages."""
            try:
                self.log_event(
                    "Incoming message",
                    sender_id=event.sender_id,
                    chat_id=event.chat_id,
                    message_length=len(event.raw_text) if event.raw_text else 0,
                )
                
                # Call custom handlers
                for handler in self.message_handlers:
                    try:
                        await handler(event)
                    except Exception as e:
                        self.log_error("Message handler error", error=str(e))
                
            except Exception as e:
                self.log_error("Message event handler error", error=str(e))
        
        @self.client.on(events.Disconnected)
        async def disconnect_handler():
            """Handle disconnection events."""
            self.log_event("Client disconnected")
            self.connection_status = ConnectionStatus.DISCONNECTED
            
            # Call custom handlers
            for handler in self.disconnect_handlers:
                try:
                    await handler()
                except Exception as e:
                    self.log_error("Disconnect handler error", error=str(e))
    
    async def _apply_rate_limit(self, chat_id: int) -> None:
        """Apply rate limiting between messages."""
        current_time = time.time()
        
        if chat_id in self.last_message_time:
            time_since_last = current_time - self.last_message_time[chat_id]
            if time_since_last < self.rate_limit_delay:
                sleep_time = self.rate_limit_delay - time_since_last
                await asyncio.sleep(sleep_time)
        
        self.last_message_time[chat_id] = time.time()
    
    async def _get_chat_id(self, entity: Union[str, int, User, Chat, Channel]) -> int:
        """Get chat ID from entity."""
        if isinstance(entity, int):
            return entity
        elif isinstance(entity, str):
            if entity.isdigit() or (entity.startswith('-') and entity[1:].isdigit()):
                return int(entity)
            else:
                # Try to resolve username
                try:
                    resolved = await self.client.get_entity(entity)
                    return resolved.id
                except:
                    return hash(entity)  # Fallback
        elif hasattr(entity, 'id'):
            return entity.id
        else:
            return hash(str(entity))
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay with exponential backoff."""
        delay = self.retry_config.base_delay * (self.retry_config.exponential_base ** attempt)
        delay = min(delay, self.retry_config.max_delay)
        
        if self.retry_config.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)  # Add 0-50% jitter
        
        return delay
    
    async def _store_session_info(self) -> None:
        """Store session information in Redis."""
        if not self.user_info:
            return
        
        session_info = {
            "session_name": self.config.session_name,
            "user_id": self.user_info.id,
            "username": self.user_info.username or "",
            "first_name": self.user_info.first_name or "",
            "last_name": self.user_info.last_name or "",
            "phone": self.user_info.phone or "",
            "connected_at": datetime.utcnow().isoformat(),
            "connection_status": self.connection_status.value,
            "device_model": self.config.device_model,
            "app_version": self.config.app_version,
        }
        
        await redis_state.hset(
            f"telegram_client:{self.config.session_name}",
            "session_info",
            json.dumps(session_info)
        )
        
        # Add to active sessions
        await redis_state.sadd("active_telegram_sessions", self.config.session_name)
        
        # Set expiration
        await redis_state.expire(f"telegram_client:{self.config.session_name}", 86400)  # 24 hours
    
    async def _remove_session_info(self) -> None:
        """Remove session information from Redis."""
        await redis_state.delete(f"telegram_client:{self.config.session_name}")
        await redis_state.srem("active_telegram_sessions", self.config.session_name)


class TelegramClientPool(LoggerMixin):
    """Pool of Telegram clients for load balancing and redundancy."""
    
    def __init__(self):
        self.clients: Dict[str, TelegramClientManager] = {}
        self.round_robin_index = 0
    
    async def add_client(self, config: ClientConfig) -> bool:
        """Add a client to the pool."""
        try:
            client_manager = TelegramClientManager(config)
            success = await client_manager.initialize()
            
            if success:
                self.clients[config.session_name] = client_manager
                self.log_event("Client added to pool", session_name=config.session_name)
                return True
            else:
                self.log_error("Failed to add client to pool", session_name=config.session_name)
                return False
                
        except Exception as e:
            self.log_error(
                "Error adding client to pool",
                session_name=config.session_name,
                error=str(e),
            )
            return False
    
    async def remove_client(self, session_name: str) -> bool:
        """Remove a client from the pool."""
        if session_name in self.clients:
            try:
                await self.clients[session_name].disconnect()
                del self.clients[session_name]
                self.log_event("Client removed from pool", session_name=session_name)
                return True
            except Exception as e:
                self.log_error(
                    "Error removing client from pool",
                    session_name=session_name,
                    error=str(e),
                )
                return False
        return False
    
    async def get_client(self, session_name: Optional[str] = None) -> Optional[TelegramClientManager]:
        """Get a client from the pool."""
        if session_name and session_name in self.clients:
            return self.clients[session_name]
        
        # Round-robin selection
        connected_clients = [
            client for client in self.clients.values()
            if client.connection_status == ConnectionStatus.CONNECTED
        ]
        
        if not connected_clients:
            return None
        
        client = connected_clients[self.round_robin_index % len(connected_clients)]
        self.round_robin_index += 1
        
        return client
    
    async def send_message(
        self,
        entity: Union[str, int, User, Chat, Channel],
        message: str,
        session_name: Optional[str] = None,
        **kwargs
    ) -> MessageSendResult:
        """Send message using pool."""
        client = await self.get_client(session_name)
        
        if not client:
            return MessageSendResult(
                success=False,
                result=MessageResult.FAILED,
                error="No available clients"
            )
        
        return await client.send_message(entity, message, **kwargs)
    
    async def get_pool_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        total_clients = len(self.clients)
        connected_clients = sum(
            1 for client in self.clients.values()
            if client.connection_status == ConnectionStatus.CONNECTED
        )
        
        client_stats = {}
        for name, client in self.clients.items():
            client_stats[name] = await client.get_stats()
        
        return {
            "total_clients": total_clients,
            "connected_clients": connected_clients,
            "client_stats": client_stats,
        }
    
    async def shutdown(self) -> None:
        """Shutdown all clients in the pool."""
        for client in self.clients.values():
            try:
                await client.disconnect()
            except Exception as e:
                self.log_error("Error disconnecting client", error=str(e))
        
        self.clients.clear()
        self.log_event("Client pool shutdown complete")


# Global client pool instance
telegram_client_pool = TelegramClientPool()
