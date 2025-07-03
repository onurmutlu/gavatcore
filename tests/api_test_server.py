#!/usr/bin/env python3
"""
🔥 Flutter Panel API Test Server 🔥

FastAPI backend for Flutter connection testing.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

app = FastAPI(
    title="GavatCore API Test Server",
    description="Flutter panel bağlantı testi için basit FastAPI server",
    version="1.0.0"
)

# CORS middleware - Flutter'dan bağlantı için gerekli
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da daha kısıtlayıcı olmalı
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Ana endpoint"""
    return {
        "message": "🔥 GavatCore API Test Server",
        "status": "active",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint - Flutter test için"""
    return {
        "status": "healthy",
        "message": "✅ FastAPI backend çalışıyor!",
        "timestamp": datetime.now().isoformat(),
        "service": "GavatCore API Test Server",
        "version": "1.0.0",
        "uptime": "active"
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "test": True,
        "message": "🎯 Test endpoint başarılı!",
        "data": {
            "flutter_connection": "OK",
            "backend_status": "running",
            "api_version": "1.0.0"
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 FastAPI Test Server başlatılıyor...")
    print("📱 Flutter'dan test etmek için: http://localhost:8000/health")
    print("🌐 Swagger UI: http://localhost:8000/docs")
    print("⚡ ReDoc: http://localhost:8000/redoc")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 