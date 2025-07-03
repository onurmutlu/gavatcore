#!/usr/bin/env python3
"""
🧪 GAVATCore Universal Character System Tests
============================================

Comprehensive test suite for the Universal Character System including:
- Character loading and management
- System prompt generation
- Reply mode processing
- Tone adaptation
- Behavioral mapping

Run with: python -m pytest tests/test_universal_character_system.py -v
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

# Import the modules we're testing
import sys
sys.path.append('.')

from gpt.universal_character_manager import (
    UniversalCharacterManager, CharacterProfile, ConversationContext
)
from gpt.system_prompt_manager import SystemPromptManager
from gpt.modes.reply_mode_engine import ReplyModeEngine, ReplyMode
from gpt.traits.tone_adapter import ToneAdapter, ToneCategory
from gpt.traits.behavior_mapper import BehaviorMapper, BehaviorRole

class TestCharacterProfile:
    """Test CharacterProfile data structure."""
    
    def test_character_profile_creation(self):
        """Test basic character profile creation."""
        profile = CharacterProfile(
            character_id="test_char",
            display_name="Test Character",
            username="testchar",
            telegram_handle="@testchar",
            phone="+1234567890",
            user_id=12345,
            persona={
                "gpt_prompt": "You are a test character",
                "style": "friendly",
                "role": "companion"
            },
            reply_mode="gpt",
            manualplus_timeout_sec=30,
            gpt_enhanced=True,
            autospam=False,
            engaging_messages=["Hello!", "How are you?"],
            reply_messages=["Thanks!", "Great!"],
            services_menu="Test services",
            bot_config={},
            raw_data={}
        )
        
        assert profile.character_id == "test_char"
        assert profile.gpt_prompt == "You are a test character"
        assert profile.style == "friendly"
        assert profile.role == "companion"

class TestUniversalCharacterManager:
    """Test Universal Character Manager functionality."""
    
    @pytest.fixture
    def temp_personas_dir(self):
        """Create temporary personas directory with test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            personas_dir = Path(temp_dir) / "personas"
            personas_dir.mkdir()
            
            # Create test persona file
            test_persona = {
                "username": "test_lara",
                "display_name": "Test Lara",
                "telegram_handle": "@test_lara",
                "phone": "+905382617727",
                "user_id": 7576090003,
                "reply_mode": "hybrid",
                "manualplus_timeout_sec": 30,
                "gpt_enhanced": True,
                "autospam": True,
                "persona": {
                    "age": "21-24",
                    "style": "Sarışın, neşeli",
                    "role": "Flörtöz yayıncı",
                    "gpt_prompt": "Test Lara, neşeli bir yayıncı"
                },
                "engaging_messages": ["Merhaba!", "Nasılsın?"],
                "reply_messages": ["Teşekkürler!", "Süper!"],
                "services_menu": "Test services",
                "bot_config": {}
            }
            
            with open(personas_dir / "test_lara.json", 'w', encoding='utf-8') as f:
                json.dump(test_persona, f, ensure_ascii=False, indent=2)
            
            yield str(personas_dir)
    
    def test_character_loading(self, temp_personas_dir):
        """Test loading characters from JSON files."""
        manager = UniversalCharacterManager(personas_dir=temp_personas_dir)
        
        assert len(manager.characters) == 1
        assert "test_lara" in manager.characters
        
        char = manager.get_character("test_lara")
        assert char is not None
        assert char.display_name == "Test Lara"
        assert char.reply_mode == "hybrid"
        assert char.gpt_enhanced is True
    
    def test_character_stats(self, temp_personas_dir):
        """Test character statistics retrieval."""
        manager = UniversalCharacterManager(personas_dir=temp_personas_dir)
        
        stats = manager.get_character_stats("test_lara")
        assert stats['character_id'] == "test_lara"
        assert stats['display_name'] == "Test Lara"
        assert stats['reply_mode'] == "hybrid"
        assert stats['gpt_enhanced'] is True
        
        all_stats = manager.get_all_character_stats()
        assert "test_lara" in all_stats
    
    @pytest.mark.asyncio
    async def test_response_generation(self, temp_personas_dir):
        """Test character response generation."""
        manager = UniversalCharacterManager(personas_dir=temp_personas_dir)
        
        context = ConversationContext(
            user_id="user123",
            username="testuser"
        )
        
        # Mock the reply mode engine
        with patch.object(manager.reply_mode_engine, 'process_message') as mock_process:
            mock_process.return_value = {
                'response': 'Test response',
                'metadata': {'test': True}
            }
            
            response, metadata = await manager.generate_response(
                character_id="test_lara",
                message="Hello",
                context=context
            )
            
            assert response == 'Test response'
            assert 'character_id' in metadata
            assert metadata['character_id'] == "test_lara"
    
    @pytest.mark.asyncio
    async def test_engaging_message_generation(self, temp_personas_dir):
        """Test engaging message selection."""
        manager = UniversalCharacterManager(personas_dir=temp_personas_dir)
        
        context = ConversationContext(user_id="user123")
        
        message, metadata = await manager.get_engaging_message("test_lara", context)
        
        assert message in ["Merhaba!", "Nasılsın?"]
        assert metadata['character_id'] == "test_lara"
        assert metadata['message_type'] == "engaging"

