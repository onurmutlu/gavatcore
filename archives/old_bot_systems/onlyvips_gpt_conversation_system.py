from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🔥🔥🔥 ONLYVIPS GPT CONVERSATION SYSTEM 🔥🔥🔥

💪 ONUR METODU - GPT-4o DESTEKLİ AKILLI SOHBET!

Features:
- GPT-4o ile grup muhabbet analizi
- Contextual ve akıllı cevaplar
- Konuşma geçmişi takibi
- Personality-based AI responses
- Real-time chat intelligence

🎯 HEDEF: ONLYVIPS'TE GERÇEK AI MUHABBET!
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import structlog
from telethon import TelegramClient, events
from telethon.tl.types import User, Chat, Channel
import openai

# Config
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

logger = structlog.get_logger("onlyvips.gpt_conversation")

class OnlyVipsGPTConversationSystem:
    """🔥 GPT-4o Destekli OnlyVips Muhabbet Sistemi"""
    
    def __init__(self):
        self.clients = {}  # Bot clientları
        self.is_running = False
        self.onlyvips_group_id = None
        self.conversation_history = []  # Son N mesajı tutacak
        self.user_profiles = {}  # Kullanıcı profilleri
        self.last_response_time = {}  # Her bot için son cevap zamanı
        
        # OpenAI Setup
        self.openai_client = None
        self._setup_openai()
        
        # Bot configurations
        self.bot_configs = [
            {
                "username": "babagavat_bot", 
                "session": "sessions/babagavat_conversation",
                "personality": {
                    "name": "BabaGAVAT",
                    "style": "sokak lideri, para odaklı, dominant",
                    "keywords": ["para", "sponsor", "vip", "gavat", "boss"],
                    "response_style": "kısa ve etkili, sokak dili"
                }
            },
            {
                "username": "geishaniz_bot",
                "session": "sessions/geishaniz_conversation", 
                "personality": {
                    "name": "Geisha",
                    "style": "eğlenceli, flörtöz, dans seven kız",
                    "keywords": ["dans", "eğlence", "güzellik", "kızlar"],
                    "response_style": "emoji'li, neşeli, çekici"
                }
            }
        ]
        
        print("""
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
🔥                                                               🔥
🔥       🤖 ONLYVIPS GPT CONVERSATION SYSTEM 🤖                 🔥
🔥                                                               🔥
🔥            🧠 GPT-4o AKILLI MUHABBET SİSTEMİ! 🧠            🔥
🔥                    💪 ONUR METODU AI POWER! 💪                🔥
🔥                                                               🔥
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥

🧠 GPT-4o: Akıllı muhabbet analizi
🤖 BOTLAR: BabaGAVAT, Geisha
💬 HEDEF: OnlyVips grubunda AI destekli sohbet
🎯 CONTEXT: Grup muhabbetini anlayıp dahil olma!
        """)
    
    def _setup_openai(self):
        """🤖 OpenAI GPT-4o setup"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("❌ OPENAI_API_KEY bulunamadı!")
                return False
            
            self.openai_client = openai.OpenAI(api_key=api_key)
            print("✅ GPT-4o bağlantısı hazır!")
            return True
            
        except Exception as e:
            logger.error(f"❌ OpenAI setup error: {e}")
            return False
    
    async def initialize(self):
        """🚀 GPT muhabbet sistemini başlat"""
        try:
            print("🚀 OnlyVips GPT Conversation System başlatılıyor...")
            
            if not self.openai_client:
                print("❌ OpenAI bağlantısı yok!")
                return False
            
            # Sessions klasörünü oluştur
            os.makedirs("sessions", exist_ok=True)
            
            # Bot client'larını başlat
            await self._initialize_bot_clients()
            
            # OnlyVips grubunu bul
            await self._find_onlyvips_group()
            
            # Event handler'ları kur
            await self._setup_gpt_handlers()
            
            # Conversation history'yi başlat
            await self._initialize_conversation_history()
            
            self.is_running = True
            print("✅ OnlyVips GPT Conversation System hazır! 🧠")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ GPT conversation system error: {e}")
            return False
    
    async def _initialize_bot_clients(self):
        """🤖 Bot client'larını başlat"""
        try:
            print("🤖 GPT Bot client'ları başlatılıyor...")
            
            for bot_config in self.bot_configs:
                try:
                    print(f"   🤖 {bot_config['personality']['name']} başlatılıyor...")
                    
                    client = TelegramClient(
                        bot_config["session"],
                        TELEGRAM_API_ID,
                        TELEGRAM_API_HASH
                    )
                    
                    await client.start()
                    me = await client.get_me()
                    
                    self.clients[bot_config["username"]] = {
                        "client": client,
                        "me": me,
                        "personality": bot_config["personality"],
                        "config": bot_config
                    }
                    
                    print(f"   ✅ {bot_config['personality']['name']}: @{me.username}")
                    
                except Exception as e:
                    logger.error(f"❌ {bot_config['username']} başlatma hatası: {e}")
            
            print(f"✅ {len(self.clients)} GPT bot hazır!")
            
        except Exception as e:
            logger.error(f"GPT bot clients error: {e}")
            raise
    
    async def _find_onlyvips_group(self):
        """🔍 OnlyVips grubunu bul"""
        try:
            print("🔍 OnlyVips grubunu arıyor...")
            
            # İlk bot ile grubunu ara
            first_bot = list(self.clients.values())[0]
            client = first_bot["client"]
            
            async for dialog in client.iter_dialogs():
                group_name = dialog.name.lower() if dialog.name else ""
                
                if any(keyword in group_name for keyword in ["onlyvips", "only vips", "vip", "gavat", "arayış"]):
                    self.onlyvips_group_id = dialog.id
                    print(f"✅ OnlyVips grubu bulundu: {dialog.name} (ID: {dialog.id})")
                    return
            
            print("⚠️ OnlyVips grubu bulunamadı!")
            
        except Exception as e:
            logger.error(f"Group search error: {e}")
    
    async def _setup_gpt_handlers(self):
        """📡 GPT conversation handler'larını kur"""
        try:
            print("📡 GPT Conversation handlers kuruluyor...")
            
            for bot_name, bot_data in self.clients.items():
                client = bot_data["client"]
                
                @client.on(events.NewMessage)
                async def handle_gpt_message(event, bot_name=bot_name):
                    """💬 GPT destekli mesaj handler'ı"""
                    try:
                        # Sadece OnlyVips grubundaki mesajları işle
                        if self.onlyvips_group_id and event.chat_id == self.onlyvips_group_id:
                            await self._process_gpt_message(event, bot_name)
                    except Exception as e:
                        logger.warning(f"GPT message handler error ({bot_name}): {e}")
            
            print("✅ GPT Conversation handlers kuruldu!")
            
        except Exception as e:
            logger.error(f"GPT handler setup error: {e}")
    
    async def _process_gpt_message(self, event, listening_bot):
        """🧠 GPT ile grup mesajını akıllıca işle"""
        try:
            sender = await event.get_sender()
            
            # Bot kendini dinlemesin
            if sender and hasattr(sender, 'username'):
                sender_username = sender.username
                if any(sender_username == bot_data["me"].username for bot_data in self.clients.values()):
                    return
            
            message_text = event.text or ""
            message_time = datetime.now()
            
            # Sender bilgilerini al
            sender_info = await self._get_sender_info(sender)
            
            # Conversation history'ye ekle
            await self._add_to_conversation_history(sender_info, message_text, message_time)
            
            # GPT ile cevap verme kararı al
            should_respond, responding_bot = await self._gpt_should_respond(message_text, sender_info)
            
            if should_respond:
                # GPT ile akıllı cevap oluştur
                await self._generate_gpt_response_and_send(responding_bot, message_text, sender_info)
            
        except Exception as e:
            logger.warning(f"GPT process message error: {e}")
    
    async def _get_sender_info(self, sender):
        """👤 Gönderen bilgilerini al"""
        try:
            if not sender:
                return {"name": "Unknown", "username": "", "id": 0}
            
            return {
                "name": getattr(sender, 'first_name', 'Unknown') or 'Unknown',
                "username": getattr(sender, 'username', '') or '',
                "id": getattr(sender, 'id', 0)
            }
            
        except Exception as e:
            logger.warning(f"Get sender info error: {e}")
            return {"name": "Unknown", "username": "", "id": 0}
    
    async def _add_to_conversation_history(self, sender_info, message_text, message_time):
        """📝 Konuşma geçmişine ekle"""
        try:
            # Son 50 mesajı tut
            self.conversation_history.append({
                "sender": sender_info,
                "message": message_text,
                "time": message_time.isoformat(),
                "timestamp": message_time
            })
            
            # Son 50 mesajı koru
            if len(self.conversation_history) > 50:
                self.conversation_history = self.conversation_history[-50:]
                
        except Exception as e:
            logger.warning(f"Add to history error: {e}")
    
    async def _gpt_should_respond(self, message_text, sender_info):
        """🧠 GPT ile cevap verme kararı al"""
        try:
            # Son 10 mesajı context olarak hazırla
            recent_messages = self.conversation_history[-10:] if len(self.conversation_history) >= 10 else self.conversation_history
            
            context = ""
            for msg in recent_messages:
                context += f"{msg['sender']['name']}: {msg['message']}\n"
            
            # GPT'ye sor
            prompt = f"""
OnlyVips Telegram grubunda son konuşmalar:

{context}

Son mesaj: {sender_info['name']}: {message_text}

Sen BabaGAVAT veya Geisha karakterlerinden birisin. Bu gruba cevap verip vermeyeceğine karar ver.

Cevap VER eğer:
- Para, sponsor, VIP, gavat gibi kelimeler varsa
- Soru sorulmuşsa
- Eğlence, dans, güzellik konuları varsa  
- Grup sessizse ve konuşma başlatılmalıysa
- Birisi yardım istiyorsa

Cevap VERME eğer:
- Çok kısa zamanda cevap verdiysen
- Mesaj spam gibi görünüyorsa
- Özel konuşma gibi görünüyorsa

Sadece "YES" (hangi karakter) veya "NO" ile cevap ver.
Format: "YES:BABAGAVAT" veya "YES:GEISHA" veya "NO"
"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.7
            )
            
            gpt_decision = response.choices[0].message.content.strip().upper()
            
            if gpt_decision.startswith("YES:"):
                character = gpt_decision.split(":")[1]
                if character == "BABAGAVAT":
                    return True, "babagavat_bot"
                elif character == "GEISHA":
                    return True, "geishaniz_bot"
            
            return False, None
            
        except Exception as e:
            logger.warning(f"GPT should respond error: {e}")
            # Fallback: basit kurallarla karar ver
            import random
            if any(keyword in message_text.lower() for keyword in ["para", "vip", "sponsor", "gavat"]):
                return True, random.choice(list(self.clients.keys()))
            return False, None
    
    async def _generate_gpt_response_and_send(self, bot_name, original_message, sender_info):
        """🧠 GPT ile akıllı cevap oluştur ve gönder"""
        try:
            bot_data = self.clients[bot_name]
            client = bot_data["client"]
            personality = bot_data["personality"]
            
            # Son konuşma context'i hazırla
            recent_messages = self.conversation_history[-15:]
            context = ""
            for msg in recent_messages:
                context += f"{msg['sender']['name']}: {msg['message']}\n"
            
            # Personality prompt'u oluştur
            system_prompt = f"""
