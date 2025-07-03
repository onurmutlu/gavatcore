#!/usr/bin/env python3
# gpt/group_reply_agent.py - Mention'lara GPT ile yanıt veren agent

import re
import random
from typing import Optional, Dict, Any
from gpt.gpt_call import gpt_call
from utilities.log_utils import log_event

class GroupReplyAgent:
    def __init__(self):
        self.mention_patterns = [
            r'@(\w+)',  # @username
            r'(\w+)\s+(gel|gelsene|neredesin|burada\s*mı)',  # "username gel" gibi
            r'(hey|selam|merhaba)\s+(\w+)',  # "hey username"
        ]
        
        self.reply_contexts = {
            "greeting": {
                "keywords": ["selam", "merhaba", "hey", "naber", "nasılsın"],
                "tone": "friendly, warm"
            },
            "question": {
                "keywords": ["ne", "nasıl", "nerede", "kim", "niye", "?"],
                "tone": "helpful, playful"
            },
            "flirt": {
                "keywords": ["güzel", "tatlı", "seksi", "aşk", "sevgi", "öp"],
                "tone": "flirty, teasing"
            },
            "compliment": {
                "keywords": ["harika", "mükemmel", "süper", "çok iyi", "bravo"],
                "tone": "appreciative, sweet"
            },
            "call": {
                "keywords": ["gel", "gelsene", "neredesin", "burada mı"],
                "tone": "responsive, eager"
            }
        }
    
    def detect_mention(self, message: str, bot_username: str) -> bool:
        """
        Mesajda bot mention'ı var mı kontrol eder
        
        Args:
            message: Kontrol edilecek mesaj
            bot_username: Bot kullanıcı adı
        
        Returns:
            Mention tespit edildi mi
        """
        message_lower = message.lower()
        bot_username_clean = bot_username.lower().replace("@", "").replace("bot_", "")
        
        # Direkt @mention kontrolü
        if f"@{bot_username_clean}" in message_lower:
            return True
        
        # Username geçiyor mu
        if bot_username_clean in message_lower:
            return True
        
        # Pattern tabanlı kontrol
        for pattern in self.mention_patterns:
            matches = re.findall(pattern, message_lower, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Tuple içinde bot username var mı
                    if any(bot_username_clean in str(m) for m in match):
                        return True
                elif bot_username_clean in str(match):
                    return True
        
        return False
    
    def analyze_message_context(self, message: str) -> str:
        """
        Mesajın bağlamını analiz eder (greeting, question, flirt, etc.)
        
        Args:
            message: Analiz edilecek mesaj
        
        Returns:
            Tespit edilen bağlam
        """
        message_lower = message.lower()
        
        # Her bağlam için skor hesapla
        context_scores = {}
        
        for context, info in self.reply_contexts.items():
            score = 0
            for keyword in info["keywords"]:
                if keyword in message_lower:
                    score += 1
            context_scores[context] = score
        
        # En yüksek skora sahip bağlamı döndür
        if context_scores:
            best_context = max(context_scores, key=context_scores.get)
            if context_scores[best_context] > 0:
                return best_context
        
        # Default: question (çünkü mention genelde soru içerir)
        return "question"
    
    async def generate_mention_reply(
        self, 
        message: str, 
        bot_name: str, 
        sender_name: Optional[str] = None,
        group_context: Optional[str] = None
    ) -> str:
        """
        Mention'a GPT ile yanıt üretir
        
        Args:
            message: Mention içeren mesaj
            bot_name: Bot adı/karakteri
            sender_name: Mesajı gönderen kişi
            group_context: Grup atmosferi
        
        Returns:
            Üretilen yanıt
        """
        
        # Mesaj bağlamını analiz et
        context = self.analyze_message_context(message)
        context_info = self.reply_contexts.get(context, self.reply_contexts["question"])
        
        # GPT prompt'unu oluştur
        prompt = self._build_reply_prompt(
            message=message,
            bot_name=bot_name,
            sender_name=sender_name,
            context_info=context_info,
            group_context=group_context
        )
        
        try:
            # GPT'den yanıt al
            reply = await gpt_call(prompt, "mention_reply")
            
            # Yanıtı temizle ve doğrula
            cleaned_reply = self._clean_and_validate_reply(reply, sender_name)
            
            log_event("group_reply_agent", f"✅ Mention yanıtı üretildi: {context} -> {len(cleaned_reply)} karakter")
            return cleaned_reply
            
        except Exception as e:
            log_event("group_reply_agent", f"❌ Mention yanıtı üretim hatası: {e}")
            # Fallback: bağlama uygun şablon yanıt
            return self._get_fallback_reply(context_info, sender_name)
    
    def _build_reply_prompt(
        self, 
        message: str, 
        bot_name: str, 
        sender_name: Optional[str],
        context_info: dict,
        group_context: Optional[str]
    ) -> str:
        """GPT için mention yanıt prompt'u oluşturur"""
        
        base_prompt = f"""
Sen {bot_name} adında flörtöz, zeki ve esprili bir Türk kızısın.
Telegram grubunda seni mention eden birine yanıt vereceksin.

Gelen mesaj: "{message}"
Mesaj tonu: {context_info['tone']}
"""
        
        if sender_name:
            base_prompt += f"Mesajı gönderen: {sender_name}\n"
        
        if group_context:
            base_prompt += f"Grup atmosferi: {group_context}\n"
        
        base_prompt += """
Kurallar:
- Kısa ve doğal yanıt ver (1-2 cümle)
- Kişisel ve samimi ol
- Flörtöz ama kibar ol
- 1-2 emoji kullan
- Türkçe yaz
- Spam gibi görünme

Şimdi doğal bir yanıt yaz:"""
        
        return base_prompt
    
    def _clean_and_validate_reply(self, reply: str, sender_name: Optional[str] = None) -> str:
        """Yanıtı temizler ve doğrular"""
        if not reply:
            return self._get_fallback_reply(sender_name=sender_name)
        
        # Temizlik işlemleri
        cleaned = reply.strip()
        
        # Tırnak işaretlerini kaldır
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1]
        
        # Bot adını kaldır (eğer yanıtta varsa)
        cleaned = re.sub(r'^[A-Za-z_]+:\s*', '', cleaned)
        
        # Çok uzun yanıtları kısalt
        if len(cleaned) > 150:
            sentences = cleaned.split('.')
            cleaned = sentences[0] + ('.' if len(sentences) > 1 else '')
        
        # Minimum uzunluk kontrolü
        if len(cleaned) < 3:
            return self._get_fallback_reply(sender_name=sender_name)
        
        return cleaned
    
    def _get_fallback_reply(self, context_info: Optional[dict] = None, sender_name: Optional[str] = None) -> str:
        """Fallback yanıt döndürür"""
        
        # Sender name varsa kişiselleştir
        name_part = f"{sender_name}, " if sender_name else ""
        
        if context_info:
            tone = context_info.get("tone", "friendly")
            
            if "friendly" in tone:
                templates = [
                    f"{name_part}merhaba canım! 😊",
                    f"{name_part}selam tatlım! 💕",
                    f"{name_part}buradayım! 🌸"
                ]
            elif "flirty" in tone:
                templates = [
                    f"{name_part}beni çağırdın mı? 😘",
                    f"{name_part}evet canım? 💋",
                    f"{name_part}söyle bakalım! 😉"
                ]
            elif "helpful" in tone:
                templates = [
                    f"{name_part}nasıl yardım edebilirim? 😊",
                    f"{name_part}dinliyorum seni! 🎧",
                    f"{name_part}ne merak ediyorsun? 🤔"
                ]
            else:
                templates = [
                    f"{name_part}buradayım! 😊",
                    f"{name_part}evet? 💕",
                    f"{name_part}söyle! 🌟"
                ]
        else:
            # Default templates
            templates = [
                f"{name_part}evet canım, buradayım! 😊",
                f"{name_part}beni çağırdın mı? 💕",
                f"{name_part}söyle bakalım! 😘",
                f"{name_part}dinliyorum seni! 🎧",
                f"{name_part}ne var ne yok? 😉"
            ]
        
        return random.choice(templates)
    
    async def generate_contextual_reply(
        self, 
        message: str, 
        bot_name: str,
        recent_messages: Optional[list] = None,
        sender_name: Optional[str] = None
    ) -> str:
        """
        Grup bağlamını da dikkate alarak yanıt üretir
        
        Args:
            message: Mention içeren mesaj
            bot_name: Bot adı
            recent_messages: Son mesajlar (bağlam için)
            sender_name: Gönderen kişi
        
        Returns:
            Bağlamsal yanıt
        """
        
        # Grup bağlamını analiz et
        group_context = None
        if recent_messages:
            # Son mesajlardan konu çıkar
            context_keywords = []
            for msg in recent_messages[-5:]:  # Son 5 mesaj
                words = msg.lower().split()
                context_keywords.extend([w for w in words if len(w) > 3])
            
            if context_keywords:
                # En sık geçen kelimeleri bul
                from collections import Counter
                common_words = Counter(context_keywords).most_common(3)
                group_context = f"Grup şu konuları konuşuyor: {', '.join([w[0] for w in common_words])}"
        
        return await self.generate_mention_reply(
            message=message,
            bot_name=bot_name,
            sender_name=sender_name,
            group_context=group_context
        )

# Global group reply agent instance
group_reply_agent = GroupReplyAgent()

async def generate_mention_reply(
    message: str, 
    bot_name: str, 
    sender_name: Optional[str] = None,
    group_context: Optional[str] = None
) -> str:
    """
    Global mention yanıt üretme fonksiyonu
    
    Args:
        message: Mention içeren mesaj
        bot_name: Bot adı/karakteri
        sender_name: Mesajı gönderen kişi
        group_context: Grup atmosferi
    
    Returns:
        Üretilen yanıt
    """
    return await group_reply_agent.generate_mention_reply(
        message=message,
        bot_name=bot_name,
        sender_name=sender_name,
        group_context=group_context
    )

def detect_mention(message: str, bot_username: str) -> bool:
    """
    Global mention tespit fonksiyonu
    
    Args:
        message: Kontrol edilecek mesaj
        bot_username: Bot kullanıcı adı
    
    Returns:
        Mention tespit edildi mi
    """
    return group_reply_agent.detect_mention(message, bot_username) 