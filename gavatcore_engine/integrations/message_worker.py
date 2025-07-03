"""
Enhanced Message Worker
======================

Message worker that integrates with legacy bots and new engine.
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from ..logger import LoggerMixin
from ..message_pool import message_pool, Message, MessageStatus
from ..redis_state import redis_state
from .legacy_bot_adapter import legacy_adapter


class EnhancedMessageWorker(LoggerMixin):
    """Enhanced message worker with legacy bot integration."""
    
    def __init__(self, worker_id: str = "main"):
        self.worker_id = worker_id
        self.is_running = False
        self.processed_count = 0
        self.error_count = 0
        self.start_time: Optional[datetime] = None
        
    async def start(self) -> None:
        """Start the enhanced message worker."""
        self.log_event("Starting enhanced message worker", worker_id=self.worker_id)
        
        self.is_running = True
        self.start_time = datetime.utcnow()
        
        # Start processing loop
        await self._process_messages()
    
    async def stop(self) -> None:
        """Stop the message worker."""
        self.log_event("Stopping enhanced message worker", worker_id=self.worker_id)
        self.is_running = False
    
    async def _process_messages(self) -> None:
        """Main message processing loop."""
        while self.is_running:
            try:
                # Get next message from queue
                message = await message_pool.get_next_message()
                
                if message:
                    await self._process_single_message(message)
                    self.processed_count += 1
                else:
                    # No messages, wait a bit
                    await asyncio.sleep(1.0)
                    
            except Exception as e:
                self.log_error(
                    "Message processing loop error",
                    worker_id=self.worker_id,
                    error=str(e),
                )
                self.error_count += 1
                await asyncio.sleep(5.0)  # Wait before retrying
    
    async def _process_single_message(self, message: Message) -> None:
        """Process a single message."""
        try:
            self.log_event(
                "Processing message",
                worker_id=self.worker_id,
                message_id=message.id,
                bot_id=message.bot_id,
                type=message.type.value,
                priority=message.priority.value,
            )
            
            # Mark message as processing
            await message_pool.update_message_status(message.id, MessageStatus.PROCESSING)
            
            # Determine how to send the message
            success = False
            
            # Try legacy bot adapter first
            if message.bot_id and legacy_adapter.is_running:
                if message.bot_id in legacy_adapter.bot_instances:
                    success = await legacy_adapter.send_message_via_legacy(
                        message.bot_id, message
                    )
                    
                    if success:
                        self.log_event(
                            "Message sent via legacy adapter",
                            message_id=message.id,
                            bot_id=message.bot_id,
                        )
            
            # If legacy adapter failed or not available, try engine clients
            if not success and message.bot_id:
                engine_client = legacy_adapter.engine_clients.get(message.bot_id)
                if engine_client and engine_client.is_connected:
                    success = await self._send_via_engine_client(engine_client, message)
                    
                    if success:
                        self.log_event(
                            "Message sent via engine client",
                            message_id=message.id,
                            bot_id=message.bot_id,
                        )
            
            # Update message status
            if success:
                await message_pool.update_message_status(
                    message.id, 
                    MessageStatus.COMPLETED,
                    {"sent_at": datetime.utcnow().isoformat()}
                )
                
                # Update bot stats
                await redis_state.increment_bot_stat(message.bot_id, "messages_sent")
                
            else:
                # Handle failure
                await self._handle_message_failure(message)
                
        except Exception as e:
            self.log_error(
                "Failed to process message",
                worker_id=self.worker_id,
                message_id=message.id,
                error=str(e),
            )
            await self._handle_message_failure(message)
    
    async def _send_via_engine_client(
        self, 
        client_manager, 
        message: Message
    ) -> bool:
        """Send message via engine client."""
        try:
            if not client_manager.client:
                return False
            
            # Determine target
            if message.target_chat_id:
                target = message.target_chat_id
            elif message.target_username:
                target = message.target_username
            else:
                return False
            
            # Send message
            sent_message = await client_manager.client.send_message(
                entity=target,
                message=message.content,
                parse_mode='markdown',
                link_preview=False,
            )
            
            return True
            
        except Exception as e:
            self.log_error(
                "Failed to send via engine client",
                message_id=message.id,
                error=str(e),
            )
            return False
    
    async def _handle_message_failure(self, message: Message) -> None:
        """Handle message sending failure."""
        try:
            # Increment attempt count
            message.attempt_count += 1
            
            # Check if we should retry
            max_retries = 3
            if message.attempt_count < max_retries:
                # Calculate retry delay (exponential backoff)
                delay_minutes = 2 ** message.attempt_count
                retry_at = datetime.utcnow() + timedelta(minutes=delay_minutes)
                
                await message_pool.update_message_status(
                    message.id,
                    MessageStatus.PENDING,
                    {
                        "retry_at": retry_at.isoformat(),
                        "attempt_count": message.attempt_count,
                        "last_error": "Send failed",
                    }
                )
                
                self.log_event(
                    "Message scheduled for retry",
                    message_id=message.id,
                    attempt=message.attempt_count,
                    retry_at=retry_at.isoformat(),
                )
                
            else:
                # Max retries exceeded
                await message_pool.update_message_status(
                    message.id,
                    MessageStatus.FAILED,
                    {
                        "final_error": "Max retries exceeded",
                        "attempt_count": message.attempt_count,
                        "failed_at": datetime.utcnow().isoformat(),
                    }
                )
                
                self.log_error(
                    "Message failed permanently",
                    message_id=message.id,
                    attempts=message.attempt_count,
                )
                
                # Update bot stats
                await redis_state.increment_bot_stat(message.bot_id, "messages_failed")
                
        except Exception as e:
            self.log_error(
                "Failed to handle message failure",
                message_id=message.id,
                error=str(e),
            )
    
    async def get_worker_stats(self) -> Dict[str, Any]:
        """Get worker statistics."""
        uptime = None
        if self.start_time:
            uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            "worker_id": self.worker_id,
            "is_running": self.is_running,
            "processed_count": self.processed_count,
            "error_count": self.error_count,
            "uptime_seconds": uptime,
            "start_time": self.start_time.isoformat() if self.start_time else None,
        }


# Global enhanced message worker
enhanced_worker = EnhancedMessageWorker() 