Sen {personality['name']} karakterisin. OnlyVips Telegram grubunda konuşuyorsun.

KİŞİLİK: {personality['style']}
ANAHTAR KELİMELER: {', '.join(personality['keywords'])}
CEVAP TARZI: {personality['response_style']}

ÖNEMLİ KURALLAR:
- Türkçe cevap ver
- Kısa ve etkili ol (max 1-2 cümle)
- Karakterine uygun davran
- Samimi ve dostane ol
- Emoji kullanabilirsin ama abartma
- OnlyVips grubunun havasına uygun konuş
"""

            user_prompt = f"""
Grup konuşması:
{context}

{sender_info['name']} az önce şöyle dedi: "{original_message}"

Sen {personality['name']} olarak bu mesaja nasıl cevap verirsin?
"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=100,
                temperature=0.8
            )
            
            gpt_response = response.choices[0].message.content.strip()
            
            if gpt_response:
                # Rate limiting - aynı bot 30 saniyede bir cevap versin
                last_time = self.last_response_time.get(bot_name, datetime.min)
                if (datetime.now() - last_time).seconds > 30:
                    
                    # Mesajı gönder
                    await client.send_message(self.onlyvips_group_id, gpt_response)
                    
                    # Last response time güncelle
                    self.last_response_time[bot_name] = datetime.now()
                    
                    print(f"""
🧠 GPT AKILLI CEVAP GÖNDERİLDİ!
🤖 Bot: {personality['name']} ({bot_name})
📝 GPT Cevap: {gpt_response}
💬 Orijinal: {original_message}
👤 Gönderen: {sender_info['name']}
⏰ Zaman: {datetime.now().strftime('%H:%M:%S')}
════════════════════════════════════════════════════
                    """)
                    
                    # Kendi cevabını history'ye ekle
                    await self._add_to_conversation_history(
                        {"name": personality['name'], "username": bot_data["me"].username, "id": bot_data["me"].id},
                        gpt_response,
                        datetime.now()
                    )
                
        except Exception as e:
            logger.error(f"GPT response generation error ({bot_name}): {e}")
    
    async def _initialize_conversation_history(self):
        """📝 Conversation history'yi başlat"""
        try:
            # Son 24 saatin mesajlarını yükle (varsa)
            print("📝 Conversation history başlatılıyor...")
            self.conversation_history = []
            print("✅ Conversation history hazır!")
            
        except Exception as e:
            logger.warning(f"Initialize history error: {e}")
    
    async def run_gpt_conversation_system(self):
        """🚀 GPT Conversation sistemini çalıştır"""
        try:
            print("🚀 OnlyVips GPT Conversation System çalışıyor!")
            print("🧠 GPT-4o ile akıllı muhabbet aktif!")
            print("💬 Grup mesajları analiz ediliyor...")
            print("🛑 Durdurmak için Ctrl+C kullanın")
            
            # Ana monitoring loop
            while self.is_running:
                try:
                    # Sistem durumunu logla
                    if datetime.now().minute % 15 == 0:
                        await self._log_gpt_conversation_status()
                    
                    await asyncio.sleep(30)
                    
                except KeyboardInterrupt:
                    print("\n🛑 Kullanıcı tarafından durduruldu")
                    break
                    
        except Exception as e:
            logger.error(f"GPT conversation system error: {e}")
        finally:
            await self.shutdown()
    
    async def _log_gpt_conversation_status(self):
        """📊 GPT conversation durumunu logla"""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "active_bots": len(self.clients),
                "conversation_history_length": len(self.conversation_history),
                "openai_connected": self.openai_client is not None,
                "last_response_times": {
                    bot_name: time.isoformat() if bot_name in self.last_response_time 
                    else "Never" for bot_name, time in self.last_response_time.items()
                }
            }
            
            logger.info(f"🧠 GPT Conversation Status: {json.dumps(status, default=str)}")
            
        except Exception as e:
            logger.warning(f"GPT status log error: {e}")
    
    async def shutdown(self):
        """🛑 GPT sistemin kapatılması"""
        try:
            print("\n🛑 OnlyVips GPT Conversation System kapatılıyor...")
            
            self.is_running = False
            
            # Bot clientları kapat
            for bot_name, bot_data in self.clients.items():
                try:
                    await bot_data["client"].disconnect()
                    print(f"   ✅ {bot_name} kapatıldı")
                except Exception as e:
                    logger.error(f"{bot_name} shutdown error: {e}")
            
            print("✅ OnlyVips GPT Conversation System kapatıldı!")
            
        except Exception as e:
            logger.error(f"GPT shutdown error: {e}")

async def main():
    """🚀 Ana fonksiyon - GPT Conversation System"""
    try:
        # GPT conversation system oluştur
        gpt_conversation_system = OnlyVipsGPTConversationSystem()
        
        # Başlat
        if await gpt_conversation_system.initialize():
            # Çalıştır
            await gpt_conversation_system.run_gpt_conversation_system()
        else:
            print("❌ GPT conversation system başlatılamadı")
            import sys
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"❌ GPT Main error: {e}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    # Logging setup
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'onlyvips_gpt_conversation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )
    
    # Çalıştır
    asyncio.run(main()) 