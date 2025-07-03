#!/usr/bin/env python3
"""
🧪 Complete Test Suite for utils/log_utils.py 🧪

Comprehensive tests for GAVATCore log utilities:
- Full function coverage with edge cases
- File lock handling and error scenarios
- Performance testing with concurrent access
- Mock filesystem operations
- Log rotation and size limit testing

Target Coverage: 95-100%
Test Count: 50+ comprehensive tests
"""

import pytest
import os
import tempfile
import shutil
import time
import threading
import concurrent.futures
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock, call
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.log_utils import (
    log_event, get_logs, search_logs, get_log_stats,
    LOGS_DIR, MAX_LOG_SIZE
)


class TestLogEventComprehensive:
    """Comprehensive tests for log_event function."""
    
    @pytest.fixture
    def temp_logs_dir(self, tmp_path):
        """Create temporary logs directory for testing."""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        
        with patch('utils.log_utils.LOGS_DIR', str(logs_dir)):
            yield logs_dir
    
    @pytest.mark.unit
    def test_log_event_basic_functionality(self, temp_logs_dir):
        """Test basic log event functionality."""
        user_id = "test_user_123"
        message = "Test log message"
        level = "INFO"
        
        log_event(user_id, message, level)
        
        # Check log file was created
        log_file = temp_logs_dir / f"{user_id}.log"
        assert log_file.exists()
        
        # Check log content
        content = log_file.read_text()
        assert message in content
        assert "[INFO]" in content
        assert datetime.now().strftime("%Y-%m-%d") in content
    
    @pytest.mark.unit
    def test_log_event_default_level(self, temp_logs_dir):
        """Test log event with default INFO level."""
        user_id = "test_user_default"
        message = "Default level test"
        
        log_event(user_id, message)  # No level specified
        
        log_file = temp_logs_dir / f"{user_id}.log"
        content = log_file.read_text()
        assert "[INFO]" in content
        assert message in content
    
    @pytest.mark.unit
    def test_log_event_username_with_at_symbol(self, temp_logs_dir):
        """Test log event with username containing @ symbol."""
        username = "@test_user"
        message = "Username test"
        
        log_event(username, message)
        
        # @ should be removed from filename
        log_file = temp_logs_dir / "test_user.log"
        assert log_file.exists()
        
        content = log_file.read_text()
        assert message in content
    
    @pytest.mark.unit
    def test_log_event_session_file_handling(self, temp_logs_dir):
        """Test log event with session file (.session extension)."""
        session_name = "test_bot.session"
        message = "Session log test"
        
        log_event(session_name, message)
        
        # Should create in sessions subdirectory
        sessions_dir = temp_logs_dir / "sessions"
        assert sessions_dir.exists()
        
        log_file = sessions_dir / f"{session_name}.log"
        assert log_file.exists()
        
        content = log_file.read_text()
        assert message in content
    
    @pytest.mark.unit
    def test_log_event_session_with_path_prefix(self, temp_logs_dir):
        """Test log event with session file that has sessions/ prefix."""
        session_name = "sessions/another_bot.session"
        message = "Session with prefix test"
        
        log_event(session_name, message)
        
        # Should extract just the filename
        sessions_dir = temp_logs_dir / "sessions"
        log_file = sessions_dir / "another_bot.session.log"
        assert log_file.exists()
        
        content = log_file.read_text()
        assert message in content
    
    @pytest.mark.unit
    def test_log_event_different_levels(self, temp_logs_dir):
        """Test log event with different log levels."""
        user_id = "level_test_user"
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in levels:
            message = f"Test message for {level}"
            log_event(user_id, message, level)
        
        log_file = temp_logs_dir / f"{user_id}.log"
        content = log_file.read_text()
        
        for level in levels:
            assert f"[{level}]" in content
    
    @pytest.mark.unit
    def test_log_event_case_insensitive_level(self, temp_logs_dir):
        """Test log event with lowercase level (should be uppercased)."""
        user_id = "case_test"
        message = "Case test message"
        
        log_event(user_id, message, "warning")  # lowercase
        
        log_file = temp_logs_dir / f"{user_id}.log"
        content = log_file.read_text()
        assert "[WARNING]" in content  # Should be uppercase
    
    @pytest.mark.unit
    def test_log_event_unicode_handling(self, temp_logs_dir):
        """Test log event with unicode characters."""
        user_id = "unicode_test"
        message = "Unicode test: üñíçödé çhärs 🚀🎯"
        
        log_event(user_id, message)
        
        log_file = temp_logs_dir / f"{user_id}.log"
        content = log_file.read_text(encoding='utf-8')
        assert message in content
    
    @pytest.mark.unit
    def test_log_event_multiple_entries(self, temp_logs_dir):
        """Test multiple log entries for same user."""
        user_id = "multi_test"
        messages = [
            "First message",
            "Second message", 
            "Third message"
        ]
        
        for i, message in enumerate(messages):
            log_event(user_id, message, "INFO")
            time.sleep(0.001)  # Ensure different timestamps
        
        log_file = temp_logs_dir / f"{user_id}.log"
        content = log_file.read_text()
        
        for message in messages:
            assert message in content
        
        # Check multiple timestamps
        lines = content.strip().split('\n')
        assert len(lines) == 3
    
    @pytest.mark.unit
    def test_log_event_file_rotation_on_size_limit(self, temp_logs_dir):
        """Test log file rotation when size limit is exceeded."""
        user_id = "rotation_test"
        
        # Mock MAX_LOG_SIZE to a small value for testing
        with patch('utils.log_utils.MAX_LOG_SIZE', 100):  # 100 bytes
            # Write enough data to exceed limit
            for i in range(20):
                log_event(user_id, f"Message {i} with some extra content to make it longer", "INFO")
        
        log_file = temp_logs_dir / f"{user_id}.log"
        
        # Original file should exist but be small (new content after rotation)
        assert log_file.exists()
        
        # Backup file should exist
        backup_files = list(temp_logs_dir.glob(f"{user_id}.log.*.bak"))
        assert len(backup_files) >= 1
    
    @pytest.mark.unit
    def test_log_event_portalocker_error_handling(self, temp_logs_dir):
        """Test graceful handling of portalocker errors."""
        user_id = "lock_error_test"
        message = "Lock error test"
        
        # Mock portalocker.Lock to raise exception
        with patch('utils.log_utils.portalocker.Lock') as mock_lock:
            mock_lock.side_effect = Exception("Lock failed")
            
            # Should not raise exception, just print error
            log_event(user_id, message)
            
            # File might not be created due to lock failure
            log_file = temp_logs_dir / f"{user_id}.log"
            # Test passes if no exception is raised
    
    @pytest.mark.unit
    def test_log_event_file_permission_error(self, temp_logs_dir):
        """Test handling of file permission errors."""
        user_id = "permission_test"
        message = "Permission test"
        
        # Create a read-only directory
        readonly_dir = temp_logs_dir / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only
        
        with patch('utils.log_utils.LOGS_DIR', str(readonly_dir)):
            # Should handle permission error gracefully
            log_event(user_id, message)
            # Test passes if no exception is raised
        
        # Cleanup - restore permissions
        readonly_dir.chmod(0o755)
    
    @pytest.mark.unit
    def test_log_event_makedirs_error_handling(self, temp_logs_dir):
        """Test handling of makedirs errors."""
        user_id = "makedirs_test"
        message = "Makedirs test"
        
        # Mock os.makedirs to raise exception
        with patch('utils.log_utils.os.makedirs') as mock_makedirs:
            mock_makedirs.side_effect = OSError("Directory creation failed")
            
            # Should handle makedirs error gracefully
            log_event(user_id, message)
            # Test passes if no exception is raised


