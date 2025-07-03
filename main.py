#!/usr/bin/env python3
"""
🚀 GavatCore Kernel 1.0 🚀
📂 Ana Sistem Dosyası

GavatCore Kernel 1.0, spam-aware Telegram botları, contact management,
coin sistemi ve GPT destekli yanıt altyapısını yöneten merkezi Python kodudur.
Bu dosya, sistemin çekirdek bileşenlerini organize eder ve async mimari ile çalışır.

Architecture:
Telegram ◄─► Redis ◄─► MongoDB ◄─► Contact Utils

🔧 Enhanced Features:
- Type annotations ve comprehensive error handling
- Professional logging ve monitoring
- Graceful shutdown ve resource management
- Performance metrics ve health checks
"""

import asyncio
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union, List
import traceback
import weakref
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
import atexit
import os

# Core Telegram Integration
from telethon import TelegramClient, events
from telethon.tl.types import User
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, RPCError

# GavatCore Modules
from utilities.contact_utils import add_contact_with_fallback, quick_cleanup

# Database & Cache
from redis.asyncio import Redis
from motor.motor_asyncio import AsyncIOMotorClient

# Logging
import structlog

# --- Config ---
try:
    from config import (
        API_ID, API_HASH, SESSION_NAME, MONGO_URI, REDIS_URL, DEBUG_MODE,
        AUTHORIZED_USERS, validate_config, get_config_summary
    )
except ImportError as e:
    print(f"❌ config.py import error: {e}")
    print("Önce config.py oluşturun ve .env dosyasını yapılandırın.")
    sys.exit(1)

# --- Configuration Validation ---
try:
    if not validate_config():
        print("⚠️ Configuration warnings detected, but continuing...")
except Exception as e:
    print(f"🚨 Critical configuration error: {e}")
    sys.exit(1)

# --- Structured Logging Setup ---
log_processors = [
    structlog.stdlib.filter_by_level,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
]

if DEBUG_MODE:
    log_processors.append(structlog.dev.ConsoleRenderer())
else:
    log_processors.append(structlog.processors.JSONRenderer())

