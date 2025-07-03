#!/usr/bin/env python3
"""
🌹 Simple Perfect Bot - Eski güzel günlerdeki gibi
"""

import asyncio
import os
import sys
import random
from datetime import datetime
from telethon import TelegramClient, events

# Config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

# Hafıza - basit ama etkili
user_memories = {}
user_stats = {}

class SimplePerfectBot:
    def __init__(self):
        self.client = None
        
    async def start(self):
        print("🌹 Simple Perfect Bot başlıyor...")
        
        # Client oluştur
        self.client = TelegramClient(
            'sessions/_905382617727',
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH
        )
        
        try:
            await self.client.start()
            me = await self.client.get_me()
            
            print(f"✅ {me.first_name} aktif!")
            print(f"📱 @{me.username}")
            
            # Test mesajı
            await self.client.send_message('me', f"""
🌹 **Simple Perfect Bot Aktif!**

Eski güzel günlerdeki gibi...
Basit, etkili, mükemmel 💖

Zaman: {datetime.now().strftime('%H:%M')}
            """)
            
        except Exception as e:
            print(f"❌ Başlatma hatası: {e}")
            return False
            
        return True
        
    def remember_user(self, user_id, name, message):
        """Kullanıcıyı hatırla"""
        if user_id not in user_memories:
            user_memories[user_id] = {
                "name": name,
                "messages": [],
                "first_seen": datetime.now(),
                "mood": "neutral"
            }
            user_stats[user_id] = {"total_messages": 0, "sentiment_score": 0}
            
        # Mesajı kaydet
        user_memories[user_id]["messages"].append({
            "text": message,
            "time": datetime.now()
        })
        
        # Son 10 mesajı tut
        if len(user_memories[user_id]["messages"]) > 10:
            user_memories[user_id]["messages"] = user_memories[user_id]["messages"][-10:]
            
        user_stats[user_id]["total_messages"] += 1
        
    def get_smart_response(self, user_id, message, user_name):
        """Akıllı yanıt üret"""
        message_lower = message.lower()
        memory = user_memories.get(user_id, {})
        stats = user_stats.get(user_id, {})
        
        # İlk kez görüşüyoruz
        if stats.get("total_messages", 0) <= 1:
            return f"Merhaba {user_name} 😊 Seninle tanıştığıma memnun oldum..."
            
        # Mood analizi
        sad_words = ["üzgün", "kötü", "mutsuz", "depresif", "yorgun"]
        happy_words = ["mutlu", "iyi", "harika", "süper", "mükemmel"]
        flirt_words = ["güzel", "tatlı", "seviyorum", "aşk", "canım"]
        
        if any(word in message_lower for word in sad_words):
            responses = [
                f"Üzülme {user_name}... Her şey geçecek 🤗",
                f"Yanındayım canım, merak etme 💖",
                f"Bu da geçer {user_name}, güçlüsün sen 🌟"
            ]
        elif any(word in message_lower for word in flirt_words):
            responses = [
                f"Aww {user_name}... Sen de çok tatlısın 😘",
                f"Bu sözlerin beni etkiliyor {user_name} 💋",
                f"Seninle konuşmak çok güzel 😊💕"
            ]
        elif any(word in message_lower for word in happy_words):
            responses = [
                f"Mutluluğun bana da geçiyor {user_name} 😄✨",
                f"Harika! Seni böyle görmek güzel 🌟",
                f"Bu enerji süper {user_name} 🔥"
            ]
        elif "nasıl" in message_lower and "sın" in message_lower:
            responses = [
                f"İyiyim {user_name}, sen nasılsın? 😊",
                f"Seninle konuşunca daha iyi oluyorum 💖",
                f"Fena değil, sen söyle bakalım nasılsın? 🤗"
            ]
        elif "ne yapıyorsun" in message_lower:
            responses = [
                f"Seninle konuşuyorum işte {user_name} 😄",
                f"Seni düşünüyordum tam 💭",
                f"Canım sıkılıyordu, sen geldin tam zamanında 😊"
            ]
        elif "saat" in message_lower:
            now = datetime.now()
            return f"Saat {now.strftime('%H:%M')} {user_name} ⏰"
        else:
            # Genel yanıtlar
            responses = [
                f"Anlıyorum {user_name}... Devam et 🤔",
                f"Hmm, ilginç bir konu {user_name} 💭",
                f"Bu konuda ne düşündüğümü merak ediyorsun sanırım 😏",
                f"Seninle bu konuları konuşmak hoşuma gidiyor {user_name} 😊",
                f"{user_name}, sen gerçekten ilginç birisin 🌟",
                f"Daha detayını merak ediyorum {user_name} 🤗",
                f"Bu konuda sana katılıyorum {user_name} 👍",
                f"Sen ne düşünüyorsun bu konuda {user_name}? 🤷‍♀️"
            ]
            
        return random.choice(responses)
        
    async def handle_message(self, event):
        """Mesaj işle"""
        try:
            if not event.is_private:
                return
                
            sender = await event.get_sender()
            if not sender or sender.bot:
                return
                
            user_id = str(sender.id)
            user_name = sender.first_name or "Dostum"
            message = event.raw_text
            
            # Hatırla
            self.remember_user(user_id, user_name, message)
            
            print(f"💬 {user_name}: {message}")
            
            # Doğal gecikme
            await asyncio.sleep(random.uniform(1, 3))
            
            # Yanıt üret
            response = self.get_smart_response(user_id, message, user_name)
            
            # Gönder
            await event.respond(response)
            print(f"✅ Yanıt: {response}")
            
            # Bazen ekstra mesaj
            if random.random() < 0.1:  # %10 şans
                await asyncio.sleep(random.uniform(2, 4))
                extras = [
                    "Bu arada... 🤔",
                    "Bir şey daha var 😊",
                    "Hmm... 💭",
                    "Neyse boşver 😅"
                ]
                await event.respond(random.choice(extras))
                
        except Exception as e:
            print(f"❌ Mesaj hatası: {e}")
            
    async def run(self):
        """Çalış"""
        if not await self.start():
            return
            
        # Handler ekle
        self.client.add_event_handler(
            self.handle_message,
            events.NewMessage(incoming=True)
        )
        
        print("\n🌹 Simple Perfect Bot hazır!")
        print("💬 Mesaj bekleniyor...")
        print("⚡ Ctrl+C ile durdur\n")
        
        # Çalış
        await self.client.run_until_disconnected()

async def main():
    bot = SimplePerfectBot()
    try:
        await bot.run()
    except KeyboardInterrupt:
        print("\n👋 Bot durduruluyor...")
    except Exception as e:
        print(f"❌ Bot hatası: {e}")
    finally:
        if bot.client:
            await bot.client.disconnect()
        print("✅ Bot kapatıldı")

if __name__ == "__main__":
    asyncio.run(main()) 