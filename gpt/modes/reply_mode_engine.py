#!/usr/bin/env python3
"""
🔄 GAVATCore Reply Mode Engine
=============================

Handles different reply modes for characters:
- manual: Stores message for manual reply, no automatic response
- gpt: Generates and sends GPT response immediately
- hybrid: Generates GPT response, stores for approval before sending
- manualplus: Waits for manual reply with timeout, falls back to GPT

Features:
- Asynchronous timeout handling for manualplus mode
- Message queuing and approval workflow for hybrid mode
- GPT response generation integration
- Performance monitoring and logging
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog

logger = structlog.get_logger("gavatcore.gpt.reply_mode")

class ReplyMode(Enum):
    """Reply mode enumeration."""
    MANUAL = "manual"
    GPT = "gpt"
    HYBRID = "hybrid"
    MANUALPLUS = "manualplus"

@dataclass
class PendingMessage:
    """Pending message data structure."""
    message_id: str
    character_id: str
    user_id: str
    original_message: str
    generated_response: str
    system_prompt: str
    timestamp: datetime
    expires_at: Optional[datetime] = None
    status: str = "pending"  # pending, approved, rejected, expired
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReplyModeResponse:
    """Reply mode response structure."""
    response: str
    should_send: bool
    needs_approval: bool
    message_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ReplyModeEngine:
    """
    🔄 Reply Mode Processing Engine
    
    Manages different reply modes and their specific behaviors:
    - Manual: No automatic responses
    - GPT: Immediate GPT responses
    - Hybrid: GPT + approval workflow
    - Manualplus: Manual with GPT fallback
    """
    
    def __init__(self):
        self.pending_messages: Dict[str, PendingMessage] = {}
        self.active_timeouts: Dict[str, asyncio.Task] = {}
        self.approval_handlers: Dict[str, Callable] = {}
        
        # Performance metrics
        self.mode_stats = {
            'manual': {'total': 0, 'processed': 0},
            'gpt': {'total': 0, 'processed': 0, 'avg_time': 0},
            'hybrid': {'total': 0, 'approved': 0, 'rejected': 0},
            'manualplus': {'total': 0, 'manual_replies': 0, 'gpt_fallbacks': 0}
        }
        
        # Initialize cleanup task (will be started when event loop is available)
        self._cleanup_task = None
        self._cleanup_started = False
        
        logger.info("🔄 Reply Mode Engine initialized")
    
    def _ensure_cleanup_started(self):
        """Ensure cleanup task is started when event loop is available."""
        if not self._cleanup_started:
            try:
                self._cleanup_task = asyncio.create_task(self._cleanup_expired_messages())
                self._cleanup_started = True
            except RuntimeError:
                # No event loop running, will start later
                pass
    
    async def process_message(
        self,
        character,      # CharacterProfile
        message: str,
        context,        # ConversationContext
        system_prompt: str,
        reply_mode: str,
        gpt_generator: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Process message according to reply mode.
        
        Args:
            character: Character profile
            message: User message
            context: Conversation context
            system_prompt: Generated system prompt
            reply_mode: Reply mode to use
            gpt_generator: GPT response generator function
        
        Returns:
            Response data with metadata
        """
        try:
            # Ensure cleanup task is started
            self._ensure_cleanup_started()
            
            mode = ReplyMode(reply_mode.lower())
            self.mode_stats[mode.value]['total'] += 1
            
            logger.info(f"🔄 Processing message in {mode.value} mode",
                       character=character.character_id,
                       user=context.user_id)
            
            if mode == ReplyMode.MANUAL:
                return await self._handle_manual_mode(
                    character, message, context, system_prompt
                )
            
            elif mode == ReplyMode.GPT:
                return await self._handle_gpt_mode(
                    character, message, context, system_prompt, gpt_generator
                )
            
            elif mode == ReplyMode.HYBRID:
                return await self._handle_hybrid_mode(
                    character, message, context, system_prompt, gpt_generator
                )
            
            elif mode == ReplyMode.MANUALPLUS:
                return await self._handle_manualplus_mode(
                    character, message, context, system_prompt, gpt_generator
                )
            
            else:
                raise ValueError(f"Unknown reply mode: {reply_mode}")
                
        except Exception as e:
            logger.error(f"❌ Error processing message in {reply_mode} mode: {e}")
            return {
                'response': '',
                'should_send': False,
                'error': str(e),
                'metadata': {'mode': reply_mode, 'error': True}
            }
    
    async def _handle_manual_mode(
        self,
        character,
        message: str,
        context,
        system_prompt: str
    ) -> Dict[str, Any]:
        """Handle manual reply mode - store for manual processing."""
        try:
            # Store message for manual reply
            message_data = {
                'character_id': character.character_id,
                'user_id': context.user_id,
                'username': context.username,
                'message': message,
                'system_prompt': system_prompt,
                'timestamp': datetime.now().isoformat(),
                'mode': 'manual'
            }
            
            # Here you would typically store this in a database or queue
            # For now, we'll log it
            logger.info("📝 Message stored for manual reply",
                       character=character.character_id,
                       user=context.user_id)
            
            self.mode_stats['manual']['processed'] += 1
            
            return {
                'response': '',
                'should_send': False,
                'needs_approval': False,
                'metadata': {
                    'mode': 'manual',
                    'stored': True,
                    'message_data': message_data
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in manual mode: {e}")
            raise
    
    async def _handle_gpt_mode(
        self,
        character,
        message: str,
        context,
        system_prompt: str,
        gpt_generator: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Handle GPT reply mode - generate and send immediately."""
        try:
            start_time = time.time()
            
            # Generate GPT response
            if gpt_generator:
                gpt_response = await gpt_generator(system_prompt, message)
            else:
                # Fallback to mock response
                gpt_response = await self._generate_mock_response(character, message)
            
            processing_time = time.time() - start_time
            
            # Update stats
            self.mode_stats['gpt']['processed'] += 1
            current_avg = self.mode_stats['gpt']['avg_time']
            processed = self.mode_stats['gpt']['processed']
            self.mode_stats['gpt']['avg_time'] = (current_avg * (processed - 1) + processing_time) / processed
            
            logger.info("🤖 GPT response generated",
                       character=character.character_id,
                       response_length=len(gpt_response),
                       processing_time_ms=int(processing_time * 1000))
            
            return {
                'response': gpt_response,
                'should_send': True,
                'needs_approval': False,
                'metadata': {
                    'mode': 'gpt',
                    'processing_time': processing_time,
                    'generated': True
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in GPT mode: {e}")
            raise
    
    async def _handle_hybrid_mode(
        self,
        character,
        message: str,
        context,
        system_prompt: str,
        gpt_generator: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Handle hybrid mode - generate GPT response and wait for approval."""
        try:
            # Generate GPT response
            if gpt_generator:
                gpt_response = await gpt_generator(system_prompt, message)
            else:
                gpt_response = await self._generate_mock_response(character, message)
            
            # Create pending message
            message_id = f"{character.character_id}_{context.user_id}_{int(time.time())}"
            
            pending_msg = PendingMessage(
                message_id=message_id,
                character_id=character.character_id,
                user_id=context.user_id,
                original_message=message,
                generated_response=gpt_response,
                system_prompt=system_prompt,
                timestamp=datetime.now(),
                status="pending",
                metadata={
                    'username': context.username,
                    'mode': 'hybrid'
                }
            )
            
            # Store for approval
            self.pending_messages[message_id] = pending_msg
            
            logger.info("⏳ Message pending approval",
                       message_id=message_id,
                       character=character.character_id,
                       response_preview=gpt_response[:50] + "...")
            
            return {
                'response': gpt_response,
                'should_send': False,
                'needs_approval': True,
                'message_id': message_id,
                'metadata': {
                    'mode': 'hybrid',
                    'pending': True,
                    'message_id': message_id
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in hybrid mode: {e}")
            raise
    
    async def _handle_manualplus_mode(
        self,
        character,
        message: str,
        context,
        system_prompt: str,
        gpt_generator: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Handle manualplus mode - wait for manual reply with GPT fallback."""
        try:
            timeout_sec = character.manualplus_timeout_sec
            message_id = f"{character.character_id}_{context.user_id}_{int(time.time())}"
            
            # Store message for manual reply opportunity
            message_data = {
                'character_id': character.character_id,
                'user_id': context.user_id,
                'username': context.username,
                'message': message,
                'system_prompt': system_prompt,
                'timeout_sec': timeout_sec,
                'message_id': message_id
            }
            
            # Start timeout task
            timeout_task = asyncio.create_task(
                self._manualplus_timeout_handler(
                    message_id, character, message, context, 
                    system_prompt, timeout_sec, gpt_generator
                )
            )
            
            self.active_timeouts[message_id] = timeout_task
            
            logger.info("⏰ Manual+ mode started",
                       message_id=message_id,
                       timeout_sec=timeout_sec,
                       character=character.character_id)
            
            return {
                'response': '',
                'should_send': False,
                'needs_approval': False,
                'message_id': message_id,
                'metadata': {
                    'mode': 'manualplus',
                    'waiting_manual': True,
                    'timeout_sec': timeout_sec,
                    'message_id': message_id,
                    'message_data': message_data
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in manualplus mode: {e}")
            raise
    
    async def _manualplus_timeout_handler(
        self,
        message_id: str,
        character,
        message: str,
        context,
        system_prompt: str,
        timeout_sec: int,
        gpt_generator: Optional[Callable] = None
    ) -> None:
        """Handle timeout for manualplus mode."""
        try:
            await asyncio.sleep(timeout_sec)
            
            # Check if manual reply was provided
            if message_id in self.active_timeouts:
                # No manual reply, generate GPT fallback
                logger.info("⏰ Manual+ timeout reached, generating GPT fallback",
                           message_id=message_id)
                
                if gpt_generator:
                    gpt_response = await gpt_generator(system_prompt, message)
                else:
                    gpt_response = await self._generate_mock_response(character, message)
                
                # Send GPT fallback response
                # Here you would integrate with your message sending system
                logger.info("🤖 Manual+ GPT fallback sent",
                           message_id=message_id,
                           response_length=len(gpt_response))
                
                self.mode_stats['manualplus']['gpt_fallbacks'] += 1
                
                # Cleanup
                self.active_timeouts.pop(message_id, None)
                
        except asyncio.CancelledError:
            # Manual reply was provided, timeout cancelled
            logger.info("✅ Manual+ timeout cancelled - manual reply provided",
                       message_id=message_id)
            self.mode_stats['manualplus']['manual_replies'] += 1
        
        except Exception as e:
            logger.error(f"❌ Error in manual+ timeout handler: {e}")
    
    async def provide_manual_reply(self, message_id: str, manual_response: str) -> bool:
        """Provide manual reply for manualplus mode."""
        try:
            if message_id in self.active_timeouts:
                # Cancel timeout
                self.active_timeouts[message_id].cancel()
                self.active_timeouts.pop(message_id, None)
                
                # Send manual response
                # Here you would integrate with your message sending system
                logger.info("✅ Manual reply provided",
                           message_id=message_id,
                           response_length=len(manual_response))
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error providing manual reply: {e}")
            return False
    
    async def approve_hybrid_message(self, message_id: str) -> bool:
        """Approve pending hybrid message."""
        try:
            pending_msg = self.pending_messages.get(message_id)
            if not pending_msg or pending_msg.status != "pending":
                return False
            
            pending_msg.status = "approved"
            
            # Send the approved response
            # Here you would integrate with your message sending system
            logger.info("✅ Hybrid message approved",
                       message_id=message_id,
                       response_length=len(pending_msg.generated_response))
            
            self.mode_stats['hybrid']['approved'] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error approving hybrid message: {e}")
            return False
    
    async def reject_hybrid_message(self, message_id: str, reason: str = "") -> bool:
        """Reject pending hybrid message."""
        try:
            pending_msg = self.pending_messages.get(message_id)
            if not pending_msg or pending_msg.status != "pending":
                return False
            
            pending_msg.status = "rejected"
            pending_msg.metadata['rejection_reason'] = reason
            
            logger.info("❌ Hybrid message rejected",
                       message_id=message_id,
                       reason=reason)
            
            self.mode_stats['hybrid']['rejected'] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error rejecting hybrid message: {e}")
            return False
    
    async def edit_hybrid_message(self, message_id: str, edited_response: str) -> bool:
        """Edit and approve hybrid message."""
        try:
            pending_msg = self.pending_messages.get(message_id)
            if not pending_msg or pending_msg.status != "pending":
                return False
            
            pending_msg.generated_response = edited_response
            pending_msg.status = "approved"
            pending_msg.metadata['edited'] = True
            
            # Send the edited response
            # Here you would integrate with your message sending system
            logger.info("✏️ Hybrid message edited and approved",
                       message_id=message_id,
                       new_length=len(edited_response))
            
            self.mode_stats['hybrid']['approved'] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error editing hybrid message: {e}")
            return False
    
    def get_pending_messages(self, character_id: Optional[str] = None) -> List[PendingMessage]:
        """Get list of pending messages."""
        messages = list(self.pending_messages.values())
        
        if character_id:
            messages = [msg for msg in messages if msg.character_id == character_id]
        
        # Filter only pending messages
        return [msg for msg in messages if msg.status == "pending"]
    
    def get_mode_statistics(self) -> Dict[str, Any]:
        """Get reply mode statistics."""
        return {
            'mode_stats': self.mode_stats.copy(),
            'pending_messages': len(self.pending_messages),
            'active_timeouts': len(self.active_timeouts),
            'total_processed': sum(
                mode_data.get('total', 0) 
                for mode_data in self.mode_stats.values()
            )
        }
    
    async def _generate_mock_response(self, character, message: str) -> str:
        """Generate mock response when no GPT generator is provided."""
        responses = [
            f"Merhaba! {character.display_name} olarak size yanıt veriyorum. 😊",
            f"Bu konuyla ilgili {character.display_name} olarak ne düşünüyorum... 🤔",
            f"İlginç bir soru! {character.display_name} perspektifinden bakarsak... ✨"
        ]
        
        import random
        return random.choice(responses) + f" (Mock response for: {message[:30]}...)"
    
    async def _cleanup_expired_messages(self) -> None:
        """Cleanup expired pending messages."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                current_time = datetime.now()
                expired_messages = []
                
                for message_id, pending_msg in self.pending_messages.items():
                    # Remove messages older than 1 hour
                    if current_time - pending_msg.timestamp > timedelta(hours=1):
                        expired_messages.append(message_id)
                
                for message_id in expired_messages:
                    self.pending_messages.pop(message_id, None)
                    logger.debug(f"🧹 Cleaned up expired message: {message_id}")
                
                if expired_messages:
                    logger.info(f"🧹 Cleaned up {len(expired_messages)} expired messages")
                    
            except Exception as e:
                logger.error(f"❌ Error in cleanup task: {e}")
                await asyncio.sleep(60) 