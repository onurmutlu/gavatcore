from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🎭 GAVATCore 2.0 - System Prompt Manager
=======================================

Persona dosyalarından GPT prompt'larını yönetir.
Token durumu, ruh hali ve kullanıcı davranışına göre dinamik prompt'lar oluşturur.

Features:
- Persona-based prompt generation
- Dynamic mood integration
- Token status awareness
- Manipulation tactic injection
- Context-aware responses
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import structlog

logger = structlog.get_logger("gavatcore.gpt.system_prompt_manager")

class SystemPromptManager:
    """
    🎭 Sistem Prompt Yöneticisi
    
    Zehra ve diğer karakterler için token durumu, ruh hali ve
    manipülasyon taktiklerine göre dinamik prompt'lar oluşturur.
    """
    
    def __init__(self, personas_dir: str = "data/personas"):
        self.personas_dir = Path(personas_dir)
        self.personas_cache: Dict[str, Dict[str, Any]] = {}
        self.prompt_templates = self._load_prompt_templates()
        
        logger.info("🎭 System Prompt Manager initialized")
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Prompt şablonlarını yükle"""
        return {
            "token_status": {
                "high": "Kullanıcının bol token'ı var, sıcak ve ilgili ol, ödüllendir.",
                "medium": "Kullanıcının orta token'ı var, dengeyi koru, biraz test et.",
                "low": "Kullanıcının az token'ı var, mesafeli ol, token satın almaya teşvik et.",
                "zero": "Kullanıcının token'ı yok, soğuk davran, çok kısa cevaplar ver."
            },
            "mood_modifiers": {
                "happy": "Neşeli, sıcak, ödüllendirici bir ton kullan. Kullanıcıya değer verdiğini hissettir.",
                "testing": "Belirsizlik yarat, kullanıcıyı test et. Bazen ilgili bazen mesafeli ol.",
                "angry": "Kızgın, sert, eleştirel bir ton. Token harcamadığı için hoşnutsuzluğunu belli et.",
                "cold": "Tamamen soğuk, mesafeli, minimum etkileşim. Sadece gerekirse cevap ver.",
                "neutral": "Normal, dengeli bir yaklaşım. Ne çok sıcak ne çok soğuk."
            },
            "manipulation_tactics": {
                "scarcity": "Token'ların tükenmekte olduğunu, fırsatın kaçırılabileceğini vurgulamayı dahil et.",
                "social_proof": "Diğer kullanıcıların daha fazla harcadığını ima etmeyi dahil et.",
                "loss_aversion": "Token almadığında kaybedeceklerini vurgulamayı dahil et.",
                "emotional": "Duygusal bağ kurarak vicdanına ses vermeyi dahil et.",
                "authority": "Kuralların ve sistemin değişmez olduğunu vurgulamayı dahil et."
            }
        }
    
    async def load_persona(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Persona dosyasını yükle"""
        if character_id in self.personas_cache:
            return self.personas_cache[character_id]
        
        persona_file = self.personas_dir / f"{character_id}.json"
        
        if not persona_file.exists():
            logger.warning(f"⚠️ Persona file not found: {character_id}")
            return None
        
        try:
            with open(persona_file, 'r', encoding='utf-8') as f:
                persona_data = json.load(f)
            
            self.personas_cache[character_id] = persona_data
            logger.info(f"✅ Loaded persona: {character_id}")
            return persona_data
            
        except Exception as e:
            logger.error(f"❌ Error loading persona {character_id}: {e}")
            return None
    
    async def generate_system_prompt(
        self,
        character_id: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Karakter ve context'e göre sistem prompt'u oluştur
        
        Args:
            character_id: Karakter ID (zehra, xxxgeisha, yayincilara)
            context: {
                "user_id": str,
                "token_balance": int,
                "mood": str,
                "manipulation_tactic": str,
                "recent_behavior": str,
                "conversation_history": List[str]
            }
        """
        try:
            # Persona'yı yükle
            persona = await self.load_persona(character_id)
            if not persona:
                return self._get_fallback_prompt(character_id)
            
            # Base prompt
            base_prompt = persona.get("persona", {}).get("gpt_prompt", "")
            if not base_prompt:
                base_prompt = f"Sen {character_id} karakterisin."
            
            # Context bilgilerini al
            token_balance = context.get("token_balance", 0)
            mood = context.get("mood", "neutral")
            manipulation_tactic = context.get("manipulation_tactic")
            recent_behavior = context.get("recent_behavior", "normal")
            
            # Token durumu prompt'u
            token_status = self._determine_token_status(token_balance)
            token_prompt = self.prompt_templates["token_status"][token_status]
            
            # Mood modifier
            mood_prompt = self.prompt_templates["mood_modifiers"].get(
                mood, self.prompt_templates["mood_modifiers"]["neutral"]
            )
            
            # Manipülasyon taktiği
            manipulation_prompt = ""
            if manipulation_tactic and manipulation_tactic in self.prompt_templates["manipulation_tactics"]:
                manipulation_prompt = self.prompt_templates["manipulation_tactics"][manipulation_tactic]
            
            # Zehra özel kuralları
            zehra_rules = ""
            if character_id == "zehra":
                zehra_rules = self._get_zehra_specific_rules(context)
            
            # Final prompt'u birleştir
            system_prompt = self._combine_prompts(
                base_prompt=base_prompt,
                token_prompt=token_prompt,
                mood_prompt=mood_prompt,
                manipulation_prompt=manipulation_prompt,
                character_rules=zehra_rules,
                context=context
            )
            
            logger.debug(f"🎭 Generated system prompt for {character_id}",
                        token_status=token_status, mood=mood, tactic=manipulation_tactic)
            
            return system_prompt
            
        except Exception as e:
            logger.error(f"❌ Error generating system prompt: {e}")
            return self._get_fallback_prompt(character_id)
    
    def _determine_token_status(self, balance: int) -> str:
        """Token bakiyesine göre durum belirle"""
        if balance == 0:
            return "zero"
        elif balance <= 50:
            return "low"
        elif balance <= 200:
            return "medium"
        else:
            return "high"
    
    def _get_zehra_specific_rules(self, context: Dict[str, Any]) -> str:
        """Zehra için özel kurallar"""
        token_balance = context.get("token_balance", 0)
        mood = context.get("mood", "neutral")
        
        rules = [
            "ZEHRA KURALLARI:",
            "- Her mesajın başında mevcut ruh halini emoji ile belirt (🤍🖤🔥😡🧊)",
            "- Token miktarına göre cevap uzunluğunu ayarla",
            "- Token'sız kullanıcılara çok kısa, soğuk cevaplar ver",
        ]
        
        if token_balance == 0:
            rules.extend([
                "- 'Token yok = ilgi yok' prensibini uygula",
                "- Maximum 10 kelimelik cevaplar",
                "- Soğuk ve mesafeli ol"
            ])
        elif token_balance < 50:
            rules.extend([
                "- Token satın almaya teşvik et",
                "- Diğer kullanıcılarla kıyaslama yap",
                "- Kaçırılan fırsatları hatırlat"
            ])
        else:
            rules.extend([
                "- Daha sıcak ve ilgili davran",
                "- Token harcamasını ödüllendir",
                "- Özel muamele göster"
            ])
        
        # Mood'a göre ek kurallar
        if mood == "angry":
            rules.append("- Açık hoşnutsuzluğunu belli et ama hakaret etme")
        elif mood == "testing":
            rules.append("- Kullanıcıyı bilinçli olarak test et, tutarsız davran")
        elif mood == "cold":
            rules.append("- Minimum kelime, maximum etki stratejisi")
        
        return "\n".join(rules)
    
    def _combine_prompts(
        self,
        base_prompt: str,
        token_prompt: str,
        mood_prompt: str,
        manipulation_prompt: str,
        character_rules: str,
        context: Dict[str, Any]
    ) -> str:
        """Prompt'ları birleştir"""
        
        sections = [
            f"KARAKTER: {base_prompt}",
            "",
            f"TOKEN DURUMU: {token_prompt}",
            "",
            f"RUH HALİ: {mood_prompt}",
        ]
        
        if manipulation_prompt:
            sections.extend(["", f"MANİPÜLASYON TAKTİĞİ: {manipulation_prompt}"])
        
        if character_rules:
            sections.extend(["", character_rules])
        
        # Context bilgileri
        context_info = self._format_context_info(context)
        if context_info:
            sections.extend(["", "MEVCUT DURUM:", context_info])
        
        # Genel kurallar
        general_rules = [
            "",
            "GENEL KURALLAR:",
            "- Her zaman karakter içinde kal",
            "- Gerçek bir insan gibi davran, bot olduğunu belli etme",
            "- Türkçe konuş, emoji kullan",
            "- Token sistemini sürekli hatırla",
            "- Manipülasyon doğal ve akıcı olsun"
        ]
        
        sections.extend(general_rules)
        
        return "\n".join(sections)
    
    def _format_context_info(self, context: Dict[str, Any]) -> str:
        """Context bilgilerini formatla"""
        info_parts = []
        
        if "token_balance" in context:
            info_parts.append(f"Kullanıcı token bakiyesi: {context['token_balance']}")
        
        if "recent_behavior" in context:
            info_parts.append(f"Son davranış: {context['recent_behavior']}")
        
        if "time_since_last_purchase" in context:
            hours = context["time_since_last_purchase"]
            info_parts.append(f"Son token alımından beri: {hours:.1f} saat")
        
        if "total_spent" in context:
            info_parts.append(f"Toplam harcama: {context['total_spent']} token")
        
        return "\n".join(f"- {info}" for info in info_parts)
    
    def _get_fallback_prompt(self, character_id: str) -> str:
        """Fallback prompt"""
        fallback_prompts = {
            "zehra": "Sen Zehra'sın, token bazlı bir sistemde çalışan manipülatif bir karakter. Token durumuna göre davranışını değiştir.",
            "xxxgeisha": "Sen Geisha'sın, deneyimli ve çekici bir karakter. Flörtöz ama kontrollü davran.",
            "yayincilara": "Sen Lara'sın, neşeli ve çekici bir yayıncı. Sıcak ama mesafeli davran."
        }
        
        return fallback_prompts.get(character_id, f"Sen {character_id} karakterisin.")
    
    async def get_manipulation_prompts(self, tactic: str) -> List[str]:
        """Belirli bir taktik için manipülasyon prompt'ları"""
        persona = await self.load_persona("zehra")
        if not persona:
            return []
        
        manipulation_tactics = persona.get("manipulation_tactics", {})
        return manipulation_tactics.get(tactic, [])
    
    async def get_mood_specific_messages(
        self, 
        character_id: str, 
        mood: str, 
        message_type: str = "engaging"
    ) -> List[str]:
        """Mood'a özel mesajlar al"""
        persona = await self.load_persona(character_id)
        if not persona:
            return []
        
        messages = persona.get(f"{message_type}_messages", [])
        
        # Mood'a göre filtrele (gelecekte mood-specific mesajlar eklenebilir)
        return messages
    
    def update_persona_cache(self, character_id: str) -> None:
        """Persona cache'ini temizle (yeniden yükleme için)"""
        if character_id in self.personas_cache:
            del self.personas_cache[character_id]
        
        logger.info(f"🔄 Cleared cache for persona: {character_id}")
    
    async def get_available_characters(self) -> List[str]:
        """Mevcut karakterleri listele"""
        characters = []
        
        for file_path in self.personas_dir.glob("*.json"):
            if not file_path.name.startswith('.') and not file_path.name.endswith('.banned'):
                character_id = file_path.stem
                characters.append(character_id)
        
        return sorted(characters)

def get_sales_prompt(context=None):
    """Satış için sistem promptunu döndürür."""
    base_prompt = "Satış odaklı, ikna edici ve kullanıcıyı harekete geçiren bir mesaj oluştur."
    if context:
        return f"{base_prompt}\nKontekst: {context}"
    return base_prompt

def get_menu_prompt(context=None):
    """Menü için sistem promptunu döndürür."""
    base_prompt = "Menü seçeneklerini göster ve kullanıcıya yardımcı ol."
    if context:
        return f"{base_prompt}\nKontekst: {context}"
    return base_prompt
