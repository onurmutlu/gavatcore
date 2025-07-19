from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
BEHAVIORAL ANALYTICS API - Admin Dashboard Endpoints
=====================================================

Advanced Behavioral Engine için REST API endpoints.
Admin paneli dashboard güncellemeleri ve analytics raporlama.

Endpoints:
- /api/behavioral/analytics/dashboard
- /api/behavioral/analytics/user/{user_id}
- /api/behavioral/analytics/metrics
- /api/behavioral/analytics/reports

@version: 1.0.0
@created: 2025-01-30
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import structlog

# FastAPI imports
try:
    from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Core imports
from core.behavioral_psychological_engine import (
    AdvancedBehavioralPsychologicalEngine,
    AdvancedUserProfile,
    BigFiveTraits
)
from core.behavioral_cache_manager import get_cache_manager

logger = structlog.get_logger("behavioral_api")

# ==================== DATA MODELS ====================

class DashboardMetrics(BaseModel):
    """Dashboard metrics model"""
    total_users: int = Field(..., description="Total analyzed users")
    active_users_24h: int = Field(..., description="Active users last 24h")
    total_analyses: int = Field(..., description="Total behavioral analyses")
    cache_hit_rate: float = Field(..., description="Cache hit rate percentage")
    avg_response_time: float = Field(..., description="Average API response time")
    system_health: str = Field(..., description="System health status")

class PersonalityDistribution(BaseModel):
    """Personality traits distribution"""
    openness: Dict[str, int] = Field(default_factory=dict)
    conscientiousness: Dict[str, int] = Field(default_factory=dict)
    extraversion: Dict[str, int] = Field(default_factory=dict)
    agreeableness: Dict[str, int] = Field(default_factory=dict)
    neuroticism: Dict[str, int] = Field(default_factory=dict)

class EngagementInsights(BaseModel):
    """User engagement insights"""
    high_conversion_users: int = Field(..., description="Users with high conversion probability")
    high_churn_risk_users: int = Field(..., description="Users with high churn risk")
    engagement_trends: Dict[str, float] = Field(default_factory=dict)
    optimal_contact_times: Dict[str, int] = Field(default_factory=dict)

class UserAnalyticsResponse(BaseModel):
    """Individual user analytics response"""
    user_id: int
    personality_summary: str
    engagement_score: float
    conversion_probability: float
    churn_risk: float
    optimal_strategies: List[str]
    last_analysis: str
    trends: Dict[str, Any]

class SystemPerformanceMetrics(BaseModel):
    """System performance metrics"""
    memory_usage: Dict[str, float]
    cache_performance: Dict[str, Any]
    api_latency: Dict[str, float]
    error_rates: Dict[str, float]
    uptime: float

# ==================== API ROUTER ====================

