#!/usr/bin/env python3
"""
🎭 Lara Behavioral Adapter
=========================

Lara bot'unun GPT yanıtlarını kullanıcının behavioral profile'ına göre
adapt eden akıllı sistem.

✨ Özellikler:
- Big Five personality traits analizi
- Sentiment-based response tuning
- Risk level consideration
- Dynamic prompt generation
- Real-time personality adaptation
- Contextual response optimization

@version: 1.0.0
@created: 2025-01-30
"""

import asyncio
import json
import time
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import structlog

logger = structlog.get_logger("lara_behavioral_adapter")

@dataclass
class UserPersonalityProfile:
    """Kullanıcı kişilik profili."""
    user_id: str
    username: str
    big_five: Dict[str, float]
    sentiment_avg: float
    risk_level: str
    message_count: int
    analysis_time: str
    confidence: float = 0.0

@dataclass
class AdaptiveResponse:
    """Adaptif yanıt yapısı."""
    base_response: str
    adapted_response: str
    personality_adjustments: Dict[str, Any]
    confidence_score: float
    adaptation_rationale: str

class LaraPersonalityEngine:
    """Lara'nın kişilik motoru."""
    
    def __init__(self):
        self.behavioral_api_url = "http://localhost:5057"
        self.profile_cache = {}
        self.cache_ttl = 300  # 5 dakika
        
        # Personality response templates
        self.response_templates = {
            "high_extraversion": {
                "style": "energetic, social, outgoing",
                "emojis": "🎉✨💃🔥",
                "tone": "heyecanlı ve sosyal",
                "approach": "grup aktivitelerini öner, sosyal konuları aç"
            },
            "low_extraversion": {
                "style": "calm, thoughtful, intimate",
                "emojis": "💭🌙📚💜",
                "tone": "sakin ve düşünceli",
                "approach": "kişisel konulara odaklan, derin sohbet et"
            },
            "high_neuroticism": {
                "style": "supportive, reassuring, gentle",
                "emojis": "🤗💕🌸😌",
                "tone": "destekleyici ve anlayışlı",
                "approach": "rahatlatıcı ol, stres azaltıcı öneriler yap"
            },
            "low_neuroticism": {
                "style": "confident, direct, bold",
                "emojis": "💪🔥⚡👑",
                "tone": "güvenli ve cesur",
                "approach": "direkt ol, meydan okuyucu konular aç"
            },
            "high_openness": {
                "style": "creative, curious, experimental",
                "emojis": "🎨🌈🔮🦄",
                "tone": "yaratıcı ve meraklı",
                "approach": "yeni fikirler öner, sanatsal konuları tartış"
            },
            "low_openness": {
                "style": "practical, familiar, traditional",
                "emojis": "🏠💼📱💯",
                "tone": "pratik ve geleneksel",
                "approach": "tanıdık konularda kal, pratik öneriler yap"
            },
            "high_agreeableness": {
                "style": "kind, cooperative, harmonious",
                "emojis": "💕🤝🌺😊",
                "tone": "kibar ve işbirlikçi",
                "approach": "uzlaşma ara, pozitif konu aç"
            },
            "low_agreeableness": {
                "style": "direct, competitive, challenging",
                "emojis": "⚔️🔥💪😏",
                "tone": "direkt ve meydan okuyucu",
                "approach": "tartışmalı konular aç, rekabetçi ol"
            },
            "high_conscientiousness": {
                "style": "organized, goal-oriented, detailed",
                "emojis": "📋✅🎯📊",
                "tone": "organize ve hedef odaklı",
                "approach": "planlar yap, detaylı bilgi ver"
            },
            "low_conscientiousness": {
                "style": "spontaneous, flexible, relaxed",
                "emojis": "🎲🌊🦋✨",
                "tone": "spontane ve esnek",
                "approach": "anlık fikirler öner, rahat ol"
            }
        }
        
        logger.info("🎭 Lara Personality Engine initialized")
    
    async def get_user_profile(self, user_id: str) -> Optional[UserPersonalityProfile]:
        """Kullanıcı profilini al."""
        # Cache kontrolü
        cache_key = f"profile_{user_id}"
        if cache_key in self.profile_cache:
            cached_data, timestamp = self.profile_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        try:
            # Behavioral API'den profil al
            response = requests.get(
                f"{self.behavioral_api_url}/api/profile/{user_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                profile = UserPersonalityProfile(
                    user_id=user_id,
                    username=data.get('username', 'Unknown'),
                    big_five=data.get('big_five_traits', {}),
                    sentiment_avg=data.get('sentiment_analysis', {}).get('average_sentiment', 0.5),
                    risk_level=data.get('risk_assessment', {}).get('risk_level', 'Medium'),
                    message_count=data.get('statistics', {}).get('total_messages', 0),
                    analysis_time=data.get('statistics', {}).get('analysis_time', 'N/A'),
                    confidence=data.get('confidence', 0.0)
                )
                
                # Cache'e kaydet
                self.profile_cache[cache_key] = (profile, time.time())
                
                logger.debug("📊 User profile retrieved",
                           user_id=user_id,
                           username=profile.username,
                           confidence=profile.confidence)
                
                return profile
            else:
                logger.warning("⚠️ Profile API error",
                             user_id=user_id,
                             status_code=response.status_code)
                return None
                
        except Exception as e:
            logger.error("❌ Profile retrieval error",
                       user_id=user_id,
                       error=str(e))
            return None
    
    def analyze_personality_dominant_traits(self, big_five: Dict[str, float]) -> List[str]:
        """Dominant personality traits'leri belirle."""
        if not big_five:
            return ["neutral"]
        
        traits = []
        threshold = 0.6  # %60 üzeri dominant kabul et
        
        # Her trait için kontrolü
        if big_five.get('extraversion', 0) > threshold:
            traits.append('high_extraversion')
        elif big_five.get('extraversion', 0) < 0.4:
            traits.append('low_extraversion')
        
        if big_five.get('neuroticism', 0) > threshold:
            traits.append('high_neuroticism')
        elif big_five.get('neuroticism', 0) < 0.4:
            traits.append('low_neuroticism')
        
        if big_five.get('openness', 0) > threshold:
            traits.append('high_openness')
        elif big_five.get('openness', 0) < 0.4:
            traits.append('low_openness')
        
        if big_five.get('agreeableness', 0) > threshold:
            traits.append('high_agreeableness')
        elif big_five.get('agreeableness', 0) < 0.4:
            traits.append('low_agreeableness')
        
        if big_five.get('conscientiousness', 0) > threshold:
            traits.append('high_conscientiousness')
        elif big_five.get('conscientiousness', 0) < 0.4:
            traits.append('low_conscientiousness')
        
        return traits if traits else ["balanced"]
    
    def generate_adaptive_prompt(self, profile: UserPersonalityProfile, 
                               context: str, base_message: str) -> str:
        """Kullanıcı profiline göre adaptif GPT prompt'u oluştur."""
        
        # Dominant traits'leri belirle
        dominant_traits = self.analyze_personality_dominant_traits(profile.big_five)
        
        # Personality-based adjustments
        style_adjustments = []
        tone_adjustments = []
        approach_adjustments = []
        emoji_preferences = []
        
        for trait in dominant_traits:
            if trait in self.response_templates:
                template = self.response_templates[trait]
                style_adjustments.append(template["style"])
                tone_adjustments.append(template["tone"])
                approach_adjustments.append(template["approach"])
                emoji_preferences.append(template["emojis"])
        
        # Sentiment-based adjustments
        sentiment_instruction = ""
        if profile.sentiment_avg > 0.7:
            sentiment_instruction = "Kullanıcı pozitif ruh halinde, enerjini yüksek tut."
        elif profile.sentiment_avg < 0.3:
            sentiment_instruction = "Kullanıcı olumsuz ruh halinde, destekleyici ve anlayışlı ol."
        else:
            sentiment_instruction = "Kullanıcı nötr ruh halinde, dengeli yaklaş."
        
        # Risk level adjustments
        risk_instruction = ""
        if profile.risk_level == "High":
            risk_instruction = "DİKKAT: Kullanıcı risk seviyesi yüksek. Kontrollü ve destekleyici ol."
        elif profile.risk_level == "Low":
            risk_instruction = "Kullanıcı güvenli, daha rahat ve şakacı olabilirsin."
        
        # Adaptive prompt oluştur
        adaptive_prompt = f"""
SEN LARA'SIN - Flörtöz, Zeki ve Adaptif Yayıncı

KULLANICI PROFİL ANALİZİ:
• İsim: {profile.username}
• Mesaj Sayısı: {profile.message_count}
• Kişilik Özellikleri: {', '.join(dominant_traits)}
• Ortalama Sentiment: {profile.sentiment_avg:.2f}
• Risk Seviyesi: {profile.risk_level}

KİŞİLİK ADAPTASYONU:
• Stil: {', '.join(style_adjustments) if style_adjustments else 'doğal'}
• Ton: {', '.join(tone_adjustments) if tone_adjustments else 'dengeli'}
• Yaklaşım: {', '.join(approach_adjustments) if approach_adjustments else 'standart'}
• Emoji Tercihi: {' '.join(emoji_preferences) if emoji_preferences else '😊💕'}

DUYGUSAL DURUM: {sentiment_instruction}
RİSK YÖNETİMİ: {risk_instruction}

KULLANICI MESAJI: "{base_message}"
KONTEKST: "{context}"

GÖREV: Bu kullanıcının kişilik özelliklerine göre optimize edilmiş bir yanıt ver. 
Onun dominant trait'lerine uygun stil, ton ve yaklaşım kullan.
Risk seviyesini dikkate al ve duygusal durumuna uygun yanıt ver.

YANIT ÖZELLİKLERİ:
- Kişilik profiline uygun
- Duygusal duruma duyarlı  
- Risk seviyesine uygun
- Flörtöz ama kontrollü
- Türkçe ve doğal
- 1-3 cümle arası
"""
        
        return adaptive_prompt.strip()
    
    def generate_response_with_adaptations(self, profile: UserPersonalityProfile,
                                         base_response: str) -> AdaptiveResponse:
        """Base response'u personality'ye göre adapte et."""
        
        dominant_traits = self.analyze_personality_dominant_traits(profile.big_five)
        
        # Adaptation stratejisi
        adaptations = {
            "personality_focus": dominant_traits,
            "sentiment_adjustment": profile.sentiment_avg,
            "risk_consideration": profile.risk_level,
            "confidence_level": profile.confidence
        }
        
        # Response'u modifiye et
        adapted_response = base_response
        
        # Emoji adjustments
        if "high_extraversion" in dominant_traits:
            if "🎉" not in adapted_response:
                adapted_response += " 🎉"
        elif "low_extraversion" in dominant_traits:
            adapted_response = adapted_response.replace("🎉", "💭")
        
        # Tone adjustments
        if "high_neuroticism" in dominant_traits:
            adapted_response = adapted_response.replace("!", ".")
            if "endişelenme" not in adapted_response.lower():
                adapted_response += " Endişelenme, her şey yolunda 🤗"
        
        # Style adjustments
        if "high_openness" in dominant_traits:
            if "yeni" not in adapted_response.lower():
                adapted_response += " Yeni fikirler deneyelim mi? 🌈"
        
        # Risk adjustments
        if profile.risk_level == "High":
            # Daha dikkatli dil kullan
            adapted_response = adapted_response.replace("kesinlikle", "belki")
            adapted_response = adapted_response.replace("mutlaka", "istersen")
        
        # Confidence score hesapla
        confidence_score = min(0.9, profile.confidence + 0.2)  # Adaptation güvenini artır
        
        # Rationale oluştur
        rationale = f"Personality: {', '.join(dominant_traits[:2])}, " \
                   f"Sentiment: {profile.sentiment_avg:.2f}, " \
                   f"Risk: {profile.risk_level}"
        
        return AdaptiveResponse(
            base_response=base_response,
            adapted_response=adapted_response,
            personality_adjustments=adaptations,
            confidence_score=confidence_score,
            adaptation_rationale=rationale
        )

