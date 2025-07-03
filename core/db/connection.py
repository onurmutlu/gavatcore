#!/usr/bin/env python3
# core/db/connection.py - PostgreSQL Async Connection

import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
import structlog
# from utils.log_utils import log_event  # Circular import önleme

logger = structlog.get_logger("gavatcore.db")

# Base model
Base = declarative_base()
metadata = MetaData()

# Global engine ve session maker
engine = None
async_session_factory = None

async def init_database():
    """Veritabanı bağlantısını başlat"""
    global engine, async_session_factory
    
    try:
        database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./gavatcore.db")
        
        # SQLite optimizasyonları - aiosqlite uyumlu
        connect_args = {}
        if database_url.startswith("sqlite"):
            connect_args = {
                "timeout": 60,
                "check_same_thread": False
            }
        
        engine = create_async_engine(
            database_url,
            connect_args=connect_args,
            pool_size=10,
            max_overflow=20,
            pool_timeout=60,
            pool_recycle=1800,
            echo=False
        )
        
        async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
        
        # Tabloları oluştur
        from core.db.models import EventLog, SaleLog, MessageRecord, UserSession
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("✅ Veritabanı başarıyla başlatıldı")
        return engine, async_session_factory
        
    except Exception as e:
        logger.error(f"❌ Veritabanı başlatma hatası: {e}")
        raise

async def get_db_session():
    """Async database session al"""
    if async_session_factory is None:
        await init_database()
    
    session = async_session_factory()
    try:
        yield session
    finally:
        await session.close()

async def get_session() -> AsyncSession:
    """Yeni bir veritabanı oturumu al"""
    if async_session_factory is None:
        await init_database()
    return async_session_factory()

async def close_database():
    """Veritabanı bağlantısını kapat"""
    global engine
    if engine:
        await engine.dispose()
        logger.info("✅ Veritabanı bağlantısı kapatıldı") 