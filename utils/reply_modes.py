from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🔄 GAVATCORE REPLY MODES
Different reply modes for bot interactions
"""

import asyncio
import random
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import structlog

logger = structlog.get_logger("gavatcore.reply_modes")

class ReplyMode(Enum):
    """Reply mode enumeration"""
    MANUAL = "manual"
    GPT = "gpt"
    HYBRID = "hybrid"
    MANUALPLUS = "manualplus"

class ReplyModeManager:
    """Manages different reply modes for bots"""
    
    def __init__(self, bot_name: str, config: Dict[str, Any]):
        self.bot_name = bot_name
        self.config = config
        self.current_mode = ReplyMode(config.get('reply_mode', 'manual'))
        
        # Pending responses for hybrid mode
        self.pending_responses = {}
        
        # ManualPlus timers
        self.manualplus_timers = {}
        
        # Mode-specific settings
        self.mode_settings = {
            ReplyMode.HYBRID: {
                'approval_timeout': 60,  # seconds
                'auto_approve_after': 120  # auto approve if no response
            },
            ReplyMode.MANUALPLUS: {
                'timeout': config.get('manualplus_timeout_sec', 45),
                'max_queued': 5
            }
        }
    
    async def process_message(self, event, gpt_handler: Any = None) -> bool:
        """Process message based on current reply mode"""
        try:
            if self.current_mode == ReplyMode.MANUAL:
                return await self._process_manual(event)
            
            elif self.current_mode == ReplyMode.GPT:
                return await self._process_gpt(event, gpt_handler)
            
            elif self.current_mode == ReplyMode.HYBRID:
                return await self._process_hybrid(event, gpt_handler)
            
            elif self.current_mode == ReplyMode.MANUALPLUS:
                return await self._process_manualplus(event, gpt_handler)
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Reply mode processing error: {e}")
            return False
    
    async def _process_manual(self, event) -> bool:
        """Manual mode: No automatic responses"""
        logger.debug(f"📝 Manual mode - message logged only")
        return False  # No automatic response
    
    async def _process_gpt(self, event, gpt_handler) -> bool:
        """GPT mode: Automatic GPT responses"""
        if not gpt_handler:
            return False
        
        try:
            response = await gpt_handler._generate_gpt_response(event)
            
            if response:
                # Add natural delay
                delay = random.uniform(1.5, 4.0)
                await asyncio.sleep(delay)
                
                await event.respond(response)
                logger.info(f"🤖 GPT auto-response sent")
                return True
                
        except Exception as e:
            logger.error(f"❌ GPT mode error: {e}")
        
        return False
    
    async def _process_hybrid(self, event, gpt_handler) -> bool:
        """Hybrid mode: GPT prepares, admin approves"""
        if not gpt_handler:
            return False
        
        try:
            response = await gpt_handler._generate_gpt_response(event)
            
            if response:
                # Store pending response
                response_id = f"hybrid_{event.sender_id}_{datetime.now().timestamp()}"
                
                self.pending_responses[response_id] = {
                    'event': event,
                    'response': response,
                    'timestamp': datetime.now(),
                    'approved': False
                }
                
                # TODO: Send to admin channel for approval
                logger.info(f"🤝 Hybrid response pending approval", 
                           response_id=response_id,
                           preview=response[:50])
                
                # Auto-approve after timeout (fallback)
                timeout = self.mode_settings[ReplyMode.HYBRID]['auto_approve_after']
                asyncio.create_task(self._auto_approve_hybrid(response_id, timeout))
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Hybrid mode error: {e}")
        
        return False
    
    async def _process_manualplus(self, event, gpt_handler) -> bool:
        """ManualPlus mode: Auto-send after timeout"""
        if not gpt_handler:
            return False
        
        try:
            response = await gpt_handler._generate_gpt_response(event)
            
            if response:
                timeout = self.mode_settings[ReplyMode.MANUALPLUS]['timeout']
                
                # Create timer for auto-send
                timer_id = f"manualplus_{event.sender_id}_{datetime.now().timestamp()}"
                
                self.manualplus_timers[timer_id] = {
                    'event': event,
                    'response': response,
                    'timestamp': datetime.now(),
                    'timeout': timeout
                }
                
                logger.info(f"⏰ ManualPlus timer started", 
                           timer_id=timer_id,
                           timeout=timeout)
                
                # Schedule auto-send
                asyncio.create_task(self._auto_send_manualplus(timer_id))
                
                return True
                
        except Exception as e:
            logger.error(f"❌ ManualPlus mode error: {e}")
        
        return False
    
    async def _auto_approve_hybrid(self, response_id: str, timeout: int):
        """Auto-approve hybrid response after timeout"""
        try:
            await asyncio.sleep(timeout)
            
            if response_id in self.pending_responses:
                pending = self.pending_responses[response_id]
                
                if not pending['approved']:
                    # Auto-approve and send
                    await pending['event'].respond(pending['response'])
                    
                    logger.info(f"🕐 Hybrid response auto-approved", 
                               response_id=response_id)
                    
                    # Clean up
                    del self.pending_responses[response_id]
                    
        except Exception as e:
            logger.error(f"❌ Hybrid auto-approve error: {e}")
    
    async def _auto_send_manualplus(self, timer_id: str):
        """Auto-send ManualPlus response after timeout"""
        try:
            if timer_id not in self.manualplus_timers:
                return
            
            timer_data = self.manualplus_timers[timer_id]
            timeout = timer_data['timeout']
            
            await asyncio.sleep(timeout)
            
            # Check if timer still exists (might be cancelled)
            if timer_id in self.manualplus_timers:
                await timer_data['event'].respond(timer_data['response'])
                
                logger.info(f"⏰ ManualPlus response auto-sent", 
                           timer_id=timer_id)
                
                # Clean up
                del self.manualplus_timers[timer_id]
                
        except Exception as e:
            logger.error(f"❌ ManualPlus auto-send error: {e}")
    
    def approve_hybrid_response(self, response_id: str) -> bool:
        """Manually approve a hybrid response"""
        if response_id in self.pending_responses:
            self.pending_responses[response_id]['approved'] = True
            return True
        return False
    
    def cancel_manualplus_timer(self, timer_id: str) -> bool:
        """Cancel a ManualPlus timer"""
        if timer_id in self.manualplus_timers:
            del self.manualplus_timers[timer_id]
            return True
        return False
    
    def change_mode(self, new_mode: str) -> bool:
        """Change reply mode"""
        try:
            new_mode_enum = ReplyMode(new_mode.lower())
            old_mode = self.current_mode
            self.current_mode = new_mode_enum
            
            logger.info(f"🔄 Reply mode changed", 
                       bot=self.bot_name,
                       old_mode=old_mode.value,
                       new_mode=new_mode_enum.value)
            
            # Clear pending operations
            self.pending_responses.clear()
            self.manualplus_timers.clear()
            
            return True
            
        except ValueError:
            logger.error(f"❌ Invalid reply mode: {new_mode}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get reply mode status"""
        return {
            'bot_name': self.bot_name,
            'current_mode': self.current_mode.value,
            'pending_hybrid': len(self.pending_responses),
            'pending_manualplus': len(self.manualplus_timers),
            'mode_settings': {
                mode.value: settings 
                for mode, settings in self.mode_settings.items()
            }
        } 