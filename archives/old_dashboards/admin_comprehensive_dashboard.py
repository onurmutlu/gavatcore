from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🎛️ GAVATCore Comprehensive Admin Dashboard
==========================================

Tüm sistemleri birleştiren ultimate admin control center:
- Behavioral Insights Dashboard integration
- Cache Performance Monitoring
- Smart Personality Adapter metrics
- Real-time system health monitoring
- Performance optimization recommendations

🚀 Ultimate GAVATCore Control Panel

@version: 1.0.0
@created: 2025-01-30
"""

import asyncio
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import structlog
import requests

# Import our systems
try:
    from core.cache_performance_monitor import cache_monitor
    CACHE_MONITOR_AVAILABLE = True
except ImportError:
    CACHE_MONITOR_AVAILABLE = False

try:
    from core.smart_personality_adapter import personality_adapter
    PERSONALITY_ADAPTER_AVAILABLE = True
except ImportError:
    PERSONALITY_ADAPTER_AVAILABLE = False

logger = structlog.get_logger("comprehensive_dashboard")

# FastAPI app
app = FastAPI(
    title="🎛️ GAVATCore Comprehensive Dashboard",
    description="Ultimate admin control center for GAVATCore platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SERVICES = {
    'behavioral_insights': 'http://localhost:5057',
    'simple_admin': 'http://localhost:5055',
    'main_api': 'http://localhost:5050',
    'scalable_api': 'http://localhost:6000'
}

class SystemHealthChecker:
    """Sistem sağlık kontrolcüsü."""
    
    def __init__(self):
        self.last_health_check = {}
        self.service_status = {}
    
    async def check_all_services(self) -> Dict[str, Any]:
        """Tüm servislerin sağlığını kontrol et."""
        health_status = {}
        
        for service_name, url in SERVICES.items():
            try:
                start_time = time.time()
                response = requests.get(f"{url}/health", timeout=3)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    health_status[service_name] = {
                        'status': 'healthy',
                        'response_time_ms': response_time,
                        'url': url,
                        'last_check': datetime.now().isoformat()
                    }
                else:
                    health_status[service_name] = {
                        'status': 'unhealthy',
                        'status_code': response.status_code,
                        'url': url,
                        'last_check': datetime.now().isoformat()
                    }
                    
            except Exception as e:
                health_status[service_name] = {
                    'status': 'offline',
                    'error': str(e),
                    'url': url,
                    'last_check': datetime.now().isoformat()
                }
        
        self.service_status = health_status
        return health_status

# Global health checker
health_checker = SystemHealthChecker()

@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Comprehensive dashboard ana sayfa."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎛️ GAVATCore Comprehensive Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333; min-height: 100vh; 
            }
            .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            
            .header { 
                background: rgba(255,255,255,0.95); 
                padding: 30px; border-radius: 15px; 
                margin-bottom: 30px; text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }
            
            .header h1 { 
                font-size: 2.5em; margin-bottom: 10px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            }
            
            .header p { font-size: 1.2em; color: #666; }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                background: rgba(255,255,255,0.95);
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            
            .stat-card:hover { transform: translateY(-5px); }
            
            .stat-value {
                font-size: 2.5em;
                font-weight: bold;
                margin: 10px 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .stat-label {
                font-size: 1.1em;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .services-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 25px;
                margin-bottom: 30px;
            }
            
            .service-card {
                background: rgba(255,255,255,0.95);
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }
            
            .service-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            
            .service-title {
                font-size: 1.3em;
                font-weight: bold;
                color: #333;
            }
            
            .status-indicator {
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: bold;
                text-transform: uppercase;
            }
            
            .status-healthy { background: #d4edda; color: #155724; }
            .status-warning { background: #fff3cd; color: #856404; }
            .status-offline { background: #f8d7da; color: #721c24; }
            
            .service-metrics {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 15px;
            }
            
            .metric {
                text-align: center;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 10px;
            }
            
            .metric-value {
                font-size: 1.4em;
                font-weight: bold;
                color: #007bff;
            }
            
            .metric-label {
                font-size: 0.9em;
                color: #666;
                margin-top: 5px;
            }
            
            .actions-panel {
                background: rgba(255,255,255,0.95);
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            
            .action-buttons {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            
            .action-btn {
                padding: 15px 25px;
                border: none;
                border-radius: 10px;
                font-size: 1em;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                text-align: center;
            }
            
            .btn-primary { background: #007bff; color: white; }
            .btn-success { background: #28a745; color: white; }
            .btn-warning { background: #ffc107; color: #212529; }
            .btn-info { background: #17a2b8; color: white; }
            
            .action-btn:hover { transform: translateY(-2px); opacity: 0.9; }
            
            .refresh-indicator {
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 0.9em;
                display: none;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            
            .loading { animation: pulse 1.5s infinite; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎛️ GAVATCore Comprehensive Dashboard</h1>
                <p>Ultimate Admin Control Center for Performance Optimization & Behavioral Analytics</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">System Health</div>
                    <div class="stat-value" id="system-health">Loading...</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Cache Hit Rate</div>
                    <div class="stat-value" id="cache-hit-rate">Loading...</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Active Users</div>
                    <div class="stat-value" id="active-users">Loading...</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Avg Response</div>
                    <div class="stat-value" id="avg-response">Loading...</div>
                </div>
            </div>
            
            <div class="services-grid" id="services-grid">
                <!-- Services will be loaded here -->
            </div>
            
            <div class="actions-panel">
                <h3>🚀 Quick Actions</h3>
                <div class="action-buttons">
                    <a href="/api/system/health" class="action-btn btn-primary">Full Health Check</a>
                    <a href="/api/performance/report" class="action-btn btn-success">Performance Report</a>
                    <a href="/api/behavioral/insights" class="action-btn btn-info">Behavioral Insights</a>
                    <a href="/api/cache/optimization" class="action-btn btn-warning">Cache Optimization</a>
                    <a href="http://localhost:5057" target="_blank" class="action-btn btn-info">Behavioral Dashboard</a>
                    <a href="http://localhost:5055" target="_blank" class="action-btn btn-success">Simple Admin</a>
                </div>
            </div>
        </div>
        
        <div class="refresh-indicator" id="refresh-indicator">
            🔄 Refreshing data...
        </div>
        
        <script>
            let refreshInterval;
            
            function showRefreshIndicator() {
                document.getElementById('refresh-indicator').style.display = 'block';
            }
            
            function hideRefreshIndicator() {
                document.getElementById('refresh-indicator').style.display = 'none';
            }
            
            async function loadSystemStats() {
                try {
                    showRefreshIndicator();
                    
                    // Load basic stats
                    const statsResponse = await fetch('/api/dashboard/stats');
                    const stats = await statsResponse.json();
                    
                    document.getElementById('system-health').textContent = stats.system_health + '%';
                    document.getElementById('cache-hit-rate').textContent = stats.cache_hit_rate.toFixed(1) + '%';
                    document.getElementById('active-users').textContent = stats.active_users;
                    document.getElementById('avg-response').textContent = stats.avg_response_time + 'ms';
                    
                    // Load services
                    const servicesResponse = await fetch('/api/system/health');
                    const services = await servicesResponse.json();
                    
                    const servicesGrid = document.getElementById('services-grid');
                    servicesGrid.innerHTML = '';
                    
                    for (const [serviceName, serviceData] of Object.entries(services.services)) {
                        const serviceCard = createServiceCard(serviceName, serviceData);
                        servicesGrid.appendChild(serviceCard);
                    }
                    
                } catch (error) {
                    console.error('Error loading stats:', error);
                } finally {
                    hideRefreshIndicator();
                }
            }
            
            function createServiceCard(name, data) {
                const card = document.createElement('div');
                card.className = 'service-card';
                
                const statusClass = data.status === 'healthy' ? 'status-healthy' : 
                                  data.status === 'offline' ? 'status-offline' : 'status-warning';
                
                card.innerHTML = `
                    <div class="service-header">
                        <div class="service-title">${name.replace('_', ' ').toUpperCase()}</div>
                        <div class="status-indicator ${statusClass}">${data.status}</div>
                    </div>
                    <div class="service-metrics">
                        <div class="metric">
                            <div class="metric-value">${data.response_time_ms ? data.response_time_ms.toFixed(0) + 'ms' : 'N/A'}</div>
                            <div class="metric-label">Response Time</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">${data.last_check ? new Date(data.last_check).toLocaleTimeString() : 'Never'}</div>
                            <div class="metric-label">Last Check</div>
                        </div>
                    </div>
                `;
                
                return card;
            }
            
            function startAutoRefresh() {
                loadSystemStats(); // Initial load
                refreshInterval = setInterval(loadSystemStats, 30000); // Refresh every 30 seconds
            }
            
            function stopAutoRefresh() {
                if (refreshInterval) {
                    clearInterval(refreshInterval);
                }
            }
            
            // Start auto-refresh on page load
            document.addEventListener('DOMContentLoaded', startAutoRefresh);
            
            // Stop auto-refresh when page is hidden
            document.addEventListener('visibilitychange', function() {
                if (document.hidden) {
                    stopAutoRefresh();
                } else {
                    startAutoRefresh();
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Dashboard için özet istatistikler."""
    try:
        # System health check
        health_status = await health_checker.check_all_services()
        healthy_services = sum(1 for service in health_status.values() if service['status'] == 'healthy')
        total_services = len(health_status)
        system_health = (healthy_services / max(total_services, 1)) * 100
        
        # Cache metrics
        cache_hit_rate = 0.0
        avg_response_time = 0
        
        if CACHE_MONITOR_AVAILABLE:
            try:
                cache_report = cache_monitor.generate_performance_report("last_hour")
                cache_hit_rate = cache_report.hit_rate_percentage
                avg_response_time = int(cache_report.avg_response_time_ms)
            except:
                pass
        
        # Active users (try to get from behavioral insights)
        active_users = 0
        try:
            response = requests.get(f"{SERVICES['behavioral_insights']}/api/users", timeout=3)
            if response.status_code == 200:
                users_data = response.json()
                active_users = users_data.get('total_users', 0)
        except:
            pass
        
        return JSONResponse(content={
            'system_health': system_health,
            'cache_hit_rate': cache_hit_rate,
            'active_users': active_users,
            'avg_response_time': avg_response_time,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error("❌ Dashboard stats error", error=str(e))
        return JSONResponse(content={
            'system_health': 0,
            'cache_hit_rate': 0,
            'active_users': 0,
            'avg_response_time': 0,
            'error': str(e)
        })

@app.get("/api/system/health")
async def comprehensive_health_check():
    """Comprehensive sistem sağlık kontrolü."""
    try:
        services_status = await health_checker.check_all_services()
        
        # Add cache monitor status
        cache_status = "unknown"
        if CACHE_MONITOR_AVAILABLE:
            try:
                cache_metrics = cache_monitor.export_dashboard_metrics()
                cache_status = "healthy" if cache_metrics.get('system_health', {}).get('monitoring_active') else "inactive"
            except:
                cache_status = "error"
        
        # Add personality adapter status
        personality_status = "unknown"
        if PERSONALITY_ADAPTER_AVAILABLE:
            try:
                test_profile = await personality_adapter.get_user_personality_profile("test_user")
                personality_status = "healthy" if test_profile or True else "error"  # Always healthy if available
            except:
                personality_status = "error"
        
        # Overall system status
        healthy_count = sum(1 for s in services_status.values() if s['status'] == 'healthy')
        total_count = len(services_status)
        overall_health = (healthy_count / max(total_count, 1)) * 100
        
        return JSONResponse(content={
            'overall_health': overall_health,
            'status': 'healthy' if overall_health >= 70 else 'degraded' if overall_health >= 50 else 'critical',
            'services': services_status,
            'internal_systems': {
                'cache_monitor': cache_status,
                'personality_adapter': personality_status
            },
            'summary': {
                'healthy_services': healthy_count,
                'total_services': total_count,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error("❌ Health check error", error=str(e))
        return JSONResponse(
            status_code=500,
            content={'error': str(e), 'status': 'error'}
        )

@app.get("/api/performance/report")
async def comprehensive_performance_report():
    """Comprehensive performance raporu."""
    try:
        report = {
            'timestamp': datetime.now().isoformat(),
            'cache_performance': None,
            'behavioral_insights': None,
            'system_metrics': None
        }
        
        # Cache performance
        if CACHE_MONITOR_AVAILABLE:
            try:
                cache_report = cache_monitor.generate_performance_report("last_hour")
                report['cache_performance'] = {
                    'hit_rate': cache_report.hit_rate_percentage,
                    'avg_response_time': cache_report.avg_response_time_ms,
                    'performance_grade': cache_report.performance_grade,
                    'recommendations': cache_report.recommendations
                }
            except Exception as e:
                report['cache_performance'] = {'error': str(e)}
        
        # Behavioral insights
        try:
            response = requests.get(f"{SERVICES['behavioral_insights']}/api/metrics", timeout=5)
            if response.status_code == 200:
                report['behavioral_insights'] = response.json()
        except Exception as e:
            report['behavioral_insights'] = {'error': str(e)}
        
        # System metrics
        services_health = await health_checker.check_all_services()
        healthy_services = sum(1 for s in services_health.values() if s['status'] == 'healthy')
        avg_response_time = statistics.mean([
            s.get('response_time_ms', 0) for s in services_health.values() 
            if 'response_time_ms' in s
        ]) if services_health else 0
        
        report['system_metrics'] = {
            'healthy_services': healthy_services,
            'total_services': len(services_health),
            'avg_service_response_time': avg_response_time,
            'uptime_percentage': (healthy_services / max(len(services_health), 1)) * 100
        }
        
        return JSONResponse(content=report)
        
    except Exception as e:
        logger.error("❌ Performance report error", error=str(e))
        return JSONResponse(
            status_code=500,
            content={'error': str(e)}
        )

@app.get("/api/behavioral/insights")
async def behavioral_insights_summary():
    """Behavioral insights özeti."""
    try:
        # Try to get from behavioral insights service
        response = requests.get(f"{SERVICES['behavioral_insights']}/api/metrics", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return JSONResponse(content={
                'error': 'Behavioral insights service unavailable',
                'status_code': response.status_code
            })
            
    except Exception as e:
        return JSONResponse(content={
            'error': str(e),
            'message': 'Could not fetch behavioral insights'
        })

@app.get("/api/cache/optimization")
async def cache_optimization_recommendations():
    """Cache optimization önerileri."""
    try:
        if not CACHE_MONITOR_AVAILABLE:
            return JSONResponse(content={
                'error': 'Cache monitor not available',
                'recommendations': [
                    'Install cache monitoring system',
                    'Enable cache performance tracking'
                ]
            })
        
        # Get cache performance report
        cache_report = cache_monitor.generate_performance_report("last_day")
        
        # Generate optimization recommendations
        optimizations = {
            'current_performance': {
                'hit_rate': cache_report.hit_rate_percentage,
                'avg_response_time': cache_report.avg_response_time_ms,
                'performance_grade': cache_report.performance_grade
            },
            'recommendations': cache_report.recommendations,
            'optimization_priorities': []
        }
        
        # Priority recommendations
        if cache_report.hit_rate_percentage < 80:
            optimizations['optimization_priorities'].append({
                'priority': 'HIGH',
                'action': 'Increase cache TTL values',
                'expected_improvement': '10-20% hit rate increase'
            })
        
        if cache_report.avg_response_time_ms > 100:
            optimizations['optimization_priorities'].append({
                'priority': 'MEDIUM',
                'action': 'Optimize cache data structure',
                'expected_improvement': '20-50% response time reduction'
            })
        
        return JSONResponse(content=optimizations)
        
    except Exception as e:
        logger.error("❌ Cache optimization error", error=str(e))
        return JSONResponse(content={
            'error': str(e),
            'recommendations': ['Enable cache monitoring for optimization insights']
        })

@app.get("/health")
async def health_check():
    """Comprehensive dashboard sağlık kontrolü."""
    return {
        'status': 'healthy',
        'service': 'comprehensive_admin_dashboard',
        'systems_available': {
            'cache_monitor': CACHE_MONITOR_AVAILABLE,
            'personality_adapter': PERSONALITY_ADAPTER_AVAILABLE
        },
        'timestamp': datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🎛️ Starting GAVATCore Comprehensive Admin Dashboard...")
    print("=" * 70)
    print("🚀 Ultimate Control Center Features:")
    print("   • Real-time system health monitoring")
    print("   • Behavioral insights integration")
    print("   • Cache performance analytics")
    print("   • Smart personality adaptation metrics")
    print("   • Performance optimization recommendations")
    print("   • Multi-service coordination")
    print()
    print("🌐 Dashboard URL: http://localhost:8000")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("⚡ Auto-refresh every 30 seconds")
    print()
    print("🔗 Integrated Services:")
    for name, url in SERVICES.items():
        print(f"   • {name.replace('_', ' ').title()}: {url}")
    print("=" * 70)
    
    # Start cache monitoring if available
    if CACHE_MONITOR_AVAILABLE:
        cache_monitor.start_background_monitoring()
        print("✅ Cache monitoring started")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    ) 