if FASTAPI_AVAILABLE:
    behavioral_router = FastAPI()
    
    # Global behavioral engine
    behavioral_engine = AdvancedBehavioralPsychologicalEngine()

    # ==================== HELPER FUNCTIONS ====================

    async def get_behavioral_engine():
        """Get behavioral engine dependency"""
        return behavioral_engine

    async def calculate_dashboard_metrics(engine: AdvancedBehavioralPsychologicalEngine) -> DashboardMetrics:
        """Dashboard metriklerini hesapla"""
        
        try:
            # Basic stats
            engine_stats = engine.get_advanced_engine_stats()
            total_users = engine_stats.get("total_profiles", 0)
            
            # Cache stats
            cache_manager = await get_cache_manager()
            cache_stats = await cache_manager.get_cache_stats()
            cache_hit_rate = cache_stats.get("metrics", {}).get("hit_rate", 0.0)
            avg_response_time = cache_stats.get("metrics", {}).get("avg_response_time", 0.0)
            
            # Active users (simulate - gerçek uygulamada DB'den alınır)
            active_users_24h = min(total_users, max(1, total_users // 3))
            
            # Total analyses (cache hit + miss)
            cache_metrics = cache_stats.get("metrics", {})
            total_analyses = cache_metrics.get("hits", 0) + cache_metrics.get("misses", 0)
            
            # System health
            system_health = "healthy" if cache_hit_rate > 50 and avg_response_time < 1.0 else "warning"
            
            return DashboardMetrics(
                total_users=total_users,
                active_users_24h=active_users_24h,
                total_analyses=total_analyses,
                cache_hit_rate=cache_hit_rate,
                avg_response_time=avg_response_time,
                system_health=system_health
            )
            
        except Exception as e:
            logger.error(f"❌ Dashboard metrics calculation error: {e}")
            raise HTTPException(status_code=500, detail=f"Metrics calculation failed: {str(e)}")

    async def get_personality_distribution(engine: AdvancedBehavioralPsychologicalEngine) -> PersonalityDistribution:
        """Personality traits dağılımını hesapla"""
        
        try:
            engine_stats = engine.get_advanced_engine_stats()
            big_five_dist = engine_stats.get("big_five_distribution", {})
            
            return PersonalityDistribution(
                openness=big_five_dist.get("openness", {}),
                conscientiousness=big_five_dist.get("conscientiousness", {}),
                extraversion=big_five_dist.get("extraversion", {}),
                agreeableness=big_five_dist.get("agreeableness", {}),
                neuroticism=big_five_dist.get("neuroticism", {})
            )
            
        except Exception as e:
            logger.error(f"❌ Personality distribution error: {e}")
            return PersonalityDistribution()

    async def get_engagement_insights(engine: AdvancedBehavioralPsychologicalEngine) -> EngagementInsights:
        """Engagement insights hesapla"""
        
        try:
            # Profilleri analiz et
            high_conversion = 0
            high_churn = 0
            contact_times = {"morning": 0, "afternoon": 0, "evening": 0, "night": 0}
            
            for user_id, profile in engine.user_profiles.items():
                if hasattr(profile, 'predictive_insights'):
                    if profile.predictive_insights.conversion_probability > 0.7:
                        high_conversion += 1
                    if profile.predictive_insights.churn_risk > 0.6:
                        high_churn += 1
                
                if hasattr(profile, 'timing_pattern'):
                    optimal_time = profile.timing_pattern.optimal_contact_time
                    if optimal_time in contact_times:
                        contact_times[optimal_time] += 1
            
            # Engagement trends (simulate)
            engagement_trends = {
                "weekly_growth": 15.2,
                "monthly_retention": 78.5,
                "avg_session_time": 12.4
            }
            
            return EngagementInsights(
                high_conversion_users=high_conversion,
                high_churn_risk_users=high_churn,
                engagement_trends=engagement_trends,
                optimal_contact_times=contact_times
            )
            
        except Exception as e:
            logger.error(f"❌ Engagement insights error: {e}")
            return EngagementInsights(
                high_conversion_users=0,
                high_churn_risk_users=0,
                engagement_trends={},
                optimal_contact_times={}
            )

    # ==================== API ENDPOINTS ====================

    @behavioral_router.get("/api/behavioral/analytics/dashboard", 
                          response_model=Dict[str, Any],
                          summary="Get complete dashboard analytics",
                          description="Returns comprehensive dashboard metrics for admin panel")
    async def get_dashboard_analytics(
        engine: AdvancedBehavioralPsychologicalEngine = Depends(get_behavioral_engine)
    ):
        """📊 Complete dashboard analytics"""
        
        try:
            logger.info("📊 Dashboard analytics request received")
            
            # Parallel processing için async tasks
            dashboard_task = calculate_dashboard_metrics(engine)
            personality_task = get_personality_distribution(engine)
            engagement_task = get_engagement_insights(engine)
            
            # Concurrent execution
            dashboard_metrics, personality_dist, engagement_insights = await asyncio.gather(
                dashboard_task,
                personality_task, 
                engagement_task
            )
            
            # Cache performance
            cache_manager = await get_cache_manager()
            cache_stats = await cache_manager.get_cache_stats()
            
            response = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "metrics": dashboard_metrics.dict(),
                "personality_distribution": personality_dist.dict(),
                "engagement_insights": engagement_insights.dict(),
                "cache_performance": cache_stats,
                "system_info": {
                    "engine_version": "2.0.0",
                    "total_profiles": len(engine.user_profiles),
                    "gpt_available": engine.gpt_available
                }
            }
            
            logger.info(f"✅ Dashboard analytics completed: {len(engine.user_profiles)} profiles")
            return response
            
        except Exception as e:
            logger.error(f"❌ Dashboard analytics error: {e}")
            raise HTTPException(status_code=500, detail=f"Dashboard analytics failed: {str(e)}")

    @behavioral_router.get("/api/behavioral/analytics/user/{user_id}",
                          response_model=UserAnalyticsResponse,
                          summary="Get individual user analytics",
                          description="Returns detailed behavioral analytics for specific user")
    async def get_user_analytics(
        user_id: int,
        engine: AdvancedBehavioralPsychologicalEngine = Depends(get_behavioral_engine)
    ):
        """👤 Individual user behavioral analytics"""
        
        try:
            logger.info(f"👤 User analytics request: {user_id}")
            
            if user_id not in engine.user_profiles:
                raise HTTPException(status_code=404, detail=f"User {user_id} not found in behavioral profiles")
            
            profile = engine.user_profiles[user_id]
            
            # Generate comprehensive report
            report = engine.generate_comprehensive_report(user_id)
            
            if "error" in report:
                raise HTTPException(status_code=500, detail=report["error"])
            
            # Engagement score calculation
            engagement_score = (
                profile.social_dynamics.engagement_rate * 0.4 +
                (1.0 - profile.predictive_insights.churn_risk) * 0.3 +
                profile.sentiment_trend.emotional_stability * 0.3
            )
            
            # Trends data
            trends = {
                "personality_stability": profile.sentiment_trend.emotional_stability,
                "engagement_trend": profile.sentiment_trend.trend_direction,
                "social_influence": profile.social_dynamics.influence_score,
                "motivation_level": profile.motivation_profile.drive_level
            }
            
            response = UserAnalyticsResponse(
                user_id=user_id,
                personality_summary=report["big_five_personality"]["personality_summary"],
                engagement_score=engagement_score,
                conversion_probability=profile.predictive_insights.conversion_probability,
                churn_risk=profile.predictive_insights.churn_risk,
                optimal_strategies=profile.predictive_insights.optimal_strategies,
                last_analysis=profile.last_updated.isoformat(),
                trends=trends
            )
            
            logger.info(f"✅ User analytics completed: {user_id}")
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ User analytics error: {e}")
            raise HTTPException(status_code=500, detail=f"User analytics failed: {str(e)}")

    @behavioral_router.get("/api/behavioral/analytics/metrics/performance",
                          response_model=SystemPerformanceMetrics,
                          summary="Get system performance metrics",
                          description="Returns detailed system performance and optimization metrics")
    async def get_performance_metrics(
        engine: AdvancedBehavioralPsychologicalEngine = Depends(get_behavioral_engine)
    ):
        """⚡ System performance metrics"""
        
        try:
            logger.info("⚡ Performance metrics request")
            
            # Cache performance
            cache_manager = await get_cache_manager()
            cache_stats = await cache_manager.get_cache_stats()
            
            # Memory usage simulation
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            memory_usage = {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "cache_size": len(engine.user_profiles),
                "memory_percent": process.memory_percent()
            }
            
            # API latency (simulated)
            api_latency = {
                "avg_response_time": cache_stats.get("metrics", {}).get("avg_response_time", 0.0),
                "p95_response_time": cache_stats.get("metrics", {}).get("avg_response_time", 0.0) * 1.5,
                "cache_latency": 0.05
            }
            
            # Error rates (simulated)
            error_rates = {
                "api_error_rate": 0.1,
                "cache_error_rate": 0.05,
                "analysis_error_rate": 0.02
            }
            
            response = SystemPerformanceMetrics(
                memory_usage=memory_usage,
                cache_performance=cache_stats,
                api_latency=api_latency,
                error_rates=error_rates,
                uptime=3600.0  # Simulated uptime
            )
            
            logger.info("✅ Performance metrics completed")
            return response
            
        except Exception as e:
            logger.error(f"❌ Performance metrics error: {e}")
            raise HTTPException(status_code=500, detail=f"Performance metrics failed: {str(e)}")

    @behavioral_router.post("/api/behavioral/analytics/cache/invalidate/{user_id}",
                           summary="Invalidate user cache",
                           description="Invalidates all cached data for specific user")
    async def invalidate_user_cache(
        user_id: int,
        background_tasks: BackgroundTasks
    ):
        """🗑️ Invalidate user cache"""
        
        try:
            logger.info(f"🗑️ Cache invalidation request: {user_id}")
            
            # Background task for cache invalidation
            async def _invalidate():
                cache_manager = await get_cache_manager()
                await cache_manager.invalidate_user_cache(user_id)
            
            background_tasks.add_task(_invalidate)
            
            return {
                "status": "success",
                "message": f"Cache invalidation initiated for user {user_id}",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Cache invalidation error: {e}")
            raise HTTPException(status_code=500, detail=f"Cache invalidation failed: {str(e)}")

    @behavioral_router.get("/api/behavioral/analytics/reports/export/{report_type}",
                          summary="Export analytics reports",
                          description="Export detailed analytics reports in various formats")
    async def export_analytics_report(
        report_type: str,
        format: str = "json",
        engine: AdvancedBehavioralPsychologicalEngine = Depends(get_behavioral_engine)
    ):
        """📄 Export analytics reports"""
        
        try:
            logger.info(f"📄 Report export request: {report_type} ({format})")
            
            if report_type not in ["dashboard", "users", "performance"]:
                raise HTTPException(status_code=400, detail="Invalid report type")
            
            if format not in ["json", "csv"]:
                raise HTTPException(status_code=400, detail="Invalid format")
            
            # Generate report based on type
            if report_type == "dashboard":
                dashboard_metrics = await calculate_dashboard_metrics(engine)
                personality_dist = await get_personality_distribution(engine)
                engagement_insights = await get_engagement_insights(engine)
                
                report_data = {
                    "metrics": dashboard_metrics.dict(),
                    "personality": personality_dist.dict(),
                    "engagement": engagement_insights.dict(),
                    "export_timestamp": datetime.now().isoformat()
                }
                
            elif report_type == "users":
                users_data = []
                for user_id in engine.user_profiles.keys():
                    try:
                        user_report = engine.generate_comprehensive_report(user_id)
                        if "error" not in user_report:
                            users_data.append(user_report)
                    except Exception as e:
                        logger.warning(f"⚠️ User report error {user_id}: {e}")
                
                report_data = {
                    "users": users_data,
                    "total_count": len(users_data),
                    "export_timestamp": datetime.now().isoformat()
                }
                
            elif report_type == "performance":
                cache_manager = await get_cache_manager()
                cache_stats = await cache_manager.get_cache_stats()
                engine_stats = engine.get_advanced_engine_stats()
                
                report_data = {
                    "cache_performance": cache_stats,
                    "engine_stats": engine_stats,
                    "export_timestamp": datetime.now().isoformat()
                }
            
            # Format handling
            if format == "json":
                return JSONResponse(
                    content=report_data,
                    headers={
                        "Content-Disposition": f"attachment; filename={report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    }
                )
            elif format == "csv":
                # CSV formatı için basit implementation
                import io
                import csv
                
                output = io.StringIO()
                if report_type == "users" and "users" in report_data:
                    writer = csv.DictWriter(output, fieldnames=["user_id", "personality_summary", "conversion_probability", "churn_risk"])
                    writer.writeheader()
                    for user in report_data["users"]:
                        writer.writerow({
                            "user_id": user.get("user_id"),
                            "personality_summary": user.get("big_five_personality", {}).get("personality_summary", ""),
                            "conversion_probability": user.get("predictive_insights", {}).get("conversion_probability", 0),
                            "churn_risk": user.get("predictive_insights", {}).get("churn_risk", 0)
                        })
                
                return JSONResponse(
                    content={"csv_data": output.getvalue()},
                    headers={
                        "Content-Disposition": f"attachment; filename={report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    }
                )
            
            logger.info(f"✅ Report export completed: {report_type}")
            return report_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Report export error: {e}")
            raise HTTPException(status_code=500, detail=f"Report export failed: {str(e)}")

    @behavioral_router.get("/api/behavioral/analytics/health",
                          summary="Health check endpoint",
                          description="Returns system health status")
    async def health_check():
        """🏥 System health check"""
        
        try:
            cache_manager = await get_cache_manager()
            cache_stats = await cache_manager.get_cache_stats()
            
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "behavioral_engine": "online",
                    "cache_manager": "online" if cache_stats else "offline",
                    "redis": "online" if cache_stats.get("cache_type") == "redis" else "fallback"
                },
                "version": "2.0.0"
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    logger.info("🌐 Behavioral Analytics API endpoints initialized")

else:
    logger.warning("⚠️ FastAPI not available, behavioral API disabled")
    behavioral_router = None

__all__ = [
    "behavioral_router",
    "DashboardMetrics",
    "PersonalityDistribution", 
    "EngagementInsights",
    "UserAnalyticsResponse",
    "SystemPerformanceMetrics"
] 