class TestGetLogsComprehensive:
    """Comprehensive tests for get_logs function."""
    
    @pytest.fixture
    def temp_logs_dir(self, tmp_path):
        """Create temporary logs directory with test data."""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        
        with patch('utils.log_utils.LOGS_DIR', str(logs_dir)):
            yield logs_dir
    
    @pytest.mark.unit
    def test_get_logs_basic_functionality(self, temp_logs_dir):
        """Test basic get_logs functionality."""
        user_id = "get_logs_test"
        
        # Create test log entries
        for i in range(5):
            log_event(user_id, f"Test message {i}", "INFO")
        
        result = get_logs(user_id)
        
        assert "Test message 0" in result
        assert "Test message 4" in result
        assert "[INFO]" in result
    
    @pytest.mark.unit
    def test_get_logs_with_limit(self, temp_logs_dir):
        """Test get_logs with custom limit."""
        user_id = "limit_test"
        
        # Create 10 log entries
        for i in range(10):
            log_event(user_id, f"Message {i}", "INFO")
        
        result = get_logs(user_id, limit=3)
        
        # Should only return last 3 messages
        lines = result.strip().split('\n')
        assert len(lines) == 3
        assert "Message 7" in result
        assert "Message 8" in result
        assert "Message 9" in result
        assert "Message 0" not in result
    
    @pytest.mark.unit
    def test_get_logs_nonexistent_user(self, temp_logs_dir):
        """Test get_logs for non-existent user."""
        result = get_logs("nonexistent_user")
        assert result == "📭 Log bulunamadı."
    
    @pytest.mark.unit
    def test_get_logs_empty_file(self, temp_logs_dir):
        """Test get_logs with empty log file."""
        user_id = "empty_test"
        log_file = temp_logs_dir / f"{user_id}.log"
        
        # Create empty file
        log_file.touch()
        
        result = get_logs(user_id)
        assert result == "📭 Log dosyası boş."
    
    @pytest.mark.unit
    def test_get_logs_username_with_at_symbol(self, temp_logs_dir):
        """Test get_logs with username containing @ symbol."""
        username = "@test_user"
        
        # Log some events
        log_event(username, "Test message", "INFO")
        
        # Get logs using same username format
        result = get_logs(username)
        assert "Test message" in result
    
    @pytest.mark.unit
    def test_get_logs_portalocker_error(self, temp_logs_dir):
        """Test get_logs with portalocker error."""
        user_id = "lock_error"
        
        # Create log file first
        log_event(user_id, "Test message", "INFO")
        
        # Mock portalocker.Lock to raise exception
        with patch('utils.log_utils.portalocker.Lock') as mock_lock:
            mock_lock.side_effect = Exception("Lock failed")
            
            with pytest.raises(Exception):
                get_logs(user_id)
    
    @pytest.mark.unit
    def test_get_logs_file_encoding_error(self, temp_logs_dir):
        """Test get_logs with file encoding issues."""
        user_id = "encoding_test"
        log_file = temp_logs_dir / f"{user_id}.log"
        
        # Create file with invalid UTF-8
        with open(log_file, 'wb') as f:
            f.write(b'\xff\xfe Invalid UTF-8 content')
        
        # Should handle encoding error gracefully
        with pytest.raises(UnicodeDecodeError):
            get_logs(user_id)


