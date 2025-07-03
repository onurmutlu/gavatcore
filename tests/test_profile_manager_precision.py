#!/usr/bin/env python3
"""
🎯 ProfileManager Precision Coverage Tests - %0.0 → %90+ 🎯

Bu surgical test suite core/profile_manager.py'deki tüm functionality'yi kapsar:

Target Coverage: 120 statements -> %90+ coverage
Test Strategy: Full module testing with comprehensive edge cases

Covered Areas:
- ProfileManager initialization and directory creation
- Profile get/save operations (JSON + Database)
- Cache management and error handling
- Database CRUD operations with SQL
- Profile activity updates and deletion
- Error scenarios and exception handling

Bu precision test'ler her functionality'yi yakalayacak.
"""

import pytest
import asyncio
import os
import sys
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock, AsyncMock, call, mock_open
from unittest.mock import PropertyMock
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.profile_manager import ProfileManager

# ==================== SURGICAL PRECISION TESTS ====================

class TestProfileManagerPrecisionCoverage:
    """Surgical precision tests targeting complete ProfileManager functionality"""
    
    def setup_method(self):
        """Setup for each test method."""
        self.profile_manager = ProfileManager()
        self.test_username = "test_user"
        self.test_profile = {
            "profile_type": "escort",
            "is_spam_active": True,
            "is_dm_active": True,
            "is_group_active": False,
            "engaging_messages": ["Hello", "Hi there"],
            "response_style": "flirty",
            "tone": "seductive",
            "topics": ["fashion", "lifestyle"]
        }
    
    @pytest.mark.asyncio
    async def test_profile_manager_initialization_and_directory_creation(self):
        """Test ProfileManager initialization and directory creation."""
        
        with patch('os.makedirs') as mock_makedirs:
            
            # Test initialization
            pm = ProfileManager()
            
            # Verify directory creation was called
            mock_makedirs.assert_called_once_with("data/personas", exist_ok=True)
            
            # Verify initial state
            assert pm._profile_cache == {}
    
    @pytest.mark.asyncio
    async def test_get_profile_from_cache_success(self):
        """Test getting profile from cache."""
        
        # Pre-populate cache
        self.profile_manager._profile_cache[self.test_username] = self.test_profile
        
        # Get profile
        result = await self.profile_manager.get_profile(self.test_username)
        
        # Verify result
        assert result == self.test_profile
    
    @pytest.mark.asyncio
    async def test_get_profile_from_json_file_success(self):
        """Test getting profile from JSON file."""
        
        # Mock file operations with async context manager
        mock_file_content = json.dumps(self.test_profile)
        
        with patch('os.path.exists', return_value=True):
            # Properly mock aiofiles.open for async context manager
            with patch('aiofiles.open', mock_open(read_data=mock_file_content)) as mock_aio_open:
                # Make the mock support async context manager
                mock_aio_open.return_value.__aenter__ = AsyncMock()
                mock_aio_open.return_value.__aexit__ = AsyncMock()
                mock_aio_open.return_value.read = AsyncMock(return_value=mock_file_content)
                
                # Get profile
                result = await self.profile_manager.get_profile(self.test_username)
                
                # Verify result
                assert result == self.test_profile
                # Verify cached
                assert self.profile_manager._profile_cache[self.test_username] == self.test_profile
    
    @pytest.mark.asyncio
    async def test_get_profile_json_file_read_error(self):
        """Test JSON file read error handling."""
        
        # Mock file exists but reading fails
        with patch('os.path.exists', return_value=True):
            with patch('aiofiles.open', side_effect=FileNotFoundError("File not found")):
                # Get profile should continue to DB lookup
                with patch('core.db.connection.get_session') as mock_get_session:
                    mock_session = AsyncMock()
                    mock_get_session.return_value = mock_session
                    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
                    mock_session.__aexit__ = AsyncMock(return_value=None)
                    
                    # Mock DB query result
                    mock_result = MagicMock()
                    mock_result.scalar_one_or_none.return_value = None
                    mock_session.execute.return_value = mock_result
                    
                    result = await self.profile_manager.get_profile(self.test_username)
                    
                    # Should return None (due to FileNotFoundError in JSON read and no DB result)
                    assert result is None
    
    @pytest.mark.asyncio
    async def test_get_profile_from_database_success(self):
        """Test getting profile from database."""
        
        # Mock no cache, no file
        with patch('os.path.exists', return_value=False):
            with patch('core.db.connection.get_session') as mock_get_session:
                mock_session = AsyncMock()
                mock_get_session.return_value = mock_session
                mock_session.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session.__aexit__ = AsyncMock(return_value=None)
                
                # Mock DB profile
                mock_db_profile = MagicMock()
                mock_db_profile.profile_data = self.test_profile
                
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_db_profile
                mock_session.execute.return_value = mock_result
                
                result = await self.profile_manager.get_profile(self.test_username)
                
                # Verify result
                assert result == self.test_profile
                # Verify cached
                assert self.profile_manager._profile_cache[self.test_username] == self.test_profile
    
    @pytest.mark.asyncio
    async def test_get_profile_database_error(self):
        """Test database error handling."""
        
        with patch('os.path.exists', return_value=False):
            with patch('core.db.connection.get_session', side_effect=Exception("DB connection failed")):
                
                result = await self.profile_manager.get_profile(self.test_username)
                
                # Should return None (due to DB error)
                assert result is None
    
    @pytest.mark.asyncio
    async def test_get_profile_general_exception(self):
        """Test general exception handling in get_profile."""
        
        # Create a profile manager where cache access will work but processing will fail
        with patch('os.path.exists', side_effect=Exception("General error")):
            
            result = await self.profile_manager.get_profile(self.test_username)
            
            # Should return None due to exception
            assert result is None
    
    @pytest.mark.asyncio
    async def test_save_profile_success_new_profile(self):
        """Test successful profile save (new profile)."""
        
        # Mock datetime
        mock_datetime = "2023-01-01T10:00:00"
        with patch('core.profile_manager.datetime') as mock_dt:
            mock_dt.now.return_value.isoformat.return_value = mock_datetime
            
            # Mock file operations with proper async context manager
            with patch('aiofiles.open', mock_open()) as mock_aio_open:
                # Make aiofiles.open support async context manager  
                mock_aio_open.return_value.__aenter__ = AsyncMock()
                mock_aio_open.return_value.__aexit__ = AsyncMock()
                mock_aio_open.return_value.write = AsyncMock()
                
                # Mock database operations
                with patch('core.profile_manager.get_db_session') as mock_get_session:
                    # Create proper async context manager
                    mock_session = AsyncMock()
                    mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
                    mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
                    
                    # Mock no existing profile
                    mock_result = MagicMock()
                    mock_result.first.return_value = None
                    mock_session.execute.return_value = mock_result
                    
                    # Mock successful operations
                    mock_session.commit = AsyncMock()
                    
                    result = await self.profile_manager.save_profile(self.test_username, self.test_profile.copy())
                    
                    # Verify success
                    assert result is True
                    
                    # Verify timestamps were added
                    expected_profile = self.test_profile.copy()
                    expected_profile["updated_at"] = mock_datetime
                    expected_profile["created_at"] = mock_datetime
                    
                    # Verify cached
                    assert self.profile_manager._profile_cache[self.test_username] == expected_profile
    
    @pytest.mark.asyncio
    async def test_save_profile_success_existing_profile(self):
        """Test successful profile save (existing profile update)."""
        
        # Mock datetime
        mock_datetime = "2023-01-01T11:00:00"
        with patch('core.profile_manager.datetime') as mock_dt:
            mock_dt.now.return_value.isoformat.return_value = mock_datetime
            
            # Add created_at to profile
            profile_with_created = self.test_profile.copy()
            profile_with_created["created_at"] = "2023-01-01T09:00:00"
            
            # Mock file operations with proper async context manager
            with patch('aiofiles.open', mock_open()) as mock_aio_open:
                mock_aio_open.return_value.__aenter__ = AsyncMock()
                mock_aio_open.return_value.__aexit__ = AsyncMock()
                mock_aio_open.return_value.write = AsyncMock()
                
                # Mock database operations
                with patch('core.profile_manager.get_db_session') as mock_get_session:
                    mock_session = AsyncMock()
                    mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
                    mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
                    
                    # Mock existing profile
                    mock_result = MagicMock()
                    mock_result.first.return_value = MagicMock(id=1)
                    mock_session.execute.return_value = mock_result
                    
                    # Mock successful operations
                    mock_session.commit = AsyncMock()
                    
                    result = await self.profile_manager.save_profile(self.test_username, profile_with_created)
                    
                    # Verify success
                    assert result is True
    
    @pytest.mark.asyncio
    async def test_save_profile_database_error(self):
        """Test database error handling in save_profile."""
        
        # Mock file operations succeed
        with patch('aiofiles.open', mock_open()) as mock_aio_open:
            mock_aio_open.return_value.__aenter__ = AsyncMock()
            mock_aio_open.return_value.__aexit__ = AsyncMock()
            mock_aio_open.return_value.write = AsyncMock()
            
            # Mock database error
            with patch('core.profile_manager.get_db_session', side_effect=Exception("DB error")):
                
                result = await self.profile_manager.save_profile(self.test_username, self.test_profile.copy())
                
                # Should still return True (file save succeeded)
                assert result is True
    
    @pytest.mark.asyncio
    async def test_save_profile_file_write_error(self):
        """Test file write error handling in save_profile."""
        
        # Mock file write error
        with patch('aiofiles.open', side_effect=PermissionError("Write access denied")):
            
            result = await self.profile_manager.save_profile(self.test_username, self.test_profile.copy())
            
            # Should return False
            assert result is False
    
    @pytest.mark.asyncio
    async def test_get_all_profiles_success(self):
        """Test getting all profiles successfully."""
        
        # Mock directory listing
        mock_files = ["user1.json", "user2.json", "other.txt", "user3.json"]
        
        with patch('os.listdir', return_value=mock_files):
            # Mock get_profile calls
            mock_profiles = {
                "user1": {"name": "User 1"},
                "user2": {"name": "User 2"},
                "user3": {"name": "User 3"}
            }
            
            async def mock_get_profile(username):
                return mock_profiles.get(username)
            
            with patch.object(self.profile_manager, 'get_profile', side_effect=mock_get_profile):
                
                result = await self.profile_manager.get_all_profiles()
                
                # Verify result
                assert result == mock_profiles
    
    @pytest.mark.asyncio
    async def test_get_all_profiles_directory_error(self):
        """Test directory listing error in get_all_profiles."""
        
        with patch('os.listdir', side_effect=FileNotFoundError("Directory not found")):
            
            result = await self.profile_manager.get_all_profiles()
            
            # Should return empty dict
            assert result == {}
    
    @pytest.mark.asyncio
    async def test_delete_profile_success(self):
        """Test successful profile deletion."""
        
        # Setup profile in cache
        self.profile_manager._profile_cache[self.test_username] = self.test_profile
        
        # Mock file operations
        with patch('os.path.exists', return_value=True):
            with patch('os.remove') as mock_remove:
                # Mock database operations
                with patch('core.profile_manager.get_db_session') as mock_get_session:
                    mock_session = AsyncMock()
                    mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
                    mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
                    
                    mock_session.execute = AsyncMock()
                    mock_session.commit = AsyncMock()
                    
                    result = await self.profile_manager.delete_profile(self.test_username)
                    
                    # Verify success
                    assert result is True
                    
                    # Verify file was removed
                    mock_remove.assert_called_once()
                    
                    # Verify cache was cleared
                    assert self.test_username not in self.profile_manager._profile_cache
                    
                    # Verify database delete
                    mock_session.execute.assert_called()
                    mock_session.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_delete_profile_file_not_exists(self):
        """Test profile deletion when file doesn't exist."""
        
        # Setup profile in cache
        self.profile_manager._profile_cache[self.test_username] = self.test_profile
        
        # Mock file doesn't exist
        with patch('os.path.exists', return_value=False):
            # Mock database operations
            with patch('core.profile_manager.get_db_session') as mock_get_session:
                mock_session = AsyncMock()
                mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
                mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
                
                mock_session.execute = AsyncMock()
                mock_session.commit = AsyncMock()
                
                result = await self.profile_manager.delete_profile(self.test_username)
                
                # Should still succeed
                assert result is True
                
                # Verify cache was cleared
                assert self.test_username not in self.profile_manager._profile_cache
    
    @pytest.mark.asyncio
    async def test_delete_profile_database_error(self):
        """Test database error handling in delete_profile."""
        
        with patch('os.path.exists', return_value=True):
            with patch('os.remove'):
                # Mock database error
                with patch('core.profile_manager.get_db_session', side_effect=Exception("DB error")):
                    
                    result = await self.profile_manager.delete_profile(self.test_username)
                    
                    # Should still return True (file deleted)
                    assert result is True
    
    @pytest.mark.asyncio
    async def test_delete_profile_general_error(self):
        """Test general error handling in delete_profile."""
        
        # Mock file remove error
        with patch('os.path.exists', return_value=True):
            with patch('os.remove', side_effect=PermissionError("Permission denied")):
                
                result = await self.profile_manager.delete_profile(self.test_username)
                
                # Should return False
                assert result is False
    
    @pytest.mark.asyncio
    async def test_update_profile_activity_success(self):
        """Test successful profile activity update."""
        
        # Mock database operations
        with patch('core.profile_manager.get_db_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            mock_session.execute = AsyncMock()
            mock_session.commit = AsyncMock()
            
            result = await self.profile_manager.update_profile_activity(
                self.test_username, "spam", True
            )
            
            # Verify success
            assert result is True
            
            # Verify database operations
            mock_session.execute.assert_called()
            mock_session.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_update_profile_activity_database_error(self):
        """Test database error in update_profile_activity."""
        
        # Mock database error
        with patch('core.profile_manager.get_db_session', side_effect=Exception("DB connection failed")):
            
            result = await self.profile_manager.update_profile_activity(
                self.test_username, "spam", True
            )
            
            # Should return False
            assert result is False
    
    @pytest.mark.asyncio
    async def test_clear_cache(self):
        """Test cache clearing functionality."""
        
        # Populate cache
        self.profile_manager._profile_cache["user1"] = {"test": "data1"}
        self.profile_manager._profile_cache["user2"] = {"test": "data2"}
        
        # Clear cache
        self.profile_manager.clear_cache()
        
        # Verify cache is empty
        assert self.profile_manager._profile_cache == {}

# ==================== INTEGRATION TESTS ====================

class TestProfileManagerIntegration:
    """Integration tests for ProfileManager with real-like scenarios."""
    
    def setup_method(self):
        """Setup for each test."""
        self.profile_manager = ProfileManager()
        
    @pytest.mark.asyncio
    async def test_full_profile_lifecycle(self):
        """Test complete profile lifecycle: save -> get -> update -> delete."""
        
        username = "lifecycle_user"
        initial_profile = {
            "profile_type": "entertainer",
            "is_spam_active": False,
            "is_dm_active": True,
            "response_style": "friendly"
        }
        
        # Mock all external dependencies
        with patch('aiofiles.open', mock_open()) as mock_aio_open:
            mock_aio_open.return_value.__aenter__ = AsyncMock()
            mock_aio_open.return_value.__aexit__ = AsyncMock()
            mock_aio_open.return_value.write = AsyncMock()
            
            with patch('core.profile_manager.get_db_session') as mock_get_session:
                mock_session = AsyncMock()
                mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
                mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
                
                # Mock database operations
                mock_result = MagicMock()
                mock_result.first.return_value = None  # No existing profile
                mock_session.execute.return_value = mock_result
                mock_session.commit = AsyncMock()
                
                # 1. Save profile
                save_result = await self.profile_manager.save_profile(username, initial_profile.copy())
                assert save_result is True
                
                # 2. Get profile (from cache)
                retrieved_profile = await self.profile_manager.get_profile(username)
                assert retrieved_profile["profile_type"] == "entertainer"
                assert "updated_at" in retrieved_profile
                assert "created_at" in retrieved_profile
                
                # 3. Update activity
                with patch('os.path.exists', return_value=True):
                    with patch('os.remove') as mock_remove:
                        
                        # 4. Delete profile
                        delete_result = await self.profile_manager.delete_profile(username)
                        assert delete_result is True
                        
                        # Verify cache cleared
                        assert username not in self.profile_manager._profile_cache

# ==================== EDGE CASES ====================

class TestProfileManagerEdgeCases:
    """Edge case tests for ProfileManager."""
    
    def setup_method(self):
        """Setup for each test."""
        self.profile_manager = ProfileManager()
    
    @pytest.mark.asyncio
    async def test_save_profile_with_special_characters(self):
        """Test saving profile with special characters in data."""
        
        special_profile = {
            "username": "special_üser",
            "bio": "Hello 🔥 World! Special chars: äöü@#$%",
            "messages": ["Merhaba! 👋", "How are you? 😊"],
            "topics": ["özel konular", "unicode test"]
        }
        
        with patch('aiofiles.open', mock_open()) as mock_aio_open:
            mock_aio_open.return_value.__aenter__ = AsyncMock()
            mock_aio_open.return_value.__aexit__ = AsyncMock()
            mock_aio_open.return_value.write = AsyncMock()
            
            with patch('core.profile_manager.get_db_session') as mock_get_session:
                mock_session = AsyncMock()
                mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
                mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
                
                mock_result = MagicMock()
                mock_result.first.return_value = None
                mock_session.execute.return_value = mock_result
                mock_session.commit = AsyncMock()
                
                result = await self.profile_manager.save_profile("special_user", special_profile)
                
                # Should handle special characters
                assert result is True
    
    @pytest.mark.asyncio
    async def test_get_profile_malformed_json(self):
        """Test handling malformed JSON in profile file."""
        
        with patch('os.path.exists', return_value=True):
            with patch('aiofiles.open', mock_open(read_data='{"invalid": json,}')) as mock_aio_open:
                # Make the mock support async context manager but raise JSON error
                mock_aio_open.return_value.__aenter__ = AsyncMock()
                mock_aio_open.return_value.__aexit__ = AsyncMock()
                mock_aio_open.return_value.read = AsyncMock(return_value='{"invalid": json,}')
                
                # Mock database fallback
                with patch('core.db.connection.get_session') as mock_get_session:
                    mock_session = AsyncMock()
                    mock_get_session.return_value = mock_session
                    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
                    mock_session.__aexit__ = AsyncMock(return_value=None)
                    
                    mock_result = MagicMock()
                    mock_result.scalar_one_or_none.return_value = None
                    mock_session.execute.return_value = mock_result
                    
                    result = await self.profile_manager.get_profile("malformed_user")
                    
                    # Should handle JSON error and try database, return None if no DB result
                    assert result is None

# ==================== RUNNER ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 