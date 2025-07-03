"""
Character Analytics Logger Module

Bu modül, karakter etkileşimlerini JSONL formatında kaydeder.
Async ve sync kullanımı destekler.
"""

import json
import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
import structlog

logger = structlog.get_logger("analytics")

class CharacterAnalyticsLogger:
    def __init__(self, log_dir: str = "logs/characters") -> None:
        """
        Analytics logger'ı başlat.
        
        Args:
            log_dir: Log dosyalarının tutulacağı dizin
        """
        self.log_dir = Path(log_dir)
        self._ensure_log_directory()
    
    def _ensure_log_directory(self) -> None:
        """Log dizinini oluştur."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_log_file(self, character_id: str) -> Path:
        """Karakter için log dosya yolunu döndür."""
        return self.log_dir / f"{character_id}_events.jsonl"
    
    def _create_event_data(self, 
                          character_id: str, 
                          event_type: str, 
                          metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Event verisi oluştur."""
        return {
            "character_id": character_id,
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

    def log_character_event(self, 
                          character_id: str, 
                          event_type: str, 
                          metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Karakter olayını senkron olarak logla.
        
        Args:
            character_id: Karakter ID'si
            event_type: Olay tipi (örn: "vip_sale", "message_sent")
            metadata: Olayla ilgili ek veriler
        """
        event_data = self._create_event_data(character_id, event_type, metadata)
        log_file = self._get_log_file(character_id)
        
        with open(log_file, "a", encoding="utf-8") as f:
            json.dump(event_data, f, ensure_ascii=False)
            f.write("\n")

    async def alog_character_event(self, 
                                 character_id: str, 
                                 event_type: str, 
                                 metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Karakter olayını asenkron olarak logla.
        
        Args:
            character_id: Karakter ID'si
            event_type: Olay tipi (örn: "vip_sale", "message_sent") 
            metadata: Olayla ilgili ek veriler
        """
        event_data = self._create_event_data(character_id, event_type, metadata)
        log_file = self._get_log_file(character_id)
        
        async def _write():
            with open(log_file, "a", encoding="utf-8") as f:
                json.dump(event_data, f, ensure_ascii=False)
                f.write("\n")
        
        await asyncio.get_event_loop().run_in_executor(None, _write)

# Global logger instance
_logger: Optional[CharacterAnalyticsLogger] = None

def get_logger(log_dir: str = "logs/characters") -> CharacterAnalyticsLogger:
    """Global logger instance'ı döndür."""
    global _logger
    if _logger is None:
        _logger = CharacterAnalyticsLogger(log_dir)
    return _logger

# Kolay kullanım için yardımcı fonksiyonlar
def log_character_event(character_id: str, 
                       event_type: str, 
                       metadata: Optional[Dict[str, Any]] = None) -> None:
    """Karakter olayını senkron olarak logla."""
    get_logger().log_character_event(character_id, event_type, metadata)

async def alog_character_event(character_id: str, 
                             event_type: str, 
                             metadata: Optional[Dict[str, Any]] = None) -> None:
    """Karakter olayını asenkron olarak logla."""
    await get_logger().alog_character_event(character_id, event_type, metadata)

async def log_analytics(event_type: str, data: Dict[str, Any]) -> None:
    """Analitik olayları logla"""
    try:
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        logger.info("analytics_event", **log_data)
        
    except Exception as e:
        logger.error("analytics_log_error", error=str(e))
        raise

# Singleton instance
analytics_logger = logger

