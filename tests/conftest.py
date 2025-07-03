#!/usr/bin/env python3
"""
🧪 GAVATCore Pytest Configuration & Shared Fixtures 🧪

Shared pytest configuration, fixtures, and utilities for the GAVATCore test suite.
This module provides comprehensive testing infrastructure for production-grade testing.

Author: GAVATCore Team
Version: 1.0.0
"""

import os
import sys
import asyncio
import tempfile
import pytest
import json
from pathlib import Path
from typing import Dict, Any, Generator, AsyncGenerator, Optional, List
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

# Add project root to Python path
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

# Import test dependencies
try:
    import fakeredis
    import mongomock
    from faker import Faker
    import factory
    import httpx
    from rich.console import Console
    ADVANCED_FIXTURES_AVAILABLE = True
except ImportError:
    ADVANCED_FIXTURES_AVAILABLE = False

# Environment configuration
os.environ["TESTING"] = "true"
os.environ["GAVATCORE_TEST_MODE"] = "true"
os.environ["DEBUG_MODE"] = "false"

# Load test environment variables
def load_test_env():
    """Load test environment variables from .env.test if it exists."""
    test_env_file = project_root / ".env.test"
    if test_env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(test_env_file)
        except ImportError:
            # Fallback manual loading
            with open(test_env_file) as f:
                for line in f:
                    if line.strip() and not line.startswith('#') and '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value

# Load test environment on import
load_test_env()


# ==================== PYTEST CONFIGURATION ====================

