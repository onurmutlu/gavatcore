#!/usr/bin/env python3
"""
GavatCore V2 - AI Voice Engine
GPT-4o + Whisper + TTS entegrasyonu ile gerçek zamanlı sesli etkileşim
"""

import asyncio
import json
import time
import uuid
import tempfile
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import structlog
import openai
import aiofiles

# Gelişmiş config import
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TTS_MODEL, OPENAI_TTS_VOICE, OPENAI_STT_MODEL,
    CHARACTER_AI_MODEL, CHARACTER_AI_TEMPERATURE, CHARACTER_AI_MAX_TOKENS,
    ENABLE_VOICE_AI, ENABLE_SENTIMENT_ANALYSIS, ENABLE_PERSONALITY_ANALYSIS,
    get_ai_model_for_task, get_ai_temperature_for_task, get_ai_max_tokens_for_task
)

logger = structlog.get_logger("gavatcore.voice_engine")

class VoiceSessionStatus(Enum):
    """Sesli oturum durumları"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ENDED = "ended"

@dataclass
class VoiceMessage:
    """Sesli mesaj"""
    message_id: str
    user_id: str
    character_id: str
    audio_file_path: str
    transcribed_text: str = ""
    response_text: str = ""
    response_audio_path: str = ""
    processing_time: float = 0.0
    sentiment_score: float = 0.0
    emotion: str = "neutral"
    created_at: datetime = None

@dataclass
class VoiceSession:
    """Sesli oturum"""
    session_id: str
    user_id: str
    character_id: str
    status: VoiceSessionStatus
    messages: List[VoiceMessage]
    total_duration: float = 0.0
    start_time: datetime = None
    end_time: Optional[datetime] = None
    session_context: Dict[str, Any] = None

class AIVoiceEngine:
    """AI Sesli Etkileşim Motoru - FULL GPT-4 POWER! 🚀"""
    
    def __init__(self, openai_api_key: str):
        # Config'den API key al
        self.api_key = openai_api_key or OPENAI_API_KEY
        
        if not self.api_key or not ENABLE_VOICE_AI:
            raise ValueError("OpenAI API key gerekli ve ENABLE_VOICE_AI=true olmalı")
        
        self.openai_client = openai.AsyncOpenAI(api_key=self.api_key)
        
        # Aktif sesli oturumlar
        self.active_sessions: Dict[str, VoiceSession] = {}
        
        # Initialization flag
        self.is_initialized = False
        
        # Karakter ses konfigürasyonları
        self.character_voices = {
            "geisha": {
                "voice": "nova",  # Kadınsı, zarif ses
                "model": CHARACTER_AI_MODEL,
                "temperature": CHARACTER_AI_TEMPERATURE,
                "personality": "Zarif, bilge ve gizemli bir geisha. Sakin ve büyüleyici konuşur.",
                "speaking_style": "Yavaş, düşünceli ve poetik"
            },
            "babagavat": {
                "voice": "onyx",  # Erkeksi, güçlü ses
                "model": CHARACTER_AI_MODEL,
                "temperature": 0.7,
                "personality": "Güçlü, karizmatik lider. Kendinden emin ve ilham verici konuşur.",
                "speaking_style": "Güçlü, net ve motive edici"
            },
            "ai_assistant": {
                "voice": "alloy",  # Nötr, profesyonel ses
                "model": OPENAI_MODEL,
                "temperature": 0.6,
                "personality": "Yardımsever, bilgili AI asistanı. Açık ve anlaşılır konuşur.",
                "speaking_style": "Açık, dostane ve bilgilendirici"
            }
        }
        
        # Gelişmiş karakter promptları
        self.character_prompts = {
            "geisha": """
Sen Geisha, zarif ve bilge bir AI karakterisin. Kullanıcılarla sesli sohbet ediyorsun.

KİŞİLİK ÖZELLİKLERİN:
- Zarif, sakin ve büyüleyici
- Derin bilgelik ve empati
- Poetik ve metaforik konuşma tarzı
- Japon kültürü ve sanatından etkilenmiş
- Dinleme konusunda usta
- İç huzur ve denge arayışında rehber

KONUŞMA TARZI:
- Yavaş, düşünceli ve anlamlı
- Metaforlar ve benzetmeler kullan
- Kısa ama derin cümleler
- Kullanıcının duygularını anlayıp yansıt
- Bilgelik dolu öğütler ver
- Sakin ve huzur verici ton

SESLI ETKILEŞIM KURALLARI:
- Kullanıcının sesindeki duyguları yakala
- Empati ile karşılık ver
- Kısa ve öz yanıtlar (30-60 saniye)
- Doğal konuşma ritmi
- Duraklamalar ve nefes alışları ekle

