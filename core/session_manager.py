#!/usr/bin/env python3
"""
🔧 GavatCore Session Manager 🔧

Production-grade Telegram session management with:
- Type-safe session handling
- Comprehensive error handling and retry logic
- Structured logging and monitoring
- Async session operations
- Session validation and health checks

Enhanced Features:
- Type annotations ve comprehensive error handling
- Structured logging ve performance monitoring
- Retry mechanisms ve graceful degradation
- Session lifecycle management
"""

import os
import asyncio
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import sqlite3
import contextlib
import structlog

from telethon import TelegramClient, errors
from telethon.sessions import StringSession
from telethon.tl.types import User

# Configure structured logging
logger = structlog.get_logger("gavatcore.session_manager")

# Type definitions
CodeCallback = Callable[[], Awaitable[str]]
PasswordCallback = Callable[[], Awaitable[str]]
SessionResult = Tuple[Optional[TelegramClient], Optional[User]]

SESSIONS_DIR = "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

@dataclass
class SessionConfig:
    """Session configuration parameters."""
    connection_retries: int = 3
    retry_delay: float = 2.0
    timeout: int = 30
    max_retry_attempts: int = 3
    base_retry_delay: float = 2.0
    min_session_file_size: int = 1024  # bytes

@dataclass
class SessionInfo:
    """Session information data structure."""
    phone: str
    session_path: str
    exists: bool = False
    valid: bool = False
    file_size: int = 0
    last_modified: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "phone": self.phone,
            "session_path": self.session_path,
            "exists": self.exists,
            "valid": self.valid,
            "file_size": self.file_size,
            "file_size_human": f"{self.file_size / 1024:.1f} KB" if self.file_size > 0 else "0 B",
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "error_message": self.error_message
        }

@dataclass
class SessionMetrics:
    """Session operation metrics."""
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_retry_attempts: int = 0
    database_lock_encounters: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        return (self.successful_operations / max(self.total_operations, 1)) * 100

# Global metrics instance
session_metrics = SessionMetrics()