def pytest_configure(config):
    """Configure pytest with additional settings."""
    # Add custom markers
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests that may take time")
    config.addinivalue_line("markers", "asyncio: Asynchronous tests")
    config.addinivalue_line("markers", "database: Database-related tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "security: Security-focused tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    
    # Set test directories
    test_dirs = [
        "tests",
        "tests/unit",
        "tests/integration", 
        "tests/performance",
        "tests/security",
        "tests/fixtures",
        "tests/data",
        "reports",
        "htmlcov"
    ]
    
    for test_dir in test_dirs:
        Path(test_dir).mkdir(parents=True, exist_ok=True)


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add automatic markers."""
    for item in items:
        # Auto-mark tests based on file location
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        
        # Auto-mark async tests
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)


# ==================== BASIC FIXTURES ====================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_path:
        yield Path(temp_path)


@pytest.fixture
def mock_env() -> Generator[Dict[str, str], None, None]:
    """Provide a clean environment for testing."""
    original_env = os.environ.copy()
    test_env = {
        "TESTING": "true",
        "GAVATCORE_TEST_MODE": "true",
        "DEBUG_MODE": "false",
        "TELEGRAM_API_ID": "12345",
        "TELEGRAM_API_HASH": "test_hash_123456789",
        "AUTHORIZED_USERS": "123456789,987654321",
        "ADMIN_BOT_TOKEN": "1234567890:TEST_BOT_TOKEN",
        "DATABASE_URL": "sqlite:///test_gavatcore.db",
        "REDIS_URL": "redis://localhost:6379/1",
        "MONGODB_URL": "mongodb://localhost:27017/test_gavatcore"
    }
    
    os.environ.update(test_env)
    yield test_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def console():
    """Provide a Rich console for test output."""
    return Console(file=sys.stdout, force_terminal=True)


# ==================== CONFIGURATION FIXTURES ====================

@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Provide a sample configuration for testing."""
    return {
        "API_ID": 1234567,
        "API_HASH": "test_hash_32_characters_long_test",
        "AUTHORIZED_USERS": [123456789, 987654321, 555666777],
        "DEBUG_MODE": False,
        "OPENAI_API_KEY": "sk-test-integration-key",
        "BOT_TOKEN": "1234567890:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw",
        "ENVIRONMENT": "testing",
        "MONGODB_URI": "mongodb://localhost:27017/test_gavatcore",
        "REDIS_URL": "redis://localhost:6379/1",
        "DATABASE_URL": "sqlite:///test_gavatcore.db"
    }


@pytest.fixture
def invalid_config() -> Dict[str, Any]:
    """Provide an invalid configuration for testing error cases."""
    return {
        "API_ID": -123,  # Invalid: negative
        "API_HASH": "",  # Invalid: empty
        "AUTHORIZED_USERS": [],  # Invalid: empty list
        "DEBUG_MODE": "invalid_bool"  # Invalid: not boolean
    }


@pytest.fixture
def make_config():
    """Factory fixture for creating custom configurations."""
    def _make_config(**overrides) -> Dict[str, Any]:
        base_config = {
            "API_ID": 1234567,
            "API_HASH": "test_hash_value",
            "AUTHORIZED_USERS": [123456789],
            "DEBUG_MODE": False
        }
        base_config.update(overrides)
        return base_config
    
    return _make_config


# ==================== DATABASE FIXTURES ====================

@pytest.fixture
def mock_redis():
    """Provide a mock Redis client for testing."""
    if ADVANCED_FIXTURES_AVAILABLE:
        return fakeredis.FakeRedis(decode_responses=True)
    else:
        # Simple mock fallback
        mock = Mock()
        mock.ping.return_value = True
        mock.get.return_value = None
        mock.set.return_value = True
        mock.delete.return_value = 1
        mock.exists.return_value = False
        return mock


@pytest.fixture
def mock_mongodb():
    """Provide a mock MongoDB client for testing."""
    if ADVANCED_FIXTURES_AVAILABLE:
        return mongomock.MongoClient()
    else:
        # Simple mock fallback
        mock = Mock()
        mock.gavatcore = Mock()
        mock.gavatcore.users = Mock()
        mock.gavatcore.sessions = Mock()
        return mock


@pytest.fixture
async def async_mock_database():
    """Provide async database mocks for testing."""
    class AsyncDatabaseMock:
        def __init__(self):
            self.redis = AsyncMock()
            self.mongodb = AsyncMock()
            self.postgresql = AsyncMock()
        
        async def connect(self):
            pass
        
        async def disconnect(self):
            pass
    
    db_mock = AsyncDatabaseMock()
    yield db_mock
    await db_mock.disconnect()


# ==================== API TESTING FIXTURES ====================

@pytest.fixture
def http_client():
    """Provide an HTTP client for API testing."""
    if ADVANCED_FIXTURES_AVAILABLE:
        return httpx.Client(base_url="http://testserver")
    else:
        # Mock HTTP client
        mock = Mock()
        mock.get.return_value = Mock(status_code=200, json=lambda: {})
        mock.post.return_value = Mock(status_code=201, json=lambda: {})
        return mock


@pytest.fixture
async def async_http_client():
    """Provide an async HTTP client for API testing."""
    if ADVANCED_FIXTURES_AVAILABLE:
        async with httpx.AsyncClient(base_url="http://testserver") as client:
            yield client
    else:
        # Mock async HTTP client
        mock = AsyncMock()
        mock.get.return_value = AsyncMock(status_code=200, json=AsyncMock(return_value={}))
        mock.post.return_value = AsyncMock(status_code=201, json=AsyncMock(return_value={}))
        yield mock


# ==================== MOCK SERVICES FIXTURES ====================

@pytest.fixture
def mock_telegram_client():
    """Provide a mock Telegram client for testing."""
    mock = AsyncMock()
    mock.connect.return_value = True
    mock.disconnect.return_value = True
    mock.send_message.return_value = Mock(id=12345, date=datetime.now())
    mock.get_entity.return_value = Mock(id=123456789, username="testuser")
    return mock


@pytest.fixture
def mock_openai_client():
    """Provide a mock OpenAI client for testing."""
    mock = Mock()
    mock.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Test AI response"))]
    )
    return mock


@pytest.fixture
def mock_session_manager():
    """Provide a mock session manager for testing."""
    mock = Mock()
    mock.create_session.return_value = "test_session_id"
    mock.get_session.return_value = {"user_id": 123456789, "active": True}
    mock.close_session.return_value = True
    return mock


# ==================== TEST DATA FIXTURES ====================

@pytest.fixture
def sample_users() -> List[Dict[str, Any]]:
    """Provide sample user data for testing."""
    return [
        {
            "id": 123456789,
            "username": "testuser1",
            "first_name": "Test",
            "last_name": "User1",
            "is_admin": True
        },
        {
            "id": 987654321,
            "username": "testuser2", 
            "first_name": "Test",
            "last_name": "User2",
            "is_admin": False
        }
    ]


@pytest.fixture
def sample_messages() -> List[Dict[str, Any]]:
    """Provide sample message data for testing."""
    return [
        {
            "id": 1,
            "user_id": 123456789,
            "text": "Hello, this is a test message",
            "timestamp": datetime.now() - timedelta(minutes=5)
        },
        {
            "id": 2,
            "user_id": 987654321,
            "text": "Another test message",
            "timestamp": datetime.now() - timedelta(minutes=2)
        }
    ]


