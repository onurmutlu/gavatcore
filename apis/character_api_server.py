#!/usr/bin/env python3
"""
GavatCore Character API Server
Production-ready FastAPI server for character management

Features:
- Read/Write character data from data/personas/*.json
- Async IO for file operations
- Pydantic models for data validation
- CORS middleware for Flutter web
- Comprehensive logging and error handling
- RESTful API design
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
import uvicorn
import aiofiles

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('character_api.log')
    ]
)
logger = logging.getLogger("GavatCore.CharacterAPI")

# FastAPI app configuration
app = FastAPI(
    title="GavatCore Character API",
    description="Production character management API for GavatCore system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for Flutter web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Configuration
PERSONAS_DIR = Path("data/personas")
BACKUP_DIR = Path("backups/character_api")

# Ensure directories exist
PERSONAS_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Pydantic Models for data validation
class PersonaData(BaseModel):
    """Character persona information"""
    age: Optional[str] = Field(None, description="Character age range")
    style: Optional[str] = Field(None, description="Character style description")
    role: Optional[str] = Field(None, description="Character role")
    gpt_prompt: Optional[str] = Field(None, description="GPT character prompt")

class BotConfig(BaseModel):
    """Bot configuration settings"""
    dm_invite_enabled: Optional[bool] = Field(True, description="Enable DM invites")
    dm_invite_chance: Optional[float] = Field(0.7, ge=0.0, le=1.0)
    spam_protection_enabled: Optional[bool] = Field(True)
    spam_protection_type: Optional[str] = Field("aggressive")
    max_messages_per_minute: Optional[int] = Field(6, ge=1, le=100)
    reply_mode: Optional[str] = Field("gpt")
    auto_menu_enabled: Optional[bool] = Field(True)
    auto_menu_threshold: Optional[int] = Field(3, ge=1, le=10)
    vip_price: Optional[str] = Field("250")
    group_invite_aggressive: Optional[bool] = Field(True)
    group_invite_frequency: Optional[str] = Field("high")
    special_restrictions: Optional[Dict[str, Any]] = Field(default_factory=dict)

class PaymentInfo(BaseModel):
    """Payment account information"""
    iban: Optional[str] = Field(None, description="IBAN number")
    name: Optional[str] = Field(None, description="Account holder name")

class CharacterData(BaseModel):
    """Complete character data model"""
    username: str = Field(..., description="Unique character username")
    display_name: Optional[str] = Field(None, description="Display name")
    telegram_handle: Optional[str] = Field(None)
    phone: Optional[str] = Field(None)
    user_id: Optional[int] = Field(None)
    created_at: Optional[str] = Field(None)
    type: Optional[str] = Field("bot")
    owner_id: Optional[str] = Field("system")
    persona: Optional[PersonaData] = Field(None)
    reply_mode: Optional[str] = Field("hybrid")
    manualplus_timeout_sec: Optional[int] = Field(30, ge=5, le=300)
    use_default_templates: Optional[bool] = Field(False)
    gpt_enhanced: Optional[bool] = Field(True)
    autospam: Optional[bool] = Field(True)
    spam_frequency: Optional[str] = Field("medium")
    spam_interval_min: Optional[int] = Field(300, ge=60)
    spam_interval_max: Optional[int] = Field(600, ge=300)
    group_spam_enabled: Optional[bool] = Field(True)
    group_spam_aggressive: Optional[bool] = Field(False)
    auto_menu_enabled: Optional[bool] = Field(True)
    auto_menu_threshold: Optional[int] = Field(2, ge=1, le=10)
    show_menu_enabled: Optional[bool] = Field(True)
    show_menu_type: Optional[str] = Field("pavyon")
    engaging_messages: Optional[List[str]] = Field(default_factory=list)
    reply_messages: Optional[List[str]] = Field(default_factory=list)
    flirt_templates: Optional[List[str]] = Field(default_factory=list)
    services_menu: Optional[str] = Field("")
    papara_accounts: Optional[Dict[str, str]] = Field(default_factory=dict)
    papara_note: Optional[str] = Field("")
    personal_iban: Optional[PaymentInfo] = Field(None)
    safe_mode: Optional[bool] = Field(True)
    bot_config: Optional[BotConfig] = Field(default_factory=BotConfig)
    telegram_username: Optional[str] = Field(None)
    telegram_first_name: Optional[str] = Field(None)
    telegram_last_name: Optional[str] = Field(None)
    vip_price: Optional[str] = Field("250")

    @field_validator('username')
    def username_must_be_alphanumeric(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores allowed)')
        return v.lower()

class CharacterListResponse(BaseModel):
    """Response model for character list"""
    success: bool = True
    characters: List[Dict[str, Any]]
    count: int
    timestamp: str

class CharacterResponse(BaseModel):
    """Response model for single character"""
    success: bool = True
    character: Dict[str, Any]
    timestamp: str

class UpdateResponse(BaseModel):
    """Response model for character updates"""
    success: bool = True
    message: str
    character: Dict[str, Any]
    backup_created: bool
    timestamp: str

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: str

# Utility functions
async def read_character_file(username: str) -> Dict[str, Any]:
    """
    Async read character data from JSON file
    
    Args:
        username: Character username
        
    Returns:
        Character data dictionary
        
    Raises:
        FileNotFoundError: If character file doesn't exist
        JSONDecodeError: If file contains invalid JSON
    """
    file_path = PERSONAS_DIR / f"{username}.json"
    
    if not file_path.exists():
        raise FileNotFoundError(f"Character '{username}' not found")
    
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            data = json.loads(content)
            logger.info(f"📖 Successfully read character data for: {username}")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON decode error for {username}: {e}")
        raise ValueError(f"Invalid JSON in character file: {username}")
    except Exception as e:
        logger.error(f"❌ Error reading character file {username}: {e}")
        raise

async def write_character_file(username: str, data: Dict[str, Any], create_backup: bool = True) -> bool:
    """
    Async write character data to JSON file with backup
    
    Args:
        username: Character username
        data: Character data dictionary
        create_backup: Whether to create backup before overwriting
        
    Returns:
        True if successful
        
    Raises:
        Exception: If write operation fails
    """
    file_path = PERSONAS_DIR / f"{username}.json"
    
    # Create backup if file exists and backup is requested
    backup_created = False
    if create_backup and file_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"{username}_{timestamp}.json"
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as src:
                content = await src.read()
            async with aiofiles.open(backup_path, 'w', encoding='utf-8') as dst:
                await dst.write(content)
            backup_created = True
            logger.info(f"📦 Backup created: {backup_path}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create backup for {username}: {e}")
    
    # Write new data
    try:
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            json_content = json.dumps(data, indent=2, ensure_ascii=False)
            await f.write(json_content)
        
        logger.info(f"💾 Successfully wrote character data for: {username}")
        return backup_created
    except Exception as e:
        logger.error(f"❌ Error writing character file {username}: {e}")
        raise

async def get_all_character_files() -> List[str]:
    """
    Get list of all character usernames from personas directory
    
    Returns:
        List of character usernames (without .json extension)
    """
    try:
        files = []
        for file_path in PERSONAS_DIR.glob("*.json"):
            if not file_path.name.startswith('.') and not file_path.name.endswith('.banned'):
                username = file_path.stem
                files.append(username)
        
        logger.info(f"📋 Found {len(files)} character files")
        return sorted(files)
    except Exception as e:
        logger.error(f"❌ Error scanning character files: {e}")
        return []

# API Endpoints
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = datetime.now()
    
    # Log request
    logger.info(f"🔄 {request.method} {request.url.path} - Client: {request.client.host}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"✅ {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
    
    return response

@app.get("/", response_model=Dict[str, Any])
async def root():
    """API root endpoint with system information"""
    return {
        "message": "GavatCore Character API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "characters": "GET /characters - List all characters",
            "character_detail": "GET /characters/{username} - Get specific character",
            "character_update": "PUT /characters/{username} - Update character data"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "personas_dir": str(PERSONAS_DIR),
        "personas_exists": PERSONAS_DIR.exists(),
        "backup_dir": str(BACKUP_DIR),
        "backup_exists": BACKUP_DIR.exists()
    }

@app.get("/characters", response_model=CharacterListResponse)
async def get_all_characters():
    """
    Get all characters from data/personas/*.json files
    
    Returns:
        JSON response with list of all character data
    """
    try:
        logger.info("🔄 Getting all characters...")
        
        # Get all character files
        usernames = await get_all_character_files()
        
        if not usernames:
            logger.warning("⚠️ No character files found")
            return CharacterListResponse(
                characters=[],
                count=0,
                timestamp=datetime.now().isoformat()
            )
        
        # Read all character data
        characters = []
        for username in usernames:
            try:
                character_data = await read_character_file(username)
                characters.append(character_data)
            except Exception as e:
                logger.error(f"❌ Failed to read character {username}: {e}")
                # Continue with other characters instead of failing completely
                continue
        
        logger.info(f"✅ Successfully loaded {len(characters)} characters")
        
        return CharacterListResponse(
            characters=characters,
            count=len(characters),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Error in get_all_characters: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load characters: {str(e)}"
        )

@app.get("/characters/{username}", response_model=CharacterResponse)
async def get_character(username: str):
    """
    Get specific character data
    
    Args:
        username: Character username
        
    Returns:
        JSON response with character data
    """
    try:
        logger.info(f"🔄 Getting character: {username}")
        
        # Validate username
        username = username.lower().strip()
        if not username.replace('_', '').isalnum():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid username format"
            )
        
        # Read character data
        character_data = await read_character_file(username)
        
        logger.info(f"✅ Successfully retrieved character: {username}")
        
        return CharacterResponse(
            character=character_data,
            timestamp=datetime.now().isoformat()
        )
        
    except FileNotFoundError:
        logger.warning(f"⚠️ Character not found: {username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{username}' not found"
        )
    except ValueError as e:
        logger.error(f"❌ Invalid character data for {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error getting character {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve character: {str(e)}"
        )

@app.put("/characters/{username}", response_model=UpdateResponse)
async def update_character(username: str, character_data: Dict[str, Any]):
    """
    Update character data (overwrites entire JSON file)
    
    Args:
        username: Character username
        character_data: Complete character data to write
        
    Returns:
        JSON response with update confirmation
    """
    try:
        logger.info(f"🔄 Updating character: {username}")
        
        # Validate username
        username = username.lower().strip()
        if not username.replace('_', '').isalnum():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid username format"
            )
        
        # Ensure username consistency in data
        character_data['username'] = username
        
        # Validate character data structure (basic validation)
        try:
            # Parse with Pydantic for validation
            validated_data = CharacterData.parse_obj(character_data)
            # Convert back to dict for JSON storage
            character_data = validated_data.dict(exclude_unset=True)
        except Exception as e:
            logger.error(f"❌ Character data validation failed for {username}: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid character data: {str(e)}"
            )
        
        # Write character data with backup
        backup_created = await write_character_file(username, character_data, create_backup=True)
        
        logger.info(f"✅ Successfully updated character: {username} (backup: {backup_created})")
        
        return UpdateResponse(
            message=f"Character '{username}' updated successfully",
            character=character_data,
            backup_created=backup_created,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error updating character {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update character: {str(e)}"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"❌ Unhandled exception in {request.method} {request.url.path}: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            timestamp=datetime.now().isoformat()
        ).dict()
    )

if __name__ == "__main__":
    logger.info("🚀 Starting GavatCore Character API Server...")
    logger.info(f"📁 Personas directory: {PERSONAS_DIR.absolute()}")
    logger.info(f"📦 Backup directory: {BACKUP_DIR.absolute()}")
    logger.info("📡 API will be available at: http://localhost:8001")
    logger.info("📖 API documentation at: http://localhost:8001/docs")
    logger.info("🔄 CORS enabled for Flutter web integration")
    
    # Ensure directories exist
    if not PERSONAS_DIR.exists():
        logger.warning(f"⚠️ Creating personas directory: {PERSONAS_DIR}")
        PERSONAS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # Changed from 8000 to avoid conflicts
        reload=False,  # Set to True for development
        log_level="info",
        access_log=True
    ) 