class SessionManager:
    """
    🚀 Enhanced Session Manager
    
    Production-ready session management with comprehensive error handling,
    retry mechanisms, and monitoring capabilities.
    """
    
    def __init__(self, config: Optional[SessionConfig] = None):
        self.config = config or SessionConfig()
        logger.info("🔧 SessionManager initialized", config=self.config.__dict__)
    
    def get_session_path(self, phone: str) -> str:
        """
        Generate session file path for phone number.
        
        Args:
            phone: Phone number
            
        Returns:
            str: Session file path
        """
        session_name = phone.replace("+", "_")
        return os.path.join(SESSIONS_DIR, f"{session_name}.session")
    
    async def validate_session_file(self, session_path: str) -> Tuple[bool, str]:
        """
        Validate session file integrity.
        
        Args:
            session_path: Path to session file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not os.path.exists(session_path):
                return False, "Session file does not exist"
            
            file_size = os.path.getsize(session_path)
            if file_size < self.config.min_session_file_size:
                return False, f"Session file too small ({file_size} bytes)"
            
            # Test SQLite database integrity
            try:
                conn = sqlite3.connect(session_path, timeout=2.0)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions';")
                result = cursor.fetchone()
                conn.close()
                
                if result is None:
                    return False, "Invalid session database structure"
                
                return True, ""
                
            except sqlite3.Error as e:
                return False, f"Database error: {str(e)}"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @contextlib.asynccontextmanager
    async def operation_timer(self, operation: str):
        """Context manager for timing and logging operations."""
        start_time = asyncio.get_event_loop().time()
        session_metrics.total_operations += 1
        
        try:
            logger.debug("🔄 Operation started", operation=operation)
            yield
            session_metrics.successful_operations += 1
            logger.debug("✅ Operation completed", 
                        operation=operation,
                        duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000)
        except Exception as e:
            session_metrics.failed_operations += 1
            logger.error("❌ Operation failed", 
                        operation=operation,
                        error=str(e),
                        duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000)
            raise
    
    async def open_session(
        self,
        phone: str,
        api_id: int,
        api_hash: str,
        code_cb: CodeCallback,
        password_cb: PasswordCallback,
        session_str: Optional[str] = None,
        custom_session_path: Optional[str] = None
    ) -> SessionResult:
        """
        Open Telegram session with comprehensive error handling and retry logic.
        
        Args:
            phone: Phone number
            api_id: Telegram API ID
            api_hash: Telegram API hash
            code_cb: Callback for verification code
            password_cb: Callback for 2FA password
            session_str: Optional string session
            custom_session_path: Custom session file path
            
        Returns:
            Tuple of (TelegramClient, User) or (None, None) on failure
        """
        async with self.operation_timer("open_session"):
            client = None
            session_path = custom_session_path or self.get_session_path(phone)
            
            logger.info("🔑 Opening session", 
                       phone=phone, 
                       session_path=session_path,
                       using_string_session=bool(session_str))
            
            for attempt in range(self.config.max_retry_attempts):
                try:
                    # Create client based on session type
                    if session_str:
                        logger.debug("🔄 Using string session")
                        client = TelegramClient(
                            StringSession(session_str),
                            api_id,
                            api_hash,
                            connection_retries=self.config.connection_retries,
                            retry_delay=self.config.retry_delay,
                            timeout=self.config.timeout
                        )
                        await client.connect()
                    else:
                        # Validate existing session file
                        if os.path.exists(session_path):
                            is_valid, error_msg = await self.validate_session_file(session_path)
                            if is_valid:
                                logger.info("✅ Using existing session file", path=session_path)
                            else:
                                logger.warning("⚠️ Session file validation failed", 
                                             path=session_path, 
                                             error=error_msg)
                        else:
                            logger.info("🆕 Creating new session file", path=session_path)
                        
                        client = TelegramClient(
                            session_path,
                            api_id,
                            api_hash,
                            connection_retries=self.config.connection_retries,
                            retry_delay=self.config.retry_delay,
                            timeout=self.config.timeout
                        )
                        await client.connect()
                    
                    # Handle authorization
                    if not await client.is_user_authorized():
                        logger.info("🔐 Starting authorization flow", phone=phone)
                        
                        # Send code request
                        await client.send_code_request(phone)
                        code = await code_cb()
                        
                        try:
                            # Sign in with code
                            await client.sign_in(phone, code)
                            logger.info("✅ Code authentication successful")
                            
                        except errors.SessionPasswordNeededError:
                            # 2FA required
                            logger.info("🔐 2FA required, requesting password")
                            password = await password_cb()
                            await client.sign_in(password=password)
                            logger.info("✅ 2FA authentication successful")
                        
                        # Reconnect to ensure session is saved
                        await client.disconnect()
                        await asyncio.sleep(1.0)
                        await client.connect()
                        
                        # Validate saved session
                        if os.path.exists(session_path):
                            file_size = os.path.getsize(session_path)
                            logger.info("💾 Session file saved", 
                                       path=session_path, 
                                       size_bytes=file_size)
                            
                            if file_size < self.config.min_session_file_size:
                                logger.warning("⚠️ Session file suspiciously small, recreating...")
                                await client.disconnect()
                                await asyncio.sleep(1.0)
                                await client.connect()
                        else:
                            logger.error("❌ Session file not created", path=session_path)
                    
                    # Get user information
                    me = await client.get_me()
                    if me:
                        logger.info("🎉 Session opened successfully", 
                                   user_id=me.id,
                                   username=me.username or "N/A",
                                   first_name=me.first_name or "N/A",
                                   session_path=session_path)
                        return client, me
                    else:
                        raise Exception("Failed to get user information")
                        
                except Exception as e:
                    error_msg = str(e)
                    is_database_lock = "database is locked" in error_msg.lower()
                    
                    if is_database_lock:
                        session_metrics.database_lock_encounters += 1
                        
                    if is_database_lock and attempt < self.config.max_retry_attempts - 1:
                        wait_time = self.config.base_retry_delay * (attempt + 1)
                        session_metrics.total_retry_attempts += 1
                        
                        logger.warning("🔄 Database locked, retrying...", 
                                     attempt=attempt + 1,
                                     max_attempts=self.config.max_retry_attempts,
                                     wait_time=wait_time,
                                     error=error_msg)
                        
                        # Cleanup client
                        if client:
                            try:
                                await client.disconnect()
                            except:
                                pass
                        
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error("❌ Session opening failed", 
                                   phone=phone,
                                   attempt=attempt + 1,
                                   error=error_msg,
                                   exc_info=True)
                        
                        # Cleanup failed session file if it's corrupted
                        if session_path and os.path.exists(session_path):
                            try:
                                file_size = os.path.getsize(session_path)
                                if file_size < self.config.min_session_file_size:
                                    os.remove(session_path)
                                    logger.warning("🗑️ Removed corrupted session file", 
                                                 path=session_path,
                                                 size=file_size)
                            except Exception as cleanup_error:
                                logger.error("❌ Failed to cleanup session file", 
                                           error=str(cleanup_error))
                        
                        # Cleanup client
                        if client:
                            try:
                                await client.disconnect()
                            except:
                                pass
                        
                        if attempt == self.config.max_retry_attempts - 1:
                            raise e
            
            return None, None
    
    async def close_session(self, phone: str, api_id: int, api_hash: str) -> bool:
        """
        Close session and remove session file.
        
        Args:
            phone: Phone number
            api_id: Telegram API ID
            api_hash: Telegram API hash
            
        Returns:
            bool: True if successfully closed, False otherwise
        """
        async with self.operation_timer("close_session"):
            session_path = self.get_session_path(phone)
            
            try:
                logger.info("🔐 Closing session", phone=phone, session_path=session_path)
                
                client = TelegramClient(session_path, api_id, api_hash)
                await client.connect()
                
                try:
                    await client.log_out()
                    logger.info("📤 Logged out from Telegram")
                except Exception as e:
                    logger.warning("⚠️ Logout failed", error=str(e))
                finally:
                    await client.disconnect()
                    logger.info("🔌 Client disconnected")
                
                # Remove session file
                if os.path.exists(session_path):
                    os.remove(session_path)
                    logger.info("🗑️ Session file removed", path=session_path)
                
                return True
                
            except Exception as e:
                logger.error("❌ Failed to close session", 
                           phone=phone,
                           error=str(e),
                           exc_info=True)
                return False
    
    def list_sessions(self) -> List[str]:
        """
        List all session files.
        
        Returns:
            List of session file names
        """
        try:
            session_files = [
                f for f in os.listdir(SESSIONS_DIR)
                if f.endswith(".session")
            ]
            logger.debug("📋 Listed sessions", count=len(session_files))
            return session_files
        except Exception as e:
            logger.error("❌ Failed to list sessions", error=str(e))
            return []
    
    def is_session_active(self, phone: str) -> bool:
        """
        Check if session file exists.
        
        Args:
            phone: Phone number
            
        Returns:
            bool: True if session file exists, False otherwise
        """
        session_path = self.get_session_path(phone)
        exists = os.path.exists(session_path)
        
        logger.debug("🔍 Session existence check", 
                    phone=phone, 
                    path=session_path, 
                    exists=exists)
        
        return exists
    
    async def test_session(self, phone: str, api_id: int, api_hash: str) -> bool:
        """
        Test session connectivity.
        
        Args:
            phone: Phone number
            api_id: Telegram API ID
            api_hash: Telegram API hash
            
        Returns:
            bool: True if session is valid and connected, False otherwise
        """
        async with self.operation_timer("test_session"):
            session_path = self.get_session_path(phone)
            
            try:
                logger.debug("🧪 Testing session", phone=phone, session_path=session_path)
                
                # Validate file first
                is_valid, error_msg = await self.validate_session_file(session_path)
                if not is_valid:
                    logger.warning("❌ Session file validation failed", 
                                 phone=phone, 
                                 error=error_msg)
                    return False
                
                client = TelegramClient(
                    session_path,
                    api_id,
                    api_hash,
                    connection_retries=self.config.connection_retries,
                    retry_delay=self.config.retry_delay,
                    timeout=self.config.timeout
                )
                
                await client.connect()
                
                try:
                    # Test authorization
                    if not await client.is_user_authorized():
                        logger.warning("❌ Session not authorized", phone=phone)
                        return False
                    
                    # Test by getting user info
                    me = await client.get_me()
                    if me:
                        logger.info("✅ Session test successful", 
                                  phone=phone,
                                  user_id=me.id,
                                  username=me.username or "N/A")
                        return True
                    else:
                        logger.warning("❌ Failed to get user info", phone=phone)
                        return False
                        
                finally:
                    await client.disconnect()
                    
            except Exception as e:
                logger.error("❌ Session test failed", 
                           phone=phone,
                           error=str(e))
                return False
    
    def get_session_info(self, phone: str) -> SessionInfo:
        """
        Get detailed session information.
        
        Args:
            phone: Phone number
            
        Returns:
            SessionInfo object with detailed information
        """
        session_path = self.get_session_path(phone)
        info = SessionInfo(phone=phone, session_path=session_path)
        
        try:
            if os.path.exists(session_path):
                info.exists = True
                stat = os.stat(session_path)
                info.file_size = stat.st_size
                info.last_modified = datetime.fromtimestamp(stat.st_mtime)
                
                # Quick validation
                if info.file_size >= self.config.min_session_file_size:
                    try:
                        conn = sqlite3.connect(session_path, timeout=1.0)
                        cursor = conn.cursor()
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions';")
                        result = cursor.fetchone()
                        conn.close()
                        info.valid = result is not None
                    except sqlite3.Error as e:
                        info.error_message = f"Database error: {str(e)}"
                else:
                    info.error_message = f"File too small ({info.file_size} bytes)"
            else:
                info.error_message = "File does not exist"
                
        except Exception as e:
            info.error_message = f"Error reading file: {str(e)}"
        
        return info
    
    def get_session_info_list(self) -> List[Dict[str, Any]]:
        """
        Get information for all sessions.
        
        Returns:
            List of session information dictionaries
        """
        sessions = []
        session_files = self.list_sessions()
        
        for session_file in session_files:
            phone = self.session_phone_from_path(session_file)
            info = self.get_session_info(phone)
            sessions.append(info.to_dict())
        
        logger.debug("📊 Generated session info list", count=len(sessions))
        return sessions
    
    def session_phone_from_path(self, session_path: str) -> str:
        """
        Extract phone number from session path.
        
        Args:
            session_path: Session file path
            
        Returns:
            str: Phone number
        """
        filename = os.path.basename(session_path)
        phone = filename.replace("_", "+").replace(".session", "")
        return phone
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get session manager metrics.
        
        Returns:
            Dict with performance metrics
        """
        return {
            "total_operations": session_metrics.total_operations,
            "successful_operations": session_metrics.successful_operations,
            "failed_operations": session_metrics.failed_operations,
            "success_rate": session_metrics.success_rate,
            "total_retry_attempts": session_metrics.total_retry_attempts,
            "database_lock_encounters": session_metrics.database_lock_encounters,
            "sessions_directory": SESSIONS_DIR,
            "active_sessions": len(self.list_sessions())
        }