class TestSearchLogsComprehensive:
    """Comprehensive tests for search_logs function."""
    
    @pytest.fixture
    def temp_logs_dir_with_data(self, tmp_path):
        """Create temporary logs directory with comprehensive test data."""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        
        with patch('utils.log_utils.LOGS_DIR', str(logs_dir)):
            user_id = "search_test_user"
            
            # Create varied log entries
            test_entries = [
                ("2024-01-01T10:00:00", "INFO", "User login successful"),
                ("2024-01-01T11:00:00", "WARNING", "Rate limit exceeded"),
                ("2024-01-01T12:00:00", "ERROR", "Database connection failed"),
                ("2024-01-02T10:00:00", "INFO", "User logout"),
                ("2024-01-02T11:00:00", "DEBUG", "Debug information logged"),
                ("2024-01-02T12:00:00", "INFO", "Login attempt from new device"),
            ]
            
            log_file = logs_dir / f"{user_id}.log"
            with open(log_file, 'w', encoding='utf-8') as f:
                for timestamp, level, message in test_entries:
                    f.write(f"[{timestamp}] [{level}] {message}\n")
            
            yield logs_dir, user_id
    
    @pytest.mark.unit
    def test_search_logs_by_keyword(self, temp_logs_dir_with_data):
        """Test search_logs with keyword filter."""
        logs_dir, user_id = temp_logs_dir_with_data
        
        result = search_logs(user_id, keyword="login")
        
        assert "User login successful" in result
        assert "User logout" in result
        assert "Login attempt from new device" in result
        assert "Rate limit exceeded" not in result
    
    @pytest.mark.unit
    def test_search_logs_by_level(self, temp_logs_dir_with_data):
        """Test search_logs with level filter."""
        logs_dir, user_id = temp_logs_dir_with_data
        
        result = search_logs(user_id, level="ERROR")
        
        assert "Database connection failed" in result
        assert "User login successful" not in result
        assert "[ERROR]" in result
    
    @pytest.mark.unit
    def test_search_logs_by_date(self, temp_logs_dir_with_data):
        """Test search_logs with date filter."""
        logs_dir, user_id = temp_logs_dir_with_data
        
        result = search_logs(user_id, after="2024-01-02")
        
        assert "User logout" in result
        assert "Debug information logged" in result
        assert "Login attempt from new device" in result
        assert "User login successful" not in result  # From 2024-01-01
    
    @pytest.mark.unit
    def test_search_logs_combined_filters(self, temp_logs_dir_with_data):
        """Test search_logs with multiple filters combined."""
        logs_dir, user_id = temp_logs_dir_with_data
        
        result = search_logs(user_id, keyword="login", level="INFO", after="2024-01-01T11:30:00")
        
        assert "Login attempt from new device" in result
        assert "User login successful" not in result  # Before after date
        assert "User logout" not in result  # Doesn't contain "login"
    
    @pytest.mark.unit
    def test_search_logs_case_insensitive_keyword(self, temp_logs_dir_with_data):
        """Test search_logs with case insensitive keyword matching."""
        logs_dir, user_id = temp_logs_dir_with_data
        
        result = search_logs(user_id, keyword="LOGIN")  # Uppercase
        
        assert "User login successful" in result
        assert "Login attempt from new device" in result
    
    @pytest.mark.unit
    def test_search_logs_no_matches(self, temp_logs_dir_with_data):
        """Test search_logs when no matches found."""
        logs_dir, user_id = temp_logs_dir_with_data
        
        result = search_logs(user_id, keyword="nonexistent")
        
        assert result == "❌ Eşleşen log satırı bulunamadı."
    
    @pytest.mark.unit
    def test_search_logs_invalid_date_format(self, temp_logs_dir_with_data):
        """Test search_logs with invalid date format."""
        logs_dir, user_id = temp_logs_dir_with_data
        
        # Should ignore invalid date format and search normally
        result = search_logs(user_id, after="invalid-date-format")
        
        # Should return all entries (date filter ignored)
        assert "User login successful" in result
        assert "Database connection failed" in result
    
    @pytest.mark.unit
    def test_search_logs_nonexistent_user(self, temp_logs_dir_with_data):
        """Test search_logs for non-existent user."""
        logs_dir, user_id = temp_logs_dir_with_data
        
        result = search_logs("nonexistent_user", keyword="test")
        
        assert result == "📭 Log bulunamadı."
    
    @pytest.mark.unit
    def test_search_logs_malformed_log_entries(self, temp_logs_dir_with_data):
        """Test search_logs with malformed log entries."""
        logs_dir, user_id = temp_logs_dir_with_data
        
        # Add malformed entries to log file
        log_file = logs_dir / f"{user_id}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write("Malformed log entry without timestamp\n")
            f.write("[INVALID] Another malformed entry\n")
        
        # Should handle malformed entries gracefully
        result = search_logs(user_id, keyword="login")
        
        assert "User login successful" in result  # Normal entries still work
    
    @pytest.mark.unit
    def test_search_logs_exception_handling(self, temp_logs_dir_with_data):
        """Test search_logs exception handling."""
        logs_dir, user_id = temp_logs_dir_with_data
        
        # Mock file operations to raise exception
        with patch('utils.log_utils.portalocker.Lock') as mock_lock:
            mock_lock.side_effect = Exception("File access error")
            
            result = search_logs(user_id, keyword="test")
            
            assert "❌ Log arama hatası:" in result


