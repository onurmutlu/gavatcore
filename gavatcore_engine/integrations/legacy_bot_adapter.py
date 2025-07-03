"""
Legacy Bot Adapter
==================

Adapter to integrate existing GavatCore bots with the new FastAPI engine.
"""

import asyncio
import json
import os
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from pathlib import Path

from telethon import TelegramClient, events
from telethon.tl.types import User

from ..config import get_settings
from ..logger import LoggerMixin
from ..redis_state import redis_state
from ..message_pool import message_pool, Message, MessageType, MessagePriority
from ..telegram_client import TelegramClientManager
from ..ai_blending import ai_blending


class LegacyBotAdapter(LoggerMixin):
    """Adapter to integrate existing GavatCore bots with new engine."""
    
    def __init__(self):
        self.settings = get_settings()
        self.bot_instances: Dict[str, Dict[str, Any]] = {}
        self.legacy_clients: Dict[str, TelegramClient] = {}
        self.engine_clients: Dict[str, TelegramClientManager] = {}
        self.is_running = False
        
        # Load bot configurations from existing persona files
        self.bot_configs = self._load_bot_configs()
    
    def _load_bot_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load bot configurations from existing persona files."""
        configs = {}
        persona_dir = Path("data/personas")
        
        if not persona_dir.exists():
            self.log_warning("Persona directory not found", path=str(persona_dir))
            return configs
        
        # Load known bots according to memory
        bot_files = {
            "yayincilara": "yayincilara.json",
            "xxxgeisha": "xxxgeisha.json",
        }
        
        for bot_name, filename in bot_files.items():
            persona_file = persona_dir / filename
            
            if persona_file.exists():
                try:
                    with open(persona_file, 'r', encoding='utf-8') as f:
                        persona_data = json.load(f)
                    
                    configs[bot_name] = {
                        "username": bot_name,
                        "display_name": persona_data.get("display_name", bot_name),
                        "phone": persona_data.get("phone"),
                        "telegram_handle": persona_data.get("telegram_handle"),
                        "user_id": persona_data.get("user_id"),
                        "persona_data": persona_data,
                        "session_paths": self._get_session_paths(persona_data.get("phone", "")),
                        "enabled": True,  # BabaGavat banned according to memory
                    }
                    
                    self.log_event(
                        "Bot config loaded",
                        bot_name=bot_name,
                        phone=persona_data.get("phone"),
                    )
                    
                except Exception as e:
                    self.log_error(f"Failed to load persona for {bot_name}", error=str(e))
            else:
                self.log_warning(f"Persona file not found for {bot_name}", file=str(persona_file))
        
        return configs
    
    def _get_session_paths(self, phone: str) -> List[str]:
        """Get possible session file paths for a phone number."""
        if not phone:
            return []
        
        clean_phone = phone.replace('+', '')
        
        # Multiple possible session paths based on existing patterns
        paths = [
            f"sessions/_{clean_phone}.session",
            f"sessions/{clean_phone}.session",
            f"sessions/yayincilara_conversation.session",
            f"sessions/xxxgeisha_conversation.session",
            f"sessions/geishaniz_conversation.session",
        ]
        
        # Return existing paths
        return [path for path in paths if os.path.exists(path)]
    
    async def initialize(self) -> None:
        """Initialize the adapter and connect to existing bots."""
        self.log_event("Initializing legacy bot adapter")
        
        # Connect to Redis
        await redis_state.connect()
        
        # Initialize each bot
        for bot_name, config in self.bot_configs.items():
            if config["enabled"]:
                await self._initialize_bot(bot_name, config)
        
        self.is_running = True
        self.log_event("Legacy bot adapter initialized", active_bots=len(self.bot_instances))
    
    async def _initialize_bot(self, bot_name: str, config: Dict[str, Any]) -> bool:
        """Initialize a single bot."""
        try:
            self.log_event("Initializing bot", bot_name=bot_name)
            
            # Find existing session
            session_paths = config["session_paths"]
            if not session_paths:
                self.log_error("No session files found", bot_name=bot_name)
                return False
            
            session_path = session_paths[0]  # Use first available
            session_name = session_path.replace('.session', '')
            
            # Create legacy Telegram client (for compatibility)
            legacy_client = TelegramClient(
                session_name,
                self.settings.telegram_api_id,
                self.settings.telegram_api_hash,
                device_model=f"GavatCore Legacy - {config['display_name']}",
                system_version="2.0.0",
                app_version="GavatCore Engine v1.0",
            )
            
            # Connect legacy client
            await legacy_client.start()
            me = await legacy_client.get_me()
            
            # Create engine client wrapper
            engine_client = TelegramClientManager(session_name, bot_name)
            engine_client.client = legacy_client  # Use same underlying client
            engine_client.is_connected = True
            engine_client.user_info = me
            
            # Store session info in Redis
            await engine_client._store_session_info()
            
            # Store clients
            self.legacy_clients[bot_name] = legacy_client
            self.engine_clients[bot_name] = engine_client
            
            # Setup event handlers
            await self._setup_bot_handlers(bot_name, legacy_client)
            
            # Store bot instance info
            self.bot_instances[bot_name] = {
                "config": config,
                "legacy_client": legacy_client,
                "engine_client": engine_client,
                "user_info": me,
                "session_path": session_path,
                "initialized_at": datetime.utcnow(),
            }
            
            self.log_event(
                "Bot initialized successfully",
                bot_name=bot_name,
                username=me.username,
                user_id=me.id,
                session_path=session_path,
            )
            
            return True
            
        except Exception as e:
            self.log_error(
                "Failed to initialize bot",
                bot_name=bot_name,
                error=str(e),
            )
            return False
    
    async def _setup_bot_handlers(self, bot_name: str, client: TelegramClient) -> None:
        """Setup event handlers for a bot."""
        
        @client.on(events.NewMessage(incoming=True))
        async def message_handler(event):
            """Handle incoming messages and route to engine."""
            try:
                await self._handle_incoming_message(bot_name, event)
            except Exception as e:
                self.log_error(
                    "Message handler error",
                    bot_name=bot_name,
                    error=str(e),
                )
        
        self.log_event("Event handlers setup", bot_name=bot_name)
    
    async def _handle_incoming_message(self, bot_name: str, event) -> None:
        """Handle incoming message and integrate with engine."""
        try:
            # Get sender info
            sender = await event.get_sender()
            if not sender or getattr(sender, 'bot', False):
                return  # Skip bot messages
            
            # Determine message type
            if event.is_private:
                message_type = MessageType.DIRECT_MESSAGE
                target_id = sender.id
                target_username = getattr(sender, 'username', None)
            elif event.is_group:
                message_type = MessageType.GROUP_MESSAGE
                target_id = event.chat_id
                target_username = None
            else:
                return  # Skip channels for now
            
            # Log incoming message
            self.log_event(
                "Incoming message",
                bot_name=bot_name,
                sender_id=sender.id,
                sender_name=getattr(sender, 'first_name', 'Unknown'),
                message_type=message_type.value,
                text_preview=event.raw_text[:50] if event.raw_text else "Media",
            )
            
            # Generate AI response if it's a DM
            if message_type == MessageType.DIRECT_MESSAGE and event.raw_text:
                await self._generate_and_queue_response(
                    bot_name=bot_name,
                    user_message=event.raw_text,
                    user_id=sender.id,
                    target_chat_id=target_id,
                    target_username=target_username,
                )
            
        except Exception as e:
            self.log_error(
                "Failed to handle incoming message",
                bot_name=bot_name,
                error=str(e),
            )
    
    async def _generate_and_queue_response(
        self,
        bot_name: str,
        user_message: str,
        user_id: int,
        target_chat_id: int,
        target_username: Optional[str],
    ) -> None:
        """Generate AI response and queue it for sending."""
        try:
            # Generate AI response
            ai_response = await ai_blending.generate_response(
                bot_username=bot_name,
                user_message=user_message,
                conversation_context={},
                user_profile={"user_id": user_id},
            )
            
            if not ai_response or not ai_response.get("content"):
                self.log_warning("No AI response generated", bot_name=bot_name)
                return
            
            # Create message for queue
            message = Message(
                type=MessageType.DIRECT_MESSAGE,
                priority=MessagePriority.HIGH,  # DM responses are high priority
                content=ai_response["content"],
                target_chat_id=target_chat_id,
                target_username=target_username,
                bot_id=bot_name,
                context={
                    "ai_response": ai_response,
                    "original_message": user_message,
                    "user_id": user_id,
                    "generated_via": "legacy_adapter",
                },
            )
            
            # Add to message pool
            message_id = await message_pool.add_message(message)
            
            # Update conversation context
            await ai_blending.update_conversation_context(
                bot_username=bot_name,
                user_id=user_id,
                message=user_message,
                response=ai_response["content"],
            )
            
            self.log_event(
                "AI response queued",
                bot_name=bot_name,
                message_id=message_id,
                user_id=user_id,
                response_length=len(ai_response["content"]),
            )
            
        except Exception as e:
            self.log_error(
                "Failed to generate and queue response",
                bot_name=bot_name,
                error=str(e),
            )
    
    async def send_message_via_legacy(
        self,
        bot_name: str,
        message: Message,
    ) -> bool:
        """Send message using legacy client."""
        try:
            bot_instance = self.bot_instances.get(bot_name)
            if not bot_instance:
                self.log_error("Bot instance not found", bot_name=bot_name)
                return False
            
            legacy_client = bot_instance["legacy_client"]
            
            # Determine target
            if message.target_chat_id:
                target = message.target_chat_id
            elif message.target_username:
                target = message.target_username
            else:
                self.log_error("No target specified for message", message_id=message.id)
                return False
            
            # Send message
            sent_message = await legacy_client.send_message(
                entity=target,
                message=message.content,
                parse_mode='markdown',
                link_preview=False,
            )
            
            self.log_event(
                "Message sent via legacy client",
                bot_name=bot_name,
                message_id=message.id,
                sent_message_id=sent_message.id,
                target=str(target),
            )
            
            return True
            
        except Exception as e:
            self.log_error(
                "Failed to send message via legacy client",
                bot_name=bot_name,
                message_id=message.id,
                error=str(e),
            )
            return False
    
    async def get_bot_status(self) -> Dict[str, Any]:
        """Get status of all bots."""
        status = {
            "adapter_running": self.is_running,
            "total_bots": len(self.bot_configs),
            "active_bots": len(self.bot_instances),
            "bots": {},
        }
        
        for bot_name, instance in self.bot_instances.items():
            client = instance["legacy_client"]
            user_info = instance["user_info"]
            
            # Check if client is connected
            try:
                is_connected = client.is_connected()
                me = await client.get_me() if is_connected else None
            except:
                is_connected = False
                me = None
            
            status["bots"][bot_name] = {
                "display_name": instance["config"]["display_name"],
                "username": user_info.username if user_info else None,
                "user_id": user_info.id if user_info else None,
                "phone": instance["config"]["phone"],
                "connected": is_connected,
                "session_path": instance["session_path"],
                "initialized_at": instance["initialized_at"].isoformat(),
            }
        
        return status
    
    async def shutdown(self) -> None:
        """Shutdown all bot connections."""
        self.log_event("Shutting down legacy bot adapter")
        
        for bot_name, client in self.legacy_clients.items():
            try:
                await client.disconnect()
                self.log_event("Bot disconnected", bot_name=bot_name)
            except Exception as e:
                self.log_error("Failed to disconnect bot", bot_name=bot_name, error=str(e))
        
        self.is_running = False
        self.bot_instances.clear()
        self.legacy_clients.clear()
        self.engine_clients.clear()
        
        self.log_event("Legacy bot adapter shutdown complete")


# Global legacy bot adapter instance
legacy_adapter = LegacyBotAdapter() 