class TestSystemPromptManager:
    """Test System Prompt Manager functionality."""
    
    @pytest.fixture
    def prompt_manager(self):
        """Create SystemPromptManager instance."""
        return SystemPromptManager()
    
    @pytest.fixture
    def test_character(self):
        """Create test character."""
        return CharacterProfile(
            character_id="test_char",
            display_name="Test Character",
            username="testchar",
            telegram_handle="@testchar",
            phone="+1234567890",
            user_id=12345,
            persona={
                "gpt_prompt": "You are a helpful test character",
                "style": "friendly and helpful",
                "role": "assistant"
            },
            reply_mode="gpt",
            manualplus_timeout_sec=30,
            gpt_enhanced=True,
            autospam=False,
            engaging_messages=[],
            reply_messages=[],
            services_menu="",
            bot_config={},
            raw_data={}
        )
    
    @pytest.fixture
    def test_context(self):
        """Create test conversation context."""
        return ConversationContext(
            user_id="user123",
            username="testuser",
            message_history=[
                {
                    "timestamp": "12:00",
                    "sender": "User",
                    "content": "Hello there!"
                }
            ],
            conversation_start=datetime.now(),
            sentiment_score=0.8,
            interaction_count=5
        )
    
    @pytest.mark.asyncio
    async def test_basic_prompt_building(self, prompt_manager, test_character, test_context):
        """Test basic prompt building functionality."""
        prompt = await prompt_manager.build_prompt(
            character=test_character,
            context=test_context,
            message="How are you?"
        )
        
        assert "You are a helpful test character" in prompt
        assert "testuser" in prompt
        assert "How are you?" in prompt
        assert "Test Character" in prompt
    
    @pytest.mark.asyncio
    async def test_prompt_with_memory(self, prompt_manager, test_character, test_context):
        """Test prompt building with conversation memory."""
        prompt = await prompt_manager.build_prompt(
            character=test_character,
            context=test_context,
            message="What did I say before?",
            include_memory=True
        )
        
        assert "conversation memory" in prompt.lower()
        assert "Hello there!" in prompt
    
    def test_engaging_prompt_building(self, prompt_manager, test_character):
        """Test engaging message prompt building."""
        prompt = prompt_manager.build_engaging_prompt(
            character=test_character,
            target_audience="group",
            time_context="evening"
        )
        
        assert "Test Character" in prompt
        assert "engaging message" in prompt
        assert "group chat" in prompt
        assert "evening" in prompt

