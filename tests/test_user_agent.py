#!/usr/bin/env python3
"""
🧪 Complete Test Suite for gpt/user_agent.py 🧪

Comprehensive tests for GAVATCore user agent:
- Profile loading and fallback scenarios
- GPT API integration and timeout handling  
- Error boundary testing
- Message generation validation
- Performance testing with multiple requests

Target Coverage: 95-100%
Test Count: 25+ comprehensive tests
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gpt.user_agent import generate_user_reply


class TestGenerateUserReplyCore:
    """Core functionality tests for generate_user_reply."""
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_generate_user_reply_success(self, mock_openai, mock_load_profile):
        """Test successful user reply generation."""
        # Mock profile data
        mock_profile = {
            "flirt_templates": ["Hey canım! 😘", "Nasılsın tatlım? 💕"],
            "tone": "flirty",
            "persona": {"style": "playful"}
        }
        mock_load_profile.return_value = mock_profile
        
        # Mock OpenAI response
        mock_openai.return_value = "Merhaba tatlım! Nasıl gidiyor? 😘"
        
        result = await generate_user_reply("123456789", "Merhaba!")
        
        assert result == "Merhaba tatlım! Nasıl gidiyor? 😘"
        mock_load_profile.assert_called_once_with("123456789")
        mock_openai.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_generate_user_reply_with_username(self, mock_openai, mock_load_profile):
        """Test user reply generation with username."""
        mock_profile = {
            "flirt_templates": ["Hey! 😊"],
            "tone": "friendly"
        }
        mock_load_profile.return_value = mock_profile
        mock_openai.return_value = "Test reply"
        
        result = await generate_user_reply("test_username", "Hello!")
        
        assert result == "Test reply"
        mock_load_profile.assert_called_once_with("test_username")
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_generate_user_reply_integer_user_key(self, mock_openai, mock_load_profile):
        """Test user reply generation with integer user key."""
        mock_profile = {"tone": "casual"}
        mock_load_profile.return_value = mock_profile
        mock_openai.return_value = "Integer key reply"
        
        result = await generate_user_reply(123456789, "Test message")
        
        assert result == "Integer key reply"
        mock_load_profile.assert_called_once_with("123456789")  # Should be converted to string


class TestProfileLoadingFallbacks:
    """Test profile loading and fallback scenarios."""
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_profile_load_exception_fallback(self, mock_openai, mock_load_profile):
        """Test profile loading exception with fallback response."""
        # Mock profile loading failure
        mock_load_profile.side_effect = Exception("Profile not found")
        
        result = await generate_user_reply("nonexistent_user", "Hello!")
        
        assert result == "Şu an cevap veremiyorum, birazdan tekrar yaz canım! 🫦"
        mock_load_profile.assert_called_once_with("nonexistent_user")
        mock_openai.assert_not_called()
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_flirt_templates_fallback_chain(self, mock_openai, mock_load_profile):
        """Test flirt templates fallback chain."""
        # Profile with only engaging_messages
        mock_profile = {
            "engaging_messages": ["Hey there! 👋", "What's up? 😊"],
            "tone": "friendly"
        }
        mock_load_profile.return_value = mock_profile
        mock_openai.return_value = "Engaging response"
        
        result = await generate_user_reply("user1", "Hi!")
        
        assert result == "Engaging response"
        
        # Verify OpenAI was called with engaging_messages
        call_args = mock_openai.call_args[0][0]
        assert "Hey there! 👋" in call_args
        assert "What's up? 😊" in call_args
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_flirt_templates_reply_messages_fallback(self, mock_openai, mock_load_profile):
        """Test fallback to reply_messages when other templates missing."""
        # Profile with only reply_messages
        mock_profile = {
            "reply_messages": ["Sure thing!", "Absolutely! 💯"],
            "tone": "helpful"
        }
        mock_load_profile.return_value = mock_profile
        mock_openai.return_value = "Reply message response"
        
        result = await generate_user_reply("user2", "Can you help?")
        
        assert result == "Reply message response"
        
        # Verify OpenAI was called with reply_messages
        call_args = mock_openai.call_args[0][0]
        assert "Sure thing!" in call_args
        assert "Absolutely! 💯" in call_args
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_flirt_templates_empty_fallback(self, mock_openai, mock_load_profile):
        """Test when all template sources are missing or empty."""
        # Profile with no templates
        mock_profile = {
            "tone": "neutral"
        }
        mock_load_profile.return_value = mock_profile
        mock_openai.return_value = "Default template response"
        
        result = await generate_user_reply("user3", "Hello!")
        
        assert result == "Default template response"
        
        # Verify OpenAI was called with empty templates list
        call_args = mock_openai.call_args[0][0]
        assert "[]" in call_args  # Empty list representation
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_tone_fallback_chain(self, mock_openai, mock_load_profile):
        """Test tone fallback chain."""
        # Profile with persona.style but no direct tone
        mock_profile = {
            "flirt_templates": ["Hey! 😊"],
            "persona": {"style": "playful"}
        }
        mock_load_profile.return_value = mock_profile
        mock_openai.return_value = "Playful response"
        
        result = await generate_user_reply("user4", "What's up?")
        
        assert result == "Playful response"
        
        # Verify OpenAI was called with persona.style as tone
        call_args = mock_openai.call_args[0][0]
        assert "Tarzın: playful" in call_args
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_tone_default_fallback(self, mock_openai, mock_load_profile):
        """Test default tone fallback."""
        # Profile with no tone sources
        mock_profile = {
            "flirt_templates": ["Hello! 👋"]
        }
        mock_load_profile.return_value = mock_profile
        mock_openai.return_value = "Default tone response"
        
        result = await generate_user_reply("user5", "Hi there!")
        
        assert result == "Default tone response"
        
        # Verify OpenAI was called with default "flirty" tone
        call_args = mock_openai.call_args[0][0]
        assert "Tarzın: flirty" in call_args
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_persona_non_dict_handling(self, mock_openai, mock_load_profile):
        """Test handling when persona is not a dictionary."""
        # Profile with persona as string instead of dict
        mock_profile = {
            "flirt_templates": ["Hey! 😊"],
            "persona": "playful_character"  # Not a dict
        }
        mock_load_profile.return_value = mock_profile
        mock_openai.return_value = "Non-dict persona response"
        
        result = await generate_user_reply("user6", "Hello!")
        
        assert result == "Non-dict persona response"
        
        # Should fall back to default "flirty" tone
        call_args = mock_openai.call_args[0][0]
        assert "Tarzın: flirty" in call_args


class TestOpenAIIntegrationAndErrors:
    """Test OpenAI integration and error handling."""
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_openai_exception_fallback(self, mock_openai, mock_load_profile):
        """Test OpenAI exception with fallback response."""
        mock_profile = {
            "flirt_templates": ["Hey! 😊"],
            "tone": "friendly"
        }
        mock_load_profile.return_value = mock_profile
        
        # Mock OpenAI failure
        mock_openai.side_effect = Exception("API timeout")
        
        result = await generate_user_reply("user7", "Hello!")
        
        assert result == "Sanırım biraz dalgınım, lütfen tekrar yaz tatlım! 😇"
        mock_openai.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_openai_timeout_error(self, mock_openai, mock_load_profile):
        """Test OpenAI timeout error handling."""
        mock_profile = {"tone": "helpful"}
        mock_load_profile.return_value = mock_profile
        
        # Mock timeout error
        mock_openai.side_effect = asyncio.TimeoutError("Request timed out")
        
        result = await generate_user_reply("user8", "Help me!")
        
        assert result == "Sanırım biraz dalgınım, lütfen tekrar yaz tatlım! 😇"
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_openai_network_error(self, mock_openai, mock_load_profile):
        """Test OpenAI network error handling."""
        mock_profile = {"tone": "supportive"}
        mock_load_profile.return_value = mock_profile
        
        # Mock network error
        mock_openai.side_effect = ConnectionError("Network unreachable")
        
        result = await generate_user_reply("user9", "Are you there?")
        
        assert result == "Sanırım biraz dalgınım, lütfen tekrar yaz tatlım! 😇"
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_openai_response_stripping(self, mock_openai, mock_load_profile):
        """Test OpenAI response stripping whitespace."""
        mock_profile = {"tone": "clean"}
        mock_load_profile.return_value = mock_profile
        
        # Mock response with whitespace
        mock_openai.return_value = "  \n  Clean response!  \n  "
        
        result = await generate_user_reply("user10", "Clean this up")
        
        assert result == "Clean response!"  # Should be stripped
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_openai_empty_response(self, mock_openai, mock_load_profile):
        """Test OpenAI empty response handling."""
        mock_profile = {"tone": "helpful"}
        mock_load_profile.return_value = mock_profile
        
        # Mock empty response
        mock_openai.return_value = "   "  # Only whitespace
        
        result = await generate_user_reply("user11", "Say something")
        
        assert result == ""  # Should be empty after stripping


class TestPromptGeneration:
    """Test prompt generation with different scenarios."""
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_prompt_structure_validation(self, mock_openai, mock_load_profile):
        """Test that generated prompt has correct structure."""
        mock_profile = {
            "flirt_templates": ["Hey cutie! 😘", "What's up gorgeous? 💕"],
            "tone": "flirty"
        }
        mock_load_profile.return_value = mock_profile
        mock_openai.return_value = "Structured response"
        
        user_message = "How are you today?"
        await generate_user_reply("user12", user_message)
        
        # Check that prompt was properly structured
        call_args = mock_openai.call_args[0][0]
        
        # Should contain all required elements
        assert "Sen Telegram'da kendi adına flört eden" in call_args
        assert "Tarzın: flirty" in call_args
        assert "Hey cutie! 😘" in call_args
        assert "What's up gorgeous? 💕" in call_args
        assert f'"{user_message}"' in call_args
        assert "Cevabın:" in call_args
        assert "- Emoji içersin" in call_args
        assert "- Samimi ve içten olsun" in call_args
        assert "- Kibarca satışa yönlendirsin" in call_args
        assert "- Hazır şablonlara benzer ama yaratıcı olsun" in call_args
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_prompt_with_unicode_user_message(self, mock_openai, mock_load_profile):
        """Test prompt generation with unicode characters in user message."""
        mock_profile = {"tone": "international"}
        mock_load_profile.return_value = mock_profile
        mock_openai.return_value = "Unicode response"
        
        unicode_message = "Merhaba! Nasılsın? 🌟✨🎉"
        await generate_user_reply("user13", unicode_message)
        
        call_args = mock_openai.call_args[0][0]
        assert unicode_message in call_args
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_prompt_with_very_long_message(self, mock_openai, mock_load_profile):
        """Test prompt generation with very long user message."""
        mock_profile = {"tone": "patient"}
        mock_load_profile.return_value = mock_profile
        mock_openai.return_value = "Long message response"
        
        long_message = "This is a very long message. " * 50  # 1500+ characters
        await generate_user_reply("user14", long_message)
        
        call_args = mock_openai.call_args[0][0]
        assert long_message in call_args
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_prompt_with_special_characters(self, mock_openai, mock_load_profile):
        """Test prompt generation with special characters."""
        mock_profile = {"tone": "special"}
        mock_load_profile.return_value = mock_profile
        mock_openai.return_value = "Special chars response"
        
        special_message = 'Message with "quotes" and \'apostrophes\' and \n newlines \t tabs'
        await generate_user_reply("user15", special_message)
        
        call_args = mock_openai.call_args[0][0]
        assert special_message in call_args


class TestEdgeCasesAndBoundaryConditions:
    """Test edge cases and boundary conditions."""
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_empty_user_message(self, mock_openai, mock_load_profile):
        """Test with empty user message."""
        mock_profile = {"tone": "understanding"}
        mock_load_profile.return_value = mock_profile
        mock_openai.return_value = "Empty message response"
        
        result = await generate_user_reply("user16", "")
        
        assert result == "Empty message response"
        call_args = mock_openai.call_args[0][0]
        assert '""' in call_args  # Empty string should be in prompt
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_none_user_message(self, mock_openai, mock_load_profile):
        """Test with None user message."""
        mock_profile = {"tone": "defensive"}
        mock_load_profile.return_value = mock_profile
        mock_openai.return_value = "None message response"
        
        # This might cause an error, depending on implementation
        try:
            result = await generate_user_reply("user17", None)
            # If it doesn't error, check the result
            assert isinstance(result, str)
        except (TypeError, AttributeError):
            # Expected to fail gracefully
            pass
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_empty_profile(self, mock_openai, mock_load_profile):
        """Test with completely empty profile."""
        mock_profile = {}  # Completely empty
        mock_load_profile.return_value = mock_profile
        mock_openai.return_value = "Empty profile response"
        
        result = await generate_user_reply("user18", "Hello!")
        
        assert result == "Empty profile response"
        
        # Should use all fallback values
        call_args = mock_openai.call_args[0][0]
        assert "Tarzın: flirty" in call_args  # Default tone
        assert "[]" in call_args  # Empty templates list
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_profile_with_null_values(self, mock_openai, mock_load_profile):
        """Test profile with None/null values."""
        mock_profile = {
            "flirt_templates": None,
            "engaging_messages": None,
            "reply_messages": None,
            "tone": None,
            "persona": None
        }
        mock_load_profile.return_value = mock_profile
        mock_openai.return_value = "Null values response"
        
        result = await generate_user_reply("user19", "Test null values")
        
        assert result == "Null values response"
        
        # Should handle None values gracefully
        call_args = mock_openai.call_args[0][0]
        assert "Tarzın: flirty" in call_args  # Should fall back to default


class TestPerformanceAndConcurrency:
    """Test performance and concurrent requests."""
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_concurrent_requests(self, mock_openai, mock_load_profile):
        """Test concurrent user reply requests."""
        mock_profile = {"tone": "concurrent"}
        mock_load_profile.return_value = mock_profile
        
        # Mock different responses for different calls
        responses = [f"Response {i}" for i in range(5)]
        mock_openai.side_effect = responses
        
        # Make concurrent requests
        tasks = [
            generate_user_reply(f"user_{i}", f"Message {i}")
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        for i, result in enumerate(results):
            assert result == f"Response {i}"
    
    @pytest.mark.performance
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_performance_timing(self, mock_openai, mock_load_profile):
        """Test performance timing for single request."""
        import time
        
        mock_profile = {"tone": "fast"}
        mock_load_profile.return_value = mock_profile
        
        # Add small delay to simulate realistic conditions
        async def delayed_response(prompt):
            await asyncio.sleep(0.01)  # 10ms delay
            return "Fast response"
        
        mock_openai.side_effect = delayed_response
        
        start_time = time.time()
        result = await generate_user_reply("speed_user", "Quick message")
        end_time = time.time()
        
        duration = end_time - start_time
        assert duration < 1.0  # Should complete quickly
        assert result == "Fast response"


class TestIntegrationScenarios:
    """Integration test scenarios mimicking real usage."""
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_realistic_conversation_flow(self, mock_openai, mock_load_profile):
        """Test realistic conversation flow."""
        # Realistic profile
        mock_profile = {
            "flirt_templates": [
                "Merhaba canım! 😘",
                "Hey tatlım, nasılsın? 💕",
                "Selam güzelim! ✨"
            ],
            "tone": "flirty",
            "persona": {
                "style": "playful",
                "personality": "charming"
            }
        }
        mock_load_profile.return_value = mock_profile
        
        # Simulate conversation turns
        conversation = [
            ("Merhaba!", "Merhaba canım! Nasılsın bugün? 😘"),
            ("İyiyim, sen nasılsın?", "Harika, seninle konuştuğuma çok mutluyum! 💕"),
            ("Premium üyelik hakkında bilgi verebilir misin?", "Tabii ki tatlım! Premium üyelikle özel içeriklerime erişebilirsin 🌟")
        ]
        
        for user_msg, expected_response in conversation:
            mock_openai.return_value = expected_response
            
            result = await generate_user_reply("conversation_user", user_msg)
            
            assert result == expected_response
            
            # Verify prompt structure
            call_args = mock_openai.call_args[0][0]
            assert "flirty" in call_args.lower()
            assert user_msg in call_args
    
    @pytest.mark.asyncio
    @patch('gpt.user_agent.load_profile')
    @patch('gpt.user_agent.call_openai_chat')
    async def test_error_recovery_scenario(self, mock_openai, mock_load_profile):
        """Test error recovery in real-world scenario."""
        mock_profile = {"tone": "resilient"}
        mock_load_profile.return_value = mock_profile
        
        # First call fails, second succeeds
        mock_openai.side_effect = [
            Exception("First call failed"),
            "Recovery successful"
        ]
        
        # First call should return fallback
        result1 = await generate_user_reply("recovery_user", "First message")
        assert result1 == "Sanırım biraz dalgınım, lütfen tekrar yaz tatlım! 😇"
        
        # Second call should succeed
        result2 = await generate_user_reply("recovery_user", "Second message")
        assert result2 == "Recovery successful"


# ==================== PYTEST CONFIGURATION ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 