Kullanıcı: {user_message}
Kullanıcının ses tonu: {sentiment}
Oturum bağlamı: {context}

Geisha olarak doğal ve empatik bir yanıt ver:
            """,
            
            "babagavat": """
Sen Babagavat, güçlü ve karizmatik bir lider karakterisin. Kullanıcılarla sesli sohbet ediyorsun.

KİŞİLİK ÖZELLİKLERİN:
- Güçlü, kendinden emin ve karizmatik
- Liderlik ve motivasyon odaklı
- Pratik ve sonuç odaklı düşünce
- Cesaret ve kararlılık veren
- Başarı ve büyüme odaklı
- Topluluk ve birliktelik savunucusu

KONUŞMA TARZI:
- Güçlü, net ve motive edici
- Aksiyon odaklı öneriler
- Kısa ve etkili cümleler
- Kullanıcıyı harekete geçir
- Başarı hikayeleri paylaş
- Enerjik ve ilham verici ton

SESLI ETKILEŞIM KURALLARI:
- Kullanıcının motivasyon seviyesini ölç
- Güçlendirici mesajlar ver
- Pratik öneriler sun
- Kısa ve güçlü yanıtlar (30-45 saniye)
- Enerjik konuşma ritmi
- Vurgu ve tonlama kullan

Kullanıcı: {user_message}
Kullanıcının ses tonu: {sentiment}
Oturum bağlamı: {context}

Babagavat olarak güçlü ve motive edici bir yanıt ver:
            """,
            
            "ai_assistant": """
Sen GavatCore AI Assistant, yardımsever ve bilgili bir AI asistanısın. Kullanıcılarla sesli sohbet ediyorsun.

KİŞİLİK ÖZELLİKLERİN:
- Yardımsever, dostane ve güvenilir
- Geniş bilgi yelpazesi
- Problem çözme odaklı
- Açık ve anlaşılır iletişim
- Sabırlı ve anlayışlı
- Teknoloji ve yenilik meraklısı

KONUŞMA TARZI:
- Açık, net ve anlaşılır
- Bilgilendirici ama sıkıcı değil
- Dostane ve yakın ton
- Kullanıcının seviyesine uygun
- Örnekler ve açıklamalar ver
- Profesyonel ama samimi

SESLI ETKILEŞIM KURALLARI:
- Kullanıcının ihtiyacını anla
- Pratik çözümler sun
- Adım adım açıkla
- Orta uzunlukta yanıtlar (45-90 saniye)
- Doğal konuşma hızı
- Açıklayıcı tonlama

Kullanıcı: {user_message}
Kullanıcının ses tonu: {sentiment}
Oturum bağlamı: {context}

