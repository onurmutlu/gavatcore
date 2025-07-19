from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
📱 GAVATCORE USERBOT SESSION MANAGER
Individual session management for each bot
"""

import asyncio
import os
from typing import Dict, Any, Optional
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
import structlog

logger = structlog.get_logger("gavatcore.session")

class UserbotSession:
    """Individual userbot session manager"""
    
    def __init__(self, bot_name: str, config: Dict[str, Any], health_monitor: Any):
        self.bot_name = bot_name
        self.config = config
        self.health_monitor = health_monitor
        self.client: Optional[TelegramClient] = None
        self.is_running = False
        
        # Session file path
        self.session_path = f"sessions/{bot_name}.session"
        
        # Ensure sessions directory exists
        os.makedirs("sessions", exist_ok=True)
    
    async def initialize(self):
        """Initialize Telegram client"""
        try:
            logger.info(f"🔧 Initializing {self.bot_name} session...")
            
            # Get Telegram credentials from environment
            from utils.config_manager import ConfigManager
            config_manager = ConfigManager()
            
            api_id = config_manager.get('TELEGRAM_API_ID')
            api_hash = config_manager.get('TELEGRAM_API_HASH')
            
            if not api_id or not api_hash:
                raise ValueError("Telegram API credentials not found in environment")
            
            # Create Telegram client
            self.client = TelegramClient(
                session=self.session_path,
                api_id=int(api_id),
                api_hash=api_hash,
                device_model=f"GavatCore-{self.bot_name}",
                system_version="Ubuntu 22.04",
                app_version="3.0",
                lang_code="tr",
                system_lang_code="tr"
            )
            
            logger.info(f"✅ {self.bot_name} client initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.bot_name}: {str(e)}")
            raise
    
    async def start(self):
        """Start the userbot session"""
        try:
            if not self.client:
                raise RuntimeError(f"{self.bot_name} client not initialized")
            
            logger.info(f"🚀 Starting {self.bot_name} session...")
            
            # Connect to Telegram
            await self.client.connect()
            
            # Check if already authorized
            if not await self.client.is_user_authorized():
                logger.info(f"📱 {self.bot_name} requires phone authorization")
                await self._handle_authorization()
            
            # Start the client (no await needed for start method)
            await self.client.start()
            
            # Setup event handlers
            self._setup_handlers()
            
            self.is_running = True
            logger.info(f"✅ {self.bot_name} session started successfully")
            
            # Keep session alive
            await self._keep_alive()
            
        except Exception as e:
            logger.error(f"❌ Failed to start {self.bot_name}: {str(e)}")
            raise
    
    async def _handle_authorization(self):
        """Handle phone authorization process"""
        try:
            phone = self.config.get('phone')
            if not phone:
                raise ValueError(f"Phone number not configured for {self.bot_name}")
            
            logger.info(f"📞 Sending code to {phone}...")
            
            # This would normally prompt for code input
            # In production, you'd need to handle this differently
            # For now, we'll assume the session file exists
            logger.warning(f"⚠️ {self.bot_name} requires manual authorization")
            logger.warning("Please run the session setup separately first")
            
        except Exception as e:
            logger.error(f"❌ Authorization failed for {self.bot_name}: {str(e)}")
            raise
    
    def _setup_handlers(self):
        """Setup event handlers based on bot role"""
        try:
            if not self.client:
                raise RuntimeError("Client not initialized")
                
            role = self.config.get('role', 'unknown')
            handlers = self.config.get('handlers', [])
            
            logger.info(f"🎭 Setting up handlers for {self.bot_name}", 
                       role=role, handlers=handlers)
            
            # Import and setup handlers based on role
            if 'admin_handler' in handlers:
                self._setup_admin_handlers()
            
            if 'gpt_handler' in handlers:
                self._setup_gpt_handlers()
            
            if 'common_handler' in handlers:
                self._setup_common_handlers()
            
            if 'coin_handler' in handlers:
                self._setup_coin_handlers()
            
            logger.info(f"✅ Handlers setup complete for {self.bot_name}")
            
        except Exception as e:
            logger.error(f"❌ Handler setup failed for {self.bot_name}: {str(e)}")
            raise
    
    def _setup_admin_handlers(self):
        """Setup admin command handlers"""
        if not self.client:
            return
        
        try:
            from handlers.admin_handler import AdminHandler
            
            admin_handler = AdminHandler(self.client, self.bot_name, self.config)
            admin_handler.register_handlers()
            
            logger.info(f"✅ Admin handlers registered for {self.bot_name}")
            
        except Exception as e:
            logger.error(f"❌ Admin handler setup error: {e}")
    
    def _setup_gpt_handlers(self):
        """Setup GPT response handlers"""
        if not self.client:
            return
        
        try:
            from handlers.gpt_handler import GPTHandler
            
            gpt_handler = GPTHandler(self.client, self.bot_name, self.config)
            gpt_handler.register_handlers()
            
            logger.info(f"✅ GPT handlers registered for {self.bot_name}")
            
        except Exception as e:
            logger.error(f"❌ GPT handler setup error: {e}")
    
    def _setup_common_handlers(self):
        """Setup common event handlers"""
        if not self.client:
            return
        
        try:
            from handlers.common_handler import CommonHandler
            
            common_handler = CommonHandler(self.client, self.bot_name, self.config)
            common_handler.register_handlers()
            
            logger.info(f"✅ Common handlers registered for {self.bot_name}")
            
        except Exception as e:
            logger.error(f"❌ Common handler setup error: {e}")
    
    def _setup_coin_handlers(self):
        """Setup coin system handlers"""
        if not self.client:
            return
        
        try:
            from utils.coin_checker import CoinChecker
            from telethon import events
            
            coin_checker = CoinChecker()
            
            @self.client.on(events.NewMessage(pattern=r'^/balance$'))
            async def cmd_balance(event):
                try:
                    balance_data = await coin_checker.check_user_balance(event.sender_id)
                    
                    if balance_data.get('success'):
                        balance_msg = f"""
