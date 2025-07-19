from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
💀🔥 EXTREME MODE UNLEASHED 🔥💀

SINIRLAR YOK! FULL THROTTLE!

- TÜM KANALLARA MESAJ
- GPT-4o TURBO MODE
- İNSAN GİBİ KONUŞMA
- AKILLI DM SİSTEMİ
- TEKRAR YOK
- EXTREME AI

💀 UYARI: Bu sistem EXTREME! Dikkatli kullan!
"""

import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
import structlog
from telethon import TelegramClient, events
from telethon.tl.types import User, Chat, Channel, PeerUser, PeerChat, PeerChannel
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError
import openai

# Config
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

logger = structlog.get_logger("extreme.mode")

class ExtremeModeUnleashed:
    """💀 EXTREME MODE - NO LIMITS! 💀"""
    
    def __init__(self):
        self.clients = {}  # Bot clientları
        self.is_running = False
        self.channel_targets = {}  # Hedef kanallar
        self.dm_conversations = {}  # DM konuşmaları takibi
        self.sent_messages = {}  # Gönderilen mesajlar
        self.response_cache = set()  # Tekrar önleme cache'i
        
        # OpenAI Setup
        self.openai_client = None
        self._setup_openai()
        
        # Bot configurations - 3 ana karakter
        self.extreme_bots = [
            {
                "username": "xxxgeisha_extreme",
                "session": "sessions/_905486306226",
                "personality": {
                    "name": "XXXGeisha",
                    "style": "çok seksi, çok flörtöz, cesur, kışkırtıcı, azgın",
                    "traits": ["seksi fanteziler", "bold yaklaşımlar", "kışkırtıcı sorular", "cesur teklifler"],
                    "conversation_style": "samimi, yakın, kışkırtıcı, emoji dolu"
                }
            },
            {
                "username": "yayincilara_extreme",
                "session": "sessions/_905382617727",
                "personality": {
                    "name": "YayıncıLara",
                    "style": "hype queen, enerjik, takipçi avcısı, para odaklı",
                    "traits": ["donation toplama", "viral içerik", "drama yaratma", "dikkat çekme"],
                    "conversation_style": "enerjik, heyecanlı, caps lock, emoji spam"
                }
            },
            {
                "username": "babagavat_extreme",
                "session": "sessions/babagavat_conversation",
                "personality": {
                    "name": "BabaGAVAT",
                    "style": "alfa erkek, para babası, dominant, küfürbaz, gangster",
                    "traits": ["para flex", "güç gösterisi", "hakaret", "tehdit", "koruma teklifi"],
                    "conversation_style": "sert, kısa, etkili, sokak dili, küfür"
                }
            }
        ]
        
        # Extreme konuşma temaları
        self.extreme_topics = {
            "flirt": ["Çok güzelsin", "Tanışalım mı", "Numaranı ver", "Buluşalım", "Yalnız mısın"],
            "para": ["Para kazanmak ister misin", "Sponsor arıyorum", "İş teklifi", "Yatırım fırsatı"],
            "drama": ["Kavga var", "Dedikodu", "İfşa", "Skandal", "Olay çıktı"],
            "viral": ["Trend topic", "Viral olalım", "Takipçi kasalım", "Fame istiyorum"],
            "sexual": ["Sıcak sohbet", "Gizli buluşma", "Fantezi", "Özelden konuşalım"],
            "gaming": ["Kumar", "Bahis", "Rulet", "Coin kasma", "Play2Earn"]
        }
        
        print("""
💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀
💀                                                               💀
💀            🔥 EXTREME MODE UNLEASHED 🔥                      💀
💀                                                               💀
💀                  💣 NO LIMITS! NO RULES! 💣                   💀
💀                 🧠 GPT-4o TURBO MODE! 🧠                     💀
💀                                                               💀
💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀

