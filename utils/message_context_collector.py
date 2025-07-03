#!/usr/bin/env python3
# utils/message_context_collector.py - Grup mesaj bağlamı analiz edici

import re
import asyncio
from typing import List, Optional, Dict, Any
from collections import Counter
from datetime import datetime, timedelta
from gpt.gpt_call import gpt_call
from utils.log_utils import log_event

class MessageContextCollector:
    def __init__(self):
        self.context_keywords = {
            "flirt": ["güzel", "tatlı", "seksi", "aşk", "sevgi", "öp", "sarıl", "romantik"],
            "casual": ["nasıl", "naber", "keyif", "sohbet", "konuş", "anlat"],
            "question": ["ne", "nasıl", "nerede", "kim", "niye", "hangi", "?"],
            "greeting": ["selam", "merhaba", "günaydın", "iyi akşam", "hey"],
            "compliment": ["harika", "mükemmel", "süper", "çok iyi", "bravo", "tebrik"],
            "emotional": ["üzgün", "mutlu", "kızgın", "sevinç", "heyecan", "korku"],
            "activity": ["gidiyorum", "geliyorum", "yapıyorum", "izliyorum", "dinliyorum"],
            "time": ["sabah", "öğlen", "akşam", "gece", "bugün", "yarın", "dün"]
        }
        
        self.spam_indicators = [
            "link", "http", "www", "telegram.me", "t.me",
            "reklam", "satış", "para", "ücret", "bedava",
            "grup", "kanal", "katıl", "davet"
        ]
    
    async def extract_group_context(
        self, 
        messages: List[str], 
        time_window_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        Grup mesajlarından bağlam çıkarır
        
        Args:
            messages: Analiz edilecek mesajlar
            time_window_minutes: Zaman penceresi (dakika)
        
        Returns:
            Grup bağlamı bilgileri
        """
        
        if not messages:
            return self._get_default_context()
        
        # Son mesajları filtrele (spam olmayan)
        filtered_messages = self._filter_spam_messages(messages)
        
        if not filtered_messages:
            return self._get_default_context()
        
        # Bağlam analizi
        context_analysis = {
            "dominant_theme": self._analyze_dominant_theme(filtered_messages),
            "activity_level": self._calculate_activity_level(filtered_messages),
            "emotional_tone": self._analyze_emotional_tone(filtered_messages),
            "topic_keywords": self._extract_topic_keywords(filtered_messages),
            "conversation_flow": self._analyze_conversation_flow(filtered_messages),
            "time_context": self._get_time_context()
        }
        
        # GPT ile detaylı analiz (opsiyonel)
        try:
            gpt_context = await self._get_gpt_context_analysis(filtered_messages[-10:])
            context_analysis["gpt_summary"] = gpt_context
        except Exception as e:
            log_event("context_collector", f"⚠️ GPT bağlam analizi hatası: {e}")
            context_analysis["gpt_summary"] = None
        
        log_event("context_collector", f"✅ Grup bağlamı analiz edildi: {context_analysis['dominant_theme']}")
        return context_analysis
    
    def _filter_spam_messages(self, messages: List[str]) -> List[str]:
        """Spam mesajları filtreler"""
        filtered = []
        
        for message in messages:
            message_lower = message.lower()
            
            # Spam göstergeleri var mı
            is_spam = any(indicator in message_lower for indicator in self.spam_indicators)
            
            # Çok kısa mesajlar (emoji-only)
            if len(message.strip()) < 3:
                is_spam = True
            
            # Çok uzun mesajlar (muhtemelen spam)
            if len(message) > 500:
                is_spam = True
            
            # Çok fazla büyük harf
            if len(message) > 10 and sum(1 for c in message if c.isupper()) / len(message) > 0.7:
                is_spam = True
            
            if not is_spam:
                filtered.append(message)
        
        return filtered
    
    def _analyze_dominant_theme(self, messages: List[str]) -> str:
        """Baskın temayı analiz eder"""
        theme_scores = {theme: 0 for theme in self.context_keywords.keys()}
        
        for message in messages:
            message_lower = message.lower()
            
            for theme, keywords in self.context_keywords.items():
                for keyword in keywords:
                    if keyword in message_lower:
                        theme_scores[theme] += 1
        
        # En yüksek skora sahip tema
        if theme_scores:
            dominant_theme = max(theme_scores, key=theme_scores.get)
            if theme_scores[dominant_theme] > 0:
                return dominant_theme
        
        return "casual"
    
    def _calculate_activity_level(self, messages: List[str]) -> str:
        """Aktivite seviyesini hesaplar"""
        message_count = len(messages)
        
        if message_count >= 20:
            return "high"
        elif message_count >= 10:
            return "medium"
        elif message_count >= 5:
            return "low"
        else:
            return "very_low"
    
    def _analyze_emotional_tone(self, messages: List[str]) -> str:
        """Duygusal tonu analiz eder"""
        positive_indicators = ["😊", "😄", "😍", "💕", "❤️", "🎉", "harika", "süper", "mükemmel"]
        negative_indicators = ["😢", "😞", "😠", "💔", "üzgün", "kötü", "berbat"]
        neutral_indicators = ["🤔", "😐", "normal", "idare eder"]
        
        positive_score = 0
        negative_score = 0
        neutral_score = 0
        
        for message in messages:
            message_lower = message.lower()
            
            for indicator in positive_indicators:
                if indicator in message_lower:
                    positive_score += 1
            
            for indicator in negative_indicators:
                if indicator in message_lower:
                    negative_score += 1
            
            for indicator in neutral_indicators:
                if indicator in message_lower:
                    neutral_score += 1
        
        # En yüksek skora sahip ton
        scores = {"positive": positive_score, "negative": negative_score, "neutral": neutral_score}
        return max(scores, key=scores.get) if any(scores.values()) else "neutral"
    
    def _extract_topic_keywords(self, messages: List[str], top_n: int = 5) -> List[str]:
        """Konu anahtar kelimelerini çıkarır"""
        # Tüm mesajları birleştir
        combined_text = " ".join(messages).lower()
        
        # Kelimeleri ayır ve temizle
        words = re.findall(r'\b[a-züğışçö]{3,}\b', combined_text)
        
        # Stop words'leri filtrele
        stop_words = {
            "bir", "bu", "şu", "o", "ben", "sen", "biz", "siz", "onlar",
            "ve", "ile", "için", "gibi", "kadar", "daha", "çok", "az",
            "var", "yok", "olan", "olur", "oldu", "ama", "fakat", "ancak"
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # En sık geçen kelimeleri bul
        word_counts = Counter(filtered_words)
        return [word for word, count in word_counts.most_common(top_n)]
    
    def _analyze_conversation_flow(self, messages: List[str]) -> str:
        """Konuşma akışını analiz eder"""
        if len(messages) < 3:
            return "starting"
        
        # Son mesajlardaki soru işareti sayısı
        question_count = sum(1 for msg in messages[-5:] if "?" in msg)
        
        # Mesaj uzunluklarının ortalaması
        avg_length = sum(len(msg) for msg in messages) / len(messages)
        
        if question_count >= 2:
            return "interactive"
        elif avg_length > 50:
            return "detailed"
        elif avg_length < 20:
            return "brief"
        else:
            return "flowing"
    
    def _get_time_context(self) -> str:
        """Zaman bağlamını döndürür"""
        now = datetime.now()
        hour = now.hour
        
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 23:
            return "evening"
        else:
            return "night"
    
    async def _get_gpt_context_analysis(self, messages: List[str]) -> Optional[str]:
        """GPT ile detaylı bağlam analizi"""
        if not messages:
            return None
        
        # Son 10 mesajı al
        recent_messages = messages[-10:]
        combined_text = "\n".join([f"- {msg}" for msg in recent_messages])
        
        prompt = f"""
Aşağıdaki Telegram grup sohbetini analiz et ve grup atmosferini tek cümle ile özetle:

{combined_text}

Grup atmosferi nasıl? (örnek: "Grup eğlenceli ve samimi sohbet ediyor", "Sessiz ve sakin bir atmosfer var", "Flörtöz ve oyuncu bir hava var")
"""
        
        try:
            context_summary = await gpt_call(prompt, "group_context")
            return context_summary.strip() if context_summary else None
        except Exception as e:
            log_event("context_collector", f"❌ GPT bağlam analizi hatası: {e}")
            return None
    
    def _get_default_context(self) -> Dict[str, Any]:
        """Default bağlam döndürür"""
        return {
            "dominant_theme": "casual",
            "activity_level": "low",
            "emotional_tone": "neutral",
            "topic_keywords": [],
            "conversation_flow": "starting",
            "time_context": self._get_time_context(),
            "gpt_summary": None
        }
    
    def format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """Bağlamı GPT prompt'u için formatlar"""
        parts = []
        
        # Ana tema
        parts.append(f"Grup teması: {context['dominant_theme']}")
        
        # Aktivite seviyesi
        activity_map = {
            "high": "çok aktif",
            "medium": "orta seviye aktif", 
            "low": "az aktif",
            "very_low": "sessiz"
        }
        parts.append(f"Aktivite: {activity_map.get(context['activity_level'], 'normal')}")
        
        # Duygusal ton
        tone_map = {
            "positive": "pozitif ve neşeli",
            "negative": "negatif veya üzgün",
            "neutral": "nötr"
        }
        parts.append(f"Atmosfer: {tone_map.get(context['emotional_tone'], 'normal')}")
        
        # Zaman bağlamı
        time_map = {
            "morning": "sabah saatleri",
            "afternoon": "öğleden sonra",
            "evening": "akşam saatleri", 
            "night": "gece saatleri"
        }
        parts.append(f"Zaman: {time_map.get(context['time_context'], 'gündüz')}")
        
        # Konu anahtar kelimeleri
        if context['topic_keywords']:
            parts.append(f"Konular: {', '.join(context['topic_keywords'][:3])}")
        
        # GPT özeti varsa ekle
        if context.get('gpt_summary'):
            parts.append(f"Genel durum: {context['gpt_summary']}")
        
        return " | ".join(parts)

# Global message context collector instance
message_context_collector = MessageContextCollector()

async def extract_group_context(
    messages: List[str], 
    time_window_minutes: int = 30
) -> Dict[str, Any]:
    """
    Global grup bağlamı çıkarma fonksiyonu
    
    Args:
        messages: Analiz edilecek mesajlar
        time_window_minutes: Zaman penceresi (dakika)
    
    Returns:
        Grup bağlamı bilgileri
    """
    return await message_context_collector.extract_group_context(
        messages=messages,
        time_window_minutes=time_window_minutes
    )

def format_context_for_prompt(context: Dict[str, Any]) -> str:
    """
    Global bağlam formatlama fonksiyonu
    
    Args:
        context: Grup bağlamı
    
    Returns:
        GPT prompt'u için formatlanmış bağlam
    """
    return message_context_collector.format_context_for_prompt(context) 