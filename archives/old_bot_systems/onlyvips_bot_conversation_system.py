#!/usr/bin/env python3
"""
🔥🔥🔥 ONLYVIPS BOT CONVERSATION SYSTEM 🔥🔥🔥

💪 ONUR METODU - BOTLAR ARASI MUHABBET + LAF ATMA!

Features:
- OnlyVips grubunda botlar arası sohbet
- Diğer kullanıcılara laf atma sistemi
- Real-time grup mesaj takibi
- GPT-4o ile sokak zekası
- BabaGAVAT personality'si

🎯 HEDEF: ONLYVIPS GRUBUNDA FULL MUHABBET!
"""

import asyncio
import random
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import structlog
from telethon import TelegramClient, events
from telethon.tl.types import User, Chat, Channel

# Config
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

logger = structlog.get_logger("onlyvips.conversation")

class OnlyVipsBotConversationSystem:
    """🔥 OnlyVips Bot Muhabbet Sistemi - Sokak Sohbeti + Laf Atma"""
    
    def __init__(self):
        self.clients = {}  # Bot clientları
        self.is_running = False
        self.onlyvips_group_id = None
        self.last_message_time = {}  # Her bot için son mesaj zamanı
        self.conversation_topics = []
        self.user_profiles = {}  # Kullanıcı profilleri için laf atma
        
        # Bot configurations
        self.bot_configs = [
            {
                "username": "babagavat_bot", 
                "session": "sessions/babagavat_conversation",
                "personality": "sokak_lideri"
            },
            {
                "username": "geishaniz_bot",
                "session": "sessions/geishaniz_conversation", 
                "personality": "eglenceli_kiz"
            },
            {
                "username": "yayincilara_bot",
                "session": "sessions/yayincilara_conversation",
                "personality": "yaratik_adam"
            }
        ]
        
        # Conversation starter topics
        self.conversation_starters = [
            "Lan bugün nasıl gitti?",
            "Kim var kimse yok burada?",
            "Parasız adam adam değil",
            "VIP olmak ayrıcalık",
            "Sponsorlar ne alemde?",
            "Para var mı lan ortamda?",
            "Bugün hangi olay var?",
            "Kim konuşacak biraz?",
            "Sessizlik çok saçma",
            "Aktif olun lan biraz!"
        ]
        
        # Laf atma kalıpları
        self.laf_atma_templates = [
            "{user_name} ne sessiz lan, uyudun mu?",
            "{user_name} VIP gibi durmuyor ama",
            "Ee {user_name} para var mı sende?",
            "{user_name} sponsorluk için başvur bence",
            "Hay {user_name} çok konuşuyorsun az sus",
            "{user_name} girdiğinden beri ortalık karıştı",
            "VIP'ler {user_name}'e göre değil sanki",
            "{user_name} premium alabilir mi ki?",
            "Dayı {user_name} sen ne işle uğraşıyorsun?",
            "{user_name} sokağı bilmiyor belli ki"
        ]
        
        print("""
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
🔥                                                               🔥
🔥      🤖 ONLYVIPS BOT CONVERSATION SYSTEM 🤖                  🔥
🔥                                                               🔥
🔥            💬 BOTLAR ARASI MUHABBET + LAF ATMA! 💬           🔥
🔥                    💪 ONUR METODU FULL GÜÇ! 💪                🔥
🔥                                                               🔥
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥

🤖 BOTLAR: babagavat, geishaniz, yayincilara
💬 HEDEF: OnlyVips grubunda muhabbet + laf atma
🎯 SOKAK ZEKAsı: GPT-4o ile tam güç!
        """)
    
    async def initialize(self):
        """🚀 Bot muhabbet sistemini başlat"""
        try:
            print("🚀 OnlyVips Bot Conversation System başlatılıyor...")
            
            # Sessions klasörünü oluştur
            os.makedirs("sessions", exist_ok=True)
            
            # Bot client'larını başlat
            await self._initialize_bot_clients()
            
            # OnlyVips grubunu bul
            await self._find_onlyvips_group()
            
            # Event handler'ları kur
            await self._setup_conversation_handlers()
            
            # Conversation topics'leri yükle
            await self._load_conversation_topics()
            
            self.is_running = True
            print("✅ OnlyVips Bot Conversation System hazır! 💬")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Conversation system error: {e}")
            return False
    
    async def _initialize_bot_clients(self):
        """🤖 Bot client'larını başlat"""
        try:
            print("🤖 Bot client'ları başlatılıyor...")
            
            for bot_config in self.bot_configs:
                try:
                    print(f"   🤖 {bot_config['username']} başlatılıyor...")
                    
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
                    
                    print(f"   ✅ {bot_config['username']}: @{me.username} (ID: {me.id})")
                    
                except Exception as e:
                    logger.error(f"❌ {bot_config['username']} başlatma hatası: {e}")
            
            print(f"✅ {len(self.clients)} bot client hazır!")
            
        except Exception as e:
            logger.error(f"Bot clients error: {e}")
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
                
                if any(keyword in group_name for keyword in ["onlyvips", "only vips", "vip", "gavat"]):
                    self.onlyvips_group_id = dialog.id
                    print(f"✅ OnlyVips grubu bulundu: {dialog.name} (ID: {dialog.id})")
                    return
            
            print("⚠️ OnlyVips grubu bulunamadı!")
            
        except Exception as e:
            logger.error(f"Group search error: {e}")
    
    async def _setup_conversation_handlers(self):
        """📡 Conversation handler'larını kur"""
        try:
            print("📡 Conversation handlers kuruluyor...")
            
            for bot_name, bot_data in self.clients.items():
                client = bot_data["client"]
                
                @client.on(events.NewMessage)
                async def handle_group_message(event, bot_name=bot_name):
                    """💬 Grup mesaj handler'ı"""
                    try:
                        # Sadece OnlyVips grubundaki mesajları işle
                        if self.onlyvips_group_id and event.chat_id == self.onlyvips_group_id:
                            await self._process_group_message(event, bot_name)
                    except Exception as e:
                        logger.warning(f"Message handler error ({bot_name}): {e}")
            
            print("✅ Conversation handlers kuruldu!")
            
        except Exception as e:
            logger.error(f"Handler setup error: {e}")
    
    async def _process_group_message(self, event, listening_bot):
        """💬 Grup mesajını işle ve cevap ver"""
        try:
            sender = await event.get_sender()
            
            # Bot kendini dinlemesin
            if sender and hasattr(sender, 'username'):
                sender_username = sender.username
                if any(sender_username == bot_data["me"].username for bot_data in self.clients.values()):
                    return
            
            message_text = event.text or ""
            
            # User profili güncelle
            if sender and hasattr(sender, 'id'):
                await self._update_user_profile(sender)
            
            # Mesaj analizi ve cevap kararı
            should_respond = await self._should_bot_respond(message_text, listening_bot)
            
            if should_respond:
                # Hangi bot cevap verecek seç
                responding_bot = await self._select_responding_bot(listening_bot, message_text)
                
                # Cevap oluştur ve gönder
                await self._generate_and_send_response(responding_bot, event, message_text, sender)
            
        except Exception as e:
            logger.warning(f"Process message error: {e}")
    
    async def _should_bot_respond(self, message_text, listening_bot):
        """🤔 Bot cevap vermeli mi?"""
        try:
            # Rastgele cevap verme olasılığı
            random_chance = random.random()
            
            # Yüksek olasılık durumlar
            if any(keyword in message_text.lower() for keyword in ["bot", "gavat", "para", "vip", "sponsor"]):
                return random_chance < 0.8  # %80 olasılık
            
            # Orta olasılık
            if any(keyword in message_text.lower() for keyword in ["ne", "kim", "nasıl", "nerede", "lan"]):
                return random_chance < 0.5  # %50 olasılık
            
            # Düşük olasılık (genel muhabbet)
            return random_chance < 0.2  # %20 olasılık
            
        except Exception as e:
            logger.warning(f"Should respond error: {e}")
            return False
    
    async def _select_responding_bot(self, listening_bot, message_text):
        """🎭 Hangi bot cevap verecek seç"""
        try:
            # Mevcut botlardan rastgele seç
            available_bots = list(self.clients.keys())
            
            # Personality'ye göre ağırlıklı seçim
            if "para" in message_text.lower() or "sponsor" in message_text.lower():
                # Para konularında babagavat öncelikli
                weights = []
                for bot_name in available_bots:
                    if "babagavat" in bot_name:
                        weights.append(0.6)
                    else:
                        weights.append(0.2)
                return random.choices(available_bots, weights=weights)[0]
            
            elif "eğlen" in message_text.lower() or "😂" in message_text:
                # Eğlence konularında geishaniz öncelikli
                weights = []
                for bot_name in available_bots:
                    if "geishaniz" in bot_name:
                        weights.append(0.6)
                    else:
                        weights.append(0.2)
                return random.choices(available_bots, weights=weights)[0]
            
            else:
                # Rastgele seç
                return random.choice(available_bots)
                
        except Exception as e:
            logger.warning(f"Select bot error: {e}")
            return random.choice(list(self.clients.keys()))
    
    async def _generate_and_send_response(self, bot_name, event, original_message, sender):
        """💬 Cevap oluştur ve gönder"""
        try:
            bot_data = self.clients[bot_name]
            client = bot_data["client"]
            personality = bot_data["personality"]
            
            # Cevap oluştur
            response = await self._generate_response(personality, original_message, sender)
            
            if response:
                # Mesajı gönder
                await client.send_message(self.onlyvips_group_id, response)
                
                print(f"""
💬 BOT CEVAP GÖNDERİLDİ!
🤖 Bot: {bot_name} ({personality})
📝 Cevap: {response}
⏰ Zaman: {datetime.now().strftime('%H:%M:%S')}
════════════════════════════════════════════════════
                """)
                
                # Son mesaj zamanını güncelle
                self.last_message_time[bot_name] = datetime.now()
                
        except Exception as e:
            logger.error(f"Send response error ({bot_name}): {e}")
    
    async def _generate_response(self, personality, original_message, sender):
        """🧠 Personality'ye göre cevap oluştur"""
        try:
            sender_name = ""
            if sender and hasattr(sender, 'first_name'):
                sender_name = sender.first_name or "Anonim"
            
            # Personality'ye göre farklı cevap tarzları
            if personality == "sokak_lideri":  # babagavat
                responses = [
                    f"Aynen {sender_name} kardeşim, sen bilirsin işi!",
                    f"Para konuşuyor {sender_name}, kulak ver!",
                    f"Vay be {sender_name}, sokağı iyi biliyorsun!",
                    f"Hadi {sender_name}, VIP'lere göster kendini!",
                    f"Lan {sender_name} sen bizden birisin!",
                    "Para var mı ortamda? Sponsor arıyoruz!",
                    "VIP olmayan kapıdan çıkabilir!",
                    "Sokağın kuralı bu kardeşim!"
                ]
            
            elif personality == "eglenceli_kiz":  # geishaniz
                responses = [
                    f"Ayyy {sender_name} çok tatlısın! 😘",
                    f"Hahaha {sender_name} sen ne komiksin! 😂",
                    f"Geisha gibi zarifim ben {sender_name}! 💃",
                    f"VIP'ler için özel dans var {sender_name}! 💋",
                    f"Sen de sponsor ol {sender_name}, eğlence artar! 🎉",
                    "Kızlar buraya! Erkekler sponsor olsun! 💅",
                    "Eğlence zamanı! Para hazır mı? 💰",
                    "VIP gecesi başlasın! 🍾"
                ]
            
            elif personality == "yaratik_adam":  # yayincilara
                responses = [
                    f"{sender_name} yayını açsın, izleyelim!",
                    f"Evet {sender_name}, stream zamanı!",
                    f"Canlı yayında görüşürüz {sender_name}!",
                    f"Yayıncı kardeşim {sender_name}, ne duruyorsun?",
                    f"Stream açılsın {sender_name}, para var!",
                    "Donation rain başlasın! 💸",
                    "Yayın kalitesi VIP olmalı!",
                    "Streamer'lar buraya toplanın!"
                ]
            
            else:
                responses = [
                    f"Katılıyorum {sender_name}!",
                    f"Doğru söylüyorsun {sender_name}!",
                    "VIP'ler ne diyor bakalım?",
                    "Para konuşuyor burada!"
                ]
            
            # Bazen laf atma ekle
            if random.random() < 0.3:  # %30 olasılık
                laf_atma = random.choice(self.laf_atma_templates)
                # Rastgele bir kullanıcıya laf at
                random_users = ["Ahmet", "Mehmet", "Fatma", "Ayşe", "Mustafa", "Zeynep"]
                target_user = random.choice(random_users)
                laf_response = laf_atma.format(user_name=target_user)
                responses.append(laf_response)
            
            return random.choice(responses)
            
        except Exception as e:
            logger.warning(f"Generate response error: {e}")
            return "VIP'ler ne alemde? 💰"
    
    async def _update_user_profile(self, sender):
        """👤 Kullanıcı profilini güncelle"""
        try:
            if not sender or not hasattr(sender, 'id'):
                return
                
            user_id = sender.id
            user_name = getattr(sender, 'first_name', 'Anonim')
            username = getattr(sender, 'username', '')
            
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = {
                    "name": user_name,
                    "username": username,
                    "message_count": 0,
                    "last_seen": datetime.now(),
                    "laf_atilma_count": 0
                }
            
            self.user_profiles[user_id]["message_count"] += 1
            self.user_profiles[user_id]["last_seen"] = datetime.now()
            
        except Exception as e:
            logger.warning(f"Update user profile error: {e}")
    
    async def _load_conversation_topics(self):
        """📝 Conversation topic'lerini yükle"""
        try:
            self.conversation_topics = [
                "Para var mı burada?",
                "VIP olmak isteyenler?",
                "Sponsor arıyoruz!",
                "Bugün kim aktif?",
                "Premium özellikler açılsın!",
                "Yeni üyeler hoş geldiniz!",
                "Eğlence zamanı!",
                "Canlı yayın zamanı!",
                "Donation time!",
                "VIP gecesi başlasın!"
            ]
            
        except Exception as e:
            logger.warning(f"Load topics error: {e}")
    
    async def start_periodic_conversations(self):
        """🔄 Periyodik sohbet başlatıcı"""
        try:
            while self.is_running:
                try:
                    # Her 5-15 dakikada bir bot muhabbet başlatsın
                    await asyncio.sleep(random.randint(300, 900))
                    
                    if self.onlyvips_group_id and self.clients:
                        await self._start_random_conversation()
                    
                except Exception as e:
                    logger.warning(f"Periodic conversation error: {e}")
                    await asyncio.sleep(60)
                    
        except Exception as e:
            logger.error(f"Periodic conversations error: {e}")
    
    async def _start_random_conversation(self):
        """🎲 Rastgele sohbet başlat"""
        try:
            # Rastgele bot seç
            bot_name = random.choice(list(self.clients.keys()))
            bot_data = self.clients[bot_name]
            client = bot_data["client"]
            
            # Rastgele topic seç
            topic = random.choice(self.conversation_starters + self.conversation_topics)
            
            # Mesajı gönder
            await client.send_message(self.onlyvips_group_id, topic)
            
            print(f"""
🎲 RASTGELE SOHBET BAŞLATILDI!
🤖 Bot: {bot_name}
💬 Topic: {topic}
⏰ Zaman: {datetime.now().strftime('%H:%M:%S')}
════════════════════════════════════════════════════
            """)
            
        except Exception as e:
            logger.error(f"Start random conversation error: {e}")
    
    async def run_conversation_system(self):
        """🚀 Conversation sistemini çalıştır"""
        try:
            print("🚀 OnlyVips Bot Conversation System çalışıyor!")
            print("💬 Grup mesajları takip ediliyor...")
            print("🤖 Botlar hazır muhabbet etmeye!")
            print("🛑 Durdurmak için Ctrl+C kullanın")
            
            # Periyodik sohbet task'ını başlat
            conversation_task = asyncio.create_task(self.start_periodic_conversations())
            
            # Ana monitoring loop
            while self.is_running:
                try:
                    # Sistem durumunu logla
                    if datetime.now().minute % 10 == 0:
                        await self._log_conversation_status()
                    
                    await asyncio.sleep(30)
                    
                except KeyboardInterrupt:
                    print("\n🛑 Kullanıcı tarafından durduruldu")
                    break
                    
            conversation_task.cancel()
            
        except Exception as e:
            logger.error(f"Run conversation system error: {e}")
        finally:
            await self.shutdown()
    
    async def _log_conversation_status(self):
        """📊 Conversation durumunu logla"""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "active_bots": len(self.clients),
                "tracked_users": len(self.user_profiles),
                "last_message_times": {
                    bot_name: time.isoformat() if bot_name in self.last_message_time 
                    else "Never" for bot_name, time in self.last_message_time.items()
                }
            }
            
            logger.info(f"💬 Conversation Status: {json.dumps(status, default=str)}")
            
        except Exception as e:
            logger.warning(f"Status log error: {e}")
    
    async def shutdown(self):
        """🛑 Sistemi kapat"""
        try:
            print("\n🛑 OnlyVips Bot Conversation System kapatılıyor...")
            
            self.is_running = False
            
            # Bot clientları kapat
            for bot_name, bot_data in self.clients.items():
                try:
                    await bot_data["client"].disconnect()
                    print(f"   ✅ {bot_name} kapatıldı")
                except Exception as e:
                    logger.error(f"{bot_name} shutdown error: {e}")
            
            print("✅ OnlyVips Bot Conversation System kapatıldı!")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

async def main():
    """🚀 Ana fonksiyon"""
    try:
        # Conversation system oluştur
        conversation_system = OnlyVipsBotConversationSystem()
        
        # Başlat
        if await conversation_system.initialize():
            # Çalıştır
            await conversation_system.run_conversation_system()
        else:
            print("❌ Conversation system başlatılamadı")
            import sys
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"❌ Main error: {e}")
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
            logging.FileHandler(f'onlyvips_conversation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )
    
    # Çalıştır
    asyncio.run(main()) 