from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🤖 GavatCore Admin Bot 🤖

Telegram admin bot with enhanced features:
- Comprehensive command handling
- Type-safe implementation
- Structured logging and error handling
- Health monitoring and status reporting

Enhanced Features:
- Type annotations ve comprehensive error handling
- Structured logging ve monitoring
- Admin command validation
- Graceful shutdown ve resource management
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import structlog
from contextlib import asynccontextmanager

# Path düzeltmesi - parent directory'yi ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telethon import TelegramClient, events
from telethon.tl.types import User, Message
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, RPCError

try:
    from config import (
        ADMIN_BOT_TOKEN, TELEGRAM_API_ID, TELEGRAM_API_HASH, 
        AUTHORIZED_USERS, DEBUG_MODE
    )
except ImportError as e:
    print(f"❌ Config import hatası: {e}")
    print("Config dosyasını kontrol edin.")
    sys.exit(1)

# Configure structured logging
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

logger = structlog.get_logger("gavatcore.adminbot")

@dataclass
class BotMetrics:
    """Admin bot performance metrics."""
    start_time: datetime
    messages_processed: int = 0
    commands_executed: int = 0
    errors_encountered: int = 0
    authorized_access_attempts: int = 0
    unauthorized_access_attempts: int = 0
    
    @property
    def uptime_seconds(self) -> float:
        """Calculate uptime in seconds."""
        return (datetime.now() - self.start_time).total_seconds()
    
    @property
    def uptime_human(self) -> str:
        """Human readable uptime."""
        return str(timedelta(seconds=int(self.uptime_seconds)))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": self.uptime_seconds,
            "uptime_human": self.uptime_human,
            "messages_processed": self.messages_processed,
            "commands_executed": self.commands_executed,
            "errors_encountered": self.errors_encountered,
            "authorized_access_attempts": self.authorized_access_attempts,
            "unauthorized_access_attempts": self.unauthorized_access_attempts,
            "success_rate": (
                (self.commands_executed / max(self.messages_processed, 1)) * 100
                if self.messages_processed > 0 else 0
            )
        }

