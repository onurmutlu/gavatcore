#!/usr/bin/env python3
"""
🧪 GAVATCore Test Configuration & Fixtures 🧪

Global test configuration and shared fixtures for comprehensive testing:
- Database mocking and cleanup
- Telegram client mocking
- Session management fixtures
- API testing helpers
- Performance monitoring fixtures
"""

import pytest
import asyncio
import os
import tempfile
import shutil
from pathlib import Path
from typing import Generator, AsyncGenerator, Dict, Any, Optional
from unittest.mock import AsyncMock, MagicMock, patch
import sqlite3
from datetime import datetime

# Test imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ConfigValidationError
from core.session_manager import SessionManager, SessionConfig, SessionInfo
from contact_utils import ContactManager, ContactManagerConfig


# ==================== PYTEST CONFIGURATION ====================

def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interaction"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer than 5 seconds"
    )
    config.addinivalue_line(
        "markers", "network: Tests that require network access"
    )
    config.addinivalue_line(
        "markers", "database: Tests that require database access"
    )

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ==================== TEMPORARY DIRECTORY FIXTURES ====================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def temp_sessions_dir(temp_dir: Path) -> Path:
    """Create temporary sessions directory."""
    sessions_dir = temp_dir / "test_sessions"
    sessions_dir.mkdir(exist_ok=True)
    return sessions_dir

@pytest.fixture
def temp_logs_dir(temp_dir: Path) -> Path:
    """Create temporary logs directory."""
    logs_dir = temp_dir / "test_logs"
    logs_dir.mkdir(exist_ok=True)
    return logs_dir


# ==================== CONFIG FIXTURES ====================

@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Mock configuration for testing."""
    return {
        "API_ID": 12345,
        "API_HASH": "test_api_hash_12345",
        "AUTHORIZED_USERS": [123456789, 987654321],
        "DEBUG_MODE": True,
        "DATABASE_URL": "sqlite:///test.db",
        "REDIS_URL": "redis://localhost:6379/1",
        "MONGODB_URL": "mongodb://localhost:27017/test_gavatcore",
        "ADMIN_BOT_TOKEN": "1234567890:TEST_BOT_TOKEN_FOR_TESTING"
    }

@pytest.fixture
def invalid_config() -> Dict[str, Any]:
    """Invalid configuration for testing error handling."""
    return {
        "API_ID": None,  # Invalid
        "API_HASH": "",  # Invalid
        "AUTHORIZED_USERS": [],  # Invalid
        "DEBUG_MODE": "invalid",  # Invalid type
    }


# ==================== SESSION MANAGEMENT FIXTURES ====================

@pytest.fixture
def session_config() -> SessionConfig:
    """Create test session configuration."""
    return SessionConfig(
        connection_retries=1,
        retry_delay=0.1,
        timeout=5,
        max_retry_attempts=2,
        base_retry_delay=0.1,
        min_session_file_size=512  # Smaller for tests
    )

@pytest.fixture
def session_manager(session_config: SessionConfig, temp_sessions_dir: Path) -> SessionManager:
    """Create test session manager with temporary directory."""
    with patch('core.session_manager.SESSIONS_DIR', str(temp_sessions_dir)):
        return SessionManager(session_config)

@pytest.fixture
def mock_session_file(temp_sessions_dir: Path) -> Path:
    """Create a mock session file for testing."""
    session_path = temp_sessions_dir / "test_session.session"
    
    # Create a minimal SQLite database that mimics Telethon session structure
    conn = sqlite3.connect(str(session_path))
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE sessions (
            dc_id INTEGER PRIMARY KEY,
            server_address TEXT,
            port INTEGER,
            auth_key BLOB
        )
    ''')
    cursor.execute('INSERT INTO sessions VALUES (2, "149.154.167.50", 443, ?)', (b'test_auth_key',))
    conn.commit()
    conn.close()
    
    return session_path


# ==================== TELEGRAM CLIENT MOCKING ====================

@pytest.fixture
def mock_telegram_client():
    """Create mock Telegram client for testing."""
    mock_client = AsyncMock()
    mock_client.connect = AsyncMock()
    mock_client.disconnect = AsyncMock()
    mock_client.is_user_authorized = AsyncMock(return_value=True)
    mock_client.is_connected = AsyncMock(return_value=True)
    mock_client.send_code_request = AsyncMock()
    mock_client.sign_in = AsyncMock()
    mock_client.send_message = AsyncMock()
    
    # Mock user object
    mock_user = MagicMock()
    mock_user.id = 123456789
    mock_user.username = "test_user"
    mock_user.first_name = "Test"
    mock_user.last_name = "User"
    
    mock_client.get_me = AsyncMock(return_value=mock_user)
    
    return mock_client

@pytest.fixture
def mock_telegram_client_factory(mock_telegram_client):
    """Factory for creating mock Telegram clients."""
    def _create_mock_client(*args, **kwargs):
        return mock_telegram_client
    return _create_mock_client


# ==================== CONTACT MANAGER FIXTURES ====================

@pytest.fixture
def contact_manager_config() -> ContactManagerConfig:
    """Create test contact manager configuration."""
    return ContactManagerConfig(
        max_retries=2,
        base_delay=0.1,
        max_delay=1.0,
        timeout=5.0,
        rate_limit_delay=0.1,
        max_concurrent=2
    )

@pytest.fixture
def contact_manager(contact_manager_config: ContactManagerConfig) -> ContactManager:
    """Create test contact manager."""
    return ContactManager(contact_manager_config)


# ==================== DATABASE FIXTURES ====================

@pytest.fixture
def temp_sqlite_db(temp_dir: Path) -> Path:
    """Create temporary SQLite database for testing."""
    db_path = temp_dir / "test.db"
    
    # Create basic tables if needed
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Example table creation (adjust based on your actual schema)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            phone TEXT PRIMARY KEY,
            session_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    return db_path


# ==================== HTTP/API FIXTURES ====================

@pytest.fixture
def mock_http_client():
    """Create mock HTTP client for API testing."""
    mock_client = MagicMock()
    mock_client.get = AsyncMock()
    mock_client.post = AsyncMock()
    mock_client.put = AsyncMock()
    mock_client.delete = AsyncMock()
    
    # Default successful responses
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_response.text = "OK"
    
    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response
    
    return mock_client


# ==================== PERFORMANCE MONITORING FIXTURES ====================

@pytest.fixture
def performance_monitor():
    """Performance monitoring fixture for tests."""
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.metrics = {}
        
        def start(self):
            self.start_time = datetime.now()
        
        def stop(self):
            self.end_time = datetime.now()
        
        @property
        def duration_ms(self) -> float:
            if self.start_time and self.end_time:
                return (self.end_time - self.start_time).total_seconds() * 1000
            return 0.0
        
        def record_metric(self, name: str, value: Any):
            self.metrics[name] = value
        
        def assert_performance(self, max_duration_ms: float):
            assert self.duration_ms <= max_duration_ms, f"Performance test failed: {self.duration_ms}ms > {max_duration_ms}ms"
    
    return PerformanceMonitor()


# ==================== ERROR SIMULATION FIXTURES ====================

@pytest.fixture
def error_simulator():
    """Error simulation utilities for testing resilience."""
    class ErrorSimulator:
        def __init__(self):
            self.active_errors = set()
        
        def enable_network_error(self):
            self.active_errors.add("network")
        
        def enable_database_error(self):
            self.active_errors.add("database")
        
        def enable_timeout_error(self):
            self.active_errors.add("timeout")
        
        def clear_errors(self):
            self.active_errors.clear()
        
        def should_raise_error(self, error_type: str) -> bool:
            return error_type in self.active_errors
    
    return ErrorSimulator()


# ==================== ASYNC TESTING UTILITIES ====================

@pytest.fixture
async def async_test_context():
    """Async context manager for testing async operations."""
    context = {
        "tasks": [],
        "clients": [],
        "cleanup_functions": []
    }
    
    yield context
    
    # Cleanup
    for task in context["tasks"]:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    for client in context["clients"]:
        if hasattr(client, 'disconnect'):
            try:
                await client.disconnect()
            except:
                pass
    
    for cleanup_func in context["cleanup_functions"]:
        try:
            if asyncio.iscoroutinefunction(cleanup_func):
                await cleanup_func()
            else:
                cleanup_func()
        except:
            pass


# ==================== TEST DATA FIXTURES ====================

@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Sample user data for testing."""
    return {
        "id": 123456789,
        "username": "test_user",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+905555555555",
        "is_premium": False,
        "language_code": "tr"
    }

