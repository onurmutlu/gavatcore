#!/usr/bin/env python3
# gpt/gpt_call.py - GPT API bağlantısı ve fallback sistemi

import asyncio
import random
import json
from typing import Optional, Dict, Any
from pathlib import Path
from utilities.log_utils import log_event
from config import OPENAI_API_KEY

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class GPTClient:
    def __init__(self):
        self.config = self._load_config()
        self.fallback_templates = self._load_fallback_templates()
        
        # OpenAI client setup
        if OPENAI_AVAILABLE and OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY
            self.openai_enabled = True
            log_event("gpt_client", "✅ OpenAI API key yüklendi")
        else:
            self.openai_enabled = False
            log_event("gpt_client", "⚠️ OpenAI API key bulunamadı, fallback mode aktif")
    
    def _load_config(self) -> Dict[str, Any]:
        """GPT konfigürasyonunu yükler"""
        try:
            config_path = Path("data/gpt_config.json")
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            log_event("gpt_client", f"❌ Config yükleme hatası: {e}")
        
        # Default config
        return {
            "model": "gpt-3.5-turbo",
            "temperature": 0.8,
            "max_tokens": 150,
            "top_p": 0.9,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.3,
            "timeout": 10
        }
    
    def _load_fallback_templates(self) -> Dict[str, list]:
        """Fallback şablonlarını yükler"""
        try:
            templates_path = Path("data/gpt_fallback_templates.json")
            if templates_path.exists():
                with open(templates_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            log_event("gpt_client", f"❌ Fallback templates yükleme hatası: {e}")
        
        # Default fallback templates
        return {
            "flirty": [
                "Selam canım! Nasılsın? 😘",
                "Bugün çok güzelsin! 💕",
                "Sohbet etmek ister misin? 😊",
                "Keyifler nasıl? 🌸",
                "Merhaba tatlım! 💋"
            ],
            "mention_reply": [
                "Evet canım, buradayım! 😊",
                "Beni çağırdın mı? 💕",
                "Söyle bakalım! 😘",
                "Dinliyorum seni! 🎧",
                "Ne var ne yok? 😉"
            ],
            "group_context": [
                "Harika sohbet! 🎉",
                "Çok eğlenceli! 😄",
                "Devam edelim! 💪",
                "Süper! 🌟",
                "Mükemmel! ✨"
            ]
        }
    
    async def gpt_call(self, prompt: str, message_type: str = "general") -> str:
        """
        GPT API çağrısı yapar, başarısız olursa fallback kullanır
        
        Args:
            prompt: GPT'ye gönderilecek prompt
            message_type: Mesaj tipi (flirty, mention_reply, group_context)
        
        Returns:
            Üretilen mesaj
        """
        
        # Önce GPT API'yi dene
        if self.openai_enabled:
            try:
                response = await self._call_openai_api(prompt)
                if response:
                    log_event("gpt_client", f"✅ GPT API başarılı: {len(response)} karakter")
                    return response
            except Exception as e:
                log_event("gpt_client", f"⚠️ GPT API hatası: {e}, fallback kullanılıyor")
        
        # Fallback: şablonlardan rastgele seç
        return self._get_fallback_message(message_type)
    
    async def _call_openai_api(self, prompt: str) -> Optional[str]:
        """OpenAI API çağrısı"""
        try:
            # Async timeout ile API çağrısı
            response = await asyncio.wait_for(
                self._make_openai_request(prompt),
                timeout=self.config.get("timeout", 10)
            )
            
            if response and response.choices:
                content = response.choices[0].message.content.strip()
                
                # İçerik kontrolü
                if len(content) > 10 and len(content) < 500:
                    return content
                else:
                    log_event("gpt_client", f"⚠️ GPT yanıtı uygun değil: {len(content)} karakter")
                    return None
            
        except asyncio.TimeoutError:
            log_event("gpt_client", "⏰ GPT API timeout")
        except Exception as e:
            log_event("gpt_client", f"❌ OpenAI API hatası: {e}")
        
        return None
    
    async def _make_openai_request(self, prompt: str):
        """Gerçek OpenAI API isteği"""
        return await openai.ChatCompletion.acreate(
            model=self.config.get("model", "gpt-3.5-turbo"),
            messages=[
                {
                    "role": "system", 
                    "content": "You are a flirty, playful Turkish woman chatting on Telegram. Keep responses short, natural and engaging. Use Turkish language and appropriate emojis."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=self.config.get("temperature", 0.8),
            max_tokens=self.config.get("max_tokens", 150),
            top_p=self.config.get("top_p", 0.9),
            frequency_penalty=self.config.get("frequency_penalty", 0.5),
            presence_penalty=self.config.get("presence_penalty", 0.3)
        )
    
    def _get_fallback_message(self, message_type: str) -> str:
        """Fallback şablonlarından rastgele mesaj seçer"""
        templates = self.fallback_templates.get(message_type, self.fallback_templates.get("flirty", []))
        
        if not templates:
            # Son çare default mesajlar
            default_messages = [
                "Merhaba! 😊",
                "Nasılsın? 💕",
                "Selam canım! 😘",
                "Keyifler nasıl? 🌸"
            ]
            return random.choice(default_messages)
        
        selected = random.choice(templates)
        log_event("gpt_client", f"🔄 Fallback mesaj kullanıldı: {message_type}")
        return selected
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """GPT konfigürasyonunu günceller"""
        try:
            self.config.update(new_config)
            
            # Config dosyasına kaydet
            config_path = Path("data/gpt_config.json")
            config_path.parent.mkdir(exist_ok=True)
            
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            log_event("gpt_client", "✅ GPT config güncellendi")
            return True
            
        except Exception as e:
            log_event("gpt_client", f"❌ Config güncelleme hatası: {e}")
            return False

# Global GPT client instance
gpt_client = GPTClient()

async def gpt_call(prompt: str, message_type: str = "general") -> str:
    """
    Global GPT çağrısı fonksiyonu
    
    Args:
        prompt: GPT'ye gönderilecek prompt
        message_type: Mesaj tipi (flirty, mention_reply, group_context)
    
    Returns:
        Üretilen mesaj
    """
    return await gpt_client.gpt_call(prompt, message_type) 