#!/usr/bin/env python3
"""
🔄 Fallback Reply Manager - Yedek yanıt yönetim sistemi
"""

import random
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import structlog

logger = structlog.get_logger("gavatcore.fallback_reply_manager")

class FallbackReplyManager:
    """Timeout ve no-reply durumları için yedek yanıt yöneticisi"""
    
    def __init__(self):
        self.fallback_replies: List[Dict[str, Any]] = []
        logger.info("🔄 FallbackReplyManager başlatıldı")
        
        # Fallback kategorileri ve şablonları
        self.fallback_templates = {
            "timeout": {
                "flirty": [
                    "Beni unutmadın değil mi? 😊",
                    "Sessizliğin çok seksi... ama biraz da konuşsak? 💋",
                    "Meşgul müsün canım? Seni merak ettim 🥰",
                    "Bu kadar sessiz olma, özledim seni 💕"
                ],
                "soft": [
                    "Umarım iyisindir 🌸",
                    "Sessizliğin endişelendiriyor beni...",
                    "Her şey yolunda mı tatlım?",
                    "Konuşmak istediğinde buradayım 💝"
                ],
                "dark": [
                    "Sessizlik... ilginç bir seçim.",
                    "Karanlıkta kaybolmuş gibisin...",
                    "Bu sessizliğin bir anlamı var mı?",
                    "Gölgelerde saklanmayı mı tercih ediyorsun?"
                ],
                "mystic": [
                    "Evren senin adına konuşuyor... sessizliğinle 🔮",
                    "Ruhun başka alemlerde geziniyor sanırım ✨",
                    "Sessizlik de bir cevaptır aslında 🌙",
                    "Enerjin uzaklarda hissediyorum 🙏"
                ],
                "aggressive": [
                    "Cevap versene!",
                    "Bu kadar sus yeter artık",
                    "Konuş benimle, hemen!",
                    "Sessizliğin sinir bozucu"
                ]
            },
            "no_reply": {
                "flirty": [
                    "Galiba bugün beni düşünmüyorsun 😔💔",
                    "Başka biriyle mi konuşuyorsun? 😏",
                    "Seni beklemekten yoruldum... ama değersin 💋",
                    "Bu oyunu sevdim, sen kaçıyorsun ben kovalıyorum 😈"
                ],
                "soft": [
                    "Belki sonra konuşuruz 🌺",
                    "Seni zorlamak istemem, hazır olduğunda yazarsın",
                    "Buradayım, ne zaman istersen 💫",
                    "Herkesin kendine zaman ayırmaya hakkı var 🤗"
                ],
                "dark": [
                    "İlgisizliğin bir mesaj veriyor...",
                    "Görünmez olmayı başardın",
                    "Bu sessizlik oyunu hoşuma gitti",
                    "Kaybolmuşsun... ya da kaçıyorsun?"
                ],
                "mystic": [
                    "Kader bizi tekrar buluşturacak 🌟",
                    "Sessizliğin içindeki mesajı okuyorum",
                    "Ruhların buluşması için doğru zaman değil henüz",
                    "Evrenin planı farklıymış demek ki ☯️"
                ],
                "aggressive": [
                    "Beni görmezden gelmeye devam et bakalım",
                    "Bu tavrın hoşuma gitmiyor!",
                    "Seninle işim bitmedi daha",
                    "Kaçamazsın benden!"
                ]
            },
            "re_engage": {
                "flirty": [
                    "Seni özledim... hala orada mısın? 👀",
                    "Bir selam bile çok mu? 🥺💕",
                    "Sensiz geçen her dakika işkence 😩",
                    "Gel artık, sana anlatacaklarım var 😘"
                ],
                "soft": [
                    "Merhaba, nasılsın? 🌸",
                    "Umarım güzel bir gün geçiriyorsundur",
                    "Sadece selam vermek istedim 😊",
                    "İyi misin? Merak ettim seni"
                ],
                "dark": [
                    "Hala hayatta mısın?",
                    "Sessizliğin sırrını çözdüm sanırım...",
                    "Geri dön, oyun bitmedi",
                    "Karanlıktan korkmuyorsun değil mi?"
                ],
                "mystic": [
                    "Yıldızlar senin adını fısıldıyor 🌟",
                    "Bir işaret gönderdim, aldın mı?",
                    "Rüyalarında görüştük sanki ✨",
                    "Enerjin yaklaşıyor, hissediyorum"
                ],
                "aggressive": [
                    "YAZ ARTIK!",
                    "Daha ne kadar bekleyeceğim?",
                    "Sabrim taşıyor!",
                    "CEVAP VER!"
                ]
            }
        }
        
        # Kullanıcı bazlı fallback geçmişi
        self.user_fallback_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Fallback stratejileri
        self.strategies = {
            "progressive": self._progressive_strategy,
            "random": self._random_strategy,
            "adaptive": self._adaptive_strategy,
            "persistent": self._persistent_strategy
        }
    
    async def get_fallback_reply(
        self,
        user_id: str,
        character_config: Dict[str, Any],
        fallback_type: str = "timeout",
        last_message_time: Optional[datetime] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Fallback yanıtı getir
        
        Args:
            user_id: Kullanıcı ID
            character_config: Karakter konfigürasyonu
            fallback_type: Fallback tipi (timeout/no_reply/re_engage)
            last_message_time: Son mesaj zamanı
            user_context: Kullanıcı bağlam bilgileri
        
        Returns:
            Fallback yanıt veya None
        """
        tone = character_config.get("tone", "flirty")
        fallback_strategy = character_config.get("fallback_strategy", "random")
        
        # Kullanıcı geçmişini kontrol et
        if user_id not in self.user_fallback_history:
            self.user_fallback_history[user_id] = []
        
        # Fallback zamanlamasını kontrol et
        if not self._should_send_fallback(user_id, last_message_time):
            return None
        
        # Stratejiyi uygula
        if fallback_strategy == "template":
            # Sadece template kullan
            reply = self._get_template_reply(fallback_type, tone)
        elif fallback_strategy == "template_or_gpt":
            # Önce template dene, yoksa GPT (GPT kısmı dış modülde)
            reply = self._get_template_reply(fallback_type, tone)
        elif fallback_strategy in self.strategies:
            # Özel strateji uygula
            reply = await self.strategies[fallback_strategy](
                user_id, character_config, fallback_type, user_context
            )
        else:
            # Default random
            reply = self._get_template_reply(fallback_type, tone)
        
        # Geçmişe ekle
        self._add_to_history(user_id, fallback_type, reply)
        
        logger.info(f"🔄 Fallback yanıt üretildi - Tip: {fallback_type}, Ton: {tone}")
        
        return reply
    
    def _should_send_fallback(self, user_id: str, last_message_time: Optional[datetime]) -> bool:
        """Fallback gönderilmeli mi kontrol et"""
        if not last_message_time:
            return True
        
        # Son fallback zamanını kontrol et
        user_history = self.user_fallback_history.get(user_id, [])
        if user_history:
            last_fallback = user_history[-1]
            last_fallback_time = datetime.fromisoformat(last_fallback["timestamp"])
            
            # En az 30 dakika bekle
            if datetime.now() - last_fallback_time < timedelta(minutes=30):
                return False
        
        # Son mesajdan bu yana geçen süre
        time_since_last_message = datetime.now() - last_message_time
        
        # En az 15 dakika bekle
        if time_since_last_message < timedelta(minutes=15):
            return False
        
        return True
    
    def _get_template_reply(self, fallback_type: str, tone: str) -> str:
        """Template yanıt seç"""
        templates = self.fallback_templates.get(fallback_type, {}).get(tone, [])
        
        if not templates:
            # Default templates
            templates = self.fallback_templates.get(fallback_type, {}).get("flirty", [])
        
        if templates:
            return random.choice(templates)
        
        return "Hey, orada mısın? 👋"
    
    def _add_to_history(self, user_id: str, fallback_type: str, reply: str) -> None:
        """Fallback geçmişine ekle"""
        if user_id not in self.user_fallback_history:
            self.user_fallback_history[user_id] = []
        
        self.user_fallback_history[user_id].append({
            "timestamp": datetime.now().isoformat(),
            "type": fallback_type,
            "reply": reply
        })
        
        # Maksimum 50 kayıt tut
        if len(self.user_fallback_history[user_id]) > 50:
            self.user_fallback_history[user_id] = self.user_fallback_history[user_id][-50:]
    
    # Strateji fonksiyonları
    async def _progressive_strategy(
        self,
        user_id: str,
        character_config: Dict[str, Any],
        fallback_type: str,
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Progressive strateji - Giderek artan yoğunluk"""
        tone = character_config.get("tone", "flirty")
        user_history = self.user_fallback_history.get(user_id, [])
        
        # Kaç kez fallback gönderilmiş
        fallback_count = len(user_history)
        
        if fallback_count < 2:
            # İlk fallbackler soft
            templates = self.fallback_templates.get("timeout", {}).get("soft", [])
        elif fallback_count < 5:
            # Orta seviye
            templates = self.fallback_templates.get(fallback_type, {}).get(tone, [])
        else:
            # Yoğun
            templates = self.fallback_templates.get("re_engage", {}).get("aggressive", [])
        
        if templates:
            return random.choice(templates)
        
        return self._get_template_reply(fallback_type, tone)
    
    async def _random_strategy(
        self,
        user_id: str,
        character_config: Dict[str, Any],
        fallback_type: str,
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Random strateji - Tamamen rastgele"""
        tone = character_config.get("tone", "flirty")
        return self._get_template_reply(fallback_type, tone)
    
    async def _adaptive_strategy(
        self,
        user_id: str,
        character_config: Dict[str, Any],
        fallback_type: str,
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Adaptive strateji - Kullanıcı davranışına göre uyarla"""
        tone = character_config.get("tone", "flirty")
        
        if user_context:
            trust_index = user_context.get("trust_index", 0.5)
            response_rate = user_context.get("response_rate", 0.5)
            
            # Düşük güven veya yanıt oranı - soft yaklaş
            if trust_index < 0.3 or response_rate < 0.3:
                tone = "soft"
            # Yüksek güven - daha agresif olabilir
            elif trust_index > 0.8:
                tone = "aggressive" if random.random() > 0.5 else tone
        
        return self._get_template_reply(fallback_type, tone)
    
    async def _persistent_strategy(
        self,
        user_id: str,
        character_config: Dict[str, Any],
        fallback_type: str,
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Persistent strateji - Israrcı ve sürekli"""
        # Her zaman re_engage tipinde agresif mesajlar
        templates = self.fallback_templates.get("re_engage", {}).get("aggressive", [])
        
        if templates:
            return random.choice(templates)
        
        return "CEVAP VER ARTIK!"
    
    def get_fallback_schedule(self, user_id: str) -> List[Dict[str, Any]]:
        """Kullanıcı için fallback zamanlamasını getir"""
        base_schedule = [
            {"delay_minutes": 15, "type": "timeout"},
            {"delay_minutes": 60, "type": "no_reply"},
            {"delay_minutes": 180, "type": "re_engage"},
            {"delay_minutes": 1440, "type": "re_engage"}  # 24 saat
        ]
        
        # Kullanıcı geçmişine göre özelleştir
        user_history = self.user_fallback_history.get(user_id, [])
        if len(user_history) > 10:
            # Çok fallback gönderilmiş, araları aç
            for item in base_schedule:
                item["delay_minutes"] *= 2
        
        return base_schedule
    
    def clear_user_history(self, user_id: str) -> None:
        """Kullanıcı fallback geçmişini temizle"""
        if user_id in self.user_fallback_history:
            del self.user_fallback_history[user_id]
            logger.info(f"🗑️ Fallback geçmişi temizlendi: {user_id}")

    def add_fallback_reply(self, reply: Dict[str, Any]):
        """Yedek yanıt ekle"""
        self.fallback_replies.append(reply)
        logger.info(f"✅ Yedek yanıt eklendi: {reply.get('id', 'unknown')}")

    def get_fallback_replies(self) -> List[Dict[str, Any]]:
        """Tüm yedek yanıtları getir"""
        return self.fallback_replies

# Global instance
fallback_reply_manager = FallbackReplyManager() 