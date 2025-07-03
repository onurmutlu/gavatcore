#!/usr/bin/env python3
"""
🔐 AUTHENTICATION SERVICE
JWT token management and user authentication
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ValidationError
from app.models.user import User


class AuthService:
    """Authentication service for JWT tokens and user management"""
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, user_id: int, user_data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire)
        
        payload = {
            "user_id": user_id,
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: int) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire)
        
        payload = {
            "user_id": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
    
    async def register_user(
        self, 
        db: AsyncSession,
        username: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        telegram_data: Optional[Dict] = None
    ) -> User:
        """Register new user"""
        
        # Check if username exists
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise ValidationError("Username already exists")
        
        # Check if email exists (if provided)
        if email:
            stmt = select(User).where(User.email == email)
            result = await db.execute(stmt)
            existing_email = result.scalar_one_or_none()
            
            if existing_email:
                raise ValidationError("Email already exists")
        
        # Create new user
        user_data = {
            "username": username,
            "email": email,
            "is_active": True,
            "registration_source": "telegram" if telegram_data else "web"
        }
        
        # Hash password if provided
        if password:
            user_data["password_hash"] = self.hash_password(password)
        
        # Add telegram data if provided
        if telegram_data:
            user_data.update({
                "telegram_user_id": telegram_data.get("id"),
                "telegram_username": telegram_data.get("username"),
                "telegram_first_name": telegram_data.get("first_name"),
                "telegram_last_name": telegram_data.get("last_name"),
                "telegram_language_code": telegram_data.get("language_code", "tr")
            })
        
        user = User(**user_data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    async def authenticate_user(
        self,
        db: AsyncSession,
        username: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user with username/password"""
        
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not user.password_hash:  # type: ignore
            raise AuthenticationError("User has no password set")
        
        if not self.verify_password(password, user.password_hash):  # type: ignore
            return None
        
        if not user.is_active:  # type: ignore
            raise AuthenticationError("User account is disabled")
        
        # Update last login
        user.last_login_at = datetime.utcnow()  # type: ignore
        await db.commit()
        
        return user
    
    async def authenticate_telegram(
        self,
        db: AsyncSession,
        telegram_user_id: int
    ) -> Optional[User]:
        """Authenticate user with Telegram ID"""
        
        stmt = select(User).where(User.telegram_user_id == telegram_user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not user.is_active:  # type: ignore
            raise AuthenticationError("User account is disabled")
        
        # Update last login
        user.last_login_at = datetime.utcnow()  # type: ignore
        await db.commit()
        
        return user
    
    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    def create_token_pair(self, user: User) -> Dict[str, Any]:
        """Create access and refresh token pair"""
        user_data = {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
        
        access_token = self.create_access_token(user.id, user_data)  # type: ignore
        refresh_token = self.create_refresh_token(user.id)  # type: ignore
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire * 60  # seconds
        } 