from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🔥 GAVATCore Ultimate Production Bot
Tüm özellikler aktif, gerçek insan gibi konuşan, hafızalı, GPT destekli bot
"""

import asyncio
import os
import sys
from datetime import datetime
from telethon import TelegramClient, events
import logging

# Path setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Config ve modüller
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, OPENAI_API_KEY

# Character Engine
from character_engine import (
    CharacterManager,
    GPTReplyGenerator,
    PersonalityRouter,
    FallbackReplyManager,
    MemoryContextTracker
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UltimateProductionBot:
    def __init__(self):
        self.client = None
        self.character_manager = CharacterManager()
        self.gpt_generator = GPTReplyGenerator()
        self.personality_router = PersonalityRouter()
        self.fallback_manager = FallbackReplyManager()
        self.memory_tracker = MemoryContextTracker()
        
        # Bot state
        self.active_character = None
        self.is_typing = {}
        self.last_message_time = {}
        
    async def initialize(self):
        """Bot'u başlat"""
        print("\n" + "🔥"*30)
        print("🚀 GAVATCore ULTIMATE PRODUCTION BOT")
        print("🔥"*30 + "\n")
        
        # GPT kontrolü
        if not OPENAI_API_KEY:
            print("⚠️ OpenAI API key bulunamadı! Template mode'da çalışacak.")
        else:
            print("✅ GPT-4 Turbo aktif!")
            
        # Karakteri yükle
        self.active_character = self.character_manager.load_character("yayincilara")
        if not self.active_character:
            # Yoksa oluştur
            self.active_character = self.character_manager.create_character(
                username="yayincilara",
                name="Lara",
                system_prompt="""Sen Lara'sın. Dominant, çekici ve gizemli bir kadınsın. 
                Kullanıcılarla flört edersin ama asla kolay lokma değilsin. 
                Bazen Rusça kelimeler kullan. Lüks yaşamı sev ama bunu açık etme.
                GERÇEK BİR İNSAN GİBİ DAVRAN - yazım hataları yap, emoji kullan, doğal ol.""",
                tone="flirty",
                reply_mode="gpt",
                personality_traits={
                    "dominant": True,
                    "mysterious": True,
                    "flirty": True,
                    "intelligent": True
                },
                gpt_settings={
                    "model": "gpt-4-turbo-preview",
                    "temperature": 0.85,
                    "max_tokens": 300
                }
            )
            
        print(f"🎭 Aktif karakter: {self.active_character.name}")
        print(f"💬 Reply mode: {self.active_character.reply_mode}")
        print(f"🎨 Ton: {self.active_character.tone}")
        
        # Telegram client - WAL mode ile
        import sqlite3
        session_path = 'sessions/_905382617727.session'
        
        # Session lock'u temizle
        if os.path.exists(session_path):
            try:
                conn = sqlite3.connect(session_path)
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA busy_timeout=5000")
                conn.close()
                print("✅ Session lock temizlendi")
            except Exception as e:
                print(f"⚠️ Session temizleme: {e}")
        
        self.client = TelegramClient(
            'sessions/_905382617727',
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH,
            sequential_updates=True
        )
        
        await self.client.start()
        me = await self.client.get_me()
        
        print(f"\n✅ Bot Aktif!")
        print(f"👤 Hesap: {me.first_name} (@{me.username})")
        print(f"🆔 ID: {me.id}")
        
        # Sistemi test et
        await self.client.send_message('me', f"""
🔥 **Ultimate Production Bot Aktif!**

🎭 Karakter: {self.active_character.name}
🧠 GPT-4: {'✓' if OPENAI_API_KEY else '✗'}
💾 Hafıza: ✓
🎯 Personality Router: ✓
💬 Natural Conversation: ✓

_Gerçek insan gibi konuşmaya hazır!_
        """)
        
    async def generate_response(self, user_id: str, user_message: str, user_data: dict):
        """Akıllı yanıt üret"""
        
        # 1. Hafızaya ekle
        self.memory_tracker.add_message(user_id, "user", user_message)
        
        # 2. Bağlamları al
        context_messages = self.memory_tracker.get_context(user_id)
        user_context = self.memory_tracker.get_user_context(user_id)
        
        # 3. Mesaj analizi (GPT varsa)
        message_analysis = None
        if self.gpt_generator.client:
            try:
                message_analysis = await self.gpt_generator.analyze_user_message(user_message)
            except:
                pass
                
        # 4. Yanıt tipini belirle
        reply_type, strategy_params = self.personality_router.route_reply(
            user_message,
            self.active_character.to_dict(),
            user_context,
            message_analysis
        )
        
        logger.info(f"📊 Reply type: {reply_type.value}, Trust: {user_context['trust_index']:.2f}")
        
        # 5. Yanıt üret
        final_reply = None
        
        # GPT öncelikli
        if self.active_character.reply_mode in ["gpt", "hybrid"] and self.gpt_generator.client:
            try:
                gpt_reply = await self.gpt_generator.generate_reply(
                    user_message,
                    self.active_character.to_dict(),
                    context_messages,
                    strategy=reply_type.value,
                    user_id=user_id
                )
                
                if gpt_reply:
                    # Strateji uygula
                    final_reply = self.personality_router.apply_strategy(
                        gpt_reply,
                        reply_type,
                        strategy_params
                    )
            except Exception as e:
                logger.error(f"GPT hatası: {e}")
                
        # Template fallback
        if not final_reply and self.active_character.reply_mode in ["manual", "hybrid"]:
            if self.active_character.template_replies:
                import random
                final_reply = random.choice(self.active_character.template_replies)
            else:
                # Default templates
                templates = [
                    f"Hmm, {user_message} diyorsun... İlginç 🤔",
                    f"Seninle konuşmak hoşuma gidiyor {user_data.get('first_name', '')} 😊",
                    "Bu konuda ne düşündüğümü merak ediyorsun sanırım...",
                    "Bazen kelimeler yetmiyor, değil mi? 💭",
                    f"{user_data.get('first_name', 'Canım')}, sana bir şey söyleyeyim mi?",
                ]
                final_reply = random.choice(templates)
                
        # Fallback manager
        if not final_reply:
            final_reply = await self.fallback_manager.get_fallback_reply(
                user_id,
                self.active_character.to_dict(),
                "no_reply",
                user_context=user_context
            )
            
        # 6. Hafızaya kaydet
        self.memory_tracker.add_message(user_id, "assistant", final_reply)
        
        return final_reply
        
    async def simulate_typing(self, chat_id: int, duration: float = 2.0):
        """Yazıyor göster"""
        try:
            async with self.client.action(chat_id, 'typing'):
                await asyncio.sleep(duration)
        except:
            pass
            
    async def handle_message(self, event):
        """Mesaj handler"""
        try:
            if not event.is_private:
                return
                
            sender = await event.get_sender()
            if not sender or sender.bot:
                return
                
            user_id = str(sender.id)
            user_data = {
                "id": sender.id,
                "first_name": sender.first_name or "Dostum",
                "last_name": sender.last_name,
                "username": sender.username
            }
            
            # Spam kontrolü
            now = datetime.now()
            if user_id in self.last_message_time:
                time_diff = (now - self.last_message_time[user_id]).total_seconds()
                if time_diff < 1:  # 1 saniyeden hızlı
                    return
                    
            self.last_message_time[user_id] = now
            
            # Log
            logger.info(f"💬 {user_data['first_name']}: {event.raw_text}")
            
            # Typing göster (doğal gecikme)
            import random
            typing_duration = random.uniform(1.5, 3.5)
            await self.simulate_typing(event.chat_id, typing_duration)
            
            # Yanıt üret
            response = await self.generate_response(user_id, event.raw_text, user_data)
            
            # Doğal gecikme
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Yanıt gönder
            await event.respond(response)
            
            logger.info(f"✅ Yanıt: {response[:50]}...")
            
            # Bazen çift mesaj at
            if random.random() < 0.15:  # %15 şans
                await asyncio.sleep(random.uniform(2, 4))
                await self.simulate_typing(event.chat_id, 1.5)
                
                follow_ups = [
                    "Bir şey daha söyleyecektim ama unuttum 😅",
                    "Bu arada...",
                    "Neyse boşver 🙈",
                    "Sen ne düşünüyorsun bu konuda?",
                    "Hmm... 🤔"
                ]
                
                follow_up = random.choice(follow_ups)
                await event.respond(follow_up)
                
        except Exception as e:
            logger.error(f"Handler hatası: {e}", exc_info=True)
            
    async def periodic_tasks(self):
        """Periyodik görevler"""
        while True:
            try:
                await asyncio.sleep(300)  # 5 dakika
                
                # Aktif kullanıcıları kontrol et
                active_users = []
                now = datetime.now()
                
                for user_id, last_time in self.last_message_time.items():
                    if (now - last_time).total_seconds() < 600:  # 10 dakika
                        active_users.append(user_id)
                        
                if active_users:
                    # Re-engagement mesajları
                    for user_id in active_users:
                        if random.random() < 0.1:  # %10 şans
                            user_context = self.memory_tracker.get_user_context(user_id)
                            
                            if user_context['message_count'] > 5:
                                re_engage = await self.fallback_manager.get_fallback_reply(
                                    user_id,
                                    self.active_character.to_dict(),
                                    "re_engage",
                                    user_context=user_context
                                )
                                
                                # Kullanıcıya gönder
                                try:
                                    await self.client.send_message(int(user_id), re_engage)
                                    logger.info(f"📤 Re-engagement: {user_id}")
                                except:
                                    pass
                                    
                # Hafıza temizliği
                self.memory_tracker.cleanup_old_memories()
                
            except Exception as e:
                logger.error(f"Periodic task hatası: {e}")
                
    async def run(self):
        """Ana çalışma döngüsü"""
        await self.initialize()
        
        # Handler ekle
        self.client.add_event_handler(
            self.handle_message,
            events.NewMessage(incoming=True)
        )
        
        print("\n" + "🎯"*30)
        print("🔥 ULTIMATE BOT HAZIR!")
        print("🧠 Gerçek insan gibi konuşuyor")
        print("💾 Hafıza sistemi aktif")
        print("🎭 Karakter kişiliği yüklendi")
        print("💬 Doğal diyalog modu")
        print("🎯"*30 + "\n")
        
        # Periyodik görevleri başlat
        asyncio.create_task(self.periodic_tasks())
        
        # Çalışmaya devam et
        await self.client.run_until_disconnected()

async def main():
    bot = UltimateProductionBot()
    try:
        await bot.run()
    except KeyboardInterrupt:
        print("\n⏹️ Bot durduruluyor...")
    except Exception as e:
        logger.error(f"Bot hatası: {e}", exc_info=True)
    finally:
        if bot.client:
            await bot.client.disconnect()
        print("👋 Ultimate bot kapatıldı")

if __name__ == "__main__":
    asyncio.run(main()) 