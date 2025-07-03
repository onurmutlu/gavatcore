#!/usr/bin/env python3
"""
🧪 Character Engine Full Test Suite
Test Coverage hedefi: %80+
"""

import pytest
import asyncio
import json
import os
import sys
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

# Path setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from character_engine import (
    CharacterManager,
    CharacterConfig,
    GPTReplyGenerator,
    PersonalityRouter,
    ReplyType,
    FallbackReplyManager,
    MemoryContextTracker
)
from character_engine.token_usage_logger import TokenUsageLogger, TokenUsage

# Test fixtures
@pytest.fixture
def character_manager():
    """Test için character manager"""
    return CharacterManager(config_dir="test_configs")

@pytest.fixture
def test_character_config():
    """Test karakter config'i"""
    return CharacterConfig(
        name="TestBot",
        username="testbot",
        system_prompt="Test bot prompt",
        reply_mode="hybrid",
        tone="flirty",
        cooldown_seconds=30,
        trust_index=0.5,
        template_replies=["Test yanıt 1", "Test yanıt 2"]
    )

@pytest.fixture
def memory_tracker():
    """Test için memory tracker"""
    return MemoryContextTracker(storage_dir="test_memory")

@pytest.fixture
def token_logger():
    """Test için token logger"""
    return TokenUsageLogger(log_dir="test_logs")

# ==================== CHARACTER MANAGER TESTS ====================

class TestCharacterManager:
    """CharacterManager test sınıfı"""
    
    def test_create_character(self, character_manager):
        """Karakter oluşturma testi"""
        char = character_manager.create_character(
            username="test_char",
            name="Test Character",
            system_prompt="Test prompt",
            tone="aggressive"
        )
        
        assert char.username == "test_char"
        assert char.name == "Test Character"
        assert char.tone == "aggressive"
        assert char.reply_mode == "hybrid"  # default
    
    def test_load_character(self, character_manager):
        """Karakter yükleme testi"""
        # Önce oluştur
        character_manager.create_character(
            username="load_test",
            name="Load Test",
            system_prompt="Test"
        )
        
        # Sonra yükle
        loaded = character_manager.load_character("load_test")
        assert loaded is not None
        assert loaded.name == "Load Test"
    
    def test_update_character(self, character_manager):
        """Karakter güncelleme testi"""
        # Oluştur
        character_manager.create_character(
            username="update_test",
            name="Update Test",
            system_prompt="Test"
        )
        
        # Güncelle
        success = character_manager.update_character(
            "update_test",
            tone="dark",
            cooldown_seconds=60
        )
        
        assert success is True
        
        # Kontrol et
        updated = character_manager.load_character("update_test")
        assert updated.tone == "dark"
        assert updated.cooldown_seconds == 60
    
    def test_delete_character(self, character_manager):
        """Karakter silme testi"""
        # Oluştur
        character_manager.create_character(
            username="delete_test",
            name="Delete Test",
            system_prompt="Test"
        )
        
        # Sil
        success = character_manager.delete_character("delete_test")
        assert success is True
        
        # Yüklemeyi dene
        deleted = character_manager.load_character("delete_test")
        assert deleted is None
    
    def test_list_characters(self, character_manager):
        """Karakter listeleme testi"""
        # Birkaç karakter oluştur
        for i in range(3):
            character_manager.create_character(
                username=f"list_test_{i}",
                name=f"List Test {i}",
                system_prompt="Test"
            )
        
        characters = character_manager.list_characters()
        assert len(characters) >= 3
        assert "list_test_0" in characters

# ==================== GPT REPLY GENERATOR TESTS ====================

class TestGPTReplyGenerator:
    """GPTReplyGenerator test sınıfı"""
    
    @pytest.mark.asyncio
    async def test_generate_reply_no_client(self):
        """GPT client olmadan test"""
        generator = GPTReplyGenerator(api_key=None)
        
        reply = await generator.generate_reply(
            "Test mesaj",
            {"name": "Test", "system_prompt": "Test"},
            []
        )
        
        assert reply is None
    
    @pytest.mark.asyncio
    @patch('character_engine.gpt_reply_generator.AsyncOpenAI')
    async def test_generate_reply_with_mock(self, mock_openai):
        """Mock GPT client ile test"""
        # Mock response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Mock yanıt"))]
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20)
        
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client
        
        generator = GPTReplyGenerator(api_key="test-key")
        
        reply = await generator.generate_reply(
            "Test mesaj",
            {
                "name": "Test",
                "system_prompt": "Test prompt",
                "tone": "flirty"
            },
            []
        )
        
        assert reply == "Mock yanıt"
        mock_client.chat.completions.create.assert_called_once()
    
    def test_build_system_prompt(self):
        """System prompt oluşturma testi"""
        generator = GPTReplyGenerator()
        
        prompt = generator._build_system_prompt(
            {
                "name": "TestBot",
                "system_prompt": "Base prompt",
                "tone": "aggressive"
            },
            strategy="manipulate"
        )
        
        assert "TestBot" in prompt
        assert "Base prompt" in prompt
        assert "dominant" in prompt.lower()  # aggressive tone
        assert "kontrol" in prompt.lower()  # manipulate strategy
    
    def test_select_model(self):
        """Model seçimi testi"""
        generator = GPTReplyGenerator()
        
        # Basit mesaj - ucuz model
        model = generator._select_model(
            {"tone": "soft"},
            None,
            "Merhaba"
        )
        assert model == "gpt-3.5-turbo"
        
        # VIP sorgu - pahalı model
        model = generator._select_model(
            {"tone": "flirty"},
            None,
            "VIP gruba nasıl katılabilirim?"
        )
        assert model == "gpt-4-turbo-preview"
        
        # Config'de belirtilmişse
        model = generator._select_model(
            {"gpt_model": "gpt-4"},
            None,
            "Test"
        )
        assert model == "gpt-4"

