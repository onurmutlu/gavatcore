from infrastructure.config.logger import get_logger

"""
GavatCore Engine - Main FastAPI Application
==========================================

Complete integrated system with all modules working together.
"""

import asyncio
import json
import logging
import signal
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# GavatCore modules
from .config import get_settings
from .logger import LoggerMixin, get_logger
from .redis_state import redis_state
from .message_pool import message_pool, Message, MessageType, MessagePriority, MessageStatus
from .telegram_client import (
    telegram_client_pool, TelegramClientManager, ClientConfig,
    ConnectionStatus, MessageResult
)
from .scheduler_engine import scheduler_engine, ScheduledTask, TaskType, SpamProtection
from .ai_blending import ai_blending
from .admin_commands import admin_commands

# Pydantic models
class SendMessageRequest(BaseModel):
    entity: str
    message: str
    parse_mode: Optional[str] = "html"
    session_name: Optional[str] = None
    priority: MessagePriority = MessagePriority.NORMAL
    silent: bool = False
    schedule_at: Optional[datetime] = None

class ScheduleTaskRequest(BaseModel):
    task_type: TaskType
    target_entity: str
    message_content: str
    execute_at: Optional[datetime] = None
    cron_expression: Optional[str] = None
    interval_minutes: Optional[int] = None
    max_executions: Optional[int] = None
    session_name: Optional[str] = None

class BotConfigRequest(BaseModel):
    session_name: str
    api_id: int
    api_hash: str
    phone: Optional[str] = None
    bot_token: Optional[str] = None
    device_model: str = "GavatCore Bot"

class AdminCommandRequest(BaseModel):
    command: str
    user_id: int
    args: Optional[List[str]] = None

# Global variables
background_tasks = set()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("🚀 Starting GavatCore Engine...")
    
    # Initialize Redis
    try:
        await redis_state.connect()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        sys.exit(1)
    
    # Initialize message pool
    try:
        await message_pool.initialize()
        logger.info("✅ Message pool initialized")
    except Exception as e:
        logger.error(f"❌ Message pool initialization failed: {e}")
    
    # Initialize scheduler engine
    try:
        await scheduler_engine.initialize()
        logger.info("✅ Scheduler engine initialized")
    except Exception as e:
        logger.error(f"❌ Scheduler initialization failed: {e}")
    
    # Initialize AI blending
    try:
        await ai_blending.initialize()
        logger.info("✅ AI blending initialized")
    except Exception as e:
        logger.error(f"❌ AI blending initialization failed: {e}")
    
    # Load existing bot configurations
    await load_existing_bots()
    
    # Start background workers
    await start_background_workers()
    
    logger.info("🎉 GavatCore Engine started successfully!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down GavatCore Engine...")
    
    # Stop background tasks
    for task in background_tasks:
        task.cancel()
    
    # Shutdown modules
    try:
        await scheduler_engine.shutdown()
        await telegram_client_pool.shutdown()
        await message_pool.shutdown()
        await redis_state.disconnect()
        logger.info("✅ Clean shutdown completed")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")