structlog.configure(
    processors=log_processors,
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger("gavatcore.main")

# --- System Stats ---
@dataclass
class SystemStats:
    """System performance ve usage statistics."""
    start_time: datetime = field(default_factory=datetime.now)
    messages_processed: int = 0
    contacts_added: int = 0
    errors_encountered: int = 0
    cleanup_runs: int = 0
    last_cleanup: Optional[datetime] = None
    uptime_seconds: float = 0.0
    
    def update_uptime(self) -> None:
        """Update uptime calculation."""
        self.uptime_seconds = (datetime.now() - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        self.update_uptime()
        return {
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": self.uptime_seconds,
            "uptime_human": str(timedelta(seconds=int(self.uptime_seconds))),
            "messages_processed": self.messages_processed,
            "contacts_added": self.contacts_added,
            "errors_encountered": self.errors_encountered,
            "cleanup_runs": self.cleanup_runs,
            "last_cleanup": self.last_cleanup.isoformat() if self.last_cleanup else None,
            "error_rate": self.errors_encountered / max(self.messages_processed, 1),
            "contact_success_rate": self.contacts_added / max(self.messages_processed, 1) if self.messages_processed > 0 else 0.0,
        }

# Global stats instance
stats = SystemStats()

# --- Global Clients ---
class ClientManager:
    """Manages Telegram and database clients with proper lifecycle."""
    
    def __init__(self):
        self.client: Optional[TelegramClient] = None
        self.redis: Optional[Redis] = None
        self.mongo: Optional[AsyncIOMotorClient] = None
        self.mongo_db: Optional[Any] = None
        self.contact_failures: Optional[Any] = None
        self._initialized = False
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def initialize(self) -> bool:
        """Initialize all clients with proper error handling."""
        try:
            log.info("🔧 Initializing clients...")
            
            # Initialize Telegram client
            self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
            
            # Connect to Telegram
            await self.client.start()
            log.info("📱 Telegram client connected successfully")
            
            # Initialize Redis
            self.redis = Redis.from_url(
                REDIS_URL, 
                encoding="utf-8", 
                decode_responses=True,
                socket_connect_timeout=10,
                socket_timeout=10,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Initialize MongoDB
            self.mongo = AsyncIOMotorClient(
                MONGO_URI,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            self.mongo_db = self.mongo["gavatcore"]
            self.contact_failures = self.mongo_db["contact_failures"]
            
            self._initialized = True
            log.info("✅ All clients initialized successfully")
            return True
            
        except Exception as e:
            log.error("❌ Client initialization failed", error=str(e), exc_info=True)
            return False
    
    async def test_connections(self) -> Dict[str, bool]:
        """Test all database connections."""
        results = {}
        
        # Test Redis
        try:
            if self.redis:
                await self.redis.ping()
                results["redis"] = True
                log.info("🔴 Redis connection ✅")
            else:
                results["redis"] = False
        except Exception as e:
            results["redis"] = False
            log.error("❌ Redis connection failed", error=str(e))
        
        # Test MongoDB
        try:
            if self.mongo_db is not None:
                await self.mongo_db.command("ping")
                results["mongodb"] = True
                log.info("🍃 MongoDB connection ✅")
            else:
                results["mongodb"] = False
        except Exception as e:
            results["mongodb"] = False
            log.error("❌ MongoDB connection failed", error=str(e))
        
        return results
    
    async def cleanup(self) -> None:
        """Cleanup all clients gracefully."""
        log.info("🧹 Cleaning up clients...")
        
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self.client:
            try:
                await self.client.disconnect()
                log.info("📱 Telegram client disconnected")
            except Exception as e:
                log.warning("⚠️ Telegram disconnect error", error=str(e))
        
        if self.redis:
            try:
                await self.redis.close()
                log.info("🔴 Redis connection closed")
            except Exception as e:
                log.warning("⚠️ Redis close error", error=str(e))
        
        if self.mongo:
            try:
                self.mongo.close()
                log.info("🍃 MongoDB connection closed")
            except Exception as e:
                log.warning("⚠️ MongoDB close error", error=str(e))

# Global client manager
client_manager = ClientManager()

# Event handler'ları kaydet
def register_event_handlers():
    """Event handler'ları client başlatıldıktan sonra kaydeder."""
    if not client_manager.client:
        log.error("❌ Client not initialized")
        return
        
    @client_manager.client.on(events.NewMessage)
    async def handle_reply(event) -> None:
        """
        Handle new messages with DM requests.
        
        Enhanced with proper type checking, error handling, and metrics.
        """
        async with error_context("handle_reply", getattr(event, 'sender_id', None)):
            stats.messages_processed += 1
            
            # Get user info first for filtering
            user = await event.get_sender()
            if not isinstance(user, User):
                return  # Skip non-user entities
            
            # Filter out bots and unwanted users
            if user.bot:
                log.debug("🤖 Skipping bot message", 
                         user_id=user.id, 
                         username=getattr(user, 'username', None))
                return
            
            # Filter out specific problematic users/bots
            excluded_usernames = ["missrose_bot", "rose", "grouphelp_bot"]
            excluded_user_ids = [609517172]  # Rose bot ID
            
            if (user.id in excluded_user_ids or 
                (hasattr(user, 'username') and user.username and 
                 user.username.lower() in excluded_usernames)):
                log.debug("🚫 Skipping excluded user", 
                         user_id=user.id, 
                         username=getattr(user, 'username', None))
                return
            
            # Check for DM request keywords
            dm_keywords = ["dm", "mesaj", "yaz", "contact", "iletişim", "yazışma"]
            message_text = (event.raw_text or "").lower()
            
            if event.is_reply and any(keyword in message_text for keyword in dm_keywords):
                log.info("📩 DM request detected", 
                        user_id=event.sender_id, 
                        message=event.raw_text[:50] if event.raw_text else "")
                
                # User info already validated above
                if not isinstance(user, User):
                    await event.respond("❌ Kullanıcı bilgisi alınamadı")
                    log.warning("⚠️ Invalid user type", 
                               sender_type=type(user).__name__,
                               sender_id=event.sender_id)
                    return
                
                # Process contact addition with comprehensive logging
                try:
                    message = await add_contact_with_fallback(client_manager.client, user)
                    
                    # Try to respond, but handle permission errors
                    try:
                        await event.respond(message)
                    except Exception as respond_error:
                        log.warning("⚠️ Cannot respond to user", 
                                   user_id=user.id,
                                   error=str(respond_error))
                    
                    # Update statistics with detailed logging
                    if "✅" in message:
                        stats.contacts_added += 1
                        log.info("✅ Contact added successfully", 
                                user_id=user.id, 
                                username=getattr(user, 'username', None),
                                first_name=getattr(user, 'first_name', None))
                    else:
                        log.warning("⚠️ Contact addition failed", 
                                   user_id=user.id)
                except Exception as e:
                    log.error("❌ Contact addition error", 
                             user_id=user.id,
                             error=str(e))
                    # Don't try to respond if we already have permission issues

    @client_manager.client.on(events.NewMessage(pattern='/stats'))
    async def handle_stats_command(event) -> None:
        """Handle /stats command."""
        try:
            if not await is_authorized_user(event.sender_id):
                try:
                    await event.respond("❌ Yetkisiz erişim")
                except Exception:
                    log.warning("⚠️ Cannot respond to unauthorized user", user_id=event.sender_id)
                return
                
            stats.update_uptime()
            stats_dict = stats.to_dict()
            
            response = (
                "📊 Sistem İstatistikleri:\n"
                f"⏱️ Çalışma Süresi: {stats_dict['uptime_human']}\n"
                f"📨 İşlenen Mesaj: {stats_dict['messages_processed']}\n"
                f"👥 Eklenen Kişi: {stats_dict['contacts_added']}\n"
                f"❌ Hata Sayısı: {stats_dict['errors_encountered']}\n"
                f"🧹 Temizlik Sayısı: {stats_dict['cleanup_runs']}\n"
                f"📈 Hata Oranı: {stats_dict['error_rate']:.2%}\n"
                f"✅ Başarı Oranı: {stats_dict['contact_success_rate']:.2%}"
            )
            
            try:
                await event.respond(response)
            except Exception as e:
                log.warning("⚠️ Cannot send stats response", user_id=event.sender_id, error=str(e))
        except Exception as e:
            log.error("❌ Stats command error", user_id=event.sender_id, error=str(e))

    @client_manager.client.on(events.NewMessage(pattern='/cleanup'))
    async def handle_cleanup_command(event) -> None:
        """Handle /cleanup command."""
        try:
            if not await is_authorized_user(event.sender_id):
                try:
                    await event.respond("❌ Yetkisiz erişim")
                except Exception:
                    log.warning("⚠️ Cannot respond to unauthorized user", user_id=event.sender_id)
                return
                
            try:
                await event.respond("🧹 Temizlik başlatılıyor...")
                await periodic_cleanup()
                await event.respond("✅ Temizlik tamamlandı!")
            except Exception as e:
                log.warning("⚠️ Cannot send cleanup response", user_id=event.sender_id, error=str(e))
        except Exception as e:
            log.error("❌ Cleanup command error", user_id=event.sender_id, error=str(e))

# --- Event Handlers ---

@asynccontextmanager
async def error_context(operation: str, user_id: Optional[int] = None):
    """Context manager for consistent error handling and logging."""
    try:
        yield
    except FloodWaitError as e:
        stats.errors_encountered += 1
        log.warning("🚫 FloodWait error", 
                   operation=operation, 
                   user_id=user_id, 
                   wait_seconds=e.seconds)
        raise
    except UserPrivacyRestrictedError as e:
        stats.errors_encountered += 1
        log.warning("🔒 User privacy restricted", 
                   operation=operation, 
                   user_id=user_id)
        raise
    except RPCError as e:
        stats.errors_encountered += 1
        log.error("🌐 Telegram RPC error", 
                 operation=operation, 
                 user_id=user_id, 
                 error_code=e.code,
                 error_message=e.message)
        raise
    except Exception as e:
        stats.errors_encountered += 1
        log.error("❌ Unexpected error", 
                 operation=operation, 
                 user_id=user_id, 
                 error=str(e),
                 exc_info=True)
        raise

async def is_authorized_user(user_id: int) -> bool:
    """Check if user is authorized for admin commands."""
    return user_id in AUTHORIZED_USERS if AUTHORIZED_USERS else False

# --- Background Tasks ---

async def periodic_cleanup() -> None:
    """
    Background session cleanup task with improved error handling and scheduling.
    """
    cleanup_interval = 6 * 60 * 60  # 6 hours in seconds
    
    while True:
        try:
            log.info("⏰ Scheduled cleanup sleep started", interval_hours=6)
            await asyncio.sleep(cleanup_interval)
            
            log.info("🧹 Running scheduled cleanup...")
            
            # Run cleanup with timeout
            result = await asyncio.wait_for(quick_cleanup(), timeout=600.0)  # 10 minute timeout
            
            if result.get("success", False):
                stats.cleanup_runs += 1
                stats.last_cleanup = datetime.now()
                log.info("✅ Scheduled cleanup completed",
                        deleted=result.get("sessions_deleted", 0),
                        found=result.get("sessions_found", 0),
                        duration=result.get("processing_time_seconds", 0))
            else:
                log.error("❌ Scheduled cleanup failed", 
                         error=result.get("error", "Unknown error"))
                
        except asyncio.CancelledError:
            log.info("🛑 Periodic cleanup task cancelled")
            break
        except asyncio.TimeoutError:
            log.error("⏰ Scheduled cleanup timeout")
        except Exception as e:
            log.error("❌ Background cleanup error", 
                     error=str(e),
                     exc_info=True)
            # Continue running even after errors

# --- Signal Handlers ---

_shutdown_event = asyncio.Event()

def signal_handler(signum: int, frame) -> None:
    """Handle shutdown signals gracefully with proper cleanup."""
    log.info("🛑 Shutdown signal received", 
            signal=signum, 
            signal_name=signal.Signals(signum).name)
    print(f"\n🛑 GavatCore Kernel shutting down... (Signal: {signal.Signals(signum).name})")
    _shutdown_event.set()

# Register cleanup on exit
@atexit.register
def cleanup_on_exit():
    """Ensure cleanup runs on process exit."""
    if client_manager._initialized:
        asyncio.create_task(client_manager.cleanup())

# --- Main Functions ---

async def startup_sequence() -> bool:
    """Initialize and start the bot."""
    try:
        # Initialize clients
        if not await client_manager.initialize():
            return False
            
        # Test connections
        connection_results = await client_manager.test_connections()
        if not all(connection_results.values()):
            log.error("❌ Some connections failed", results=connection_results)
            return False
            
        # Register event handlers
        register_event_handlers()
        
        # Start cleanup task
        client_manager._cleanup_task = asyncio.create_task(periodic_cleanup())
        
        log.info("✅ Startup sequence completed successfully")
        return True
        
    except Exception as e:
        log.error("❌ Startup sequence failed", error=str(e))
        return False

async def main() -> None:
    """
    Main entry point for GavatCore Kernel 1.0 with enhanced error handling.
    """
    
    print("🔥" + "="*60 + "🔥")
    print("🚀 GavatCore Kernel 1.0 - Yazılım Tarihine Geçecek Bot! 🚀")
    print("🔥" + "="*60 + "🔥")
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Run startup sequence
        if not await startup_sequence():
            log.error("❌ Startup failed, exiting...")
            sys.exit(1)
        
        print("\n🎉 GavatCore Kernel 1.0 aktif! Ctrl+C ile durdurabilirsiniz.")
        print("📊 /stats komutu ile istatistikleri görebilirsiniz.")
        print("🧹 /cleanup komutu ile manuel session temizliği yapabilirsiniz.")
        
        # Main event loop
        log.info("🔄 Entering main event loop...")
        await client_manager.client.run_until_disconnected()
        
    except KeyboardInterrupt:
        log.info("⌨️ Keyboard interrupt received")
    except Exception as e:
        log.error("❌ Unexpected error in main", 
                 error=str(e),
                 exc_info=True)
    finally:
        log.info("🛑 Initiating graceful shutdown...")
        
        # Cleanup resources
        await client_manager.cleanup()
        
        # Final stats
        final_stats = stats.to_dict()
        log.info("📊 Final statistics", **final_stats)
        
        print("\n✅ GavatCore Kernel 1.0 temiz bir şekilde kapatıldı.")
        print(f"📊 Toplam işlenen mesaj: {stats.messages_processed}")
        print(f"✅ Eklenen contact: {stats.contacts_added}")
        print(f"🧹 Cleanup çalışma sayısı: {stats.cleanup_runs}")

if __name__ == "__main__":
    try:
        if os.environ.get('TESTING') == 'true':
            from unittest.mock import MagicMock
            client_manager.client = MagicMock()
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⌨️ Program kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Kritik hata: {e}")
        sys.exit(1) 