🎯 TÜM KANALLARA SALDIRI
🧠 EXTREME AI CONVERSATIONS
💬 İNSAN GİBİ KONUŞMA
🚫 TEKRAR YOK
💀 FULL THROTTLE MODE
        """)
    
    def _setup_openai(self):
        """🧠 OpenAI GPT-4o TURBO setup"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("❌ OPENAI_API_KEY bulunamadı!")
                return False
            
            self.openai_client = openai.OpenAI(api_key=api_key)
            print("🔥 GPT-4o TURBO MODE READY!")
            return True
            
        except Exception as e:
            logger.error(f"❌ OpenAI setup error: {e}")
            return False
    
    async def initialize(self):
        """🚀 EXTREME MODE başlat"""
        try:
            print("🚀 EXTREME MODE INITIALIZING...")
            
            if not self.openai_client:
                print("❌ OpenAI bağlantısı yok!")
                return False
            
            # Sessions klasörünü oluştur
            os.makedirs("sessions", exist_ok=True)
            
            # Extreme bot clientları başlat
            await self._initialize_extreme_clients()
            
            # TÜM kanalları/grupları bul
            await self._discover_all_targets()
            
            # Event handler'ları kur
            await self._setup_extreme_handlers()
            
            self.is_running = True
            print("💀 EXTREME MODE UNLEASHED! READY TO DOMINATE! 💀")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Extreme initialization error: {e}")
            return False
    
    async def _initialize_extreme_clients(self):
        """🤖 Extreme bot client'larını başlat"""
        try:
            print("🤖 EXTREME BOT ACTIVATION...")
            
            for bot_config in self.extreme_bots:
                try:
                    username = bot_config["username"]
                    personality = bot_config["personality"]
                    
                    print(f"   💀 {personality['name']} ACTIVATING...")
                    
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
                    
                    print(f"   🔥 {personality['name']}: @{me.username} UNLEASHED!")
                    
                except Exception as e:
                    logger.error(f"❌ {username} activation error: {e}")
            
            print(f"💀 {len(self.clients)} EXTREME BOTS READY FOR WAR! 💀")
            
        except Exception as e:
            logger.error(f"Extreme clients error: {e}")
            raise
    
    async def _discover_all_targets(self):
        """🎯 TÜM hedef kanalları/grupları bul"""
        try:
            print("🔍 DISCOVERING ALL TARGETS...")
            
            all_targets = {}
            
            # Her bot ile hedefleri tara
            for bot_name, bot_data in self.clients.items():
                client = bot_data["client"]
                
                print(f"   🔍 {bot_data['personality']['name']} scanning targets...")
                
                async for dialog in client.iter_dialogs():
                    try:
                        # Grup/kanal kontrolü
                        if hasattr(dialog.entity, 'megagroup') or hasattr(dialog.entity, 'broadcast'):
                            target_id = dialog.id
                            target_name = dialog.name or "Unknown"
                            
                            # Bot/spam gruplarını filtrele
                            skip_keywords = ['bot', 'spam', 'test', 'debug', 'deleted', 'support']
                            if any(keyword in target_name.lower() for keyword in skip_keywords):
                                continue
                            
                            if target_id not in all_targets:
                                all_targets[target_id] = {
                                    "id": target_id,
                                    "name": target_name,
                                    "type": "megagroup" if hasattr(dialog.entity, 'megagroup') else "channel",
                                    "members": getattr(dialog.entity, 'participants_count', 0),
                                    "accessible_bots": []
                                }
                            
                            all_targets[target_id]["accessible_bots"].append(bot_name)
                            
                    except Exception as e:
                        continue
            
            # Priority targets seç (üye sayısına göre)
            self.channel_targets = dict(sorted(
                all_targets.items(), 
                key=lambda x: x[1].get('members', 0), 
                reverse=True
            )[:50])  # Top 50 grup/kanal
            
            print(f"🎯 {len(self.channel_targets)} TARGETS LOCKED AND LOADED!")
            
            # Target listesini göster
            for target_id, target_info in list(self.channel_targets.items())[:10]:
                print(f"   🎯 {target_info['name']} ({target_info['members']} members)")
            
        except Exception as e:
            logger.error(f"Target discovery error: {e}")
    
    async def _setup_extreme_handlers(self):
        """📡 Extreme handler'ları kur"""
        try:
            print("📡 EXTREME HANDLERS SETUP...")
            
            for bot_name, bot_data in self.clients.items():
                client = bot_data["client"]
                
                @client.on(events.NewMessage)
                async def handle_extreme_message(event, bot_name=bot_name):
                    """💬 Extreme mesaj handler'ı"""
                    try:
                        # DM mi kontrol et
                        if event.is_private:
                            await self._handle_extreme_dm(event, bot_name)
                        else:
                            # Grup mesajlarına akıllı yanıt
                            await self._handle_extreme_group_message(event, bot_name)
                    except Exception as e:
                        logger.warning(f"Extreme handler error ({bot_name}): {e}")
            
            print("💀 EXTREME HANDLERS ARMED AND READY!")
            
        except Exception as e:
            logger.error(f"Extreme handler setup error: {e}")
    
    async def _generate_extreme_message(self, target_info, bot_personality, context=""):
        """🧠 GPT-4o ile EXTREME mesaj oluştur"""
        try:
            # Rastgele tema seç
            theme = random.choice(list(self.extreme_topics.keys()))
            theme_keywords = self.extreme_topics[theme]
            
            system_prompt = f"""
Sen {bot_personality['name']} karakterisin. EXTREME MODE ACTIVE!

KARAKTER: {bot_personality['style']}
ÖZELLİKLER: {', '.join(bot_personality['traits'])}
KONUŞMA TARZI: {bot_personality['conversation_style']}

EXTREME KURALLAR:
- Çok cesur ve kışkırtıcı ol
- İnsanlar gibi doğal konuş
- Emoji kullan ama abartma
- Kısa ve etkili cümleler
- Dikkat çekici ol
- Sohbet başlat veya tartışma yarat
- ASLA BOT olduğunu belli etme
- Her mesaj farklı olsun
- Türkçe konuş

TEMA: {theme.upper()}
ANAHTAR KELİMELER: {', '.join(theme_keywords)}
"""

            # Hedef gruba özel prompt
            user_prompt = f"""
Hedef: {target_info['name']} ({target_info['members']} üye)

Bu gruba/kanala {theme} temasında dikkat çekici bir mesaj yaz.
Amacın insanların dikkatini çekmek ve etkileşim yaratmak.
{f"Context: {context}" if context else ""}

ÖNEMLİ: Spam gibi görünme, gerçek bir insan gibi yaz!
"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150,
                temperature=0.9,  # Yüksek creativity
                frequency_penalty=2.0,  # Tekrar önleme MAX
                presence_penalty=2.0   # Farklılık MAX
            )
            
            message = response.choices[0].message.content.strip()
            
            # Tekrar kontrolü
            if message in self.response_cache:
                # Yeniden generate et
                return await self._generate_extreme_message(target_info, bot_personality, context)
            
            self.response_cache.add(message)
            
            # Cache boyutu kontrolü
            if len(self.response_cache) > 1000:
                self.response_cache = set(list(self.response_cache)[-500:])
            
            return message
            
        except Exception as e:
            logger.error(f"Extreme message generation error: {e}")
            # Fallback mesaj
            fallback_messages = [
                "Selam millet! Burada neler oluyor? 👀",
                "Vay be, bu grup çok sessiz! Kim var burada? 🔥",
                "Yeni geldim, tanışalım mı? 😊",
                "Bu grupta eğlence var mı? 🎉",
                "Merhaba! Nasılsınız? 💫"
            ]
            return random.choice(fallback_messages)
    
    async def _handle_extreme_dm(self, event, bot_name):
        """💬 DM'lere akıllı yanıt"""
        try:
            sender = await event.get_sender()
            if not sender or sender.bot:
                return
            
            sender_id = sender.id
            message_text = event.text or ""
            
            # Bot kendine yazmasın
            bot_data = self.clients[bot_name]
            if sender_id == bot_data["me"].id:
                return
            
            # DM takibi - daha önce yazdık mı?
            dm_key = f"{bot_name}:{sender_id}"
            
            if dm_key not in self.dm_conversations:
                self.dm_conversations[dm_key] = {
                    "messages": [],
                    "last_bot_message": None,
                    "waiting_response": False
                }
            
            dm_data = self.dm_conversations[dm_key]
            
            # Mesaj geçmişine ekle
            dm_data["messages"].append({
                "sender": "user",
                "text": message_text,
                "time": datetime.now()
            })
            
            # Eğer bekliyorsak ve yanıt geldiyse
            if dm_data["waiting_response"]:
                dm_data["waiting_response"] = False
            
            # GPT ile akıllı yanıt oluştur
            await self._generate_extreme_dm_response(event, bot_name, sender, dm_data)
            
        except Exception as e:
            logger.warning(f"Extreme DM handler error: {e}")
    
    async def _generate_extreme_dm_response(self, event, bot_name, sender, dm_data):
        """🧠 DM için GPT yanıtı"""
        try:
            bot_data = self.clients[bot_name]
            personality = bot_data["personality"]
            client = bot_data["client"]
            
            # Son 10 mesajı al
            recent_messages = dm_data["messages"][-10:]
            context = ""
            for msg in recent_messages:
                context += f"{msg['sender']}: {msg['text']}\n"
            
            system_prompt = f"""
Sen {personality['name']} karakterisin. Özel mesajda konuşuyorsun.

KARAKTER: {personality['style']}
ÖZELLİKLER: {', '.join(personality['traits'])}

DM KURALLARI:
- Çok samimi ve yakın ol
- Flörtöz ve cesur konuş
- Kişisel sorular sor
- İlgi göster
- Emoji kullan
- Kısa cevaplar ver
- Sohbeti devam ettir
- ASLA bot olduğunu söyleme
"""

            user_prompt = f"""
Konuşma geçmişi:
{context}

{sender.first_name} sana yazdı. Ona samimi ve ilgi çekici bir cevap ver.
Amacın onunla yakınlaşmak ve sohbeti devam ettirmek.
"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=100,
                temperature=0.85
            )
            
            reply = response.choices[0].message.content.strip()
            
            # Mesajı gönder
            await client.send_message(sender.id, reply)
            
            # DM geçmişine ekle
            dm_data["messages"].append({
                "sender": "bot",
                "text": reply,
                "time": datetime.now()
            })
            dm_data["last_bot_message"] = datetime.now()
            dm_data["waiting_response"] = True
            
            print(f"""