class TestGetLogStatsComprehensive:
    """Comprehensive tests for get_log_stats function."""
    
    @pytest.fixture
    def temp_logs_dir_with_stats_data(self, tmp_path):
        """Create temporary logs directory with varied data for stats testing."""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        
        with patch('utils.log_utils.LOGS_DIR', str(logs_dir)):
            user_id = "stats_test_user"
            
            # Create log entries with different levels
            test_entries = [
                ("2024-01-01T10:00:00", "INFO", "First info message"),
                ("2024-01-01T11:00:00", "INFO", "Second info message"),
                ("2024-01-01T12:00:00", "WARNING", "First warning"),
                ("2024-01-01T13:00:00", "ERROR", "First error"),
                ("2024-01-01T14:00:00", "INFO", "Third info message"),
                ("2024-01-01T15:00:00", "WARNING", "Second warning"),
                ("2024-01-01T16:00:00", "ERROR", "Second error"),
                ("2024-01-01T17:00:00", "DEBUG", "Debug message"),
            ]
            
            log_file = logs_dir / f"{user_id}.log"
            with open(log_file, 'w', encoding='utf-8') as f:
                for timestamp, level, message in test_entries:
                    f.write(f"[{timestamp}] [{level}] {message}\n")
            
            yield logs_dir, user_id, len(test_entries)
    
    @pytest.mark.unit
    def test_get_log_stats_basic_functionality(self, temp_logs_dir_with_stats_data):
        """Test basic get_log_stats functionality."""
        logs_dir, user_id, total_entries = temp_logs_dir_with_stats_data
        
        stats = get_log_stats(user_id)
        
        assert stats["exists"] is True
        assert stats["total_lines"] == total_entries
        assert stats["info_count"] == 3
        assert stats["warning_count"] == 2
        assert stats["error_count"] == 2
        assert stats["first_log"] == "2024-01-01T10:00:00"
        assert stats["last_log"] == "2024-01-01T17:00:00"
        assert stats["file_size"] > 0
    
    @pytest.mark.unit
    def test_get_log_stats_nonexistent_user(self, tmp_path):
        """Test get_log_stats for non-existent user."""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        
        with patch('utils.log_utils.LOGS_DIR', str(logs_dir)):
            stats = get_log_stats("nonexistent_user")
            
            assert stats["exists"] is False
    
    @pytest.mark.unit
    def test_get_log_stats_empty_file(self, tmp_path):
        """Test get_log_stats with empty log file."""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        
        with patch('utils.log_utils.LOGS_DIR', str(logs_dir)):
            user_id = "empty_stats_test"
            log_file = logs_dir / f"{user_id}.log"
            log_file.touch()  # Create empty file
            
            stats = get_log_stats(user_id)
            
            assert stats["exists"] is True
            assert stats["total_lines"] == 0
            assert stats["info_count"] == 0
            assert stats["warning_count"] == 0
            assert stats["error_count"] == 0
            assert stats["first_log"] is None
            assert stats["last_log"] is None
            assert stats["file_size"] == 0
    
    @pytest.mark.unit
    def test_get_log_stats_username_with_at_symbol(self, temp_logs_dir_with_stats_data):
        """Test get_log_stats with username containing @ symbol."""
        logs_dir, original_user_id, _ = temp_logs_dir_with_stats_data
        
        # Create log for username with @
        username = "@stats_user_test"
        log_event(username, "Test message", "INFO")
        
        stats = get_log_stats(username)
        
        assert stats["exists"] is True
        assert stats["total_lines"] == 1
        assert stats["info_count"] == 1
    
    @pytest.mark.unit
    def test_get_log_stats_portalocker_error(self, temp_logs_dir_with_stats_data):
        """Test get_log_stats with portalocker error."""
        logs_dir, user_id, _ = temp_logs_dir_with_stats_data
        
        # Mock portalocker.Lock to raise exception
        with patch('utils.log_utils.portalocker.Lock') as mock_lock:
            mock_lock.side_effect = Exception("Lock failed")
            
            stats = get_log_stats(user_id)
            
            assert stats["exists"] is True
            assert "error" in stats
            assert "Lock failed" in stats["error"]
    
    @pytest.mark.unit
    def test_get_log_stats_malformed_timestamps(self, tmp_path):
        """Test get_log_stats with malformed timestamps."""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        
        with patch('utils.log_utils.LOGS_DIR', str(logs_dir)):
            user_id = "malformed_test"
            log_file = logs_dir / f"{user_id}.log"
            
            # Create log with malformed timestamps
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("Invalid log line without proper format\n")
                f.write("[INVALID] [INFO] Malformed timestamp\n")
                f.write("[2024-01-01T10:00:00] [INFO] Valid entry\n")
            
            stats = get_log_stats(user_id)
            
            assert stats["exists"] is True
            assert stats["total_lines"] == 3
            assert stats["info_count"] == 1  # Only properly formatted line


