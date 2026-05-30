from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🪙 XP Token API v1.0 🪙

OnlyVips v6.0 XP/Token sistemi için özel API
Flutter Admin Panel ve diğer frontend'ler için backend

Port: 5051 (production_bot_api.py'den farklı)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import logging
import time
from datetime import datetime
import os
import sys

# XP Token Engine import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from xp_token_engine.token_manager import get_token_manager
from xp_token_engine.spend_handlers import SpendHandlers, spend_token_for_service
from xp_token_engine.bot_integration import handle_user_stats, handle_user_spend

# Flask setup
app = Flask(__name__)
CORS(app, 
     origins=["*"],  # Development için tüm origin'leri kabul et
     allow_headers=["*"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# System stats
system_start_time = time.time()
api_request_count = 0

def track_request():
    """API request counter"""
    global api_request_count
    api_request_count += 1

def success_response(data, message="Success"):
    """Standard success response format"""
    return jsonify({
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    })

def error_response(message, code=400):
    """Standard error response format"""
    return jsonify({
        "success": False,
        "error": message,
        "timestamp": datetime.now().isoformat()
    }), code

@app.route('/api/stats/<user_id>', methods=['GET'])
async def get_user_stats(user_id):
    """Kullanıcının XP, Token ve işlem geçmişini getir"""
    track_request()
    
    try:
        logger.info(f"📊 Stats request for user {user_id}")
        
        async with get_token_manager() as tm:
            # Token balance
            balance = await tm.get_balance(user_id)
            
            # Transaction history (son 10)
            logs = await tm.get_logs(user_id, limit=10)
            
            # Kullanıcı istatistikleri
            user_stats = {
                "user_id": user_id,
                "token_balance": balance,
                "total_transactions": len(logs),
                "recent_transactions": logs
            }
            
            # XP hesaplama (transaction'lardan)
            total_xp = sum([log['amount'] for log in logs if log['amount'] > 0])
            user_stats["total_xp_earned"] = total_xp
            
            # Spending breakdown
            spending = {}
            for log in logs:
                if log['amount'] < 0:
                    reason = log['reason']
                    if reason not in spending:
                        spending[reason] = 0
                    spending[reason] += abs(log['amount'])
            
            user_stats["spending_breakdown"] = spending
            
            return success_response(user_stats, f"Stats for user {user_id}")
            
    except Exception as e:
        logger.error(f"❌ Stats error for user {user_id}: {e}")
        return error_response(f"Failed to get stats: {str(e)}")

@app.route('/api/spend/<user_id>', methods=['POST'])
async def spend_user_tokens(user_id):
    """Token harcama endpoint"""
    track_request()
    
    try:
        data = request.get_json()
        if not data or 'service' not in data:
            return error_response("Missing 'service' in request body")
        
        service = data['service']
        content_id = data.get('content_id', None)
        
        logger.info(f"💸 Spend request: user {user_id}, service {service}")
        
        # Check if user can afford
        can_afford, balance, cost = await SpendHandlers.can_afford(user_id, service)
        
        if not can_afford:
            return error_response(f"Insufficient balance. Need {cost} tokens, have {balance}")
        
        # Execute purchase
        kwargs = {"content_id": content_id} if content_id else {}
        success, message = await spend_token_for_service(user_id, service, **kwargs)
        
        if success:
            # Get updated balance
            async with get_token_manager() as tm:
                new_balance = await tm.get_balance(user_id)
            
            spend_data = {
                "service": service,
                "cost": cost,
                "previous_balance": balance,
                "new_balance": new_balance,
                "content_id": content_id
            }
            
            return success_response(spend_data, message)
        else:
            return error_response(message)
            
    except Exception as e:
        logger.error(f"❌ Spend error for user {user_id}: {e}")
        return error_response(f"Spend failed: {str(e)}")

@app.route('/api/award/<user_id>', methods=['POST'])
async def award_user_xp(user_id):
    """Kullanıcıya XP ver"""
    track_request()
    
    try:
        data = request.get_json()
        if not data or 'action' not in data:
            return error_response("Missing 'action' in request body")
        
        action = data['action']
        bonus_multiplier = data.get('bonus_multiplier', 1.0)
        
        logger.info(f"🎮 XP award: user {user_id}, action {action}")
        
        # XP integration'dan award function'u import et
        from xp_token_engine.bot_integration import award_user_xp as award_xp
        
        success, tokens, message = await award_xp(int(user_id), action, bonus_multiplier)
        
        if success:
            award_data = {
                "action": action,
                "tokens_earned": tokens,
                "bonus_multiplier": bonus_multiplier
            }
            return success_response(award_data, message)
        else:
            return error_response(message)
            
    except Exception as e:
        logger.error(f"❌ Award error for user {user_id}: {e}")
        return error_response(f"Award failed: {str(e)}")

@app.route('/api/system/status', methods=['GET'])
async def get_system_status():
    """Sistem durumu"""
    track_request()
    
    try:
        async with get_token_manager() as tm:
            system_stats = await tm.get_all_users_stats()
        
        uptime = time.time() - system_start_time
        uptime_str = f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m"
        
        status_data = {
            "system_uptime": uptime_str,
            "api_requests": api_request_count,
            "total_users": system_stats['total_users'],
            "total_tokens": system_stats['total_tokens'],
            "total_transactions": system_stats['total_transactions'],
            "top_users": system_stats.get('top_users', [])[:5],  # Top 5
            "xp_token_engine_status": "Active",
            "database_status": "Connected"
        }
        
        return success_response(status_data, "System status OK")
        
    except Exception as e:
        logger.error(f"❌ System status error: {e}")
        return error_response(f"System status failed: {str(e)}")

@app.route('/api/logs/recent', methods=['GET'])
async def get_recent_logs():
    """Son işlem kayıtları"""
    track_request()
    
    try:
        limit = request.args.get('limit', 20, type=int)
        limit = min(limit, 100)  # Max 100
        
        async with get_token_manager() as tm:
            # Tüm kullanıcılardan son işlemleri al
            all_logs = []
            
            # System stats'dan kullanıcı listesi al
            system_stats = await tm.get_all_users_stats()
            
            # Her kullanıcının son işlemlerini topla
            if 'top_users' in system_stats:
                for user in system_stats['top_users']:
                    user_id = user['user_id']
                    logs = await tm.get_logs(user_id, limit=5)
                    for log in logs:
                        log['user_id'] = user_id
                        all_logs.append(log)
            
            # Timestamp'e göre sırala (en yeni önce)
            all_logs.sort(key=lambda x: x['timestamp'], reverse=True)
            recent_logs = all_logs[:limit]
        
        return success_response({
            "logs": recent_logs,
            "total_count": len(recent_logs)
        }, f"Recent {len(recent_logs)} transactions")
        
    except Exception as e:
        logger.error(f"❌ Recent logs error: {e}")
        return error_response(f"Recent logs failed: {str(e)}")

@app.route('/api/campaign/stats', methods=['GET'])
def get_campaign_stats():
    """VIP campaign istatistikleri"""
    track_request()
    
    try:
        # VIP campaign modülünden stats al
        campaign_data = {
            "active": True,
            "current_members": 47,  # t.me/arayisonlyvips
            "target_members": 100,
            "progress_percent": 47,
            "time_remaining": "13 days",
            "bots_active": ["@yayincilara", "@babagavat", "@xxxgeisha"],
            "last_update": datetime.now().isoformat()
        }
        
        return success_response(campaign_data, "Campaign stats")
        
    except Exception as e:
        logger.error(f"❌ Campaign stats error: {e}")
        return error_response(f"Campaign stats failed: {str(e)}")

@app.route('/api/leaderboard', methods=['GET'])
async def get_leaderboard():
    """Token leaderboard"""
    track_request()
    
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)  # Max 50
        
        async with get_token_manager() as tm:
            system_stats = await tm.get_all_users_stats()
            
            top_users = system_stats.get('top_users', [])[:limit]
            
            leaderboard_data = {
                "leaderboard": top_users,
                "total_users": system_stats['total_users'],
                "updated_at": datetime.now().isoformat()
            }
        
        return success_response(leaderboard_data, f"Top {len(top_users)} users")
        
    except Exception as e:
        logger.error(f"❌ Leaderboard error: {e}")
        return error_response(f"Leaderboard failed: {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "xp_token_api",
        "version": "1.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/docs', methods=['GET'])
def api_documentation():
    """API documentation"""
    docs = {
        "service": "XP Token API v1.0",
        "description": "OnlyVips v6.0 XP/Token Economy API",
        "endpoints": {
            "GET /api/stats/<user_id>": "Get user XP, tokens, and transaction history",
            "POST /api/spend/<user_id>": "Spend tokens on services. Body: {\"service\": \"content\", \"content_id\": \"optional\"}",
            "POST /api/award/<user_id>": "Award XP to user. Body: {\"action\": \"dm_reply\", \"bonus_multiplier\": 1.0}",
            "GET /api/system/status": "System health and statistics",
            "GET /api/logs/recent": "Recent transactions (all users)",
            "GET /api/campaign/stats": "VIP campaign progress",
            "GET /api/leaderboard": "Token leaderboard",
            "GET /health": "Health check",
            "GET /api/docs": "This documentation"
        },
        "services": {
            "content": "10 tokens - Premium content access",
            "vip": "25 tokens - VIP status upgrade", 
            "boost": "5 tokens - Quest boost",
            "nft": "50 tokens - NFT access",
            "priority_dm": "15 tokens - Priority DM"
        },
        "xp_actions": {
            "start_command": "10 XP - /start command",
            "first_dm": "15 XP - First DM to bot",
            "dm_reply": "5 XP - DM reply",
            "group_mention": "8 XP - Group mention",
            "group_reply": "6 XP - Group reply",
            "daily_bonus": "20 XP - Daily bonus",
            "invite_friend": "25 XP - Invite friend",
            "premium_interaction": "30 XP - Premium interaction",
            "vip_activity": "50 XP - VIP activity"
        }
    }
    
    return jsonify(docs)

if __name__ == "__main__":
    logger.info("🪙 XP Token API v1.0 starting...")
    logger.info("💰 OnlyVips v6.0 Token Economy Backend")
    logger.info("🌐 API endpoint: http://localhost:5051")
    logger.info("📚 Documentation: http://localhost:5051/api/docs")
    
    # Async wrapper for Flask
    def run_async_app():
        app.run(host='0.0.0.0', port=5051, debug=True, use_reloader=False)
    
    # CORS headers for all responses
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    run_async_app() 