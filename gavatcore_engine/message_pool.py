"""
Message Pool Management System
=============================

Advanced message queuing and management system with Redis backend,
priority handling, and comprehensive lifecycle management.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any, Callable, Awaitable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

from .config import get_settings
from .logger import LoggerMixin
from .redis_state import redis_state


class MessageStatus(str, Enum):
    """Message processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessagePriority(str, Enum):
    """Message priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class MessageType(str, Enum):
    """Message types."""
    DIRECT_MESSAGE = "dm"
    GROUP_MESSAGE = "group"
    BROADCAST = "broadcast"
    SCHEDULED = "scheduled"


@dataclass
class Message:
    """Message data structure."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.DIRECT_MESSAGE
    priority: MessagePriority = MessagePriority.NORMAL
    status: MessageStatus = MessageStatus.PENDING
    
    # Content
    content: str = ""
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    
    # Targeting
    target_chat_id: Optional[int] = None
    target_username: Optional[str] = None
    target_group_id: Optional[int] = None
    
    # Bot context
    bot_id: str = ""
    bot_username: Optional[str] = None
    
    # Scheduling
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    attempts: int = 0
    max_attempts: int = 3
    
    # Context data
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "content": self.content,
            "media_url": self.media_url,
            "media_type": self.media_type,
            "target_chat_id": self.target_chat_id,
            "target_username": self.target_username,
            "target_group_id": self.target_group_id,
            "bot_id": self.bot_id,
            "bot_username": self.bot_username,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "context": self.context,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        message = cls(
            id=data["id"],
            type=MessageType(data["type"]),
            priority=MessagePriority(data["priority"]),
            status=MessageStatus(data["status"]),
            content=data["content"],
            media_url=data.get("media_url"),
            media_type=data.get("media_type"),
            target_chat_id=data.get("target_chat_id"),
            target_username=data.get("target_username"),
            target_group_id=data.get("target_group_id"),
            bot_id=data["bot_id"],
            bot_username=data.get("bot_username"),
            attempts=data.get("attempts", 0),
            max_attempts=data.get("max_attempts", 3),
            context=data.get("context", {}),
        )
        
        if data.get("scheduled_at"):
            message.scheduled_at = datetime.fromisoformat(data["scheduled_at"])
        if data.get("expires_at"):
            message.expires_at = datetime.fromisoformat(data["expires_at"])
        if data.get("created_at"):
            message.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            message.updated_at = datetime.fromisoformat(data["updated_at"])
        
        return message


