from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
GavatCore V2 - Advanced AI Manager
Tüm AI sistemlerini koordine eden merkezi yönetim sistemi
FULL GPT-4 POWER! 🚀
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import structlog
import openai
from dataclasses import dataclass, asdict
from enum import Enum

# Config import
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TURBO_MODEL, OPENAI_VISION_MODEL,
    CRM_AI_MODEL, CHARACTER_AI_MODEL, SOCIAL_AI_MODEL,
    ENABLE_VOICE_AI, ENABLE_CRM_AI, ENABLE_SOCIAL_AI, ENABLE_ADVANCED_ANALYTICS,
    ENABLE_REAL_TIME_ANALYSIS, ENABLE_PREDICTIVE_ANALYTICS, ENABLE_SENTIMENT_ANALYSIS,
    ENABLE_PERSONALITY_ANALYSIS, AI_CONCURRENT_REQUESTS, AI_RATE_LIMIT_PER_MINUTE,
    get_ai_model_for_task, get_ai_temperature_for_task, get_ai_max_tokens_for_task
)

logger = structlog.get_logger("gavatcore.advanced_ai")

class AITaskType(Enum):
    """AI görev tipleri"""
    CHARACTER_INTERACTION = "character_interaction"
    CRM_ANALYSIS = "crm_analysis"
    SOCIAL_GAMING = "social_gaming"
    VOICE_PROCESSING = "voice_processing"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    PERSONALITY_ANALYSIS = "personality_analysis"
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    REAL_TIME_ANALYSIS = "real_time_analysis"
    CONTENT_GENERATION = "content_generation"
    VISION_ANALYSIS = "vision_analysis"
    HEAVY_ANALYSIS = "heavy_analysis"

class AIPriority(Enum):
    """AI görev öncelikleri"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    REAL_TIME = 5

@dataclass
class AITask:
    """AI görevi"""
    task_id: str
    task_type: AITaskType
    priority: AIPriority
    user_id: str
    character_id: Optional[str]
    prompt: str
    context: Dict[str, Any]
    model_override: Optional[str] = None
    temperature_override: Optional[float] = None
    max_tokens_override: Optional[int] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@dataclass
class AIAnalyticsResult:
    """AI analiz sonucu"""
    analysis_id: str
    analysis_type: str
    target_id: str
    confidence_score: float
    insights: Dict[str, Any]
    recommendations: List[str]
    metadata: Dict[str, Any]
    created_at: datetime

class AdvancedAIManager:
    """Gelişmiş AI Yönetim Sistemi - FULL GPT-4 POWER! 🚀"""
    
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY gerekli!")
        
        self.openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        # Görev kuyruğu ve işleme
        self.task_queue: List[AITask] = []
        self.active_tasks: Dict[str, AITask] = {}
        self.completed_tasks: Dict[str, AITask] = {}
        
        # Rate limiting
        self.request_count = 0
        self.last_minute_reset = time.time()
        
        # Analytics cache
        self.analytics_cache: Dict[str, AIAnalyticsResult] = {}
        
        # Specialized AI prompts
        self.specialized_prompts = {
            "personality_analysis": """
Sen bir uzman psikolog ve kişilik analistisin. Aşağıdaki kullanıcı etkileşim verilerini analiz ederek detaylı kişilik profili çıkar:

Kullanıcı Verileri:
{user_data}

ADVANCED PERSONALITY ANALYSIS:
1. Big Five Personality Traits (OCEAN Model)
2. Communication Style Analysis
3. Emotional Intelligence Indicators
4. Social Behavior Patterns
5. Decision Making Style
6. Stress Response Patterns
7. Motivation Drivers
8. Learning Preferences
9. Relationship Dynamics
10. Growth Potential Areas

