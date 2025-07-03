#!/usr/bin/env python3
"""
📱 Flutter Dashboard Adapter API
===============================

Flutter mobile/web panel'den kolayca çağrılabilecek 
özel API adapter'ı.

✨ Özellikler:
- CORS configured for Flutter web
- Simplified JSON responses  
- Mobile-friendly data structure
- Authentication ready endpoints
- Real-time data aggregation
- Minimal bandwidth usage

@version: 1.0.0
@created: 2025-01-30
"""

import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics

from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import structlog
import requests

logger = structlog.get_logger("flutter_adapter")

# FastAPI app
app = FastAPI(
    title="📱 Flutter Dashboard Adapter",
    description="Mobile-optimized API for GAVATCore Flutter panels",
    version="1.0.0"
)

# CORS for Flutter web/mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://127.0.0.1",
        "*"  # For development - tighten in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SERVICES = {
    'comprehensive': 'http://localhost:8000',
    'behavioral': 'http://localhost:5057',
    'scalable': 'http://localhost:6000'
}

class FlutterDataTransformer:
    """Flutter için veri dönüştürücü."""
    
    @staticmethod
    def simplify_health_data(health_data: Dict) -> Dict:
        """Health data'yı Flutter için basitleştir."""
        return {
            'overall_health': health_data.get('overall_health', 0),
            'status': health_data.get('status', 'unknown'),
            'healthy_services': health_data.get('summary', {}).get('healthy_services', 0),
            'total_services': health_data.get('summary', {}).get('total_services', 0),
            'timestamp': health_data.get('summary', {}).get('timestamp', datetime.now().isoformat())
        }
    
    @staticmethod  
    def simplify_performance_data(perf_data: Dict) -> Dict:
        """Performance data'yı Flutter için basitleştir."""
        cache_perf = perf_data.get('cache_performance', {})
        behavioral = perf_data.get('behavioral_insights', {})
        system = perf_data.get('system_metrics', {})
        
        return {
            'cache_hit_rate': cache_perf.get('hit_rate', 0),
            'avg_response_time': cache_perf.get('avg_response_time', 0),
            'performance_grade': cache_perf.get('performance_grade', 'N/A'),
            'total_users': behavioral.get('database_stats', {}).get('total_users', 0),
            'total_messages': behavioral.get('database_stats', {}).get('total_messages', 0),
            'uptime_percentage': system.get('uptime_percentage', 0),
            'timestamp': perf_data.get('timestamp', datetime.now().isoformat())
        }
    
    @staticmethod
    def simplify_user_data(users_data: Dict) -> List[Dict]:
        """User data'yı Flutter için basitleştir."""
        users = users_data.get('users', [])
        return [
            {
                'id': user.get('user_id', ''),
                'name': user.get('username', 'Unknown'),
                'message_count': user.get('message_count', 0)
            }
            for user in users[:10]  # Top 10 only for mobile
        ]

transformer = FlutterDataTransformer()

@app.get("/api/flutter/dashboard")
async def flutter_dashboard_summary():
    """
    Flutter dashboard için özet bilgiler.
    
    Returns:
        Simplified dashboard data optimized for mobile display
    """
    try:
        # Get dashboard stats
        dashboard_stats = {}
        try:
            response = requests.get(f"{SERVICES['comprehensive']}/api/dashboard/stats", timeout=3)
            if response.status_code == 200:
                dashboard_stats = response.json()
        except:
            pass
        
        # Get system health
        health_data = {}
        try:
            response = requests.get(f"{SERVICES['comprehensive']}/api/system/health", timeout=3)
            if response.status_code == 200:
                health_data = response.json()
        except:
            pass
        
        # Get user count
        user_count = 0
        try:
            response = requests.get(f"{SERVICES['behavioral']}/api/users", timeout=3)
            if response.status_code == 200:
                users_data = response.json()
                user_count = users_data.get('total_users', 0)
        except:
            pass
        
        # Create Flutter-friendly response
        flutter_response = {
            'success': True,
            'data': {
                'system_health': dashboard_stats.get('system_health', 0),
                'cache_hit_rate': dashboard_stats.get('cache_hit_rate', 0),
                'active_users': user_count,
                'avg_response_time': dashboard_stats.get('avg_response_time', 0),
                'overall_status': health_data.get('status', 'unknown'),
                'healthy_services': health_data.get('summary', {}).get('healthy_services', 0),
                'total_services': health_data.get('summary', {}).get('total_services', 0)
            },
            'timestamp': datetime.now().isoformat(),
            'refresh_interval': 30  # Seconds
        }
        
        logger.debug("📱 Flutter dashboard data sent", 
                    health=flutter_response['data']['system_health'],
                    users=flutter_response['data']['active_users'])
        
        return JSONResponse(content=flutter_response)
        
    except Exception as e:
        logger.error("❌ Flutter dashboard error", error=str(e))
        return JSONResponse(
            content={
                'success': False,
                'error': str(e),
                'data': None,
                'timestamp': datetime.now().isoformat()
            },
            status_code=500
        )

