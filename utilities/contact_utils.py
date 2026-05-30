from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
# contact_utils.py
"""
🔥 GavatCore Contact Management Utils 🔥

Production-grade contact management for Telegram bots with:
- Redis session management (TTL-based)
- MongoDB failure logging
- Async contact.addContact integration
- Comprehensive error handling
- Type safety ve performance optimizations

Architecture Integration:
- Telethon (Telegram Bot) ◄─► Redis (Session Cache) ◄─► MongoDB (Failure Logs)

Enhanced Features:
- Comprehensive type annotations
- Structured error handling with context
- Performance monitoring ve metrics
- Configurable retry strategies
- Graceful degradation support
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List, Union, Protocol
from dataclasses import dataclass, field
from enum import Enum
import contextlib
import structlog
import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient
from telethon import TelegramClient
from telethon.tl.functions.contacts import AddContactRequest
from telethon.tl.types import User, InputUser
from telethon.errors import (
    FloodWaitError, 
    UserPrivacyRestrictedError,
    RPCError
)

# Configure structured logging
logger = structlog.get_logger("gavatcore.contact_utils")

# Type definitions
ContactResult = Tuple[bool, str, Optional[str]]
SessionData = Dict[str, Any]
AnalyticsData = Dict[str, Union[str, int, float, List, Dict]]

class ContactError(Enum):
    """Contact addition error types."""
    VALIDATION_ERROR = "validation_error"
    ACCESS_HASH_ERROR = "access_hash_error"
    FLOOD_WAIT = "flood_wait"
    PRIVACY_RESTRICTED = "privacy_restricted"
    RPC_ERROR = "rpc_error"
    UNEXPECTED_ERROR = "unexpected_error"
    CONNECTION_ERROR = "connection_error"
    TIMEOUT_ERROR = "timeout_error"

class ContactStatus(Enum):
    """Contact operation status."""
    INITIATED = "initiated"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class ContactAttempt:
    """Contact addition attempt information."""
    user_id: int
    bot_username: str
    attempt_number: int
    timestamp: datetime = field(default_factory=datetime.now)
    error_type: Optional[ContactError] = None
    error_message: Optional[str] = None
    success: bool = False
    response_time_ms: float = 0.0

@dataclass
class ContactManagerConfig:
    """Configuration for ContactManager."""
    redis_url: str = "redis://localhost:6379"
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "gavatcore"
    session_ttl: int = 3600  # 1 hour
    retry_delay: float = 2.0
    max_retries: int = 3
    connection_timeout: int = 10
    operation_timeout: int = 30

class DatabaseProtocol(Protocol):
    """Protocol for database operations."""
    async def ping(self) -> None: ...
    async def close(self) -> None: ...

class ContactManager:
    """
    🚀 GavatCore Contact Management System
    
    Enhanced contact management with comprehensive error handling,
    performance monitoring, and graceful degradation.
    """
    
    def __init__(self, config: Optional[ContactManagerConfig] = None):
        self.config = config or ContactManagerConfig()
        self._redis_client: Optional[redis.Redis] = None
        self._mongo_client: Optional[AsyncIOMotorClient] = None
        self._mongo_db: Optional[Any] = None
        self._initialized = False
        self._performance_metrics: Dict[str, Any] = {
            "total_attempts": 0,
            "successful_attempts": 0,
            "failed_attempts": 0,
            "avg_response_time_ms": 0.0,
            "error_counts": {error.value: 0 for error in ContactError}
        }
        
        logger.info("🔧 ContactManager initialized", 
                   redis_url=self.config.redis_url, 
                   mongodb_url=self.config.mongodb_url)
    
    @contextlib.asynccontextmanager
    async def _operation_timer(self, operation: str):
        """Context manager for timing operations."""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.debug("⏱️ Operation timing", 
                        operation=operation, 
                        duration_ms=duration_ms)
    
    async def initialize(self) -> bool:
        """
        Initialize Redis and MongoDB connections with comprehensive error handling.
        
        Returns:
            bool: True if at least one connection successful, False if all failed
        """
        redis_success = await self._initialize_redis()
        mongo_success = await self._initialize_mongodb()
        
        # System can work with partial functionality
        self._initialized = redis_success or mongo_success
        
        if self._initialized:
            logger.info("✅ ContactManager initialized", 
                       redis=redis_success, 
                       mongodb=mongo_success)
        else:
            logger.error("❌ ContactManager initialization failed - no databases available")
        
        return self._initialized
    
    async def _initialize_redis(self) -> bool:
        """Initialize Redis connection."""
        try:
            self._redis_client = redis.from_url(
                self.config.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=self.config.connection_timeout,
                socket_timeout=self.config.operation_timeout,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            await asyncio.wait_for(
                self._redis_client.ping(), 
                timeout=self.config.connection_timeout
            )
            
            logger.info("✅ Redis connection established")
            return True
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Redis connection timeout")
            self._redis_client = None
            return False
        except Exception as e:
            logger.warning("⚠️ Redis connection failed", error=str(e))
            self._redis_client = None
            return False
    
    async def _initialize_mongodb(self) -> bool:
        """Initialize MongoDB connection."""
        try:
            self._mongo_client = AsyncIOMotorClient(
                self.config.mongodb_url,
                serverSelectionTimeoutMS=self.config.connection_timeout * 1000,
                connectTimeoutMS=self.config.connection_timeout * 1000,
                socketTimeoutMS=self.config.operation_timeout * 1000
            )
            
            # Test connection
            self._mongo_db = self._mongo_client[self.config.database_name]
            await asyncio.wait_for(
                self._mongo_db.command("ping"), 
                timeout=self.config.connection_timeout
            )
            
            logger.info("✅ MongoDB connection established")
            return True
            
        except asyncio.TimeoutError:
            logger.warning("⏰ MongoDB connection timeout")
            self._mongo_client = None
            self._mongo_db = None
            return False
        except Exception as e:
            logger.warning("⚠️ MongoDB connection failed", error=str(e))
            self._mongo_client = None
            self._mongo_db = None
            return False
    
    async def close(self) -> None:
        """Close all connections gracefully."""
        async with self._operation_timer("cleanup"):
            tasks = []
            
            if self._redis_client:
                tasks.append(self._safe_close(self._redis_client, "Redis"))
                
            if self._mongo_client:
                tasks.append(self._safe_close(self._mongo_client, "MongoDB"))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _safe_close(self, client: DatabaseProtocol, name: str) -> None:
        """Safely close a database client."""
        try:
            if name == "MongoDB":
                # MongoDB client uses sync close()
                client.close()
            else:
                # Redis uses async close()
                await client.close()
            logger.info(f"🔌 {name} connection closed")
        except Exception as e:
            logger.warning(f"⚠️ {name} close error", error=str(e))
    
    def _create_session_key(self, user_id: int, bot_username: str) -> str:
        """Generate Redis session key."""
        return f"gavatcore:contact_session:{bot_username}:{user_id}"
    
    async def set_user_session(
        self, 
        user_id: int, 
        bot_username: str, 
        session_data: SessionData
    ) -> bool:
        """
        Store user session in Redis with TTL and error handling.
        
        Returns:
            bool: True if stored successfully, False otherwise
        """
        if not self._redis_client:
            logger.debug("⚠️ Redis not available for session storage")
            return False
        
        try:
            async with self._operation_timer("set_session"):
                session_key = self._create_session_key(user_id, bot_username)
                session_json = json.dumps({
                    **session_data,
                    "created_at": datetime.now().isoformat(),
                    "ttl": self.config.session_ttl
                })
                
                # Set with TTL
                await self._redis_client.setex(
                    session_key, 
                    self.config.session_ttl, 
                    session_json
                )
                
                logger.debug("📝 Session stored in Redis", 
                           user_id=user_id, 
                           bot=bot_username, 
                           ttl=self.config.session_ttl)
                return True
                
        except Exception as e:
            logger.error("❌ Failed to store session", 
                        error=str(e), 
                        user_id=user_id,
                        bot=bot_username)
            return False
    
    async def get_user_session(
        self, 
        user_id: int, 
        bot_username: str
    ) -> Optional[SessionData]:
        """
        Retrieve user session from Redis.
        
        Returns:
            Optional[SessionData]: Session data if found, None otherwise
        """
        if not self._redis_client:
            return None
        
        try:
            async with self._operation_timer("get_session"):
                session_key = self._create_session_key(user_id, bot_username)
                session_json = await self._redis_client.get(session_key)
                
                if session_json:
                    return json.loads(session_json)
                return None
                
        except Exception as e:
            logger.error("❌ Failed to retrieve session", 
                        error=str(e), 
                        user_id=user_id,
                        bot=bot_username)
            return None
    
    async def log_contact_failure(
        self,
        attempt: ContactAttempt,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log contact addition failure to MongoDB with structured data.
        
        Returns:
            bool: True if logged successfully, False otherwise
        """
        if not self._mongo_db:
            logger.debug("⚠️ MongoDB not available for failure logging")
            return False
        
        try:
            async with self._operation_timer("log_failure"):
                failure_document = {
                    "user_id": attempt.user_id,
                    "bot_username": attempt.bot_username,
                    "attempt_number": attempt.attempt_number,
                    "error_type": attempt.error_type.value if attempt.error_type else "unknown",
                    "error_message": attempt.error_message or "",
                    "timestamp": attempt.timestamp,
                    "response_time_ms": attempt.response_time_ms,
                    "additional_data": additional_data or {},
                    "system_info": {
                        "component": "contact_utils",
                        "version": "2.0.0",
                        "environment": "production"
                    }
                }
                
                collection = self._mongo_db["contact_failures"]
                result = await collection.insert_one(failure_document)
                
                # Update metrics
                if attempt.error_type:
                    self._performance_metrics["error_counts"][attempt.error_type.value] += 1
                
                logger.info("📊 Contact failure logged",
                           user_id=attempt.user_id,
                           bot=attempt.bot_username,
                           error_type=attempt.error_type.value if attempt.error_type else "unknown",
                           document_id=str(result.inserted_id))
                return True
                
        except Exception as e:
            logger.error("❌ Failed to log contact failure", 
                        error=str(e),
                        user_id=attempt.user_id)
            return False
    
    async def attempt_contact_addition(
        self, 
        bot: TelegramClient, 
        user: User
    ) -> ContactResult:
        """
        Attempt to add contact via Telegram API with comprehensive error handling.
        
        Returns:
            ContactResult: Tuple of (success, message, error_type)
        """
        start_time = time.perf_counter()
        
        try:
            # Validate user object
            if not self._validate_user(user):
                return False, "Invalid user object", ContactError.VALIDATION_ERROR.value
            
            # Create InputUser
            input_user = InputUser(user_id=user.id, access_hash=user.access_hash)
            
            # Attempt contact addition with timeout
            result = await asyncio.wait_for(
                bot(AddContactRequest(
                    id=input_user,
                    first_name=user.first_name or "Friend",
                    last_name=user.last_name or "",
                    phone="",  # Empty phone - use Telegram ID
                    add_phone_privacy_exception=False
                )),
                timeout=self.config.operation_timeout
            )
            
            response_time_ms = (time.perf_counter() - start_time) * 1000
            
            # Update metrics
            self._performance_metrics["total_attempts"] += 1
            self._performance_metrics["successful_attempts"] += 1
            self._update_avg_response_time(response_time_ms)
            
            logger.info("✅ Contact addition successful",
                       user_id=user.id,
                       user_name=user.first_name or "Unknown",
                       response_time_ms=response_time_ms)
            
            return True, "✅ Ekledim, DM başlatabilirsin", None
            
        except asyncio.TimeoutError:
            self._performance_metrics["total_attempts"] += 1
            self._performance_metrics["failed_attempts"] += 1
            logger.warning("⏰ Contact addition timeout", user_id=user.id)
            return False, "Seni ekleyemedim, bana DM atmaya çalış", ContactError.TIMEOUT_ERROR.value
            
        except FloodWaitError as e:
            response_time_ms = (time.perf_counter() - start_time) * 1000
            self._performance_metrics["total_attempts"] += 1
            self._performance_metrics["failed_attempts"] += 1
            self._update_avg_response_time(response_time_ms)
            
            logger.warning("⏰ FloodWait error", 
                          seconds=e.seconds, 
                          user_id=user.id,
                          response_time_ms=response_time_ms)
            return False, "Seni ekleyemedim, bana DM atmaya çalış", ContactError.FLOOD_WAIT.value
            
        except UserPrivacyRestrictedError:
            response_time_ms = (time.perf_counter() - start_time) * 1000
            self._performance_metrics["total_attempts"] += 1
            self._performance_metrics["failed_attempts"] += 1
            self._update_avg_response_time(response_time_ms)
            
            logger.warning("🔒 User privacy restricted", 
                          user_id=user.id,
                          response_time_ms=response_time_ms)
            return False, "Seni ekleyemedim, bana DM atmaya çalış", ContactError.PRIVACY_RESTRICTED.value
            
        except RPCError as e:
            response_time_ms = (time.perf_counter() - start_time) * 1000
            self._performance_metrics["total_attempts"] += 1
            self._performance_metrics["failed_attempts"] += 1
            self._update_avg_response_time(response_time_ms)
            
            logger.error("🔌 RPC error during contact addition", 
                        error=str(e), 
                        user_id=user.id,
                        response_time_ms=response_time_ms)
            return False, "Seni ekleyemedim, bana DM atmaya çalış", ContactError.RPC_ERROR.value
            
        except Exception as e:
            response_time_ms = (time.perf_counter() - start_time) * 1000
            self._performance_metrics["total_attempts"] += 1
            self._performance_metrics["failed_attempts"] += 1
            self._update_avg_response_time(response_time_ms)
            
            logger.error("💥 Unexpected error during contact addition", 
                        error=str(e), 
                        user_id=user.id,
                        response_time_ms=response_time_ms)
            return False, "Seni ekleyemedim, bana DM atmaya çalış", ContactError.UNEXPECTED_ERROR.value
    
    def _validate_user(self, user: User) -> bool:
        """Validate user object for contact addition."""
        if not user or not hasattr(user, 'id') or not user.id:
            logger.warning("⚠️ Invalid user: missing ID")
            return False
        
        if not hasattr(user, 'access_hash') or user.access_hash is None:
            logger.warning("⚠️ Invalid user: missing access_hash", user_id=user.id)
            return False
        
        return True
    
    def _update_avg_response_time(self, response_time_ms: float) -> None:
        """Update average response time metric."""
        current_avg = self._performance_metrics["avg_response_time_ms"]
        total_attempts = self._performance_metrics["total_attempts"]
        
        if total_attempts <= 1:
            self._performance_metrics["avg_response_time_ms"] = response_time_ms
        else:
            # Calculate new average
            new_avg = ((current_avg * (total_attempts - 1)) + response_time_ms) / total_attempts
            self._performance_metrics["avg_response_time_ms"] = new_avg
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            **self._performance_metrics,
            "success_rate": (
                self._performance_metrics["successful_attempts"] / 
                max(self._performance_metrics["total_attempts"], 1)
            ),
            "timestamp": datetime.now().isoformat()
        }

