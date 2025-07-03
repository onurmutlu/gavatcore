#!/usr/bin/env python3
"""
🔥🔥🔥 ONLYVIPS FULL BOT ACTIVATION SYSTEM 🔥🔥🔥

💪 ONUR METODU - TÜM BOTLARI OTOMATİK AKTİVE ET!

Features:
- Mevcut session dosyalarını otomatik tespit
- Tüm botları aynı anda aktive etme
- GPT-4o ile akıllı sohbet
- Tam otomatik bot yönetimi
- Multiple bot conversation

🎯 HEDEF: TÜM BOTLARI AKTIVE ET!
"""

import asyncio
import json
import os
import glob
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import structlog
from telethon import TelegramClient, events
from telethon.tl.types import User, Chat, Channel
import openai

# Config
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

logger = structlog.get_logger("onlyvips.full_activation")

class OnlyVipsFullBotActivationSystem:
    """🔥 Tüm Botları Otomatik Aktive Eden Sistem"""
    
    def __init__(self):
        self.clients = {}  # Bot clientları
        self.is_running = False
        self.onlyvips_group_id = None
        self.conversation_history = []  # Son N mesajı tutacak
        self.last_response_time = {}  # Her bot için son cevap zamanı
        
        # OpenAI Setup
        self.openai_client = None
        self._setup_openai()
        
        # Session dosyalarını otomatik tespit et
        self.available_sessions = self._detect_available_sessions()
        
        print("""
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
🔥                                                               🔥
🔥      🤖 ONLYVIPS FULL BOT ACTIVATION SYSTEM 🤖               🔥
🔥                                                               🔥
🔥           💪 TÜM BOTLARI OTOMATİK AKTİVE ET! 💪              🔥
🔥                  🧠 GPT-4o AKILLI MUHABBET! 🧠               🔥
🔥                                                               🔥
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥

🔍 Session Detection: Otomatik session tespiti
🤖 Multi-Bot Activation: Tüm botları aynı anda aktive et
🧠 GPT-4o Intelligence: Akıllı muhabbet sistemi
💬 Group Monitoring: OnlyVips grup takibi
        """)
    
    def _detect_available_sessions(self):
        """📂 Mevcut session dosyalarını tespit et"""
        try:
            print("📂 Mevcut session dosyaları tespit ediliyor...")
            
            sessions = []
            session_files = glob.glob("sessions/*.session")
            
            for session_file in session_files:
                session_name = os.path.basename(session_file).replace(".session", "")
                
                # Temp/test session'ları atla
                if any(skip in session_name.lower() for skip in ["test", "debug", "monitor", "gpt_test"]):
                    continue
                
                # Bot personalities tanımla
                personality = self._get_personality_for_session(session_name)
                
                sessions.append({
                    "session_name": session_name,
                    "session_path": f"sessions/{session_name}",
                    "personality": personality
                })
                
                print(f"   ✅ Session bulundu: {session_name} → {personality['name']}")
            
            print(f"✅ Toplam {len(sessions)} bot session'ı tespit edildi!")
            return sessions
            
        except Exception as e:
            logger.error(f"Session detection error: {e}")
            return []
    
    def _get_personality_for_session(self, session_name):
        """🎭 Session adına göre personality belirle"""
        name_lower = session_name.lower()
        
        if "babagavat" in name_lower or "gavat" in name_lower:
            return {
                "name": "BabaGAVAT",
                "style": "sokak lideri, para odaklı, dominant, patron havası",
                "keywords": ["para", "sponsor", "vip", "gavat", "boss", "iş"],
                "response_style": "kısa ve etkili, sokak dili, güçlü"
            }
        elif "geisha" in name_lower:
            return {
                "name": "Geisha",
                "style": "eğlenceli, flörtöz, dans seven, çekici kız",
                "keywords": ["dans", "eğlence", "güzellik", "kızlar", "parti"],
                "response_style": "emoji'li, neşeli, çekici, samimi"
            }
        elif "yayinci" in name_lower:
            return {
                "name": "YayıncıLara",
                "style": "yayıncı kız, enerjik, takipçi odaklı",
                "keywords": ["yayın", "stream", "takipçi", "donation", "chat"],
                "response_style": "enerjik, yayıncı slangı, etkileşimli"
            }
        else:
            # Numeric session için generic personality
            return {
                "name": f"Bot{session_name[-3:]}",
                "style": "sosyal, aktif, grup odaklı",
                "keywords": ["sohbet", "grup", "arkadaş", "eğlence"],
                "response_style": "dostane, sosyal, grup ruhuna uygun"
            }
    
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
        """🚀 Full bot activation sistemini başlat"""
        try:
            print("🚀 OnlyVips Full Bot Activation başlatılıyor...")
            
            if not self.openai_client:
                print("❌ OpenAI bağlantısı yok!")
                return False
            
            if not self.available_sessions:
                print("❌ Aktive edilecek session bulunamadı!")
                return False
            
            # Sessions klasörünü oluştur
            os.makedirs("sessions", exist_ok=True)
            
            # Tüm bot client'larını başlat
            await self._initialize_all_bot_clients()
            
            # OnlyVips grubunu bul
            await self._find_onlyvips_group()
            
            # Event handler'ları kur
            await self._setup_full_activation_handlers()
            
            # Conversation history'yi başlat
            await self._initialize_conversation_history()
            
            self.is_running = True
            print("✅ OnlyVips Full Bot Activation System hazır! 🤖🧠")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Full activation error: {e}")
            return False
    
    async def _initialize_all_bot_clients(self):
        """🤖 Tüm bot client'larını başlat"""
        try:
            print("🤖 Tüm bot client'ları başlatılıyor...")
            
            for session_config in self.available_sessions:
                try:
                    session_name = session_config["session_name"]
                    personality = session_config["personality"]
                    
                    print(f"   🤖 {personality['name']} başlatılıyor... ({session_name})")
                    
                    client = TelegramClient(
                        session_config["session_path"],
                        TELEGRAM_API_ID,
                        TELEGRAM_API_HASH
                    )
                    
                    await client.start()
                    me = await client.get_me()
                    
                    self.clients[session_name] = {
                        "client": client,
                        "me": me,
                        "personality": personality,
                        "session_config": session_config
                    }
                    
                    print(f"   ✅ {personality['name']}: @{me.username} (ID: {me.id})")
                    
                except Exception as e:
                    logger.error(f"❌ {session_name} başlatma hatası: {e}")
            
            print(f"🔥 {len(self.clients)} BOT AKTİVE EDİLDİ! 🔥")
            
        except Exception as e:
            logger.error(f"All bot clients error: {e}")
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
    
    async def _setup_full_activation_handlers(self):
        """📡 Full activation handler'larını kur"""
        try:
            print("📡 Full Activation handlers kuruluyor...")
            
            for bot_name, bot_data in self.clients.items():
                client = bot_data["client"]
                
                @client.on(events.NewMessage)
                async def handle_full_activation_message(event, bot_name=bot_name):
                    """💬 Full activation mesaj handler'ı"""
                    try:
                        # Sadece OnlyVips grubundaki mesajları işle
                        if self.onlyvips_group_id and event.chat_id == self.onlyvips_group_id:
                            await self._process_full_activation_message(event, bot_name)
                    except Exception as e:
                        logger.warning(f"Full activation handler error ({bot_name}): {e}")
            
            print("✅ Full Activation handlers kuruldu!")
            
        except Exception as e:
            logger.error(f"Full activation handler setup error: {e}")
    
    async def _process_full_activation_message(self, event, listening_bot):
        """🧠 GPT ile grup mesajını akıllıca işle - Full Activation"""
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
            responding_bots = await self._gpt_decide_responding_bots(message_text, sender_info)
            
            if responding_bots:
                print(f"🧠 GPT Kararı: {len(responding_bots)} bot cevap verecek!")
                
                # Seçilen botlarla cevap ver
                for bot_name in responding_bots:
                    await self._generate_gpt_response_and_send(bot_name, message_text, sender_info)
                    # Botlar arası 5-10 saniye bekle
                    await asyncio.sleep(5)
            
        except Exception as e:
            logger.warning(f"Full activation process error: {e}")
    
    async def _gpt_decide_responding_bots(self, message_text, sender_info):
        """🧠 GPT ile hangi botların cevap vereceğine karar ver"""
        try:
            # Son 10 mesajı context olarak hazırla
            recent_messages = self.conversation_history[-10:] if len(self.conversation_history) >= 10 else self.conversation_history
            
            context = ""
            for msg in recent_messages:
                context += f"{msg['sender']['name']}: {msg['message']}\n"
            
            # Mevcut botları listele
            bot_list = []
            for bot_name, bot_data in self.clients.items():
                personality = bot_data["personality"]
                bot_list.append(f"{personality['name']} ({', '.join(personality['keywords'])})")
            
            # GPT'ye sor
            prompt = f"""
OnlyVips Telegram grubunda son konuşmalar:

{context}

Son mesaj: {sender_info['name']}: {message_text}

Mevcut botlar:
{chr(10).join(bot_list)}

Bu mesaja hangi bot(lar) cevap versin? 

Kurallar:
- Para/sponsor/VIP konuları: BabaGAVAT
- Eğlence/dans/güzellik: Geisha  
- Yayın/stream konuları: YayıncıLara
- Genel sohbet: Herhangi biri
- Soru sorulmuşsa: İlgili bot
- Maksimum 2 bot cevap versin

Cevap formatı: Bot isimlerini virgülle ayır veya "YOK"
Örnek: "BabaGAVAT, Geisha" veya "YayıncıLara" veya "YOK"
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
            
            # Bot isimlerini çıkar ve session ile eşleştir
            selected_bots = []
            if "," in gpt_decision:
                bot_names = [name.strip() for name in gpt_decision.split(",")]
            else:
                bot_names = [gpt_decision.strip()]
            
            for bot_name in bot_names:
                # Personality name ile session eşleştir
                for session_name, bot_data in self.clients.items():
                    if bot_data["personality"]["name"].lower() == bot_name.lower():
                        selected_bots.append(session_name)
                        break
            
            return selected_bots
            
        except Exception as e:
            logger.warning(f"GPT bot selection error: {e}")
            # Fallback: rastgele bir bot seç
            import random
            if any(keyword in message_text.lower() for keyword in ["para", "vip", "sponsor", "gavat", "eğlence", "dans"]):
                return [random.choice(list(self.clients.keys()))]
            return []
    
    async def _generate_gpt_response_and_send(self, bot_name, original_message, sender_info):
        """🧠 GPT ile akıllı cevap oluştur ve gönder - Full Version"""
        try:
            if bot_name not in self.clients:
                return
                
            bot_data = self.clients[bot_name]
            client = bot_data["client"]
            personality = bot_data["personality"]
            
            # Rate limiting kontrol
            last_time = self.last_response_time.get(bot_name, datetime.min)
            if (datetime.now() - last_time).seconds < 30:
                return  # 30 saniye bekle
            
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
🧠 GPT FULL ACTIVATION CEVAP!
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
            logger.error(f"GPT response generation error ({bot_name}): {e}")
    
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
    
    async def _initialize_conversation_history(self):
        """📝 Conversation history'yi başlat"""
        try:
            print("📝 Conversation history başlatılıyor...")
            self.conversation_history = []
            print("✅ Conversation history hazır!")
            
        except Exception as e:
            logger.warning(f"Initialize history error: {e}")
    
    async def run_full_activation_system(self):
        """🚀 Full Activation sistemini çalıştır"""
        try:
            print("🚀 OnlyVips Full Bot Activation System çalışıyor!")
            print(f"🤖 {len(self.clients)} bot aktif!")
            print("🧠 GPT-4o ile akıllı muhabbet aktif!")
            print("💬 Grup mesajları analiz ediliyor...")
            print("🛑 Durdurmak için Ctrl+C kullanın")
            
            # Aktif botları listele
            print("\n🤖 AKTİF BOTLAR:")
            for bot_name, bot_data in self.clients.items():
                personality = bot_data["personality"]
                print(f"   ✅ {personality['name']}: @{bot_data['me'].username}")
            
            # Ana monitoring loop
            while self.is_running:
                try:
                    # Sistem durumunu logla
                    if datetime.now().minute % 15 == 0:
                        await self._log_full_activation_status()
                    
                    await asyncio.sleep(30)
                    
                except KeyboardInterrupt:
                    print("\n🛑 Kullanıcı tarafından durduruldu")
                    break
                    
        except Exception as e:
            logger.error(f"Full activation system error: {e}")
        finally:
            await self.shutdown()
    
    async def _log_full_activation_status(self):
        """📊 Full activation durumunu logla"""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "active_bots": len(self.clients),
                "conversation_history_length": len(self.conversation_history),
                "openai_connected": self.openai_client is not None,
                "bot_list": [
                    {
                        "name": bot_data["personality"]["name"],
                        "username": bot_data["me"].username,
                        "last_response": self.last_response_time.get(bot_name, "Never")
                    }
                    for bot_name, bot_data in self.clients.items()
                ]
            }
            
            logger.info(f"🤖 Full Activation Status: {json.dumps(status, default=str)}")
            
        except Exception as e:
            logger.warning(f"Full activation status log error: {e}")
    
    async def shutdown(self):
        """🛑 Full activation sistemin kapatılması"""
        try:
            print("\n🛑 OnlyVips Full Bot Activation System kapatılıyor...")
            
            self.is_running = False
            
            # Tüm bot clientları kapat
            for bot_name, bot_data in self.clients.items():
                try:
                    await bot_data["client"].disconnect()
                    print(f"   ✅ {bot_name} kapatıldı")
                except Exception as e:
                    logger.error(f"{bot_name} shutdown error: {e}")
            
            print("✅ OnlyVips Full Bot Activation System kapatıldı!")
            
        except Exception as e:
            logger.error(f"Full activation shutdown error: {e}")

async def main():
    """🚀 Ana fonksiyon - Full Bot Activation System"""
    try:
        # Full activation system oluştur
        full_activation_system = OnlyVipsFullBotActivationSystem()
        
        # Başlat
        if await full_activation_system.initialize():
            # Çalıştır
            await full_activation_system.run_full_activation_system()
        else:
            print("❌ Full Bot Activation system başlatılamadı")
            import sys
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"❌ Full Activation Main error: {e}")
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
            logging.FileHandler(f'onlyvips_full_activation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )
    
    # Çalıştır
    asyncio.run(main()) 