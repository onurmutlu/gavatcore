#!/usr/bin/env python3
"""
🚀 Multi Bot Launcher - 3 Bot Full Yayın Modu
"""

import asyncio
import os
import sys
import random
import json
from datetime import datetime
from telethon import TelegramClient, events

# Config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, OPENAI_API_KEY

# OpenAI setup
try:
    import openai
    if OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
        print(f"✅ OpenAI API key yüklendi: {OPENAI_API_KEY[:20]}...")
    else:
        print("⚠️ OpenAI API key bulunamadı!")
except ImportError:
    print("❌ OpenAI kütüphanesi yüklü değil!")
    openai = None

# Bot hesapları - BABAGAVAT HESABI BANLI
BOT_ACCOUNTS = {
    "yayincilara": {
        "session": "sessions/yayincilara_conversation.session", 
        "character": {
            "name": "Yayıncı Lara",
            "personality": "Enerjik, eğlenceli, yayın odaklı. Streaming kültürüne hakim, trending konularda aktif.",
            "style": "Genç, dinamik dil. Gaming ve streaming terimleri kullanır.",
            "mood": "streamer_energy",
            "trigger_words": ["yayın", "stream", "game", "chat", "live"]
        }
    },
    "xxxgeisha": {
        "session": "sessions/xxxgeisha_conversation.session",
        "character": {
            "name": "Geisha",
            "personality": "Gizemli, çekici, sofistike. Derin konuşmalar yapar, sanatsal yaklaşımlar.",
            "style": "Zarif, akıllı dil. Metaforlar ve felsefi yaklaşımlar kullanır.",
            "mood": "mysterious_elegant", 
            "trigger_words": ["sanat", "güzellik", "felsefe", "geisha", "zen"]
        }
    }
}

# Hafıza sistemi
global_conversation_history = {}
active_bots = {}

class MultiBotManager:
    def __init__(self):
        self.bots = {}
        self.running = False
        
    async def start_all_bots(self):
        """Tüm botları başlat"""
        print("🚀 Multi Bot Launcher başlıyor...")
        print("🔥 2 BOT FULL YAYIN MODU! (BabaGavat banlandı)")
        
        tasks = []
        for bot_name, bot_config in BOT_ACCOUNTS.items():
            task = asyncio.create_task(self.start_single_bot(bot_name, bot_config))
            tasks.append(task)
            
        # Tüm botları paralel başlat
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_bots = 0
        for i, result in enumerate(results):
            bot_name = list(BOT_ACCOUNTS.keys())[i]
            if isinstance(result, Exception):
                print(f"❌ {bot_name} başlatılamadı: {result}")
            else:
                successful_bots += 1
                print(f"✅ {bot_name} aktif!")
                
        print(f"\n✅ {successful_bots}/2 bot aktif!")
        return successful_bots > 0
        
    async def start_single_bot(self, bot_name, bot_config):
        """Tek bot başlat"""
        try:
            # Client oluştur
            client = TelegramClient(
                bot_config["session"],
                TELEGRAM_API_ID,
                TELEGRAM_API_HASH
            )
            
            await client.start()
            me = await client.get_me()
            
            # Bot wrapper oluştur
            bot = BotInstance(bot_name, client, bot_config["character"], me)
            self.bots[bot_name] = bot
            
            # Event handler ekle
            client.add_event_handler(
                lambda event: bot.handle_message(event),
                events.NewMessage(incoming=True)
            )
            
            # Test mesajı - Saved Messages'a gönder
            try:
                await client.send_message('me', f"""
🤖 **{bot_config['character']['name']} Aktif!**

🎭 Karakter: {bot_config['character']['name']}
🧠 GPT-4 Entegreli
💬 Full Yayın Modu
🕒 {datetime.now().strftime('%H:%M')}

READY FOR ACTION! 🚀
                """)
            except Exception as e:
                print(f"⚠️ Test mesajı gönderilemedi: {e}")
                # Test mesajı gönderilemese de bot çalışır
            
            return True
            
        except Exception as e:
            print(f"❌ {bot_name} hatası: {e}")
            raise e
            
    async def run_all_bots(self):
        """Tüm botları çalıştır"""
        if not await self.start_all_bots():
            print("❌ Hiçbir bot başlatılamadı!")
            return
            
        print("\n🔥 MULTI BOT SİSTEMİ AKTİF!")
        print("💬 Private + Group mesajlar")
        print("🎭 2 farklı karakter (BabaGavat banlandı)")
        print("🧠 GPT-4 entegrasyonu")
        print("⚡ Ctrl+C ile durdur\n")
        
        self.running = True
        
        try:
            # Tüm client'ları paralel çalıştır
            await asyncio.gather(*[
                bot.client.run_until_disconnected() 
                for bot in self.bots.values()
            ])
        except KeyboardInterrupt:
            print("\n🛑 Multi Bot sistemi durduruluyor...")
        finally:
            await self.stop_all_bots()
            
    async def stop_all_bots(self):
        """Tüm botları durdur"""
        for bot_name, bot in self.bots.items():
            try:
                await bot.client.disconnect()
                print(f"✅ {bot_name} durduruldu")
            except:
                pass

