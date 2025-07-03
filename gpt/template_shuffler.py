#!/usr/bin/env python3
# gpt/template_shuffler.py

import random
import re
from typing import List, Dict, Optional
from utilities.log_utils import log_event

class TemplateShuffler:
    def __init__(self):
        # Emoji kategorileri
        self.emoji_categories = {
            "flirt": ["😘", "😍", "🥰", "💋", "😈", "🔥", "💕", "💖"],
            "friendly": ["😊", "😄", "🌟", "✨", "🌺", "🎉", "💫", "🌙"],
            "playful": ["🎭", "🎪", "🎡", "🎨", "🎯", "🎲", "🎈", "🎊"],
            "romantic": ["💗", "💘", "💝", "💞", "💓", "❤️", "🌹", "💐"],
            "mysterious": ["🤫", "😏", "🔮", "🌙", "⭐", "✨", "🎭", "🖤"]
        }
        
        # Mesaj başlangıçları
        self.message_starters = [
            "Merhaba", "Selam", "Hey", "Herkese selam", "Nasılsınız",
            "Ne yapıyorsunuz", "Keyifler nasıl", "Bugün nasıl geçiyor",
            "Sohbet edecek var mı", "Kim aktif", "Konuşalım mı"
        ]
        
        # Mesaj sonları
        self.message_endings = [
            "😊", "💕", "🌟", "✨", "🔥", "💋", "😘", "🥰",
            "Ne dersiniz?", "Katılmak ister misiniz?", "Sohbet edelim",
            "Yazın bana", "DM atın", "Konuşalım"
        ]
        
        # VIP satış varyasyonları
        self.vip_variants = {
            "invitation": [
                "VIP grubuma katılmak ister misin?",
                "Özel VIP kanalımda seni bekliyorum",
                "VIP üyeliğin ile çok daha fazlasına erişebilirsin",
                "Sana özel VIP teklifim var"
            ],
            "benefits": [
                "çok daha özel içerikler var",
                "daha cesur paylaşımlar yapıyorum",
                "özel muamele görürsün",
                "sadece seçkin üyelerim var"
            ],
            "call_to_action": [
                "İlgin varsa yaz",
                "Mesaj at",
                "DM'den ulaş",
                "Kaçırma bu fırsatı"
            ]
        }

    def shuffle_message_structure(self, base_message: str, style: str = "friendly") -> List[str]:
        """Mesaj yapısını karıştırarak varyasyonlar oluştur"""
        variants = []
        
        # 5 farklı varyasyon oluştur
        for i in range(5):
            variant = base_message
            
            # Emoji değiştir
            variant = self._replace_emojis(variant, style)
            
            # Noktalama değiştir
            variant = self._vary_punctuation(variant, i)
            
            # Kelime sırası değiştir (hafif)
            if i >= 2:
                variant = self._vary_word_order(variant)
            
            # Başlangıç/son ekle
            if i >= 3:
                variant = self._add_starter_ending(variant, style)
            
            variants.append(variant)
        
        return variants

    def _replace_emojis(self, message: str, style: str) -> str:
        """Emoji'leri stil bazında değiştir"""
        emoji_set = self.emoji_categories.get(style, self.emoji_categories["friendly"])
        
        # Mevcut emoji'leri bul
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+'
        
        def replace_emoji(match):
            return random.choice(emoji_set)
        
        return re.sub(emoji_pattern, replace_emoji, message)

    def _vary_punctuation(self, message: str, variant_index: int) -> str:
        """Noktalama işaretlerini değiştir"""
        if variant_index == 0:
            return message
        elif variant_index == 1:
            return message.replace("...", ".").replace("!", ".")
        elif variant_index == 2:
            return message.replace(".", "!").replace("?", "!")
        elif variant_index == 3:
            return message.replace(".", "...").replace("!", "...")
        else:
            return message.replace("?", " 😊").replace("!", " 💕")

    def _vary_word_order(self, message: str) -> str:
        """Kelime sırasını hafifçe değiştir"""
        # Basit kelime değişimleri
        replacements = {
            "Merhaba": random.choice(["Selam", "Hey", "Herkese merhaba"]),
            "Nasılsınız": random.choice(["Keyifler nasıl", "Ne yapıyorsunuz", "Nasıl gidiyor"]),
            "Sohbet edelim": random.choice(["Konuşalım", "Muhabbet edelim", "Sohbet yapalım"]),
            "Ne yapıyorsunuz": random.choice(["Neler yapıyorsunuz", "Ne var ne yok", "Nasıl geçiyor"])
        }
        
        for old, new in replacements.items():
            if old in message:
                message = message.replace(old, new)
                break
        
        return message

    def _add_starter_ending(self, message: str, style: str) -> str:
        """Başlangıç ve son ekle"""
        emoji_set = self.emoji_categories.get(style, self.emoji_categories["friendly"])
        
        # Rastgele başlangıç ekle
        if random.random() < 0.3:
            starter = random.choice(self.message_starters)
            if not message.startswith(starter):
                message = f"{starter}! {message}"
        
        # Rastgele son ekle
        if random.random() < 0.4:
            ending = random.choice(emoji_set)
            if not message.endswith(ending):
                message = f"{message} {ending}"
        
        return message

    def create_vip_sales_variants(self, base_concept: str = "general") -> List[str]:
        """VIP satış mesajı varyasyonları oluştur"""
        variants = []
        
        for i in range(5):
            # Rastgele bileşenler seç
            invitation = random.choice(self.vip_variants["invitation"])
            benefit = random.choice(self.vip_variants["benefits"])
            cta = random.choice(self.vip_variants["call_to_action"])
            
            # Farklı yapılar oluştur
            if i == 0:
                # Basit davet
                variant = f"{invitation} 💎"
            elif i == 1:
                # Fayda vurgulu
                variant = f"VIP grubumda {benefit} 🔥 {cta}!"
            elif i == 2:
                # Soru formatı
                variant = f"{invitation} Orada {benefit} 😈"
            elif i == 3:
                # Merak uyandırıcı
                variant = f"Sana özel bir teklifim var... VIP kanalımda {benefit} 💋 {cta}"
            else:
                # Kombinasyon
                variant = f"{invitation} {benefit.capitalize()} 🌟 {cta}!"
            
            # Emoji varyasyonu ekle
            variant = self._replace_emojis(variant, "flirt")
            variants.append(variant)
        
        return variants

    async def create_gpt_enhanced_variants(self, base_message: str, character_style: str, count: int = 3) -> List[str]:
        """GPT ile geliştirilmiş varyasyonlar oluştur"""
        try:
            from gpt.openai_utils import generate_gpt_reply
            
            # GPT prompt'u oluştur
            prompt = f"""
Aşağıdaki mesajın {count} farklı varyasyonunu oluştur. Her varyasyon:
- Aynı anlamı taşımalı ama farklı kelimelerle yazılmalı
- {character_style} karakterine uygun olmalı
- Emoji kullanmalı
- Doğal ve samimi olmalı
- Spam gibi görünmemeli

Orijinal mesaj: "{base_message}"

Sadece varyasyonları listele, başka açıklama yapma.
"""
            
            system_prompt = f"""
Sen {character_style} karakterinde mesaj varyasyonları oluşturan bir asistansın.
Görevin: Verilen mesajın farklı versiyonlarını oluşturmak.
Stil: Doğal, samimi, emoji'li, spam olmayan.
"""
            
            gpt_response = generate_gpt_reply(prompt, system_prompt)
            
            # GPT yanıtını parse et
            variants = []
            lines = gpt_response.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                # Numaraları ve işaretleri temizle
                line = re.sub(r'^\d+[\.\)]\s*', '', line)
                line = re.sub(r'^[-\*]\s*', '', line)
                
                if line and len(line) > 10:  # Çok kısa olanları atla
                    variants.append(line)
            
            # Yeterli varyasyon yoksa manuel ekle
            while len(variants) < count:
                manual_variants = self.shuffle_message_structure(base_message, "friendly")
                variants.extend(manual_variants[:count - len(variants)])
            
            return variants[:count]
            
        except Exception as e:
            log_event("template_shuffler", f"❌ GPT varyasyon hatası: {e}")
            # Fallback: manuel varyasyonlar
            return self.shuffle_message_structure(base_message, "friendly")[:count]

    def get_anti_spam_message_set(self, base_messages: List[str], character_style: str = "friendly") -> List[str]:
        """Anti-spam için mesaj seti oluştur"""
        all_variants = []
        
        for base_message in base_messages:
            # Her mesaj için 3 varyasyon oluştur
            variants = self.shuffle_message_structure(base_message, character_style)
            all_variants.extend(variants[:3])
        
        # VIP satış mesajları ekle
        vip_variants = self.create_vip_sales_variants()
        all_variants.extend(vip_variants[:2])  # 2 VIP mesajı ekle
        
        # Rastgele karıştır
        random.shuffle(all_variants)
        
        # Tekrarları kaldır
        unique_variants = []
        for variant in all_variants:
            if variant not in unique_variants:
                unique_variants.append(variant)
        
        return unique_variants

    def analyze_message_diversity(self, messages: List[str]) -> Dict:
        """Mesaj çeşitliliğini analiz et"""
        if not messages:
            return {"diversity_score": 0, "unique_words": 0, "emoji_variety": 0}
        
        # Benzersiz kelimeler
        all_words = []
        for msg in messages:
            words = re.findall(r'\b\w+\b', msg.lower())
            all_words.extend(words)
        
        unique_words = len(set(all_words))
        total_words = len(all_words)
        
        # Emoji çeşitliliği
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+'
        all_emojis = []
        for msg in messages:
            emojis = re.findall(emoji_pattern, msg)
            all_emojis.extend(emojis)
        
        unique_emojis = len(set(all_emojis))
        
        # Çeşitlilik skoru
        diversity_score = (unique_words / max(total_words, 1)) * 100
        
        return {
            "diversity_score": round(diversity_score, 2),
            "unique_words": unique_words,
            "total_words": total_words,
            "emoji_variety": unique_emojis,
            "message_count": len(messages)
        }

# Global instance
template_shuffler = TemplateShuffler() 