# ==================== PERSONALITY ROUTER TESTS ====================

class TestPersonalityRouter:
    """PersonalityRouter test sınıfı"""
    
    def test_route_reply_basic(self):
        """Temel yanıt yönlendirme testi"""
        router = PersonalityRouter()
        
        reply_type, params = router.route_reply(
            "Seni özledim",
            {"tone": "flirty"},
            {"trust_index": 0.8, "message_count": 10},
            {"emotion": "desperate"}
        )
        
        assert reply_type == ReplyType.MANIPULATIVE
        assert params["intensity"] == "high"
    
    def test_route_reply_sad_emotion(self):
        """Üzgün duygu testi"""
        router = PersonalityRouter()
        
        reply_type, params = router.route_reply(
            "Çok üzgünüm",
            {"tone": "soft"},
            {"trust_index": 0.5, "message_count": 5},
            {"emotion": "sad"}
        )
        
        assert reply_type == ReplyType.COMFORTING
        assert params["warmth"] == "high"
    
    def test_apply_strategy_romantic(self):
        """Romantik strateji testi"""
        router = PersonalityRouter()
        
        result = router._romantic_strategy(
            "Test yanıt",
            {"intensity": "high", "emoji_count": 2}
        )
        
        assert "Aşkım" in result
        assert result.count("❤") >= 1 or result.count("💕") >= 1
    
    def test_apply_strategy_aggressive(self):
        """Agresif strateji testi"""
        router = PersonalityRouter()
        
        result = router._aggressive_strategy(
            "Yapabilir misin bunu?",
            {}
        )
        
        assert "yap" in result
        assert result.endswith("!")

# ==================== MEMORY CONTEXT TRACKER TESTS ====================

class TestMemoryContextTracker:
    """MemoryContextTracker test sınıfı"""
    
    def test_add_message(self, memory_tracker):
        """Mesaj ekleme testi"""
        user_id = "test_user"
        
        memory_tracker.add_message(
            user_id,
            "user",
            "Test mesaj",
            {"timestamp": datetime.now().isoformat()}
        )
        
        context = memory_tracker.get_context(user_id)
        assert len(context) == 1
        assert context[0]["content"] == "Test mesaj"
    
    def test_get_user_context(self, memory_tracker):
        """Kullanıcı bağlamı testi"""
        user_id = "context_test"
        
        # Birkaç mesaj ekle
        for i in range(5):
            memory_tracker.add_message(
                user_id,
                "user" if i % 2 == 0 else "assistant",
                f"Mesaj {i}"
            )
        
        context = memory_tracker.get_user_context(user_id)
        
        assert context["user_id"] == user_id
        assert context["message_count"] == 5
        assert "trust_index" in context
        assert "relationship_depth" in context
    
    def test_calculate_trust_index(self, memory_tracker):
        """Trust index hesaplama testi"""
        stats = {
            "total_messages": 50,
            "emotion_scores": {
                "happy": 20,
                "flirty": 10,
                "sad": 5,
                "angry": 2
            },
            "last_contact": datetime.now().isoformat(),
            "karma_score": 50
        }
        
        trust = memory_tracker._calculate_trust_index(stats)
        
        assert 0.0 <= trust <= 1.0
        assert trust > 0.5  # Pozitif duygular fazla
    
    def test_clear_memory(self, memory_tracker):
        """Hafıza temizleme testi"""
        user_id = "clear_test"
        
        # Mesaj ekle
        memory_tracker.add_message(user_id, "user", "Test")
        
        # Temizle
        memory_tracker.clear_user_memory(user_id)
        
        # Kontrol et
        context = memory_tracker.get_context(user_id)
        assert len(context) == 0

# ==================== FALLBACK REPLY MANAGER TESTS ====================