JSON formatında detaylı analiz ver:
{{
    "personality_profile": {{
        "openness": 0-100,
        "conscientiousness": 0-100,
        "extraversion": 0-100,
        "agreeableness": 0-100,
        "neuroticism": 0-100
    }},
    "communication_style": "analytical/expressive/driver/amiable",
    "emotional_intelligence": 0-100,
    "social_behavior": "introvert/ambivert/extrovert",
    "decision_making": "analytical/intuitive/directive/conceptual",
    "stress_response": "fight/flight/freeze/flow",
    "primary_motivators": ["achievement", "affiliation", "power"],
    "learning_style": "visual/auditory/kinesthetic/reading",
    "relationship_approach": "secure/anxious/avoidant/disorganized",
    "growth_areas": ["area1", "area2"],
    "strengths": ["strength1", "strength2"],
    "optimal_interaction_style": "detailed_recommendations",
    "personalization_tips": ["tip1", "tip2"],
    "insights": "comprehensive_psychological_analysis"
}}
            """,
            
            "real_time_sentiment": """
Sen bir duygu analizi uzmanısın. Aşağıdaki metni gerçek zamanlı olarak analiz et:

Metin: {text}
Bağlam: {context}

REAL-TIME SENTIMENT ANALYSIS:
1. Emotional Valence (Pozitif/Negatif)
2. Emotional Intensity (Düşük/Orta/Yüksek)
3. Specific Emotions (Mutluluk, Üzüntü, Öfke, Korku, Şaşkınlık, İğrenme)
4. Emotional Stability
5. Mood Indicators
6. Stress Levels
7. Engagement Quality
8. Response Recommendations

JSON formatında hızlı analiz ver:
{{
    "sentiment_score": -1.0 to 1.0,
    "emotional_intensity": 0-100,
    "primary_emotion": "emotion_name",
    "secondary_emotions": ["emotion1", "emotion2"],
    "mood_state": "positive/neutral/negative",
    "stress_level": 0-100,
    "engagement_quality": 0-100,
    "emotional_stability": 0-100,
    "response_tone": "empathetic/supportive/energetic/calming",
    "recommended_approach": "specific_interaction_strategy",
    "insights": "quick_emotional_analysis"
}}
            """,
            
            "predictive_behavior": """
Sen bir davranış analisti ve tahmin uzmanısın. Kullanıcı verilerini analiz ederek gelecek davranışları tahmin et:

Kullanıcı Geçmişi:
{user_history}

PREDICTIVE BEHAVIOR ANALYSIS:
1. Activity Pattern Prediction
2. Engagement Trend Forecasting
3. Churn Risk Timeline
4. Feature Usage Prediction
5. Social Interaction Forecast
6. Content Preference Evolution
7. Optimal Intervention Timing
8. Success Probability Modeling

JSON formatında tahmin analizi ver:
{{
    "activity_prediction": {{
        "next_7_days": "high/medium/low",
        "next_30_days": "trend_description",
        "peak_activity_times": ["time1", "time2"]
    }},
    "engagement_forecast": {{
        "trend": "increasing/stable/decreasing",
        "confidence": 0-100,
        "expected_change": "percentage"
    }},
    "churn_prediction": {{
        "risk_level": "low/medium/high/critical",
        "timeline": "days_until_risk",
        "probability": 0-100
    }},
    "feature_usage": {{
        "voice_adoption": 0-100,
        "social_participation": 0-100,
        "quest_completion": 0-100
    }},
    "optimal_interventions": [
        {{"action": "intervention_type", "timing": "when", "success_rate": 0-100}}
    ],
    "behavioral_insights": "detailed_predictions_and_recommendations"
}}
            """,
            
            "content_optimization": """
Sen bir içerik stratejisti ve engagement uzmanısın. Kullanıcı verilerine göre optimal içerik stratejisi geliştir:

Kullanıcı Profili:
{user_profile}

İçerik Geçmişi:
{content_history}

CONTENT OPTIMIZATION STRATEGY:
1. Content Type Preferences
2. Optimal Content Length
3. Best Posting Times
4. Engagement Triggers
5. Personalization Level
6. Visual vs Text Preference
7. Interactive Elements
8. Emotional Tone Optimization

