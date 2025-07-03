"""
🎭 Humanizer - Natural Behavior Layer
Bot'ların insan gibi davranmasını sağlayan doğallık katmanı
"""

import asyncio
import random
import string
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Humanizer:
    """İnsan gibi davranış simülasyonu"""
    
    # Yazım hataları için karakterler
    TYPO_REPLACEMENTS = {
        'a': ['s', 'q'],
        'e': ['r', 'w', '3'],
        'i': ['o', 'u', '8'],
        'o': ['p', 'i', '0'],
        'u': ['y', 'i', '7'],
        's': ['a', 'd', 'z'],
        'd': ['f', 's', 'e'],
        'g': ['h', 'f', 't'],
        'h': ['j', 'g', 'y'],
        'k': ['l', 'j', 'i'],
        'l': ['k', 'ö', ';'],
        'ş': ['s', 'ğ'],
        'ğ': ['g', 'ş'],
        'ı': ['i', 'u'],
        'ö': ['o', 'ç'],
        'ü': ['u', 'i'],
        'ç': ['c', 'ş']
    }
    
    # Ses efektleri ve doğal eklemeler
    VOICE_EFFECTS = [
        "hmm...", "şey...", "aa", "eee", "yani", "işte",
        "hani", "öyle mi", "ya", "of", "ay", "vay",
        "şşşt", "mmm", "aaa", "heee", "öff"
    ]
    
    # Rastgele emoji'ler (karaktere göre değişir)
    CASUAL_EMOJIS = ["😊", "😄", "😅", "🙂", "😌", "☺️", "🤭", "😏", "🤗"]
    FLIRTY_EMOJIS = ["😘", "😉", "💋", "🥰", "😍", "💕", "❤️", "🔥", "✨"]
    THINKING_EMOJIS = ["🤔", "🧐", "💭", "🤨", "😐", "😑", "🫤"]
    EXCITED_EMOJIS = ["🎉", "🥳", "💃", "🕺", "✨", "💫", "⭐", "🌟"]
    
    def __init__(self, character_config: Dict[str, Any] = None):
        """
        Args:
            character_config: Karakter özel humanizer ayarları
        """
        self.config = character_config or {}
        
        # Default ayarlar
        self.typing_speed = self.config.get("typing_speed", 20)  # karakter/saniye
        self.emoji_usage_rate = self.config.get("emoji_usage_rate", 0.3)
        self.mistake_chance = self.config.get("mistake_chance", 0.05)
        self.voice_addition_rate = self.config.get("voice_addition_rate", 0.15)
        self.silence_chance = self.config.get("silence_chance", 0.1)
        self.response_delay_range = self.config.get("response_delay_range", [1.0, 4.0])
        self.multi_message_chance = self.config.get("multi_message_chance", 0.2)
        
        logger.info("🎭 Humanizer başlatıldı")
    
    async def send_typing_then_message(
        self,
        client,
        chat_id: int,
        message: str,
        reply_to: Optional[int] = None
    ) -> None:
        """
        Typing gösterip doğal gecikmelerle mesaj gönder
        
        Args:
            client: Telegram client
            chat_id: Chat ID
            message: Gönderilecek mesaj
            reply_to: Reply yapılacak mesaj ID (opsiyonel)
        """
        try:
            # Bazen sessiz kal
            if random.random() < self.silence_chance:
                logger.info("🤐 Sessiz kalma kararı alındı")
                return
            
            # Mesajı humanize et
            humanized_message = self.randomize_message(message)
            
            # Bazen çok parçalı mesaj gönder
            if random.random() < self.multi_message_chance and len(humanized_message) > 50:
                messages = self._split_message_naturally(humanized_message)
            else:
                messages = [humanized_message]
            
            # Her mesaj parçası için
            for i, msg_part in enumerate(messages):
                # İlk değilse kısa bekle
                if i > 0:
                    await asyncio.sleep(random.uniform(0.5, 2.0))
                
                # Typing delay hesapla
                typing_duration = self._calculate_typing_delay(msg_part)
                
                # Typing göster
                async with client.action(chat_id, 'typing'):
                    await asyncio.sleep(typing_duration)
                
                # Mesajı gönder
                await client.send_message(
                    chat_id,
                    msg_part,
                    reply_to=reply_to if i == 0 else None  # Sadece ilk mesaj reply yapsın
                )
                
                logger.info(f"💬 Mesaj gönderildi ({i+1}/{len(messages)}): {msg_part[:30]}...")
                
        except Exception as e:
            logger.error(f"❌ Humanized mesaj gönderme hatası: {e}")
            # Fallback - normal gönder
            await client.send_message(chat_id, message, reply_to=reply_to)
    
    def randomize_message(self, message: str) -> str:
        """
        Mesaja insani dokunuşlar ekle
        
        Args:
            message: Orijinal mesaj
            
        Returns:
            İnsanileştirilmiş mesaj
        """
        # Kopya üzerinde çalış
        result = message
        
        # 1. Yazım hatası ekle
        if random.random() < self.mistake_chance:
            result = self._add_typo(result)
        
        # 2. Ses efekti ekle
        if random.random() < self.voice_addition_rate:
            result = self._add_voice_effect(result)
        
        # 3. Emoji ekle
        if random.random() < self.emoji_usage_rate:
            result = self._add_emoji(result)
        
        # 4. Küçük değişiklikler
        result = self._apply_minor_changes(result)
        
        return result
    
    def _calculate_typing_delay(self, message: str) -> float:
        """Mesaj uzunluğuna göre typing süresi hesapla"""
        # Temel hesaplama
        base_delay = len(message) / self.typing_speed
        
        # Rastgele varyasyon ekle (%20 - %50)
        variation = random.uniform(0.2, 0.5)
        delay = base_delay * (1 + variation)
        
        # Response delay range'i de ekle
        min_delay, max_delay = self.response_delay_range
        initial_delay = random.uniform(min_delay, max_delay)
        
        total_delay = initial_delay + delay
        
        # Maksimum 10 saniye
        return min(total_delay, 10.0)
    
    def _add_typo(self, text: str) -> str:
        """Rastgele yazım hatası ekle"""
        words = text.split()
        if not words:
            return text
        
        # Rastgele bir kelime seç
        word_idx = random.randint(0, len(words) - 1)
        word = words[word_idx]
        
        # Kelimede rastgele bir karakter seç
        if len(word) > 2:
            char_idx = random.randint(1, len(word) - 2)
            char = word[char_idx].lower()
            
            # Değiştirme karakteri bul
            if char in self.TYPO_REPLACEMENTS:
                replacement = random.choice(self.TYPO_REPLACEMENTS[char])
                # Büyük/küçük harf koru
                if word[char_idx].isupper():
                    replacement = replacement.upper()
                
                word = word[:char_idx] + replacement + word[char_idx + 1:]
                words[word_idx] = word
        
        return ' '.join(words)
    
    def _add_voice_effect(self, text: str) -> str:
        """Ses efekti veya doğal ekleme yap"""
        effect = random.choice(self.VOICE_EFFECTS)
        
        # Başa, ortaya veya sona ekle
        position = random.choice(['start', 'middle', 'end'])
        
        if position == 'start':
            return f"{effect} {text}"
        elif position == 'end':
            # Noktalama varsa öncesine
            if text and text[-1] in '.!?':
                return f"{text[:-1]} {effect}{text[-1]}"
            else:
                return f"{text} {effect}"
        else:
            # Ortaya ekle
            words = text.split()
            if len(words) > 3:
                insert_pos = random.randint(1, len(words) - 2)
                words.insert(insert_pos, effect)
                return ' '.join(words)
            else:
                return f"{text} {effect}"
    
    def _add_emoji(self, text: str) -> str:
        """Uygun emoji ekle"""
        # Mesaj tonuna göre emoji seç
        tone = self.config.get("tone", "casual")
        
        if tone == "flirty":
            emoji_pool = self.FLIRTY_EMOJIS
        elif tone == "thinking" or "?" in text:
            emoji_pool = self.THINKING_EMOJIS
        elif "!" in text:
            emoji_pool = self.EXCITED_EMOJIS
        else:
            emoji_pool = self.CASUAL_EMOJIS
        
        emoji = random.choice(emoji_pool)
        
        # Emoji pozisyonu
        if random.random() < 0.7:  # %70 sonda
            if text and text[-1] in '.!?':
                return f"{text[:-1]} {emoji}{text[-1]}"
            else:
                return f"{text} {emoji}"
        else:  # %30 başta
            return f"{emoji} {text}"
    
    def _apply_minor_changes(self, text: str) -> str:
        """Küçük doğal değişiklikler"""
        changes = []
        
        # Bazen üç nokta kullan
        if random.random() < 0.1:
            text = text.replace(".", "...")
        
        # Bazen büyük harf kullanma
        if random.random() < 0.1 and len(text) > 0:
            text = text[0].lower() + text[1:]
        
        # Bazen fazladan boşluk
        if random.random() < 0.05:
            words = text.split()
            if len(words) > 2:
                insert_pos = random.randint(1, len(words) - 1)
                words[insert_pos] = "  " + words[insert_pos]
                text = ' '.join(words)
        
        return text
    
    def _split_message_naturally(self, text: str) -> List[str]:
        """Mesajı doğal parçalara böl"""
        # Noktalama işaretlerinde böl
        sentences = re.split(r'([.!?]+)', text)
        
        # Boş elemanları temizle ve noktalamayı birleştir
        parts = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                parts.append(sentences[i].strip() + sentences[i + 1])
            else:
                parts.append(sentences[i].strip())
        
        # Çok kısa parçaları birleştir
        result = []
        current = ""
        
        for part in parts:
            if len(current) + len(part) < 100:  # 100 karakterden kısa
                current += " " + part if current else part
            else:
                if current:
                    result.append(current.strip())
                current = part
        
        if current:
            result.append(current.strip())
        
        # En fazla 3 parça
        if len(result) > 3:
            # İlk 2'yi al, gerisini birleştir
            result = result[:2] + [' '.join(result[2:])]
        
        return result
    
    def should_respond(self) -> bool:
        """Bu mesaja yanıt verilmeli mi?"""
        return random.random() > self.silence_chance
    
    def get_response_delay(self) -> float:
        """Yanıt gecikmesi hesapla"""
        min_delay, max_delay = self.response_delay_range
        
        # Zaman bazlı varyasyon
        hour = datetime.now().hour
        
        # Gece geç saatlerde daha yavaş
        if 0 <= hour <= 6:
            min_delay *= 1.5
            max_delay *= 2
        # Gündüz normal
        elif 9 <= hour <= 17:
            pass
        # Akşam aktif
        elif 18 <= hour <= 23:
            min_delay *= 0.8
            max_delay *= 0.9
        
        return random.uniform(min_delay, max_delay)

