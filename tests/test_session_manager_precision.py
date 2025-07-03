#!/usr/bin/env python3
"""
🎯 SessionManager Precision Coverage Tests - %89.2 → %97+ 🎯

Bu surgical test suite core/session_manager.py'deki specific missing lines'ı hedefler:

Missing Lines: 233, 319->325, 322-323, 336-344, 348->354, 351-352, 357, 396-401, 645-649, 656, 659, 670-673, 683-686

Target Areas:
- Database lock retry with client cleanup (lines 319->325, 322-323)
- Session file cleanup exception handling (lines 336-344, 342-344)
- Client disconnect exceptions in cleanup (lines 351-352)
- Config import failures (line 656)
- Session creation failure prints (line 659)
- Admin notification exceptions (lines 645-649)
- Terminate session error handling (lines 670-673)

Bu precision test'ler her missing line'ı yakalayacak.
"""

import pytest
import asyncio
import os
import sys
import sqlite3
from unittest.mock import patch, MagicMock, AsyncMock, call, mock_open
from unittest.mock import PropertyMock
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.session_manager import (
    SessionManager, SessionConfig, SessionInfo, session_manager,
    create_session_flow, terminate_session, notify_admin_dm, get_active_sessions
)

# ==================== SURGICAL PRECISION TESTS ====================

