#!/usr/bin/env python3
"""
🪙 Simple Token API v1.0 🪙
Basit token economy endpoint'leri - Flutter panel için
"""

from flask import Flask, jsonify
from flask_cors import CORS
import time
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

# Mock data
SYSTEM_START_TIME = time.time()
API_REQUEST_COUNT = 0

# Mock user data
MOCK_USERS = {
    "999999": {"balance": 1250, "total_earned": 2400, "total_spent": 1150},
    "123456": {"balance": 850, "total_earned": 1200, "total_spent": 350},
    "654321": {"balance": 2100, "total_earned": 3500, "total_spent": 1400},
}

MOCK_TRANSACTIONS = [
    {"user_id": "999999", "amount": 50, "type": "earn", "reason": "dm_reply", "timestamp": "2025-07-03T20:30:00"},
    {"user_id": "999999", "amount": -25, "type": "spend", "reason": "vip_content", "timestamp": "2025-07-03T19:15:00"},
    {"user_id": "123456", "amount": 100, "type": "earn", "reason": "daily_bonus", "timestamp": "2025-07-03T18:45:00"},
    {"user_id": "654321", "amount": -10, "type": "spend", "reason": "content", "timestamp": "2025-07-03T17:20:00"},
    {"user_id": "999999", "amount": 15, "type": "earn", "reason": "group_mention", "timestamp": "2025-07-03T16:10:00"},
]

def track_request():
    global API_REQUEST_COUNT
    API_REQUEST_COUNT += 1

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """Sistem durumu"""
    track_request()
    
    uptime = time.time() - SYSTEM_START_TIME
    uptime_str = f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s"
    
    total_tokens = sum(user["balance"] for user in MOCK_USERS.values())
    total_users = len(MOCK_USERS)
    
    return jsonify({
        "success": True,
        "data": {
            "system_uptime": uptime_str,
            "api_requests": API_REQUEST_COUNT,
            "total_users": total_users,
            "total_tokens": total_tokens,
            "total_transactions": len(MOCK_TRANSACTIONS),
            "xp_token_engine_status": "Active",
            "database_status": "Connected",
            "active_bots": ["gawatbaba", "yayincilara", "xxxgeisha"]
        },
        "message": "System status OK",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/stats/<user_id>', methods=['GET'])
def get_user_stats(user_id):
    """Kullanıcı istatistikleri"""
    track_request()
    
    if user_id in MOCK_USERS:
        user_data = MOCK_USERS[user_id]
        user_transactions = [t for t in MOCK_TRANSACTIONS if t["user_id"] == user_id]
        
        return jsonify({
            "success": True,
            "data": {
                "user_id": user_id,
                "token_balance": user_data["balance"],
                "total_xp_earned": user_data["total_earned"],
                "total_spent": user_data["total_spent"],
                "recent_transactions": user_transactions[-5:],  # Son 5 işlem
                "spending_breakdown": {
                    "content": 150,
                    "vip_content": 200,
                    "boost": 50
                }
            },
            "message": f"Stats for user {user_id}",
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "success": False,
            "error": "User not found",
            "timestamp": datetime.now().isoformat()
        }), 404

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Token leaderboard"""
    track_request()
    
    # En yüksek bakiyeye göre sırala
    sorted_users = sorted(MOCK_USERS.items(), key=lambda x: x[1]["balance"], reverse=True)
    
    leaderboard = []
    for rank, (user_id, data) in enumerate(sorted_users, 1):
        leaderboard.append({
            "rank": rank,
            "user_id": user_id,
            "balance": data["balance"],
            "total_earned": data["total_earned"]
        })
    
    return jsonify({
        "success": True,
        "data": {
            "leaderboard": leaderboard,
            "total_users": len(MOCK_USERS),
            "updated_at": datetime.now().isoformat()
        },
        "message": f"Top {len(leaderboard)} users",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/logs/recent', methods=['GET'])
def get_recent_logs():
    """Son işlemler"""
    track_request()
    
    # Timestamp'e göre sırala
    sorted_transactions = sorted(MOCK_TRANSACTIONS, key=lambda x: x["timestamp"], reverse=True)
    
    return jsonify({
        "success": True,
        "data": {
            "logs": sorted_transactions[:10],  # Son 10 işlem
            "total_count": len(MOCK_TRANSACTIONS)
        },
        "message": f"Recent {len(sorted_transactions[:10])} transactions",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/campaign/stats', methods=['GET'])
def get_campaign_stats():
    """VIP campaign istatistikleri"""
    track_request()
    
    return jsonify({
        "success": True,
        "data": {
            "active": True,
            "current_members": 47,
            "target_members": 100,
            "progress_percent": 47,
            "time_remaining": "13 days",
            "bots_active": ["@yayincilara", "@babagavat", "@xxxgeisha"],
            "rewards_distributed": 1200,
            "last_update": datetime.now().isoformat()
        },
        "message": "Campaign stats",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/award/<award_id>', methods=['GET', 'POST', 'OPTIONS'])
def handle_award(award_id):
    """Award sistemi - GET ve POST istekleri için"""
    track_request()
    
    if award_id == "admin_demo_123":
        # Admin demo award
        return jsonify({
            "success": True,
            "data": {
                "award_id": award_id,
                "title": "Admin Demo Award",
                "description": "Demo award for testing purposes",
                "token_value": 500,
                "xp_value": 100,
                "status": "active",
                "recipients_count": 12,
                "total_distributed": 6000,
                "created_by": "admin",
                "created_at": "2025-07-03T15:30:00",
                "last_awarded": datetime.now().isoformat()
            },
            "message": f"Award details for {award_id}",
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "success": False,
            "error": "Award not found",
            "available_awards": ["admin_demo_123"],
            "timestamp": datetime.now().isoformat()
        }), 404

@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "service": "simple_token_api",
        "version": "1.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API documentation"""
    return jsonify({
        "service": "Simple Token API v1.0",
        "description": "Basic token economy endpoints",
        "endpoints": {
            "GET /api/system/status": "System status and statistics",
            "GET /api/stats/<user_id>": "User token statistics",
            "GET /api/leaderboard": "Token leaderboard",
            "GET /api/logs/recent": "Recent transactions",
            "GET /api/campaign/stats": "VIP campaign progress",
            "GET /health": "Health check",
            "GET /api/docs": "This documentation"
        },
        "sample_user_ids": list(MOCK_USERS.keys()),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def home():
    """Ana sayfa"""
    return jsonify({
        "message": "🪙 Simple Token API v1.0",
        "description": "Token economy system for Flutter panel",
        "documentation": "/api/docs",
        "health": "/health",
        "status": "/api/system/status"
    })

if __name__ == "__main__":
    print("🪙 Simple Token API v1.0 starting...")
    print("💰 Token Economy Backend for Flutter Panel")
    print("🌐 API endpoint: http://localhost:5051")
    print("📚 Documentation: http://localhost:5051/api/docs")
    print("🔍 Health check: http://localhost:5051/health")
    print("")
    
    app.run(host='0.0.0.0', port=5051, debug=True, use_reloader=False) 