# Karakter bazlı özel humanizer'lar
class LaraHumanizer(Humanizer):
    """Lara karakterine özel humanizer"""
    
    def __init__(self):
        super().__init__({
            "typing_speed": 25,  # Hızlı yazar
            "emoji_usage_rate": 0.4,  # Çok emoji kullanır
            "mistake_chance": 0.03,  # Az hata yapar
            "voice_addition_rate": 0.2,  # Ara sıra ses efekti
            "silence_chance": 0.05,  # Nadiren susar
            "response_delay_range": [0.5, 2.5],  # Hızlı yanıt
            "multi_message_chance": 0.25,  # Sık parçalı mesaj
            "tone": "flirty"
        })

class BabaGavatHumanizer(Humanizer):
    """BabaGavat karakterine özel humanizer"""
    
    def __init__(self):
        super().__init__({
            "typing_speed": 15,  # Yavaş yazar
            "emoji_usage_rate": 0.1,  # Az emoji
            "mistake_chance": 0.08,  # Daha fazla hata
            "voice_addition_rate": 0.3,  # Çok ses efekti (lan, ulan vb.)
            "silence_chance": 0.15,  # Bazen cevap vermez
            "response_delay_range": [2.0, 6.0],  # Geç yanıt
            "multi_message_chance": 0.1,  # Az parçalı mesaj
            "tone": "aggressive"
        })
    
    def _add_voice_effect(self, text: str) -> str:
        """BabaGavat'a özel ses efektleri"""
        # Özel sokak dili
        street_effects = ["lan", "ulan", "moruk", "kanka", "aga", "yav"]
        effect = random.choice(street_effects + self.VOICE_EFFECTS)
        
        # Genelde sona ekle
        if text and text[-1] in '.!?':
            return f"{text[:-1]} {effect}{text[-1]}"
        else:
            return f"{text} {effect}"