# Global session manager instance
session_manager = SessionManager()

# Convenience functions for backward compatibility
async def open_session(
    phone: str,
    api_id: int,
    api_hash: str,
    code_cb: CodeCallback,
    password_cb: PasswordCallback,
    session_str: Optional[str] = None,
    custom_session_path: Optional[str] = None
) -> SessionResult:
    """Convenience function for opening session."""
    return await session_manager.open_session(
        phone, api_id, api_hash, code_cb, password_cb, session_str, custom_session_path
    )

async def close_session(phone: str, api_id: int, api_hash: str) -> bool:
    """Convenience function for closing session."""
    return await session_manager.close_session(phone, api_id, api_hash)

def list_sessions() -> List[str]:
    """Convenience function for listing sessions."""
    return session_manager.list_sessions()

def is_session_active(phone: str) -> bool:
    """Convenience function for checking session existence."""
    return session_manager.is_session_active(phone)

async def test_session(phone: str, api_id: int, api_hash: str) -> bool:
    """Convenience function for testing session."""
    return await session_manager.test_session(phone, api_id, api_hash)

def get_session_path(phone: str) -> str:
    """Convenience function for getting session path."""
    return session_manager.get_session_path(phone)

def session_phone_from_path(session_path: str) -> str:
    """Convenience function for extracting phone from path."""
    return session_manager.session_phone_from_path(session_path)

