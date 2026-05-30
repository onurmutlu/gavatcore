from infrastructure.config.logger import get_logger

"""
🤖 GPT Reply Generator - Karakter bazlı GPT yanıt üretim motoru
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio
from openai import AsyncOpenAI

# Token usage logger import
try:
    from .token_usage_logger import token_logger
    TOKEN_LOGGING_ENABLED = True
except ImportError:
    TOKEN_LOGGING_ENABLED = False
    
logger = logging.getLogger(__name__)

class GPTReplyGenerator:
    """GPT tabanlı yanıt üretici"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ OpenAI API key bulunamadı - GPT özellikleri devre dışı")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info("✅ GPT Reply Generator başlatıldı")
        
        # Default GPT ayarları
        self.default_settings = {
            "model": "gpt-4-turbo-preview",
            "temperature": 0.8,
            "max_tokens": 300,
            "presence_penalty": 0.3,
            "frequency_penalty": 0.3
        }
    
    async def generate_reply(
        self,
        user_message: str,
        character_config: Dict[str, Any],
        context_messages: List[Dict[str, str]] = None,
        strategy: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Optional[str]:
        """
        GPT ile yanıt üret
        
        Args:
            user_message: Kullanıcının mesajı
            character_config: Karakter konfigürasyonu
            context_messages: Önceki mesajlar (bağlam)
            strategy: Özel strateji (flirt, tease, spiritual vb.)
            user_id: Kullanıcı ID (token loglama için)
        
        Returns:
            GPT'nin ürettiği yanıt veya None
        """
        if not self.client:
            logger.error("❌ GPT client mevcut değil")
            return None
        
        try:
            # Sistem promptunu hazırla
            system_prompt = self._build_system_prompt(character_config, strategy)
            
            # Mesajları hazırla
            messages = [{"role": "system", "content": system_prompt}]
            
            # Bağlam mesajlarını ekle
            if context_messages:
                for msg in context_messages[-10:]:  # Son 10 mesaj
                    messages.append(msg)
            
            # Kullanıcı mesajını ekle
            messages.append({"role": "user", "content": user_message})
            
            # GPT ayarlarını al
            gpt_settings = character_config.get("gpt_settings", {})
            settings = {**self.default_settings, **gpt_settings}
            
            # Model seçimi - dynamic model selection
            model = self._select_model(character_config, strategy, user_message)
            
            # GPT'ye sor
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=settings["temperature"],
                max_tokens=settings["max_tokens"],
                presence_penalty=settings["presence_penalty"],
                frequency_penalty=settings["frequency_penalty"]
            )
            
            reply = response.choices[0].message.content.strip()
            
            # Token kullanımını logla
            if TOKEN_LOGGING_ENABLED and response.usage:
                token_logger.log_usage(
                    character=character_config.get("name", "Unknown"),
                    user_id=user_id or "unknown",
                    model=model,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    reply_mode=character_config.get("reply_mode", "gpt"),
                    success=True
                )
            
            # Karaktere özel düzenlemeler
            reply = self._apply_character_style(reply, character_config)
            
            logger.info(f"✅ GPT yanıtı üretildi - Model: {model}, {len(reply)} karakter")
            return reply
            
        except Exception as e:
            logger.error(f"❌ GPT yanıt üretme hatası: {e}")
            
            # Hata durumunda da logla
            if TOKEN_LOGGING_ENABLED:
                token_logger.log_usage(
                    character=character_config.get("name", "Unknown"),
                    user_id=user_id or "unknown",
                    model=settings.get("model", "unknown"),
                    prompt_tokens=0,
                    completion_tokens=0,
                    reply_mode=character_config.get("reply_mode", "gpt"),
                    success=False
                )
            
            return None
    
    def _select_model(self, character_config: Dict[str, Any], strategy: Optional[str], message: str) -> str:
        """
        Dinamik model seçimi - maliyet optimizasyonu
        
        Stratejiler:
        - Kısa/basit mesajlar → GPT-3.5
        - Flört/satış → GPT-4
        - Teknik/karmaşık → GPT-4
        - Grup mesajları → GPT-3.5 (hız öncelikli)
        """
        # Config'de belirtilmişse öncelik onda
        if "gpt_model" in character_config:
            return character_config["gpt_model"]
        
        # Mesaj uzunluğu ve karmaşıklık kontrolü
        message_length = len(message.split())
        
        # Basit selamlaşma, kısa sorular
        if message_length < 5 or any(word in message.lower() for word in ["merhaba", "selam", "nasılsın", "naber"]):
            return "gpt-3.5-turbo"
        
        # Satış/VIP sorgular - yüksek kalite gerekli
        if any(word in message.lower() for word in ["vip", "özel", "video", "ödeme", "fiyat", "papara"]):
            return "gpt-4-turbo-preview"
        
        # Flört stratejisi - yaratıcılık gerekli
        if strategy in ["flirt", "seductive", "manipulative"]:
            return "gpt-4-turbo-preview"
        
        # Karakter tonu agresif/dominant - güçlü model
        tone = character_config.get("tone", "")
        if tone in ["aggressive", "dark"]:
            return "gpt-4"
        
        # Default: orta seviye
        return "gpt-3.5-turbo-16k"
    
    def _build_system_prompt(self, character_config: Dict[str, Any], strategy: str = None) -> str:
        """Karakter ve stratejiye göre sistem promptu oluştur"""
        
        base_prompt = character_config.get("system_prompt", "")
        
        # Humanizer ekleme
        humanizer_prompt = """
        
        ÖNEMLI: ASLA BOT GİBİ DAVRANMA! İnsan gibi yaz:
        - Bazen yazım hataları yap (çok az)
        - Emoji ve ses efektleri kullan (hmm, şey, aa gibi)
        - Bazen eksik cümle kur veya yarıda kes
        - Duygusal tepkiler ver
        - Mükemmel değil, doğal ol
        """
        
        # Strateji bazlı eklemeler
        strategy_prompts = {
            "engage": """
            Kullanıcıyı konuşmaya teşvik et. Sorular sor, merak uyandır.
            Aktif dinleme göster, onun söylediklerini referans al.
            """,
            
            "tease": """
            Biraz mesafe koy ama ilgiyi koru. Gizemli ol.
            Her şeyi açıklama, merak bırak. Flörtöz ama ulaşılmaz.
            """,
            
            "emotionally_intense": """
            Duygusal yoğunluk yarat. Derin hisler, tutkulu ifadeler.
            Ama manipülatif değil, samimi görün.
            """,
            
            "casual": """
            Rahat ve samimi ol. Arkadaşça konuş.
            Günlük konulardan bahset, ortak noktalar bul.
            """,
            
            "mysterious": """
            Az konuş, çok şey ima et. Gizemini koru.
            Direkt cevaplar verme, dolaylı ol.
            """,
            
            "pullback": """
            Biraz soğuk davran. Meşgul görün.
            Kısa cevaplar ver ama tamamen kopma.
            """
        }
        
        # Prompt birleştir
        final_prompt = base_prompt + humanizer_prompt
        
        if strategy and strategy in strategy_prompts:
            final_prompt += f"\n\nSTRATEJİ: {strategy_prompts[strategy]}"
        
        # Ton bazlı eklemeler
        tone = character_config.get("tone", "casual")
        tone_prompts = {
            "flirty": "Flörtöz, çekici ama asla ucuz olmayan bir tonda yaz.",
            "soft": "Yumuşak, anlayışlı, destekleyici bir tonda yaz.",
            "dark": "Biraz karanlık, gizemli, tehlikeli bir havada yaz.",
            "mystic": "Mistik, ruhsal, derin anlamlar içeren bir tonda yaz.",
            "aggressive": "Sert, dominant, kontrolcü bir tonda yaz."
        }
        
        if tone in tone_prompts:
            final_prompt += f"\n\nTON: {tone_prompts[tone]}"
        
        return final_prompt
    
    def _apply_character_style(self, reply: str, character_config: Dict[str, Any]) -> str:
        """Karaktere özel stil düzenlemeleri uygula"""
        name = character_config.get("name", "")
        tone = character_config.get("tone", "flirty")
        
        # Karakter bazlı özel düzenlemeler
        if name.lower() == "lara":
            # Lara'ya özel
            if tone == "flirty" and "?" not in reply:
                reply += " 😊"
        
        elif name.lower() == "babagavat":
            # BabaGavat'a özel - sokak ağzı ekle
            reply = reply.replace("merhaba", "naber lan")
            reply = reply.replace("nasılsın", "naptın la")
        
        elif name.lower() == "geisha":
            # Geisha'ya özel - mistik dokunuş
            if tone == "mystic":
                reply = f"🌸 {reply} 🌸"
        
        return reply
    
    async def generate_fallback_reply(
        self,
        character_config: Dict[str, Any],
        context: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Fallback (yedek) yanıt üret
        
        Args:
            character_config: Karakter konfigürasyonu  
            context: Ek bağlam bilgisi
            user_id: Kullanıcı ID (token loglama için)
        
        Returns:
            Fallback yanıt
        """
        if not self.client:
            # GPT yoksa template kullan
            templates = character_config.get("template_replies", [])
            if templates:
                import random
                return random.choice(templates)
            return None
        
        try:
            name = character_config.get("name", "Assistant")
            tone = character_config.get("tone", "flirty")
            
            prompt = f"""Sen {name} isimli bir karaktersin. Kullanıcı bir süredir yazmıyor veya yanıt vermedi. 
            Ona {tone} tonda kısa bir hatırlatma/takılma mesajı yaz. Maksimum 1-2 cümle.
            """
            
            if context:
                prompt += f"\nBağlam: {context}"
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Fallback için ucuz model
                messages=[{"role": "system", "content": prompt}],
                temperature=0.9,
                max_tokens=100
            )
            
            # Token kullanımını logla
            if TOKEN_LOGGING_ENABLED and response.usage:
                token_logger.log_usage(
                    character=name,
                    user_id=user_id or "fallback",
                    model="gpt-3.5-turbo",
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    reply_mode="fallback",
                    success=True
                )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ Fallback yanıt üretme hatası: {e}")
            
            # GPT başarısız olursa template kullan
            templates = character_config.get("template_replies", [])
            if templates:
                import random
                return random.choice(templates)
            
            return None
    
    async def analyze_user_message(self, message: str) -> Dict[str, Any]:
        """
        Kullanıcı mesajını analiz et
        
        Returns:
            Duygu, niyet, risk skoru vb. analiz sonuçları
        """
        if not self.client:
            return {
                "emotion": "neutral",
                "intent": "chat",
                "risk_score": 0.5,
                "topics": []
            }
        
        try:
            analysis_prompt = f"""
            Aşağıdaki mesajı analiz et ve JSON formatında yanıt ver:
            
            Mesaj: "{message}"
            
            JSON formatı:
            {{
                "emotion": "happy/sad/angry/neutral/flirty/desperate",
                "intent": "chat/flirt/complaint/question/spam",
                "risk_score": 0.0-1.0 (manipulation riski),
                "topics": ["konu1", "konu2"],
                "urgency": "low/medium/high"
            }}
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Analiz için ucuz model yeterli
                messages=[{"role": "system", "content": analysis_prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            result = response.choices[0].message.content.strip()
            return json.loads(result)
            
        except Exception as e:
            logger.error(f"❌ Mesaj analiz hatası: {e}")
            return {
                "emotion": "neutral",
                "intent": "chat",
                "risk_score": 0.5,
                "topics": [],
                "urgency": "medium"
            } 