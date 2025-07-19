from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🤖 GAVATCORE GPT HANDLER
GPT response system for intelligent bot interactions
"""

import asyncio
import sys
import os
import random
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import structlog

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telethon import events
from telethon.tl.types import Message, User

logger = structlog.get_logger("gavatcore.gpt_handler")

class GPTHandler:
    """GPT response handler for intelligent interactions"""
    
    def __init__(self, client, bot_name: str, config: Dict[str, Any]):
        self.client = client
        self.bot_name = bot_name
        self.config = config
        self.reply_mode = config.get('reply_mode', 'manual')
        self.last_message_time = {}
        self.cooldown_seconds = 30  # Default cooldown
        
        # Load character-specific settings
        self.personality = self._load_personality()
        
    def _load_personality(self) -> Dict[str, Any]:
        """Load personality settings for the bot"""
        personalities = {
            'yayincilara': {
                'trigger_words': ['yayın', 'stream', 'game', 'oyun', 'twitch', 'youtube', 'canlı'],
                'style': 'gaming_girl',
                'language': 'tr_ru_mix',
                'emoji_rate': 0.3,
                'response_chance': 0.7
            },
            'xxxgeisha': {
                'trigger_words': ['güzel', 'seksi', 'aşk', 'sevgi', 'canım', 'tatlım', 'geisha'],
                'style': 'seductive_sophisticated',
                'language': 'tr',
                'emoji_rate': 0.2,
                'response_chance': 0.8
            },
            'gawatbaba': {
                'trigger_words': ['abi', 'baba', 'hocam', 'tavsiye', 'yardım', 'para'],
                'style': 'wise_mentor',
                'language': 'tr',
                'emoji_rate': 0.1,
                'response_chance': 0.5
            }
        }
        
        return personalities.get(self.bot_name, personalities['gawatbaba'])
    
    def register_handlers(self):
        """Register GPT event handlers"""
        logger.info(f"🤖 Registering GPT handlers for {self.bot_name}")
        
        # Message handlers based on reply mode
        if self.reply_mode in ['gpt', 'hybrid', 'manualplus']:
            self.client.on(events.NewMessage(incoming=True))(self.handle_incoming_message)
            self.client.on(events.NewMessage(pattern=r'.*'))(self.handle_trigger_words)
        
        # Manual override commands
        self.client.on(events.NewMessage(pattern=r'^/gpt (.+)$'))(self.manual_gpt_command)
        self.client.on(events.NewMessage(pattern=r'^/reply_mode (\w+)$'))(self.change_reply_mode)
        
        logger.info(f"✅ GPT handlers registered for {self.bot_name} (mode: {self.reply_mode})")
    
    async def handle_incoming_message(self, event):
        """Handle incoming messages for GPT processing"""
        # Skip own messages
        if event.out:
            return
        
        # Skip if GPT not enabled
        if not self.config.get('gpt_enabled', False):
            return
        
        try:
            sender = await event.get_sender()
            
            # Skip bots and system users
            if isinstance(sender, User) and sender.bot:
                return
            
            # Check cooldown
            if not self._check_cooldown(event.sender_id):
                return
            
            # Check if should respond
            if not self._should_respond(event):
                return
            
            logger.info(f"💬 Processing GPT message", 
                       bot=self.bot_name, 
                       sender=event.sender_id,
                       mode=self.reply_mode)
            
            # Process based on reply mode
            if self.reply_mode == 'gpt':
                await self._process_auto_gpt(event)
            elif self.reply_mode == 'hybrid':
                await self._process_hybrid_gpt(event)
            elif self.reply_mode == 'manualplus':
                await self._process_manualplus_gpt(event)
                
        except Exception as e:
            logger.error(f"❌ GPT message processing error: {e}")
    
    async def handle_trigger_words(self, event):
        """Handle trigger word detection"""
        if event.out or not self.config.get('gpt_enabled', False):
            return
        
        message_text = (event.raw_text or "").lower()
        trigger_words = self.personality.get('trigger_words', [])
        
        # Check for trigger words
        if any(word in message_text for word in trigger_words):
            logger.info(f"🎯 Trigger word detected", 
                       bot=self.bot_name,
                       message=message_text[:50])
            
            # Increase response chance for trigger words
            if random.random() < 0.9:  # 90% chance for trigger words
                await self._generate_gpt_response(event, triggered=True)
    
    async def manual_gpt_command(self, event):
        """Manual GPT command"""
        try:
            user_message = event.pattern_match.group(1).strip()
            
            logger.info(f"🎯 Manual GPT command", 
                       bot=self.bot_name,
                       user_id=event.sender_id)
            
            response = await self._call_gpt_api(user_message, manual=True)
            
            if response:
                await event.respond(response)
            else:
                await event.respond("❌ GPT yanıtı oluşturulamadı.")
                
        except Exception as e:
            logger.error(f"❌ Manual GPT command error: {e}")
            await event.respond(f"❌ Hata: {str(e)}")
    
    async def change_reply_mode(self, event):
        """Change reply mode command"""
        try:
            new_mode = event.pattern_match.group(1).lower()
            
            if new_mode in ['manual', 'gpt', 'hybrid', 'manualplus']:
                self.reply_mode = new_mode
                self.config['reply_mode'] = new_mode
                
                await event.respond(f"✅ Reply mode değiştirildi: **{new_mode}**")
                logger.info(f"🔧 Reply mode changed", 
                           bot=self.bot_name, 
                           new_mode=new_mode)
            else:
                await event.respond("❌ Geçersiz mod! Kullanım: /reply_mode [manual|gpt|hybrid|manualplus]")
                
        except Exception as e:
            logger.error(f"❌ Reply mode change error: {e}")
    
    def _check_cooldown(self, user_id: int) -> bool:
        """Check if user is in cooldown"""
        now = datetime.now()
        last_time = self.last_message_time.get(user_id)
        
        if last_time and (now - last_time).total_seconds() < self.cooldown_seconds:
            return False
        
        self.last_message_time[user_id] = now
        return True
    
    def _should_respond(self, event) -> bool:
        """Determine if should respond to message"""
        # Check response chance
        response_chance = self.personality.get('response_chance', 0.5)
        
        # Increase chance for replies to our messages
        if event.is_reply:
            response_chance += 0.3
        
        # Increase chance for private messages
        if event.is_private:
            response_chance += 0.2
        
        # Check mentions
        if self.bot_name.lower() in (event.raw_text or "").lower():
            response_chance += 0.4
        
        return random.random() < min(response_chance, 0.95)
    
    async def _process_auto_gpt(self, event):
        """Process message in auto GPT mode"""
        response = await self._generate_gpt_response(event)
        
        if response:
            # Add some delay to seem natural
            await asyncio.sleep(random.uniform(1, 3))
            await event.respond(response)
    
    async def _process_hybrid_gpt(self, event):
        """Process message in hybrid mode (GPT + user approval)"""
        response = await self._generate_gpt_response(event)
        
        if response:
            # For hybrid mode, you'd typically send to an admin channel for approval
            # For now, we'll just log and send after delay
            logger.info(f"🤝 Hybrid response prepared", 
                       bot=self.bot_name,
                       response_preview=response[:50])
            
            # Simulate approval delay
            await asyncio.sleep(random.uniform(2, 5))
            await event.respond(response)
    
    async def _process_manualplus_gpt(self, event):
        """Process message in manual+ mode (auto send after timeout)"""
        response = await self._generate_gpt_response(event)
        
        if response:
            # Wait for manual intervention timeout
            timeout = self.config.get('manualplus_timeout_sec', 45)
            
            logger.info(f"⏰ ManualPlus timeout: {timeout}s", 
                       bot=self.bot_name)
            
            await asyncio.sleep(timeout)
            await event.respond(response)
    
    async def _generate_gpt_response(self, event, triggered: bool = False) -> Optional[str]:
        """Generate GPT response for the message"""
        try:
            message_text = event.raw_text or ""
            
            # Get sender info
            sender = await event.get_sender()
            sender_name = getattr(sender, 'first_name', 'Unknown')
            
            # Prepare context
            context = {
                'message': message_text,
                'sender_name': sender_name,
                'is_private': event.is_private,
                'is_reply': event.is_reply,
                'triggered': triggered,
                'bot_personality': self.personality
            }
            
            # Generate response
            response = await self._call_gpt_api(message_text, context=context)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ GPT response generation error: {e}")
            return None
    
    async def _call_gpt_api(self, message: str, context: Optional[Dict] = None, manual: bool = False) -> Optional[str]:
        """Call GPT API to generate response"""
        try:
            # Mock GPT API call for testing
            # In production, implement actual OpenAI API call
            
            bot_responses = {
                'yayincilara': [
                    "Привет дорогой! 🎮 Şu an hangi oyunu oynuyorsun?",
                    "Yayın açsana canım, beraber oynayalım! 🔥",
                    "Gaming moodundayım ben bugün 💪 Sen nasılsın?",
                    "Twitch'te görüşürüz mi bu akşam? 😘",
                ],
                'xxxgeisha': [
                    "Merhaba güzelim... 🌸 Nasıl geçiyor günün?",
                    "Çok şık görünüyorsun bugün 💋",
                    "Seninle sohbet etmek beni mutlu ediyor ✨",
                    "Gece mi gündüz mü daha güzelsin acaba? 🌙",
                ],
                'gawatbaba': [
                    "Lan moruk naber? İşler nasıl gidiyor? 💪",
                    "Evlat bir tavsiye istersen, abi burada 🔥",
                    "Kanka hayat nasıl, para kazanıyor muyuz? 💰",
                    "Oğlum sen de çok çalışma ha, dinlen biraz 😎",
                ]
            }
            
            responses = bot_responses.get(self.bot_name, bot_responses['gawatbaba'])
            
                         # Add context-aware modifications
            if context is not None and not manual:
                if context.get('triggered'):
                    # More enthusiastic for trigger words
                    selected = random.choice(responses) + " 🎯"
                elif context.get('is_private'):
                    # More personal for DMs
                    selected = random.choice(responses).replace("moruk", "canım")
                else:
                    selected = random.choice(responses)
            else:
                selected = random.choice(responses)
            
            logger.info(f"🤖 GPT response generated", 
                       bot=self.bot_name,
                       response_length=len(selected))
            
            return selected
            
        except Exception as e:
            logger.error(f"❌ GPT API call error: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get GPT handler status"""
        return {
            'bot_name': self.bot_name,
            'reply_mode': self.reply_mode,
            'gpt_enabled': self.config.get('gpt_enabled', False),
            'personality': self.personality,
            'cooldown_seconds': self.cooldown_seconds,
            'active_conversations': len(self.last_message_time)
        } 