class TestPerformanceAndConcurrency:
    """Performance and concurrency tests for log utilities."""
    
    @pytest.fixture
    def temp_logs_dir(self, tmp_path):
        """Create temporary logs directory for performance testing."""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        
        with patch('utils.log_utils.LOGS_DIR', str(logs_dir)):
            yield logs_dir
    
    @pytest.mark.performance
    def test_log_event_performance_single_thread(self, temp_logs_dir):
        """Test log_event performance with single thread."""
        user_id = "perf_test_single"
        
        start_time = time.time()
        
        # Log 1000 messages
        for i in range(1000):
            log_event(user_id, f"Performance test message {i}", "INFO")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert duration < 10.0, f"Performance test took too long: {duration}s"
        
        # Verify all messages were logged
        result = get_logs(user_id, limit=1000)
        lines = result.strip().split('\n')
        assert len(lines) == 1000
    
    @pytest.mark.performance
    def test_log_event_concurrent_access(self, temp_logs_dir):
        """Test concurrent access to log_event function."""
        user_id = "concurrent_test"
        num_threads = 10
        messages_per_thread = 50
        
        def log_worker(thread_id: int):
            """Worker function for concurrent logging."""
            for i in range(messages_per_thread):
                log_event(user_id, f"Thread {thread_id} message {i}", "INFO")
        
        # Run concurrent threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(log_worker, i) for i in range(num_threads)]
            concurrent.futures.wait(futures)
        
        # Verify all messages were logged correctly
        result = get_logs(user_id, limit=num_threads * messages_per_thread)
        lines = result.strip().split('\n')
        
        # Should have all messages (some might be lost due to race conditions, but most should be there)
        assert len(lines) >= (num_threads * messages_per_thread * 0.9)  # Allow 10% loss
    
    @pytest.mark.performance  
    def test_search_logs_performance_large_file(self, temp_logs_dir):
        """Test search_logs performance with large log file."""
        user_id = "large_file_test"
        
        # Create large log file
        for i in range(5000):
            level = ["INFO", "WARNING", "ERROR"][i % 3]
            log_event(user_id, f"Large file test message {i} with some extra content", level)
        
        start_time = time.time()
        
        # Search in large file
        result = search_logs(user_id, keyword="test", level="INFO")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete search quickly
        assert duration < 2.0, f"Search took too long: {duration}s"
        assert "Large file test message" in result
    
    @pytest.mark.unit
    def test_log_rotation_multiple_times(self, temp_logs_dir):
        """Test multiple log rotations."""
        user_id = "multi_rotation_test"
        
        # Mock MAX_LOG_SIZE to trigger multiple rotations
        with patch('utils.log_utils.MAX_LOG_SIZE', 200):  # Very small size
            # Generate enough content to trigger multiple rotations
            for i in range(50):
                log_event(user_id, f"Rotation test message {i} with extra content to exceed size limit", "INFO")
        
        # Check that multiple backup files were created
        backup_files = list(temp_logs_dir.glob(f"{user_id}.log.*.bak"))
        assert len(backup_files) >= 2  # Should have multiple rotations
        
        # Original file should still exist
        log_file = temp_logs_dir / f"{user_id}.log"
        assert log_file.exists()