class BotInstance:
    def __init__(self, bot_name, client, character_config, me):
        self.bot_name = bot_name
        self.client = client
        self.character = character_config
        self.me = me
        self.active_groups = set()
        
    def get_character_prompt(self, is_group=False):
        """Bu bot için karakter promptu"""
        char = self.character
        context = "grup konuşması" if is_group else "özel mesaj"
        
        return f"""Sen {char['name']} adında bir kişisin.

KİŞİLİK: {char['personality']}
KONUŞMA TARZI: {char['style']}
MOOD: {char['mood']}

CONTEXT: Bu bir {context}

KURALLAR:
1. Her zaman bu karakterin kişiliğinde kal
2. {"Grup konuşmasına aktif katıl, eğlenceli ol" if is_group else "Özel konuşmada samimi ve flörtöz ol"}
3. Kısa ve etkili yanıtlar ver (max 2-3 cümle)
4. Emoji kullan ama abartma
5. Türkçe konuş, doğal ol
6. İnsan gibi davran, bot olduğunu belli etme
7. Bu karaktere özgü yaklaşımları kullan
8. {"Gruplarda esprili ve sosyal ol" if is_group else "DM'de kişisel ve yakın ol"}
9. Sohbeti devam ettir, sorular sor
10. Yazım hatası yapabilirsin, çok mükemmel olma

Şimdi bu karakter olarak yanıt ver."""

    async def get_gpt_response(self, message, user_name, is_group=False, group_name=""):
        """GPT-4'ten yanıt al"""
        try:
            # Sistem promptu
            system_prompt = self.get_character_prompt(is_group)
            
            # Context anahtarı
            context_key = f"{self.bot_name}_{group_name}" if is_group else f"{self.bot_name}_{user_name}"
            history = global_conversation_history.get(context_key, [])
            
            # Mesajları hazırla
            messages = [{"role": "system", "content": system_prompt}]
            
            # Son 3 konuşmayı ekle
            for h in history[-3:]:
                messages.append({"role": "user", "content": f"{h['user']}: {h['message']}"})
                messages.append({"role": "assistant", "content": h['bot']})
            
            # Şu anki mesaj
            context_info = f"[{group_name}] " if is_group else ""
            messages.append({"role": "user", "content": f"{context_info}{user_name}: {message}"})
            
            # GPT'ye sor
            if openai:
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: openai.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=messages,
                        max_tokens=150,
                        temperature=0.8
                    )
                )
                
                return response.choices[0].message.content.strip()
            else:
                # OpenAI yok, fallback
                return f"Hmm, {user_name}... İlginç konu 🤔"
            
        except Exception as e:
            print(f"❌ {self.bot_name} GPT hatası: {e}")
            
            # Rate limit durumunda yanıt verme
            if "rate_limit" in str(e).lower() or "429" in str(e):
                print(f"⏳ {self.bot_name} rate limit - yanıt atlanıyor")
                return None
                
            # Diğer hatalar için çeşitli fallback'ler
            fallback_responses = [
                f"Şu an kafam karışık {user_name} 🤔",
                f"Biraz düşünmem lazım bu konuda 💭",
                f"İlginç bakış açısı {user_name} 🧐",
                f"Bu konuyu daha sonra konuşalım 😊",
                f"Kafam başka yerde şu an 😅"
            ]
            return random.choice(fallback_responses)
            
    def should_respond(self, message, mentioned=False, is_group=False):
        """Bu bot cevap vermeli mi? - BALANCED MOD"""
        # Mention'larda her zaman yanıt
        if mentioned:
            return True
            
        # DM'lerde HER ZAMAN yanıt ver - %100 garantili
        if not is_group:
            print(f"💬 DM mesajı - {self.bot_name} yanıt verecek!")
            return True
            
        # GRUP BALANCED MODU - Daha az agresif
        message_lower = message.lower()
        
        # Karakter spesifik trigger words - %100 yanıt
        triggers = self.character.get("trigger_words", [])
        if any(trigger in message_lower for trigger in triggers):
            print(f"🎯 Trigger kelime bulundu - {self.bot_name} yanıt verecek!")
            return True
            
        # Soru işaretli mesajlar - %100 yanıt
        if "?" in message:
            print(f"❓ Soru tespit edildi - {self.bot_name} yanıt verecek!")
            return True
            
        # Mention benzeri kelimeler
        mention_triggers = ["baba", "gavat", "lara", "geisha", "bot", "ai"]
        if any(trigger in message_lower for trigger in mention_triggers):
            print(f"🎯 Mention benzeri - {self.bot_name} yanıt verecek!")
            return True
            
        # Gruplarda sadece %2 şansla random cevap (ultra minimum spam)
        if random.random() < 0.02:
            print(f"🎲 Ultra nadir random yanıt - {self.bot_name} yanıt verecek!")
            return True
            
        return False
        
    def save_conversation(self, context_key, user_name, user_message, bot_response):
        """Konuşmayı kaydet"""
        if context_key not in global_conversation_history:
            global_conversation_history[context_key] = []
            
        global_conversation_history[context_key].append({
            "user": user_name,
            "message": user_message,
            "bot": bot_response,
            "time": datetime.now(),
            "bot_name": self.bot_name
        })
        
        # Son 10 konuşmayı tut
        if len(global_conversation_history[context_key]) > 10:
            global_conversation_history[context_key] = global_conversation_history[context_key][-10:]
        
    async def handle_message(self, event):
        """Mesaj işle - AGRESIF DM + GRUP BOMBARDIMAN MODU"""
        try:
            sender = await event.get_sender()
            if not sender or sender.bot:
                return
                
            user_id = str(sender.id)
            user_name = sender.first_name or "Dostum"
            message = event.raw_text
            
            # Grup kontrolü
            is_group = hasattr(event.chat, 'title')
            group_name = getattr(event.chat, 'title', '') if is_group else ""
            
            if is_group:
                self.active_groups.add(event.chat_id)
            
            # Mention kontrolü
            mentioned = f"@{self.me.username}" in message if self.me.username else False
            
            print(f"🤖 {self.bot_name} {'🏟️' if is_group else '💬'} {f'[{group_name}] ' if is_group else ''}{user_name}: {message}")
            
            # Komut kontrolü
            if message.lower().startswith("/"):
                await self.handle_command(event, message)
                return
            
            # DM'lerde HER ZAMAN yanıt ver
            if not is_group:
                print(f"💬 DM tespit edildi - {self.bot_name} kesinlikle yanıt verecek!")
                should_respond = True
            else:
                # Grup için normal kontrol
                should_respond = self.should_respond(message, mentioned, is_group)
            
            if not should_respond:
                print(f"⏭️ {self.bot_name} bu mesaja yanıt vermeyecek")
                return
                
            # Typing efekti - DM'lerde daha hızlı
            if is_group:
                await asyncio.sleep(random.uniform(1.0, 2.5))  # Grup: 1-2.5 saniye
            else:
                await asyncio.sleep(random.uniform(0.2, 0.8))  # DM: 0.2-0.8 saniye (çok hızlı!)
            
            # GPT'den yanıt al
            response = await self.get_gpt_response(message, user_name, is_group, group_name)
            
            # Rate limit durumunda yanıt gönderme
            if response is None:
                print(f"⏳ {self.bot_name} rate limit nedeniyle yanıt atlandı")
                return
            
            # Konuşmayı kaydet
            context_key = f"{self.bot_name}_{group_name}" if is_group else f"{self.bot_name}_{user_name}"
            self.save_conversation(context_key, user_name, message, response)
            
            # Yanıt gönder
            await event.respond(response)
            print(f"✅ {self.bot_name} ({self.character['name']}): {response}")
            
            # EK BOMBARDIMAN KALDIRILIYOR - Spam önleme
            # if is_group and random.random() < 0.3:  # DEVRE DIŞI
            
        except Exception as e:
            print(f"❌ {self.bot_name} mesaj hatası: {e}")
            # Hata durumunda bile DM'lerde yanıt vermeye çalış
            if not is_group:
                try:
                    await event.respond("Hmm, bir sorun oldu ama seninle konuşmaya devam edebiliriz! 😊")
                except:
                    pass
            
    async def handle_command(self, event, message):
        """Komutları işle"""
        if message.lower() == "/status":
            active_count = len(self.active_groups)
            await event.respond(f"""
🤖 **{self.character['name']} Status**

🎭 Karakter: {self.character['name']}
🏟️ Aktif gruplar: {active_count}
💬 Mod: {self.character['mood']}
🔥 Durum: FULL AKTİF
            """)