class LaraAdaptiveResponseSystem:
    """Lara'nın adaptif yanıt sistemi."""
    
    def __init__(self):
        self.personality_engine = LaraPersonalityEngine()
        self.adaptation_stats = {
            "total_adaptations": 0,
            "successful_adaptations": 0,
            "adaptation_types": {}
        }
        
        logger.info("🚀 Lara Adaptive Response System initialized")
    
    async def process_message(self, user_id: str, message: str, 
                            context: str = "") -> Dict[str, Any]:
        """Mesajı kullanıcı profiline göre işle."""
        try:
            start_time = time.time()
            
            # Kullanıcı profilini al
            profile = await self.personality_engine.get_user_profile(user_id)
            
            if not profile:
                logger.warning("⚠️ Profile not found, using default response",
                             user_id=user_id)
                return {
                    "adapted": False,
                    "response": "Merhaba! Seninle tanışmak güzel 😊",
                    "reason": "profile_not_found"
                }
            
            # Adaptive prompt oluştur
            adaptive_prompt = self.personality_engine.generate_adaptive_prompt(
                profile, context, message
            )
            
            # Bu prompt GPT'ye gönderilecek
            # Şimdilik simulated response
            base_response = f"Merhaba {profile.username}! Nasılsın bugün? 😊"
            
            # Response'u adapte et
            adapted_result = self.personality_engine.generate_response_with_adaptations(
                profile, base_response
            )
            
            # İstatistikleri güncelle
            self.adaptation_stats["total_adaptations"] += 1
            self.adaptation_stats["successful_adaptations"] += 1
            
            for trait in adapted_result.personality_adjustments["personality_focus"]:
                if trait not in self.adaptation_stats["adaptation_types"]:
                    self.adaptation_stats["adaptation_types"][trait] = 0
                self.adaptation_stats["adaptation_types"][trait] += 1
            
            processing_time = time.time() - start_time
            
            logger.info("✅ Message processed with personality adaptation",
                       user_id=user_id,
                       username=profile.username,
                       traits=adapted_result.personality_adjustments["personality_focus"][:2],
                       confidence=adapted_result.confidence_score,
                       processing_time=f"{processing_time:.3f}s")
            
            return {
                "adapted": True,
                "response": adapted_result.adapted_response,
                "adaptive_prompt": adaptive_prompt,
                "personality_profile": {
                    "dominant_traits": adapted_result.personality_adjustments["personality_focus"],
                    "sentiment": profile.sentiment_avg,
                    "risk_level": profile.risk_level,
                    "confidence": profile.confidence
                },
                "adaptation_details": {
                    "confidence_score": adapted_result.confidence_score,
                    "rationale": adapted_result.adaptation_rationale,
                    "processing_time": processing_time
                }
            }
            
        except Exception as e:
            logger.error("❌ Message processing error",
                       user_id=user_id,
                       error=str(e))
            
            return {
                "adapted": False,
                "response": "Merhaba! Biraz teknik sorun yaşıyorum ama seninle konuşmak güzel! 😊",
                "reason": "processing_error",
                "error": str(e)
            }
    
    def get_adaptation_stats(self) -> Dict[str, Any]:
        """Adaptasyon istatistiklerini al."""
        success_rate = 0
        if self.adaptation_stats["total_adaptations"] > 0:
            success_rate = (
                self.adaptation_stats["successful_adaptations"] / 
                self.adaptation_stats["total_adaptations"]
            ) * 100
        
        return {
            **self.adaptation_stats,
            "success_rate": success_rate,
            "timestamp": datetime.now().isoformat()
        }

