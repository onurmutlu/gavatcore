#!/usr/bin/env python3
"""
🌹 Perfect GPT Bot - Karakter sistemi + GPT-4 entegrasyonu
"""

import asyncio
import os
import sys
import random
import json
from datetime import datetime
from telethon import TelegramClient, events
import openai

# Config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, OPENAI_API_KEY

# OpenAI setup
openai.api_key = OPENAI_API_KEY

# Karakter sistemi
CHARACTERS = {
    "lara": {
        "name": "Lara",
        "personality": "Çok tatlı, sevimli, biraz utangaç ama sıcakkanlı bir kız. Emoji kullanmayı seviyor, romantik konuşmalar yapıyor.",
        "style": "Genç, modern dil kullanır. 'ya', 'işte', 'falan' gibi kelimeler kullanır. Çok samimi ve doğal.",
        "mood": "flirty_sweet",
        "example_responses": [
            "Aww çok tatlısın ya 😊💕",
            "Sen gerçekten çok ilginç birisin 🌟",
            "Seninle konuşmak çok hoş 💖"
        ]
    },
    "babagavat": {
        "name": "Baba Gavat", 
        "personality": "Bilge, tecrübeli, bazen ironik ama herzaman samimi. Hayat tecrübesi olan biri gibi konuşur.",
        "style": "Daha olgun dil, bazen argo, genelde öğüt verici. 'Evlat', 'oğlum' gibi hitaplar kullanır.",
        "mood": "wise_friendly",
        "example_responses": [
            "Evlat, bu konuda sana şunu söyleyeyim...",
            "Oğlum, hayat tecrübesi konuşuyor şimdi",
            "Bu işin püf noktası şurada..."
        ]
    }
}

# Hafıza sistemi
user_memories = {}
conversation_history = {}

class PerfectGPTBot:
    def __init__(self):
        self.client = None
        self.current_character = "lara"
        
    async def start(self):
        print("🤖 Perfect GPT Bot başlıyor...")
        
        self.client = TelegramClient(
            'sessions/_905382617727',
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH
        )
        
        try:
            await self.client.start()
            me = await self.client.get_me()
            
            print(f"✅ {me.first_name} aktif!")
            print(f"🎭 Aktif karakter: {CHARACTERS[self.current_character]['name']}")
            
            await self.client.send_message('me', f"""
🤖 **Perfect GPT Bot Aktif!**

🎭 Karakter: {CHARACTERS[self.current_character]['name']}
🧠 GPT-4 Entegreli
💬 Doğal konuşma
🕒 {datetime.now().strftime('%H:%M')}
            """)
            
        except Exception as e:
            print(f"❌ Başlatma hatası: {e}")
            return False
            
        return True
        
    def get_character_prompt(self, character_key):
        """Karakter için sistem promptu"""
        char = CHARACTERS[character_key]
        return f"""Sen {char['name']} adında bir kişisin.

KİŞİLİK: {char['personality']}
KONUŞMA TARZI: {char['style']}
MOOD: {char['mood']}

KURALLAR:
1. Her zaman bu karakterin kişiliğinde kal
2. Doğal ve samimi konuş
3. Çok uzun mesajlar yazma, kısa tut
4. Emoji kullan ama abartma
5. Türkçe konuş
6. İnsan gibi davran, bot olduğunu belli etme

ÖRNEK YANIT STİLİ: {', '.join(char['example_responses'])}

Şimdi bu karakter olarak doğal bir şekilde yanıt ver."""

    async def get_gpt_response(self, message, user_name, character_key):
        """GPT-4'ten yanıt al"""
        try:
            # Konuşma geçmişini al
            history = conversation_history.get(user_name, [])
            
            # Sistem promptu
            system_prompt = self.get_character_prompt(character_key)
            
            # Mesajları hazırla
            messages = [{"role": "system", "content": system_prompt}]
            
            # Son 5 konuşmayı ekle
            for h in history[-5:]:
                messages.append({"role": "user", "content": f"{user_name}: {h['user']}"})
                messages.append({"role": "assistant", "content": h['bot']})
            
            # Şu anki mesaj
            messages.append({"role": "user", "content": f"{user_name}: {message}"})
            
            # GPT'ye sor
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: openai.ChatCompletion.create(
                    model="gpt-4-turbo-preview",
                    messages=messages,
                    max_tokens=200,
                    temperature=0.8
                )
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ GPT hatası: {e}")
            # Fallback yanıtlar
            char = CHARACTERS[character_key]
            return random.choice(char['example_responses'])
            
    def save_conversation(self, user_name, user_message, bot_response):
        """Konuşmayı kaydet"""
        if user_name not in conversation_history:
            conversation_history[user_name] = []
            
        conversation_history[user_name].append({
            "user": user_message,
            "bot": bot_response,
            "time": datetime.now()
        })
        
        # Son 20 konuşmayı tut
        if len(conversation_history[user_name]) > 20:
            conversation_history[user_name] = conversation_history[user_name][-20:]
            
    def remember_user(self, user_id, name):
        """Kullanıcıyı hatırla"""
        if user_id not in user_memories:
            user_memories[user_id] = {
                "name": name,
                "first_seen": datetime.now(),
                "total_messages": 0,
                "favorite_topics": [],
                "mood_history": []
            }
        user_memories[user_id]["total_messages"] += 1
        
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
            
            # Kullanıcıyı hatırla
            self.remember_user(user_id, user_name)
            
            print(f"💬 {user_name}: {message}")
            
            # Karakter değiştirme komutu
            if message.lower().startswith("/karakter"):
                parts = message.split()
                if len(parts) > 1 and parts[1] in CHARACTERS:
                    self.current_character = parts[1]
                    char_name = CHARACTERS[self.current_character]['name']
                    await event.respond(f"🎭 Karakter değiştirildi: {char_name}")
                    return
                else:
                    chars = ", ".join(CHARACTERS.keys())
                    await event.respond(f"🎭 Mevcut karakterler: {chars}")
                    return
            
            # Typing efekti
            await asyncio.sleep(random.uniform(1, 2))
            
            # GPT'den yanıt al
            response = await self.get_gpt_response(message, user_name, self.current_character)
            
            # Konuşmayı kaydet
            self.save_conversation(user_name, message, response)
            
            # Yanıt gönder
            await event.respond(response)
            print(f"✅ {CHARACTERS[self.current_character]['name']}: {response}")
            
            # Bazen ekstra dokunuş
            if random.random() < 0.05:  # %5 şans
                await asyncio.sleep(random.uniform(2, 4))
                extras = [
                    "Bu arada... 🤔",
                    "Hmm, bir şey daha var 💭",
                    "Neyse, geçti 😅"
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
        
        print("\n🤖 Perfect GPT Bot hazır!")
        print(f"🎭 Aktif karakter: {CHARACTERS[self.current_character]['name']}")
        print("💬 GPT-4 ile doğal konuşma")
        print("⚡ Ctrl+C ile durdur")
        print("🎭 /karakter [isim] ile karakter değiştir\n")
        
        # Çalış
        await self.client.run_until_disconnected()

async def main():
    bot = PerfectGPTBot()
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