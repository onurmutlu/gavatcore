from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🔥🔥🔥 ONLYVIPS TRIO BOT SYSTEM 🔥🔥🔥

💪 ONUR METODU - 3 ANA BOT SADECE!

Features:
- Sadece 3 ana bot: xxxgeisha, yayincilara, babagavat
- GPT-4o ile akıllı sohbet
- Duplicate bot önleme
- Optimal performance

🎯 HEDEF: 3 ANA BOT AKTİVE ET!
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

logger = structlog.get_logger("onlyvips.trio_bot")

class OnlyVipsTrioBotSystem:
    """🔥 3 Ana Bot Sistemi"""
    
    def __init__(self):
        self.clients = {}  # Bot clientları
        self.is_running = False
        self.onlyvips_group_id = None
        self.conversation_history = []  # Son N mesajı tutacak
        self.last_response_time = {}  # Her bot için son cevap zamanı
        
        # OpenAI Setup
        self.openai_client = None
        self._setup_openai()
        
        # 3 Ana Bot Configuration
        self.trio_bots = [
            {
                "username": "xxxgeisha_bot",
                "session": "sessions/_905486306226",
                "personality": {
                    "name": "XXXGeisha",
                    "style": "seksi, eğlenceli, çekici kız, flörtöz",
                    "keywords": ["seksi", "dans", "eğlence", "güzellik", "çekici"],
                    "response_style": "emoji'li, flörtöz, çekici, seksi"
                }
            },
            {
                "username": "yayincilara_bot",
                "session": "sessions/_905382617727",
                "personality": {
                    "name": "YayıncıLara",
                    "style": "yayıncı kız, enerjik, takipçi odaklı, stream",
                    "keywords": ["yayın", "stream", "takipçi", "donation", "chat"],
                    "response_style": "enerjik, yayıncı slangı, etkileşimli"
                }
            },
            {
                "username": "babagavat_bot",
                "session": "sessions/babagavat_conversation",
                "personality": {
                    "name": "BabaGAVAT",
                    "style": "sokak lideri, para odaklı, dominant, patron havası",
                    "keywords": ["para", "sponsor", "vip", "gavat", "boss", "iş"],
                    "response_style": "kısa ve etkili, sokak dili, güçlü"
                }
            }
        ]
        
        print("""
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
🔥                                                               🔥
🔥        🤖 ONLYVIPS TRIO BOT SYSTEM 🤖                        🔥
🔥                                                               🔥
🔥             💪 3 ANA BOT SADECE! 💪                           🔥
🔥              🧠 GPT-4o AKILLI MUHABBET! 🧠                  🔥
🔥                                                               🔥
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥

🎯 3 ANA BOT: xxxgeisha, yayincilara, babagavat
🧠 GPT-4o Intelligence: Akıllı muhabbet sistemi
💬 Group Monitoring: OnlyVips grup takibi
🚫 Duplicate Prevention: Tek bot instance
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
        """🚀 Trio bot sistemini başlat"""
        try:
            print("🚀 OnlyVips Trio Bot System başlatılıyor...")
            
            if not self.openai_client:
                print("❌ OpenAI bağlantısı yok!")
                return False
            
            # Sessions klasörünü oluştur
            os.makedirs("sessions", exist_ok=True)
            
            # 3 Ana bot client'larını başlat
            await self._initialize_trio_bot_clients()
            
            # OnlyVips grubunu bul
            await self._find_onlyvips_group()
            
            # Event handler'ları kur
            await self._setup_trio_handlers()
            
            # Conversation history'yi başlat
            await self._initialize_conversation_history()
            
            self.is_running = True
            print("✅ OnlyVips Trio Bot System hazır! 🤖🧠")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Trio bot error: {e}")
            return False
    
    async def _initialize_trio_bot_clients(self):
        """🤖 3 Ana bot client'larını başlat"""
        try:
            print("🤖 3 Ana bot client'ları başlatılıyor...")
            
            for bot_config in self.trio_bots:
                try:
                    username = bot_config["username"]
                    personality = bot_config["personality"]
                    
                    print(f"   🤖 {personality['name']} başlatılıyor... ({username})")
                    
                    client = TelegramClient(
                        bot_config["session"],
                        TELEGRAM_API_ID,
                        TELEGRAM_API_HASH
                    )
                    
                    await client.start()
                    me = await client.get_me()
                    
                    self.clients[username] = {
                        "client": client,
                        "me": me,
                        "personality": personality,
                        "config": bot_config
                    }
                    
                    print(f"   ✅ {personality['name']}: @{me.username} (ID: {me.id})")
                    
                except Exception as e:
                    logger.error(f"❌ {username} başlatma hatası: {e}")
            
            print(f"🔥 {len(self.clients)} TRIO BOT AKTİVE EDİLDİ! 🔥")
            
        except Exception as e:
            logger.error(f"Trio bot clients error: {e}")
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
    
    async def _setup_trio_handlers(self):
        """📡 Trio handler'larını kur"""
        try:
            print("📡 Trio Bot handlers kuruluyor...")
            
            for bot_name, bot_data in self.clients.items():
                client = bot_data["client"]
                
                @client.on(events.NewMessage)
                async def handle_trio_message(event, bot_name=bot_name):
                    """💬 Trio mesaj handler'ı"""
                    try:
                        # Sadece OnlyVips grubundaki mesajları işle
                        if self.onlyvips_group_id and event.chat_id == self.onlyvips_group_id:
                            await self._process_trio_message(event, bot_name)
                    except Exception as e:
                        logger.warning(f"Trio handler error ({bot_name}): {e}")
            
            print("✅ Trio Bot handlers kuruldu!")
            
        except Exception as e:
            logger.error(f"Trio handler setup error: {e}")
    
    async def _process_trio_message(self, event, listening_bot):
        """🧠 GPT ile grup mesajını akıllıca işle - Trio Version"""
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
            
            # GPT ile hangi botların cevap vereceğine karar ver
            responding_bots = await self._gpt_decide_trio_responding_bots(message_text, sender_info)
            
            if responding_bots:
                print(f"🧠 GPT Trio Kararı: {len(responding_bots)} bot cevap verecek!")
                
                # Seçilen botlarla cevap ver
                for bot_name in responding_bots:
                    await self._generate_trio_gpt_response_and_send(bot_name, message_text, sender_info)
                    # Botlar arası 3-5 saniye bekle
                    await asyncio.sleep(3)
            
        except Exception as e:
            logger.warning(f"Trio process error: {e}")
    
    async def _gpt_decide_trio_responding_bots(self, message_text, sender_info):
        """🧠 GPT ile hangi trio botların cevap vereceğine karar ver"""
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

Mevcut 3 ana bot:
- XXXGeisha (seksi, eğlenceli, çekici, dans)
- YayıncıLara (yayın, stream, takipçi, donation)
- BabaGAVAT (para, sponsor, vip, gavat, boss)

Bu mesaja hangi bot(lar) cevap versin? 

Kurallar:
- Para/sponsor/VIP/iş konuları: BabaGAVAT
- Seksi/eğlence/dans/güzellik: XXXGeisha
- Yayın/stream/takipçi konuları: YayıncıLara
- Genel sohbet: En uygun 1 bot
- Soru sorulmuşsa: İlgili bot
- Maksimum 2 bot cevap versin

Cevap formatı: Bot isimlerini virgülle ayır veya "YOK"
Örnek: "BabaGAVAT, XXXGeisha" veya "YayıncıLara" veya "YOK"
"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.7
            )
            
            gpt_decision = response.choices[0].message.content.strip()
            
            if gpt_decision.upper() == "YOK":
                return []
            
            # Bot isimlerini çıkar ve username ile eşleştir
            selected_bots = []
            if "," in gpt_decision:
                bot_names = [name.strip() for name in gpt_decision.split(",")]
            else:
                bot_names = [gpt_decision.strip()]
            
            for bot_name in bot_names:
                if "babagavat" in bot_name.lower() or "gavat" in bot_name.lower():
                    selected_bots.append("babagavat_bot")
                elif "xxxgeisha" in bot_name.lower() or "geisha" in bot_name.lower():
                    selected_bots.append("xxxgeisha_bot")
                elif "yayinci" in bot_name.lower() or "lara" in bot_name.lower():
                    selected_bots.append("yayincilara_bot")
            
            return selected_bots
            
        except Exception as e:
            logger.warning(f"GPT trio bot selection error: {e}")
            # Fallback: rastgele bir bot seç
            import random
            if any(keyword in message_text.lower() for keyword in ["para", "vip", "sponsor", "gavat"]):
                return ["babagavat_bot"]
            elif any(keyword in message_text.lower() for keyword in ["seksi", "dans", "eğlence", "güzel"]):
                return ["xxxgeisha_bot"]
            elif any(keyword in message_text.lower() for keyword in ["yayın", "stream", "takipçi"]):
                return ["yayincilara_bot"]
            return []
    
    async def _generate_trio_gpt_response_and_send(self, bot_name, original_message, sender_info):
        """🧠 GPT ile trio bot akıllı cevap oluştur ve gönder"""
        try:
            if bot_name not in self.clients:
                return
                
            bot_data = self.clients[bot_name]
            client = bot_data["client"]
            personality = bot_data["personality"]
            
            # Rate limiting kontrol
            last_time = self.last_response_time.get(bot_name, datetime.min)
            if (datetime.now() - last_time).seconds < 25:
                return  # 25 saniye bekle
            
            # Son konuşma context'i hazırla
            recent_messages = self.conversation_history[-12:]
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
- Diğer botlarla çakışma, kendi tarzında ol
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
                # Mesajı gönder
                await client.send_message(self.onlyvips_group_id, gpt_response)
                
                # Last response time güncelle
                self.last_response_time[bot_name] = datetime.now()
                
                print(f"""
🧠 GPT TRIO BOT CEVAP!
🤖 Bot: {personality['name']} (@{bot_data['me'].username})
📝 GPT Cevap: {gpt_response}
💬 Orijinal: {original_message}
👤 Gönderen: {sender_info['name']}
⏰ Zaman: {datetime.now().strftime('%H:%M:%S')}
═══════════════════════════════════════════════════════════════
                """)
                
                # Kendi cevabını history'ye ekle
                await self._add_to_conversation_history(
                    {"name": personality['name'], "username": bot_data["me"].username, "id": bot_data["me"].id},
                    gpt_response,
                    datetime.now()
                )
                
        except Exception as e:
            logger.error(f"GPT trio response error ({bot_name}): {e}")
    
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
            # Son 40 mesajı tut
            self.conversation_history.append({
                "sender": sender_info,
                "message": message_text,
                "time": message_time.isoformat(),
                "timestamp": message_time
            })
            
            # Son 40 mesajı koru
            if len(self.conversation_history) > 40:
                self.conversation_history = self.conversation_history[-40:]
                
        except Exception as e:
            logger.warning(f"Add to history error: {e}")
    
    async def _initialize_conversation_history(self):
        """📝 Conversation history'yi başlat"""
        try:
            print("📝 Conversation history başlatılıyor...")
            self.conversation_history = []
            print("✅ Conversation history hazır!")
            
        except Exception as e:
            logger.warning(f"Initialize history error: {e}")
    
    async def run_trio_bot_system(self):
        """🚀 Trio Bot sistemini çalıştır"""
        try:
            print("🚀 OnlyVips Trio Bot System çalışıyor!")
            print(f"🤖 {len(self.clients)} trio bot aktif!")
            print("🧠 GPT-4o ile akıllı muhabbet aktif!")
            print("💬 Grup mesajları analiz ediliyor...")
            print("🛑 Durdurmak için Ctrl+C kullanın")
            
            # Aktif trio botları listele
            print("\n🤖 AKTİF TRIO BOTLAR:")
            for bot_name, bot_data in self.clients.items():
                personality = bot_data["personality"]
                print(f"   ✅ {personality['name']}: @{bot_data['me'].username}")
            
            # Ana monitoring loop
            while self.is_running:
                try:
                    # Sistem durumunu logla
                    if datetime.now().minute % 10 == 0:
                        await self._log_trio_status()
                    
                    await asyncio.sleep(30)
                    
                except KeyboardInterrupt:
                    print("\n🛑 Kullanıcı tarafından durduruldu")
                    break
                    
        except Exception as e:
            logger.error(f"Trio bot system error: {e}")
        finally:
            await self.shutdown()
    
    async def _log_trio_status(self):
        """📊 Trio bot durumunu logla"""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "active_trio_bots": len(self.clients),
                "conversation_history_length": len(self.conversation_history),
                "openai_connected": self.openai_client is not None,
                "trio_bot_list": [
                    {
                        "name": bot_data["personality"]["name"],
                        "username": bot_data["me"].username,
                        "last_response": self.last_response_time.get(bot_name, "Never")
                    }
                    for bot_name, bot_data in self.clients.items()
                ]
            }
            
            logger.info(f"🤖 Trio Bot Status: {json.dumps(status, default=str)}")
            
        except Exception as e:
            logger.warning(f"Trio status log error: {e}")
    
    async def shutdown(self):
        """🛑 Trio bot sistemin kapatılması"""
        try:
            print("\n🛑 OnlyVips Trio Bot System kapatılıyor...")
            
            self.is_running = False
            
            # Trio bot clientları kapat
            for bot_name, bot_data in self.clients.items():
                try:
                    await bot_data["client"].disconnect()
                    print(f"   ✅ {bot_name} kapatıldı")
                except Exception as e:
                    logger.error(f"{bot_name} shutdown error: {e}")
            
            print("✅ OnlyVips Trio Bot System kapatıldı!")
            
        except Exception as e:
            logger.error(f"Trio shutdown error: {e}")

async def main():
    """🚀 Ana fonksiyon - Trio Bot System"""
    try:
        # Trio bot system oluştur
        trio_bot_system = OnlyVipsTrioBotSystem()
        
        # Başlat
        if await trio_bot_system.initialize():
            # Çalıştır
            await trio_bot_system.run_trio_bot_system()
        else:
            print("❌ Trio Bot System başlatılamadı")
            import sys
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"❌ Trio Main error: {e}")
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
            logging.FileHandler(f'onlyvips_trio_bot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )
    
    # Çalıştır
    asyncio.run(main()) 