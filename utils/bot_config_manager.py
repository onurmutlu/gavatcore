#!/usr/bin/env python3
# utils/bot_config_manager.py

import json
from pathlib import Path
from typing import Dict, Any, Optional
from utils.log_utils import log_event

class BotConfigManager:
    def __init__(self):
        self.config_file = Path("data/bot_config.json")
        self.config_cache = None
        self.cache_timestamp = 0
        self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Konfigürasyon dosyasını yükle"""
        try:
            if self.config_file.exists():
                # Cache kontrolü - dosya değişti mi?
                current_timestamp = self.config_file.stat().st_mtime
                if self.config_cache and current_timestamp == self.cache_timestamp:
                    return self.config_cache
                
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config_cache = json.load(f)
                    self.cache_timestamp = current_timestamp
                    log_event("bot_config", f"✅ Bot konfigürasyonu yüklendi: {len(self.config_cache.get('bot_specific', {}))} bot")
                    return self.config_cache
            else:
                log_event("bot_config", "⚠️ Bot konfigürasyon dosyası bulunamadı, default ayarlar kullanılıyor")
                return self._get_default_config()
        except Exception as e:
            log_event("bot_config", f"❌ Konfigürasyon yükleme hatası: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default konfigürasyon"""
        return {
            "global_settings": {
                "dm_invite_enabled": True,
                "dm_invite_chance": 0.3,
                "target_group": "@arayisonlyvips",
                "spam_protection_enabled": True,
                "anti_spam_cooldown_base": 30,
                "anti_spam_cooldown_max": 300
            },
            "bot_specific": {},
            "default_bot_config": {
                "dm_invite_enabled": True,
                "spam_protection_enabled": True,
                "reply_mode": "manualplus",
                "auto_menu_enabled": True,
                "auto_menu_threshold": 3,
                "vip_price": "300",
                "special_restrictions": {}
            }
        }
    
    def get_bot_config(self, bot_username: str) -> Dict[str, Any]:
        """Belirli bir bot için konfigürasyon al - persona dosyasından da okur"""
        config = self._load_config()
        
        # Önce default ayarları al
        bot_config = config.get("default_bot_config", {}).copy()
        
        # Persona dosyasından ayarları yükle
        persona_config = self._load_persona_config(bot_username)
        if persona_config:
            bot_config.update(persona_config)
            log_event("bot_config", f"📄 {bot_username} persona dosyasından ayarlar yüklendi")
        
        # JSON konfigürasyondan özel ayarları al (öncelikli)
        if bot_username in config.get("bot_specific", {}):
            json_config = config["bot_specific"][bot_username].copy()
            bot_config.update(json_config)
            log_event("bot_config", f"🎯 {bot_username} için JSON konfigürasyon öncelikli")
        else:
            log_event("bot_config", f"📋 {bot_username} için persona + default konfigürasyon")
        
        # Global ayarları ekle
        global_settings = config.get("global_settings", {})
        bot_config.update({
            "global_" + key: value for key, value in global_settings.items()
        })
        
        return bot_config
    
    def _load_persona_config(self, bot_username: str) -> Optional[Dict[str, Any]]:
        """Persona dosyasından bot konfigürasyonunu yükle"""
        try:
            persona_file = Path(f"data/personas/{bot_username}.json")
            if not persona_file.exists():
                return None
            
            with open(persona_file, "r", encoding="utf-8") as f:
                persona_data = json.load(f)
            
            # Persona dosyasından bot konfigürasyon ayarlarını çıkar
            config = {}
            
            # Temel ayarlar
            if "reply_mode" in persona_data:
                config["reply_mode"] = persona_data["reply_mode"]
            
            if "manualplus_timeout_sec" in persona_data:
                config["manualplus_timeout_sec"] = persona_data["manualplus_timeout_sec"]
            
            if "auto_menu_enabled" in persona_data:
                config["auto_menu_enabled"] = persona_data["auto_menu_enabled"]
            
            if "auto_menu_threshold" in persona_data:
                config["auto_menu_threshold"] = persona_data["auto_menu_threshold"]
            
            if "vip_price" in persona_data:
                config["vip_price"] = persona_data["vip_price"]
            
            if "services_menu" in persona_data:
                config["services_menu"] = persona_data["services_menu"]
            
            if "papara_accounts" in persona_data:
                config["papara_accounts"] = persona_data["papara_accounts"]
            
            # Bot konfigürasyon bölümü varsa (yeni format)
            if "bot_config" in persona_data:
                bot_config_section = persona_data["bot_config"]
                config.update(bot_config_section)
            
            return config if config else None
            
        except Exception as e:
            log_event("bot_config", f"⚠️ {bot_username} persona dosyası okuma hatası: {e}")
            return None
    
    def is_dm_invite_enabled(self, bot_username: str) -> tuple[bool, str]:
        """Bot için DM davet aktif mi?"""
        config = self.get_bot_config(bot_username)
        
        # Global ayar kontrolü
        global_enabled = config.get("global_dm_invite_enabled", True)
        if not global_enabled:
            return False, "Global DM davet devre dışı"
        
        # Bot özel ayar kontrolü
        bot_enabled = config.get("dm_invite_enabled", True)
        if not bot_enabled:
            reason = config.get("dm_invite_reason", "Bot için DM davet devre dışı")
            return False, reason
        
        # Özel kısıtlamalar kontrolü
        restrictions = config.get("special_restrictions", {})
        if not restrictions.get("can_invite_users", True):
            return False, "Bot kullanıcı davet edemez"
        
        if not restrictions.get("can_send_dm", True):
            return False, "Bot DM gönderemez"
        
        return True, "DM davet aktif"
    
    def get_dm_invite_chance(self, bot_username: str) -> float:
        """Bot için DM davet şansı"""
        config = self.get_bot_config(bot_username)
        return config.get("global_dm_invite_chance", 0.3)
    
    def get_target_group(self, bot_username: str) -> str:
        """Hedef grup"""
        config = self.get_bot_config(bot_username)
        return config.get("global_target_group", "@arayisonlyvips")
    
    def is_spam_protection_enabled(self, bot_username: str) -> bool:
        """Spam koruması aktif mi?"""
        config = self.get_bot_config(bot_username)
        return config.get("spam_protection_enabled", True)
    
    def get_spam_protection_type(self, bot_username: str) -> str:
        """Spam koruması türü"""
        config = self.get_bot_config(bot_username)
        return config.get("spam_protection_type", "standard")
    
    def get_max_messages_per_minute(self, bot_username: str) -> int:
        """Dakikada maksimum mesaj sayısı"""
        config = self.get_bot_config(bot_username)
        return config.get("max_messages_per_minute", 3)
    
    def get_reply_mode(self, bot_username: str) -> str:
        """Yanıt modu"""
        config = self.get_bot_config(bot_username)
        return config.get("reply_mode", "manualplus")
    
    def get_auto_menu_settings(self, bot_username: str) -> tuple[bool, int]:
        """Otomatik menü ayarları"""
        config = self.get_bot_config(bot_username)
        enabled = config.get("auto_menu_enabled", True)
        threshold = config.get("auto_menu_threshold", 3)
        return enabled, threshold
    
    def get_vip_price(self, bot_username: str) -> str:
        """VIP fiyatı"""
        config = self.get_bot_config(bot_username)
        return config.get("vip_price", "300")
    
    def get_special_restrictions(self, bot_username: str) -> Dict[str, Any]:
        """Özel kısıtlamalar"""
        config = self.get_bot_config(bot_username)
        return config.get("special_restrictions", {})
    
    def is_group_invite_aggressive(self, bot_username: str) -> bool:
        """Agresif grup daveti aktif mi?"""
        config = self.get_bot_config(bot_username)
        return config.get("group_invite_aggressive", False)
    
    def get_group_invite_frequency(self, bot_username: str) -> str:
        """Grup daveti sıklığı"""
        config = self.get_bot_config(bot_username)
        return config.get("group_invite_frequency", "medium")
    
    def get_dm_invite_chance_enhanced(self, bot_username: str) -> float:
        """Bot özel DM davet şansı (bot_config'den)"""
        config = self.get_bot_config(bot_username)
        # Bot özel ayarı varsa onu kullan, yoksa global ayarı
        return config.get("dm_invite_chance", config.get("global_dm_invite_chance", 0.3))
    
    def update_bot_config(self, bot_username: str, updates: Dict[str, Any]):
        """Bot konfigürasyonunu güncelle"""
        try:
            config = self._load_config()
            
            if "bot_specific" not in config:
                config["bot_specific"] = {}
            
            if bot_username not in config["bot_specific"]:
                config["bot_specific"][bot_username] = config.get("default_bot_config", {}).copy()
            
            # Güncellemeleri uygula
            config["bot_specific"][bot_username].update(updates)
            
            # Dosyaya kaydet
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # Cache'i temizle
            self.config_cache = None
            
            log_event("bot_config", f"✅ {bot_username} konfigürasyonu güncellendi: {updates}")
            return True
            
        except Exception as e:
            log_event("bot_config", f"❌ Konfigürasyon güncelleme hatası: {e}")
            return False
    
    def get_all_bot_configs(self) -> Dict[str, Dict[str, Any]]:
        """Tüm bot konfigürasyonları"""
        config = self._load_config()
        return config.get("bot_specific", {})
    
    def reload_config(self):
        """Konfigürasyonu yeniden yükle"""
        self.config_cache = None
        self.cache_timestamp = 0
        self._load_config()
        log_event("bot_config", "🔄 Bot konfigürasyonu yeniden yüklendi")

# Global instance
bot_config_manager = BotConfigManager() 