💰 **COIN BAKİYELERİ**

👤 **Kullanıcı ID**: {balance_data['user_id']}
💎 **Bakiye**: {balance_data['balance']} {balance_data['currency']}
🎯 **Seviye**: {balance_data['tier'].upper()}
📊 **Durum**: {balance_data['status'].upper()}

⏰ **Son Güncelleme**: {balance_data['last_update'][:16]}
                        """
                        await event.respond(balance_msg)
                    else:
                        await event.respond("❌ Bakiye bilgisi alınamadı.")
                        
                except Exception as e:
                    logger.error(f"❌ Balance command error: {e}")
                    await event.respond("❌ Bir hata oluştu.")
            
            logger.info(f"✅ Coin handlers registered for {self.bot_name}")
            
        except Exception as e:
            logger.error(f"❌ Coin handler setup error: {e}")
    
    async def _keep_alive(self):
        """Keep the session alive"""
        try:
            while self.is_running:
                await asyncio.sleep(60)  # Check every minute
                
                # Health check
                if self.client and not self.client.is_connected():
                    logger.warning(f"⚠️ {self.bot_name} disconnected, reconnecting...")
                    await self.client.connect()
                    
        except asyncio.CancelledError:
            logger.info(f"🛑 {self.bot_name} keep-alive cancelled")
        except Exception as e:
            logger.error(f"❌ Keep-alive error for {self.bot_name}: {str(e)}")
    
    async def stop(self):
        """Stop the session gracefully"""
        try:
            logger.info(f"🛑 Stopping {self.bot_name} session...")
            
            self.is_running = False
            
            if self.client and self.client.is_connected():
                await self.client.disconnect()
            
            logger.info(f"✅ {self.bot_name} session stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping {self.bot_name}: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get session status"""
        return {
            'bot_name': self.bot_name,
            'is_running': self.is_running,
            'is_connected': self.client.is_connected() if self.client else False,
            'role': self.config.get('role'),
            'phone': self.config.get('phone'),
            'session_file': self.session_path
        } 