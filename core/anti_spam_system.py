"""
🛡️ Anti Spam System - Spam koruma sistemi
"""
from telethon import events
from datetime import datetime, timedelta
import re

class AntiSpamSystem:
    def __init__(self):
        self.message_history = {}  # {user_id: [(timestamp, message), ...]}
        self.banned_words = set()  # Yasaklı kelimeler
        self.max_messages = 5  # 1 dakikada max mesaj
        self.time_window = 60  # 60 saniye
        self.load_banned_words()
        
    def load_banned_words(self):
        """Yasaklı kelimeleri yükle"""
        try:
            # Varsayılan yasaklı kelimeler
            self.banned_words = {
                'spam', 'reklam', 'kazan', 'bedava',
                'para', 'kumar', 'bahis', 'iddaa',
                'lottery', 'winner', 'prize', 'money'
            }
        except Exception as e:
            print(f"Banned Words Load Error: {e}")
            
    async def is_spam(self, event: events.NewMessage.Event) -> bool:
        """Mesajın spam olup olmadığını kontrol et"""
        try:
            user_id = event.sender_id
            message = event.message.text.lower()
            now = datetime.now()
            
            # Kullanıcı geçmişini kontrol et
            if user_id not in self.message_history:
                self.message_history[user_id] = []
                
            # Eski mesajları temizle
            self.message_history[user_id] = [
                (ts, msg) for ts, msg in self.message_history[user_id]
                if now - ts < timedelta(seconds=self.time_window)
            ]
            
            # Spam kontrolleri
            if await self.check_message_frequency(user_id, now):
                return True
                
            if await self.check_banned_words(message):
                return True
                
            if await self.check_message_pattern(message):
                return True
                
            # Mesajı geçmişe ekle
            self.message_history[user_id].append((now, message))
            return False
            
        except Exception as e:
            print(f"Spam Check Error: {e}")
            return False
            
    async def check_message_frequency(self, user_id: int, now: datetime) -> bool:
        """Mesaj sıklığını kontrol et"""
        try:
            recent_messages = [
                ts for ts, _ in self.message_history[user_id]
                if now - ts < timedelta(seconds=self.time_window)
            ]
            
            return len(recent_messages) >= self.max_messages
            
        except Exception as e:
            print(f"Frequency Check Error: {e}")
            return False
            
    async def check_banned_words(self, message: str) -> bool:
        """Yasaklı kelimeleri kontrol et"""
        try:
            words = set(re.findall(r'\w+', message.lower()))
            return bool(words & self.banned_words)
            
        except Exception as e:
            print(f"Banned Words Check Error: {e}")
            return False
            
    async def check_message_pattern(self, message: str) -> bool:
        """Mesaj desenini kontrol et"""
        try:
            # Tekrar eden karakterler
            if re.search(r'(.)\1{4,}', message):
                return True
                
            # Çok uzun mesajlar
            if len(message) > 1000:
                return True
                
            # Çok fazla emoji
            emoji_count = len(re.findall(r'[\U0001F300-\U0001F9FF]', message))
            if emoji_count > 10:
                return True
                
            return False
            
        except Exception as e:
            print(f"Pattern Check Error: {e}")
            return False
            
    async def enable(self):
        """Spam korumasını aktifleştir"""
        try:
            self.max_messages = 5
            self.time_window = 60
            print("✅ Spam koruması aktif edildi!")
            
        except Exception as e:
            print(f"Enable Error: {e}")
            
    async def disable(self):
        """Spam korumasını devre dışı bırak"""
        try:
            self.max_messages = 999999
            self.time_window = 1
            print("✅ Spam koruması devre dışı bırakıldı!")
            
        except Exception as e:
            print(f"Disable Error: {e}")
            
    async def add_banned_word(self, word: str):
        """Yasaklı kelime ekle"""
        try:
            self.banned_words.add(word.lower())
            print(f"✅ '{word}' yasaklı kelimelere eklendi!")
            
        except Exception as e:
            print(f"Add Banned Word Error: {e}")
            
    async def remove_banned_word(self, word: str):
        """Yasaklı kelimeyi kaldır"""
        try:
            self.banned_words.discard(word.lower())
            print(f"✅ '{word}' yasaklı kelimelerden kaldırıldı!")
            
        except Exception as e:
            print(f"Remove Banned Word Error: {e}")
            
    async def get_stats(self) -> dict:
        """Spam istatistiklerini getir"""
        try:
            return {
                "max_messages": self.max_messages,
                "time_window": self.time_window,
                "banned_words": len(self.banned_words),
                "active_users": len(self.message_history)
            }
            
        except Exception as e:
            print(f"Stats Error: {e}")
            return {} 