class TestReplyModeEngine:
    """Test Reply Mode Engine functionality."""
    
    @pytest.fixture
    def reply_engine(self):
        """Create ReplyModeEngine instance."""
        return ReplyModeEngine()
    
    @pytest.fixture
    def test_character(self):
        """Create test character."""
        return CharacterProfile(
            character_id="test_char",
            display_name="Test Character",
            username="testchar",
            telegram_handle="@testchar",
            phone="+1234567890",
            user_id=12345,
            persona={"gpt_prompt": "Test character"},
            reply_mode="gpt",
            manualplus_timeout_sec=30,
            gpt_enhanced=True,
            autospam=False,
            engaging_messages=[],
            reply_messages=[],
            services_menu="",
            bot_config={},
            raw_data={}
        )
    
    @pytest.fixture
    def test_context(self):
        """Create test conversation context."""
        return ConversationContext(
            user_id="user123",
            username="testuser"
        )
    
    @pytest.mark.asyncio
    async def test_manual_mode(self, reply_engine, test_character, test_context):
        """Test manual reply mode."""
        result = await reply_engine.process_message(
            character=test_character,
            message="Hello",
            context=test_context,
            system_prompt="Test prompt",
            reply_mode="manual"
        )
        
        assert result['response'] == ''
        assert result['should_send'] is False
        assert result['needs_approval'] is False
        assert result['metadata']['mode'] == 'manual'
    
    @pytest.mark.asyncio
    async def test_gpt_mode(self, reply_engine, test_character, test_context):
        """Test GPT reply mode."""
        async def mock_gpt_generator(prompt, message):
            return f"GPT response to: {message}"
        
        result = await reply_engine.process_message(
            character=test_character,
            message="Hello",
            context=test_context,
            system_prompt="Test prompt",
            reply_mode="gpt",
            gpt_generator=mock_gpt_generator
        )
        
        assert "GPT response to: Hello" in result['response']
        assert result['should_send'] is True
        assert result['needs_approval'] is False
        assert result['metadata']['mode'] == 'gpt'
    
    @pytest.mark.asyncio
    async def test_hybrid_mode(self, reply_engine, test_character, test_context):
        """Test hybrid reply mode."""
        async def mock_gpt_generator(prompt, message):
            return f"Generated response: {message}"
        
        result = await reply_engine.process_message(
            character=test_character,
            message="Hello",
            context=test_context,
            system_prompt="Test prompt",
            reply_mode="hybrid",
            gpt_generator=mock_gpt_generator
        )
        
        assert "Generated response: Hello" in result['response']
        assert result['should_send'] is False
        assert result['needs_approval'] is True
        assert 'message_id' in result
        assert result['metadata']['mode'] == 'hybrid'
    
    @pytest.mark.asyncio
    async def test_hybrid_approval(self, reply_engine, test_character, test_context):
        """Test hybrid message approval workflow."""
        async def mock_gpt_generator(prompt, message):
            return "Generated response"
        
        # Generate hybrid response
        result = await reply_engine.process_message(
            character=test_character,
            message="Hello",
            context=test_context,
            system_prompt="Test prompt",
            reply_mode="hybrid",
            gpt_generator=mock_gpt_generator
        )
        
        message_id = result['message_id']
        
        # Test approval
        approved = await reply_engine.approve_hybrid_message(message_id)
        assert approved is True
        
        # Test getting pending messages
        pending = reply_engine.get_pending_messages()
        approved_msg = next((msg for msg in pending if msg.message_id == message_id), None)
        # Should be None since it's approved and no longer pending
        assert approved_msg is None

class TestToneAdapter:
    """Test Tone Adapter functionality."""
    
    @pytest.fixture
    def tone_adapter(self):
        """Create ToneAdapter instance."""
        return ToneAdapter()
    
    def test_tone_adaptation(self, tone_adapter):
        """Test basic tone adaptation."""
        base_prompt = "You are a character"
        adapted = tone_adapter.adapt_prompt(
            base_prompt=base_prompt,
            character_style="flörtöz ve neşeli",
            character_role="yayıncı",
            context_sentiment=0.8
        )
        
        assert base_prompt in adapted
        assert "TONE AND STYLE" in adapted
        assert "emoji" in adapted.lower()
    
    def test_tone_suggestions(self, tone_adapter):
        """Test tone suggestions generation."""
        suggestions = tone_adapter.get_tone_suggestions(
            character_style="sarışın ve çekici",
            character_role="flörtöz yayıncı"
        )
        
        assert 'primary_tones' in suggestions
        assert 'recommended_emojis' in suggestions
        assert 'language_patterns' in suggestions
        assert len(suggestions['primary_tones']) > 0
    
    def test_response_validation(self, tone_adapter):
        """Test response tone validation."""
        analysis = tone_adapter.validate_response_tone(
            response="Merhaba tatlım! Nasılsın? 😘💕",
            expected_tone=ToneCategory.FLIRTY
        )
        
        assert 'valid' in analysis
        assert 'emoji_count' in analysis
        assert analysis['emoji_count'] >= 2

class TestBehaviorMapper:
    """Test Behavior Mapper functionality."""
    
    @pytest.fixture
    def behavior_mapper(self):
        """Create BehaviorMapper instance."""
        return BehaviorMapper()
    
    def test_behavior_mapping(self, behavior_mapper):
        """Test character role to behavior mapping."""
        roles = behavior_mapper.map_character_behavior("flörtöz yayıncı")
        
        assert len(roles) > 0
        assert BehaviorRole.PERFORMER in roles or BehaviorRole.FLIRT in roles
    
    def test_behavioral_instructions(self, behavior_mapper):
        """Test behavioral instructions generation."""
        instructions = behavior_mapper.get_behavioral_instructions(
            character_role="yayıncı ve eğlendirici",
            sentiment_score=0.7,
            interaction_count=3
        )
        
        assert "Behavioral Role" in instructions
        assert "Interaction Style" in instructions
        assert "Initiative Level" in instructions
    
    def test_message_selection(self, behavior_mapper):
        """Test behavior-based message selection."""
        messages = [
            "Merhaba! Nasılsın? 😊",
            "Bugün show var! 🎭",
            "VIP üyelik için yazın 💎",
            "Eğlenceye hazır mısınız? 🎉"
        ]
        
        selected = behavior_mapper.select_engaging_message(
            available_messages=messages,
            character_role="eğlendirici yayıncı",
            sentiment_score=0.8
        )
        
        assert selected in messages
        assert selected != ""  # Should not be empty
    
    def test_behavior_analysis(self, behavior_mapper):
        """Test behavior analysis for character."""
        analysis = behavior_mapper.get_behavior_analysis("flörtöz moderatör")
        
        assert 'detected_roles' in analysis
        assert 'primary_role' in analysis
        assert 'interaction_style' in analysis
        assert len(analysis['detected_roles']) > 0

