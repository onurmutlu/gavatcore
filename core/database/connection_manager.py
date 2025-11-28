#!/usr/bin/env python3
"""
Unified Database Connection Manager
Centralized connection pooling for all database types
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, Optional

import aioredis
import aiosqlite
import structlog
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import QueuePool

from core.config import get_config

logger = structlog.get_logger("gavatcore.database")


class DatabaseConnectionManager:
    """Unified database connection manager with pooling"""

    def __init__(self):
        self.config = get_config()
        self._pg_engine = None
        self._pg_session_factory = None
        self._redis_pool = None
        self._mongo_client = None
        self._sqlite_connections = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize all database connections"""
        if self._initialized:
            return

        logger.info("Initializing database connections...")

        try:
            await self._init_postgresql()
            await self._init_redis()
            await self._init_mongodb()
            await self._init_sqlite()

            self._initialized = True
            logger.info("All database connections initialized successfully")

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    async def _init_postgresql(self) -> None:
        """Initialize PostgreSQL connection pool"""
        if not self.config.database.postgresql_url:
            logger.info("PostgreSQL URL not configured, skipping")
            return

        self._pg_engine = create_async_engine(
            self.config.database.postgresql_url,
            poolclass=QueuePool,
            pool_size=self.config.database.connection_pool_size,
            max_overflow=self.config.database.max_overflow,
            pool_pre_ping=True,
            echo=self.config.debug,
        )

        self._pg_session_factory = async_sessionmaker(
            self._pg_engine, class_=AsyncSession, expire_on_commit=False
        )

        logger.info("PostgreSQL connection pool initialized")

    async def _init_redis(self) -> None:
        """Initialize Redis connection pool"""
        try:
            self._redis_pool = aioredis.from_url(
                self.config.database.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=self.config.database.connection_pool_size,
            )

            # Test connection
            await self._redis_pool.ping()
            logger.info("Redis connection pool initialized")

        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}")
            self._redis_pool = None

    async def _init_mongodb(self) -> None:
        """Initialize MongoDB connection"""
        if not self.config.database.mongodb_url:
            logger.info("MongoDB URL not configured, skipping")
            return

        try:
            self._mongo_client = AsyncIOMotorClient(
                self.config.database.mongodb_url,
                maxPoolSize=self.config.database.connection_pool_size,
            )

            # Test connection
            await self._mongo_client.admin.command("ping")
            logger.info("MongoDB connection initialized")

        except Exception as e:
            logger.warning(f"MongoDB initialization failed: {e}")
            self._mongo_client = None

    async def _init_sqlite(self) -> None:
        """Initialize SQLite connections"""
        logger.info("SQLite connections will be created on-demand")

    @asynccontextmanager
    async def get_postgresql_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get PostgreSQL session with automatic cleanup"""
        if not self._pg_session_factory:
            raise RuntimeError("PostgreSQL not configured")

        async with self._pg_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def get_redis(self) -> aioredis.Redis:
        """Get Redis connection"""
        if not self._redis_pool:
            raise RuntimeError("Redis not configured or failed to initialize")
        return self._redis_pool

    def get_mongodb(self) -> AsyncIOMotorClient:
        """Get MongoDB client"""
        if not self._mongo_client:
            raise RuntimeError("MongoDB not configured or failed to initialize")
        return self._mongo_client

    @asynccontextmanager
    async def get_sqlite_connection(
        self, db_path: Optional[str] = None
    ) -> AsyncGenerator[aiosqlite.Connection, None]:
        """Get SQLite connection with automatic cleanup"""
        db_path = db_path or self.config.database.sqlite_path

        async with aiosqlite.connect(db_path) as conn:
            conn.row_factory = aiosqlite.Row
            yield conn

    async def health_check(self) -> Dict[str, bool]:
        """Check health of all database connections"""
        health = {}

        # PostgreSQL
        try:
            if self._pg_engine:
                async with self.get_postgresql_session() as session:
                    await session.execute(text("SELECT 1"))
                health["postgresql"] = True
            else:
                health["postgresql"] = None
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            health["postgresql"] = False

        # Redis
        try:
            if self._redis_pool:
                await self._redis_pool.ping()
                health["redis"] = True
            else:
                health["redis"] = None
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            health["redis"] = False

        # MongoDB
        try:
            if self._mongo_client:
                await self._mongo_client.admin.command("ping")
                health["mongodb"] = True
            else:
                health["mongodb"] = None
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            health["mongodb"] = False

        # SQLite
        try:
            async with self.get_sqlite_connection() as conn:
                await conn.execute("SELECT 1")
            health["sqlite"] = True
        except Exception as e:
            logger.error(f"SQLite health check failed: {e}")
            health["sqlite"] = False

        return health

    async def close(self) -> None:
        """Close all database connections"""
        logger.info("Closing database connections...")

        if self._pg_engine:
            await self._pg_engine.dispose()

        if self._redis_pool:
            await self._redis_pool.close()

        if self._mongo_client:
            self._mongo_client.close()

        self._initialized = False
        logger.info("All database connections closed")


# Global connection manager instance
_connection_manager: Optional[DatabaseConnectionManager] = None


async def get_connection_manager() -> DatabaseConnectionManager:
    """Get global connection manager instance"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = DatabaseConnectionManager()
        await _connection_manager.initialize()
    return _connection_manager


# Convenience functions for backward compatibility
async def get_postgresql_session():
    """Get PostgreSQL session"""
    manager = await get_connection_manager()
    return manager.get_postgresql_session()


async def get_redis():
    """Get Redis connection"""
    manager = await get_connection_manager()
    return await manager.get_redis()


async def get_mongodb():
    """Get MongoDB client"""
    manager = await get_connection_manager()
    return manager.get_mongodb()


async def get_sqlite_connection(db_path: Optional[str] = None):
    """Get SQLite connection"""
    manager = await get_connection_manager()
    return manager.get_sqlite_connection(db_path)