class MessagePool(LoggerMixin):
    """Async message pool for managing message queues."""
    
    def __init__(self):
        self.redis = redis_state
        self.processing_messages: Dict[str, Message] = {}
        self.message_handlers: Dict[MessageType, List[Callable]] = {
            MessageType.DIRECT_MESSAGE: [],
            MessageType.GROUP_MESSAGE: [],
            MessageType.BROADCAST: [],
            MessageType.SCHEDULED: [],
        }
    
    async def initialize(self) -> None:
        """Initialize message pool."""
        await self.redis.connect()
        self.log_event("Message pool initialized")
    
    async def shutdown(self) -> None:
        """Shutdown message pool."""
        # Cancel all processing messages
        for message_id in list(self.processing_messages.keys()):
            await self.cancel_message(message_id)
        
        await self.redis.disconnect()
        self.log_event("Message pool shutdown")
    
    # Message Management
    async def add_message(self, message: Message) -> str:
        """Add message to pool."""
        message.updated_at = datetime.utcnow()
        
        # Store message data
        await self.redis.hset(
            f"message:{message.id}",
            message.to_dict()
        )
        
        # Add to appropriate queue based on priority
        queue_name = f"queue:{message.priority.value}"
        await self.redis.add_to_message_queue(queue_name, {"message_id": message.id})
        
        # Add to scheduled queue if needed
        if message.scheduled_at and message.scheduled_at > datetime.utcnow():
            await self.redis.sadd("scheduled_messages", message.id)
        
        self.log_event(
            "Message added to pool",
            message_id=message.id,
            type=message.type.value,
            priority=message.priority.value,
        )
        
        return message.id
    
    async def get_message(self, message_id: str) -> Optional[Message]:
        """Get message by ID."""
        data = await self.redis.hgetall(f"message:{message_id}")
        
        if not data:
            return None
        
        return Message.from_dict(data)
    
    async def update_message(self, message: Message) -> None:
        """Update message in pool."""
        message.updated_at = datetime.utcnow()
        
        await self.redis.hset(
            f"message:{message.id}",
            message.to_dict()
        )
        
        self.log_debug("Message updated", message_id=message.id)
    
    async def delete_message(self, message_id: str) -> bool:
        """Delete message from pool."""
        # Remove from Redis
        deleted = await self.redis.delete(f"message:{message_id}")
        
        # Remove from processing if exists
        if message_id in self.processing_messages:
            del self.processing_messages[message_id]
        
        # Remove from scheduled messages
        await self.redis.srem("scheduled_messages", message_id)
        
        self.log_debug("Message deleted", message_id=message_id)
        return bool(deleted)
    
    # Queue Operations
    async def get_next_message(self, priority: Optional[MessagePriority] = None) -> Optional[Message]:
        """Get next message from queue."""
        # Priority order: urgent -> high -> normal -> low
        priorities = [MessagePriority.URGENT, MessagePriority.HIGH, MessagePriority.NORMAL, MessagePriority.LOW]
        
        if priority:
            priorities = [priority]
        
        for prio in priorities:
            queue_name = f"queue:{prio.value}"
            message_data = await self.redis.pop_from_message_queue(queue_name)
            
            if message_data:
                message_id = message_data["message_id"]
                message = await self.get_message(message_id)
                
                if message and message.status == MessageStatus.PENDING:
                    # Check if message is expired
                    if message.expires_at and message.expires_at < datetime.utcnow():
                        await self.cancel_message(message_id)
                        continue
                    
                    # Mark as processing
                    message.status = MessageStatus.PROCESSING
                    await self.update_message(message)
                    
                    self.processing_messages[message_id] = message
                    
                    self.log_debug("Message retrieved from queue", message_id=message_id)
                    return message
        
        return None
    
    async def get_scheduled_messages(self) -> List[Message]:
        """Get messages ready for scheduling."""
        scheduled_ids = await self.redis.smembers("scheduled_messages")
        ready_messages = []
        
        for message_id in scheduled_ids:
            message = await self.get_message(message_id)
            
            if not message:
                await self.redis.srem("scheduled_messages", message_id)
                continue
            
            # Check if message is ready to be sent
            if (message.scheduled_at and 
                message.scheduled_at <= datetime.utcnow() and 
                message.status == MessageStatus.PENDING):
                
                ready_messages.append(message)
        
        return ready_messages
    
    async def complete_message(self, message_id: str) -> bool:
        """Mark message as completed."""
        message = await self.get_message(message_id)
        
        if not message:
            return False
        
        message.status = MessageStatus.COMPLETED
        await self.update_message(message)
        
        # Remove from processing
        if message_id in self.processing_messages:
            del self.processing_messages[message_id]
        
        # Remove from scheduled if exists
        await self.redis.srem("scheduled_messages", message_id)
        
        self.log_event("Message completed", message_id=message_id)
        return True
    
    async def fail_message(self, message_id: str, error: str = "") -> bool:
        """Mark message as failed."""
        message = await self.get_message(message_id)
        
        if not message:
            return False
        
        message.attempts += 1
        
        # Check if we should retry
        if message.attempts < message.max_attempts:
            message.status = MessageStatus.PENDING
            message.context["last_error"] = error
            await self.update_message(message)
            
            # Re-add to queue with lower priority
            queue_name = f"queue:{MessagePriority.LOW.value}"
            await self.redis.add_to_message_queue(queue_name, {"message_id": message_id})
            
            self.log_warning(
                "Message failed, retrying",
                message_id=message_id,
                attempt=message.attempts,
                error=error,
            )
        else:
            message.status = MessageStatus.FAILED
            message.context["final_error"] = error
            await self.update_message(message)
            
            self.log_error(
                "Message failed permanently",
                message_id=message_id,
                attempts=message.attempts,
                error=error,
            )
        
        # Remove from processing
        if message_id in self.processing_messages:
            del self.processing_messages[message_id]
        
        return True
    
    async def cancel_message(self, message_id: str) -> bool:
        """Cancel message processing."""
        message = await self.get_message(message_id)
        
        if not message:
            return False
        
        message.status = MessageStatus.CANCELLED
        await self.update_message(message)
        
        # Remove from processing
        if message_id in self.processing_messages:
            del self.processing_messages[message_id]
        
        # Remove from scheduled
        await self.redis.srem("scheduled_messages", message_id)
        
        self.log_event("Message cancelled", message_id=message_id)
        return True
    
    # Statistics and Monitoring
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        stats = {}
        
        for priority in MessagePriority:
            queue_name = f"queue:{priority.value}"
            stats[priority.value] = await self.redis.llen(queue_name)
        
        stats["processing"] = len(self.processing_messages)
        stats["scheduled"] = len(await self.redis.smembers("scheduled_messages"))
        
        return stats
    
    async def get_message_stats(self) -> Dict[str, int]:
        """Get message statistics by status."""
        # This would require scanning all messages, which might be expensive
        # For production, consider maintaining counters in Redis
        return {
            "pending": 0,  # Would need to implement proper counting
            "processing": len(self.processing_messages),
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
        }
    
    # Message Handlers
    def register_handler(self, message_type: MessageType, handler: Callable[[Message], Awaitable[bool]]) -> None:
        """Register message handler for specific type."""
        self.message_handlers[message_type].append(handler)
        self.log_event("Message handler registered", type=message_type.value)
    
    async def process_message(self, message: Message) -> bool:
        """Process message using registered handlers."""
        handlers = self.message_handlers.get(message.type, [])
        
        if not handlers:
            self.log_warning("No handlers registered for message type", type=message.type.value)
            return False
        
        for handler in handlers:
            try:
                success = await handler(message)
                if success:
                    return True
            except Exception as e:
                self.log_error(
                    "Message handler failed",
                    message_id=message.id,
                    handler=handler.__name__,
                    error=str(e),
                )
        
        return False


# Global message pool instance
message_pool = MessagePool() 