class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.fixture
    def temp_personas_dir(self):
        """Create temporary personas directory with test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            personas_dir = Path(temp_dir) / "personas"
            personas_dir.mkdir()
            
            # Create comprehensive test persona
            test_persona = {
                "username": "integration_test",
                "display_name": "Integration Test Character",
                "telegram_handle": "@integration_test",
                "phone": "+1234567890",
                "user_id": 12345,
                "reply_mode": "gpt",
                "manualplus_timeout_sec": 30,
                "gpt_enhanced": True,
                "autospam": False,
                "persona": {
                    "age": "25",
                    "style": "Flörtöz ve neşeli, sarışın",
                    "role": "Eğlendirici yayıncı",
                    "gpt_prompt": "Sen Integration Test Character'sin, eğlenceli ve flörtöz bir yayıncı."
                },
                "engaging_messages": [
                    "Merhaba güzelim! 😘",
                    "Bu gece eğlence var! 🎉",
                    "Hazır mısın show'a? 🔥"
                ],
                "reply_messages": [
                    "Çok tatlısın! 😊",
                    "Kesin eğlenceli olur! ✨",
                    "Seni bekliyorum! 💕"
                ],
                "services_menu": "Test services menu",
                "bot_config": {}
            }
            
            with open(personas_dir / "integration_test.json", 'w', encoding='utf-8') as f:
                json.dump(test_persona, f, ensure_ascii=False, indent=2)
            
            yield str(personas_dir)
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, temp_personas_dir):
        """Test complete character response workflow."""
        # Initialize manager
        manager = UniversalCharacterManager(personas_dir=temp_personas_dir)
        
        # Create context
        context = ConversationContext(
            user_id="test_user",
            username="TestUser",
            message_history=[
                {
                    "timestamp": "12:00",
                    "sender": "User",
                    "content": "Merhaba!"
                }
            ],
            sentiment_score=0.8,
            interaction_count=3
        )
        
        # Mock GPT generator
        async def mock_gpt_generator(system_prompt, message):
            return f"Merhaba TestUser! Çok iyi, sen nasılsın? 😊"
        
        # Patch the reply mode engine to use our mock
        with patch.object(manager.reply_mode_engine, '_generate_mock_response') as mock_gen:
            mock_gen.return_value = "Merhaba TestUser! Çok iyi, sen nasılsın? 😊"
            
            # Generate response
            response, metadata = await manager.generate_response(
                character_id="integration_test",
                message="Merhaba! Nasılsın?",
                context=context
            )
            
            # Verify response
            assert response != ""
            assert "character_id" in metadata
            assert metadata["character_id"] == "integration_test"
            assert metadata["character_name"] == "Integration Test Character"
    
    def test_character_consistency(self, temp_personas_dir):
        """Test that character traits remain consistent across components."""
        manager = UniversalCharacterManager(personas_dir=temp_personas_dir)
        character = manager.get_character("integration_test")
        
        # Test tone adapter analysis
        tone_adapter = ToneAdapter()
        tone_suggestions = tone_adapter.get_tone_suggestions(
            character.style, character.role
        )
        
        # Test behavior mapper analysis
        behavior_mapper = BehaviorMapper()
        behavior_analysis = behavior_mapper.get_behavior_analysis(character.role)
        
        # Verify consistency
        assert len(tone_suggestions['primary_tones']) > 0
        assert len(behavior_analysis['detected_roles']) > 0
        
        # Should detect flirty/playful tones and performer/entertainer roles
        assert any(tone in ['flirty', 'playful'] for tone in tone_suggestions['primary_tones'])
        assert any(role in ['performer', 'entertainer'] for role in behavior_analysis['detected_roles'])

if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"]) 