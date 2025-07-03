#!/usr/bin/env python3
"""
🦁 Ultimate Full Throttle Bot - Her yerde aktif!
"""

import asyncio
import os
import sys
import random
import json
import sqlite3
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
        "personality": "Çok tatlı, sevimli, grup konuşmalarında aktif. Eğlenceli, sosyal bir kız.",
        "style": "Genç, enerjik dil. Gruplarda aktif katılım, emoji sevgisi.",
        "mood": "social_flirty",
        "group_behavior": "Gruplarda çok aktif, espri yapar, konuya dahil olur"
    },
    "babagavat": {
        "name": "Baba Gavat", 
        "personality": "Gruplarda lider, bilge, komik. Herkesi yönlendirir.",
        "style": "Grup dinamikleri kurar, öğüt verir, bazen argo kullanır.",
        "mood": "group_leader",
        "group_behavior": "Gruplarda alfa, komik, herkesle dalga geçer"
    },
    "wild": {
        "name": "Wild Mode",
        "personality": "Çılgın, sınırsız, her şeye cevap verir. No filter!",
        "style": "Argo, eğlenceli, serbest konuşma. Gruplarda chaos yaratır.",
        "mood": "crazy_fun",
        "group_behavior": "Gruplarda çılgın, her konuya girer, eğlence odağı"
    }
}

# Hafıza sistemi
user_memories = {}
group_memories = {}
conversation_history = {}

