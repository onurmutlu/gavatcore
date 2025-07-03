#!/usr/bin/env python3
"""
Flutter Admin Panel Backend Endpoints
=====================================

GavatCore Flutter Admin Panel için gerekli tüm API endpoint'leri
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import random
import os

app = FastAPI(title="GavatCore Flutter API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data storage
characters_data = {
    "lara": {
        "name": "Lara",
        "system_prompt": "Sen Lara, yarı Rus kökenli baştan çıkarıcı bir karaktersin.",
        "reply_mode": "hybrid",
        "tone": "flirty",
        "gpt_model": "gpt-4",
        "humanizer_enabled": True,
        "humanizer_settings": {
            "typing_speed": 25,
            "emoji_usage_rate": 0.4,
            "mistake_chance": 0.03,
            "voice_addition_rate": 0.2,
            "silence_chance": 0.05,
            "response_delay_range": [0.5, 2.5],
            "multi_message_chance": 0.25
        },
        "is_active": True,
        "message_count": 1250,
        "last_activity": datetime.now().isoformat()
    },
    "babagavat": {
        "name": "BabaGavat",
        "system_prompt": "Sen BabaGavat, sokak dilini kullanan sert mizaçlı bir karakter.",
        "reply_mode": "hybrid",
        "tone": "aggressive",
        "gpt_model": "gpt-4",
        "humanizer_enabled": True,
        "humanizer_settings": {
            "typing_speed": 15,
            "emoji_usage_rate": 0.1,
            "mistake_chance": 0.08,
            "voice_addition_rate": 0.3,
            "silence_chance": 0.15,
            "response_delay_range": [2.0, 6.0],
            "multi_message_chance": 0.1
        },
        "is_active": True,
        "message_count": 980,
        "last_activity": datetime.now().isoformat()
    },
    "geisha": {
        "name": "Geisha",
        "system_prompt": "Sen Geisha, mistik ve ruhsal bir karakter.",
        "reply_mode": "gpt",
        "tone": "mystic",
        "gpt_model": "gpt-4-turbo-preview",
        "humanizer_enabled": True,
        "humanizer_settings": {
            "typing_speed": 18,
            "emoji_usage_rate": 0.35,
            "mistake_chance": 0.02,
            "voice_addition_rate": 0.1,
            "silence_chance": 0.2,
            "response_delay_range": [1.5, 4.5],
            "multi_message_chance": 0.15
        },
        "is_active": False,
        "message_count": 750,
        "last_activity": (datetime.now() - timedelta(hours=2)).isoformat()
    }
}

# Request models
class CharacterUpdateRequest(BaseModel):
    mode: Optional[str] = None
    tone: Optional[str] = None
    system_prompt: Optional[str] = None
    humanizer_enabled: Optional[bool] = None
    gpt_model: Optional[str] = None

class TestReplyRequest(BaseModel):
    message: str
    user_id: Optional[str] = "test_user"

class ShowcuCreateRequest(BaseModel):
    name: str
    papara_iban: str
    character: str
    tone: str
    custom_prompt: Optional[Dict[str, Any]] = None

# Character endpoints
@app.get("/api/characters")
async def get_characters():
    """Get list of available characters"""
    return {
        "success": True,
        "characters": list(characters_data.keys())
    }

@app.get("/api/characters/{character_id}/stats")
async def get_character_stats(character_id: str):
    """Get character statistics"""
    if character_id not in characters_data:
        raise HTTPException(status_code=404, detail="Character not found")
    
    char = characters_data[character_id]
    return {
        "success": True,
        "is_active": char["is_active"],
        "message_count": char["message_count"],
        "last_activity": char["last_activity"],
        "performance_score": random.randint(70, 95)
    }

@app.get("/api/characters/stats")
async def get_all_character_stats():
    """Get stats for all characters"""
    stats = {}
    for char_id, char_data in characters_data.items():
        stats[char_id] = {
            "is_active": char_data["is_active"],
            "message_count": char_data["message_count"],
            "last_activity": char_data["last_activity"],
            "performance_score": random.randint(70, 95)
        }
    return stats

@app.post("/api/characters/{character_id}/mode")
async def update_character_mode(character_id: str, request: dict):
    """Update character mode"""
    if character_id not in characters_data:
        raise HTTPException(status_code=404, detail="Character not found")
    
    characters_data[character_id]["reply_mode"] = request.get("mode", "hybrid")
    return {"success": True, "message": "Mode updated"}

@app.post("/api/characters/{character_id}/reply")
async def test_character_reply(character_id: str, request: TestReplyRequest):
    """Test character reply"""
    if character_id not in characters_data:
        raise HTTPException(status_code=404, detail="Character not found")
    
    char = characters_data[character_id]
    
    # Simulate different replies based on tone
    replies = {
        "flirty": [
            "Canım benim, ne tatlı soruyorsun öyle 💋",
            "Seninle konuşmak beni mutlu ediyor 😊",
            "Bu kadar güzel konuşma, başım dönüyor 💕"
        ],
        "aggressive": [
            "Ne diyon lan sen?",
            "Bak güzel konuş benimle",
            "Fazla uzatma moruk"
        ],
        "mystic": [
            "Evrenin sana bir mesajı var... 🌙",
            "Ruhun bana çok şey anlatıyor ✨",
            "Bu bir tesadüf değil, kader... 🔮"
        ]
    }
    
    tone = char.get("tone", "flirty")
    reply = random.choice(replies.get(tone, ["Merhaba!"]))
    
    return {
        "success": True,
        "reply": reply,
        "character": character_id,
        "mode": char["reply_mode"]
    }

@app.get("/api/characters/{character_id}/config")
async def get_character_config(character_id: str):
    """Get character configuration"""
    if character_id not in characters_data:
        return {
            "success": False,
            "error": "Character not found"
        }
    
    return {
        "success": True,
        "config": characters_data[character_id]
    }

@app.post("/api/characters/{character_id}/update_prompt")
async def update_character_prompt(character_id: str, request: dict):
    """Update character system prompt"""
    if character_id not in characters_data:
        raise HTTPException(status_code=404, detail="Character not found")
    
    characters_data[character_id]["system_prompt"] = request.get("system_prompt", "")
    return {"success": True, "message": "Prompt updated"}

@app.post("/api/characters/{character_id}/set_tone")
async def set_character_tone(character_id: str, request: dict):
    """Set character tone"""
    if character_id not in characters_data:
        raise HTTPException(status_code=404, detail="Character not found")
    
    characters_data[character_id]["tone"] = request.get("tone", "flirty")
    return {"success": True, "message": "Tone updated"}

# Dashboard endpoints
@app.get("/api/admin/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    return {
        "success": True,
        "total_users": random.randint(150, 200),
        "active_sessions": random.randint(20, 40),
        "messages_today": random.randint(500, 1000),
        "vip_candidates": random.randint(5, 15),
        "user_trend": random.uniform(-5, 15),
        "message_trend": random.uniform(-10, 20),
        "revenue_today": random.uniform(100, 500),
        "conversion_rate": random.uniform(2, 8)
    }

# Token stats endpoint
@app.get("/api/token-stats")
async def get_token_stats():
    """Get token usage statistics"""
    return {
        "success": True,
        "total_tokens": 125000,
        "total_cost": 2.5,
        "today_tokens": 5000,
        "today_cost": 0.1,
        "by_model": {
            "gpt-4": {"tokens": 80000, "cost": 2.0},
            "gpt-3.5-turbo": {"tokens": 45000, "cost": 0.5}
        },
        "by_character": {
            "lara": {"tokens": 50000, "cost": 1.0},
            "babagavat": {"tokens": 40000, "cost": 0.8},
            "geisha": {"tokens": 35000, "cost": 0.7}
        }
    }

# Behavioral endpoints
@app.get("/api/behavioral/profile/{user_id}")
async def get_user_behavior(user_id: str):
    """Get user behavioral profile"""
    return {
        "success": True,
        "profile": {
            "user_id": user_id,
            "username": f"User_{user_id[:8]}",
            "trust_index": random.uniform(0.3, 0.9),
            "vip_probability": random.uniform(0.1, 0.95),
            "message_count": random.randint(10, 500),
            "emotional_profile": {
                "happy": random.uniform(0, 1),
                "love": random.uniform(0, 1),
                "neutral": random.uniform(0, 1),
                "sad": random.uniform(0, 1),
                "angry": random.uniform(0, 1)
            },
            "message_history": [
                {
                    "message": "Merhaba nasılsın?",
                    "timestamp": datetime.now().isoformat(),
                    "is_bot": False,
                    "emotion": "neutral"
                }
            ],
            "suggested_strategy": {
                "recommendation": "Bu kullanıcı yüksek güven gösteriyor, samimi yaklaşım önerilir.",
                "tone": "flirty",
                "approach": "engaged",
                "reply_mode": "hybrid"
            },
            "last_activity": datetime.now().isoformat(),
            "manipulation_resistance": random.uniform(0.2, 0.8),
            "silence_threshold": random.uniform(0.1, 0.5)
        }
    }

@app.get("/api/behavioral/users/high-risk")
async def get_high_risk_users():
    """Get high risk users"""
    users = []
    for i in range(10):
        users.append({
            "user_id": f"user_{i}",
            "username": f"RiskUser{i}",
            "trust_index": random.uniform(0.1, 0.4),
            "vip_probability": random.uniform(0.6, 0.95),
            "message_count": random.randint(50, 200),
            "emotional_profile": {},
            "message_history": [],
            "suggested_strategy": {},
            "last_activity": datetime.now().isoformat(),
            "manipulation_resistance": random.uniform(0.5, 0.9),
            "silence_threshold": random.uniform(0.3, 0.7)
        })
    
    return {
        "success": True,
        "users": users
    }

@app.get("/api/behavioral/insights/summary")
async def get_behavioral_insights():
    """Get behavioral insights summary"""
    return {
        "success": True,
        "total_users": 187,
        "avg_trust_index": 0.65,
        "high_vip_potential": 23,
        "low_trust_users": 12,
        "active_conversations": 42
    }

# Campaign stats
@app.get("/api/campaign/stats")
async def get_campaign_stats():
    """Get campaign statistics"""
    return {
        "success": True,
        "is_active": True,
        "total_targets": 500,
        "reached_targets": 350,
        "success_rate": 70,
        "remaining_time": "2d 14h",
        "campaign_name": "VIP Kazanım Kampanyası"
    }

# Showcu endpoints
@app.post("/api/showcu/create")
async def create_showcu(request: ShowcuCreateRequest):
    """Create new showcu"""
    return {
        "success": True,
        "showcu_id": f"showcu_{random.randint(1000, 9999)}",
        "message": "Showcu başarıyla oluşturuldu"
    }

# Health check
@app.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 