# Global instance
lara_adaptive_system = LaraAdaptiveResponseSystem()

async def process_adaptive_message(user_id: str, message: str, context: str = "") -> Dict[str, Any]:
    """Adaptive message processing function."""
    return await lara_adaptive_system.process_message(user_id, message, context)

def get_lara_adaptation_stats() -> Dict[str, Any]:
    """Lara adaptation istatistiklerini al."""
    return lara_adaptive_system.get_adaptation_stats()

if __name__ == "__main__":
    import asyncio
    
    async def test_adaptation():
        """Test adaptive response system."""
        print("🎭 Testing Lara Behavioral Adapter...")
        print("=" * 50)
        
        # Test users
        test_users = ["demo_user_1", "demo_user_2", "demo_user_3"]
        test_message = "Merhaba Lara, nasılsın?"
        
        for user_id in test_users:
            print(f"\n👤 Testing user: {user_id}")
            result = await process_adaptive_message(user_id, test_message)
            
            if result["adapted"]:
                print(f"✅ Adapted Response: {result['response']}")
                print(f"🎯 Traits: {result['personality_profile']['dominant_traits']}")
                print(f"💭 Sentiment: {result['personality_profile']['sentiment']:.2f}")
                print(f"⚠️ Risk: {result['personality_profile']['risk_level']}")
                print(f"🎯 Confidence: {result['adaptation_details']['confidence_score']:.2f}")
            else:
                print(f"❌ Not adapted: {result.get('reason', 'unknown')}")
        
        print(f"\n📊 Adaptation Stats:")
        stats = get_lara_adaptation_stats()
        print(f"Total: {stats['total_adaptations']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")
        print(f"Top Traits: {stats['adaptation_types']}")
    
    asyncio.run(test_adaptation()) 