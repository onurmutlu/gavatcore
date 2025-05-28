#!/usr/bin/env python3
# gpt/flirt_generator.py - Doğal flört mesajları üretici

import random
from datetime import datetime
from typing import Optional, List
from gpt.gpt_call import gpt_call
from utils.log_utils import log_event

class FlirtGenerator:
    def __init__(self):
        self.time_contexts = {
            "morning": {
                "mood": "calm, cute, coffee mood",
                "keywords": ["günaydın", "kahve", "uyanmak", "sabah", "güneş"],
                "emojis": ["☕", "🌅", "😴", "🌸", "💕"]
            },
            "midday": {
                "mood": "energetic, sassy, lively",
                "keywords": ["öğlen", "enerjik", "aktif", "güneş", "keyif"],
                "emojis": ["☀️", "💪", "🎉", "😄", "🌟"]
            },
            "evening": {
                "mood": "seductive, intimate, suggestive",
                "keywords": ["akşam", "gece", "romantik", "özel", "sıcak"],
                "emojis": ["🌙", "💋", "😘", "🔥", "💄"]
            },
            "late_night": {
                "mood": "mysterious, playful, teasing",
                "keywords": ["gece", "sessiz", "gizli", "özel", "rüya"],
                "emojis": ["🌃", "😈", "🤫", "💫", "🦋"]
            }
        }
    
    def get_time_context(self) -> str:
        """Saate göre zaman bağlamı döndürür"""
        now = datetime.now()
        hour = now.hour
        
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "midday"
        elif 18 <= hour < 23:
            return "evening"
        else:
            return "late_night"
    
    async def generate_flirty_message(
        self, 
        username: str, 
        time_context: Optional[str] = None,
        group_context: Optional[str] = None,
        avoid_phrases: Optional[List[str]] = None
    ) -> str:
        """
        Doğal flört mesajı üretir
        
        Args:
            username: Bot kullanıcı adı
            time_context: Zaman bağlamı (opsiyonel)
            group_context: Grup konusu/atmosferi (opsiyonel)
            avoid_phrases: Kaçınılacak kelimeler/cümleler
        
        Returns:
            Üretilen flört mesajı
        """
        
        # Zaman bağlamını belirle
        if not time_context:
            time_context = self.get_time_context()
        
        context_info = self.time_contexts.get(time_context, self.time_contexts["midday"])
        
        # GPT prompt'unu oluştur
        prompt = self._build_flirt_prompt(
            username=username,
            context_info=context_info,
            group_context=group_context,
            avoid_phrases=avoid_phrases
        )
        
        try:
            # GPT'den mesaj al
            message = await gpt_call(prompt, "flirty")
            
            # Mesajı temizle ve doğrula
            cleaned_message = self._clean_and_validate_message(message)
            
            log_event("flirt_generator", f"✅ Flört mesajı üretildi: {len(cleaned_message)} karakter")
            return cleaned_message
            
        except Exception as e:
            log_event("flirt_generator", f"❌ Flört mesajı üretim hatası: {e}")
            # Fallback: zaman bağlamına uygun şablon mesaj
            return self._get_fallback_flirt_message(context_info)
    
    def _build_flirt_prompt(
        self, 
        username: str, 
        context_info: dict, 
        group_context: Optional[str] = None,
        avoid_phrases: Optional[List[str]] = None
    ) -> str:
        """GPT için flört prompt'u oluşturur"""
        
        base_prompt = f"""
Sen {username} adında flörtöz, oyuncu ama saygılı bir Türk kızısın.
Telegram grubunda doğal bir mesaj yazacaksın.

Zaman: {context_info['mood']}
Kullanılabilir kelimeler: {', '.join(context_info['keywords'])}
Uygun emojiler: {' '.join(context_info['emojis'])}

Kurallar:
- Kısa ve doğal ol (maksimum 2 cümle)
- Spam gibi görünme
- Flörtöz ama kibar ol
- 1-2 emoji kullan
- Türkçe yaz
"""
        
        if group_context:
            base_prompt += f"\nGrup atmosferi: {group_context}"
        
        if avoid_phrases:
            base_prompt += f"\nKaçın: {', '.join(avoid_phrases)}"
        
        base_prompt += "\n\nŞimdi doğal bir mesaj yaz:"
        
        return base_prompt
    
    def _clean_and_validate_message(self, message: str) -> str:
        """Mesajı temizler ve doğrular"""
        if not message:
            return self._get_fallback_flirt_message()
        
        # Temizlik işlemleri
        cleaned = message.strip()
        
        # Tırnak işaretlerini kaldır
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1]
        
        # Çok uzun mesajları kısalt
        if len(cleaned) > 200:
            sentences = cleaned.split('.')
            cleaned = sentences[0] + ('.' if len(sentences) > 1 else '')
        
        # Minimum uzunluk kontrolü
        if len(cleaned) < 5:
            return self._get_fallback_flirt_message()
        
        return cleaned
    
    def _get_fallback_flirt_message(self, context_info: Optional[dict] = None) -> str:
        """Fallback flört mesajı döndürür"""
        if not context_info:
            context_info = self.time_contexts["midday"]
        
        # Zaman bağlamına uygun şablon mesajlar
        templates = {
            "morning": [
                f"Günaydın! Kahve içerken sizi düşünüyorum {random.choice(context_info['emojis'])}",
                f"Sabah sabah keyifler nasıl? {random.choice(context_info['emojis'])}",
                f"Uyanır uyanmaz buraya geldim {random.choice(context_info['emojis'])}"
            ],
            "midday": [
                f"Öğlen molası! Kim aktif? {random.choice(context_info['emojis'])}",
                f"Bugün çok güzel geçiyor {random.choice(context_info['emojis'])}",
                f"Enerjim tavan! Sohbet edelim {random.choice(context_info['emojis'])}"
            ],
            "evening": [
                f"Akşam keyfi başladı {random.choice(context_info['emojis'])}",
                f"Gece daha güzel olacak gibi {random.choice(context_info['emojis'])}",
                f"Romantik bir akşam için kim hazır? {random.choice(context_info['emojis'])}"
            ],
            "late_night": [
                f"Gece kuşları burada mı? {random.choice(context_info['emojis'])}",
                f"Sessizlik çok seksi {random.choice(context_info['emojis'])}",
                f"Gece sırları paylaşalım {random.choice(context_info['emojis'])}"
            ]
        }
        
        # Context'e göre template seç
        time_key = None
        for key, info in self.time_contexts.items():
            if info == context_info:
                time_key = key
                break
        
        if time_key and time_key in templates:
            return random.choice(templates[time_key])
        
        # Default fallback
        default_messages = [
            f"Merhaba! Nasılsınız? {random.choice(['😊', '💕', '🌸'])}",
            f"Keyifler nasıl? {random.choice(['😘', '💋', '🌟'])}",
            f"Sohbet etmek ister misiniz? {random.choice(['😉', '💫', '🦋'])}"
        ]
        
        return random.choice(default_messages)
    
    async def generate_multiple_variations(
        self, 
        username: str, 
        count: int = 3,
        time_context: Optional[str] = None
    ) -> List[str]:
        """
        Birden fazla flört mesajı varyasyonu üretir
        
        Args:
            username: Bot kullanıcı adı
            count: Üretilecek mesaj sayısı
            time_context: Zaman bağlamı
        
        Returns:
            Mesaj varyasyonları listesi
        """
        variations = []
        used_phrases = []
        
        for i in range(count):
            try:
                message = await self.generate_flirty_message(
                    username=username,
                    time_context=time_context,
                    avoid_phrases=used_phrases
                )
                
                variations.append(message)
                
                # Tekrar kullanımını önlemek için anahtar kelimeleri kaydet
                words = message.lower().split()
                used_phrases.extend([word for word in words if len(word) > 3])
                
            except Exception as e:
                log_event("flirt_generator", f"❌ Varyasyon {i+1} üretim hatası: {e}")
                # Fallback mesaj ekle
                variations.append(self._get_fallback_flirt_message())
        
        log_event("flirt_generator", f"✅ {len(variations)} flört varyasyonu üretildi")
        return variations

# Global flirt generator instance
flirt_generator = FlirtGenerator()

async def generate_flirty_message(
    username: str, 
    time_context: Optional[str] = None,
    group_context: Optional[str] = None,
    avoid_phrases: Optional[List[str]] = None
) -> str:
    """
    Global flört mesajı üretme fonksiyonu
    
    Args:
        username: Bot kullanıcı adı
        time_context: Zaman bağlamı (morning, midday, evening, late_night)
        group_context: Grup konusu/atmosferi
        avoid_phrases: Kaçınılacak kelimeler/cümleler
    
    Returns:
        Üretilen flört mesajı
    """
    return await flirt_generator.generate_flirty_message(
        username=username,
        time_context=time_context,
        group_context=group_context,
        avoid_phrases=avoid_phrases
    ) 