class TestFallbackReplyManager:
    """FallbackReplyManager test sınıfı"""
    
    @pytest.mark.asyncio
    async def test_get_fallback_reply(self):
        """Fallback yanıt testi"""
        manager = FallbackReplyManager()
        
        reply = await manager.get_fallback_reply(
            "test_user",
            {"tone": "flirty"},
            "timeout"
        )
        
        assert reply is not None
        assert len(reply) > 0
    
    def test_get_template_reply(self):
        """Template yanıt testi"""
        manager = FallbackReplyManager()
        
        reply = manager._get_template_reply("timeout", "aggressive")
        
        assert reply is not None
        assert any(word in reply for word in ["Cevap", "konuş", "sus"])
    
    @pytest.mark.asyncio
    async def test_progressive_strategy(self):
        """Progressive strateji testi"""
        manager = FallbackReplyManager()
        
        # İlk fallback - soft olmalı
        reply1 = await manager._progressive_strategy(
            "prog_test",
            {"tone": "flirty"},
            "timeout",
            None
        )
        
        # Geçmiş ekle
        manager.user_fallback_history["prog_test"] = [
            {"timestamp": datetime.now().isoformat()} for _ in range(6)
        ]
        
        # 6. fallback - agresif olmalı
        reply2 = await manager._progressive_strategy(
            "prog_test",
            {"tone": "flirty"},
            "timeout",
            None
        )
        
        assert reply1 != reply2

# ==================== TOKEN USAGE LOGGER TESTS ====================

class TestTokenUsageLogger:
    """TokenUsageLogger test sınıfı"""
    
    def test_log_usage(self, token_logger):
        """Token kullanım loglama testi"""
        usage = token_logger.log_usage(
            character="TestBot",
            user_id="test_user",
            model="gpt-3.5-turbo",
            prompt_tokens=100,
            completion_tokens=50,
            reply_mode="gpt",
            success=True
        )
        
        assert usage.total_tokens == 150
        assert usage.cost_usd > 0
        assert usage.character == "TestBot"
    
    def test_calculate_cost(self, token_logger):
        """Maliyet hesaplama testi"""
        # GPT-3.5 maliyeti
        cost = token_logger._calculate_cost(
            "gpt-3.5-turbo",
            1000,  # 1K prompt token
            500    # 0.5K completion token
        )
        
        expected = (1.0 * 0.0005) + (0.5 * 0.0015)  # $0.00125
        assert abs(cost - expected) < 0.0001
    
    def test_get_daily_stats(self, token_logger):
        """Günlük istatistik testi"""
        # Birkaç kullanım logla
        for i in range(3):
            token_logger.log_usage(
                character="TestBot",
                user_id=f"user_{i}",
                model="gpt-3.5-turbo",
                prompt_tokens=100,
                completion_tokens=50,
                reply_mode="gpt"
            )
        
        stats = token_logger.get_daily_stats()
        
        assert stats["total_requests"] >= 3
        assert stats["total_tokens"] >= 450
        assert stats["total_cost_usd"] > 0
        assert "TestBot" in stats["by_character"]
    
    def test_format_stats_message(self, token_logger):
        """İstatistik mesajı formatlama testi"""
        # Test verisi ekle
        token_logger.log_usage(
            character="TestBot",
            user_id="test",
            model="gpt-4",
            prompt_tokens=500,
            completion_tokens=200,
            reply_mode="gpt"
        )
        
        message = token_logger.format_stats_message()
        
        assert "Token İstatistikleri" in message
        assert "Toplam İstek" in message
        assert "Maliyet" in message
        assert "$" in message

# ==================== INTEGRATION TESTS ====================

class TestIntegration:
    """Entegrasyon testleri"""
    
    @pytest.mark.asyncio
    async def test_full_flow(self, character_manager, memory_tracker):
        """Tam akış testi"""
        # Karakter oluştur
        char = character_manager.create_character(
            username="integration_test",
            name="Integration Bot",
            system_prompt="Test bot",
            reply_mode="manual",
            template_replies=["Test yanıt"]
        )
        
        # Mesaj ekle
        memory_tracker.add_message(
            "test_user",
            "user",
            "Merhaba"
        )
        
        # Bağlam al
        context = memory_tracker.get_context("test_user")
        user_context = memory_tracker.get_user_context("test_user")
        
        # Router ile yanıt tipi belirle
        router = PersonalityRouter()
        reply_type, params = router.route_reply(
            "Merhaba",
            char.to_dict(),
            user_context
        )
        
        assert reply_type is not None
        assert params is not None
        
        # Template yanıt al
        import random
        reply = random.choice(char.template_replies)
        
        # Hafızaya ekle
        memory_tracker.add_message(
            "test_user",
            "assistant",
            reply
        )
        
        # Final kontrol
        final_context = memory_tracker.get_context("test_user")
        assert len(final_context) == 2

# Test cleanup
@pytest.fixture(autouse=True)
def cleanup():
    """Test sonrası temizlik"""
    yield
    
    # Test dosyalarını temizle
    import shutil
    for dir_name in ["test_configs", "test_memory", "test_logs"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=character_engine", "--cov-report=html"]) 