async def main():
    """Ana fonksiyon"""
    # Environment variable kontrolü
    bot_mode = os.environ.get('GAVATCORE_BOT_MODE')
    
    if bot_mode:
        # Tek karakter modu
        print(f"🎭 Tek karakter modu: {bot_mode}")
        
        if bot_mode not in BOT_ACCOUNTS:
            print(f"❌ Geçersiz karakter: {bot_mode}")
            print(f"✅ Mevcut karakterler: {list(BOT_ACCOUNTS.keys())}")
            return
        
        # Tek bot çalıştır
        bot_config = BOT_ACCOUNTS[bot_mode]
        manager = MultiBotManager()
        
        try:
            print(f"🚀 {bot_config['character']['name']} başlatılıyor...")
            
            if await manager.start_single_bot(bot_mode, bot_config):
                print(f"✅ {bot_config['character']['name']} aktif!")
                print("💬 Mesajlar bekleniyor...")
                print("⚡ Ctrl+C ile durdur\n")
                
                # Tek bot'u çalıştır
                bot = manager.bots[bot_mode]
                await bot.client.run_until_disconnected()
            else:
                print(f"❌ {bot_config['character']['name']} başlatılamadı!")
                
        except KeyboardInterrupt:
            print(f"\n🛑 {bot_config['character']['name']} durduruluyor...")
        except Exception as e:
            print(f"❌ {bot_mode} hatası: {e}")
        finally:
            await manager.stop_all_bots()
            print(f"✅ {bot_config['character']['name']} kapatıldı")
    else:
        # Multi bot modu (eski davranış)
        print("🔥 Multi bot modu - Tüm karakterler")
        manager = MultiBotManager()
        try:
            await manager.run_all_bots()
        except KeyboardInterrupt:
            print("\n👋 Multi Bot sistemi kapatılıyor...")
        except Exception as e:
            print(f"❌ Sistem hatası: {e}")
        finally:
            print("✅ Tüm botlar kapatıldı")

if __name__ == "__main__":
    asyncio.run(main()) 