#!/usr/bin/env python3
"""
🎭 Character Manager - Karakter konfigürasyon yönetim sistemi
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
import logging
from pathlib import Path
import structlog

logger = structlog.get_logger("gavatcore.character_manager")

@dataclass
class CharacterConfig:
    """Karakter konfigürasyon veri modeli"""
    name: str
    username: str
    system_prompt: str
    reply_mode: str = "hybrid"  # manual / gpt / hybrid / manualplus
    tone: str = "flirty"  # flirty / soft / dark / mystic / aggressive
    cooldown_seconds: int = 45
    trust_index: float = 0.7
    fallback_strategy: str = "template_or_gpt"
    template_replies: List[str] = field(default_factory=list)
    personality_traits: Dict[str, Any] = field(default_factory=dict)
    gpt_settings: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Config'i dictionary'e çevir"""
        return {
            "name": self.name,
            "username": self.username,
            "system_prompt": self.system_prompt,
            "reply_mode": self.reply_mode,
            "tone": self.tone,
            "cooldown_seconds": self.cooldown_seconds,
            "trust_index": self.trust_index,
            "fallback_strategy": self.fallback_strategy,
            "template_replies": self.template_replies,
            "personality_traits": self.personality_traits,
            "gpt_settings": self.gpt_settings
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterConfig':
        """Dictionary'den CharacterConfig oluştur"""
        return cls(
            name=data.get("name", "Unknown"),
            username=data.get("username", "unknown"),
            system_prompt=data.get("system_prompt", ""),
            reply_mode=data.get("reply_mode", "hybrid"),
            tone=data.get("tone", "flirty"),
            cooldown_seconds=data.get("cooldown_seconds", 45),
            trust_index=data.get("trust_index", 0.7),
            fallback_strategy=data.get("fallback_strategy", "template_or_gpt"),
            template_replies=data.get("template_replies", []),
            personality_traits=data.get("personality_traits", {}),
            gpt_settings=data.get("gpt_settings", {})
        )

@dataclass
class Character:
    id: str
    name: str
    description: str
    personality: Dict[str, Any]
    created_at: str

class CharacterManager:
    """Karakter yönetim sistemi"""
    
    def __init__(self, config_dir: str = "character_engine/character_config"):
        self.config_dir = Path(config_dir)
        self.characters: Dict[str, CharacterConfig] = {}
        self.active_character: Optional[str] = None
        
        # Config dizinini oluştur
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Tüm karakterleri yükle
        self._load_all_characters()
        
        logger.info(f"🎭 CharacterManager başlatıldı - {len(self.characters)} karakter yüklendi")
    
    def _load_all_characters(self) -> None:
        """Tüm karakter config dosyalarını yükle"""
        for config_file in self.config_dir.glob("*.json"):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    username = config_file.stem
                    character = CharacterConfig.from_dict(data)
                    self.characters[username] = character
                    logger.info(f"✅ Karakter yüklendi: {username} ({character.name})")
            except Exception as e:
                logger.error(f"❌ Karakter yükleme hatası {config_file}: {e}")
    
    def load_character(self, username: str) -> Optional[CharacterConfig]:
        """Belirli bir karakteri yükle veya getir"""
        if username in self.characters:
            self.active_character = username
            return self.characters[username]
        
        # Config dosyasını kontrol et
        config_path = self.config_dir / f"{username}.json"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    character = CharacterConfig.from_dict(data)
                    self.characters[username] = character
                    self.active_character = username
                    logger.info(f"✅ Karakter yüklendi: {username}")
                    return character
            except Exception as e:
                logger.error(f"❌ Karakter yükleme hatası: {e}")
        
        return None
    
    def save_character(self, username: str, config: CharacterConfig) -> bool:
        """Karakter config'ini kaydet"""
        try:
            config_path = self.config_dir / f"{username}.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, ensure_ascii=False, indent=2)
            
            self.characters[username] = config
            logger.info(f"✅ Karakter kaydedildi: {username}")
            return True
        except Exception as e:
            logger.error(f"❌ Karakter kaydetme hatası: {e}")
            return False
    
    def get_active_character(self) -> Optional[CharacterConfig]:
        """Aktif karakteri getir"""
        if self.active_character and self.active_character in self.characters:
            return self.characters[self.active_character]
        return None
    
    def list_characters(self) -> List[str]:
        """Mevcut tüm karakterleri listele"""
        return list(self.characters.keys())
    
    def create_character(self, username: str, name: str, system_prompt: str, **kwargs) -> CharacterConfig:
        """Yeni karakter oluştur"""
        config = CharacterConfig(
            username=username,
            name=name,
            system_prompt=system_prompt,
            **kwargs
        )
        
        if self.save_character(username, config):
            return config
        else:
            raise Exception(f"Karakter oluşturulamadı: {username}")
    
    def update_character(self, username: str, **updates) -> bool:
        """Mevcut karakteri güncelle"""
        if username not in self.characters:
            logger.error(f"❌ Karakter bulunamadı: {username}")
            return False
        
        character = self.characters[username]
        
        # Güncellemeleri uygula
        for key, value in updates.items():
            if hasattr(character, key):
                setattr(character, key, value)
        
        return self.save_character(username, character)
    
    def delete_character(self, username: str) -> bool:
        """Karakteri sil"""
        try:
            config_path = self.config_dir / f"{username}.json"
            if config_path.exists():
                config_path.unlink()
            
            if username in self.characters:
                del self.characters[username]
            
            if self.active_character == username:
                self.active_character = None
            
            logger.info(f"🗑️ Karakter silindi: {username}")
            return True
        except Exception as e:
            logger.error(f"❌ Karakter silme hatası: {e}")
            return False
    
    def get_character_prompt(self, username: str) -> Optional[str]:
        """Karakterin system prompt'unu getir"""
        character = self.characters.get(username)
        return character.system_prompt if character else None
    
    def get_character_settings(self, username: str) -> Optional[Dict[str, Any]]:
        """Karakterin tüm ayarlarını getir"""
        character = self.characters.get(username)
        return character.to_dict() if character else None

# Global instance
character_manager = CharacterManager() 