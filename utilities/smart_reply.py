#!/usr/bin/env python3
# utils/smart_reply.py

import random
import re
import json
from pathlib import Path
from typing import Optional, List, Dict
from gpt.flirt_agent import generate_reply
from utilities.log_utils import log_event

class SmartReplySystem:
    def __init__(self):
        # Genel mesaj havuzlarını yükle
        self.global_engaging_messages = self._load_global_messages("data/group_spam_messages.json", "engaging_messages")
        self.global_reply_messages = self._load_global_messages("data/reply_messages.json", "default")
        
        # VIP grup satış odaklı mesajlar
        self.vip_sales_messages = [
            "VIP grubumda çok daha özel içerikler var 🔥 Katılmak ister misin?",
            "Özel VIP kanalımda seni bekliyorum 💋 Daha fazlası için DM at",
            "VIP üyeliğin ile özel show'larıma erişebilirsin 😈",
            "Sana özel VIP teklifim var... İlgin varsa yaz 💎",
            "VIP grubumda sadece seçkin üyelerim var 👑 Sen de katıl",
            "Özel VIP içeriklerim için mesaj at 🎭 Pişman olmayacaksın",
            "VIP kanalımda daha cesur içerikler paylaşıyorum 🔥",
            "Sana özel VIP fırsatım var... Kaçırma 💋",
            "VIP üyelerime özel muamele yapıyorum 😘 Sen de ol",
            "Özel VIP grubumda seni görmek isterim 💕"
        ]
        
        # ===== YENİ: SATIŞ KAPATMA ODAKLI MESAJLAR =====
        self.sales_closing_messages = [
            "VIP grubuma katılmak istersen sadece 300₺ 💎 Hemen IBAN'ımı verebilirim",
            "Özel VIP kanalım için 300₺ 🔥 Hangi banka kullanıyorsun?",
            "VIP üyelik 300₺ canım 💋 Ödeme yapmak istersen banka seç",
            "300₺ ile VIP grubuma katıl 👑 IBAN bilgimi göndereyim mi?",
            "VIP deneyim sadece 300₺ 😈 Hangi bankadan ödeme yapacaksın?",
            "Özel VIP içerikler 300₺ 💕 Papara mı yoksa IBAN mı?",
            "VIP grubum 300₺ tatlım 🎭 Ödeme bilgilerimi paylaşayım mı?",
            "300₺ VIP üyelik 🔥 Hangi banka hesabın var?",
            "VIP kanalıma 300₺ ile katıl 💎 IBAN'ımı atayım mı?",
            "Özel VIP grup 300₺ 💋 Banka bilgilerini söyle, IBAN göndereyim"
        ]
        
        # Basit anahtar kelime eşleştirmeleri
        self.keyword_responses = {
            # Selamlaşma
            "selam|merhaba|hey|hi|hello": [
                "Selam canım! Nasılsın? 😘",
                "Merhaba tatlım! Bugün nasıl geçiyor? 💋",
                "Hey! Seni görmek güzel 😍",
                "Selam yakışıklı! Ne yapıyorsun? 🔥"
            ],
            
            # Nasılsın soruları
            "nasılsın|naber|ne yapıyorsun|keyifler": [
                "İyiyim canım, sen nasılsın? 😊",
                "Harikayım! Sen ne yapıyorsun? 💖",
                "Çok iyiyim, seninle daha da iyi oldum 😘",
                "Mükemmelim! Senden haber bekliyordum 🥰"
            ],
            
            # Flört/ilgi
            "güzelsin|seksi|harika|muhteşem|çok güzel": [
                "Teşekkür ederim canım 😍 Sen de çok tatlısın",
                "Ah, beni utandırdın 🙈 Ama hoşuma gitti",
                "Sen de çok yakışıklısın 😘",
                "Bu sözlerin beni çok mutlu etti 💕"
            ],
            
            # Buluşma/görüşme
            "buluşalım|görüşelim|çıkalım|randevu": [
                "Tabii ki! Ne zaman müsaitsin? 😊",
                "Çok isterim! Nerede buluşalım? 💋",
                "Harika fikir! Planını dinliyorum 😍",
                "Evet! Çok heyecanlıyım 🥰"
            ],
            
            # Fiyat/hizmet soruları
            "fiyat|ücret|kaç para|ne kadar|hizmet|menü": [
                "Hizmet menümü gönderdim, incele bakalım 💋",
                "Fiyatlarım çok uygun, menüye bak 😘",
                "Her bütçeye uygun seçeneklerim var 💖"
            ],
            
            # VIP/özel içerik
            "vip|özel|premium|exclusive|kanal|grup": [
                "VIP grubumda çok daha özel şeyler var 🔥 Katılmak ister misin?",
                "Özel VIP kanalımda seni bekliyorum 💋",
                "VIP üyeliğin ile çok daha fazlasına erişebilirsin 😈",
                "Sana özel VIP teklifim var... İlgin varsa yaz 💎"
            ],
            
            # Olumsuz/reddedici
            "hayır|istemiyorum|olmaz|gerek yok": [
                "Tamam canım, anlıyorum 😊",
                "Sorun değil, ne zaman istersen 💋",
                "Peki tatlım, başka bir şey var mı? 😘"
            ],
            
            # Teşekkür
            "teşekkür|sağol|thanks": [
                "Rica ederim canım 😘",
                "Ne demek tatlım 💋",
                "Her zaman! 😍"
            ]
        }
        
        # Emoji'li kısa mesajlar
        self.emoji_responses = {
            "❤️|💕|💖|💗|💘": [
                "Aww 🥰💕",
                "Sen de 💖😘",
                "Çok tatlısın 💋❤️"
            ],
            "😘|😍|🥰|😊": [
                "😘💋",
                "🥰❤️",
                "😍💕"
            ],
            "🔥|💋|😈": [
                "🔥😈",
                "💋🔥",
                "😈💕"
            ]
        }

    def _load_global_messages(self, file_path: str, key: str) -> List[str]:
        """Genel mesaj dosyalarından mesajları yükler."""
        try:
            path = Path(file_path)
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if file_path.endswith("group_spam_messages.json"):
                        return data.get("_template", {}).get(key, [])
                    else:
                        return data.get(key, [])
            return []
        except Exception as e:
            log_event("smart_reply", f"❌ Mesaj dosyası yükleme hatası {file_path}: {e}")
            return []

    def get_mixed_messages(self, bot_messages: List[str], message_type: str = "reply") -> str:
        """
        Bot'a özgü mesajları ana kaynak olarak kullanır, genel havuzdan çeşitlilik sağlar.
        
        Dağılım:
        - %70 bot'a özgü mesajlar
        - %30 genel havuz mesajları
        """
        if not bot_messages:
            # Bot mesajı yoksa genel havuzdan seç
            if message_type == "engaging":
                return random.choice(self.global_engaging_messages) if self.global_engaging_messages else "Merhaba! 😊"
            else:
                return random.choice(self.global_reply_messages) if self.global_reply_messages else "Teşekkürler! 😘"
        
        # %60 bot özgü, %40 genel havuz (daha dengeli çeşitlilik)
        use_bot_message = random.random() < 0.6
        
        if use_bot_message:
            return random.choice(bot_messages)
        else:
            # Genel havuzdan seç
            if message_type == "engaging":
                global_pool = self.global_engaging_messages
            else:
                global_pool = self.global_reply_messages
            
            if global_pool:
                return random.choice(global_pool)
            else:
                # Fallback: bot mesajı
                return random.choice(bot_messages)

    async def get_hybrid_reply(self, message: str, bot_profile: dict, agent_name: str) -> str:
        """
        Hybrid Mode: %60 GPT, %30 Bot Profili, %10 Genel Mesajlar
        GPT ağırlıklı doğal ve insani yanıt sistemi
        """
        
        # Rastgele dağılım belirle
        rand = random.random()
        
        if rand < 0.60:  # %60 GPT - Daha doğal ve insani
            try:
                log_event(agent_name, f"🤖 HYBRID: GPT yanıtı kullanılıyor (doğal mod)...")
                # VIP satış odaklı GPT prompt'u ile
                gpt_response = await self._get_vip_focused_gpt_reply(message, bot_profile, agent_name)
                log_event(agent_name, f"🤖 HYBRID GPT: {gpt_response}")
                return gpt_response
            except Exception as e:
                log_event(agent_name, f"❌ HYBRID GPT hatası: {e}")
                # Fallback bot profiline
                return await self._get_bot_profile_reply(message, bot_profile, agent_name)
                
        elif rand < 0.90:  # %30 Bot Profili (0.60 + 0.30 = 0.90)
            log_event(agent_name, f"👤 HYBRID: Bot profil yanıtı kullanılıyor...")
            response = await self._get_bot_profile_reply(message, bot_profile, agent_name)
            log_event(agent_name, f"👤 HYBRID BOT: {response}")
            return response
            
        else:  # %10 Genel Mesajlar
            log_event(agent_name, f"🌐 HYBRID: Genel mesaj havuzu kullanılıyor...")
            response = await self._get_global_pool_reply(message, agent_name)
            log_event(agent_name, f"🌐 HYBRID GLOBAL: {response}")
            return response

    async def _get_vip_focused_gpt_reply(self, message: str, bot_profile: dict, agent_name: str) -> str:
        """VIP grup satışına odaklı GPT yanıtı"""
        try:
            # Gelişmiş VIP satış odaklı sistem prompt'u kullan
            from gpt.system_prompt_manager import get_hybrid_vip_prompt
            from gpt.openai_utils import generate_gpt_reply
            
            vip_prompt = get_hybrid_vip_prompt(agent_name)
            
            user_prompt = f'Kullanıcı şöyle dedi: "{message}"\n\nBu mesaja VIP grup satışını teşvik edecek şekilde yanıt ver.'
            
            response = generate_gpt_reply(user_prompt, vip_prompt)
            return response.strip()
            
        except Exception as e:
            log_event(agent_name, f"❌ VIP GPT hatası: {e}")
            # Fallback: VIP satış mesajlarından rastgele seç
            return random.choice(self.vip_sales_messages)

    async def _get_bot_profile_reply(self, message: str, bot_profile: dict, agent_name: str) -> str:
        """Bot profilinden yanıt al - GPT destekli"""
        
        # %40 GPT ile doğal yanıt, %60 template yanıt
        if random.random() < 0.40:
            try:
                # GPT ile bot karakterine uygun doğal yanıt
                from gpt.system_prompt_manager import get_default_prompt
                from gpt.openai_utils import generate_gpt_reply
                
                character_prompt = get_default_prompt(agent_name)
                user_prompt = f'Kullanıcı şöyle dedi: "{message}"\n\nKarakterine uygun, doğal ve samimi bir yanıt ver.'
                
                gpt_response = generate_gpt_reply(user_prompt, character_prompt)
                log_event(agent_name, f"🤖 BOT PROFILE GPT: {gpt_response}")
                return gpt_response.strip()
                
            except Exception as e:
                log_event(agent_name, f"❌ Bot profil GPT hatası: {e}")
                # Fallback template'e
        
        # Template yanıt sistemi
        template_response = self.find_template_response(message, bot_profile)
        if template_response:
            return template_response
        
        # Bot'un reply_messages'ından seç
        reply_messages = bot_profile.get("reply_messages", [])
        if reply_messages:
            # %30 VIP satış mesajı karıştır
            if random.random() < 0.30:
                return random.choice(self.vip_sales_messages)
            else:
                return random.choice(reply_messages)
        
        # Fallback: VIP satış mesajı
        return random.choice(self.vip_sales_messages)

    async def _get_global_pool_reply(self, message: str, agent_name: str) -> str:
        """Genel mesaj havuzundan yanıt al - GPT destekli"""
        
        # %50 GPT ile doğal yanıt, %30 VIP satış, %20 genel mesajlar
        rand = random.random()
        
        if rand < 0.50:  # %50 GPT
            try:
                from gpt.system_prompt_manager import get_default_prompt
                from gpt.openai_utils import generate_gpt_reply
                
                # Genel doğal yanıt prompt'u
                general_prompt = f"""
Sen Telegram'da kullanıcılarla sohbet eden, sıcak ve eğlenceli bir yapay zekâ botsun.
Görevlerin: Samimi ol, emoji kullan, doğal konuş ve karakterini bozma.
Kısa, etkili ve emoji'li yanıtlar ver.
"""
                
                user_prompt = f'Kullanıcı şöyle dedi: "{message}"\n\nDoğal, samimi ve kısa bir yanıt ver.'
                
                gpt_response = generate_gpt_reply(user_prompt, general_prompt)
                log_event(agent_name, f"🤖 GLOBAL GPT: {gpt_response}")
                return gpt_response.strip()
                
            except Exception as e:
                log_event(agent_name, f"❌ Global GPT hatası: {e}")
                # Fallback VIP mesajına
        
        if rand < 0.60:  # %30 VIP satış mesajı (normal)
            return random.choice(self.vip_sales_messages)
        elif rand < 0.80:  # %20 Satış kapatma odaklı
            return random.choice(self.sales_closing_messages)
        elif self.global_reply_messages:  # %20 genel reply mesajları
            return random.choice(self.global_reply_messages)
        else:
            return random.choice(self.sales_closing_messages)

    def find_template_response(self, message: str, bot_profile: dict) -> Optional[str]:
        """Kayıtlı template'lerden uygun yanıt bulur."""
        message_lower = message.lower()
        
        # Bot profilinden reply_messages'ı al
        reply_messages = bot_profile.get("reply_messages", [])
        
        # Anahtar kelime eşleştirmesi
        for pattern, responses in self.keyword_responses.items():
            if re.search(pattern, message_lower):
                return random.choice(responses)
        
        # Emoji eşleştirmesi
        for pattern, responses in self.emoji_responses.items():
            if re.search(pattern, message):
                return random.choice(responses)
        
        # Bot'un kendi reply_messages'ından karışık seç
        if reply_messages and len(reply_messages) > 0:
            return self.get_mixed_messages(reply_messages, "reply")
        
        return None

    async def get_smart_reply(self, message: str, bot_profile: dict, agent_name: str) -> str:
        """
        Akıllı yanıt sistemi - GPT ağırlıklı:
        %70 GPT, %30 Template
        """
        
        # %70 GPT öncelikli doğal yanıt
        if random.random() < 0.70:
            try:
                log_event(agent_name, f"🤖 SMART REPLY: GPT öncelikli yanıt...")
                gpt_response = await generate_reply(agent_name=agent_name, user_message=message)
                log_event(agent_name, f"🤖 SMART GPT: {gpt_response}")
                return gpt_response
            except Exception as e:
                log_event(agent_name, f"❌ Smart GPT hatası: {e}")
                # Fallback template'e
        
        # %30 Template yanıt
        template_response = self.find_template_response(message, bot_profile)
        if template_response:
            log_event(agent_name, f"📝 Template yanıt kullanıldı: {template_response}")
            return template_response
        
        # Son fallback - GPT tekrar dene
        try:
            log_event(agent_name, f"🤖 GPT son fallback...")
            gpt_response = await generate_reply(agent_name=agent_name, user_message=message)
            log_event(agent_name, f"🤖 GPT fallback yanıtı: {gpt_response}")
            return gpt_response
        except Exception as e:
            log_event(agent_name, f"❌ GPT fallback hatası: {e}")
            # En son fallback
            fallback_messages = [
                "Biraz düşünmem lazım... Birazdan yazarım 😘",
                "Şu an kafam karışık, sonra konuşalım mı? 💋",
                "Bu konuyu biraz sonra konuşalım canım 😊",
                "Hmm... İlginç soru, düşüneyim 🤔💕"
            ]
            return random.choice(fallback_messages)

# Global instance
smart_reply = SmartReplySystem() 