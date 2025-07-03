#!/usr/bin/env python3
"""
🧪 Comprehensive Test Suite for adminbot/main.py 🧪

Testing Strategy:
- Bot initialization and configuration
- Command handlers (start, status, health, help, unknown)
- Authorization system
- Error handling and context managers
- Metrics collection and calculation
- Event handlers setup
- Telethon integration mocking
- Config validation and edge cases

Target Coverage: 95-100%
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock, MagicMock
from typing import Dict, Any

# Add path to import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock imports before importing the main module
mock_telethon = MagicMock()
mock_telethon.TelegramClient = MagicMock
mock_telethon.events = MagicMock()
mock_telethon.errors = MagicMock()

mock_telethon.errors.FloodWaitError = Exception
mock_telethon.errors.UserPrivacyRestrictedError = Exception  
mock_telethon.errors.RPCError = Exception

# Mock the config module
mock_config = MagicMock()
mock_config.ADMIN_BOT_TOKEN = "test_token_123"
mock_config.TELEGRAM_API_ID = 123456
mock_config.TELEGRAM_API_HASH = "test_hash"
mock_config.AUTHORIZED_USERS = [12345, 67890]
mock_config.DEBUG_MODE = True

# Patch the modules before import
with patch.dict('sys.modules', {
    'telethon': mock_telethon,
    'telethon.errors': mock_telethon.errors,
    'telethon.events': mock_telethon.events,
    'config': mock_config
}):
    from adminbot.main import AdminBot, BotMetrics, main

# ==================== FIXTURES ====================

@pytest.fixture
def bot_metrics():
    """Create test BotMetrics instance."""
    return BotMetrics(start_time=datetime.now() - timedelta(hours=1))

@pytest.fixture
def admin_bot():
    """Create test AdminBot instance."""
    return AdminBot()

@pytest.fixture
def mock_event():
    """Create mock Telegram event."""
    event = AsyncMock()
    event.sender_id = 12345  # Authorized user
    event.raw_text = "/test"
    event.respond = AsyncMock()
    return event

@pytest.fixture
def unauthorized_event():
    """Create mock event from unauthorized user."""
    event = AsyncMock()
    event.sender_id = 99999  # Unauthorized user
    event.raw_text = "/test"
    event.respond = AsyncMock()
    return event

@pytest.fixture
def mock_telegram_client():
    """Create mock TelegramClient."""
    client = AsyncMock()
    client.start = AsyncMock()
    client.is_connected = MagicMock(return_value=True)
    client.disconnect = AsyncMock()
    client.run_until_disconnected = AsyncMock()
    client.on = MagicMock()
    
    # Mock get_me response
    me = MagicMock()
    me.id = 123456789
    me.username = "test_bot"
    me.first_name = "Test Bot"
    client.get_me = AsyncMock(return_value=me)
    
    return client

# ==================== BOTMETRICS TESTS ====================

class TestBotMetrics:
    """Test BotMetrics dataclass functionality."""
    
    def test_botmetrics_initialization(self):
        """Test BotMetrics initialization."""
        start_time = datetime.now()
        metrics = BotMetrics(start_time=start_time)
        
        assert metrics.start_time == start_time
        assert metrics.messages_processed == 0
        assert metrics.commands_executed == 0
        assert metrics.errors_encountered == 0
        assert metrics.authorized_access_attempts == 0
        assert metrics.unauthorized_access_attempts == 0
    
    def test_uptime_seconds_calculation(self, bot_metrics):
        """Test uptime seconds calculation."""
        uptime = bot_metrics.uptime_seconds
        assert isinstance(uptime, float)
        assert uptime > 3500  # Should be about 1 hour (3600 seconds)
        assert uptime < 3700
    
    def test_uptime_human_format(self, bot_metrics):
        """Test human readable uptime format."""
        uptime_human = bot_metrics.uptime_human
        assert isinstance(uptime_human, str)
        assert ":" in uptime_human  # Should contain time format
    
    def test_to_dict_conversion(self, bot_metrics):
        """Test metrics to dictionary conversion."""
        # Add some test data
        bot_metrics.messages_processed = 10
        bot_metrics.commands_executed = 8
        bot_metrics.errors_encountered = 2
        
        metrics_dict = bot_metrics.to_dict()
        
        assert isinstance(metrics_dict, dict)
        assert "start_time" in metrics_dict
        assert "uptime_seconds" in metrics_dict
        assert "uptime_human" in metrics_dict
        assert "messages_processed" in metrics_dict
        assert "commands_executed" in metrics_dict
        assert "errors_encountered" in metrics_dict
        assert "authorized_access_attempts" in metrics_dict
        assert "unauthorized_access_attempts" in metrics_dict
        assert "success_rate" in metrics_dict
        
        # Test success rate calculation
        assert metrics_dict["success_rate"] == 80.0  # 8/10 * 100
    
    def test_success_rate_zero_messages(self):
        """Test success rate calculation with zero messages."""
        metrics = BotMetrics(start_time=datetime.now())
        metrics_dict = metrics.to_dict()
        assert metrics_dict["success_rate"] == 0.0

# ==================== ADMINBOT INITIALIZATION TESTS ====================

class TestAdminBotInitialization:
    """Test AdminBot initialization and configuration."""
    
    def test_adminbot_init(self, admin_bot):
        """Test AdminBot initialization."""
        assert admin_bot.client is None
        assert isinstance(admin_bot.metrics, BotMetrics)
        assert admin_bot._running is False
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, admin_bot, mock_telegram_client):
        """Test successful bot initialization."""
        with patch('adminbot.main.TelegramClient', return_value=mock_telegram_client):
            result = await admin_bot.initialize()
            
            assert result is True
            assert admin_bot.client is not None
            mock_telegram_client.start.assert_called_once()
            mock_telegram_client.get_me.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_missing_token(self, admin_bot):
        """Test initialization with missing bot token."""
        with patch('adminbot.main.ADMIN_BOT_TOKEN', None):
            result = await admin_bot.initialize()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_initialize_missing_api_credentials(self, admin_bot):
        """Test initialization with missing API credentials."""
        with patch('adminbot.main.TELEGRAM_API_ID', None):
            result = await admin_bot.initialize()
            assert result is False
        
        with patch('adminbot.main.TELEGRAM_API_HASH', None):
            result = await admin_bot.initialize()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_initialize_telegram_error(self, admin_bot):
        """Test initialization with Telegram connection error."""
        with patch('adminbot.main.TelegramClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.start.side_effect = Exception("Connection failed")
            mock_client_class.return_value = mock_client
            
            result = await admin_bot.initialize()
            assert result is False

# ==================== AUTHORIZATION TESTS ====================

class TestAuthorization:
    """Test user authorization system."""
    
    def test_authorized_user_valid(self, admin_bot):
        """Test authorization with valid user."""
        assert admin_bot.is_authorized_user(12345) is True
        assert admin_bot.is_authorized_user(67890) is True
    
    def test_authorized_user_invalid(self, admin_bot):
        """Test authorization with invalid user."""
        assert admin_bot.is_authorized_user(99999) is False
        assert admin_bot.is_authorized_user(11111) is False
    
    def test_authorized_user_no_config(self, admin_bot):
        """Test authorization with no authorized users configured."""
        with patch('adminbot.main.AUTHORIZED_USERS', None):
            assert admin_bot.is_authorized_user(12345) is False
        
        with patch('adminbot.main.AUTHORIZED_USERS', []):
            assert admin_bot.is_authorized_user(12345) is False

# ==================== ERROR CONTEXT TESTS ====================

class TestErrorContext:
    """Test error context manager functionality."""
    
    @pytest.mark.asyncio
    async def test_error_context_success(self, admin_bot):
        """Test error context with successful operation."""
        async with admin_bot.error_context("test_operation", 12345):
            pass  # No error
        # Should complete without exceptions
    
    @pytest.mark.asyncio
    async def test_error_context_flood_wait(self, admin_bot):
        """Test error context with FloodWaitError."""
        # Create a custom FloodWaitError for testing
        class MockFloodWaitError(Exception):
            def __init__(self, request=None, capture=60):
                self.request = request
                self.seconds = capture
                super().__init__()
        
        with patch('adminbot.main.FloodWaitError', MockFloodWaitError):
            with pytest.raises(MockFloodWaitError):
                async with admin_bot.error_context("test_operation", 12345):
                    raise MockFloodWaitError(request=None, capture=60)
            
            assert admin_bot.metrics.errors_encountered == 1
    
    @pytest.mark.asyncio
    async def test_error_context_generic_error(self, admin_bot):
        """Test error context with generic exception."""
        with pytest.raises(ValueError):
            async with admin_bot.error_context("test_operation", 12345):
                raise ValueError("Test error")
        
        assert admin_bot.metrics.errors_encountered == 1

# ==================== COMMAND HANDLER TESTS ====================

class TestStartCommand:
    """Test /start command handler."""
    
    @pytest.mark.asyncio
    async def test_start_command_authorized(self, admin_bot, mock_event):
        """Test /start command with authorized user."""
        await admin_bot.handle_start_command(mock_event)
        
        mock_event.respond.assert_called_once()
        response = mock_event.respond.call_args[0][0]
        assert "Admin Paneli Hazır" in response
        assert "Onaylandı" in response
        assert admin_bot.metrics.authorized_access_attempts == 1
        assert admin_bot.metrics.commands_executed == 1
    
    @pytest.mark.asyncio
    async def test_start_command_unauthorized(self, admin_bot, unauthorized_event):
        """Test /start command with unauthorized user."""
        await admin_bot.handle_start_command(unauthorized_event)
        
        unauthorized_event.respond.assert_called_once()
        response = unauthorized_event.respond.call_args[0][0]
        assert "Erişim Reddedildi" in response
        assert admin_bot.metrics.unauthorized_access_attempts == 1
        assert admin_bot.metrics.commands_executed == 1

class TestStatusCommand:
    """Test /status command handler."""
    
    @pytest.mark.asyncio
    async def test_status_command_authorized(self, admin_bot, mock_event):
        """Test /status command with authorized user."""
        # Add some metrics data
        admin_bot.metrics.messages_processed = 5
        admin_bot.metrics.commands_executed = 3
        
        await admin_bot.handle_status_command(mock_event)
        
        mock_event.respond.assert_called_once()
        response = mock_event.respond.call_args[0][0]
        assert "GavatCore Admin Bot Status" in response
        assert "Uptime" in response
        assert "5" in response  # messages processed
        assert admin_bot.metrics.authorized_access_attempts == 1
        assert admin_bot.metrics.commands_executed == 4  # 3 + 1 from this command
    
    @pytest.mark.asyncio
    async def test_status_command_unauthorized(self, admin_bot, unauthorized_event):
        """Test /status command with unauthorized user."""
        await admin_bot.handle_status_command(unauthorized_event)
        
        unauthorized_event.respond.assert_called_once()
        response = unauthorized_event.respond.call_args[0][0]
        assert "Bu komut için yetkiniz yok" in response
        assert admin_bot.metrics.unauthorized_access_attempts == 1

class TestHealthCommand:
    """Test /health command handler."""
    
    @pytest.mark.asyncio
    async def test_health_command_authorized_healthy(self, admin_bot, mock_event):
        """Test /health command with authorized user - healthy state."""
        # Setup healthy state
        admin_bot.client = MagicMock()
        admin_bot.client.is_connected.return_value = True
        admin_bot.metrics.errors_encountered = 2  # Below threshold
        
        await admin_bot.handle_health_command(mock_event)
        
        mock_event.respond.assert_called_once()
        response = mock_event.respond.call_args[0][0]
        assert "System Health Check" in response
        assert "✅" in response
        assert "Healthy" in response
        assert admin_bot.metrics.authorized_access_attempts == 1
        assert admin_bot.metrics.commands_executed == 1
    
    @pytest.mark.asyncio
    async def test_health_command_authorized_degraded(self, admin_bot, mock_event):
        """Test /health command with authorized user - degraded state."""
        # Setup degraded state
        admin_bot.client = MagicMock()
        admin_bot.client.is_connected.return_value = False
        admin_bot.metrics.errors_encountered = 15  # Above threshold
        
        await admin_bot.handle_health_command(mock_event)
        
        mock_event.respond.assert_called_once()
        response = mock_event.respond.call_args[0][0]
        assert "System Health Check" in response
        assert "❌" in response
        assert "Degraded" in response
    
    @pytest.mark.asyncio
    async def test_health_command_unauthorized(self, admin_bot, unauthorized_event):
        """Test /health command with unauthorized user."""
        await admin_bot.handle_health_command(unauthorized_event)
        
        unauthorized_event.respond.assert_called_once()
        response = unauthorized_event.respond.call_args[0][0]
        assert "Bu komut için yetkiniz yok" in response
        assert admin_bot.metrics.unauthorized_access_attempts == 1
    
    @pytest.mark.asyncio
    async def test_health_check_no_client(self, admin_bot, mock_event):
        """Test health check with no client."""
        admin_bot.client = None
        
        await admin_bot.handle_health_command(mock_event)
        
        response = mock_event.respond.call_args[0][0]
        assert "Degraded" in response

class TestHelpCommand:
    """Test /help command handler."""
    
    @pytest.mark.asyncio
    async def test_help_command_authorized(self, admin_bot, mock_event):
        """Test /help command with authorized user."""
        await admin_bot.handle_help_command(mock_event)
        
        mock_event.respond.assert_called_once()
        response = mock_event.respond.call_args[0][0]
        assert "GavatCore Admin Bot - Help" in response
        assert "Available Commands" in response
        assert "/start" in response
        assert "/status" in response
        assert "/health" in response
        assert admin_bot.metrics.authorized_access_attempts == 1
        assert admin_bot.metrics.commands_executed == 1
    
    @pytest.mark.asyncio
    async def test_help_command_unauthorized(self, admin_bot, unauthorized_event):
        """Test /help command with unauthorized user."""
        await admin_bot.handle_help_command(unauthorized_event)
        
        unauthorized_event.respond.assert_called_once()
        response = unauthorized_event.respond.call_args[0][0]
        assert "Bu komut için yetkiniz yok" in response
        assert admin_bot.metrics.unauthorized_access_attempts == 1

class TestUnknownCommand:
    """Test unknown command handler."""
    
    @pytest.mark.asyncio
    async def test_unknown_command_authorized(self, admin_bot, mock_event):
        """Test unknown command with authorized user."""
        mock_event.raw_text = "/unknown_command"
        
        await admin_bot.handle_unknown_command(mock_event)
        
        mock_event.respond.assert_called_once()
        response = mock_event.respond.call_args[0][0]
        assert "Bilinmeyen Komut" in response
        assert "/unknown_command" in response
        assert "/help" in response
        assert admin_bot.metrics.authorized_access_attempts == 1
    
    @pytest.mark.asyncio
    async def test_unknown_command_long_message(self, admin_bot, mock_event):
        """Test unknown command with long message (truncation)."""
        long_message = "x" * 150  # Longer than 100 chars
        mock_event.raw_text = long_message
        
        await admin_bot.handle_unknown_command(mock_event)
        
        mock_event.respond.assert_called_once()
        response = mock_event.respond.call_args[0][0]
        assert "..." in response  # Should be truncated
    
    @pytest.mark.asyncio
    async def test_unknown_command_unauthorized(self, admin_bot, unauthorized_event):
        """Test unknown command with unauthorized user."""
        await admin_bot.handle_unknown_command(unauthorized_event)
        
        unauthorized_event.respond.assert_called_once()
        response = unauthorized_event.respond.call_args[0][0]
        assert "Bu komut için yetkiniz yok" in response
        assert admin_bot.metrics.unauthorized_access_attempts == 1
    
    @pytest.mark.asyncio
    async def test_event_handler_with_none_text(self, admin_bot, mock_event):
        """Test event handler with None text."""
        mock_event.raw_text = None
        
        await admin_bot.handle_unknown_command(mock_event)
        
        mock_event.respond.assert_called_once()

# ==================== EVENT HANDLER SETUP TESTS ====================

class TestEventHandlers:
    """Test event handlers setup."""
    
    @pytest.mark.asyncio
    async def test_setup_event_handlers_success(self, admin_bot, mock_telegram_client):
        """Test successful event handlers setup."""
        admin_bot.client = mock_telegram_client
        
        await admin_bot.setup_event_handlers()
        
        # Verify that client.on was called for each command
        assert mock_telegram_client.on.call_count >= 6  # 5 commands + 1 catch-all
    
    @pytest.mark.asyncio
    async def test_setup_event_handlers_no_client(self, admin_bot):
        """Test event handlers setup without client."""
        with pytest.raises(RuntimeError, match="Client not initialized"):
            await admin_bot.setup_event_handlers()

# ==================== BOT EXECUTION TESTS ====================

class TestBotExecution:
    """Test bot execution and lifecycle."""
    
    @pytest.mark.asyncio
    async def test_run_success(self, admin_bot, mock_telegram_client):
        """Test successful bot run."""
        with patch.object(admin_bot, 'initialize', return_value=True), \
             patch.object(admin_bot, 'setup_event_handlers'), \
             patch.object(admin_bot, 'cleanup'):
            
            admin_bot.client = mock_telegram_client
            
            await admin_bot.run()
            
            mock_telegram_client.run_until_disconnected.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_initialization_failed(self, admin_bot):
        """Test bot run with initialization failure."""
        with patch.object(admin_bot, 'initialize', return_value=False), \
             patch.object(admin_bot, 'cleanup'):
            
            await admin_bot.run()
            
            # Should return early without setting up handlers
    
    @pytest.mark.asyncio
    async def test_run_keyboard_interrupt(self, admin_bot, mock_telegram_client):
        """Test bot run with keyboard interrupt."""
        with patch.object(admin_bot, 'initialize', return_value=True), \
             patch.object(admin_bot, 'setup_event_handlers'), \
             patch.object(admin_bot, 'cleanup'):
            
            admin_bot.client = mock_telegram_client
            mock_telegram_client.run_until_disconnected.side_effect = KeyboardInterrupt()
            
            await admin_bot.run()
            
            # Should handle KeyboardInterrupt gracefully
    
    @pytest.mark.asyncio
    async def test_run_exception(self, admin_bot, mock_telegram_client):
        """Test bot run with exception."""
        with patch.object(admin_bot, 'initialize', return_value=True), \
             patch.object(admin_bot, 'setup_event_handlers'), \
             patch.object(admin_bot, 'cleanup'):
            
            admin_bot.client = mock_telegram_client
            mock_telegram_client.run_until_disconnected.side_effect = Exception("Test error")
            
            with pytest.raises(Exception, match="Test error"):
                await admin_bot.run()
    
    @pytest.mark.asyncio
    async def test_cleanup_success(self, admin_bot, mock_telegram_client):
        """Test successful cleanup."""
        admin_bot.client = mock_telegram_client
        admin_bot.metrics.messages_processed = 10
        
        await admin_bot.cleanup()
        
        mock_telegram_client.disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup_no_client(self, admin_bot):
        """Test cleanup with no client."""
        await admin_bot.cleanup()
        # Should complete without error
    
    @pytest.mark.asyncio
    async def test_cleanup_not_connected(self, admin_bot, mock_telegram_client):
        """Test cleanup with disconnected client."""
        mock_telegram_client.is_connected.return_value = False
        admin_bot.client = mock_telegram_client
        
        await admin_bot.cleanup()
        
        mock_telegram_client.disconnect.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_cleanup_exception(self, admin_bot, mock_telegram_client):
        """Test cleanup with exception."""
        mock_telegram_client.disconnect.side_effect = Exception("Disconnect error")
        admin_bot.client = mock_telegram_client
        
        await admin_bot.cleanup()
        
        # Should handle exception gracefully

# ==================== MAIN FUNCTION TESTS ====================

class TestMainFunction:
    """Test main function and entry point."""
    
    @pytest.mark.asyncio
    async def test_main_success(self):
        """Test successful main function execution."""
        with patch('adminbot.main.AdminBot') as mock_bot_class, \
             patch('builtins.print'):
            
            mock_bot = AsyncMock()
            mock_bot_class.return_value = mock_bot
            
            await main()
            
            mock_bot.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_main_keyboard_interrupt(self):
        """Test main function with keyboard interrupt."""
        with patch('adminbot.main.AdminBot') as mock_bot_class, \
             patch('builtins.print'):
            
            mock_bot = AsyncMock()
            mock_bot.run.side_effect = KeyboardInterrupt()
            mock_bot_class.return_value = mock_bot
            
            await main()
            
            # Should handle KeyboardInterrupt gracefully
    
    @pytest.mark.asyncio
    async def test_main_exception(self):
        """Test main function with exception."""
        with patch('adminbot.main.AdminBot') as mock_bot_class, \
             patch('builtins.print'), \
             patch('sys.exit') as mock_exit:
            
            mock_bot = AsyncMock()
            mock_bot.run.side_effect = Exception("Test error")
            mock_bot_class.return_value = mock_bot
            
            await main()
            
            mock_exit.assert_called_once_with(1)

# ==================== INTEGRATION TESTS ====================

class TestIntegration:
    """Integration tests combining multiple components."""
    
    @pytest.mark.asyncio
    async def test_full_command_flow_authorized(self, admin_bot, mock_event, mock_telegram_client):
        """Test complete command flow for authorized user."""
        admin_bot.client = mock_telegram_client
        
        # Simulate start command flow
        await admin_bot.handle_start_command(mock_event)
        await admin_bot.handle_status_command(mock_event)
        await admin_bot.handle_health_command(mock_event)
        await admin_bot.handle_help_command(mock_event)
        
        # Check metrics
        assert admin_bot.metrics.authorized_access_attempts == 4
        assert admin_bot.metrics.commands_executed == 4
        assert admin_bot.metrics.unauthorized_access_attempts == 0
    
    @pytest.mark.asyncio
    async def test_full_command_flow_unauthorized(self, admin_bot, unauthorized_event):
        """Test complete command flow for unauthorized user."""
        # Simulate unauthorized command flow
        await admin_bot.handle_start_command(unauthorized_event)
        await admin_bot.handle_status_command(unauthorized_event)
        await admin_bot.handle_health_command(unauthorized_event)
        await admin_bot.handle_help_command(unauthorized_event)
        
        # Check metrics
        assert admin_bot.metrics.unauthorized_access_attempts == 4
        assert admin_bot.metrics.commands_executed == 1  # Only start command increments

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 