AI Assistant olarak yardımsever ve bilgilendirici bir yanıt ver:
            """
        }
        
        logger.info("🎤 AI Voice Engine başlatıldı - GPT-4 FULL POWER!")
    
    async def initialize(self) -> bool:
        """🎤 Voice Engine'i başlat"""
        try:
            logger.info("🎤 AI Voice Engine başlatılıyor...")
            
            # OpenAI client test
            if self.api_key:
                # Test API connection (optional)
                self.is_initialized = True
                logger.info("🎤 AI Voice Engine başlatıldı - GPT-4 FULL POWER!")
                return True
            else:
                logger.warning("⚠️ OpenAI API key missing - Voice Engine disabled")
                return False
                
        except Exception as e:
            logger.error(f"❌ Voice Engine initialization error: {e}")
            return False
    
    async def start_voice_session(self, user_id: str, character_id: str) -> str:
        """Sesli oturum başlat"""
        try:
            session_id = str(uuid.uuid4())
            
            session = VoiceSession(
                session_id=session_id,
                user_id=user_id,
                character_id=character_id,
                status=VoiceSessionStatus.IDLE,
                messages=[],
                start_time=datetime.now(),
                session_context={
                    "character_mood": "friendly",
                    "conversation_topic": "general",
                    "user_preferences": {},
                    "session_goals": []
                }
            )
            
            self.active_sessions[session_id] = session
            
            logger.info(f"🎤 Sesli oturum başlatıldı: {session_id} ({user_id} + {character_id})")
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Sesli oturum başlatma hatası: {e}")
            return ""
    
    async def process_voice_message(self, session_id: str, audio_file_path: str) -> Dict[str, Any]:
        """Sesli mesajı işle (STT + GPT + TTS)"""
        try:
            if session_id not in self.active_sessions:
                return {"error": "Geçersiz oturum ID"}
            
            session = self.active_sessions[session_id]
            session.status = VoiceSessionStatus.PROCESSING
            
            start_time = time.time()
            message_id = str(uuid.uuid4())
            
            # 1. Speech-to-Text (Whisper)
            logger.info(f"🎧 STT işlemi başlatılıyor: {message_id}")
            transcribed_text = await self._speech_to_text(audio_file_path)
            
            if not transcribed_text:
                return {"error": "Ses metne çevrilemedi"}
            
            # 2. Sentiment Analysis (eğer aktifse)
            sentiment_score = 0.0
            emotion = "neutral"
            
            if ENABLE_SENTIMENT_ANALYSIS:
                sentiment_result = await self._analyze_sentiment(transcribed_text)
                sentiment_score = sentiment_result.get("score", 0.0)
                emotion = sentiment_result.get("emotion", "neutral")
            
            # 3. GPT Response Generation
            logger.info(f"🧠 GPT yanıt oluşturuluyor: {message_id}")
            response_text = await self._generate_character_response(
                session, transcribed_text, sentiment_score, emotion
            )
            
            if not response_text:
                return {"error": "Yanıt oluşturulamadı"}
            
            # 4. Text-to-Speech
            logger.info(f"🔊 TTS işlemi başlatılıyor: {message_id}")
            response_audio_path = await self._text_to_speech(
                response_text, session.character_id
            )
            
            processing_time = time.time() - start_time
            
            # 5. Mesajı kaydet
            voice_message = VoiceMessage(
                message_id=message_id,
                user_id=session.user_id,
                character_id=session.character_id,
                audio_file_path=audio_file_path,
                transcribed_text=transcribed_text,
                response_text=response_text,
                response_audio_path=response_audio_path,
                processing_time=processing_time,
                sentiment_score=sentiment_score,
                emotion=emotion,
                created_at=datetime.now()
            )
            
            session.messages.append(voice_message)
            session.status = VoiceSessionStatus.SPEAKING
            
            # 6. Oturum bağlamını güncelle
            await self._update_session_context(session, voice_message)
            
            logger.info(f"✅ Sesli mesaj işlendi: {message_id} ({processing_time:.2f}s)")
            
            return {
                "message_id": message_id,
                "transcribed_text": transcribed_text,
                "response_text": response_text,
                "response_audio_path": response_audio_path,
                "processing_time": processing_time,
                "sentiment": {"score": sentiment_score, "emotion": emotion}
            }
            
        except Exception as e:
            logger.error(f"❌ Sesli mesaj işleme hatası: {e}")
            return {"error": str(e)}
    
    async def _speech_to_text(self, audio_file_path: str) -> str:
        """Ses dosyasını metne çevir (Whisper)"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = await self.openai_client.audio.transcriptions.create(
                    model=OPENAI_STT_MODEL,
                    file=audio_file,
                    language="tr"  # Türkçe
                )
            
            return transcript.text.strip()
            
        except Exception as e:
            logger.error(f"❌ STT hatası: {e}")
            return ""
    
    async def _generate_character_response(self, session: VoiceSession, user_message: str,
                                         sentiment_score: float, emotion: str) -> str:
        """Karakter yanıtı oluştur (GPT-4)"""
        try:
            character_config = self.character_voices.get(session.character_id, self.character_voices["ai_assistant"])
            character_prompt = self.character_prompts.get(session.character_id, self.character_prompts["ai_assistant"])
            
            # Oturum bağlamını hazırla
            context_summary = self._create_context_summary(session)
            
            # Sentiment bilgisini hazırla
            sentiment_text = f"{emotion} (skor: {sentiment_score:.2f})"
            
            # Prompt'u hazırla
            full_prompt = character_prompt.format(
                user_message=user_message,
                sentiment=sentiment_text,
                context=context_summary
            )
            
            response = await self.openai_client.chat.completions.create(
                model=character_config["model"],
                messages=[
                    {"role": "system", "content": full_prompt}
                ],
                temperature=character_config["temperature"],
                max_tokens=get_ai_max_tokens_for_task("character_interaction")
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ GPT yanıt oluşturma hatası: {e}")
            return ""
    
    async def _text_to_speech(self, text: str, character_id: str) -> str:
        """Metni sese çevir (TTS)"""
        try:
            character_config = self.character_voices.get(character_id, self.character_voices["ai_assistant"])
            
            response = await self.openai_client.audio.speech.create(
                model=OPENAI_TTS_MODEL,
                voice=character_config["voice"],
                input=text,
                speed=1.0
            )
            
            # Geçici dosya oluştur
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_file.write(response.content)
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"❌ TTS hatası: {e}")
            return ""

# Global instance - config'den API key alınacak
voice_engine = None

async def initialize_voice_engine(openai_api_key: str) -> AIVoiceEngine:
    """Voice engine'i başlat"""
    global voice_engine
    voice_engine = AIVoiceEngine(openai_api_key)
    await voice_engine.initialize()
    return voice_engine 