@pytest.fixture
def fake_data():
    """Provide Faker instance for generating test data."""
    if ADVANCED_FIXTURES_AVAILABLE:
        return Faker()
    else:
        # Simple mock faker
        mock = Mock()
        mock.name.return_value = "Test User"
        mock.email.return_value = "test@example.com"
        mock.phone_number.return_value = "+1234567890"
        return mock


# ==================== PERFORMANCE TESTING FIXTURES ====================

@pytest.fixture
def performance_monitor():
    """Provide a performance monitoring fixture."""
    import time
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.measurements = []
        
        def start(self):
            self.start_time = time.perf_counter()
        
        def stop(self):
            self.end_time = time.perf_counter()
            if self.start_time:
                duration = self.end_time - self.start_time
                self.measurements.append(duration)
                return duration
            return 0
        
        def assert_performance(self, max_time_seconds: float):
            if self.start_time is None or self.end_time is None:
                raise ValueError("Performance monitor not properly started/stopped")
            
            duration = self.end_time - self.start_time
            assert duration <= max_time_seconds, f"Performance test failed: {duration:.3f}s > {max_time_seconds}s"
        
        def get_average_time(self) -> float:
            return sum(self.measurements) / len(self.measurements) if self.measurements else 0
    
    return PerformanceMonitor()


# ==================== ASYNC TESTING UTILITIES ====================

@pytest.fixture
async def async_context_manager():
    """Provide an async context manager for testing."""
    class AsyncContextManager:
        def __init__(self):
            self.entered = False
            self.exited = False
        
        async def __aenter__(self):
            self.entered = True
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            self.exited = True
    
    yield AsyncContextManager()


# ==================== SECURITY TESTING FIXTURES ====================

@pytest.fixture
def security_test_data():
    """Provide security-focused test data."""
    return {
        "sql_injection_attempts": [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM passwords--"
        ],
        "xss_attempts": [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "eval('malicious_code')"
        ],
        "path_traversal_attempts": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "file:///etc/passwd"
        ]
    }


# ==================== CLEANUP FIXTURES ====================

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically cleanup test files after each test."""
    yield
    
    # Cleanup temporary test files
    test_files = [
        "test_gavatcore.db",
        "test_gavatcore.session",
        "test_config.json",
        "test_logs.txt"
    ]
    
    for test_file in test_files:
        file_path = Path(test_file)
        if file_path.exists():
            try:
                file_path.unlink()
            except (PermissionError, OSError):
                pass  # Ignore cleanup errors


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables after each test."""
    original_env = os.environ.copy()
    yield
    
    # Reset to original environment
    test_vars = ["TESTING", "GAVATCORE_TEST_MODE", "DEBUG_MODE"]
    for var in test_vars:
        if var in original_env:
            os.environ[var] = original_env[var]
        elif var in os.environ:
            del os.environ[var]


# ==================== UTILITY FUNCTIONS ====================

def create_test_file(content: str, filename: str = "test_file.txt") -> Path:
    """Create a temporary test file with content."""
    test_file = Path(filename)
    test_file.write_text(content)
    return test_file


def load_test_json(filename: str) -> Dict[str, Any]:
    """Load JSON test data from file."""
    test_data_dir = Path("tests/data")
    test_data_dir.mkdir(exist_ok=True)
    
    json_file = test_data_dir / filename
    if json_file.exists():
        with open(json_file) as f:
            return json.load(f)
    else:
        # Return empty dict if file doesn't exist
        return {}


def assert_valid_config(config: Dict[str, Any]) -> None:
    """Assert that a configuration is valid."""
    required_fields = ["API_ID", "API_HASH", "AUTHORIZED_USERS"]
    for field in required_fields:
        assert field in config, f"Missing required field: {field}"
        assert config[field] is not None, f"Field cannot be None: {field}"


# ==================== PYTEST HOOKS ====================

def pytest_runtest_setup(item):
    """Setup for each test item."""
    # Add any per-test setup here
    pass


def pytest_runtest_teardown(item, nextitem):
    """Teardown for each test item."""
    # Add any per-test cleanup here
    pass


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add custom summary information to test output."""
    if hasattr(terminalreporter, '_session'):
        session = terminalreporter._session
        if hasattr(session, 'testscollected'):
            terminalreporter.write_sep("=", "GAVATCore Test Summary")
            terminalreporter.write_line(f"Total tests collected: {session.testscollected}")
            
            # Add coverage information if available
            if hasattr(terminalreporter, '_coverage'):
                terminalreporter.write_line("Coverage report generated in htmlcov/") 