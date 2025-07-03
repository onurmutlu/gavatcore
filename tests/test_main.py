#!/usr/bin/env python3
"""
🧪 GavatCore Kernel 1.0 Test Suite 🧪

Test scenarios for main.py functionality including:
- Connection testing
- Event handlers
- Background tasks
- Statistics tracking
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

# Test imports
import main
from main import test_connections, handle_reply, handle_stats_command, handle_cleanup_command

class TestGavatCoreMain:
    """🚀 Test suite for main.py GavatCore Kernel"""
    
    @pytest.mark.asyncio
    async def test_connection_success(self):
        """Test successful database connections"""
        
        # Mock the actual Redis and MongoDB objects at module level
        with patch.object(main, 'redis') as mock_redis, \
             patch.object(main, 'mongo_db') as mock_mongo:
            
            # Mock successful connections
            mock_redis.ping = AsyncMock(return_value=True)
            mock_mongo.command = AsyncMock(return_value={"ok": 1})
            
            result = await test_connections()
            
            assert result is True
            mock_redis.ping.assert_called_once()
            mock_mongo.command.assert_called_once_with("ping")
    
    @pytest.mark.asyncio
    async def test_connection_failure(self):
        """Test database connection failures"""
        
        with patch.object(main, 'redis') as mock_redis:
            # Mock Redis failure
            mock_redis.ping = AsyncMock(side_effect=Exception("Redis connection failed"))
            
            result = await test_connections()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_dm_request_handling(self):
        """Test DM request message handling"""
        
        # Mock event
        mock_event = AsyncMock()
        mock_event.is_reply = True
        mock_event.raw_text = "dm at bana"
        mock_event.sender_id = 123456
        mock_event.respond = AsyncMock()
        
        # Mock user - needs to be instance of User type
        from telethon.tl.types import User
        mock_user = MagicMock(spec=User)
        mock_user.id = 123456
        mock_user.username = "testuser"
        mock_event.get_sender = AsyncMock(return_value=mock_user)
        
        # Mock contact_utils
        with patch.object(main, 'add_contact_with_fallback') as mock_contact:
            mock_contact.return_value = "✅ Ekledim, DM başlatabilirsin"
            
            # Execute handler
            await handle_reply(mock_event)
            
            # Assertions
            mock_event.get_sender.assert_called_once()
            mock_contact.assert_called_once()
            mock_event.respond.assert_called_once_with("✅ Ekledim, DM başlatabilirsin")
    
    @pytest.mark.asyncio 
    async def test_stats_command(self):
        """Test /stats command handler"""
        
        # Mock event
        mock_event = AsyncMock()
        mock_event.sender_id = 123456
        mock_event.respond = AsyncMock()
        
        # Set initial stats
        main.stats["start_time"] = datetime.now() - timedelta(hours=1)
        main.stats["messages_processed"] = 10
        main.stats["contacts_added"] = 5
        main.stats["errors_encountered"] = 1
        main.stats["cleanup_runs"] = 2
        
        # Execute handler
        await handle_stats_command(mock_event)
        
        # Verify response was sent
        mock_event.respond.assert_called_once()
        
        # Check response contains stats
        response_text = mock_event.respond.call_args[0][0]
        assert "İstatistikleri" in response_text
        assert "10" in response_text  # messages processed
        assert "5" in response_text   # contacts added
    
    @pytest.mark.asyncio
    async def test_cleanup_command_success(self):
        """Test successful /cleanup command"""
        
        # Mock event
        mock_event = AsyncMock()
        mock_event.sender_id = 123456
        mock_event.respond = AsyncMock()
        
        # Mock successful cleanup
        with patch.object(main, 'quick_cleanup') as mock_cleanup:
            mock_cleanup.return_value = {
                "success": True,
                "sessions_found": 10,
                "sessions_deleted": 7,
                "sessions_preserved": 3,
                "processing_time_seconds": 0.15,
                "log_document_id": "test_log_id_123456"
            }
            
            # Execute handler
            await handle_cleanup_command(mock_event)
            
            # Verify responses
            assert mock_event.respond.call_count == 2  # Status + result
            
            # Check first response (status)
            first_call = mock_event.respond.call_args_list[0][0][0]
            assert "cleanup başlatılıyor" in first_call
            
            # Check second response (result)
            second_call = mock_event.respond.call_args_list[1][0][0]
            assert "Cleanup Tamamlandı" in second_call
            assert "7" in second_call  # deleted sessions
    
    @pytest.mark.asyncio
    async def test_cleanup_command_failure(self):
        """Test failed /cleanup command"""
        
        # Mock event
        mock_event = AsyncMock()
        mock_event.sender_id = 123456
        mock_event.respond = AsyncMock()
        
        # Mock failed cleanup
        with patch.object(main, 'quick_cleanup') as mock_cleanup:
            mock_cleanup.return_value = {
                "success": False,
                "error": "Redis connection failed"
            }
            
            # Execute handler
            await handle_cleanup_command(mock_event)
            
            # Verify error response
            assert mock_event.respond.call_count == 2
            
            second_call = mock_event.respond.call_args_list[1][0][0]
            assert "başarısız" in second_call
            assert "Redis connection failed" in second_call
    
    @pytest.mark.asyncio
    async def test_non_dm_message_ignored(self):
        """Test that non-DM messages are ignored"""
        
        # Mock event with non-DM message - not a reply OR no DM keywords
        mock_event = AsyncMock()
        mock_event.is_reply = False  # Not a reply - should be ignored
        mock_event.raw_text = "normal mesaj"
        mock_event.sender_id = 123456
        mock_event.respond = AsyncMock()
        
        # Execute handler
        await handle_reply(mock_event)
        
        # Should not respond
        mock_event.respond.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_reply_without_dm_keywords(self):
        """Test reply message without DM keywords"""
        
        # Mock event that's a reply but no DM keywords
        mock_event = AsyncMock()
        mock_event.is_reply = True
        mock_event.raw_text = "teşekkürler"  # No DM keywords
        mock_event.sender_id = 123456
        mock_event.respond = AsyncMock()
        
        # Execute handler
        await handle_reply(mock_event)
        
        # Should not respond (no DM keywords)
        mock_event.respond.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_error_handling_in_message(self):
        """Test error handling in message processing"""
        
        # Mock event that causes error
        mock_event = AsyncMock()
        mock_event.is_reply = True
        mock_event.raw_text = "dm at bana"
        mock_event.sender_id = 123456
        mock_event.get_sender = AsyncMock(side_effect=Exception("Network error"))
        mock_event.respond = AsyncMock()
        
        # Execute handler (should not crash)
        await handle_reply(mock_event)
        
        # Should send error response
        mock_event.respond.assert_called_once()
        response = mock_event.respond.call_args[0][0]
        assert "hata oluştu" in response
    
    def test_stats_initialization(self):
        """Test that global stats are properly initialized"""
        
        assert "start_time" in main.stats
        assert "messages_processed" in main.stats
        assert "contacts_added" in main.stats
        assert "errors_encountered" in main.stats
        assert "cleanup_runs" in main.stats
        
        # Should be datetime object
        assert isinstance(main.stats["start_time"], datetime)
    
    @pytest.mark.asyncio
    async def test_signal_handler_functionality(self):
        """Test signal handler setup (mock test)"""
        
        with patch('main.signal') as mock_signal, \
             patch('main.sys') as mock_sys:
            
            # Import should set up signal handlers
            from main import signal_handler
            
            # Test signal handler function
            signal_handler(2, None)  # SIGINT
            
            # Should exit
            mock_sys.exit.assert_called_once_with(0)

# --- Additional Connection Tests ---
@pytest.mark.asyncio
async def test_connections_direct():
    """Direct test for connection function"""
    
    with patch.object(main, 'redis') as mock_redis, \
         patch.object(main, 'mongo_db') as mock_mongo:
        
        # Mock successful connections
        mock_redis.ping = AsyncMock(return_value=True)
        mock_mongo.command = AsyncMock(return_value={"ok": 1})
        
        result = await test_connections()
        
        assert result is True
        mock_redis.ping.assert_called_once()
        mock_mongo.command.assert_called_once_with("ping")

# --- Test Configuration ---
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

if __name__ == "__main__":
    # Run tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--asyncio-mode=auto"
    ]) 