JSON formatında strateji ver:
{{
    "content_strategy": {{
        "preferred_types": ["type1", "type2"],
        "optimal_length": "short/medium/long",
        "best_times": ["time1", "time2"],
        "frequency": "daily/weekly/bi-weekly"
    }},
    "engagement_optimization": {{
        "primary_triggers": ["trigger1", "trigger2"],
        "emotional_tone": "motivational/educational/entertaining",
        "personalization_level": "high/medium/low",
        "interactive_elements": ["element1", "element2"]
    }},
    "content_recommendations": [
        {{"type": "content_type", "topic": "topic", "expected_engagement": 0-100}}
    ],
    "a_b_test_suggestions": ["test1", "test2"],
    "performance_predictions": {{
        "engagement_rate": 0-100,
        "completion_rate": 0-100,
        "sharing_probability": 0-100
    }},
    "insights": "comprehensive_content_strategy"
}}
            """
        }
        
        # Background task processor başlat
        asyncio.create_task(self._process_task_queue())
        
        logger.info("🚀 Advanced AI Manager başlatıldı - FULL GPT-4 POWER!")
    
    async def submit_ai_task(self, task_type: AITaskType, user_id: str, prompt: str,
                           context: Dict[str, Any] = None, character_id: str = None,
                           priority: AIPriority = AIPriority.NORMAL,
                           model_override: str = None) -> str:
        """AI görevi gönder"""
        try:
            task_id = f"{task_type.value}_{user_id}_{int(time.time())}"
            
            task = AITask(
                task_id=task_id,
                task_type=task_type,
                priority=priority,
                user_id=user_id,
                character_id=character_id,
                prompt=prompt,
                context=context or {},
                model_override=model_override,
                created_at=datetime.now()
            )
            
            # Priority'ye göre kuyruğa ekle
            if priority == AIPriority.REAL_TIME:
                self.task_queue.insert(0, task)
            elif priority == AIPriority.CRITICAL:
                # Critical task'ları en başa ekle (real-time'dan sonra)
                real_time_count = sum(1 for t in self.task_queue if t.priority == AIPriority.REAL_TIME)
                self.task_queue.insert(real_time_count, task)
            else:
                self.task_queue.append(task)
            
            logger.info(f"🎯 AI görevi eklendi: {task_id} ({task_type.value}, {priority.name})")
            return task_id
            
        except Exception as e:
            logger.error(f"❌ AI görev ekleme hatası: {e}")
            return ""
    
    async def get_task_result(self, task_id: str, wait_timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Görev sonucunu al"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < wait_timeout:
                # Tamamlanan görevlerde kontrol et
                if task_id in self.completed_tasks:
                    task = self.completed_tasks[task_id]
                    if task.error:
                        return {"error": task.error}
                    return task.result
                
                # Kısa bekleme
                await asyncio.sleep(0.1)
            
            return {"error": "Timeout - görev tamamlanamadı"}
            
        except Exception as e:
            logger.error(f"❌ Görev sonucu alma hatası: {e}")
            return {"error": str(e)}
    
    async def analyze_personality(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Kişilik analizi yap"""
        if not ENABLE_PERSONALITY_ANALYSIS:
            return {"error": "Personality analysis devre dışı"}
        
        task_id = await self.submit_ai_task(
            task_type=AITaskType.PERSONALITY_ANALYSIS,
            user_id=user_id,
            prompt=self.specialized_prompts["personality_analysis"].format(user_data=json.dumps(user_data, default=str)),
            priority=AIPriority.HIGH
        )
        
        return await self.get_task_result(task_id)
    
    async def analyze_real_time_sentiment(self, user_id: str, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Gerçek zamanlı duygu analizi"""
        if not ENABLE_SENTIMENT_ANALYSIS:
            return {"error": "Sentiment analysis devre dışı"}
        
        task_id = await self.submit_ai_task(
            task_type=AITaskType.SENTIMENT_ANALYSIS,
            user_id=user_id,
            prompt=self.specialized_prompts["real_time_sentiment"].format(text=text, context=json.dumps(context or {}, default=str)),
            priority=AIPriority.REAL_TIME
        )
        
        return await self.get_task_result(task_id, wait_timeout=5.0)  # Hızlı yanıt
    
    async def predict_user_behavior(self, user_id: str, user_history: Dict[str, Any]) -> Dict[str, Any]:
        """Kullanıcı davranışı tahmin et"""
        if not ENABLE_PREDICTIVE_ANALYTICS:
            return {"error": "Predictive analytics devre dışı"}
        
        task_id = await self.submit_ai_task(
            task_type=AITaskType.PREDICTIVE_ANALYTICS,
            user_id=user_id,
            prompt=self.specialized_prompts["predictive_behavior"].format(user_history=json.dumps(user_history, default=str)),
            priority=AIPriority.HIGH
        )
        
        return await self.get_task_result(task_id)
    
    async def optimize_content_strategy(self, user_id: str, user_profile: Dict[str, Any], content_history: Dict[str, Any]) -> Dict[str, Any]:
        """İçerik stratejisini optimize et"""
        task_id = await self.submit_ai_task(
            task_type=AITaskType.CONTENT_GENERATION,
            user_id=user_id,
            prompt=self.specialized_prompts["content_optimization"].format(
                user_profile=json.dumps(user_profile, default=str),
                content_history=json.dumps(content_history, default=str)
            ),
            priority=AIPriority.NORMAL
        )
        
        return await self.get_task_result(task_id)
    
    async def _process_task_queue(self) -> None:
        """Görev kuyruğunu işle"""
        while True:
            try:
                # Rate limiting kontrolü
                if not await self._check_rate_limit():
                    await asyncio.sleep(1)
                    continue
                
                # Kuyrukta görev var mı?
                if not self.task_queue:
                    await self._adaptive_delay()
                    continue
                
                # Çok fazla aktif görev varsa bekle
                if len(self.active_tasks) >= AI_CONCURRENT_REQUESTS:
                    await asyncio.sleep(0.5)
                    continue
                
                # En yüksek öncelikli görevi al
                task = self.task_queue.pop(0)
                
                # Görevi işle
                await self._process_single_task(task)
                
                # Adaptif gecikme
                await self._adaptive_delay()
                
            except Exception as e:
                logger.error(f"❌ Task queue processing hatası: {e}")
                await asyncio.sleep(1)
    
    def _clean_json_response(self, response_content: str) -> str:
        """OpenAI yanıtından markdown formatını temizle"""
        # Markdown code block'ları temizle
        content = response_content.strip()
        
        # ```json ile başlayıp ``` ile bitiyorsa temizle
        if content.startswith("```json"):
            content = content[7:]  # ```json kısmını çıkar
        elif content.startswith("```"):
            content = content[3:]   # ``` kısmını çıkar
        
        if content.endswith("```"):
            content = content[:-3]  # Son ``` kısmını çıkar
        
        return content.strip()
    
    async def _process_single_task(self, task: AITask) -> None:
        """Tek bir görevi işle"""
        try:
            task.started_at = datetime.now()
            self.active_tasks[task.task_id] = task
            
            # Model ve parametreleri belirle
            model = task.model_override or get_ai_model_for_task(task.task_type.value)
            temperature = task.temperature_override or get_ai_temperature_for_task(task.task_type.value)
            max_tokens = task.max_tokens_override or get_ai_max_tokens_for_task(task.task_type.value)
            
            # GPT-4 ile işle
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": f"Sen {task.task_type.value} konusunda uzman bir AI'sın. Yanıtını SADECE geçerli JSON formatında ver, markdown kullanma."},
                    {"role": "user", "content": task.prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Güvenli JSON parsing
            response_content = response.choices[0].message.content.strip()
            logger.info(f"🔍 AI Task yanıtı ({task.task_type.value}) - ilk 200 karakter: {response_content[:200]}...")
            
            # Markdown formatını temizle
            cleaned_content = self._clean_json_response(response_content)
            
            try:
                result = json.loads(cleaned_content)
            except json.JSONDecodeError as e:
                logger.error(f"❌ AI Task JSON parse hatası ({task.task_id}): {e}")
                logger.error(f"❌ Orijinal yanıt: {response_content}")
                logger.error(f"❌ Temizlenmiş yanıt: {cleaned_content}")
                # Fallback: Basit yanıt formatı
                result = {
                    "response": response_content,
                    "task_type": task.task_type.value,
                    "status": "processed_as_text",
                    "error": f"JSON parse hatası: {str(e)}"
                }
            
            task.result = result
            task.completed_at = datetime.now()
            
            # Tamamlanan görevlere taşı
            self.completed_tasks[task.task_id] = task
            del self.active_tasks[task.task_id]
            
            processing_time = (task.completed_at - task.started_at).total_seconds()
            logger.info(f"✅ AI görevi tamamlandı: {task.task_id} ({processing_time:.2f}s)")
            
        except Exception as e:
            task.error = str(e)
            task.completed_at = datetime.now()
            
            self.completed_tasks[task.task_id] = task
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            
            logger.error(f"❌ AI görev işleme hatası ({task.task_id}): {e}")
    
    async def _check_rate_limit(self) -> bool:
        """Rate limit kontrolü"""
        current_time = time.time()
        
        # Dakika sıfırlandı mı?
        if current_time - self.last_minute_reset >= 60:
            self.request_count = 0
            self.last_minute_reset = current_time
        
        # Limit aşıldı mı?
        if self.request_count >= AI_RATE_LIMIT_PER_MINUTE:
            logger.warning(f"⚠️ AI Rate limit aşıldı: {self.request_count}/{AI_RATE_LIMIT_PER_MINUTE}")
            return False
        
        self.request_count += 1
        return True
    
    async def _adaptive_delay(self) -> None:
        """Adaptif gecikme - sistem yoğunluğuna göre ayarla"""
        # Aktif görev sayısına göre gecikme
        active_count = len(self.active_tasks)
        queue_count = len(self.task_queue)
        
        if active_count > 5:
            await asyncio.sleep(2.0)  # Çok yoğun
        elif active_count > 3:
            await asyncio.sleep(1.0)  # Orta yoğun
        elif queue_count > 10:
            await asyncio.sleep(0.5)  # Kuyruk dolu
        else:
            await asyncio.sleep(0.1)  # Normal
    
    async def get_system_analytics(self) -> Dict[str, Any]:
        """Sistem analitiklerini al"""
        try:
            return {
                "queue_status": {
                    "pending_tasks": len(self.task_queue),
                    "active_tasks": len(self.active_tasks),
                    "completed_tasks": len(self.completed_tasks)
                },
                "task_breakdown": {
                    task_type.value: len([t for t in self.task_queue if t.task_type == task_type])
                    for task_type in AITaskType
                },
                "priority_breakdown": {
                    priority.name: len([t for t in self.task_queue if t.priority == priority])
                    for priority in AIPriority
                },
                "rate_limiting": {
                    "requests_this_minute": self.request_count,
                    "limit": AI_RATE_LIMIT_PER_MINUTE,
                    "utilization": f"{(self.request_count / AI_RATE_LIMIT_PER_MINUTE) * 100:.1f}%"
                },
                "ai_features": {
                    "voice_ai": ENABLE_VOICE_AI,
                    "crm_ai": ENABLE_CRM_AI,
                    "social_ai": ENABLE_SOCIAL_AI,
                    "advanced_analytics": ENABLE_ADVANCED_ANALYTICS,
                    "real_time_analysis": ENABLE_REAL_TIME_ANALYSIS,
                    "predictive_analytics": ENABLE_PREDICTIVE_ANALYTICS,
                    "sentiment_analysis": ENABLE_SENTIMENT_ANALYSIS,
                    "personality_analysis": ENABLE_PERSONALITY_ANALYSIS
                }
            }
            
        except Exception as e:
            logger.error(f"❌ System analytics hatası: {e}")
            return {"error": str(e)}

# Global instance
advanced_ai_manager = None

async def initialize_advanced_ai_manager() -> AdvancedAIManager:
    """Advanced AI Manager'ı başlat"""
    global advanced_ai_manager
    advanced_ai_manager = AdvancedAIManager()
    return advanced_ai_manager 