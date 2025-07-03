#!/usr/bin/env python3
"""
⚡ Power Mode Controller API
===========================

System power mode management with real-time configuration.
Moved to port 7500 to avoid conflicts.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("power_mode_controller")

# Power Modes Configuration
POWER_MODES = {
    "normal": {
        "name": "Normal",
        "description": "Standart performans modu",
        "cpu_limit": 50,
        "memory_limit": 1024,
        "concurrent_requests": 10,
        "cache_ttl": 300,
        "ai_response_quality": "balanced",
        "features": ["basic_responses", "user_profiles"],
        "color": "#4CAF50"
    },
    "performance": {
        "name": "Performance",
        "description": "Gelişmiş performans ve özellikler",
        "cpu_limit": 75,
        "memory_limit": 2048,
        "concurrent_requests": 25,
        "cache_ttl": 600,
        "ai_response_quality": "high",
        "features": ["basic_responses", "user_profiles", "advanced_ai", "real_time_analytics"],
        "color": "#FF9800"
    },
    "turbo": {
        "name": "Turbo",
        "description": "Maksimum performans ve tüm özellikler",
        "cpu_limit": 90,
        "memory_limit": 4096,
        "concurrent_requests": 50,
        "cache_ttl": 900,
        "ai_response_quality": "premium",
        "features": ["basic_responses", "user_profiles", "advanced_ai", "real_time_analytics", "behavioral_insights", "voice_responses"],
        "color": "#F44336"
    },
    "extreme": {
        "name": "Extreme",
        "description": "Sınırsız performans - deneysel",
        "cpu_limit": 100,
        "memory_limit": 8192,
        "concurrent_requests": 100,
        "cache_ttl": 1800,
        "ai_response_quality": "ultra",
        "features": ["basic_responses", "user_profiles", "advanced_ai", "real_time_analytics", "behavioral_insights", "voice_responses", "predictive_ai", "auto_optimization"],
        "color": "#9C27B0"
    }
}

@dataclass
class PowerModeChange:
    timestamp: str
    old_mode: str
    new_mode: str
    user: str
    reason: Optional[str] = None

class PowerModeManager:
    def __init__(self):
        self.config_file = Path("config/power_mode.json")
        self.history_file = Path("logs/power_mode_history.json")
        self.current_mode = "turbo"  # Default mode
        self.mode_history: List[PowerModeChange] = []
        self.performance_metrics = {
            "requests_processed": 0,
            "average_response_time": 0.0,
            "cache_hit_rate": 0.0,
            "memory_usage": 0.0,
            "cpu_usage": 0.0,
            "last_updated": datetime.now().isoformat()
        }
        
        self._ensure_directories()
        self._load_config()
        logger.debug("📄 Config loaded", current_mode=self.current_mode)
    
    def _ensure_directories(self):
        """Create necessary directories."""
        self.config_file.parent.mkdir(exist_ok=True)
        self.history_file.parent.mkdir(exist_ok=True)
    
    def _load_config(self):
        """Load power mode configuration."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_mode = data.get('current_mode', 'turbo')
                    
                    # Load history
                    history_data = data.get('history', [])
                    self.mode_history = [
                        PowerModeChange(**item) for item in history_data
                    ]
        except Exception as e:
            logger.warning("⚠️ Config load error, using defaults", error=str(e))
    
    def _save_config(self):
        """Save current configuration."""
        try:
            config_data = {
                'current_mode': self.current_mode,
                'last_updated': datetime.now().isoformat(),
                'history': [asdict(change) for change in self.mode_history[-50:]]  # Keep last 50
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error("💾 Config save error", error=str(e))
    
    def change_mode(self, new_mode: str, user: str = "system", reason: str = None) -> bool:
        """Change power mode."""
        if new_mode not in POWER_MODES:
            return False
        
        old_mode = self.current_mode
        self.current_mode = new_mode
        
        # Add to history
        change = PowerModeChange(
            timestamp=datetime.now().isoformat(),
            old_mode=old_mode,
            new_mode=new_mode,
            user=user,
            reason=reason
        )
        self.mode_history.append(change)
        
        # Save config
        self._save_config()
        
        logger.info("⚡ Power mode changed", 
                   old_mode=old_mode, 
                   new_mode=new_mode, 
                   user=user)
        
        return True
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get current mode configuration."""
        mode_config = POWER_MODES[self.current_mode].copy()
        mode_config['current_mode'] = self.current_mode
        mode_config['performance_metrics'] = self.performance_metrics
        return mode_config
    
    def get_mode_info(self, mode: str) -> Optional[Dict[str, Any]]:
        """Get specific mode information."""
        return POWER_MODES.get(mode)
    
    def update_performance_metrics(self, metrics: Dict[str, Any]):
        """Update performance metrics."""
        self.performance_metrics.update(metrics)
        self.performance_metrics['last_updated'] = datetime.now().isoformat()

# Global power mode manager
power_manager = PowerModeManager()

# FastAPI app
app = FastAPI(
    title="GavatCore Power Mode Controller",
    description="⚡ System power mode management with real-time configuration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class PowerModeChangeRequest(BaseModel):
    user: str = "admin"
    reason: Optional[str] = None

class PerformanceMetricsUpdate(BaseModel):
    requests_processed: Optional[int] = None
    average_response_time: Optional[float] = None
    cache_hit_rate: Optional[float] = None
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None

# API Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "power_mode_controller",
        "status": "running",
        "current_mode": power_manager.current_mode,
        "available_modes": list(POWER_MODES.keys()),
        "port": 7500,  # Updated port
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "power_mode_controller",
        "current_mode": power_manager.current_mode,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/power/status")
async def get_power_status():
    """Get current power mode status."""
    try:
        config = power_manager.get_current_config()
        return {
            "success": True,
            "current_mode": power_manager.current_mode,
            "config": config,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("❌ Status error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/power/modes")
async def get_available_modes():
    """Get all available power modes."""
    return {
        "success": True,
        "modes": POWER_MODES,
        "current_mode": power_manager.current_mode,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/power/mode/{mode}")
async def change_power_mode(mode: str, request: PowerModeChangeRequest):
    """Change power mode."""
    try:
        if mode not in POWER_MODES:
            raise HTTPException(status_code=400, detail=f"Invalid mode: {mode}")
        
        success = power_manager.change_mode(mode, request.user, request.reason)
        
        if success:
            return {
                "success": True,
                "message": f"Power mode changed to {mode}",
                "old_mode": power_manager.mode_history[-1].old_mode if power_manager.mode_history else None,
                "new_mode": mode,
                "config": power_manager.get_current_config(),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to change mode")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ Mode change error", error=str(e), mode=mode)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/power/mode/{mode}/info")
async def get_mode_info(mode: str):
    """Get information about a specific mode."""
    mode_info = power_manager.get_mode_info(mode)
    
    if not mode_info:
        raise HTTPException(status_code=404, detail=f"Mode not found: {mode}")
    
    return {
        "success": True,
        "mode": mode,
        "info": mode_info,
        "is_current": mode == power_manager.current_mode,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/power/history")
async def get_mode_history():
    """Get power mode change history."""
    try:
        history = [asdict(change) for change in power_manager.mode_history[-20:]]  # Last 20 changes
        
        return {
            "success": True,
            "history": history,
            "total_changes": len(power_manager.mode_history),
            "current_mode": power_manager.current_mode,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("❌ History error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/power/performance")
async def get_performance_metrics():
    """Get current performance metrics."""
    try:
        return {
            "success": True,
            "metrics": power_manager.performance_metrics,
            "current_mode": power_manager.current_mode,
            "mode_config": POWER_MODES[power_manager.current_mode],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("❌ Performance metrics error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/power/performance")
async def update_performance_metrics(metrics: PerformanceMetricsUpdate):
    """Update performance metrics."""
    try:
        metrics_dict = metrics.dict(exclude_unset=True)
        power_manager.update_performance_metrics(metrics_dict)
        
        return {
            "success": True,
            "message": "Performance metrics updated",
            "updated_metrics": metrics_dict,
            "all_metrics": power_manager.performance_metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("❌ Metrics update error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

async def startup_event():
    """Startup tasks."""
    logger.info("⚡ Power Mode Manager initialized", current_mode=power_manager.current_mode)

app.add_event_handler("startup", startup_event)

if __name__ == "__main__":
    print("⚡ Starting Power Mode Controller...")
    print("==================================================")
    print("🚀 Features:")
    print("   • Power mode toggle (normal/performance/turbo/extreme)")
    print("   • Real-time performance adjustment")
    print("   • Configuration management")
    print("   • System impact monitoring")
    print("   • Flutter UI integration")
    print(f"🌐 API Base URL: http://localhost:7500")  # Updated port
    print(f"⚡ Power Status: http://localhost:7500/api/power/status")
    print(f"🎛️ Available Modes: http://localhost:7500/api/power/modes")
    print(f"📊 Performance: http://localhost:7500/api/power/performance")
    print("📋 Available Endpoints:")
    print("   • GET /api/power/status - Current power status")
    print("   • GET /api/power/modes - Available modes")
    print("   • POST /api/power/mode/{mode} - Change power mode")
    print("   • GET /api/power/mode/{mode}/info - Mode information")
    print("   • GET /api/power/history - Mode change history")
    print("   • GET /api/power/performance - Performance metrics")
    print("==================================================")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=7500,  # Updated port
        log_level="info"
    ) 