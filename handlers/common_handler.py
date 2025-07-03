#!/usr/bin/env python3
"""
🔄 GAVATCORE COMMON HANDLER
Common event handlers for all bots
"""

import asyncio
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime
import structlog

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telethon import events
from telethon.tl.types import Message, User

logger = structlog.get_logger("gavatcore.common_handler")

class CommonHandler:
    """Common event handler for all bots"""
    
    def __init__(self, client, bot_name: str, config: Dict[str, Any]):
        self.client = client
        self.bot_name = bot_name
        self.config = config
        self.message_count = 0
        self.start_time = datetime.now()
        
    def register_handlers(self):
        """Register common event handlers"""
        logger.info(f"🔄 Registering common handlers for {self.bot_name}")
        
        # Connection events
        self.client.on(events.Raw)(self.handle_raw_update)
        
        # User events
        self.client.on(events.UserUpdate)(self.handle_user_update)
        
        # Message events
        self.client.on(events.MessageRead)(self.handle_message_read)
        self.client.on(events.MessageDeleted)(self.handle_message_deleted)
        
        # Chat events
        self.client.on(events.ChatAction)(self.handle_chat_action)
        
        logger.info(f"✅ Common handlers registered for {self.bot_name}")
    
    async def handle_raw_update(self, event):
        """Handle raw Telegram updates"""
        try:
            # Log only important updates to avoid spam
            update_type = type(event.original_update).__name__
            
            if update_type in ['UpdateNewMessage', 'UpdateUserStatus']:
                logger.debug(f"📡 Raw update received", 
                           bot=self.bot_name,
                           update_type=update_type)
                           
        except Exception as e:
            logger.error(f"❌ Raw update error: {e}")
    
    async def handle_user_update(self, event):
        """Handle user status updates"""
        try:
            if hasattr(event, 'user_id') and hasattr(event, 'status'):
                logger.debug(f"👤 User status update", 
                           bot=self.bot_name,
                           user_id=event.user_id)
                           
        except Exception as e:
            logger.error(f"❌ User update error: {e}")
    
    async def handle_message_read(self, event):
        """Handle message read events"""
        try:
            logger.debug(f"📖 Message read event", 
                       bot=self.bot_name,
                       chat_id=getattr(event, 'chat_id', None))
                       
        except Exception as e:
            logger.error(f"❌ Message read error: {e}")
    
    async def handle_message_deleted(self, event):
        """Handle message deletion events"""
        try:
            logger.info(f"🗑️ Message deleted", 
                       bot=self.bot_name,
                       chat_id=getattr(event, 'chat_id', None),
                       deleted_count=len(getattr(event, 'deleted_ids', [])))
                       
        except Exception as e:
            logger.error(f"❌ Message deleted error: {e}")
    
    async def handle_chat_action(self, event):
        """Handle chat action events (user join/leave, etc.)"""
        try:
            action_type = type(event.action_message.action).__name__
            
            logger.info(f"💬 Chat action", 
                       bot=self.bot_name,
                       action=action_type,
                       chat_id=event.chat_id)
            
            # Handle specific actions
            if 'Join' in action_type:
                await self._handle_user_join(event)
            elif 'Left' in action_type:
                await self._handle_user_leave(event)
                
        except Exception as e:
            logger.error(f"❌ Chat action error: {e}")
    
    async def _handle_user_join(self, event):
        """Handle user joining chat"""
        try:
            # Welcome message logic could go here
            logger.info(f"👋 User joined chat", 
                       bot=self.bot_name,
                       chat_id=event.chat_id)
                       
        except Exception as e:
            logger.error(f"❌ User join handling error: {e}")
    
    async def _handle_user_leave(self, event):
        """Handle user leaving chat"""
        try:
            logger.info(f"👋 User left chat", 
                       bot=self.bot_name,
                       chat_id=event.chat_id)
                       
        except Exception as e:
            logger.error(f"❌ User leave handling error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get handler statistics"""
        uptime = datetime.now() - self.start_time
        
        return {
            'bot_name': self.bot_name,
            'message_count': self.message_count,
            'uptime_seconds': uptime.total_seconds(),
            'start_time': self.start_time.isoformat(),
            'handlers_active': True
        } 