# 🚀 Main function - yazılım tarihine geçecek fonksiyon
async def add_contact_with_fallback(bot: TelegramClient, user: User) -> str:
    """
    🔥 GavatCore Contact Addition with Redis Session & MongoDB Logging
    
    Bu fonksiyon yazılım tarihine geçecek! 🚀
    
    Architecture Flow:
    1. Redis session creation (TTL: 3600s)
    2. Telegram contacts.addContact attempt
    3. Success: Return positive message
    4. Failure: Log to MongoDB + return fallback message
    
    Args:
        bot: TelegramClient instance
        user: Telegram User object
        
    Returns:
        str: Success or fallback message
        
    Example:
        >>> message = await add_contact_with_fallback(bot, user)
        >>> print(message)  # "✅ Ekledim, DM başlatabilirsin"
    """
    
    # Initialize contact manager
    contact_manager = ContactManager()
    
    try:
        # Initialize connections
        if not await contact_manager.initialize():
            logger.error("❌ Failed to initialize ContactManager")
            return "Seni ekleyemedim, bana DM atmaya çalış"
        
        # Get bot info
        bot_me = await bot.get_me()
        bot_username = bot_me.username or f"bot_{bot_me.id}"
        
        # Create Redis session
        session_data = {
            "user_id": user.id,
            "user_first_name": user.first_name or "Unknown",
            "user_last_name": user.last_name or "",
            "user_username": user.username or "",
            "bot_username": bot_username,
            "contact_attempt": True,
            "status": "initiated"
        }
        
        session_stored = await contact_manager.set_user_session(
            user.id, 
            bot_username, 
            session_data
        )
        
        if not session_stored:
            logger.warning("⚠️ Failed to store session, proceeding anyway")
        
        # Attempt contact addition with retries
        for attempt in range(contact_manager.config.max_retries):
            try:
                success, message, error_type = await contact_manager.attempt_contact_addition(bot, user)
                
                if success:
                    # Update session on success
                    if session_stored:
                        session_data["status"] = "success"
                        session_data["completed_at"] = datetime.now().isoformat()
                        await contact_manager.set_user_session(user.id, bot_username, session_data)
                    
                    logger.info(
                        "🎉 Contact addition successful",
                        user_id=user.id,
                        bot=bot_username,
                        attempt=attempt + 1
                    )
                    return message
                
                # Log failure
                await contact_manager.log_contact_failure(
                    ContactAttempt(
                        user_id=user.id,
                        bot_username=bot_username,
                        attempt_number=attempt + 1,
                        error_type=error_type,
                        error_message=message
                    ),
                    additional_data={
                        "attempt": attempt + 1,
                        "max_retries": contact_manager.config.max_retries,
                        "user_data": {
                            "first_name": user.first_name,
                            "username": user.username,
                            "has_access_hash": hasattr(user, 'access_hash') and user.access_hash is not None
                        }
                    }
                )
                
                # If this was the last attempt, return failure message
                if attempt == contact_manager.config.max_retries - 1:
                    # Update session on final failure
                    if session_stored:
                        session_data["status"] = "failed"
                        session_data["error_type"] = error_type
                        session_data["failed_at"] = datetime.now().isoformat()
                        await contact_manager.set_user_session(user.id, bot_username, session_data)
                    
                    logger.error(
                        "💥 Contact addition failed after all retries",
                        user_id=user.id,
                        bot=bot_username,
                        total_attempts=contact_manager.config.max_retries
                    )
                    return message
                
                # Wait before retry (exponential backoff)
                wait_time = contact_manager.config.retry_delay * (2 ** attempt)
                logger.info(f"🔄 Retrying in {wait_time}s", attempt=attempt + 1)
                await asyncio.sleep(wait_time)
                
            except Exception as retry_error:
                logger.error(
                    "❌ Error during retry attempt",
                    error=str(retry_error),
                    attempt=attempt + 1
                )
                
                if attempt == contact_manager.config.max_retries - 1:
                    await contact_manager.log_contact_failure(
                        ContactAttempt(
                            user_id=user.id,
                            bot_username=bot_username,
                            attempt_number=attempt + 1,
                            error_type="retry_exception",
                            error_message=str(retry_error)
                        ),
                        additional_data={"final_attempt": True}
                    )
                    return "Seni ekleyemedim, bana DM atmaya çalış"
        
        return "Seni ekleyemedim, bana DM atmaya çalış"
        
    except Exception as e:
        logger.error("💥 Critical error in add_contact_with_fallback", error=str(e))
        
        # Emergency logging
        try:
            await contact_manager.log_contact_failure(
                ContactAttempt(
                    user_id=getattr(user, 'id', 0),
                    bot_username=getattr(bot_me, 'username', 'unknown') if 'bot_me' in locals() else 'unknown',
                    attempt_number=0,
                    error_type="critical_error",
                    error_message=str(e),
                    success=False
                ),
                additional_data={"emergency_log": True}
            )
        except:
            pass  # Silent fail for emergency logging
        
        return "Seni ekleyemedim, bana DM atmaya çalış"
        
    finally:
        # Cleanup
        await contact_manager.close()


