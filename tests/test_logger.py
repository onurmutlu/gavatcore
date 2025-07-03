"""
Analytics Logger Test Module

Bu test modülü, character_analytics_logger'ın doğru çalıştığını kontrol eder.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from core.analytics_logger import log_character_event, alog_character_event

TEST_CHARACTER = "lara"
TEST_EVENT = "vip_sale"
TEST_METADATA = {
    "service": "özel_mesaj",
    "amount": 50,
    "user_id": 123
}

def test_sync_logging():
    """Senkron loglama fonksiyonunu test et."""
    # Log eventi oluştur
    log_character_event(TEST_CHARACTER, TEST_EVENT, TEST_METADATA)
    
    # Log dosyasını kontrol et
    log_file = Path("logs/characters") / f"{TEST_CHARACTER}_events.jsonl"
    assert log_file.exists(), "Log dosyası oluşturulmamış!"
    
    # Son log satırını oku
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        last_log = json.loads(lines[-1])
    
    # Log içeriğini doğrula
    assert last_log["character_id"] == TEST_CHARACTER, "Karakter ID yanlış!"
    assert last_log["event_type"] == TEST_EVENT, "Event tipi yanlış!"
    assert last_log["metadata"] == TEST_METADATA, "Metadata yanlış!"
    
    # Timestamp formatını kontrol et
    timestamp = datetime.fromisoformat(last_log["timestamp"])
    assert isinstance(timestamp, datetime), "Timestamp formatı yanlış!"

@pytest.mark.asyncio
async def test_async_logging():
    """Asenkron loglama fonksiyonunu test et."""
    # Async log eventi oluştur
    await alog_character_event(TEST_CHARACTER, TEST_EVENT, TEST_METADATA)
    
    # Log dosyasını kontrol et
    log_file = Path("logs/characters") / f"{TEST_CHARACTER}_events.jsonl"
    assert log_file.exists(), "Log dosyası oluşturulmamış!"
    
    # Son log satırını oku
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        last_log = json.loads(lines[-1])
    
    # Log içeriğini doğrula
    assert last_log["character_id"] == TEST_CHARACTER, "Karakter ID yanlış!"
    assert last_log["event_type"] == TEST_EVENT, "Event tipi yanlış!"
    assert last_log["metadata"] == TEST_METADATA, "Metadata yanlış!"
    
    # Timestamp formatını kontrol et
    timestamp = datetime.fromisoformat(last_log["timestamp"])
    assert isinstance(timestamp, datetime), "Timestamp formatı yanlış!"

def test_multiple_characters():
    """Birden fazla karakter için loglama test et."""
    characters = ["erko", "mcp", "gavat"]
    
    # Her karakter için log oluştur
    for char in characters:
        log_character_event(char, "message_sent", {"msg": "test"})
    
    # Her karakterin log dosyasını kontrol et
    for char in characters:
        log_file = Path("logs/characters") / f"{char}_events.jsonl"
        assert log_file.exists(), f"{char} için log dosyası oluşturulmamış!"
        
        with open(log_file, "r", encoding="utf-8") as f:
            last_log = json.loads(f.readlines()[-1])
            assert last_log["character_id"] == char, f"{char} için karakter ID yanlış!" 