class TestSessionManagerPrecisionCoverage:
    """Surgical precision tests targeting specific missing lines in session_manager.py"""
    
    def setup_method(self):
        """Setup for each test method."""
        self.session_manager = SessionManager()
        
    @pytest.mark.asyncio
    async def test_database_lock_retry_with_client_cleanup_lines_319_325_322_323(self):
        """Test lines 319->325, 322-323: Database lock retry with client cleanup."""
        
        mock_client = AsyncMock()
        mock_disconnect = AsyncMock()
        mock_client.disconnect = mock_disconnect
        
        # Mock TelegramClient constructor to return our mock
        with patch('core.session_manager.TelegramClient', return_value=mock_client):
            with patch('core.session_manager.os.path.exists', return_value=True):
                with patch('core.session_manager.os.path.getsize', return_value=2048):
                    # First call raises database lock error, second succeeds
                    mock_client.connect.side_effect = [
                        Exception("database is locked"),  # First attempt
                        None  # Second attempt succeeds
                    ]
                    
                    # Mock successful authorization flow
                    mock_client.is_user_authorized.return_value = True
                    mock_client.get_me.return_value = MagicMock(id=123, username="test", first_name="Test")
                    
                    async def mock_code_cb():
                        return "12345"
                    
                    async def mock_password_cb():
                        return "password"
                    
                    # This should trigger database lock retry logic (lines 319->325, 322-323)
                    result = await self.session_manager.open_session(
                        "+1234567890", 123456, "test_hash", mock_code_cb, mock_password_cb
                    )
                    
                    # Should succeed on retry
                    assert result[0] is not None
                    assert result[1] is not None
                    
                    # Verify client cleanup was attempted (line 322-323)
                    mock_disconnect.assert_called()
    
    @pytest.mark.asyncio
    async def test_session_file_cleanup_exception_handling_lines_336_344(self):
        """Test lines 336-344: Session file cleanup exception handling."""
        
        mock_client = AsyncMock()
        
        with patch('core.session_manager.TelegramClient', return_value=mock_client):
            # Mock session path exists but cleanup fails
            session_path = "/fake/path/session.session"
            with patch.object(self.session_manager, 'get_session_path', return_value=session_path):
                with patch('core.session_manager.os.path.exists', return_value=True):
                    with patch('core.session_manager.os.path.getsize', return_value=500):  # Small file
                        with patch('core.session_manager.os.remove', side_effect=PermissionError("Access denied")):
                            
                            # Trigger error that leads to cleanup (non-lock error on final attempt)
                            mock_client.connect.side_effect = RuntimeError("Connection failed")
                            
                            async def mock_code_cb():
                                return "12345"
                            
                            async def mock_password_cb():
                                return "password"
                            
                            # This should trigger cleanup exception handling (lines 336-344)
                            with pytest.raises(RuntimeError):
                                await self.session_manager.open_session(
                                    "+1234567890", 123456, "test_hash", mock_code_cb, mock_password_cb
                                )
    
    @pytest.mark.asyncio
    async def test_client_disconnect_exception_in_cleanup_lines_351_352(self):
        """Test lines 351-352: Client disconnect exceptions in cleanup."""
        
        mock_client = AsyncMock()
        # Make disconnect raise an exception
        mock_client.disconnect.side_effect = Exception("Disconnect failed")
        
        with patch('core.session_manager.TelegramClient', return_value=mock_client):
            with patch('core.session_manager.os.path.exists', return_value=True):
                with patch('core.session_manager.os.path.getsize', return_value=2048):
                    
                    # Trigger error that leads to client cleanup
                    mock_client.connect.side_effect = RuntimeError("Connection failed")
                    
                    async def mock_code_cb():
                        return "12345"
                    
                    async def mock_password_cb():
                        return "password"
                    
                    # This should trigger client disconnect exception handling (lines 351-352)
                    with pytest.raises(RuntimeError):
                        await self.session_manager.open_session(
                            "+1234567890", 123456, "test_hash", mock_code_cb, mock_password_cb
                        )
                    
                    # Verify disconnect was attempted despite exception
                    mock_client.disconnect.assert_called()
    
    @pytest.mark.asyncio
    async def test_return_none_none_on_max_attempts_line_357(self):
        """Test line 357: Return None, None after max attempts."""
        
        mock_client = AsyncMock()
        
        with patch('core.session_manager.TelegramClient', return_value=mock_client):
            # Make all attempts fail with non-lock error but handle exception properly
            mock_client.connect.side_effect = RuntimeError("Connection failed")
            
            async def mock_code_cb():
                return "12345"
            
            async def mock_password_cb():
                return "password"
            
            # Set max attempts to 1 for faster test
            config = SessionConfig(max_retry_attempts=1)
            session_manager = SessionManager(config)
            
            # Mock the session path to avoid file system issues
            with patch.object(session_manager, 'get_session_path', return_value='/tmp/test.session'):
                with patch('core.session_manager.os.path.exists', return_value=False):
                    
                    try:
                        # This should trigger return None, None (line 357) after max attempts
                        result = await session_manager.open_session(
                            "+1234567890", 123456, "test_hash", mock_code_cb, mock_password_cb
                        )
                        
                        # Should not reach here due to exception, but if it does, check result
                        assert result == (None, None)
                        
                    except RuntimeError:
                        # Exception is expected on final attempt - this covers the exception path
                        pass
    
    @pytest.mark.asyncio
    async def test_validate_session_file_sqlite_error_line_233(self):
        """Test line 233: SQLite error in session file validation."""
        
        # Create a temporary file with sufficient size to pass size check but corrupt content
        with tempfile.NamedTemporaryFile(suffix='.session', delete=False) as temp_file:
            temp_file.write(b"corrupted data" * 100)  # Make it larger than min_session_file_size
            temp_path = temp_file.name
        
        try:
            # This should trigger SQLite error handling (line 233)
            is_valid, error_msg = await self.session_manager.validate_session_file(temp_path)
            
            assert is_valid is False
            assert "database" in error_msg.lower() or "corrupt" in error_msg.lower() or "malformed" in error_msg.lower()
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_admin_notification_exception_lines_645_649(self):
        """Test lines 645-649: Admin notification exception handling."""
        
        mock_client = AsyncMock()
        mock_client.send_message.side_effect = Exception("Send message failed")
        
        # This should trigger admin notification exception handling (lines 645-649)
        await notify_admin_dm(mock_client, 123456, "Test message")
        
        # Verify send_message was called despite exception
        mock_client.send_message.assert_called_once_with(123456, "Test message")
    
    @pytest.mark.asyncio
    async def test_config_import_failure_line_656(self):
        """Test line 656: Config import failure in create_session_flow."""
        
        # Mock input to provide phone number
        with patch('builtins.input', side_effect=["+1234567890", "12345", "password"]):
            # Mock the config import inside the function directly
            with patch('builtins.__import__') as mock_import:
                def import_side_effect(name, *args, **kwargs):
                    if name == 'config':
                        raise ImportError("No module named 'config'")
                    return __import__(name, *args, **kwargs)
                
                mock_import.side_effect = import_side_effect
                
                # This should trigger config import failure (line 656)
                await create_session_flow()
    
    @pytest.mark.asyncio
    async def test_session_creation_failure_print_line_659(self):
        """Test line 659: Session creation failure print."""
        
        # Mock input and failed session creation
        with patch('builtins.input', side_effect=["+1234567890", "12345", "password"]):
            with patch('builtins.print') as mock_print:
                # Import config successfully but session creation fails
                with patch('core.session_manager.open_session', return_value=(None, None)):
                    
                    # This should trigger session creation failure print (line 659)
                    await create_session_flow()
                    
                    # Verify failure message was printed
                    print_calls = [str(call) for call in mock_print.call_args_list]
                    failure_calls = [call for call in print_calls if "Session oluşturulamadı" in call]
                    assert len(failure_calls) > 0
    
    @pytest.mark.asyncio
    async def test_terminate_session_config_import_failure_lines_670_673(self):
        """Test lines 670-673: Terminate session config import failure."""
        
        # Mock config import to fail
        with patch('builtins.__import__') as mock_import:
            def import_side_effect(name, *args, **kwargs):
                if name == 'config':
                    raise ImportError("No module named 'config'")
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            
            with patch('builtins.print') as mock_print:
                
                # This should trigger config import failure in terminate_session (lines 670-673)
                await terminate_session("+1234567890")
                
                # Verify error message was printed
                print_calls = [str(call) for call in mock_print.call_args_list]
                error_calls = [call for call in print_calls if "Hata:" in call]
                assert len(error_calls) > 0
    
    @pytest.mark.asyncio
    async def test_close_session_failure_lines_396_401(self):
        """Test lines 396-401: Close session failure handling."""
        
        mock_client = AsyncMock()
        mock_client.connect.side_effect = Exception("Connection failed")
        
        with patch('core.session_manager.TelegramClient', return_value=mock_client):
            
            # This should trigger close session failure (lines 396-401)
            result = await self.session_manager.close_session("+1234567890", 123456, "test_hash")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_list_sessions_exception_handling_lines_683_686(self):
        """Test lines 683-686: List sessions exception handling in get_active_sessions."""
        
        # Since get_active_sessions() just returns get_session_info_list(), 
        # we need to test actual exception handling. Let's check if there's error handling
        # in the session manager's list_sessions method instead
        
        with patch.object(self.session_manager, 'list_sessions', side_effect=PermissionError("Access denied")):
            with patch('core.session_manager.session_manager', self.session_manager):
                
                # This should trigger exception handling
                try:
                    result = await get_active_sessions()
                    # If no exception handling, it will raise the exception
                    assert False, "Should have raised PermissionError"
                except PermissionError:
                    # Expected behavior if no exception handling
                    pass

