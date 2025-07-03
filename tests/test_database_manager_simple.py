#!/usr/bin/env python3
"""
🧪 Simple Database Manager Test Suite 🧪

Sadece temel fonksiyonları test eden minimal test suite.
Coverage hedefi: %80+
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import patch, AsyncMock
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database_manager import DatabaseManager, BroadcastStatus, UserInteractionType, BroadcastTarget, UserAnalytics


# ==================== SIMPLE TEST CLASS ====================

class TestDatabaseManager:
    """Basit database manager testleri."""
    
    @pytest.mark.asyncio
    async def test_basic_operations(self):
        """Test basic database operations."""
        # Create temp database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            manager = DatabaseManager(db_path)
            await manager.initialize()
            
            # Test add broadcast target
            target_id = await manager.add_broadcast_target(
                target_id=12345,
                target_type="user", 
                description="Test user"
            )
            assert target_id == 12345
            
            # Test get targets
            targets = await manager.get_broadcast_targets()
            assert len(targets) >= 1
            
            # Test user analytics
            await manager.update_user_analytics(
                user_id=12345,
                username="testuser",
                interaction_count=5
            )
            
            # Test log interaction
            await manager.log_user_interaction(
                user_id=12345,
                interaction_type=UserInteractionType.MESSAGE
            )
            
            # Test broadcast attempt
            result = await manager.log_broadcast_attempt(
                broadcast_id="test",
                target_id=12345,
                target_type="user",
                bot_username="testbot",
                message_type="text",
                message_content="test",
                status=BroadcastStatus.SENT
            )
            assert result is True
            
            # Test stats
            stats = await manager.get_broadcast_stats()
            assert isinstance(stats, dict)
            
            # Test AI analysis
            users = await manager.get_users_for_ai_analysis()
            assert isinstance(users, list)
            
            # Test CRM segment
            result = await manager.create_crm_segment(
                segment_name="test_segment",
                criteria={"engagement_level": "high"}
            )
            assert isinstance(result, bool)
            
            await manager.close()
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in database operations."""
        # Test with invalid database path
        manager = DatabaseManager("/invalid/path/test.db")
        
        # Should not raise exception due to error handling
        await manager.initialize()
        
        # Operations should return empty/default values
        targets = await manager.get_broadcast_targets()
        assert targets == []
        
        stats = await manager.get_broadcast_stats()
        assert stats == {}
        
        users = await manager.get_users_for_ai_analysis()
        assert users == []
    
    @pytest.mark.asyncio
    async def test_database_connection_error(self):
        """Test database connection errors."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            manager = DatabaseManager(db_path)
            await manager.initialize()
            
            # Mock database connection error
            with patch('aiosqlite.connect', side_effect=Exception("Connection failed")):
                # These should handle errors gracefully
                targets = await manager.get_broadcast_targets()
                assert targets == []
                
                result = await manager.log_broadcast_attempt(
                    broadcast_id="error_test",
                    target_id=12345,
                    target_type="user",
                    bot_username="testbot",
                    message_type="text",
                    message_content="test",
                    status=BroadcastStatus.FAILED
                )
                # Should not raise exception
                
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.asyncio
    async def test_enum_values(self):
        """Test enum and dataclass functionality."""
        # Test BroadcastStatus enum
        assert BroadcastStatus.SENT == "sent"
        assert BroadcastStatus.FAILED == "failed"
        assert BroadcastStatus.PENDING == "pending"
        
        # Test UserInteractionType enum
        assert UserInteractionType.MESSAGE == "message"
        assert UserInteractionType.VOICE_CHAT == "voice_chat"
        assert UserInteractionType.DM_ACTIVITY == "dm_activity"
        
        # Test BroadcastTarget dataclass
        target = BroadcastTarget(
            target_id=12345,
            target_type="user",
            bot_username="testbot"
        )
        assert target.target_id == 12345
        assert target.target_type == "user"
        assert target.bot_username == "testbot"
        
        # Test UserAnalytics dataclass
        analytics = UserAnalytics(
            user_id=12345,
            username="testuser",
            interaction_count=10,
            last_interaction=datetime.now()
        )
        assert analytics.user_id == 12345
        assert analytics.username == "testuser"
        assert analytics.interaction_count == 10
    
    @pytest.mark.asyncio
    async def test_activity_score_calculation(self):
        """Test activity score calculation edge cases."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            manager = DatabaseManager(db_path)
            await manager.initialize()
            
            # Test with high interaction data
            await manager.update_user_analytics(
                user_id=99999,
                username="highactivity",
                interaction_data={
                    "message_count": 100,
                    "voice_minutes": 120,
                    "quest_completed": True
                }
            )
            
            # Test with minimal interaction data
            await manager.update_user_analytics(
                user_id=88888,
                username="lowactivity",
                interaction_data={"message_count": 1}
            )
            
            await manager.close()
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 