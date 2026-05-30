from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🧠 Behavioral Insights Dashboard
===============================

Gelişmiş cache sistemi kullanan kullanıcı behavioral profil paneli.
Flask + Redis + Big Five + sentiment + time pattern analysis.

✨ Özellikler:
- Her kullanıcının Big Five profili
- Günlük mood eğrisi analizi  
- Son 100 mesajdan çıkarılan etkileşimsel öngörüler
- Redis cache analizi (cache hits, misses, TTL expiry)
- Real-time behavioral pattern tracking
- Psychological risk assessment
- Time-based behavior analysis

@version: 1.0.0
@created: 2025-01-30
"""

import asyncio
import time
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import structlog

# Import optimized functions
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from optimized_performance_functions import (
        OptimizedJSONHandler,
        OptimizedHasher,
        OptimizedBehavioralAnalyzer,
        json_handler,
        hasher,
        behavioral_analyzer
    )
    OPTIMIZATIONS_AVAILABLE = True
except ImportError:
    OPTIMIZATIONS_AVAILABLE = False
    print("⚠️ Optimizations not available, using fallback")

# Configure logging
logger = structlog.get_logger("behavioral_insights")

@dataclass
class UserBehavioralProfile:
    """Kullanıcı davranışsal profil verisi."""
    user_id: str
    username: str
    big_five_scores: Dict[str, float]
    sentiment_history: List[Tuple[datetime, float]]
    message_frequency: Dict[str, int]  # hour -> count
    interaction_patterns: Dict[str, Any]
    risk_assessment: Dict[str, float]
    last_updated: datetime
    cache_hit_count: int = 0
    total_analyses: int = 0
    
    @property
    def cache_hit_rate(self) -> float:
        """Cache hit oranını hesapla."""
        if self.total_analyses == 0:
            return 0.0
        return (self.cache_hit_count / self.total_analyses) * 100

@dataclass
class SystemCacheMetrics:
    """Sistem cache metrikleri."""
    total_profiles: int
    cache_hits_24h: int
    cache_misses_24h: int
    hit_rate_24h: float
    avg_response_time: float
    top_accessed_profiles: List[Dict[str, Any]]
    cache_size_mb: float
    invalidations_24h: int

class BehavioralInsightsManager:
    """
    🧠 Behavioral Insights yöneticisi.
    
    Cache sistemi üzerinden kullanıcı davranışsal analizleri yapar.
    """
    
    def __init__(self, db_path: str = "gavatcore_v2.db"):
        self.db_path = db_path
        self.profiles: Dict[str, UserBehavioralProfile] = {}
        self.cache_metrics = defaultdict(int)
        self.response_times = deque(maxlen=1000)
        
        # Initialize optimized components
        if OPTIMIZATIONS_AVAILABLE:
            self.json_handler = json_handler
            self.hasher = hasher
            self.behavioral_analyzer = behavioral_analyzer
            logger.info("✅ Optimized components initialized")
        else:
            logger.warning("⚠️ Using fallback components")
    
    def _get_db_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı al."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error("❌ Database connection error", error=str(e))
            raise
    
    async def analyze_user_behavioral_profile(self, user_id: str) -> Optional[UserBehavioralProfile]:
        """
        Kullanıcının detaylı behavioral profilini analiz et.
        
        Args:
            user_id: Kullanıcı ID
            
        Returns:
            UserBehavioralProfile veya None
        """
        start_time = time.time()
        
        try:
            # Cache'ten kontrol et
            cache_key = f"behavioral_profile_{user_id}"
            if OPTIMIZATIONS_AVAILABLE:
                # Use hasher's internal cache (or implement simple cache)
                cached_data = self.hasher.hash_cache.get(cache_key)
                if cached_data:
                    self.cache_metrics['hits'] += 1
                    profile = UserBehavioralProfile(**cached_data)
                    profile.cache_hit_count += 1
                    logger.debug("🎯 Cache hit for behavioral profile", user_id=user_id)
                    return profile
            
            self.cache_metrics['misses'] += 1
            
            # Veritabanından kullanıcı verilerini al
            conn = self._get_db_connection()
            
            # Kullanıcı bilgileri
            user_query = "SELECT user_id, username FROM users WHERE user_id = ?"
            user_data = conn.execute(user_query, (user_id,)).fetchone()
            
            if not user_data:
                logger.warning("⚠️ User not found", user_id=user_id)
                conn.close()
                return None
            
            # Son 100 mesajı al
            messages_query = """
                SELECT message_text, timestamp, sentiment_score 
                FROM messages 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 100
            """
            messages = conn.execute(messages_query, (user_id,)).fetchall()
            
            if not messages:
                logger.warning("⚠️ No messages found for user", user_id=user_id)
                conn.close()
                return None
            
            # Big Five analizi
            if OPTIMIZATIONS_AVAILABLE:
                combined_text = " ".join([msg['message_text'] for msg in messages if msg['message_text']])
                big_five_result = self.behavioral_analyzer.analyze_big_five(combined_text)
                big_five_scores = big_five_result.get('traits', {})
            else:
                # Fallback Big Five scores
                big_five_scores = {
                    'openness': 0.5,
                    'conscientiousness': 0.5,
                    'extraversion': 0.5,
                    'agreeableness': 0.5,
                    'neuroticism': 0.5
                }
            
            # Sentiment history
            sentiment_history = []
            for msg in messages:
                if msg['timestamp'] and msg['sentiment_score'] is not None:
                    try:
                        timestamp = datetime.fromisoformat(msg['timestamp'])
                        sentiment_history.append((timestamp, float(msg['sentiment_score'])))
                    except (ValueError, TypeError):
                        continue
            
            # Mesaj frequency analizi (saat bazında)
            message_frequency = defaultdict(int)
            for msg in messages:
                if msg['timestamp']:
                    try:
                        timestamp = datetime.fromisoformat(msg['timestamp'])
                        hour = timestamp.hour
                        message_frequency[str(hour)] += 1
                    except (ValueError, TypeError):
                        continue
            
            # Interaction patterns
            interaction_patterns = {
                'total_messages': len(messages),
                'avg_sentiment': statistics.mean([s[1] for s in sentiment_history]) if sentiment_history else 0.0,
                'most_active_hour': max(message_frequency.items(), key=lambda x: x[1])[0] if message_frequency else "0",
                'sentiment_variance': statistics.variance([s[1] for s in sentiment_history]) if len(sentiment_history) > 1 else 0.0,
                'message_length_avg': statistics.mean([len(msg['message_text'] or "") for msg in messages]),
                'activity_score': len(messages) / 100.0  # 0-1 scale
            }
            
            # Risk assessment
            risk_assessment = self._calculate_risk_assessment(
                big_five_scores, 
                sentiment_history, 
                interaction_patterns
            )
            
            # Profil oluştur
            profile = UserBehavioralProfile(
                user_id=user_id,
                username=user_data['username'] or f"User_{user_id}",
                big_five_scores=big_five_scores,
                sentiment_history=sentiment_history,
                message_frequency=dict(message_frequency),
                interaction_patterns=interaction_patterns,
                risk_assessment=risk_assessment,
                last_updated=datetime.now(),
                total_analyses=1
            )
            
            # Cache'e kaydet
            if OPTIMIZATIONS_AVAILABLE:
                # Profile'ı JSON serializable hale getir
                cache_data = asdict(profile)
                cache_data['sentiment_history'] = [
                    (ts.isoformat(), score) for ts, score in profile.sentiment_history
                ]
                cache_data['last_updated'] = profile.last_updated.isoformat()
                
                self.hasher.hash_cache[cache_key] = cache_data  # Simple cache storage
                logger.debug("💾 Profile cached", user_id=user_id)
            
            # Store profile
            self.profiles[user_id] = profile
            
            conn.close()
            
            # Response time tracking
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            
            logger.info("✅ Behavioral profile analyzed",
                       user_id=user_id,
                       analysis_time=f"{response_time:.4f}s",
                       big_five_confidence=big_five_result.get('confidence', 0.0) if OPTIMIZATIONS_AVAILABLE else 0.5)
            
            return profile
            
        except Exception as e:
            logger.error("❌ Behavioral profile analysis error",
                        user_id=user_id,
                        error=str(e),
                        exc_info=True)
            # Ensure connection is closed
            try:
                conn.close()
            except:
                pass
            return None
    
    def _calculate_risk_assessment(self, 
                                 big_five: Dict[str, float],
                                 sentiment_history: List[Tuple[datetime, float]],
                                 interaction_patterns: Dict[str, Any]) -> Dict[str, float]:
        """
        Kullanıcı risk değerlendirmesi hesapla.
        
        Args:
            big_five: Big Five trait scores
            sentiment_history: Sentiment geçmişi
            interaction_patterns: Etkileşim kalıpları
            
        Returns:
            Risk assessment scores
        """
        risk_scores = {}
        
        # Emotional stability risk (yüksek neuroticism + düşük sentiment)
        neuroticism = big_five.get('neuroticism', 0.5)
        avg_sentiment = interaction_patterns.get('avg_sentiment', 0.0)
        risk_scores['emotional_instability'] = (neuroticism * 0.7) + (max(0, -avg_sentiment) * 0.3)
        
        # Social isolation risk (düşük extraversion + düşük activity)
        extraversion = big_five.get('extraversion', 0.5)
        activity_score = interaction_patterns.get('activity_score', 0.5)
        risk_scores['social_isolation'] = (1 - extraversion) * 0.6 + (1 - activity_score) * 0.4
        
        # Conflict proneness (düşük agreeableness + yüksek sentiment variance)
        agreeableness = big_five.get('agreeableness', 0.5)
        sentiment_variance = interaction_patterns.get('sentiment_variance', 0.0)
        risk_scores['conflict_proneness'] = (1 - agreeableness) * 0.7 + min(1.0, sentiment_variance) * 0.3
        
        # Attention seeking (yüksek extraversion + yüksek activity + düşük conscientiousness)
        conscientiousness = big_five.get('conscientiousness', 0.5)
        risk_scores['attention_seeking'] = (extraversion * 0.4) + (activity_score * 0.4) + ((1 - conscientiousness) * 0.2)
        
        # Overall risk score
        risk_scores['overall_risk'] = statistics.mean(risk_scores.values())
        
        return risk_scores
    
    async def get_system_cache_metrics(self) -> SystemCacheMetrics:
        """Sistem cache metriklerini al."""
        try:
            # Cache statistics
            total_hits = self.cache_metrics.get('hits', 0)
            total_misses = self.cache_metrics.get('misses', 0)
            total_requests = total_hits + total_misses
            
            hit_rate = (total_hits / max(total_requests, 1)) * 100
            
            # Average response time
            avg_response_time = statistics.mean(self.response_times) if self.response_times else 0.0
            
            # Top accessed profiles
            top_profiles = []
            for user_id, profile in list(self.profiles.items())[:10]:
                top_profiles.append({
                    'user_id': user_id,
                    'username': profile.username,
                    'cache_hit_rate': profile.cache_hit_rate,
                    'total_analyses': profile.total_analyses,
                    'last_updated': profile.last_updated.isoformat()
                })
            
            # Sort by cache hit rate
            top_profiles.sort(key=lambda x: x['cache_hit_rate'], reverse=True)
            
            return SystemCacheMetrics(
                total_profiles=len(self.profiles),
                cache_hits_24h=total_hits,
                cache_misses_24h=total_misses,
                hit_rate_24h=hit_rate,
                avg_response_time=avg_response_time,
                top_accessed_profiles=top_profiles[:5],
                cache_size_mb=0.0,  # Would need Redis info for accurate measurement
                invalidations_24h=0  # Would track cache invalidations
            )
            
        except Exception as e:
            logger.error("❌ Cache metrics error", error=str(e))
            raise
    
    async def get_behavioral_insights_summary(self) -> Dict[str, Any]:
        """Genel behavioral insights özeti."""
        try:
            if not self.profiles:
                return {
                    'total_users': 0,
                    'insights': 'No user profiles available'
                }
            
            # Aggregate statistics
            all_big_five = {}
            all_risk_scores = {}
            sentiment_trends = []
            
            for profile in self.profiles.values():
                # Big Five aggregation
                for trait, score in profile.big_five_scores.items():
                    if trait not in all_big_five:
                        all_big_five[trait] = []
                    all_big_five[trait].append(score)
                
                # Risk aggregation
                for risk_type, score in profile.risk_assessment.items():
                    if risk_type not in all_risk_scores:
                        all_risk_scores[risk_type] = []
                    all_risk_scores[risk_type].append(score)
                
                # Sentiment trends
                if profile.sentiment_history:
                    avg_sentiment = statistics.mean([s[1] for s in profile.sentiment_history])
                    sentiment_trends.append(avg_sentiment)
            
            # Calculate averages
            avg_big_five = {
                trait: statistics.mean(scores) 
                for trait, scores in all_big_five.items()
            }
            
            avg_risk_scores = {
                risk_type: statistics.mean(scores)
                for risk_type, scores in all_risk_scores.items()
            }
            
            overall_sentiment = statistics.mean(sentiment_trends) if sentiment_trends else 0.0
            
            return {
                'total_users': len(self.profiles),
                'avg_big_five_traits': avg_big_five,
                'avg_risk_assessment': avg_risk_scores,
                'overall_sentiment_trend': overall_sentiment,
                'cache_performance': {
                    'hit_rate': (self.cache_metrics.get('hits', 0) / 
                               max(self.cache_metrics.get('hits', 0) + self.cache_metrics.get('misses', 0), 1)) * 100,
                    'total_analyses': self.cache_metrics.get('hits', 0) + self.cache_metrics.get('misses', 0)
                }
            }
            
        except Exception as e:
            logger.error("❌ Behavioral insights summary error", error=str(e))
            raise

# Initialize the manager
insights_manager = BehavioralInsightsManager()

# FastAPI app
app = FastAPI(
    title="🧠 Behavioral Insights Dashboard",
    description="Advanced user behavioral analysis with cache optimization",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Ana dashboard sayfası."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🧠 Behavioral Insights Dashboard</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .card { background: white; padding: 20px; margin: 10px 0; border-radius: 10px; 
                   box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
            .metric { background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }
            .metric h3 { margin: 0 0 10px 0; color: #495057; }
            .metric .value { font-size: 2em; font-weight: bold; color: #007bff; }
            .api-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }
            .api-endpoint { background: #e9ecef; padding: 15px; border-radius: 8px; }
            .api-endpoint h4 { margin: 0 0 10px 0; color: #495057; }
            .api-endpoint a { color: #007bff; text-decoration: none; }
            .api-endpoint a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 Behavioral Insights Dashboard</h1>
                <p>Advanced user behavioral analysis with Redis cache optimization</p>
            </div>
            
            <div class="card">
                <h2>📊 Quick Metrics</h2>
                <div class="metrics">
                    <div class="metric">
                        <h3>🎯 Cache Hit Rate</h3>
                        <div class="value" id="hit-rate">Loading...</div>
                    </div>
                    <div class="metric">
                        <h3>👥 Total Profiles</h3>
                        <div class="value" id="total-profiles">Loading...</div>
                    </div>
                    <div class="metric">
                        <h3>⚡ Avg Response Time</h3>
                        <div class="value" id="response-time">Loading...</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>🔗 API Endpoints</h2>
                <div class="api-list">
                    <div class="api-endpoint">
                        <h4>🧠 User Behavioral Profile</h4>
                        <a href="/api/behavioral/profile/12345">/api/behavioral/profile/{user_id}</a>
                        <p>Get detailed behavioral analysis for a specific user</p>
                    </div>
                    <div class="api-endpoint">
                        <h4>📊 System Cache Metrics</h4>
                        <a href="/api/behavioral/cache/metrics">/api/behavioral/cache/metrics</a>
                        <p>Get comprehensive cache performance metrics</p>
                    </div>
                    <div class="api-endpoint">
                        <h4>🎯 Insights Summary</h4>
                        <a href="/api/behavioral/insights/summary">/api/behavioral/insights/summary</a>
                        <p>Get aggregated behavioral insights across all users</p>
                    </div>
                    <div class="api-endpoint">
                        <h4>🔍 Search Users by Risk</h4>
                        <a href="/api/behavioral/users/high-risk">/api/behavioral/users/high-risk</a>
                        <p>Find users with high psychological risk scores</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Load quick metrics
            fetch('/api/behavioral/cache/metrics')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('hit-rate').textContent = data.hit_rate_24h.toFixed(1) + '%';
                    document.getElementById('total-profiles').textContent = data.total_profiles;
                    document.getElementById('response-time').textContent = (data.avg_response_time * 1000).toFixed(0) + 'ms';
                })
                .catch(error => console.error('Error loading metrics:', error));
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/behavioral/profile/{user_id}")
async def get_user_behavioral_profile(user_id: str):
    """
    Kullanıcının detaylı behavioral profilini al.
    
    Returns:
        Comprehensive behavioral analysis including Big Five traits,
        sentiment history, interaction patterns, and risk assessment.
    """
    try:
        profile = await insights_manager.analyze_user_behavioral_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Convert to JSON serializable format
        profile_data = asdict(profile)
        profile_data['sentiment_history'] = [
            {
                'timestamp': ts.isoformat(),
                'sentiment_score': score
            }
            for ts, score in profile.sentiment_history
        ]
        profile_data['last_updated'] = profile.last_updated.isoformat()
        
        return JSONResponse(content={
            'success': True,
            'profile': profile_data,
            'cache_performance': {
                'hit_rate': profile.cache_hit_rate,
                'total_analyses': profile.total_analyses
            }
        })
        
    except Exception as e:
        error_msg = f"Profile analysis error: {str(e)}"
        logger.error("❌ Profile endpoint error", user_id=user_id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/behavioral/cache/metrics")
async def get_cache_metrics():
    """
    Sistem cache metriklerini al.
    
    Returns:
        Comprehensive cache performance metrics including hit rates,
        response times, and top accessed profiles.
    """
    try:
        metrics = await insights_manager.get_system_cache_metrics()
        return JSONResponse(content=asdict(metrics))
        
    except Exception as e:
        logger.error("❌ Cache metrics endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/behavioral/insights/summary")
async def get_insights_summary():
    """
    Genel behavioral insights özetini al.
    
    Returns:
        Aggregated behavioral insights across all analyzed users.
    """
    try:
        summary = await insights_manager.get_behavioral_insights_summary()
        return JSONResponse(content=summary)
        
    except Exception as e:
        logger.error("❌ Insights summary endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/behavioral/users/high-risk")
async def get_high_risk_users(risk_threshold: float = 0.7):
    """
    Yüksek risk skoruna sahip kullanıcıları bul.
    
    Args:
        risk_threshold: Risk eşik değeri (0.0-1.0)
        
    Returns:
        List of users with high psychological risk scores.
    """
    try:
        high_risk_users = []
        
        for user_id, profile in insights_manager.profiles.items():
            overall_risk = profile.risk_assessment.get('overall_risk', 0.0)
            if overall_risk >= risk_threshold:
                high_risk_users.append({
                    'user_id': user_id,
                    'username': profile.username,
                    'overall_risk': overall_risk,
                    'risk_breakdown': profile.risk_assessment,
                    'last_updated': profile.last_updated.isoformat()
                })
        
        # Sort by risk score descending
        high_risk_users.sort(key=lambda x: x['overall_risk'], reverse=True)
        
        return JSONResponse(content={
            'success': True,
            'risk_threshold': risk_threshold,
            'high_risk_users': high_risk_users,
            'count': len(high_risk_users)
        })
        
    except Exception as e:
        logger.error("❌ High risk users endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Sistem sağlık kontrolü."""
    return {
        "status": "healthy",
        "service": "behavioral_insights_dashboard",
        "optimizations_available": OPTIMIZATIONS_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🧠 Starting Behavioral Insights Dashboard...")
    print("=" * 60)
    print("🔧 Features:")
    print("   • Big Five personality analysis")
    print("   • Sentiment history tracking")
    print("   • Interaction pattern recognition")
    print("   • Psychological risk assessment")
    print("   • Redis cache optimization")
    print("   • Real-time behavioral insights")
    print()
    print("🌐 Endpoints:")
    print("   • GET / - Dashboard home page")
    print("   • GET /api/behavioral/profile/{user_id}")
    print("   • GET /api/behavioral/cache/metrics")
    print("   • GET /api/behavioral/insights/summary")
    print("   • GET /api/behavioral/users/high-risk")
    print()
    print("📊 Starting server on http://localhost:5056")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5056,
        log_level="info"
    ) 