# 🧪 Test Utilities (Production-Ready)
async def test_contact_system() -> bool:
    """Test the contact management system"""
    try:
        manager = ContactManager()
        
        if not await manager.initialize():
            logger.error("❌ Test failed: Could not initialize")
            return False
        
        # Test Redis
        test_key = "gavatcore:test:connection"
        await manager._redis_client.setex(test_key, 60, "test_value")
        result = await manager._redis_client.get(test_key)
        
        if result != "test_value":
            logger.error("❌ Redis test failed")
            return False
        
        await manager._redis_client.delete(test_key)
        
        # Test MongoDB
        test_doc = {"test": True, "timestamp": datetime.now()}
        collection = manager._mongo_db["system_tests"]
        insert_result = await collection.insert_one(test_doc)
        await collection.delete_one({"_id": insert_result.inserted_id})
        
        await manager.close()
        logger.info("✅ Contact system test passed")
        return True
        
    except Exception as e:
        logger.error("❌ Test failed", error=str(e))
        return False


# 📊 Analytics Pipelines
async def get_top_error_types(limit: int = 10) -> Dict[str, Any]:
    """
    🔥 Contact Failure Analytics - Top Error Types
    
    MongoDB aggregate pipeline to find most common error types
    in contact_failures collection.
    
    Args:
        limit: Maximum number of results to return
        
    Returns:
        Dict with error analysis results
        
    Example:
        >>> results = await get_top_error_types(5)
        >>> print(results['top_errors'])
        [
            {'error_type': 'privacy_restricted', 'count': 245, 'percentage': 45.2},
            {'error_type': 'flood_wait', 'count': 156, 'percentage': 28.8},
            ...
        ]
    """
    
    contact_manager = ContactManager()
    
    try:
        if not await contact_manager.initialize():
            logger.error("❌ Failed to initialize ContactManager for analytics")
            return {"error": "Failed to initialize database connections"}
        
        collection = contact_manager._mongo_db["contact_failures"]
        
        # 🚀 MongoDB Aggregate Pipeline - Yazılım Tarihine Geçecek Analytics!
        pipeline = [
            # Stage 1: Match recent failures (last 30 days for better relevance)
            {
                "$match": {
                    "timestamp": {
                        "$gte": datetime.now() - timedelta(days=30)
                    }
                }
            },
            
            # Stage 2: Group by error_type and count occurrences
            {
                "$group": {
                    "_id": "$error_type",
                    "count": {"$sum": 1},
                    "first_occurrence": {"$min": "$timestamp"},
                    "last_occurrence": {"$max": "$timestamp"},
                    "unique_users": {"$addToSet": "$user_id"},
                    "unique_bots": {"$addToSet": "$bot_username"},
                    "sample_errors": {
                        "$push": {
                            "error_message": "$error_message",
                            "timestamp": "$timestamp",
                            "user_id": "$user_id"
                        }
                    }
                }
            },
            
            # Stage 3: Add calculated fields
            {
                "$addFields": {
                    "error_type": "$_id",
                    "unique_user_count": {"$size": "$unique_users"},
                    "unique_bot_count": {"$size": "$unique_bots"},
                    "sample_error": {"$arrayElemAt": ["$sample_errors", 0]}
                }
            },
            
            # Stage 4: Sort by count (most frequent first)
            {
                "$sort": {"count": -1}
            },
            
            # Stage 5: Limit results
            {
                "$limit": limit
            },
            
            # Stage 6: Project final structure
            {
                "$project": {
                    "_id": 0,
                    "error_type": 1,
                    "count": 1,
                    "unique_user_count": 1,
                    "unique_bot_count": 1,
                    "first_occurrence": 1,
                    "last_occurrence": 1,
                    "sample_error": {
                        "error_message": "$sample_error.error_message",
                        "timestamp": "$sample_error.timestamp"
                    }
                }
            }
        ]
        
        # Execute pipeline
        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=limit)
        
        # Calculate total for percentages
        total_failures = sum(result["count"] for result in results)
        
        # Add percentage calculations
        for result in results:
            result["percentage"] = round((result["count"] / total_failures * 100), 2) if total_failures > 0 else 0
        
        # Get overall statistics
        total_stats_pipeline = [
            {
                "$match": {
                    "timestamp": {
                        "$gte": datetime.now() - timedelta(days=30)
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_failures": {"$sum": 1},
                    "unique_users_affected": {"$addToSet": "$user_id"},
                    "unique_bots_affected": {"$addToSet": "$bot_username"},
                    "date_range": {
                        "$push": "$timestamp"
                    }
                }
            },
            {
                "$addFields": {
                    "unique_user_count": {"$size": "$unique_users_affected"},
                    "unique_bot_count": {"$size": "$unique_bots_affected"},
                    "earliest_failure": {"$min": "$date_range"},
                    "latest_failure": {"$max": "$date_range"}
                }
            }
        ]
        
        total_cursor = collection.aggregate(total_stats_pipeline)
        total_stats = await total_cursor.to_list(length=1)
        
        # Prepare response
        analytics_result = {
            "success": True,
            "generated_at": datetime.now().isoformat(),
            "analysis_period": "Last 30 days",
            "total_failures": total_stats[0]["total_failures"] if total_stats else 0,
            "unique_users_affected": total_stats[0]["unique_user_count"] if total_stats else 0,
            "unique_bots_affected": total_stats[0]["unique_bot_count"] if total_stats else 0,
            "top_errors": results,
            "summary": {
                "most_common_error": results[0]["error_type"] if results else "No errors found",
                "most_common_count": results[0]["count"] if results else 0,
                "error_type_diversity": len(results)
            }
        }
        
        logger.info(
            "📊 Error analytics completed",
            total_failures=analytics_result["total_failures"],
            top_error=analytics_result["summary"]["most_common_error"],
            unique_users=analytics_result["unique_users_affected"]
        )
        
        return analytics_result
        
    except Exception as e:
        logger.error("❌ Analytics pipeline failed", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "generated_at": datetime.now().isoformat()
        }
        
    finally:
        await contact_manager.close()


async def get_error_trends_by_day(days: int = 7) -> Dict[str, Any]:
    """
    📈 Daily Error Trends Analysis
    
    Analyze error patterns over time to identify trends and spikes.
    
    Args:
        days: Number of days to analyze
        
    Returns:
        Dict with daily error trends
    """
    
    contact_manager = ContactManager()
    
    try:
        if not await contact_manager.initialize():
            return {"error": "Failed to initialize database connections"}
        
        collection = contact_manager._mongo_db["contact_failures"]
        
        # Pipeline for daily trends
        pipeline = [
            # Match last N days
            {
                "$match": {
                    "timestamp": {
                        "$gte": datetime.now() - timedelta(days=days)
                    }
                }
            },
            
            # Group by date and error_type
            {
                "$group": {
                    "_id": {
                        "date": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$timestamp"
                            }
                        },
                        "error_type": "$error_type"
                    },
                    "count": {"$sum": 1}
                }
            },
            
            # Reshape for easier analysis
            {
                "$group": {
                    "_id": "$_id.date",
                    "errors": {
                        "$push": {
                            "error_type": "$_id.error_type",
                            "count": "$count"
                        }
                    },
                    "total_daily_errors": {"$sum": "$count"}
                }
            },
            
            # Sort by date
            {
                "$sort": {"_id": 1}
            },
            
            # Format output
            {
                "$project": {
                    "_id": 0,
                    "date": "$_id",
                    "total_errors": "$total_daily_errors",
                    "error_breakdown": "$errors"
                }
            }
        ]
        
        cursor = collection.aggregate(pipeline)
        daily_trends = await cursor.to_list(length=days)
        
        return {
            "success": True,
            "period_days": days,
            "daily_trends": daily_trends,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Trends analysis failed", error=str(e))
        return {"success": False, "error": str(e)}
        
    finally:
        await contact_manager.close()


# 🎯 Quick Analytics Function
async def quick_error_analysis() -> None:
    """
    🚀 Quick CLI analytics for contact failures
    
    Prints formatted error analysis to console.
    Perfect for monitoring and debugging.
    """
    
    print("🔥 GavatCore Contact Failure Analysis 🔥")
    print("=" * 50)
    
    # Get top errors
    results = await get_top_error_types(10)
    
    if not results.get("success", False):
        print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
        return
    
    print(f"\n📊 Analysis Period: {results['analysis_period']}")
    print(f"📈 Total Failures: {results['total_failures']}")
    print(f"👥 Unique Users Affected: {results['unique_users_affected']}")
    print(f"🤖 Unique Bots Affected: {results['unique_bots_affected']}")
    
    print(f"\n🔝 Top Error Types:")
    print("-" * 80)
    print(f"{'Rank':<4} {'Error Type':<20} {'Count':<8} {'%':<6} {'Users':<8} {'Last Seen'}")
    print("-" * 80)
    
    for i, error in enumerate(results['top_errors'], 1):
        last_seen = error['last_occurrence'].strftime("%m-%d %H:%M") if error['last_occurrence'] else "N/A"
        print(f"{i:<4} {error['error_type']:<20} {error['count']:<8} {error['percentage']:<6.1f} "
              f"{error['unique_user_count']:<8} {last_seen}")
    
    print(f"\n🎯 Most Critical: {results['summary']['most_common_error']} "
          f"({results['summary']['most_common_count']} occurrences)")


# 🧹 Session Cleanup & Maintenance Functions
async def cleanup_expired_sessions(
    redis_url: str = "redis://localhost:6379",
    mongodb_url: str = "mongodb://localhost:27017",
    database_name: str = "gavatcore",
    batch_size: int = 100,
    max_age_hours: int = 24
) -> Dict[str, Any]:
    """
    🔥 Redis Session Cleanup + MongoDB Summary Logging
    
    Bu fonksiyon yazılım tarihine geçecek! Eski session'ları temizler ve
    detaylı istatistikleri MongoDB'ye kaydeder.
    
    Features:
    - TTL expired session detection
    - Batch processing for large datasets
    - Comprehensive MongoDB logging
    - Performance metrics
    - Error resilience
    
    Args:
        redis_url: Redis connection URL
        mongodb_url: MongoDB connection URL  
        database_name: MongoDB database name
        batch_size: Sessions to process per batch
        max_age_hours: Maximum session age before cleanup
        
    Returns:
        Dict with cleanup summary and statistics
        
    Example:
        >>> result = await cleanup_expired_sessions()
        >>> print(f"Cleaned {result['sessions_deleted']} sessions")
    """
    
    start_time = datetime.now()
    cleanup_summary = {
        "start_time": start_time.isoformat(),
        "sessions_found": 0,
        "sessions_deleted": 0,
        "sessions_preserved": 0,
        "errors_encountered": 0,
        "batch_count": 0,
        "processing_time_seconds": 0,
        "redis_operations": 0,
        "mongodb_operations": 0,
        "memory_saved_mb": 0,
        "success": False
    }
    
    # Initialize connections
    redis_client = None
    mongo_client = None
    
    try:
        logger.info("🧹 Starting Redis session cleanup", max_age_hours=max_age_hours, batch_size=batch_size)
        
        # Redis connection
        redis_client = redis.from_url(
            redis_url,
            encoding="utf-8", 
            decode_responses=True,
            socket_connect_timeout=10,
            socket_timeout=10
        )
        
        # MongoDB connection
        mongo_client = AsyncIOMotorClient(
            mongodb_url,
            serverSelectionTimeoutMS=10000
        )
        mongo_db = mongo_client[database_name]
        
        # Test connections
        await redis_client.ping()
        await mongo_db.command("ping")
        
        logger.info("✅ Database connections established")
        
        # Scan for GavatCore session keys
        session_pattern = "gavatcore:contact_session:*"
        cursor = redis_client.scan_iter(match=session_pattern, count=batch_size)
        
        expired_sessions = []
        active_sessions = []
        batch_number = 0
        
        async for key in cursor:
            try:
                cleanup_summary["sessions_found"] += 1
                cleanup_summary["redis_operations"] += 1
                
                # Get session data and TTL
                session_data = await redis_client.get(key)
                ttl = await redis_client.ttl(key)
                
                if session_data is None:
                    # Key already expired/deleted
                    expired_sessions.append({
                        "key": key,
                        "reason": "key_not_found",
                        "ttl": ttl
                    })
                    continue
                
                # Parse session data
                try:
                    session_json = json.loads(session_data)
                    created_at = datetime.fromisoformat(session_json.get("created_at", start_time.isoformat()))
                    session_age_hours = (start_time - created_at).total_seconds() / 3600
                    
                    # Check if session should be cleaned
                    should_cleanup = (
                        ttl <= 0 or  # TTL expired
                        session_age_hours > max_age_hours or  # Too old
                        session_json.get("status") == "failed"  # Failed sessions
                    )
                    
                    if should_cleanup:
                        expired_sessions.append({
                            "key": key,
                            "reason": "expired" if ttl <= 0 else "old" if session_age_hours > max_age_hours else "failed",
                            "ttl": ttl,
                            "age_hours": session_age_hours,
                            "user_id": session_json.get("user_id"),
                            "bot_username": session_json.get("bot_username"),
                            "status": session_json.get("status"),
                            "created_at": session_json.get("created_at"),
                            "data_size": len(session_data)
                        })
                    else:
                        active_sessions.append({
                            "key": key,
                            "ttl": ttl,
                            "age_hours": session_age_hours,
                            "status": session_json.get("status")
                        })
                        cleanup_summary["sessions_preserved"] += 1
                
                except (json.JSONDecodeError, ValueError) as e:
                    # Invalid JSON - mark for deletion
                    expired_sessions.append({
                        "key": key,
                        "reason": "invalid_json",
                        "error": str(e),
                        "ttl": ttl
                    })
                
                # Process batch when full
                if len(expired_sessions) >= batch_size:
                    batch_number += 1
                    deleted_count = await _process_cleanup_batch(
                        redis_client, expired_sessions, batch_number
                    )
                    cleanup_summary["sessions_deleted"] += deleted_count
                    cleanup_summary["batch_count"] += 1
                    cleanup_summary["redis_operations"] += len(expired_sessions)
                    
                    # Calculate memory saved (approximate)
                    memory_saved = sum(session.get("data_size", 100) for session in expired_sessions)
                    cleanup_summary["memory_saved_mb"] += memory_saved / (1024 * 1024)
                    
                    expired_sessions.clear()
                    
                    logger.info("📦 Batch processed", batch=batch_number, deleted=deleted_count)
                
            except Exception as e:
                cleanup_summary["errors_encountered"] += 1
                logger.error("❌ Error processing session", key=key, error=str(e))
        
        # Process remaining sessions
        if expired_sessions:
            batch_number += 1
            deleted_count = await _process_cleanup_batch(
                redis_client, expired_sessions, batch_number
            )
            cleanup_summary["sessions_deleted"] += deleted_count
            cleanup_summary["batch_count"] += 1
            cleanup_summary["redis_operations"] += len(expired_sessions)
            
            # Calculate final memory saved
            memory_saved = sum(session.get("data_size", 100) for session in expired_sessions)
            cleanup_summary["memory_saved_mb"] += memory_saved / (1024 * 1024)
        
        # Calculate processing time
        end_time = datetime.now()
        cleanup_summary["end_time"] = end_time.isoformat()
        cleanup_summary["processing_time_seconds"] = (end_time - start_time).total_seconds()
        
        # Log summary to MongoDB
        cleanup_document = {
            **cleanup_summary,
            "component": "session_cleanup", 
            "version": "1.0.0",
            "environment": "production",
            "active_sessions_count": len(active_sessions),
            "cleanup_efficiency": (
                cleanup_summary["sessions_deleted"] / cleanup_summary["sessions_found"] * 100
                if cleanup_summary["sessions_found"] > 0 else 0
            ),
            "active_sessions_sample": active_sessions[:5],  # Sample of active sessions
            "performance_metrics": {
                "sessions_per_second": (
                    cleanup_summary["sessions_found"] / cleanup_summary["processing_time_seconds"]
                    if cleanup_summary["processing_time_seconds"] > 0 else 0
                ),
                "redis_ops_per_second": (
                    cleanup_summary["redis_operations"] / cleanup_summary["processing_time_seconds"]
                    if cleanup_summary["processing_time_seconds"] > 0 else 0
                )
            }
        }
        
        collection = mongo_db["session_cleanup_logs"]
        result = await collection.insert_one(cleanup_document)
        cleanup_summary["mongodb_operations"] += 1
        cleanup_summary["log_document_id"] = str(result.inserted_id)
        
        cleanup_summary["success"] = True
        
        logger.info(
            "🎉 Session cleanup completed",
            found=cleanup_summary["sessions_found"],
            deleted=cleanup_summary["sessions_deleted"], 
            preserved=cleanup_summary["sessions_preserved"],
            errors=cleanup_summary["errors_encountered"],
            time_seconds=cleanup_summary["processing_time_seconds"],
            memory_saved_mb=round(cleanup_summary["memory_saved_mb"], 2)
        )
        
        return cleanup_summary
        
    except Exception as e:
        cleanup_summary["error"] = str(e)
        cleanup_summary["success"] = False
        
        # Emergency MongoDB logging
        try:
            if mongo_client:
                emergency_doc = {
                    **cleanup_summary,
                    "error_type": "cleanup_failure",
                    "emergency_log": True,
                    "timestamp": datetime.now()
                }
                collection = mongo_client[database_name]["session_cleanup_errors"]
                await collection.insert_one(emergency_doc)
        except:
            pass  # Silent fail for emergency logging
        
        logger.error("💥 Session cleanup failed", error=str(e))
        return cleanup_summary
        
    finally:
        # Cleanup connections
        try:
            if redis_client:
                await redis_client.close()
            if mongo_client:
                mongo_client.close()
        except Exception as e:
            logger.warning("⚠️ Error during connection cleanup", error=str(e))


async def _process_cleanup_batch(
    redis_client: redis.Redis,
    sessions_to_delete: list,
    batch_number: int
) -> int:
    """
    🗑️ Process a batch of sessions for deletion
    
    Args:
        redis_client: Redis client instance
        sessions_to_delete: List of session objects to delete
        batch_number: Current batch number for logging
        
    Returns:
        int: Number of sessions successfully deleted
    """
    
    deleted_count = 0
    
    try:
        # Extract keys for batch deletion
        keys_to_delete = [session["key"] for session in sessions_to_delete]
        
        if keys_to_delete:
            # Use pipeline for efficient batch deletion
            pipe = redis_client.pipeline()
            for key in keys_to_delete:
                pipe.delete(key)
            
            results = await pipe.execute()
            deleted_count = sum(1 for result in results if result > 0)
            
            logger.info(
                "🗑️ Batch deletion completed",
                batch=batch_number,
                attempted=len(keys_to_delete),
                deleted=deleted_count,
                reasons=[session["reason"] for session in sessions_to_delete]
            )
        
        return deleted_count
        
    except Exception as e:
        logger.error("❌ Batch deletion failed", batch=batch_number, error=str(e))
        return 0


# 🏃‍♂️ Quick Cleanup Functions
async def quick_cleanup(max_age_hours: int = 6) -> Dict[str, Any]:
    """🚀 Quick session cleanup for routine maintenance"""
    
    return await cleanup_expired_sessions(
        batch_size=50,
        max_age_hours=max_age_hours
    )


async def deep_cleanup(max_age_hours: int = 48) -> Dict[str, Any]:
    """🔍 Deep cleanup for comprehensive maintenance"""
    
    return await cleanup_expired_sessions(
        batch_size=200,
        max_age_hours=max_age_hours
    )


# 📊 Cleanup Analytics
async def get_cleanup_statistics(days: int = 7) -> Dict[str, Any]:
    """
    📈 Get session cleanup statistics from last N days
    
    Args:
        days: Number of days to analyze
        
    Returns:
        Dict with cleanup analytics
    """
    
    contact_manager = ContactManager()
    
    try:
        if not await contact_manager.initialize():
            return {"error": "Failed to initialize database connections"}
        
        collection = contact_manager._mongo_db["session_cleanup_logs"]
        
        # Aggregate cleanup statistics
        pipeline = [
            {
                "$match": {
                    "start_time": {
                        "$gte": (datetime.now() - timedelta(days=days)).isoformat()
                    },
                    "success": True
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_cleanups": {"$sum": 1},
                    "total_sessions_found": {"$sum": "$sessions_found"},
                    "total_sessions_deleted": {"$sum": "$sessions_deleted"},
                    "total_sessions_preserved": {"$sum": "$sessions_preserved"},
                    "total_errors": {"$sum": "$errors_encountered"},
                    "total_memory_saved_mb": {"$sum": "$memory_saved_mb"},
                    "avg_processing_time": {"$avg": "$processing_time_seconds"},
                    "cleanup_runs": {
                        "$push": {
                            "start_time": "$start_time",
                            "sessions_deleted": "$sessions_deleted",
                            "processing_time": "$processing_time_seconds"
                        }
                    }
                }
            }
        ]
        
        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=1)
        
        if results:
            stats = results[0]
            stats["cleanup_efficiency"] = (
                stats["total_sessions_deleted"] / stats["total_sessions_found"] * 100
                if stats["total_sessions_found"] > 0 else 0
            )
            stats["period_days"] = days
            stats["generated_at"] = datetime.now().isoformat()
            return stats
        
        return {
            "total_cleanups": 0,
            "period_days": days,
            "message": "No cleanup data found",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Cleanup statistics failed", error=str(e))
        return {"error": str(e)}
        
    finally:
        await contact_manager.close()


# 🎯 CLI Cleanup Function
async def run_session_cleanup() -> None:
    """
    🚀 CLI session cleanup runner
    
    Perfect for cron jobs and scheduled maintenance.
    """
    
    print("🧹 GavatCore Session Cleanup Starting...")
    print("=" * 50)
    
    # Run cleanup
    result = await cleanup_expired_sessions()
    
    if result["success"]:
        print("✅ Cleanup completed successfully!")
        print(f"📊 Sessions found: {result['sessions_found']}")
        print(f"🗑️ Sessions deleted: {result['sessions_deleted']}")
        print(f"💾 Sessions preserved: {result['sessions_preserved']}")
        print(f"⚡ Processing time: {result['processing_time_seconds']:.2f}s")
        print(f"💾 Memory saved: {result['memory_saved_mb']:.2f} MB")
        
        if result["errors_encountered"] > 0:
            print(f"⚠️ Errors encountered: {result['errors_encountered']}")
        
    else:
        print("❌ Cleanup failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    print("-" * 50)
    print(f"📝 MongoDB log ID: {result.get('log_document_id', 'N/A')}")


if __name__ == "__main__":
    # Test the system
    async def main():
        # Test basic system
        success = await test_contact_system()
        print(f"🧪 Test Result: {'✅ PASSED' if success else '❌ FAILED'}")
        
        # Run analytics if test passed
        if success:
            print("\n" + "="*60)
            await quick_error_analysis()
            
            print("\n" + "="*60)
            print("🧹 Running session cleanup demo...")
            await run_session_cleanup()
    
    asyncio.run(main()) 