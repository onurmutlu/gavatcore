"""
Redis State Management
=====================

Async Redis operations for state management and caching.
"""

import aioredis
import json
import asyncio
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from .config import get_settings
from .logger import LoggerMixin


class RedisStateManager(LoggerMixin):
    """Async Redis state manager for application state and caching."""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis: Optional[aioredis.Redis] = None
        self._connection_pool: Optional[aioredis.ConnectionPool] = None
    
    async def connect(self) -> None:
        """Establish Redis connection."""
        try:
            self._connection_pool = aioredis.ConnectionPool.from_url(
                self.settings.redis_url,
                password=self.settings.redis_password,
                db=self.settings.redis_db,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
                retry_on_timeout=True,
            )
            
            self.redis = aioredis.Redis(connection_pool=self._connection_pool)
            
            # Test connection
            await self.redis.ping()
            self.log_event("Redis connection established", url=self.settings.redis_url)
            
        except Exception as e:
            self.log_error("Failed to connect to Redis", error=str(e))
            raise
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            self.log_event("Redis connection closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get Redis connection context manager."""
        if not self.redis:
            await self.connect()
        
        try:
            yield self.redis
        except Exception as e:
            self.log_error("Redis operation failed", error=str(e))
            raise
    
    # Basic Operations
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a key-value pair with optional expiration."""
        async with self.get_connection() as redis:
            serialized_value = json.dumps(value) if not isinstance(value, str) else value
            result = await redis.set(key, serialized_value, ex=expire)
            
            self.log_debug("Redis SET operation", key=key, expire=expire)
            return result
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value by key with optional default."""
        async with self.get_connection() as redis:
            value = await redis.get(key)
            
            if value is None:
                return default
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
    
    async def delete(self, *keys: str) -> int:
        """Delete one or more keys."""
        async with self.get_connection() as redis:
            result = await redis.delete(*keys)
            self.log_debug("Redis DELETE operation", keys=keys, deleted=result)
            return result
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        async with self.get_connection() as redis:
            return bool(await redis.exists(key))
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for a key."""
        async with self.get_connection() as redis:
            return await redis.expire(key, seconds)
    
    # Hash Operations
    async def hset(self, name: str, mapping: Dict[str, Any]) -> int:
        """Set hash fields."""
        async with self.get_connection() as redis:
            serialized_mapping = {
                k: json.dumps(v) if not isinstance(v, str) else v
                for k, v in mapping.items()
            }
            return await redis.hset(name, mapping=serialized_mapping)
    
    async def hget(self, name: str, key: str, default: Any = None) -> Any:
        """Get hash field value."""
        async with self.get_connection() as redis:
            value = await redis.hget(name, key)
            
            if value is None:
                return default
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
    
    async def hgetall(self, name: str) -> Dict[str, Any]:
        """Get all hash fields."""
        async with self.get_connection() as redis:
            data = await redis.hgetall(name)
            
            result = {}
            for k, v in data.items():
                try:
                    result[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    result[k] = v
                    
            return result
    
    async def hdel(self, name: str, *keys: str) -> int:
        """Delete hash fields."""
        async with self.get_connection() as redis:
            return await redis.hdel(name, *keys)
    
    # List Operations
    async def lpush(self, name: str, *values: Any) -> int:
        """Push values to the left of a list."""
        async with self.get_connection() as redis:
            serialized_values = [
                json.dumps(v) if not isinstance(v, str) else v
                for v in values
            ]
            return await redis.lpush(name, *serialized_values)
    
    async def rpush(self, name: str, *values: Any) -> int:
        """Push values to the right of a list."""
        async with self.get_connection() as redis:
            serialized_values = [
                json.dumps(v) if not isinstance(v, str) else v
                for v in values
            ]
            return await redis.rpush(name, *serialized_values)
    
    async def lpop(self, name: str) -> Any:
        """Pop value from the left of a list."""
        async with self.get_connection() as redis:
            value = await redis.lpop(name)
            
            if value is None:
                return None
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
    
    async def lrange(self, name: str, start: int = 0, end: int = -1) -> List[Any]:
        """Get range of list values."""
        async with self.get_connection() as redis:
            values = await redis.lrange(name, start, end)
            
            result = []
            for v in values:
                try:
                    result.append(json.loads(v))
                except (json.JSONDecodeError, TypeError):
                    result.append(v)
                    
            return result
    
    async def llen(self, name: str) -> int:
        """Get list length."""
        async with self.get_connection() as redis:
            return await redis.llen(name)
    
    # Set Operations
    async def sadd(self, name: str, *values: Any) -> int:
        """Add values to a set."""
        async with self.get_connection() as redis:
            serialized_values = [
                json.dumps(v) if not isinstance(v, str) else v
                for v in values
            ]
            return await redis.sadd(name, *serialized_values)
    
    async def srem(self, name: str, *values: Any) -> int:
        """Remove values from a set."""
        async with self.get_connection() as redis:
            serialized_values = [
                json.dumps(v) if not isinstance(v, str) else v
                for v in values
            ]
            return await redis.srem(name, *serialized_values)
    
    async def smembers(self, name: str) -> set:
        """Get all set members."""
        async with self.get_connection() as redis:
            values = await redis.smembers(name)
            
            result = set()
            for v in values:
                try:
                    result.add(json.loads(v))
                except (json.JSONDecodeError, TypeError):
                    result.add(v)
                    
            return result
    
    async def sismember(self, name: str, value: Any) -> bool:
        """Check if value is in set."""
        async with self.get_connection() as redis:
            serialized_value = json.dumps(value) if not isinstance(value, str) else value
            return await redis.sismember(name, serialized_value)
    
    # Application-specific methods
    async def get_bot_state(self, bot_id: str) -> Dict[str, Any]:
        """Get bot state from Redis."""
        state = await self.hgetall(f"bot_state:{bot_id}")
        return state or {}
    
    async def set_bot_state(self, bot_id: str, state: Dict[str, Any]) -> None:
        """Set bot state in Redis."""
        await self.hset(f"bot_state:{bot_id}", state)
        await self.expire(f"bot_state:{bot_id}", 86400)  # 24 hours
    
    async def get_message_queue(self, queue_name: str) -> List[Dict[str, Any]]:
        """Get messages from queue."""
        return await self.lrange(f"queue:{queue_name}")
    
    async def add_to_message_queue(self, queue_name: str, message: Dict[str, Any]) -> None:
        """Add message to queue."""
        await self.rpush(f"queue:{queue_name}", message)
    
    async def pop_from_message_queue(self, queue_name: str) -> Optional[Dict[str, Any]]:
        """Pop message from queue."""
        return await self.lpop(f"queue:{queue_name}")
    
    async def set_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Set rate limit counter."""
        current = await self.get(f"rate_limit:{key}", 0)
        
        if current >= limit:
            return False
        
        await self.set(f"rate_limit:{key}", current + 1, window)
        return True
    
    async def get_active_sessions(self) -> set:
        """Get active bot sessions."""
        return await self.smembers("active_sessions")
    
    async def add_active_session(self, session_id: str) -> None:
        """Add active session."""
        await self.sadd("active_sessions", session_id)
    
    async def remove_active_session(self, session_id: str) -> None:
        """Remove active session."""
        await self.srem("active_sessions", session_id)


# Global Redis state manager instance
redis_state = RedisStateManager() 