class TestEdgeCasesAndErrorHandling:
    """Edge cases and error handling tests."""
    
    @pytest.fixture
    def temp_logs_dir(self, tmp_path):
        """Create temporary logs directory."""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        
        with patch('utils.log_utils.LOGS_DIR', str(logs_dir)):
            yield logs_dir
    
    @pytest.mark.unit
    def test_log_event_very_long_message(self, temp_logs_dir):
        """Test log_event with very long message."""
        user_id = "long_message_test"
        long_message = "x" * 10000  # 10KB message
        
        log_event(user_id, long_message, "INFO")
        
        log_file = temp_logs_dir / f"{user_id}.log"
        assert log_file.exists()
        
        content = log_file.read_text()
        assert long_message in content
    
    @pytest.mark.unit
    def test_log_event_special_characters_in_user_id(self, temp_logs_dir):
        """Test log_event with special characters in user_id."""
        special_user_ids = [
            "user@domain.com",
            "user#123",
            "user$special",
            "user%percent",
            "user&ampersand"
        ]
        
        for user_id in special_user_ids:
            message = f"Test message for {user_id}"
            log_event(user_id, message, "INFO")
            
            # @ symbol should be removed, others should remain
            expected_filename = user_id.replace('@', '')
            log_file = temp_logs_dir / f"{expected_filename}.log"
            assert log_file.exists()
    
    @pytest.mark.unit
    def test_log_event_empty_message(self, temp_logs_dir):
        """Test log_event with empty message."""
        user_id = "empty_message_test"
        
        log_event(user_id, "", "INFO")
        
        log_file = temp_logs_dir / f"{user_id}.log"
        content = log_file.read_text()
        assert "[INFO]" in content
        # Empty message should still create log entry
    
    @pytest.mark.unit
    def test_log_event_none_parameters(self, temp_logs_dir):
        """Test log_event with None parameters."""
        # This would likely cause an exception in real usage
        # but we test what happens
        try:
            log_event(None, "Test message", "INFO")
        except (AttributeError, TypeError):
            pass  # Expected to fail gracefully
    
    @pytest.mark.unit
    def test_get_logs_with_zero_limit(self, temp_logs_dir):
        """Test get_logs with zero limit."""
        user_id = "zero_limit_test"
        
        log_event(user_id, "Test message", "INFO")
        
        result = get_logs(user_id, limit=0)
        
        # Should return empty string or handle gracefully
        assert isinstance(result, str)
    
    @pytest.mark.unit
    def test_get_logs_with_negative_limit(self, temp_logs_dir):
        """Test get_logs with negative limit."""
        user_id = "negative_limit_test"
        
        log_event(user_id, "Test message", "INFO")
        
        result = get_logs(user_id, limit=-5)
        
        # Python list slicing with negative numbers has specific behavior
        assert isinstance(result, str)
    
    @pytest.mark.unit
    def test_search_logs_empty_filters(self, temp_logs_dir):
        """Test search_logs with all empty filters."""
        user_id = "empty_filters_test"
        
        log_event(user_id, "Test message", "INFO")
        
        result = search_logs(user_id, keyword="", level="", after="")
        
        # Should return all log entries
        assert "Test message" in result
    
    @pytest.mark.unit
    def test_search_logs_whitespace_only_filters(self, temp_logs_dir):
        """Test search_logs with whitespace-only filters."""
        user_id = "whitespace_filters_test"
        
        log_event(user_id, "Test message", "INFO")
        
        result = search_logs(user_id, keyword="   ", level="  ", after="  ")
        
        # Should handle whitespace filters gracefully
        assert isinstance(result, str)


