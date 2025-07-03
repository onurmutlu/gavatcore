#!/usr/bin/env python3
"""
🔌 GAVATCore Universal Character API
===================================

FastAPI integration for Universal Character System providing:
- Character management endpoints
- Response generation API
- Reply mode control
- Performance monitoring
- Admin controls

Compatible with existing bot infrastructure and Flutter panels.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import structlog

# Import our universal character system
from gpt.universal_character_manager import (
    character_manager, ConversationContext, get_character_response
)

logger = structlog.get_logger("gavatcore.api.character")

# Pydantic models for API
class CharacterStatsResponse(BaseModel):
    """Character statistics response model."""
    character_id: str
    display_name: str
    username: str
    reply_mode: str
    gpt_enhanced: bool
    autospam: bool
    engaging_messages_count: int
    reply_messages_count: int
    style: str
    role: str
    age: str
    manualplus_timeout: int

class MessageRequest(BaseModel):
    """Message request model."""
    character_id: str = Field(..., description="Character ID to respond as")
    message: str = Field(..., description="User message")
    user_id: str = Field(..., description="User ID")
    username: str = Field(default="", description="Username")
    force_mode: Optional[str] = Field(None, description="Override reply mode")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")

class MessageResponse(BaseModel):
    """Message response model."""
    response: str
    character_id: str
    character_name: str
    reply_mode: str
    should_send: bool
    needs_approval: bool
    message_id: Optional[str] = None
    processing_time_ms: int
    metadata: Dict[str, Any]

class EngagingMessageRequest(BaseModel):
    """Engaging message request model."""
    character_id: str
    target_audience: str = Field(default="group", description="group or dm")
    time_context: str = Field(default="general", description="morning, evening, night, general")
    user_context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ReplyModeUpdateRequest(BaseModel):
    """Reply mode update request model."""
    character_id: str
    new_mode: str = Field(..., description="manual, gpt, hybrid, or manualplus")
    timeout_sec: Optional[int] = Field(None, description="For manualplus mode")

class HybridApprovalRequest(BaseModel):
    """Hybrid message approval request model."""
    message_id: str
    action: str = Field(..., description="approve, reject, or edit")
    edited_response: Optional[str] = Field(None, description="For edit action")
    reason: Optional[str] = Field(None, description="For reject action")

# Initialize FastAPI app
app = FastAPI(
    title="GAVATCore Universal Character API",
    description="Universal Character Management and Response Generation",
    version="1.0.0",
    docs_url="/api/characters/docs",
    redoc_url="/api/characters/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/characters", response_model=List[str])
async def list_characters():
    """List all available characters."""
    try:
        characters = character_manager.list_characters()
        logger.info(f"📋 Listed {len(characters)} characters")
        return characters
    except Exception as e:
        logger.error(f"❌ Error listing characters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/characters/{character_id}/stats", response_model=CharacterStatsResponse)
async def get_character_stats(character_id: str = Path(...)):
    """Get character statistics and information."""
    try:
        stats = character_manager.get_character_stats(character_id)
        if not stats:
            raise HTTPException(status_code=404, detail=f"Character {character_id} not found")
        
        return CharacterStatsResponse(**stats)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting character stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/characters/stats", response_model=Dict[str, CharacterStatsResponse])
async def get_all_character_stats():
    """Get statistics for all characters."""
    try:
        all_stats = character_manager.get_all_character_stats()
        return {
            char_id: CharacterStatsResponse(**stats)
            for char_id, stats in all_stats.items()
        }
    except Exception as e:
        logger.error(f"❌ Error getting all character stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/characters/message", response_model=MessageResponse)
async def generate_character_response(request: MessageRequest):
    """Generate character response to user message."""
    try:
        start_time = time.time()
        
        # Create conversation context
        context = ConversationContext(
            user_id=request.user_id,
            username=request.username,
            user_metadata=request.context.get("user_metadata", {}),
            message_history=request.context.get("message_history", []),
            sentiment_score=request.context.get("sentiment_score", 0.5),
            interaction_count=request.context.get("interaction_count", 0)
        )
        
        # Generate response
        response_text, metadata = await character_manager.generate_response(
            character_id=request.character_id,
            message=request.message,
            context=context,
            force_mode=request.force_mode
        )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Build response
        return MessageResponse(
            response=response_text,
            character_id=metadata.get("character_id", request.character_id),
            character_name=metadata.get("character_name", "Unknown"),
            reply_mode=metadata.get("reply_mode", "unknown"),
            should_send=metadata.get("should_send", False),
            needs_approval=metadata.get("needs_approval", False),
            message_id=metadata.get("message_id"),
            processing_time_ms=processing_time_ms,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"❌ Error generating response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/characters/{character_id}/engaging", response_model=MessageResponse)
async def get_engaging_message(
    character_id: str = Path(...),
    request: EngagingMessageRequest = Body(...)
):
    """Get engaging message from character."""
    try:
        start_time = time.time()
        
        # Create context if provided
        context = None
        if request.user_context:
            context = ConversationContext(
                user_id=request.user_context.get("user_id", "anonymous"),
                username=request.user_context.get("username", ""),
                sentiment_score=request.user_context.get("sentiment_score", 0.5)
            )
        
        # Get engaging message
        message_text, metadata = await character_manager.get_engaging_message(
            character_id=character_id,
            context=context
        )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return MessageResponse(
            response=message_text,
            character_id=character_id,
            character_name=metadata.get("character_name", "Unknown"),
            reply_mode="engaging",
            should_send=True,
            needs_approval=False,
            processing_time_ms=processing_time_ms,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting engaging message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/characters/{character_id}/reply", response_model=MessageResponse)
async def get_reply_message(character_id: str = Path(...)):
    """Get reply message from character."""
    try:
        start_time = time.time()
        
        # Get reply message
        message_text, metadata = await character_manager.get_reply_message(
            character_id=character_id
        )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return MessageResponse(
            response=message_text,
            character_id=character_id,
            character_name=metadata.get("character_name", "Unknown"),
            reply_mode="reply",
            should_send=True,
            needs_approval=False,
            processing_time_ms=processing_time_ms,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting reply message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/characters/{character_id}/mode")
async def update_reply_mode(
    character_id: str = Path(...),
    request: ReplyModeUpdateRequest = Body(...)
):
    """Update character reply mode."""
    try:
        character = character_manager.get_character(character_id)
        if not character:
            raise HTTPException(status_code=404, detail=f"Character {character_id} not found")
        
        # Validate mode
        valid_modes = ["manual", "gpt", "hybrid", "manualplus"]
        if request.new_mode not in valid_modes:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid mode. Must be one of: {', '.join(valid_modes)}"
            )
        
        # Update character (this would typically update the JSON file)
        character.reply_mode = request.new_mode
        if request.timeout_sec:
            character.manualplus_timeout_sec = request.timeout_sec
        
        logger.info(f"🔄 Updated {character_id} reply mode to {request.new_mode}")
        
        return {
            "success": True,
            "character_id": character_id,
            "new_mode": request.new_mode,
            "timeout_sec": character.manualplus_timeout_sec
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating reply mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/characters/pending")
async def get_pending_messages(character_id: Optional[str] = Query(None)):
    """Get pending hybrid messages."""
    try:
        pending_messages = character_manager.reply_mode_engine.get_pending_messages(character_id)
        
        return {
            "pending_count": len(pending_messages),
            "messages": [
                {
                    "message_id": msg.message_id,
                    "character_id": msg.character_id,
                    "user_id": msg.user_id,
                    "original_message": msg.original_message,
                    "generated_response": msg.generated_response,
                    "timestamp": msg.timestamp.isoformat(),
                    "status": msg.status,
                    "metadata": msg.metadata
                }
                for msg in pending_messages
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting pending messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/characters/hybrid/approve")
async def handle_hybrid_approval(request: HybridApprovalRequest):
    """Handle hybrid message approval, rejection, or editing."""
    try:
        if request.action == "approve":
            success = await character_manager.reply_mode_engine.approve_hybrid_message(
                request.message_id
            )
            
        elif request.action == "reject":
            success = await character_manager.reply_mode_engine.reject_hybrid_message(
                request.message_id, request.reason or ""
            )
            
        elif request.action == "edit":
            if not request.edited_response:
                raise HTTPException(status_code=400, detail="edited_response required for edit action")
            
            success = await character_manager.reply_mode_engine.edit_hybrid_message(
                request.message_id, request.edited_response
            )
            
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Must be approve, reject, or edit")
        
        if not success:
            raise HTTPException(status_code=404, detail="Message not found or already processed")
        
        return {
            "success": True,
            "message_id": request.message_id,
            "action": request.action
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error handling hybrid approval: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/characters/manual/reply")
async def provide_manual_reply(
    message_id: str = Body(..., embed=True),
    manual_response: str = Body(..., embed=True)
):
    """Provide manual reply for manualplus mode."""
    try:
        success = await character_manager.reply_mode_engine.provide_manual_reply(
            message_id, manual_response
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Message not found or timeout expired")
        
        return {
            "success": True,
            "message_id": message_id,
            "manual_response": manual_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error providing manual reply: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/characters/system/stats")
async def get_system_stats():
    """Get overall system statistics."""
    try:
        mode_stats = character_manager.reply_mode_engine.get_mode_statistics()
        character_count = len(character_manager.characters)
        
        return {
            "character_count": character_count,
            "reply_mode_stats": mode_stats,
            "system_health": "healthy",
            "uptime": "running",
            "characters": list(character_manager.characters.keys())
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/characters/reload")
async def reload_characters(character_id: Optional[str] = Query(None)):
    """Reload character(s) from JSON files."""
    try:
        if character_id:
            success = character_manager.reload_character(character_id)
            if not success:
                raise HTTPException(status_code=404, detail=f"Character {character_id} not found")
            
            return {
                "success": True,
                "action": "reload_character",
                "character_id": character_id
            }
        else:
            success = character_manager.reload_all_characters()
            return {
                "success": success,
                "action": "reload_all",
                "character_count": len(character_manager.characters)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error reloading characters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/characters/{character_id}/analysis")
async def get_character_analysis(character_id: str = Path(...)):
    """Get detailed character analysis including tone and behavior mapping."""
    try:
        character = character_manager.get_character(character_id)
        if not character:
            raise HTTPException(status_code=404, detail=f"Character {character_id} not found")
        
        # Get tone suggestions
        tone_suggestions = character_manager.tone_adapter.get_tone_suggestions(
            character.style, character.role
        )
        
        # Get behavior analysis
        behavior_analysis = character_manager.behavior_mapper.get_behavior_analysis(
            character.role
        )
        
        return {
            "character_id": character_id,
            "display_name": character.display_name,
            "persona": {
                "style": character.style,
                "role": character.role,
                "age": character.age,
                "gpt_prompt": character.gpt_prompt
            },
            "tone_analysis": tone_suggestions,
            "behavior_analysis": behavior_analysis,
            "config": {
                "reply_mode": character.reply_mode,
                "gpt_enhanced": character.gpt_enhanced,
                "autospam": character.autospam,
                "manualplus_timeout": character.manualplus_timeout_sec
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting character analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/characters/health")
async def health_check():
    """Health check endpoint."""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "characters_loaded": len(character_manager.characters),
            "system": "universal_character_api",
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Convenience function for external integration
async def get_character_response_api(
    character_id: str,
    message: str,
    user_id: str,
    username: str = "",
    force_mode: Optional[str] = None,
    **context_data
) -> Dict[str, Any]:
    """
    Convenience function for external API integration.
    
    Args:
        character_id: Character to respond as
        message: User message
        user_id: User ID
        username: Username
        force_mode: Override reply mode
        **context_data: Additional context data
    
    Returns:
        Response dictionary with message and metadata
    """
    try:
        request = MessageRequest(
            character_id=character_id,
            message=message,
            user_id=user_id,
            username=username,
            force_mode=force_mode,
            context=context_data
        )
        
        response = await generate_character_response(request)
        return response.dict()
        
    except Exception as e:
        logger.error(f"❌ Error in character response API: {e}")
        return {
            "error": str(e),
            "response": "Üzgünüm, şu anda bir sorun yaşıyorum. 😔",
            "should_send": False
        }

if __name__ == "__main__":
    import uvicorn
    
    print("🔌 Starting Universal Character API...")
    print("📊 API Documentation: http://localhost:8080/api/characters/docs")
    print("🎭 Characters loaded:", len(character_manager.characters))
    
    uvicorn.run(
        "api.universal_character_api:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    ) 