@app.get("/api/flutter/performance")
async def flutter_performance_metrics():
    """
    Flutter için performance metrikleri.
    
    Returns:
        Simplified performance data for mobile charts
    """
    try:
        # Get comprehensive performance report
        perf_data = {}
        try:
            response = requests.get(f"{SERVICES['comprehensive']}/api/performance/report", timeout=5)
            if response.status_code == 200:
                perf_data = response.json()
        except:
            pass
        
        # Transform for Flutter
        flutter_perf = transformer.simplify_performance_data(perf_data)
        
        return JSONResponse(content={
            'success': True,
            'performance': flutter_perf,
            'charts_data': {
                'cache_trend': [
                    {'time': '1h ago', 'value': flutter_perf['cache_hit_rate']},
                    {'time': 'now', 'value': flutter_perf['cache_hit_rate']}
                ],
                'response_trend': [
                    {'time': '1h ago', 'value': flutter_perf['avg_response_time']},
                    {'time': 'now', 'value': flutter_perf['avg_response_time']}
                ]
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error("❌ Flutter performance error", error=str(e))
        return JSONResponse(content={
            'success': False,
            'error': str(e)
        }, status_code=500)

@app.get("/api/flutter/users")
async def flutter_users_list():
    """
    Flutter için kullanıcı listesi.
    
    Returns:
        Simplified user list for mobile display
    """
    try:
        # Get users from behavioral service
        users_data = {}
        try:
            response = requests.get(f"{SERVICES['behavioral']}/api/users", timeout=3)
            if response.status_code == 200:
                users_data = response.json()
        except:
            pass
        
        # Transform for Flutter
        flutter_users = transformer.simplify_user_data(users_data)
        
        return JSONResponse(content={
            'success': True,
            'users': flutter_users,
            'total_count': len(flutter_users),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error("❌ Flutter users error", error=str(e))
        return JSONResponse(content={
            'success': False,
            'error': str(e)
        }, status_code=500)

@app.get("/api/flutter/user/{user_id}/profile")
async def flutter_user_profile(user_id: str):
    """
    Flutter için kullanıcı profili.
    
    Args:
        user_id: User identifier
        
    Returns:
        Simplified user profile for mobile display
    """
    try:
        # Get user profile from behavioral service
        profile_data = {}
        try:
            response = requests.get(f"{SERVICES['behavioral']}/api/profile/{user_id}", timeout=5)
            if response.status_code == 200:
                profile_data = response.json()
        except:
            pass
        
        if not profile_data:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Simplify for Flutter
        big_five = profile_data.get('big_five_traits', {})
        sentiment = profile_data.get('sentiment_analysis', {})
        risk = profile_data.get('risk_assessment', {})
        
        flutter_profile = {
            'user_id': user_id,
            'username': profile_data.get('username', 'Unknown'),
            'personality': {
                'openness': round(big_five.get('openness', 0) * 100),
                'conscientiousness': round(big_five.get('conscientiousness', 0) * 100),
                'extraversion': round(big_five.get('extraversion', 0) * 100),
                'agreeableness': round(big_five.get('agreeableness', 0) * 100),
                'neuroticism': round(big_five.get('neuroticism', 0) * 100)
            },
            'sentiment': {
                'average': round(sentiment.get('average_sentiment', 0), 2),
                'total_messages': sentiment.get('total_messages', 0)
            },
            'risk_level': risk.get('risk_level', 'Unknown'),
            'analysis_time': profile_data.get('statistics', {}).get('analysis_time', 'N/A')
        }
        
        return JSONResponse(content={
            'success': True,
            'profile': flutter_profile,
            'timestamp': datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ Flutter user profile error", error=str(e), user_id=user_id)
        return JSONResponse(content={
            'success': False,
            'error': str(e)
        }, status_code=500)

@app.get("/api/flutter/services/status")
async def flutter_services_status():
    """
    Flutter için servis durumları.
    
    Returns:
        Simplified service status for mobile display
    """
    try:
        services_status = []
        
        for service_name, url in SERVICES.items():
            try:
                start_time = time.time()
                response = requests.get(f"{url}/health", timeout=2)
                response_time = int((time.time() - start_time) * 1000)
                
                status = "online" if response.status_code == 200 else "error"
                
                services_status.append({
                    'name': service_name.title(),
                    'status': status,
                    'response_time': response_time,
                    'url': url
                })
                
            except:
                services_status.append({
                    'name': service_name.title(),
                    'status': "offline",
                    'response_time': -1,
                    'url': url
                })
        
        online_count = sum(1 for s in services_status if s['status'] == 'online')
        total_count = len(services_status)
        
        return JSONResponse(content={
            'success': True,
            'services': services_status,
            'summary': {
                'online': online_count,
                'total': total_count,
                'health_percentage': (online_count / total_count) * 100
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error("❌ Flutter services status error", error=str(e))
        return JSONResponse(content={
            'success': False,
            'error': str(e)
        }, status_code=500)

@app.get("/api/flutter/quick-stats")
async def flutter_quick_stats():
    """
    Flutter için hızlı istatistikler (dashboard widget'ları için).
    
    Returns:
        Ultra-simplified stats for Flutter widgets
    """
    try:
        # Aggregate quick stats from all services
        stats = {
            'system_health': 0,
            'active_users': 0,
            'cache_efficiency': 0,
            'response_time': 0,
            'status': 'unknown'
        }
        
        # Get dashboard stats
        try:
            response = requests.get(f"{SERVICES['comprehensive']}/api/dashboard/stats", timeout=2)
            if response.status_code == 200:
                data = response.json()
                stats['system_health'] = int(data.get('system_health', 0))
                stats['active_users'] = data.get('active_users', 0)
                stats['cache_efficiency'] = int(data.get('cache_hit_rate', 0))
                stats['response_time'] = data.get('avg_response_time', 0)
        except:
            pass
        
        # Determine overall status
        if stats['system_health'] >= 80:
            stats['status'] = 'excellent'
        elif stats['system_health'] >= 60:
            stats['status'] = 'good'  
        elif stats['system_health'] >= 40:
            stats['status'] = 'warning'
        else:
            stats['status'] = 'critical'
        
        return JSONResponse(content={
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat(),
            'cache_ttl': 30  # Flutter can cache for 30 seconds
        })
        
    except Exception as e:
        logger.error("❌ Flutter quick stats error", error=str(e))
        return JSONResponse(content={
            'success': False,
            'error': str(e),
            'stats': {
                'system_health': 0,
                'active_users': 0,
                'cache_efficiency': 0,
                'response_time': 0,
                'status': 'error'
            }
        }, status_code=500)

@app.get("/health")
async def health_check():
    """Flutter adapter sağlık kontrolü."""
    return {
        'status': 'healthy',
        'service': 'flutter_dashboard_adapter',
        'flutter_compatible': True,
        'cors_enabled': True,
        'timestamp': datetime.now().isoformat()
    }

@app.get("/api/flutter/test")
async def flutter_test_endpoint():
    """Flutter bağlantı test endpoint'i."""
    return JSONResponse(content={
        'success': True,
        'message': 'Flutter adapter working perfectly!',
        'test_data': {
            'random_number': int(time.time()) % 1000,
            'timestamp': datetime.now().isoformat(),
            'flutter_ready': True
        }
    })

if __name__ == "__main__":
    print("📱 Starting Flutter Dashboard Adapter...")
    print("=" * 60)
    print("🚀 Flutter-optimized features:")
    print("   • CORS enabled for web/mobile")
    print("   • Simplified JSON responses")
    print("   • Mobile-friendly data structure")
    print("   • Minimal bandwidth usage")
    print("   • Real-time data aggregation")
    print()
    print("🌐 Flutter API Base URL: http://localhost:9500")
    print("📊 Test endpoint: http://localhost:9500/api/flutter/test")
    print("📱 Quick stats: http://localhost:9500/api/flutter/quick-stats")
    print("🎛️ Dashboard: http://localhost:9500/api/flutter/dashboard")
    print()
    print("📋 Available Endpoints:")
    print("   • GET /api/flutter/dashboard - Main dashboard data")
    print("   • GET /api/flutter/performance - Performance metrics")
    print("   • GET /api/flutter/users - Users list")
    print("   • GET /api/flutter/user/{id}/profile - User profile")
    print("   • GET /api/flutter/services/status - Services status")
    print("   • GET /api/flutter/quick-stats - Widget data")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9500,
        log_level="info"
    ) 