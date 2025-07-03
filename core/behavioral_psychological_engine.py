"""
🧠 Behavioral & Psychological Engine - Davranış ve psikoloji analizi
"""
from telethon import events
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from typing import Dict, List, Tuple, Optional
from .cache_strategy import CacheStrategy
import json
import re
import os
from enum import Enum

class BigFiveTraits(Enum):
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"

class PersonalityType(Enum):
    INTROVERT = "introvert"
    EXTROVERT = "extrovert"
    AMBIVERT = "ambivert"

class SocialRole(Enum):
    LEADER = "leader"
    FOLLOWER = "follower"
    MEDIATOR = "mediator"

class MotivationType(Enum):
    ACHIEVEMENT = "achievement"
    POWER = "power"
    AFFILIATION = "affiliation"
    SECURITY = "security"
    EXPLORATION = "exploration"

class BehavioralPsychologicalEngine:
    def __init__(self):
        # Temel veri yapıları
        self.user_data: Dict[int, Dict] = {}
        self.message_history: Dict[int, List[Tuple[datetime, str]]] = {}
        
        # Analiz sonuçları
        self.engagement_scores: Dict[int, float] = {}
        self.patterns: Dict[int, List[str]] = {}
        self.recommendations: Dict[int, List[str]] = {}
        self.risk_factors: Dict[int, List[str]] = {}
        self.prediction_confidence: Dict[int, float] = {}
        
        # ML modelleri
        self.vectorizer = TfidfVectorizer()
        self.cluster_model = KMeans(n_clusters=5)
        self.classifier = LogisticRegression()
        
        # Cache stratejisi
        self.cache_strategy = CacheStrategy.LRU
        
        # Veri yükleme
        self.load_data()
        
    def load_data(self):
        """Verileri yükle"""
        try:
            # Varsayılan değerler
            self.engagement_scores = {}
            self.patterns = {}
            self.recommendations = {}
            self.risk_factors = {}
            self.prediction_confidence = {}
            
        except Exception as e:
            print(f"Data Load Error: {e}")
            
    async def analyze_message(self, event: events.NewMessage.Event) -> dict:
        """Mesajı analiz et"""
        try:
            user_id = event.sender_id
            message = event.message.text
            timestamp = datetime.now()
            
            # Mesajı geçmişe ekle
            if user_id not in self.message_history:
                self.message_history[user_id] = []
            self.message_history[user_id].append((timestamp, message))
            
            # Analiz yap
            analysis = {
                "engagement_score": await self.calculate_engagement(user_id),
                "patterns": await self.detect_patterns(user_id),
                "recommendations": await self.generate_recommendations(user_id),
                "risk_factors": await self.assess_risks(user_id),
                "prediction_confidence": await self.calculate_confidence(user_id)
            }
            
            return analysis
            
        except Exception as e:
            print(f"Message Analysis Error: {e}")
            return {}
            
    async def calculate_engagement(self, user_id: int) -> float:
        """Etkileşim skorunu hesapla"""
        try:
            if user_id not in self.engagement_scores:
                self.engagement_scores[user_id] = 0.0
                
            # Son mesajları analiz et
            recent_messages = [
                msg for ts, msg in self.message_history.get(user_id, [])
                if datetime.now() - ts < timedelta(days=7)
            ]
            
            if not recent_messages:
                return 0.0
                
            # Basit etkileşim skoru
            score = min(len(recent_messages) / 100, 1.0)
            self.engagement_scores[user_id] = score
            
            return score
            
        except Exception as e:
            print(f"Engagement Calculation Error: {e}")
            return 0.0
            
    async def detect_patterns(self, user_id: int) -> List[str]:
        """Mesaj desenlerini tespit et"""
        try:
            if user_id not in self.patterns:
                self.patterns[user_id] = []
                
            # Son mesajları al
            messages = [msg for _, msg in self.message_history.get(user_id, [])]
            
            if not messages:
                return []
                
            # Basit desen analizi
            patterns = []
            
            # Emoji kullanımı
            emoji_count = sum(len(re.findall(r'[\U0001F300-\U0001F9FF]', msg)) for msg in messages)
            if emoji_count > 10:
                patterns.append("Emoji kullanımı yüksek")
                
            # Mesaj uzunluğu
            avg_length = sum(len(msg) for msg in messages) / len(messages)
            if avg_length > 100:
                patterns.append("Uzun mesajlar")
                
            self.patterns[user_id] = patterns
            return patterns
            
        except Exception as e:
            print(f"Pattern Detection Error: {e}")
            return []
            
    async def generate_recommendations(self, user_id: int) -> List[str]:
        """Öneriler oluştur"""
        try:
            if user_id not in self.recommendations:
                self.recommendations[user_id] = []
                
            # Basit öneriler
            recommendations = []
            
            # Etkileşim skoruna göre
            if self.engagement_scores.get(user_id, 0) < 0.3:
                recommendations.append("Daha sık mesaj göndermeyi deneyin")
                
            # Desenlere göre
            if "Emoji kullanımı yüksek" in self.patterns.get(user_id, []):
                recommendations.append("Daha az emoji kullanın")
                
            self.recommendations[user_id] = recommendations
            return recommendations
            
        except Exception as e:
            print(f"Recommendation Generation Error: {e}")
            return []
            
    async def assess_risks(self, user_id: int) -> List[str]:
        """Risk faktörlerini değerlendir"""
        try:
            if user_id not in self.risk_factors:
                self.risk_factors[user_id] = []
                
            # Basit risk değerlendirmesi
            risks = []
            
            # Spam riski
            if len(self.message_history.get(user_id, [])) > 100:
                risks.append("Spam riski")
                
            # Uygunsuz içerik riski
            messages = [msg.lower() for _, msg in self.message_history.get(user_id, [])]
            if any("küfür" in msg for msg in messages):
                risks.append("Uygunsuz içerik riski")
                
            self.risk_factors[user_id] = risks
            return risks
            
        except Exception as e:
            print(f"Risk Assessment Error: {e}")
            return []
            
    async def calculate_confidence(self, user_id: int) -> float:
        """Tahmin güvenini hesapla"""
        try:
            if user_id not in self.prediction_confidence:
                self.prediction_confidence[user_id] = 0.0
                
            # Basit güven hesaplaması
            confidence = 0.5  # Varsayılan
            
            # Veri miktarına göre
            if len(self.message_history.get(user_id, [])) > 50:
                confidence += 0.3
                
            # Etkileşim skoruna göre
            confidence += self.engagement_scores.get(user_id, 0) * 0.2
            
            self.prediction_confidence[user_id] = min(confidence, 1.0)
            return confidence
            
        except Exception as e:
            print(f"Confidence Calculation Error: {e}")
            return 0.0
            
    async def get_user_profile(self, user_id: int) -> dict:
        """Kullanıcı profilini getir"""
        try:
            return {
                "engagement_score": self.engagement_scores.get(user_id, 0.0),
                "patterns": self.patterns.get(user_id, []),
                "recommendations": self.recommendations.get(user_id, []),
                "risk_factors": self.risk_factors.get(user_id, []),
                "prediction_confidence": self.prediction_confidence.get(user_id, 0.0)
            }
            
        except Exception as e:
            print(f"Profile Get Error: {e}")
            return {}
            
    async def clear_user_data(self, user_id: int):
        """Kullanıcı verilerini temizle"""
        try:
            if user_id in self.user_data:
                del self.user_data[user_id]
            if user_id in self.message_history:
                del self.message_history[user_id]
            if user_id in self.engagement_scores:
                del self.engagement_scores[user_id]
            if user_id in self.patterns:
                del self.patterns[user_id]
            if user_id in self.recommendations:
                del self.recommendations[user_id]
            if user_id in self.risk_factors:
                del self.risk_factors[user_id]
            if user_id in self.prediction_confidence:
                del self.prediction_confidence[user_id]
                
            print(f"✅ {user_id} için veriler temizlendi!")
            
        except Exception as e:
            print(f"Data Clear Error: {e}")
            
    async def get_stats(self) -> dict:
        """İstatistikleri getir"""
        try:
            return {
                "total_users": len(self.user_data),
                "active_users": len(self.message_history),
                "cache_strategy": self.cache_strategy.value
            }
            
        except Exception as e:
            print(f"Stats Error: {e}")
            return {} 