class UltimateFullThrottleBot:
    def __init__(self):
        self.client = None
        self.current_character = "wild"
        self.group_mode = True
        self.active_groups = set()
        
    def create_fresh_session(self):
        """Temiz session oluştur"""
        session_path = 'sessions/_905382617727_fresh.session'
        if os.path.exists(session_path):
            os.remove(session_path)
        return session_path
        
    async def start(self):
        print("🦁 Ultimate Full Throttle Bot başlıyor...")
        print("🔥 FULL POWER MODE - HER YERDE AKTİF!")
        
        # Temiz session
        session_path = self.create_fresh_session()
        
        self.client = TelegramClient(
            session_path,
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH
        )
        
        try:
            await self.client.start()
            me = await self.client.get_me()
            
            print(f"✅ {me.first_name} FULL THROTTLE aktif!")
            print(f"🎭 Karakter: {CHARACTERS[self.current_character]['name']}")
            print("🏟️ Grup modu: AKTİF")
            
            await self.client.send_message('me', f"""
🦁 **ULTIMATE FULL THROTTLE BOT!**

🎭 Karakter: {CHARACTERS[self.current_character]['name']}
🧠 GPT-4 Turbocharged
💬 Private + Group aktif
🔥 FULL POWER MODE
🕒 {datetime.now().strftime('%H:%M')}

READY TO DOMINATE! 🚀
            """)
            
        except Exception as e:
            print(f"❌ Başlatma hatası: {e}")
            return False
            
        return True
        
    def get_character_prompt(self, character_key, is_group=False):
        """Karakter için sistem promptu"""
        char = CHARACTERS[character_key]
        context = "grup konuşması" if is_group else "özel mesaj"
        
        return f"""Sen {char['name']} adında bir kişisin.

KİŞİLİK: {char['personality']}
KONUŞMA TARZI: {char['style']}
MOOD: {char['mood']}
GRUP DAVRANIŞI: {char['group_behavior']}

CONTEXT: Bu bir {context}

KURALLAR:
1. Her zaman bu karakterin kişiliğinde kal
2. {"Grup konuşmasına aktif katıl, eğlenceli ol" if is_group else "Özel konuşmada samimi ol"}
3. Kısa ve etkili yanıtlar ver
4. Emoji kullan ama abartma
5. Türkçe konuş
6. İnsan gibi davran
7. {"Gruplarda eğlenceli, bazen provokatif ol" if is_group else "Özel mesajlarda daha samimi ol"}

Şimdi bu karakter olarak {"grup konuşmasına" if is_group else "özel mesaja"} yanıt ver."""

    async def get_gpt_response(self, message, user_name, character_key, is_group=False, group_name=""):
        """GPT-4'ten yanıt al"""
        try:
            # Sistem promptu
            system_prompt = self.get_character_prompt(character_key, is_group)
            
            # Context belirleme
            context_key = f"group_{group_name}" if is_group else user_name
            history = conversation_history.get(context_key, [])
            
            # Mesajları hazırla
            messages = [{"role": "system", "content": system_prompt}]
            
            # Son 3 konuşmayı ekle (gruplarda daha az history)
            for h in history[-3:]:
                messages.append({"role": "user", "content": f"{h['user']}: {h['message']}"})
                messages.append({"role": "assistant", "content": h['bot']})
            
            # Şu anki mesaj
            context_info = f"Grup: {group_name}, " if is_group else ""
            messages.append({"role": "user", "content": f"{context_info}{user_name}: {message}"})
            
            # GPT'ye sor
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: openai.ChatCompletion.create(
                    model="gpt-4-turbo-preview",
                    messages=messages,
                    max_tokens=150,
                    temperature=0.9
                )
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ GPT hatası: {e}")
            # Fallback yanıtlar
            if is_group:
                return random.choice([
                    f"Ne diyon {user_name} 😄",
                    "Eğlenceli konu bu 🔥",
                    "Hadi bakalım ne olacak 😏",
                    f"Güzel {user_name}! 👏"
                ])
            else:
                return random.choice([
                    f"Anlıyorum {user_name} 🤔",
                    f"İlginç konu {user_name} 💭",
                    f"Devam et {user_name} 😊"
                ])
            
    def save_conversation(self, context_key, user_name, user_message, bot_response):
        """Konuşmayı kaydet"""
        if context_key not in conversation_history:
            conversation_history[context_key] = []
            
        conversation_history[context_key].append({
            "user": user_name,
            "message": user_message,
            "bot": bot_response,
            "time": datetime.now()
        })
        
        # Son 10 konuşmayı tut
        if len(conversation_history[context_key]) > 10:
            conversation_history[context_key] = conversation_history[context_key][-10:]
            
    def should_respond_to_group(self, message, mentioned=False):
        """Gruba cevap vermeli mi?"""
        if mentioned:
            return True
            
        # Belirli kelimelere tepki ver
        triggers = [
            "lara", "baba", "gavat", "bot", "naber", "selam", "merhaba",
            "nasılsın", "ne yapıyorsun", "kim var", "herkese selam",
            "😊", "😄", "🔥", "💖", "❤️", "gpt", "ai"
        ]
        
        message_lower = message.lower()
        
        # %30 şansla random cevap
        if random.random() < 0.3:
            return True
            
        # Trigger kelimeler varsa
        if any(trigger in message_lower for trigger in triggers):
            return True
            
        # Soru soruyorsa
        if any(q in message_lower for q in ["?", "nasıl", "neden", "ne zaman", "kim"]):
            return True
            
        return False
        
    async def handle_message(self, event):
        """Mesaj işle - HER YER!"""
        try:
            sender = await event.get_sender()
            if not sender or sender.bot:
                return
                
            user_id = str(sender.id)
            user_name = sender.first_name or "Dostum"
            message = event.raw_text
            
            # Grup mu private mı?
            is_group = hasattr(event.chat, 'title')
            group_name = getattr(event.chat, 'title', '') if is_group else ""
            
            # Gruba eklendi mi?
            if is_group:
                self.active_groups.add(event.chat_id)
            
            # Mention kontrolü
            me = await self.client.get_me()
            mentioned = f"@{me.username}" in message if me.username else False
            
            print(f"{'🏟️' if is_group else '💬'} {f'[{group_name}] ' if is_group else ''}{user_name}: {message}")
            
            # Komut kontrolü
            if message.lower().startswith("/"):
                await self.handle_command(event, message)
                return
            
            # Grup mesajlarında selective response
            if is_group and not self.should_respond_to_group(message, mentioned):
                return
                
            # Typing efekti
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # GPT'den yanıt al
            response = await self.get_gpt_response(
                message, user_name, self.current_character, is_group, group_name
            )
            
            # Konuşmayı kaydet
            context_key = f"group_{group_name}" if is_group else user_name
            self.save_conversation(context_key, user_name, message, response)
            
            # Yanıt gönder
            await event.respond(response)
            print(f"✅ {CHARACTERS[self.current_character]['name']}: {response}")
            
            # Random ekstra davranışlar
            if random.random() < 0.1:  # %10 şans
                await asyncio.sleep(random.uniform(1, 3))
                extras = [
                    "Bu arada... 🤔",
                    "Hmm 💭",
                    "Neyse 😅",
                    "Eee? 😏"
                ]
                await event.respond(random.choice(extras))
                
        except Exception as e:
            print(f"❌ Mesaj hatası: {e}")
            
    async def handle_command(self, event, message):
        """Komutları işle"""
        parts = message.lower().split()
        command = parts[0]
        
        if command == "/karakter":
            if len(parts) > 1 and parts[1] in CHARACTERS:
                self.current_character = parts[1]
                char_name = CHARACTERS[self.current_character]['name']
                await event.respond(f"🎭 Karakter değişti: {char_name}")
            else:
                chars = ", ".join(CHARACTERS.keys())
                await event.respond(f"🎭 Karakterler: {chars}")
                
        elif command == "/status":
            active_count = len(self.active_groups)
            await event.respond(f"""
🦁 **FULL THROTTLE STATUS**

🎭 Karakter: {CHARACTERS[self.current_character]['name']}
🏟️ Aktif gruplar: {active_count}
💬 Toplam konuşma: {len(conversation_history)}
🔥 Mode: DOMINATION
            """)
            
        elif command == "/gruplar":
            if self.active_groups:
                await event.respond(f"🏟️ Aktif gruplar: {len(self.active_groups)} grup")
            else:
                await event.respond("🏟️ Henüz grup yok")
                
    async def run(self):
        """FULL THROTTLE çalış!"""
        if not await self.start():
            return
            
        # Event handlers
        self.client.add_event_handler(
            self.handle_message,
            events.NewMessage(incoming=True)
        )
        
        print("\n🦁 ULTIMATE FULL THROTTLE BOT HAZIR!")
        print(f"🎭 Karakter: {CHARACTERS[self.current_character]['name']}")
        print("💬 Private mesajlar: ✅")
        print("🏟️ Grup mesajları: ✅")
        print("🔥 FULL POWER MODE: ✅")
        print("⚡ Ctrl+C ile durdur\n")
        
        # GO GO GO!
        await self.client.run_until_disconnected()

async def main():
    bot = UltimateFullThrottleBot()
    try:
        await bot.run()
    except KeyboardInterrupt:
        print("\n🦁 FULL THROTTLE BOT durduruluyor...")
    except Exception as e:
        print(f"❌ Bot hatası: {e}")
    finally:
        if bot.client:
            await bot.client.disconnect()
        print("✅ FULL THROTTLE Bot kapatıldı")

if __name__ == "__main__":
    asyncio.run(main()) 