#!/usr/bin/env python3
# gpt/shadow_persona_generator.py - Şovcu tarzı taklit eden mesaj üretici

import random
import re
from typing import List, Optional, Dict, Any
from collections import Counter
from gpt.gpt_call import gpt_call
from utilities.log_utils import log_event

class ShadowPersonaGenerator:
    def __init__(self):
        self.min_examples = 3
        self.max_examples = 10
        self.style_patterns = {
            "emoji_usage": r'[😀-🙏🏻]',
            "punctuation": r'[!?]{2,}',
            "caps_usage": r'[A-Z]{2,}',
            "slang_words": ['lan', 'ya', 'abi', 'canım', 'tatlım', 'aşkım'],
            "question_style": r'\?+',
            "exclamation_style": r'!+'
        }
    
    async def generate_shadow_message(
        self, 
        examples: List[str], 
        context: Optional[str] = None,
        message_type: str = "casual"
    ) -> str:
        """
        Örnek mesajlardan öğrenerek benzer tarzda mesaj üretir
        
        Args:
            examples: Taklit edilecek mesaj örnekleri
            context: Mesaj bağlamı (opsiyonel)
            message_type: Mesaj tipi (casual, flirty, greeting)
        
        Returns:
            Üretilen shadow mesaj
        """
        
        if not examples or len(examples) < self.min_examples:
            log_event("shadow_persona", f"⚠️ Yetersiz örnek: {len(examples)}")
            return await self._get_fallback_message(message_type)
        
        try:
            # Stil analizi
            style_analysis = self._analyze_writing_style(examples)
            
            # GPT prompt'unu oluştur
            prompt = self._build_shadow_prompt(examples, style_analysis, context, message_type)
            
            # GPT'den mesaj üret
            shadow_message = await gpt_call(prompt, "shadow_persona")
            
            # Stil uygulaması
            styled_message = self._apply_style_patterns(shadow_message, style_analysis)
            
            # Mesajı doğrula
            validated_message = self._validate_shadow_message(styled_message, examples)
            
            log_event("shadow_persona", f"✅ Shadow mesaj üretildi: {len(validated_message)} karakter")
            return validated_message
            
        except Exception as e:
            log_event("shadow_persona", f"❌ Shadow mesaj üretim hatası: {e}")
            return await self._get_fallback_message(message_type)
    
    def _analyze_writing_style(self, examples: List[str]) -> Dict[str, Any]:
        """Yazım stilini analiz eder"""
        
        style_analysis = {
            "avg_length": 0,
            "emoji_frequency": 0,
            "caps_frequency": 0,
            "punctuation_style": {},
            "common_words": [],
            "sentence_structure": "simple",
            "tone_indicators": []
        }
        
        if not examples:
            return style_analysis
        
        # Ortalama uzunluk
        total_length = sum(len(msg) for msg in examples)
        style_analysis["avg_length"] = total_length / len(examples)
        
        # Emoji kullanımı
        emoji_count = 0
        for msg in examples:
            emoji_count += len(re.findall(self.style_patterns["emoji_usage"], msg))
        style_analysis["emoji_frequency"] = emoji_count / len(examples)
        
        # Büyük harf kullanımı
        caps_count = 0
        for msg in examples:
            caps_count += len(re.findall(self.style_patterns["caps_usage"], msg))
        style_analysis["caps_frequency"] = caps_count / len(examples)
        
        # Noktalama stilleri
        punctuation_counts = {"question": 0, "exclamation": 0, "multiple": 0}
        for msg in examples:
            if re.search(r'\?{2,}', msg):
                punctuation_counts["multiple"] += 1
            elif '?' in msg:
                punctuation_counts["question"] += 1
            
            if re.search(r'!{2,}', msg):
                punctuation_counts["multiple"] += 1
            elif '!' in msg:
                punctuation_counts["exclamation"] += 1
        
        style_analysis["punctuation_style"] = punctuation_counts
        
        # Yaygın kelimeler
        all_words = []
        for msg in examples:
            words = re.findall(r'\b[a-züğışçö]+\b', msg.lower())
            all_words.extend(words)
        
        if all_words:
            word_counts = Counter(all_words)
            style_analysis["common_words"] = [word for word, count in word_counts.most_common(10)]
        
        # Cümle yapısı analizi
        avg_sentences = sum(len(msg.split('.')) for msg in examples) / len(examples)
        if avg_sentences > 2:
            style_analysis["sentence_structure"] = "complex"
        elif avg_sentences > 1.5:
            style_analysis["sentence_structure"] = "medium"
        else:
            style_analysis["sentence_structure"] = "simple"
        
        # Ton göstergeleri
        tone_words = {
            "friendly": ["canım", "tatlım", "sevgilim", "aşkım"],
            "casual": ["ya", "lan", "abi", "kanka"],
            "excited": ["harika", "süper", "mükemmel", "çok"],
            "questioning": ["nasıl", "neden", "ne", "kim"]
        }
        
        for tone, words in tone_words.items():
            for msg in examples:
                if any(word in msg.lower() for word in words):
                    style_analysis["tone_indicators"].append(tone)
                    break
        
        return style_analysis
    
    def _build_shadow_prompt(
        self, 
        examples: List[str], 
        style_analysis: Dict[str, Any],
        context: Optional[str],
        message_type: str
    ) -> str:
        """Shadow persona için GPT prompt'u oluşturur"""
        
        # En iyi örnekleri seç (çok kısa veya çok uzun olmayanlar)
        filtered_examples = [
            msg for msg in examples 
            if 10 <= len(msg) <= 200 and not msg.startswith('http')
        ]
        
        selected_examples = filtered_examples[:self.max_examples]
        
        base_prompt = f"""
Sen bir Telegram kullanıcısının yazım tarzını taklit edeceksin.

Örnek mesajlar:
{chr(10).join([f"- {msg}" for msg in selected_examples])}

Stil özellikleri:
- Ortalama mesaj uzunluğu: {int(style_analysis['avg_length'])} karakter
- Emoji kullanımı: {style_analysis['emoji_frequency']:.1f} emoji/mesaj
- Büyük harf kullanımı: {'Sık' if style_analysis['caps_frequency'] > 1 else 'Az'}
- Cümle yapısı: {style_analysis['sentence_structure']}
- Yaygın kelimeler: {', '.join(style_analysis['common_words'][:5])}
"""
        
        if style_analysis['tone_indicators']:
            base_prompt += f"- Ton: {', '.join(set(style_analysis['tone_indicators']))}\n"
        
        if context:
            base_prompt += f"\nBağlam: {context}\n"
        
        base_prompt += f"""
Mesaj tipi: {message_type}

Kurallar:
- Aynı yazım tarzını kullan
- Benzer uzunlukta mesaj yaz
- Aynı ton ve üslubu koru
- Emoji kullanımını taklit et
- Noktalama stilini koru
- Türkçe yaz
- Orijinal örneklerle aynı olmayan ama benzer bir mesaj üret

Şimdi bu tarzda yeni bir mesaj yaz:"""
        
        return base_prompt
    
    def _apply_style_patterns(self, message: str, style_analysis: Dict[str, Any]) -> str:
        """Stil desenlerini mesaja uygular"""
        
        if not message:
            return message
        
        styled_message = message.strip()
        
        # Emoji ekleme
        if style_analysis["emoji_frequency"] > 0.5:
            common_emojis = ["😊", "😘", "💕", "🌸", "😉", "🔥", "💋", "🌟"]
            emoji_count = int(style_analysis["emoji_frequency"])
            
            for _ in range(min(emoji_count, 2)):
                if random.random() < 0.7:  # %70 şans
                    emoji = random.choice(common_emojis)
                    if emoji not in styled_message:
                        styled_message += f" {emoji}"
        
        # Noktalama stili
        punctuation = style_analysis.get("punctuation_style", {})
        
        if punctuation.get("multiple", 0) > 0:
            # Çoklu noktalama kullanımı
            if styled_message.endswith('!'):
                styled_message = styled_message[:-1] + "!!"
            elif styled_message.endswith('?'):
                styled_message = styled_message[:-1] + "??"
        
        # Büyük harf vurgusu
        if style_analysis["caps_frequency"] > 1:
            words = styled_message.split()
            if len(words) > 2:
                # Rastgele bir kelimeyi büyük harfe çevir
                emphasis_word_idx = random.randint(0, len(words) - 1)
                if len(words[emphasis_word_idx]) > 3:
                    words[emphasis_word_idx] = words[emphasis_word_idx].upper()
                styled_message = " ".join(words)
        
        return styled_message
    
    def _validate_shadow_message(self, message: str, examples: List[str]) -> str:
        """Shadow mesajını doğrular"""
        
        if not message:
            return self._get_simple_fallback()
        
        # Temizlik
        cleaned = message.strip()
        
        # Tırnak işaretlerini kaldır
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1]
        
        # Çok benzer mesaj kontrolü
        for example in examples:
            if self._calculate_similarity(cleaned.lower(), example.lower()) > 0.8:
                # Çok benzer, biraz değiştir
                cleaned = self._add_variation(cleaned)
                break
        
        # Uzunluk kontrolü
        if len(cleaned) < 5:
            return self._get_simple_fallback()
        
        if len(cleaned) > 300:
            sentences = cleaned.split('.')
            cleaned = sentences[0] + ('.' if len(sentences) > 1 else '')
        
        return cleaned
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """İki metin arasındaki benzerlik oranını hesaplar"""
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _add_variation(self, message: str) -> str:
        """Mesaja küçük varyasyon ekler"""
        
        variations = [
            lambda m: m + " 😊",
            lambda m: "Hmm, " + m.lower(),
            lambda m: m + " ya",
            lambda m: m.replace(".", "!"),
            lambda m: m + " canım"
        ]
        
        variation_func = random.choice(variations)
        return variation_func(message)
    
    async def _get_fallback_message(self, message_type: str = "casual") -> str:
        """Fallback mesaj döndürür"""
        
        fallback_templates = {
            "casual": [
                "Nasılsınız? 😊",
                "Keyifler nasıl?",
                "Selam! Ne var ne yok?",
                "Merhaba canım! 💕"
            ],
            "flirty": [
                "Bugün çok güzelsin! 😘",
                "Seni özledim 💋",
                "Flört etmek ister misin? 😉",
                "Gözlerin çok güzel ✨"
            ],
            "greeting": [
                "Merhaba! 👋",
                "Selam canım! 😊",
                "Günaydın! ☀️",
                "Hey! Nasılsın? 💕"
            ]
        }
        
        templates = fallback_templates.get(message_type, fallback_templates["casual"])
        return random.choice(templates)
    
    def _get_simple_fallback(self) -> str:
        """Basit fallback mesaj"""
        simple_messages = [
            "Merhaba! 😊",
            "Nasılsın? 💕",
            "Selam canım! 🌸",
            "Hey! 😘"
        ]
        return random.choice(simple_messages)
    
    async def analyze_persona_from_history(
        self, 
        message_history: List[str],
        min_messages: int = 10
    ) -> Dict[str, Any]:
        """
        Mesaj geçmişinden persona analizi yapar
        
        Args:
            message_history: Mesaj geçmişi
            min_messages: Minimum mesaj sayısı
        
        Returns:
            Persona analizi
        """
        
        if len(message_history) < min_messages:
            return {"status": "insufficient_data", "message_count": len(message_history)}
        
        # Mesajları filtrele (spam, çok kısa olanları çıkar)
        filtered_messages = [
            msg for msg in message_history 
            if 5 <= len(msg) <= 500 and not msg.startswith('http')
        ]
        
        if len(filtered_messages) < min_messages:
            return {"status": "insufficient_quality_data", "filtered_count": len(filtered_messages)}
        
        # Stil analizi
        style_analysis = self._analyze_writing_style(filtered_messages)
        
        # Persona özellikleri
        persona_traits = {
            "communication_style": self._determine_communication_style(style_analysis),
            "personality_type": self._determine_personality_type(filtered_messages),
            "activity_pattern": self._analyze_activity_pattern(filtered_messages),
            "preferred_topics": self._extract_preferred_topics(filtered_messages),
            "style_analysis": style_analysis
        }
        
        return {
            "status": "success",
            "message_count": len(message_history),
            "analyzed_messages": len(filtered_messages),
            "persona_traits": persona_traits
        }
    
    def _determine_communication_style(self, style_analysis: Dict[str, Any]) -> str:
        """İletişim stilini belirler"""
        
        if style_analysis["emoji_frequency"] > 2:
            return "expressive"
        elif style_analysis["avg_length"] > 100:
            return "detailed"
        elif style_analysis["caps_frequency"] > 1:
            return "enthusiastic"
        else:
            return "casual"
    
    def _determine_personality_type(self, messages: List[str]) -> str:
        """Kişilik tipini belirler"""
        
        personality_indicators = {
            "friendly": ["canım", "tatlım", "sevgilim", "aşkım", "😊", "💕"],
            "playful": ["haha", "hihi", "😄", "😂", "eğlence", "şaka"],
            "romantic": ["aşk", "sevgi", "romantik", "💋", "❤️", "😘"],
            "casual": ["ya", "lan", "abi", "normal", "idare eder"]
        }
        
        scores = {personality: 0 for personality in personality_indicators}
        
        for msg in messages:
            msg_lower = msg.lower()
            for personality, indicators in personality_indicators.items():
                for indicator in indicators:
                    if indicator in msg_lower:
                        scores[personality] += 1
        
        return max(scores, key=scores.get) if any(scores.values()) else "neutral"
    
    def _analyze_activity_pattern(self, messages: List[str]) -> str:
        """Aktivite desenini analiz eder"""
        
        if len(messages) > 50:
            return "very_active"
        elif len(messages) > 20:
            return "active"
        elif len(messages) > 10:
            return "moderate"
        else:
            return "low_activity"
    
    def _extract_preferred_topics(self, messages: List[str], top_n: int = 5) -> List[str]:
        """Tercih edilen konuları çıkarır"""
        
        # Tüm mesajları birleştir
        combined_text = " ".join(messages).lower()
        
        # Kelimeleri ayır
        words = re.findall(r'\b[a-züğışçö]{4,}\b', combined_text)
        
        # Stop words'leri filtrele
        stop_words = {
            "çok", "daha", "şey", "gibi", "için", "olan", "olur", "oldu",
            "var", "yok", "ben", "sen", "biz", "siz", "onlar"
        }
        
        filtered_words = [word for word in words if word not in stop_words]
        
        # En sık geçen kelimeleri bul
        word_counts = Counter(filtered_words)
        return [word for word, count in word_counts.most_common(top_n)]

# Global shadow persona generator instance
shadow_persona_generator = ShadowPersonaGenerator()

async def generate_shadow_message(
    examples: List[str], 
    context: Optional[str] = None,
    message_type: str = "casual"
) -> str:
    """
    Global shadow mesaj üretme fonksiyonu
    
    Args:
        examples: Taklit edilecek mesaj örnekleri
        context: Mesaj bağlamı
        message_type: Mesaj tipi
    
    Returns:
        Üretilen shadow mesaj
    """
    return await shadow_persona_generator.generate_shadow_message(
        examples=examples,
        context=context,
        message_type=message_type
    ) 