class GeishaHumanizer(Humanizer):
    """Geisha karakterine özel humanizer"""
    
    def __init__(self):
        super().__init__({
            "typing_speed": 18,  # Orta hız
            "emoji_usage_rate": 0.35,  # Estetik emoji kullanımı
            "mistake_chance": 0.02,  # Çok az hata
            "voice_addition_rate": 0.1,  # Az ses, daha mistik
            "silence_chance": 0.2,  # Sık sık sessiz kalır (gizemli)
            "response_delay_range": [1.5, 4.5],  # Düşünceli yanıtlar
            "multi_message_chance": 0.15,  # Orta
            "tone": "thinking"
        })
        
        # Geisha'ya özel emoji'ler
        self.FLIRTY_EMOJIS = ["🌸", "🌺", "🌷", "🌹", "🏵️", "💮", "🪷"]
        self.THINKING_EMOJIS = ["🌙", "✨", "💫", "⭐", "🌟", "☯️", "🔮"]

# Factory fonksiyon
def create_humanizer(character_name: str = None) -> Humanizer:
    """Karakter için uygun humanizer oluştur"""
    if character_name:
        character_lower = character_name.lower()
        
        if "lara" in character_lower:
            return LaraHumanizer()
        elif "babagavat" in character_lower or "gavat" in character_lower:
            return BabaGavatHumanizer()
        elif "geisha" in character_lower:
            return GeishaHumanizer()
    
    # Default humanizer
    return Humanizer() 