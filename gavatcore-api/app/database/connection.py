#!/usr/bin/env python3
"""
🗄️ GAVATCORE SaaS DATABASE CONNECTION
SQLAlchemy async database setup
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData
import structlog

logger = structlog.get_logger("gavatcore.database")

# Database URL - will be imported from config later
DATABASE_URL = "postgresql+asyncpg://gavatcore:password@localhost/gavatcore_saas"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging in development
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create base model
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()


async def get_db_session() -> AsyncSession:
    """Get database session"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all database tables"""
    try:
        # Import all models to register them with Base
        from app.models import user, subscription, bot_instance, payment
        
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("✅ Database tables created successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise


async def drop_tables():
    """Drop all database tables (for testing)"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            
        logger.info("🗑️ Database tables dropped successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to drop database tables: {e}")
        raise


async def close_db():
    """Close database connection"""
    await engine.dispose()
    logger.info("🔒 Database connection closed") 