from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn

app = FastAPI(title="GavatCore Character API", version="1.0.0")

# CORS middleware for Flutter web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
characters_data = {
    "lara": {
        "id": "lara",
        "name": "Lara",
        "mode": "gpt",
        "tone": "seductive",
        "system_prompt": "Sen çok çekici ve akıllı bir kadınsın. Her zaman flörtöz ve eğlenceli davranırsın. Mesajlarını çekici ve eğlenceli bir şekilde yazarsın.",
        "model": "gpt-4",
        "humanizer": True,
        "last_active": "2024-01-15T10:30:00Z",
        "stats": {"message_count": 1542, "is_active": True}
    },
    "babagavat": {
        "id": "babagavat", 
        "name": "Baba Gavat",
        "mode": "hybrid",
        "tone": "aggressive",
        "system_prompt": "Sen sert, direkt konuşan ve hiçbir şeyden çekinmeyen bir adamsın. Lafını gizlemez, açık konuşursun.",
        "model": "gpt-4o",
        "humanizer": False,
        "last_active": "2024-01-15T10:15:00Z",
        "stats": {"message_count": 892, "is_active": True}
    },
    "geisha": {
        "id": "geisha",
        "name": "Geisha",
        "mode": "gpt",
        "tone": "caring",
        "system_prompt": "Sen nazik, şefkatli ve anlayışlı bir kadınsın. Herkese saygı gösterir, yardımcı olmaya çalışırsın.",
        "model": "claude-sonnet",
        "humanizer": True,
        "last_active": "2024-01-15T08:30:00Z",
        "stats": {"message_count": 634, "is_active": False}
    },
    "balkiz": {
        "id": "balkiz",
        "name": "Bal Kız",
        "mode": "manual",
        "tone": "bubbly",
        "system_prompt": "Sen çok neşeli, enerjik ve pozitif bir kişisin. Her zaman gülümser ve mutlu görünürsün. Mesajlarına emoji eklersin.",
        "model": "gpt-3.5-turbo",
        "humanizer": True,
        "last_active": "2024-01-15T09:30:00Z", 
        "stats": {"message_count": 423, "is_active": True}
    },
    "mystic": {
        "id": "mystic",
        "name": "Mystic Oracle",
        "mode": "manualplus",
        "tone": "ironic",
        "system_prompt": "Sen gizemli, ironik ve derin düşüncelere sahip birisisin. Cevaplarını felsefi ve düşündürücü bir şekilde verirsin.",
        "model": "claude-opus",
        "humanizer": False,
        "last_active": "2024-01-14T10:30:00Z",
        "stats": {"message_count": 156, "is_active": False}
    }
}

class CharacterUpdate(BaseModel):
    mode: Optional[str] = None
    tone: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    humanizer: Optional[bool] = None

@app.get("/")
async def root():
    return {"message": "GavatCore Character API", "version": "1.0.0"}

@app.get("/characters")
async def get_characters():
    """Get all characters"""
    return {
        "success": True,
        "characters": list(characters_data.values())
    }

@app.get("/characters/{character_id}")
async def get_character(character_id: str):
    """Get a specific character"""
    if character_id not in characters_data:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return {
        "success": True,
        "character": characters_data[character_id]
    }

@app.put("/characters/{character_id}")
async def update_character(character_id: str, update: CharacterUpdate):
    """Update a character"""
    if character_id not in characters_data:
        raise HTTPException(status_code=404, detail="Character not found")
    
    character = characters_data[character_id]
    
    # Update fields if provided
    if update.mode is not None:
        character["mode"] = update.mode
    if update.tone is not None:
        character["tone"] = update.tone
    if update.system_prompt is not None:
        character["system_prompt"] = update.system_prompt
    if update.model is not None:
        character["model"] = update.model
    if update.humanizer is not None:
        character["humanizer"] = update.humanizer
    
    return {
        "success": True,
        "message": "Character updated successfully",
        "character": character
    }

@app.post("/characters/{character_id}/test")
async def test_character_reply(character_id: str, data: dict):
    """Test character reply"""
    if character_id not in characters_data:
        raise HTTPException(status_code=404, detail="Character not found")
    
    character = characters_data[character_id]
    message = data.get("message", "")
    
    # Mock reply based on character
    replies = {
        "lara": f"Merhaba tatlım 💋 Sen '{message}' diyorsun... Çok ilginç! 😊",
        "babagavat": f"Ne demek istiyorsun '{message}' diye? Düzgün konuş!",
        "geisha": f"Anlıyorum, '{message}' konusunda endişelisin. Sana yardım edebilirim 🌸",
        "balkiz": f"Vay be! '{message}' çok harika! 🎉✨ Ben de çok seviyorum!",
        "mystic": f"'{message}'... İlginç bir perspektif. Bunun altında yatan derin anlamı düşünmeliyiz..."
    }
    
    reply = replies.get(character_id, f"'{message}' hakkında ne düşüneyim acaba?")
    
    return {
        "success": True,
        "reply": reply,
        "character_id": character_id
    }

@app.get("/system/status")
async def system_status():
    """Get system status"""
    return {
        "success": True,
        "status": "running",
        "active_characters": sum(1 for c in characters_data.values() if c["stats"]["is_active"]),
        "total_characters": len(characters_data),
        "uptime": "2h 15m"
    }

if __name__ == "__main__":
    print("🚀 Starting GavatCore Character API Server...")
    print("📡 API will be available at: http://localhost:8000")
    print("📖 Docs will be available at: http://localhost:8000/docs")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True
    ) 