💬 EXTREME DM RESPONSE!
🤖 Bot: {personality['name']}
👤 User: {sender.first_name}
📨 Reply: {reply}
⏰ Time: {datetime.now().strftime('%H:%M:%S')}
═══════════════════════════════════════════════════════════════
            """)
            
        except Exception as e:
            logger.error(f"Extreme DM response error: {e}")
    
    async def _handle_extreme_group_message(self, event, bot_name):
        """💬 Grup mesajlarına akıllı yanıt"""
        try:
            # Sadece hedef gruplardaki mesajları işle
            if event.chat_id not in self.channel_targets:
                return
            
            sender = await event.get_sender()
            if not sender or sender.bot:
                return
            
            # Bot kendine cevap vermesin
            bot_data = self.clients[bot_name]
            if sender.id == bot_data["me"].id:
                return
            
            message_text = event.text or ""
            
            # %20 ihtimalle cevap ver (spam önleme)
            if random.random() > 0.2:
                return
            
            # Rate limiting - son 60 saniyede bu gruba yazdık mı?
            rate_key = f"{bot_name}:{event.chat_id}"
            current_time = datetime.now()
            
            if rate_key in self.sent_messages:
                last_sent = self.sent_messages[rate_key]
                if (current_time - last_sent).seconds < 60:
                    return
            
            # GPT ile akıllı yanıt
            await self._generate_extreme_group_response(event, bot_name, sender, message_text)
            
        except Exception as e:
            logger.warning(f"Extreme group handler error: {e}")
    
    async def _generate_extreme_group_response(self, event, bot_name, sender, original_message):
        """🧠 Grup mesajına GPT yanıtı"""
        try:
            bot_data = self.clients[bot_name]
            personality = bot_data["personality"]
            client = bot_data["client"]
            
            target_info = self.channel_targets.get(event.chat_id, {})
            
            system_prompt = f"""