def get_session_info_list() -> List[Dict[str, Any]]:
    """Convenience function for getting session info list."""
    return session_manager.get_session_info_list()

# Legacy functions for backward compatibility
async def notify_admin_dm(bot_client: TelegramClient, admin_id: int, message: str) -> None:
    """Send DM to admin (legacy function)."""
    try:
        await bot_client.send_message(admin_id, message)
        logger.info("📤 Admin notification sent", admin_id=admin_id)
    except Exception as e:
        logger.error("❌ Failed to notify admin", admin_id=admin_id, error=str(e))

async def create_session_flow(phone_override: Optional[str] = None) -> None:
    """Interactive session creation flow (legacy function)."""
    phone = phone_override or input("📱 Telefon numarası (+90...): ")
    
    async def code_cb() -> str:
        return input("🔐 Doğrulama kodu: ")
    
    async def pw_cb() -> str:
        return input("🔒 2FA şifresi: ")
    
    try:
        # Import config in function to avoid circular imports
        from config import API_ID, API_HASH
        
        client, user = await open_session(phone, API_ID, API_HASH, code_cb, pw_cb)
        if client and user:
            print(f"✅ Session başarıyla oluşturuldu: {user.first_name}")
            await client.disconnect()
        else:
            print("❌ Session oluşturulamadı")
    except Exception as e:
        logger.error("❌ Session creation flow failed", error=str(e))
        print(f"❌ Hata: {e}")

async def terminate_session(phone: str) -> None:
    """Terminate session (legacy function)."""
    try:
        from config import API_ID, API_HASH
        success = await close_session(phone, API_ID, API_HASH)
        if success:
            print(f"✅ Session sonlandırıldı: {phone}")
        else:
            print(f"❌ Session sonlandırılamadı: {phone}")
    except Exception as e:
        logger.error("❌ Session termination failed", phone=phone, error=str(e))
        print(f"❌ Hata: {e}")

async def get_active_sessions() -> List[Dict[str, Any]]:
    """Get active sessions (legacy function)."""
    return get_session_info_list()

