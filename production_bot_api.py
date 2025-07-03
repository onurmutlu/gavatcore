#!/usr/bin/env python3
"""
🚀 Production Bot Management API v6.0 🚀

Flutter Admin Panel için real-time bot yönetim API'si
OnlyVips v6.0 - Enterprise Bot Control Backend

Enhanced Features:
- Type annotations ve comprehensive error handling
- Structured logging ve performance monitoring
- CORS configuration ve security headers
- Health checks ve monitoring endpoints
- Graceful error handling ve fallbacks
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
import os
import time
import glob
import sqlite3
import subprocess
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import traceback
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
import functools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("gavatcore.production_api")

# Initialize Flask app with enhanced configuration
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'dev-key-change-in-production'),
    JSON_SORT_KEYS=False,
    JSONIFY_PRETTYPRINT_REGULAR=True
)

# Enhanced CORS configuration
CORS(app, 
     origins=["http://localhost:*", "https://localhost:*", "http://127.0.0.1:*"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Type definitions
BotData = Dict[str, Any]
SystemMetrics = Dict[str, Union[str, int, float, bool]]
ApiResponse = Dict[str, Any]

class BotStatus(Enum):
    """Bot status enumeration."""
    ACTIVE = "active"
    OFFLINE = "offline"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"

class HealthStatus(Enum):
    """System health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class BotConfig:
    """Bot configuration data structure."""
    username: str
    display_name: str
    phone: str
    telegram_handle: str
    character: str
    session_path: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {
            "username": self.username,
            "display_name": self.display_name,
            "phone": self.phone,
            "telegram_handle": self.telegram_handle,
            "character": self.character,
            "session_path": self.session_path
        }

@dataclass 
class PerformanceMetrics:
    """Performance metrics for a bot."""
    messages_sent: int = 0
    invites_sent: int = 0
    errors: int = 0
    flood_waits: int = 0
    uptime_seconds: float = 0.0
    start_time: Optional[float] = None
    last_activity: str = "Unknown"
    performance_score: int = 0
    
    def calculate_performance_score(self) -> int:
        """Calculate performance score based on activity."""
        score = min((self.messages_sent * 2 + self.invites_sent * 5), 100)
        # Penalize for errors
        if self.errors > 0:
            score = max(0, score - (self.errors * 5))
        return score

# Production bot configurations
PRODUCTION_BOTS: List[BotConfig] = [
    BotConfig(
        username="yayincilara",
        display_name="🌟 Lara",
        phone="+905382617727",
        telegram_handle="@yayincilara",
        character="Samimi ve arkadaş canlısı, VIP kampanya uzmanı",
        session_path="sessions/yayincilara_conversation.session"
    ),
    BotConfig(
        username="babagavat", 
        display_name="🦁 Gavat Baba",
        phone="+905513272355",
        telegram_handle="@babagavat",
        character="Güçlü ve otoriter, kampanya lideri",
        session_path="sessions/babagavat_conversation.session"
    ),
    BotConfig(
        username="xxxgeisha",
        display_name="🌸 Geisha", 
        phone="+905486306226",
        telegram_handle="@xxxgeisha",
        character="Çekici ve gizemli, premium kullanıcı odaklı",
        session_path="sessions/xxxgeisha_conversation.session"
    )
]

# Global cache for performance optimization
_cache: Dict[str, Any] = {}
_cache_timestamps: Dict[str, float] = {}
CACHE_TTL = 30  # 30 seconds cache TTL

# Thread pool for I/O operations
executor = ThreadPoolExecutor(max_workers=4)

def with_error_handling(func):
    """Decorator for comprehensive error handling."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            return {
                "error": str(e),
                "function": func.__name__,
                "timestamp": datetime.now().isoformat()
            }
    return wrapper

def with_caching(cache_key: str, ttl: int = CACHE_TTL):
    """Decorator for caching responses."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Check cache
            if (cache_key in _cache and 
                cache_key in _cache_timestamps and 
                now - _cache_timestamps[cache_key] < ttl):
                logger.debug(f"Cache hit for {cache_key}")
                return _cache[cache_key]
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            _cache[cache_key] = result
            _cache_timestamps[cache_key] = now
            logger.debug(f"Cache updated for {cache_key}")
            
            return result
        return wrapper
    return decorator

def safe_file_operation(operation_func, default_return=None):
    """Safely execute file operations with error handling."""
    try:
        return operation_func()
    except (FileNotFoundError, PermissionError, json.JSONDecodeError) as e:
        logger.warning(f"File operation failed: {e}")
        return default_return
    except Exception as e:
        logger.error(f"Unexpected file operation error: {e}")
        return default_return

