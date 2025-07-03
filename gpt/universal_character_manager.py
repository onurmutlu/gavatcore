#!/usr/bin/env python3
"""
🧬 GAVATCore Universal Character Manager
==========================================

Central character management system that loads persona definitions
from data/personas/*.json and provides unified access to all characters
with support for multiple reply modes, behavioral adaptation, and
dynamic prompt generation.

Features:
- Auto-loads all persona files from data/personas/
- Supports 4 reply modes: manual, gpt, hybrid, manualplus
- Character-aware tone and behavior adaptation
- GPT prompt generation with context injection
- Caching and performance optimization
"""

import os
import json
import glob
import time
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import structlog

from .system_prompt_manager import SystemPromptManager
from .modes.reply_mode_engine import ReplyModeEngine
from .traits.tone_adapter import ToneAdapter
from .traits.behavior_mapper import BehaviorMapper

logger = structlog.get_logger("gavatcore.gpt.character_manager")

@dataclass
class CharacterProfile:
    """Character profile data structure."""
    character_id: str
    display_name: str
    username: str
    telegram_handle: str
    phone: str
    user_id: int
    persona: Dict[str, Any]
    reply_mode: str
    manualplus_timeout_sec: int
    gpt_enhanced: bool
    autospam: bool
    engaging_messages: List[str]
    reply_messages: List[str]
    services_menu: str
    bot_config: Dict[str, Any]
    raw_data: Dict[str, Any]
    
    @property
    def gpt_prompt(self) -> str:
        """Get the character's GPT prompt."""
        return self.persona.get('gpt_prompt', '')
    
    @property
    def style(self) -> str:
        """Get the character's style."""
        return self.persona.get('style', '')
    
    @property
    def role(self) -> str:
        """Get the character's role."""
        return self.persona.get('role', '')
    
    @property
    def age(self) -> str:
        """Get the character's age."""
        return self.persona.get('age', '')

@dataclass
class ConversationContext:
    """Conversation context for GPT generation."""
    user_id: str
    username: str = ""
    message_history: List[Dict[str, Any]] = field(default_factory=list)
    conversation_start: datetime = field(default_factory=datetime.now)
    user_metadata: Dict[str, Any] = field(default_factory=dict)
    sentiment_score: float = 0.5
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None