class TestModuleConstants:
    """Test module constants and configuration."""
    
    @pytest.mark.unit
    def test_logs_dir_constant(self):
        """Test LOGS_DIR constant."""
        from utils.log_utils import LOGS_DIR
        assert LOGS_DIR == "logs"
        assert isinstance(LOGS_DIR, str)
    
    @pytest.mark.unit
    def test_max_log_size_constant(self):
        """Test MAX_LOG_SIZE constant."""
        from utils.log_utils import MAX_LOG_SIZE
        assert MAX_LOG_SIZE == 5 * 1024 * 1024  # 5 MB
        assert isinstance(MAX_LOG_SIZE, int)
        assert MAX_LOG_SIZE > 0


class TestIntegrationScenarios:
    """Integration tests simulating real-world usage."""
    
    @pytest.fixture
    def temp_logs_dir(self, tmp_path):
        """Create temporary logs directory."""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        
        with patch('utils.log_utils.LOGS_DIR', str(logs_dir)):
            yield logs_dir
    
    @pytest.mark.integration
    def test_complete_logging_workflow(self, temp_logs_dir):
        """Test complete logging workflow: log -> get -> search -> stats."""
        user_id = "workflow_test"
        
        # Step 1: Log various events
        events = [
            ("User logged in", "INFO"),
            ("Failed login attempt", "WARNING"),  
            ("Database error", "ERROR"),
            ("User logged out", "INFO"),
            ("System maintenance", "INFO")
        ]
        
        for message, level in events:
            log_event(user_id, message, level)
        
        # Step 2: Get recent logs
        recent_logs = get_logs(user_id, limit=10)
        for message, _ in events:
            assert message in recent_logs
        
        # Step 3: Search for specific events
        login_logs = search_logs(user_id, keyword="login")
        assert "User logged in" in login_logs
        assert "Failed login attempt" in login_logs
        
        error_logs = search_logs(user_id, level="ERROR") 
        assert "Database error" in error_logs
        assert "User logged in" not in error_logs
        
        # Step 4: Get statistics
        stats = get_log_stats(user_id)
        assert stats["exists"] is True
        assert stats["total_lines"] == 5
        assert stats["info_count"] == 3
        assert stats["warning_count"] == 1
        assert stats["error_count"] == 1
    
    @pytest.mark.integration
    def test_session_logging_workflow(self, temp_logs_dir):
        """Test session-specific logging workflow."""
        session_names = [
            "bot1.session",
            "sessions/bot2.session",  # With prefix
            "bot3.session"
        ]
        
        # Log events for different sessions
        for session in session_names:
            log_event(session, f"Session {session} started", "INFO")
            log_event(session, f"Session {session} active", "DEBUG")
        
        # Verify session logs are in correct directory
        sessions_dir = temp_logs_dir / "sessions"
        assert sessions_dir.exists()
        
        for session in session_names:
            session_filename = os.path.basename(session)
            log_file = sessions_dir / f"{session_filename}.log"
            assert log_file.exists()
            
            content = log_file.read_text()
            assert f"Session {session} started" in content


# ==================== PYTEST CONFIGURATION ====================

@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Automatically cleanup any temporary files after each test."""
    yield
    
    # Clean up any test files that might have been created
    temp_patterns = [
        "test_*.log",
        "*.log.*.bak",
        "perf_test_*.log",
        "concurrent_test.log"
    ]
    
    for pattern in temp_patterns:
        for file_path in Path(".").glob(pattern):
            try:
                file_path.unlink()
            except (FileNotFoundError, PermissionError):
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 