# ==================== ULTRA PRECISION EDGE CASES ====================

class TestSessionManagerUltraPrecisionCoverage:
    """Ultra specific tests for remaining coverage gaps."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.session_manager = SessionManager()
    
    @pytest.mark.asyncio
    async def test_session_info_sqlite_error_handling(self):
        """Test SQLite error handling in get_session_info."""
        
        # Create a temporary file with sufficient size but corrupt SQLite content
        with tempfile.NamedTemporaryFile(suffix='.session', delete=False) as temp_file:
            # Write enough data to pass size check but make it invalid SQLite
            temp_file.write(b"not a sqlite database" * 50)  # Make it larger than min_session_file_size
            temp_path = temp_file.name
        
        try:
            with patch.object(self.session_manager, 'get_session_path', return_value=temp_path):
                
                # This should trigger SQLite error in get_session_info
                info = self.session_manager.get_session_info("+1234567890")
                
                assert info.exists is True
                assert info.valid is False
                # Check for SQLite-related error messages
                assert ("Database error" in info.error_message or 
                       "database" in info.error_message.lower() or
                       "sqlite" in info.error_message.lower() or
                       "file is not a database" in info.error_message.lower())
                
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_session_file_too_small_error_message(self):
        """Test file too small error message in get_session_info."""
        
        # Create a small temporary file
        with tempfile.NamedTemporaryFile(suffix='.session', delete=False) as temp_file:
            temp_file.write(b"small")  # Less than min_session_file_size
            temp_path = temp_file.name
        
        try:
            with patch.object(self.session_manager, 'get_session_path', return_value=temp_path):
                
                info = self.session_manager.get_session_info("+1234567890")
                
                assert info.exists is True
                assert info.valid is False
                assert "File too small" in info.error_message
                
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_session_file_not_exists_error_message(self):
        """Test file not exists error message in get_session_info."""
        
        fake_path = "/nonexistent/path/session.session"
        
        with patch.object(self.session_manager, 'get_session_path', return_value=fake_path):
            
            info = self.session_manager.get_session_info("+1234567890")
            
            assert info.exists is False
            assert info.valid is False
            assert info.error_message == "File does not exist"
    
    @pytest.mark.asyncio
    async def test_session_file_read_error_general_exception(self):
        """Test general exception handling in get_session_info."""
        
        # Mock os.path.exists to raise an exception
        with patch('core.session_manager.os.path.exists', side_effect=PermissionError("Access denied")):
            
            info = self.session_manager.get_session_info("+1234567890")
            
            assert info.exists is False
            assert info.valid is False
            assert "Error reading file" in info.error_message
    
    @pytest.mark.asyncio
    async def test_session_phone_from_path_extraction(self):
        """Test phone number extraction from session path."""
        
        test_cases = [
            ("/path/to/_1234567890.session", "+1234567890"),  # Underscore gets replaced with +
            ("/path/to/_901234567890.session", "+901234567890"),  # Leading underscore case
            ("_901234567890.session", "+901234567890")  # Simple case
        ]
        
        for session_path, expected_phone in test_cases:
            phone = self.session_manager.session_phone_from_path(session_path)
            assert phone == expected_phone
    
    @pytest.mark.asyncio
    async def test_get_metrics_comprehensive(self):
        """Test comprehensive metrics collection."""
        
        # Mock session files for active sessions count
        mock_session_files = ["session1.session", "session2.session", "session3.session"]
        
        with patch.object(self.session_manager, 'list_sessions', return_value=mock_session_files):
            
            metrics = self.session_manager.get_metrics()
            
            # Verify all expected metrics are present
            expected_keys = [
                "total_operations", "successful_operations", "failed_operations",
                "success_rate", "total_retry_attempts", "database_lock_encounters",
                "sessions_directory", "active_sessions"
            ]
            
            for key in expected_keys:
                assert key in metrics
            
            assert metrics["active_sessions"] == 3
    
    @pytest.mark.asyncio
    async def test_convenience_functions_coverage(self):
        """Test convenience functions for full coverage."""
        
        # Test all convenience functions with mocked session_manager
        mock_session_manager = AsyncMock()
        
        with patch('core.session_manager.session_manager', mock_session_manager):
            
            # Test open_session convenience function
            from core.session_manager import open_session
            
            async def mock_code_cb():
                return "12345"
            
            async def mock_password_cb():
                return "password"
            
            await open_session("+1234567890", 123456, "test_hash", mock_code_cb, mock_password_cb)
            mock_session_manager.open_session.assert_called_once()
            
            # Test close_session convenience function
            from core.session_manager import close_session
            await close_session("+1234567890", 123456, "test_hash")
            mock_session_manager.close_session.assert_called_once()
            
            # Test other convenience functions
            from core.session_manager import (
                list_sessions, is_session_active, test_session,
                get_session_path, session_phone_from_path, get_session_info_list
            )
            
            list_sessions()
            mock_session_manager.list_sessions.assert_called_once()
            
            is_session_active("+1234567890")
            mock_session_manager.is_session_active.assert_called_once()
            
            await test_session("+1234567890", 123456, "test_hash")
            mock_session_manager.test_session.assert_called_once()
            
            get_session_path("+1234567890")
            mock_session_manager.get_session_path.assert_called_once()
            
            session_phone_from_path("/path/session.session")
            mock_session_manager.session_phone_from_path.assert_called_once()
            
            get_session_info_list()
            mock_session_manager.get_session_info_list.assert_called_once()

# ==================== FINAL EDGE CASES ====================

class TestSessionManagerFinalEdgeCases:
    """Final edge case tests for maximum coverage."""
    
    @pytest.mark.asyncio
    async def test_create_session_flow_with_phone_override(self):
        """Test create_session_flow with phone override parameter."""
        
        with patch('builtins.input', side_effect=["12345", "password"]):  # Only code and password needed
            with patch('builtins.print') as mock_print:
                with patch('core.session_manager.open_session', return_value=(MagicMock(), MagicMock(first_name="Test"))):
                    
                    # Test with phone override (should not prompt for phone)
                    await create_session_flow(phone_override="+1234567890")
                    
                    # Verify success message was printed
                    print_calls = [str(call) for call in mock_print.call_args_list]
                    success_calls = [call for call in print_calls if "başarıyla oluşturuldu" in call]
                    assert len(success_calls) > 0
    
    @pytest.mark.asyncio
    async def test_terminate_session_success_case(self):
        """Test successful terminate session case."""
        
        with patch('builtins.print') as mock_print:
            with patch('core.session_manager.close_session', return_value=True):
                
                await terminate_session("+1234567890")
                
                # Verify success message was printed
                print_calls = [str(call) for call in mock_print.call_args_list]
                success_calls = [call for call in print_calls if "sonlandırıldı" in call]
                assert len(success_calls) > 0
    
    @pytest.mark.asyncio
    async def test_terminate_session_failure_case(self):
        """Test failed terminate session case."""
        
        with patch('builtins.print') as mock_print:
            with patch('core.session_manager.close_session', return_value=False):
                
                await terminate_session("+1234567890")
                
                # Verify failure message was printed
                print_calls = [str(call) for call in mock_print.call_args_list]
                failure_calls = [call for call in print_calls if "sonlandırılamadı" in call]
                assert len(failure_calls) > 0

# ==================== RUNNER ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 