#!/usr/bin/env python3
"""
🚀 GAVATCORE SaaS API
Production-ready Bot-as-a-Service platform
"""

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

# Add parent directory to path for GavatCore imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.database.connection import engine, create_tables
from app.routes import auth, payment, bots, users
from app.core.exceptions import APIException


# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
    context_class=dict,
    logger_factory=structlog.WriteLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("gavatcore.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting GavatCore SaaS API...")
    
    # Create database tables
    await create_tables()
    
    # Initialize services
    # TODO: Initialize Redis, Stripe, etc.
    
    logger.info("✅ GavatCore SaaS API started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down GavatCore SaaS API...")


# Create FastAPI app
app = FastAPI(
    title="GavatCore SaaS API",
    description="Bot-as-a-Service platform with Telegram userbot automation",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(APIException)
async def api_exception_handler(request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "code": exc.code,
            "details": exc.details
        }
    )


@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": True,
            "message": "Endpoint not found",
            "code": "NOT_FOUND"
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "gavatcore-saas-api",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "🔥 GavatCore SaaS API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else "Contact support for documentation",
        "status": "operational"
    }


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(payment.router, prefix="/api/payment", tags=["Payment"])
app.include_router(bots.router, prefix="/api/bots", tags=["Bots"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
from app.routes.communication import router as communication_router
app.include_router(communication_router, prefix="/api/analysis", tags=["Analysis"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    ) 