# Create FastAPI app
app = FastAPI(
    title="GavatCore Engine",
    description="Advanced auto-messaging engine with Telegram integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MainApp(LoggerMixin):
    """Main application controller."""
    
    def __init__(self):
        self.settings = get_settings()


main_app = MainApp()


async def load_existing_bots():
    """Load existing bot configurations from the system."""
    main_app.log_event("Loading existing bot configurations")
    
    try:
        # Try to load from existing config.py
        import config
        
        # Load yayincilara bot
        if hasattr(config, 'YAYINCILARA_PHONE') and hasattr(config, 'TELEGRAM_API_ID'):
            yayincilara_config = ClientConfig(
                session_name="yayincilara",
                api_id=config.TELEGRAM_API_ID,
                api_hash=config.TELEGRAM_API_HASH,
                phone=config.YAYINCILARA_PHONE,
                device_model="GavatCore Yayıncılar Bot"
            )
            
            success = await telegram_client_pool.add_client(yayincilara_config)
            if success:
                main_app.log_event("✅ Yayıncılar bot loaded")
            else:
                main_app.log_error("❌ Yayıncılar bot failed to load")
        
        # Load xxxgeisha bot
        if hasattr(config, 'XXXGEISHA_PHONE'):
            geisha_config = ClientConfig(
                session_name="xxxgeisha",
                api_id=config.TELEGRAM_API_ID,
                api_hash=config.TELEGRAM_API_HASH,
                phone=config.XXXGEISHA_PHONE,
                device_model="GavatCore XXXGeisha Bot"
            )
            
            success = await telegram_client_pool.add_client(geisha_config)
            if success:
                main_app.log_event("✅ XXXGeisha bot loaded")
            else:
                main_app.log_error("❌ XXXGeisha bot failed to load")
        
        # Load any other configured bots from data/profiles/
        from pathlib import Path
        
        profiles_dir = Path("data/profiles")
        if profiles_dir.exists():
            for profile_file in profiles_dir.glob("*.json"):
                if profile_file.name.endswith(".banned"):
                    continue
                    
                try:
                    with open(profile_file, 'r', encoding='utf-8') as f:
                        profile_data = json.load(f)
                    
                    if 'phone' in profile_data and profile_data.get('active', True):
                        profile_config = ClientConfig(
                            session_name=profile_file.stem,
                            api_id=config.TELEGRAM_API_ID,
                            api_hash=config.TELEGRAM_API_HASH,
                            phone=profile_data['phone'],
                            device_model=f"GavatCore {profile_data.get('name', profile_file.stem).title()} Bot"
                        )
                        
                        success = await telegram_client_pool.add_client(profile_config)
                        if success:
                            main_app.log_event(f"✅ {profile_file.stem} bot loaded from profile")
                        else:
                            main_app.log_error(f"❌ {profile_file.stem} bot failed to load")
                            
                except Exception as e:
                    main_app.log_error(f"Error loading profile {profile_file}: {e}")
        
    except ImportError:
        main_app.log_error("Config.py not found, no existing bots loaded")
    except Exception as e:
        main_app.log_error(f"Error loading existing bots: {e}")


async def start_background_workers():
    """Start all background worker tasks."""
    main_app.log_event("Starting background workers")
    
    # Message processing worker
    task1 = asyncio.create_task(message_processing_worker())
    background_tasks.add(task1)
    
    # Scheduler worker
    task2 = asyncio.create_task(scheduler_worker())
    background_tasks.add(task2)
    
    # Statistics update worker
    task3 = asyncio.create_task(statistics_worker())
    background_tasks.add(task3)
    
    # Health check worker
    task4 = asyncio.create_task(health_check_worker())
    background_tasks.add(task4)
    
    main_app.log_event(f"✅ {len(background_tasks)} background workers started")


async def message_processing_worker():
    """Background worker for processing messages from the pool."""
    main_app.log_event("Message processing worker started")
    
    while True:
        try:
            # Get next message from pool
            message = await message_pool.get_next_message()
            
            if message:
                await process_single_message(message)
            else:
                # No messages, short sleep
                await asyncio.sleep(0.1)
                
        except asyncio.CancelledError:
            main_app.log_event("Message processing worker cancelled")
            break
        except Exception as e:
            main_app.log_error(f"Message processing worker error: {e}")
            await asyncio.sleep(1)


async def process_single_message(message: Message):
    """Process a single message."""
    try:
        # Update message status
        await message_pool.update_message_status(message.id, MessageStatus.PROCESSING)
        
        # Get appropriate client
        client = await telegram_client_pool.get_client(message.session_name)
        
        if not client:
            await message_pool.update_message_status(message.id, MessageStatus.FAILED)
            main_app.log_error(f"No available client for message {message.id}")
            return
        
        # Generate AI-enhanced message if needed
        if message.ai_enhanced:
            enhanced_content = await ai_blending.generate_response(
                message.content,
                message.session_name,
                message.target_entity
            )
            message.content = enhanced_content or message.content
        
        # Send message
        result = await client.send_message(
            entity=message.target_entity,
            message=message.content,
            parse_mode=message.parse_mode,
            silent=message.silent
        )
        
        if result.success:
            # Update message status
            await message_pool.update_message_status(message.id, MessageStatus.SENT)
            
            # Update statistics
            await redis_state.increment_bot_stat(message.session_name, "messages_sent")
            
            main_app.log_event(
                "Message sent successfully",
                message_id=message.id,
                telegram_message_id=result.message_id,
                session_name=message.session_name
            )
        else:
            # Handle failure
            if result.result == MessageResult.FLOOD_WAIT:
                # Reschedule message
                await message_pool.update_message_status(message.id, MessageStatus.PENDING)
                await message_pool.reschedule_message(
                    message.id, 
                    datetime.utcnow() + timedelta(seconds=result.flood_wait_time)
                )
                main_app.log_event(f"Message rescheduled due to flood wait: {result.flood_wait_time}s")
            else:
                await message_pool.update_message_status(message.id, MessageStatus.FAILED)
                await redis_state.increment_bot_stat(message.session_name, "messages_failed")
                main_app.log_error(f"Message failed: {result.error}")
        
    except Exception as e:
        await message_pool.update_message_status(message.id, MessageStatus.FAILED)
        main_app.log_error(f"Error processing message {message.id}: {e}")


async def scheduler_worker():
    """Background worker for scheduler engine."""
    main_app.log_event("Scheduler worker started")
    
    while True:
        try:
            await scheduler_engine.process_pending_tasks()
            await asyncio.sleep(1)  # Check every second
            
        except asyncio.CancelledError:
            main_app.log_event("Scheduler worker cancelled")
            break
        except Exception as e:
            main_app.log_error(f"Scheduler worker error: {e}")
            await asyncio.sleep(5)


async def statistics_worker():
    """Background worker for updating statistics."""
    main_app.log_event("Statistics worker started")
    
    while True:
        try:
            # Update system statistics
            await update_system_statistics()
            
            # Sleep for 1 minute
            await asyncio.sleep(60)
            
        except asyncio.CancelledError:
            main_app.log_event("Statistics worker cancelled")
            break
        except Exception as e:
            main_app.log_error(f"Statistics worker error: {e}")
            await asyncio.sleep(60)


async def health_check_worker():
    """Background worker for health checks."""
    main_app.log_event("Health check worker started")
    
    while True:
        try:
            # Check client connections
            pool_stats = await telegram_client_pool.get_pool_stats()
            
            if pool_stats['connected_clients'] == 0 and pool_stats['total_clients'] > 0:
                main_app.log_error("⚠️ No connected clients available!")
            
            # Check Redis connection
            try:
                await redis_state.ping()
            except Exception as e:
                main_app.log_error(f"Redis health check failed: {e}")
            
            # Sleep for 5 minutes
            await asyncio.sleep(300)
            
        except asyncio.CancelledError:
            main_app.log_event("Health check worker cancelled")
            break
        except Exception as e:
            main_app.log_error(f"Health check worker error: {e}")
            await asyncio.sleep(300)


async def update_system_statistics():
    """Update system-wide statistics."""
    try:
        # Get pool statistics
        pool_stats = await telegram_client_pool.get_pool_stats()
        
        # Get message pool statistics
        message_stats = await message_pool.get_statistics()
        
        # Get scheduler statistics
        scheduler_stats = await scheduler_engine.get_statistics()
        
        # Combine statistics
        system_stats = {
            "timestamp": datetime.utcnow().isoformat(),
            "telegram_clients": pool_stats,
            "message_pool": message_stats,
            "scheduler": scheduler_stats,
            "uptime": (datetime.utcnow() - main_app.settings.start_time).total_seconds() if hasattr(main_app.settings, 'start_time') else 0
        }
        
        # Store in Redis
        await redis_state.hset("system_stats", "latest", json.dumps(system_stats, default=str))
        
    except Exception as e:
        main_app.log_error(f"Error updating system statistics: {e}")


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "GavatCore Engine",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/send-message")
async def send_message(request: SendMessageRequest):
    """Send a message through the system."""
    try:
        # Create message object
        message = Message(
            target_entity=request.entity,
            content=request.message,
            message_type=MessageType.TEXT,
            priority=request.priority,
            session_name=request.session_name,
            parse_mode=request.parse_mode,
            silent=request.silent,
            scheduled_for=request.schedule_at,
            ai_enhanced=True  # Enable AI enhancement
        )
        
        # Add to message pool
        message_id = await message_pool.add_message(message)
        
        return {
            "success": True,
            "message_id": message_id,
            "status": "queued"
        }
        
    except Exception as e:
        main_app.log_error(f"Send message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/schedule-task")
async def schedule_task(request: ScheduleTaskRequest):
    """Schedule a task."""
    try:
        # Create scheduled task
        task = ScheduledTask(
            task_type=request.task_type,
            target_entity=request.target_entity,
            message_content=request.message_content,
            execute_at=request.execute_at,
            cron_expression=request.cron_expression,
            interval_minutes=request.interval_minutes,
            max_executions=request.max_executions,
            session_name=request.session_name
        )
        
        # Add to scheduler
        task_id = await scheduler_engine.add_task(task)
        
        return {
            "success": True,
            "task_id": task_id,
            "status": "scheduled"
        }
        
    except Exception as e:
        main_app.log_error(f"Schedule task error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-bot")
async def add_bot(request: BotConfigRequest):
    """Add a new bot to the pool."""
    try:
        config = ClientConfig(
            session_name=request.session_name,
            api_id=request.api_id,
            api_hash=request.api_hash,
            phone=request.phone,
            bot_token=request.bot_token,
            device_model=request.device_model
        )
        
        success = await telegram_client_pool.add_client(config)
        
        if success:
            return {
                "success": True,
                "message": f"Bot {request.session_name} added successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to add bot")
            
    except Exception as e:
        main_app.log_error(f"Add bot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin-command")
async def execute_admin_command(request: AdminCommandRequest):
    """Execute an admin command."""
    try:
        result = await admin_commands.execute_command(
            request.command,
            request.user_id,
            request.args or []
        )
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        main_app.log_error(f"Admin command error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """Get system status."""
    try:
        # Get all component statuses
        pool_stats = await telegram_client_pool.get_pool_stats()
        message_stats = await message_pool.get_statistics()
        scheduler_stats = await scheduler_engine.get_statistics()
        
        return {
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "telegram_clients": {
                    "total": pool_stats['total_clients'],
                    "connected": pool_stats['connected_clients'],
                    "details": pool_stats['client_stats']
                },
                "message_pool": message_stats,
                "scheduler": scheduler_stats,
                "redis": "connected" if await redis_state.ping() else "disconnected"
            }
        }
        
    except Exception as e:
        main_app.log_error(f"Status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics")
async def get_statistics():
    """Get detailed system statistics."""
    try:
        # Get stored statistics
        stats_data = await redis_state.hget("system_stats", "latest")
        
        if stats_data:
            if isinstance(stats_data, bytes):
                stats_data = stats_data.decode()
            return json.loads(stats_data)
        else:
            return {"error": "No statistics available"}
            
    except Exception as e:
        main_app.log_error(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/bot/{session_name}")
async def remove_bot(session_name: str):
    """Remove a bot from the pool."""
    try:
        success = await telegram_client_pool.remove_client(session_name)
        
        if success:
            return {
                "success": True,
                "message": f"Bot {session_name} removed successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Bot not found")
            
    except Exception as e:
        main_app.log_error(f"Remove bot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        redis_ok = await redis_state.ping()
        pool_stats = await telegram_client_pool.get_pool_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "redis": "ok" if redis_ok else "failed",
                "telegram_clients": f"{pool_stats['connected_clients']}/{pool_stats['total_clients']} connected"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    import uvicorn
    
    # Set up signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_config=None  # Use our custom logging
    ) 