@pytest.fixture
def sample_message_data() -> Dict[str, Any]:
    """Sample message data for testing."""
    return {
        "id": 12345,
        "text": "Test message",
        "from_user": {
            "id": 123456789,
            "username": "test_user",
            "first_name": "Test"
        },
        "chat": {
            "id": -1001234567890,
            "title": "Test Group",
            "type": "supergroup"
        },
        "date": datetime.now().isoformat()
    }


# ==================== ENVIRONMENT SETUP ====================

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch, temp_dir):
    """Setup test environment variables."""
    # Set test environment variables
    monkeypatch.setenv("DEBUG_MODE", "true")
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("TEST_DATA_DIR", str(temp_dir))
    
    # Mock sensitive operations in test environment
    monkeypatch.setenv("GAVATCORE_TEST_MODE", "true")

@pytest.fixture
def clean_state():
    """Ensure clean state between tests."""
    # Clear any global state
    import core.session_manager
    core.session_manager.session_metrics = core.session_manager.SessionMetrics()
    
    yield
    
    # Cleanup after test
    # Add any global state cleanup here


# ==================== HELPER UTILITIES ====================

@pytest.fixture
def test_utilities():
    """Helper utilities for tests."""
    class TestUtilities:
        @staticmethod
        def create_test_session_info(phone: str, valid: bool = True) -> SessionInfo:
            """Create test session info."""
            return SessionInfo(
                phone=phone,
                session_path=f"/tmp/test_{phone}.session",
                exists=valid,
                valid=valid,
                file_size=1024 if valid else 0,
                last_modified=datetime.now() if valid else None,
                error_message=None if valid else "Test error"
            )
        
        @staticmethod
        def assert_config_valid(config: Dict[str, Any]):
            """Assert configuration is valid."""
            required_keys = ["API_ID", "API_HASH", "AUTHORIZED_USERS"]
            for key in required_keys:
                assert key in config, f"Missing required config key: {key}"
                assert config[key] is not None, f"Config key {key} cannot be None"
        
        @staticmethod
        async def wait_for_condition(condition, timeout: float = 5.0, interval: float = 0.1):
            """Wait for a condition to become true."""
            import time
            start_time = time.time()
            while time.time() - start_time < timeout:
                if await condition() if asyncio.iscoroutinefunction(condition) else condition():
                    return True
                await asyncio.sleep(interval)
            return False
    
    return TestUtilities


# ==================== CLEANUP ====================

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Automatic cleanup after each test."""
    yield
    
    # Clear any remaining async tasks
    try:
        pending_tasks = [task for task in asyncio.all_tasks() if not task.done()]
        if pending_tasks:
            for task in pending_tasks:
                task.cancel()
    except RuntimeError:
        # Event loop might be closed
        pass 