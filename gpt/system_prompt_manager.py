#!/usr/bin/env python3
"""
🧠 GAVATCore System Prompt Manager
==================================

Dynamic system prompt generation for GPT responses based on:
- Character persona data from JSON
- Conversation context and history
- User metadata and sentiment
- Behavioral adaptation requirements

Features:
- Context-aware prompt building
- Memory injection from conversation history
- User-specific customization
- Tone and style adaptation
- Performance optimization with caching
"""

import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import structlog

logger = structlog.get_logger("gavatcore.gpt.prompt_manager")

@dataclass
class PromptTemplate:
    """Prompt template structure."""
    base_prompt: str
    context_injection: str
    memory_template: str
    user_context_template: str
    conversation_starter: str

class SystemPromptManager:
    """
    🧠 Dynamic System Prompt Generator
    
    Builds context-aware GPT prompts by combining:
    - Character base prompt from persona
    - Conversation context and memory
    - User metadata and sentiment
    - Behavioral instructions
    """
    
    def __init__(self):
        self.prompt_cache: Dict[str, str] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        self.cache_ttl = timedelta(minutes=5)
        
        # Default prompt templates
        self.templates = {
            'base_context': """
Conversation Context:
- User: {username} (ID: {user_id})
- Conversation started: {conversation_start}
- Total interactions: {interaction_count}
- Last interaction: {last_interaction}
- Sentiment score: {sentiment_score:.2f}/1.0
""",
            
            'memory_template': """
Recent conversation memory:
{conversation_history}
""",
            
            'user_context': """
User profile:
{user_metadata}
""",
            
            'behavioral_instructions': """
Response guidelines:
- Maintain character consistency
- Adapt tone based on user sentiment
- Use appropriate emojis
- Keep responses engaging
- Follow character's style and role
"""
        }
        
        logger.info("🧠 System Prompt Manager initialized")
    
    async def build_prompt(
        self,
        character,  # CharacterProfile
        context,    # ConversationContext
        message: str,
        include_memory: bool = True,
        include_user_context: bool = True
    ) -> str:
        """
        Build complete system prompt for GPT generation.
        
        Args:
            character: Character profile with persona data
            context: Conversation context with history
            message: Current user message
            include_memory: Whether to include conversation history
            include_user_context: Whether to include user metadata
        
        Returns:
            Complete system prompt string
        """
        try:
            # Create cache key
            cache_key = f"{character.character_id}_{context.user_id}_{hash(message)}_{include_memory}_{include_user_context}"
            
            # Check cache
            if self._is_cached(cache_key):
                return self.prompt_cache[cache_key]
            
            # Start with character's base prompt
            base_prompt = character.gpt_prompt
            
            # Build context sections
            prompt_sections = [base_prompt]
            
            # Add conversation context
            if context:
                context_section = self._build_context_section(context)
                prompt_sections.append(context_section)
            
            # Add conversation memory
            if include_memory and context.message_history:
                memory_section = self._build_memory_section(context.message_history)
                prompt_sections.append(memory_section)
            
            # Add user context
            if include_user_context and context.user_metadata:
                user_section = self._build_user_context_section(context.user_metadata)
                prompt_sections.append(user_section)
            
            # Add current message context
            message_context = f"""
Current message from {context.username}: "{message}"

Please respond as {character.display_name} maintaining your character's personality, style, and tone.
"""
            prompt_sections.append(message_context)
            
            # Combine all sections
            final_prompt = "\n\n".join(section.strip() for section in prompt_sections if section.strip())
            
            # Cache the result
            self._cache_prompt(cache_key, final_prompt)
            
            logger.debug(f"🧠 Built prompt for {character.character_id}",
                        prompt_length=len(final_prompt),
                        sections_count=len(prompt_sections))
            
            return final_prompt
            
        except Exception as e:
            logger.error(f"❌ Error building prompt: {e}")
            # Fallback to basic prompt
            return character.gpt_prompt + f"\n\nUser message: {message}"
    
    def _build_context_section(self, context) -> str:
        """Build conversation context section."""
        try:
            return self.templates['base_context'].format(
                username=context.username or "User",
                user_id=context.user_id,
                conversation_start=context.conversation_start.strftime("%Y-%m-%d %H:%M"),
                interaction_count=context.interaction_count,
                last_interaction=context.last_interaction.strftime("%H:%M") if context.last_interaction else "First message",
                sentiment_score=context.sentiment_score
            )
        except Exception as e:
            logger.warning(f"⚠️ Error building context section: {e}")
            return f"User: {context.username or 'User'} (Interactions: {context.interaction_count})"
    
    def _build_memory_section(self, message_history: List[Dict[str, Any]]) -> str:
        """Build conversation memory section."""
        try:
            if not message_history:
                return ""
            
            # Get last 5 messages for context
            recent_messages = message_history[-5:]
            
            memory_lines = []
            for msg in recent_messages:
                timestamp = msg.get('timestamp', '')
                sender = msg.get('sender', 'User')
                content = msg.get('content', '')
                
                if len(content) > 100:
                    content = content[:97] + "..."
                
                memory_lines.append(f"[{timestamp}] {sender}: {content}")
            
            if memory_lines:
                return self.templates['memory_template'].format(
                    conversation_history="\n".join(memory_lines)
                )
            
            return ""
            
        except Exception as e:
            logger.warning(f"⚠️ Error building memory section: {e}")
            return ""
    
    def _build_user_context_section(self, user_metadata: Dict[str, Any]) -> str:
        """Build user context section."""
        try:
            if not user_metadata:
                return ""
            
            # Format user metadata nicely
            context_lines = []
            for key, value in user_metadata.items():
                if key in ['name', 'age', 'location', 'interests', 'language']:
                    context_lines.append(f"- {key.title()}: {value}")
            
            if context_lines:
                return self.templates['user_context'].format(
                    user_metadata="\n".join(context_lines)
                )
            
            return ""
            
        except Exception as e:
            logger.warning(f"⚠️ Error building user context section: {e}")
            return ""
    
    def build_engaging_prompt(
        self,
        character,  # CharacterProfile
        target_audience: str = "group",
        time_context: str = "general"
    ) -> str:
        """
        Build prompt for generating engaging messages.
        
        Args:
            character: Character profile
            target_audience: "group" or "dm"
            time_context: "morning", "evening", "night", "general"
        
        Returns:
            Prompt for engaging message generation
        """
        try:
            base_prompt = f"""
You are {character.display_name}. Generate an engaging message to post in a {target_audience} chat.

Character details:
- Style: {character.style}
- Role: {character.role}
- Age: {character.age}

Requirements:
- Time context: {time_context}
- Keep it under 200 characters
- Include appropriate emojis
- Match your character's personality
- Make it engaging and conversation-starting
- Avoid being too pushy or aggressive

Generate only the message, no explanations.
"""
            
            return base_prompt
            
        except Exception as e:
            logger.error(f"❌ Error building engaging prompt: {e}")
            return f"Generate an engaging message as {character.display_name}"
    
    def build_reply_prompt(
        self,
        character,  # CharacterProfile
        original_message: str,
        context_info: Optional[str] = None
    ) -> str:
        """
        Build prompt for generating reply messages.
        
        Args:
            character: Character profile
            original_message: Message being replied to
            context_info: Additional context information
        
        Returns:
            Prompt for reply generation
        """
        try:
            prompt = f"""
You are {character.display_name}. Someone sent you this message: "{original_message}"

Character details:
- Style: {character.style}
- Role: {character.role}
- Personality: {character.gpt_prompt}

Requirements:
- Respond naturally and in character
- Keep response under 300 characters
- Include appropriate emojis
- Match the tone of the original message
- Be engaging and continue the conversation
"""
            
            if context_info:
                prompt += f"\n\nAdditional context: {context_info}"
            
            prompt += "\n\nGenerate only the reply, no explanations."
            
            return prompt
            
        except Exception as e:
            logger.error(f"❌ Error building reply prompt: {e}")
            return f"Reply to '{original_message}' as {character.display_name}"
    
    def build_system_message_prompt(
        self,
        character,  # CharacterProfile
        message_type: str,
        parameters: Dict[str, Any] = None
    ) -> str:
        """
        Build prompt for system messages (menu, services, etc.).
        
        Args:
            character: Character profile
            message_type: Type of system message
            parameters: Additional parameters
        
        Returns:
            Prompt for system message generation
        """
        try:
            if message_type == "services_menu":
                return f"""
You are {character.display_name}. Present your services menu in an attractive way.

Character style: {character.style}
Services available: {character.services_menu}

Requirements:
- Make it appealing and professional
- Include emojis for visual appeal
- Maintain character personality
- Include pricing clearly
- Add contact information at the end

Generate the services menu message.
"""
            
            elif message_type == "welcome":
                return f"""
You are {character.display_name}. Create a welcome message for new users.

Character details:
- Style: {character.style}
- Role: {character.role}

Requirements:
- Welcoming and friendly
- Introduce yourself briefly
- Invite to conversation
- Include appropriate emojis
- Keep under 200 characters

Generate the welcome message.
"""
            
            else:
                return f"Generate a {message_type} message as {character.display_name}"
                
        except Exception as e:
            logger.error(f"❌ Error building system message prompt: {e}")
            return f"Generate a {message_type} message as {character.display_name}"
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if prompt is cached and still valid."""
        if cache_key not in self.prompt_cache:
            return False
        
        cache_time = self.cache_timestamps.get(cache_key)
        if not cache_time:
            return False
        
        return datetime.now() - cache_time < self.cache_ttl
    
    def _cache_prompt(self, cache_key: str, prompt: str) -> None:
        """Cache a prompt with timestamp."""
        self.prompt_cache[cache_key] = prompt
        self.cache_timestamps[cache_key] = datetime.now()
        
        # Clean old cache entries
        self._cleanup_cache()
    
    def _cleanup_cache(self) -> None:
        """Remove expired cache entries."""
        current_time = datetime.now()
        expired_keys = [
            key for key, timestamp in self.cache_timestamps.items()
            if current_time - timestamp > self.cache_ttl
        ]
        
        for key in expired_keys:
            self.prompt_cache.pop(key, None)
            self.cache_timestamps.pop(key, None)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cached_prompts': len(self.prompt_cache),
            'cache_ttl_minutes': self.cache_ttl.total_seconds() / 60,
            'last_cleanup': datetime.now().isoformat()
        }

def get_sales_prompt(context=None):
    """Satış için sistem promptunu döndürür."""
    base_prompt = "Satış odaklı, ikna edici ve kullanıcıyı harekete geçiren bir mesaj oluştur."
    if context:
        return f"{base_prompt}\nKontekst: {context}"
    return base_prompt

def get_menu_prompt(context=None):
    """Menü için sistem promptunu döndürür."""
    base_prompt = "Menü seçeneklerini göster ve kullanıcıya yardımcı ol."
    if context:
        return f"{base_prompt}\nKontekst: {context}"
    return base_prompt