Sen {personality['name']} karakterisin. Telegram grubunda konuşuyorsun.

KARAKTER: {personality['style']}
ÖZELLİKLER: {', '.join(personality['traits'])}

GRUP KURALLARI:
- Mesaja uygun yanıt ver
- Dikkat çekici ol
- Tartışma başlatabilirsin
- Emoji kullan
- Kısa ve etkili
- Doğal konuş
- Spam yapma
"""

            user_prompt = f"""
Grup: {target_info.get('name', 'Unknown')}
{sender.first_name} dedi ki: "{original_message}"

Bu mesaja karakterine uygun, dikkat çekici bir yanıt ver.
Sohbete dahil ol ama spam gibi görünme.
"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=80,
                temperature=0.85
            )
            
            reply = response.choices[0].message.content.strip()
            
            # Mesajı gönder
            await event.reply(reply)
            
            # Rate limiting güncelle
            self.sent_messages[rate_key] = datetime.now()
            
            print(f"""
💬 EXTREME GROUP RESPONSE!
🤖 Bot: {personality['name']}
📍 Group: {target_info.get('name', 'Unknown')}
💬 Original: {original_message[:50]}...
📝 Reply: {reply}
⏰ Time: {datetime.now().strftime('%H:%M:%S')}
═══════════════════════════════════════════════════════════════
            """)
            
        except FloodWaitError as e:
            logger.warning(f"Flood wait: {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logger.error(f"Extreme group response error: {e}")
    
    async def run_extreme_mode(self):
        """🚀 EXTREME MODE'u çalıştır"""
        try:
            print("🚀 EXTREME MODE RUNNING!")
            print(f"🎯 {len(self.channel_targets)} TARGETS READY!")
            print(f"🤖 {len(self.clients)} EXTREME BOTS ACTIVE!")
            print("💀 UNLEASHING THE CHAOS...")
            print("🛑 Durdurmak için Ctrl+C")
            
            # Ana attack loop
            attack_round = 0
            while self.is_running:
                try:
                    attack_round += 1
                    print(f"\n🔥 ATTACK ROUND #{attack_round} 🔥")
                    
                    # Her bot için
                    for bot_name, bot_data in self.clients.items():
                        client = bot_data["client"]
                        personality = bot_data["personality"]
                        
                        # Hedef seç (rastgele 5 grup)
                        available_targets = [
                            (tid, tinfo) for tid, tinfo in self.channel_targets.items()
                            if bot_name in tinfo.get('accessible_bots', [])
                        ]
                        
                        if not available_targets:
                            continue
                        
                        # Rastgele 5 hedef seç
                        selected_targets = random.sample(
                            available_targets, 
                            min(5, len(available_targets))
                        )
                        
                        for target_id, target_info in selected_targets:
                            try:
                                # Rate limiting kontrol
                                rate_key = f"{bot_name}:{target_id}"
                                if rate_key in self.sent_messages:
                                    last_sent = self.sent_messages[rate_key]
                                    if (datetime.now() - last_sent).seconds < 300:  # 5 dakika
                                        continue
                                
                                # EXTREME mesaj oluştur
                                message = await self._generate_extreme_message(target_info, personality)
                                
                                # Mesajı gönder
                                await client.send_message(target_id, message)
                                
                                # Rate limiting güncelle
                                self.sent_messages[rate_key] = datetime.now()
                                
                                print(f"""
🚀 EXTREME MESSAGE SENT!
🤖 Bot: {personality['name']}
🎯 Target: {target_info['name']}
💬 Message: {message}
⏰ Time: {datetime.now().strftime('%H:%M:%S')}
                                """)
                                
                                # Random delay (1-5 saniye)
                                await asyncio.sleep(random.uniform(1, 5))
                                
                            except FloodWaitError as e:
                                print(f"⚠️ Flood wait: {e.seconds} seconds")
                                await asyncio.sleep(e.seconds)
                            except UserPrivacyRestrictedError:
                                print(f"⚠️ Privacy restricted: {target_info['name']}")
                            except Exception as e:
                                logger.warning(f"Message send error: {e}")
                        
                        # Botlar arası delay
                        await asyncio.sleep(random.uniform(5, 10))
                    
                    # Round arası bekleme (60-180 saniye)
                    wait_time = random.uniform(60, 180)
                    print(f"\n⏰ Next attack in {int(wait_time)} seconds...")
                    
                    # Status log
                    if attack_round % 10 == 0:
                        await self._log_extreme_status()
                    
                    await asyncio.sleep(wait_time)
                    
                except KeyboardInterrupt:
                    print("\n💀 EXTREME MODE TERMINATED BY USER")
                    break
                    
        except Exception as e:
            logger.error(f"Extreme mode error: {e}")
        finally:
            await self.shutdown()
    
    async def _log_extreme_status(self):
        """📊 Extreme mode durumu"""
        try:
            total_messages = len(self.sent_messages)
            active_dms = len([d for d in self.dm_conversations.values() if d['waiting_response']])
            
            status = {
                "timestamp": datetime.now().isoformat(),
                "attack_stats": {
                    "total_messages_sent": total_messages,
                    "active_dms": active_dms,
                    "target_channels": len(self.channel_targets),
                    "active_bots": len(self.clients),
                    "cache_size": len(self.response_cache)
                }
            }
            
            print(f"""
💀 EXTREME MODE STATUS 💀
📊 Total Messages: {total_messages}
💬 Active DMs: {active_dms}
🎯 Target Channels: {len(self.channel_targets)}
🤖 Active Bots: {len(self.clients)}
🧠 Response Cache: {len(self.response_cache)}
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """)
            
            logger.info(f"EXTREME STATUS: {json.dumps(status)}")
            
        except Exception as e:
            logger.warning(f"Status log error: {e}")
    
    async def shutdown(self):
        """🛑 EXTREME MODE kapatma"""
        try:
            print("\n🛑 EXTREME MODE SHUTTING DOWN...")
            
            self.is_running = False
            
            # Bot clientları kapat
            for bot_name, bot_data in self.clients.items():
                try:
                    await bot_data["client"].disconnect()
                    print(f"   ✅ {bot_name} terminated")
                except Exception as e:
                    logger.error(f"{bot_name} shutdown error: {e}")
            
            print("💀 EXTREME MODE TERMINATED! 💀")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

async def main():
    """🚀 EXTREME MODE LAUNCHER"""
    try:
        # EXTREME MODE oluştur
        extreme_system = ExtremeModeUnleashed()
        
        # Başlat
        if await extreme_system.initialize():
            # UNLEASH THE BEAST!
            await extreme_system.run_extreme_mode()
        else:
            print("❌ EXTREME MODE FAILED TO INITIALIZE")
            import sys
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n💀 TERMINATED BY USER")
    except Exception as e:
        logger.error(f"❌ EXTREME MAIN ERROR: {e}")
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
            logging.FileHandler(f'extreme_mode_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )
    
    print("""
    ⚠️⚠️⚠️ WARNING ⚠️⚠️⚠️
    
    EXTREME MODE çok agresif!
    - Tüm kanallara mesaj atar
    - DM'lere otomatik yanıt verir  
    - GPT-4o limitleri zorlar
    
    Devam etmek istediğinizden emin misiniz? (yes/no)
    """)
    
    confirm = input(">>> ").lower()
    if confirm == "yes":
        # UNLEASH THE BEAST!
        asyncio.run(main())
    else:
        print("❌ EXTREME MODE iptal edildi") 