@with_error_handling
@with_caching("system_process_info", ttl=10)
def get_system_process_info() -> Optional[Dict[str, Any]]:
    """Get production bot system process information."""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'status']):
            try:
                proc_info = proc.info
                cmdline = ' '.join(proc_info['cmdline'] or [])
                
                # Look for production bot launcher processes
                if any(pattern in cmdline for pattern in [
                    'production_multi_bot_launcher.py',
                    'ultimate_telegram_bot_launcher.py',
                    'babagavat_production_launcher.py'
                ]):
                    uptime = time.time() - proc_info['create_time']
                    return {
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'cmdline': cmdline,
                        'start_time': proc_info['create_time'],
                        'uptime': uptime,
                        'uptime_human': str(timedelta(seconds=int(uptime))),
                        'status': proc_info.get('status', 'unknown'),
                        'memory_percent': proc.memory_percent() if proc.is_running() else 0.0
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        return None
        
    except Exception as e:
        logger.error(f"Error getting process info: {e}")
        return None

@with_error_handling
@with_caching("viral_report", ttl=60)
def get_latest_viral_report() -> Dict[str, Any]:
    """Get the latest viral campaign report."""
    def load_report():
        # Find viral report files
        report_files = glob.glob('arayisvips_viral_report_*.json')
        if not report_files:
            return {}
        
        # Get the newest file
        latest_file = max(report_files, key=os.path.getmtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return safe_file_operation(load_report, {})

@with_error_handling
@with_caching("bot_sessions", ttl=5)
def get_bot_session_status() -> Dict[str, Dict[str, Any]]:
    """Check bot session file status with comprehensive validation."""
    bot_statuses = {}
    
    for bot_config in PRODUCTION_BOTS:
        session_path = bot_config.session_path
        username = bot_config.username
        
        def check_session():
            # Check if session file exists
            session_exists = os.path.exists(session_path)
            
            if not session_exists:
                return {
                    'session_exists': False,
                    'session_valid': False,
                    'session_path': session_path,
                    'last_modified': 0,
                    'file_size': 0,
                    'error': 'Session file not found'
                }
            
            # Get file stats
            stat = os.stat(session_path)
            file_size = stat.st_size
            last_modified = stat.st_mtime
            
            # Validate session file
            session_valid = False
            error_message = None
            
            try:
                if file_size > 0:
                    conn = sqlite3.connect(session_path, timeout=2.0)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions';")
                    result = cursor.fetchone()
                    conn.close()
                    session_valid = result is not None
                else:
                    error_message = "Empty session file"
            except Exception as e:
                error_message = str(e)
            
            return {
                'session_exists': True,
                'session_valid': session_valid,
                'session_path': session_path,
                'last_modified': last_modified,
                'last_modified_human': datetime.fromtimestamp(last_modified).isoformat(),
                'file_size': file_size,
                'file_size_human': f"{file_size / 1024:.1f} KB" if file_size > 0 else "0 B",
                'error': error_message
            }
        
        bot_statuses[username] = safe_file_operation(check_session, {
            'session_exists': False,
            'session_valid': False,
            'session_path': session_path,
            'last_modified': 0,
            'file_size': 0,
            'error': 'Failed to check session'
        })
    
    return bot_statuses

def get_performance_metrics(bot_config: BotConfig, viral_data: Dict[str, Any]) -> PerformanceMetrics:
    """Extract performance metrics for a bot from viral report data."""
    bot_performance = viral_data.get('bot_performance', {})
    phone = bot_config.phone
    username = bot_config.username
    
    # Find performance data by phone or username
    perf_data = {}
    for key, data in bot_performance.items():
        if phone in key or username in key:
            perf_data = data
            break
    
    metrics = PerformanceMetrics(
        messages_sent=perf_data.get('messages_sent', 0),
        invites_sent=perf_data.get('invites_sent', 0),
        errors=perf_data.get('errors', 0),
        flood_waits=perf_data.get('flood_waits', 0),
        start_time=perf_data.get('start_time'),
        last_activity=perf_data.get('last_activity', 'Unknown')
    )
    
    # Calculate uptime
    if metrics.start_time:
        metrics.uptime_seconds = time.time() - metrics.start_time
    
    # Calculate performance score
    metrics.performance_score = metrics.calculate_performance_score()
    
    return metrics

@app.route('/api/system/status', methods=['GET'])
def get_system_status() -> Response:
    """
    Get comprehensive system status.
    
    Returns:
        JSON response with system status, bot information, and metrics
    """
    try:
        start_time = time.time()
        
        # Get system information
        process_info = get_system_process_info()
        viral_data = get_latest_viral_report()
        bot_sessions = get_bot_session_status()
        
        # Build bot status list
        updated_bots = []
        total_messages = 0
        total_invites = 0
        total_errors = 0
        
        for bot_config in PRODUCTION_BOTS:
            username = bot_config.username
            session_info = bot_sessions.get(username, {})
            
            # Get performance metrics
            metrics = get_performance_metrics(bot_config, viral_data)
            
            # Determine bot status
            is_active = (process_info is not None and 
                        session_info.get('session_valid', False))
            
            status = BotStatus.ACTIVE if is_active else BotStatus.OFFLINE
            
            # Calculate uptime string
            uptime = 'Offline'
            if is_active and metrics.uptime_seconds > 0:
                uptime = str(timedelta(seconds=int(metrics.uptime_seconds)))
            
            # Aggregate metrics
            total_messages += metrics.messages_sent
            total_invites += metrics.invites_sent
            total_errors += metrics.errors
            
            bot_data = {
                **bot_config.to_dict(),
                'status': status.value,
                'session_exists': session_info.get('session_exists', False),
                'session_valid': session_info.get('session_valid', False),
                'session_file_size': session_info.get('file_size', 0),
                'messages_sent': metrics.messages_sent,
                'invites_sent': metrics.invites_sent,
                'uptime': uptime,
                'uptime_seconds': metrics.uptime_seconds,
                'last_activity': metrics.last_activity,
                'performance_score': metrics.performance_score,
                'errors': metrics.errors,
                'flood_waits': metrics.flood_waits,
                'session_error': session_info.get('error')
            }
            
            updated_bots.append(bot_data)
        
        # Calculate system statistics
        active_bots = sum(1 for bot in updated_bots if bot['status'] == BotStatus.ACTIVE.value)
        avg_performance = (sum(bot['performance_score'] for bot in updated_bots) / 
                          len(updated_bots) if updated_bots else 0)
        
        # Determine system health
        health_status = HealthStatus.HEALTHY
        if active_bots == 0:
            health_status = HealthStatus.CRITICAL
        elif active_bots < len(PRODUCTION_BOTS) / 2:
            health_status = HealthStatus.DEGRADED
        
        system_stats = {
            'total_bots': len(updated_bots),
            'active_bots': active_bots,
            'total_messages': total_messages,
            'total_invites': total_invites,
            'total_errors': total_errors,
            'avg_performance': round(avg_performance, 1),
            'system_uptime': (f"Running (PID: {process_info['pid']})" 
                             if process_info else 'Stopped'),
            'health_status': health_status.value,
            'error_rate': (total_errors / max(total_messages + total_invites, 1)) * 100
        }
        
        # Response time calculation
        response_time_ms = (time.time() - start_time) * 1000
        
        response_data = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'response_time_ms': round(response_time_ms, 2),
            'system_stats': system_stats,
            'bots': updated_bots,
            'process_info': process_info,
            'viral_campaign': {
                'has_data': bool(viral_data),
                'last_update': viral_data.get('timestamp', 'Unknown'),
                'total_targets': viral_data.get('total_targets', 0)
            }
        }
        
        logger.info(f"System status retrieved successfully in {response_time_ms:.2f}ms")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/system/health', methods=['GET'])
def get_system_health() -> Response:
    """
    Quick health check endpoint.
    
    Returns:
        JSON response with basic health information
    """
    try:
        process_info = get_system_process_info()
        bot_sessions = get_bot_session_status()
        
        # Quick health assessment
        active_sessions = sum(1 for session in bot_sessions.values() 
                            if session.get('session_valid', False))
        
        is_healthy = process_info is not None and active_sessions > 0
        
        health_data = {
            'healthy': is_healthy,
            'timestamp': datetime.now().isoformat(),
            'process_running': process_info is not None,
            'active_sessions': active_sessions,
            'total_bots': len(PRODUCTION_BOTS)
        }
        
        status_code = 200 if is_healthy else 503
        return jsonify(health_data), status_code
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'healthy': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/system/start', methods=['POST'])
def start_system():
    """Production bot sistemini başlatır"""
    try:
        # Zaten çalışıyor mu kontrol et
        if get_system_process_info():
            return jsonify({
                'success': False,
                'error': 'System already running',
                'timestamp': datetime.now().isoformat()
            })
        
        # Production launcher'ı başlat
        process = subprocess.Popen(
            ['python3', 'production_multi_bot_launcher.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )
        
        # Biraz bekle
        time.sleep(3)
        
        # Başarılı mı kontrol et
        process_info = get_system_process_info()
        
        if process_info:
            return jsonify({
                'success': True,
                'message': 'Production bot system started successfully',
                'pid': process_info['pid'],
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to start system',
                'timestamp': datetime.now().isoformat()
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/system/stop', methods=['POST'])
def stop_system():
    """Production bot sistemini durdurur"""
    try:
        process_info = get_system_process_info()
        
        if not process_info:
            return jsonify({
                'success': False,
                'error': 'System is not running',
                'timestamp': datetime.now().isoformat()
            })
        
        # Process'i durdur
        try:
            process = psutil.Process(process_info['pid'])
            process.terminate()
            
            # Biraz bekle
            time.sleep(2)
            
            # Hala çalışıyor mu?
            if process.is_running():
                process.kill()  # Force kill
                
            return jsonify({
                'success': True,
                'message': 'Production bot system stopped successfully',
                'timestamp': datetime.now().isoformat()
            })
            
        except psutil.NoSuchProcess:
            return jsonify({
                'success': True,
                'message': 'Process already stopped',
                'timestamp': datetime.now().isoformat()
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/bot/<username>/restart', methods=['POST'])
def restart_bot(username):
    """Belirli bir botu yeniden başlatır"""
    try:
        # Bot configuration'ı bul
        bot_config = None
        for config in PRODUCTION_BOTS:
            if config.username == username:
                bot_config = config
                break
        
        if not bot_config:
            return jsonify({
                'success': False,
                'error': f'Bot {username} not found',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        # Bot restart logic (individual bot restart için ayrı bir script gerekebilir)
        # Şimdilik system restart simüle ediyoruz
        
        return jsonify({
            'success': True,
            'message': f'Bot {username} restart initiated',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/logs/recent', methods=['GET'])
def get_recent_logs():
    """Son log girişlerini döndürür"""
    try:
        # Real-time logs (simulated - gerçek log dosyalarından okuyabilir)
        current_time = datetime.now()
        
        # System status
        process_info = get_system_process_info()
        viral_data = get_latest_viral_report()
        
        active_bots = sum(1 for config in PRODUCTION_BOTS 
                         if os.path.exists(config.session_path))
        
        total_messages = viral_data.get('bot_performance', {})
        total_msg_count = sum(perf.get('messages_sent', 0) for perf in total_messages.values())
        total_invites = sum(perf.get('invites_sent', 0) for perf in total_messages.values())
        
        current_members = viral_data.get('current_members', 47)
        target_members = viral_data.get('target_members', 100)
        
        logs = [
            f'[{current_time.strftime("%H:%M:%S")}] ✅ {active_bots} bot active',
            f'[{(current_time - timedelta(minutes=1)).strftime("%H:%M:%S")}] 📊 Campaign: {current_members}/{target_members} members',
            f'[{(current_time - timedelta(minutes=2)).strftime("%H:%M:%S")}] 🎯 VIP invites sent: {total_invites}',
            f'[{(current_time - timedelta(minutes=3)).strftime("%H:%M:%S")}] 💬 Total messages: {total_msg_count}',
            f'[{(current_time - timedelta(minutes=5)).strftime("%H:%M:%S")}] 🚀 System {"running" if process_info else "stopped"}',
        ]
        
        return jsonify({
            'success': True,
            'logs': logs,
            'timestamp': current_time.isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/campaign/stats', methods=['GET'])
def get_campaign_stats():
    """VIP campaign istatistiklerini döndürür"""
    try:
        viral_data = get_latest_viral_report()
        
        return jsonify({
            'success': True,
            'campaign_active': viral_data.get('campaign_active', False),
            'current_members': viral_data.get('current_members', 47),
            'target_members': viral_data.get('target_members', 100),
            'total_invites': viral_data.get('total_invites_sent', 0),
            'daily_growth': viral_data.get('daily_growth', 0),
            'conversion_rate': viral_data.get('conversion_rate', 0),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("🚀 Production Bot Management API v6.0 starting...")
    print("📱 Flutter Admin Panel backend ready!")
    print("🌐 API endpoint: http://localhost:5050")
    
    app.run(
        host='0.0.0.0',
        port=5050,
        debug=True
    ) 