class UniversalCharacterManager:
    """
    🧬 Universal Character Management System
    
    Loads and manages all character personas from data/personas/*.json
    Provides unified interface for character-based GPT responses.
    """
    
    def __init__(self, personas_dir: str = "data/personas"):
        self.personas_dir = Path(personas_dir)
        self.characters: Dict[str, CharacterProfile] = {}
        self.system_prompt_manager = SystemPromptManager()
        self.reply_mode_engine = ReplyModeEngine()
        self.tone_adapter = ToneAdapter()
        self.behavior_mapper = BehaviorMapper()
        
        # Performance optimization
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=10)
        
        # Load all characters
        self.load_all_characters()
        
        logger.info("🧬 Universal Character Manager initialized",
                   character_count=len(self.characters))
    
    def load_all_characters(self) -> None:
        """Load all character personas from JSON files."""
        try:
            if not self.personas_dir.exists():
                logger.warning(f"⚠️ Personas directory not found: {self.personas_dir}")
                return
            
            # Find all JSON files in personas directory
            json_files = list(self.personas_dir.glob("*.json"))
            
            for json_file in json_files:
                # Skip banned or test files
                if 'banned' in json_file.name or json_file.name.startswith('test_'):
                    continue
                
                try:
                    character = self._load_character_from_file(json_file)
                    if character:
                        self.characters[character.character_id] = character
                        logger.info(f"✅ Loaded character: {character.display_name} ({character.character_id})")
                
                except Exception as e:
                    logger.error(f"❌ Failed to load character from {json_file.name}: {e}")
            
            logger.info(f"🎭 Loaded {len(self.characters)} characters total")
            
        except Exception as e:
            logger.error(f"❌ Error loading characters: {e}")
    
    def _load_character_from_file(self, file_path: Path) -> Optional[CharacterProfile]:
        """Load a single character from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract character ID from filename (without .json)
            character_id = file_path.stem
            
            # Create CharacterProfile
            profile = CharacterProfile(
                character_id=character_id,
                display_name=data.get('display_name', character_id),
                username=data.get('username', character_id),
                telegram_handle=data.get('telegram_handle', f"@{character_id}"),
                phone=data.get('phone', ''),
                user_id=data.get('user_id', 0),
                persona=data.get('persona', {}),
                reply_mode=data.get('reply_mode', 'manual'),
                manualplus_timeout_sec=data.get('manualplus_timeout_sec', 30),
                gpt_enhanced=data.get('gpt_enhanced', False),
                autospam=data.get('autospam', False),
                engaging_messages=data.get('engaging_messages', []),
                reply_messages=data.get('reply_messages', []),
                services_menu=data.get('services_menu', ''),
                bot_config=data.get('bot_config', {}),
                raw_data=data
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"❌ Error loading character from {file_path}: {e}")
            return None
    
    def get_character(self, character_id: str) -> Optional[CharacterProfile]:
        """Get character profile by ID."""
        return self.characters.get(character_id)
    
    def list_characters(self) -> List[str]:
        """Get list of all available character IDs."""
        return list(self.characters.keys())
    
    def get_characters_by_mode(self, reply_mode: str) -> List[CharacterProfile]:
        """Get all characters using specific reply mode."""
        return [char for char in self.characters.values() if char.reply_mode == reply_mode]
    
    async def generate_response(
        self,
        character_id: str,
        message: str,
        context: ConversationContext,
        force_mode: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate character response based on message and context.
        
        Args:
            character_id: Character identifier
            message: User message
            context: Conversation context
            force_mode: Override character's default reply mode
        
        Returns:
            Tuple of (response_text, metadata)
        """
        try:
            character = self.get_character(character_id)
            if not character:
                raise ValueError(f"Character not found: {character_id}")
            
            # Determine reply mode
            reply_mode = force_mode or character.reply_mode
            
            # Generate system prompt
            system_prompt = await self.system_prompt_manager.build_prompt(
                character=character,
                context=context,
                message=message
            )
            
            # Apply tone and behavior adaptation
            adapted_prompt = self.tone_adapter.adapt_prompt(
                system_prompt, 
                character.style, 
                character.role
            )
            
            behavioral_instructions = self.behavior_mapper.get_behavioral_instructions(
                character.role,
                context.sentiment_score,
                context.interaction_count
            )
            
            # Combine prompts
            final_prompt = f"{adapted_prompt}\n\n{behavioral_instructions}"
            
            # Process through reply mode engine
            response_data = await self.reply_mode_engine.process_message(
                character=character,
                message=message,
                context=context,
                system_prompt=final_prompt,
                reply_mode=reply_mode
            )
            
            # Add character metadata
            metadata = {
                'character_id': character_id,
                'character_name': character.display_name,
                'reply_mode': reply_mode,
                'gpt_enhanced': character.gpt_enhanced,
                'style': character.style,
                'role': character.role,
                'timestamp': datetime.now().isoformat(),
                **response_data.get('metadata', {})
            }
            
            logger.info(f"✅ Generated response for {character_id}",
                       reply_mode=reply_mode,
                       response_length=len(response_data.get('response', '')))
            
            return response_data.get('response', ''), metadata
            
        except Exception as e:
            logger.error(f"❌ Error generating response for {character_id}: {e}")
            return f"Üzgünüm, şu anda bir sorun yaşıyorum. 😔", {'error': str(e)}
    
    async def get_engaging_message(
        self,
        character_id: str,
        context: Optional[ConversationContext] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Get a random engaging message from character."""
        try:
            character = self.get_character(character_id)
            if not character or not character.engaging_messages:
                return "Selam! Nasılsın? 😊", {}
            
            # Apply behavior mapping to select appropriate message
            selected_message = self.behavior_mapper.select_engaging_message(
                character.engaging_messages,
                character.role,
                context.sentiment_score if context else 0.5
            )
            
            metadata = {
                'character_id': character_id,
                'message_type': 'engaging',
                'timestamp': datetime.now().isoformat()
            }
            
            return selected_message, metadata
            
        except Exception as e:
            logger.error(f"❌ Error getting engaging message for {character_id}: {e}")
            return "Merhaba! 👋", {'error': str(e)}
    
    async def get_reply_message(
        self,
        character_id: str,
        context: Optional[ConversationContext] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Get a random reply message from character."""
        try:
            character = self.get_character(character_id)
            if not character or not character.reply_messages:
                return "Teşekkürler! 😊", {}
            
            # Apply behavior mapping to select appropriate message
            selected_message = self.behavior_mapper.select_reply_message(
                character.reply_messages,
                character.role,
                context.sentiment_score if context else 0.5
            )
            
            metadata = {
                'character_id': character_id,
                'message_type': 'reply',
                'timestamp': datetime.now().isoformat()
            }
            
            return selected_message, metadata
            
        except Exception as e:
            logger.error(f"❌ Error getting reply message for {character_id}: {e}")
            return "😊", {'error': str(e)}
    
    def get_character_stats(self, character_id: str) -> Dict[str, Any]:
        """Get character statistics and info."""
        character = self.get_character(character_id)
        if not character:
            return {}
        
        return {
            'character_id': character_id,
            'display_name': character.display_name,
            'username': character.username,
            'reply_mode': character.reply_mode,
            'gpt_enhanced': character.gpt_enhanced,
            'autospam': character.autospam,
            'engaging_messages_count': len(character.engaging_messages),
            'reply_messages_count': len(character.reply_messages),
            'style': character.style,
            'role': character.role,
            'age': character.age,
            'manualplus_timeout': character.manualplus_timeout_sec,
            'services_menu_available': bool(character.services_menu),
            'bot_config': character.bot_config
        }
    
    def get_all_character_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all characters."""
        return {
            char_id: self.get_character_stats(char_id) 
            for char_id in self.characters.keys()
        }
    
    def reload_character(self, character_id: str) -> bool:
        """Reload a specific character from file."""
        try:
            file_path = self.personas_dir / f"{character_id}.json"
            if not file_path.exists():
                logger.error(f"❌ Character file not found: {file_path}")
                return False
            
            character = self._load_character_from_file(file_path)
            if character:
                self.characters[character_id] = character
                logger.info(f"♻️ Reloaded character: {character.display_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error reloading character {character_id}: {e}")
            return False
    
    def reload_all_characters(self) -> bool:
        """Reload all characters from files."""
        try:
            old_count = len(self.characters)
            self.characters.clear()
            self.load_all_characters()
            new_count = len(self.characters)
            
            logger.info(f"♻️ Reloaded all characters: {old_count} → {new_count}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error reloading all characters: {e}")
            return False

# Global instance
character_manager = UniversalCharacterManager()

# Convenience functions
async def get_character_response(
    character_id: str,
    message: str,
    user_id: str,
    username: str = "",
    **kwargs
) -> Tuple[str, Dict[str, Any]]:
    """Convenience function for getting character response."""
    context = ConversationContext(
        user_id=user_id,
        username=username,
        **kwargs
    )
    
    return await character_manager.generate_response(
        character_id=character_id,
        message=message,
        context=context
    )

def list_available_characters() -> List[str]:
    """Convenience function to list all characters."""
    return character_manager.list_characters()

def get_character_info(character_id: str) -> Dict[str, Any]:
    """Convenience function to get character info."""
    return character_manager.get_character_stats(character_id) 