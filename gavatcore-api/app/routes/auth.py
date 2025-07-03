#!/usr/bin/env python3
"""
🔐 GAVATCORE SaaS AUTH ROUTES
Authentication and authorization endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional
import structlog

from app.core.dependencies import get_db, get_current_user, get_auth_service
from app.services.auth_service import AuthService
from app.models.user import User
from app.core.exceptions import AuthenticationError, ValidationError

logger = structlog.get_logger("gavatcore.auth")

router = APIRouter()
security = HTTPBearer()


# Request/Response Models
class UserRegisterRequest(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLoginRequest(BaseModel):
    username: str
    password: str


class TelegramAuthRequest(BaseModel):
    telegram_user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = "tr"


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    full_name: str
    is_active: bool
    registration_source: str
    telegram_username: Optional[str] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse


@router.post("/register", response_model=TokenResponse)
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """User registration with email/password"""
    try:
        # Register user
        user = await auth_service.register_user(
            db=db,
            username=request.username,
            email=request.email,
            password=request.password
        )
        
        # Create tokens
        tokens = auth_service.create_token_pair(user)
        
        logger.info(f"User registered successfully: {user.username}")
        
        return TokenResponse(
            **tokens,
            user=UserResponse.from_orm(user)
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """User login with username/password"""
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(
            db=db,
            username=request.username,
            password=request.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Create tokens
        tokens = auth_service.create_token_pair(user)
        
        logger.info(f"User logged in successfully: {user.username}")
        
        return TokenResponse(
            **tokens,
            user=UserResponse.from_orm(user)
        )
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/telegram", response_model=TokenResponse)
async def telegram_auth(
    request: TelegramAuthRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Telegram authentication/registration"""
    try:
        # Try to authenticate existing user
        user = await auth_service.authenticate_telegram(
            db=db,
            telegram_user_id=request.telegram_user_id
        )
        
        # If user doesn't exist, register them
        if not user:
            telegram_data = {
                "id": request.telegram_user_id,
                "username": request.username,
                "first_name": request.first_name,
                "last_name": request.last_name,
                "language_code": request.language_code
            }
            
            # Generate username if not provided
            username = request.username or f"tg_{request.telegram_user_id}"
            
            user = await auth_service.register_user(
                db=db,
                username=username,
                telegram_data=telegram_data
            )
            
            logger.info(f"New Telegram user registered: {user.username}")
        else:
            logger.info(f"Telegram user authenticated: {user.username}")
        
        # Create tokens
        tokens = auth_service.create_token_pair(user)
        
        return TokenResponse(
            **tokens,
            user=UserResponse.from_orm(user)
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Telegram auth failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Telegram authentication failed"
        )


@router.post("/refresh")
async def refresh_token():
    """Refresh access token"""
    return {
        "success": True,
        "message": "Token refresh - TODO: implement"
    }


@router.post("/logout")
async def logout():
    """User logout (invalidate tokens)"""
    return {
        "success": True,
        "message": "Logout successful"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse.from_orm(current_user)


@router.get("/verify")
async def verify_token(
    current_user: User = Depends(get_current_user)
):
    """Verify token validity"""
    return {
        "valid": True,
        "user_id": current_user.id,  # type: ignore
        "username": current_user.username
    } 