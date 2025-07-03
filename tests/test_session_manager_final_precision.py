#!/usr/bin/env python3
"""
🎯 SessionManager FINAL Precision Coverage - %97.6 → %100 🎯

Son 6 missing line için ultra-surgical precision:

Missing Lines:
- 319->325: Database lock retry condition
- 322-323: Exception handling in client disconnect 
- 348->354: Branch coverage in finally block
- 357: Final return None, None path
- 647: notify_admin_dm exception path
- 656: create_session_flow config import
- 659: create_session_flow print statement

BU SON ROUND - %100 COVERAGE HEDEFI!
"""

import pytest
import asyncio
import os
import sys
import tempfile
from unittest.mock import patch, AsyncMock, MagicMock, call
from typing import Dict, Any, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.session_manager import (
    SessionManager, SessionConfig, SessionMetrics,
    session_manager, session_metrics,
    notify_admin_dm, create_session_flow
)

# ==================== ULTRA-SURGICAL FINAL TESTS ====================

class TestSessionManagerUltraPrecision:
    """Ultra-surgical tests for the final 6 missing lines."""
    
    @pytest.mark.asyncio
    async def test_line_319_325_database_lock_retry_exact_path(self):
        """Test exact lines 319->325: Database lock retry condition."""
        
        session_manager_instance = SessionManager(SessionConfig(
            max_retry_attempts=3,
            base_retry_delay=0.01
        ))
        
        # Reset metrics to track precisely
        session_metrics.database_lock_encounters = 0
        session_metrics.total_retry_attempts = 0
        
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()
        mock_client.is_user_authorized = AsyncMock(return_value=False)
        mock_client.send_code_request = AsyncMock()
        mock_client.sign_in = AsyncMock()
        
        # Precise setup: First call raises database lock, second succeeds
        call_count = 0
        def mock_get_me():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # Line 319: This will trigger database lock detection
                raise Exception("database is locked")
            elif call_count == 2:
                # Line 325: This will trigger the retry logic
                raise Exception("database is locked")  
            else:
                # After retries, final attempt
                raise Exception("final failure")
        
        mock_client.get_me = AsyncMock(side_effect=mock_get_me)
        
        with patch('core.session_manager.TelegramClient', return_value=mock_client):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=2048):
                    with patch.object(session_manager_instance, 'validate_session_file', 
                                    return_value=(True, "")):
                        
                        async def mock_code_cb():
                            return "12345"
                        
                        async def mock_password_cb():
                            return "password"
                        
                        try:
                            # This should hit lines 319->325 exactly
                            result = await session_manager_instance.open_session(
                                phone="+905551234567",
                                api_id=123456,
                                api_hash="test_hash",
                                code_cb=mock_code_cb,
                                password_cb=mock_password_cb
                            )
                        except Exception as e:
                            # Expected to fail after retries
                            pass
                        
                        # Verify that database lock retry logic was triggered
                        assert session_metrics.database_lock_encounters >= 2
                        assert session_metrics.total_retry_attempts >= 2
    
    @pytest.mark.asyncio
    async def test_line_322_323_client_disconnect_exception_exact_path(self):
        """Test exact lines 322-323: Exception handling in client disconnect during retry."""
        
        session_manager_instance = SessionManager(SessionConfig(
            max_retry_attempts=2,
            base_retry_delay=0.01
        ))
        
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        # Line 322-323: Make disconnect raise exception
        mock_client.disconnect = AsyncMock(side_effect=Exception("Disconnect failed"))
        mock_client.is_user_authorized = AsyncMock(return_value=False)
        mock_client.send_code_request = AsyncMock()
        mock_client.sign_in = AsyncMock()
        
        # Trigger database lock to enter retry path
        mock_client.get_me = AsyncMock(side_effect=[
            Exception("database is locked"),  # First attempt
            Exception("database is locked")   # Second attempt  
        ])
        
        with patch('core.session_manager.TelegramClient', return_value=mock_client):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=2048):
                    with patch.object(session_manager_instance, 'validate_session_file', 
                                    return_value=(True, "")):
                        
                        async def mock_code_cb():
                            return "12345"
                        
                        async def mock_password_cb():
                            return "password"
                        
                        try:
                            # This should hit lines 322-323 (client disconnect exception in retry cleanup)
                            result = await session_manager_instance.open_session(
                                phone="+905551234567",
                                api_id=123456,
                                api_hash="test_hash",
                                code_cb=mock_code_cb,
                                password_cb=mock_password_cb
                            )
                        except Exception as e:
                            # Expected to fail, but lines 322-323 should be covered
                            pass
                        
                        # Verify disconnect was attempted despite exception
                        assert mock_client.disconnect.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_line_348_354_finally_block_branch_exact_path(self):
        """Test exact lines 348->354: Branch coverage in finally block."""
        
        session_manager_instance = SessionManager(SessionConfig(
            max_retry_attempts=1,
            base_retry_delay=0.01
        ))
        
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        # Line 351-352: Make disconnect raise exception in finally block
        mock_client.disconnect = AsyncMock(side_effect=Exception("Finally disconnect failed"))
        mock_client.is_user_authorized = AsyncMock(return_value=False)
        mock_client.send_code_request = AsyncMock()
        mock_client.sign_in = AsyncMock()
        mock_client.get_me = AsyncMock(side_effect=Exception("Connection failed"))
        
        with patch('core.session_manager.TelegramClient', return_value=mock_client):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=2048):
                    with patch.object(session_manager_instance, 'validate_session_file', 
                                    return_value=(True, "")):
                        
                        async def mock_code_cb():
                            return "12345"
                        
                        async def mock_password_cb():
                            return "password"
                        
                        try:
                            # This should hit lines 348->354 (finally block with disconnect exception)
                            result = await session_manager_instance.open_session(
                                phone="+905551234567",
                                api_id=123456,
                                api_hash="test_hash",
                                code_cb=mock_code_cb,
                                password_cb=mock_password_cb
                            )
                        except Exception as e:
                            # Expected to fail, but finally block should be covered
                            pass
                        
                        # Verify finally block was executed
                        assert mock_client.disconnect.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_line_357_final_return_none_exact_path(self):
        """Test exact line 357: Final return None, None path."""
        
        session_manager_instance = SessionManager(SessionConfig(
            max_retry_attempts=1,  # Minimal retries to reach line 357 quickly
            base_retry_delay=0.01
        ))
        
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()
        mock_client.is_user_authorized = AsyncMock(return_value=False)
        mock_client.send_code_request = AsyncMock()
        mock_client.sign_in = AsyncMock()
        # Make every attempt fail to reach line 357
        mock_client.get_me = AsyncMock(side_effect=Exception("Persistent failure"))
        
        with patch('core.session_manager.TelegramClient', return_value=mock_client):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=2048):
                    with patch.object(session_manager_instance, 'validate_session_file', 
                                    return_value=(True, "")):
                        
                        async def mock_code_cb():
                            return "12345"
                        
                        async def mock_password_cb():
                            return "password"
                        
                        # This should exhaust all retries and hit line 357: return None, None
                        result = await session_manager_instance.open_session(
                            phone="+905551234567",
                            api_id=123456,
                            api_hash="test_hash",
                            code_cb=mock_code_cb,
                            password_cb=mock_password_cb
                        )
                        
                        # Line 357: Should return None, None after exhausting retries
                        assert result == (None, None)
    
    @pytest.mark.asyncio
    async def test_line_647_notify_admin_dm_exception_exact_path(self):
        """Test exact line 647: notify_admin_dm exception path."""
        
        mock_bot_client = AsyncMock()
        # Line 647: Make send_message raise exception
        mock_bot_client.send_message = AsyncMock(side_effect=Exception("Send failed"))
        
        # This should hit line 647 exactly
        await notify_admin_dm(mock_bot_client, 123456, "Test message")
        
        # Verify send_message was attempted and exception was handled
        mock_bot_client.send_message.assert_called_once_with(123456, "Test message")
    
    @pytest.mark.asyncio
    async def test_line_656_create_session_flow_config_import_exact_path(self):
        """Test exact line 656: create_session_flow config import exception."""
        
        # Mock input to avoid hanging
        with patch('builtins.input', side_effect=["+905551234567", "12345", "password"]):
            # Create a precise import mock that only affects the config import
            original_import = __builtins__['__import__']
            
            def selective_import_mock(name, globals=None, locals=None, fromlist=(), level=0):
                if name == 'config' and fromlist == ('API_ID', 'API_HASH'):
                    # Line 656: Exact path - config import failure
                    raise ImportError("Config module not found")
                return original_import(name, globals, locals, fromlist, level)
            
            with patch('builtins.__import__', side_effect=selective_import_mock):
                with patch('builtins.print') as mock_print:
                    # This should hit line 656 exactly
                    await create_session_flow()
                    
                    # Verify error was printed (line 672)
                    assert any("❌ Hata:" in str(call) for call in mock_print.call_args_list)
    
    @pytest.mark.asyncio
    async def test_line_659_create_session_flow_print_exact_path(self):
        """Test exact line 659: create_session_flow print statement when session creation fails."""
        
        # Mock successful config import
        mock_config = MagicMock()
        mock_config.API_ID = 123456
        mock_config.API_HASH = "test_hash"
        
        with patch('builtins.input', side_effect=["+905551234567", "12345", "password"]):
            with patch.dict('sys.modules', {'config': mock_config}):
                # Line 659: Make open_session return None, None to trigger print
                with patch('core.session_manager.open_session', return_value=(None, None)):
                    with patch('builtins.print') as mock_print:
                        
                        # This should hit line 659 exactly
                        await create_session_flow()
                        
                        # Line 659: Verify exact print statement
                        mock_print.assert_any_call("❌ Session oluşturulamadı")
    
    @pytest.mark.asyncio
    async def test_comprehensive_final_missing_paths(self):
        """Comprehensive test to hit all remaining missing paths in one go."""
        
        # Test all remaining lines in sequence
        
        # 1. Line 647: notify_admin_dm exception
        mock_bot_client = AsyncMock()
        mock_bot_client.send_message = AsyncMock(side_effect=Exception("Send failed"))
        await notify_admin_dm(mock_bot_client, 123456, "Test")
        
        # 2. Line 656 + 659: create_session_flow paths
        with patch('builtins.input', side_effect=["+905551234567", "12345", "password"]):
            # First: config import failure (line 656)
            def failing_import(name, *args, **kwargs):
                if name == 'config':
                    raise ImportError("Config not found")
                return __builtins__['__import__'](name, *args, **kwargs)
            
            with patch('builtins.__import__', side_effect=failing_import):
                with patch('builtins.print'):
                    await create_session_flow()
            
            # Second: successful config but failed session (line 659)
            mock_config = MagicMock()
            mock_config.API_ID = 123456
            mock_config.API_HASH = "test_hash"
            
            with patch.dict('sys.modules', {'config': mock_config}):
                with patch('core.session_manager.open_session', return_value=(None, None)):
                    with patch('builtins.print') as mock_print:
                        await create_session_flow()
                        mock_print.assert_any_call("❌ Session oluşturulamadı")
        
        # 3. Lines 319->325, 322-323, 348->354, 357: Complex retry scenario
        session_mgr = SessionManager(SessionConfig(max_retry_attempts=2, base_retry_delay=0.01))
        session_metrics.database_lock_encounters = 0
        session_metrics.total_retry_attempts = 0
        
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock(side_effect=Exception("Disconnect failed"))  # 322-323, 348->354
        mock_client.is_user_authorized = AsyncMock(return_value=False)
        mock_client.send_code_request = AsyncMock()
        mock_client.sign_in = AsyncMock()
        mock_client.get_me = AsyncMock(side_effect=Exception("database is locked"))  # 319->325
        
        with patch('core.session_manager.TelegramClient', return_value=mock_client):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=2048):
                    with patch.object(session_mgr, 'validate_session_file', return_value=(True, "")):
                        
                        result = await session_mgr.open_session(
                            "+905551234567", 123456, "hash",
                            lambda: "12345", lambda: "password"
                        )
                        
                        # Line 357: Should return None, None
                        assert result == (None, None)
                        
                        # Lines 319->325: Database lock retry metrics
                        assert session_metrics.database_lock_encounters > 0
                        assert session_metrics.total_retry_attempts > 0

# ==================== RUNNER ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 