class AdminBot:
    """
    🤖 Enhanced GavatCore Admin Bot
    
    Production-ready admin bot with comprehensive error handling,
    metrics collection, and structured command processing.
    """
    
    def __init__(self):
        self.client: Optional[TelegramClient] = None
        self.metrics = BotMetrics(start_time=datetime.now())
        self._running = False
        
        logger.info("🔧 Admin Bot initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize Telegram client and validate configuration.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Validate configuration
            if not ADMIN_BOT_TOKEN:
                logger.error("❌ ADMIN_BOT_TOKEN bulunamadı")
                return False
            
            if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
                logger.error("❌ Telegram API credentials eksik")
                return False
            
            # Create Telegram client
            self.client = TelegramClient(
                'adminbot', 
                TELEGRAM_API_ID, 
                TELEGRAM_API_HASH,
                connection_retries=3,
                retry_delay=2,
                timeout=30
            )
            
            # Start with bot token
            await self.client.start(bot_token=ADMIN_BOT_TOKEN)
            
            # Get bot info
            me = await self.client.get_me()
            
            logger.info("✅ Admin Bot başarıyla başlatıldı!",
                       bot_id=me.id,
                       bot_username=me.username,
                       bot_first_name=me.first_name)
            
            return True
            
        except Exception as e:
            logger.error("❌ Admin Bot başlatma hatası", error=str(e), exc_info=True)
            return False
    
    def is_authorized_user(self, user_id: int) -> bool:
        """
        Check if user is authorized to use admin commands.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            bool: True if user is authorized, False otherwise
        """
        if not AUTHORIZED_USERS:
            logger.warning("⚠️ No authorized users configured")
            return False
        
        return user_id in AUTHORIZED_USERS
    
    @asynccontextmanager
    async def error_context(self, operation: str, user_id: Optional[int] = None):
        """Context manager for consistent error handling."""
        try:
            yield
        except FloodWaitError as e:
            self.metrics.errors_encountered += 1
            logger.warning("🚫 FloodWait error", 
                          operation=operation, 
                          user_id=user_id, 
                          wait_seconds=e.seconds)
            raise
        except UserPrivacyRestrictedError:
            self.metrics.errors_encountered += 1
            logger.warning("🔒 User privacy restricted", 
                          operation=operation, 
                          user_id=user_id)
            raise
        except RPCError as e:
            self.metrics.errors_encountered += 1
            logger.error("🌐 Telegram RPC error", 
                        operation=operation, 
                        user_id=user_id, 
                        error_code=e.code,
                        error_message=e.message)
            raise
        except Exception as e:
            self.metrics.errors_encountered += 1
            logger.error("❌ Unexpected error", 
                        operation=operation, 
                        user_id=user_id, 
                        error=str(e),
                        exc_info=True)
            raise
    
    async def handle_start_command(self, event: events.NewMessage.Event) -> None:
        """Handle /start command."""
        user_id = event.sender_id
        
        async with self.error_context("start_command", user_id):
            if self.is_authorized_user(user_id):
                self.metrics.authorized_access_attempts += 1
                
                response = """🤖 **GavatCore Admin Bot Aktif!**

✅ **Admin Paneli Hazır**
🔧 **Sistem Durumu**: Online
🚀 **GavatCore Kernel**: v1.0

**Kullanılabilir Komutlar:**
• `/status` - Sistem durumu
• `/stats` - Detaylı istatistikler
• `/health` - Sağlık kontrolü
• `/help` - Yardım menüsü

🎯 **Admin Yetkilendirmesi**: ✅ Onaylandı
"""
                
                logger.info("👤 Authorized start command", 
                           user_id=user_id,
                           authorized=True)
            else:
                self.metrics.unauthorized_access_attempts += 1
                
                response = """🤖 **GavatCore Admin Bot**

⚠️ **Erişim Reddedildi**
Bu bot sadece yetkilendirilmiş kullanıcılar içindir.

🔒 Admin erişimi gereklidir.
"""
                
                logger.warning("🚫 Unauthorized start command attempt", 
                              user_id=user_id,
                              authorized=False)
            
            await event.respond(response)
            self.metrics.commands_executed += 1
    
    async def handle_status_command(self, event: events.NewMessage.Event) -> None:
        """Handle /status command."""
        user_id = event.sender_id
        
        async with self.error_context("status_command", user_id):
            if not self.is_authorized_user(user_id):
                await event.respond("❌ Bu komut için yetkiniz yok.")
                self.metrics.unauthorized_access_attempts += 1
                return
            
            self.metrics.authorized_access_attempts += 1
            
            # Get system information
            metrics_data = self.metrics.to_dict()
            
            status_message = f"""📊 **GavatCore Admin Bot Status**

⏰ **Uptime**: {metrics_data['uptime_human']}
📈 **Mesaj İşlendi**: {metrics_data['messages_processed']}
⚡ **Komut Çalıştırıldı**: {metrics_data['commands_executed']}
❌ **Hata Sayısı**: {metrics_data['errors_encountered']}

🔐 **Erişim İstatistikleri**:
• Yetkili Erişim: {metrics_data['authorized_access_attempts']}
• Yetkisiz Erişim: {metrics_data['unauthorized_access_attempts']}

📊 **Başarı Oranı**: {metrics_data['success_rate']:.1f}%
🚀 **Sistem Durumu**: Aktif ✅

🕐 **Timestamp**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
            
            await event.respond(status_message)
            self.metrics.commands_executed += 1
            
            logger.info("📊 Status command executed", 
                       user_id=user_id,
                       uptime=metrics_data['uptime_human'])
    
    async def handle_health_command(self, event: events.NewMessage.Event) -> None:
        """Handle /health command."""
        user_id = event.sender_id
        
        async with self.error_context("health_command", user_id):
            if not self.is_authorized_user(user_id):
                await event.respond("❌ Bu komut için yetkiniz yok.")
                self.metrics.unauthorized_access_attempts += 1
                return
            
            self.metrics.authorized_access_attempts += 1
            
            # Quick health check
            is_healthy = (
                self.client and 
                self.client.is_connected() and
                self.metrics.errors_encountered < 10  # Error threshold
            )
            
            health_emoji = "✅" if is_healthy else "❌"
            health_status = "Healthy" if is_healthy else "Degraded"
            
            health_message = f"""🏥 **System Health Check**

{health_emoji} **Status**: {health_status}
�� **Connection**: {'✅ Connected' if self.client and self.client.is_connected() else '❌ Disconnected'}
⚡ **Performance**: {'✅ Good' if self.metrics.errors_encountered < 5 else '⚠️ Issues Detected'}

📊 **Quick Stats**:
• Uptime: {self.metrics.uptime_human}
• Error Rate: {(self.metrics.errors_encountered / max(self.metrics.messages_processed, 1)) * 100:.1f}%

🕐 **Check Time**: {datetime.now().strftime("%H:%M:%S")}
"""
            
            await event.respond(health_message)
            self.metrics.commands_executed += 1
            
            logger.info("🏥 Health check executed", 
                       user_id=user_id,
                       healthy=is_healthy)
    
    async def handle_help_command(self, event: events.NewMessage.Event) -> None:
        """Handle /help command."""
        user_id = event.sender_id
        
        async with self.error_context("help_command", user_id):
            if not self.is_authorized_user(user_id):
                await event.respond("❌ Bu komut için yetkiniz yok.")
                self.metrics.unauthorized_access_attempts += 1
                return
            
            self.metrics.authorized_access_attempts += 1
            
            help_message = """📚 **GavatCore Admin Bot - Help**

**📋 Available Commands:**

🚀 **Basic Commands:**
• `/start` - Bot'u başlat ve hoş geldin mesajı
• `/status` - Detaylı sistem durumu
• `/health` - Sağlık kontrolü
• `/help` - Bu yardım menüsü

📊 **Information Commands:**
• `/stats` - Detaylı istatistikler (alias for /status)

🔧 **System Info:**
• Bot Version: GavatCore v1.0
• Purpose: Admin panel for GavatCore system
• Authorization: Required for all commands

⚡ **Quick Tips:**
• Tüm komutlar yetkilendirme gerektirir
• Bot 7/24 aktif ve izleme yapar
• Hatalar otomatik loglanır

🆘 **Support:**
• Issues: GitHub repository
• Contact: System administrators
"""
            
            await event.respond(help_message)
            self.metrics.commands_executed += 1
            
            logger.info("📚 Help command executed", user_id=user_id)
    
    async def handle_unknown_command(self, event: events.NewMessage.Event) -> None:
        """Handle unknown or unrecognized commands."""
        user_id = event.sender_id
        message_text = event.raw_text or ""
        
        async with self.error_context("unknown_command", user_id):
            if not self.is_authorized_user(user_id):
                await event.respond("❌ Bu komut için yetkiniz yok.")
                self.metrics.unauthorized_access_attempts += 1
                return
            
            self.metrics.authorized_access_attempts += 1
            
            response = f"""❓ **Bilinmeyen Komut**

📝 **Aldığım mesaj**: `{message_text[:100]}{'...' if len(message_text) > 100 else ''}`

💡 **Kullanılabilir komutlar için** `/help` yazın

🚀 **Popüler komutlar**:
• `/status` - Sistem durumu
• `/health` - Sağlık kontrolü
• `/help` - Yardım menüsü
"""
            
            await event.respond(response)
            
            logger.info("❓ Unknown command received", 
                       user_id=user_id,
                       command=message_text[:50])
    
    async def setup_event_handlers(self) -> None:
        """Setup all event handlers for the bot."""
        if not self.client:
            raise RuntimeError("Client not initialized")
        
        # Command handlers
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            self.metrics.messages_processed += 1
            await self.handle_start_command(event)
        
        @self.client.on(events.NewMessage(pattern='/status'))
        async def status_handler(event):
            self.metrics.messages_processed += 1
            await self.handle_status_command(event)
        
        @self.client.on(events.NewMessage(pattern='/stats'))
        async def stats_handler(event):
            self.metrics.messages_processed += 1
            await self.handle_status_command(event)  # Alias for status
        
        @self.client.on(events.NewMessage(pattern='/health'))
        async def health_handler(event):
            self.metrics.messages_processed += 1
            await self.handle_health_command(event)
        
        @self.client.on(events.NewMessage(pattern='/help'))
        async def help_handler(event):
            self.metrics.messages_processed += 1
            await self.handle_help_command(event)
        
        # Catch-all handler for other messages
        @self.client.on(events.NewMessage)
        async def message_handler(event):
            # Skip if already handled by command handlers
            if event.raw_text and event.raw_text.startswith('/'):
                known_commands = ['/start', '/status', '/stats', '/health', '/help']
                if not any(event.raw_text.startswith(cmd) for cmd in known_commands):
                    self.metrics.messages_processed += 1
                    await self.handle_unknown_command(event)
            else:
                # Non-command message
                self.metrics.messages_processed += 1
                await self.handle_unknown_command(event)
        
        logger.info("📋 Event handlers configured")
    
    async def run(self) -> None:
        """
        Run the admin bot.
        
        Main execution loop with proper error handling and graceful shutdown.
        """
        try:
            self._running = True
            
            # Initialize bot
            if not await self.initialize():
                logger.error("❌ Bot initialization failed")
                return
            
            # Setup event handlers
            await self.setup_event_handlers()
            
            logger.info("📱 Bot hazır ve komutları bekliyor...")
            logger.info("🔧 Authorized users", authorized_users=AUTHORIZED_USERS)
            
            print("✅ Admin Bot başarıyla başlatıldı!")
            print("📱 Bot hazır ve komutları bekliyor...")
            print("🔄 Admin Bot çalışıyor... (Ctrl+C ile durdur)")
            
            # Run until disconnected
            await self.client.run_until_disconnected()
            
        except KeyboardInterrupt:
            logger.info("⌨️ Keyboard interrupt received")
        except Exception as e:
            logger.error("❌ Bot execution error", error=str(e), exc_info=True)
            raise
        finally:
            self._running = False
            await self.cleanup()
    
    async def cleanup(self) -> None:
        """Cleanup resources and disconnect."""
        try:
            if self.client and self.client.is_connected():
                await self.client.disconnect()
                logger.info("🔌 Bot disconnected")
            
            # Final metrics
            final_metrics = self.metrics.to_dict()
            logger.info("📊 Final bot metrics", **final_metrics)
            
        except Exception as e:
            logger.warning("⚠️ Cleanup error", error=str(e))

async def main() -> None:
    """
    Ana fonksiyon - Admin bot entry point.
    
    Enhanced main function with comprehensive error handling.
    """
    print("🤖 GAVATCORE Admin Bot Başlatılıyor...")
    
    try:
        bot = AdminBot()
        await bot.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Admin Bot kullanıcı tarafından durduruldu.")
        logger.info("🛑 Admin Bot stopped by user")
        
    except Exception as e:
        print(f"\n❌ Admin Bot kritik hatası: {e}")
        logger.error("❌ Admin Bot critical error", error=str(e), exc_info=True)
        sys.exit(1)
    
    finally:
        print("👋 Admin Bot kapandı.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⌨️ Program kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Kritik sistem hatası: {e}")
        sys.exit(1) 