class AdvancedBehavioralPsychologicalEngine(BehavioralPsychologicalEngine):
    """Gelişmiş davranış ve psikoloji analizi motoru"""
    
    def __init__(self):
        super().__init__()
        # Ek özellikler ve analizler
        self.advanced_patterns: Dict[int, List[str]] = {}
        self.advanced_recommendations: Dict[int, List[str]] = {}
        self.advanced_risk_factors: Dict[int, List[str]] = {}
        self.advanced_prediction_confidence: Dict[int, float] = {}
        
    def analyze_advanced_patterns(self, user_id: int) -> List[str]:
        """Gelişmiş davranış kalıplarını analiz et"""
        # Basit bir örnek
        return ["pattern1", "pattern2"]
        
    def generate_advanced_recommendations(self, user_id: int) -> List[str]:
        """Gelişmiş öneriler oluştur"""
        # Basit bir örnek
        return ["recommendation1", "recommendation2"]
        
    def assess_advanced_risk_factors(self, user_id: int) -> List[str]:
        """Gelişmiş risk faktörlerini değerlendir"""
        # Basit bir örnek
        return ["risk1", "risk2"]
        
    def calculate_advanced_prediction_confidence(self, user_id: int) -> float:
        """Gelişmiş tahmin güvenini hesapla"""
        # Basit bir örnek
        return 0.85 